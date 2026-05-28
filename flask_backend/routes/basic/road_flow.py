"""基础分析 - ① 道路车流量接口"""
from flask import Blueprint, jsonify

bp = Blueprint("basic_road_flow", __name__, url_prefix="/api/basic/road-flow")


@bp.route("/list", methods=["GET"])
def road_flow_list():
    """
    获取道路车流量列表（从 road_stats_realtime 表）
    """
    from flask_backend.services.mysql_service import query
    rows = query("""
        SELECT
            detector_id, detector_name, district, road_type,
            total_vehicles, avg_speed, max_speed, min_speed,
            avg_congestion, max_congestion, avg_occupancy,
            time_window_start, time_window_end, update_time
        FROM road_stats_realtime
        ORDER BY update_time DESC
        LIMIT 100
    """)
    return jsonify({"code": 0, "data": rows})
