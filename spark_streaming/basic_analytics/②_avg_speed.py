"""
② 实时统计平均车速
消费 traffic-cleaned Topic，统计各检测器的速度指标（均值/标准差/中位数），写入 MySQL speed_stats 表
"""
import os
import sys

spark_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, spark_root)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, round, percentile_approx, current_timestamp

from spark_streaming import (
    SPARK_APP_NAME, SPARK_CONFIG, KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_CLEANED, MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD,
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
        .option("kafka.group.id", "spark-avg-speed")
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

    # 平均车速统计（1分钟窗口 + 标准差/中位数）
    speed_stats_df = spark.sql("""
        SELECT
            detector_id,
            detector_name,
            district,
            ROUND(AVG(CAST(avg_speed AS DOUBLE)), 2) AS avg_speed,
            ROUND(STDDEV(CAST(avg_speed AS DOUBLE)), 2) AS speed_stddev,
            ROUND(MAX(CAST(avg_speed AS DOUBLE)), 2) AS max_speed,
            ROUND(MIN(CAST(avg_speed AS DOUBLE)), 2) AS min_speed,
            ROUND(PERCENTILE_APPROX(CAST(avg_speed AS DOUBLE), 0.5), 2) AS median_speed,
            COUNT(*) AS data_points,
            CURRENT_TIMESTAMP() AS update_time
        FROM traffic_view
        WHERE avg_speed >= 0
        GROUP BY detector_id, detector_name, district
    """)

    (speed_stats_df.writeStream
        .outputMode("append")
        .trigger(processingTime="30 seconds")
        .foreachBatch(foreach_batch_mysql(
            "speed_stats",
            primary_keys=["detector_id"],
        ))
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/basic/avg_speed")
        .start())

    print("[基础-②平均车速] 作业启动，来源 Topic:", KAFKA_TOPIC_CLEANED)
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
