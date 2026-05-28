"""基础分析 - ② 平均车速接口"""
from flask import Blueprint, jsonify

bp = Blueprint("basic_avg_speed", __name__, url_prefix="/api/basic/avg-speed")


@bp.route("/list", methods=["GET"])
def avg_speed_list():
    """
    获取各检测器平均车速列表（从 speed_stats 表）
    """
    from flask_backend.services.mysql_service import query
    rows = query("""
        SELECT
            detector_id, detector_name, district,
            avg_speed, speed_stddev, max_speed, min_speed,
            median_speed, data_points, update_time
        FROM speed_stats
        ORDER BY update_time DESC
        LIMIT 100
    """)
    return jsonify({"code": 0, "data": rows})
