"""
Spark 配置
"""
import os
import pathlib


def _load_local_config():
    """从 local_config.env 加载路径配置到 os.environ（不覆盖已有值）"""
    here = pathlib.Path(__file__).resolve()
    env_file = next(
        (p / "local_config.env" for p in here.parents if (p / "local_config.env").exists()),
        None,
    )
    if env_file is None:
        return
    with env_file.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


_load_local_config()

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
    "spark.sql.debug.maxToStringFields": "100",
}

# ============================================================
# Spark jars 目录 — 从 SPARK_HOME 环境变量获取（由 local_config.env 注入）
# ============================================================
_JAR_NAMES = [
    "spark-sql-kafka_2.12-3.3.4.jar",
    "spark-token-provider-kafka_2.12-3.3.4.jar",
    "kafka-clients-2.8.1.jar",
    "commons-pool2-2.11.1.jar",
    "lz4-java-1.8.0.jar",
    "snappy-java-1.1.8.4.jar",
    "slf4j-api-1.7.32.jar",
    "mysql-connector-j-8.0.33.jar",
]


def _find_spark_jars_dir():
    """从 SPARK_HOME 环境变量定位 jars 目录"""
    spark_home = os.getenv("SPARK_HOME")
    if spark_home:
        d = pathlib.Path(spark_home) / "jars"
        if d.is_dir():
            return d
    print("[config] WARNING: SPARK_HOME not set or jars dir not found. Check local_config.env")
    return None


_jars_dir = _find_spark_jars_dir()
if _jars_dir:
    _found = [str(_jars_dir / j).replace("\\", "/") for j in _JAR_NAMES if (_jars_dir / j).exists()]
    _missing = [j for j in _JAR_NAMES if not (_jars_dir / j).exists()]
    if _missing:
        print(f"[config] WARNING: {len(_missing)} JAR(s) not found in {_jars_dir}: {_missing}")
    if _found:
        SPARK_JARS = ",".join(f"file:///{p}" for p in _found)
    else:
        SPARK_JARS = ""
        print(f"[config] WARNING: No JARs found in {_jars_dir}")
else:
    SPARK_JARS = ""
    print("[config] WARNING: Spark jars dir not found. Kafka/MySQL JARs will be missing.")

# checkpoint 目录（Windows 兼容，使用 file:/// URI 格式）
import pathlib as _pathlib
_checkpoint_base = _pathlib.Path(__file__).parent.parent / "checkpoints"
_checkpoint_base.mkdir(exist_ok=True)
SPARK_CHECKPOINT_DIR = _checkpoint_base.as_uri()  # e.g. file:///D:/Projects/sparkDesign/checkpoints

if SPARK_JARS:
    SPARK_CONFIG["spark.jars"] = SPARK_JARS

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
