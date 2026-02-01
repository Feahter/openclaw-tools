#!/usr/bin/env python3
"""
OpenClaw 心跳机制 + 任务自动记录
定时检查服务状态、自动记录任务、同步待办
"""

import json
import subprocess
import time
import os
from pathlib import Path
from datetime import datetime, timedelta

# 配置
WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
TASKS_FILE = WORKSPACE / "task-board.json"
CONFIG_DIR = Path.home() / ".openclaw"
HEARTBEAT_LOG = CONFIG_DIR / "heartbeat-log.json"
SERVICES = {
    8765: "统一控制台",
    8768: "模型管理",
    8769: "任务看板",
    8770: "Token统计",
    8771: "自动化工作流"
}

def load_tasks():
    """加载任务"""
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE) as f:
                return json.load(f)
        except:
            pass
    return []

def save_tasks(tasks):
    """保存任务"""
    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def add_task(title, desc, tag="心跳"):
    """添加任务"""
    tasks = load_tasks()
    new_task = {
        "id": int(datetime.now().timestamp() * 1000) % 100000,
        "title": title,
        "desc": desc,
        "status": "todo",
        "priority": "mid",
        "tag": tag,
        "progress": 0,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat()
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task

def update_task(task_id, **kwargs):
    """更新任务"""
    tasks = load_tasks()
    for task in tasks:
        if task.get("id") == task_id:
            task.update(kwargs)
            task["updated"] = datetime.now().isoformat()
            save_tasks(tasks)
            return True
    return False

def check_services():
    """检查所有服务状态"""
    status = {}
    for port, name in SERVICES.items():
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"http://localhost:{port}/"],
                capture_output=True, timeout=5
            )
            running = result.returncode == 0
        except:
            running = False
        status[port] = {"name": name, "running": running}
    return status

def log_heartbeat(status):
    """记录心跳日志"""
    log = []
    if HEARTBEAT_LOG.exists():
        try:
            with open(HEARTBEAT_LOG) as f:
                log = json.load(f)
        except:
            pass
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "services": status,
        "all_running": all(s["running"] for s in status.values())
    }
    log.append(entry)
    
    # 只保留最近 100 条
    log = log[-100:]
    
    HEARTBEAT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(HEARTBEAT_LOG, 'w') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    
    return entry

def sync_to_taskboard():
    """同步心跳状态到任务看板"""
    status = check_services()
    
    # 记录心跳
    entry = log_heartbeat(status)
    
    # 检查是否有服务停止
    stopped = [f"{s['name']}({port})" for port, s in status.items() if not s["running"]]
    
    if stopped:
        # 检查是否已有记录
        tasks = load_tasks()
        has_record = any(
            "服务" in t.get("title", "") and 
            any(stop in t.get("title", "") for stop in stopped)
            for t in tasks if t.get("status") in ["todo", "progress"]
        )
        
        if not has_record:
            add_task(
                f"检查服务状态: {', '.join(stopped)}",
                f"心跳检测到以下服务未运行: {', '.join(stopped)}",
                tag="服务检查"
            )
    
    return status

def auto_execute_todos():
    """自动执行待办任务中的自动化相关任务"""
    tasks = load_tasks()
    
    # 找到标记为"自动化"的待办任务
    auto_tasks = [
        t for t in tasks 
        if t.get("status") in ["todo", "progress"] 
        and ("自动化" in t.get("tag", "") or "心跳" in t.get("tag", ""))
    ]
    
    results = []
    for task in auto_tasks:
        if "检查服务" in task.get("title", ""):
            # 执行服务检查
            status = sync_to_taskboard()
            if all(s["running"] for s in status.values()):
                update_task(task["id"], status="done", progress=100)
                results.append(f"✅ {task['title']} - 已完成")
            else:
                results.append(f"⚠️ {task['title']} - 仍有服务未运行")
    
    return results

def run_heartbeat():
    """运行一次心跳检查"""
    print(f"\n{'='*50}")
    print(f"🫀 心跳检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    
    # 检查服务
    status = check_services()
    print("\n服务状态:")
    all_running = True
    for port, info in status.items():
        icon = "✅" if info["running"] else "❌"
        if not info["running"]:
            all_running = False
        print(f"  {icon} {port} - {info['name']}")
    
    # 记录心跳
    entry = log_heartbeat(status)
    print(f"\n📊 心跳已记录: {'全部运行' if entry['all_running'] else '部分停止'}")
    
    # 自动执行待办
    results = auto_execute_todos()
    if results:
        print("\n🔄 自动执行结果:")
        for r in results:
            print(f"  {r}")
    
    return status

def start_heartbeat_loop(interval_minutes=30):
    """启动心跳循环"""
    print(f"\n🚀 启动心跳机制 (间隔: {interval_minutes} 分钟)")
    
    # 立即执行一次
    run_heartbeat()
    
    # 定时循环
    while True:
        time.sleep(interval_minutes * 60)
        run_heartbeat()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--loop":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            start_heartbeat_loop(interval)
        elif sys.argv[1] == "--check":
            status = check_services()
            for port, info in status.items():
                print(f"{'✅' if info['running'] else '❌'} {port}: {info['name']}")
        elif sys.argv[1] == "--log":
            # 显示心跳日志
            if HEARTBEAT_LOG.exists():
                with open(HEARTBEAT_LOG) as f:
                    log = json.load(f)
                print(f"\n最近 {len(log)} 条心跳记录:")
                for entry in log[-10:]:
                    ts = entry["timestamp"][:19]
                    status = "✅ 全部运行" if entry["all_running"] else "⚠️ 部分停止"
                    print(f"  {ts} - {status}")
            else:
                print("暂无心跳记录")
        else:
            print("用法: heartbeat.py [--check|--log|--loop [分钟]]")
    else:
        run_heartbeat()
