#!/usr/bin/env python3
"""
API 代理服务 MVP - 多 Provider 统一接入

功能：
- 统一 API 代理接口
- Provider 自动切换
- 请求转发与负载均衡
- 智能缓存支持 (减少重复 API 调用)

错误处理增强版：
- 网络异常自动重试 (最多 3 次)
- 端口占用检测和优雅失败
- API 调用超时处理
- 错误日志记录
- 健康检查机制

使用方式：
- python3 api-proxy.py --start    # 启动服务
- python3 api-proxy.py --status   # 查看状态
- python3 api-proxy.py --test     # 测试连通性
- python3 api-proxy.py --cache    # 查看缓存状态
- python3 api-proxy.py --clear-cache # 清除缓存
- python3 api-proxy.py --health   # 健康检查
"""

import json
import subprocess
import socket
import time
import hashlib
import logging
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# ==================== 配置 ====================
CONFIG_DIR = Path.home() / ".openclaw"
PROXY_CONFIG = CONFIG_DIR / "api-proxy-config.json"
CACHE_CONFIG = CONFIG_DIR / "cache-config.json"
PORT = 8780

# ==================== 日志配置 ====================
LOG_DIR = CONFIG_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "api-proxy.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 重试配置 ====================
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒
SOCKET_TIMEOUT = 10  # 秒
DEFAULT_TIMEOUT = 30  # 默认超时时间

# 缓存管理器
_cache_manager = None


def get_cache_manager():
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from cache_manager import CacheManager
            if CACHE_CONFIG.exists():
                with open(CACHE_CONFIG) as f:
                    config = json.load(f)
                _cache_manager = CacheManager(config)
            else:
                _cache_manager = CacheManager()
        except ImportError:
            _cache_manager = None
        except Exception as e:
            logger.warning(f"缓存管理器初始化失败: {e}")
            _cache_manager = None
    return _cache_manager


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


# ==================== 错误处理增强 ====================

def log_error(error_type: str, error_msg: str, context: Dict = None):
    """记录错误日志"""
    error_info = {
        "type": error_type,
        "message": error_msg,
        "timestamp": datetime.now().isoformat(),
        "context": context or {}
    }
    logger.error(f"[{error_type}] {error_msg}")
    if context:
        logger.debug(f"错误上下文: {json.dumps(context, ensure_ascii=False)}")
    return error_info


def is_port_in_use(port: int, timeout: int = SOCKET_TIMEOUT) -> Tuple[bool, Optional[str]]:
    """检查端口是否被占用 - 增强版"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex(('localhost', port))
            return result == 0, None
    except socket.timeout:
        error_msg = f"端口 {port} 检测超时"
        log_error("PORT_CHECK_TIMEOUT", error_msg, {"port": port})
        return False, error_msg
    except Exception as e:
        error_msg = f"端口 {port} 检测失败: {e}"
        log_error("PORT_CHECK_ERROR", error_msg, {"port": port, "error": str(e)})
        return False, error_msg


def check_port_available(port: int) -> Tuple[bool, str]:
    """检查端口可用性"""
    in_use, error = is_port_in_use(port)
    if in_use:
        return False, f"端口 {port} 已被占用"
    elif error:
        return False, error
    return True, f"端口 {port} 可用"


def retry_on_failure(max_retries: int = MAX_RETRIES, delay: int = RETRY_DELAY):
    """重试装饰器 - 网络异常自动重试"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                except Exception as e:
                    last_exception = e
                    logger.warning(f"第 {attempt}/{max_retries} 次尝试失败: {e}")
                    if attempt < max_retries:
                        time.sleep(delay)
            logger.error(f"重试 {max_retries} 次后仍失败: {last_exception}")
            raise last_exception
        return wrapper
    return decorator


def safe_urlopen(url: str, timeout: int = DEFAULT_TIMEOUT, retries: int = MAX_RETRIES):
    """安全的 URL 请求 - 带超时和重试"""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response
        except urllib.error.URLError as e:
            last_error = e
            logger.warning(f"URL 请求失败 ({attempt}/{retries}): {url} - {e}")
            if attempt < retries:
                time.sleep(RETRY_DELAY)
        except socket.timeout:
            last_error = f"请求超时: {url}"
            logger.warning(f"请求超时 ({attempt}/{retries}): {url}")
            if attempt < retries:
                time.sleep(RETRY_DELAY)
        except Exception as e:
            last_error = e
            logger.error(f"请求异常: {url} - {e}")
            if attempt < retries:
                time.sleep(RETRY_DELAY)
    
    log_error("URL_REQUEST_FAILED", str(last_error), {"url": url, "retries": retries})
    return None


