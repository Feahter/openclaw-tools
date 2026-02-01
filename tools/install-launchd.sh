#!/bin/bash
#
# OpenClaw 工具集开机启动脚本
# 安装: ./install-launchd.sh
# 卸载: ./install-launchd.sh uninstall
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$SCRIPT_DIR/tools"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$PLIST_DIR/com.openclaw.tools.plist"

install() {
    echo "📦 安装开机启动..."

    # 创建目录
    mkdir -p "$PLIST_DIR"

    # 生成 plist
    cat > "$PLIST_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.tools</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>__TOOLS_DIR__/local-model-manager.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>__HOME__/Library/Logs/openclaw-tools.log</string>
    <key>StandardErrorPath</key>
    <string>__HOME__/Library/Logs/openclaw-tools.err</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

    # 替换路径
    sed -i '' "s|__TOOLS_DIR__|$TOOLS_DIR|g" "$PLIST_FILE"
    sed -i '' "s|__HOME__|$HOME|g" "$PLIST_FILE"

    # 加载
    launchctl load "$PLIST_FILE" 2>/dev/null || true

    echo "✅ 已安装！重启后自动启动:"
    echo "  🔧 http://localhost:8765 - 统一控制台"
    echo "  🤖 http://localhost:8799 - 模型管理"
    echo "  📋 http://localhost:8769 - 任务看板"
    echo "  📈 http://localhost:8770 - Token 统计"
    echo "  ⚡ http://localhost:8771 - 自动化工作流"
    echo "  🔄 任务调度器 (后台自动运行)"
    echo ""
    echo "📋 查看日志:"
    echo "  工具日志: tail -f ~/Library/Logs/openclaw-tools.log"
    echo "  调度日志: tail -f /tmp/scheduler.log"
}

uninstall() {
    echo "🗑️ 卸载开机启动..."
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    rm -f "$PLIST_FILE"
    echo "✅ 已卸载"
}

if [ "$1" = "uninstall" ]; then
    uninstall
else
    install
fi
