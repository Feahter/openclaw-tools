#!/usr/bin/env python3
"""
MVP 发布管理器 - 版本管理与 GitHub 发布
"""

import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
VERSION_FILE = WORKSPACE / "VERSION"

def get_version():
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "0.0.0"

def release():
    v = get_version()
    print(f"🚀 当前版本: {v}")
    print("使用 --prepare 准备发布，--release 执行发布")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        release()
