#!/usr/bin/env bash
# collect-results.sh — 收集已完成会话的完整结果
# 用法: ./collect-results.sh <session_id>

set -euo pipefail
SESSION_ID="${1:?用法: collect-results.sh <session_id>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/collect-results.py" "$SESSION_ID"
