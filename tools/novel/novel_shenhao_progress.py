#!/usr/bin/env python3
"""
神豪小说创作进度追踪脚本
按分镜脚本顺序创作，每半小时执行一次
"""
import json
import os
from pathlib import Path

NOVEL_DIR = Path("/Users/fuzhuo/.openclaw/workspace/novels/重生之我是神豪")
STATE_FILE = NOVEL_DIR / "创作进度.json"

# 分镜脚本顺序
STORYBOARD_ORDER = [
    # 前卷 (01-08)
    ("前卷", "storyboards", 1, 8),
    # 中卷 (09-24)
    ("中卷", "storyboards", 9, 24),
    # 后卷 (25-34)
    ("后卷", "storyboards", 25, 34),
]

def get_current_storyboard():
    """获取当前应该创作的分镜脚本"""
    # 读取进度状态
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            state = json.load(f)
        current = state.get("current_storyboard", 1)
        completed = state.get("completed", [])
    else:
        current = 1
        completed = []

    # 检查是否全部完成
    if current > 34:
        return None, None, "全部分镜脚本已完成"

    # 找到当前分镜对应的卷和编号
    for volume, folder, start, end in STORYBOARD_ORDER:
        if start <= current <= end:
            sb_num = current
            sb_name = f"storyboard_{sb_num:02d}_*.md"
            sb_path = NOVEL_DIR / volume / folder
            
            # 找到实际文件名
            files = list(sb_path.glob(f"storyboard_{sb_num:02d}_*.md"))
            if files:
                return volume, files[0], current
            
    return None, None, "未找到分镜脚本"

def read_storyboard_content(volume, sb_path):
    """读取分镜脚本内容"""
    with open(sb_path) as f:
        return f.read()

def update_progress(current_num):
    """更新创作进度"""
    state = {}
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            state = json.load(f)
    
    completed = state.get("completed", [])
    if current_num not in completed:
        completed.append(current_num)
    
    next_num = current_num + 1 if current_num < 34 else 34
    
    state["current_storyboard"] = next_num
    state["completed"] = completed
    state["last_updated"] = str(Path(__file__).stat().st_mtime)
    
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

import sys

def main():
    # 支持 --complete 参数
    if len(sys.argv) > 1 and sys.argv[1] == "--complete":
        # 标记当前分镜完成
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                state = json.load(f)
            current = state.get("current_storyboard", 1)
            
            # 更新进度
            completed = state.get("completed", [])
            if current not in completed:
                completed.append(current)
            
            next_num = current + 1 if current < 34 else 34
            state["current_storyboard"] = next_num
            state["completed"] = completed
            state["last_updated"] = "2026-02-17"
            
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            if next_num > 34:
                print(f"✅ 第{current}个分镜脚本已完成！全部分镜脚本已创作完毕！")
            else:
                print(f"✅ 第{current}个分镜脚本已完成！下一个分镜: 第{next_num}个")
        return
    
    volume, sb_path, msg = get_current_storyboard()
    
    if volume is None:
        print(f"✅ {msg}")
        return
    
    print(f"📖 当前创作: 第{msg}个分镜脚本")
    print(f"📁 路径: {sb_path}")
    print(f"📝 内容预览:")
    print("-" * 40)
    content = read_storyboard_content(volume, sb_path)
    # 只打印前500字符
    print(content[:500] if len(content) > 500 else content)
    print("-" * 40)
    
    # 返回信息供 agent 使用
    print(f"\n🎯 任务: 请根据以上分镜脚本创作正文")
    print(f"\n📌 完成创作后，请运行: python {__file__} --complete")

if __name__ == "__main__":
    main()
