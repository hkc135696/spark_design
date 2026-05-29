"""Flask 主应用入口"""
import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(backend_dir))

import threading
import time
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from flask_backend.config import Config
from flask_backend.routes import page_console, page_collection, page_cleaning, page_basic, page_advanced
from flask_backend.routes.basic import road_flow, avg_speed, congestion_index, peak_traffic, region_heat
from flask_backend.routes.advanced import (
    sliding_window, hotspot_topn, anomaly_detect,
    accident_alert, congestion_predict, region_rank, sustained_congestion,
)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# 注册蓝图
app.register_blueprint(page_console.bp)
app.register_blueprint(page_collection.bp)
app.register_blueprint(page_cleaning.bp)
app.register_blueprint(page_advanced.bp)
# 基础分析子功能（必须在 page_basic 之前注册，避免路由被覆盖）
app.register_blueprint(road_flow.bp)
app.register_blueprint(avg_speed.bp)
app.register_blueprint(congestion_index.bp)
app.register_blueprint(peak_traffic.bp)
app.register_blueprint(region_heat.bp)
app.register_blueprint(page_basic.bp)
# 进阶分析子功能
app.register_blueprint(sliding_window.bp)
app.register_blueprint(hotspot_topn.bp)
app.register_blueprint(anomaly_detect.bp)
app.register_blueprint(accident_alert.bp)
app.register_blueprint(congestion_predict.bp)
app.register_blueprint(region_rank.bp)
app.register_blueprint(sustained_congestion.bp)


@app.route("/")
def index():
    return jsonify({"message": "智慧交通实时路况监测系统 API", "version": "1.0.0"})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# ============================================================
# WebSocket 实时推送
# ============================================================

@socketio.on("connect")
def handle_connect():
    print("[WebSocket] 客户端已连接")
    emit("connected", {"status": "ok"})


@socketio.on("disconnect")
def handle_disconnect():
    print("[WebSocket] 客户端已断开")


def start_push_tasks():
    """启动定时推送任务（在独立线程中运行）"""
    from flask_backend.services.mysql_service import get_kpi, get_region_rank, get_hotspot_roads

    def push_loop():
        while True:
            try:
                # 推送 KPI
                kpi = get_kpi()
                socketio.emit("kpi_update", kpi, namespace="/")

                # 推送区域排行
                region_data = get_region_rank(10)
                road_data = get_hotspot_roads(10)
                socketio.emit("rank_update", {"region": region_data, "road": road_data}, namespace="/")

                time.sleep(30)  # 每 30 秒推送一次
            except Exception as e:
                print(f"[推送异常] {e}")
                time.sleep(10)

    t = threading.Thread(target=push_loop, daemon=True)
    t.start()


if __name__ == "__main__":
    start_push_tasks()
    print("[Flask] 启动后端服务 http://localhost:5000")
    print("[Flask] WebSocket 监听端口 5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=Config.DEBUG)
