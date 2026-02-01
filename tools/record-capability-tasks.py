#!/usr/bin/env python3
"""
记录任务到任务看板
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

def add_task(title, desc, tag, priority="mid", status="done", progress=100):
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
        "title": "能力应用集合开发",
        "desc": "创建 capability-collector.py，集成所有 Agent 能力到统一控制台，包含本地化可行性分析和一键启用功能",
        "tag": "开发,能力集合",
        "priority": "high"
    },
    {
        "title": "本地化可行性分析",
        "desc": "分析 14 项 Agent 能力的本地化可行性，生成 capability-report.json 报告",
        "tag": "调研,本地化",
        "priority": "high"
    },
    {
        "title": "服务端口统一配置",
        "desc": "更新统一控制台和 launcher.py，添加 8772 能力集合服务端口，整理所有工具入口",
        "tag": "配置,工具",
        "priority": "mid"
    },
    {
        "title": "更新任务看板待办",
        "desc": "完成「增加本地化的语音能力」和「增加视觉能力」两项待办，通过能力应用集合实现",
        "tag": "任务,待办",
        "priority": "mid",
        "status": "done",
        "progress": 100
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
        status_icon = "✅" if task_config.get("status") == "done" else "📝"
        print(f"{status_icon} 添加: {task['title']}")
        added += 1
    
    print(f"\n共添加 {added} 个任务")
    print(f"任务文件: {TASKS_FILE}")

if __name__ == "__main__":
    main()
