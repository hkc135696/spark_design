"""【页面五】进阶流数据分析模块"""
from .②_hotspot_topn import main as hotspot_topn_main
from .③_anomaly_detect import main as anomaly_detect_main
from .⑥_region_rank import main as region_rank_main

__all__ = [
    "hotspot_topn_main",
    "anomaly_detect_main",
    "region_rank_main",
]
