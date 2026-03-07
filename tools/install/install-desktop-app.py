#!/usr/bin/env python3
"""
创建 OpenClaw 桌面应用入口
安装: python3 install-desktop-app.py
"""

import subprocess
import os
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace" / "tools"
APP_DIR = Path.home() / "Applications" / "OpenClaw Tools.app"

def create_app():
    """创建 macOS 应用"""
    print("🔧 创建 OpenClaw Tools 桌面应用...")
    
    # 创建目录结构
    APP_DIR.mkdir(parents=True, exist_ok=True)
    contents_dir = APP_DIR / "Contents"
    resources_dir = contents_dir / "Resources"
    macos_dir = contents_dir / "MacOS"
    
    resources_dir.mkdir(exist_ok=True)
    macos_dir.mkdir(exist_ok=True)
    
    # AppleScript - 智能启动服务
    script = f'''tell application "System Events"
    set workspace to "{WORKSPACE}"
    
    -- 检查并启动 8765 控制台服务
    try
        do shell script "curl -s http://localhost:8765/ > /dev/null 2>&1"
        set consoleRunning to (result starts with "<")
    on error
        set consoleRunning to false
    end try
    
    if not consoleRunning then
        do shell script "cd \\"" & workspace & "\\" && python3 unified-console.py &"
        delay 2
    end if
    
    -- 检查并启动 8768 模型管理服务
    try
        do shell script "curl -s http://localhost:8768/api/status > /dev/null 2>&1"
        set modelRunning to (result starts with "{") and (result contains "status")
    on error
        set modelRunning to false
    end try
    
    if not modelRunning then
        do shell script "cd \\"" & workspace & "\\" && python3 local-model-manager.py &"
        delay 2
    end if
    
    -- 打开浏览器
    tell application "Safari"
        activate
        open location "http://localhost:8765"
    end tell
end tell
'''
    
    # 保存 AppleScript
    script_file = resources_dir / "openclaw.scpt"
    with open(script_file, 'w') as f:
        f.write(script)
    
    # Info.plist
    plist = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key><string>en</string>
    <key>CFBundleExecutable</key><string>OpenClaw</string>
    <key>CFBundleIconFile</key><string></string>
    <key>CFBundleIdentifier</key><string>com.openclaw.tools</string>
    <key>CFBundleInfoDictionaryVersion</key><string>6.0</string>
    <key>CFBundleName</key><string>OpenClaw Tools</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>CFBundleShortVersionString</key><string>1.0</string>
    <key>CFBundleVersion</key><string>1</string>
    <key>LSMinimumSystemVersion</key><string>10.15</string>
    <key>NSHumanReadableCopyright</key><string>Copyright 2026</string>
    <key>NSPrincipalClass</keyApplication</string>
><string>NS</dict>
</plist>'''
    
    with open(contents_dir / "Info.plist", 'w') as f:
        f.write(plist)
    
    # 可执行文件
    exec_script = f'''#!/bin/bash
osascript "{script_file}"
'''
    
    exec_file = macos_dir / "OpenClaw"
    with open(exec_file, 'w') as f:
        f.write(exec_script)
    
    os.chmod(exec_file, 0o755)
    os.chmod(str(script_file), 0o644)
    
    print(f"✅ 已创建: {APP_DIR}")
    print("")
    print("📌 使用方法:")
    print("   1. 拖动 OpenClaw Tools.app 到 Dock 或启动台")
    print("   2. 点击图标启动控制台")
    print("")
    print("🔗 服务端口:")
    print("   - 8765: 控制台 + 任务管理")
    print("   - 8768: 模型管理")
    print("   - 8769: 任务看板")

def main():
    create_app()

if __name__ == "__main__":
    main()
