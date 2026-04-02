#!/usr/bin/env bash
# check-progress.sh — 检查会话进度
# 用法: ./check-progress.sh <session_id> [tail_lines=50]

set -euo pipefail

SESSION_ID="${1:?用法: check-progress.sh <session_id>}"
LINES="${2:-50}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
STATE_DIR="$SKILL_DIR/.state"
PYTHON_CHECK="$SCRIPT_DIR/check-progress.py"

# 如果有 Python 检查脚本就用 Python
if [[ -f "$PYTHON_CHECK" ]]; then
    python3 "$PYTHON_CHECK" "$SESSION_ID" "$LINES"
    exit 0
fi

# 纯 bash 回退
LOG_FILE="$STATE_DIR/logs/$SESSION_ID.log"
PROGRESS_FILE="$STATE_DIR/progress/$SESSION_ID.json"
PID_FILE="$STATE_DIR/pids/$SESSION_ID.pid"

if [[ ! -f "$PROGRESS_FILE" ]]; then
    echo "ERROR: session $SESSION_ID not found"
    exit 1
fi

STATUS=$(python3 -c "
import json
d=json.load(open('$PROGRESS_FILE'))
print(d.get('status','unknown'))
" 2>/dev/null || echo "unknown")

RUNNING="false"
if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    kill -0 "$PID" 2>/dev/null && RUNNING="true"
fi

if [[ "$RUNNING" == "false" && "$STATUS" == "running" ]]; then
    STATUS="completed"
fi

echo "=== Session $SESSION_ID ==="
echo "Status: $STATUS"
echo "PID: $(cat "$PID_FILE" 2>/dev/null || echo 'N/A')"
echo "--- Last $LINES lines ---"
tail -n "$LINES" "$LOG_FILE" 2>/dev/null || echo "(no output)"
