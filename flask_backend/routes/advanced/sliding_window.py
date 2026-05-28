"""进阶分析 - ① 滑动窗口统计接口（待开发）"""
from flask import Blueprint, jsonify

bp = Blueprint("advanced_sliding_window", __name__, url_prefix="/api/advanced/sliding-window")


@bp.route("/stats", methods=["GET"])
def sliding_window_stats():
    return jsonify({
        "code": 0,
        "data": [],
        "message": "此功能待开发"
    })
