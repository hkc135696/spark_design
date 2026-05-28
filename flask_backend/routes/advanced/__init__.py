"""进阶分析路由模块"""
from . import (
    sliding_window, hotspot_topn, anomaly_detect,
    accident_alert, congestion_predict, region_rank, sustained_congestion,
)

__all__ = [
    "sliding_window", "hotspot_topn", "anomaly_detect",
    "accident_alert", "congestion_predict", "region_rank", "sustained_congestion",
]
