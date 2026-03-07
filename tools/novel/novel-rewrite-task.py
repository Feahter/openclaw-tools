#!/usr/bin/env python3
"""
小说章节扩写任务 - 心跳触发
每次执行扩写一章，按SOP标准
"""
import os
import re
import json
import glob
from datetime import datetime

WORK_DIR = "/Users/fuzhuo/.openclaw/workspace/novels/宇宙super英雄传"
STATE_FILE = f"{WORK_DIR}/data/rewrite_state.json"
PROGRESS_FILE = f"{WORK_DIR}/重写进度.md"

# 重写队列（按顺序）
CHAPTER_QUEUE = []

def load_queue():
    """加载重写队列"""
    # 从重写进度.md读取
    queue = []
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取章节名（简化处理）
        matches = re.findall(r'(ch\d+[_-]\S+)', content)
        for m in matches:
            if '_' in m and any(c.isdigit() for c in m.split('_')[-1]):
                queue.append(m.replace('_', '-').replace('-', '_', 1))
    
    # 去重保持顺序
    seen = set()
    result = []
    for c in queue:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result

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

def get_chapter_files():
    """获取所有待重写的章节文件"""
    files = glob.glob(f"{WORK_DIR}/ch0*_*.md") + glob.glob(f"{WORK_DIR}/ch1*_*.md")
    # 过滤掉已完成的
    files = [f for f in files if "-QA" not in f and "summary" not in f]
    return sorted(files)

def get_prev_chapter_content(filepath):
    """获取前一章内容用于连贯"""
    files = get_chapter_files()
    idx = -1
    for i, f in enumerate(files):
        if os.path.basename(f) == os.path.basename(filepath):
            idx = i
            break
    
    if idx > 0:
        prev_file = files[idx - 1]
        with open(prev_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 取最后1000字
            return content[-1000:] if len(content) > 1000 else content
    return None

def get_next_chapter_preview(filepath):
    """获取下一章预览"""
    files = get_chapter_files()
    idx = -1
    for i, f in enumerate(files):
        if os.path.basename(f) == os.path.basename(filepath):
            idx = i
            break
    
    if idx >= 0 and idx < len(files) - 1:
        next_file = files[idx + 1]
        with open(next_file, 'r', encoding='utf-8') as f:
            content = f.read()
            return content[:500] if len(content) > 500 else content
    return None

def analyze_current_chapter(filepath):
    """分析当前章节"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(filepath)
    
    # 去除非正文
    body = re.sub(r'## .*$', '', content, flags=re.MULTILINE)
    body = body.replace('#', '').replace('*', '')
    current_words = len(body)
    
    # 提取章节结构
    sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    
    return {
        "title": title,
        "current_words": current_words,
        "sections": sections,
        "filepath": filepath
    }

def generate_task_prompt(filepath):
    """生成任务提示"""
    info = analyze_current_chapter(filepath)
    prev_context = get_prev_chapter_content(filepath)
    next_hint = get_next_chapter_preview(filepath)
    
    prompt = f"""
📝 **章节扩写任务**

**当前章节**: {info['title']}
**当前字数**: ~{info['current_words']}字
**目标字数**: 8000-15000字

**章节结构**:
"""
    for s in info['sections']:
        prompt += f"- {s}\n"
    
    if prev_context:
        prompt += f"""
**前情提要**（前章结尾）:
{prev_context}
"""
    
    if next_hint:
        prompt += f"""
**下章预告**:
{next_hint[:300]}...
"""
    
    prompt += """
---

## 扩写要求（SOP标准）

1. **字数目标**: 8000-15000字
2. **保持核心**: 不改变原有情节和故事走向
3. **扩写要点**:
   - 补充场景细节（视觉、听觉、嗅觉）
   - 增加人物心理描写
   - 扩展对话深度
   - 添加动作描写
4. **保持风格**: 林启的幽默逗比人设不能崩
5. **连贯性**: 与前后章节自然衔接

## 五项自检（完成后检查）
- [ ] 场景具体：说"在哪"不说"什么圈子"
- [ ] 画面感：闭眼能想象画面
- [ ] 数字感知：大数字换算成可感描述
- [ ] 反派存在：每章有明确对手
- [ ] 情感共鸣：触发基础情绪

**完成后更新重写进度.md记录字数**
"""
    return prompt

def main():
    """主函数"""
    state = load_state()
    files = get_chapter_files()
    
    if not files:
        print("没有待重写的章节文件")
        return
    
    current_idx = state.get("current_index", 0)
    
    if current_idx >= len(files):
        print(f"✅ 所有章节已重写完成！({len(state.get('completed', []))}章)")
        return
    
    filepath = files[current_idx]
    filename = os.path.basename(filepath)
    
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}]")
    print(f"第 {current_idx + 1}/{len(files)} 章: {filename}")
    print(f"{'='*60}")
    
    # 生成任务提示
    prompt = generate_task_prompt(filepath)
    print(prompt)
    
    # 保存待处理状态
    state["pending"] = {
        "file": filename,
        "time": datetime.now().isoformat()
    }
    save_state(state)

if __name__ == "__main__":
    main()
