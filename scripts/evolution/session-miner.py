#!/usr/bin/env python3
"""
Session Miner - 跨Session模式挖掘 v3
从 LCM 数据库提取真实用户消息，过滤系统注入噪声，输出高频模式

数据源：~/.qclaw/memory/lossless/lcm.db
- conversations 表：session 列表
- messages 表：消息内容（role=user/assistant/system/tool）
"""
import json, os, sys, re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

# LCM 数据库路径（优先用 workspace 下的，备用 ~/.qclaw）
LCM_DB_ALT  = Path.home() / ".openclaw/workspace/~/.qclaw/memory/lossless/lcm.db"
LCM_DB_PRIMARY = Path.home() / ".qclaw/memory/lossless/lcm.db"
OUTPUT_DIR = Path.home() / ".openclaw/workspace/.state/evolution"

# ── 噪声黑名单 ──────────────────────────────────────────────
# 匹配到任一 pattern 的消息整条丢弃
NOISE_PATTERNS = [
    re.compile(r'^Read HEARTBEAT\.md', re.MULTILINE),           # 心跳探针
    re.compile(r'^Conversation info', re.MULTILINE),            # 元数据信封头
    re.compile(r'^\[HEARTBEAT[_\] ]', re.MULTILINE),           # 心跳标记
    re.compile(r'reply HEARTBEAT', re.IGNORECASE),              # 心跳响应
    re.compile(r'OpenClaw runtime context', re.IGNORECASE),     # 系统上下文注入
    re.compile(r'This context is runtime-generated', re.IGNORECASE),
    re.compile(r'\[Internal task completion', re.IGNORECASE),
    re.compile(r'\[Subagent Context\]', re.IGNORECASE),        # Subagent 启动消息
    re.compile(r'^An async command the user already approved', re.MULTILINE),
    re.compile(r'^<!\[CDATA\[', re.MULTILINE),                 # XML/CDATA 噪声
    re.compile(r'^```json', re.MULTILINE),                     # JSON 代码块
    re.compile(r'^```\w+', re.MULTILINE),                      # 任意代码块标记
    # 系统角色本身不是用户
    re.compile(r'^你是专业的', re.MULTILINE),                   # TD-AI 系统 prompt
    re.compile(r'^你的任务是分析用户', re.MULTILINE),            # TD-AI 切分任务
    re.compile(r'^## 🗺️ Scene Navigation', re.MULTILINE),      # 场景导航注入
    re.compile(r'^## Memory Tools', re.MULTILINE),              # 记忆工具指南
    re.compile(r'^## Path Variable Mappings', re.MULTILINE),    # 路径映射
    re.compile(r'^## Current Date', re.MULTILINE),              # 时间注入
    re.compile(r'^## Runtime', re.MULTILINE),                   # 运行时信息
    re.compile(r'^## Inbound Context', re.MULTILINE),           # 入站上下文
    re.compile(r'^## Project Context', re.MULTILINE),           # 项目上下文
    re.compile(r'^# Project Context', re.MULTILINE),            # 项目上下文变体
    re.compile(r'^system_prompt', re.MULTILINE),
    re.compile(r'^\{openclaw_', re.MULTILINE),                 # {openclaw_xxx} 占位符
    re.compile(r'\{bundled_skill_dir\}', re.IGNORECASE),
    re.compile(r'\{workspace_root_dir\}', re.IGNORECASE),
    re.compile(r'__import__|eval\(|exec\('),                   # 代码注入
]

# 英文停用词（短意图分析时过滤）
EN_STOP = {
    'the','a','an','is','are','was','were','be','been','being',
    'do','does','did','have','has','had','will','would','could',
    'should','may','might','can','in','on','at','to','for','of',
    'and','or','but','if','then','else','when','up','out',
    'so','no','not','as','it','its','this','that','these','those',
    'with','from','by','about','into','over','after','before',
}

# 纯噪声词：出现即丢弃整条
PURE_NOISE_TOKENS = {
    'reply HEARTBEAT_OK', 'HEARTBEAT_OK', '[HEARTBEAT',
    'System:', '"System":', 'conversation_id',
    'openclaw.weixin:', 'im.wechat',
}

# 已知是系统注入的 role（不是用户消息）
SYSTEM_ROLES = {'system', 'tool'}

def is_noise(text):
    """Return True if text is system-generated noise."""
    if not text or len(text.strip()) < 3:
        return True
    if len(text) > 20000:  # 超长系统上下文
        return True
    for token in PURE_NOISE_TOKENS:
        if token in text:
            return True
    for pat in NOISE_PATTERNS:
        if pat.search(text):
            return True
    return False

def get_db():
    """Try to connect to LCM db."""
    for p in [LCM_DB_PRIMARY, LCM_DB_ALT]:
        if p.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(str(p))
                conn.row_factory = sqlite3.Row
                return conn
            except Exception:
                pass
    return None

def extract_from_lcm(days=7):
    """从 LCM 数据库提取近 N 天用户消息。"""
    conn = get_db()
    if not conn:
        print("WARNING: LCM db not found, falling back to JSONL", file=sys.stderr)
        return []

    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.cursor()

    # 找主会话（排除 memory/session/cron 子 agent）
    cur.execute("""
        SELECT conversation_id, session_id, title, created_at
        FROM conversations
        WHERE created_at >= ?
        ORDER BY created_at DESC
    """, (cutoff,))
    convs = cur.fetchall()

    queries = []
    for conv in convs:
        cid = conv['conversation_id']
        sid = conv['session_id']

        # 排除 sub-agent session（session_id 含 memory/session/cron/subagent 等关键词）
        skip_keywords = ['memory', 'session-', 'cron:', 'subagent', 'l1-extraction', 'scene']
        if any(k in sid for k in skip_keywords):
            continue

        cur.execute("""
            SELECT message_id, content, role, created_at
            FROM messages
            WHERE conversation_id = ? AND role = 'user'
            ORDER BY message_id ASC
        """, (cid,))

        for row in cur.fetchall():
            text = (row['content'] or '').strip()
            if text and not is_noise(text):
                queries.append({'text': text, 'ts': row['created_at'], 'conv': cid})

    conn.close()
    return queries

