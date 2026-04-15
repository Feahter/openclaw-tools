#!/bin/bash
# OpenClaw Subagents 并行批量更新脚本
# 用法: ./parallel-update-skills.sh [并发数]

MAX_PARALLEL=${1:-4}
CLAWHUB="npx clawhub@latest"

echo "🚀 启动并行更新 (并发数: $MAX_PARALLEL)"

# 获取 skills 列表
skills=$($CLAWHUB list 2>/dev/null | grep -v "^$" | tail -n +2 | awk '{print $1}')

# 启动更新任务
pids=()
for skill in $skills; do
  # 后台更新每个 skill
  $CLAWHUB install "$skill" --force >/dev/null 2>&1 &
  pids+=($!)
  
  # 达到并发上限则等待
  while [ ${#pids[@]} -ge $MAX_PARALLEL ]; do
    sleep 1
    # 移除已完成的 PID
    new_pids=()
    for pid in "${pids[@]}"; do
      if kill -0 $pid 2>/dev/null; then
        new_pids+=($pid)
      fi
    done
    pids=("${new_pids[@]}")
  done
done

# 等待所有任务完成
for pid in "${pids[@]}"; do
  wait $pid 2>/dev/null
done

echo "✅ 批量更新完成!"
