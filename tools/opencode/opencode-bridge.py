#!/usr/bin/env python3
"""
OpenCode 桥接工具 v2 - 优化版
解决：PATH、超时、Shell 初始化问题
"""
import subprocess
import json
import sys
import os
import time
import threading
from pathlib import Path

# 配置
OPENCODE_PATH = "/Users/fuzhuo/.opencode/bin/opencode"
WORKSPACE = "/Users/fuzhuo/.openclaw/workspace"
TIMEOUT = 300  # 5分钟超时

def run_opencode(command: str, timeout: int = TIMEOUT) -> dict:
    """
    执行 OpenCode 命令并返回结果
    """
    # 构建环境变量
    env = os.environ.copy()
    # 确保 PATH 包含 OpenCode 和系统命令
    env['PATH'] = f"{os.environ.get('HOME')}/.opencode/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/bin:{env.get('PATH', '')}"
    # 禁用某些可能干扰的环境变量
    env.pop('TMPDIR', None)
    
    # 构建命令 - 使用 -l 登录 shell 确保加载配置
    cmd = [
        'zsh', '-l', '-c',  # 登录 shell 加载配置
        f'cd {WORKSPACE} && {OPENCODE_PATH} run "{command}"'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=WORKSPACE
        )
        
        # 解析输出
        output = result.stdout + result.stderr
        
        # 检查是否成功
        if result.returncode == 0:
            # 提取关键结果（最后几行）
            lines = output.strip().split('\n')
            # 找到实际回复内容
            response_lines = []
            in_response = False
            for line in lines:
                if '→' in line or '✱' in line:
                    in_response = True
                if in_response:
                    response_lines.append(line)
            
            return {
                "success": True,
                "output": '\n'.join(response_lines[-10:]) if response_lines else output[-500:],
                "full_output": output[-2000:]
            }
        else:
            return {
                "success": False,
                "error": output[-500:],
                "code": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Timeout after {timeout}s",
            "code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "code": -2
        }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided. Usage: opencode-bridge.py 'your task'"}))
        sys.exit(1)
    
    command = ' '.join(sys.argv[1:])
    
    # 支持 --timeout 参数
    timeout = TIMEOUT
    if '--timeout' in sys.argv:
        idx = sys.argv.index('--timeout')
        if idx + 1 < len(sys.argv):
            timeout = int(sys.argv[idx + 1])
            command = command.replace('--timeout', '').replace(str(timeout), '').strip()
    
    result = run_opencode(command, timeout)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
