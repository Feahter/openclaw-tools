#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# collect-results.py — 收集已完成会话的完整结果
# 用法: ./collect-results.py <session_id>

import json, os, sys, datetime, subprocess
from pathlib import Path

SESSION_ID = sys.argv[1] if len(sys.argv) > 1 else None
if not SESSION_ID:
    print("ERROR: session_id required", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
STATE_DIR = SKILL_DIR / ".state"
RESULTS_DIR = STATE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PROGRESS_FILE = STATE_DIR / "progress" / f"{SESSION_ID}.json"
LOG_FILE = STATE_DIR / "logs" / f"{SESSION_ID}.log"
RESULTS_FILE = RESULTS_DIR / f"{SESSION_ID}.json"

if not PROGRESS_FILE.exists():
    print(f"ERROR: session {SESSION_ID} not found", file=sys.stderr)
    sys.exit(1)

with open(PROGRESS_FILE) as f:
    progress = json.load(f)

AGENT = progress.get("agent", "")
TASK = progress.get("task", "")[:200]
WORKDIR = progress.get("workdir", "")

# Git diff
git_diff = ""
git_status = ""
files_changed = []
if WORKDIR and os.path.isdir(os.path.join(WORKDIR, ".git")):
    try:
        diff_out = subprocess.check_output(
            ["git", "diff", "--stat"], cwd=WORKDIR, stderr=subprocess.DEVNULL, text=True
        )
        status_out = subprocess.check_output(
            ["git", "status", "--short"], cwd=WORKDIR, stderr=subprocess.DEVNULL, text=True
        )
        files_out = subprocess.check_output(
            ["git", "diff", "--name-only"], cwd=WORKDIR, stderr=subprocess.DEVNULL, text=True
        )
        git_diff = diff_out.strip()
        git_status = status_out.strip()
        files_changed = [f for f in files_out.strip().split("\n") if f]
    except Exception:
        pass

# Read log
log_content = ""
if LOG_FILE.exists():
    with open(LOG_FILE) as f:
        log_content = f.read()

progress["status"] = "collected"
progress["collected_at"] = datetime.datetime.utcnow().isoformat() + "Z"
progress["git"] = {
    "diff_summary": git_diff,
    "status": git_status,
    "files_changed": files_changed,
}
progress["log_length"] = len(log_content)
progress["log_preview"] = log_content[-3000:] if len(log_content) > 3000 else log_content

with open(RESULTS_FILE, "w") as f:
    json.dump(progress, f, ensure_ascii=False, indent=2)

print(f"Results saved to {RESULTS_FILE}")
print()
print("=== Summary ===")
print(f"Session: {SESSION_ID}")
print(f"Agent: {AGENT}")
print(f"Files changed: {len(files_changed)}")
for f in files_changed:
    print(f"  + {f}")
if not files_changed:
    print("  (none)")
