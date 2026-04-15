#!/usr/bin/env python3
"""
Cloudflare Worker Proxy — Fetch 模式调用器

注意：由于 macOS Python ssl 模块不支持 Cloudflare Workers 要求的 TLS 版本，
实际抓取由 proxy_fetch.js（Node.js）完成。

用法：
    python3 proxy_fetch.py <目标URL> [--max-chars N] [--proxy <代理URL>]

示例：
    python3 proxy_fetch.py https://github.com
    python3 proxy_fetch.py https://huggingface.co --max-chars 200000
"""

import subprocess
import sys
import os
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JS_SCRIPT = os.path.join(SCRIPT_DIR, "proxy_fetch.js")
DEFAULT_PROXY = "https://arthur-proxy.frankfeahter.workers.dev"


def main():
    args = sys.argv[1:]

    if not args or "--help" in args:
        print(__doc__)
        sys.exit(0)

    # 找到 Node.js
    node = shutil.which("node") or "/usr/local/bin/node"
    if not os.path.exists(node):
        print("ERROR: Node.js not found. Please install Node.js.", file=sys.stderr)
        sys.exit(1)

    # 构建 Node.js 调用参数
    js_args = [node, JS_SCRIPT] + args
    result = subprocess.run(js_args, capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
