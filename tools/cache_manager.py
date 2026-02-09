#!/usr/bin/env python3
"""
Cache Manager - API 缓存管理器

功能：
- 请求去重 (基于请求内容 hash)
- 响应缓存 (可配置 TTL)
- LRU 缓存策略 (最大 100 条)
- 缓存命中率统计
- TTL 过期清理

使用方式：
- python3 cache-manager.py --status   # 查看缓存状态
- python3 cache-manager.py --clear     # 清除所有缓存
- python3 cache-manager.py --stats     # 查看统计信息
- python3 cache-manager.py --test      # 测试缓存功能
"""

import hashlib
import json
import time
from collections import OrderedDict
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

# 配置
CACHE_DIR = Path.home() / ".openclaw" / "cache"
CACHE_FILE = CACHE_DIR / "api-cache.json"
STATS_FILE = CACHE_DIR / "cache-stats.json"

# 默认配置
DEFAULT_CONFIG = {
    "max_size": 100,           # 最大缓存条数 (LRU)
    "default_ttl": 300,         # 默认 TTL (秒, 5分钟)
    "enabled": True,            # 是否启用缓存
    "exclude_patterns": []      # 排除的 URL 模式
}


class CacheManager:
    """API 缓存管理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.cache: OrderedDict[str, Dict] = OrderedDict()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "requests": 0,
            "evictions": 0,
            "cleanups": 0,
            "last_cleanup": None
        }
        self._load_cache()
        self._load_stats()
    
    def _hash_request(self, request: Dict) -> str:
        """生成请求内容的 hash"""
        # 将请求内容序列化为字符串并计算 hash
        content = json.dumps(request, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _load_cache(self):
        """从磁盘加载缓存"""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    self.cache = OrderedDict(data.get("items", {}))
                    self.config.update(data.get("config", {}))
            except Exception:
                self.cache = OrderedDict()
    
    def _save_cache(self):
        """保存缓存到磁盘"""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # 保留最近的 max_size 条
        trimmed_cache = OrderedDict(list(self.cache.items())[-self.config["max_size"]:])
        
        with open(CACHE_FILE, 'w') as f:
            json.dump({
                "items": trimmed_cache,
                "config": self.config,
                "updated": datetime.now().isoformat()
            }, f, indent=2)
    
    def _load_stats(self):
        """从磁盘加载统计信息"""
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE, 'r') as f:
                    self.stats.update(json.load(f))
            except Exception:
                pass
    
    def _save_stats(self):
        """保存统计信息到磁盘"""
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def get(self, request: Dict) -> Optional[Tuple[Any, float]]:
        """获取缓存的响应
        
        Returns:
            (响应内容, 剩余 TTL) 或 None
        """
        if not self.config["enabled"]:
            return None
        
        self.stats["requests"] += 1
        key = self._hash_request(request)
        current_time = time.time()
        
        if key in self.cache:
            entry = self.cache[key]
            cached_time = entry.get("timestamp", 0)
            ttl = entry.get("ttl", self.config["default_ttl"])
            
            # 检查是否过期
            if current_time - cached_time < ttl:
                # LRU: 移动到末尾
                self.cache.move_to_end(key)
                self.stats["hits"] += 1
                remaining_ttl = ttl - (current_time - cached_time)
                return entry["response"], remaining_ttl
            else:
                # 已过期，删除
                del self.cache[key]
        
        self.stats["misses"] += 1
        return None
    
    def set(self, request: Dict, response: Any, ttl: Optional[int] = None):
        """缓存响应
        
        Args:
            request: 请求内容
            response: 响应内容
            ttl: 生存时间 (秒)
        """
        if not self.config["enabled"]:
            return
        
        key = self._hash_request(request)
        current_time = time.time()
        
        # LRU: 如果已存在，移除旧条目
        if key in self.cache:
            del self.cache[key]
        
        # 如果缓存已满，删除最旧的条目
        if len(self.cache) >= self.config["max_size"]:
            self.cache.popitem(last=False)
            self.stats["evictions"] += 1
        
        # 添加新条目
        self.cache[key] = {
            "response": response,
            "timestamp": current_time,
            "ttl": ttl or self.config["default_ttl"],
            "request_hash": key
        }
        
        self._save_cache()
    
    def cleanup_expired(self) -> int:
        """清理过期的缓存条目
        
        Returns:
            清理的条目数量
        """
        current_time = time.time()
        default_ttl = self.config["default_ttl"]
        
        # 优化: 使用字典推导式一次性过滤，O(n) 而非 O(n²)
        original_count = len(self.cache)
        self.cache = {
            key: entry for key, entry in self.cache.items()
            if current_time - entry.get("timestamp", 0) < entry.get("ttl", default_ttl)
        }
        
        expired_count = original_count - len(self.cache)
        
        if expired_count:
            self.stats["cleanups"] += expired_count
            self.stats["last_cleanup"] = datetime.now().isoformat()
            self._save_cache()
        
        return expired_count
    
    def clear(self):
        """清除所有缓存"""
        self.cache.clear()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "requests": 0,
            "evictions": 0,
            "cleanups": 0,
            "last_cleanup": None
        }
        self._save_cache()
        self._save_stats()
    
    def get_hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.stats["hits"] + self.stats["misses"]
        if total == 0:
            return 0.0
        return self.stats["hits"] / total * 100
    
    def get_status(self) -> Dict:
        """获取缓存状态"""
        current_time = time.time()
        valid_count = 0
        expired_count = 0
        
        for entry in self.cache.values():
            cached_time = entry.get("timestamp", 0)
            ttl = entry.get("ttl", self.config["default_ttl"])
            
            if current_time - cached_time < ttl:
                valid_count += 1
            else:
                expired_count += 1
        
        return {
            "enabled": self.config["enabled"],
            "total_entries": len(self.cache),
            "valid_entries": valid_count,
            "expired_entries": expired_count,
            "max_size": self.config["max_size"],
            "default_ttl": self.config["default_ttl"],
            "hit_rate": f"{self.get_hit_rate():.1f}%",
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "cleanups": self.stats["cleanups"],
            "last_cleanup": self.stats.get("last_cleanup")
        }
    
    def configure(self, **kwargs):
        """配置缓存管理器"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        self._save_cache()


