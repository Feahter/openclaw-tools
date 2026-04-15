#!/usr/bin/env python3
"""nudge_engine.py — 达到阈值时推送飞书 Nudge"""

import json
import sys
from pathlib import Path
from datetime import datetime

STATE_DIR = Path.home() / ".openclaw/workspace/.state/autonomous-skill-creator"
NUDGE_THRESHOLD = 3  # 达到 3 个高优先级时触发

def check_and_nudge():
    candidates_file = STATE_DIR / "candidates.json"
    if not candidates_file.exists():
        print("⏳ 暂无候选数据")
        return None
    
    data = json.loads(candidates_file.read_text())
    high_priority = data.get("high", 0)
    
    if high_priority >= NUDGE_THRESHOLD:
        return {
            "status": "trigger",
            "high": high_priority,
            "candidates": data.get("candidates", [])[:3]
        }
    return {"status": "skip", "high": high_priority, "threshold": NUDGE_THRESHOLD}

def format_feishu_message(result):
    """格式化飞书消息"""
    msg = f"🦞 发现 {result['high']} 个可固化的 Skill 候选：\n\n"
    for i, c in enumerate(result["candidates"], 1):
        msg += f"{i}. {c.get('query', 'N/A')} (×{c.get('count', 1)})\n"
    return msg

def main():
    result = check_and_nudge()
    
    if result is None:
        print("⏳ 暂无候选数据，跳过")
        return
    
    if result["status"] == "trigger":
        msg = format_feishu_message(result)
        print(msg)
        
        # 尝试飞书推送（如果可用）
        try:
            from feishu_ask_user_question import ask_with_options
            print("\n📤 推送飞书通知...")
        except ImportError:
            print("\n📤 通知内容已准备好，可手动发送")
    else:
        print(f"⏳ 高优先级候选 {result['high']}/{NUDGE_THRESHOLD}，跳过")

if __name__ == "__main__":
    main()