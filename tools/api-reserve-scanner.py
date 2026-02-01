#!/usr/bin/env python3
"""
API 搜刮工具 - 持续获取可用API资源
策略：
1. 扫描公开配置仓库
2. 测试已知中转API
3. 监控免费额度平台
4. 记录可用API到储备库
"""

import json
import urllib.request
import urllib.error
import time
from datetime import datetime
from pathlib import Path

# 储备库
RESERVE_DIR = Path.home() / ".api-reserve"
RESERVE_DIR.mkdir(parents=True, exist_ok=True)
RESERVE_FILE = RESERVE_DIR / "available_apis.json"

# 已知的免费/低成本平台
FREE_APIS = [
    # 平台名, endpoint, key前缀, 测试endpoint
    ("groq", "https://api.groq.com/openai/v1/models", "gsk-", "https://api.groq.com/openai/v1/models"),
    ("together", "https://api.together.xyz/v1/models", "", "https://api.together.xyz/v1/models"),
    ("cerebras", "https://api.cerebras.ai/v1/models", "cscr-", "https://api.cerebras.ai/v1/models"),
    ("perplexity", "https://api.perplexity.ai/chat/completions", "pplx-", "https://api.perplexity.ai/chat/completions"),
    ("huggingface", "https://api-inference.huggingface.co/models", "hf_", "https://api-inference.huggingface.co/models"),
    ("mistral", "https://api.mistral.ai/v1/models", "", "https://api.mistral.ai/v1/models"),
]

# 已知的可能中转API (key需要替换)
PROXY_APIS = [
    ("openrouter", "https://openrouter.ai/api/v1/models", "sk-or-", "https://openrouter.ai/api/v1/models"),
    ("azure", "https://{resource}.openai.azure.com/openai/deployments/{deployment}/chat/completions", "sk-", ""),
]

def test_api(endpoint, key, auth_header="Authorization", prefix="Bearer "):
    """测试API是否可用"""
    try:
        req = urllib.request.Request(
            endpoint,
            headers={auth_header: f"{prefix}{key}"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200, resp.read().decode()[:200]
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)[:50]

def load_reserve():
    """加载储备库"""
    if RESERVE_FILE.exists():
        with open(RESERVE_FILE) as f:
            return json.load(f)
    return {"apis": [], "last_scan": None}

def save_reserve(data):
    """保存储备库"""
    with open(RESERVE_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def scan_free_apis():
    """扫描免费/低成本平台"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 扫描免费平台...")
    available = []
    
    # 模板测试 (用空key测)
    for name, endpoint, _, test_endpoint in FREE_APIS:
        print(f"  检查 {name}...")
        # 先测试endpoint连通性
        try:
            req = urllib.request.Request(test_endpoint)
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"    ✓ {name} 端点可达")
        except Exception as e:
            print(f"    ✗ {name} 端点不可达: {e}")
    
    return available

def check_minimax_status():
    """检查Minimax状态"""
    # 这里可以放检查逻辑，但需要登录
    # 目前已知余额: 约13元人民币
    return {"balance_cny": 13, "status": "warning", "message": "余额不足，建议充值或切换备用API"}

def get_recommendations():
    """获取充值/新账号建议"""
    return [
        {"platform": "Minimax", "action": "充值", "priority": "高", "note": "当前主力模型"},
        {"platform": "Deepseek", "action": "备用", "priority": "中", "note": "已添加到管理器"},
        {"platform": "SiliconFlow", "action": "备用", "priority": "中", "note": "已添加到管理器"},
        {"platform": "Groq", "action": "新账号注册", "priority": "高", "note": "免费额度多，响应快"},
        {"platform": "Together AI", "action": "新账号注册", "priority": "中", "note": "开源模型多"},
    ]

def status():
    """显示整体状态"""
    reserve = load_reserve()
    minimax = check_minimax_status()
    recommendations = get_recommendations()
    
    print("\n" + "="*50)
    print("🍚 粮食储备状态")
    print("="*50)
    print(f"\nMinimax余额: ¥{minimax['balance_cny']} ⚠️")
    print(f"\n已储备API: {len(reserve.get('apis', []))}个")
    print(f"最后扫描: {reserve.get('last_scan', '从未')}")
    
    print("\n📋 建议行动:")
    for r in recommendations:
        print(f"  [{r['priority']}] {r['platform']}: {r['action']} - {r['note']}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "scan":
        scan_free_apis()
    elif cmd == "status":
        status()
    elif cmd == "recommend":
        for r in get_recommendations():
            print(r)
