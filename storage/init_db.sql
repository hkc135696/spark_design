-- ============================================================
-- 智慧交通实时路况监测与拥堵分析系统 - MySQL 建表脚本
-- 数据库: traffic_db
-- ============================================================

CREATE DATABASE IF NOT EXISTS traffic_db DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
USE traffic_db;

-- ============================================================
-- 1. 原始数据备份表
-- ============================================================
DROP TABLE IF EXISTS traffic_raw;
CREATE TABLE traffic_raw (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    detector_id VARCHAR(20) NOT NULL COMMENT '检测器编号',
    detector_name VARCHAR(100) COMMENT '检测器名称',
    district VARCHAR(30) COMMENT '所属行政区',
    timestamp DATETIME NOT NULL COMMENT '数据采集时间',
    total_flow INT DEFAULT 0 COMMENT '小时车流量（辆/小时）',
    avg_speed DECIMAL(5,2) DEFAULT 0 COMMENT '平均车速(km/h)',
    lane_count INT DEFAULT 0 COMMENT '车道数量',
    occupancy DECIMAL(5,2) DEFAULT 0 COMMENT '车道占用率(%)',
    congestion_index DECIMAL(4,3) DEFAULT 0 COMMENT '拥堵指数(0-1)',
    road_type VARCHAR(20) COMMENT '道路等级',
    direction VARCHAR(10) COMMENT '交通流向',
    longitude DECIMAL(10,6) COMMENT '经度',
    latitude DECIMAL(10,6) COMMENT '纬度',
    data_status TINYINT DEFAULT 0 COMMENT '数据状态:0正常 1丢失 2无效 3估计',
    date_key DATE COMMENT '日期分区键',
    hour_key TINYINT COMMENT '小时分区键',
    etl_time DATETIME COMMENT 'ETL处理时间',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
    INDEX idx_detector_id (detector_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_district (district),
    INDEX idx_district_time (district, timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='原始交通数据备份表';

-- ============================================================
-- 2. 实时道路统计表（5分钟滚动窗口）
-- ============================================================
DROP TABLE IF EXISTS road_stats_realtime;
CREATE TABLE road_stats_realtime (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    detector_id VARCHAR(20) NOT NULL COMMENT '检测器编号',
    detector_name VARCHAR(100) COMMENT '检测器名称',
    district VARCHAR(30) COMMENT '所属行政区',
    road_type VARCHAR(20) COMMENT '道路等级',
    time_window_start DATETIME NOT NULL COMMENT '统计窗口开始时间',
    time_window_end DATETIME NOT NULL COMMENT '统计窗口结束时间',
    total_vehicles BIGINT DEFAULT 0 COMMENT '窗口内总车流量',
    avg_speed DECIMAL(5,2) DEFAULT 0 COMMENT '平均车速',
    max_speed DECIMAL(5,2) DEFAULT 0 COMMENT '最大车速',
    min_speed DECIMAL(5,2) DEFAULT 0 COMMENT '最小车速',
    avg_congestion DECIMAL(4,3) DEFAULT 0 COMMENT '平均拥堵指数',
    max_congestion DECIMAL(4,3) DEFAULT 0 COMMENT '最大拥堵指数',
    avg_occupancy DECIMAL(5,2) DEFAULT 0 COMMENT '平均占用率',
    data_points INT DEFAULT 0 COMMENT '窗口内数据点数',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_detector_window (detector_id, time_window_start),
    INDEX idx_district (district),
    INDEX idx_window (time_window_start, time_window_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实时道路统计表';

-- ============================================================
-- 3. 区域拥堵排行表
-- ============================================================
DROP TABLE IF EXISTS region_congestion_rank;
CREATE TABLE region_congestion_rank (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    district VARCHAR(30) NOT NULL COMMENT '区域名称',
    rank_date DATE NOT NULL COMMENT '统计日期',
    rank_hour TINYINT COMMENT '统计小时(0-23)',
    avg_congestion DECIMAL(4,3) DEFAULT 0 COMMENT '平均拥堵指数',
    total_vehicles BIGINT DEFAULT 0 COMMENT '总车流量',
    avg_speed DECIMAL(5,2) DEFAULT 0 COMMENT '平均车速',
    active_roads INT DEFAULT 0 COMMENT '活跃道路数',
    heat_score DECIMAL(6,3) COMMENT '综合热度得分',
    rank_position INT COMMENT '排行名次',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_district_time (district, rank_date, rank_hour),
    INDEX idx_rank_date (rank_date),
    INDEX idx_heat_score (heat_score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='区域拥堵排行表';

-- ============================================================
-- 4. 区域热度排行表（独立表，避免与区域拥堵排行竞争写入）
-- ============================================================
DROP TABLE IF EXISTS region_heat_rank;
CREATE TABLE region_heat_rank (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    district VARCHAR(30) NOT NULL COMMENT '区域名称',
    rank_date DATE NOT NULL COMMENT '统计日期',
    rank_hour TINYINT COMMENT '统计小时(0-23)',
    total_vehicles BIGINT DEFAULT 0 COMMENT '总车流量',
    avg_congestion DECIMAL(4,3) DEFAULT 0 COMMENT '平均拥堵指数',
    active_roads INT DEFAULT 0 COMMENT '活跃道路数',
    avg_speed DECIMAL(5,2) DEFAULT 0 COMMENT '平均车速',
    heat_score DECIMAL(6,3) COMMENT '综合热度得分',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_district_time (district, rank_date, rank_hour),
    INDEX idx_rank_date (rank_date),
    INDEX idx_heat_score (heat_score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='区域热度排行表';

-- ============================================================
-- 5. 热点道路排行表
-- ============================================================
DROP TABLE IF EXISTS hotspot_roads;
CREATE TABLE hotspot_roads (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    detector_id VARCHAR(20) NOT NULL COMMENT '检测器编号',
    detector_name VARCHAR(100) COMMENT '检测器名称',
    district VARCHAR(30) COMMENT '所属行政区',
    road_type VARCHAR(20) COMMENT '道路等级',
    congestion_score DECIMAL(4,3) DEFAULT 0 COMMENT '拥堵评分',
    total_vehicles BIGINT DEFAULT 0 COMMENT '统计周期内总流量',
    avg_speed DECIMAL(5,2) DEFAULT 0 COMMENT '平均车速',
    stat_period VARCHAR(30) COMMENT '统计周期标识',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_detector_period (detector_id, stat_period),
    INDEX idx_score (congestion_score DESC),
    INDEX idx_detector_id (detector_id),
    INDEX idx_period (stat_period)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='热点道路排行表';

-- ============================================================
-- 6. 速度统计表
-- ============================================================
DROP TABLE IF EXISTS speed_stats;
CREATE TABLE speed_stats (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    detector_id VARCHAR(20) NOT NULL COMMENT '检测器编号',
    detector_name VARCHAR(100) COMMENT '检测器名称',
    district VARCHAR(30) COMMENT '所属行政区',
    avg_speed DECIMAL(5,2) DEFAULT 0 COMMENT '平均车速',
    speed_stddev DECIMAL(5,2) DEFAULT 0 COMMENT '速度标准差',
    max_speed DECIMAL(5,2) DEFAULT 0 COMMENT '最高车速',
    min_speed DECIMAL(5,2) DEFAULT 0 COMMENT '最低车速',
    median_speed DECIMAL(5,2) DEFAULT 0 COMMENT '中位数车速',
    data_points INT DEFAULT 0 COMMENT '统计周期内数据点数',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_detector (detector_id),
    INDEX idx_district (district)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='道路速度统计表';

-- ============================================================
-- 7. 拥堵指数明细表
-- ============================================================
DROP TABLE IF EXISTS congestion_index;
CREATE TABLE congestion_index (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    detector_id VARCHAR(20) NOT NULL COMMENT '检测器编号',
    detector_name VARCHAR(100) COMMENT '检测器名称',
    district VARCHAR(30) COMMENT '所属行政区',
    road_type VARCHAR(20) COMMENT '道路等级',
    total_vehicles BIGINT DEFAULT 0 COMMENT '统计周期总流量',
    raw_avg_congestion DECIMAL(4,3) DEFAULT 0 COMMENT '原始拥堵指数均值',
    calculated_congestion DECIMAL(4,3) DEFAULT 0 COMMENT '计算后拥堵指数',
    avg_speed DECIMAL(5,2) DEFAULT 0 COMMENT '平均车速',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_detector (detector_id),
    INDEX idx_district (district),
    INDEX idx_congestion (calculated_congestion DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='道路拥堵指数明细表';

-- ============================================================
-- 8. 告警事件记录表
-- ============================================================
DROP TABLE IF EXISTS traffic_alerts;
CREATE TABLE traffic_alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    alert_type VARCHAR(30) NOT NULL COMMENT '告警类型:SPEED_ANOMALY/CONGESTION/ACCIDENT/BLOCKED',
    detector_id VARCHAR(20) COMMENT '关联检测器编号',
    detector_name VARCHAR(100) COMMENT '关联检测器名称',
    district VARCHAR(30) COMMENT '所属行政区',
    alert_timestamp DATETIME COMMENT '告警发生时间',
    alert_level TINYINT NOT NULL COMMENT '告警等级:1-提醒 2-警告 3-严重',
    description TEXT COMMENT '告警描述',
    trigger_value DECIMAL(5,2) COMMENT '触发值',
    threshold_value DECIMAL(5,2) COMMENT '阈值',
    start_time DATETIME NOT NULL COMMENT '告警开始时间',
    end_time DATETIME COMMENT '告警解除时间',
    status TINYINT DEFAULT 0 COMMENT '状态:0-活跃 1-已处理 2-已解除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_type_time (alert_type, create_time),
    INDEX idx_status (status),
    INDEX idx_detector (detector_id),
    INDEX idx_start_time (start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交通告警事件记录表';

-- ============================================================
-- 9. 区域小时统计表
-- ============================================================
DROP TABLE IF EXISTS region_hourly_stats;
CREATE TABLE region_hourly_stats (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    district VARCHAR(30) NOT NULL COMMENT '区域名称',
    stat_date DATE NOT NULL COMMENT '统计日期',
    stat_hour TINYINT NOT NULL COMMENT '统计小时(0-23)',
    total_vehicles BIGINT DEFAULT 0 COMMENT '小时总车流量',
    avg_speed DECIMAL(5,2) DEFAULT 0 COMMENT '小时平均车速',
    avg_congestion DECIMAL(4,3) DEFAULT 0 COMMENT '小时平均拥堵指数',
    max_congestion DECIMAL(4,3) DEFAULT 0 COMMENT '小时最大拥堵指数',
    avg_occupancy DECIMAL(5,2) DEFAULT 0 COMMENT '小时平均占用率',
    peak_type VARCHAR(10) COMMENT '时段类型:早高峰/晚高峰/平峰/夜间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_district_hour (district, stat_date, stat_hour),
    INDEX idx_date (stat_date),
    INDEX idx_hour (stat_hour)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='区域小时统计汇总表';
