#!/usr/bin/env python3
"""
algo_hunter — 扫描 arxiv/GitHub 发现新算法，研究后归档到 skill-algo-master
Usage: python3 algo_hunter.py [--days 7] [--limit 5]
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ALGO_MASTER = Path.home() / ".openclaw/workspace/skills/skill-algo-master"
ALGOS_MD = ALGO_MASTER / "references/algorithms.md"
SKILL_MD = ALGO_MASTER / "SKILL.md"
LOG_FILE = Path(__file__).parent.parent / "references/hunt-log.md"

ALGO_KEYWORDS = [
    "algorithm", "data structure", "optimization", "graph neural",
    "transformer", "reinforcement learning", "clustering", "classification",
    "regression", "prediction", "detection", "segmentation", "generation",
    "embedding", "alignment", "inference", "training", "compression",
    "approximation", "heuristic", "sampling", "search", "planning",
    "scheduling", "routing", "matching", "parsing", "encoding", "decoding"
]

EXCLUDE_KEYWORDS = [
    "web app", "mobile app", "database system", "operating system",
    "hardware design", "visualization tool", "security vulnerability"
]


def fetch_arxiv(days: int = 7, limit: int = 30) -> list[dict]:
    """获取 arxiv cs.AI 最近 N 天新提交"""
    try:
        date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        url = (
            f"https://export.arxiv.org/api/query?"
            f"search_query=cat:cs.AI&start=0&max_results={limit}"
            f"&sortBy=submittedDate&sortOrder=descending"
        )
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            xml = r.read().decode("utf-8", errors="ignore")
        return parse_arxiv_feed(xml)
    except Exception as e:
        print(f"⚠️ arxiv 获取失败: {e}")
        return []


def parse_arxiv_feed(xml: str) -> list[dict]:
    """解析 arxiv Atom feed"""
    results = []
    entries = xml.split("<entry>")
    for entry in entries[1:]:
        try:
            title = extract_tag(entry, "title")
            summary = extract_tag(entry, "summary")
            published = extract_tag(entry, "published")[:10]
            authors_raw = extract_tag(entry, "name")
            results.append({
                "title": title.strip().replace("\n", " "),
                "summary": summary.strip()[:300].replace("\n", " "),
                "published": published,
                "authors": authors_raw,
                "source": "arxiv"
            })
        except Exception:
            continue
    return results


def extract_tag(xml: str, tag: str) -> str:
    """简单 XML 标签提取"""
    start = xml.find(f"<{tag}>")
    if start == -1:
        start = xml.find(f"<{tag}>")
    if start == -1:
        return ""
    start += len(tag) + 2
    end = xml.find(f"</{tag}>", start)
    if end == -1:
        return ""
    return xml[start:end]


def filter_algorithms(papers: list[dict]) -> list[dict]:
    """过滤出算法相关论文"""
    candidates = []
    for p in papers:
        text = (p["title"] + " " + p["summary"]).lower()
        if any(kw in text for kw in ALGO_KEYWORDS):
            if not any(ex in text for ex in EXCLUDE_KEYWORDS):
                score = sum(1 for kw in ALGO_KEYWORDS if kw in text)
                p["score"] = score
                candidates.append(p)
    return sorted(candidates, key=lambda x: -x["score"])[:10]


def fetch_github_trending(days: int = 7, limit: int = 10) -> list[dict]:
    """获取 GitHub trending 算法相关项目"""
    try:
        date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        url = (
            f"https://api.github.com/search/repositories"
            f"?q=algorithm+created:>{date_from}+OR+data+structure+created:>{date_from}"
            f"&sort=stars&per_page={limit}"
        )
        import urllib.request
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Mozilla/5.0"
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        results = []
        for item in data.get("items", [])[:limit]:
            results.append({
                "title": item["full_name"],
                "summary": item.get("description", ""),
                "stars": item["stargazers_count"],
                "url": item["html_url"],
                "created": item["created_at"][:10],
                "source": "github"
            })
        return results
    except Exception as e:
        print(f"⚠️ GitHub 获取失败: {e}")
        return []


def score_and_rank(arxiv_candidates: list, github_projects: list) -> list:
    """合并 + 排序"""
    all_items = []
    for p in arxiv_candidates:
        p["combined_score"] = p.get("score", 0) * 1.5  # arxiv 加权
        all_items.append(p)
    for p in github_projects:
        stars_norm = min(p["stars"] / 1000, 10)
        p["combined_score"] = stars_norm + 5
        all_items.append(p)
    return sorted(all_items, key=lambda x: -x["combined_score"])[:5]


def generate_report(items: list[dict], days: int) -> str:
    """生成猎手报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [f"## 算法猎手报告 — {today}", ""]
    lines.append(f"**扫描范围**：过去 {days} 天 | arxiv cs.AI + GitHub")
    lines.append(f"**候选总数**：{len(items)} 个")

    if items:
        lines.append("")
        lines.append("### 候选池（Top 5）")
        lines.append("| # | 名称 | 来源 | 评分 |")
        lines.append("|---|------|------|------|")
        for i, item in enumerate(items, 1):
            name = item["title"][:40]
            src = item["source"]
            score = f"{item['combined_score']:.1f}"
            lines.append(f"| {i} | {name} | {src} | {score} |")
            if "summary" in item and item["summary"]:
                lines.append(f"|   | {item['summary'][:80]}... | | |")
    else:
        lines.append("")
        lines.append("> 本期无新增候选算法。")

    lines.append("")
    lines.append("### 待研究（手动触发 RESEARCH）")
    for i, item in enumerate(items[:3], 1):
        lines.append(f"{i}. `{item['title']}` — [{item['source']}]")
        lines.append(f"   → RESEARCH 命令：`研究 {item['title']}`")

    return "\n".join(lines)


def append_log(report: str):
    """追加到狩猎日志"""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LOG_FILE.exists():
        content = LOG_FILE.read_text()
    else:
        content = "# 算法狩猎日志\n\n"
    content += "\n---\n\n" + report
    LOG_FILE.write_text(content)
    print(f"📋 狩猎日志: {LOG_FILE}")


def main():
    parser = argparse.ArgumentParser(description="算法猎手")
    parser.add_argument("--days", type=int, default=7, help="扫描天数（默认7天）")
    parser.add_argument("--limit", type=int, default=30, help="arxiv 获取上限")
    parser.add_argument("--dry-run", action="store_true", help="仅扫描不写日志")
    args = parser.parse_args()

    print(f"\n🕵️ 算法猎手启动 — 扫描过去 {args.days} 天\n")

    # ① 扫描
    print("① 扫描信号源...")
    papers = fetch_arxiv(args.days, args.limit)
    github = fetch_github_trending(args.days, 15)
    print(f"   arxiv: {len(papers)} 篇 | GitHub: {len(github)} 个项目")

    # ② 过滤
    print("② 过滤算法相关...")
    candidates = filter_algorithms(papers)
    print(f"   arxiv 候选: {len(candidates)} 篇")

    # ③ 排序
    print("③ 排序评分...")
    ranked = score_and_rank(candidates, github[:5])

    # ⑥ 报告
    report = generate_report(ranked, args.days)
    print(f"\n{report}")

    if not args.dry_run:
        append_log(report)

    print(f"\n✅ 猎取完成。{len(ranked)} 个候选已记录。")


if __name__ == "__main__":
    main()
