#!/usr/bin/env python3
"""
为新添加的 GitHub Skills 添加 GitHub 源
"""
import os
from pathlib import Path

SKILLS_DIR = "/Users/fuzhuo/.openclaw/workspace/skills"

# GitHub 源映射
GITHUB_SOURCES = {
    "fastapi": "https://github.com/tiangolo/fastapi",
    "pydantic": "https://github.com/pydantic/pydantic",
    "pandas": "https://github.com/pandas-dev/pandas",
    "pyyaml": "https://github.com/pyyaml/pyyaml",
    "black": "https://github.com/psf/black",
    "ruff": "https://github.com/astral-sh/ruff",
    "deno": "https://github.com/denoland/deno",
    "bun": "https://github.com/oven-sh/bun",
    "esbuild": "https://github.com/evanw/esbuild",
    "next.js": "https://github.com/vercel/next.js",
    "docker": "https://github.com/docker/cli",
    "kubernetes": "https://github.com/kubernetes/kubernetes",
    "terraform": "https://github.com/hashicorp/terraform",
    "ansible": "https://github.com/ansible/ansible",
    "langchain": "https://github.com/langchain-ai/langchain",
    "llama-index": "https://github.com/run-llama/llama_index",
    "transformers": "https://github.com/huggingface/transformers",
    "redis": "https://github.com/redis/redis",
    "mongodb": "https://github.com/mongodb/mongo",
    "jjwt": "https://github.com/jwtk/jjwt",
    "guava": "https://github.com/google/guava",
    "lombok": "https://github.com/projectlombok/lombok",
    "cli": "https://github.com/cli/cli",
}

def add_github_source(skill_name, github_source):
    """为 Skill 添加 GitHub 源"""
    skill_file = Path(SKILLS_DIR) / skill_name / "SKILL.md"
    if not skill_file.exists():
        return False
    
    content = skill_file.read_text()
    
    # 检查是否已有 github_source
    if "github_source:" in content:
        return False
    
    # 添加 GitHub 源到 frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        parts[1] = parts[1].rstrip() + f"\ngithub_source: {github_source}\n"
        content = "---".join(parts)
    else:
        # 提取 name
        name = skill_name
        match_lines = content.split("\n")[:10]
        for line in match_lines:
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip()
                break
        
        content = f'---\nname: {name}\ngithub_source: {github_source}\n---\n' + content
    
    skill_file.write_text(content)
    return True

def main():
    added = 0
    skipped = 0
    
    for skill_name, source in GITHUB_SOURCES.items():
        if add_github_source(skill_name, source):
            print(f"✓ {skill_name}")
            added += 1
        else:
            print(f"? {skill_name} (已存在或文件不存在)")
            skipped += 1
    
    print(f"\n添加: {added}, 跳过: {skipped}")

if __name__ == "__main__":
    main()
