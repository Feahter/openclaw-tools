#!/bin/bash
# quick-tts.sh - 快速语音测试

text="${1:-你好，这是一条测试语音。我的声音怎么样？}"

echo "🎙️ 朗读文本: $text"
echo ""

# 使用中文语音（Ting-Ting 是普通话）
say -v "Ting-Ting" "$text"

echo ""
echo "✅ 朗读完成"
