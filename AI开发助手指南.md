# AI 开发助手指南 - 智慧交通实时路况监测系统

> 本文件面向 AI 编程助手（Claude Code / Cursor 等）。当你第一次面对这个项目时，请先完整阅读本文件，它包含了理解项目所需的一切背景知识。

---

## 一、项目基本信息

**项目名称**: 智慧交通实时路况监测与拥堵分析系统
**技术栈**: Python + Kafka + Spark Structured Streaming + MySQL + Flask + Vue 3
**工作目录**: `D:\Projects\sparkDesign`
**负责人**: 请在此处填写你的名字

**外部依赖服务**（必须先启动）:
- **Kafka**: `127.0.0.1:9092`（Kafka 3.5.1）
- **MySQL**: `127.0.0.1:3306`，数据库 `traffic_db`，用户 `root`，密码 `123456`
- **Java**: Spark 3.3.4 需要 JDK 8 或 11
- **Spark**: `D:\Spark\spark-3.3.4-bin-hadoop3`

---

## 二、系统架构（速览）

```
Python 模拟器
(traffic_simulator.py)
        ↓ 生产
Kafka topic: traffic-raw-data (6 分区)
        ↓ 消费
Spark 清洗作业
(spark_cleaner.py)
        ↓ 写入
    ① MySQL: traffic_raw 表
    ② Kafka topic: traffic-cleaned (6 分区)
        ↓ 消费（多个作业并行）
┌──────────────────────────────────────────────┐
│  5 个基础分析作业（Spark）                    │
│  road_flow / avg_speed / congestion_index    │
│  peak_traffic / region_heat                 │
│  (30 秒触发，各写 MySQL 对应表)              │
├──────────────────────────────────────────────┤
│  4 个进阶分析作业（Spark，已实现）           │
│  hotspot_topn / anomaly_detect / region_rank │
│  (30 秒触发)                                │
└──────────────────────────────────────────────┘
        ↓ 查询
Flask 后端 (端口 5000)
REST API + WebSocket（30 秒推送一次）
        ↓
Vue 3 前端 (ECharts 图表)
```

---

## 三、关键配置文件位置

所有配置集中在以下文件中，修改配置只需改这些文件：

| 配置内容 | 文件路径 |
|---------|---------|
| Spark / Kafka / MySQL 连接配置 | `spark_streaming/config.py` |
| Kafka Topic 名称 / 生产者配置 | `data_generator/config.py` |
| Flask MySQL 连接 / Secret Key | `flask_backend/config.py` |
| MySQL 建表语句 | `storage/init_db.sql` |
| Python 依赖 | `requirements.txt` |

**重要**: Kafka Bootstrap Server 在所有配置中统一为 `127.0.0.1:9092`，MySQL Host 统一为 `127.0.0.1`。如果服务不在本机，请修改以上 3 个 config.py 中的对应地址。

---

## 四、启动顺序（推荐：通过 Web 界面一键启动）

### 前置条件：确保 Kafka 和 MySQL 已运行

### 步骤 1：启动 Flask 后端
```powershell
python flask_backend\app.py
```
访问 `http://localhost:5000` 打开 Web 控制台。

### 步骤 2：启动前端（如果前后端分离）
```powershell
cd web_frontend
npm install
npm run dev
```

### 步骤 3：通过 Web 界面启动作业（推荐）

打开浏览器访问 `http://localhost:5000`，进入 **总控制台页面**，点击以下按钮：

- **一键启动** — 启动所有作业（模拟器 + 清洗 + 所有分析作业）
- 或者单独启动某个作业 — 点击对应作业行的「启动」按钮

正常情况下，各作业会在控制台页面显示为「运行中」状态。

### 步骤 4（备选）：手动终端启动

如果 Web 界面无法使用，可通过终端手动启动（需按以下顺序）：

#### 步骤 4.1：启动数据模拟器
```powershell
python data_generator\traffic_simulator.py
```
每 5 秒向 Kafka 生产约 50 条模拟数据。正常输出：
```
[采集] 生成 50 条模拟数据
[采集] 消息已发送至 Kafka
```

#### 步骤 4.2：启动数据清洗作业（等模拟器稳定后，约 30 秒）
```powershell
python spark_streaming\data_cleaning\spark_cleaner.py
```
正常输出：
```
[清洗] Kafka 消费已连接，Topic: traffic-raw-data
[清洗] JSON 解析配置成功
[清洗] 数据清洗 SQL 执行成功
[清洗] 作业启动，监听 Kafka topic: traffic-raw-data
```
10 秒触发一次。完成后会看到：
```
[Kafka] 写入成功，XXXXX 条消息已发送
[清洗] Batch X 完成，原始=XXXXX 过滤=XX 去重=0 入库=XXXXX
```

