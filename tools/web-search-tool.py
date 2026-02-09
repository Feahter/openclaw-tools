#!/usr/bin/env python3
"""
Web Search Tool - Brave Search API 集成
提供网络搜索能力，支持时间过滤和地区过滤
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import requests

# 配置
CONFIG_DIR = Path.home() / ".api-keys"
KEYS_FILE = CONFIG_DIR / "keys.json"
CONFIG_FILE = CONFIG_DIR / "web-search-config.json"

# 默认配置
DEFAULT_CONFIG = {
    "provider": "brave",
    "default_results": 10,
    "max_results": 20,
    "default_country": "US",
    "default_lang": "zh-CN",
    "rate_limit": 5,  # 每分钟最大请求数
    "rate_limit_window": 60  # 窗口时间（秒）
}

# 请求记录
REQUEST_LOG_FILE = CONFIG_DIR / "web-search-requests.json"


class BraveSearchAPI:
    """Brave Search API 客户端"""
    
    BASE_URL = "https://api.search.brave.com/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "X-Subscription-Token": api_key
        })
    
    def search(self, query: str, count: int = 10, 
               country: str = "US", 
               search_lang: str = "zh-CN",
               freshness: Optional[str] = None) -> Dict[str, Any]:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            count: 返回结果数量 (1-20)
            country: 国家代码 (US, CN, DE, JP, etc.)
            search_lang: 搜索语言
            freshness: 时间过滤 (pd=24h, pw=1周, pm=1月, py=1年, 或日期范围)
        
        Returns:
            包含搜索结果的字典
        """
        params = {
            "q": query,
            "count": min(max(1, count), 20),
            "country": country.upper(),
            "search_lang": search_lang
        }
        
        if freshness:
            params["freshness"] = freshness
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/search",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError("API密钥无效或已过期")
            elif response.status_code == 429:
                raise RateLimitError("请求过于频繁，请稍后再试")
            else:
                raise ConnectionError(f"HTTP错误: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"网络请求失败: {str(e)}")


class RateLimitError(Exception):
    """请求频率限制错误"""
    pass


class WebSearchTool:
    """Web Search 工具主类"""
    
    def __init__(self):
        self.config = self._load_config()
        self.request_log = self._load_request_log()
        self._api_client: Optional[BraveSearchAPI] = None
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    return {**DEFAULT_CONFIG, **json.load(f)}
            except:
                pass
        return DEFAULT_CONFIG.copy()
    
    def _save_config(self):
        """保存配置"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _load_request_log(self) -> List[Dict]:
        """加载请求记录"""
        if REQUEST_LOG_FILE.exists():
            try:
                with open(REQUEST_LOG_FILE) as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_request_log(self):
        """保存请求记录"""
        with open(REQUEST_LOG_FILE, 'w') as f:
            json.dump(self.request_log, f, indent=2, ensure_ascii=False)
    
    def _check_api_key(self) -> Optional[str]:
        """检查并获取API Key"""
        # 检查环境变量
        api_key = os.environ.get("BRAVE_API_KEY")
        if api_key:
            return api_key
        
        # 检查配置文件
        if KEYS_FILE.exists():
            try:
                with open(KEYS_FILE) as f:
                    keys = json.load(f)
                    if "brave" in keys and keys["brave"]:
                        return keys["brave"][0].get("key")
            except:
                pass
        
        return None
    
    def _check_rate_limit(self) -> bool:
        """检查是否超过请求频率限制"""
        now = time.time()
        window = self.config["rate_limit_window"]
        
        # 清理过期记录
        self.request_log = [r for r in self.request_log if now - r["timestamp"] < window]
        
        if len(self.request_log) >= self.config["rate_limit"]:
            oldest = self.request_log[0]["timestamp"]
            wait_time = window - (now - oldest)
            if wait_time > 0:
                raise RateLimitError(f"请求过于频繁，请等待 {int(wait_time)} 秒")
        
        return True
    
    def _record_request(self, query: str, results_count: int):
        """记录请求"""
        self.request_log.append({
            "timestamp": time.time(),
            "query": query,
            "results": results_count
        })
        self._save_request_log()
    
    def get_api_client(self) -> BraveSearchAPI:
        """获取API客户端"""
        if not self._api_client:
            api_key = self._check_api_key()
            if not api_key:
                raise ValueError(
                    "未配置Brave API密钥。请设置:\n"
                    "1. 环境变量: export BRAVE_API_KEY='your_key'\n"
                    "2. 或在 ~/.api-keys/keys.json 中添加 brave provider"
                )
            self._api_client = BraveSearchAPI(api_key)
        return self._api_client
    
    def search(self, query: str, recent: bool = False, 
               country: str = None, 
               lang: str = None,
               count: int = None) -> Dict[str, Any]:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            recent: 是否只搜索最近的结果
            country: 国家代码
            lang: 语言代码
            count: 结果数量
        
        Returns:
            搜索结果字典
        """
        # 参数设置
        count = count or self.config["default_results"]
        country = country or self.config["default_country"]
        search_lang = lang or self.config["default_lang"]
        
        # 时间过滤
        freshness = None
        if recent:
            freshness = "pw"  # 过去一周
        
        # 频率限制检查
        self._check_rate_limit()
        
        # 执行搜索
        client = self.get_api_client()
        result = client.search(
            query=query,
            count=count,
            country=country,
            search_lang=search_lang,
            freshness=freshness
        )
        
        # 记录请求
        results_count = len(result.get("web", {}).get("results", []))
        self._record_request(query, results_count)
        
        return result
    
    def search_simple(self, query: str, recent: bool = False) -> List[Dict[str, str]]:
        """
        简化搜索接口，返回格式化结果
        
        Args:
            query: 搜索关键词
            recent: 是否只搜索最近结果
        
        Returns:
            结果列表，每个包含 title, url, description
        """
        raw_results = self.search(query, recent=recent)
        
        results = []
        for item in raw_results.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "age": item.get("age", ""),
                "profile": item.get("profile", {})
            })
        
        return results
    
    def configure(self, **kwargs):
        """配置工具"""
        valid_keys = ["default_results", "max_results", "default_country", 
                      "default_lang", "rate_limit", "rate_limit_window"]
        for key, value in kwargs.items():
            if key in valid_keys:
                self.config[key] = value
            else:
                print(f"警告: 未知配置项 {key}")
        self._save_config()
        print("✓ 配置已更新")
    
    def status(self) -> Dict[str, Any]:
        """查看状态"""
        api_key = self._check_api_key()
        return {
            "api_key_configured": bool(api_key),
            "provider": self.config["provider"],
            "default_results": self.config["default_results"],
            "rate_limit": self.config["rate_limit"],
            "requests_in_window": len(self.request_log)
        }
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            client = self.get_api_client()
            # 执行简单搜索测试
            result = client.search("test", count=1)
            return "web" in result
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            return False


