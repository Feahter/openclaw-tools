#!/usr/bin/env python3
"""
algo_hunt_cron.py — 轻量算法发现，编程学习cron附加步骤。
在编程学习cron后执行，发现新算法→追加到skill-algo-master。

集成方式：在编程学习cron prompt末尾追加：
  "然后运行：python3 scripts/algo_hunt_cron.py"

独立运行：
  python3 scripts/algo_hunt_cron.py --dry-run  # 仅扫描不写日志
"""

import subprocess, sys

SKILL_DIR = __file__.rsplit("/", 1)[0].rsplit("/", 1)[0]
HUNTER = f"{SKILL_DIR}/skills/skill-algo-hunter/scripts/algo_hunter.py"

def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args

    cmd = ["python3", HUNTER] + args
    print(f"🕵️ 执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr[:500])
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
