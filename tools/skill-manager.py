#!/usr/bin/env python3
"""
Skill Manager - 批量检查 Skills 状态、自动升级（优化版）
"""
import os
import sys
import json
import hashlib
import subprocess
import argparse
import re
from pathlib import Path
from datetime import datetime
import time

# 工具目录路径
_TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(_TOOLS_DIR))

SKILLS_DIRS = [
    "/Users/fuzhuo/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills",
    "/Users/fuzhuo/.openclaw/workspace/skills"
]

GITHUB_API = "https://api.github.com"
CACHE_FILE = _TOOLS_DIR / ".skill-status.json"
CACHE_TTL = 3600  # 1小时缓存

class SkillManager:
    def __init__(self):
        self.github_token = self._get_github_token()
        self.cache = self._load_cache()

    def _get_github_token(self):
        try:
            from resource_manager import ResourceManager
            resource = ResourceManager()
            for r in resource.get_all_resources():
                if r.get("type") == "api_key" and r.get("provider") == "github":
                    return r.get("value")
        except:
            pass
        return None

    def _load_cache(self):
        if CACHE_FILE.exists():
            try:
                data = json.loads(CACHE_FILE.read_text())
                if time.time() - data.get("timestamp", 0) < CACHE_TTL:
                    return data
            except:
                pass
        return {}

    def _save_cache(self, data):
        data["timestamp"] = time.time()
        CACHE_FILE.write_text(json.dumps(data, indent=2))

    def _call_github_api(self, url, cache_key=None):
        """调用 GitHub API（带缓存）"""
        if cache_key and cache_key in self.cache:
            return self.cache[cache_key]
        
        cmd = ["curl", "-s"]
        if self.github_token:
            cmd.extend(["-H", f"Authorization: token {self.github_token}"])
        cmd.append(url)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        data = result.stdout if result.returncode == 0 else ""
        
        if cache_key:
            self.cache[cache_key] = data
        return data

    def scan_skills(self):
        """扫描所有 Skills"""
        skills = []
        for skills_dir in SKILLS_DIRS:
            if not os.path.exists(skills_dir):
                continue
            for item in os.listdir(skills_dir):
                skill_path = Path(skills_dir) / item
                if skill_path.is_dir():
                    skill_info = self._read_skill_metadata(skill_path)
                    if skill_info:
                        skills.append(skill_info)
        return skills

    def _read_skill_metadata(self, skill_path):
        """读取 Skill 元数据"""
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            return None

        content = skill_file.read_text()
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                metadata = self._parse_yaml(parts[1])
                return {
                    "name": metadata.get("name", skill_path.name),
                    "description": metadata.get("description", ""),
                    "path": str(skill_path),
                    "github_source": metadata.get("github_source", None),
                    "local_hash": self._calc_content_hash(content),
                    "last_updated": self._get_file_mtime(skill_path)
                }
        return None

    def _parse_yaml(self, yaml_str):
        """简单 YAML 解析"""
        result = {}
        for line in yaml_str.strip().split("\n"):
            line = line.strip()
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            result[key] = value
        return result

    def _calc_content_hash(self, content):
        return hashlib.md5(content.encode()).hexdigest()

    def _get_file_mtime(self, path):
        try:
            return os.path.getmtime(str(path))
        except:
            return None

    def check_remote_update(self, skill_info, use_cache=True):
        """检查远程是否有更新"""
        github_source = skill_info.get("github_source")
        if not github_source:
            return {"has_update": False, "reason": "no_github_source"}

        match = re.search(r"github\.com/([^/]+)/([^/]+)", github_source)
        if not match:
            return {"has_update": False, "reason": "invalid_github_url"}

        owner, repo = match.groups()
        repo = repo.replace(".git", "").rstrip("/")

        # 获取远程最新 commit
        url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/main"
        cache_key = f"commits:{owner}:{repo}"
        
        response = self._call_github_api(url, cache_key if use_cache else None)
        if not response:
            url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/master"
            cache_key = f"commits:{owner}:{repo}:master"
            response = self._call_github_api(url, cache_key if use_cache else None)

        try:
            data = json.loads(response)
            if isinstance(data, list) and len(data) > 0:
                commit = data[0]
                sha = commit.get("sha", "")[:7]
                return {"has_update": True, "remote_sha": sha, "commit_url": commit.get("html_url", "")}
        except:
            pass

        return {"has_update": False, "reason": "api_error"}

    def check_all(self, use_cache=True):
        """检查所有 Skills 状态"""
        skills = self.scan_skills()
        report = {
            "total": len(skills),
            "with_github_source": 0,
            "up_to_date": 0,
            "outdated": 0,
            "no_github_source": 0,
            "skills": []
        }

        for skill in skills:
            if skill.get("github_source"):
                report["with_github_source"] += 1
                remote_info = self.check_remote_update(skill, use_cache)
                
                status = "outdated" if remote_info.get("has_update") else "up_to_date"
                skill_status = {
                    "name": skill["name"],
                    "path": skill["path"],
                    "github_source": skill["github_source"],
                    "status": status
                }
                if remote_info.get("has_update"):
                    skill_status["remote_sha"] = remote_info.get("remote_sha")
                    skill_status["commit_url"] = remote_info.get("commit_url")
                    report["outdated"] += 1
                else:
                    report["up_to_date"] += 1
                report["skills"].append(skill_status)
            else:
                report["no_github_source"] += 1
                report["skills"].append({
                    "name": skill["name"],
                    "path": skill["path"],
                    "status": "no_github_source"
                })

        self._save_cache(report)
        return report

    def print_report(self, report):
        print(f"\n=== Skills 状态报告 ===")
        print(f"总 Skills 数: {report['total']}")
        print(f"有 GitHub 源: {report['with_github_source']}")
        print(f"  ✓ 已是最新: {report['up_to_date']}")
        print(f"  ✗ 需要更新: {report['outdated']}")
        print(f"  ? 无 GitHub 源: {report['no_github_source']}")
        print()

        print("=== 需要更新的 Skills ===")
        outdated = [s for s in report["skills"] if s.get("status") == "outdated"]
        if outdated:
            for skill in outdated:
                print(f"  ✗ {skill['name']}")
                print(f"      远程: {skill.get('remote_sha', '?')}")
                print(f"      {skill.get('github_source', '')}")
        else:
            print("  ✓ 没有需要更新的 Skills")

        print("\n=== 无 GitHub 源的 Skills ===")
        no_source = [s for s in report["skills"] if s.get("status") == "no_github_source"]
        if no_source:
            for skill in no_source[:10]:  # 只显示前10个
                print(f"  ? {skill['name']}")
            if len(no_source) > 10:
                print(f"  ... 共 {len(no_source)} 个")

def main():
    parser = argparse.ArgumentParser(description="Skill Manager")
    parser.add_argument("action", choices=["check", "upgrade"], default="check")
    parser.add_argument("--skill", help="指定 Skill 名称")
    parser.add_argument("--no-cache", action="store_true", help="不使用缓存")
    args = parser.parse_args()

    manager = SkillManager()

    if args.action == "check":
        report = manager.check_all(use_cache=not args.no_cache)
        manager.print_report(report)
        print(f"\n报告已缓存到: {CACHE_FILE}")

    elif args.action == "upgrade":
        print("升级功能待实现")

if __name__ == "__main__":
    main()
