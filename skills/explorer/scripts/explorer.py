#!/usr/bin/env python3
"""
explorer.py — 探索者 Agent

网络海洋的航海日志，每天出海发现有趣项目。
"""

import urllib.request
import json
import re
import os
from datetime import datetime, timedelta
from html import unescape

DATE = datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = f"/tmp/explorer-{DATE}.md"
DISCOVERED_DB = os.path.expanduser("~/.openclaw/workspace/memory/explorer-discovered.json")

# ========== 配置 ==========

INTEREST_KEYWORDS = ["AI", "Agent", "Claude", "LLM", "local", "edge", "runnable", "open source", "indie"]

# ========== 信息源 ==========

def fetch_hackernews():
    """获取 Hacker News 最新项"""
    try:
        # 获取最新提交 + AI相关排序
        req = urllib.request.Request(
            "https://hn.algolia.com/api/v1/search?query=AI+agent&hitsPerPage=10",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            items = []
            for hit in data.get('hits', [])[:5]:
                title = hit.get('title', '')
                url = hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                points = hit.get('points', 0)
                if title and points >= 10:
                    items.append({
                        'title': title[:60],
                        'url': url,
                        'stars': points,
                        'source': 'Hacker News'
                    })
            return items
    except Exception as e:
        return []

def fetch_github_trending():
    """获取 GitHub Trending"""
    try:
        # Python 语言的 AI/ML 项目
        req = urllib.request.Request(
            "https://api.github.com/search/repositories?q=AI+OR+machine-learning+language:python&sort=stars&per_page=10",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            items = []
            for repo in data.get('items', [])[:5]:
                items.append({
                    'name': repo.get('full_name', ''),
                    'stars': repo.get('stargazers_count', 0),
                    'desc': (repo.get('description') or '')[:50],
                    'url': repo.get('html_url', ''),
                    'lang': repo.get('language', 'N/A') or 'N/A',
                    'source': 'GitHub'
                })
            return items
    except Exception as e:
        return []

def fetch_github_fresh():
    """获取 GitHub 最近活跃项目"""
    try:
        now = datetime.now()
        week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        req = urllib.request.Request(
            f"https://api.github.com/search/repositories?q=created:>{week_ago}&sort=updated&per_page=10",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            items = []
            for repo in data.get('items', [])[:3]:
                desc = (repo.get('description') or '')[:40]
                if any(kw.lower() in desc.lower() for kw in INTEREST_KEYWORDS):
                    items.append({
                        'name': repo.get('full_name', ''),
                        'stars': repo.get('stargazers_count', 0),
                        'desc': desc,
                        'url': repo.get('html_url', ''),
                        'source': 'GitHub Fresh'
                    })
            return items
    except:
        return []

def fetch_producthunt():
    """Product Hunt（简化版）"""
    # 由于 PH 需要 API，简化处理
    try:
        req = urllib.request.Request(
            "https://www.producthunt.com/posts.atom",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            # 简化解析
            return []
    except:
        return []

# ========== 去重检查 ==========

def load_discovered():
    """加载已发现项目"""
    if not os.path.exists(DISCOVERED_DB):
        return set()
    try:
        with open(DISCOVERED_DB, 'r') as f:
            data = json.load(f)
            return set(data.get('projects', []))
    except:
        return set()

def save_discovered(projects):
    """保存已发现项目"""
    os.makedirs(os.path.dirname(DISCOVERED_DB), exist_ok=True)
    data = {'projects': list(projects), 'updated': DATE}
    with open(DISCOVERED_DB, 'w') as f:
        json.dump(data, f, indent=2)

# ========== 探索报告 ==========

def explore():
    """执行探索"""
    print(f"🚢 探索者日志生成中... {DATE}")
    print()

    # 多线程撒网
    print("🌊 出海中...")
    hn = fetch_hackernews()
    print(f"   Hacker News: {len(hn)} 收")
    
    gh_trend = fetch_github_trending()
    print(f"   GitHub Trending: {len(gh_trend)} 收")
    
    gh_fresh = fetch_github_fresh()
    print(f"   GitHub Fresh: {len(gh_fresh)} 收")

    # 已发现去重
    discovered = load_discovered()

    # 筛选珍宝
    treasures = []
    
    for item in hn + gh_trend + gh_fresh:
        key = item.get('name') or item.get('title', '')
        if key and key not in discovered:
            # 简单评分
            stars = item.get('stars', 0)
            if stars >= 100 or item.get('source') == 'Hacker News':
                treasures.append(item)
                discovered.add(key)

    # 保存
    save_discovered(discovered)

    # 确定今日方向
    direction = "AI Agent + 本地运行 + 开源落地"

    # 生成报告
    report = f"""# 🚢 探索者日志 | {DATE}

**🌊 出海方向**: {direction}
**⏰ 探索时间**: {datetime.now().strftime("%H:%M")}

---

## 🎣 撒网收获

### Hacker News
"""
    for i, item in enumerate(hn[:3], 1):
        report += f"{i}. **{item['title']}** - ⭐{item['stars']}\n"

    report += """
### GitHub Trending
"""
    for i, item in enumerate(gh_trend[:3], 1):
        report += f"{i}. **{item['name']}** ({item['lang']}) - ⭐{item['stars']:,}\n   {item['desc']}\n"

    report += """
### GitHub 新鲜项目
"""
    for i, item in enumerate(gh_fresh[:2], 1):
        report += f"{i}. **{item['name']}** - ⭐{item['stars']:,}\n   {item['desc']}\n"

    # 珍宝候选
    if treasures:
        report += f"""
---

## 💎 珍宝候选

这些项目值得进一步研究：
"""
        for i, item in enumerate(treasures[:3], 1):
            key = item.get('name') or item.get('title', '')
            report += f"{i}. **{key}**\n"

    report += f"""

---

## ⚓ 锚定

**下次探索方向**: AI Agent 工作流 + 本地运行模型

---

*🚢 Explorer × feather 自动生成*
"""
    
    # 保存
    os.makedirs("/tmp", exist_ok=True)
    with open(OUTPUT_DIR, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print()
    print(f"✅ 探索报告已生成: {OUTPUT_DIR}")
    return report

if __name__ == '__main__':
    report = explore()
    print()
    print(report[:2000])