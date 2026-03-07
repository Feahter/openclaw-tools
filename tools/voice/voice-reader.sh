#!/bin/bash
# voice-reader.sh - 自动朗读 OpenClaw 回复
# 用法: 在另一个终端保持运行

RESPONSE_FILE="/Users/$USER/.openclaw/workspace/data/voice-response.txt"
LAST_FILE="/Users/$USER/.openclaw/workspace/data/.voice-response-last"

echo "🎧 OpenClaw 语音回复监听启动"
echo "使用方法:"
echo "1. 把我给你的回复复制保存到: $RESPONSE_FILE"
echo "   echo '回复内容' > $RESPONSE_FILE"
echo "2. 或者粘贴到这里，按 Ctrl+C 结束"
echo ""

# 确保文件存在
touch "$RESPONSE_FILE"
[ -f "$LAST_FILE" ] || echo "" > "$LAST_FILE"

# 轮询监听文件变化
echo "🔄 监听文件变化..."
(
    LAST_CHECKSUM=""
    while true; do
        if [ -s "$RESPONSE_FILE" ]; then
            TEXT=$(cat "$RESPONSE_FILE" | tr -d '\n\r')
            CHECKSUM=$(echo "$TEXT" | md5)
            
            # 避免重复朗读
            if [ "$CHECKSUM" != "$LAST_CHECKSUM" ] && [ -n "$TEXT" ]; then
                echo ""
                echo "💬 收到回复: $TEXT"
                echo "🔊 朗读中..."
                
                # 使用中文语音
                say -v "Ting-Ting" "$TEXT"
                
                # 保存本次校验
                LAST_CHECKSUM="$CHECKSUM"
            fi
        fi
        sleep 1
    done
) &

BG_PID=$!

# 捕获退出信号
trap 'kill $BG_PID 2>/dev/null; exit' INT

# 同时支持直接输入
echo "或者直接输入文字朗读 (按 Ctrl+C 退出):"
while IFS= read -r line; do
    if [ -n "$line" ]; then
        echo "🔊 朗读: $line"
        say -v "Ting-Ting" "$line"
        
        # 同时保存到响应文件
        echo "$line" > "$RESPONSE_FILE"
    fi
done
