#!/usr/bin/env python3
"""
记录安装完成状态
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
        "title": "安装 Ollama 视觉模型 llava",
        "desc": "ollama pull llava 安装完成，提供本地图片分析能力",
        "tag": "安装,视觉,ollama",
        "priority": "high",
        "status": "done",
        "progress": 100
    },
    {
        "title": "测试视觉模型",
        "desc": "测试 moondream 和 llava 视觉模型，确认可正常识别图片",
        "tag": "测试,视觉",
        "priority": "high",
        "status": "done",
        "progress": 100
    },
    {
        "title": "安装 FFmpeg",
        "desc": "brew install ffmpeg，为 Whisper 语音转文字提供支持",
        "tag": "安装,依赖,ffmpeg",
        "priority": "mid",
        "status": "in_progress",
        "progress": 50
    },
    {
        "title": "安装 Whisper 语音转文字",
        "desc": "pip install openai-whisper，提供本地 STT 能力",
        "tag": "安装,语音,whisper",
        "priority": "mid",
        "status": "pending",
        "progress": 0
    }
]

def main():
    print(f"\n📝 记录安装状态 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
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
        status_icon = "✅" if task_config["status"] == "done" else "🔵" if task_config["status"] == "in_progress" else "⚪"
        print(f"{status_icon} 添加: {task['title']}")
        added += 1
    
    print(f"\n共添加 {added} 个任务")
    print(f"任务文件: {TASKS_FILE}")

if __name__ == "__main__":
    main()