#### 步骤 4.3：启动分析作业（等清洗作业稳定后，再开新终端）
```powershell
spark-submit spark_streaming\basic_analytics\①_road_flow.py
spark-submit spark_streaming\basic_analytics\②_avg_speed.py
spark-submit spark_streaming\basic_analytics\③_congestion_index.py
spark-submit spark_streaming\basic_analytics\④_peak_traffic.py
spark-submit spark_streaming\basic_analytics\⑤_region_heat.py
spark-submit spark_streaming\advanced_analytics\②_hotspot_topn.py
spark-submit spark_streaming\advanced_analytics\③_anomaly_detect.py
spark-submit spark_streaming\advanced_analytics\⑥_region_rank.py
```
每个作业 30 秒触发一次。正常输出：
```
[基础-①道路车流量] 作业启动，来源 Topic: traffic-cleaned
[DEBUG] foreachBatch called, batch_id=0, rows=XXXX
[MySQL] Batch 0 覆盖写入 road_stats_realtime 成功（XXXX 条）
```

---

## 五、修改代码后的重启流程

**每次修改 Spark 作业代码后**（清洗逻辑 / 分析逻辑 / 状态管理），必须执行以下步骤，否则会报 HDFSBackedStateStore delta 文件丢失错误：

### 5.1 删除 checkpoint（强制从头开始，规避 Windows 文件系统 bug）

```powershell
Remove-Item -Recurse -Force "D:\Projects\sparkDesign\checkpoints\cleaner"
Remove-Item -Recurse -Force "D:\Projects\sparkDesign\checkpoints\basic"
Remove-Item -Recurse -Force "D:\Projects\sparkDesign\checkpoints\advanced"
```

### 5.2 重置 Kafka Consumer Group Offset

```powershell
D:\KAFKA\kafka_2.12-3.5.1\bin\windows\kafka-consumer-groups.bat --bootstrap-server 127.0.0.1:9092 --group spark-cleaner --reset-offsets --to-earliest --topic traffic-raw-data --execute

D:\KAFKA\kafka_2.12-3.5.1\bin\windows\kafka-consumer-groups.bat --bootstrap-server 127.0.0.1:9092 --group spark-road-flow --reset-offsets --to-earliest --topic traffic-cleaned --execute
```

> 注意：每个 Spark 分析作业使用不同的 consumer group。如果修改了某个作业的 group id 配置，需要单独重置对应 group 的 offset。

### 5.3 重新启动所有作业

按"四、启动顺序"重新执行步骤 1-5。

---

## 六、每个文件是做什么的（速查）

### 数据模拟层
| 文件 | 作用 |
|------|------|
| `data_generator/traffic_simulator.py` | 主程序，每 5 秒随机选 50 个检测器生成数据，推送 Kafka |
| `data_generator/road_data.py` | 105 个检测器的基础信息（北京 10 个区） |
| `data_generator/config.py` | Kafka 连接配置 |

### Spark 清洗层
| 文件 | 作用 |
|------|------|
| `spark_streaming/config.py` | 共享配置：Spark / Kafka / MySQL / Schema / Checkpoint 目录 |
| `spark_streaming/__init__.py` | 共享工具：`build_schema()` / `foreach_batch_mysql()` |
| `spark_streaming/data_cleaning/spark_cleaner.py` | 清洗作业：JSON 解析 → 过滤空值/异常 → 去重 → MySQL + Kafka 双输出 |

### Spark 分析层
| 文件 | 作用 |
|------|------|
| `spark_streaming/basic_analytics/①_road_flow.py` | 按检测器 + 1 分钟窗口聚合车流量，写入 `road_stats_realtime` |
| `spark_streaming/basic_analytics/②_avg_speed.py` | 按检测器聚合速度统计（含中位数），写入 `speed_stats` |
| `spark_streaming/basic_analytics/③_congestion_index.py` | 复合公式计算拥堵指数，写入 `congestion_index` |
| `spark_streaming/basic_analytics/④_peak_traffic.py` | 按区域 + 小时聚合，高峰分类，写入 `region_hourly_stats` |
| `spark_streaming/basic_analytics/⑤_region_heat.py` | 综合热度评分，写入 `region_heat_rank` |
| `spark_streaming/advanced_analytics/②_hotspot_topn.py` | Top10 热点道路（窗口函数），写入 `hotspot_roads` |
| `spark_streaming/advanced_analytics/③_anomaly_detect.py` | Z-Score 速度异常检测，写入 `traffic_alerts` + `traffic-alerts` Topic |
| `spark_streaming/advanced_analytics/⑥_region_rank.py` | 区域拥堵排行，写入 `region_congestion_rank` |

### 后端服务层
| 文件 | 作用 |
|------|------|
| `flask_backend/app.py` | 主入口，注册所有 Blueprint，启动 WebSocket 推送 |
| `flask_backend/config.py` | Flask MySQL 连接配置 |
| `flask_backend/services/job_service.py` | 作业管理：启动/停止/重启 13 个作业进程 |
| `flask_backend/services/mysql_service.py` | 所有 MySQL 查询函数 |
| `flask_backend/routes/page_*.py` | 5 个页面级 API |
| `flask_backend/routes/basic/*.py` | 5 个基础分析子功能 API |
| `flask_backend/routes/advanced/*.py` | 7 个进阶分析子功能 API |

