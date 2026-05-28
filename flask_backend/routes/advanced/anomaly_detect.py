"""进阶分析 - ③ 异常检测接口"""
from flask import Blueprint, jsonify

bp = Blueprint("advanced_anomaly_detect", __name__, url_prefix="/api/advanced/anomaly-detect")


@bp.route("/list", methods=["GET"])
def anomaly_detect_list():
    """
    获取异常检测告警列表（从 traffic_alerts 表，筛选 SPEED_ANOMALY 类型）
    """
    from flask_backend.services.mysql_service import query
    rows = query("""
        SELECT
            id, alert_type, alert_level, detector_id, detector_name,
            district, description, trigger_value, threshold_value,
            start_time, end_time, status, create_time
        FROM traffic_alerts
        WHERE alert_type = 'SPEED_ANOMALY'
        ORDER BY create_time DESC
        LIMIT 100
    """)
    return jsonify({"code": 0, "data": rows})
