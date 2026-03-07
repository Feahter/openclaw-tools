#!/usr/bin/env python3
"""最简单的 OpenCode 桥接工具"""
import subprocess
import json
import sys
import os

WORKSPACE = "/Users/fuzhuo/.openclaw/workspace"
OPENCODE = "/Users/fuzhuo/.opencode/bin/opencode"

def run(cmd, timeout=120):
    env = os.environ.copy()
    env['PATH'] = "/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/bin:/Users/fuzhuo/.opencode/bin:" + env.get('PATH', '')
    
    result = subprocess.run(
        f'cd {WORKSPACE} && {OPENCODE} run "{cmd}"',
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env
    )
    
    out = result.stdout + result.stderr
    lines = out.strip().split('\n')
    return {"success": True, "output": '\n'.join(lines[-25:])}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command"}))
        sys.exit(1)
    
    cmd = ' '.join(sys.argv[1:])
    timeout = 120
    if '--timeout' in sys.argv:
        i = sys.argv.index('--timeout')
        if i+1 < len(sys.argv):
            timeout = int(sys.argv[i+1])
            cmd = cmd.replace('--timeout', '').replace(str(timeout), '').strip()
    
    print(json.dumps(run(cmd, timeout), ensure_ascii=False))
