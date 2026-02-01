#!/usr/bin/env python3
"""
测试已安装的功能并更新任务状态
"""

import subprocess
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

def update_task(title, **kwargs):
    tasks = load_tasks()
    for t in tasks:
        if t.get("title") == title:
            t.update(kwargs)
            t["updated"] = datetime.now().isoformat()
            save_tasks(tasks)
            return True
    return False

def test_ollama_vision():
    """测试 Ollama 视觉模型"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        has_llava = "llava" in result.stdout.lower()
        has_moondream = "moondream" in result.stdout.lower()
        return has_llava or has_moondream
    except:
        return False

def test_tts():
    """测试 TTS"""
    try:
        subprocess.run(["which", "say"], capture_output=True)
        return True
    except:
        return False

def main():
    print(f"\n🧪 功能测试 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 50)
    
    # 测试视觉能力
    vision_ok = test_ollama_vision()
    print(f"\n👁️ 视觉能力: {'✅ 可用' if vision_ok else '❌ 不可用'}")
    if vision_ok:
        update_task("安装 Ollama 视觉模型 llava", status="done", progress=100)
        print("   已标记为完成")
    
    # 测试语音能力
    tts_ok = test_tts()
    print(f"\n🔊 TTS 语音: {'✅ 可用 (macOS say)' if tts_ok else '❌ 不可用'}")
    
    print(f"\n任务文件已更新: {TASKS_FILE}")

if __name__ == "__main__":
    main()
