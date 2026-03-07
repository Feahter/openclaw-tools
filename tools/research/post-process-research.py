#!/usr/bin/env python3
"""
研究结果后处理脚本
功能：
1. 从报告中提取行动项 → 写入 action-items.md
2. 知识结构化归档 → knowledge-base/
3. 更新趋势索引
"""

import os
import re
import json
import glob
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.path.expanduser("~/.openclaw/workspace"))
MEMORY_DIR = WORKSPACE / "memory"
DIARY_DIR = WORKSPACE / "diary"
ACTION_FILE = MEMORY_DIR / "action-items.md"
KB_DIR = WORKSPACE / "knowledge-base"

def extract_action_items(content: str, source_file: str) -> list:
    """从报告内容中提取行动项"""
    items = []
    # 匹配 [ ] 或 - [ ] 格式
    pattern = r'[-*]\s*\[([ x])\]\s*(.+?)(?:\n|$)'
    matches = re.findall(pattern, content)
    for status, text in matches:
        items.append({
            'text': text.strip(),
            'done': status == 'x',
            'source': source_file,
            'date': datetime.now().strftime('%Y-%m-%d')
        })
    return items

def load_existing_actions() -> list:
    """加载已有行动项"""
    if ACTION_FILE.exists():
        content = ACTION_FILE.read_text()
        # 简单解析：查找未完成的 [ ]
        return extract_action_items(content, "existing")
    return []

def save_action_items(new_items: list):
    """保存行动项到文件"""
    sections = {}
    
    # 按来源分组
    for item in new_items:
        source = item.get('source', 'unknown')
        if source not in sections:
            sections[source] = []
        sections[source].append(item)
    
    # 生成 Markdown
    md = "# 行动项追踪\n\n"
    md += f"*更新于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
    
    for source, items in sections.items():
        source_name = Path(source).stem.replace('-', ' ').title()
        md += f"## {source_name}\n\n"
        for item in items:
            status = '[x]' if item['done'] else '[ ]'
            md += f"- {status} {item['text']}\n"
        md += "\n"
    
    ACTION_FILE.write_text(md)
    print(f"✅ 已更新行动项: {len(new_items)} 项")

def archive_to_knowledgebase(content: str, source_file: str):
    """归档到知识库"""
    # 简单实现：按主题分类存储
    source = Path(source_file).stem
    
    # 判断主题
    if 'wealth' in source.lower() or '财富' in content[:500]:
        category = "wealth"
    elif 'longevity' in source.lower() or '健康' in content[:500]:
        category = "health"
    else:
        category = "misc"
    
    kb_path = KB_DIR / category
    kb_path.mkdir(parents=True, exist_ok=True)
    
    # 写入文件（带日期前缀）
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    dest_file = kb_path / f"{date_prefix}-{source}.md"
    
    # 如果已存在则跳过
    if dest_file.exists():
        print(f"⏭️ 跳过归档: {source} (已存在)")
        return
    
    # 添加元信息
    header = f"""---
source: {source_file}
archived: {datetime.now().isoformat()}
---

"""
    dest_file.write_text(header + content)
    print(f"✅ 已归档: {category}/{dest_file.name}")

def process_research_files():
    """处理所有研究文件"""
    # 查找最新的趋势文件
    patterns = [
        MEMORY_DIR / "*trends*.md",
        MEMORY_DIR / "*research*.md"
    ]
    
    all_items = []
    
    for pattern in patterns:
        for f in glob.glob(str(pattern)):
            if 'action-items' in f:  # 跳过自身
                continue
            
            try:
                content = Path(f).read_text()
                items = extract_action_items(content, Path(f).name)
                all_items.extend(items)
                
                # 归档到知识库
                archive_to_knowledgebase(content, Path(f).name)
            except Exception as e:
                print(f"❌ 处理失败 {f}: {e}")
    
    if all_items:
        save_action_items(all_items)
    else:
        print("⏭️ 未发现新行动项")

if __name__ == "__main__":
    print(f"🔄 开始处理研究结果... ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    process_research_files()
    print("✨ 完成")
