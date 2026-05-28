"""【页面二：实时数据采集】数据采集状态监控"""
import os
import json
from flask import Blueprint, jsonify
from flask_backend.services.job_service import is_job_alive

bp = Blueprint("page_collection", __name__, url_prefix="/api/collection")

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_METRICS_PATH = os.path.join(_PROJECT_ROOT, "flask_backend", "logs", "simulator_metrics.json")


def _read_metrics():
    try:
        if os.path.exists(_METRICS_PATH):
            with open(_METRICS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"total_count": 0, "msg_rate": 0, "detectors": 0}


@bp.route("/status", methods=["GET"])
def collection_status():
    alive = is_job_alive("simulator")
    metrics = _read_metrics()
    return jsonify({
        "code": 0,
        "data": {
            "simulator_running": alive,
            "kafka_topic": "traffic-raw-data",
            "message_rate": metrics.get("msg_rate", 0),
            "message_count": metrics.get("total_count", 0),
            "detectors_active": metrics.get("detectors", 0) if alive else 0,
        }
    })


@bp.route("/stats", methods=["GET"])
def collection_stats():
    return jsonify({
        "code": 0,
        "data": {
            "total_sent": 0,
            "error_count": 0,
            "last_send_time": None,
        }
    })
