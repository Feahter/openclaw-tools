#!/usr/bin/env python3
"""
OpenClaw 快速任务面板
简洁的任务管理 Web UI - 运行在端口 8765
"""

import json
import os
from pathlib import Path
from datetime import datetime
import http.server
import socketserver
import webbrowser

# 配置
CONFIG_DIR = Path.home() / ".openclaw"
TASKS_FILE = CONFIG_DIR / "quick-tasks.json"
PORT = 8765

# 默认任务
DEFAULT_TASKS = [
    {"id": 1, "title": "完善任务工具集合", "status": "progress", "priority": "high", "tag": "开发", "created": datetime.now().isoformat()},
    {"id": 2, "title": "优化本地模型管理", "status": "todo", "priority": "mid", "tag": "工具", "created": datetime.now().isoformat()},
]

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📋 任务面板</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #fff; min-height: 100vh; padding: 20px;
        }
        h1 { color: #00d9ff; font-size: 1.5em; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
        .subtitle { color: #666; font-size: 0.85em; margin-bottom: 20px; }
        
        /* 快捷操作 */
        .quick-actions { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .btn { 
            background: linear-gradient(135deg, #e94560, #ff6b6b); color: #fff; border: none;
            padding: 10px 18px; border-radius: 10px; cursor: pointer; font-size: 0.9em;
            transition: all 0.2s; display: flex; align-items: center; gap: 6px;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(233,69,96,0.4); }
        .btn.green { background: linear-gradient(135deg, #00c853, #00e676); }
        .btn.green:hover { box-shadow: 0 5px 20px rgba(0,200,83,0.4); }
        .btn.blue { background: linear-gradient(135deg, #00d9ff, #00a8cc); }
        .btn.blue:hover { box-shadow: 0 5px 20px rgba(0,217,255,0.4); }
        
        /* 统计卡片 */
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 15px; margin-bottom: 25px; }
        .stat-card { 
            background: rgba(22, 33, 62, 0.8); border-radius: 12px; padding: 15px; 
            text-align: center; border: 1px solid rgba(255,255,255,0.1);
        }
        .stat-num { font-size: 2em; font-weight: bold; }
        .stat-label { font-size: 0.8em; color: #888; margin-top: 5px; }
        .stat-todo .stat-num { color: #ff9800; }
        .stat-progress .stat-num { color: #00d9ff; }
        .stat-done .stat-num { color: #00c853; }
        
        /* 看板 */
        .board { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .column { 
            background: rgba(22, 33, 62, 0.8); backdrop-filter: blur(10px);
            border-radius: 16px; padding: 15px; border: 1px solid rgba(255,255,255,0.1);
        }
        .column-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .column-title { font-size: 1em; font-weight: 600; display: flex; align-items: center; gap: 8px; }
        .column-count { background: rgba(255,255,255,0.1); padding: 2px 10px; border-radius: 10px; font-size: 0.8em; }
        
        .col-todo .column-title { color: #ff9800; }
        .col-progress .column-title { color: #00d9ff; }
        .col-done .column-title { color: #00c853; }
        
        /* 任务卡片 */
        .task { 
            background: rgba(15, 52, 96, 0.6); border-radius: 10px; padding: 12px;
            margin: 10px 0; transition: all 0.2s; border: 1px solid transparent;
            cursor: pointer; position: relative;
        }
        .task:hover { background: rgba(15, 52, 96, 0.9); border-color: rgba(0,217,255,0.3); }
        .task-title { font-weight: 500; color: #fff; font-size: 0.95em; }
        .task-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; font-size: 0.8em; }
        .task-tag { background: rgba(0,217,255,0.2); color: #00d9ff; padding: 2px 8px; border-radius: 4px; }
        .task-time { color: #666; }
        
        /* 优先级指示 */
        .priority-high { border-left: 3px solid #ff5252; }
        .priority-mid { border-left: 3px solid #ff9800; }
        .priority-low { border-left: 3px solid #00c853; }
        
        /* 添加表单 */
        .add-form { 
            background: rgba(15, 52, 96, 0.4); border-radius: 10px; padding: 15px; 
            margin: 10px 0; display: none;
        }
        .add-form.show { display: block; }
        .add-form input, .add-form select { 
            width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.2); color: #fff;
        }
        .add-form input::placeholder { color: #666; }
        .form-actions { display: flex; gap: 10px; }
        .form-actions .btn { flex: 1; justify-content: center; }
        
        /* 空状态 */
        .empty { text-align: center; color: #555; padding: 30px 0; font-size: 0.9em; }
        
        /* 快捷链接 */
        .links { margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); }
        .links h3 { color: #888; font-size: 0.85em; margin-bottom: 10px; }
        .link-item { 
            display: inline-block; margin: 5px 10px 5px 0; color: #00d9ff; 
            text-decoration: none; font-size: 0.85em; padding: 5px 12px;
            background: rgba(0,217,255,0.1); border-radius: 6px;
        }
        .link-item:hover { background: rgba(0,217,255,0.2); }
        
        @media (max-width: 768px) {
            .board { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <h1>📋 任务面板</h1>
    <div class="subtitle">快速任务管理 · 端口 8765</div>
    
    <div class="quick-actions">
        <button class="btn green" onclick="showAddForm()">+ 添加任务</button>
        <button class="btn" onclick="loadSample()">📥 示例</button>
        <button class="btn blue" onclick="exportTasks()">📤 导出</button>
        <button class="btn" onclick="openBoard()">📋 详细看板</button>
    </div>
    
    <div class="stats" id="stats">
        <div class="stat-card stat-todo">
            <div class="stat-num" id="count-todo">0</div>
            <div class="stat-label">待办</div>
        </div>
        <div class="stat-card stat-progress">
            <div class="stat-num" id="count-progress">0</div>
            <div class="stat-label">进行中</div>
        </div>
        <div class="stat-card stat-done">
            <div class="stat-num" id="count-done">0</div>
            <div class="stat-label">已完成</div>
        </div>
    </div>
    
    <!-- 添加表单 -->
    <div class="add-form" id="addForm">
        <input type="text" id="taskTitle" placeholder="任务标题..." onkeypress="if(event.key==='Enter')saveTask()">
        <select id="taskPriority">
            <option value="high">🔴 高优先级</option>
            <option value="mid" selected>🟡 中优先级</option>
            <option value="low">🟢 低优先级</option>
        </select>
        <input type="text" id="taskTag" placeholder="标签 (可选)">
        <div class="form-actions">
            <button class="btn" onclick="hideAddForm()">取消</button>
            <button class="btn green" onclick="saveTask()">保存</button>
        </div>
    </div>
    
    <div class="board">
        <!-- 待办 -->
        <div class="column col-todo">
            <div class="column-header">
                <div class="column-title">📝 待办 <span class="column-count" id="count-col-todo">0</span></div>
            </div>
            <div id="col-todo"></div>
        </div>
        
        <!-- 进行中 -->
        <div class="column col-progress">
            <div class="column-header">
                <div class="column-title">🚀 进行中 <span class="column-count" id="count-col-progress">0</span></div>
            </div>
            <div id="col-progress"></div>
        </div>
        
        <!-- 已完成 -->
        <div class="column col-done">
            <div class="column-header">
                <div class="column-title">✅ 已完成 <span class="column-count" id="count-col-done">0</span></div>
            </div>
            <div id="col-done"></div>
        </div>
    </div>
    
    <div class="links">
        <h3>🔗 快速链接</h3>
        <a href="http://localhost:8768" class="link-item">🤖 模型管理</a>
        <a href="http://localhost:8769" class="link-item">📋 详细看板</a>
        <a href="http://localhost:8766" class="link-item">📊 用量统计</a>
    </div>
    
    <script>
        let tasks = [];
        
        async function load() {
            try {
                const res = await fetch('/api/tasks');
                tasks = await res.json();
                renderBoard();
            } catch (e) {
                console.error('加载失败:', e);
                loadSample();
            }
        }
        
        function renderBoard() {
            const cols = { todo: [], progress: [], done: [] };
            tasks.forEach(t => {
                if (cols[t.status]) cols[t.status].push(t);
            });
            
            // 更新统计
            document.getElementById('count-todo').textContent = cols.todo.length;
            document.getElementById('count-progress').textContent = cols.progress.length;
            document.getElementById('count-done').textContent = cols.done.length;
            
            // 更新列计数
            ['todo', 'progress', 'done'].forEach(s => {
                document.getElementById(`count-col-${s}`).textContent = cols[s].length;
            });
            
            // 渲染任务
            ['todo', 'progress', 'done'].forEach(status => {
                const el = document.getElementById(`col-${status}`);
                el.innerHTML = cols[status].length === 0 
                    ? '<div class="empty">暂无任务</div>'
                    : cols[status].map(t => renderTaskCard(t)).join('');
            });
        }
        
        function renderTaskCard(task) {
            const icons = { high: '🔴', mid: '🟡', low: '🟢' };
            return `
                <div class="task priority-${task.priority}" onclick="toggleStatus(${task.id})">
                    <div class="task-title">${escapeHtml(task.title)}</div>
                    <div class="task-meta">
                        ${task.tag ? `<span class="task-tag">${escapeHtml(task.tag)}</span>` : '<span></span>'}
                        <span class="task-time">${formatTime(task.updated || task.created)}</span>
                    </div>
                </div>
            `;
        }
        
        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function formatTime(dateStr) {
            const d = new Date(dateStr);
            const now = new Date();
            const diff = now - d;
            if (diff < 60000) return '刚刚';
            if (diff < 3600000) return Math.floor(diff/60000) + 'm';
            if (diff < 86400000) return Math.floor(diff/3600000) + 'h';
            return d.toLocaleDateString('m/d');
        }
        
        function showAddForm() {
            document.getElementById('addForm').classList.add('show');
            document.getElementById('taskTitle').focus();
        }
        
        function hideAddForm() {
            document.getElementById('addForm').classList.remove('show');
            document.getElementById('taskTitle').value = '';
            document.getElementById('taskTag').value = '';
        }
        
        async function saveTask() {
            const title = document.getElementById('taskTitle').value.trim();
            if (!title) return;
            
            const task = {
                id: Date.now(),
                title: title,
                status: 'todo',
                priority: document.getElementById('taskPriority').value,
                tag: document.getElementById('taskTag').value.trim(),
                created: new Date().toISOString(),
                updated: new Date().toISOString()
            };
            
            await fetch('/api/tasks', { method: 'POST', body: JSON.stringify(task) });
            hideAddForm();
            load();
        }
        
        async function toggleStatus(id) {
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            
            const nextStatus = task.status === 'todo' ? 'progress' : task.status === 'progress' ? 'done' : 'todo';
            await fetch('/api/tasks/move', { 
                method: 'POST', 
                body: JSON.stringify({id, status: nextStatus}) 
            });
            load();
        }
        
        function exportTasks() {
            const data = JSON.stringify(tasks, null, 2);
            const blob = new Blob([data], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tasks-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
        }
        
        function loadSample() {
            const sample = [
                {id: 1, title: '完善任务工具集合', status: 'progress', priority: 'high', tag: '开发', created: new Date().toISOString(), updated: new Date().toISOString()},
                {id: 2, title: '优化本地模型管理', status: 'todo', priority: 'mid', tag: '工具', created: new Date().toISOString(), updated: new Date().toISOString()},
                {id: 3, title: '更新桌面应用入口', status: 'done', priority: 'high', tag: '工具', created: new Date().toISOString(), updated: new Date().toISOString()}
            ];
            fetch('/api/tasks/import', { method: 'POST', body: JSON.stringify(sample) }).then(() => load());
        }
        
        function openBoard() {
            window.open('http://localhost:8769', '_blank');
        }
        
        load();
        setInterval(load, 15000);
    </script>
</body>
</html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/tasks':
            self.send_json(self.get_tasks())
        elif self.path == '/api/status':
            self.send_json({'status': 'ok', 'service': 'quick-task-panel', 'port': PORT})
        elif self.path == '/':
            self.send_html(HTML)
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/tasks':
            self.handle_add()
        elif self.path == '/api/tasks/move':
            self.handle_move()
        elif self.path == '/api/tasks/import':
            self.handle_import()
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def get_tasks(self):
        if TASKS_FILE.exists():
            try:
                with open(TASKS_FILE) as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_TASKS
    
    def save_tasks(self, tasks):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    
    def handle_add(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        tasks = self.get_tasks()
        tasks.append(data)
        self.save_tasks(tasks)
        self.send_json({'ok': True})
    
    def handle_move(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        tasks = self.get_tasks()
        for t in tasks:
            if t.get('id') == data.get('id'):
                t['status'] = data.get('status')
                t['updated'] = datetime.now().isoformat()
                break
        self.save_tasks(tasks)
        self.send_json({'ok': True})
    
    def handle_import(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.save_tasks(data)
        self.send_json({'ok': True})

def run():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✓ 快速任务面板已启动: http://localhost:{PORT}")
        print("  - 简洁任务管理")
        print("  - 快速添加/切换状态")
        print("  - 点击任务卡片切换状态")
        print("\n按 Ctrl+C 停止")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")

if __name__ == "__main__":
    run()
