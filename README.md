# 智慧交通实时路况监测与拥堵分析系统

## 环境准备（运行前必读）

### 1. 确认软件环境

| 软件 | 版本要求 | 说明 |
|------|----------|------|
| **Java** | JDK 8 | Spark 和 Kafka 的运行环境，`java -version` 确认已安装 |
| **Kafka** | 2.12-3.5.1（本地安装并启动） | 消息队列，需监听 `localhost:9092` |
| **MySQL** | 8.0（本地安装并启动） | 统计结果持久化存储，需监听 `localhost:3306` |
| **Python** | 3.9+ | 模拟器、Flask 后端运行环境 |
| **Spark** | spark-3.3.4-bin-hadoop3（本地安装） | Structured Streaming 计算引擎 |
| **Node.js** | 18.x | 前端构建工具 |

> **Spark 安装路径示例**：`D:\Spark\spark-3.3.4-bin-hadoop3`。其他人在自己的 Windows 电脑上安装时，路径可能不同（如 `E:\spark-3.3.4-bin-hadoop3`），下文所有涉及 Spark 路径的地方都需要替换为自己的实际路径。

### 2. 创建 Conda 环境（推荐）

```bash
# 创建并激活环境
conda create -n spark python=3.10 -y
conda activate spark

# 安装 Python 依赖
pip install -r requirements.txt
```

### 3. 下载并配置 Spark 依赖包

#### 3.1 下载 JAR 文件

将以下 8 个 JAR 下载到 Spark 安装目录的 `jars/` 子目录下：

```powershell
curl -L -o spark-sql-kafka_2.12-3.3.4.jar "https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka_2.12/3.3.4/spark-sql-kafka_2.12-3.3.4.jar"
curl -L -o spark-token-provider-kafka_2.12-3.3.4.jar "https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka_2.12/3.3.4/spark-token-provider-kafka_2.12-3.3.4.jar"
curl -L -o kafka-clients-2.8.1.jar "https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.8.1/kafka-clients-2.8.1.jar"
curl -L -o commons-pool2-2.11.1.jar "https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar"
curl -L -o lz4-java-1.8.0.jar "https://repo1.maven.org/maven2/org/lz4/lz4-java/1.8.0/lz4-java-1.8.0.jar"
curl -L -o snappy-java-1.1.8.4.jar "https://repo1.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.8.4/snappy-java-1.1.8.4.jar"
curl -L -o slf4j-api-1.7.32.jar "https://repo1.maven.org/maven2/org/slf4j/slf4j-api/1.7.32/slf4j-api-1.7.32.jar"
curl -L -o mysql-connector-j-8.0.33.jar "https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.0.33/mysql-connector-j-8.0.33.jar"
```

#### 3.2 创建 Spark 配置文件

在 `你的spark安装目录\conf\` 目录下新建 `spark-defaults.conf` 文件（从 `spark-defaults.conf.template` 复制后改名），填入以下内容：

```properties
# ============================================================
# Spark 配置 - 智慧交通实时路况监测与拥堵分析系统
# ============================================================
# 重要：Windows 下路径必须使用正斜杠（/），不能用反斜杠（\）
# ============================================================

# Kafka Structured Source + MySQL JDBC JAR 包路径
spark.jars  file:///你的spark安装目录/jars/spark-sql-kafka_2.12-3.3.4.jar,file:///你的spark安装目录/jars/spark-token-provider-kafka_2.12-3.3.4.jar,file:///你的spark安装目录/jars/kafka-clients-2.8.1.jar,file:///你的spark安装目录/jars/commons-pool2-2.11.1.jar,file:///你的spark安装目录/jars/lz4-java-1.8.0.jar,file:///你的spark安装目录/jars/snappy-java-1.1.8.4.jar,file:///你的spark安装目录/jars/slf4j-api-1.7.32.jar,file:///你的spark安装目录/jars/mysql-connector-j-8.0.33.jar

# Python 解释器路径（必须指定为 conda spark 环境的 Python）
spark.pyspark.python        D:/anaconda3/envs/spark/python.exe
spark.pyspark.driver.python D:/anaconda3/envs/spark/python.exe

