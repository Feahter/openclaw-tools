#!/usr/bin/env python3
"""
小说章节扩写脚本 - 按SOP标准重写章节
每次执行重写一章，确保前后连贯
"""
import os
import re
import json
import glob
from datetime import datetime

WORK_DIR = "/Users/fuzhuo/.openclaw/workspace/novels/宇宙super英雄传"
PROGRESS_FILE = f"{WORK_DIR}/重写进度.md"
STATE_FILE = f"{WORK_DIR}/data/rewrite_state.json"

# 待重写章节队列（按顺序）
CHAPTER_QUEUE = [
    # ch017
    "ch017-1-真相前的宁静", "ch017-2-父亲的真相", "ch017-3-艰难的选择", "ch017-4-商议",
    # ch018
    "ch018-兄弟情_1", "ch018-兄弟情_2", "ch018-兄弟情_3", "ch018-兄弟情_4",
    "ch018-兄弟情_5", "ch018-兄弟情_6", "ch018-兄弟情_7", "ch018-兄弟情_8",
    # ch019
    "ch019-帝国公主_1", "ch019-帝国公主_2", "ch019-帝国公主_3", "ch019-帝国公主_4",
    # ch020
    "ch020-告白_1", "ch020-告白_2", "ch020-告白_3",
    # ch021
    "ch021-帝国追击_1", "ch021-帝国追击_2", "ch021-帝国追击_3", "ch021-帝国追击_4",
    # ch022
    "ch022-舌战群儒_1", "ch022-舌战群儒_2", "ch022-舌战群儒_3", "ch022-舌战群儒_4",
    # ch023
    "ch023-结盟_1", "ch023-结盟_2", "ch023-结盟_3", "ch023-结盟_4", "ch023-结盟_5",
    # ch024
    "ch024-教团总攻_1", "ch024-教团总攻_2", "ch024-教团总攻_3", "ch024-教团总攻_4", "ch024-教团总攻_5",
    # ch025
    "ch025-牺牲_1", "ch025-牺牲_2", "ch025-牺牲_3", "ch025-牺牲_4", "ch025-牺牲_5", "ch025-牺牲_6", "ch025-牺牲_7",
    # ch055
    "ch055_蜜月危机_1", "ch055_蜜月危机_2", "ch055_蜜月危机_3", "ch055_蜜月危机_4",
    # ch059
    "ch059_永恒之核的守护者_1", "ch059_永恒之核的守护者_2", "ch059_永恒之核的守护者_3",
    "ch059_永恒之核的守护者_4", "ch059_永恒之核的守护者_5",
    # ch064
    "ch064_地球秘密_1", "ch064_地球秘密_2", "ch064_地球秘密_3", "ch064_地球秘密_4",
    "ch064_地球秘密_5", "ch064_地球秘密_6", "ch064_地球秘密_7", "ch064_地球秘密_8",
    # ch079
    "ch079_苏小暖的谈判艺术_1", "ch079_苏小暖的谈判艺术_2", "ch079_苏小暖的谈判艺术_3",
    "ch079_苏小暖的谈判艺术_4", "ch079_苏小暖的谈判艺术_5", "ch079_苏小暖的谈判艺术_6",
    # ch082
    "ch082_备考文明_1", "ch082_备考文明_2", "ch082_备考文明_3", "ch082_备考文明_4", "ch082_备考文明_5",
    # ch083
    "ch083_文明审判开始_1", "ch083_文明审判开始_2", "ch083_文明审判开始_3",
    "ch083_文明审判开始_4", "ch083_文明审判开始_5", "ch083_文明审判开始_6",
]

def load_state():
    """加载当前状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"current_index": 0, "completed": []}

def save_state(state):
    """保存状态"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_chapter_content(chapter_name):
    """获取章节内容"""
    # 尝试多种文件扩展名
    for ext in ['.md', '.txt']:
        filepath = f"{WORK_DIR}/{chapter_name}{ext}"
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
    return None

def get_prev_chapter(chapter_name):
    """获取前一章内容（用于连贯性）"""
    idx = CHAPTER_QUEUE.index(chapter_name) if chapter_name in CHAPTER_QUEUE else -1
    if idx > 0:
        prev = CHAPTER_QUEUE[idx - 1]
        content = get_chapter_content(prev)
        if content:
            # 提取最后500字
            return content[-500:] if len(content) > 500 else content
    return None

def get_next_chapter_summary(chapter_name):
    """获取下一章概要（用于埋钩子）"""
    idx = CHAPTER_QUEUE.index(chapter_name) if chapter_name in CHAPTER_QUEUE else -1
    if idx >= 0 and idx < len(CHAPTER_QUEUE) - 1:
        next_ch = CHAPTER_QUEUE[idx + 1]
        content = get_chapter_content(next_ch)
        if content:
            # 提取前200字作为概要
            return content[:200] if len(content) > 200 else content
    return None

def rewrite_chapter(chapter_name):
    """重写章节"""
    content = get_chapter_content(chapter_name)
    if not content:
        print(f"章节文件不存在: {chapter_name}")
        return False
    
    # 获取上下文
    prev_context = get_prev_chapter(chapter_name)
    next_hint = get_next_chapter_summary(chapter_name)
    
    # 提取章节标题
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else chapter_name
    
    # 统计当前字数
    # 去除创作说明等非正文部分
    body = re.sub(r'## 创作说明.*', '', content, flags=re.DOTALL)
    body = re.sub(r'## 关键信息点.*', '', body, flags=re.DOTALL)
    body = re.sub(r'## 下一章预告.*', '', body, flags=re.DOTALL)
    current_words = len(body)
    
    print(f"\n{'='*50}")
    print(f"开始重写: {chapter_name}")
    print(f"当前字数: ~{current_words}")
    print(f"{'='*50}")
    
    # TODO: 这里调用LLM进行重写
    # 目前先输出任务信息，实际重写需要LLM配合
    
    return True

def main():
    """主函数"""
    state = load_state()
    current_idx = state.get("current_index", 0)
    
    if current_idx >= len(CHAPTER_QUEUE):
        print("✅ 所有章节已重写完成！")
        return
    
    chapter_name = CHAPTER_QUEUE[current_idx]
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 准备重写第 {current_idx + 1}/{len(CHAPTER_QUEUE)} 章: {chapter_name}")
    
    # 检查文件是否存在
    content = get_chapter_content(chapter_name)
    if not content:
        print(f"⚠️ 跳过: {chapter_name} (文件不存在)")
        state["current_index"] += 1
        save_state(state)
        return
    
    # 重写章节
    success = rewrite_chapter(chapter_name)
    
    if success:
        state["completed"].append({
            "chapter": chapter_name,
            "time": datetime.now().isoformat()
        })
        state["current_index"] += 1
        save_state(state)
        print(f"✅ {chapter_name} 重写任务已记录")

if __name__ == "__main__":
    main()
