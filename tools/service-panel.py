#!/usr/bin/env python3
"""
服务管理面板 - 子工具服务状态监控
URL: http://localhost:8773
"""

import http.server, socket, json
from pathlib import Path

PORT = 8773

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

if __name__ == "__main__":
    if not is_port_in_use(PORT):
        print(f"✅ 服务面板: http://localhost:{PORT}")
    else:
        print(f"端口 {PORT} 已被占用")
