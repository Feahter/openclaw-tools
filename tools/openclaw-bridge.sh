#!/bin/bash
# openclaw-bridge.sh - Siri/OpenClaw 桥接脚本
# 常驻后台运行，监听语音输入请求

REQUEST_FILE="/Users/$USER/.openclaw/workspace/data/siri-input.txt"
RESPONSE_FILE="/Users/$USER/.openclaw/workspace/data/siri-response.txt"
LOG_FILE="/Users/$USER/.openclaw/workspace/data/siri-bridge.log"

# 确保目录存在
mkdir -p "$(dirname "$REQUEST_FILE")"

# 清理旧文件
> "$REQUEST_FILE"
> "$RESPONSE_FILE"

echo "$(date): 🟢 OpenClaw Siri 桥接启动" | tee -a "$LOG_FILE"
echo "监听文件: $REQUEST_FILE"
echo ""
echo "使用方式:"
echo "1. 运行此脚本保持后台: nohup ./openclaw-bridge.sh >/dev/null 2>&1 &"
echo "2. 在 Shortcuts 里把语音写入 $REQUEST_FILE"
echo "3. 从 $RESPONSE_FILE 读取回复"
echo ""

# 主循环
while true; do
    # 检查是否有新输入
    if [ -s "$REQUEST_FILE" ]; then
        INPUT=$(cat "$REQUEST_FILE")
        TIMESTAMP=$(date +%H:%M:%S)
        
        echo ""
        echo "[$TIMESTAMP] 📩 收到: $INPUT"
        
        # 清空输入文件（表示已处理）
        > "$REQUEST_FILE"
        
        # 显示提示，等待用户手动复制回复
        echo "[$TIMESTAMP] ⏳ 请把回复写入: $RESPONSE_FILE"
        echo "    echo '你的回复' > $RESPONSE_FILE"
        
        # 记录到日志
        echo "[$TIMESTAMP] REQUEST: $INPUT" >> "$LOG_FILE"
    fi
    
    # 每秒检查一次
    sleep 1
done
