#!/usr/bin/env python3
"""
OpenClaw 工具集启动器 (CLI版)
简单管理所有工具的启动和状态
"""

import subprocess
import os
import json
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "tools"
CONFIG_FILE = Path.home() / ".openclaw" / "tool-launcher.json"

TOOLS = [
    {
        "name": "🤖 模型管理 + 看板",
        "desc": "Ollama 本地模型 + API Keys + 任务看板",
        "script": "local-model-manager.py",
        "port": 8768,
        "url": "http://localhost:8768",
        "type": "web"
    },
    {
        "name": "🔑 API Key 管理",
        "desc": "多 Provider API Keys 管理",
        "script": "api-key-manager.py",
        "type": "cli",
        "params": ["list"]
    },
    {
        "name": "🔄 自动切换",
        "desc": "API 余额不足自动切换备用 Key",
        "script": "api-auto-switch.py",
        "type": "cli",
        "params": ["monitor"]
    },
    {
        "name": "🔍 API 扫描",
        "desc": "扫描收集免费/廉价 API",
        "script": "api-reserve-scanner.py",
        "type": "cli"
    },
    {
        "name": "⚙️ 安装开机启动",
        "desc": "重启后自动启动服务",
        "script": "install-launchd.sh",
        "type": "cli"
    },
]

def load_state():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"running": [], "port_status": {}}

def save_state(state):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(state, f)

def check_port(port):
    """检查端口是否被占用"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def start_tool(tool):
    """启动工具"""
    script = WORKSPACE / tool["script"]
    if not script.exists():
        print(f"❌ 脚本不存在: {script}")
        return False

    cmd = ["python3", str(script)]
    if "params" in tool:
        cmd.extend(tool["params"])

    try:
        if tool.get("type") == "web":
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ 已启动: {tool['name']} ({tool['url']})")
        else:
            subprocess.run(cmd)
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def status():
    """显示所有工具状态"""
    print("\n📊 OpenClaw 工具状态\n")
    print(f"{'工具':<25} {'状态':<10} {'地址'}")
    print("-" * 60)

    for tool in TOOLS:
        port = tool.get("port")
        if port and check_port(port):
            status_text = "✅ 运行中"
            url = tool.get("url", f"localhost:{port}")
        elif port:
            status_text = "⏸️ 已停止"
            url = f"localhost:{port}"
        else:
            status_text = "📝 CLI 工具"
            url = "-"

        print(f"{tool['name']:<25} {status_text:<10} {url}")

    print("\n📋 可用命令:")
    print("  run <编号>    - 启动工具")
    print("  start all     - 启动所有 Web 服务")
    print("  status        - 查看状态")
    print("  open <编号>   - 在浏览器打开")
    print("  quit/exit     - 退出")
    print()

def main():
    state = load_state()

    print("🔧 OpenClaw 工具集 (CLI版)")
    print("=" * 40)

    status()

    while True:
        try:
            cmd = input("命令> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见!")
            break

        if not cmd:
            continue

        parts = cmd.split()
        action = parts[0]

        if action in ["quit", "exit", "q"]:
            print("👋 再见!")
            break

        elif action == "status":
            status()

        elif action == "start":
            if len(parts) > 1 and parts[1] == "all":
                print("\n🚀 启动所有服务...")
                for tool in TOOLS:
                    if tool.get("type") == "web":
                        if not check_port(tool.get("port", 0)):
                            start_tool(tool)
                status()
            else:
                print("用法: start all")

        elif action == "run":
            if len(parts) != 2:
                print("用法: run <编号>")
                continue
            try:
                idx = int(parts[1]) - 1
                if 0 <= idx < len(TOOLS):
                    start_tool(TOOLS[idx])
                else:
                    print("❌ 无效编号")
            except ValueError:
                print("❌ 请输入数字")

        elif action == "open":
            if len(parts) != 2:
                print("用法: open <编号>")
                continue
            try:
                idx = int(parts[1]) - 1
                if 0 <= idx < len(TOOLS):
                    tool = TOOLS[idx]
                    if tool.get("url"):
                        import webbrowser
                        webbrowser.open(tool["url"])
                        print(f"🌐 已在浏览器打开: {tool['url']}")
                    else:
                        print("⚠️ 此工具没有 URL")
                else:
                    print("❌ 无效编号")
            except ValueError:
                print("❌ 请输入数字")

        else:
            print("❓ 未知命令。可用: status, start all, run <编号>, open <编号>, quit")

if __name__ == "__main__":
    main()
