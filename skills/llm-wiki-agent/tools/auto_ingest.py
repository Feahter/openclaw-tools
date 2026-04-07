#!/usr/bin/env python3
"""
LLM Wiki Auto-Ingest Script
增量检测并输出待摄入文件列表
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

# 硬编码路径（避免 Path(__file__) 问题）
MEMORY_ROOT = Path("/Users/fuzhuo/.openclaw/workspace/memory")
WIKI_ROOT = Path("/Users/fuzhuo/.openclaw/workspace/skills/llm-wiki-agent/wiki")
STATE_FILE = WIKI_ROOT / ".ingested.json"


def load_state() -> dict:
    """加载摄入状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict):
    """保存摄入状态"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def get_file_hash(filepath: Path) -> str:
    """计算文件内容哈希"""
    content = filepath.read_bytes()
    return hashlib.md5(content).hexdigest()[:12]


def scan_memory() -> list:
    """扫描 memory 目录"""
    files = []
    for f in MEMORY_ROOT.rglob("*.md"):
        # 跳过隐藏目录（但允许 .openclaw 这种顶层配置目录）
        # 只检查 memory 目录内部的隐藏目录
        rel_parts = f.relative_to(MEMORY_ROOT).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        try:
            rel_path = f.relative_to(MEMORY_ROOT)
            files.append({
                "path": str(rel_path),
                "abs_path": str(f),
                "mtime": f.stat().st_mtime,
                "size": f.stat().st_size,
                "hash": get_file_hash(f)
            })
        except Exception as e:
            print(f"Error processing {f}: {e}")
    return sorted(files, key=lambda x: x["mtime"], reverse=True)


def detect_changes(state: dict, files: list) -> dict:
    """检测变更"""
    changes = {"new": [], "modified": [], "unchanged": []}
    current_paths = {f["path"] for f in files}
    state_paths = set(state.keys())
    
    for f in files:
        path = f["path"]
        if path not in state:
            changes["new"].append(f)
        elif state[path].get("hash") != f["hash"]:
            changes["modified"].append(f)
        else:
            changes["unchanged"].append(f)
    
    # 检测删除
    deleted = state_paths - current_paths
    if deleted:
        print(f"Deleted files: {deleted}")
    
    return changes


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--mark-ingested", type=str)
    args = parser.parse_args()
    
    print(f"Scanning {MEMORY_ROOT}...")
    state = load_state()
    files = scan_memory()
    changes = detect_changes(state, files)
    
    if args.status:
        print(f"\n=== LLM Wiki Ingest Status ===")
        print(f"Total files: {len(files)}")
        print(f"Already ingested: {len(state)}")
        print(f"New: {len(changes['new'])}")
        print(f"Modified: {len(changes['modified'])}")
        return
    
    if args.mark_ingested:
        filepath = args.mark_ingested
        for f in files:
            if f["path"] == filepath:
                state[filepath] = {
                    "ingested_at": datetime.now().isoformat(),
                    "mtime": f["mtime"],
                    "hash": f["hash"]
                }
                save_state(state)
                print(f"Marked: {filepath}")
                return
        print(f"Not found: {filepath}")
        return
    
    # 默认：显示待摄入文件
    pending = changes["new"] + changes["modified"]
    if pending:
        print(f"\n=== Pending ingest ({len(pending)}) ===")
        for i, f in enumerate(pending[:15], 1):
            status = "NEW" if f in changes["new"] else "MOD"
            print(f"{i}. [{status}] {f['path']}")
    else:
        print("No files pending ingest.")


if __name__ == "__main__":
    main()
