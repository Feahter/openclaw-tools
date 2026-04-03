#!/usr/bin/env python3
"""
Session Miner - 跨Session模式挖掘 v2
从历史session JSONL中提取query，按周聚类，输出高频模式
"""
import json, os, sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
import re

SESSION_DIR = Path.home() / ".openclaw/agents/main/sessions"
OUTPUT_DIR = Path.home() / ".openclaw/workspace/.state/evolution"

def extract_queries(jsonl_path):
    queries = []
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    obj = json.loads(line)
                except: continue
                if obj.get('type') == 'message':
                    msg = obj.get('message', {})
                    if msg.get('role') == 'user':
                        content = msg.get('content', [])
                        if isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get('type') == 'text':
                                    text = block.get('text', '').strip()
                                    if text and len(text) > 5 and '[HEARTBEAT' not in text:
                                        queries.append({'text': text, 'ts': obj.get('timestamp','')})
                elif obj.get('type') == 'text':
                    text = obj.get('text', '').strip()
                    if text and len(text) > 5 and '[HEARTBEAT' not in text:
                        queries.append({'text': text, 'ts': obj.get('timestamp','')})
    except: pass
    return queries

def get_recent_sessions(days=7):
    cutoff = datetime.now() - timedelta(days=days)
    sessions = []
    if SESSION_DIR.exists():
        for f in SESSION_DIR.glob("*.jsonl"):
            if datetime.fromtimestamp(f.stat().st_mtime) >= cutoff:
                sessions.append(f)
    return sessions

def analyze(queries):
    bigrams = []
    for q in queries:
        sents = re.split(r'[,，。、！？；;\n]+', q['text'])
        for s in sents:
            s = s.strip()
            if 4 <= len(s) <= 60:
                bigrams.append(s)
    short = [b for b in bigrams if len(b) <= 15]
    medium = [b for b in bigrams if 15 < len(b) <= 40]
    chinese = re.findall(r'[\u4e00-\u9fff]{2,}', ' '.join(q['text'] for q in queries))
    return {
        'total': len(queries),
        'sessions': len(get_recent_sessions(7)),
        'short': Counter(short).most_common(15),
        'medium': Counter(medium).most_common(10),
        'chinese': Counter(chinese).most_common(20),
    }

if __name__ == '__main__':
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    sessions = get_recent_sessions(days)
    all_q = []
    for s in sessions:
        all_q.extend(extract_queries(s))
    
    seen = set()
    deduped = [q for q in all_q if not (q['text'][:40] in seen or seen.add(q['text'][:40]))]
    
    r = analyze(deduped)
    lines = [
        f'## 每日模式报告 {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'- 最近{days}天 {r["sessions"]} 个Session，{r["total"]}条Query',
        '',
        '### 高频意图（≤15字）',
    ]
    for p, c in r['short']:
        if c >= 2: lines.append(f'- {p} ×{c}')
    lines += ['', '### 描述性请求（16-40字）']
    for p, c in r['medium']:
        if c >= 2: lines.append(f'- {p} ×{c}')
    lines += ['', '### 高频中文词']
    for w, c in r['chinese']:
        if c >= 3: lines.append(f'- {w} ×{c}')
    
    report = '\n'.join(lines)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / 'daily-mining.md'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(report + '\n')
    print(report)
