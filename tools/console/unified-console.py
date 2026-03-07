#!/usr/bin/env python3
"""
OpenClaw 统一管理面板
整合所有工具 + 快速任务管理 + Web搜索
"""

import json
import subprocess
import os
import sys
import time
from pathlib import Path
from datetime import datetime
import http.server
import socketserver
import webbrowser
import threading

# 导入Web Search工具
try:
    import importlib.util
    tool_path = Path(__file__).parent / "web-search-tool.py"
    spec = importlib.util.spec_from_file_location("web_search_tool", str(tool_path.resolve()))
    web_search_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(web_search_module)
    WebSearchTool = web_search_module.WebSearchTool
    RateLimitError = web_search_module.RateLimitError
    WEB_SEARCH_AVAILABLE = True
except Exception as e:
    WEB_SEARCH_AVAILABLE = False
    print(f"⚠ Web Search 不可用: {e}")

# 配置
PORT = 8765
CONFIG_DIR = Path.home() / ".openclaw"
TASKS_FILE = CONFIG_DIR / "console-tasks.json"

TOOLS = {
    8765: {"name": "统一控制台", "icon": "🔧", "url": "http://localhost:8765"},
    8768: {"name": "模型管理", "icon": "🤖", "url": "http://localhost:8768"},
    8769: {"name": "任务看板", "icon": "📋", "url": "http://localhost:8769"},
    8770: {"name": "Token统计", "icon": "📊", "url": "http://localhost:8770"},
    8771: {"name": "自动化", "icon": "⚡", "url": "http://localhost:8771"},
    8772: {"name": "能力集合", "icon": "🧠", "url": "http://localhost:8772"},
    8780: {"name": "并发任务", "icon": "🚀", "url": "http://localhost:8780"},
}

DEFAULT_TASKS = []

def check_port(port):
    try:
        sock = __import__('socket').socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def get_system_stats():
    stats = {"python_procs": 0, "memory_mb": 0, "uptime": "unknown"}
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        stats["python_procs"] = sum(1 for line in result.stdout.split('\n') if 'python' in line.lower())
        
        total_mem = 0
        for line in result.stdout.split('\n'):
            if 'python' in line.lower():
                parts = line.split()
                if len(parts) > 5:
                    try:
                        total_mem += float(parts[5])
                    except:
                        pass
        stats["memory_mb"] = round(total_mem / 1024, 1)
        
        result = subprocess.run(["ps", "-o", "etime=", "-p", str(os.getpid())], capture_output=True, text=True)
        stats["uptime"] = result.stdout.strip() or "unknown"
    except:
        pass
    return stats

def get_tasks():
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE) as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_TASKS

