"""【页面五：进阶流数据分析】汇总接口"""
from flask import Blueprint, jsonify, request
from flask_backend.services.mysql_service import (
    get_hotspot_roads, get_alerts,
    getSlidingWindowStats, getHotspotTopnList, getAnomalyDetectList,
    getAccidentAlertList, getCongestionPredictList,
    getRegionRankList, getSustainedCongestionList,
)

bp = Blueprint("page_advanced", __name__, url_prefix="/api/advanced")


@bp.route("/hotspot-roads", methods=["GET"])
def hotspot_roads():
    """TopN 热点道路"""
    limit = int(request.args.get("limit", 10))
    data = get_hotspot_roads(limit)
    return jsonify({"code": 0, "data": data})


@bp.route("/alerts", methods=["GET"])
def alerts():
    """告警列表"""
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))
    alert_type = request.args.get("alert_type") or None
    status = request.args.get("status")
    status = int(status) if status is not None else None
    data = get_alerts(page, page_size, alert_type, status)
    return jsonify({"code": 0, "data": data})


# ============================================================
# 进阶分析子功能路由
# ============================================================

@bp.route("/sliding-window/stats", methods=["GET"])
def sliding_window_stats():
    """滑动窗口统计"""
    data = getSlidingWindowStats()
    return jsonify({"code": 0, "data": data})


@bp.route("/hotspot-topn/list", methods=["GET"])
def hotspot_topn_list():
    """TopN 热点道路列表"""
    data = getHotspotTopnList()
    return jsonify({"code": 0, "data": data})


@bp.route("/anomaly-detect/list", methods=["GET"])
def anomaly_detect_list():
    """异常车辆检测列表"""
    data = getAnomalyDetectList()
    return jsonify({"code": 0, "data": data})


@bp.route("/accident-alert/list", methods=["GET"])
def accident_alert_list():
    """交通事故告警列表"""
    data = getAccidentAlertList()
    return jsonify({"code": 0, "data": data})


@bp.route("/congestion-predict/list", methods=["GET"])
def congestion_predict_list():
    """拥堵预测列表"""
    data = getCongestionPredictList()
    return jsonify({"code": 0, "data": data})


@bp.route("/region-rank/list", methods=["GET"])
def region_rank_list():
    """区域拥堵排行"""
    data = getRegionRankList()
    return jsonify({"code": 0, "data": data})


@bp.route("/sustained-congestion/list", methods=["GET"])
def sustained_congestion_list():
    """持续拥堵检测列表"""
    data = getSustainedCongestionList()
    return jsonify({"code": 0, "data": data})
