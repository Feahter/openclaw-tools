#!/usr/bin/env bash
# talent-mind.sh — 天才思维启动器（三层递归操作系统）
# 用法: ./talent-mind.sh "<问题描述>"
# 输出: 结构化的三层思维分析

set -euo pipefail

PROBLEM="${1:?用法: talent-mind.sh \"你的问题\"}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$(dirname "$SCRIPT_DIR")/.state"
LOG_FILE="$STATE_DIR/talent-mind-$(date +%Y%m%d-%H%M%S).md"

mkdir -p "$STATE_DIR"

echo "=== 天才思维三层操作系统 ===" > "$LOG_FILE"
echo "问题: $PROBLEM" >> "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# ═══════════════════════════════════════════
# 第一层：认知架构（系统A/B双轨）
# ═══════════════════════════════════════════
echo "## 第一层：认知架构" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "### 系统A直觉（快）" >> "$LOG_FILE"
echo "**直觉反应**：对这个问题的第一印象是什么？" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "### 系统B验证（慢）" >> "$LOG_FILE"
echo "**强制反例搜索**：这个直觉在什么条件下失效？" >> "$LOG_FILE"
echo "- 反例1: " >> "$LOG_FILE"
echo "- 反例2: " >> "$LOG_FILE"
echo "- 反例3: " >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "### 系统冲突结论" >> "$LOG_FILE"
echo "当系统A和系统B冲突时，真正的认知发生在张力区：" >> "$LOG_FILE"
echo "**结论**：___" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# ═══════════════════════════════════════════
# 第二层：表征方式（多模态转换）
# ═══════════════════════════════════════════
echo "## 第二层：表征方式" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "### 表征1：数学/精确语言" >> "$LOG_FILE"
echo "用精确的语言重新表述问题（定义变量、量化关系）：" >> "$LOG_FILE"
echo "___" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "### 表征2：几何/视觉语言" >> "$LOG_FILE"
echo "画出来/用空间关系描述（即使无法画，也要想象空间结构）：" >> "$LOG_FILE"
echo "___" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "### 表征3：隐喻/叙事语言" >> "$LOG_FILE"
echo "用一个日常故事或类比来描述问题的核心：" >> "$LOG_FILE"
echo "___" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "### 表征发现" >> "$LOG_FILE"
echo "**哪个表征暴露了其他表征没有发现的盲区？**" >> "$LOG_FILE"
echo "___" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# ═══════════════════════════════════════════
# 第三层：元认知协议（递归循环）
# ═══════════════════════════════════════════
echo "## 第三层：元认知协议" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "### 对象层（第一层答案是什么）" >> "$LOG_FILE"
echo "**我的答案**：___" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "### 过程层（我为什么这样思考）" >> "$LOG_FILE"
echo "**我的思考路径**：___" >> "$LOG_FILE"
echo "**用了什么隐含假设**：___" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "### 元层（我的思考框架本身是否正确）" >> "$LOG_FILE"
echo "**如果推翻自己的核心假设**：___" >> "$LOG_FILE"
echo "**我用的分类标准本身是否有问题**：___" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# ═══════════════════════════════════════════
# 四组对立统一审视
# ═══════════════════════════════════════════
echo "## 四组对立统一审视" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "| 张力对 | 分解视角 | 综合视角 | 发现 |" >> "$LOG_FILE"
echo "|--------|---------|---------|------|" >> "$LOG_FILE"
echo "| 分解↔综合 | ___ | ___ | ___ |" >> "$LOG_FILE"
echo "| 抽象↔具体 | ___ | ___ | ___ |" >> "$LOG_FILE"
echo "| 怀疑↔确信 | ___ | ___ | ___ |" >> "$LOG_FILE"
echo "| 自我↔无我 | ___ | ___ | ___ |" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# ═══════════════════════════════════════════
# 负空间意识
# ═══════════════════════════════════════════
echo "## 负空间意识" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "**默认排除了什么**：___" >> "$LOG_FILE"
echo "**创造了什么新问题**：___" >> "$LOG_FILE"
echo "**如果核心假设是错的**：___" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# ═══════════════════════════════════════════
# 最终洞察
# ═══════════════════════════════════════════
echo "## 最终洞察（认知复利时刻）" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "三层分析后，最突破性的发现是什么？" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "1. ___" >> "$LOG_FILE"
echo "2. ___" >> "$LOG_FILE"
echo "3. ___" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
echo "*天才思维三层操作系统 | $(date '+%Y-%m-%d %H:%M:%S')*" >> "$LOG_FILE"

cat "$LOG_FILE"
echo ""
echo "→ 已保存到 $LOG_FILE"
