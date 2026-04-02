#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# check-progress.py — 检查会话进度

import json, os, sys, signal
from pathlib import Path

SESSION_ID = sys.argv[1] if len(sys.argv) > 1 else None
LINES = int(sys.argv[2]) if len(sys.argv) > 2 else 50

if not SESSION_ID:
    print("ERROR: session_id required", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
STATE_DIR = SKILL_DIR / ".state"

PROGRESS_FILE = STATE_DIR / "progress" / f"{SESSION_ID}.json"
LOG_FILE = STATE_DIR / "logs" / f"{SESSION_ID}.log"
PID_FILE = STATE_DIR / "pids" / f"{SESSION_ID}.pid"

if not PROGRESS_FILE.exists():
    print(f"ERROR: session {SESSION_ID} not found")
    sys.exit(1)

with open(PROGRESS_FILE) as f:
    progress = json.load(f)

status = progress.get("status", "unknown")
pid_str = progress.get("pid", "")
if not pid_str and PID_FILE.exists():
    pid_str = PID_FILE.read_text().strip()

# Check if process is still running
running = False
if pid_str:
    try:
        os.kill(int(pid_str), 0)
        running = True
    except (ProcessLookupError, ValueError):
        running = False

if not running and status == "running":
    status = "completed"
    progress["status"] = "completed"
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

print(f"=== Session {SESSION_ID} ===")
print(f"Status:  {status}")
print(f"PID:     {pid_str or 'N/A'}")
print(f"Agent:   {progress.get('agent', '?')}")
print(f"Task:    {progress.get('task', '')[:80]}")
print(f"Started: {progress.get('started_at', '')[:19]}")
print(f"--- Last {LINES} lines ---")

if LOG_FILE.exists():
    lines = LOG_FILE.read_text().splitlines()
    for line in lines[-LINES:]:
        print(line)
else:
    print("(log file not found)")
