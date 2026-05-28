"""基础分析 - ③ 拥堵指数接口"""
from flask import Blueprint, jsonify

bp = Blueprint("basic_congestion_index", __name__, url_prefix="/api/basic/congestion-index")


@bp.route("/list", methods=["GET"])
def congestion_index_list():
    """
    获取各道路拥堵指数（从 congestion_index 表）
    """
    from flask_backend.services.mysql_service import query
    rows = query("""
        SELECT
            detector_id, detector_name, district, road_type,
            total_vehicles, raw_avg_congestion, calculated_congestion,
            avg_speed, update_time
        FROM congestion_index
        ORDER BY calculated_congestion DESC
        LIMIT 100
    """)
    return jsonify({"code": 0, "data": rows})
