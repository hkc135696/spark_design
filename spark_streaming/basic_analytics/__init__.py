"""【页面四】基础流数据分析模块"""
from .①_road_flow import main as road_flow_main
from .②_avg_speed import main as avg_speed_main
from .③_congestion_index import main as congestion_index_main
from .④_peak_traffic import main as peak_traffic_main
from .⑤_region_heat import main as region_heat_main

__all__ = [
    "road_flow_main",
    "avg_speed_main",
    "congestion_index_main",
    "peak_traffic_main",
    "region_heat_main",
]
