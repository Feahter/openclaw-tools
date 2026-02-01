#!/usr/bin/env python3
"""
Token 统计面板
实时显示各 API 消耗、余额预警
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import http.server
import socketserver
import webbrowser

# 配置
CONFIG_DIR = Path.home() / ".api-keys"
USAGE_FILE = CONFIG_DIR / "usage.json"
PORT = 8770

# 读取使用数据
def load_usage():
    if USAGE_FILE.exists():
        try:
            with open(USAGE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"providers": {}, "daily": {}}

def save_usage(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(USAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_daily_cost():
    """计算今日成本"""
    usage = load_usage()
    today = datetime.now().strftime('%Y-%m-%d')
    daily = usage.get("daily", {}).get(today, {})
    return daily.get("tokens", 0), daily.get("cost", 0)

def get_provider_stats():
    """获取各 Provider 统计"""
    usage = load_usage()
    providers = {}
    for p, stats in usage.get("providers", {}).items():
        providers[p] = {
            "total_tokens": stats.get("total_tokens", 0),
            "total_cost": stats.get("total_cost", 0),
            "requests": stats.get("requests", 0)
        }
    return providers

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Token 统计</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #eee; 
               min-height: 100vh; padding: 20px; }
        h1 { color: #00d9ff; margin-bottom: 20px; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .stat-card { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; text-align: center; }
        .stat-value { font-size: 2em; font-weight: bold; color: #00d9ff; }
        .stat-label { color: #888; margin-top: 5px; }
        
        .provider-list { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; }
        .provider-item { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .provider-item:last-child { border-bottom: none; }
        .provider-name { font-weight: bold; color: #00d9ff; }
        .provider-stats { color: #888; font-size: 0.9em; }
        
        .refresh-btn { background: #e94560; color: #fff; border: none; padding: 12px 24px; 
                       border-radius: 8px; cursor: pointer; font-size: 1em; margin-bottom: 20px; }
        .refresh-btn:hover { background: #ff6b6b; }
    </style>
</head>
<body>
    <h1>📊 Token 统计面板</h1>
    <button class="refresh-btn" onclick="location.reload()">🔄 刷新</button>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" id="daily-tokens">0</div>
            <div class="stat-label">今日 Tokens</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="daily-cost">¥0</div>
            <div class="stat-label">今日消耗</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="providers">0</div>
            <div class="stat-label">活跃 Provider</div>
        </div>
    </div>
    
    <div class="provider-list">
        <h2 style="margin-bottom: 15px;">各 Provider 消耗</h2>
        <div id="provider-list"></div>
    </div>

    <script>
    async function loadStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            
            document.getElementById('daily-tokens').textContent = data.daily_tokens.toLocaleString();
            document.getElementById('daily-cost').textContent = '¥' + data.daily_cost.toFixed(2);
            document.getElementById('providers').textContent = data.provider_count;
            
            const list = document.getElementById('provider-list');
            let html = '';
            for (const [name, stats] of Object.entries(data.providers)) {
                html += `
                    <div class="provider-item">
                        <span class="provider-name">${name}</span>
                        <span class="provider-stats">
                            ${stats.requests} 次请求 | ${stats.tokens.toLocaleString()} tokens | ¥${stats.cost.toFixed(2)}
                        </span>
                    </div>
                `;
            }
            list.innerHTML = html || '<p>暂无数据</p>';
        } catch (e) {
            console.error('加载失败:', e);
        }
    }
    
    loadStats();
    setInterval(loadStats, 30000);  // 每30秒刷新
    </script>
</body>
</html>
"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path == '/api/stats':
            daily_tokens, daily_cost = get_daily_cost()
            providers = get_provider_stats()
            
            response = {
                "daily_tokens": daily_tokens,
                "daily_cost": daily_cost,
                "provider_count": len(providers),
                "providers": providers
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        pass  # 禁用日志

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ Token 统计已启动: http://localhost:{PORT}")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")

if __name__ == "__main__":
    run()
