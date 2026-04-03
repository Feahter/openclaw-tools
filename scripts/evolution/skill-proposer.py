#!/usr/bin/env python3
"""
Skill Proposal Generator - 基于模式挖掘的自动技能提案
读取每日挖掘报告，生成技能提案
"""
import json, sys
from datetime import datetime
from pathlib import Path
from collections import Counter
import re

OUTPUT_DIR = Path.home() / ".openclaw/workspace/.state/evolution"
PROPOSALS_DIR = Path.home() / ".openclaw/workspace/.state/evolution/proposals"

def extract_chinese_words(text):
    return re.findall(r'[\u4e00-\u9fff]{2,}', text)

def analyze_and_propose():
    mining_path = OUTPUT_DIR / 'daily-mining.md'
    if not mining_path.exists():
        print("No mining data yet")
        return
    
    content = mining_path.read_text(encoding='utf-8')
    proposals = []
    
    # 分析中文高频词找意图
    chinese_lines = [l for l in content.split('\n') if '×' in l and re.search(r'[\u4e00-\u9fff]', l)]
    
    # 高频领域检测
    domains = {
        '节气': [],
        '八字': [],
        '命理': [],
        '新闻': [],
        '天气': [],
        '邮件': [],
        '日历': [],
        '搜索': [],
        '飞书': [],
        'GitHub': [],
    }
    
    for line in chinese_lines:
        for domain in domains:
            if domain in line:
                # 提取数量
                match = re.search(r'×(\d+)', line)
                if match:
                    count = int(match.group(1))
                    phrase = re.sub(r'×\d+', '', line).strip().lstrip('- ')
                    domains[domain].append((phrase, count))
    
    # 生成提案
    for domain, mentions in domains.items():
        total = sum(m[1] for m in mentions)
        if total >= 10:
            top_items = sorted(mentions, key=lambda x: -x[1])[:3]
            proposals.append({
                'domain': domain,
                'total_mentions': total,
                'top_patterns': top_items,
                'priority': 'high' if total >= 30 else 'medium',
                'suggestion': f"高频领域「{domain}」在最近7天出现{total}次，建议评估是否需要专用Skill"
            })
    
    # 高频短Query检测
    short_lines = [l for l in content.split('\n') if '高频意图' in l]
    idx = content.find('### 高频意图')
    if idx >= 0:
        section = content[idx:idx+500]
        high_freq = re.findall(r'^-\s+(.+?)\s+×(\d+)', section, re.MULTILINE)
        for phrase, count in high_freq:
            count = int(count)
            if count >= 5:
                proposals.append({
                    'domain': 'high_freq_query',
                    'pattern': phrase,
                    'count': count,
                    'priority': 'high' if count >= 7 else 'medium',
                    'suggestion': f"高频指令「{phrase}」出现{count}次，可能需要创建专用Skill或优化现有Skill触发词"
                })
    
    return proposals

if __name__ == '__main__':
    proposals = analyze_and_propose()
    if not proposals:
        print("No proposals generated")
        sys.exit(0)
    
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = PROPOSALS_DIR / f'proposals-{datetime.now().strftime("%Y%m%d")}.md'
    
    lines = [f"# 技能提案报告 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    for p in proposals:
        priority_emoji = '🔴' if p['priority'] == 'high' else '🟡'
        lines.append(f"{priority_emoji} **{p['domain']}** (优先级:{p['priority']})")
        lines.append(f"  - {p['suggestion']}")
        if 'top_patterns' in p:
            for pattern, count in p['top_patterns']:
                lines.append(f"    - {pattern}: ×{count}")
        lines.append("")
    
    report = '\n'.join(lines)
    report_path.write_text(report, encoding='utf-8')
    
    # 同时输出
    print(report)
