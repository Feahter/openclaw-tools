#!/usr/bin/env python3
"""
能力应用集合 - 展示和启用 OpenClaw Agent 的所有能力
集成到统一控制台 (端口 8765)
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import http.server
import socketserver
import webbrowser

# 配置
PORT = 8772
CONFIG_DIR = Path.home() / ".openclaw"
CAPABILITIES_FILE = CONFIG_DIR / "capabilities.json"

# 能力定义
CAPABILITIES = {
    "消息能力": {
        "icon": "💬",
        "status": "ready",
        "local": True,
        "description": "通过 Slack、Telegram、WhatsApp 等发送消息",
        "depends": "OpenClaw gateway",
        "actions": [{"label": "打开控制台", "url": "http://localhost:18789"}]
    },
    "文件操作": {
        "icon": "📁",
        "status": "ready",
        "local": True,
        "description": "读写、移动、搜索文件",
        "depends": "Python",
        "actions": [{"label": "查看文档", "type": "doc"}]
    },
    "命令执行": {
        "icon": "⚙️",
        "status": "ready",
        "local": True,
        "description": "执行 shell 命令、脚本、自动化任务",
        "depends": "无",
        "actions": []
    },
    "TTS 语音合成": {
        "icon": "🔊",
        "status": "ready",
        "local": True,
        "description": "将文字转换为语音朗读（macOS 内置）",
        "depends": "macOS say",
        "test_cmd": "say '测试语音'",
        "actions": [
            {"label": "🔊 测试播放", "cmd": "say '你好，我是 OpenClaw'"},
            {"label": "📋 语音列表", "cmd": "say -v '?' | head -10"}
        ]
    },
    "定时任务": {
        "icon": "⏰",
        "status": "ready",
        "local": True,
        "description": "定时执行任务、心跳监控、自动同步",
        "depends": "heartbeat.py",
        "actions": [
            {"label": "▶️ 启动心跳", "cmd": "cd /Users/fuzhuo/.openclaw/workspace/tools && nohup python3 heartbeat.py --loop 30 > /tmp/heartbeat.log 2>&1 &"},
            {"label": "📊 查看日志", "cmd": "tail -20 /tmp/heartbeat.log"}
        ]
    },
    "Canvas 画布": {
        "icon": "🎨",
        "status": "config",
        "local": True,
        "description": "生成图片、图表、验证码",
        "depends": "Node.js + canvas",
        "install": "npm install canvas",
        "actions": [
            {"label": "📦 安装依赖", "cmd": "cd /Users/fuzhuo/.openclaw/workspace && npm install canvas"}
        ]
    },
    "会话管理": {
        "icon": "💭",
        "status": "ready",
        "local": True,
        "description": "管理对话历史、上下文记忆",
        "depends": "OpenClaw sessions",
        "actions": [{"label": "查看会话", "url": "http://localhost:18789/sessions"}]
    },
    "工具管理": {
        "icon": "🧰",
        "status": "ready",
        "local": True,
        "description": "加载和管理 Agent Skills",
        "depends": "OpenClaw skills",
        "actions": [{"label": "查看技能", "url": "http://localhost:18789/skills"}]
    },
    "图片分析": {
        "icon": "👁️",
        "status": "config",
        "local": "partial",
        "description": "识别图片内容、看图回答问题（需 Ollama 视觉模型）",
        "depends": "Ollama + llava/bakllava",
        "install": "ollama pull llava",
        "actions": [
            {"label": "📥 安装 llava", "cmd": "ollama pull llava"},
            {"label": "📥 安装 bakllava", "cmd": "ollama pull bakllava"}
        ]
    },
    "STT 语音转文字": {
        "icon": "🎤",
        "status": "config",
        "local": "partial",
        "description": "将录音转换为文字（需 Whisper）",
        "depends": "openai-whisper",
        "install": "pip install openai-whisper",
        "actions": [
            {"label": "📦 安装 Whisper", "cmd": "pip3 install openai-whisper"}
        ]
    },
    "Web Fetch": {
        "icon": "🌐",
        "status": "ready",
        "local": "partial",
        "description": "获取网页内容、提取关键信息",
        "depends": "curl / requests",
        "actions": []
    },
    "记忆功能": {
        "icon": "🧠",
        "status": "config",
        "local": "partial",
        "description": "长期记忆、语义搜索、智能回忆",
        "depends": "SQLite / LanceDB",
        "actions": []
    },
    "Web 搜索": {
        "icon": "🔍",
        "status": "cloud",
        "local": False,
        "description": "网络搜索、实时信息查询",
        "depends": "Brave API / Perplexity API",
        "config_needed": "tools.web.search.apiKey",
        "actions": []
    },
    "浏览器控制": {
        "icon": "🌍",
        "status": "config",
        "local": "partial",
        "description": "自动化浏览器操作、截图、表单填写",
        "depends": "Chrome/Chromium + Playwright",
        "actions": []
    }
}

def check_status():
    """检查各能力状态"""
    status = {}
    
    # 检查 macOS say
    try:
        subprocess.run(["which", "say"], capture_output=True)
        status["TTS 语音合成"] = {"available": True, "installed": True}
    except:
        status["TTS 语音合成"] = {"available": True, "installed": False}
    
    # 检查 Ollama
    try:
        result = subprocess.run(["curl", "-s", "http://localhost:11434/api/version"], capture_output=True, timeout=5)
        if result.returncode == 0:
            status["Ollama"] = {"available": True}
            # 检查视觉模型
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            has_vision = "llava" in result.stdout.lower() or "bakllava" in result.stdout.lower()
            status["Ollama"]["vision_model"] = has_vision
    except:
        status["Ollama"] = {"available": False}
    
    # 检查 Whisper
    try:
        subprocess.run(["which", "whisper"], capture_output=True)
        status["Whisper"] = {"available": True}
    except:
        status["Whisper"] = {"available": False}
    
    return status

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 能力应用集合</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', Roboto, sans-serif; 
               background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #eee; 
               min-height: 100vh; padding: 20px; }
        h1 { color: #00d9ff; margin-bottom: 10px; font-size: 1.6em; display: flex; align-items: center; gap: 12px; }
        .subtitle { color: #888; margin-bottom: 25px; font-size: 0.9em; }
        
        .stats-row { display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }
        .stat-card { background: rgba(255,255,255,0.08); border-radius: 12px; padding: 15px 20px; 
                     min-width: 140px; text-align: center; }
        .stat-value { font-size: 1.8em; font-weight: bold; color: #00d9ff; }
        .stat-label { color: #888; font-size: 0.8em; margin-top: 5px; }
        .stat-value.ready { color: #00c853; }
        .stat-value.config { color: #ff9800; }
        .stat-value.cloud { color: #9e9e9e; }
        
        .section { margin-bottom: 30px; }
        .section-title { color: #e94560; font-size: 0.95em; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
        
        .cap-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 15px; }
        .cap-card { 
            background: rgba(255,255,255,0.06); border-radius: 14px; padding: 18px; 
            transition: all 0.3s; border: 1px solid transparent;
        }
        .cap-card:hover { background: rgba(255,255,255,0.1); transform: translateY(-3px); }
        .cap-card.ready { border-color: rgba(0,200,83,0.3); }
        .cap-card.config { border-color: rgba(255,152,0,0.3); }
        .cap-card.cloud { border-color: rgba(158,158,158,0.3); }
        
        .cap-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
        .cap-icon { font-size: 1.8em; }
        .cap-name { font-weight: 600; color: #fff; font-size: 1.05em; }
        .cap-badge { 
            margin-left: auto; padding: 3px 8px; border-radius: 10px; font-size: 0.7em; font-weight: 500;
        }
        .badge-ready { background: rgba(0,200,83,0.2); color: #00c853; }
        .badge-config { background: rgba(255,152,0,0.2); color: #ff9800; }
        .badge-cloud { background: rgba(158,158,158,0.2); color: #9e9e9e; }
        .badge-local { background: rgba(0,217,255,0.2); color: #00d9ff; }
        
        .cap-desc { color: #aaa; font-size: 0.85em; line-height: 1.5; margin-bottom: 12px; }
        .cap-depends { color: #666; font-size: 0.75em; margin-bottom: 12px; }
        
        .cap-actions { display: flex; gap: 8px; flex-wrap: wrap; }
        .btn { 
            background: rgba(255,255,255,0.1); color: #fff; border: none; padding: 6px 12px; 
            border-radius: 6px; cursor: pointer; font-size: 0.8em; transition: all 0.2s;
        }
        .btn:hover { background: rgba(255,255,255,0.2); }
        .btn.green { background: rgba(0,200,83,0.3); color: #00c853; }
        .btn.blue { background: rgba(0,217,255,0.3); color: #00d9ff; }
        .btn.orange { background: rgba(255,152,0,0.3); color: #ff9800; }
        
        .terminal { 
            background: rgba(0,0,0,0.4); border-radius: 8px; padding: 15px; 
            font-family: 'SF Mono', Monaco, monospace; font-size: 0.8em; 
            margin-top: 15px; display: none;
        }
        .terminal.show { display: block; }
        .terminal-output { color: #00ff00; white-space: pre-wrap; word-break: break-all; }
        .terminal-close { float: right; cursor: pointer; color: #666; }
    </style>
</head>
<body>
    <h1>🧠 能力应用集合</h1>
    <div class="subtitle">OpenClaw Agent 所有能力一览 · 可本地化部署</div>
    
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-value ready" id="ready-count">0</div>
            <div class="stat-label">就绪可用</div>
        </div>
        <div class="stat-card">
            <div class="stat-value config" id="config-count">0</div>
            <div class="stat-label">需配置/安装</div>
        </div>
        <div class="stat-card">
            <div class="stat-value cloud" id="cloud-count">0</div>
            <div class="stat-label">需云端</div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">✅ 完全本地化</div>
        <div class="cap-grid" id="local-grid"></div>
    </div>
    
    <div class="section">
        <div class="section-title">⚙️ 需配置/安装</div>
        <div class="cap-grid" id="config-grid"></div>
    </div>
    
    <div class="section">
        <div class="section-title">☁️ 需要云端服务</div>
        <div class="cap-grid" id="cloud-grid"></div>
    </div>

    <script>
    const capabilities = CAPABILITIES;
    
    function renderCards() {
        const ready = [];
        const config = [];
        const cloud = [];
        
        for (const [name, cap] of Object.entries(capabilities)) {
            const card = createCard(name, cap);
            if (cap.status === 'ready') ready.push(card);
            else if (cap.status === 'config' || cap.local === 'partial') config.push(card);
            else if (!cap.local) cloud.push(card);
        }
        
        document.getElementById('local-grid').innerHTML = ready.join('');
        document.getElementById('config-grid').innerHTML = config.join('');
        document.getElementById('cloud-grid').innerHTML = cloud.join('');
        
        document.getElementById('ready-count').textContent = ready.length;
        document.getElementById('config-count').textContent = config.length;
        document.getElementById('cloud-count').textContent = cloud.length;
    }
    
    function createCard(name, cap) {
        const statusClass = cap.status === 'ready' ? 'ready' : cap.status === 'config' ? 'config' : 'cloud';
        const badgeClass = cap.local === true ? 'badge-local' : cap.local === 'partial' ? 'badge-config' : 'badge-cloud';
        const badgeText = cap.local === true ? '本地' : cap.local === 'partial' ? '部分' : '云端';
        
        let actions = '';
        if (cap.actions) {
            actions = '<div class="cap-actions">' + cap.actions.map(a => {
                if (a.cmd) return `<button class="btn orange" onclick="runCmd(this, '${a.cmd.replace(/'/g, "\\'")}')">${a.label}</button>`;
                if (a.url) return `<a href="${a.url}" target="_blank" class="btn blue">${a.label}</a>`;
                return '';
            }).join('') + '</div>';
        }
        
        return `
            <div class="cap-card ${statusClass}">
                <div class="cap-header">
                    <span class="cap-icon">${cap.icon}</span>
                    <span class="cap-name">${name}</span>
                    <span class="cap-badge ${badgeClass}">${badgeText}</span>
                </div>
                <div class="cap-desc">${cap.description}</div>
                <div class="cap-depends">依赖: ${cap.depends}</div>
                ${actions}
                <div class="terminal" onclick="event.stopPropagation()">
                    <span class="terminal-close" onclick="this.parentElement.classList.remove('show')">✕</span>
                    <div class="terminal-output"></div>
                </div>
            </div>
        `;
    }
    
    function runCmd(btn, cmd) {
        const terminal = btn.closest('.cap-card').querySelector('.terminal');
        const output = terminal.querySelector('.terminal-output');
        terminal.classList.add('show');
        output.textContent = '执行中...\n\n' + cmd + '\n\n---\n';
        
        fetch('/api/run', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({cmd})
        })
        .then(r => r.json())
        .then(data => {
            output.textContent += data.stdout || data.stderr || '完成';
        })
        .catch(e => {
            output.textContent += '错误: ' + e;
        });
    }
    
    renderCards();
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
            self.wfile.write(HTML.replace("CAPABILITIES", json.dumps(CAPABILITIES, ensure_ascii=False)).encode())
        elif self.path == '/api/status':
            status = check_status()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        elif self.path == '/api/capabilities':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(CAPABILITIES, ensure_ascii=False).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/run':
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length)
            data = json.loads(body)
            cmd = data.get('cmd', '')
            
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                response = {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
            except Exception as e:
                response = {"stdout": "", "stderr": str(e), "returncode": -1}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        pass

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ 能力应用集合已启动: http://localhost:{PORT}")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")

if __name__ == "__main__":
    run()
