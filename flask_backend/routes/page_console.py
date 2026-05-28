"""【页面一：总控制台】作业管理与状态监控"""
import time
from flask import Blueprint, jsonify
from flask_backend.services.job_service import (
    _JOBS, _running_processes, launch_job, stop_job_process,
    get_running_process, set_running_process, is_job_alive,
)

bp = Blueprint("page_console", __name__, url_prefix="/api/console")

_LOG_DIR = "D:\\Projects\\sparkDesign\\flask_backend\\logs"


@bp.route("/jobs", methods=["GET"])
def list_jobs():
    jobs = []
    for job_id, job_def in _JOBS.items():
        alive = is_job_alive(job_id)
        entry = get_running_process(job_id)
        proc = entry.get("proc") if entry else None
        pid = proc.pid if alive and proc else None
        jobs.append({
            "id": job_id,
            "name": job_def["name"],
            "desc": job_def["desc"],
            "status": "running" if alive else "stopped",
            "pid": pid,
            "implemented": job_def["script"] is not None,
        })
    return jsonify({"code": 0, "data": jobs})


@bp.route("/jobs/<job_id>/start", methods=["POST"])
def start_job(job_id):
    if job_id not in _JOBS:
        return jsonify({"code": 404, "message": f"未知的作业: {job_id}"}), 404

    job_def = _JOBS[job_id]
    if job_def["script"] is None:
        return jsonify({"code": 400, "message": f"{job_def['name']} 尚未实现"}), 400

    if is_job_alive(job_id):
        return jsonify({"code": 409, "message": f"{job_def['name']} 已在运行"}), 409

    try:
        p, log_file = launch_job(job_def)
        set_running_process(job_id, {"proc": p, "log_file": log_file})
        print(f"[Console] 已启动 {job_def['name']} (PID={p.pid})")
        return jsonify({
            "code": 0,
            "message": f"{job_def['name']} 已启动",
            "data": {"id": job_id, "pid": p.pid},
        })
    except FileNotFoundError as e:
        return jsonify({"code": 500, "message": f"找不到可执行文件: {e}"}), 500
    except Exception as e:
        return jsonify({"code": 500, "message": f"启动失败: {e}"}), 500


@bp.route("/jobs/<job_id>/stop", methods=["POST"])
def stop_job(job_id):
    if job_id not in _JOBS:
        return jsonify({"code": 404, "message": f"未知的作业: {job_id}"}), 404

    if not is_job_alive(job_id):
        return jsonify({"code": 409, "message": f"{_JOBS[job_id]['name']} 未在运行"}), 409

    try:
        entry = get_running_process(job_id)
        if not entry:
            return jsonify({"code": 500, "message": "进程记录丢失"}), 500
        proc = entry.get("proc")
        log_file = entry.get("log_file")
        stop_job_process(proc.pid, log_file)
        set_running_process(job_id, None)
        print(f"[Console] 已停止 {_JOBS[job_id]['name']}")
        return jsonify({"code": 0, "message": f"{_JOBS[job_id]['name']} 已停止"})
    except Exception as e:
        return jsonify({"code": 500, "message": f"停止失败: {e}"}), 500


@bp.route("/jobs/<job_id>/restart", methods=["POST"])
def restart_job(job_id):
    stop_job(job_id)
    time.sleep(1)
    return start_job(job_id)


@bp.route("/jobs/start-all", methods=["POST"])
def start_all_jobs():
    results = []
    for job_id, job_def in _JOBS.items():
        if job_def["script"] is None:
            results.append({"id": job_id, "status": "not_implemented"})
            continue
        if is_job_alive(job_id):
            results.append({"id": job_id, "status": "already_running"})
            continue
        try:
            p, log_file = launch_job(job_def)
            set_running_process(job_id, {"proc": p, "log_file": log_file})
            results.append({"id": job_id, "status": "started", "pid": p.pid})
        except Exception as e:
            results.append({"id": job_id, "status": "error", "error": str(e)})
    return jsonify({"code": 0, "message": "一键启动完成", "data": results})


@bp.route("/jobs/stop-all", methods=["POST"])
def stop_all_jobs():
    results = []
    for job_id in _JOBS:
        if not is_job_alive(job_id):
            results.append({"id": job_id, "status": "not_running"})
            continue
        try:
            entry = get_running_process(job_id)
            if entry:
                stop_job_process(entry["proc"].pid, entry.get("log_file"))
                set_running_process(job_id, None)
            results.append({"id": job_id, "status": "stopped"})
        except Exception:
            results.append({"id": job_id, "status": "error"})
    return jsonify({"code": 0, "message": "一键停止完成", "data": results})


@bp.route("/jobs/<job_id>/log", methods=["GET"])
def get_job_log(job_id):
    if job_id not in _JOBS:
        return jsonify({"code": 404, "message": "未知的作业"}), 404
    import os
    log_path = os.path.join(_LOG_DIR, f"{job_id}.log")
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return jsonify({"code": 0, "data": lines[-200:]})
    except FileNotFoundError:
        return jsonify({"code": 0, "data": []})
    except Exception as e:
        return jsonify({"code": 500, "message": f"读取日志失败: {e}"}), 500
