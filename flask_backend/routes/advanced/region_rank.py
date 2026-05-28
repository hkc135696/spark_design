"""进阶分析 - ⑥ 区域拥堵排行接口"""
from flask import Blueprint, jsonify

bp = Blueprint("advanced_region_rank", __name__, url_prefix="/api/advanced/region-rank")


@bp.route("/list", methods=["GET"])
def region_rank_list():
    """
    获取区域拥堵排行（从 region_congestion_rank 表）
    """
    from flask_backend.services.mysql_service import query
    rows = query("""
        SELECT
            district, rank_date, rank_hour,
            avg_congestion, total_vehicles, avg_speed,
            active_roads, heat_score, update_time
        FROM region_congestion_rank
        ORDER BY avg_congestion DESC
        LIMIT 50
    """)
    return jsonify({"code": 0, "data": rows})
