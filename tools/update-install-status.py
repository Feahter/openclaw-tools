#!/usr/bin/env python3
"""
更新任务看板 - 安装状态
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

def update_task_by_title(title, **kwargs):
    tasks = load_tasks()
    for t in tasks:
        if t.get("title") == title and t.get("status") in ["todo", "progress"]:
            t.update(kwargs)
            t["updated"] = datetime.now().isoformat()
            save_tasks(tasks)
            return True
    return False

def main():
    print(f"\n📝 更新安装任务状态 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 50)
    
    # 更新视觉模型安装进度
    if update_task_by_title("安装 Ollama 视觉模型 llava", progress=60):
        print("📊 视觉模型: 安装中 (60%)")
    
    # 更新 Whisper 安装进度
    if update_task_by_title("安装 Whisper 语音转文字", progress=30):
        print("📊 Whisper: 安装中 (30%)")
    
    # 显示当前任务状态
    tasks = load_tasks()
    print("\n当前任务状态:")
    for t in tasks:
        if t.get("status") in ["todo", "progress"]:
            icon = "🔵" if t["status"] == "progress" else "⚪"
            print(f"  {icon} [{t['progress']:3}%] {t['title']}")

if __name__ == "__main__":
    main()
