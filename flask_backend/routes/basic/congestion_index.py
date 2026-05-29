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


@bp.route("/trend", methods=["GET"])
def congestion_index_trend():
    """
    获取拥堵指数变化趋势（按道路类型分组的时间序列）
    数据来源: road_stats_realtime 表（包含历史时间窗口数据）
    """
    from flask_backend.services.mysql_service import query
    rows = query("""
        SELECT
            DATE_FORMAT(time_window_start, '%H:%i') AS time_label,
            road_type,
            ROUND(AVG(avg_congestion), 3) AS avg_congestion
        FROM road_stats_realtime
        WHERE time_window_start >= DATE_SUB(NOW(), INTERVAL 60 MINUTE)
        GROUP BY time_label, road_type, time_window_start
        ORDER BY time_window_start ASC, road_type
        LIMIT 500
    """)
    return jsonify({"code": 0, "data": rows})