def save_tasks(tasks):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔧 OpenClaw 控制台</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', Roboto, sans-serif; 
               background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #eee; 
               min-height: 100vh; padding: 20px; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        h1 { color: #00d9ff; font-size: 1.6em; }
        .status-badge { background: #00c853; color: #fff; padding: 4px 10px; border-radius: 12px; font-size: 0.8em; }
        
        .stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 12px; margin-bottom: 20px; }
        .stat-card { background: rgba(255,255,255,0.08); border-radius: 10px; padding: 15px; text-align: center; }
        .stat-value { font-size: 1.5em; font-weight: bold; color: #00d9ff; }
        .stat-label { color: #888; font-size: 0.75em; margin-top: 5px; }
        
        .main-grid { display: grid; grid-template-columns: 1fr 320px; gap: 20px; }
        @media (max-width: 850px) { .main-grid { grid-template-columns: 1fr; } }
        
        .section { background: rgba(255,255,255,0.05); border-radius: 14px; padding: 18px; margin-bottom: 18px; }
        .section h2 { color: #e94560; margin-bottom: 12px; font-size: 1em; }
        
        .tools-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; }
        .tool-card { 
            background: rgba(255,255,255,0.08); border-radius: 12px; padding: 18px; 
            text-decoration: none; color: inherit; transition: all 0.2s; display: block; text-align: center;
        }
        .tool-card:hover { background: rgba(255,255,255,0.15); transform: translateY(-2px); }
        .tool-card.offline { opacity: 0.4; }
        .tool-icon { font-size: 2em; margin-bottom: 8px; }
        .tool-name { font-size: 0.9em; font-weight: 600; color: #00d9ff; }
        .tool-status { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.7em; margin-top: 8px; }
        .status-running { background: #00c853; color: #fff; }
        .status-stopped { background: #e94560; color: #fff; }
        
        .actions { display: flex; gap: 8px; margin-bottom: 18px; flex-wrap: wrap; }
        .btn { 
            background: linear-gradient(135deg, #e94560, #ff6b6b); color: #fff; border: none; 
            padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 0.85em;
            display: flex; align-items: center; gap: 6px; transition: all 0.2s;
        }
        .btn:hover { transform: translateY(-1px); box-shadow: 0 3px 10px rgba(233,69,96,0.3); }
        .btn.green { background: linear-gradient(135deg, #00c853, #00e676); }
        .btn.blue { background: linear-gradient(135deg, #00d9ff, #00a8cc); }
        .btn.small { padding: 6px 12px; font-size: 0.8em; }
        
        .task-stats { display: flex; gap: 12px; margin-bottom: 15px; }
        .task-stat { text-align: center; flex: 1; }
        .task-stat-num { font-size: 1.3em; font-weight: bold; }
        .task-stat-num.todo { color: #ff9800; }
        .task-stat-num.progress { color: #00d9ff; }
        .task-stat-num.done { color: #00c853; }
        
        .task-list { max-height: 350px; overflow-y: auto; }
        .task-item { 
            background: rgba(15, 52, 96, 0.5); border-radius: 8px; padding: 10px; 
            margin-bottom: 6px; cursor: pointer; transition: all 0.2s; border-left: 3px solid transparent;
        }
        .task-item:hover { background: rgba(15, 52, 96, 0.8); }
        .task-item.priority-high { border-left-color: #ff5252; }
        .task-item.priority-mid { border-left-color: #ff9800; }
        .task-item.priority-low { border-left-color: #00c853; }
        .task-title { font-size: 0.85em; color: #fff; margin-bottom: 4px; }
        .task-meta { display: flex; justify-content: space-between; font-size: 0.7em; color: #666; }
        .task-tag { background: rgba(0,217,255,0.2); color: #00d9ff; padding: 2px 6px; border-radius: 4px; }
        
        .quick-links { display: flex; gap: 8px; flex-wrap: wrap; }
        .quick-link { 
            background: rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 6px; 
            color: #00d9ff; text-decoration: none; font-size: 0.8em; transition: all 0.2s;
        }
        .quick-link:hover { background: rgba(0,217,255,0.2); }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔧 OpenClaw 控制台</h1>
        <span class="status-badge" id="system-status">正常</span>
    </div>
    
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-value" id="python-procs">0</div>
            <div class="stat-label">Python 进程</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="memory">0 MB</div>
            <div class="stat-label">内存</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="services">0/0</div>
            <div class="stat-label">服务</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="uptime">--</div>
            <div class="stat-label">运行时间</div>
        </div>
    </div>
    
    <div class="actions">
        <button class="btn small" onclick="loadTasks()">🔄 刷新</button>
        <button class="btn small" onclick="addTask()">+ 添加</button>
        <button class="btn blue small" onclick="openBoard()">📋 看板</button>
    </div>
    
    <div class="main-grid">
        <div>
            <div class="section">
                <h2>🔧 服务工具</h2>
                <div class="tools-grid" id="tools-grid"></div>
            </div>
            
            <div class="section">
                <h2>⚡ 快速链接</h2>
                <div class="quick-links">
                    <a href="http://localhost:8768" target="_blank" class="quick-link">🤖 模型管理</a>
                    <a href="http://localhost:8769" target="_blank" class="quick-link">📋 任务看板</a>
                    <a href="http://localhost:8770" target="_blank" class="quick-link">📊 Token统计</a>
                    <a href="http://localhost:8771" target="_blank" class="quick-link">⚡ 自动化</a>
                    <a href="http://localhost:8772" target="_blank" class="quick-link">🧠 能力集合</a>
                    <a href="http://localhost:8780" target="_blank" class="quick-link">🚀 并发任务</a>
                </div>
            </div>
            
            <!-- 搜索区域 -->
            <div class="section">
                <h2>🔍 Web搜索</h2>
                <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                    <input type="text" id="search-input" placeholder="输入搜索关键词..." 
                           style="flex: 1; padding: 10px 14px; border-radius: 8px; border: 1px solid #333; 
                                  background: rgba(255,255,255,0.08); color: #fff; font-size: 0.9em;"
                           onkeypress="if(event.key==='Enter') doSearch()">
                    <button class="btn small blue" onclick="doSearch()">🔍 搜索</button>
                </div>
                <div style="display: flex; gap: 8px; margin-bottom: 12px; font-size: 0.8em;">
                    <label style="color: #888; display: flex; align-items: center; gap: 4px;">
                        <input type="checkbox" id="search-recent"> 只搜索最近结果
                    </label>
                </div>
                <div id="search-results" style="max-height: 400px; overflow-y: auto;"></div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 快速任务</h2>
            <div class="task-stats">
                <div class="task-stat">
                    <div class="task-stat-num todo" id="task-todo">0</div>
                    <div class="stat-label">待办</div>
                </div>
                <div class="task-stat">
                    <div class="task-stat-num progress" id="task-progress">0</div>
                    <div class="stat-label">进行</div>
                </div>
                <div class="task-stat">
                    <div class="task-stat-num done" id="task-done">0</div>
                    <div class="stat-label">完成</div>
                </div>
            </div>
            <div class="task-list" id="task-list"></div>
        </div>
    </div>
    
    <script>
    async function loadStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            
            document.getElementById('python-procs').textContent = data.python_procs;
            document.getElementById('memory').textContent = data.memory_mb + ' MB';
            document.getElementById('uptime').textContent = data.uptime;
            document.getElementById('services').textContent = data.running_services + '/' + data.total_services;
            
            const grid = document.getElementById('tools-grid');
            let html = '';
            for (const [port, tool] of Object.entries(data.tools)) {
                const running = data.tools[port].running;
                const statusClass = running ? 'status-running' : 'status-stopped';
                const statusText = running ? '运行' : '停止';
                const offlineClass = running ? '' : 'offline';
                
                html += `<a href="${tool.url}" target="_blank" class="tool-card ${offlineClass}">
                    <div class="tool-icon">${tool.icon}</div>
                    <div class="tool-name">${tool.name}</div>
                    <span class="tool-status ${statusClass}">${statusText}</span>
                </a>`;
            }
            grid.innerHTML = html || '<div style="color:#666;font-size:0.85em;">无服务</div>';
            
            const allRunning = data.running_services === data.total_services;
            document.getElementById('system-status').textContent = allRunning ? '全部运行' : '部分停止';
            document.getElementById('system-status').style.background = allRunning ? '#00c853' : '#e94560';
        } catch (e) {
            console.error('加载失败:', e);
        }
    }
    
    async function loadTasks() {
        try {
            const res = await fetch('/api/tasks');
            const tasks = await res.json();
            
            const counts = { todo: 0, progress: 0, done: 0 };
            tasks.forEach(t => counts[t.status]++);
            
            document.getElementById('task-todo').textContent = counts.todo;
            document.getElementById('task-progress').textContent = counts.progress;
            document.getElementById('task-done').textContent = counts.done;
            
            const list = document.getElementById('task-list');
            list.innerHTML = tasks.length === 0 
                ? '<div style="color:#666;text-align:center;padding:20px;font-size:0.85em;">暂无任务</div>'
                : tasks.map(t => `
                    <div class="task-item priority-${t.priority}" onclick="toggleTask(${t.id})">
                        <div class="task-title">${escapeHtml(t.title)}</div>
                        <div class="task-meta">
                            ${t.tag ? `<span class="task-tag">${escapeHtml(t.tag)}</span>` : '<span></span>'}
                            <span>${t.status === 'todo' ? '📝' : t.status === 'progress' ? '🚀' : '✅'}</span>
                        </div>
                    </div>
                `).join('');
        } catch (e) {
            console.error('加载任务失败:', e);
        }
    }
    
    async function toggleTask(id) {
        try {
            await fetch('/api/tasks/toggle', { method: 'POST', body: JSON.stringify({id}) });
            loadTasks();
        } catch (e) {
            console.error('切换失败:', e);
        }
    }
    
    async function addTask() {
        const title = prompt('输入任务标题:');
        if (!title) return;
        try {
            await fetch('/api/tasks/add', { 
                method: 'POST', 
                body: JSON.stringify({id: Date.now(), title: title, status: 'todo', priority: 'mid', created: new Date().toISOString()}) 
            });
            loadTasks();
        } catch (e) {
            alert('添加失败');
        }
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Web搜索功能
    async function doSearch() {
        const input = document.getElementById('search-input');
        const recentCheckbox = document.getElementById('search-recent');
        const query = input.value.trim();
        
        if (!query) {
            alert('请输入搜索关键词');
            return;
        }
        
        const container = document.getElementById('search-results');
        container.innerHTML = '<div style="color:#00d9ff;text-align:center;padding:20px;">🔍 搜索中...</div>';
        
        try {
            const recent = recentCheckbox.checked;
            const params = new URLSearchParams({ q: query, recent: recent });
            const res = await fetch('/api/search?' + params);
            const data = await res.json();
            
            if (data.error) {
                container.innerHTML = '<div style="color:#e94560;padding:15px;">⚠ ' + data.error + '</div>';
                return;
            }
            
            if (!data.results || data.results.length === 0) {
                container.innerHTML = '<div style="color:#888;padding:15px;">未找到结果</div>';
                return;
            }
            
            container.innerHTML = '<div style="margin-bottom:10px;color:#00c853;font-size:0.85em;">✓ 找到 ' + data.count + ' 条结果</div>' +
                data.results.map(r => `
                    <div style="background:rgba(15,52,96,0.4);border-radius:8px;padding:12px;margin-bottom:10px;border-left:3px solid #00d9ff;">
                        <div style="font-size:0.95em;color:#fff;margin-bottom:6px;">${escapeHtml(r.title)}</div>
                        <a href="${r.url}" target="_blank" style="font-size:0.8em;color:#00d9ff;word-break:break-all;">${escapeHtml(r.url)}</a>
                        ${r.description ? '<div style="font-size:0.8em;color:#888;margin-top:6px;line-height:1.5;">' + escapeHtml(r.description.substring(0,150)) + '</div>' : ''}
                        ${r.age ? '<div style="font-size:0.75em;color:#666;margin-top:4px;">⏰ ' + r.age + '</div>' : ''}
                    </div>
                `).join('');
        } catch (e) {
            console.error('搜索失败:', e);
            container.innerHTML = '<div style="color:#e94560;padding:15px;">✗ 搜索失败: ' + e.message + '</div>';
        }
    }
    
    function openBoard() {
        window.open('http://localhost:8769', '_blank');
    }
    
    loadStats();
    loadTasks();
    setInterval(loadStats, 15000);
    setInterval(loadTasks, 10000);
    </script>
</body>
</html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path == '/api/stats':
            stats = get_system_stats()
            tools_status = {}
            running = 0
            for port, tool in TOOLS.items():
                is_running = check_port(port)
                if is_running:
                    running += 1
                tools_status[str(port)] = {"name": tool["name"], "icon": tool["icon"], "url": tool["url"], "running": is_running}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({**stats, "tools": tools_status, "running_services": running, "total_services": len(TOOLS)}).encode())
        elif self.path == '/api/tasks':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_tasks(), ensure_ascii=False).encode())
        elif self.path.startswith('/api/search'):
            # Web搜索API
            if not WEB_SEARCH_AVAILABLE:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Web Search 不可用"}).encode())
                return
            
            try:
                from urllib.parse import urlparse, parse_qs
                # 分离路径和查询参数
                path_only = self.path.split('?')[0]
                query_string = self.path.split('?')[1] if '?' in self.path else ''
                params = parse_qs(query_string)
                query = params.get('q', [''])[0]
                recent = params.get('recent', ['false'])[0].lower() == 'true'
                
                tool = web_search_module.WebSearchTool()
                results = tool.search_simple(query, recent=recent)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "query": query,
                    "recent": recent,
                    "count": len(results),
                    "results": results
                }, ensure_ascii=False).encode())
            except web_search_module.RateLimitError as e:
                self.send_response(429)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        elif self.path == '/api/search/status':
            # 搜索状态API
            if not WEB_SEARCH_AVAILABLE:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Web Search 不可用"}).encode())
                return
            
            tool = web_search_module.WebSearchTool()
            status = tool.status()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/tasks/toggle':
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            tasks = get_tasks()
            for t in tasks:
                if t.get('id') == data.get('id'):
                    t['status'] = 'done' if t['status'] == 'progress' else 'progress' if t['status'] == 'todo' else 'todo'
                    break
            save_tasks(tasks)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
        elif self.path == '/api/tasks/add':
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            tasks = get_tasks()
            tasks.append(data)
            save_tasks(tasks)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        pass

def run():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ 统一控制台已启动: http://localhost:{PORT}")
        print("  控制台 + 任务管理")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")

if __name__ == "__main__":
    run()
