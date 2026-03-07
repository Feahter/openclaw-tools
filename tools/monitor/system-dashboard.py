#!/usr/bin/env python3
"""
系统仪表盘 - System Dashboard
实时监控 CPU、内存、磁盘、网络
"""

import json
import psutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser

WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
OUTPUT_FILE = WORKSPACE / "public" / "dashboard.html"

def get_system_info():
    """获取系统信息"""
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_freq = psutil.cpu_freq()
    
    # 内存
    memory = psutil.virtual_memory()
    
    # 磁盘
    disk = psutil.disk_usage('/')
    
    # 网络
    net = psutil.net_io_counters()
    
    # 进程
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            if info['cpu_percent'] and float(info['cpu_percent']) > 5:
                processes.append(info)
        except:
            pass
    processes.sort(key=lambda x: float(x.get('cpu_percent', 0) or 0), reverse=True)
    
    return {
        "cpu": {
            "percent": cpu_percent,
            "freq_mhz": cpu_freq.current if cpu_freq else 0
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 1),
            "used_gb": round(memory.used / (1024**3), 1),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 1),
            "used_gb": round(disk.used / (1024**3), 1),
            "percent": disk.percent,
            "free_gb": round(disk.free / (1024**3), 1)
        },
        "network": {
            "bytes_sent_mb": round(net.bytes_sent / (1024**2), 1),
            "bytes_recv_mb": round(net.bytes_recv / (1024**2), 1)
        },
        "top_processes": processes[:8],
        "timestamp": datetime.now().strftime('%H:%M:%S')
    }

def generate_html(data):
    """生成仪表盘 HTML"""
    
    cpu_color = "#4ade80" if data['cpu']['percent'] < 50 else "#fbbf24" if data['cpu']['percent'] < 80 else "#ef4444"
    mem_color = "#4ade80" if data['memory']['percent'] < 50 else "#fbbf24" if data['memory']['percent'] < 80 else "#ef4444"
    disk_color = "#4ade80" if data['disk']['percent'] < 70 else "#fbbf24" if data['disk']['percent'] < 90 else "#ef4444"
    
    process_rows = ""
    for proc in data['top_processes']:
        cpu = proc.get('cpu_percent') or 0
        mem = proc.get('memory_percent') or 0
        name = proc.get('name', 'unknown')[:20]
        process_rows += f"""
        <tr>
            <td>{name}</td>
            <td>{cpu:.1f}%</td>
            <td>{mem:.1f}%</td>
        </tr>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>系统仪表盘</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: white;
            min-height: 100vh;
            padding: 20px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }}
        .header h1 {{ font-size: 1.8em; }}
        .timestamp {{ color: #888; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: #1e293b;
            border-radius: 16px;
            padding: 24px;
        }}
        .card h3 {{
            color: #94a3b8;
            font-size: 0.9em;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .big-number {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .progress-bar {{
            height: 8px;
            background: #334155;
            border-radius: 4px;
            overflow: hidden;
            margin: 15px 0;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        .stats {{
            display: flex;
            justify-content: space-between;
            color: #94a3b8;
            font-size: 0.9em;
        }}
        .processes table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .processes th, .processes td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }}
        .processes th {{ color: #94a3b8; font-weight: normal; }}
        .network-stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .net-item {{
            background: #334155;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}
        .net-item .value {{ font-size: 1.5em; font-weight: bold; }}
        .net-item .label {{ color: #94a3b8; font-size: 0.8em; margin-top: 5px; }}
        
        .emoji {{ font-size: 1.5em; margin-right: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 系统仪表盘</h1>
        <span class="timestamp">{data['timestamp']} (每5秒刷新)</span>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3><span class="emoji">🖥️</span>CPU</h3>
            <div class="big-number" style="color: {cpu_color}">{data['cpu']['percent']}%</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {data['cpu']['percent']}%; background: {cpu_color}"></div>
            </div>
            <div class="stats">
                <span>频率: {data['cpu']['freq_mhz']:.0f} MHz</span>
                <span>核心: {psutil.cpu_count()} 个</span>
            </div>
        </div>
        
        <div class="card">
            <h3><span class="emoji">🧠</span>内存</h3>
            <div class="big-number" style="color: {mem_color}">{data['memory']['percent']}%</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {data['memory']['percent']}%; background: {mem_color}"></div>
            </div>
            <div class="stats">
                <span>{data['memory']['used_gb']} GB / {data['memory']['total_gb']} GB</span>
            </div>
        </div>
        
        <div class="card">
            <h3><span class="emoji">💾</span>磁盘</h3>
            <div class="big-number" style="color: {disk_color}">{data['disk']['percent']}%</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {data['disk']['percent']}%; background: {disk_color}"></div>
            </div>
            <div class="stats">
                <span>{data['disk']['used_gb']} GB / {data['disk']['total_gb']} GB</span>
                <span>可用 {data['disk']['free_gb']} GB</span>
            </div>
        </div>
        
        <div class="card">
            <h3><span class="emoji">🌐</span>网络</h3>
            <div class="network-stats">
                <div class="net-item">
                    <div class="value">📤 {data['network']['bytes_sent_mb']} MB</div>
                    <div class="label">已发送</div>
                </div>
                <div class="net-item">
                    <div class="value">📥 {data['network']['bytes_recv_mb']} MB</div>
                    <div class="label">已接收</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="card processes">
        <h3><span class="emoji">⚡</span>CPU 占用 Top 8</h3>
        <table>
            <thead>
                <tr>
                    <th>进程</th>
                    <th>CPU</th>
                    <th>内存</th>
                </tr>
            </thead>
            <tbody>
                {process_rows}
            </tbody>
        </table>
    </div>
</body>
</html>"""
    
    return html

def auto_refresh():
    """自动刷新模式"""
    print("🌐 启动系统仪表盘...")
    print("   访问: http://localhost:8765")
    print("   按 Ctrl+C 停止\n")
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入初始页面
    with open(OUTPUT_FILE, 'w') as f:
        f.write(generate_html(get_system_info()))
    
    # 启动自动刷新线程
    def refresh_loop():
        while True:
            try:
                data = get_system_info()
                with open(OUTPUT_FILE, 'w') as f:
                    f.write(generate_html(data))
                time.sleep(5)
            except:
                break
    
    thread = threading.Thread(target=refresh_loop, daemon=True)
    thread.start()
    
    # 尝试打开浏览器
    try:
        webbrowser.open('http://localhost:8765')
    except:
        pass
    
    # 简单 HTTP 服务器
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/dashboard.html'
            return super().do_GET()
    
    server = HTTPServer(('localhost', 8765), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 停止仪表盘")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='系统仪表盘')
    parser.add_argument('--static', action='store_true', help='生成静态HTML并退出')
    args = parser.parse_args()
    
    if args.static:
        data = get_system_info()
        html = generate_html(data)
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, 'w') as f:
            f.write(html)
        print(f"✅ 已生成: {OUTPUT_FILE}")
        return 0
    else:
        auto_refresh()
        return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
