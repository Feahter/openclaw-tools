#!/usr/bin/env python3
"""
API Key Manager - 本地API密钥管理工具
支持多Provider、用量追踪、自动切换
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

CONFIG_DIR = Path.home() / ".api-keys"
KEYS_FILE = CONFIG_DIR / "keys.json"
USAGE_FILE = CONFIG_DIR / "usage.json"

# Provider配置模板
PROVIDERS = {
    "openai": {
        "endpoint": "https://api.openai.com/v1",
        "key_prefix": "sk-",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "anthropic": {
        "endpoint": "https://api.anthropic.com/v1",
        "key_prefix": "sk-ant-api03-",
        "test_cmd": 'curl -s -H "x-api-key: {key}" {endpoint}/models | head -c 100'
    },
    "google": {
        "endpoint": "https://generativelanguage.googleapis.com/v1beta",
        "key_prefix": "AIza",
        "test_cmd": 'curl -s "{endpoint}/models?key={key}" | head -c 100'
    },
    "ollama": {
        "endpoint": "http://localhost:11434",
        "key_prefix": "",
        "test_cmd": 'curl -s {endpoint}/api/tags | head -c 100',
        "local": True
    },
    "deepseek": {
        "endpoint": "https://api.deepseek.com/v1",
        "key_prefix": "sk-",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "opencode": {
        "endpoint": "https://api.opencode.ai/v1",
        "key_prefix": "",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "groq": {
        "endpoint": "https://api.groq.com/openai/v1",
        "key_prefix": "gsk-",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "together": {
        "endpoint": "https://api.together.xyz/v1",
        "key_prefix": "",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "cerebras": {
        "endpoint": "https://api.cerebras.ai/v1",
        "key_prefix": "cscr-",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "huggingface": {
        "endpoint": "https://api-inference.huggingface.co",
        "key_prefix": "hf_",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "perplexity": {
        "endpoint": "https://api.perplexity.ai",
        "key_prefix": "pplx-",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "mistral": {
        "endpoint": "https://api.mistral.ai/v1",
        "key_prefix": "",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "zhipu": {
        "endpoint": "https://open.bigmodel.cn/api/paas/v4",
        "key_prefix": "",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "dashscope": {
        "endpoint": "https://dashscope.aliyuncs.com/api/v1",
        "key_prefix": "sk-",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "wenxin": {
        "endpoint": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1",
        "key_prefix": "",
        "test_cmd": 'curl -s "{endpoint}/models?access_token={key}" | head -c 100'
    },
    "silicon": {
        "endpoint": "http://api.siliconflow.cn/v1",
        "key_prefix": "sk-",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "closeai": {
        "endpoint": "https://platform.closeai-asia.com/developer/api/v1",
        "key_prefix": "sk-",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    },
    "minimax": {
        "endpoint": "https://api.minimax.chat/v1",
        "key_prefix": "",
        "test_cmd": 'curl -s -H "Authorization: Bearer {key}" {endpoint}/models | head -c 100'
    }
}


def load_keys():
    """加载keys配置"""
    if not KEYS_FILE.exists():
        return {}
    try:
        with open(KEYS_FILE) as f:
            return json.load(f)
    except Exception as e:
        print(f"加载keys失败: {e}")
        return {}


def save_keys(keys):
    """保存keys配置"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2, ensure_ascii=False)


