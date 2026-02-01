#!/usr/bin/env python3
"""
并发任务管理器 - 分身术系统
功能：
- 并发执行多个任务
- 子代理管理
- 任务队列和分发
- 结果聚合
"""

import json
import subprocess
import threading
import queue
import time
import os
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import http.server
import socketserver
import webbrowser

# 配置
WORKSPACE = Path("/Users/fuzhuo/.openclaw/workspace")
TASKS_DIR = WORKSPACE / "concurrent-tasks"
TASKS_DIR.mkdir(parents=True, exist_ok=True)

PORT = 8780
MAX_WORKERS = 4  # 最大并发数

# 任务模板
TASK_TEMPLATES = {
    "research": {
        "name": "研究调研",
        "cmd": "python3 research-agent.py",
        "description": "深入研究某个主题"
    },
    "coding": {
        "name": "代码开发",
        "cmd": "python3 coding-agent.py",
        "description": "编写或修改代码"
    },
    "testing": {
        "name": "测试验证",
        "cmd": "python3 testing-agent.py",
        "description": "测试功能并验证结果"
    },
    "analysis": {
        "name": "数据分析",
        "cmd": "python3 analysis-agent.py",
        "description": "分析数据并生成报告"
    },
    "general": {
        "name": "通用任务",
        "cmd": "python3 general-agent.py",
        "description": "执行一般性任务"
    }
}

