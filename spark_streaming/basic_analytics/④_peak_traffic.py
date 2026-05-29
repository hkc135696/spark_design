"""
④ 统计高峰时段流量变化
消费 traffic-cleaned Topic，按高峰/平峰/夜间分类统计，写入 MySQL region_hourly_stats 表
"""
import os
import sys

spark_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, spark_root)

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    to_timestamp,
    date_format,
    hour,
    round,
    current_timestamp,
    when,
    sum as spark_sum,
    avg,
    max as spark_max,
    lit,
)

from spark_streaming import (
    SPARK_APP_NAME,
    SPARK_CONFIG,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_CLEANED,
    SPARK_CHECKPOINT_DIR,
    build_schema,
    foreach_batch_mysql,
)


def main():
    spark_local_dir = os.path.join(spark_root, "temp_spark")
    os.makedirs(spark_local_dir, exist_ok=True)

    spark = SparkSession.builder \
        .config("spark.local.dir", spark_local_dir) \
        .config("spark.sql.streaming.fileSink.log.enabled", "false") \
        .config("spark.sql.streaming.stateStore.stateSchemaCheck", "false") \
        .config("spark.sql.streaming.stateStore.maintenance.interval", "86400") \
        .config(
            "spark.sql.streaming.stateStore.stateStoreProviderClass",
            "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider",
        )
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
        .option("startingOffsets", "earliest")
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

    # 高峰时段流量变化统计（按区域 + 小时聚合，并标记时段类型）
    base_df = (
        parsed_df
        .filter(col("district").isNotNull() & col("timestamp").isNotNull())
        .filter(col("ts").isNotNull())
        .withColumn("stat_date", date_format(col("ts"), "yyyy-MM-dd"))
        .withColumn("stat_hour", hour(col("ts")))
        .withColumn(
            "peak_type",
            when(col("stat_hour").between(7, 9), "早高峰")
            .when(col("stat_hour").between(17, 19), "晚高峰")
            .when((col("stat_hour") >= 22) | (col("stat_hour") <= 6), "夜间")
            .otherwise("平峰"),
        )
        .withColumn("total_flow_i", col("total_flow").cast("int"))
        .withColumn("avg_speed_d", col("avg_speed").cast("double"))
        .withColumn("congestion_index_d", col("congestion_index").cast("double"))
        .withColumn("occupancy_d", col("occupancy").cast("double"))
        .filter(col("total_flow_i").isNotNull() & (col("total_flow_i") >= 0))
    )

    peak_stats_df = (
        base_df
        .groupBy("district", "stat_date", "stat_hour", "peak_type")
        .agg(
            spark_sum(col("total_flow_i")).alias("total_vehicles"),
            round(avg(col("avg_speed_d")), 2).alias("avg_speed"),
            round(avg(col("congestion_index_d")), 3).alias("avg_congestion"),
            round(spark_max(col("congestion_index_d")), 3).alias("max_congestion"),
            round(avg(col("occupancy_d")), 2).alias("avg_occupancy"),
        )
        .withColumn("update_time", current_timestamp())
    )

    # 变化指标：与上一小时对比（hour-over-hour）
    # 说明：Structured Streaming 不支持任意非时间窗口的 ordered window lag，
    # 所以这里在写入 MySQL 后，用一条 SQL 回填 delta / pct_change。
    post_sql = """
        UPDATE region_hourly_stats cur
        LEFT JOIN region_hourly_stats prev
          ON prev.district = cur.district
         AND prev.stat_date = cur.stat_date
         AND prev.stat_hour = cur.stat_hour - 1
        SET
          cur.delta_vehicles = CASE
            WHEN prev.total_vehicles IS NULL THEN NULL
            ELSE cur.total_vehicles - prev.total_vehicles
          END,
          cur.pct_change = CASE
            WHEN prev.total_vehicles IS NULL OR prev.total_vehicles = 0 THEN NULL
            ELSE ROUND((cur.total_vehicles - prev.total_vehicles) / prev.total_vehicles, 4)
          END
        WHERE cur.stat_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);
    """

    (peak_stats_df.writeStream
        .outputMode("update")
        .trigger(processingTime="30 seconds")
        .foreachBatch(
            foreach_batch_mysql(
                "region_hourly_stats",
                primary_keys=["district", "stat_date", "stat_hour"],
                post_sql=post_sql,
            )
        )
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/basic/peak_traffic")
        .start())

    print("[基础-④高峰时段] 作业启动，来源 Topic:", KAFKA_TOPIC_CLEANED)
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
