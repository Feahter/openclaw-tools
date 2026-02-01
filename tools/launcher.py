#!/usr/bin/env python3
"""
OpenClaw 工具箱桌面启动器
简洁的入口应用，管理所有工具的启动和状态
"""

# 检查 tkinter 是否可用，否则使用 CLI 版本
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False

if not HAS_TKINTER:
    print("⚠️ tkinter 不可用，使用 CLI 版本...")
    import subprocess
    import sys
    cli_script = __file__.replace("launcher.py", "launcher-cli.py")
    if __file__.endswith("launcher.py") and subprocess.run([sys.executable, cli_script]).returncode == 0:
        sys.exit(0)

import subprocess
import threading
import os
import time
import json
from datetime import datetime

# 配置
WORKSPACE = "/Users/fuzhuo/.openclaw/workspace/tools"
CONFIG_FILE = os.path.expanduser("~/.openclaw/tool-launcher.json")

# 工具配置
TOOLS = [
    {
        "name": "📋 快速任务",
        "desc": "简洁任务面板 - 快速添加/切换状态",
        "script": "quick-task-panel.py",
        "port": 8765,
        "url": "http://localhost:8765",
        "type": "web"
    },
    {
        "name": "🤖 模型管理",
        "desc": "Ollama 本地模型 + API Keys 管理",
        "script": "local-model-manager.py",
        "port": 8768,
        "url": "http://localhost:8768",
        "type": "web"
    },
    {
        "name": "📋 任务看板",
        "desc": "主动任务追踪、四列看板视图",
        "script": "task-board.py",
        "port": 8769,
        "url": "http://localhost:8769",
        "type": "web"
    },
    {
        "name": "🧠 能力集合",
        "desc": "Agent 所有能力一览 + 快速启用",
        "script": "capability-collector.py",
        "port": 8772,
        "url": "http://localhost:8772",
        "type": "web"
    },
    {
        "name": "📊 Token统计",
        "desc": "实时 API 消耗监控和成本统计",
        "script": "token-stats.py",
        "port": 8770,
        "url": "http://localhost:8770",
        "type": "web"
    },
    {
        "name": "⚡ 自动化工作流",
        "desc": "并行任务执行和批量操作",
        "script": "automation-workflow.py",
        "port": 8771,
        "url": "http://localhost:8771",
        "type": "web"
    },
    {
        "name": "🚀 并发任务",
        "desc": "分身术系统 - 高效并发执行多个任务",
        "script": "concurrent-task-manager.py",
        "port": 8780,
        "url": "http://localhost:8780",
        "type": "web"
    },
    {
        "name": "🔑 API Key 管理",
        "desc": "多 Provider API Keys 管理",
        "script": "api-key-manager.py",
        "type": "cli",
        "params": ["list"]
    },
    {
        "name": "🔄 自动切换",
        "desc": "API 余额不足自动切换备用 Key",
        "script": "api-auto-switch.py",
        "type": "cli",
        "params": ["monitor"]
    },
    {
        "name": "🔍 API 扫描",
        "desc": "扫描收集免费/廉价 API",
        "script": "api-reserve-scanner.py",
        "type": "cli"
    },
]

class ToolLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔧 OpenClaw 工具箱")
        self.root.geometry("500x650")
        self.root.configure(bg="#1a1a2e")
        
        # 进程管理
        self.processes = {}
        self.running_ports = set()
        
        # 加载配置
        self.load_config()
        
        # 创建界面
        self.create_ui()
        
        # 启动状态检测
        self.check_status()
        
    def load_config(self):
        """加载保存的配置"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.running_ports = set(config.get('running_ports', []))
        except:
            pass
            
    def save_config(self):
        """保存配置"""
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    'running_ports': list(self.running_ports),
                    'last_updated': datetime.now().isoformat()
                }, f)
        except:
            pass
        
    def create_ui(self):
        # 标题
        title_frame = tk.Frame(self.root, bg="#1a1a2e")
        title_frame.pack(pady=20)
        
        tk.Label(title_frame, text="🔧 OpenClaw 工具箱", 
                font=("SF Pro Display", 24, "bold"),
                bg="#1a1a2e", fg="#00d9ff").pack()
        
        tk.Label(title_frame, text="集成开发与管理工具集合",
                font=("SF Pro Display", 11),
                bg="#1a1a2e", fg="#888").pack()
        
        # 快捷操作栏
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(pady=15, padx=20, fill="x")
        
        self.create_button(btn_frame, "🚀 启动全部 Web", self.start_all_web, "#00c853").pack(side="left", expand=True, fill="x", padx=2)
        self.create_button(btn_frame, "🔍 刷新状态", self.check_status, "#0f3460").pack(side="left", expand=True, fill="x", padx=2)
        self.create_button(btn_frame, "📁 打开目录", self.open_folder, "#0f3460").pack(side="left", expand=True, fill="x", padx=2)
        
        # 工具列表
        list_frame = tk.Frame(self.root, bg="#16213e")
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas = tk.Canvas(list_frame, bg="#16213e", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=scrollbar.set)
        
        inner_frame = tk.Frame(self.canvas, bg="#16213e")
        self.canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # 创建工具卡片
        self.tool_widgets = []
        for i, tool in enumerate(TOOLS):
            card = self.create_tool_card(inner_frame, tool, i)
            card.pack(fill="x", pady=8, padx=5)
            self.tool_widgets.append(card)
        
        # 底部状态栏
        status_frame = tk.Frame(self.root, bg="#0f3460", height=30)
        status_frame.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(status_frame, text="就绪", 
                                    bg="#0f3460", fg="#888", font=("SF Pro Display", 9))
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # 点击链接打开网页
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
    def create_button(self, parent, text, command, bg="#0f3460"):
        """创建统一风格的按钮"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg, fg="#fff", font=("SF Pro Display", 10),
                       borderwidth=0, highlightthickness=0,
                       activebackground="#1a4a7a", activeforeground="#fff",
                       cursor="hand2", pady=8)
        return btn
        
    def create_tool_card(self, parent, tool, index):
        """创建工具卡片"""
        card = tk.Frame(parent, bg="rgba(255,255,255,0.05)", 
                       highlightthickness=1, highlightbackground="rgba(255,255,255,0.1)")
        
        # 状态指示灯
        status_indicator = tk.Frame(card, bg="#16213e", width=8)
        status_indicator.pack(side="left", fill="y")
        status_indicator.config(bg=self.get_status_color(tool.get("port")))
        
        # 内容区
        content = tk.Frame(card, bg="#16213e", padx=15, pady=12)
        content.pack(side="left", fill="both", expand=True)
        
        # 名称和类型
        header = tk.Frame(content, bg="#16213e")
        header.pack(fill="x")
        
        tk.Label(header, text=tool["name"], font=("SF Pro Display", 14, "bold"),
                bg="#16213e", fg="#fff").pack(side="left")
        
        type_label = tk.Label(header, text=tool["type"].upper(), 
                             font=("SF Pro Display", 8), bg="#0f3460", fg="#888")
        type_label.pack(side="right", padx=5)
        
        # 描述
        tk.Label(content, text=tool["desc"], font=("SF Pro Display", 10),
                bg="#16213e", fg="#888").pack(anchor="w", pady=5)
        
        # 端口/链接
        if tool.get("url"):
            tk.Label(content, text=tool["url"], font=("SF Pro Display", 9),
                    bg="#16213e", fg="#00d9ff").pack(anchor="w")
        
        # 按钮行
        btn_row = tk.Frame(content, bg="#16213e")
        btn_row.pack(fill="x", pady=10)
        
        if tool["type"] == "web":
            self.create_button(btn_row, "▶ 启动", lambda: self.start_tool(tool)).pack(side="left", padx=2)
            self.create_button(btn_row, "🛑 停止", lambda: self.stop_tool(tool), "#c62828").pack(side="left", padx=2)
            if tool.get("url"):
                self.create_button(btn_row, "🌐 打开", lambda: self.open_url(tool["url"]), "#0f3460").pack(side="left", padx=2)
        else:
            self.create_button(btn_row, "▶ 运行", lambda: self.run_cli(tool)).pack(side="left", expand=True, fill="x", padx=2)
        
        # 保存引用用于更新状态
        card.status_indicator = status_indicator
        card.tool = tool
        
        return card
        
    def get_status_color(self, port):
        """获取状态颜色"""
        if port and port in self.running_ports:
            return "#00c853"  # 绿色 - 运行中
        return "#444"  # 灰色 - 未运行
        
    def check_status(self):
        """检测所有 Web 服务状态"""
        import socket
        
        for i, tool in enumerate(TOOLS):
            port = tool.get("port")
            if port:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    sock.close()
                    
                    if result == 0:
                        self.running_ports.add(port)
                    else:
                        self.running_ports.discard(port)
                except:
                    self.running_ports.discard(port)
        
        # 更新卡片状态
        for i, widget in enumerate(self.tool_widgets):
            port = TOOLS[i].get("port")
            color = self.get_status_color(port)
            widget.status_indicator.config(bg=color)
        
        self.save_config()
        
        # 更新状态栏
        running_count = len([p for p in self.running_ports])
        self.status_label.config(text=f"运行中: {running_count} 个服务 | 工具总数: {len(TOOLS)}")
        
        # 5秒后再次检测
        self.root.after(5000, self.check_status)
        
    def start_tool(self, tool):
        """启动单个工具"""
        def run():
            try:
                self.update_status(f"正在启动 {tool['name']}...")
                cmd = ["python3", tool["script"]]
                if tool.get("params"):
                    cmd.extend(tool["params"])
                
                proc = subprocess.Popen(cmd, cwd=WORKSPACE, 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE)
                self.processes[tool["script"]] = proc
                
                # 等待服务启动
                time.sleep(2)
                self.check_status()
                self.update_status(f"✅ {tool['name']} 已启动")
            except Exception as e:
                self.update_status(f"❌ 启动失败: {e}")
                
        threading.Thread(target=run, daemon=True).start()
        
    def stop_tool(self, tool):
        """停止工具"""
        script = tool["script"]
        if script in self.processes:
            self.processes[script].terminate()
            del self.processes[script]
            self.running_ports.discard(tool.get("port"))
            self.check_status()
            self.update_status(f"已停止 {tool['name']}")
        else:
            messagebox.showinfo("提示", f"{tool['name']} 未运行")
            
    def start_all_web(self):
        """启动所有 Web 服务"""
        for tool in TOOLS:
            if tool["type"] == "web" and tool.get("port") not in self.running_ports:
                self.start_tool(tool)
        self.update_status("正在启动所有 Web 服务...")
        
    def run_cli(self, tool):
        """运行 CLI 工具（打开终端窗口）"""
        try:
            cmd = f"cd {WORKSPACE} && python3 {tool['script']}"
            if tool.get("params"):
                cmd += " " + " ".join(tool["params"])
            
            # macOS 上用 osascript 打开终端
            apple_script = f'''
            tell application "Terminal"
                do script "{cmd}"
                activate
            end tell
            '''
            subprocess.run(["osascript", "-e", apple_script], check=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法启动终端: {e}")
            
    def open_url(self, url):
        """打开 URL"""
        import webbrowser
        webbrowser.open(url)
        
    def open_folder(self):
        """打开工具目录"""
        import subprocess
        subprocess.run(["open", WORKSPACE])
        
    def update_status(self, text):
        """更新状态栏"""
        self.status_label.config(text=text)
        
    def on_canvas_click(self, event):
        """处理点击事件"""
        # 暂时不使用，保留扩展
        pass
        
    def run(self):
        self.root.mainloop()

def main():
    app = ToolLauncher()
    app.run()

if __name__ == "__main__":
    main()



# === Token 自动记录集成 ===
import subprocess
import json
from datetime import datetime

TOKEN_MONITOR = "/Users/fuzhuo/.openclaw/workspace/tools/token-monitor.py"

def log_api_call(provider, model, prompt_tokens, completion_tokens, cost=0, session_key=None):
    """记录 API 调用"""
    try:
        cmd = [
            "python3", TOKEN_MONITOR, "log",
            provider, model,
            str(prompt_tokens), str(completion_tokens),
            str(cost)
        ]
        if session_key:
            cmd.append(session_key)
        subprocess.run(cmd, capture_output=True)
    except:
        pass  # 静默失败，不影响主流程

def check_and_optimize_context(messages, session_key=None):
    """检查上下文，必要时优化"""
    try:
        result = subprocess.run(
            ["python3", TOKEN_MONITOR, "check"],
            capture_output=True, text=True
        )
        return result.stdout
    except:
        return ""

def get_usage_report(hours=24):
    """获取消耗报告"""
    try:
        result = subprocess.run(
            ["python3", TOKEN_MONITOR, "recent", str(hours)],
            capture_output=True, text=True
        )
        return result.stdout
    except:
        return ""
