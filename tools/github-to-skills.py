#!/usr/bin/env python3
"""
GitHub to Skills - 专用 GitHub 项目转 Skills
"""
import os
import sys
import json
import re
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

GITHUB_API = "https://api.github.com"
GITHUB_RAW = "https://raw.githubusercontent.com"

class GitHubToSkills:
    def __init__(self):
        self.output_base = Path(__file__).parent / "generated-skills"
        self.output_base.mkdir(exist_ok=True)
        self.github_token = self._get_github_token()

    def _get_github_token(self):
        """获取 GitHub Token"""
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from resource_manager import ResourceManager
            resource = ResourceManager()
            resources = resource.get_all_resources()
            for r in resources:
                if r.get("type") == "api_key" and r.get("provider") == "github":
                    return r.get("value")
        except:
            pass
        return os.environ.get("GITHUB_TOKEN", "")

    def _parse_github_url(self, url):
        """解析 GitHub URL"""
        patterns = [
            r"github\.com/([^/]+)/([^/]+)/?",
            r"git@github\.com:([^/]+)/([^/]+)\.git",
            r"^([^/]+)/([^/]+)$"
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.groups()
                repo = repo.replace(".git", "").rstrip("/")
                return owner, repo
        return None, None

    def _fetch_content(self, url):
        """获取内容"""
        cmd = ["curl", "-s"]
        if self.github_token:
            cmd.extend(["-H", f"Authorization: token {self.github_token}"])
        cmd.append(url)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout if result.returncode == 0 else None

    def _fetch_repo_info(self, owner, repo):
        """获取仓库信息"""
        url = f"{GITHUB_API}/repos/{owner}/{repo}"
        response = self._fetch_content(url)
        if response:
            try:
                return json.loads(response)
            except:
                pass
        return None

    def _extract_core_content(self, readme_content):
        """提取 README 核心内容"""
        lines = readme_content.split("\n")
        main_content = []
        started = False
        
        skip_patterns = ["Table of", "目录", "Install", "Start", "License"]
        
        for line in lines:
            if line.startswith("![") or line.startswith("[!"):
                continue
            if line.startswith("## ") and not started:
                if not any(p in line for p in skip_patterns):
                    started = True
            if started:
                main_content.append(line)
        
        return "\n".join(main_content)

    def _parse_frontmatter(self, yaml_str):
        """解析简单 YAML"""
        result = {}
        for line in yaml_str.strip().split("\n"):
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            result[key] = value
        return result

    def convert(self, github_url):
        """转换 GitHub URL 为 Skill"""
        owner, repo = self._parse_github_url(github_url)
        if not owner:
            print(f"无效的 GitHub URL: {github_url}")
            return None

        print(f"处理: {owner}/{repo}...")

        # 获取仓库信息
        repo_info = self._fetch_repo_info(owner, repo)
        if not repo_info:
            print(f"无法获取仓库信息")
            return None

        # 获取 README
        readme_url = f"{GITHUB_RAW}/{owner}/{repo}/main/README.md"
        readme = self._fetch_content(readme_url)
        if not readme:
            readme_url = f"{GITHUB_RAW}/{owner}/{repo}/master/README.md"
            readme = self._fetch_content(readme_url)

        if not readme:
            print(f"无法获取 README")
            return None

        # 提取核心内容
        core_content = self._extract_core_content(readme)

        # 生成 Skill
        skill_name = repo.lower().replace("_", "-")
        desc = repo_info.get("description", f"GitHub 项目 {owner}/{repo}")
        if len(desc) > 200:
            desc = desc[:197] + "..."

        skill_dir = self.output_base / skill_name
        skill_dir.mkdir(exist_ok=True)

        skill_file = skill_dir / "SKILL.md"
        content = f'''---
name: {skill_name}
description: {desc}
github_source: https://github.com/{owner}/{repo}
source_repo: https://github.com/{owner}/{repo}
stars: {repo_info.get("stargazers_count", 0)}
language: {repo_info.get("language", "Unknown")}
last_updated: {datetime.now().isoformat()[:10]}
---

# {skill_name.replace("-", " ").title()}

## 来自 GitHub

- 仓库: [https://github.com/{owner}/{repo}](https://github.com/{owner}/{repo})
- ⭐ Star: {repo_info.get("stargazers_count", 0)}
- 语言: {repo_info.get("language", "Unknown")}

## 核心功能

{core_content}

## 使用场景

根据 README 描述的使用场景调用此 Skill。

## 注意事项

此 Skill 由 github-to-skills 自动生成，内容来自 GitHub 仓库的 README。
'''

        skill_file.write_text(content)
        print(f"✓ 已生成: {skill_file}")
        return skill_dir

    def convert_from_file(self, file_path):
        """批量转换"""
        urls = [l.strip() for l in open(file_path) if l.strip() and not l.strip().startswith("#")]
        results = []
        for url in urls:
            result = self.convert(url)
            if result:
                results.append(result)
        return results

def main():
    parser = argparse.ArgumentParser(description="GitHub to Skills 转换器")
    parser.add_argument("url", nargs="?", help="GitHub 仓库 URL")
    parser.add_argument("--file", "-f", help="批量转换的 URL 列表文件")
    parser.add_argument("--output", "-o", help="输出目录")
    args = parser.parse_args()

    converter = GitHubToSkills()

    if args.output:
        converter.output_base = Path(args.output)
        converter.output_base.mkdir(exist_ok=True)

    if args.url:
        converter.convert(args.url)
    elif args.file:
        results = converter.convert_from_file(args.file)
        print(f"\n完成: 转换了 {len(results)} 个仓库")
    else:
        print("用法:")
        print("  python3 github-to-skills.py <github-url>")
        print("  python3 github-to-skills.py -f urls.txt")

if __name__ == "__main__":
    main()
