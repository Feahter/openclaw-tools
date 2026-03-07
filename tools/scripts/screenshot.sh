#!/usr/bin/env bash
# Quick Screenshot Tool - 快速截图工具
# 用于 OpenClaw 直接调用

# 设置输出目录
OUTPUT_DIR="/Users/fuzhuo/.openclaw/workspace"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/screenshot_${TIMESTAMP}.png"

# 截取整个屏幕（带阴影效果，更美观）
screencapture -x "$OUTPUT_FILE"

# 检查结果
if [ $? -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
    echo "截图已保存: $OUTPUT_FILE"
    # 输出文件路径供外部读取
    echo "$OUTPUT_FILE" > /tmp/last_screenshot_path.txt
else
    echo "截图失败"
    exit 1
fi
