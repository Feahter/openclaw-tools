#!/usr/bin/env python3
"""
Resource Monitor - 资源监控器

功能：
- 系统资源监控 (CPU、内存、磁盘)
- API 调用统计与缓存
- 性能指标收集

使用方式：
- python3 resource-monitor.py --status   # 查看状态
- python3 resource-monitor.py --stats    # 查看统计
- python3 resource-monitor.py --clear    # 清除统计
- python3 resource-monitor.py --test      # 测试功能
"""

import json
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# 配置
CONFIG_DIR = Path.home() / ".openclaw"
STATS_FILE = CONFIG_DIR / "resource-stats.json"
CACHE_TTL = 60  # 缓存 TTL (秒)


class ResourceMonitor:
    """资源监控器"""
    
    def __init__(self):
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """加载统计信息"""
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "api_calls": 0,
            "cached_calls": 0,
            "total_tokens": 0,
            "requests": [],
            "last_update": None
        }
    
    def _save_stats(self):
        """保存统计信息"""
        self.stats["last_update"] = datetime.now().isoformat()
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def get_cpu_usage(self) -> float:
        """获取 CPU 使用率"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            # 备用方法
            try:
                result = subprocess.run(['top', '-l', '1'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'CPU usage' in line:
                        parts = line.split()
                        return float(parts[-2].replace('%', ''))
            except Exception:
                pass
        return 0.0
    
    def get_memory_usage(self) -> Dict:
        """获取内存使用情况"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "total": f"{mem.total / (1024**3):.1f}GB",
                "used": f"{mem.used / (1024**3):.1f}GB",
                "percent": mem.percent
            }
        except ImportError:
            # macOS 备用方法
            try:
                result = subprocess.run(['vm_stat'], capture_output=True, text=True)
                return {"total": "unknown", "used": "unknown", "percent": 0}
            except Exception:
                pass
        return {"total": "unknown", "used": "unknown", "percent": 0}
    
    def get_disk_usage(self) -> Dict:
        """获取磁盘使用情况"""
        try:
            stat = os.statvfs('/')
            total = stat.f_blocks * stat.f_frsize
            used = (stat.f_blocks - stat.f_bfree) * stat.f_frsize
            percent = (used / total) * 100
            return {
                "total": f"{total / (1024**3):.1f}GB",
                "used": f"{used / (1024**3):.1f}GB",
                "percent": round(percent, 1)
            }
        except Exception:
            return {"total": "unknown", "used": "unknown", "percent": 0}
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        return {
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "timestamp": datetime.now().isoformat()
        }
    
    def record_api_call(self, provider: str, endpoint: str, tokens: int = 0, 
                        cached: bool = False):
        """记录 API 调用"""
        self.stats["api_calls"] += 1
        if cached:
            self.stats["cached_calls"] += 1
        self.stats["total_tokens"] += tokens
        
        self.stats["requests"].append({
            "provider": provider,
            "endpoint": endpoint,
            "tokens": tokens,
            "cached": cached,
            "timestamp": datetime.now().isoformat()
        })
        
        # 只保留最近 100 条记录
        if len(self.stats["requests"]) > 100:
            self.stats["requests"] = self.stats["requests"][-100:]
        
        self._save_stats()
    
    def get_api_stats(self) -> Dict:
        """获取 API 统计"""
        total = self.stats["api_calls"]
        cached = self.stats["cached_calls"]
        
        return {
            "total_calls": total,
            "cached_calls": cached,
            "live_calls": total - cached,
            "cache_rate": f"{(cached/total*100):.1f}%" if total > 0 else "0%",
            "total_tokens": self.stats["total_tokens"],
            "requests": self.stats["requests"][-10:]  # 最近 10 条
        }
    
    def clear_stats(self):
        """清除统计"""
        self.stats = {
            "api_calls": 0,
            "cached_calls": 0,
            "total_tokens": 0,
            "requests": [],
            "last_update": None
        }
        self._save_stats()
    
    def get_status(self) -> Dict:
        """获取完整状态"""
        system = self.get_system_status()
        api_stats = self.get_api_stats()
        
        return {
            "system": system,
            "api": api_stats,
            "monitor": {
                "status": "运行中",
                "last_update": self.stats.get("last_update")
            }
        }


