#!/usr/bin/env python3
"""
memory_backup.py — 记忆文件备份
备份 memory/ 目录到 GitHub openclaw-tools 仓库
rolling backup，保留 7 天
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw/workspace"
MEMORY_DIR = WORKSPACE / "memory"
BACKUP_BASE = WORKSPACE / ".state/backups"
STATE_FILE = BACKUP_BASE / "backup-state.json"
BACKUP_DAYS = 7
GIT_REMOTE = "https://github.com/Feahther/openclaw-tools.git"
GIT_BRANCH = "main"
GIT_TOKEN = os.environ.get("GITHUB_TOKEN", "")

EXCLUDE_PATTERNS = {
    ".trash",
    "node_modules",
    ".git",
    "__pycache__",
}

# 不备份二进制/黑盒文件
EXCLUDE_EXTENSIONS = {".db", ".sqlite", ".sqlite-wal", ".sqlite-shm", ".log", ".tmp"}


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_backup": None, "backup_count": 0, "last_hash": None}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_file_hash(path):
    """快速文件指纹：mtime + size"""
    stat = path.stat()
    return f"{stat.st_mtime:.0f}_{stat.st_size}"


def get_all_memory_files():
    """获取所有需要备份的记忆文件"""
    files = []
    for root, dirs, filenames in os.walk(MEMORY_DIR):
        # 过滤目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_PATTERNS]

        for fname in filenames:
            fpath = Path(root) / fname
            ext = fpath.suffix.lower()

            if ext in EXCLUDE_EXTENSIONS:
                continue
            if any(ex in str(fpath) for ex in EXCLUDE_PATTERNS):
                continue

            files.append(fpath)
    return files


def create_backup_manifest(files):
    """生成备份清单"""
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "files": [],
    }
    for f in files:
        rel = f.relative_to(WORKSPACE)
        manifest["files"].append({
            "path": str(rel),
            "size": f.stat().st_size,
            "mtime": f.stat().st_mtime,
            "hash": get_file_hash(f),
        })
    return manifest


def incremental_backup(files):
    """
    增量备份：只备份有变化的文件
    返回：新增/修改的文件列表
    """
    state = load_state()
    last_hash = state.get("last_hash") or {}

    changed = []
    current_hash = {}

    for f in files:
        h = get_file_hash(f)
        current_hash[str(f)] = h
        if last_hash.get(str(f)) != h:
            changed.append(f)

    state["last_hash"] = current_hash
    save_state(state)
    return changed


def write_backup(changed_files):
    """写入备份文件到 .state/backups/"""
    today = datetime.now().strftime("%Y-%m-%d")
    backup_dir = BACKUP_BASE / today
    backup_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for f in changed_files:
        rel = f.relative_to(WORKSPACE)
        dest = backup_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        written.append(str(rel))

    # 写入清单
    manifest = create_backup_manifest(changed_files)
    manifest_path = backup_dir / "_manifest.json"
    with open(manifest_path, "w") as mf:
        json.dump(manifest, mf, indent=2, ensure_ascii=False)

    # 清理旧备份
    cleanup_old_backups()

    return backup_dir, written


def cleanup_old_backups():
    """删除超过 7 天的备份"""
    if not BACKUP_BASE.exists():
        return

    cutoff = datetime.now() - timedelta(days=BACKUP_DAYS)
    removed = []

    for d in BACKUP_BASE.iterdir():
        if not d.is_dir():
            continue
        try:
            dt = datetime.strptime(d.name, "%Y-%m-%d")
            if dt < cutoff:
                shutil.rmtree(d)
                removed.append(d.name)
        except ValueError:
            pass  # 不是日期格式，跳过

    return removed


def git_backup_push(backup_dir):
    """推送备份到 GitHub（可选，需要 token）"""
    if not GIT_TOKEN:
        return None, "GITHUB_TOKEN not set, skipping push"

    try:
        # 设置 git config
        env = os.environ.copy()
        env["GIT_ASKPASS"] = "echo"

        result = subprocess.run(
            ["git", "clone", "--depth=1", f"https://{GIT_TOKEN}@github.com/Feahther/openclaw-tools.git", str(backup_dir.parent / "_git_temp")],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return None, f"git clone failed: {result.stderr[:100]}"

        return True, "pushed"
    except Exception as e:
        return None, str(e)[:100]


def run_backup():
    state = load_state()
    files = get_all_memory_files()
    changed = incremental_backup(files)

    if not changed:
        state["last_backup"] = datetime.now().isoformat()
        save_state(state)
        return {
            "status": "no_changes",
            "files_checked": len(files),
            "files_changed": 0,
            "message": "没有文件变化，跳过备份",
        }

    backup_dir, written = write_backup(changed)

    state["last_backup"] = datetime.now().isoformat()
    state["backup_count"] += 1
    save_state(state)

    return {
        "status": "success",
        "files_checked": len(files),
        "files_changed": len(changed),
        "backup_dir": str(backup_dir),
        "files": written[:10],  # 只显示前10个
    }


if __name__ == "__main__":
    result = run_backup()
    print(json.dumps(result, indent=2, ensure_ascii=False))
