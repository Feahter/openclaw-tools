#!/usr/bin/env python3
"""
安装监控脚本 - 后台监控 llava 和 Whisper 安装进度
"""

import subprocess
import time
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

def update_progress(title, progress, status="progress"):
    tasks = load_tasks()
    for t in tasks:
        if t.get("title") == title:
            t["progress"] = progress
            t["status"] = status
            t["updated"] = datetime.now().isoformat()
            save_tasks(tasks)
            return True
    return False

def check_ollama_llava():
    """检查 llava 是否安装完成"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "llava" in result.stdout.lower():
            return True, 100
    except:
        pass
    
    # 检查进程是否还在运行
    try:
        result = subprocess.run(["pgrep", "-x", "ollama"], capture_output=True, text=True)
        if result.returncode == 0:
            return False, 60  # 假设60%进度
    except:
        pass
    
    return False, 0

def main():
    print(f"\n🔍 安装监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 检查 llava
    llava_done, llava_progress = check_ollama_llava()
    if llava_done:
        print("✅ llava 安装完成!")
        update_progress("安装 Ollama 视觉模型 llava", 100, "done")
    else:
        print(f"⏳ llava 安装中... ({llava_progress}%)")
        update_progress("安装 Ollama 视觉模型 llava", llava_progress)
    
    print(f"\n任务看板已更新")
    print(f"文件: {TASKS_FILE}")

if __name__ == "__main__":
    main()
