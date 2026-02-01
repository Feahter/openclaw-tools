#!/usr/bin/env python3
"""
批量为 Skills 添加 GitHub 源配置
"""
import os
import sys
import re
import subprocess
import json
from pathlib import Path

SKILLS_DIRS = [
    "/Users/fuzhuo/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills",
    "/Users/fuzhuo/.openclaw/workspace/skills"
]

# 已知的 GitHub 源映射（工具名 -> 仓库）
KNOWN_SOURCES = {
    # 官方工具
    "github": "https://github.com/cli/cli",
    "slack": "https://github.com/slackapi/python-slack-sdk",
    "discord": "https://github.com/Rapptz/discord.py",
    "weather": "https://github.com/pipermerriam/pyWeather",
    
    # 开源工具
    "himalaya": "https://github.com/soywod/himalaya",
    "bear-notes": "https://github.com/bearlang/bear-swift",
    "obsidian": "https://github.com/obsidianmd/obsidian-releases",
    "notion": "https://github.com/jamalex/notion-py",
    "openai-whisper": "https://github.com/openai/whisper",
    "spotify-player": "https://github.com/k0rf/tokimeki",
    "tmux": "https://github.com/tmux/tmux",
    
    # 本地 Skills（如果是原创的，可以不填或填 OpenClaw 源）
    "backend-patterns": None,
    "frontend-patterns": None,
    "coding-standards": None,
    "golang-patterns": None,
    "golang-testing": None,
    "springboot-patterns": None,
    "springboot-security": None,
    "springboot-tdd": None,
    "jpa-patterns": None,
    "postgres-patterns": None,
    "clickhouse-io": None,
    "security-review": None,
    "tdd-workflow": None,
    "eval-harness": None,
    "continuous-learning-v2": None,
    "iterative-retrieval": None,
    "strategic-compact": None,
    
    # 需要猜测的
    "nano-pdf": "https://github.com/juliusc/nano-pdf",
    "mcporter": "https://github.com/anthropic/mcp",
    "skill-creator": "https://github.com/anthropic/CLAUDE-SKILL-EXAMPLE",
}

# OpenClaw 官方仓库
OPENCLAW_SOURCE = "https://github.com/openclaw/openclaw"

def get_current_frontmatter(content):
    """解析当前 frontmatter"""
    if not content.startswith("---"):
        return {}
    
    parts = content.split("---", 2)
    if len(parts) < 2:
        return {}
    
    yaml_str = parts[1]
    result = {}
    for line in yaml_str.strip().split("\n"):
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        result[key] = value
    return result

def update_frontmatter(content, github_source):
    """更新 frontmatter"""
    parts = content.split("---", 2)
    if len(parts) < 2:
        return content
    
    yaml_str = parts[1]
    lines = yaml_str.strip().split("\n")
    
    # 检查是否已有 github_source
    has_github_source = False
    new_lines = []
    for line in lines:
        if line.strip().startswith("github_source:"):
            has_github_source = True
            new_lines.append(f'github_source: {github_source}')
        else:
            new_lines.append(line)
    
    if not has_github_source:
        new_lines.append(f'github_source: {github_source}')
    
    new_yaml = "\n".join(new_lines)
    return parts[0] + "---\n" + new_yaml + "\n---\n" + (parts[2] if len(parts) > 2 else "")

def process_skill(skill_path):
    """处理单个 Skill"""
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        return None
    
    skill_name = skill_path.name
    content = skill_file.read_text()
    frontmatter = get_current_frontmatter(content)
    
    # 已有 github_source，跳过
    if frontmatter.get("github_source"):
        return {"skipped": True, "reason": "已有 github_source", "name": skill_name}
    
    # 查找 GitHub 源
    github_source = KNOWN_SOURCES.get(skill_name)
    
    # 尝试通过 OpenClaw 官方仓库查找
    if not github_source:
        # 检查是否是 OpenClaw 官方 Skills
        if "openclaw/skills" in str(skill_path):
            github_source = OPENCLAW_SOURCE
    
    if not github_source:
        return {"skipped": True, "reason": "未找到 GitHub 源", "name": skill_name}
    
    # 更新文件
    new_content = update_frontmatter(content, github_source)
    skill_file.write_text(new_content)
    
    return {"updated": True, "source": github_source, "name": skill_name}

def main():
    updated = []
    skipped = []
    
    for skills_dir in SKILLS_DIRS:
        if not os.path.exists(skills_dir):
            continue
        
        print(f"\n处理目录: {skills_dir}")
        
        for item in os.listdir(skills_dir):
            skill_path = Path(skills_dir) / item
            if not skill_path.is_dir():
                continue
            
            result = process_skill(skill_path)
            if not result:
                continue
            
            if result.get("updated"):
                print(f"  ✓ {result['name']} -> {result['source']}")
                updated.append(result)
            else:
                print(f"  ? {result['name']} ({result['reason']})")
                skipped.append(result)
    
    print(f"\n=== 总结 ===")
    print(f"已更新: {len(updated)}")
    print(f"跳过: {len(skipped)}")
    
    # 保存报告
    report = {"updated": updated, "skipped": skipped}
    report_file = Path(__file__).parent / ".skill-sources-update.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n报告: {report_file}")

if __name__ == "__main__":
    main()
