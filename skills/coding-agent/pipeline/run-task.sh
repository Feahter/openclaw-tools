#!/usr/bin/env bash
# run-task.sh — 启动一个编程任务会话（Claude Code 非交互模式）
# 用法: ./run-task.sh <task> <workdir> [session_id]
# 环境变量: AGENT=claude|opencode (default: claude)
# 返回: session_id 和 JSON 状态

set -euo pipefail

TASK="${1:?用法: run-task.sh <task> <workdir> [session_id]}"
WORKDIR="${2:?需要指定工作目录}"
SESSION_ID="${3:-$(date +%s)-$$}"
AGENT="${AGENT:-claude}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
STATE_DIR="$SKILL_DIR/.state"
LOG_DIR="$STATE_DIR/logs"
PROGRESS_DIR="$STATE_DIR/progress"
PID_DIR="$STATE_DIR/pids"

mkdir -p "$LOG_DIR" "$PROGRESS_DIR" "$PID_DIR"

LOG_FILE="$LOG_DIR/$SESSION_ID.log"
PROGRESS_FILE="$PROGRESS_DIR/$SESSION_ID.json"
PID_FILE="$PID_DIR/$SESSION_ID.pid"

# 验证 agent 可用
case "$AGENT" in
  claude)
    if ! command -v claude &>/dev/null; then
      echo "ERROR: claude not found. Install from https://claude.ai/code" >&2
      exit 1
    fi
    ;;
  opencode)
    if ! command -v opencode &>/dev/null; then
      echo "ERROR: opencode not found." >&2
      exit 1
    fi
    ;;
  *)
    echo "ERROR: unknown agent: $AGENT" >&2
    exit 1
    ;;
esac

# 验证 workdir
if [[ ! -d "$WORKDIR" ]]; then
  echo "ERROR: workdir not found: $WORKDIR" >&2
  exit 1
fi

# 构建命令
case "$AGENT" in
  claude)
    # 非交互模式：-p 打印输出，--output-format json 结构化输出
    CMD="claude -p \"$TASK\" --output-format json --no-session-persistence --permission-mode bypassPermissions"
    ;;
  opencode)
    # opencode run 是非交互模式
    CMD="opencode run \"$TASK\""
    ;;
esac

# 记录会话状态
cat > "$PROGRESS_FILE" <<EOF
{
  "session_id": "$SESSION_ID",
  "agent": "$AGENT",
  "task": "$TASK",
  "workdir": "$WORKDIR",
  "status": "running",
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "log_file": "$LOG_FILE"
}
EOF

# 启动后台进程
cd "$WORKDIR"
nohup bash -c "$CMD" > "$LOG_FILE" 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"

# 等待一下确认进程启动了
sleep 1
if ! kill -0 "$PID" 2>/dev/null; then
  echo "ERROR: process failed to start" >&2
  cat "$LOG_FILE"
  exit 1
fi

echo "SESSION_ID=$SESSION_ID PID=$PID"
