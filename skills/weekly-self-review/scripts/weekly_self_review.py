#!/usr/bin/env python3
"""
weekly_self_review.py — 每周自省扫描
扫描上周 session 日志，识别高频意图模式
对标 Hermes nudge 机制：自动生成 skill 建议推送飞书
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path.home() / ".openclaw/workspace"
STATE_FILE = WORKSPACE / ".state/weekly-review-state.json"
REVIEW_DAYS = 7
MIN_QUERY_COUNT = 5
MIN_INTENT_COUNT = 10


# 意图关键词映射（用于识别高频领域）
INTENT_KEYWORDS = {
    "八字/命理": ["八字", "命理", "起名", "喜用神", "神煞", "大运", "纳音"],
    "天气": ["天气", "下雨", "气温", "温度", "晴", "带伞"],
    "新闻": ["新闻", "发生了什么", "今天有什么", "最新消息"],
    "搜索": ["搜一下", "帮我查", "搜索", "找一下"],
    "写作/创作": ["写", "创作", "小说", "文章", "文案"],
    "代码/技术": ["代码", "编程", "脚本", "Python", "GitHub"],
    "提醒/定时": ["提醒", "几点", "叫我", "闹钟"],
    "文件整理": ["整理", "分类", "桌面", "文件"],
    "飞书": ["飞书", "文档", "协作文档"],
    "邮件": ["邮件", "邮箱", "发邮件"],
}


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_review": None, "last_patterns": {}, "last_skills_suggested": []}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_session_logs(days=7):
    """读取最近 N 天的 session 日志"""
    cutoff = datetime.now() - timedelta(days=days)
    log_files = []

    # 查找所有 .md 日志文件
    memory_dir = WORKSPACE / "memory"
    if memory_dir.exists():
        for f in memory_dir.iterdir():
            if f.is_file() and f.suffix == ".md":
                try:
                    dt = datetime.strptime(f.stem[:10], "%Y-%m-%d")
                    if dt >= cutoff:
                        log_files.append(f)
                except ValueError:
                    pass

    return log_files


def extract_short_queries(log_files, max_len=15):
    """提取短 query（≤max_len字符），统计频率"""
    counter = Counter()
    seen = set()

    for f in log_files:
        try:
            content = f.read_text(errors="replace")
            # 简单分句：按行或句号分割
            for line in content.split("\n"):
                line = line.strip()
                # 提取引号内的用户查询
                for m in re.finditer(r'[的用户问说让]"([^"]{1,%d})"' % max_len, line):
                    q = m.group(1).strip()
                    if q and len(q) >= 2:
                        key = q[:max_len]
                        if key not in seen:
                            counter[key] += 1
                            seen.add(key)
        except Exception:
            pass

    return {q: c for q, c in counter.items() if c >= MIN_QUERY_COUNT}


def detect_intent_domains(log_files):
    """统计各意图领域的出现次数"""
    domain_counts = {domain: 0 for domain in INTENT_KEYWORDS}
    domain_examples = {domain: [] for domain in INTENT_KEYWORDS}

    for f in log_files:
        try:
            content = f.read_text(errors="replace")
            for domain, keywords in INTENT_KEYWORDS.items():
                for kw in keywords:
                    count = content.count(kw)
                    if count > 0:
                        domain_counts[domain] += count
                        # 记录一个例子
                        if len(domain_examples[domain]) < 3:
                            idx = content.find(kw)
                            start = max(0, idx - 20)
                            end = min(len(content), idx + 30)
                            domain_examples[domain].append(content[start:end].replace("\n", " ").strip())
        except Exception:
            pass

    return {
        domain: {"count": count, "examples": domain_examples[domain]}
        for domain, count in domain_counts.items()
        if count >= MIN_INTENT_COUNT
    }


def should_create_skill(short_queries, intent_domains):
    """判断是否需要创建新 skill"""
    suggestions = []

    # 高频短 query → 建议创建 skill
    for q, count in sorted(short_queries.items(), key=lambda x: -x[1]):
        suggestions.append({
            "type": "skill_candidate",
            "trigger": q,
            "count": count,
            "suggestion": f"高频查询「{q}」出现 {count} 次，建议创建 dedicated skill"
        })

    # 高频意图领域 → 建议扩充
    for domain, data in intent_domains.items():
        suggestions.append({
            "type": "intent_expansion",
            "domain": domain,
            "count": data["count"],
            "suggestion": f"「{domain}」领域上周出现 {data['count']} 次，建议检查现有 skill 覆盖度"
        })

    return suggestions


def format_report(short_queries, intent_domains, suggestions):
    """格式化飞书推送报告"""
    lines = ["📊 **本周自省报告**", ""]

    # 高频查询
    if short_queries:
        lines.append("**🔍 高频短查询（出现 ≥5 次）**")
        for q, count in sorted(short_queries.items(), key=lambda x: -x[1])[:5]:
            lines.append(f"  {q} × {count}")
        lines.append("")

    # 意图领域
    if intent_domains:
        lines.append("**🎯 意图领域分布**")
        for domain, data in sorted(intent_domains.items(), key=lambda x: -x[1]["count"]):
            lines.append(f"  {domain}: {data['count']} 次")
        lines.append("")

    # 技能建议
    if suggestions:
        lines.append("**💡 技能建议**")
        for s in suggestions[:5]:
            if s["type"] == "skill_candidate":
                lines.append(f"  • 「{s['trigger']}」×{s['count']} → 建议建 skill")
            else:
                lines.append(f"  • 「{s['domain']}」领域可扩充")
        lines.append("")

    lines.append(f"扫描范围：最近 {REVIEW_DAYS} 天")
    return "\n".join(lines)


def run_review():
    state = load_state()
    log_files = get_session_logs(REVIEW_DAYS)

    if not log_files:
        return {"status": "no_data", "message": "最近7天无 session 日志"}

    short_queries = extract_short_queries(log_files)
    intent_domains = detect_intent_domains(log_files)
    suggestions = should_create_skill(short_queries, intent_domains)

    state["last_review"] = datetime.now().isoformat()
    state["last_patterns"] = {
        "short_queries": short_queries,
        "intent_domains": {k: v["count"] for k, v in intent_domains.items()},
    }
    state["last_skills_suggested"] = suggestions
    save_state(state)

    report = format_report(short_queries, intent_domains, suggestions)

    return {
        "status": "success",
        "log_files_scanned": len(log_files),
        "short_queries": short_queries,
        "intent_domains": intent_domains,
        "suggestions": suggestions,
        "report": report,
    }


if __name__ == "__main__":
    result = run_review()
    print(json.dumps(result, indent=2, ensure_ascii=False))
