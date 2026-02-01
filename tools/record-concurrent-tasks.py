#!/usr/bin/env python3
"""
记录并发任务管理器开发任务
"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
TASKS_FILE = WORKSPACE / "task-board.json"

def load_tasks():
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE) as f:
                return json.load(f)
        except:
            pass
    return []

def save_tasks(tasks):
    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def add_task(title, desc, tag, priority="high", status="done", progress=100):
    tasks = load_tasks()
    new_task = {
        "id": int(datetime.now().timestamp() * 1000) % 100000,
        "title": title,
        "desc": desc,
        "status": status,
        "priority": priority,
        "tag": tag,
        "progress": progress,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat()
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task

TODAY_TASKS = [
    {
        "title": "并发任务管理器开发",
        "desc": "创建 concurrent-task-manager.py (端口 8780)，支持并行任务执行、任务队列、结果聚合",
        "tag": "开发,并发,分身术",
        "priority": "high",
        "status": "done",
        "progress": 100
    },
    {
        "title": "并行代理执行器",
        "desc": "创建 parallel-agent.py，支持真正的子代理并行执行和流水线任务",
        "tag": "开发,并发,子代理",
        "priority": "high",
        "status": "done",
        "progress": 100
    },
    {
        "title": "更新工具启动器配置",
        "desc": "更新 launcher.py 和 unified-console.py，添加 8780 并发任务入口",
        "tag": "配置,工具",
        "priority": "mid",
        "status": "done",
        "progress": 100
    },
    {
        "title": "测试并发任务功能",
        "desc": "测试并行执行多个任务、流水线任务、结果聚合功能",
        "tag": "测试,并发",
        "priority": "high",
        "status": "in_progress",
        "progress": 50
    }
]

def main():
    print(f"\n📝 记录任务 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 50)
    
    added = 0
    for task_config in TODAY_TASKS:
        task = add_task(
            title=task_config["title"],
            desc=task_config["desc"],
            tag=task_config["tag"],
            priority=task_config.get("priority", "mid"),
            status=task_config.get("status", "todo"),
            progress=task_config.get("progress", 0)
        )
        status_icon = "✅" if task_config["status"] == "done" else "🔵"
        print(f"{status_icon} 添加: {task['title']}")
        added += 1
    
    print(f"\n共添加 {added} 个任务")
    print(f"任务文件: {TASKS_FILE}")

if __name__ == "__main__":
    main()