def status():
    """查看缓存状态"""
    manager = CacheManager()
    s = manager.get_status()
    
    output = f"""
╔══════════════════════════════════════════════════════════════╗
║                    API 缓存管理器                             ║
╠══════════════════════════════════════════════════════════════╣
║ 状态: {'启用' if s['enabled'] else '禁用':<47}║
╠══════════════════════════════════════════════════════════════╣
║ 缓存统计                                                   ║
║   总条目: {s['total_entries']:<42}║
║   有效条目: {s['valid_entries']:<41}║
║   过期条目: {s['expired_entries']:<41}║
║   最大容量: {s['max_size']:<44}║
║   默认 TTL: {s['default_ttl']} 秒{' ' * (40 - len(str(s['default_ttl'])))}║
╠══════════════════════════════════════════════════════════════╣
║ 命中率统计                                                 ║
║   命中率: {s['hit_rate']:<43}║
║   命中次数: {s['hits']:<43}║
║   未命中: {s['misses']:<44}║
║   总请求: {s['hits'] + s['misses']:<44}║
╠══════════════════════════════════════════════════════════════╣
║ 维护统计                                                   ║
║   驱逐次数: {s['evictions']:<41}║
║   清理次数: {s['cleanups']:<42}║
║   上次清理: {s['last_cleanup'] or '从未':<41}║
╚══════════════════════════════════════════════════════════════╝
"""
    print(output)
    return s


def stats():
    """显示简洁的统计信息"""
    manager = CacheManager()
    s = manager.get_status()
    
    print(f"""
缓存统计:
  命中率: {s['hit_rate']}
  命中: {s['hits']} | 未命中: {s['misses']} | 总请求: {s['requests']}
  有效缓存: {s['valid_entries']}/{s['total_entries']}
  驱逐: {s['evictions']} | 清理: {s['cleanups']}
""")


def clear():
    """清除所有缓存"""
    manager = CacheManager()
    manager.clear()
    print("✅ 缓存已清除")


def cleanup():
    """清理过期缓存"""
    manager = CacheManager()
    count = manager.cleanup_expired()
    print(f"✅ 已清理 {count} 条过期缓存")


def test():
    """测试缓存功能"""
    print("🧪 测试缓存功能...")
    
    manager = CacheManager()
    
    # 测试请求
    test_request = {
        "url": "https://api.example.com/v1/models",
        "method": "GET",
        "headers": {"Content-Type": "application/json"}
    }
    
    test_response = {"models": ["gpt-3.5", "gpt-4"]}
    
    # 第一次请求 (未命中)
    result = manager.get(test_request)
    print(f"  首次请求: {'❌ 缓存未命中' if result is None else '✅ 缓存命中'}")
    
    # 设置缓存
    manager.set(test_request, test_response, ttl=60)
    print(f"  ✅ 已缓存响应 (TTL=60秒)")
    
    # 第二次请求 (命中)
    result = manager.get(test_request)
    if result:
        print(f"  ✅ 缓存命中! 响应: {result[0]}")
        print(f"  ⏱️ 剩余 TTL: {result[1]:.1f} 秒")
    
    # 检查状态
    s = manager.get_status()
    print(f"  📊 当前命中率: {s['hit_rate']}")
    
    # 测试 LRU (超过 max_size)
    print("  🔄 测试 LRU 策略...")
    for i in range(manager.config["max_size"] + 5):
        req = {"url": f"https://api.example.com/v1/test/{i}", "method": "GET"}
        manager.set(req, {"index": i})
    
    final_size = len(manager.cache)
    print(f"  ✅ 缓存大小已限制为: {final_size} (最大: {manager.config['max_size']})")
    
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
    elif sys.argv[1] == "--cleanup":
        cleanup()
    elif sys.argv[1] == "--test":
        test()
    elif sys.argv[1] == "--help":
        print("""
🚀 API 缓存管理器

用法:
  python3 cache-manager.py           # 查看缓存状态
  python3 cache-manager.py --status # 查看详细状态
  python3 cache-manager.py --stats   # 查看简洁统计
  python3 cache-manager.py --clear   # 清除所有缓存
  python3 cache-manager.py --cleanup # 清理过期缓存
  python3 cache-manager.py --test    # 测试缓存功能
        """)
    else:
        print("❌ 未知参数")
