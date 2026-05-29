"""
MySQL 查询服务
"""
import decimal
import pymysql
from pymysql.cursors import DictCursor
from flask_backend.config import Config


def get_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset="utf8mb4",
        cursorclass=DictCursor,
    )


def _convert_decimals(obj):
    """将 dict/list 中所有 Decimal 递归转为 float（解决 JSON 序列化问题）"""
    if isinstance(obj, dict):
        return {k: _convert_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_decimals(item) for item in obj]
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    return obj


def query(sql, args=None, fetchone=False):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, args)
            result = cursor.fetchone() if fetchone else cursor.fetchall()
            return _convert_decimals(result)
    finally:
        conn.close()


def get_kpi():
    """获取全局 KPI"""
    row = query("""
        SELECT
            COALESCE(SUM(total_vehicles), 0) AS total_vehicles,
            COALESCE(ROUND(AVG(avg_speed), 1), 0) AS avg_speed,
            COALESCE(ROUND(AVG(avg_congestion), 3), 0) AS avg_congestion,
            COALESCE(MAX(max_congestion), 0) AS max_congestion
        FROM road_stats_realtime
        WHERE update_time >= DATE_SUB(NOW(), INTERVAL 10 MINUTE)
    """, fetchone=True)

    alerts = query("""
        SELECT COUNT(*) AS count
        FROM traffic_alerts
        WHERE status = 0
    """, fetchone=True)

    return {
        "total_vehicles": int(row["total_vehicles"]) if row else 0,
        "avg_speed": row["avg_speed"] or 0,
        "avg_congestion": row["avg_congestion"] or 0,
        "max_congestion": row["max_congestion"] or 0,
        "active_alerts": int(alerts["count"]) if alerts else 0,
    }


def get_trend(metric="congestion", minutes=60):
    """获取时间序列趋势数据"""
    col_map = {
        "flow": "SUM(total_vehicles)",
        "speed": "AVG(avg_speed)",
        "congestion": "AVG(avg_congestion)",
    }
    col = col_map.get(metric, "AVG(avg_congestion)")
    rows = query(f"""
        SELECT
            DATE_FORMAT(time_window_start, '%%H:%%i') AS time_label,
            {col} AS value
        FROM road_stats_realtime
        WHERE update_time >= DATE_SUB(NOW(), INTERVAL {minutes} MINUTE)
        GROUP BY DATE_FORMAT(time_window_start, '%%H:%%i'), time_window_start
        ORDER BY time_window_start ASC
        LIMIT 60
    """)
    return rows


def get_region_rank(limit=10):
    """获取区域拥堵排行"""
    return query(f"""
        SELECT
            district,
            ROUND(avg_congestion, 3) AS avg_congestion,
            total_vehicles,
            active_roads,
            heat_score,
            update_time
        FROM region_congestion_rank
        ORDER BY avg_congestion DESC
        LIMIT {limit}
    """)


def get_hotspot_roads(limit=10):
    """获取热点道路排行"""
    return query(f"""
        SELECT
            detector_id,
            detector_name,
            district,
            ROUND(congestion_score, 3) AS congestion_score,
            total_vehicles,
            avg_speed,
            stat_period
        FROM hotspot_roads
        ORDER BY congestion_score DESC
        LIMIT {limit}
    """)


def get_alerts(page=1, page_size=20, alert_type=None, status=None):
    """获取告警列表（分页）"""
    conditions = []
    args = []
    if alert_type:
        conditions.append("alert_type = %s")
        args.append(alert_type)
    if status is not None:
        conditions.append("status = %s")
        args.append(status)
    where = " AND ".join(conditions) if conditions else "1=1"

    offset = (page - 1) * page_size
    rows = query(f"""
        SELECT
            id, alert_type, alert_level, detector_id, detector_name,
            district, description, trigger_value, threshold_value,
            start_time, end_time, status, create_time
        FROM traffic_alerts
        WHERE {where}
        ORDER BY create_time DESC
        LIMIT %s OFFSET %s
    """, args + [page_size, offset])

    total_row = query(f"""
        SELECT COUNT(*) AS total FROM traffic_alerts WHERE {where}
    """, args, fetchone=True)

    return {
        "total": int(total_row["total"]) if total_row else 0,
        "page": page,
        "page_size": page_size,
        "data": rows,
    }