def status():
    """查看监控状态"""
    monitor = ResourceMonitor()
    s = monitor.get_status()
    
    cpu = s["system"]["cpu"]
    mem = s["system"]["memory"]
    disk = s["system"]["disk"]
    api = s["api"]
    
    output = f"""
╔══════════════════════════════════════════════════════════════╗
║                    资源监控器                                 ║
╠══════════════════════════════════════════════════════════════╣
║ 系统资源                                                   ║
║   CPU: {cpu:<5.1f}%{' ' * 40}║
║   内存: {mem['used']} / {mem['total']} ({mem['percent']:.1f}%){' ' * (28 - len(mem['used']) - len(mem['total']))}║
║   磁盘: {disk['used']} / {disk['total']} ({disk['percent']:.1f}%){' ' * (28 - len(disk['used']) - len(disk['total']))}║
╠══════════════════════════════════════════════════════════════╣
║ API 统计                                                   ║
║   总调用: {api['total_calls']:<41}║
║   缓存调用: {api['cached_calls']:<39}║
║   实时调用: {api['live_calls']:<41}║
║   缓存率: {api['cache_rate']:<41}║
║   Token 消耗: {api['total_tokens']:<37}║
╠══════════════════════════════════════════════════════════════╣
║ 状态: {s['monitor']['status']:<45}║
╚══════════════════════════════════════════════════════════════╝
"""
    print(output)
    return s


def stats():
    """显示简洁统计"""
    monitor = ResourceMonitor()
    api = monitor.get_api_stats()
    
    print(f"""
API 统计:
  总调用: {api['total_calls']}
  缓存调用: {api['cached_calls']} ({api['cache_rate']})
  实时调用: {api['live_calls']}
  Token 消耗: {api['total_tokens']}

最近请求:
""")
    for req in api["requests"]:
        cached = "📦" if req["cached"] else "🌐"
        print(f"  {cached} {req['provider']} {req['endpoint']} ({req['tokens']} tokens)")


def clear():
    """清除统计"""
    monitor = ResourceMonitor()
    monitor.clear_stats()
    print("✅ 统计已清除")


def test():
    """测试监控功能"""
    print("🧪 测试资源监控...")
    
    monitor = ResourceMonitor()
    
    # 测试系统状态
    system = monitor.get_system_status()
    print(f"  ✅ CPU: {system['cpu']}%")
    print(f"  ✅ 内存: {system['memory']['percent']}%")
    print(f"  ✅ 磁盘: {system['disk']['percent']}%")
    
    # 测试 API 记录
    monitor.record_api_call("minimax", "/v1/chat/completions", 100)
    monitor.record_api_call("deepseek", "/v1/models", 50, cached=True)
    
    api = monitor.get_api_stats()
    print(f"  ✅ API 统计: 总调用 {api['total_calls']}, 缓存 {api['cached_calls']}")
    
    print("\n✅ 测试完成!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        status()
    elif sys.argv[1] == "--status":
        status()
    elif sys.argv[1] == "--stats":
        stats()
    elif sys.argv[1] == "--clear":
        clear()
    elif sys.argv[1] == "--test":
        test()
    elif sys.argv[1] == "--help":
        print("""
🚀 资源监控器

用法:
  python3 resource-monitor.py      # 查看状态
  python3 resource-monitor.py --status # 查看详细状态
  python3 resource-monitor.py --stats  # 查看 API 统计
  python3 resource-monitor.py --clear  # 清除统计
  python3 resource-monitor.py --test   # 测试功能
        """)
    else:
        print("❌ 未知参数")
