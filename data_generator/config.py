"""
Kafka 连接配置
"""
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
KAFKA_TOPIC_RAW = "traffic-raw-data"
KAFKA_TOPIC_CLEANED = "traffic-cleaned"
KAFKA_TOPIC_ALERTS = "traffic-alerts"
KAFKA_TOPIC_STATS = "traffic-stats"

KAFKA_PRODUCER_CONFIG = {
    "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
    "acks": 1,
    "batch_size": 16384,
    "linger_ms": 10,
}
