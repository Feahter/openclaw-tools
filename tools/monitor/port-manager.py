#!/usr/bin/env python3
"""
🌟 Port Manager - 端口管理器

功能：
- 自动检测可用端口
- 防止端口冲突
- 管理工具服务的生命周期
- 支持优雅关闭和重启
"""

import socket
import json
import os
import signal
import atexit
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

# 配置
CONFIG_DIR = Path.home() / ".openclaw" / "data"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
PORT_FILE = CONFIG_DIR / "port-allocations.json"

# 保留端口范围 (8760-8799)
RESERVED_START = 8760
RESERVED_END = 8799

# 默认端口映射
DEFAULT_PORTS = {
    "local-model-manager": 8768,
    "task-board": 8769,
    "token-monitor": 8770,
    "api-auto-switch": 8771,
    "custom-tool": 8772,
}


class PortManager:
    """端口管理器"""

    def __init__(self):
        self.locked_ports = self.load_locks()
        self.processes = {}

    def load_locks(self) -> dict:
        """加载已锁定的端口"""
        if PORT_FILE.exists():
            with open(PORT_FILE) as f:
                return json.load(f)
        return {}

    def save_locks(self):
        """保存端口锁定状态"""
        # 清理已关闭的进程
        active = {}
        for name, info in self.locked_ports.items():
            pid = info.get("pid")
            if pid and self.is_process_alive(pid):
                active[name] = info
            elif not pid:  # 静态分配
                active[name] = info

        self.locked_ports = active

        with open(PORT_FILE, "w") as f:
            json.dump(active, f, indent=2)

    def is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False

    def find_available_port(self, base_port: int = None) -> int:
        """查找可用端口"""
        if base_port is None:
            base_port = RESERVED_START

        for port in range(base_port, RESERVED_END + 1):
            if port not in self.locked_ports and self.is_port_available(port):
                return port
        return None

    def lock_port(self, name: str, port: int, pid: int = None) -> bool:
        """锁定端口"""
        if port in self.locked_ports:
            existing = self.locked_ports[port]
            # 如果端口被同一个工具占用，检查进程是否存活
            if existing.get("name") == name:
                if pid and existing.get("pid"):
                    if not self.is_process_alive(existing["pid"]):
                        # 进程已死，清理并重新锁定
                        pass
                    else:
                        return port  # 端口已被占用
                return port

            # 端口被其他工具占用
            return False

        self.locked_ports[name] = {
            "port": port,
            "pid": pid,
            "name": name,
            "locked_at": datetime.now().isoformat()
        }
        self.save_locks()
        return True

    def unlock_port(self, name: str):
        """释放端口"""
        if name in self.locked_ports:
            pid = self.locked_ports[name].get("pid")
            if pid:
                self.kill_process(pid)
            del self.locked_ports[name]
            self.save_locks()

    def is_process_alive(self, pid: int) -> bool:
        """检查进程是否存活"""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def kill_process(self, pid: int):
        """终止进程"""
        try:
            os.kill(pid, signal.SIGTERM)
            # 等待进程结束
            for _ in range(10):
                if not self.is_process_alive(pid):
                    return
                time.sleep(0.1)
            # 强制终止
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass

    def register_process(self, name: str, pid: int, port: int):
        """注册进程"""
        self.locked_ports[name] = {
            "port": port,
            "pid": pid,
            "name": name,
            "registered_at": datetime.now().isoformat()
        }
        self.save_locks()

    def start_tool(self, name: str, script: str, workdir: str = None,
                   base_port: int = None, wait_ready: bool = True) -> dict:
        """
        启动工具并管理端口

        Args:
            name: 工具名称
            script: 启动脚本
            workdir: 工作目录
            base_port: 首选端口
            wait_ready: 等待服务就绪

        Returns:
            {"status": "started"|"error", "port": int, "pid": int, "url": str}
        """
        import subprocess
        import time
        import urllib.request

        # 查找可用端口
        port = self.find_available_port(base_port)
        if not port:
            return {"status": "error", "message": "没有可用端口"}

        # 检查是否已运行
        if name in self.locked_ports:
            existing = self.locked_ports[name]
            pid = existing.get("pid")
            if pid and self.is_process_alive(pid):
                return {
                    "status": "already_running",
                    "port": existing["port"],
                    "pid": pid,
                    "url": f"http://localhost:{existing['port']}"
                }

        # 启动进程
        cmd = ["python3", script]
        if workdir:
            cwd = workdir
        else:
            cwd = os.path.dirname(script) if os.path.dirname(script) else "."

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )

            # 等待服务就绪
            url = f"http://localhost:{port}"
            if wait_ready:
                for _ in range(30):  # 最多等 30 秒
                    try:
                        req = urllib.request.Request(url)
                        urllib.request.urlopen(req, timeout=2)
                        break
                    except:
                        time.sleep(1)

            # 注册进程
            self.register_process(name, proc.pid, port)

            return {
                "status": "started",
                "port": port,
                "pid": proc.pid,
                "url": url
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def stop_tool(self, name: str) -> bool:
        """停止工具"""
        if name in self.locked_ports:
            self.unlock_port(name)
            return True
        return False

    def stop_all(self):
        """停止所有工具"""
        for name in list(self.locked_ports.keys()):
            self.unlock_port(name)

    def status(self) -> dict:
        """获取状态"""
        return {
            "locked": dict(self.locked_ports),
            "available_ports": [p for p in range(RESERVED_START, RESERVED_END + 1)
                               if self.is_port_available(p)]
        }


# CLI 入口
def main():
    import argparse

    parser = argparse.ArgumentParser(description="🌟 Port Manager")
    parser.add_argument("action", choices=["status", "find", "lock", "unlock", "start", "stop", "stop-all"])
    parser.add_argument("--name", "-n", help="工具名称")
    parser.add_argument("--port", "-p", type=int, help="端口号")
    parser.add_argument("--script", "-s", help="启动脚本")

    args = parser.parse_args()

    pm = PortManager()

    if args.action == "status":
        status = pm.status()
        print("🔒 已锁定端口:")
        for name, info in status["locked"].items():
            print(f"  • {name}: {info['port']} (PID: {info.get('pid')})")
        print(f"\n可用端口: {status['available_ports']}")

    elif args.action == "find":
        port = pm.find_available_port(args.port)
        print(f"可用端口: {port}" if port else "无可用端口")

    elif args.action == "lock":
        if args.name and args.port:
            result = pm.lock_port(args.name, args.port)
            print(f"锁定{'成功' if result else '失败'}")

    elif args.action == "unlock":
        if args.name:
            pm.unlock_port(args.name)
            print("已释放")

    elif args.action == "start":
        if args.name and args.script:
            result = pm.start_tool(args.name, args.script, base_port=args.port)
            print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.action == "stop":
        if args.name:
            pm.stop_tool(args.name)
            print("已停止")

    elif args.action == "stop-all":
        pm.stop_all()
        print("已停止所有工具")


if __name__ == "__main__":
    main()