# CLI 入口
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Search Tool - Brave Search API")
    parser.add_argument("command", choices=["search", "status", "test", "configure"],
                       help="命令")
    parser.add_argument("query", nargs="?", help="搜索关键词")
    parser.add_argument("--recent", action="store_true", help="只搜索最近结果")
    parser.add_argument("--count", type=int, default=10, help="结果数量")
    parser.add_argument("--country", help="国家代码 (如 US, CN)")
    parser.add_argument("--lang", help="语言代码 (如 zh-CN, en)")
    
    # 配置参数
    parser.add_argument("--set-results", type=int, help="设置默认结果数量")
    parser.add_argument("--set-rate", type=int, help="设置请求频率限制")
    
    args = parser.parse_args()
    
    tool = WebSearchTool()
    
    if args.command == "search":
        if not args.query:
            print("错误: 需要指定搜索关键词")
            return
        
        print(f"🔍 搜索: {args.query}")
        if args.recent:
            print("  [过滤: 最近结果]")
        print()
        
        try:
            results = tool.search_simple(args.query, recent=args.recent)
            
            if not results:
                print("未找到结果")
                return
            
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['title']}")
                print(f"   URL: {r['url']}")
                if r['description']:
                    desc = r['description'][:200] + "..." if len(r['description']) > 200 else r['description']
                    print(f"   摘要: {desc}")
                if r['age']:
                    print(f"   时间: {r['age']}")
                print()
            
            print(f"✓ 找到 {len(results)} 条结果")
        except RateLimitError as e:
            print(f"⚠ {e}")
        except ValueError as e:
            print(f"⚠ {e}")
        except Exception as e:
            print(f"✗ 搜索失败: {e}")
    
    elif args.command == "status":
        status = tool.status()
        print("=== Web Search 状态 ===")
        print(f"Provider: {status['provider']}")
        print(f"API Key: {'✓ 已配置' if status['api_key_configured'] else '✗ 未配置'}")
        print(f"默认结果数: {status['default_results']}")
        print(f"频率限制: {status['rate_limit']}/分钟")
        print(f"窗口内请求: {status['requests_in_window']}")
    
    elif args.command == "test":
        print("测试连接...")
        if tool.test_connection():
            print("✓ 连接成功!")
        else:
            print("✗ 连接失败")
    
    elif args.command == "configure":
        changes = {}
        if args.set_results:
            changes["default_results"] = args.set_results
        if args.set_rate:
            changes["rate_limit"] = args.set_rate
        
        if changes:
            tool.configure(**changes)
        else:
            print("用法: python3 web-search-tool.py configure --set-results 10 --set-rate 5")


if __name__ == "__main__":
    main()