def extract_from_jsonl(days=7):
    """Fallback：从 session JSONL 提取（质量较差）。"""
    SESSION_DIR = Path.home() / ".openclaw/agents/main/sessions"
    cutoff = datetime.now() - timedelta(days=days)
    queries = []

    if not SESSION_DIR.exists():
        return queries

    for f in SESSION_DIR.glob("*.jsonl"):
        # 按 mtime 过滤
        try:
            if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                continue
        except Exception:
            continue

        try:
            for line in open(f, encoding='utf-8'):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue

                # type=message 且 role=user
                if obj.get('type') == 'message':
                    msg = obj.get('message', {})
                    if msg.get('role') == 'user':
                        content = msg.get('content', [])
                        if isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get('type') == 'text':
                                    text = block.get('text', '').strip()
                                    if text and not is_noise(text):
                                        queries.append({'text': text, 'ts': obj.get('timestamp', '')})

                # type=text（旧格式兼容）
                elif obj.get('type') == 'text':
                    text = obj.get('text', '').strip()
                    if text and not is_noise(text):
                        queries.append({'text': text, 'ts': obj.get('timestamp', '')})
        except Exception:
            continue

    return queries

def extract_queries(days=7):
    """主入口：优先 LCM，回退 JSONL。"""
    q = extract_from_lcm(days)
    if not q:
        q = extract_from_jsonl(days)
    return q

def analyze(queries):
    """
    分析 queries 中的高频模式。
    策略：
    - 短意图（≤15字）：中文 2-gram；英文 1-gram（过滤停用词）
    - 中意图（16-40字）：中文保留完整短语；英文取 1-2 词
    - 高频中文词：全局 bigram 统计（来自全部文本合并）
    """
    chinese_chars = re.compile(r'[\u4e00-\u9fff]')
    chinese_bigrams_all = []

    short_chinese, short_english = [], []
    medium_chinese, medium_english = [], []

    for q in queries:
        text = q['text']

        # 分离中英文
        english_parts = re.findall(r'[a-zA-Z]{2,}', text)
        chinese_part  = ''.join(chinese_chars.findall(text))

        # 英文过滤停用词
        en_words = [w.lower() for w in english_parts if w.lower() not in EN_STOP]

        text_len = len(text)

        if text_len <= 15:
            for w in en_words:
                if 2 <= len(w) <= 8:
                    short_english.append(w)
            if chinese_part:
                for i in range(len(chinese_part) - 1):
                    bg = chinese_part[i:i+2]
                    if bg not in {'的是', '了的', '是在', '有的', '和的'}:
                        short_chinese.append(bg)

        elif text_len <= 40:
            for w in en_words[:2]:
                if 2 <= len(w) <= 12:
                    medium_english.append(w)
            if chinese_part and len(chinese_part) >= 2:
                medium_chinese.append(chinese_part[:8])

        # 收集所有汉字用于全局 bigram 统计
        chinese_bigrams_all.append(chinese_part)

    # 高频中文词：全局 bigram（来自合并全文）
    all_chinese = ''.join(chinese_bigrams_all)
    chinese_bigram_counter = Counter()
    for i in range(len(all_chinese) - 1):
        bg = all_chinese[i:i+2]
        if bg not in {'的是', '了的', '是在', '有的', '和的', '我你', '你他'}:
            chinese_bigram_counter[bg] += 1

    return {
        'total':    len(queries),
        'sessions': 0,  # 不再从 JSONL 统计 session 数
        'short':   (Counter(short_chinese).most_common(15) +
                    Counter(short_english).most_common(15))[:15],
        'medium':  (Counter(medium_chinese).most_common(10) +
                    Counter(medium_english).most_common(10))[:10],
        'chinese': chinese_bigram_counter.most_common(20),
    }

def get_recent_sessions(days=7):
    cutoff = datetime.now() - timedelta(days=days)
    SESSION_DIR = Path.home() / ".openclaw/agents/main/sessions"
    if not SESSION_DIR.exists():
        return []
    return [f for f in SESSION_DIR.glob("*.jsonl")
            if datetime.fromtimestamp(f.stat().st_mtime) >= cutoff]

def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7

    # 统计 session 数（从文件系统）
    sessions = get_recent_sessions(days)

    queries = extract_queries(days)
    r = analyze(queries)
    r['sessions'] = len(sessions)

    lines = [
        f"## 每日模式报告 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- 最近{days}天 {r['sessions']} 个Session文件，{r['total']}条有效Query",
        "",
        "### 高频意图（≤15字）",
    ]
    for p, c in r['short']:
        if c >= 2:
            lines.append(f"- {p} ×{c}")

    lines += ["", "### 描述性请求（16-40字）"]
    for p, c in r['medium']:
        if c >= 2:
            lines.append(f"- {p} ×{c}")

    lines += ["", "### 高频中文词"]
    for w, c in r['chinese']:
        if c >= 3:
            lines.append(f"- {w} ×{c}")

    report = "\n".join(lines)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "daily-mining.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(report)

if __name__ == "__main__":
    main()
