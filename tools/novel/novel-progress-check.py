#!/usr/bin/env python3
"""小说进度检查脚本 - 替代 jq"""

import json
import sys
from pathlib import Path

NOVEL_DIR = Path("/Users/fuzhuo/.openclaw/workspace/novels/宇宙super英雄传")
PROGRESS_FILE = NOVEL_DIR / "progress.json"


def check_progress():
    """检查小说进度"""
    if not PROGRESS_FILE.exists():
        print(f"❌ 进度文件不存在: {PROGRESS_FILE}")
        return
    
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取进度信息
    progress = data.get('progress', {})
    total = data.get('novel', {}).get('chapter_count', 120)
    current = progress.get('total_chapters', 0)
    
    print(f"📚 {data.get('novel', {}).get('title', '未知')}")
    print(f"进度: {current}/{total} 章 ({(current * 100) // total}%)")
    print(f"当前卷: {data.get('novel', {}).get('current_volume', '未知')}")
    print(f"最后更新: {progress.get('last_update', '未知')}")
    
    # 章节状态统计
    chapters = data.get('chapters', {})
    completed = sum(1 for v in chapters.values() if v.get('status') == 'completed')
    print(f"已完成章节记录: {completed} 个")
    
    return current


if __name__ == "__main__":
    check_progress()
