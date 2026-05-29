"""
数据清洗与预处理
消费 traffic-raw-data Topic，清洗后写入 traffic-cleaned Topic + MySQL traffic_raw 表
"""
import os
import sys
import time
import json

spark_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, spark_root)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_json, struct, coalesce, current_timestamp, to_date, hour
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

from spark_streaming import (
    SPARK_APP_NAME, SPARK_CONFIG, KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_RAW, KAFKA_TOPIC_CLEANED,
    MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD, MYSQL_URL,
    TRAFFIC_SCHEMA, SPARK_CHECKPOINT_DIR,
)

from confluent_kafka import Producer


def build_schema():
    fields = [
        StructField(k, StringType() if v == "string" else
                    IntegerType() if v == "int" else DoubleType(), True)
        for k, v in TRAFFIC_SCHEMA.items()
    ]
    return StructType(fields)


def main():
    spark_local_dir = os.path.join(spark_root, "temp_spark")
    os.makedirs(spark_local_dir, exist_ok=True)

    _metrics_path = os.path.join(spark_root, "flask_backend", "logs", "cleaner_metrics.json")
    _errlog_path = os.path.join(spark_root, "flask_backend", "logs", "cleaner_errors.json")

    def write_metrics(processed, dedup, total_input, total_clean, last_batch_id, last_batch_processed, last_batch_dedup):
        try:
            with open(_metrics_path, "w", encoding="utf-8") as f:
                json.dump({
                    "total_processed": processed,
                    "total_dedup": dedup,
                    "total_input": total_input,
                    "total_clean": total_clean,
                    "last_batch_id": last_batch_id,
                    "last_batch_processed": last_batch_processed,
                    "last_batch_dedup": last_batch_dedup,
                }, f)
        except Exception as e:
            print(f"[ERROR] write_metrics FAILED: {e}")

    def append_error_log(batch_id, reason, records):
        try:
            entry = {
                "batch_id": batch_id,
                "reason": reason,
                "count": len(records),
                "examples": records[:3],
            }
            with open(_errlog_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def load_cumulative():
        try:
            # 当 Spark checkpoint 目录不存在时，强制重置进度（避免本地进度与 checkpoint 不一致）
            checkpoint_dir = SPARK_CHECKPOINT_DIR.replace("file://", "").replace("/", "\\")
            if os.path.exists(_metrics_path) and os.path.exists(checkpoint_dir):
                with open(_metrics_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return {
                    "processed": data.get("total_processed", 0) or 0,
                    "dedup": data.get("total_dedup", 0) or 0,
                    "total_input": data.get("total_input", 0) or 0,
                    "total_clean": data.get("total_clean", 0) or 0,
                    "last_batch_id": data.get("last_batch_id", -1) or -1,
                    "last_batch_processed": data.get("last_batch_processed", 0) or 0,
                    "last_batch_dedup": data.get("last_batch_dedup", 0) or 0,
                }
        except Exception:
            pass
        return {"processed": 0, "dedup": 0, "total_input": 0, "total_clean": 0, "last_batch_id": -1, "last_batch_processed": 0, "last_batch_dedup": 0}

    cumulative = load_cumulative()
    print(f"[清洗] 恢复累计进度: input={cumulative['total_input']} clean={cumulative['total_clean']} dedup={cumulative['dedup']} last_batch_id={cumulative['last_batch_id']}")

    try:
        spark = SparkSession.builder \
            .config("spark.local.dir", spark_local_dir) \
            .config("spark.sql.streaming.fileSink.log.enabled", "false") \
            .config("spark.sql.shuffle.partitions", "1") \
            .config("spark.sql.streaming.stateStore.stateSchemaCheck", "false") \
            .config("spark.sql.streaming.stateStore.maintenance.interval", "86400") \
            .config("spark.sql.streaming.stateStore.stateStoreProviderClass",
                    "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")
        for k, v in SPARK_CONFIG.items():
            spark = spark.config(k, v)
        spark = spark.getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
    except Exception as e:
        import traceback
        print(f"[错误] SparkSession 创建失败: {e}")
        traceback.print_exc()
        return

    schema = build_schema()

    try:
        raw_df = (
            spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
            .option("subscribe", KAFKA_TOPIC_RAW)
            .option("startingOffsets", "earliest")
            .option("kafka.group.id", "spark-cleaner")
            .option("failOnDataLoss", "false")
            .load()
        )
        print(f"[清洗] Kafka 消费已连接，Topic: {KAFKA_TOPIC_RAW}")
    except Exception as e:
        import traceback
        print(f"[错误] Kafka 连接失败: {e}")
        traceback.print_exc()
        return

    try:
        parsed_df = (
            raw_df.select(
                from_json(col("value").cast("string"), schema).alias("data")
            ).select("data.*")
        )
        print("[清洗] JSON 解析配置成功")
    except Exception as e:
        import traceback
        print(f"[错误] JSON 解析失败: {e}")
        traceback.print_exc()
        return

    parsed_df.createOrReplaceTempView("traffic_raw_view")

    try:
        cleaned_df = spark.sql("""
        SELECT
            COALESCE(detector_id, '') AS detector_id,
            detector_name,
            district,
            COALESCE(timestamp, '') AS timestamp,
            CASE WHEN total_flow < 0 THEN 0 ELSE total_flow END AS total_flow,
            CASE WHEN avg_speed < 0 OR avg_speed > 200 THEN 0 ELSE avg_speed END AS avg_speed,
            lane_count,
            CASE
                WHEN occupancy < 0 THEN 0
                WHEN occupancy > 100 THEN 100
                ELSE occupancy
            END AS occupancy,
            CASE
                WHEN congestion_index < 0 THEN 0.0
                WHEN congestion_index > 1 THEN 1.0
                ELSE congestion_index
            END AS congestion_index,
            road_type,
            longitude,
            latitude,
            direction,
            data_status
        FROM traffic_raw_view
    """)
        print("[清洗] 数据清洗 SQL 执行成功")
    except Exception as e:
        import traceback
        print(f"[错误] 数据清洗 SQL 执行失败: {e}")
        traceback.print_exc()
        return

    deduplicated_df = cleaned_df.dropDuplicates(["detector_id", "timestamp"])

    final_df = (
        deduplicated_df
        .withColumn("date_key", to_date(col("timestamp")))
        .withColumn("hour_key", hour(col("timestamp")))
        .withColumn("etl_time", current_timestamp())
    )

    kafka_producer = Producer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "acks": 1,
        "socket.timeout.ms": 5000,
        "socket.connection.setup.timeout.ms": 5000,
        "broker.address.family": "v4",
        "retries": 3,
    })

    def send_to_kafka(messages):
        errors = []
        delivery_errors = []
        def on_delivery(err, msg):
            if err:
                delivery_errors.append(err)
        for msg in messages:
            from datetime import date, datetime
            def json_safe(v):
                if isinstance(v, (date, datetime)):
                    return v.isoformat()
                return v
            clean_msg = {k: (json_safe(v) if k in {"date_key", "hour_key", "etl_time"} else v)
                         for k, v in msg.items() if k != "id"}
            try:
                kafka_producer.produce(
                    KAFKA_TOPIC_CLEANED,
                    key=clean_msg.get("detector_id", "").encode("utf-8"),
                    value=json.dumps(clean_msg, ensure_ascii=False, default=str).encode("utf-8"),
                    on_delivery=on_delivery,
                )
            except Exception as e:
                errors.append(str(e))
            # 定期 poll 释放回调队列，避免 "Queue full"
            if len(messages) > 100:
                kafka_producer.poll(0)
        remaining = kafka_producer.flush(timeout=30)
        if errors or delivery_errors or remaining > 0:
            print(f"[Kafka 错误] produce错误={len(errors)} delivery错误={len(delivery_errors)} 未发送={remaining}")
            for e in (errors + delivery_errors):
                print(f"  {e}")
        else:
            print(f"[Kafka] 写入成功，{len(messages)} 条消息已发送")

    def foreach_batch_fn(batch_df, batch_id):
        print(f"[清洗] foreach_batch_fn 被调用 batch_id={batch_id}")
        try:
            if batch_id <= cumulative["last_batch_id"]:
                print(f"[清洗] batch_id={batch_id} 已处理过，跳过")
                return

            raw_rows = batch_df.collect()
            raw_count = len(raw_rows)
            print(f"[清洗] batch_id={batch_id} 原始行数={raw_count}")

            dedup_count = 0
            try:
                deduped = batch_df.dropDuplicates(["detector_id", "timestamp"]).count()
                dedup_count = raw_count - deduped
            except Exception:
                pass

            records = [row.asDict() for row in raw_rows]

            # 统计并丢弃：关键字段缺失（detector_id / timestamp）
            bad_missing_key = [
                r for r in records
                if not (r.get("detector_id") and str(r.get("detector_id")).strip())
                or not (r.get("timestamp") and str(r.get("timestamp")).strip())
            ]
            if bad_missing_key:
                append_error_log(batch_id, "丢弃：detector_id 或 timestamp 为空", [
                    {"detector_id": r.get("detector_id") or "(空)", "timestamp": r.get("timestamp") or "(空)"}
                    for r in bad_missing_key
                ][:3])

            filtered_records = [
                r for r in records
                if (r.get("detector_id") and str(r.get("detector_id")).strip())
                and (r.get("timestamp") and str(r.get("timestamp")).strip())
            ]

            # 丢弃策略：坏数据直接丢弃，但保留日志。
            # 数值字段：尽量转型，失败则丢弃。
            bad_numeric = []
            cleaned_records = []
            for r in filtered_records:
                try:
                    total_flow = int(r.get("total_flow"))
                    avg_speed = float(r.get("avg_speed"))
                    occupancy = float(r.get("occupancy"))
                    congestion_index = float(r.get("congestion_index"))
                except Exception:
                    bad_numeric.append({
                        "detector_id": r.get("detector_id"),
                        "timestamp": r.get("timestamp"),
                        "total_flow": r.get("total_flow"),
                        "avg_speed": r.get("avg_speed"),
                        "occupancy": r.get("occupancy"),
                        "congestion_index": r.get("congestion_index"),
                    })
                    continue

                # 仍保留原先的“夹逼/修正”策略（但这是在数值可解析的前提下）
                r["total_flow"] = max(0, total_flow)
                r["avg_speed"] = 0.0 if avg_speed < 0 or avg_speed > 200 else avg_speed
                r["occupancy"] = 0.0 if occupancy < 0 else (100.0 if occupancy > 100 else occupancy)
                r["congestion_index"] = 0.0 if congestion_index < 0 else (1.0 if congestion_index > 1 else congestion_index)

                # 关键维度字段缺失也丢弃（不影响 schema，但会影响聚合质量）
                if not (r.get("district") and str(r.get("district")).strip()):
                    bad_numeric.append({"detector_id": r.get("detector_id"), "timestamp": r.get("timestamp"), "reason": "district 为空"})
                    continue

                cleaned_records.append(r)

            if bad_numeric:
                append_error_log(batch_id, "丢弃：数值字段无法解析或维度缺失", bad_numeric[:3])

            final_clean_count = len(cleaned_records)

            # 最终输出使用 cleaned_records
            filtered_records = cleaned_records
            filtered_count = raw_count - len(filtered_records)

            cumulative["processed"] += final_clean_count
            cumulative["dedup"] += dedup_count
            cumulative["total_input"] += raw_count
            cumulative["total_clean"] += final_clean_count
            cumulative["last_batch_id"] = batch_id
            write_metrics(
                cumulative["processed"], cumulative["dedup"],
                cumulative["total_input"], cumulative["total_clean"],
                batch_id, final_clean_count, dedup_count,
            )

            if final_clean_count == 0:
                print(f"[清洗] Batch {batch_id} 无有效数据，跳过输出")
                return

            send_to_kafka(filtered_records)

            # 用 pymysql 直接写入，避免 streaming 上下文中的 Python worker 冲突
            mysql_cols = [c for c in filtered_records[0].keys() if c != "id"]
            mysql_records = [[r.get(c) for c in mysql_cols] for r in filtered_records]
            try:
                import pymysql
                mysql_conn = pymysql.connect(
                    host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
                    password=MYSQL_PASSWORD, database=MYSQL_DB,
                    charset="utf8mb4", autocommit=False,
                )
                with mysql_conn.cursor() as mysql_cur:
                    mysql_cur.executemany(
                        f"INSERT INTO traffic_raw ({', '.join(mysql_cols)}) VALUES ({', '.join(['%s'] * len(mysql_cols))})",
                        mysql_records
                    )
                    mysql_conn.commit()
                mysql_conn.close()
            except Exception as e:
                print(f"[MySQL] Batch {batch_id} 写入失败: {e}")
                import traceback
                traceback.print_exc()

            print(f"[清洗] Batch {batch_id} 完成，原始={raw_count} 过滤={filtered_count} 去重={dedup_count} 入库={final_clean_count}")
        except Exception as e:
            import traceback
            print(f"[错误] Batch {batch_id} 处理失败: {e}")
            traceback.print_exc()

    query = (
        final_df.writeStream
        .foreachBatch(foreach_batch_fn)
        .outputMode("append")
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/cleaner")
        .trigger(processingTime="10 seconds")
        .start()
    )

    print(f"[清洗] 作业启动，监听 Kafka topic: {KAFKA_TOPIC_RAW}")
    try:
        while True:
            query.awaitTermination(30)
            if not query.isActive:
                break
    except Exception as e:
        import traceback
        print(f"[错误] Streaming 查询异常: {e}")
        traceback.print_exc()
        print("[清洗] 作业已退出，请检查 Kafka Topic 是否有数据后重新启动。")


if __name__ == "__main__":
    main()
