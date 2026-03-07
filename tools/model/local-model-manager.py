#!/usr/bin/env python3
"""
本地模型 + API Key 管理工具 (macOS桌面版)
功能：
- 查看ollama模型列表和状态
- 管理多API Key
- 快速切换/测试
- 用量统计
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
import http.server
import socketserver
import webbrowser
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import threading

CONFIG_DIR = Path.home() / ".api-keys"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

KEYS_FILE = CONFIG_DIR / "keys.json"
USAGE_FILE = CONFIG_DIR / "usage.json"
PORT = 8768

# 今日日期
TODAY = datetime.now().strftime('%Y-%m-%d')

# 预设Provider配置
PROVIDERS = {
    "openai": {"endpoint": "https://api.openai.com/v1", "key_prefix": "sk-"},
    "anthropic": {"endpoint": "https://api.anthropic.com/v1", "key_prefix": "sk-ant-api03-"},
    "google": {"endpoint": "https://generativelanguage.googleapis.com/v1beta", "key_prefix": "AIza"},
    "deepseek": {"endpoint": "https://api.deepseek.com/v1", "key_prefix": "sk-"},
    "ollama": {"endpoint": "http://localhost:11434", "key_prefix": "", "local": True},
    "opencode": {"endpoint": "https://api.opencode.ai/v1", "key_prefix": ""},
    "groq": {"endpoint": "https://api.groq.com/openai/v1", "key_prefix": "gsk-"},
    "together": {"endpoint": "https://api.together.xyz/v1", "key_prefix": ""},
    "cerebras": {"endpoint": "https://api.cerebras.ai/v1", "key_prefix": "cscr-"},
    "huggingface": {"endpoint": "https://api-inference.huggingface.co", "key_prefix": "hf_"},
    "perplexity": {"endpoint": "https://api.perplexity.ai", "key_prefix": "pplx-"},
    "mistral": {"endpoint": "https://api.mistral.ai/v1", "key_prefix": ""},
    "zhipu": {"endpoint": "https://open.bigmodel.cn/api/paas/v4", "key_prefix": ""},
    "dashscope": {"endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1", "key_prefix": "sk-"},
    "siliconflow": {"endpoint": "https://api.siliconflow.cn/v1", "key_prefix": "sk-"},
}

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API & 模型管理器</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #eee; min-height: 100vh; padding: 20px; }
        h1 { color: #00d9ff; margin-bottom: 8px; font-size: 1.8em; display: flex; align-items: center; gap: 10px; }
        .subtitle { color: #888; margin-bottom: 20px; font-size: 0.9em; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }
        .card { background: rgba(22, 33, 62, 0.8); backdrop-filter: blur(10px); 
                border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        h2 { color: #ff6b6b; font-size: 1.1em; display: flex; align-items: center; gap: 8px; }
        .badge { background: #e94560; color: #fff; font-size: 0.7em; padding: 2px 8px; border-radius: 10px; }
        
        /* 模型卡片 */
        .model-item { display: flex; justify-content: space-between; align-items: center;
                      padding: 12px 15px; background: rgba(15, 52, 96, 0.6); 
                      margin: 8px 0; border-radius: 10px; transition: all 0.2s; border: 1px solid transparent; }
        .model-item:hover { background: rgba(15, 52, 96, 0.9); border-color: rgba(0, 217, 255, 0.3); transform: translateX(5px); }
        .model-info { flex: 1; }
        .model-name { font-weight: 600; color: #00d9ff; font-size: 1em; }
        .model-meta { color: #666; font-size: 0.85em; margin-top: 4px; display: flex; gap: 15px; }
        .model-actions { display: flex; gap: 8px; }
        .status { padding: 4px 12px; border-radius: 20px; font-size: 0.75em; font-weight: 500; }
        .status.ok { background: linear-gradient(135deg, #00c853, #00e676); color: #fff; box-shadow: 0 2px 10px rgba(0,200,83,0.3); }
        .status.pull { background: linear-gradient(135deg, #ff9800, #ffb74d); color: #fff; animation: pulse 1.5s infinite; }
        .status.err { background: linear-gradient(135deg, #ff1744, #ff5252); color: #fff; }
        
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        
        /* 按钮 */
        .btn { background: #e94560; color: #fff; border: none; padding: 6px 14px; 
               border-radius: 6px; cursor: pointer; font-size: 0.85em; transition: all 0.2s; }
        .btn:hover { background: #ff6b6b; transform: scale(1.05); }
        .btn.green { background: linear-gradient(135deg, #00c853, #00e676); color: #fff; }
        .btn.green:hover { background: linear-gradient(135deg, #00e676, #69f0ae); }
        .btn.small { padding: 4px 10px; font-size: 0.8em; }
        .btn.danger { background: linear-gradient(135deg, #ff1744, #ff5252); }
        
        /* 表单 */
        .form { display: flex; gap: 10px; margin: 15px 0; flex-wrap: wrap; }
        input, select { padding: 12px 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); 
                        background: rgba(15, 52, 96, 0.6); color: #fff; flex: 1; min-width: 150px; transition: all 0.2s; }
        input:focus, select:focus { outline: none; border-color: #00d9ff; background: rgba(15, 52, 96, 0.9); }
        input::placeholder { color: #666; }
        
        /* 统计卡片 */
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 15px 0; }
        .stat { background: rgba(15, 52, 96, 0.6); padding: 15px; border-radius: 10px; text-align: center; transition: all 0.2s; }
        .stat:hover { background: rgba(15, 52, 96, 0.9); transform: translateY(-3px); }
        .stat-num { font-size: 1.6em; font-weight: bold; background: linear-gradient(135deg, #00d9ff, #00c853); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .stat-label { color: #888; font-size: 0.8em; margin-top: 5px; text-transform: uppercase; letter-spacing: 1px; }
        
        /* Keys */
        .key-item { display: flex; justify-content: space-between; align-items: center;
                    padding: 12px 15px; background: rgba(15, 52, 96, 0.6); 
                    margin: 8px 0; border-radius: 10px; transition: all 0.2s; }
        .key-item:hover { background: rgba(15, 52, 96, 0.9); }
        .key-info { flex: 1; }
        .key-name { color: #00d9ff; font-weight: 500; }
        .key-preview { color: #666; font-family: 'SF Mono', Monaco, monospace; font-size: 0.85em; margin-top: 4px; }
        .key-actions { display: flex; gap: 8px; }
        
        /* 搜索框 */
        .search-box { position: relative; margin-bottom: 15px; }
        .search-box input { padding-left: 40px; }
        .search-icon { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: #666; }
        
        /* 通知 */
        .toast { position: fixed; bottom: 20px; right: 20px; background: #00c853; color: #fff; 
                 padding: 12px 20px; border-radius: 8px; opacity: 0; transform: translateY(20px); 
                 transition: all 0.3s; z-index: 1000; }
        .toast.show { opacity: 1; transform: translateY(0); }
        .toast.error { background: #ff1744; }
        
        /* 加载动画 */
        .loading { display: inline-block; width: 16px; height: 16px; border: 2px solid #333; 
                   border-top-color: #00d9ff; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        /* 空状态 */
        .empty { text-align: center; color: #666; padding: 30px; }
        .empty-icon { font-size: 3em; margin-bottom: 10px; opacity: 0.5; }
        
        /* 响应式 */
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            .form { flex-direction: column; }
            .stats { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <h1>🔑 API & 模型管理器</h1>
    <div class="subtitle">本地模型 + API Keys 一站式管理</div>
    
    <div class="grid">
        <div class="card">
            <div class="card-header">
                <h2>🤖 本地模型 <span class="badge" id="modelCount">0</span></h2>
                <button class="btn small" onclick="refreshModels()">刷新</button>
            </div>
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="modelSearch" placeholder="搜索模型..." oninput="renderModels()">
            </div>
            <div id="models">加载中...</div>
            <div class="form">
                <input type="text" id="modelName" placeholder="模型名如: qwen2.5:7b">
                <button class="btn green" onclick="pullModel()">下载</button>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2>📊 统计概览</h2>
            </div>
            <div class="stats">
                <div class="stat"><div class="stat-num" id="statKeys">0</div><div class="stat-label">API Keys</div></div>
                <div class="stat"><div class="stat-num" id="statModels">0</div><div class="stat-label">本地模型</div></div>
                <div class="stat"><div class="stat-num" id="statRunning">0</div><div class="stat-label">运行中</div></div>
            </div>
            <div style="margin-top: 20px;">
                <h2 style="font-size: 1em; margin-bottom: 10px;">💡 快捷建议</h2>
                <div id="suggestions" style="color: #888; font-size: 0.9em; line-height: 1.8;"></div>
            </div>
        </div>
    </div>
    
    <div class="card" style="margin-top: 20px;">
        <div class="card-header">
            <h2>🔐 API Keys <span class="badge" id="keyCount">0</span></h2>
        </div>
        <div class="form">
            <select id="provider">
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="google">Google</option>
                <option value="deepseek">DeepSeek</option>
                <option value="opencode">OpenCode</option>
                <option value="groq">Groq</option>
                <option value="together">TogetherAI</option>
                <option value="cerebras">Cerebras</option>
                <option value="huggingface">HuggingFace</option>
                <option value="perplexity">Perplexity</option>
                <option value="mistral">Mistral</option>
                <option value="zhipu">智谱 AI</option>
                <option value="dashscope">阿里通义</option>
                <option value="siliconflow">SiliconFlow</option>
            </select>
            <input type="text" id="apiKey" placeholder="sk-...">
            <input type="text" id="keyName" placeholder="名称(可选)">
            <button class="btn green" onclick="addKey()">添加</button>
        </div>
        <div id="keys">加载中...</div>
    </div>
    
    <div id="toast" class="toast"></div>
    
    <script>
        let models = [];
        let keys = [];
        let pullingModels = new Set();
        
        async function load() {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 5000);
                const res = await fetch('/api/status', { signal: controller.signal });
                clearTimeout(timeoutId);
                const data = await res.json();
                models = data.models || [];
                keys = data.keys || [];
                window.usageData = data.usage || {};
                render();
            } catch (e) {
                if (e.name !== 'AbortError') {
                    console.error('加载失败:', e);
                }
            }
        }
        
        function render() {
            renderModels();
            renderKeys();
            updateStats();
            updateSuggestions();
        }
        
        function updateStats() {
            document.getElementById('statModels').textContent = models.length;
            document.getElementById('statRunning').textContent = models.filter(m => m.running).length;
            
            // 用量统计
            if (window.usageData) {
                document.getElementById('statReqs').textContent = window.usageData.requests || 0;
                document.getElementById('statTokens').textContent = formatNumber(window.usageData.tokens || 0);
                document.getElementById('statCost').textContent = '$' + (window.usageData.cost || 0).toFixed(2);
            }
        }
        
        function formatNumber(num) {
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num;
        }
        
        function renderModels() {
            const search = document.getElementById('modelSearch').value.toLowerCase();
            const filtered = models.filter(m => m.name.toLowerCase().includes(search));
            
            if (filtered.length === 0) {
                document.getElementById('models').innerHTML = '<div class="empty"><div class="empty-icon">📦</div>暂无模型<br><small>下载一个试试</small></div>';
            } else {
                document.getElementById('models').innerHTML = filtered.map(m => `
                    <div class="model-item">
                        <div class="model-info">
                            <div class="model-name">${escapeHtml(m.name)}</div>
                            <div class="model-meta">
                                <span>📦 ${formatSize(m.size)}</span>
                                ${m.pullProgress !== undefined ? `<span>📥 ${m.pullProgress}%</span>` : ''}
                            </div>
                        </div>
                        <div class="model-actions">
                            ${pullingModels.has(m.name) 
                                ? `<span class="status pull">下载中...</span>`
                                : `<span class="status ${m.running ? 'ok' : 'err'}">${m.running ? '运行中' : '已停止'}</span>`
                            }
                            ${!m.running ? `<button class="btn small green" onclick="startModel('${escapeHtml(m.name)}')">启动</button>` : ''}
                            <button class="btn small danger" onclick="deleteModel('${escapeHtml(m.name)}')">删除</button>
                        </div>
                    </div>
                `).join('');
            }
            document.getElementById('modelCount').textContent = models.length;
        }
        
        function renderKeys() {
            if (keys.length === 0) {
                document.getElementById('keys').innerHTML = '<div class="empty"><div class="empty-icon">🔑</div>暂无API Keys<br><small>添加一个开始使用</small></div>';
            } else {
                document.getElementById('keys').innerHTML = keys.map(k => `
                    <div class="key-item">
                        <div class="key-info">
                            <div class="key-name">${escapeHtml(k.provider)} - ${escapeHtml(k.name || '默认')}</div>
                            <div class="key-preview">${escapeHtml(k.key.slice(0,12))}${k.key.length > 12 ? '...' : ''}</div>
                        </div>
                        <div class="key-actions">
                            <button class="btn small" onclick="copyKey('${escapeHtml(k.key)}')">复制</button>
                            <button class="btn small" onclick="testKey('${escapeHtml(k.provider)}', '${escapeHtml(k.key)}')">测试</button>
                            <button class="btn small danger" onclick="removeKey('${escapeHtml(k.provider)}', '${escapeHtml(k.name)}')">删除</button>
                        </div>
                    </div>
                `).join('');
            }
            document.getElementById('keyCount').textContent = keys.length;
            document.getElementById('statKeys').textContent = keys.length;
        }
        
        function updateSuggestions() {
            const suggestions = [];
            if (models.length === 0) {
                suggestions.push('• 下载一个本地模型开始使用');
            }
            if (keys.length === 0) {
                suggestions.push('• 添加 API Key 启用云端模型');
            }
            if (models.filter(m => m.running).length === 0 && models.length > 0) {
                suggestions.push('• 启动本地模型开始对话');
            }
            if (suggestions.length === 0) {
                suggestions.push('✓ 所有功能就绪！');
            }
            document.getElementById('suggestions').innerHTML = suggestions.join('<br>');
        }
        
        function formatSize(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB';
            if (bytes < 1024*1024*1024) return (bytes/(1024*1024)).toFixed(1) + ' MB';
            return (bytes/(1024*1024*1024)).toFixed(1) + ' GB';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function showToast(msg, isError = false) {
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.className = 'toast' + (isError ? ' error' : '');
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }
        
        async function pullModel() {
            const name = document.getElementById('modelName').value.trim();
            if (!name) {
                showToast('请输入模型名称', true);
                return;
            }
            pullingModels.add(name);
            renderModels();
            showToast('开始下载: ' + name);
            
            try {
                await fetch('/api/ollama/pull', {
                    method: 'POST', body: JSON.stringify({name})
                });
                document.getElementById('modelName').value = '';
            } catch (e) {
                showToast('下载失败: ' + e.message, true);
            }
            pullingModels.delete(name);
            load();
        }
        
        async function startModel(name) {
            showToast('启动中: ' + name);
            await fetch('/api/ollama/start', {
                method: 'POST', body: JSON.stringify({name})
            });
            load();
        }
        
        async function deleteModel(name) {
            if (!confirm('确定删除模型 ' + name + '?')) return;
            showToast('删除中: ' + name);
            await fetch('/api/ollama/delete', {
                method: 'POST', body: JSON.stringify({name})
            });
            load();
        }
        
        async function addKey() {
            const provider = document.getElementById('provider').value;
            const key = document.getElementById('apiKey').value.trim();
            const name = document.getElementById('keyName').value.trim() || provider;
            
            if (!key) {
                showToast('请输入 API Key', true);
                return;
            }
            
            await fetch('/api/key/add', {
                method: 'POST', body: JSON.stringify({provider, key, name})
            });
            document.getElementById('apiKey').value = '';
            showToast('添加成功: ' + provider);
            load();
        }
        
        async function removeKey(provider, name) {
            if (!confirm('确定删除 ' + provider + ' - ' + name + '?')) return;
            await fetch('/api/key/remove', {
                method: 'POST', body: JSON.stringify({provider, name})
            });
            showToast('已删除');
            load();
        }
        
        async function testKey(provider, key) {
            showToast('测试中...');
            try {
                const res = await fetch('/api/key/test?' + new URLSearchParams({provider, key}));
                const data = await res.json();
                showToast(data.ok ? '✓ 可用' : '✗ 不可用', !data.ok);
            } catch (e) {
                showToast('测试失败: ' + e.message, true);
            }
        }
        
        function copyKey(key) {
            navigator.clipboard.writeText(key);
            showToast('已复制到剪贴板');
        }
        
        async function refreshModels() {
            showToast('刷新中...');
            load();
        }
        
        load();
        setInterval(load, 5000);
    </script>
</body>
</html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/status':
            self.send_json(self.get_status())
        elif self.path == '/api/keys':
            self.send_json(self.get_keys())
        elif self.path.startswith('/api/key/test'):
            self.handle_key_test()
        elif self.path == '/api/health':
            self.send_json({'status': 'ok', 'service': 'local-model-manager'})
        elif self.path == '/':
            self.send_html(HTML)
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/ollama/pull':
            self.handle_ollama_pull()
        elif self.path == '/api/ollama/start':
            self.handle_ollama_start()
        elif self.path == '/api/ollama/delete':
            self.handle_ollama_delete()
        elif self.path == '/api/key/add':
            self.handle_key_add()
        elif self.path == '/api/key/remove':
            self.handle_key_remove()
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
    
    def get_status(self):
        # Ollama模型
        models = []
        try:
            req = Request('http://localhost:11434/api/tags')
            with urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                for m in data.get('models', []):
                    models.append({
                        'name': m['name'],
                        'size': m['size'],
                        'running': True
                    })
        except:
            pass
        
        # Keys
        keys = []
        if KEYS_FILE.exists():
            with open(KEYS_FILE) as f:
                data = json.load(f)
                for provider, klist in data.items():
                    for k in klist:
                        keys.append({
                            'provider': provider,
                            'name': k.get('name', ''),
                            'key': k.get('key', ''),
                            'active': k.get('active', True)
                        })
        
        # 用量统计
        usage = self.get_usage()
        
        return {'models': models, 'keys': keys, 'usage': usage}
    
    def get_usage(self):
        """获取今日用量统计"""
        usage = {'requests': 0, 'tokens': 0, 'cost': 0}
        if USAGE_FILE.exists():
            try:
                with open(USAGE_FILE) as f:
                    data = json.load(f)
                    today = data.get(TODAY, {})
                    usage['requests'] = today.get('requests', 0)
                    usage['tokens'] = today.get('tokens', 0)
                    usage['cost'] = today.get('cost', 0)
            except:
                pass
        return usage
    
    def log_usage(self, tokens=0, cost=0):
        """记录用量"""
        data = {}
        if USAGE_FILE.exists():
            try:
                with open(USAGE_FILE) as f:
                    data = json.load(f)
            except:
                pass
        
        if TODAY not in data:
            data[TODAY] = {'requests': 0, 'tokens': 0, 'cost': 0}
        
        data[TODAY]['requests'] = data[TODAY].get('requests', 0) + 1
        data[TODAY]['tokens'] = data[TODAY].get('tokens', 0) + tokens
        data[TODAY]['cost'] = data[TODAY].get('cost', 0) + cost
        
        with open(USAGE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def handle_ollama_pull(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        name = data.get('name', '')
        if name:
            subprocess.Popen(['ollama', 'pull', name], stdout=subprocess.DEVNULL)
        self.send_json({'ok': True})
    
    def handle_key_add(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        keys = {}
        if KEYS_FILE.exists():
            with open(KEYS_FILE) as f:
                keys = json.load(f)
        
        provider = data['provider']
        if provider not in keys:
            keys[provider] = []
        keys[provider].append({
            'key': data['key'],
            'name': data['name'],
            'added': datetime.now().isoformat(),
            'active': True
        })
        
        with open(KEYS_FILE, 'w') as f:
            json.dump(keys, f, indent=2)
        self.send_json({'ok': True})
    
    def handle_key_remove(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        keys = {}
        if KEYS_FILE.exists():
            with open(KEYS_FILE) as f:
                keys = json.load(f)
        
        provider = data['provider']
        name = data['name']
        if provider in keys:
            keys[provider] = [k for k in keys[provider] if k.get('name') != name]
            with open(KEYS_FILE, 'w') as f:
                json.dump(keys, f, indent=2)
        self.send_json({'ok': True})
    
    def handle_key_test(self):
        from urllib.parse import parse_qs
        params = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
        provider = params.get('provider', [''])[0]
        key = params.get('key', [''])[0]
        
        if provider in PROVIDERS:
            p = PROVIDERS[provider]
            cmd = p.get('test_cmd', '').format(key=key, endpoint=p['endpoint'])
            try:
                result = subprocess.run(cmd.split()[:5], capture_output=True, timeout=5)
                self.send_json({'ok': result.returncode == 0})
            except:
                self.send_json({'ok': False})
        else:
            self.send_json({'ok': False})
    
    def handle_ollama_start(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        name = data.get('name', '')
        if name:
            subprocess.Popen(['ollama', 'run', name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.send_json({'ok': True})
    
    def handle_ollama_delete(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        name = data.get('name', '')
        if name:
            subprocess.run(['ollama', 'rm', name], capture_output=True)
        self.send_json({'ok': True})

def run():
    # 启动统一控制台
    console_script = Path(__file__).parent / "unified-console.py"
    if console_script.exists():
        subprocess.Popen(['python3', str(console_script)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ 统一控制台已启动: http://localhost:8765")

    # 启动任务看板
    task_board_script = Path(__file__).parent / "task-board.py"
    if task_board_script.exists():
        subprocess.Popen(['python3', str(task_board_script)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ 任务看板已启动: http://localhost:8769")

    # 启动 Token 统计
    token_stats_script = Path(__file__).parent / "token-stats.py"
    if token_stats_script.exists():
        subprocess.Popen(['python3', str(token_stats_script)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ Token 统计已启动: http://localhost:8770")

    # 启动自动化工作流
    workflow_script = Path(__file__).parent / "automation-workflow.py"
    if workflow_script.exists():
        subprocess.Popen(['python3', str(workflow_script)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ 自动化工作流已启动: http://localhost:8771")

    # 启动 API 自动切换监控
    auto_switch_script = Path(__file__).parent / "api-auto-switch.py"
    if auto_switch_script.exists():
        subprocess.Popen(['python3', str(auto_switch_script), 'monitor'],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ API 自动切换已启动")

    # 启动模型管理
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✓ 工具已启动: http://localhost:{PORT}")
        print("按 Ctrl+C 停止")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")

if __name__ == "__main__":
    run()
