#!/bin/bash
# Xcode 修复提醒脚本
# 运行时间: 2026-03-02 21:30

MESSAGE="🔧 提醒：修复 Xcode CommandLineTools"

echo "$MESSAGE"
echo "问题：xcrun 报错 invalid developer path"
echo "解决：sudo rm -rf /Library/Developer/CommandLineTools && xcode-select --install"

# 发送消息到 Feishu（通过 OpenClaw）
openclaw message send --channel feishu --target ou_0e5857df3bb6f78a51014c325c0d2c81 --message "$MESSAGE

问题：xcrun 报错 invalid developer path
解决：sudo rm -rf /Library/Developer/CommandLineTools && xcode-select --install"
