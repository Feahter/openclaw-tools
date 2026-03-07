#!/usr/bin/env python3
"""
晨间简报生成器 - Morning Briefing
明天早上自动生成：天气 + 日历 + 任务摘要
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import urlopen
import urllib.error

WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data"
OUTPUT_DIR = WORKSPACE / "public"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_weather():
    """获取天气（无需 API key）"""
    try:
        url = "https://wttr.in/Shanghai?format=j1"
        with urlopen(url, timeout=5) as response:  # 5秒超时
            data = json.loads(response.read().decode())
            current = data.get("current_condition", [{}])[0]
            return {
                "temp": current.get("temp_C", "N/A"),
                "weather": current.get("weatherDesc", ["N/A"])[0],
                "humidity": current.get("humidity", "N/A"),
                "wind": current.get("windspeedKmph", "N/A")
            }
    except Exception as e:
        return {"temp": "N/A", "weather": "多云", "humidity": "N/A", "wind": "N/A"}

def get_tasks():
    """读取今日任务"""
    task_file = WORKSPACE / "task-board.json"
    if not task_file.exists():
        return {"total": 0, "pending": 0, "today": []}
    
    try:
        with open(task_file) as f:
            tasks = json.load(f)
        
        today = datetime.now()
        today_tasks = [t for t in tasks if t.get("status") != "done"]
        
        return {
            "total": len(tasks),
            "pending": len(today_tasks),
            "today": today_tasks[:5]
        }
    except:
        return {"total": 0, "pending": 0, "today": []}

def get_quotes():
    """每日语录"""
    quotes = [
        ("每一个不曾起舞的日子，都是对生命的辜负。", "尼采"),
        ("今天是最好的礼物。", "未知"),
        ("小的进步也是进步。", "未知"),
        ("你已经走了很远。", "未知"),
        ("相信过程。", "Unknown"),
    ]
    day_of_year = datetime.now().timetuple().tm_yday
    return quotes[day_of_year % len(quotes)]

def generate_html(weather, tasks, quote):
    """生成晨间简报 HTML"""
    
    task_items = ""
    for task in tasks["today"]:
        status = "✅" if task.get("status") == "done" else "⏳"
        task_items += f"""
        <li class="task-item">
            <span class="status">{status}</span>
            <span class="title">{task.get('title', '未命名任务')}</span>
        </li>
        """
    
    if not tasks["today"]:
        task_items = "<li class='task-item'>🎉 今天没有待办任务！</li>"
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>晨间简报 - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .date {{ font-size: 1.2em; opacity: 0.9; }}
        .greeting {{ font-size: 2em; font-weight: bold; margin-top: 10px; }}
        .weather {{
            padding: 25px;
            border-bottom: 1px solid #eee;
        }}
        .weather h2 {{ font-size: 1em; color: #666; margin-bottom: 15px; }}
        .weather-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            text-align: center;
        }}
        .weather-item {{ padding: 15px; background: #f8f9fa; border-radius: 12px; }}
        .weather-item .value {{ font-size: 1.5em; font-weight: bold; color: #333; }}
        .weather-item .label {{ font-size: 0.8em; color: #888; margin-top: 5px; }}
        .tasks {{
            padding: 25px;
            border-bottom: 1px solid #eee;
        }}
        .tasks h2 {{ font-size: 1em; color: #666; margin-bottom: 15px; display: flex; justify-content: space-between; }}
        .task-count {{ background: #f5576c; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.8em; }}
        .task-list {{ list-style: none; }}
        .task-item {{
            padding: 12px;
            background: #f8f9fa;
            margin-bottom: 8px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .status {{ font-size: 1.2em; }}
        .quote {{
            padding: 25px;
            background: #f8f9fa;
        }}
        .quote p {{ font-size: 1.1em; color: #333; font-style: italic; text-align: center; }}
        .quote .author {{ text-align: center; color: #888; margin-top: 10px; font-size: 0.9em; }}
        .footer {{
            padding: 15px;
            text-align: center;
            color: #aaa;
            font-size: 0.8em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="date">{datetime.now().strftime('%Y年%m月%d日 %A')}</div>
            <div class="greeting">早上好 👋</div>
        </div>
        
        <div class="weather">
            <h2>🌤️ 今日天气</h2>
            <div class="weather-grid">
                <div class="weather-item">
                    <div class="value">{weather.get('temp', '--')}°C</div>
                    <div class="label">温度</div>
                </div>
                <div class="weather-item">
                    <div class="value">{weather.get('humidity', '--')}%</div>
                    <div class="label">湿度</div>
                </div>
                <div class="weather-item">
                    <div class="value">{weather.get('wind', '--')}</div>
                    <div class="label">风速 km/h</div>
                </div>
            </div>
            <p style="text-align: center; margin-top: 15px; color: #666;">{weather.get('weather', '获取中...')}</p>
        </div>
        
        <div class="tasks">
            <h2>📋 今日任务 <span class="task-count">{tasks['pending']}</span></h2>
            <ul class="task-list">
                {task_items}
            </ul>
        </div>
        
        <div class="quote">
            <p>"{quote[0]}"</p>
            <div class="author">— {quote[1]}</div>
        </div>
        
        <div class="footer">
            生成时间: {datetime.now().strftime('%H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
    
    return html

def main():
    print("🌅 晨间简报生成器")
    print("=" * 40)
    
    # 获取数据
    print("📡 获取天气...")
    weather = get_weather()
    
    print("📋 读取任务...")
    tasks = get_tasks()
    
    print("💬 每日语录...")
    quote = get_quotes()
    
    # 生成 HTML
    print("🎨 生成简报...")
    html = generate_html(weather, tasks, quote)
    
    # 保存
    output_file = OUTPUT_DIR / f"morning-briefing-{datetime.now().strftime('%Y-%m-%d')}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ 已生成: {output_file}")
    print(f"\n📌 今日摘要:")
    print(f"   天气: {weather.get('temp', 'N/A')}°C, {weather.get('weather', 'N/A')}")
    print(f"   待办: {tasks['pending']} 项")
    print(f"   语录: {quote[0][:30]}...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
