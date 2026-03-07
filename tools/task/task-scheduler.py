#!/usr/bin/env python3
"""
OpenClaw 自动化任务调度器
基于 Minimax 套餐周期自动调度任务
"""

import subprocess
import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta

# 配置
CONFIG_DIR = Path.home() / ".api-keys"
TASK_QUEUE_FILE = CONFIG_DIR / "task-queue.json"
LOG_FILE = CONFIG_DIR / "automation.log"
CYCLE_HOURS = 5  # 5小时周期

def get_current_cycle():
    """获取当前周期信息"""
    now = datetime.now()
    hour = now.hour
    
    # 周期: 10:00-15:00, 15:00-20:00, 20:00-01:00, 01:00-06:00, 06:00-10:00
    if 10 <= hour < 15:
        start = now.replace(hour=10, minute=0, second=0, microsecond=0)
        end = now.replace(hour=15, minute=0, second=0, microsecond=0)
    elif 15 <= hour < 20:
        start = now.replace(hour=15, minute=0, second=0, microsecond=0)
        end = now.replace(hour=20, minute=0, second=0, microsecond=0)
    elif 20 <= hour < 24:
        start = now.replace(hour=20, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    elif 0 <= hour < 6:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=5, minute=59, second=59, microsecond=0)
    else:
        start = now.replace(hour=6, minute=0, second=0, microsecond=0)
        end = now.replace(hour=10, minute=0, second=0, microsecond=0)
    
    remaining = (end - now).total_seconds()
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "remaining_seconds": remaining,
        "remaining_minutes": round(remaining / 60, 1)
    }

def load_task_queue():
    """加载任务队列"""
    if TASK_QUEUE_FILE.exists():
        try:
            with open(TASK_QUEUE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"tasks": [], "last_run": None, "total_runs": 0}

def save_task_queue(queue):
    """保存任务队列"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(TASK_QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

def add_task(name, command, priority="normal", max_runs=10):
    """添加自动化任务"""
    queue = load_task_queue()
    task_id = len(queue["tasks"]) + 1
    queue["tasks"].append({
        "id": task_id,
        "name": name,
        "command": command,
        "priority": priority,
        "max_runs": max_runs,
        "runs": 0,
        "enabled": True,
        "created": datetime.now().isoformat()
    })
    save_task_queue(queue)
    return task_id

def run_task(task):
    """执行单个任务"""
    start = time.time()
    try:
        result = subprocess.run(
            task["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        duration = round(time.time() - start, 2)
        log(task["name"], "success", duration, result.stdout[:200])
        return True, duration
    except Exception as e:
        duration = round(time.time() - start, 2)
        log(task["name"], "failed", duration, str(e))
        return False, duration

def log(task_name, status, duration, output):
    """记录执行日志"""
    log_entry = {
        "time": datetime.now().isoformat(),
        "task": task_name,
        "status": status,
        "duration": duration,
        "output": output[:500]
    }
    
    logs = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE) as f:
                logs = json.load(f)
        except:
            logs = []
    
    logs.insert(0, log_entry)
    logs = logs[:100]  # 只保留最近100条
    
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

def run_scheduler():
    """运行调度器"""
    print("🤖 OpenClaw 自动化调度器已启动")
    print(f"📅 周期: {CYCLE_HOURS} 小时")
    
    queue = load_task_queue()
    
    while True:
        try:
            cycle = get_current_cycle()
            
            # 周期开始时执行任务
            if cycle["remaining_minutes"] < 2 and cycle["remaining_minutes"] > 0:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔄 新周期开始，执行任务...")
                
                queue = load_task_queue()
                queue["last_run"] = datetime.now().isoformat()
                queue["total_runs"] += 1
                
                # 按优先级排序
                sorted_tasks = sorted(
                    [t for t in queue["tasks"] if t["enabled"] and t["runs"] < t["max_runs"]],
                    key=lambda x: {"high": 0, "normal": 1, "low": 2}.get(x["priority"], 1)
                )
                
                for task in sorted_tasks:
                    if task["runs"] < task["max_runs"]:
                        success, duration = run_task(task)
                        task["runs"] += 1
                        print(f"  {'✅' if success else '❌'} {task['name']} ({duration}s)")
                
                save_task_queue(queue)
            
            time.sleep(30)  # 每30秒检查一次
            
        except KeyboardInterrupt:
            print("\n调度器已停止")
            break
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(60)

def status():
    """查看调度状态"""
    cycle = get_current_cycle()
    queue = load_task_queue()
    logs = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE) as f:
                logs = json.load(f)
        except:
            pass
    
    print(f"\n{'='*50}")
    print(f"📅 当前周期剩余: {cycle['remaining_minutes']} 分钟")
    print(f"📊 任务队列: {len(queue['tasks'])} 个任务")
    print(f"🔄 总执行次数: {queue['total_runs']} 次")
    print(f"{'='*50}")
    
    if queue["tasks"]:
        print("\n📋 任务列表:")
        for t in queue["tasks"]:
            status = "✅" if t["enabled"] else "⏸️"
            print(f"  {status} [{t['priority'][:1].upper()}] {t['name']} (执行: {t['runs']}/{t['max_runs']})")
    
    if logs:
        print("\n📝 最近执行:")
        for log in logs[:5]:
            icon = "✅" if log["status"] == "success" else "❌"
            print(f"  {icon} {log['task']} - {log['duration']}s")

def main():
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "monitor":
        run_scheduler()
    elif cmd == "status":
        status()
    elif cmd == "add" and len(sys.argv) > 3:
        name = sys.argv[2]
        command = sys.argv[3]
        priority = sys.argv[4] if len(sys.argv) > 4 else "normal"
        task_id = add_task(name, command, priority)
        print(f"✅ 添加任务成功: #{task_id} {name}")
    elif cmd == "log":
        if LOG_FILE.exists():
            with open(LOG_FILE) as f:
                print(f.read())
        else:
            print("暂无日志")
    else:
        print("用法:")
        print("  python3 task-scheduler.py status       # 查看状态")
        print("  python3 task-scheduler.py monitor      # 启动调度器")
        print("  python3 task-scheduler.py add <名称> <命令> [优先级]")
        print("  python3 task-scheduler.py log          # 查看日志")

if __name__ == "__main__":
    main()
