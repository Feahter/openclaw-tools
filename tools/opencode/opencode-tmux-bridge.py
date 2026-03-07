#!/usr/bin/env python3
"""
OpenCode + Tmux 桥接工具 - 整合版
基于高星 tmux skill 的最佳实践
"""
import subprocess
import json
import sys
import os
import time
import signal
from pathlib import Path

# 配置
SOCKET_DIR = os.environ.get("CLAWDBOT_TMUX_SOCKET_DIR", f"{os.environ.get('TMPDIR', '/tmp')}/opencode-tmux-sockets")
SOCKET = f"{SOCKET_DIR}/opencode.sock"
SESSION = "opencode"
WORKSPACE = "/Users/fuzhuo/.openclaw/workspace"
OPENCODE = "/Users/fuzhuo/.opencode/bin/opencode"
TIMEOUT = 300

def run_cmd(cmd, timeout=30, capture=True):
    """执行命令"""
    env = os.environ.copy()
    env['PATH'] = "/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/bin:/Users/fuzhuo/.opencode/bin:" + env.get('PATH', '')
    
    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=capture,
            text=True,
            timeout=timeout,
            env=env,
            cwd=WORKSPACE
        )
        return result
    except subprocess.TimeoutExpired:
        return None

def ensure_socket():
    """确保 socket 目录存在"""
    os.makedirs(SOCKET_DIR, exist_ok=True)

def ensure_session():
    """确保 tmux 会话存在"""
    ensure_socket()
    
    # 检查会话是否存在
    result = run_cmd(f'tmux -S {SOCKET} has-session -t {SESSION} 2>/dev/null', timeout=5)
    if result and result.returncode != 0:
        # 创建新会话
        run_cmd(f'tmux -S {SOCKET} new-session -d -s {SESSION} -n shell')
        time.sleep(1)
        # 切换到工作目录
        run_cmd(f'tmux -S {SOCKET} send-keys -t {SESSION} "cd {WORKSPACE}" C-m')
        time.sleep(1)

def send_command(command):
    """发送命令到 tmux 会话"""
    ensure_session()
    
    # 发送命令
    cmd = f'{OPENCODE} run "{command}"'
    run_cmd(f'tmux -S {SOCKET} send-keys -t {SESSION} {cmd} C-m')
    
    return True

def get_output(wait=10):
    """获取会话输出"""
    time.sleep(wait)
    result = run_cmd(f'tmux -S {SOCKET} capture-pane -p -J -t {SESSION} -S -200', timeout=15)
    if result:
        return result.stdout
    return ""

def list_sessions():
    """列出所有会话"""
    result = run_cmd(f'tmux -S {SOCKET} list-sessions 2>/dev/null')
    if result and result.returncode == 0:
        return result.stdout.strip()
    return "No sessions"

def kill_session():
    """杀死会话"""
    run_cmd(f'tmux -S {SOCKET} kill-session -t {SESSION} 2>/dev/null')

def run_single_task(command, timeout=TIMEOUT):
    """运行单次任务（绕过 tmux，直接用 shell）"""
    env = os.environ.copy()
    env['PATH'] = "/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/bin:/Users/fuzhuo/.opencode/bin:" + env.get('PATH', '')
    
    cmd = f'cd {WORKSPACE} && {OPENCODE} run "{command}"'
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=WORKSPACE
        )
        
        output = result.stdout + result.stderr
        lines = output.strip().split('\n')
        
        return {
            "success": True,
            "output": '\n'.join(lines[-30:])
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "No command provided",
            "usage": "python opencode-tmux-bridge.py 'task' [--timeout 180]"
        }))
        sys.exit(1)
    
    command = ' '.join(sys.argv[1:])
    timeout = TIMEOUT
    
    # 解析 --timeout
    if '--timeout' in sys.argv:
        idx = sys.argv.index('--timeout')
        if idx + 1 < len(sys.argv):
            try:
                timeout = int(sys.argv[idx + 1])
                command = command.replace('--timeout', '').replace(str(timeout), '').strip()
            except:
                pass
    
    # 使用单次任务模式（更稳定）
    result = run_single_task(command, timeout)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
