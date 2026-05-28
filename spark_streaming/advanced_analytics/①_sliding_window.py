"""
① 滑动窗口统计
功能：基于滑动窗口进行流式聚合统计（待开发）

TODO:
- 实现 Tumbling Window（滚动窗口）统计
- 实现 Sliding Window（滑动窗口）统计
- 实现 Session Window（会话窗口）统计
- 支持自定义窗口大小和滑动步长
"""
import os
import sys

spark_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, spark_root)


def main():
    print("[进阶-①滑动窗口] 此功能待开发，详见文件注释")
    # TODO: 实现滑动窗口统计逻辑
    # 参考其他已实现的分析作业，基于 traffic-cleaned Topic 进行滑动窗口聚合
    # 建议使用 pyspark.sql.functions.window() 实现滑动窗口
    pass


if __name__ == "__main__":
    main()
