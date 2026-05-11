#!/usr/bin/env python3
"""
builder_pulse.py — AI 独立开发者日报生成器

每天收集并生成精选情报报告
"""

import urllib.request
import json
import re
from datetime import datetime
import sys
import os

DATE = datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = f"/tmp/builder-pulse-{DATE}.md"

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
                if title:
                    items.append(f"- {title}")
            return items
    except Exception as e:
        return [f"- 获取失败: {e}"]

def fetch_producthunt():
    """获取 Product Hunt AI 产品"""
    try:
        req = urllib.request.Request(
            "https://api.producthunt.com/v2/api/graphql",
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Authorization': 'Bearer',  # 需要 API token
                'Content-Type': 'application/json'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            return ["- Product Hunt API 需要认证"]
    except:
        return ["- Product Hunt API 需要认证"]

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
                name = repo.get('full_name', '')
                stars = repo.get('stargazers_count', 0)
                desc = repo.get('description', '')[:50]
                items.append(f"- **{name}** ({stars}⭐) — {desc}")
            return items
    except Exception as e:
        return [f"- GitHub 获取失败: {e}"]

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
                name = repo.get('full_name', '')
                lang = repo.get('language', 'N/A') or 'N/A'
                desc = (repo.get('description') or '')[:60]
                items.append(f"- {name} ({lang}) — {desc}")
            return items if items else ["- 暂无数据"]
    except Exception as e:
        return [f"- 获取失败: {e}"]

# ========== 报告生成 ==========

def generate_report():
    """生成日报"""
    print(f"📡 BuilderPulse 日报生成中... {DATE}")
    print()

    print("📡 获取 Hacker News...")
    hn_items = fetch_hackernews_top()
    print(f"   获取到 {len(hn_items)} 条")

    print("📡 获取 GitHub Trending...")
    gh_trending = fetch_github_trending()
    print(f"   获取到 {len(gh_trending)} 条")

    print("📡 获取 AI 新项目...")
    gh_ai = fetch_github_ai_repos()
    print(f"   获取到 {len(gh_ai)} 条")

    # 组装报告
    report = f"""# 🤖 BuilderPulse 日报

**日期**: {DATE}
**定位**: AI 独立开发者情报精选

---

## 📰 今日 AI 产品发布

{chr(10).join(hn_items) if hn_items else "- 暂无数据"}

---

## 🚀 GitHub Trending

{chr(10).join(gh_trending) if gh_trending else "- 暂无数据"}

---

## 💡 AI 新项目发现

{chr(10).join(gh_ai) if gh_ai else "- 暂无数据"}

---

## 📊 报告说明

- 数据来源: Hacker News, GitHub
- 生成时间: {datetime.now().strftime("%H:%M:%S")}
- 覆盖周期: 最近 24-48 小时

---

*由 BuilderPulse Skill 自动生成*
"""

    # 写入文件
    with open(OUTPUT_DIR, 'w', encoding='utf-8') as f:
        f.write(report)

    print()
    print(f"✅ 报告已生成: {OUTPUT_DIR}")
    return report

def main():
    source_filter = None
    if len(sys.argv) > 1:
        source_filter = sys.argv[1].lower()
    
    if source_filter == 'github':
        print("📡 获取 GitHub Trending...")
        items = fetch_github_trending()
        print(f"获取到 {len(items)} 条")
        print()
        print("## 🚀 GitHub Trending")
        for item in items:
            print(item)
    elif source_filter == 'hn':
        print("📡 获取 Hacker News...")
        items = fetch_hackernews_top()
        print(f"获取到 {len(items)} 条")
        print()
        print("## 📰 Hacker News")
        for item in items:
            print(item)
    else:
        report = generate_report()
        print()
        print(report)

if __name__ == '__main__':
    main()
