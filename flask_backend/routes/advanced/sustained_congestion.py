"""进阶分析 - ⑦ 持续拥堵检测接口（待开发）"""
from flask import Blueprint, jsonify

bp = Blueprint("advanced_sustained_congestion", __name__, url_prefix="/api/advanced/sustained-congestion")


@bp.route("/list", methods=["GET"])
def sustained_congestion_list():
    return jsonify({
        "code": 0,
        "data": [],
        "message": "此功能待开发"
    })
