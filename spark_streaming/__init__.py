"""
共享 Schema 与辅助函数
"""
from .config import (
    SPARK_APP_NAME, SPARK_CONFIG, KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_RAW, KAFKA_TOPIC_CLEANED, KAFKA_TOPIC_ALERTS, KAFKA_TOPIC_STATS,
    MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD, MYSQL_URL,
    TRAFFIC_SCHEMA, SPARK_CHECKPOINT_DIR,
)


def build_schema():
    """根据 TRAFFIC_SCHEMA 构建 PySpark StructType"""
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
    fields = [
        StructField(k, StringType() if v == "string" else
                    IntegerType() if v == "int" else DoubleType(), True)
        for k, v in TRAFFIC_SCHEMA.items()
    ]
    return StructType(fields)


def foreach_batch_mysql(table_name, primary_keys=None, post_sql=None):
    """
    通用 foreachBatch 写入 MySQL 回调工厂。

    Parameters
    ----------
    table_name : str
        MySQL 目标表名
    primary_keys : list[str], optional
        联合主键列名，用于生成 REPLACE INTO 语句实现 upsert。
        如果不指定，则使用 append 模式（可能产生重复数据）。
    post_sql : str, optional
        每个 batch 写入完成后要执行的 SQL（可用于派生字段回填、修正等）。

    用法::

        (df.writeStream
            .outputMode("append")
            .trigger(processingTime="30 seconds")
            .foreachBatch(foreach_batch_mysql(
                "road_stats_realtime",
                primary_keys=["detector_id", "time_window_start"],
                post_sql="...",
            ))
            .option("checkpointLocation", ...)
            .start())
    """
    import pymysql

    def write(df, batch_id):
        if df.isEmpty():
            return
        rows = df.collect()
        if not rows:
            return

        use_replace = primary_keys is not None

        mysql_conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            charset="utf8mb4",
            autocommit=False,
        )
        try:
            with mysql_conn.cursor() as cur:
                cols = list(rows[0].asDict().keys())
                placeholders = ", ".join(["%s"] * len(cols))

                if use_replace:
                    sql = f"REPLACE INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})"
                else:
                    sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})"

                batch = [tuple(row.asDict().get(c) for c in cols) for row in rows]
                cur.executemany(sql, batch)

                if post_sql:
                    cur.execute(post_sql)

                mysql_conn.commit()
            print(f"[MySQL] Batch {batch_id} 写入 {table_name}，{len(rows)} 条")
        finally:
            mysql_conn.close()

    return write


__all__ = [
    "SPARK_APP_NAME", "SPARK_CONFIG", "KAFKA_BOOTSTRAP_SERVERS",
    "KAFKA_TOPIC_RAW", "KAFKA_TOPIC_CLEANED", "KAFKA_TOPIC_ALERTS", "KAFKA_TOPIC_STATS",
    "MYSQL_HOST", "MYSQL_PORT", "MYSQL_DB", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_URL",
    "TRAFFIC_SCHEMA", "SPARK_CHECKPOINT_DIR",
    "build_schema", "foreach_batch_mysql",
]
