"""
④ 统计高峰时段流量变化
消费 traffic-cleaned Topic，按高峰/平峰/夜间分类统计，写入 MySQL region_hourly_stats 表
"""
import os
import sys

spark_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, spark_root)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, date_format, hour, round, current_timestamp

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
        .option("kafka.group.id", "spark-peak-traffic")
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

    # 高峰时段流量变化统计
    peak_stats_df = spark.sql("""
        SELECT
            district,
            DATE_FORMAT(ts, 'yyyy-MM-dd') AS stat_date,
            HOUR(ts) AS stat_hour,
            SUM(CAST(total_flow AS INT)) AS total_vehicles,
            ROUND(AVG(CAST(avg_speed AS DOUBLE)), 2) AS avg_speed,
            ROUND(AVG(CAST(congestion_index AS DOUBLE)), 3) AS avg_congestion,
            ROUND(MAX(CAST(congestion_index AS DOUBLE)), 3) AS max_congestion,
            ROUND(AVG(CAST(occupancy AS DOUBLE)), 2) AS avg_occupancy,
            CASE
                WHEN HOUR(ts) BETWEEN 7 AND 9  THEN '早高峰'
                WHEN HOUR(ts) BETWEEN 17 AND 19 THEN '晚高峰'
                WHEN HOUR(ts) BETWEEN 22 AND 23
                  OR HOUR(ts) BETWEEN 0 AND 6   THEN '夜间'
                ELSE '平峰'
            END AS peak_type,
            CURRENT_TIMESTAMP() AS update_time
        FROM traffic_view
        GROUP BY
            district,
            DATE_FORMAT(ts, 'yyyy-MM-dd'),
            HOUR(ts)
    """)

    (peak_stats_df.writeStream
        .outputMode("append")
        .trigger(processingTime="30 seconds")
        .foreachBatch(foreach_batch_mysql(
            "region_hourly_stats",
            primary_keys=["district", "stat_date", "stat_hour"],
        ))
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/basic/peak_traffic")
        .start())

    print("[基础-④高峰时段] 作业启动，来源 Topic:", KAFKA_TOPIC_CLEANED)
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
