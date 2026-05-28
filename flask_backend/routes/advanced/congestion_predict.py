"""进阶分析 - ⑤ 拥堵预测接口（待开发）"""
from flask import Blueprint, jsonify

bp = Blueprint("advanced_congestion_predict", __name__, url_prefix="/api/advanced/congestion-predict")


@bp.route("/list", methods=["GET"])
def congestion_predict_list():
    return jsonify({
        "code": 0,
        "data": [],
        "message": "此功能待开发"
    })
