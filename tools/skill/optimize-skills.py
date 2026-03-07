#!/usr/bin/env python3
"""
Skills 优化器 - 删除低价值 Skills，从 GitHub 补充优质 Skills
"""
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

SKILLS_DIR = "/Users/fuzhuo/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills"
WORKSPACE_SKILLS = "/Users/fuzhuo/.openclaw/workspace/skills"

# 需要删除的低价值 Skills（实用性低、临时性、重叠）
TO_DELETE = {
    # 临时/实验性
    "bird",           # 临时项目
    "food-order",     # 临时项目  
    "eightctl",       # 临时项目
    "gog",            # 临时项目
    "sag",            # 临时项目
    "goplaces",       # 临时项目
    "ordercli",       # 临时项目
    "oracle",         # 临时项目
    "nano-banana-pro", # 临时项目
    "wacli",          # 临时项目
    "songsee",        # 临时项目
    
    # 实用性低的工具
    "camsnap",        # 摄像头相关，使用频率低
    "gifgrep",        # 小众需求
    "peekaboo",       # 不确定用途
    "blogwatcher",    # 临时需求
    "video-frames",   # 临时需求
    
    # Mac 原生工具（不如直接用系统）
    "apple-notes",    # 系统工具
    "apple-reminders", # 系统工具
    "things-mac",     # 系统工具
    "1password",      # 系统工具
    
    # 通信工具（你有更好的替代）
    "bluebubbles",    # 小众
    "voice-call",     # 不常用
}

# 需要从 GitHub 补充的优质 Skills
GITHUB_REPOS = [
    # Python 生态
    ("https://github.com/tiangolo/fastapi", "fastapi"),
    ("https://github.com/pydantic/pydantic", "pydantic"),
    ("https://github.com/pandas-dev/pandas", "pandas"),
    ("https://github.com/pyyaml/pyyaml", "pyyaml"),
    ("https://github.com/psf/black", "black"),
    ("https://github.com/astral-sh/ruff", "ruff"),
    
    # JavaScript/TypeScript
    ("https://github.com/denoland/deno", "deno"),
    ("https://github.com/oven-sh/bun", "bun"),
    ("https://github.com/evanw/esbuild", "esbuild"),
    ("https://github.com/vercel/next.js", "nextjs"),
    
    # DevOps
    ("https://github.com/docker/cli", "docker"),
    ("https://github.com/kubernetes/kubernetes", "kubernetes"),
    ("https://github.com/hashicorp/terraform", "terraform"),
    ("https://github.com/ansible/ansible", "ansible"),
    
    # AI/ML
    ("https://github.com/langchain-ai/langchain", "langchain"),
    ("https://github.com/run-llama/llama_index", "llama-index"),
    ("https://github.com/huggingface/transformers", "transformers"),
    
    # 数据库
    ("https://github.com/redis/redis", "redis"),
    ("https.com/mongodb/mongo", "mongodb"),
    ("https://github.com/etcd-io/etcd", "etcd"),
    
    # 工具库
    ("https://github.com/jwtk/jjwt", "jjwt"),
    ("https://github.com/google/guava", "guava"),
    ("https://github.com/LombokPOM/Lombok", "lombok"),
]

def delete_skills():
    """删除低价值 Skills"""
    deleted = []
    
    for skill_name in TO_DELETE:
        skill_path = Path(SKILLS_DIR) / skill_name
        if skill_path.exists():
            subprocess.run(["rm", "-rf", str(skill_path)], check=True)
            deleted.append(skill_name)
    
    return deleted

def add_github_source(skill_name, github_source):
    """为本地 Skills 添加 GitHub 源"""
    for skills_dir in [SKILLS_DIR, WORKSPACE_SKILLS]:
        skill_path = Path(skills_dir) / skill_name / "SKILL.md"
        if skill_path.exists():
            content = skill_path.read_text()
            if "github_source:" not in content:
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    parts[1] = parts[1].rstrip() + f"\ngithub_source: {github_source}\n"
                    content = "---".join(parts)
                    skill_path.write_text(content)
                else:
                    content = f'---\nname: {skill_name}\n---\n' + content
                    skill_path.write_text(content)
            return True
    return False

def main():
    print("=== Skills 优化 ===\n")
    
    # 1. 删除低价值 Skills
    print("1. 删除低价值 Skills...")
    deleted = delete_skills()
    for d in deleted:
        print(f"   ✗ 删除: {d}")
    print(f"   共删除 {len(deleted)} 个\n")
    
    # 2. 为本地 Skills 添加 GitHub 源
    print("2. 为本地 Skills 添加 GitHub 源...")
    workspace_skills_github = {
        "backend-patterns": "https://github.com/openclaw/openclaw",
        "frontend-patterns": "https://github.com/openclaw/openclaw",
        "coding-standards": "https://github.com/openclaw/openclaw",
        "golang-patterns": "https://github.com/openclaw/openclaw",
        "golang-testing": "https://github.com/openclaw/openclaw",
        "springboot-patterns": "https://github.com/openclaw/openclaw",
        "springboot-security": "https://github.com/openclaw/openclaw",
        "springboot-tdd": "https://github.com/openclaw/openclaw",
        "jpa-patterns": "https://github.com/openclaw/openclaw",
        "postgres-patterns": "https://github.com/openclaw/openclaw",
        "clickhouse-io": "https://github.com/openclaw/openclaw",
        "security-review": "https://github.com/openclaw/openclaw",
        "tdd-workflow": "https://github.com/openclaw/openclaw",
        "eval-harness": "https://github.com/openclaw/openclaw",
        "continuous-learning-v2": "https://github.com/openclaw/openclaw",
        "iterative-retrieval": "https://github.com/openclaw/openclaw",
        "strategic-compact": "https://github.com/openclaw/openclaw",
    }
    
    for skill, source in workspace_skills_github.items():
        if add_github_source(skill, source):
            print(f"   ✓ {skill}")
    
    print("\n3. 从 GitHub 补充 Skills...")
    print("   (使用 github-to-skills.py 批量添加)")
    print(f"   待添加: {len(GITHUB_REPOS)} 个\n")
    
    # 保存待添加列表
    repo_list = [repo[0] for repo in GITHUB_REPOS]
    list_file = Path(__file__).parent / ".pending-github-skills.txt"
    list_file.write_text("\n".join(repo_list))
    print(f"   列表已保存到: {list_file}")
    
    print("\n=== 完成 ===")
    print(f"删除: {len(deleted)} 个")
    print(f"待添加 GitHub Skills: {len(GITHUB_REPOS)} 个")

if __name__ == "__main__":
    main()
