"""
Spark 配置
"""
import os

SPARK_APP_NAME = "TrafficDataProcessor"

# Kafka 配置
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
KAFKA_TOPIC_RAW = "traffic-raw-data"
KAFKA_TOPIC_CLEANED = "traffic-cleaned"
KAFKA_TOPIC_ALERTS = "traffic-alerts"
KAFKA_TOPIC_STATS = "traffic-stats"

# MySQL 配置
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB = os.getenv("MYSQL_DB", "traffic_db")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")

MYSQL_URL = (
    f"jdbc:mysql://{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    f"?useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true"
)

# Spark 运行配置
SPARK_CONFIG = {
    "spark.app.name": SPARK_APP_NAME,
    "spark.sql.shuffle.partitions": "200",
    "spark.default.parallelism": "200",
    "spark.streaming.backpressure.enabled": "true",
    "spark.sql.adaptive.enabled": "false",
}

# checkpoint 目录（Windows 兼容，使用 file:/// URI 格式）
import pathlib as _pathlib
_checkpoint_base = _pathlib.Path(__file__).parent.parent / "checkpoints"
_checkpoint_base.mkdir(exist_ok=True)
SPARK_CHECKPOINT_DIR = _checkpoint_base.as_uri()  # e.g. file:///D:/Projects/sparkDesign/checkpoints

# 数据 Schema
TRAFFIC_SCHEMA = {
    "detector_id": "string",
    "detector_name": "string",
    "district": "string",
    "timestamp": "string",
    "total_flow": "int",
    "avg_speed": "double",
    "lane_count": "int",
    "occupancy": "double",
    "congestion_index": "double",
    "road_type": "string",
    "longitude": "double",
    "latitude": "double",
    "direction": "string",
    "data_status": "int",
}
