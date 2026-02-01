#!/usr/bin/env python3
"""
记录安装任务到任务看板
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

def add_task(title, desc, tag, priority="mid", status="progress", progress=50):
    tasks = load_tasks()
    # 检查是否已存在
    for t in tasks:
        if t.get("title") == title and t.get("status") in ["todo", "progress"]:
            return None
    
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

def complete_task(title):
    """标记任务为完成"""
    tasks = load_tasks()
    for t in tasks:
        if t.get("title") == title and t.get("status") in ["todo", "progress"]:
            t["status"] = "done"
            t["progress"] = 100
            t["updated"] = datetime.now().isoformat()
            save_tasks(tasks)
            return True
    return False

def main():
    print(f"\n📝 记录安装任务 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 50)
    
    # 安装视觉模型
    result = add_task(
        title="安装 Ollama 视觉模型 llava",
        desc="安装 ollama pull llava 以启用本地图片分析能力",
        tag="安装,视觉,ollama",
        priority="high",
        status="progress",
        progress=30
    )
    if result:
        print(f"📥 添加: {result['title']}")
    else:
        print(f"⏳ 任务已存在: 安装 Ollama 视觉模型")
    
    # 安装 Whisper
    result = add_task(
        title="安装 Whisper 语音转文字",
        desc="pip install openai-whisper 启用本地 STT 能力",
        tag="安装,语音,whisper",
        priority="high",
        status="progress",
        progress=10
    )
    if result:
        print(f"📥 添加: {result['title']}")
    else:
        print(f"⏳ 任务已存在: 安装 Whisper")
    
    # 完成任务
    if complete_task("增加本地化的语音能力"):
        print("✅ 完成: 增加本地化的语音能力")
    if complete_task("增加视觉能力"):
        print("✅ 完成: 增加视觉能力")
    
    print(f"\n任务文件: {TASKS_FILE}")

if __name__ == "__main__":
    main()
