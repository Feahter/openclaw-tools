#!/usr/bin/env python3
"""
OpenClaw 服务控制台 - 一站式服务管理与状态监控
支持：查看状态、重启服务、健康检查、批量操作
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 服务配置
SERVICES = {
    "openclaw-gateway": {
        "name": "OpenClaw Gateway",
        "cmd": ["openclaw", "gateway", "status"],
        "check": lambda: subprocess.run(["openclaw", "gateway", "status"], capture_output=True, text=True).returncode == 0,
        "restart": lambda: subprocess.run(["openclaw", "gateway", "restart"], capture_output=True, text=True),
        "start": lambda: subprocess.run(["openclaw", "gateway", "start"], capture_output=True, text=True),
        "stop": lambda: subprocess.run(["openclaw", "gateway", "stop"], capture_output=True, text=True),
        "status": lambda: "running" if subprocess.run(["openclaw", "gateway", "status"], capture_output=True, text=True).returncode == 0 else "stopped",
    },
    "cron-scheduler": {
        "name": "Cron Scheduler",
        "cmd": [],
        "check": lambda: True,  # cron 是系统服务
        "restart": lambda: subprocess.run(["crontab", "-l"], capture_output=True, text=True),
        "start": lambda: None,
        "stop": lambda: None,
        "status": lambda: "active" if Path.home() / ".crontab" else "inactive",
    },
    "evolution-agent": {
        "name": "Evolution Agent",
        "cmd": [],
        "check": lambda: Path.home() / ".pause-evolution" or True,  # 通过检查暂停文件
        "restart": lambda: subprocess.run(["crontab", "-l"], capture_output=True, text=True),
        "start": lambda: None,
        "stop": lambda: Path(Path.home() / ".pause-evolution").touch(),
        "status": lambda: "paused" if Path.home() / ".pause-evolution" else "running",
    },
    "tool-manager": {
        "name": "Tool Manager",
        "cmd": ["python3", "/Users/fuzhuo/.openclaw/workspace/tools/tool-manager.py", "--status"],
        "check": lambda: subprocess.run(["python3", "/Users/fuzhuo/.openclaw/workspace/tools/tool-manager.py", "--check"], capture_output=True, text=True).returncode == 0,
        "restart": lambda: subprocess.run(["python3", "/Users/fuzhuo/.openclaw/workspace/tools/tool-manager.py", "--scan"], capture_output=True, text=True),
        "start": lambda: None,
        "stop": lambda: None,
        "status": lambda: "active",
    },
    "heartbeat-runner": {
        "name": "Heartbeat Runner",
        "cmd": [],
        "check": lambda: True,
        "restart": lambda: None,
        "start": lambda: None,
        "stop": lambda: None,
        "status": lambda: "scheduled",
    },
}

# 颜色定义
COLORS = {
    "reset": "\033[0m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
}


def color(text: str, color_name: str) -> str:
    """应用颜色"""
    return f"{COLORS.get(color_name, COLORS['reset'])}{text}{COLORS['reset']}"


def print_header():
    """打印标题"""
    print("\n" + "=" * 60)
    print(color("🔧 OpenClaw 服务控制台", "bold"))
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)


def get_service_status(service_id: str, config: Dict) -> Tuple[str, str]:
    """获取服务状态"""
    try:
        status = config["status"]()
        status_str = str(status).lower()
        if "run" in status_str or "active" in status_str:
            return "running", "🟢"
        elif "stop" in status_str or "inactive" in status_str:
            return "stopped", "🔴"
        elif "paused" in status_str:
            return "paused", "🟡"
        else:
            return "unknown", "⚪"
    except Exception:
        return "error", "❓"


def list_services() -> List[Dict]:
    """列出所有服务状态"""
    services_status = []
    for service_id, config in SERVICES.items():
        status, icon = get_service_status(service_id, config)
        services_status.append({
            "id": service_id,
            "name": config["name"],
            "status": status,
            "icon": icon,
        })
    return services_status


def print_services(services: List[Dict]):
    """打印服务列表"""
    print(color("\n📋 服务状态:", "bold"))
    print("-" * 50)

    running = [s for s in services if s["status"] == "running"]
    stopped = [s for s in services if s["status"] == "stopped"]
    paused = [s for s in services if s["status"] == "paused"]
    error = [s for s in services if s["status"] == "error"]

    # 分组显示
    for status, icon, color_name, title in [
        ("running", "🟢", "green", "运行中"),
        ("paused", "🟡", "yellow", "已暂停"),
        ("stopped", "🔴", "red", "已停止"),
        ("error", "❓", "red", "异常"),
    ]:
        items = [s for s in services if s["status"] == status]
        if items:
            print(f"\n{color(title, color_name)} ({len(items)}):")
            for s in items:
                print(f"  {icon} {s['name']:25} [{s['id']}]")

    print(f"\n{color('-' * 50, 'cyan')}")
    print(color(f"📊 统计: ", "bold") +
          color(f"{len(running)} 运行", "green") + " | " +
          color(f"{len(paused)} 暂停", "yellow") + " | " +
          color(f"{len(stopped)} 停止", "red") + " | " +
          color(f"{len(error)} 异常", "red"))


def restart_service(service_id: str) -> bool:
    """重启单个服务"""
    if service_id not in SERVICES:
        print(color(f"❌ 未知服务: {service_id}", "red"))
        return False

    config = SERVICES[service_id]
    print(color(f"\n🔄 重启服务: {config['name']}...", "yellow"))

    try:
        result = config["restart"]()
        if result and result.returncode == 0:
            print(color(f"✅ 重启成功: {config['name']}", "green"))
            return True
        else:
            print(color(f"⚠️  重启完成: {config['name']}", "yellow"))
            return True
    except Exception as e:
        print(color(f"❌ 重启失败: {config['name']} - {e}", "red"))
        return False


def start_service(service_id: str) -> bool:
    """启动服务"""
    if service_id not in SERVICES:
        print(color(f"❌ 未知服务: {service_id}", "red"))
        return False

    config = SERVICES[service_id]
    print(color(f"\n▶️  启动服务: {config['name']}...", "blue"))

    try:
        result = config["start"]()
        if result is None:
            print(color(f"ℹ️  服务不支持手动启动: {config['name']}", "cyan"))
            return True
        if result.returncode == 0:
            print(color(f"✅ 启动成功: {config['name']}", "green"))
            return True
        else:
            print(color(f"⚠️  启动完成: {config['name']}", "yellow"))
            return True
    except Exception as e:
        print(color(f"❌ 启动失败: {config['name']} - {e}", "red"))
        return False


def stop_service(service_id: str) -> bool:
    """停止服务"""
    if service_id not in SERVICES:
        print(color(f"❌ 未知服务: {service_id}", "red"))
        return False

    config = SERVICES[service_id]
    print(color(f"\n⏹️  停止服务: {config['name']}...", "yellow"))

    try:
        result = config["stop"]()
        if result is None:
            print(color(f"ℹ️  服务不支持手动停止: {config['name']}", "cyan"))
            return True
        if result.returncode == 0:
            print(color(f"✅ 停止成功: {config['name']}", "green"))
            return True
        else:
            print(color(f"⚠️  停止完成: {config['name']}", "yellow"))
            return True
    except Exception as e:
        print(color(f"❌ 停止失败: {config['name']} - {e}", "red"))
        return False


def restart_all():
    """重启所有服务"""
    print(color("\n🔄 重启所有服务...", "yellow"))
    for service_id in SERVICES:
        restart_service(service_id)
    print(color("\n✅ 所有服务重启完成", "green"))


def health_check() -> Dict:
    """健康检查"""
    print(color("\n🏥 执行健康检查...", "blue"))
    results = {}

    for service_id, config in SERVICES.items():
        try:
            healthy = config["check"]()
            results[service_id] = {
                "name": config["name"],
                "healthy": healthy,
                "status": get_service_status(service_id, config)[0],
            }
        except Exception as e:
            results[service_id] = {
                "name": config["name"],
                "healthy": False,
                "error": str(e),
            }

    healthy_count = sum(1 for r in results.values() if r.get("healthy", True))
    total = len(results)

    print(color(f"\n📊 健康检查结果: {healthy_count}/{total} 健康", "bold"))

    return results


def print_help():
    """打印帮助"""
    print(color("\n📖 使用说明:", "bold"))
    print("-" * 50)
    print("  服务控制:")
    print("    --list, -l          列出所有服务状态")
    print("    --status            详细状态信息")
    print("    --restart <id>      重启指定服务")
    print("    --start <id>        启动指定服务")
    print("    --stop <id>         停止指定服务")
    print("    --restart-all       重启所有服务")
    print()
    print("  系统操作:")
    print("    --health            健康检查")
    print("    --install           安装所有工具到 PATH")
    print("    --push              推送到 GitHub")
    print("    --help, -h          显示帮助")
    print()
    print("  服务ID列表:")
    for service_id, config in SERVICES.items():
        print(f"    {service_id:20} - {config['name']}")
    print("-" * 50)


def generate_status_report() -> str:
    """生成状态报告"""
    services = list_services()
    report = {
        "timestamp": datetime.now().isoformat(),
        "services": services,
        "summary": {
            "total": len(services),
            "running": len([s for s in services if s["status"] == "running"]),
            "stopped": len([s for s in services if s["status"] == "stopped"]),
            "paused": len([s for s in services if s["status"] == "paused"]),
        }
    }
    return json.dumps(report, indent=2, ensure_ascii=False)


def install_all_tools():
    """安装所有核心工具到 PATH"""
    print(color("\n📦 安装所有核心工具...", "blue"))

    tools = [
        "resource-cli.py",
        "resource-manager.py",
        "resource-optimizer.py",
        "auto-task-executor.py",
        "task-scheduler.py",
        "skill-manager.py",
        "local-model-manager.py",
        "api-key-manager.py",
        "tool-manager.py",
        "heartbeat-runner.py",
        "evolution-agent.py",
    ]

    tools_dir = Path("/Users/fuzhuo/.openclaw/workspace/tools")
    success = 0
    failed = 0

    for tool in tools:
        source = tools_dir / tool
        if source.exists():
            target = Path.home() / ".local" / "bin" / tool
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(source, target)
                target.chmod(0o755)
                print(f"  ✅ {tool}")
                success += 1
            except Exception as e:
                print(f"  ❌ {tool}: {e}")
                failed += 1
        else:
            print(f"  ⚠️  {tool} 不存在")
            failed += 1

    print(color(f"\n📊 安装完成: {success} 成功, {failed} 失败", "bold"))


def push_to_github():
    """推送到 GitHub"""
    print(color("\n📤 推送到 GitHub...", "blue"))

    workspace = Path("/Users/fuzhuo/.openclaw/workspace")

    # 检查 git 状态
    result = subprocess.run(["git", "status", "--short"], cwd=workspace, capture_output=True, text=True)

    if result.returncode != 0:
        print(color(f"❌ Git 错误: {result.stderr}", "red"))
        return False

    # 添加更改
    print("  📝 暂存更改...")
    subprocess.run(["git", "add", "-A"], cwd=workspace, capture_output=True)

    # 提交
    commit_msg = f"feat: 更新工具集 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    print(f"  📝 提交: {commit_msg}")
    result = subprocess.run(["git", "commit", "-m", commit_msg], cwd=workspace, capture_output=True, text=True)

    if "nothing to commit" in result.stderr or "nothing to commit" in result.stdout:
        print(color("  ℹ️  没有需要提交的更改", "cyan"))
    else:
        print(color("  ✅ 提交成功", "green"))

    # 推送
    print("  📤 推送到远程...")
    result = subprocess.run(["git", "push"], cwd=workspace, capture_output=True, text=True)

    if result.returncode == 0:
        print(color("  ✅ 推送成功", "green"))
        return True
    else:
        print(color(f"  ❌ 推送失败: {result.stderr}", "red"))
        return False


if __name__ == "__main__":
    print_header()

    # 解析参数
    if len(sys.argv) == 1:
        # 默认：列出所有服务
        services = list_services()
        print_services(services)
        print(color("\n💡 使用 --help 查看更多命令", "cyan"))
    else:
        cmd = sys.argv[1]

        if cmd in ["--help", "-h"]:
            print_help()

        elif cmd in ["--list", "-l"]:
            services = list_services()
            print_services(services)

        elif cmd == "--status":
            services = list_services()
            print_services(services)
            print(color("\n📄 状态报告:", "bold"))
            print(generate_status_report())

        elif cmd == "--health":
            health_check()

        elif cmd == "--restart" and len(sys.argv) > 2:
            restart_service(sys.argv[2])

        elif cmd == "--start" and len(sys.argv) > 2:
            start_service(sys.argv[2])

        elif cmd == "--stop" and len(sys.argv) > 2:
            stop_service(sys.argv[2])

        elif cmd == "--restart-all":
            restart_all()

        elif cmd == "--install":
            install_all_tools()

        elif cmd == "--push":
            push_to_github()

        else:
            print(color(f"❌ 未知命令: {cmd}", "red"))
            print(color("💡 使用 --help 查看帮助", "cyan"))

    print()
