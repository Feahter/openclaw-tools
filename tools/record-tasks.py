#!/usr/bin/env python3
"""
记录今日执行的任务到任务看板
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
    """添加任务"""
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

# 今日执行的任务记录
TODAY_TASKS = [
    {
        "title": "统一控制台服务配置",
        "desc": "更新 unified-console.py，添加 8770 Token统计 和 8771 自动化工作流 的服务链接和快速访问",
        "tag": "开发,工具",
        "priority": "high"
    },
    {
        "title": "Token统计服务启动",
        "desc": "启动 token-stats.py 服务，端口 8770，用于实时显示各 API 消耗和余额预警",
        "tag": "服务,监控",
        "priority": "high"
    },
    {
        "title": "自动化工作流服务启动",
        "desc": "启动 automation-workflow.py 服务，端口 8771，用于快速执行并行任务和批量操作",
        "tag": "服务,自动化",
        "priority": "high"
    },
    {
        "title": "模型管理服务启动",
        "desc": "启动 local-model-manager.py 服务，端口 8768，用于 Ollama 本地模型和 API Keys 管理",
        "tag": "服务,模型",
        "priority": "high"
    },
    {
        "title": "建立心跳机制",
        "desc": "创建 heartbeat.py 脚本，定时检查所有服务状态、自动记录任务、同步待办到任务看板",
        "tag": "自动化,心跳",
        "priority": "high"
    },
    {
        "title": "服务状态监控集成",
        "desc": "心跳机制自动检测 8765/8768/8769/8770/8771 五个服务运行状态，并在服务停止时自动创建修复任务",
        "tag": "监控,自动化",
        "priority": "mid"
    }
]

def main():
    print(f"\n📝 记录今日任务 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 50)
    
    added = 0
    for task_config in TODAY_TASKS:
        task = add_task(
            title=task_config["title"],
            desc=task_config["desc"],
            tag=task_config["tag"],
            priority=task_config.get("priority", "mid"),
            status="done",
            progress=100
        )
        print(f"✅ 添加: {task['title']}")
        added += 1
    
    print(f"\n共添加 {added} 个任务到任务看板")
    print(f"任务文件: {TASKS_FILE}")

if __name__ == "__main__":
    main()
