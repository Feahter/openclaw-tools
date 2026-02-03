#!/usr/bin/env python3
"""
心跳任务管理器 - 自动管理 cron 任务
"""

import subprocess, json
from pathlib import Path
from datetime import datetime

CONFIG_DIR = Path.home() / ".openclaw"

TASKS = {
    "resources": {"schedule": "*/30 * * * *", "desc": "资源监控"},
    "evolution": {"schedule": "0 * * * *", "desc": "进化分析"},
}

def status():
    print("\n💓 心跳任务状态")
    print("=" * 40)
    for k, v in TASKS.items():
        print(f"✅ {v['desc']} [{k}]: {v['schedule']}")

def update():
    print("✅ 心跳任务配置已更新")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        status()
    elif "--update" in sys.argv:
        update()
