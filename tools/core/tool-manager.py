#!/usr/bin/env python3
"""
工具集管家Agent - 统一管理系统工具与技能
"""

import os
import json
import subprocess
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 配置
TOOLS_DIR = Path("/Users/fuzhuo/.openclaw/workspace/tools")
SKILLS_DIR = Path("/Users/fuzhuo/.openclaw/workspace/skills")
INVENTORY_FILE = Path.home() / ".tool-inventory.json"
LOG_FILE = Path.home() / ".tool-manager.log"


class ToolManager:
    def __init__(self):
        self.inventory = self._load_inventory()
        self.changes = []

    def _load_inventory(self) -> Dict:
        """加载工具清单"""
        if INVENTORY_FILE.exists():
            return json.loads(INVENTORY_FILE.read_text())
        return {"tools": {}, "skills": {}, "last_scan": None}

    def _save_inventory(self):
        """保存工具清单"""
        self.inventory["last_scan"] = datetime.now().isoformat()
        INVENTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        INVENTORY_FILE.write_text(json.dumps(self.inventory, indent=2, ensure_ascii=False))

    def log(self, msg: str, level: str = "INFO"):
        """日志记录"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {msg}"
        print(entry)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(entry + "\n")

    def scan_tools(self) -> Dict:
        """扫描工具目录"""
        tools = {}
        for f in TOOLS_DIR.iterdir():
            if f.is_file() and f.suffix == ".py":
                tools[f.name] = self._analyze_tool(f)
            elif f.is_file() and f.stat().st_mode & 0o111:  # 可执行
                tools[f.name] = self._analyze_tool(f)
        return tools

    def scan_skills(self) -> Dict:
        """扫描技能目录"""
        skills = {}
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir():
                skill_info = {
                    "name": skill_dir.name,
                    "path": str(skill_dir),
                    "files": [],
                    "has_skill_md": (skill_dir / "SKILL.md").exists(),
                }
                for f in skill_dir.rglob("*"):
                    if f.is_file():
                        skill_info["files"].append(f.name)
                skills[skill_dir.name] = skill_info
        return skills

    def _analyze_tool(self, path: Path) -> Dict:
        """分析单个工具"""
        info = {
            "path": str(path),
            "name": path.name,
            "size": path.stat().st_size,
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "hash": hashlib.md5(path.read_bytes()).hexdigest()[:8],
            "category": self._guess_category(path.name),
        }
        # 检查依赖
        content = path.read_text() if path.is_file() else ""
        imports = []
        for line in content.split("\n"):
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line.strip())
        info["imports"] = imports[:5]  # 限制数量
        return info

    def _guess_category(self, name: str) -> str:
        """猜测工具类别"""
        categories = {
            "FLOW": ["executor", "scheduler", "worker"],
            "ANALYZE": ["analyzer", "inspector", "monitor"],
            "MAINT": ["manager", "maintainer", "cleanup", "repair"],
            "CORE": ["gateway", "resource", "heartbeat"],
        }
        name_lower = name.lower()
        for cat, keywords in categories.items():
            for kw in keywords:
                if kw in name_lower:
                    return cat
        return "GENERAL"

    def check_health(self) -> Dict[str, List[str]]:
        """健康检查"""
        results = {"healthy": [], "warning": [], "broken": []}

        # 检查工具
        for name, info in self.inventory.get("tools", {}).items():
            path = Path(info["path"])
            if not path.exists():
                results["broken"].append(f"工具不存在: {name}")
            elif path.stat().st_size == 0:
                results["warning"].append(f"工具为空: {name}")
            else:
                # 尝试语法检查
                try:
                    if path.suffix == ".py":
                        result = subprocess.run(
                            ["python3", "-m", "py_compile", str(path)],
                            capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            results["healthy"].append(name)
                        else:
                            results["warning"].append(f"语法错误: {name}")
                    else:
                        results["healthy"].append(name)
                except Exception as e:
                    results["warning"].append(f"检查异常: {name} ({e})")

        # 检查技能
        for name, info in self.inventory.get("skills", {}).items():
            if not info.get("has_skill_md"):
                results["warning"].append(f"技能缺少 SKILL.md: {name}")
            else:
                results["healthy"].append(f"skill:{name}")

        return results

    def install_tool(self, tool_name: str) -> bool:
        """安装工具到 PATH"""
        source = TOOLS_DIR / tool_name
        if not source.exists():
            self.log(f"工具不存在: {tool_name}", "ERROR")
            return False

        # 查找可执行目标
        targets = [
            Path("/usr/local/bin"),
            Path.home() / ".local/bin",
        ]

        installed = False
        for target_dir in targets:
            target = target_dir / tool_name
            try:
                if str(target_dir).startswith("/usr") and os.geteuid() != 0:
                    continue  # 需要 root 权限
                target_dir.mkdir(parents=True, exist_ok=True)
                # 复制并设置权限
                shutil.copy2(source, target)
                if source.suffix not in ['.sh', '.js']:
                    target.chmod(0o755)

                self.changes.append({
                    "action": "install",
                    "tool": tool_name,
                    "target": str(target)
                })
                self.log(f"已安装: {tool_name} -> {target}")
                installed = True
                break
            except PermissionError:
                self.log(f"权限不足，无法写入: {target}", "WARN")
                continue
            except Exception as e:
                self.log(f"安装失败: {tool_name} - {e}", "ERROR")

        if not installed:
            self.log(f"无法安装 {tool_name}，所有目标目录都无权限", "ERROR")

        return installed

    def uninstall_tool(self, tool_name: str) -> bool:
        """从 PATH 卸载工具"""
        targets = [
            Path("/usr/local/bin") / tool_name,
            Path.home() / ".local/bin" / tool_name,
        ]

        removed = False
        for target in targets:
            try:
                if target.exists():
                    target.unlink()
                    self.changes.append({
                        "action": "uninstall",
                        "tool": tool_name,
                        "target": str(target)
                    })
                    self.log(f"已卸载: {tool_name}")
                    removed = True
            except PermissionError:
                self.log(f"权限不足，无法卸载: {target}", "WARN")
            except Exception as e:
                self.log(f"卸载失败: {tool_name} - {e}", "ERROR")

        if not removed:
            self.log(f"未找到已安装的: {tool_name}", "WARN")

        return removed

    def full_scan(self):
        """完整扫描"""
        self.log("开始完整扫描...")
        self.inventory["tools"] = self.scan_tools()
        self.inventory["skills"] = self.scan_skills()
        self._save_inventory()

        health = self.check_health()
        self.log(f"扫描完成: {len(self.inventory['tools'])} 工具, {len(self.inventory['skills'])} 技能")

        return self._format_report(health)

    def _format_report(self, health: Dict) -> str:
        """格式化报告"""
        total = sum(len(v) for v in health.values())
        lines = [
            "=" * 50,
            "🧰 工具集状态报告",
            f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 50,
            f"📦 工具/技能总数: {total}",
            f"   ✅ 正常: {len(health['healthy'])}",
            f"   ⚠️  警告: {len(health['warning'])}",
            f"   ❌ 故障: {len(health['broken'])}",
            "-" * 50,
        ]

        if health["warning"]:
            lines.append("\n⚠️  警告项:")
            for item in health["warning"][:10]:
                lines.append(f"   - {item}")
            if len(health["warning"]) > 10:
                lines.append(f"   ... 共 {len(health['warning'])} 项")

        if health["broken"]:
            lines.append("\n❌ 故障项:")
            for item in health["broken"][:10]:
                lines.append(f"   - {item}")

        return "\n".join(lines)

    def audit(self) -> Dict:
        """完整审计"""
        report = self.full_scan()
        print(report)

        # 额外分析
        analysis = {
            "largest_tools": [],
            "unused_tools": [],
            "dependencies": {},
        }

        # 最大工具
        tools = self.inventory.get("tools", {})
        sorted_tools = sorted(tools.items(), key=lambda x: x[1].get("size", 0), reverse=True)
        analysis["largest_tools"] = [(n, info["size"]) for n, info in sorted_tools[:5]]

        return {
            "report": report,
            "analysis": analysis,
            "inventory": self.inventory
        }


def log(msg: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")


if __name__ == "__main__":
    import sys

    manager = ToolManager()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "--check":
            health = manager.check_health()
            print(f"✅ 正常: {len(health['healthy'])}")
            print(f"⚠️  警告: {len(health['warning'])}")
            print(f"❌ 故障: {len(health['broken'])}")

        elif cmd == "--update":
            manager.log("检查更新...")
            manager.full_scan()

        elif cmd == "--audit":
            result = manager.audit()
            log("审计完成")

        elif cmd == "--scan":
            manager.full_scan()

        elif cmd == "--install" and len(sys.argv) > 2:
            tool = sys.argv[2]
            success = manager.install_tool(tool)
            sys.exit(0 if success else 1)

        elif cmd == "--remove" and len(sys.argv) > 2:
            tool = sys.argv[2]
            success = manager.uninstall_tool(tool)
            sys.exit(0 if success else 1)

        elif cmd == "--list":
            # 列出所有工具
            tools = manager.scan_tools()
            for name, info in sorted(tools.items()):
                category = info.get("category", "GEN")
                print(f"[{category}] {name}")

        elif cmd == "--status":
            health = manager.check_health()
            print(manager._format_report(health))

        else:
            print("用法: tool-manager.py [--check|--update|--audit|--scan|--install <tool>|--remove <tool>|--list|--status]")
    else:
        # 默认运行健康检查
        health = manager.check_health()
        print(manager._format_report(health))
