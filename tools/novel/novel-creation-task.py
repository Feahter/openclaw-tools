#!/usr/bin/env python3
"""
小说章节创作任务 - 严格SOP版
每次创作一章，自动加载上下文 + 质量检查
"""
import os
import re
import json
import glob
from datetime import datetime

WORK_DIR = "/Users/fuzhuo/.openclaw/workspace/novels/宇宙super英雄传"
STATE_FILE = f"{WORK_DIR}/data/creation_state.json"
LOG_FILE = f"{WORK_DIR}/data/creation_log.md"

# 章节队列（按顺序）
CHAPTER_QUEUE = None

def load_chapter_queue():
    """加载章节队列"""
    global CHAPTER_QUEUE
    if CHAPTER_QUEUE:
        return CHAPTER_QUEUE
    
    files = glob.glob(f"{WORK_DIR}/ch0*_*.md") + glob.glob(f"{WORK_DIR}/ch1*_*.md")
    files = [f for f in files if not any(x in f for x in ["QA", "summary", "planning", "storyboard"])]
    files = sorted(files)
    
    # 加载状态
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    
    completed = state.get("completed", [])
    
    # 过滤已完成的
    queue = []
    for f in files:
        name = os.path.basename(f)
        if name not in completed:
            queue.append(f)
    
    CHAPTER_QUEUE = queue
    return queue

def save_state(completed_file):
    """保存状态"""
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    
    if "completed" not in state:
        state["completed"] = []
    
    state["completed"].append(completed_file)
    state["last_updated"] = datetime.now().isoformat()
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_chapter_files():
    """获取所有章节文件"""
    files = glob.glob(f"{WORK_DIR}/ch0*_*.md") + glob.glob(f"{WORK_DIR}/ch1*_*.md")
    files = [f for f in files if not any(x in f for x in ["QA", "summary", "planning", "storyboard"])]
    return sorted(files)

def load_context(filepath, num_chapters=3):
    """加载上下文 - 前后各N章"""
    files = get_chapter_files()
    idx = -1
    for i, f in enumerate(files):
        if os.path.basename(f) == os.path.basename(filepath):
            idx = i
            break
    
    context = {"before": [], "after": []}
    
    # 前文
    for i in range(idx - 1, max(0, idx - num_chapters - 1), -1):
        with open(files[i], 'r', encoding='utf-8') as f:
            content = f.read()
            context["before"].append({
                "file": os.path.basename(files[i]),
                "content": content[:2000]  # 只取前2000字
            })
    
    # 后文
    for i in range(idx + 1, min(len(files), idx + num_chapters + 1)):
        with open(files[i], 'r', encoding='utf-8') as f:
            content = f.read()
            context["after"].append({
                "file": os.path.basename(files[i]),
                "content": content[:1000]  # 取前1000字作为预告
            })
    
    return context

def analyze_chapter(filepath):
    """分析当前章节"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(filepath)
    
    # 提取章节结构
    sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    
    # 字数统计（去除元数据）
    body = re.sub(r'## .*$', '', content, flags=re.MULTILINE)
    body = body.replace('#', '').replace('*', '').replace('-', '')
    current_words = len(body)
    
    return {
        "title": title,
        "current_words": current_words,
        "sections": sections,
        "filepath": filepath,
        "filename": os.path.basename(filepath)
    }

def generate_detailed_prompt(filepath):
    """生成详细的任务提示"""
    info = analyze_chapter(filepath)
    context = load_context(filepath, num_chapters=3)
    
    prompt = f"""
# 📝 小说章节创作任务

**当前章节**: {info['title']}
**文件**: {info['filename']}
**当前字数**: ~{info['current_words']}字
**目标字数**: 8000-15000字

---

## 🎯 任务要求

### 1. 必须扩写
当前章节字数不足，需要大幅扩写至 8000-15000 字。

### 2. 保持原有情节
- 不改变故事走向
- 不删除已有情节
- 在此基础上补充细节

### 3. 扩写要点
- 补充场景细节（视觉、听觉、嗅觉、味觉、触觉）
- 增加人物心理描写
- 扩展对话深度
- 添加动作描写和战斗场景
- 埋设伏笔和钩子

---

## 📖 上下文（必须参考）

### 前情提要（第{len(context['before'])}章）:
"""
    
    for c in context["before"]:
        prompt += f"\n**{c['file']}**:\n{c['content']}\n"
    
    prompt += f"""
---

### 当前章节内容:
"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        current_content = f.read()
    prompt += current_content[:3000]  # 当前章节取前3000字
    
    prompt += f"""

---

### 下章预告:
"""
    
    for c in context["after"]:
        prompt += f"\n**{c['file']}**:\n{c['content']}\n"
    
    prompt += """
---

## ✅ 五项自检（创作完成后必须检查）

完成扩写后，逐项检查：

1. **场景具体** [ ]
   - 说"在哪"不说"什么圈子"
   - 例：✓"星际酒店VIP包间" ✗"高档场所"

2. **画面感** [ ]
   - 闭眼能想象画面
   - 例：✓"记者的长枪短炮对准主角" ✗"成为焦点"

3. **数字感知** [ ]
   - 大数字换算成可感描述
   - 例：✓"每人分100万需要14亿人" ✗"14万亿"

4. **反派存在** [ ]
   - 每章有明确对手/压力
   - 例：✓"秦昊脸色铁青" ✗"主角成功了"

5. **情感共鸣** [ ]
   - 触发基础情绪（恐惧/愤怒/喜悦/惊讶/厌恶/悲伤）
   - 主角行为符合人性

---

## 📝 输出格式

完成扩写后：
1. 保存文件到原路径（覆盖）
2. 更新状态：运行 `python3 tools/novel-creation-complete.py {info['filename']}`
3. 报告：当前字数、新增字数

---

## ⚠️ 警告

- 不要跳过任何检查项
- 不要减少原有情节
- 不要改变人设和故事走向
- 确保与前后文连贯
"""
    
    return prompt

def main():
    """主函数"""
    queue = load_chapter_queue()
    
    if not queue:
        print("✅ 所有章节已完成创作！")
        return
    
    filepath = queue[0]
    filename = os.path.basename(filepath)
    
    print(f"\n{'='*70}")
    print(f"📝 小说章节创作任务")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"章节: {filename}")
    print(f"{'='*70}")
    
    # 生成详细提示
    prompt = generate_detailed_prompt(filepath)
    print(prompt)
    
    # 提示LLM需要执行的操作
    print("\n" + "="*70)
    print("🎯 执行步骤:")
    print("="*70)
    print("""
1. 阅读上方【上下文】部分，理解前后情节
2. 阅读【当前章节内容】，了解需要扩写的部分
3. 按照【扩写要点】进行创作，目标是 8000-15000 字
4. 完成后进行【五项自检】
5. 保存文件（覆盖原文件）
6. 运行状态更新命令

""")
    
    # 保存当前任务信息
    task_info = {
        "filename": filename,
        "filepath": filepath,
        "time": datetime.now().isoformat()
    }
    with open(f"{WORK_DIR}/data/current_task.json", 'w') as f:
        json.dump(task_info, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
