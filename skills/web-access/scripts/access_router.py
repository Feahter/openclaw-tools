#!/usr/bin/env python3
"""
access_router.py - 通用网页获取路由
优先级：缓存 → webfetch → Jina → wechat → cf_proxy → cdp
"""
import os
import re
from typing import Optional
from .wechat_parser import parse_wechat_article, is_wechat_url

# 路由优先级
FETCHERS = [
    ('wechat', is_wechat_url),
]


def fetch_url(url: str, timeout: int = 30) -> Optional[str]:
    """
    通用 URL 获取入口，自动选择最佳 fetcher
    
    Returns:
        页面内容，失败返回 None
    """
    # 1. 微信文章 → 用专用解析器
    if is_wechat_url(url):
        content = _fetch_wechat(url, timeout)
        if content:
            return content
    
    # 2. 其他 URL → 回退到通用方式
    # 这里可以扩展其他 fetcher
    return _fetch_fallback(url, timeout)


def _fetch_wechat(url: str, timeout: int) -> Optional[str]:
    """获取微信文章"""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            text = parse_wechat_article(html)
            if text:
                return text
    except Exception:
        pass
    return None


def _fetch_fallback(url: str, timeout: int) -> Optional[str]:
    """回退方案：直接用 urllib 拉原始 HTML"""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception:
        return None
