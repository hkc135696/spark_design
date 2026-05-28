# 智慧交通实时路况监测与拥堵分析系统

## 新成员配置（每台机器只做一次）

### 第一步：安装软件

| 软件 | 版本要求 | 备注 |
|------|----------|------|
| **JDK** | 8 | 安装后设置 `JAVA_HOME` 环境变量 |
| **Kafka** | 任意版本 | 安装到任意路径 |
| **Spark** | 3.3.4-bin-hadoop3 | 安装到任意路径 |
| **Python** | 3.9 或 3.10 | 直接安装（非 conda），安装到任意路径 |
| **MySQL** | 8.0 | 标准安装，密码统一设为 `123456` |
| **Node.js** | 18+ | 安装后确认 `npm` 在 PATH 中 |

### 第二步：创建 `local_config.env`

在项目根目录创建 `local_config.env` 文件（此文件不提交 git），填入自己机器上的实际路径：

```ini
KAFKA_HOME=D:\kafka
SPARK_HOME=D:\spark
PYTHON_EXE=D:\Python3.9.6\python.exe
MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe
MYSQL_PASSWORD=123456
```

> 路径改成你自己机器的实际安装路径即可，名称不限。

### 第三步：下载 8 个 Spark JAR，放入 `SPARK_HOME\jars\`

在 `SPARK_HOME\jars\` 目录下执行（将 `D:\spark\jars` 替换为你的实际路径）：

```powershell
cd D:\spark\jars
curl -L -o spark-sql-kafka_2.12-3.3.4.jar "https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka_2.12/3.3.4/spark-sql-kafka_2.12-3.3.4.jar"
curl -L -o spark-token-provider-kafka_2.12-3.3.4.jar "https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka_2.12/3.3.4/spark-token-provider-kafka_2.12-3.3.4.jar"
curl -L -o kafka-clients-2.8.1.jar "https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.8.1/kafka-clients-2.8.1.jar"
curl -L -o commons-pool2-2.11.1.jar "https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar"
curl -L -o lz4-java-1.8.0.jar "https://repo1.maven.org/maven2/org/lz4/lz4-java/1.8.0/lz4-java-1.8.0.jar"
curl -L -o snappy-java-1.1.8.4.jar "https://repo1.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.8.4/snappy-java-1.1.8.4.jar"
curl -L -o slf4j-api-1.7.32.jar "https://repo1.maven.org/maven2/org/slf4j/slf4j-api/1.7.32/slf4j-api-1.7.32.jar"
curl -L -o mysql-connector-j-8.0.33.jar "https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.0.33/mysql-connector-j-8.0.33.jar"
```

### 第四步：初始化 MySQL（只做一次）

```bash
mysql -u root -p123456 < storage\init_db.sql
```

### 第五步：安装前端依赖（只做一次）

```bash
cd web_frontend && npm install
```

---

## 每次启动项目

**双击 `zhuchang_start.bat`**，自动启动 ZooKeeper、Kafka、Flask、Vue。

启动完成后，打开浏览器进入 **http://localhost:3000**，在「总控制台」点击「一键启动」，启动所有 Spark 分析作业。

---

## 创建 Kafka Topic（新机器首次运行前）

```bat
%KAFKA_HOME%\bin\windows\kafka-topics.bat --create --topic traffic-raw-data --partitions 6 --bootstrap-server localhost:9092 --replication-factor 1
%KAFKA_HOME%\bin\windows\kafka-topics.bat --create --topic traffic-cleaned --partitions 6 --bootstrap-server localhost:9092 --replication-factor 1
%KAFKA_HOME%\bin\windows\kafka-topics.bat --create --topic traffic-alerts --partitions 3 --bootstrap-server localhost:9092 --replication-factor 1
%KAFKA_HOME%\bin\windows\kafka-topics.bat --create --topic traffic-stats --partitions 3 --bootstrap-server localhost:9092 --replication-factor 1
```

---

## 分工说明

| 成员 | 负责模块 |
|------|----------|
| 黄科程 | 组长，系统架构设计、数据采集与清洗、基础流数据分析（① 实时统计道路车流量）、进阶流数据分析（② 实时 TopN 热点道路分析） |
| 解文海 | 进阶流数据分析（①滑动窗口统计、③异常车辆检测）、系统功能测试和稳定性测试 |
| 朱畅 | 基础流数据分析（⑤统计区域交通热度）、进阶流数据分析（④交通事故预警）、系统性能分析与优化 |
| 杨乐乐 | 进阶流数据分析（⑤实时路径拥堵预测、⑥实时区域拥堵排行、⑦基于状态计算的持续拥堵检测） |
| 李奕坤 | 基础流数据分析（② 实时统计平均车速、③实时计算道路拥堵指数） |
| 张钲乾 | 基础流数据分析（④统计高峰时段流量变化）、系统可视化优化 |

---

