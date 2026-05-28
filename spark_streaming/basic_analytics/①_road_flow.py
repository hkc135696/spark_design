"""
① 实时统计道路车流量
消费 traffic-cleaned Topic，统计各检测器的车辆总数，写入 MySQL road_stats_realtime 表
"""
import os
import sys

spark_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, spark_root)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, date_format, round as spark_round, sum as spark_sum, avg as spark_avg, max as spark_max, min as spark_min, count as spark_count, current_timestamp as spark_now

from spark_streaming import (
    SPARK_APP_NAME, SPARK_CONFIG, KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_CLEANED, MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD,
    TRAFFIC_SCHEMA, SPARK_CHECKPOINT_DIR, build_schema,
)


def main():
    spark_local_dir = os.path.join(spark_root, "temp_spark")
    os.makedirs(spark_local_dir, exist_ok=True)

    spark = SparkSession.builder \
        .config("spark.local.dir", spark_local_dir) \
        .config("spark.sql.streaming.fileSink.log.enabled", "false") \
        .config("spark.sql.streaming.stateStore.stateSchemaCheck", "false") \
        .config("spark.sql.streaming.stateStore.maintenance.interval", "86400") \
        .config("spark.sql.streaming.stateStore.stateStoreProviderClass",
                "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")
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
        .option("kafka.group.id", "spark-road-flow")
        .option("failOnDataLoss", "false")
        .load()
    )

    parsed_df = (
        cleaned_df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
    )

    road_flow_df = (
        parsed_df
        .filter(col("detector_id").isNotNull() & col("timestamp").isNotNull())
        .withColumn("ts", to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss"))
        .filter(col("ts").isNotNull())
        .withColumn("time_window_start", date_format(col("ts"), "yyyy-MM-dd HH:mm:00"))
        .withColumn("time_window_end", date_format(col("ts"), "yyyy-MM-dd HH:mm:59"))
        .groupBy("detector_id", "detector_name", "district", "road_type", "time_window_start", "time_window_end")
        .agg(
            spark_sum(col("total_flow").cast("int")).alias("total_vehicles"),
            spark_round(spark_avg(col("avg_speed").cast("double")), 2).alias("avg_speed"),
            spark_round(spark_max(col("avg_speed").cast("double")), 2).alias("max_speed"),
            spark_round(spark_min(col("avg_speed").cast("double")), 2).alias("min_speed"),
            spark_round(spark_avg(col("congestion_index").cast("double")), 3).alias("avg_congestion"),
            spark_round(spark_max(col("congestion_index").cast("double")), 3).alias("max_congestion"),
            spark_round(spark_avg(col("occupancy").cast("double")), 2).alias("avg_occupancy"),
            spark_count("*").alias("data_points"),
            spark_now().alias("update_time"),
        )
    )

    def foreach_batch_jdbc(batch_df, batch_id):
        row_count = batch_df.count()
        print(f"[DEBUG] foreachBatch called, batch_id={batch_id}, rows={row_count}")
        if row_count == 0:
            print(f"[DEBUG] Batch {batch_id} is empty, skipping")
            return
        jdbc_url = (
            f"jdbc:mysql://{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
            "?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai"
        )
        jdbc_props = {
            "driver": "com.mysql.cj.jdbc.Driver",
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "batchsize": "2000",
        }
        try:
            batch_df.write.jdbc(url=jdbc_url, table="road_stats_realtime", mode="overwrite", properties=jdbc_props)
            print(f"[MySQL] Batch {batch_id} 覆盖写入 road_stats_realtime 成功（{row_count} 条）")
        except Exception as e:
            print(f"[MySQL] Batch {batch_id} 写入失败: {e}")
            import traceback
            traceback.print_exc()

    (road_flow_df.writeStream
        .outputMode("update")
        .trigger(processingTime="30 seconds")
        .foreachBatch(foreach_batch_jdbc)
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/basic/road_flow")
        .start())

    print("[基础-①道路车流量] 作业启动，来源 Topic:", KAFKA_TOPIC_CLEANED)
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
