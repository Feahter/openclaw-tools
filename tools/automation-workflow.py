#!/usr/bin/env python3
"""
自动化工作流工具
快速执行并行任务、定时任务、批量操作
"""

import subprocess
import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import http.server
import socketserver
import webbrowser
import threading

# 配置
WORKFLOW_DIR = Path.home() / ".openclaw" / "workflows"
PORT = 8771

WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)

# 预设工作流模板
TEMPLATES = {
    "parallel_test": {
        "name": "并行测试",
        "description": "同时执行多个测试任务",
        "tasks": [
            {"cmd": "echo '任务1'", "name": "任务1"},
            {"cmd": "echo '任务2'", "name": "任务2"},
            {"cmd": "echo '任务3'", "name": "任务3"}
        ]
    },
    "daily_check": {
        "name": "每日检查",
        "description": "检查服务状态和资源使用",
        "tasks": [
            {"cmd": "curl -s http://localhost:8768/api/status | head -1", "name": "检查模型服务"},
            {"cmd": "curl -s http://localhost:8769/api/tasks | python3 -c \"import json,sys; print(len(json.load(sys.stdin)), '个任务')\"", "name": "检查任务看板"},
            {"cmd": "ps aux | grep -c '[p]ython' || echo '0'", "name": "检查Python进程"}
        ]
    },
    "backup_data": {
        "name": "数据备份",
        "description": "备份重要配置文件",
        "tasks": [
            {"cmd": "cp ~/.openclaw/task-board.json ~/.openclaw/backups/task-board.json 2>/dev/null || echo '无备份'", "name": "备份任务看板"},
            {"cmd": "cp ~/.api-keys/keys.json ~/.openclaw/backups/keys.json 2>/dev/null || echo '无备份'", "name": "备份API Keys"}
        ]
    }
}

def run_task(task, timeout=30):
    """执行单个任务"""
    try:
        result = subprocess.run(
            task["cmd"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "name": task.get("name", "未知"),
            "cmd": task["cmd"],
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
            "duration": 0
        }
    except subprocess.TimeoutExpired:
        return {
            "name": task.get("name", "未知"),
            "cmd": task["cmd"],
            "stdout": "",
            "stderr": "超时",
            "returncode": -1,
            "duration": timeout
        }
    except Exception as e:
        return {
            "name": task.get("name", "未知"),
            "cmd": task["cmd"],
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
            "duration": 0
        }

def run_workflow(workflow):
    """执行工作流（并行）"""
    start_time = time.time()
    results = []
    
    threads = []
    for task in workflow.get("tasks", []):
        t = threading.Thread(target=lambda r=task, res=results: res.append(run_task(r)))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    duration = time.time() - start_time
    return {
        "results": results,
        "duration": round(duration, 2),
        "success_count": sum(1 for r in results if r["returncode"] == 0)
    }

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ 自动化工作流</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #eee; 
               min-height: 100vh; padding: 20px; }
        h1 { color: #00d9ff; margin-bottom: 20px; }
        h2 { color: #e94560; margin: 20px 0 15px; }
        
        .btn { background: #e94560; color: #fff; border: none; padding: 10px 18px; 
               border-radius: 8px; cursor: pointer; font-size: 0.9em; margin-right: 8px; margin-bottom: 8px; }
        .btn:hover { background: #ff6b6b; }
        .btn.green { background: #00c853; }
        .btn.green:hover { background: #00e676; }
        .btn.blue { background: #00d9ff; color: #1a1a2e; }
        .btn.blue:hover { background: #00e6ff; }
        
        .template-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .template-card { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; }
        .template-name { font-weight: bold; color: #00d9ff; margin-bottom: 5px; }
        .template-desc { color: #888; font-size: 0.85em; margin-bottom: 10px; }
        
        .result-card { background: rgba(255,255,255,0.05); border-radius: 8px; padding: 12px; margin-bottom: 10px; }
        .result-name { font-weight: bold; color: #00d9ff; margin-bottom: 5px; }
        .result-cmd { color: #666; font-size: 0.8em; font-family: monospace; margin-bottom: 8px; }
        .result-output { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; font-family: monospace; font-size: 0.85em; white-space: pre-wrap; word-break: break-all; }
        .result-success { border-left: 3px solid #00c853; }
        .result-failed { border-left: 3px solid #e94560; }
        
        .stats { display: flex; gap: 20px; margin-bottom: 20px; }
        .stat { background: rgba(255,255,255,0.1); padding: 15px 25px; border-radius: 10px; text-align: center; }
        .stat-value { font-size: 1.8em; font-weight: bold; color: #00d9ff; }
        .stat-label { color: #888; font-size: 0.85em; margin-top: 5px; }
    </style>
</head>
<body>
    <h1>⚡ 自动化工作流</h1>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value" id="success-count">0</div>
            <div class="stat-label">成功任务</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="total-count">0</div>
            <div class="stat-label">总任务数</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="duration">0s</div>
            <div class="stat-label">执行时间</div>
        </div>
    </div>
    
    <button class="btn green" onclick="runTemplate('parallel_test')">▶️ 并行测试</button>
    <button class="btn green" onclick="runTemplate('daily_check')">📊 每日检查</button>
    <button class="btn green" onclick="runTemplate('backup_data')">💾 数据备份</button>
    <button class="btn" onclick="loadResults()">🔄 刷新</button>
    
    <h2>执行结果</h2>
    <div id="results">
        <p style="color: #666;">点击上方按钮执行工作流</p>
    </div>

    <script>
    async function runTemplate(name) {
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = '执行中...';
        
        try {
            const res = await fetch('/api/run', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({template: name})
            });
            const data = await res.json();
            displayResults(data);
        } catch (e) {
            document.getElementById('results').innerHTML = '<p style="color: #e94560;">执行失败: ' + e + '</p>';
        }
        
        btn.disabled = false;
        btn.textContent = '▶️ ' + name.replace('_', ' ');
    }
    
    function displayResults(data) {
        const results = data.results || [];
        const success = data.success_count || 0;
        
        document.getElementById('success-count').textContent = success;
        document.getElementById('total-count').textContent = results.length;
        document.getElementById('duration').textContent = (data.duration || 0) + 's';
        
        let html = '';
        results.forEach(r => {
            const status = r.returncode === 0 ? 'success' : 'failed';
            const statusText = r.returncode === 0 ? '✅' : '❌';
            html += `
                <div class="result-card result-${status}">
                    <div class="result-name">${statusText} ${r.name}</div>
                    <div class="result-cmd">${r.cmd}</div>
                    <div class="result-output">${r.stdout || r.stderr || '无输出'}</div>
                </div>
            `;
        });
        document.getElementById('results').innerHTML = html || '<p>无结果</p>';
    }
    
    function loadResults() {
        fetch('/api/results')
            .then(r => r.json())
            .then(displayResults)
            .catch(e => console.log('加载失败'));
    }
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
        elif self.path == '/api/results':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "无历史数据"}).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/run':
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length)
            data = json.loads(body)
            
            template_name = data.get('template')
            workflow = TEMPLATES.get(template_name, {})
            
            result = run_workflow(workflow)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        pass

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ 自动化工作流已启动: http://localhost:{PORT}")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")

if __name__ == "__main__":
    run()
