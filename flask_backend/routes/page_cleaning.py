"""【页面三：数据清洗与预处理】数据清洗状态监控"""
import json
import os
from flask import Blueprint, jsonify
from flask_backend.services.job_service import is_job_alive

bp = Blueprint("page_cleaning", __name__, url_prefix="/api/cleaning")

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CLEAN_METRICS = os.path.join(_PROJECT_ROOT, "flask_backend", "logs", "cleaner_metrics.json")
_ERR_LOG = os.path.join(_PROJECT_ROOT, "flask_backend", "logs", "cleaner_errors.json")


def _read_json(path, default=None):
    if default is None:
        default = {}
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


@bp.route("/status", methods=["GET"])
def cleaning_status():
    alive = is_job_alive("cleaner")
    clean = _read_json(_CLEAN_METRICS, {
        "total_input": 0, "total_clean": 0, "total_dedup": 0,
        "last_batch_processed": 0, "last_batch_dedup": 0,
        "last_batch_id": -1,
    })

    total_input = clean.get("total_input", 0) or 0
    total_clean = clean.get("total_clean", 0) or 0
    total_dedup = clean.get("total_dedup", 0) or 0
    batch_clean = clean.get("last_batch_processed", 0) or 0

    return jsonify({
        "code": 0,
        "data": {
            "job_running": alive,
            "total_input": total_input,
            "total_clean": total_clean,
            "total_dedup": total_dedup,
            "batch_clean": batch_clean,
        }
    })


@bp.route("/errors", methods=["GET"])
def cleaning_errors():
    errors = []
    try:
        if os.path.exists(_ERR_LOG):
            with open(_ERR_LOG, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            errors.append(json.loads(line))
                        except Exception:
                            pass
    except Exception:
        pass
    return jsonify({"code": 0, "data": errors[-50:]})