def get_hourly_stats(district=None, date=None):
    """获取区域小时统计"""
    conditions = []
    args = []
    if district:
        conditions.append("district = %s")
        args.append(district)
    if date:
        conditions.append("stat_date = %s")
        args.append(date)
    where = " AND ".join(conditions) if conditions else "1=1"

    return query(f"""
        SELECT
            stat_hour, total_vehicles, avg_speed, avg_congestion,
            max_congestion, peak_type
        FROM region_hourly_stats
        WHERE {where}
        ORDER BY stat_hour ASC
    """, args)


def get_heatmap_data():
    """获取热力图数据（从 traffic_raw 取最新记录及经纬度）"""
    return query("""
        SELECT
            r.detector_id,
            r.detector_name,
            r.district,
            r.longitude,
            r.latitude,
            r.congestion_index,
            r.total_flow,
            r.avg_speed
        FROM (
            SELECT detector_id, MAX(timestamp) AS max_ts
            FROM traffic_raw
            WHERE longitude IS NOT NULL AND latitude IS NOT NULL
            GROUP BY detector_id
        ) latest
        JOIN traffic_raw r ON r.detector_id = latest.detector_id
            AND r.timestamp = latest.max_ts
        LIMIT 200
    """)


def get_history(district=None, detector_id=None, start_time=None, end_time=None, page=1, page_size=50):
    """历史数据查询（分页）"""
    conditions = []
    args = []
    if district:
        conditions.append("district = %s")
        args.append(district)
    if detector_id:
        conditions.append("detector_id = %s")
        args.append(detector_id)
    if start_time:
        conditions.append("timestamp >= %s")
        args.append(start_time)
    if end_time:
        conditions.append("timestamp <= %s")
        args.append(end_time)
    where = " AND ".join(conditions) if conditions else "1=1"

    offset = (page - 1) * page_size
    rows = query(f"""
        SELECT
            detector_id, detector_name, district, timestamp,
            total_flow, avg_speed, occupancy, congestion_index,
            road_type, direction
        FROM traffic_raw
        WHERE {where}
        ORDER BY timestamp DESC
        LIMIT %s OFFSET %s
    """, args + [page_size, offset])

    total_row = query(f"""
        SELECT COUNT(*) AS total FROM traffic_raw WHERE {where}
    """, args, fetchone=True)

    return {
        "total": int(total_row["total"]) if total_row else 0,
        "page": page,
        "page_size": page_size,
        "data": rows,
    }


# ============================================================
# 基础分析子功能
# ============================================================

def getRoadFlowList():
    """道路车流量列表（最新 100 条）"""
    return query("""
        SELECT
            detector_id, detector_name, district, road_type,
            time_window_start, time_window_end,
            total_vehicles, avg_speed, max_speed, min_speed,
            avg_congestion, max_congestion, avg_occupancy,
            data_points, update_time
        FROM road_stats_realtime
        ORDER BY update_time DESC
        LIMIT 100
    """)


def getAvgSpeedList():
    """平均车速列表（最新 100 条）"""
    return query("""
        SELECT
            detector_id, detector_name, district,
            avg_speed, speed_stddev, max_speed, min_speed,
            median_speed, data_points, update_time
        FROM speed_stats
        ORDER BY update_time DESC
        LIMIT 100
    """)


def getCongestionIndexList():
    """拥堵指数列表（按计算拥堵指数降序）"""
    return query("""
        SELECT
            detector_id, detector_name, district, road_type,
            total_vehicles, raw_avg_congestion, calculated_congestion,
            avg_speed, update_time
        FROM congestion_index
        ORDER BY calculated_congestion DESC
        LIMIT 100
    """)


def getPeakTrafficStats(days=7, limit=200):
    """高峰时段统计（最近 N 天）"""
    days = int(days or 7)
    limit = int(limit or 200)
    return query(f"""
        SELECT
            district, stat_date, stat_hour,
            total_vehicles, delta_vehicles, pct_change,
            avg_speed, avg_congestion, max_congestion, avg_occupancy,
            peak_type, update_time
        FROM region_hourly_stats
        WHERE stat_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        ORDER BY stat_date DESC, stat_hour DESC
        LIMIT {limit}
    """)


def getPeakSummary():
    """高峰时段汇总（今日各区高峰统计）"""
    return query("""
        SELECT
            district,
            SUM(CASE WHEN peak_type = '早高峰' THEN total_vehicles ELSE 0 END) AS morning_peak_vehicles,
            SUM(CASE WHEN peak_type = '晚高峰' THEN total_vehicles ELSE 0 END) AS evening_peak_vehicles,
            ROUND(AVG(CASE WHEN peak_type = '早高峰' THEN avg_speed END), 2) AS morning_avg_speed,
            ROUND(AVG(CASE WHEN peak_type = '晚高峰' THEN avg_speed END), 2) AS evening_avg_speed,
            SUM(CASE WHEN peak_type = '夜间' THEN total_vehicles ELSE 0 END) AS night_vehicles
        FROM region_hourly_stats
        WHERE stat_date >= CURDATE()
        GROUP BY district
    """)


