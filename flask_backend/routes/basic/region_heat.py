"""基础分析 - ⑤ 区域热度接口"""
from flask import Blueprint, jsonify

bp = Blueprint("basic_region_heat", __name__, url_prefix="/api/basic/region-heat")


@bp.route("/rank", methods=["GET"])
def region_heat_rank():
    """
    获取区域热度排行（从 region_heat_rank 表）
    """
    from flask_backend.services.mysql_service import query
    rows = query("""
        SELECT
            district, rank_date, rank_hour,
            total_vehicles, avg_congestion, active_roads,
            avg_speed, heat_score, update_time
        FROM region_heat_rank
        ORDER BY heat_score DESC
        LIMIT 50
    """)
    return jsonify({"code": 0, "data": rows})
