"""进阶分析 - ④ 事故预警接口（待开发）"""
from flask import Blueprint, jsonify

bp = Blueprint("advanced_accident_alert", __name__, url_prefix="/api/advanced/accident-alert")


@bp.route("/list", methods=["GET"])
def accident_alert_list():
    return jsonify({
        "code": 0,
        "data": [],
        "message": "此功能待开发"
    })