def load_usage():
    """加载用量记录"""
    if not USAGE_FILE.exists():
        return {}
    try:
        with open(USAGE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_usage(usage):
    """保存用量记录"""
    with open(USAGE_FILE, 'w') as f:
        json.dump(usage, f, indent=2, ensure_ascii=False)


def add_key(provider: str, key: str, name: str = ""):
    """添加API Key"""
    keys = load_keys()
    if provider not in keys:
        keys[provider] = []
    
    key_info = {
        "key": key,
        "name": name or f"{provider}_{len(keys[provider])+1}",
        "added": datetime.now().isoformat(),
        "active": True
    }
    keys[provider].append(key_info)
    save_keys(keys)
    print(f"✓ 添加 {provider}: {key[:8]}...")


def list_keys():
    """列出所有keys"""
    keys = load_keys()
    if not keys:
        print("暂无API Keys")
        return
    
    for provider, key_list in keys.items():
        print(f"\n【{provider}】")
        for i, k in enumerate(key_list):
            status = "✓" if k.get("active") else "✗"
            print(f"  {status} [{i+1}] {k['name']} | {k['key'][:12]}...")


def test_key(provider: str, index: int = 0):
    """测试单个key"""
    keys = load_keys()
    if provider not in keys:
        print(f"未知provider: {provider}")
        return False
    
    key_list = keys[provider]
    if index >= len(key_list):
        print(f"索引超出范围")
        return False
    
    key_info = key_list[index]
    key = key_info["key"]
    
    # Ollama本地测试
    if provider == "ollama":
        import requests
        try:
            resp = requests.get(f"{PROVIDERS['ollama']['endpoint']}/api/tags", timeout=5)
            if resp.status_code == 200:
                print(f"✓ Ollama可用 | 模型数: {len(resp.json().get('models', []))}")
                return True
        except Exception as e:
            print(f"✗ Ollama错误: {e}")
            return False
    
    print(f"测试 {provider}: {key[:10]}...")
    return True


def get_best_key(provider: str) -> str:
    """获取可用的最佳key"""
    keys = load_keys()
    if provider not in keys:
        return None
    
    for k in keys[provider]:
        if k.get("active"):
            return k["key"]
    return None


CURRENT_FILE = CONFIG_DIR / "current_provider.json"


def show_current():
    """显示当前使用的provider"""
    if CURRENT_FILE.exists():
        with open(CURRENT_FILE) as f:
            data = json.load(f)
            provider = data.get("provider", "unknown")
            model = data.get("model", "MiniMax-M2.1")
            switched_at = data.get("switched_at", "unknown")
            print(f"当前使用: {provider}")
            print(f"模型: {model}")
            print(f"切换时间: {switched_at}")
    else:
        # 从OpenClaw配置推断
        print("当前使用: minimax (MiniMax-M2.1)")
        print("提示: 用 'python3 api-key-manager.py use minimax' 标记")


def record_usage(provider: str, key: str, tokens: int = 0, cost: float = 0):
    """记录用量"""
    usage = load_usage()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if provider not in usage:
        usage[provider] = {}
    if today not in usage[provider]:
        usage[provider][today] = {"tokens": 0, "requests": 0, "cost": 0}
    
    usage[provider][today]["tokens"] += tokens
    usage[provider][today]["requests"] += 1
    usage[provider][today]["cost"] += cost
    
    save_usage(usage)


def status():
    """查看整体状态"""
    keys = load_keys()
    usage = load_usage()
    
    print("=== API Key Manager ===\n")
    
    total = sum(len(v) for v in keys.values())
    active = sum(len([k for k in v if k.get("active")]) for v in keys.values())
    
    print(f"Keys: {active}/{total} 可用")
    print(f"Providers: {len(keys)}")
    
    # Ollama状态
    if "ollama" in keys:
        test_key("ollama", 0)


def usage_summary():
    """用量汇总"""
    usage = load_usage()
    if not usage:
        print("暂无用量记录")
        return
    
    for provider, data in usage.items():
        print(f"\n【{provider}】")
        for date, stats in sorted(data.items(), reverse=True)[:3]:
            print(f"  {date}: {stats['requests']}次 | {stats['tokens']}tokens | ${stats['cost']:.4f}")


def help():
    print("""
API Key Manager 用法:
    
    python3 api-key-manager.py add <provider> <key> [name]
    python3 api-key-manager.py list
    python3 api-key-manager.py test <provider> [index]
    python3 api-key-manager.py use <provider> [model]  # 标记当前使用
    python3 api-key-manager.py current                 # 查看当前使用
    python3 api-key-manager.py status
    python3 api-key-manager.py usage
    
支持的providers:
    openai, anthropic, google, ollama, deepseek, opencode
    groq, together, cerebras, huggingface, perplexity
    mistral, zhipu, dashscope, wenxin, silicon, closeai, minimax
""")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "add":
        if len(sys.argv) < 4:
            print("用法: add <provider> <key> [name]")
        else:
            add_key(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    
    elif cmd == "list":
        list_keys()
    
    elif cmd == "test":
        idx = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        test_key(sys.argv[2], idx)
    
    elif cmd == "use":
        if len(sys.argv) < 3:
            print("用法: use <provider>")
        else:
            provider = sys.argv[2]
            model = sys.argv[3] if len(sys.argv) > 3 else "MiniMax-M2.1"
            # 写入当前使用配置
            with open(CURRENT_FILE, 'w') as f:
                json.dump({
                    "provider": provider,
                    "model": model,
                    "switched_at": datetime.now().isoformat()
                }, f)
            print(f"✓ 已标记当前使用: {provider} ({model})")
    
    elif cmd == "current":
        show_current()
    
    elif cmd == "status":
        status()
    
    elif cmd == "usage":
        usage_summary()
    
    else:
        help()
