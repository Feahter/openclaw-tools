#!/usr/bin/env python3
"""skill_generator.py — 从候选生成 SKILL.md 草稿"""

import json, re
from pathlib import Path
from datetime import datetime

STATE_DIR = Path.home() / ".openclaw/workspace/.state/autonomous-skill-creator"
DRAFTS_DIR = STATE_DIR / "drafts"
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

def to_snake(name):
    # 转换为 a-z_ 格式
    s = re.sub(r'[^a-z0-9\u4e00-\u9fa5]+', '_', name.lower())
    # 处理中文
    import hashlib
    if '\u4e00' <= name[0] <= '\u9fa5':
        return "auto_" + hashlib.md5(name.encode()).hexdigest()[:8]
    return s.strip('_')[:50]

def generate_skill_md(candidate):
    name = to_snake(candidate["query"])
    keywords = [candidate["query"]]
    
    return f"""---
name: {name}
description: >
  自动创建的Skill - 基于高频词「{candidate['query']}」
  近期出现 {candidate['count']} 次，触发自动创建
triggers:
  - keywords: {keywords}
    load: true
    priority: medium
---

# {candidate['query']} 任务Procedure

1. [TODO] 分析用户具体需求
2. [TODO] 执行相关操作
3. [TODO] 返回结果

## 元数据
- 自动生成于: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- 候选优先级: {candidate['priority']}
- 出现次数: {candidate['count']}
"""

def main():
    candidates_file = STATE_DIR / "candidates.json"
    if not candidates_file.exists():
        print("❌ 暂无候选，请先运行 complexity_detector.py")
        return
    
    data = json.loads(candidates_file.read_text())
    generated = []
    
    for c in data.get("candidates", [])[:5]:
        slug = to_snake(c["query"])
        draft_file = DRAFTS_DIR / f"{slug}.md"
        draft_file.write_text(generate_skill_md(c))
        generated.append(slug)
        print(f"✅ 生成了: {slug}.md")
    
    print(f"\n📦 共生成 {len(generated)} 个草稿 → {DRAFTS_DIR}")

if __name__ == "__main__":
    main()