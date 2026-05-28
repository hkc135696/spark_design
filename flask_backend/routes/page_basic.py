"""【页面四：基础流数据分析】汇总接口"""
from flask import Blueprint, jsonify, request
from flask_backend.services.mysql_service import (
    get_kpi, get_trend, get_region_rank, get_hourly_stats,
    getRoadFlowList, getAvgSpeedList, getCongestionIndexList,
    getPeakTrafficStats, getPeakSummary, getRegionHeatRank,
)

bp = Blueprint("page_basic", __name__, url_prefix="/api/basic")


@bp.route("/kpi", methods=["GET"])
def kpi():
    data = get_kpi()
    return jsonify({"code": 0, "data": data})


@bp.route("/trend", methods=["GET"])
def trend():
    """时间序列趋势数据"""
    metric = request.args.get("type", "congestion")
    minutes = int(request.args.get("minutes", 60))
    data = get_trend(metric, minutes)
    return jsonify({"code": 0, "data": data})


@bp.route("/region-rank", methods=["GET"])
def region_rank():
    """区域拥堵排行"""
    limit = int(request.args.get("limit", 10))
    data = get_region_rank(limit)
    return jsonify({"code": 0, "data": data})


@bp.route("/hourly-stats", methods=["GET"])
def hourly_stats():
    """小时统计"""
    district = request.args.get("district") or None
    date = request.args.get("date") or None
    data = get_hourly_stats(district, date)
    return jsonify({"code": 0, "data": data})


# ============================================================
# 基础分析子功能路由
# ============================================================

@bp.route("/road-flow/list", methods=["GET"])
def road_flow_list():
    """道路车流量列表"""
    data = getRoadFlowList()
    return jsonify({"code": 0, "data": data})


@bp.route("/avg-speed/list", methods=["GET"])
def avg_speed_list():
    """平均车速列表"""
    data = getAvgSpeedList()
    return jsonify({"code": 0, "data": data})


@bp.route("/congestion-index/list", methods=["GET"])
def congestion_index_list():
    """拥堵指数列表"""
    data = getCongestionIndexList()
    return jsonify({"code": 0, "data": data})


@bp.route("/peak-traffic/stats", methods=["GET"])
def peak_traffic_stats():
    """高峰时段统计"""
    data = getPeakTrafficStats()
    return jsonify({"code": 0, "data": data})


@bp.route("/peak-traffic/summary", methods=["GET"])
def peak_traffic_summary():
    """高峰时段汇总"""
    data = getPeakSummary()
    return jsonify({"code": 0, "data": data})


@bp.route("/region-heat/rank", methods=["GET"])
def region_heat_rank():
    """区域热度排行"""
    data = getRegionHeatRank()
    return jsonify({"code": 0, "data": data})
