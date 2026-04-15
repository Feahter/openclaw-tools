#!/usr/bin/env bash
# Screenshot Skill - 屏幕截图工具
# 使用 macOS 原生 screencapture

OUTPUT_DIR="${1:-$HOME/Desktop}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/screenshot_${TIMESTAMP}.png"

# 检查 screencapture 是否可用
if ! command -v screencapture &> /dev/null; then
    echo "错误: screencapture 命令不可用"
    echo "此 Skill 仅支持 macOS 系统"
    exit 1
fi

# 解析参数
case "${1:-full}" in
    full|--full)
        # 截取整个屏幕
        screencapture -x "$OUTPUT_FILE"
        ;;
    interactive|-i|--interactive|-i)
        # 交互式选择（窗口或区域）
        screencapture -i -x "$OUTPUT_FILE"
        ;;
    window|--window|-W)
        # 截取特定窗口（需要提供窗口名称）
        WINDOW_NAME="${2:-}"
        if [ -z "$WINDOW_NAME" ]; then
            echo "请指定窗口名称"
            echo "用法: screenshot window <窗口名>"
            exit 1
        fi
        screencapture -w "$OUTPUT_FILE"
        ;;
    region|--region|-R)
        # 交互式选择区域
        screencapture -s -x "$OUTPUT_FILE"
        ;;
    help|--help|-h)
        echo "Screenshot Skill - 屏幕截图工具"
        echo ""
        echo "用法: screenshot [类型] [参数]"
        echo ""
        echo "类型:"
        echo "  full        截取整个屏幕 (默认)"
        echo "  interactive  交互式选择窗口或区域 (-i)"
        echo "  region      交互式选择区域 (-s)"
        echo "  window      截取特定窗口 (-w)"
        echo ""
        echo "输出目录: $OUTPUT_DIR"
        exit 0
        ;;
    *)
        # 未知参数，尝试作为文件名
        OUTPUT_FILE="$1"
        screencapture -x "$OUTPUT_FILE"
        ;;
esac

# 检查是否成功
if [ $? -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
    echo "截图已保存: $OUTPUT_FILE"
    echo "MEDIA: $OUTPUT_FILE"
else
    echo "截图失败或被取消"
    exit 1
fi
