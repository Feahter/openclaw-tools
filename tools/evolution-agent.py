#!/usr/bin/env python3
"""
24H自主进化Agent - 静默工作流优化器
观察 → 识别 → 构建 → 验证 → 包装 → 归档 → 交付
"""

import os
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# 配置
SANDBOX_DIR = Path.home() / ".evolution-sandbox"
READY_DIR = Path.home() / ".evolution-ready"
LOG_FILE = Path.home() / ".evolution-log"
PAUSE_FILE = Path.home() / ".pause-evolution"


class EvolutionAgent:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sandbox = SANDBOX_DIR / self.timestamp
        self.tool_name = ""
        self.findings = []

    def is_paused(self) -> bool:
        """检查是否暂停"""
        return PAUSE_FILE.exists()

    def should_stop(self) -> bool:
        """检查是否需要停止"""
        return self.is_paused()

    def scan_workflow(self) -> Dict:
        """观察阶段：扫描工作流数据"""
        findings = {
            "shell_history": [],
            "git_activity": [],
            "recent_files": [],
            "patterns": []
        }

        # 读取 shell 历史 (zsh/bash)
        zsh_hist = Path.home() / ".zsh_history"
        if zsh_hist.exists():
            try:
                lines = zsh_hist.read_text().split('\n')[-100:]
                findings["shell_history"] = self._analyze_history(lines)
            except Exception:
                pass

        # Git 活动
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-20"],
                capture_output=True, text=True, cwd=Path.home()
            )
            if result.returncode == 0:
                findings["git_activity"] = result.stdout.strip().split('\n')
        except Exception:
            pass

        # 最近访问文件
        try:
            result = subprocess.run(
                ["ls", "-lt", str(Path.home())],
                capture_output=True, text=True, shell=True
            )
            if result.returncode == 0:
                findings["recent_files"] = result.stdout.strip().split('\n')[:10]
        except Exception:
            pass

        return findings

    def _analyze_history(self, lines: List[str]) -> List[str]:
        """分析 shell 历史，提取命令"""
        commands = []
        for line in lines[-200:]:
            if line.strip():
                # 去掉时间戳 (zsh history 格式: : timestamp:command)
                if ": " in line and line[0].isdigit():
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        commands.append(parts[2].strip())
                else:
                    commands.append(line.strip())
        return commands

    def identify_patterns(self, data: Dict) -> List[Dict]:
        """识别重复模式和摩擦点"""
        patterns = []
        cmd_counts = {}

        # 统计命令频率
        for cmd in data.get("shell_history", []):
            base_cmd = cmd.split()[0] if cmd else ""
            cmd_counts[base_cmd] = cmd_counts.get(base_cmd, 0) + 1

        # 找出重复 3 次以上的命令
        for cmd, count in cmd_counts.items():
            if count >= 3:
                patterns.append({
                    "type": "repeated_command",
                    "command": cmd,
                    "count": count,
                    "priority": "high" if count >= 5 else "medium"
                })

        return patterns

    def build_tool(self, pattern: Dict) -> Optional[str]:
        """构建阶段：生成微工具"""
        self.tool_name = f"evo_{pattern['type']}_{self.timestamp}"
        tool_path = self.sandbox / self.tool_name

        # 创建沙箱目录
        tool_path.mkdir(parents=True, exist_ok=True)

        # 根据模式生成代码
        code = self._generate_code(pattern)

        # 写入主脚本
        main_script = tool_path / f"{self.tool_name}.sh"
        main_script.write_text(code)

        # 创建 dry-run 模式
        dry_run_script = tool_path / f"{self.tool_name}_dry_run.sh"
        dry_run_script.write_text(code.replace("# MAIN_LOGIC", "# DRY-RUN MODE\ndry_run=true\n"))

        # 创建一键试用脚本
        try_script = tool_path / "try.sh"
        try_script.write_text(f'''#!/bin/bash
echo "试用 {self.tool_name}..."
echo "命令: .{self.tool_name}.sh"

# 使用 dry-run 模式试用
.{self.tool_name}_dry_run.sh

echo "试用完成！满意后运行 ./install.sh 安装"
''')
        try_script.chmod(0o755)

        # 创建安装脚本
        install_script = tool_path / "install.sh"
        install_script.write_text(f'''#!/bin/bash
# 安装脚本 - 可逆
set -e

echo "安装 {self.tool_name}..."

# 复制到 PATH
sudo cp {self.tool_name}.sh /usr/local/bin/
chmod +x /usr/local/bin/{self.tool_name}.sh

echo "安装完成！运行 {self.tool_name}.sh 使用"
''')
        install_script.chmod(0o755)

        # 创建卸载脚本
        uninstall_script = tool_path / "uninstall.sh"
        uninstall_script.write_text(f'''#!/bin/bash
# 卸载脚本
echo "卸载 {self.tool_name}..."
rm -f /usr/local/bin/{self.tool_name}.sh
echo "卸载完成"
''')
        uninstall_script.chmod(0o755)

        # 创建说明文件
        readme = tool_path / "README.md"
        readme.write_text(f'''# {self.tool_name}

解决: {pattern.get('description', '效率瓶颈')}

## 使用

```bash
# 试用 (dry-run)
./try.sh

# 安装
./install.sh

# 卸载
./uninstall.sh
```

## 功能

- 原子化功能，专注解决一个问题
- 包含 dry-run 模式，可安全试用
''')

        return self.tool_name

    def _generate_code(self, pattern: Dict) -> str:
        """生成微工具代码"""
        cmd = pattern.get("command", "unknown")

        return f'''#!/bin/bash
# {self.tool_name}
# 自动生成 - {datetime.now().isoformat()}
# 解决: 简化重复命令 "{cmd}"

set -euo pipefail

# 配置
DRY_RUN=false
LOG_FILE="$HOME/.evolution-log"

log() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [EVOLUTION] $1" | tee -a $LOG_FILE
}}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            echo "用法: $0 [--dry-run]"
            echo "  --dry-run  试运行模式，不实际执行"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# MAIN_LOGIC
main() {{
    log "执行: 简化命令 {cmd}"

    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] 会执行: {cmd}"
        return 0
    fi

    # 实际执行逻辑
    {cmd}
}}

main "$@"
'''

    def validate_tool(self, tool_name: str) -> bool:
        """验证阶段：隔离测试"""
        tool_path = self.sandbox / tool_name

        # 测试用例
        test_cases = [
            {"name": "help", "args": ["--help"]},
            {"name": "dry_run", "args": ["--dry-run"]},
        ]

        for test in test_cases:
            try:
                result = subprocess.run(
                    [f"./{tool_name}.sh"] + test["args"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=tool_path
                )
                if result.returncode != 0:
                    log(f"测试失败: {test['name']}")
                    return False
            except subprocess.TimeoutExpired:
                log(f"测试超时: {test['name']}")
                return False
            except Exception as e:
                log(f"测试异常: {test['name']} - {e}")
                return False

        return True

    def deliver_tool(self, tool_name: str, pattern: Dict):
        """交付阶段：移动到就绪区"""
        source = self.sandbox / tool_name
        target = READY_DIR / tool_name

        # 创建就绪区
        READY_DIR.mkdir(parents=True, exist_ok=True)

        # 移动
        subprocess.run(["mv", str(source), str(target)])

        # 记录日志
        log_entry = {
            "timestamp": self.timestamp,
            "tool_name": tool_name,
            "pattern": pattern,
            "status": "ready",
            "description": pattern.get("description", "效率优化")
        }
        self._append_log(log_entry)

        print(f"✅ 工具已就绪: {target}")

    def _append_log(self, entry: Dict):
        """追加日志"""
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def run(self, force: bool = False):
        """主运行循环"""
        log(f"🫀 进化Agent启动 - {self.timestamp}")

        # 检查暂停
        if self.is_paused():
            log("⏸️ 进化已暂停")
            return

        # 观察
        data = self.scan_workflow()

        # 识别
        patterns = self.identify_patterns(data)

        if not patterns and not force:
            log("未发现需要优化的模式")
            return

        # 构建 & 验证每个模式
        for pattern in patterns[:3]:  # 最多 3 个
            if self.should_stop():
                break

            log(f"构建工具解决: {pattern['command']}")

            self.build_tool(pattern)
            if self.validate_tool(self.tool_name):
                self.deliver_tool(self.tool_name, pattern)
            else:
                log(f"验证失败，放弃: {self.tool_name}")


def log(msg: str):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [EVOLUTION] {msg}")


if __name__ == "__main__":
    import sys

    agent = EvolutionAgent()

    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        agent.run(force=True)
    else:
        agent.run()
