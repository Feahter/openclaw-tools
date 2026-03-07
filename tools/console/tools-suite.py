#!/usr/bin/env python3
"""
小工具合集管理器 - Tools Suite
晨间简报 | 系统仪表盘 | 每日惊喜
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS = {
    "1": ("morning-briefing", "🌅 晨间简报 - 生成今日天气+任务摘要"),
    "2": ("system-dashboard", "📊 系统仪表盘 - 实时监控 CPU/内存/磁盘"),
    "3": ("daily-surprise", "🎁 每日惊喜 - 随机鼓励和彩蛋"),
}

def main():
    print("""
╔═══════════════════════════════════════════════╗
║         🧰 OpenClaw 小工具合集               ║
╠═══════════════════════════════════════════════╣
║                                               ║
║  1. 🌅 晨间简报                               ║
║     生成今日天气、日历、任务摘要（HTML）      ║
║                                               ║
║  2. 📊 系统仪表盘                             ║
║     实时监控 CPU、内存、磁盘、网络进程        ║
║     访问: http://localhost:8765               ║
║                                               ║
║  3. 🎁 每日惊喜                               ║
║     随机获取鼓励语、功能提示、彩蛋           ║
║                                               ║
║  4. 🚀 全部启动                               ║
║     启动晨间简报 + 后台仪表盘 + 惊喜          ║
║                                               ║
║  h. 📖 帮助                                   ║
║  q. 🚪 退出                                   ║
║                                               ║
╚═══════════════════════════════════════════════╝
""")
    
    choice = input("请选择 (1-4, h, q): ").strip()
    
    tools_dir = Path("/Users/fuzhuo/.openclaw/workspace/tools")
    
    if choice == "1":
        print("\n🌅 生成晨间简报...")
        subprocess.run([f"{tools_dir}/morning-briefing.py"], check=True)
        
    elif choice == "2":
        print("\n📊 启动系统仪表盘...")
        print("   访问 http://localhost:8765 查看\n")
        subprocess.run([f"{tools_dir}/system-dashboard.py"])
        
    elif choice == "3":
        print("\n🎁 每日惊喜...")
        subprocess.run([f"{tools_dir}/daily-surprise.py", "--notify"])
        
    elif choice == "4":
        print("\n🚀 启动全部小工具...")
        print("   1. 生成晨间简报...")
        subprocess.run([f"{tools_dir}/morning-briefing.py"], capture_output=True)
        print("   2. 启动系统仪表盘 (后台)...")
        subprocess.Popen([f"{tools_dir}/system-dashboard.py"])
        print("   3. 每日惊喜...")
        subprocess.run([f"{tools_dir}/daily-surprise.py", "--notify"])
        print("\n✅ 全部启动完成！")
        print("   📊 仪表盘: http://localhost:8765")
        
    elif choice.lower() == "h":
        print("""
使用说明：

🌅 晨间简报:
   python tools/morning-briefing.py
   输出: public/morning-briefing-YYYY-MM-DD.html

📊 系统仪表盘:
   python tools/system-dashboard.py
   访问: http://localhost:8765 (自动刷新)
   静态版: python tools/system-dashboard.py --static

🎁 每日惊喜:
   python tools/daily-surprise.py --notify
   循环模式: python tools/daily-surprise.py --loop

📅 添加到 crontab (每天早上7点生成简报):
   0 7 * * * cd ~/.openclaw/workspace && python tools/morning-briefing.py
        """)
        
    elif choice.lower() == "q":
        print("👋 再见！")
        sys.exit(0)
        
    else:
        print("无效选择，请重试。")

if __name__ == "__main__":
    main()
