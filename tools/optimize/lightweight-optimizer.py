#!/usr/bin/env python3
"""
OpenClaw 轻量优化器
整合 Token 压缩和响应缓存
"""

import hashlib
import json
import os
import time
from pathlib import Path

WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
CACHE_DIR = Path.home() / ".openclaw" / "cache" / "responses"
SKILLS_DIR = WORKSPACE / "skills"
CACHE_SKILLS_DIR = Path.home() / ".openclaw" / "skill-cache"
LOG_FILE = Path.home() / ".openclaw" / "logs" / "optimize.log"

# 保留的常用 Skills
CORE_SKILLS = [
    "skill-vetter", "memory-on-demand", "fast-edit",
    "algorithm-toolkit", "mcp-builder", "writer",
    "canvas-design", "pdf", "docx", "pptx", "xlsx",
    "tavily-search", "qmd", "proactive-agent",
    "computer-use", "agent-browser-0", "apple-notes",
    "auto-knowledge-acquisition", "autonomous-brain"
]

def log(msg: str):
    """日志"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    print(line.strip())
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line)

def clean_cache():
    """清理过期缓存"""
    if not CACHE_DIR.exists():
        log("缓存目录不存在，跳过")
        return
    
    # 清理 24 小时前的系统信息缓存
    cutoff = time.time() - 86400
    for f in CACHE_DIR.glob("*.json"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
    
    count = len(list(CACHE_DIR.glob("*.json")))
    log(f"缓存清理完成: {count} 条")

def cache_stats():
    """缓存统计"""
    if not CACHE_DIR.exists():
        return {"entries": 0, "size_mb": 0}
    
    files = list(CACHE_DIR.glob("*.json"))
    total = sum(f.stat().st_size for f in files)
    return {"entries": len(files), "size_mb": round(total / 1024 / 1024, 2)}

def clean_skills():
    """清理不常用的 Skills"""
    CACHE_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 获取当前活跃的
    active = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]
    
    # 移动不常用的
    moved = 0
    for d in SKILLS_DIR.iterdir():
        if d.is_dir() and d.name not in CORE_SKILLS:
            target = CACHE_SKILLS_DIR / d.name
            if not target.exists():
                d.rename(target)
                moved += 1
    
    active_count = len(list(SKILLS_DIR.iterdir()))
    cached_count = len(list(CACHE_SKILLS_DIR.iterdir()))
    
    log(f"Skills 优化: 活跃 {active_count} 个, 缓存 {cached_count} 个 (移动 {moved} 个)")

def main():
    log("=" * 40)
    log("🫀 OpenClaw 轻量优化")
    log("=" * 40)
    
    # 1. 缓存清理
    log("📦 缓存优化:")
    clean_cache()
    stats = cache_stats()
    log(f"   缓存: {stats['entries']} 条, {stats['size_mb']} MB")
    
    # 2. Skills 清理
    log("🧹 Skills 优化:")
    clean_skills()
    
    log("✅ 优化完成")

if __name__ == "__main__":
    main()
