"""基础分析 - ④ 高峰时段接口"""
from flask import Blueprint, jsonify

bp = Blueprint("basic_peak_traffic", __name__, url_prefix="/api/basic/peak-traffic")


@bp.route("/stats", methods=["GET"])
def peak_traffic_stats():
    """
    获取高峰时段统计（从 region_hourly_stats 表）
    """
    from flask_backend.services.mysql_service import query
    rows = query("""
        SELECT
            district, stat_date, stat_hour,
            total_vehicles, avg_speed, avg_congestion,
            max_congestion, avg_occupancy, peak_type, update_time
        FROM region_hourly_stats
        ORDER BY stat_date DESC, stat_hour ASC
        LIMIT 200
    """)
    return jsonify({"code": 0, "data": rows})


@bp.route("/summary", methods=["GET"])
def peak_summary():
    """
    获取高峰时段汇总
    """
    from flask_backend.services.mysql_service import query
    rows = query("""
        SELECT
            peak_type,
            COUNT(*) AS periods,
            SUM(total_vehicles) AS total_vehicles,
            ROUND(AVG(avg_congestion), 3) AS avg_congestion,
            ROUND(AVG(avg_speed), 2) AS avg_speed
        FROM region_hourly_stats
        GROUP BY peak_type
    """)
    return jsonify({"code": 0, "data": rows})
