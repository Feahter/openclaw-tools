#!/usr/bin/env python3
"""
从 everything-claude-code 移植核心功能到 OpenClaw
"""

import subprocess
import json
from pathlib import Path
import sys

WORKSPACE = Path.home() / ".openclaw" / "workspace"
CLONE_DIR = WORKSPACE / "temp" / "everything-claude-code"

def clone_repo():
    """克隆仓库"""
    print("📦 克隆 everything-claude-code...")
    CLONE_DIR.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "clone", "--depth", "1", 
         "https://github.com/affaan-m/everything-claude-code.git", 
         str(CLONE_DIR)],
        capture_output=True
    )
    if result.returncode != 0:
        print(f"❌ 克隆失败: {result.stderr.decode()}")
        return False
    print("✅ 克隆成功")
    return True

def install_rules():
    """安装规则"""
    print("\n📜 安装规则...")
    rules_src = CLONE_DIR / "rules"
    rules_dst = WORKSPACE / "rules"
    rules_dst.mkdir(exist_ok=True)
    
    for rule in rules_src.glob("*.md"):
        dst = rules_dst / rule.name
        if not dst.exists():
            dst.write_text(rule.read_text())
            print(f"  ✅ {rule.name}")
        else:
            print(f"  ⏭️ {rule.name} 已存在")
    return True

def install_skills():
    """安装技能"""
    print("\n🛠️ 安装技能...")
    skills_src = CLONE_DIR / "skills"
    skills_dst = WORKSPACE / "skills"
    skills_dst.mkdir(exist_ok=True)
    
    for skill in skills_src.iterdir():
        if skill.is_dir():
            dst = skills_dst / skill.name
            if not dst.exists():
                # 复制整个目录
                subprocess.run(["cp", "-r", str(skill), str(dst)], capture_output=True)
                print(f"  ✅ {skill.name}")
            else:
                print(f"  ⏭️ {skill.name} 已存在")
    return True

def install_agents():
    """安装子代理"""
    print("\n🤖 安装子代理...")
    agents_src = CLONE_DIR / "agents"
    agents_dst = WORKSPACE / "agents"
    agents_dst.mkdir(exist_ok=True)
    
    for agent in agents_src.glob("*.md"):
        dst = agents_dst / agent.name
        if not dst.exists():
            dst.write_text(agent.read_text())
            print(f"  ✅ {agent.name}")
        else:
            print(f"  ⏭️ {agent.name} 已存在")
    return True

def install_commands():
    """安装命令"""
    print("\n⚡ 安装命令...")
    commands_src = CLONE_DIR / "commands"
    commands_dst = WORKSPACE / "commands"
    commands_dst.mkdir(exist_ok=True)
    
    for cmd in commands_src.glob("*.md"):
        dst = commands_dst / cmd.name
        if not dst.exists():
            dst.write_text(cmd.read_text())
            print(f"  ✅ {cmd.name}")
        else:
            print(f"  ⏭️ {cmd.name} 已存在")
    return True

def main():
    if not clone_repo():
        return 1
    
    install_rules()
    install_skills()
    install_agents()
    install_commands()
    
    # 清理
    subprocess.run(["rm", "-rf", str(CLONE_DIR)], capture_output=True)
    
    print("\n✅ 安装完成！")
    print("\n新增文件:")
    print(f"  📜 {WORKSPACE}/rules/")
    print(f"  🛠️ {WORKSPACE}/skills/")
    print(f"  🤖 {WORKSPACE}/agents/")
    print(f"  ⚡ {WORKSPACE}/commands/")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
