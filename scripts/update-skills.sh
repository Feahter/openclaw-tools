#!/bin/bash
# OpenClaw Skills 批量更新脚本

set -e

CLAWHUB="npx clawhub@latest"
SKILLS_DIR="$HOME/.openclaw/workspace/skills"

echo "📦 获取已安装的 Skills 列表..."
installed=$($CLAWHUB list 2>/dev/null | grep -v "^$" | tail -n +2)

echo "Found $(echo "$installed" | wc -l) skills to check"
echo ""

count=0
success=0
failed=0

for line in $installed; do
  slug=$(echo "$line" | awk '{print $1}')
  [ -z "$slug" ] && continue
  
  ((count++))
  echo "[$count] Checking $slug..."
  
  result=$($CLAWHUB install "$slug" --force 2>&1)
  
  if echo "$result" | grep -q "OK"; then
    ((success++))
    echo "  ✅ Updated"
  elif echo "$result" | grep -q "not found"; then
    echo "  ⚠️ Not in registry (skip)"
  else
    ((failed++))
    echo "  ❌ Failed: $(echo "$result" | head -1)"
  fi
done

echo ""
echo "📊 统计:"
echo "  总数: $count"
echo "  成功: $success"
echo "  失败: $failed"
