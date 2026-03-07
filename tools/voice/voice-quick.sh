#!/bin/bash
# voice-quick.sh - 快速语音输入 + 朗读
# 用法: 绑定到快捷键 (如 ⌃⌥Space)

# 配置
RECORDING_FILE="/tmp/openclaw-voice-$(date +%s).wav"
INPUT_FILE="/Users/$USER/.openclaw/workspace/data/voice-input.txt"
RESPONSE_FILE="/Users/$USER/.openclaw/workspace/data/voice-response.txt"

# 检查 sox
if ! command -v rec &> /dev/null; then
    osascript -e 'display notification "请先安装 sox: brew install sox" with title "OpenClaw Voice"'
    exit 1
fi

# 播放提示音
afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || true

echo "🔴 录音中... (按 Enter 停止)"

# 后台录音
rec "$RECORDING_FILE" 2>/dev/null &
REC_PID=$!

# 等待用户按 Enter
read -t 10

# 停止录音
kill $REC_PID 2>/dev/null
wait $REC_PID 2>/dev/null

# 播放停止提示音
afplay /System/Library/Sounds/Basso.aiff 2>/dev/null || true

if [ ! -f "$RECORDING_FILE" ] || [ ! -s "$RECORDING_FILE" ]; then
    osascript -e 'display notification "录音失败，请重试" with title "OpenClaw Voice"'
    exit 1
fi

# 尝试用 Whisper 识别（如果安装了）
if command -v whisper &> /dev/null; then
    TEXT=$(whisper "$RECORDING_FILE" --language Chinese --output_format txt 2>/dev/null | head -1 | sed 's/^[[:space:]]*//')
else
    # 没装 Whisper，用 macOS 内置听写
    # 播放录音让用户听到自己说的
    TEXT=""
fi

# 清理录音文件
rm -f "$RECORDING_FILE"

if [ -n "$TEXT" ]; then
    # 写入文件
    echo "$TEXT" > "$INPUT_FILE"
    
    # 复制到剪贴板
    echo "$TEXT" | pbcopy
    
    # 显示确认对话框
    osascript <<EOF
tell application "System Events"
    set dialogResult to display dialog "识别结果:" default answer "$TEXT" buttons {"取消", "发送"} default button "发送" with icon note
    if button returned of dialogResult is "发送" then
        set textReturned to text returned of dialogResult
        do shell script "echo '" & textReturned & "' | pbcopy"
        return "OK"
    else
        return "CANCEL"
    end if
end tell
EOF
    
    if [ "$?" -eq 0 ]; then
        osascript -e 'display notification "已复制到剪贴板，请粘贴发送" with title "OpenClaw Voice"'
        say -v "Ting-Ting" "已准备好，请粘贴发送"
    fi
else
    # 没识别出文字，让用户手动输入
    osascript -e 'display notification "未识别到语音，请手动输入" with title "OpenClaw Voice"'
fi
