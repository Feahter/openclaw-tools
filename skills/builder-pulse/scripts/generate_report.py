#!/usr/bin/env python3
"""
builder_pulse.py v2 — AI 独立开发者日报生成器（优化版）

输出包含：
- 结构化表格
- 中文解读
- 趋势洞察
- 研究候选标记
"""

import urllib.request
import json
import re
from datetime import datetime
import sys
import os

DATE = datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = f"/tmp/builder-pulse-{DATE}.md"
RESEARCH_PICK_FILE = f"/tmp/builder-pulse-research-picks-{DATE}.txt"

# ========== 信息源 ==========

def fetch_hackernews_top():
    """获取 Hacker News Top 5"""
    try:
        req = urllib.request.Request(
            "https://hn.algolia.com/api/v1/search?query=AI+indie+hacker&hitsPerPage=5",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            items = []
            for hit in data.get('hits', [])[:5]:
                title = hit.get('title', '')
                url = hit.get('url', hit.get('story_url', ''))
                obj_id = hit.get('objectID', '')
                if title:
                    items.append({
                        'title': title,
                        'url': url,
                        'id': obj_id,
                        'type': 'hn'
                    })
            return items
    except Exception as e:
        return []

def fetch_github_trending():
    """获取 GitHub Trending AI 项目"""
    try:
        req = urllib.request.Request(
            "https://api.github.com/search/repositories?q=AI+created:>2026-04-01&sort=stars&per_page=5",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            items = []
            for repo in data.get('items', [])[:5]:
                items.append({
                    'name': repo.get('full_name', ''),
                    'stars': repo.get('stargazers_count', 0),
                    'desc': repo.get('description', '')[:80],
                    'url': repo.get('html_url', ''),
                    'lang': repo.get('language', 'N/A') or 'N/A',
                    'type': 'github'
                })
            return items
    except Exception as e:
        return []

def fetch_github_ai_repos():
    """获取 AI 相关新项目"""
    try:
        req = urllib.request.Request(
            "https://api.github.com/search/repositories?q=AI+OR+machine-learning+language:python&sort=updated&per_page=5",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            items = []
            for repo in (data.get('items') or [])[:5]:
                if not isinstance(repo, dict):
                    continue
                items.append({
                    'name': repo.get('full_name', ''),
                    'lang': repo.get('language', 'N/A') or 'N/A',
                    'desc': (repo.get('description') or '')[:80],
                    'url': repo.get('html_url', ''),
                    'type': 'ai_new'
                })
            return items
    except Exception as e:
        return []

# ========== 报告生成 ==========

def generate_report():
    """生成优化版日报"""
    print(f"📡 BuilderPulse 日报生成中... {DATE}")

    print("📡 获取 Hacker News...")
    hn_items = fetch_hackernews_top()
    print(f"   获取到 {len(hn_items)} 条")

    print("📡 获取 GitHub Trending...")
    gh_trending = fetch_github_trending()
    print(f"   获取到 {len(gh_trending)} 条")

    print("📡 获取 AI 新项目...")
    gh_ai = fetch_github_ai_repos()
    print(f"   获取到 {len(gh_ai)} 条")

    # 候选研究项目（Pick 1-2 个最有价值的）
    research_picks = []

    # 选择标准：GitHub 3k+⭐ 或 有明确应用场景
    for repo in gh_trending:
        if repo['stars'] >= 3000:
            research_picks.append({
                'name': repo['name'],
                'reason': f"{repo['stars']}⭐ {repo['desc'][:50]}",
                'url': repo['url']
            })
            break  # 只选第一个

    for item in gh_ai[:2]:
        if item['name'] and item['desc'] != 'None':
            research_picks.append({
                'name': item['name'],
                'reason': f"{item['lang']} · {item['desc'][:50]}",
                'url': item['url']
            })

    research_picks = research_picks[:2]  # 最多 2 个

    # 保存研究候选
    with open(RESEARCH_PICK_FILE, 'w') as f:
        for pick in research_picks:
            f.write(f"{pick['name']}|{pick['reason']}|{pick['url']}\n")

    # 组装报告
    report = f"""# 🤖 BuilderPulse 日报 | {DATE}

**定位**：AI 独立开发者情报精选
**生成**：{datetime.now().strftime("%H:%M")} | **覆盖**：最近 48 小时

---

## 📰 今日 AI 产品发布

| 产品 | 一句话描述 | 中文解读 |
|------|-----------|---------|
"""

    for item in hn_items:
        report += f"| {item['title'][:40]} | [链接]({item['url']}) | 待分析 |\n"

    report += f"""
**💡 洞察**：{'本周 AI 工具层基础设施完善，差异化在应用层' if hn_items else ''}

---

## 🚀 GitHub Trending TOP 5

| 项目 | ⭐ | 类型 | 中文解读 |
|------|-----|------|---------|
"""

    for repo in gh_trending:
        lang = repo.get('lang', 'N/A') or 'N/A'
        desc = repo.get('desc', '')[:50] or '无描述'
        report += f"| **{repo['name']}** | {repo['stars']:,} | {lang} | {desc} |\n"

    report += f"""
**💡 洞察**：{'记忆/上下文管理仍是痛点；Skills 是新流量方向' if gh_trending else ''}

---

## 💡 新项目发现

| 项目 | 领域 | 亮点 |
|------|------|------|
"""

    for item in gh_ai:
        lang = item.get('lang', 'N/A') or 'N/A'
        desc = (item.get('desc', '') or '无描述')[:50]
        report += f"| {item['name']} | {lang} | {desc} |\n"

    if research_picks:
        report += f"""
---

## 🎯 研究候选（10点研究任务将自动选取）

"""
        for i, pick in enumerate(research_picks, 1):
            report += f"{i}. **{pick['name']}** — {pick['reason']}\n"
            report += f"   {pick['url']}\n"

    report += f"""

---

## 📊 趋势总结

1. **AI 基础设施饱和** — 记忆、编码、Token 优化已成红海
2. **应用层机会** — B2C、AI+垂直场景、AI Agent 落地案例
3. **Skills 是新流量** — AI 工具本身可以成为产品

---

*🤖 BuilderPulse × feather 优化版*
*数据源：Hacker News · GitHub*
"""

    # 写入文件
    with open(OUTPUT_DIR, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 报告已生成: {OUTPUT_DIR}")
    print(f"✅ 研究候选已保存: {RESEARCH_PICK_FILE}")
    return report

def get_research_picks():
    """获取研究候选"""
    picks = []
    if os.path.exists(RESEARCH_PICK_FILE):
        with open(RESEARCH_PICK_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 3:
                    picks.append({'name': parts[0], 'reason': parts[1], 'url': parts[2]})
    return picks

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--picks':
        picks = get_research_picks()
        if picks:
            print("🎯 今日研究候选：")
            for i, pick in enumerate(picks, 1):
                print(f"{i}. {pick['name']} — {pick['url']}")
        else:
            print("❌ 暂无研究候选，请先生成日报")
    else:
        report = generate_report()
        print()
        print(report)

if __name__ == '__main__':
    main()
