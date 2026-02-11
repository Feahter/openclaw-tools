#!/usr/bin/env python3
"""
每日惊喜 - Daily Surprise
随机生成小惊喜：鼓励语、彩蛋、功能提示
"""

import json
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")

# 惊喜配置
SURPRISES = {
    "encouragement": [
        ("🌟", "你今天已经迈出了第一步，这很棒！"),
        ("💪", "每一个小进步都在积累成大改变。"),
        ("🎯", "专注当下，你正在正确的道路上。"),
        ("✨", "你已经比昨天的自己更好了。"),
        ("🚀", "你的潜力无限，继续前行！"),
        ("💡", "问题不大，你一定能解决它。"),
        ("🌈", "风雨过后总会见彩虹。"),
        ("⚡", "你的努力世界都看得到。"),
    ],
    "tips": [
        ("💡", "试试说『用六顶思考帽分析...』来全面思考问题"),
        ("📊", "可以说『分析这个CSV文件』来快速处理数据"),
        ("🎨", "可以说『生成一张鼓励卡片』来获取视觉激励"),
        ("🔍", "可以说『搜索XXX』来查找信息"),
        ("📝", "可以说『总结这个文档』来提取关键信息"),
        ("🔄", "可以说『帮我自动化XXX』来简化重复工作"),
    ],
    "easter_eggs": [
        ("🎮", "彩蛋: 其实我会玩游戏，想试试吗？"),
        ("🎵", "彩蛋: 我可以帮你生成语音播报！"),
        ("🎭", "彩蛋: 我还能帮你画图做设计！"),
        ("🎪", "彩蛋: 试试说『给我讲个笑话』"),
        ("🎯", "彩蛋: 我可以帮你追踪习惯和目标！"),
    ],
    "fun_facts": [
        ("🧠", "人类大脑每天产生约70000个想法。"),
        ("🌱", "一棵树一天可以产生约4.5公斤的氧气。"),
        ("💻", 'Bug这个词源于1947年一只飞进计算机的飞蛾。'),
        ("🌊", "地球上的水已经存在了超过40亿年。"),
        ("⭐", "你身体里的碳原子可以组成9000支铅笔。"),
    ]
}

def get_productivity_stats():
    """获取今日生产力统计"""
    stats = {
        "tasks_done": 0,
        "tasks_total": 0,
        "last_activity": "未知"
    }
    
    task_file = WORKSPACE / "task-board.json"
    if task_file.exists():
        try:
            with open(task_file) as f:
                tasks = json.load(f)
            stats["tasks_total"] = len(tasks)
            stats["tasks_done"] = sum(1 for t in tasks if t.get("status") == "done")
        except:
            pass
    
    return stats

def get_random_surprise():
    """获取随机惊喜"""
    # 根据时间调整权重
    hour = datetime.now().hour
    
    if hour < 6:
        # 深夜 - 更多鼓励
        category = "encouragement"
    elif hour < 9:
        # 早晨 - 鼓励 + 提示
        category = random.choice(["encouragement", "tips"])
    elif hour < 12:
        # 上午 - 各种惊喜
        category = random.choice(["encouragement", "tips", "fun_facts"])
    elif hour < 14:
        # 中午 - 轻松一下
        category = random.choice(["easter_eggs", "fun_facts", "tips"])
    elif hour < 18:
        # 下午 - 鼓励为主
        category = random.choice(["encouragement", "tips"])
    else:
        # 晚上 - 总结鼓励
        category = "encouragement"
    
    return random.choice(SURPRISES[category])

def get_progress_message(stats):
    """生成进度消息"""
    if stats["tasks_total"] == 0:
        return "还没有任务，开始新的挑战吧！"
    
    percent = stats["tasks_done"] / stats["tasks_total"] * 100
    
    if percent == 100:
        return "🎉 太棒了！今天所有任务都完成了！"
    elif percent >= 75:
        return "💪 快完成了！就差一点点！"
    elif percent >= 50:
        return "📈 已经完成一半了，继续加油！"
    elif percent >= 25:
        return "🌱 有进展了！稳步前进中..."
    else:
        return "🚀 还有时间，慢慢来！"

def show_surprise(notify=False):
    """展示惊喜"""
    stats = get_productivity_stats()
    emoji, message = get_random_surprise()
    progress = get_progress_message(stats)
    
    surprise = f"""
╔══════════════════════════════════════════════╗
║           🎁 每日惊喜 🎁                      ║
╠══════════════════════════════════════════════╣
║  {emoji}  {message}
╠══════════════════════════════════════════════╣
║  📊 进度: {stats['tasks_done']}/{stats['tasks_total']} 任务完成
║  💬 {progress}
╚══════════════════════════════════════════════╝
"""
    
    print(surprise)
    
    # 系统通知（macOS）
    if notify:
        try:
            subprocess.run([
                'osascript', '-e',
                f'display notification "{message} {progress}" with title "🎁 每日惊喜"'
            ])
        except:
            pass
    
    return {"emoji": emoji, "message": message, "progress": progress}

def main():
    import argparse
    parser = argparse.ArgumentParser(description='每日惊喜')
    parser.add_argument('--notify', action='store_true', help='发送系统通知')
    parser.add_argument('--loop', action='store_true', help='循环模式（每小时提醒一次）')
    args = parser.parse_args()
    
    if args.loop:
        import time
        print("🔄 惊喜循环模式已启动（每小时一次，按 Ctrl+C 停止）\n")
        while True:
            show_surprise(args.notify)
            print(f"\n⏰ 下次惊喜: 1小时后 ({datetime.now().hour % 24 + 1}:00)")
            time.sleep(3600)
    else:
        show_surprise(args.notify)
        return 0

if __name__ == "__main__":
    sys.exit(main())
