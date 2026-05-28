"""
⑥ 实时区域拥堵排行
消费 traffic-cleaned Topic，按拥堵指数对各区域排序，写入 MySQL region_congestion_rank 表
"""
import os
import sys

spark_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, spark_root)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, round, approx_count_distinct, current_timestamp

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
        .option("kafka.group.id", "spark-region-rank")
        .option("failOnDataLoss", "false")
        .load()
    )

    parsed_df = (
        cleaned_df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
    )

    parsed_df = parsed_df.withColumn("ts", col("timestamp").cast("timestamp"))
    parsed_df.createOrReplaceTempView("traffic_view")

    # 区域拥堵排行
    region_rank_df = spark.sql("""
        SELECT
            district,
            CURRENT_DATE() AS rank_date,
            HOUR(CURRENT_TIMESTAMP()) AS rank_hour,
            ROUND(AVG(CAST(congestion_index AS DOUBLE)), 3) AS avg_congestion,
            SUM(CAST(total_flow AS INT)) AS total_vehicles,
            ROUND(AVG(CAST(avg_speed AS DOUBLE)), 2) AS avg_speed,
            approx_count_distinct(detector_id) AS active_roads,
            ROUND(
                (SUM(CAST(total_flow AS INT)) / 1000.0) * 0.3 +
                AVG(CAST(congestion_index AS DOUBLE)) * 0.5 +
                ((100.0 - AVG(CAST(avg_speed AS DOUBLE))) / 100.0) * 0.2,
                3
            ) AS heat_score,
            CURRENT_TIMESTAMP() AS update_time
        FROM traffic_view
        GROUP BY district
    """)

    (region_rank_df.writeStream
        .outputMode("append")
        .trigger(processingTime="30 seconds")
        .foreachBatch(foreach_batch_mysql(
            "region_congestion_rank",
            primary_keys=["district"],
        ))
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/advanced/region_rank")
        .start())

    print("[进阶-⑥区域排行] 作业启动，来源 Topic:", KAFKA_TOPIC_CLEANED)
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
