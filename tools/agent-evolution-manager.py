#!/usr/bin/env python3
"""
Agent 进化管理器 - 分配 Skills 并管理 agent 能力
"""

from pathlib import Path

SKILLS_DIR = Path.home() / ".nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills"

AGENT_SKILLS = {
    "task-watcher": ["model-usage", "clawdhub"],
    "message-watcher": ["model-usage", "discord"],
    "evolution-agent": ["github", "model-usage"],
    "code-optimizer": ["coding-agent", "github"],
    "research-agent": ["github", "mcporter"],
}

def get_skills():
    if not SKILLS_DIR.exists(): return []
    return [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]

def show():
    skills = get_skills()
    print(f"\n🤖 Agent Skills 分配 ({len(skills)} 可用)")
    print("=" * 50)
    for agent, s in AGENT_SKILLS.items():
        print(f"📦 {agent}: {', '.join(s)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        show()
