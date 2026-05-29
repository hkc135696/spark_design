"""
③ 实时计算道路拥堵指数
消费 traffic-cleaned Topic，按复合公式计算各道路拥堵指数，写入 MySQL congestion_index 表
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
    round,
    current_timestamp,
    avg,
    sum as spark_sum,
    least,
    when,
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

    # 道路拥堵指数（复合公式：流量 * 道路系数 * 速度影响系数）
    # 说明：road_factor 使用 when 链实现（避免 streaming SQL 的解析/分组坑）
    base_df = (
        parsed_df
        .filter(col("detector_id").isNotNull() & col("timestamp").isNotNull())
        .filter(col("ts").isNotNull())
        .withColumn("total_flow_i", col("total_flow").cast("int"))
        .withColumn("avg_speed_d", col("avg_speed").cast("double"))
        .withColumn("congestion_index_d", col("congestion_index").cast("double"))
        .filter(col("total_flow_i").isNotNull() & (col("total_flow_i") >= 0))
        .filter(col("avg_speed_d").isNotNull() & (col("avg_speed_d") >= 0))
        .withColumn(
            "road_factor",
            when(col("road_type") == "高速", 0.8)
            .when(col("road_type") == "快速路", 0.85)
            .when(col("road_type") == "主干路", 1.0)
            .when(col("road_type") == "次干路", 1.2)
            .when(col("road_type") == "支路", 1.5)
            .otherwise(1.0),
        )
    )

    agg_df = (
        base_df
        .groupBy("detector_id", "detector_name", "district", "road_type")
        .agg(
            spark_sum(col("total_flow_i")).alias("total_vehicles"),
            round(avg(col("congestion_index_d")), 3).alias("raw_avg_congestion"),
            round(avg(col("avg_speed_d")), 2).alias("avg_speed"),
            avg(col("road_factor")).alias("road_factor_avg"),
        )
        .withColumn(
            "calculated_congestion",
            round(
                least(
                    col("total_vehicles") / 200.0
                    * col("road_factor_avg")
                    * (0.5 + (1 - (col("avg_speed") / 80.0)) * 0.5),
                    lit(1.0),
                ),
                3,
            ),
        )
        .withColumn("update_time", current_timestamp())
        .drop("road_factor_avg")
    )

    (agg_df.writeStream
        .outputMode("update")
        .trigger(processingTime="30 seconds")
        .foreachBatch(
            foreach_batch_mysql(
                "congestion_index",
                primary_keys=["detector_id"],
            )
        )
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/basic/congestion_index")
        .start())

    print("[基础-③拥堵指数] 作业启动，来源 Topic:", KAFKA_TOPIC_CLEANED)
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