### MySQL 表（9 张）
`traffic_raw` / `road_stats_realtime` / `speed_stats` / `congestion_index` / `region_hourly_stats` / `region_heat_rank` / `hotspot_roads` / `region_congestion_rank` / `traffic_alerts`

---

## 七、编写新 Spark 作业的标准模板

当你需要新增一个分析作业时，按以下结构编写：

```python
import os
import sys

spark_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, spark_root)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, ...

from spark_streaming import (
    SPARK_APP_NAME, SPARK_CONFIG, KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_CLEANED,
    MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD,
    TRAFFIC_SCHEMA, SPARK_CHECKPOINT_DIR, build_schema, foreach_batch_mysql,
)


def main():
    spark_local_dir = os.path.join(spark_root, "temp_spark")
    os.makedirs(spark_local_dir, exist_ok=True)

    # ★ 必须包含以下配置（避免 Windows HDFS 文件系统 bug）★
    spark = SparkSession.builder \
        .config("spark.local.dir", spark_local_dir) \
        .config("spark.sql.streaming.fileSink.log.enabled", "false") \
        .config("spark.sql.streaming.stateStore.stateSchemaCheck", "false") \
        .config("spark.sql.streaming.stateStore.stateStoreProviderClass",
                "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")

    for k, v in SPARK_CONFIG.items():
        spark = spark.config(k, v)
    spark = spark.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    schema = build_schema()

    # 消费 Kafka cleaned topic
    df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPIC_CLEANED)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .load()
    )

    parsed = df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")

    # ★ 业务逻辑在这里实现 ★
    result_df = parsed.groupBy(...).agg(...)

    # ★ MySQL 写入（upsert via REPLACE INTO）★
    write_fn = foreach_batch_mysql("your_table_name", primary_keys=["col1", "col2"])

    (result_df.writeStream
        .outputMode("update")
        .trigger(processingTime="30 seconds")
        .foreachBatch(write_fn)
        .option("checkpointLocation", SPARK_CHECKPOINT_DIR + "/your/checkpoint/path")
        .start())

    print("[你的作业名] 作业启动，来源 Topic:", KAFKA_TOPIC_CLEANED)
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
```

然后：
1. 在 `flask_backend/routes/advanced/` 创建对应的 API 路由
2. 在 `flask_backend/services/mysql_service.py` 添加查询函数
3. 在 `flask_backend/app.py` 注册 Blueprint
4. 在 `flask_backend/services/job_service.py` 的 `_JOBS` 字典添加作业条目

---

## 八、常见错误与解决

| 错误信息 | 原因 | 解决方法 |
|---------|------|---------|
| `NameError: name 'MYSQL_HOST' is not defined` | 常量未从 spark_streaming 导入 | 在 import 语句中添加缺少的常量名 |
| `Local: Queue full` | Kafka Producer 回调队列堆积 | 在 produce 循环内加 `producer.poll(0)` |
| `Error reading delta file ... does not exist` | Windows HDFS 文件系统竞争 bug | 改用 `RocksDBStateStoreProvider`（见上方模板） |
| `Consumer group has no active members` | Spark 作业进程已退出 | 查看终端日志定位具体错误 |
| `Table doesn't exist` | MySQL 表未创建 | 执行 `storage/init_db.sql` |

---

## 九、验证系统是否正常

**Kafka 消费进度检查**（LAG 应逐渐变为 0）:
```powershell
D:\KAFKA\kafka_2.12-3.5.1\bin\windows\kafka-consumer-groups.bat --bootstrap-server 127.0.0.1:9092 --all-groups --describe
```

**MySQL 数据检查**:
```sql
SELECT COUNT(*) FROM traffic_cleaned;
SELECT COUNT(*) FROM road_stats_realtime;
SELECT COUNT(*) FROM traffic_alerts;
```

**Web 前端**: 访问 `http://localhost:5000`，查看图表是否有数据更新。

**日志文件**:
- 清洗作业指标: `flask_backend/logs/cleaner_metrics.json`
- 清洗作业错误: `flask_backend/logs/cleaner_errors.json`
- Spark 作业日志: `flask_backend/logs/spark-submit.log`
- Python 全局日志: `flask_backend/logs/python.exe.log`

---

## 十、重要注意事项

1. **所有 Spark 作业必须分开终端运行**，不要在同一个终端里同时跑多个 spark-submit
2. **Kafka Topic 分区数为 6**，多个作业可以并行消费同一 topic 而不丢数据
3. **MySQL upsert 使用 `REPLACE INTO`**，相当于先 DELETE 再 INSERT，确保主键唯一
4. **Checkpoint 目录按作业名分开**：`cleaner/` / `basic/` / `advanced/`，修改某个作业不影响其他作业
5. **Spark UI**: 作业启动后访问 `http://localhost:4041`（或 4042/4043...），查看 Structured Streaming tab 可看到每个 batch 的处理情况
6. **Kafka 积压数据**：如果模拟器长时间运行后停止，数据会积压在 Kafka 中。重启后 Spark 会继续消费积压数据，LAG 会逐渐变为 0。
