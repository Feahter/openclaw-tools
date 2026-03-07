#!/usr/bin/env python3
"""
小说章节创作完成 - 状态更新
在章节创作完成后运行，记录完成状态
"""
import os
import sys
import json
from datetime import datetime

WORK_DIR = "/Users/fuzhuo/.openclaw/workspace/novels/宇宙super英雄传"
STATE_FILE = f"{WORK_DIR}/data/creation_state.json"
LOG_FILE = f"{WORK_DIR}/data/creation_log.md"

def load_state():
    """加载状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"completed": [], "logs": []}

def save_state(state):
    """保存状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def add_log(filename, word_count):
    """添加日志"""
    log_entry = {
        "time": datetime.now().isoformat(),
        "file": filename,
        "words": word_count
    }
    
    # 读取现有日志
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # 简单解析
            if "## 创作日志" in content:
                logs = []  # 已有格式
    
    # 追加新日志
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n### {log_entry['time'][:19]} - {filename}\n")
        f.write(f"- 字数: {word_count}\n")
        f.write(f"- 状态: ✅ 完成\n")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python novel-creation-complete.py <文件名> [字数]")
        print("例: python novel-creation-complete.py ch018-兄弟情_1.md 12000")
        return
    
    filename = sys.argv[1]
    word_count = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    # 读取当前文件字数
    if word_count == 0:
        filepath = f"{WORK_DIR}/{filename}"
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # 简单字数统计
            word_count = len(content.replace('#', '').replace('*', '').replace('-', ''))
    
    # 更新状态
    state = load_state()
    if "completed" not in state:
        state["completed"] = []
    
    if filename not in state["completed"]:
        state["completed"].append(filename)
    
    state["last_completed"] = filename
    state["last_completed_at"] = datetime.now().isoformat()
    state["last_word_count"] = word_count
    
    save_state(state)
    add_log(filename, word_count)
    
    print(f"✅ 已记录完成: {filename} ({word_count}字)")
    print(f"总完成章节数: {len(state['completed'])}")

if __name__ == "__main__":
    main()
