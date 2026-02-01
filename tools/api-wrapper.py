#!/usr/bin/env python3
"""
API 调用包装器 - 自动记录 token 消耗
在调用 LLM API 前使用此包装器
"""

import subprocess
import sys

MONITOR_SCRIPT = "/Users/fuzhuo/.openclaw/workspace/tools/token-monitor.py"

def call_with_logging(provider, model, api_func, *args, **kwargs):
    """带日志记录的 API 调用"""
    import time
    start = time.time()
    
    # 调用实际 API
    result = api_func(*args, **kwargs)
    
    # 从结果提取 token 信息
    # 假设 result 是 dict，包含 usage 字段
    if isinstance(result, dict):
        usage = result.get("usage", {})
        prompt = usage.get("prompt_tokens", 0)
        completion = usage.get("completion_tokens", 0)
        cost = usage.get("cost", 0)
        
        # 记录
        subprocess.run([
            "python3", MONITOR_SCRIPT, "log",
            provider, model,
            str(prompt), str(completion), str(cost)
        ], capture_output=True)
    
    return result

if __name__ == "__main__":
    print("API 包装器 - 用于自动记录 token 消耗")
    print("用法: from api_wrapper import call_with_logging")