class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.results = {}
        self.running = set()
        self.lock = threading.Lock()
        self.load_tasks()
    
    def load_tasks(self):
        """加载任务列表"""
        tasks_file = TASKS_DIR / "tasks.json"
        if tasks_file.exists():
            try:
                with open(tasks_file) as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", {})
                    self.results = data.get("results", {})
            except:
                pass
    
    def save_tasks(self):
        """保存任务列表"""
        tasks_file = TASKS_DIR / "tasks.json"
        with open(tasks_file, 'w') as f:
            json.dump({
                "tasks": self.tasks,
                "results": self.results,
                "updated": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def create_task(self, name, task_type, description, params=None):
        """创建新任务"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.tasks)}"
        
        self.tasks[task_id] = {
            "id": task_id,
            "name": name,
            "type": task_type,
            "description": description,
            "params": params or {},
            "status": "pending",
            "created": datetime.now().isoformat(),
            "started": None,
            "completed": None,
            "output": None,
            "error": None
        }
        
        self.save_tasks()
        return task_id
    
    def run_task(self, task_id):
        """执行单个任务"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task["status"] in ["running", "completed"]:
            return False
        
        task["status"] = "running"
        task["started"] = datetime.now().isoformat()
        self.save_tasks()
        
        def execute():
            try:
                template = TASK_TEMPLATES.get(task["type"], TASK_TEMPLATES["general"])
                cmd = template["cmd"]
                
                # 构建命令参数
                args = [
                    "python3",
                    "-c",
                    f"""
import json
import sys
params = {json.dumps(task.get("params", {}))}
description = {json.dumps(task.get("description", ""))}
print(f"执行任务: {{description}}")
print(f"参数: {{json.dumps(params)}}")
# 模拟任务执行
time.sleep(2)
result = {{"status": "success", "output": f"任务完成: {{description}}"}}
print(json.dumps(result))
"""
                ]
                
                result = subprocess.run(
                    args,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                with self.lock:
                    task["status"] = "completed"
                    task["completed"] = datetime.now().isoformat()
                    task["output"] = result.stdout
                    if result.returncode != 0:
                        task["error"] = result.stderr
                    self.save_tasks()
                    
            except Exception as e:
                with self.lock:
                    task["status"] = "failed"
                    task["completed"] = datetime.now().isoformat()
                    task["error"] = str(e)
                    self.save_tasks()
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        return True
    
    def run_concurrent(self, task_ids, max_workers=None):
        """并发执行多个任务"""
        max_workers = max_workers or MAX_WORKERS
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.run_task, tid): tid for tid in task_ids}
            
            for future in as_completed(futures):
                tid = futures[future]
                try:
                    results[tid] = future.result()
                except Exception as e:
                    results[tid] = {"error": str(e)}
        
        return results
    
    def run_parallel_from_template(self, template_type, count, common_params=None):
        """从模板批量创建并行任务"""
        task_ids = []
        for i in range(count):
            task_id = self.create_task(
                name=f"{TASK_TEMPLATES[template_type]['name']} #{i+1}",
                task_type=template_type,
                description=f"{TASK_TEMPLATES[template_type]['description']} #{i+1}",
                params={**common_params, "index": i} if common_params else {"index": i}
            )
            task_ids.append(task_id)
        
        # 并发执行
        self.run_concurrent(task_ids)
        return task_ids
    
    def get_status(self):
        """获取状态"""
        pending = sum(1 for t in self.tasks.values() if t["status"] == "pending")
        running = sum(1 for t in self.tasks.values() if t["status"] == "running")
        completed = sum(1 for t in self.tasks.values() if t["status"] == "completed")
        failed = sum(1 for t in self.tasks.values() if t["status"] == "failed")
        
        return {
            "total": len(self.tasks),
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed
        }

manager = TaskManager()

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ 并发任务管理器</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', Roboto, sans-serif; 
               background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #eee; 
               min-height: 100vh; padding: 20px; }
        h1 { color: #00d9ff; margin-bottom: 10px; font-size: 1.6em; display: flex; align-items: center; gap: 10px; }
        .subtitle { color: #888; margin-bottom: 20px; font-size: 0.9em; }
        
        .stats-row { display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }
        .stat-card { background: rgba(255,255,255,0.08); border-radius: 12px; padding: 15px 20px; 
                     min-width: 100px; text-align: center; }
        .stat-value { font-size: 1.8em; font-weight: bold; color: #00d9ff; }
        .stat-label { color: #888; font-size: 0.8em; margin-top: 5px; }
        
        .section { margin-bottom: 25px; }
        .section-title { color: #e94560; font-size: 0.95em; margin-bottom: 15px; }
        
        .form { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .form-row { display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; }
        input, select, textarea { 
            padding: 12px 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); 
            background: rgba(15, 52, 96, 0.6); color: #fff; flex: 1; min-width: 200px; 
        }
        textarea { min-height: 80px; resize: vertical; }
        
        .btn { background: #e94560; color: #fff; border: none; padding: 12px 20px; 
               border-radius: 8px; cursor: pointer; font-size: 0.9em; transition: all 0.2s; }
        .btn:hover { background: #ff6b6b; transform: translateY(-2px); }
        .btn.green { background: linear-gradient(135deg, #00c853, #00e676); }
        .btn.blue { background: linear-gradient(135deg, #00d9ff, #00a8cc); }
        .btn.orange { background: linear-gradient(135deg, #ff9800, #ffb74d); }
        
        .task-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
        .task-card { 
            background: rgba(255,255,255,0.06); border-radius: 12px; padding: 15px; 
            border-left: 4px solid #666;
        }
        .task-card.pending { border-left-color: #ff9800; }
        .task-card.running { border-left-color: #00d9ff; }
        .task-card.completed { border-left-color: #00c853; }
        .task-card.failed { border-left-color: #e94560; }
        
        .task-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .task-name { font-weight: 600; color: #fff; }
        .task-badge { padding: 3px 8px; border-radius: 10px; font-size: 0.7em; }
        .badge-pending { background: rgba(255,152,0,0.2); color: #ff9800; }
        .badge-running { background: rgba(0,217,255,0.2); color: #00d9ff; }
        .badge-completed { background: rgba(0,200,83,0.2); color: #00c853; }
        .badge-failed { background: rgba(233,69,96,0.2); color: #e94560; }
        
        .task-desc { color: #aaa; font-size: 0.85em; margin-bottom: 10px; }
        .task-meta { color: #666; font-size: 0.75em; }
        
        .templates { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px; }
        .template-btn { 
            background: rgba(255,255,255,0.1); color: #00d9ff; border: 1px solid rgba(0,217,255,0.3);
            padding: 8px 15px; border-radius: 8px; cursor: pointer; font-size: 0.85em;
        }
        .template-btn:hover { background: rgba(0,217,255,0.2); }
    </style>
</head>
<body>
    <h1>⚡ 并发任务管理器</h1>
    <div class="subtitle">分身术系统 - 高效并发执行多个任务</div>
    
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-value" id="total-count">0</div>
            <div class="stat-label">总任务</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="pending-count">0</div>
            <div class="stat-label">待执行</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="running-count">0</div>
            <div class="stat-label">运行中</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="completed-count">0</div>
            <div class="stat-label">已完成</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="failed-count">0</div>
            <div class="stat-label">失败</div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">🚀 快速并行任务</div>
        <div class="templates">
            <button class="template-btn" onclick="runParallel('research', 3)">📚 研究调研 x3</button>
            <button class="template-btn" onclick="runParallel('coding', 2)">💻 代码开发 x2</button>
            <button class="template-btn" onclick="runParallel('testing', 3)">🧪 测试验证 x3</button>
            <button class="template-btn" onclick="runParallel('analysis', 2)">📊 数据分析 x2</button>
        </div>
    </div>
    
    <div class="form">
        <div class="section-title">➕ 创建新任务</div>
        <div class="form-row">
            <input type="text" id="task-name" placeholder="任务名称">
            <select id="task-type">
                <option value="general">通用任务</option>
                <option value="research">研究调研</option>
                <option value="coding">代码开发</option>
                <option value="testing">测试验证</option>
                <option value="analysis">数据分析</option>
            </select>
        </div>
        <div class="form-row">
            <textarea id="task-desc" placeholder="任务描述和参数..."></textarea>
        </div>
        <div class="form-row">
            <button class="btn" onclick="createTask()">创建任务</button>
            <button class="btn green" onclick="runAllPending()">运行所有待执行</button>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">📋 任务列表</div>
        <div class="task-grid" id="task-list"></div>
    </div>

    <script>
    async function loadStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            
            document.getElementById('total-count').textContent = data.total;
            document.getElementById('pending-count').textContent = data.pending;
            document.getElementById('running-count').textContent = data.running;
            document.getElementById('completed-count').textContent = data.completed;
            document.getElementById('failed-count').textContent = data.failed;
            
            loadTasks();
        } catch (e) {
            console.error('加载失败:', e);
        }
    }
    
    async function loadTasks() {
        try {
            const res = await fetch('/api/tasks');
            const tasks = await res.json();
            
            const grid = document.getElementById('task-list');
            let html = '';
            
            for (const [id, task] of Object.entries(tasks)) {
                const badgeClass = `badge-${task.status}`;
                const cardClass = task.status;
                const statusText = {pending: '待执行', running: '运行中', completed: '已完成', failed: '失败'}[task.status];
                
                html += `
                    <div class="task-card ${cardClass}">
                        <div class="task-header">
                            <span class="task-name">${task.name}</span>
                            <span class="task-badge ${badgeClass}">${statusText}</span>
                        </div>
                        <div class="task-desc">${task.description || '无描述'}</div>
                        <div class="task-meta">
                            创建: ${task.created?.slice(0, 19) || '未知'}
                            ${task.started ? '<br>开始: ' + task.started.slice(0, 19) : ''}
                            ${task.completed ? '<br>完成: ' + task.completed.slice(0, 19) : ''}
                        </div>
                        ${task.output ? `<div class="task-meta" style="color:#00c853;margin-top:8px;">✓ ${task.output.slice(0,50)}...</div>` : ''}
                        ${task.error ? `<div class="task-meta" style="color:#e94560;margin-top:8px;">✗ ${task.error.slice(0,50)}...</div>` : ''}
                    </div>
                `;
            }
            
            grid.innerHTML = html || '<p style="color:#666;">暂无任务</p>';
        } catch (e) {
            console.error('加载任务失败:', e);
        }
    }
    
    async function createTask() {
        const name = document.getElementById('task-name').value;
        const type = document.getElementById('task-type').value;
        const desc = document.getElementById('task-desc').value;
        
        if (!name) {
            alert('请输入任务名称');
            return;
        }
        
        try {
            const res = await fetch('/api/tasks/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, type, description: desc})
            });
            const data = await res.json();
            
            if (data.task_id) {
                alert('任务创建成功: ' + data.task_id);
                document.getElementById('task-name').value = '';
                document.getElementById('task-desc').value = '';
                loadStatus();
            }
        } catch (e) {
            alert('创建失败: ' + e);
        }
    }
    
    async function runParallel(type, count) {
        try {
            const res = await fetch('/api/parallel', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type, count})
            });
            const data = await res.json();
            alert(`已创建 ${data.task_ids?.length || 0} 个并行任务`);
            loadStatus();
        } catch (e) {
            alert('执行失败: ' + e);
        }
    }
    
    async function runAllPending() {
        try {
            const res = await fetch('/api/run-all', {method: 'POST'});
            const data = await res.json();
            alert(`已启动 ${data.started || 0} 个任务`);
            loadStatus();
        } catch (e) {
            alert('执行失败: ' + e);
        }
    }
    
    loadStatus();
    setInterval(loadStatus, 3000);
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
        elif self.path == '/api/status':
            status = manager.get_status()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        elif self.path == '/api/tasks':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(manager.tasks, ensure_ascii=False).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/tasks/create':
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length)
            data = json.loads(body)
            
            task_id = manager.create_task(
                name=data.get('name', '未命名任务'),
                task_type=data.get('type', 'general'),
                description=data.get('description', '')
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"task_id": task_id}).encode())
        
        elif self.path == '/api/parallel':
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length)
            data = json.loads(body)
            
            task_ids = manager.run_parallel_from_template(
                data.get('type', 'general'),
                data.get('count', 1)
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"task_ids": task_ids}).encode())
        
        elif self.path == '/api/run-all':
            pending_ids = [tid for tid, t in manager.tasks.items() if t["status"] == "pending"]
            results = manager.run_concurrent(pending_ids)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"started": len(pending_ids), "results": results}).encode())
        
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        pass

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ 并发任务管理器已启动: http://localhost:{PORT}")
        print(f"   最大并发数: {MAX_WORKERS}")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")

if __name__ == "__main__":
    run()
