#!/usr/bin/env python3
"""
API 自动切换工具 - Minimax余额不足时自动切换备用API
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

# 配置
CONFIG_DIR = Path.home() / ".api-keys"
PRIMARY_PROVIDER = "minimax"
FALLBACK_PROVIDERS = ["deepseek", "silicon", "zhipu", "dashscope", "closeai", "ollama"]
CHECK_INTERVAL = 300  # 5分钟检查一次
MINIMAX_BALANCE_THRESHOLD = 10  # 余额低于10元切换

def get_current_provider():
    """获取当前使用的provider"""
    openclaw_config = Path.home() / ".openclaw" / "config.json"
    if openclaw_config.exists():
        try:
            with open(openclaw_config) as f:
                config = json.load(f)
                return config.get("model", "").split("/")[0] if "/" in config.get("model", "") else None
        except:
            pass
    return None

def check_minimax_balance():
    """检查Minimax余额（需要登录，这里用预估）"""
    # 实际应该爬取网页或用API
    # 目前已知: ~13CNY
    return {"balance": 13, "currency": "CNY", "last_check": datetime.now().isoformat()}

def get_fallback_key(provider):
    """获取备用provider的key"""
    keys_file = CONFIG_DIR / "keys.json"
    if keys_file.exists():
        with open(keys_file) as f:
            keys = json.load(f)
            if provider in keys:
                for k in keys[provider]:
                    if k.get("active"):
                        return k.get("key")
    return None

def test_provider(provider):
    """测试provider是否可用"""
    key = get_fallback_key(provider)
    if not key:
        return False, "无key"
    
    if provider == "ollama":
        try:
            import urllib.request
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return True, "本地运行"
        except:
            return False, "服务未启动"
    
    # 其他provider测试逻辑
    return True, "key存在"

def switch_to(provider):
    """切换到指定provider"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⚠️ 切换到 {provider}")
    
    # 写入切换标记
    switch_file = CONFIG_DIR / "current_provider.json"
    with open(switch_file, 'w') as f:
        json.dump({
            "provider": provider,
            "switched_at": datetime.now().isoformat(),
            "reason": "余额不足或主provider不可用"
        }, f)
    
    # 设置环境变量供OpenClaw读取
    os.environ["OPENCLAW_MODEL_PROVIDER"] = provider
    
    return True

def monitor():
    """主监控循环"""
    print("\n" + "="*50)
    print("🔄 API自动切换监控已启动")
    print(f"主Provider: {PRIMARY_PROVIDER}")
    print(f"备用: {FALLBACK_PROVIDERS}")
    print(f"检查间隔: {CHECK_INTERVAL}秒")
    print("="*50)
    
    while True:
        try:
            # 检查主provider状态
            balance = check_minimax_balance()
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 检查...")
            print(f"  Minimax余额: ¥{balance['balance']}")
            
            # 判断是否需要切换
            need_switch = balance['balance'] < MINIMAX_BALANCE_THRESHOLD
            
            if need_switch:
                # 找可用的备用
                for fallback in FALLBACK_PROVIDERS:
                    ok, msg = test_provider(fallback)
                    if ok:
                        switch_to(fallback)
                        break
                else:
                    print("  ⚠️ 无可用备用provider!")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n监控已停止")
            break
        except Exception as e:
            print(f"  错误: {e}")
            time.sleep(CHECK_INTERVAL)

def status():
    """查看当前状态"""
    print("\n" + "="*50)
    print("📊 API切换状态")
    print("="*50)
    
    balance = check_minimax_balance()
    print(f"\n主Provider: {PRIMARY_PROVIDER}")
    print(f"余额: ¥{balance['balance']} (阈值: ¥{MINIMAX_BALANCE_THRESHOLD})")
    
    switch_file = CONFIG_DIR / "current_provider.json"
    if switch_file.exists():
        with open(switch_file) as f:
            data = json.load(f)
            print(f"当前使用: {data.get('provider', 'unknown')}")
            print(f"切换时间: {data.get('switched_at', 'unknown')}")
    
    print(f"\n备用Provider: {FALLBACK_PROVIDERS}")
    for fb in FALLBACK_PROVIDERS:
        ok, msg = test_provider(fb)
        status = "✓" if ok else "✗"
        print(f"  {status} {fb}: {msg}")
    
    print("="*50)

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "monitor":
        monitor()
    elif cmd == "status":
        status()
