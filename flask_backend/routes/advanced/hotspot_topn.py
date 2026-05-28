"""进阶分析 - ② TopN 热点道路接口"""
from flask import Blueprint, jsonify

bp = Blueprint("advanced_hotspot_topn", __name__, url_prefix="/api/advanced/hotspot-topn")


@bp.route("/list", methods=["GET"])
def hotspot_topn_list():
    """
    获取 TopN 热点道路排行（从 hotspot_roads 表）
    """
    from flask_backend.services.mysql_service import query
    rows = query("""
        SELECT
            detector_id, detector_name, district, road_type,
            congestion_score, total_vehicles, avg_speed,
            stat_period, update_time
        FROM hotspot_roads
        ORDER BY congestion_score DESC
        LIMIT 50
    """)
    return jsonify({"code": 0, "data": rows})
