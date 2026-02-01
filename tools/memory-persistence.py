#!/usr/bin/env python3
"""
内存持久化 Hook
自动保存/加载会话上下文，避免每次从头开始
"""

import json
import os
from pathlib import Path
from datetime import datetime

# 配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
STATE_FILE = MEMORY_DIR / "session-state.json"

# 上次会话的上下文
LAST_SESSION_FILE = WORKSPACE / ".last-session.json"

def save_session_context(session_id: str, summary: str = "", tools_used: list = None):
    """保存当前会话上下文"""
    state = {
        "last_session_id": session_id,
        "last_session_time": datetime.now().isoformat(),
        "summary": summary,
        "tools_used": tools_used or [],
        "continuation": True
    }
    
    try:
        with open(LAST_SESSION_FILE, 'w') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存会话上下文失败: {e}")
        return False

def load_session_context():
    """加载上次会话上下文"""
    if not LAST_SESSION_FILE.exists():
        return None
    
    try:
        with open(LAST_SESSION_FILE) as f:
            return json.load(f)
    except:
        return None

def check_continuation_needed():
    """检查是否需要恢复上下文"""
    context = load_session_context()
    if not context:
        return None
    
    # 如果超过 2 小时，认为需要重新开始
    last_time = datetime.fromisoformat(context.get("last_session_time", "2000-01-01"))
    hours_since = (datetime.now() - last_time).total_seconds() / 3600
    
    if hours_since > 2:
        return None
    
    return context

def clear_session_context():
    """清除会话上下文（重新开始对话时）"""
    if LAST_SESSION_FILE.exists():
        LAST_SESSION_FILE.unlink()
        return True
    return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "save":
            session_id = sys.argv[2] if len(sys.argv) > 2 else "unknown"
            summary = sys.argv[3] if len(sys.argv) > 3 else ""
            save_session_context(session_id, summary)
            print("✅ 会话上下文已保存")
        
        elif cmd == "load":
            context = load_session_context()
            if context:
                print(json.dumps(context, indent=2, ensure_ascii=False))
            else:
                print("无上下文")
        
        elif cmd == "check":
            context = check_continuation_needed()
            if context:
                print("需要恢复上下文")
                print(json.dumps(context, indent=2, ensure_ascii=False))
            else:
                print("无需恢复")
        
        elif cmd == "clear":
            clear_session_context()
            print("✅ 上下文已清除")
        
        else:
            print("用法: python3 memory-persistence.py [save|load|check|clear]")
    else:
        print("内存持久化 Hook")
        print("用法: python3 memory-persistence.py [save|load|check|clear]")
