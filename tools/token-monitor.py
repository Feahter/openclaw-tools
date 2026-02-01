#!/usr/bin/env python3
"""
Token 消耗监控器
记录 API 调用，统计 token 消耗，监控上下文大小
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 配置
WORKSPACE = "/Users/fuzhuo/.openclaw/workspace"
DATA_DIR = Path(WORKSPACE) / "data"
TOKEN_LOG_FILE = DATA_DIR / "token-usage.json"
SESSION_DIR = DATA_DIR / "sessions"
MAX_CONTEXT_TOKENS = 100000  # 上下文过大阈值
MAX_HISTORY_MESSAGES = 20    # 最大历史消息数

DATA_DIR.mkdir(parents=True, exist_ok=True)
SESSION_DIR.mkdir(parents=True, exist_ok=True)

def init_log():
    """初始化日志文件"""
    if not TOKEN_LOG_FILE.exists():
        TOKEN_LOG_FILE.write_text(json.dumps({"records": [], "daily_stats": {}}, indent=2))

def log_usage(provider: str, model: str, prompt_tokens: int, completion_tokens: int, 
              cost: float, session_key: str = None, message_type: str = "chat"):
    """记录一次 API 调用"""
    now = datetime.now()
    date_key = now.strftime("%Y-%m-%d")
    hour_key = now.strftime("%Y-%m-%d %H:00")
    
    record = {
        "timestamp": now.isoformat(),
        "date": date_key,
        "hour": hour_key,
        "provider": provider,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "cost": cost,
        "session_key": session_key,
        "message_type": message_type
    }
    
    # 读取现有数据
    data = json.loads(TOKEN_LOG_FILE.read_text())
    
    # 添加记录
    data["records"].append(record)
    
    # 更新每日统计
    if date_key not in data["daily_stats"]:
        data["daily_stats"][date_key] = {"total_tokens": 0, "cost": 0, "requests": 0, "by_provider": {}}
    
    stats = data["daily_stats"][date_key]
    stats["total_tokens"] += record["total_tokens"]
    stats["cost"] += cost
    stats["requests"] += 1
    
    if provider not in stats["by_provider"]:
        stats["by_provider"][provider] = {"tokens": 0, "cost": 0, "requests": 0}
    
    pstats = stats["by_provider"][provider]
    pstats["tokens"] += record["total_tokens"]
    pstats["cost"] += cost
    pstats["requests"] += 1
    
    # 只保留最近 30 天的数据
    cutoff = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    data["daily_stats"] = {k: v for k, v in data["daily_stats"].items() if k >= cutoff}
    data["records"] = [r for r in data["records"] if r["date"] >= cutoff]
    
    # 写入文件
    TOKEN_LOG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    return record

def get_daily_stats(date: str = None):
    """获取每日统计"""
    data = json.loads(TOKEN_LOG_FILE.read_text())
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    return data["daily_stats"].get(date, {"total_tokens": 0, "cost": 0, "requests": 0})

def get_recent_usage(hours: int = 24):
    """获取最近 N 小时的消耗"""
    cutoff = datetime.now() - timedelta(hours=hours)
    data = json.loads(TOKEN_LOG_FILE.read_text())
    
    recent = [r for r in data["records"] if datetime.fromisoformat(r["timestamp"]) > cutoff]
    
    total_prompt = sum(r["prompt_tokens"] for r in recent)
    total_completion = sum(r["completion_tokens"] for r in recent)
    total_cost = sum(r["cost"] for r in recent)
    
    by_provider = defaultdict(lambda: {"prompt": 0, "completion": 0, "cost": 0})
    for r in recent:
        by_provider[r["provider"]]["prompt"] += r["prompt_tokens"]
        by_provider[r["provider"]]["completion"] += r["completion_tokens"]
        by_provider[r["provider"]]["cost"] += r["cost"]
    
    return {
        "period_hours": hours,
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_tokens": total_prompt + total_completion,
        "total_cost": total_cost,
        "by_provider": dict(by_provider),
        "records": recent[-50:]  # 最近 50 条
    }

def check_context_size(messages: list, session_key: str = None) -> dict:
    """检查上下文大小，返回状态和建议"""
    # 简单估算：平均每个 token 约 4 字符
    content = json.dumps(messages)
    estimated_tokens = len(content) // 4
    
    status = "ok"
    actions = []
    
    if estimated_tokens > MAX_CONTEXT_TOKENS:
        status = "warning"
        actions.append(f"⚠️ 上下文过大 ({estimated_tokens:,} tokens)")
        actions.append(f"建议: 减少历史消息至 {MAX_HISTORY_MESSAGES} 条以内")
    
    if len(messages) > MAX_HISTORY_MESSAGES:
        status = "warning"
        actions.append(f"📝 历史消息过多 ({len(messages)} 条)")
        actions.append(f"建议: 保留最近 {MAX_HISTORY_MESSAGES} 条，压缩早期内容")
    
    return {
        "estimated_tokens": estimated_tokens,
        "message_count": len(messages),
        "status": status,
        "actions": actions,
        "session_key": session_key
    }

def optimize_history(messages: list, keep_last: int = MAX_HISTORY_MESSAGES) -> list:
    """优化历史消息，自动减负"""
    if len(messages) <= keep_last:
        return messages
    
    # 保留系统提示 + 最近 N 条
    optimized = messages[:1] + messages[-keep_last+1:] if messages else messages
    
    # 如果第一条是系统消息，保留；否则从后往前保留
    if not optimized or optimized[0].get("role") != "system":
        optimized = messages[-keep_last:]
    
    return optimized

def save_session_history(session_key: str, messages: list, token_count: int = 0):
    """保存会话历史"""
    session_file = SESSION_DIR / f"{session_key}.json"
    session_data = {
        "session_key": session_key,
        "saved_at": datetime.now().isoformat(),
        "message_count": len(messages),
        "estimated_tokens": token_count,
        "messages": messages[-50:]  # 只保存最近 50 条
    }
    session_file.write_text(json.dumps(session_data, indent=2, ensure_ascii=False))

def get_session_history(session_key: str) -> list:
    """获取会话历史"""
    session_file = SESSION_DIR / f"{session_key}.json"
    if session_file.exists():
        data = json.loads(session_file.read_text())
        return data.get("messages", [])
    return []

def print_usage_report(usage: dict):
    """打印消耗报告"""
    print(f"\n📊 Token 消耗报告 (最近 {usage['period_hours']} 小时)")
    print("=" * 50)
    print(f"总消耗 Tokens: {usage['total_tokens']:,}")
    print(f"  - Prompt: {usage['total_prompt_tokens']:,}")
    print(f"  - Completion: {usage['total_completion_tokens']:,}")
    print(f"总费用: ${usage['total_cost']:.4f}")
    print("\n按 Provider:")
    for provider, stats in usage["by_provider"].items():
        print(f"  {provider}: {stats['prompt']+stats['completion']:,} tokens, ${stats['cost']:.4f}")
    print(f"\n最近 {len(usage['records'])} 条记录")

def main():
    import sys
    
    init_log()
    
    if len(sys.argv) < 2:
        print("Token Monitor - Token 消耗监控")
        print("\n用法:")
        print("  python3 token-monitor.py log <provider> <model> <prompt> <completion> [cost] [session]")
        print("  python3 token-monitor.py daily          # 今日统计")
        print("  python3 token-monitor.py recent [hours] # 最近消耗")
        print("  python3 token-monitor.py check          # 检查当前会话")
        print("  python3 token-monitor.py optimize <file> # 优化历史文件")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "daily":
        stats = get_daily_stats()
        print(f"\n📊 今日统计")
        print(f"总 Tokens: {stats['total_tokens']:,}")
        print(f"总请求: {stats['requests']}")
        print(f"总费用: ${stats['cost']:.4f}")
        for provider, ps in stats.get("by_provider", {}).items():
            print(f"  {provider}: {ps['tokens']:,} tokens, ${ps['cost']:.4f}")
    
    elif cmd == "recent":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        usage = get_recent_usage(hours)
        print_usage_report(usage)
    
    elif cmd == "log":
        # python3 token-monitor.py log <provider> <model> <prompt_tokens> <completion_tokens> [cost] [session]
        provider = sys.argv[2]
        model = sys.argv[3]
        prompt = int(sys.argv[4])
        completion = int(sys.argv[5])
        cost = float(sys.argv[6]) if len(sys.argv) > 6 else 0
        session = sys.argv[7] if len(sys.argv) > 7 else None
        
        record = log_usage(provider, model, prompt, completion, cost, session)
        print(f"✅ 已记录: {provider}/{model} - {record['total_tokens']:,} tokens")
    
    elif cmd == "check":
        # 检查当前会话大小
        print("\n🔍 检查会话上下文大小...")
        print(f"阈值: {MAX_CONTEXT_TOKENS:,} tokens")
        print(f"最大历史消息: {MAX_HISTORY_MESSAGES} 条")
        
        # 检查所有 session 文件
        total_tokens = 0
        session_count = 0
        for f in SESSION_DIR.glob("*.json"):
            data = json.loads(f.read_text())
            tokens = data.get("estimated_tokens", 0)
            total_tokens += tokens
            session_count += 1
            if tokens > MAX_CONTEXT_TOKENS:
                print(f"  ⚠️ {f.name}: {tokens:,} tokens")
        
        print(f"\n总计: {session_count} 个会话, 约 {total_tokens:,} tokens")
    
    elif cmd == "optimize":
        if len(sys.argv) > 2:
            file_path = sys.argv[2]
            if os.path.exists(file_path):
                messages = json.loads(open(file_path).read())
                optimized = optimize_history(messages)
                print(f"原始: {len(messages)} 条")
                print(f"优化后: {len(optimized)} 条")
                # 输出到 stdout
                print("\n" + json.dumps(optimized, ensure_ascii=False, indent=2))
            else:
                print(f"文件不存在: {file_path}")
        else:
            print("用法: python3 token-monitor.py optimize <file>")
    
    else:
        print(f"未知命令: {cmd}")
        print("用 python3 token-monitor.py 查看帮助")

if __name__ == "__main__":
    main()
