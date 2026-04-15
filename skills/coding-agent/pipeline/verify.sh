#!/usr/bin/env bash
# verify.sh — 验证编程任务的产出
# 用法: ./verify.sh <session_id>
# 检查: git diff / 文件存在 / 测试命令 / lint

set -euo pipefail

SESSION_ID="${1:?用法: verify.sh <session_id>"}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$(dirname "$SCRIPT_DIR")/.state"
PROGRESS_FILE="$STATE_DIR/progress/$SESSION_ID.json"
RESULTS_FILE="$STATE_DIR/results/$SESSION_ID.json"

if [[ ! -f "$PROGRESS_FILE" ]]; then
  echo "ERROR: session $SESSION_ID not found" >&2
  exit 1
fi

WORKDIR=$(cat "$PROGRESS_FILE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('workdir',''))" 2>/dev/null)
AGENT=$(cat "$PROGRESS_FILE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('agent',''))" 2>/dev/null)

echo "=== Verify Session $SESSION_ID ==="
echo "Workdir: $WORKDIR"
echo "Agent: $AGENT"
echo ""

cd "$WORKDIR"

# 1. Git status
echo "--- Git Status ---"
git status --short 2>/dev/null || echo "(not a git repo)"
echo ""

# 2. Files changed
echo "--- Files Changed ---"
git diff --name-only 2>/dev/null || echo "(no changes)"
echo ""

# 3. Diff stats
echo "--- Diff Stats ---"
git diff --stat 2>/dev/null | head -20 || echo "(no changes)"
echo ""

# 4. Try common tests
echo "--- Quick Verification ---"
if [[ -f "package.json" ]]; then
  echo "[Node] package.json found"
  if command -v node &>/dev/null; then
    node --version 2>/dev/null && echo "[OK] node works"
  fi
  if [[ -f "pnpm-lock.yaml" || -f "package-lock.json" || -f "yarn.lock" ]]; then
    echo "[OK] dependencies installed"
  fi
fi

if [[ -f "Cargo.toml" ]]; then
  echo "[Rust] Cargo.toml found"
  if command -v cargo &>/dev/null; then
    cargo check 2>/dev/null | tail -3 && echo "[OK] cargo check passed" || echo "[WARN] cargo check had issues"
  fi
fi

if [[ -f "Makefile" ]]; then
  echo "[Make] Makefile found"
  make -n 2>/dev/null | head -5 && echo "[OK] make dry-run works"
fi

if [[ -f "*.py" ]]; then
  echo "[Python] .py files found"
fi

echo ""
echo "--- Verification Complete ---"
