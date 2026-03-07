#!/bin/bash
# voice-bridge.sh - 语音交互桥接脚本
# 用法: ./voice-bridge.sh "你的问题"

QUESTION="$1"

if [ -z "$$QUESTION" ]; then
    echo "用法: ./voice-bridge.sh \"你的问题\""
    echo "或:   echo \"你的问题\" | ./voice-bridge.sh"
    exit 1
fi

# 发送给 OpenClaw 并获取回复
echo "🎤 发送: $$QUESTION"

# 使用 openclaw 命令行发送消息并获取回复
# 这里需要替换成实际的 openclaw CLI 调用方式
REPLY=$(openclaw send --message "$$QUESTION" --wait-for-reply 2>/dev/null || echo "请手动复制回复")

echo "💬 回复: $$REPLY"

# 使用 macOS 内置 say 命令朗读回复
if command -v say >/dev/null 2>&1; then
    echo "🔊 朗读中..."
    say -v "Ting-Ting" "$$REPLY" 2>/dev/null || say "$$REPLY"
else
    echo "⚠️  say 命令不可用"
fi
