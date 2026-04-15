#!/usr/bin/env bash
# list-sessions.sh — 列出所有活跃会话
# 用法: ./list-sessions.sh [status_filter]
# status_filter: running|completed|all (default: all)

FILTER="${1:-all}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$(dirname "$SCRIPT_DIR")/.state"
PROGRESS_DIR="$STATE_DIR/progress"

mkdir -p "$PROGRESS_DIR"

echo "=== Coding Agent Sessions ==="
echo ""

if [[ ! -d "$PROGRESS_DIR" ]] || [[ -z "$(ls -A "$PROGRESS_DIR" 2>/dev/null)" ]]; then
  echo "No sessions found."
  exit 0
fi

for f in "$PROGRESS_DIR"/*.json; do
  [[ -f "$f" ]] || continue
  SESSION=$(basename "$f" .json)

  python3 -c "
import json, sys, os
f = '$f'
try:
    d = json.load(open(f))
    sid = d.get('session_id', '$SESSION')
    agent = d.get('agent', '?')
    task = d.get('task', '')[:60]
    status = d.get('status', '?')
    started = d.get('started_at', '')[:19]
    workdir = d.get('workdir', '')
    pid = ''
    pid_file = '$STATE_DIR/pids/' + sid + '.pid'
    if os.path.exists(pid_file):
        pid = open(pid_file).read().strip()
    # status filter
    filter = '$FILTER'
    if filter != 'all' and status != filter:
        sys.exit(0)
    print(f'SESSION: {sid}')
    print(f'  Status:  {status}')
    print(f'  Agent:   {agent}')
    print(f'  PID:     {pid}')
    print(f'  Started: {started}')
    print(f'  Task:   {task}')
    print(f'  Dir:    {workdir}')
    print()
except Exception as e:
    print(f'ERROR {sid}: {e}', file=sys.stderr)
" 2>/dev/null
done
