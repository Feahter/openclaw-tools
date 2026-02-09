#!/bin/bash
# voice-simple.sh - 简化版语音输入（无需 sox）
# 使用 macOS 内置录屏功能和 afrecord

# 配置
RESPONSE_FILE="/Users/$USER/.openclaw/workspace/data/voice-response.txt"

echo "🎙️ 简单语音方案"
echo ""
echo "macOS 内置听写快捷键："
echo "  连续按两下 Fn 键 (⌃Fn 或 🌐)"
echo ""
echo "或者手动输入文字"
echo ""

# 启动语音监听（保持运行）
if ! pgrep -f "voice-reader.sh" > /dev/null; then
    echo "🔧 启动语音监听..."
    nohup ~/.openclaw/workspace/tools/voice-reader.sh > /dev/null 2>&1 &
    sleep 1
fi

# 打开文本输入框
osascript <<EOF
tell application "System Events"
    activate
    set dialogResult to display dialog "🎤 按 ⌃Fn 使用听写，或输入文字:" default answer "" buttons {"取消", "发送"} default button "发送" with icon note
    if button returned of dialogResult is "发送" then
        set textReturned to text returned of dialogResult
        do shell script "echo '" & textReturned & "' | pbcopy"
        do shell script "echo '" & textReturned & "' > /Users/$USER/.openclaw/workspace/data/voice-input.txt"
        return textReturned
    else
        return "CANCEL"
    end if
end tell
EOF

if [ "$?" -eq 0 ]; then
    say -v "Ting-Ting" "已复制，请粘贴发送"
    echo "✅ 文字已复制到剪贴板，请粘贴给我"
else
    echo "❌ 已取消"
fi
