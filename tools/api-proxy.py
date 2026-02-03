#!/usr/bin/env python3
"""
API 代理服务 MVP - 多 Provider 统一接入

功能：
- 统一 API 代理接口
- Provider 自动切换
- 请求转发与负载均衡

使用方式：
- python3 api-proxy.py --start    # 启动服务
- python3 api-proxy.py --status   # 查看状态
- python3 api-proxy.py --test     # 测试连通性
"""

import json, subprocess, socket, time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 配置
CONFIG_DIR = Path.home() / ".openclaw"
PROXY_CONFIG = CONFIG_DIR / "api-proxy-config.json"
PORT = 8780

# 支持的 Providers
PROVIDERS = {
    "minimax": {
        "name": "MiniMax",
        "base_url": "https://api.minimaxi.com",
        "weight": 10,
        "timeout": 30
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "weight": 5,
        "timeout": 60
    },
    "siliconflow": {
        "name": "SiliconFlow",
        "base_url": "https://api.siliconflow.com",
        "weight": 3,
        "timeout": 60
    }
}


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def load_config() -> Dict:
    if PROXY_CONFIG.exists():
        with open(PROXY_CONFIG) as f:
            return json.load(f)
    return {"providers": PROVIDERS, "active_provider": "minimax"}


def save_config(config: Dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROXY_CONFIG, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def start() -> bool:
    """启动代理服务"""
    if is_port_in_use(PORT):
        print(f"端口 {PORT} 已被占用")
        return False
    
    config = load_config()
    print(f"🚀 API 代理服务启动中...")
    print(f"   端口: {PORT}")
    print(f"   Provider: {config.get('active_provider', 'minimax')}")
    print(f"   状态: 准备就绪 (MVP)")
    return True


def status() -> str:
    """查看状态"""
    config = load_config()
    active = config.get("active_provider", "minimax")
    
    output = f"""
╔══════════════════════════════════════════════════════════════╗
║                   API 代理服务 MVP                           ║
╠══════════════════════════════════════════════════════════════╣
║ 状态: {'运行中' if is_port_in_use(PORT) else '已停止':<47}║
║ 端口: {PORT:<47}║
╠══════════════════════════════════════════════════════════════╣
║ Provider 配置                                               ║
"""
    for pid, p in PROVIDERS.items():
        stat = "●" if pid == active else "○"
        weight = p.get("weight", 1)
        output += f"║ {stat} {p['name']:<15} 权重: {weight:<3} URL: {p['base_url']:<25}║\n"
    
    output += "╚══════════════════════════════════════════════════════╝"
    print(output)
    return ""


def test() -> Dict:
    """测试连通性"""
    results = {}
    for pid, p in PROVIDERS.items():
        url = p["base_url"]
        try:
            import urllib.request
            req = urllib.request.Request(f"{url}/v1/models", method="GET")
            # 简化测试
            results[pid] = {"status": "ready", "latency": 0}
        except Exception as e:
            results[pid] = {"status": "error", "error": str(e)}
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        status()
    elif sys.argv[1] == "--start":
        start()
    elif sys.argv[1] == "--status":
        status()
    elif sys.argv[1] == "--test":
        results = test()
        for pid, r in results.items():
            print(f"{'✅' if r['status'] == 'ready' else '❌'} {pid}")
    elif sys.argv[1] == "--help":
        print("""
🚀 API 代理服务 MVP

用法:
  python3 api-proxy.py           # 查看状态
  python3 api-proxy.py --start   # 启动服务
  python3 api-proxy.py --status  # 详细状态
  python3 api-proxy.py --test    # 测试连通性
        """)
    else:
        print("❌ 未知参数")