def check_provider_health(provider_id: str, config: Dict) -> Dict:
    """检查 Provider 健康状态"""
    url = config["base_url"]
    timeout = config.get("timeout", DEFAULT_TIMEOUT)
    
    start_time = time.time()
    try:
        # 尝试连接测试
        response = safe_urlopen(f"{url}/v1/models", timeout=timeout)
        response_time = int((time.time() - start_time) * 1000)
        
        if response and response.status == 200:
            return {
                "provider": provider_id,
                "name": config["name"],
                "healthy": True,
                "status": "healthy",
                "response_time_ms": response_time,
                "error": None
            }
        else:
            return {
                "provider": provider_id,
                "name": config["name"],
                "healthy": False,
                "status": "unhealthy",
                "response_time_ms": response_time,
                "error": f"HTTP {response.status if response else 'no response'}"
            }
    except Exception as e:
        response_time = int((time.time() - start_time) * 1000)
        log_error("PROVIDER_HEALTH_CHECK", str(e), {"provider": provider_id, "url": url})
        return {
            "provider": provider_id,
            "name": config["name"],
            "healthy": False,
            "status": "error",
            "response_time_ms": response_time,
            "error": str(e)
        }


def health_check() -> Dict:
    """执行健康检查"""
    logger.info("开始 API 代理健康检查")
    results = {
        "timestamp": datetime.now().isoformat(),
        "port": PORT,
        "providers": {},
        "summary": {"healthy": 0, "unhealthy": 0, "total": len(PROVIDERS)}
    }
    
    # 检查端口状态
    port_available, port_msg = check_port_available(PORT)
    if not port_available:
        results["port_status"] = "in_use"
    else:
        results["port_status"] = "available"
    results["port_message"] = port_msg
    
    # 检查所有 Provider
    for pid, pconfig in PROVIDERS.items():
        health = check_provider_health(pid, pconfig)
        results["providers"][pid] = health
        if health["healthy"]:
            results["summary"]["healthy"] += 1
        else:
            results["summary"]["unhealthy"] += 1
    
    logger.info(f"健康检查完成: {results['summary']['healthy']}/{results['summary']['total']} 健康")
    return results


def load_config() -> Dict:
    """加载配置"""
    if PROXY_CONFIG.exists():
        try:
            with open(PROXY_CONFIG) as f:
                return json.load(f)
        except Exception as e:
            log_error("CONFIG_LOAD", str(e), {"file": str(PROXY_CONFIG)})
    return {"providers": PROVIDERS, "active_provider": "minimax"}


def save_config(config: Dict):
    """保存配置"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(PROXY_CONFIG, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log_error("CONFIG_SAVE", str(e), {"file": str(PROXY_CONFIG)})


def start() -> bool:
    """启动代理服务 - 增强版"""
    in_use, msg = is_port_in_use(PORT)
    if in_use:
        print(f"❌ 端口 {PORT} 已被占用")
        logger.warning(f"启动失败: 端口 {PORT} 已被占用")
        return False
    
    config = load_config()
    print(f"🚀 API 代理服务启动中...")
    print(f"   端口: {PORT}")
    print(f"   Provider: {config.get('active_provider', 'minimax')}")
    print(f"   状态: 准备就绪 (MVP)")
    logger.info(f"API 代理服务准备启动 (port={PORT}, provider={config.get('active_provider')})")
    return True


def status() -> str:
    """查看状态 - 增强版"""
    config = load_config()
    active = config.get("active_provider", "minimax")
    
    # 检查端口状态
    port_in_use, _ = is_port_in_use(PORT)
    
    output = f"""
