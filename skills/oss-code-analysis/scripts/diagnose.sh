#!/usr/bin/env bash
# diagnose.sh — 项目代码质量快速诊断
# 用法：bash diagnose.sh <项目src目录> [语言扩展名，默认ts]
# 示例：bash diagnose.sh ~/project/github/AionUi/src ts

SRC="${1:-.}"
EXT="${2:-ts}"

echo "========================================"
echo "  OSS Code Analysis — 快速诊断"
echo "  目录: $SRC | 语言: .$EXT"
echo "========================================"
echo ""

echo "── 文件规模 ──────────────────────────────"
echo "总文件数:"
find "$SRC" -name "*.$EXT" | grep -v "\.test\.\|\.spec\." | wc -l

echo ""
echo "超大文件 (> 500 行):"
find "$SRC" -name "*.$EXT" | xargs wc -l 2>/dev/null | sort -rn | awk '$1 > 500 && $2 != "total" {printf "  %5d 行  %s\n", $1, $2}' | head -10

echo ""
echo "── 错误处理质量 ──────────────────────────"
TOTAL=$(grep -rn "} catch" "$SRC" --include="*.$EXT" 2>/dev/null | wc -l | tr -d ' ')
SILENT=$(grep -rn "} catch {" "$SRC" --include="*.$EXT" 2>/dev/null | wc -l | tr -d ' ')
WARN=$(grep -rn -A1 "} catch" "$SRC" --include="*.$EXT" 2>/dev/null | grep "console.warn" | wc -l | tr -d ' ')
THROW=$(grep -rn -A1 "} catch" "$SRC" --include="*.$EXT" 2>/dev/null | grep -E "throw|reject" | wc -l | tr -d ' ')

echo "  总 catch 块:    $TOTAL"
echo "  静默吞掉:       $SILENT"
echo "  只打 warn:      $WARN"
echo "  throw/reject:   $THROW"

if [ "$TOTAL" -gt 0 ]; then
  RATIO=$(echo "scale=1; $SILENT * 100 / $TOTAL" | bc 2>/dev/null || echo "?")
  echo "  静默比例:       ${RATIO}%"
  if [ "$SILENT" -gt 0 ] && [ "$(echo "$RATIO > 30" | bc 2>/dev/null)" = "1" ]; then
    echo "  ⚠️  静默 catch 比例过高，技术债警告"
  fi
fi

echo ""
echo "── 历史债务 ──────────────────────────────"
echo "TODO/FIXME/HACK:"
grep -rn "TODO\|FIXME\|HACK" "$SRC" --include="*.$EXT" 2>/dev/null | wc -l | tr -d ' ' | xargs echo " "
echo "legacy/deprecated/backward compat:"
grep -rn "legacy\|deprecated\|backward compat" "$SRC" --include="*.$EXT" 2>/dev/null | wc -l | tr -d ' ' | xargs echo " "

echo ""
echo "── 架构信号 ──────────────────────────────"
echo "单例数量 (static instance):"
grep -rn "static instance" "$SRC" --include="*.$EXT" 2>/dev/null | wc -l | tr -d ' ' | xargs echo " "

echo "any 使用数量:"
grep -rn ": any\|as any\|<any>" "$SRC" --include="*.$EXT" 2>/dev/null | wc -l | tr -d ' ' | xargs echo " "

echo ""
echo "── 测试覆盖 ──────────────────────────────"
TEST=$(find . -name "*.test.$EXT" -o -name "*.spec.$EXT" 2>/dev/null | wc -l | tr -d ' ')
SRC_COUNT=$(find "$SRC" -name "*.$EXT" 2>/dev/null | grep -v "\.test\.\|\.spec\." | wc -l | tr -d ' ')
echo "  测试文件: $TEST"
echo "  源码文件: $SRC_COUNT"
if [ "$SRC_COUNT" -gt 0 ]; then
  RATIO=$(echo "scale=1; $TEST * 100 / $SRC_COUNT" | bc 2>/dev/null || echo "?")
  echo "  覆盖比例: ${RATIO}%"
fi

echo ""
echo "── 被依赖最多的模块 (Top 10) ────────────"
grep -rh "from ['\"]" "$SRC" --include="*.$EXT" 2>/dev/null \
  | sed -E "s/.*from ['\"]([^'\"]+)['\"].*/\1/" \
  | grep -v "^[./]" \
  | sort | uniq -c | sort -rn | head -10 \
  | awk '{printf "  %3d次  %s\n", $1, $2}'

echo ""
echo "========================================"
echo "  诊断完成。详细分析请参考 SKILL.md 流程。"
echo "========================================"
