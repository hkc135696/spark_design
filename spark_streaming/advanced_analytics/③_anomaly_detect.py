"""
③ 异常车辆检测
消费 traffic-cleaned Topic，基于 3σ 原则检测速度异常，写入 MySQL traffic_alerts 表
"""
import os
import sys

spark_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, spark_root)

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, to_json, struct,
    abs as spark_abs, round, current_timestamp,
    date_format,
)

from spark_streaming import (
    SPARK_APP_NAME, SPARK_CONFIG, KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_CLEANED, KAFKA_TOPIC_ALERTS, MYSQL_URL, MYSQL_USER, MYSQL_PASSWORD,
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
        .option("kafka.group.id", "spark-anomaly")
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

    # 异常车辆检测（3σ 原则）
    anomaly_df = spark.sql("""
        SELECT
            detector_id,
            detector_name,
            district,
            DATE_FORMAT(ts, 'yyyy-MM-dd HH:mm:ss') AS alert_timestamp,
            ROUND(CAST(avg_speed AS DOUBLE), 2) AS avg_speed,
            ROUND(
                (CAST(avg_speed AS DOUBLE) - AVG(CAST(avg_speed AS DOUBLE)) OVER (
                    PARTITION BY detector_id
                    ORDER BY ts
                    ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING
                )) / NULLIF(
                    STDDEV(CAST(avg_speed AS DOUBLE)) OVER (
                        PARTITION BY detector_id
                        ORDER BY ts
                        ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING
                    ), 0
                ), 2
            ) AS z_score,
            'SPEED_ANOMALY' AS alert_type,
            2 AS alert_level,
            CONCAT('检测器 ', detector_id, ' 速度异常，Z-Score=', ROUND(
                (CAST(avg_speed AS DOUBLE) - AVG(CAST(avg_speed AS DOUBLE)) OVER (
                    PARTITION BY detector_id ORDER BY ts ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING
                )) / NULLIF(
                    STDDEV(CAST(avg_speed AS DOUBLE)) OVER (
                        PARTITION BY detector_id ORDER BY ts ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING
                    ), 0
                ), 2
            )) AS description,
            ROUND(CAST(avg_speed AS DOUBLE), 2) AS trigger_value,
            0.9 AS threshold_value,
            DATE_FORMAT(ts, 'yyyy-MM-dd HH:mm:ss') AS start_time,
            DATE_FORMAT(ts, 'yyyy-MM-dd HH:mm:ss') AS end_time,
            CURRENT_TIMESTAMP() AS create_time,
            0 AS status
        FROM traffic_view
        WHERE avg_speed >= 0
    """)

    # 过滤 |z_score| > 3 的异常记录
    anomalies = anomaly_df.where(spark_abs(col("z_score")) > 3)

    (anomalies.writeStream
        .outputMode("append")
        .trigger(processingTime="30 seconds")
        .foreachBatch(foreach_batch_mysql("traffic_alerts"))
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/advanced/anomaly")
        .start())

    # 异常告警写入 Kafka
    (anomalies.select(to_json(struct("*")).alias("value"))
        .writeStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("topic", KAFKA_TOPIC_ALERTS)
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/advanced/anomaly_kafka")
        .outputMode("append")
        .start())

    print("[进阶-③异常检测] 作业启动，来源 Topic:", KAFKA_TOPIC_CLEANED)
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
