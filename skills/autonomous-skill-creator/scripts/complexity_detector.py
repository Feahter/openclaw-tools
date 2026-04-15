#!/usr/bin/env python3
"""complexity_detector.py — 从会话历史检测值得固化的 Skill 候选"""

import json, sys, re
from pathlib import Path
from datetime import datetime, timedelta

STATE_DIR = Path.home() / ".openclaw/workspace/.state/autonomous-skill-creator"
STATE_DIR.mkdir(parents=True, exist_ok=True)

def check_daily_mining():
    """从 daily-mining.md 读取高频词作为候选"""
    dm = Path.home() / ".openclaw/workspace/.state/evolution/daily-mining.md"
    if not dm.exists(): return []
    content = dm.read_text()
    candidates = []
    # 匹配格式："- 搜索 ×43" → 提取"搜索"
    for match in re.finditer(r'^- (.+?) ×(\d+)$', content, re.MULTILINE):
        word = match.group(1).strip()
        count = int(match.group(2))
        if count >= 5 and len(word) > 1:
            candidates.append({"query": word, "count": count, "priority": "high" if count >= 7 else "medium"})
    return candidates

def generate_candidates():
    daily_mining = check_daily_mining()
    # 去重
    seen = set()
    candidates = []
    for c in daily_mining:
        if c["query"] not in seen:
            seen.add(c["query"])
            candidates.append(c)
    candidates.sort(key=lambda x: (-x["count"], x["priority"]=="medium"))
    return {
        "checked_at": datetime.now().isoformat(),
        "candidates": candidates,
        "high": len([c for c in candidates if c["priority"]=="high"]),
        "medium": len([c for c in candidates if c["priority"]=="medium"]),
    }

if __name__ == "__main__":
    result = generate_candidates()
    out = STATE_DIR / "candidates.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"🦞 复杂度检测: {result['high']}高/{result['medium']}中 → {out}")
    for i, c in enumerate(result["candidates"][:5], 1):
        print(f"  {i}. [{c['priority']}] {c['query']} (×{c['count']})")