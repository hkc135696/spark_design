"""
作业管理服务
封装作业启动、停止、状态查询等通用逻辑，供 Flask 路由调用
"""
import os
import sys
import subprocess
import psutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

_SPARK_SUBMIT = os.getenv(
    "SPARK_HOME",
    r"D:\Spark\spark-3.3.4-bin-hadoop3"
) + r"\bin\spark-submit.cmd"

_JOBS = {
    "simulator": {
        "name": "模拟器",
        "script": os.path.join(PROJECT_ROOT, "..", "data_generator", "traffic_simulator.py"),
        "desc": "模拟交通数据并发送到 Kafka",
        "cmd_template": [sys.executable, "{script}"],
    },
    "cleaner": {
        "name": "数据清洗",
        "script": os.path.join(PROJECT_ROOT, "..", "spark_streaming", "data_cleaning", "spark_cleaner.py"),
        "desc": "消费 raw-data，清洗后写入 cleaned Topic + MySQL",
        "cmd_template": [_SPARK_SUBMIT, "{script}"],
    },
    "analytics_road_flow": {
        "name": "基础-道路车流量",
        "script": os.path.join(PROJECT_ROOT, "..", "spark_streaming", "basic_analytics", "①_road_flow.py"),
        "desc": "① 实时统计道路车流量",
        "cmd_template": [_SPARK_SUBMIT, "{script}"],
    },
    "analytics_avg_speed": {
        "name": "基础-平均车速",
        "script": os.path.join(PROJECT_ROOT, "..", "spark_streaming", "basic_analytics", "②_avg_speed.py"),
        "desc": "② 实时统计平均车速",
        "cmd_template": [_SPARK_SUBMIT, "{script}"],
    },
    "analytics_congestion": {
        "name": "基础-拥堵指数",
        "script": os.path.join(PROJECT_ROOT, "..", "spark_streaming", "basic_analytics", "③_congestion_index.py"),
        "desc": "③ 实时计算道路拥堵指数",
        "cmd_template": [_SPARK_SUBMIT, "{script}"],
    },
    "analytics_peak": {
        "name": "基础-高峰时段",
        "script": os.path.join(PROJECT_ROOT, "..", "spark_streaming", "basic_analytics", "④_peak_traffic.py"),
        "desc": "④ 统计高峰时段流量变化",
        "cmd_template": [_SPARK_SUBMIT, "{script}"],
    },
    "analytics_region_heat": {
        "name": "基础-区域热度",
        "script": os.path.join(PROJECT_ROOT, "..", "spark_streaming", "basic_analytics", "⑤_region_heat.py"),
        "desc": "⑤ 统计区域交通热度",
        "cmd_template": [_SPARK_SUBMIT, "{script}"],
    },
    "advanced_hotspot": {
        "name": "进阶-TopN热点",
        "script": os.path.join(PROJECT_ROOT, "..", "spark_streaming", "advanced_analytics", "②_hotspot_topn.py"),
        "desc": "② 实时 TopN 热点道路分析",
        "cmd_template": [_SPARK_SUBMIT, "{script}"],
    },
    "advanced_anomaly": {
        "name": "进阶-异常检测",
        "script": os.path.join(PROJECT_ROOT, "..", "spark_streaming", "advanced_analytics", "③_anomaly_detect.py"),
        "desc": "③ 异常车辆检测",
        "cmd_template": [_SPARK_SUBMIT, "{script}"],
    },
    "advanced_region_rank": {
        "name": "进阶-区域排行",
        "script": os.path.join(PROJECT_ROOT, "..", "spark_streaming", "advanced_analytics", "⑥_region_rank.py"),
        "desc": "⑥ 实时区域拥堵排行",
        "cmd_template": [_SPARK_SUBMIT, "{script}"],
    },
    "advanced_sliding": {
        "name": "进阶-滑动窗口",
        "script": None,
        "desc": "① 滑动窗口统计（待开发）",
        "cmd_template": [],
    },
    "advanced_accident": {
        "name": "进阶-事故预警",
        "script": None,
        "desc": "④ 交通事故预警（待开发）",
        "cmd_template": [],
    },
    "advanced_predict": {
        "name": "进阶-拥堵预测",
        "script": None,
        "desc": "⑤ 实时路径拥堵预测（待开发）",
        "cmd_template": [],
    },
    "advanced_sustained": {
        "name": "进阶-持续拥堵",
        "script": None,
        "desc": "⑦ 基于状态计算的持续拥堵检测（待开发）",
        "cmd_template": [],
    },
}


def _ensure_log_dir():
    os.makedirs(_LOG_DIR, exist_ok=True)


def _is_process_alive(proc):
    if proc is None:
        return False
    if hasattr(proc, "poll"):
        return proc.poll() is None
    return False


def _kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        parent.terminate()
        gone, alive = psutil.wait_procs(children + [parent], timeout=3)
        for p in alive:
            try:
                p.kill()
            except psutil.NoSuchProcess:
                pass
    except psutil.NoSuchProcess:
        pass
    except Exception:
        pass


def _open_log_file(job_id, mode="a"):
    _ensure_log_dir()
    log_path = os.path.join(_LOG_DIR, f"{job_id}.log")
    return open(log_path, mode, encoding="utf-8", buffering=1)


_running_processes = {}


def launch_job(job_def):
    script = job_def["script"]
    if not script:
        raise FileNotFoundError("作业脚本未实现")
    cmd = [part.replace("{script}", script) for part in job_def["cmd_template"]]
    env = os.environ.copy()
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    job_log_id = cmd[0].split(os.sep)[-1].replace(".cmd", "")
    log_file = _open_log_file(job_log_id)
    p = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        env=env,
        startupinfo=startupinfo,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
    )
    return p, log_file


def stop_job_process(pid, log_file=None):
    if log_file:
        try:
            log_file.close()
        except Exception:
            pass
    _kill_process_tree(pid)


def get_running_process(job_id):
    return _running_processes.get(job_id)


def set_running_process(job_id, entry):
    _running_processes[job_id] = entry


def is_job_alive(job_id):
    entry = _running_processes.get(job_id)
    if not entry:
        return False
    return _is_process_alive(entry.get("proc"))
