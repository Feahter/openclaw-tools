#!/usr/bin/env python3
"""
OpenClaw Token 自动记录器
在 API 调用时自动记录 token 消耗，集成到工具箱
"""

import json
import sys
from pathlib import Path

# 注入到工具箱的启动器
INTEGRATION_CODE = '''
# === Token 自动记录集成 ===
import subprocess
import json
from datetime import datetime

TOKEN_MONITOR = "/Users/fuzhuo/.openclaw/workspace/tools/token-monitor.py"

def log_api_call(provider, model, prompt_tokens, completion_tokens, cost=0, session_key=None):
    """记录 API 调用"""
    try:
        cmd = [
            "python3", TOKEN_MONITOR, "log",
            provider, model,
            str(prompt_tokens), str(completion_tokens),
            str(cost)
        ]
        if session_key:
            cmd.append(session_key)
        subprocess.run(cmd, capture_output=True)
    except:
        pass  # 静默失败，不影响主流程

def check_and_optimize_context(messages, session_key=None):
    """检查上下文，必要时优化"""
    try:
        result = subprocess.run(
            ["python3", TOKEN_MONITOR, "check"],
            capture_output=True, text=True
        )
        return result.stdout
    except:
        return ""

def get_usage_report(hours=24):
    """获取消耗报告"""
    try:
        result = subprocess.run(
            ["python3", TOKEN_MONITOR, "recent", str(hours)],
            capture_output=True, text=True
        )
        return result.stdout
    except:
        return ""
'''

def integrate_to_launcher():
    """集成到 launcher.py"""
    launcher_path = Path("/Users/fuzhuo/.openclaw/workspace/tools/launcher.py")
    
    if not launcher_path.exists():
        print("launcher.py 不存在")
        return False
    
    content = launcher_path.read_text()
    
    if "TOKEN_MONITOR" in content:
        print("已集成 Token 记录器")
        return True
    
    # 在文件末尾添加集成代码
    content += "\n\n" + INTEGRATION_CODE
    
    launcher_path.write_text(content)
    print("✅ 已集成 Token 记录器到 launcher.py")
    return True

def create_wrapper_script():
    """创建包装脚本，用于在 API 调用时自动记录"""
    wrapper = '''#!/usr/bin/env python3
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
'''
    
    wrapper_path = Path("/Users/fuzhuo/.openclaw/workspace/tools/api-wrapper.py")
    wrapper_path.write_text(wrapper)
    wrapper_path.chmod(0o755)
    print(f"✅ 已创建包装器: {wrapper_path}")
    return True

def main():
    import sys
    
    print("🔧 Token Monitor 安装器")
    print("=" * 40)
    
    actions = {
        "1": ("集成到启动器", integrate_to_launcher),
        "2": ("创建 API 包装器", create_wrapper_script),
        "3": ("运行测试报告", lambda: subprocess.run(["python3", "/Users/fuzhuo/.openclaw/workspace/tools/token-monitor.py", "recent", "24"])),
        "4": ("检查上下文状态", lambda: subprocess.run(["python3", "/Users/fuzhuo/.openclaw/workspace/tools/token-monitor.py", "check"])),
        "5": ("全部安装", lambda: (integrate_to_launcher(), create_wrapper_script())),
    }
    
    if len(sys.argv) > 1:
        action = actions.get(sys.argv[1], actions["5"])
        action[1]()
    else:
        for k, (name, _) in actions.items():
            print(f"  {k}. {name}")
        print("\n选择要执行的操作")

if __name__ == "__main__":
    main()