def getRegionHeatRank():
    """区域热度排行"""
    return query("""
        SELECT
            district, rank_date, rank_hour,
            total_vehicles, avg_congestion, active_roads,
            avg_speed, heat_score, update_time
        FROM region_heat_rank
        ORDER BY heat_score DESC
        LIMIT 50
    """)


# ============================================================
# 进阶分析子功能
# ============================================================

def getSlidingWindowStats():
    """滑动窗口统计（基于 road_stats_realtime 模拟）"""
    return query("""
        SELECT
            district,
            DATE_FORMAT(time_window_start, '%H:%i') AS window_time,
            SUM(total_vehicles) AS window_vehicles,
            ROUND(AVG(avg_speed), 2) AS window_avg_speed,
            ROUND(AVG(avg_congestion), 3) AS window_avg_congestion,
            COUNT(DISTINCT detector_id) AS detector_count,
            MAX(update_time) AS update_time
        FROM road_stats_realtime
        WHERE time_window_start >= DATE_SUB(NOW(), INTERVAL 2 HOUR)
        GROUP BY district, DATE_FORMAT(time_window_start, '%H:%i')
        ORDER BY window_time DESC
        LIMIT 100
    """)


def getHotspotTopnList():
    """TopN 热点道路列表"""
    return query("""
        SELECT
            detector_id, detector_name, district, road_type,
            congestion_score, total_vehicles, avg_speed,
            stat_period, update_time
        FROM hotspot_roads
        ORDER BY congestion_score DESC
        LIMIT 20
    """)


def getAnomalyDetectList():
    """异常车辆检测列表（最近告警）"""
    return query("""
        SELECT
            id, detector_id, detector_name, district,
            alert_timestamp, alert_type, alert_level,
            description, trigger_value, threshold_value,
            status, create_time
        FROM traffic_alerts
        WHERE alert_type = 'SPEED_ANOMALY'
        ORDER BY create_time DESC
        LIMIT 50
    """)


def getAccidentAlertList():
    """交通事故告警列表"""
    return query("""
        SELECT
            id, detector_id, detector_name, district,
            alert_timestamp, alert_type, alert_level,
            description, trigger_value, threshold_value,
            start_time, end_time, status, create_time
        FROM traffic_alerts
        WHERE alert_type LIKE '%ACCIDENT%'
           OR alert_type LIKE '%BLOCKED%'
           OR description LIKE '%事故%'
        ORDER BY create_time DESC
        LIMIT 50
    """)


def getCongestionPredictList():
    """拥堵预测列表（暂无预测表，返回历史趋势模拟）"""
    return query("""
        SELECT
            district,
            DATE_FORMAT(time_window_start, '%H:%i') AS predict_time,
            ROUND(AVG(avg_congestion), 3) AS predicted_congestion,
            ROUND(AVG(avg_speed), 2) AS predicted_speed,
            'EMA' AS method,
            MAX(update_time) AS update_time
        FROM road_stats_realtime
        WHERE time_window_start >= DATE_SUB(NOW(), INTERVAL 30 MINUTE)
        GROUP BY district, DATE_FORMAT(time_window_start, '%H:%i')
        ORDER BY predict_time ASC
        LIMIT 50
    """)


def getRegionRankList():
    """区域拥堵排行（进阶页面用）"""
    return query("""
        SELECT
            district,
            ROUND(avg_congestion, 3) AS avg_congestion,
            total_vehicles,
            active_roads,
            heat_score,
            update_time
        FROM region_congestion_rank
        ORDER BY heat_score DESC
        LIMIT 50
    """)


def getSustainedCongestionList():
    """持续拥堵检测列表"""
    return query("""
        SELECT
            id, detector_id, detector_name, district,
            alert_timestamp, alert_type, alert_level,
            description, trigger_value, threshold_value,
            start_time, end_time, status, create_time
        FROM traffic_alerts
        WHERE alert_type LIKE '%CONGESTION%'
           OR alert_type LIKE '%SUSTAINED%'
        ORDER BY create_time DESC
        LIMIT 50
    """)
