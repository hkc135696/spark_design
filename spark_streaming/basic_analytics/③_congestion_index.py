"""
③ 实时计算道路拥堵指数
消费 traffic-cleaned Topic，按复合公式计算各道路拥堵指数，写入 MySQL congestion_index 表
"""
import os
import sys

spark_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, spark_root)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, round, when, current_timestamp

from spark_streaming import (
    SPARK_APP_NAME, SPARK_CONFIG, KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_CLEANED, MYSQL_URL, MYSQL_USER, MYSQL_PASSWORD,
    TRAFFIC_SCHEMA, SPARK_CHECKPOINT_DIR, build_schema, foreach_batch_mysql,
)


def main():
    spark_local_dir = os.path.join(spark_root, "temp_spark")
    os.makedirs(spark_local_dir, exist_ok=True)

    spark = SparkSession.builder \
        .config("spark.local.dir", spark_local_dir) \
        .config("spark.sql.streaming.fileSink.log.enabled", "false")
    for k, v in SPARK_CONFIG.items():
        spark = spark.config(k, v)
    spark = spark.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    schema = build_schema()

    cleaned_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPIC_CLEANED)
        .option("startingOffsets", "latest")
        .option("kafka.group.id", "spark-congestion-index")
        .option("failOnDataLoss", "false")
        .load()
    )

    parsed_df = (
        cleaned_df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
    )

    parsed_df = parsed_df.withColumn("ts", to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss"))
    parsed_df.createOrReplaceTempView("traffic_view")

    # 道路拥堵指数（复合公式：流量 * 道路系数 * 速度影响系数）
    congestion_df = spark.sql("""
        SELECT
            detector_id,
            detector_name,
            district,
            road_type,
            SUM(CAST(total_flow AS INT)) AS total_vehicles,
            ROUND(AVG(CAST(congestion_index AS DOUBLE)), 3) AS raw_avg_congestion,
            ROUND(LEAST(1.0,
                (SUM(CAST(total_flow AS INT)) / 200.0) *
                CASE road_type
                    WHEN '高速'   THEN 0.8
                    WHEN '快速路'  THEN 0.85
                    WHEN '主干路'  THEN 1.0
                    WHEN '次干路'  THEN 1.2
                    WHEN '支路'   THEN 1.5
                    ELSE 1.0
                END *
                (0.5 + (1 - AVG(CAST(avg_speed AS DOUBLE)) / 80.0) * 0.5)
            ), 3) AS calculated_congestion,
            ROUND(AVG(CAST(avg_speed AS DOUBLE)), 2) AS avg_speed,
            CURRENT_TIMESTAMP() AS update_time
        FROM traffic_view
        GROUP BY detector_id, detector_name, district, road_type
    """)

    (congestion_df.writeStream
        .outputMode("append")
        .trigger(processingTime="30 seconds")
        .foreachBatch(foreach_batch_mysql(
            "congestion_index",
            primary_keys=["detector_id"],
        ))
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/basic/congestion_index")
        .start())

    print("[基础-③拥堵指数] 作业启动，来源 Topic:", KAFKA_TOPIC_CLEANED)
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