# 调试相关
spark.sql.debug.maxToStringFields  100
```

> **路径替换说明**：所有人的 Spark 安装路径、conda 环境路径都可能不同。配置文件中所有路径都需要替换为实际值。

### 4. 创建 Kafka Topic

在 Kafka 安装目录下执行（Windows 用 `.bat`，Linux/Mac 用 `.sh`），创建 4 个 Topic：

```bat
cd D:\KAFKA\kafka_2.12-3.5.1
bin\windows\kafka-topics.bat --create --topic traffic-raw-data --partitions 6 --bootstrap-server localhost:9092 --replication-factor 1
bin\windows\kafka-topics.bat --create --topic traffic-cleaned --partitions 6 --bootstrap-server localhost:9092 --replication-factor 1
bin\windows\kafka-topics.bat --create --topic traffic-alerts --partitions 3 --bootstrap-server localhost:9092 --replication-factor 1
bin\windows\kafka-topics.bat --create --topic traffic-stats --partitions 3 --bootstrap-server localhost:9092 --replication-factor 1
```

### 5. 初始化 MySQL 数据库

执行建表脚本，创建 9 张数据表：

```bash
mysql -u root -p123456 -e "source D:\Projects\sparkDesign\storage\init_db.sql"
```

`D:\Projects\sparkDesign\storage\init_db.sql` 替换为实际目录

### 6. 安装前端依赖

```bash
cd web_frontend
npm install
```

### 7. 验证环境

```bash
# 确认 Kafka 可达
netstat -an | findstr 9092

# 确认 MySQL 可达
netstat -an | findstr 3306

# 确认 Spark 可用
spark-submit --version

# 确认 Python 环境
python --version
```

## 项目启动

系统支持两种启动方式：**方式一**为可视化一键启动（推荐），**方式二**为手动终端启动（适合开发调试）。

### 方式一：可视化一键启动（推荐）

```
1. 启动 Flask 后端（终端 1）
   cd D:\Projects\sparkDesign
   python flask_backend\app.py

2. 启动前端（终端 2）
   cd web_frontend
   npm run dev

3. 打开浏览器访问 http://localhost:3000
   点击顶部导航栏「总控制台」，在页面中点击「一键启动」
```

控制台页面支持：
- 独立启动/停止每个作业（模拟器 / 数据清洗 / 基础统计 / 进阶分析）
- 一键启动全部作业
- 一键停止全部作业
- 实时显示各作业 PID 和运行状态
- 底部日志窗口输出操作记录

---

### 方式二：手动终端启动（开发调试用）

需要 5 个终端，各自运行一个模块：

```
# 终端 1 - 模拟器（发送原始数据到 Kafka）
conda activate spark
cd D:\Projects\sparkDesign
python data_generator\traffic_simulator.py

# 终端 2 - 数据清洗（消费 raw-data，清洗后写入 cleaned Topic + MySQL traffic_raw）
conda activate spark
cd D:\Projects\sparkDesign
spark-submit spark_streaming\data_cleaning\spark_cleaner.py

# 终端 3 - 基础统计分析（5 项功能）
conda activate spark
cd D:\Projects\sparkDesign
spark-submit spark_streaming\basic_analytics\①_road_flow.py

# 终端 4 - 进阶分析（已实现的功能）
conda activate spark
cd D:\Projects\sparkDesign
spark-submit spark_streaming\advanced_analytics\②_hotspot_topn.py

# 终端 5 - Flask 后端
conda activate spark
cd D:\Projects\sparkDesign
python flask_backend\app.py

# 终端 6 - 前端（可选，前端启动后即可关闭此终端）
cd web_frontend
npm run dev
```

验证各模块是否正常：
- Kafka 写入：`spark-submit` 日志中观察 `[清洗] Kafka 输出已启动`
- MySQL 写入：Flask 后端控制台无报错
- WebSocket 推送：`[推送异常]` 出现频率应逐渐降低
- 浏览器访问 `http://localhost:3000`，页面应在 30 秒内开始刷新数据
- 点击顶部导航「基础分析」，各子功能应显示对应数据

## 分工说明

每个成员领取一个或多个功能进行开发：

| 成员 | 负责模块 |
|------|----------|
| 黄科程 | 组长，系统架构设计、数据采集与清洗、基础流数据分析（① 实时统计道路车流量）、进阶流数据分析（② 实时 TopN 热点道路分析） |
| 解文海 | 进阶流数据分析（①滑动窗口统计、③异常车辆检测）、系统功能测试和稳定性测试 |
| 朱畅 | 基础流数据分析（⑤统计区域交通热度）、进阶流数据分析（④交通事故预警）、系统性能分析与优化 |
| 杨乐乐 | 进阶流数据分析（⑤实时路径拥堵预测、⑥实时区域拥堵排行、⑦基于状态计算的持续拥堵检测） |
| 李奕坤 | 基础流数据分析（② 实时统计平均车速、③实时计算道路拥堵指数） |
| 张钲乾 | 基础流数据分析（④统计高峰时段流量变化）、系统可视化优化 |

---

