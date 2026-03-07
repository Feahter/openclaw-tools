#!/bin/bash
# voice-chat.sh - 一键语音对话
# 用法: ./voice-chat.sh

RECORDING_FILE="/tmp/openclaw-recording.wav"
INPUT_FILE="/Users/$USER/.openclaw/workspace/data/voice-input.txt"

echo "🎙️ 开始录音 (按 Ctrl+C 停止)..."

# 使用 sox 录音（需要先安装: brew install sox）
if command -v rec &> /dev/null; then
    rec "$RECORDING_FILE" 2>/dev/null
else
    # 备用方案：使用 macOS 内置的音频录制
    echo "⚠️ 请先安装 sox: brew install sox"
    echo "或者手动输入:"
    read -p "> " text_input
    echo "$text_input" > "$INPUT_FILE"
    echo "✅ 已记录: $text_input"
    exit 0
fi

if [ -f "$RECORDING_FILE" ]; then
    echo "✅ 录音完成，准备识别..."
    
    # 如果安装了 whisper，这里调用识别
    if command -v whisper &> /dev/null; then
        TEXT=$(whisper "$RECORDING_FILE" --language Chinese --output_format txt 2>/dev/null | head -1)
        echo "📝 识别结果: $TEXT"
        echo "$TEXT" > "$INPUT_FILE"
    else
        echo "⚠️ Whisper 未安装，录音保存在: $RECORDING_FILE"
    fi
    
    rm -f "$RECORDING_FILE"
fi

echo ""
echo "下一步:"
echo "1. 把 ~/.openclaw/workspace/data/voice-input.txt 的内容发给我"
echo "2. 收到回复后运行: say -v Ting-Ting '回复内容'"
