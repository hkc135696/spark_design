"""
② 实时 TopN 热点道路分析
消费 traffic-cleaned Topic，滑动窗口内统计各道路拥堵分，取 Top10 写入 MySQL hotspot_roads 表
"""
import os
import sys

spark_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, spark_root)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, date_format, round, current_timestamp
from pyspark.sql.window import Window
from pyspark.sql import functions as F

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
        .option("kafka.group.id", "spark-hotspot")
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

    # TopN 热点道路（滑动窗口 + ROW_NUMBER）
    hotspot_df = spark.sql("""
        SELECT
            detector_id,
            detector_name,
            district,
            road_type,
            ROUND(AVG(CAST(congestion_index AS DOUBLE)), 3) AS congestion_score,
            SUM(CAST(total_flow AS INT)) AS total_vehicles,
            ROUND(AVG(CAST(avg_speed AS DOUBLE)), 2) AS avg_speed,
            CURRENT_TIMESTAMP() AS update_time,
            DATE_FORMAT(ts, 'yyyy-MM-dd HH:mm') AS stat_period
        FROM traffic_view
        WHERE congestion_index > 0
        GROUP BY
            detector_id, detector_name, district, road_type,
            DATE_FORMAT(ts, 'yyyy-MM-dd HH:mm')
    """)

    # 截取 Top10
    window = Window.orderBy(F.col("congestion_score").desc())
    top10 = hotspot_df.withColumn("_rn", F.row_number().over(window)).where(F.col("_rn") <= 10).drop("_rn")

    (top10.writeStream
        .outputMode("append")
        .trigger(processingTime="30 seconds")
        .foreachBatch(foreach_batch_mysql(
            "hotspot_roads",
            primary_keys=["detector_id", "stat_period"],
        ))
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/advanced/hotspot")
        .start())

    print("[进阶-②TopN热点] 作业启动，来源 Topic:", KAFKA_TOPIC_CLEANED)
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
