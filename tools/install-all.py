#!/usr/bin/env python3
"""
OpenClaw Tools 一键集成安装器
自动安装和配置所有工具
"""

import os
import sys
import json
import subprocess
from pathlib import Path

WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
TOOLS_DIR = WORKSPACE / "tools"

def run_cmd(cmd, cwd=None):
    """运行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"警告: 命令执行失败 - {result.stderr}")
    return result

def install_token_monitor():
    """安装 Token 监控器"""
    print("\n📊 1. 安装 Token 监控器...")
    
    # 确保 token-monitor.py 可执行
    (TOOLS_DIR / "token-monitor.py").chmod(0o755)
    (TOOLS_DIR / "token-monitor-setup.py").chmod(0o755)
    (TOOLS_DIR / "token-logger.js").chmod(0o755)
    
    # 初始化数据目录
    data_dir = WORKSPACE / "data"
    data_dir.mkdir(exist_ok=True)
    
    # 运行安装器
    run_cmd(f"python3 {TOOLS_DIR / 'token-monitor-setup.py'} 5")
    
    print("✅ Token 监控器已安装")

def update_api_keys():
    """更新 API Keys"""
    print("\n🔑 2. 检查 API Keys...")
    
    keys_file = Path.home() / ".api-keys" / "keys.json"
    if keys_file.exists():
        data = json.loads(keys_file.read_text())
        
        # 检查 SiliconFlow
        if "silicon" in data and len(data["silicon"]) > 0:
            old_key = data["silicon"][0]["key"]
            print(f"  SiliconFlow: {'✓' if 'qguxdgms' in old_key else '需要更新'}")
        else:
            print("  SiliconFlow: 未配置")
    else:
        print("  API Keys 文件不存在")

def clean_git_history():
    """清理 Git 历史"""
    print("\n🗑️ 3. Git 历史清理...")
    
    tools_git = TOOLS_DIR / ".git"
    if tools_git.exists():
        # 检查是否有远程仓库
        result = run_cmd("git remote -v", cwd=TOOLS_DIR)
        
        if not result.stdout.strip():
            print("  无远程仓库，可以安全清理")
            choice = input("  是否删除 .git 目录重新初始化? (y/n): ")
            if choice.lower() == 'y':
                run_cmd(f"rm -rf {tools_git}", cwd=TOOLS_DIR)
                run_cmd("git init && git add .", cwd=TOOLS_DIR)
                print("  ✅ 已重新初始化 Git")
        else:
            print("  检测到远程仓库，清理需谨慎操作")
            print("  建议: 手动执行 git filter-repo 或联系管理员")
    else:
        print("  无 Git 仓库")

def create_launcher_shortcut():
    """创建启动器快捷方式"""
    print("\n🚀 4. 创建启动器...")
    
    # 检查 launcher.py
    launcher = TOOLS_DIR / "launcher.py"
    if launcher.exists():
        launcher.chmod(0o755)
        
        # 创建 macOS 应用快捷方式
        app_script = '''#!/usr/bin/env osascript
tell application "Terminal"
    do script "cd /Users/fuzhuo/.openclaw/workspace/tools && python3 launcher.py"
    activate
end tell
'''
        app_path = Path.home() / "Desktop" / "OpenClaw Tools.app"
        if not app_path.exists():
            run_cmd(f'echo "{app_script}" | osascript')
            print(f"  ✅ 已创建桌面快捷方式: OpenClaw Tools")
    
    print("  运行: cd tools && python3 launcher.py")

def print_summary():
    """打印摘要"""
    print("\n" + "=" * 50)
    print("📦 OpenClaw Tools 安装完成")
    print("=" * 50)
    print("\n工具列表:")
    print("  1. launcher.py      - 桌面启动器")
    print("  2. token-monitor.py - Token 消耗监控")
    print("  3. token-logger.js  - Node.js 集成")
    print("  4. local-model-manager.py - 模型管理 Web UI")
    print("  5. task-board.py    - 任务看板")
    print("  6. api-key-manager.py - API Keys 管理")
    print("\n快速启动:")
    print("  cd /Users/fuzhuo/.openclaw/workspace/tools")
    print("  python3 launcher.py")
    print("\nToken 监控:")
    print("  python3 token-monitor.py daily      # 今日统计")
    print("  python3 token-monitor.py recent 24  # 最近 24 小时")
    print("=" * 50)

def main():
    print("🔧 OpenClaw Tools 集成安装器")
    print("-" * 40)
    
    # 执行安装步骤
    install_token_monitor()
    update_api_keys()
    clean_git_history()
    create_launcher_shortcut()
    print_summary()

if __name__ == "__main__":
    main()
