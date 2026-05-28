"""
智慧交通数据模拟器
功能：按固定间隔生成模拟交通数据，发送到 Kafka Topic traffic-raw-data
"""
import random
import json
import time
import sys
import os
from datetime import datetime

from confluent_kafka import Producer

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)
from data_generator.road_data import ROAD_DATA
from data_generator.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_RAW


def get_traffic_params(hour: int) -> dict:
    """根据时段返回基础交通参数区间"""
    if 7 <= hour <= 9:       # 早高峰
        return {"flow": (1500, 3500), "speed": (20, 40), "occupancy": (50, 70), "congestion": (0.6, 0.9)}
    elif 17 <= hour <= 19:   # 晚高峰
        return {"flow": (1800, 4000), "speed": (15, 35), "occupancy": (55, 80), "congestion": (0.7, 0.95)}
    elif hour >= 22 or hour <= 6:  # 夜间
        return {"flow": (200, 500), "speed": (60, 80), "occupancy": (10, 25), "congestion": (0.1, 0.3)}
    else:                    # 平峰
        return {"flow": (500, 1500), "speed": (40, 60), "occupancy": (25, 45), "congestion": (0.2, 0.5)}


def generate_record(detector: dict) -> dict:
    """生成单条交通记录"""
    hour = datetime.now().hour
    params = get_traffic_params(hour)

    total_flow = int(random.uniform(*params["flow"]))
    avg_speed = round(random.uniform(*params["speed"]), 1)
    occupancy = round(random.uniform(*params["occupancy"]), 1)
    congestion_index = round(random.uniform(*params["congestion"]), 3)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 约 15% 概率注入异常数据
    if random.random() < 0.15:
        anomaly = random.randint(0, 3)
        if anomaly == 0:
            detector_id_val = ""           # detector_id 为空字符串
        elif anomaly == 1:
            timestamp = ""                 # timestamp 为空字符串
        elif anomaly == 2:
            detector_id_val = None         # detector_id 为 None
        else:
            timestamp = None              # timestamp 为 None
    else:
        detector_id_val = detector["detector_id"]

    return {
        "detector_id": detector_id_val if 'detector_id_val' in dir() else detector["detector_id"],
        "detector_name": detector["detector_name"],
        "district": detector["district"],
        "timestamp": timestamp,
        "total_flow": total_flow,
        "avg_speed": avg_speed,
        "lane_count": detector["lane_count"],
        "occupancy": occupancy,
        "congestion_index": congestion_index,
        "road_type": detector["road_type"],
        "longitude": detector["longitude"],
        "latitude": detector["latitude"],
        "direction": detector["direction"],
        "data_status": 0,
    }


def main():
    print(f"[模拟器] 启动，连接 Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"[模拟器] 目标 Topic: {KAFKA_TOPIC_RAW}")

    producer = Producer({
        "bootstrap.servers": "127.0.0.1:9092",
        "acks": 1,
    })

    print(f"[模拟器] 共加载 {len(ROAD_DATA)} 个检测器，每 5 秒发送一批数据...")
    print("[模拟器] 按 Ctrl+C 停止\n")

    # metrics 文件路径
    _logs_dir = os.path.join(_PROJECT_ROOT, "flask_backend", "logs")
    os.makedirs(_logs_dir, exist_ok=True)
    _metrics_path = os.path.join(_logs_dir, "simulator_metrics.json")

    def write_metrics(total, rate):
        try:
            with open(_metrics_path, "w", encoding="utf-8") as f:
                json.dump({"total_count": total, "msg_rate": rate, "detectors": len(ROAD_DATA)}, f)
        except Exception:
            pass

    def delivery_callback(err, msg):
        if err:
            print(f"[发送失败] {err}")

    total_count = 0
    try:
        while True:
            batch = random.sample(ROAD_DATA, 50)
            ts = datetime.now().strftime("%H:%M:%S")

            for detector in batch:
                record = generate_record(detector)
                payload = json.dumps(record, ensure_ascii=False)
                producer.produce(
                    KAFKA_TOPIC_RAW,
                    key=detector["detector_id"].encode("utf-8"),
                    value=payload.encode("utf-8"),
                    callback=delivery_callback,
                )
                total_count += 1

            producer.poll(0)
            producer.flush()
            rate = len(batch) / 5
            write_metrics(total_count, rate)
            print(f"[{ts}] 发送 {len(batch)} 条数据到 {KAFKA_TOPIC_RAW}")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n[模拟器] 已停止")
        producer.flush()
        write_metrics(total_count, 0)


if __name__ == "__main__":
    main()
