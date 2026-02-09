#!/usr/bin/env python3
"""
批量同步 Skills - 后台自动处理
避免速率限制，分批执行
"""

import subprocess
import time
import json
from pathlib import Path

def run_command(cmd, timeout=60):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def get_skills_to_sync():
    """获取需要同步的 skills 列表"""
    stdout, stderr, code = run_command("clawdhub sync --dry-run 2>/dev/null || clawdhub list 2>/dev/null")
    
    to_sync = []
    for line in stdout.split('\n'):
        line = line.strip()
        if 'UPDATE' in line or 'NEW' in line:
            parts = line.split()
            if parts:
                to_sync.append(parts[0])
    return to_sync

def sync_skill(skill):
    """同步单个 skill"""
    print(f"  🔄 同步 {skill}...")
    stdout, stderr, code = run_command(f"clawdhub update {skill} --force 2>&1", timeout=120)
    
    if code == 0:
        print(f"    ✅ {skill} 完成")
        return True
    elif "Rate limit" in stderr or "Rate limit" in stdout:
        print(f"    ⏸️ {skill} 速率限制，暂停...")
        return "rate_limit"
    else:
        print(f"    ⚠️ {skill} 失败: {stderr[:100]}")
        return False

def main():
    print("🛠️  Skills 批量同步开始")
    print("=" * 50)
    
    # 需要同步的 skills 列表（从之前的同步输出中提取）
    skills_to_sync = [
        # 新增 skills
        "a-tool-for", "agent-commander", "article-extractor",
        "auto-knowledge-acquisition", "brainstorming", "chromadb",
        "coding-agent", "download-waytoagi-prompts",
        "finishing-a-development-branch", "github-to-skills",
        "macos-image-generation", "canvas-design", "clawdhub",
        "find-skills", "mcporter", "pptx", "skill-creator",
        "webapp-testing", "xlsx", "skill-manager",
        "skill-from-github", "skill-from-masters", "skill-from-notebook",
        "skill-evolution-manager", "test-driven-development",
        "using-git-worktrees", "web-artifacts-builder",
        # 更新 skills
        "cron-writer", "mineru"
    ]
    
    success_count = 0
    failed_skills = []
    
    for i, skill in enumerate(skills_to_sync, 1):
        print(f"\n[{i}/{len(skills_to_sync)}]")
        result = sync_skill(skill)
        
        if result == True:
            success_count += 1
            # 每成功3个后暂停，避免速率限制
            if i % 3 == 0 and i < len(skills_to_sync):
                print("  ⏱️  暂停 10 秒...")
                time.sleep(10)
        elif result == "rate_limit":
            print("\n⏸️ 触发速率限制，等待 60 秒后继续...")
            time.sleep(60)
            # 重试当前 skill
            result = sync_skill(skill)
            if result == True:
                success_count += 1
        else:
            failed_skills.append(skill)
    
    print("\n" + "=" * 50)
    print(f"✅ 完成: {success_count}/{len(skills_to_sync)}")
    if failed_skills:
        print(f"❌ 失败: {', '.join(failed_skills)}")
    print("💾 下次心跳会继续处理剩余任务")

if __name__ == "__main__":
    main()