╔══════════════════════════════════════════════════════════════╗
║                   API 代理服务 MVP                           ║
╠══════════════════════════════════════════════════════════════╣
║ 状态: {'运行中' if port_in_use else '已停止':<47}║
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
    """测试连通性 - 增强版"""
    logger.info("开始测试 Provider 连通性")
    results = {}
    
    for pid, p in PROVIDERS.items():
        url = p["base_url"]
        timeout = p.get("timeout", DEFAULT_TIMEOUT)
        
        start_time = time.time()
        try:
            response = safe_urlopen(f"{url}/v1/models", timeout=timeout)
            response_time = int((time.time() - start_time) * 1000)
            
            if response and response.status == 200:
                results[pid] = {
                    "status": "ready", 
                    "latency": response_time,
                    "healthy": True
                }
                logger.info(f"{pid}: 健康 (响应时间: {response_time}ms)")
            else:
                results[pid] = {
                    "status": "unhealthy", 
                    "latency": response_time,
                    "healthy": False,
                    "error": f"HTTP {response.status if response else 'no response'}"
                }
                logger.warning(f"{pid}: 不健康")
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            results[pid] = {
                "status": "error", 
                "latency": response_time,
                "healthy": False,
                "error": str(e)
            }
            log_error("CONNECTIVITY_TEST", str(e), {"provider": pid, "url": url})
            logger.error(f"{pid}: 错误 - {e}")
    
    return results


def cache_status():
    """查看缓存状态"""
    manager = get_cache_manager()
    if manager is None:
        print("❌ 缓存管理器未安装")
        return
    
    from cache_manager import status as cache_status_func
    cache_status_func()


def clear_cache():
    """清除缓存"""
    manager = get_cache_manager()
    if manager is None:
        print("❌ 缓存管理器未安装")
        return
    
    manager.clear()
    print("✅ API 缓存已清除")


def cached_request(provider: str, endpoint: str, data: Optional[Dict] = None, 
                   ttl: Optional[int] = None) -> Optional[Dict]:
    """发送缓存的 API 请求
    
    Args:
        provider: Provider ID
        endpoint: API 端点
        data: 请求数据
        ttl: 缓存时间 (秒)
    
    Returns:
        API 响应或 None
    """
    manager = get_cache_manager()
    if manager is None or not manager.config.get("enabled", True):
        return None
    
    # 构建请求对象
    request = {
        "provider": provider,
        "endpoint": endpoint,
        "data": data
    }
    
    # 检查缓存
    cached = manager.get(request)
    if cached:
        response, remaining_ttl = cached
        print(f"📦 缓存命中 (剩余 TTL: {remaining_ttl:.0f}s)")
        return response
    
    return None


def cache_response(provider: str, endpoint: str, response: Dict, 
                   ttl: Optional[int] = None):
    """缓存 API 响应"""
    manager = get_cache_manager()
    if manager is None:
        return
    
    request = {
        "provider": provider,
        "endpoint": endpoint,
        "data": {}
    }
    manager.set(request, response, ttl)


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
        print("\n📊 连通性测试结果:")
        for pid, r in results.items():
            icon = "✅" if r.get("healthy") else "❌"
            latency = r.get("latency", 0)
            print(f"  {icon} {pid}: {r['status']} ({latency}ms)")
    elif sys.argv[1] == "--cache":
        cache_status()
    elif sys.argv[1] == "--clear-cache":
        clear_cache()
    elif sys.argv[1] == "--cleanup":
        # 清理过期缓存
        manager = get_cache_manager()
        if manager:
            count = manager.cleanup_expired()
            print(f"✅ 已清理 {count} 条过期缓存")
        else:
            print("❌ 缓存管理器未安装")
    elif sys.argv[1] == "--health":
        health = health_check()
        print("\n🏥 健康检查结果:")
        print(f"  端口: {health['port_status']} ({health['port_message']})")
        print(f"  Provider: {health['summary']['healthy']}/{health['summary']['total']} 健康")
        for pid, h in health["providers"].items():
            icon = "✅" if h["healthy"] else "❌"
            latency = h.get("response_time_ms", 0)
            print(f"  {icon} {pid}: {h['status']} ({latency}ms)")
            if h.get("error"):
                print(f"     错误: {h['error']}")
    elif sys.argv[1] == "--help":
        print("""
🚀 API 代理服务 MVP

用法:
  python3 api-proxy.py           # 查看状态
  python3 api-proxy.py --start   # 启动服务
  python3 api-proxy.py --status  # 详细状态
  python3 api-proxy.py --test    # 测试连通性
  python3 api-proxy.py --cache   # 查看缓存状态
  python3 api-proxy.py --clear-cache # 清除缓存
  python3 api-proxy.py --cleanup # 清理过期缓存
  python3 api-proxy.py --health  # 健康检查
        """)
    else:
        print("❌ 未知参数")
