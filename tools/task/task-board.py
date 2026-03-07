#!/usr/bin/env python3
"""
任务看板 - 主动任务追踪工具
功能：
- 可视化任务状态
- 支持 TODO / 进行中 / 完成 / 暂停
- 自动保存到本地
- 简单的 Web UI
"""

import json
import os
from pathlib import Path
from datetime import datetime
import http.server
import socketserver
import webbrowser

# 配置
BOARD_DIR = Path(__file__).parent.parent / "data"
BOARD_FILE = BOARD_DIR / "task-board.json"
PORT = 8769

# 默认任务模板
DEFAULT_TASKS = []

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📋 任务看板</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #eee; 
               min-height: 100vh; padding: 20px; }
        h1 { color: #00d9ff; margin-bottom: 8px; font-size: 1.8em; display: flex; align-items: center; gap: 10px; }
        .subtitle { color: #888; margin-bottom: 20px; font-size: 0.9em; }
        
        /* 头部操作区 */
        .header-actions { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .btn { background: #e94560; color: #fff; border: none; padding: 10px 18px; 
               border-radius: 8px; cursor: pointer; font-size: 0.9em; transition: all 0.2s; }
        .btn:hover { background: #ff6b6b; transform: scale(1.05); }
        .btn.green { background: linear-gradient(135deg, #00c853, #00e676); }
        .btn.green:hover { background: linear-gradient(135deg, #00e676, #69f0ae); }
        .btn.blue { background: linear-gradient(135deg, #00d9ff, #00a8cc); }
        .btn.blue:hover { background: linear-gradient(135deg, #00e6ff, #00c4ff); }
        
        /* 搜索框 */
        .search-box { position: relative; flex: 1; min-width: 200px; }
        .search-box input { width: 100%; padding: 10px 15px 10px 40px; border-radius: 8px; 
                           border: 1px solid rgba(255,255,255,0.1); background: rgba(15,52,96,0.6); 
                           color: #fff; }
        .search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #666; }
        
        /* 看板列 */
        .board { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
        .column { background: rgba(22, 33, 62, 0.8); backdrop-filter: blur(10px); 
                  border-radius: 16px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); }
        .column-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .column-title { font-size: 1em; font-weight: 600; display: flex; align-items: center; gap: 8px; }
        .column-count { background: rgba(255,255,255,0.1); padding: 2px 10px; border-radius: 10px; font-size: 0.8em; }
        
        /* 列颜色标识 */
        .col-todo .column-title { color: #ff9800; }
        .col-progress .column-title { color: #00d9ff; }
        .col-done .column-title { color: #00c853; }
        .col-pause .column-title { color: #ff5252; }
        
        /* 任务卡片 */
        .task { background: rgba(15, 52, 96, 0.6); border-radius: 10px; padding: 12px; 
                margin: 10px 0; transition: all 0.2s; border: 1px solid transparent; cursor: pointer; }
        .task:hover { background: rgba(15, 52, 96, 0.9); border-color: rgba(0,217,255,0.3); }
        .task-title { font-weight: 500; color: #fff; margin-bottom: 8px; }
        .task-desc { color: #888; font-size: 0.85em; line-height: 1.5; }
        .task-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; 
                     font-size: 0.8em; color: #666; }
        .task-tag { background: rgba(0,217,255,0.2); color: #00d9ff; padding: 2px 8px; border-radius: 4px; }
        .task-priority { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 5px; }
        .priority-high { background: #ff5252; }
        .priority-mid { background: #ff9800; }
        .priority-low { background: #00c853; }
        
        /* 空状态 */
        .empty { text-align: center; color: #666; padding: 30px 0; opacity: 0.5; }
        
        /* 模态框 */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                 background: rgba(0,0,0,0.7); z-index: 1000; align-items: center; justify-content: center; }
        .modal.show { display: flex; }
        .modal-content { background: #16213e; border-radius: 16px; padding: 25px; width: 90%; max-width: 500px; 
                         border: 1px solid rgba(255,255,255,0.1); }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .modal-title { font-size: 1.2em; color: #00d9ff; }
        .modal-close { background: none; border: none; color: #666; font-size: 1.5em; cursor: pointer; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; color: #888; margin-bottom: 5px; font-size: 0.9em; }
        .form-group input, .form-group select, .form-group textarea { 
            width: 100%; padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); 
            background: rgba(15,52,96,0.6); color: #fff; }
        .form-group textarea { min-height: 80px; resize: vertical; }
        .modal-actions { display: flex; gap: 10px; margin-top: 20px; justify-content: flex-end; }
        
        /* 任务详情弹窗 */
        .task-detail { position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                       background: rgba(0,0,0,0.7); z-index: 1000; display: none; }
        .task-detail.show { display: flex; }
        .detail-content { background: #16213e; border-radius: 16px; padding: 25px; width: 90%; max-width: 600px; 
                          margin: auto; border: 1px solid rgba(255,255,255,0.1); max-height: 80vh; overflow-y: auto; }
        .detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
        .detail-title { font-size: 1.3em; color: #fff; font-weight: 600; }
        .detail-desc { color: #ccc; line-height: 1.8; margin-bottom: 20px; white-space: pre-wrap; }
        .detail-meta { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }
        .meta-item { background: rgba(15,52,96,0.6); padding: 10px; border-radius: 8px; }
        .meta-label { color: #888; font-size: 0.8em; }
        .meta-value { color: #00d9ff; margin-top: 5px; }
        
        /* 进度条 */
        .progress-bar { height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #00d9ff, #00c853); transition: width 0.3s; }
        
        /* 响应式 */
        @media (max-width: 768px) {
            .board { grid-template-columns: 1fr; }
            .header-actions { flex-direction: column; }
        }
    </style>
</head>
<body>
    <h1>📋 任务看板</h1>
    <div class="subtitle">主动任务追踪 · 记得我正在做什么</div>
    
    <div class="header-actions">
        <button class="btn green" onclick="showAddModal()">+ 添加任务</button>
        <div class="search-box">
            <span class="search-icon">🔍</span>
            <input type="text" id="taskSearch" placeholder="搜索任务..." oninput="renderBoard()">
        </div>
        <button class="btn blue" onclick="exportBoard()">📤 导出</button>
        <button class="btn" onclick="loadSample()">📥 示例</button>
    </div>
    
    <div class="board" id="board">
        <!-- TODO 列 -->
        <div class="column col-todo">
            <div class="column-header">
                <div class="column-title">📝 待办 <span class="column-count" id="count-todo">0</span></div>
            </div>
            <div id="col-todo"></div>
        </div>
        
        <!-- 进行中 列 -->
        <div class="column col-progress">
            <div class="column-header">
                <div class="column-title">🚀 进行中 <span class="column-count" id="count-progress">0</span></div>
            </div>
            <div id="col-progress"></div>
        </div>
        
        <!-- 完成 列 -->
        <div class="column col-done">
            <div class="column-header">
                <div class="column-title">✅ 已完成 <span class="column-count" id="count-done">0</span></div>
            </div>
            <div id="col-done"></div>
        </div>
        
        <!-- 暂停 列 -->
        <div class="column col-pause">
            <div class="column-header">
                <div class="column-title">⏸️ 暂停 <span class="column-count" id="count-pause">0</span></div>
            </div>
            <div id="col-pause"></div>
        </div>
    </div>
    
    <!-- 添加任务模态框 -->
    <div class="modal" id="addModal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">添加新任务</div>
                <button class="modal-close" onclick="hideAddModal()">×</button>
            </div>
            <div class="form-group">
                <label>任务标题 *</label>
                <input type="text" id="taskTitle" placeholder="简洁描述任务">
            </div>
            <div class="form-group">
                <label>详细描述</label>
                <textarea id="taskDesc" placeholder="任务细节、目标、注意事项..."></textarea>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div class="form-group">
                    <label>状态</label>
                    <select id="taskStatus">
                        <option value="todo">待办</option>
                        <option value="progress">进行中</option>
                        <option value="pause">暂停</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>优先级</label>
                    <select id="taskPriority">
                        <option value="high">🔴 高</option>
                        <option value="mid" selected>🟡 中</option>
                        <option value="low">🟢 低</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label>标签</label>
                <input type="text" id="taskTag" placeholder="如: 代码, 文档, 实验 (逗号分隔)">
            </div>
            <div class="modal-actions">
                <button class="btn" onclick="hideAddModal()">取消</button>
                <button class="btn green" onclick="saveTask()">保存</button>
            </div>
        </div>
    </div>
    
    <!-- 任务详情弹窗 -->
    <div class="task-detail" id="detailModal">
        <div class="detail-content">
            <div class="detail-header">
                <div class="detail-title" id="detailTitle"></div>
                <button class="modal-close" onclick="hideDetailModal()">×</button>
            </div>
            <div class="detail-desc" id="detailDesc"></div>
            <div class="detail-meta">
                <div class="meta-item">
                    <div class="meta-label">状态</div>
                    <div class="meta-value" id="detailStatus"></div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">优先级</div>
                    <div class="meta-value" id="detailPriority"></div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">标签</div>
                    <div class="meta-value" id="detailTag"></div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">进度</div>
                    <div class="meta-value" id="detailProgress"></div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">创建时间</div>
                    <div class="meta-value" id="detailCreated"></div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">更新时间</div>
                    <div class="meta-value" id="detailUpdated"></div>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="detailProgressBar" style="width: 0%"></div>
            </div>
            <div class="modal-actions">
                <button class="btn danger" onclick="deleteTask()">🗑️ 删除</button>
                <button class="btn" onclick="moveTask('todo')">📝 待办</button>
                <button class="btn blue" onclick="moveTask('progress')">🚀 进行</button>
                <button class="btn green" onclick="moveTask('done')">✅ 完成</button>
                <button class="btn" onclick="moveTask('pause')">⏸️ 暂停</button>
            </div>
        </div>
    </div>
    
    <script>
        let tasks = [];
        let currentTaskId = null;
        
        async function load() {
            try {
                const res = await fetch('/api/tasks');
                tasks = await res.json();
                renderBoard();
            } catch (e) {
                console.error('加载失败:', e);
            }
        }
        
        function renderBoard() {
            const search = document.getElementById('taskSearch').value.toLowerCase();
            const filtered = tasks.filter(t => 
                t.title.toLowerCase().includes(search) || 
                (t.desc || '').toLowerCase().includes(search) ||
                (t.tag || '').toLowerCase().includes(search)
            );
            
            const cols = { todo: [], progress: [], done: [], pause: [] };
            filtered.forEach(t => cols[t.status]?.push(t));
            
            // 渲染各列
            Object.keys(cols).forEach(status => {
                document.getElementById(`col-${status}`).innerHTML = cols[status].length === 0 
                    ? '<div class="empty">暂无任务</div>'
                    : cols[status].map(t => renderTaskCard(t)).join('');
                document.getElementById(`count-${status}`).textContent = cols[status].length;
            });
        }
        
        function renderTaskCard(task) {
            const priorityIcon = task.priority === 'high' ? '🔴' : task.priority === 'mid' ? '🟡' : '🟢';
            const tags = (task.tag || '').split(',').filter(Boolean).map(t => 
                `<span class="task-tag">${t.trim()}</span>`
            ).join('');
            
            return `
                <div class="task" onclick="showDetail(${task.id})">
                    <div class="task-title">
                        <span class="task-priority priority-${task.priority}"></span>
                        ${escapeHtml(task.title)}
                    </div>
                    ${task.desc ? `<div class="task-desc">${escapeHtml(task.desc.slice(0,60))}${task.desc.length > 60 ? '...' : ''}</div>` : ''}
                    <div class="task-meta">
                        <div>${tags}</div>
                        <div>${formatDate(task.updated)}</div>
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
        
        function formatDate(dateStr) {
            const d = new Date(dateStr);
            const now = new Date();
            const diff = now - d;
            if (diff < 60000) return '刚刚';
            if (diff < 3600000) return Math.floor(diff/60000) + '分钟前';
            if (diff < 86400000) return Math.floor(diff/3600000) + '小时前';
            return d.toLocaleDateString('zh-CN');
        }
        
        function showAddModal() {
            document.getElementById('addModal').classList.add('show');
            document.getElementById('taskTitle').focus();
        }
        
        function hideAddModal() {
            document.getElementById('addModal').classList.remove('show');
            document.getElementById('taskTitle').value = '';
            document.getElementById('taskDesc').value = '';
            document.getElementById('taskTag').value = '';
        }
        
        async function saveTask() {
            const title = document.getElementById('taskTitle').value.trim();
            if (!title) { alert('请输入任务标题'); return; }
            
            const task = {
                id: Date.now(),
                title: title,
                desc: document.getElementById('taskDesc').value.trim(),
                status: document.getElementById('taskStatus').value,
                priority: document.getElementById('taskPriority').value,
                tag: document.getElementById('taskTag').value.trim(),
                progress: document.getElementById('taskStatus').value === 'progress' ? 0 : null,
                created: new Date().toISOString(),
                updated: new Date().toISOString()
            };
            
            await fetch('/api/tasks', {
                method: 'POST', body: JSON.stringify(task)
            });
            hideAddModal();
            load();
        }
        
        function showDetail(id) {
            currentTaskId = id;
            const task = tasks.find(t => t.id === id);
            if (!task) return;
            
            document.getElementById('detailTitle').textContent = task.title;
            document.getElementById('detailDesc').textContent = task.desc || '无描述';
            document.getElementById('detailStatus').textContent = 
                task.status === 'todo' ? '📝 待办' : 
                task.status === 'progress' ? '🚀 进行中' : 
                task.status === 'done' ? '✅ 已完成' : '⏸️ 暂停';
            document.getElementById('detailPriority').textContent = 
                task.priority === 'high' ? '🔴 高' : 
                task.priority === 'mid' ? '🟡 中' : '🟢 低';
            document.getElementById('detailTag').textContent = task.tag || '无';
            document.getElementById('detailProgress').textContent = task.progress !== null ? task.progress + '%' : '未开始';
            document.getElementById('detailProgressBar').style.width = (task.progress || 0) + '%';
            document.getElementById('detailCreated').textContent = formatDate(task.created);
            document.getElementById('detailUpdated').textContent = formatDate(task.updated);
            
            document.getElementById('detailModal').classList.add('show');
        }
        
        function hideDetailModal() {
            document.getElementById('detailModal').classList.remove('show');
            currentTaskId = null;
        }
        
        async function moveTask(status) {
            if (currentTaskId === null) return;
            await fetch('/api/tasks/move', {
                method: 'POST', body: JSON.stringify({id: currentTaskId, status})
            });
            hideDetailModal();
            load();
        }
        
        async function deleteTask() {
            if (!confirm('确定删除此任务？')) return;
            if (currentTaskId === null) return;
            await fetch('/api/tasks/delete', {
                method: 'POST', body: JSON.stringify({id: currentTaskId})
            });
            hideDetailModal();
            load();
        }
        
        function exportBoard() {
            const data = JSON.stringify(tasks, null, 2);
            const blob = new Blob([data], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `task-board-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
        }
        
        function loadSample() {
            if (tasks.length > 0 && !confirm('示例任务会覆盖现有任务，确定？')) return;
            const sample = [
                {id: 1, title: '优化工具UI', desc: '完善 local-model-manager.py 的界面效果', status: 'progress', priority: 'high', tag: '工具,UI', progress: 60, created: new Date().toISOString(), updated: new Date().toISOString()},
                {id: 2, title: '添加用量追踪', desc: '记录 API 调用次数和 Token 消耗', status: 'progress', priority: 'mid', tag: '功能', progress: 80, created: new Date().toISOString(), updated: new Date().toISOString()},
                {id: 3, title: '下载本地模型', desc: 'smollm:1.7b, moondream2, nemotron-mini, codegemma', status: 'todo', priority: 'mid', tag: '模型', created: new Date().toISOString(), updated: new Date().toISOString()},
                {id: 4, title: '完善任务看板', desc: '创建主动任务追踪看板', status: 'done', priority: 'high', tag: '工具', progress: 100, created: new Date().toISOString(), updated: new Date().toISOString()},
                {id: 5, title: '学习新技能', desc: '探索 ClawdHub 技能市场', status: 'pause', priority: 'low', tag: '学习', created: new Date().toISOString(), updated: new Date().toISOString()}
            ];
            fetch('/api/tasks/import', {
                method: 'POST', body: JSON.stringify(sample)
            }).then(() => load());
        }
        
        load();
        setInterval(load, 30000);
    </script>
</body>
</html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/tasks':
            self.send_json(self.get_tasks())
        elif self.path == '/api/status':
            self.send_json({'status': 'ok', 'service': 'task-board'})
        elif self.path == '/':
            self.send_html(HTML)
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/tasks':
            self.handle_task_add()
        elif self.path == '/api/tasks/move':
            self.handle_task_move()
        elif self.path == '/api/tasks/delete':
            self.handle_task_delete()
        elif self.path == '/api/tasks/import':
            self.handle_tasks_import()
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
        if BOARD_FILE.exists():
            try:
                with open(BOARD_FILE) as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_TASKS
    
    def save_tasks(self, tasks):
        with open(BOARD_FILE, 'w') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    
    def handle_task_add(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        tasks = self.get_tasks()
        tasks.append(data)
        self.save_tasks(tasks)
        self.send_json({'ok': True})
    
    def handle_task_move(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        tasks = self.get_tasks()
        for t in tasks:
            if t.get('id') == data.get('id'):
                t['status'] = data.get('status')
                t['updated'] = datetime.now().isoformat()
                break
        self.save_tasks(tasks)
        self.send_json({'ok': True})
    
    def handle_task_delete(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        tasks = self.get_tasks()
        tasks = [t for t in tasks if t.get('id') != data.get('id')]
        self.save_tasks(tasks)
        self.send_json({'ok': True})
    
    def handle_tasks_import(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.save_tasks(data)
        self.send_json({'ok': True})

def run():
    BOARD_DIR.mkdir(parents=True, exist_ok=True)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✓ 任务看板已启动: http://localhost:{PORT}")
        print("按 Ctrl+C 停止")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")

if __name__ == "__main__":
    run()
