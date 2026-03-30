#!/usr/bin/env python3
"""
Cloudflare Worker Proxy — fetch 模式

通过 Cloudflare Worker 代理访问目标 URL，返回原始 HTML 内容。
适用于程序提取（如 article summarization、data extraction）。

用法：
    python3 proxy_fetch.py <url> [--proxy <proxy_url>]

示例：
    python3 proxy_fetch.py https://twitter.com/user/status/123
    python3 proxy_fetch.py https://github.com/user/repo --proxy https://your-worker.workers.dev
"""

import argparse
import urllib.parse
import sys
import urllib.request
import urllib.error


def proxy_fetch(target_url: str, proxy_url: str = "https://webproxy.stratosphericus.workers.dev") -> str:
    """
    通过 CF Worker 代理获取目标 URL 内容。

    Args:
        target_url: 要访问的目标 URL
        proxy_url: Cloudflare Worker 代理地址

    Returns:
        目标的 HTML 内容（原始，无链接重写）

    Raises:
        Exception: 代理请求失败
    """
    encoded_url = urllib.parse.quote(target_url, safe="")
    proxy_fetch_url = f"{proxy_url.rstrip('/')}/proxy?url={encoded_url}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
    }

    req = urllib.request.Request(proxy_fetch_url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            html = content.decode("utf-8", errors="replace")
            # Check for Cloudflare/Turnstile challenge
            if "cf-challenge" in html.lower() or "turnstile" in html.lower() or "_cf_translation" in html:
                raise Exception(
                    "CF验证墙拦截：此代理地址触发了人机验证。"
                    "建议：(1) 自建 Worker（参考 deploy-guide.md）；"
                    "(2) 使用 browse 模式手动访问。"
                )
            return html
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if "cf-challenge" in body or "turnstile" in body or "_cf_translation" in body:
            raise Exception("CF验证墙拦截：自建 Worker 可避免此问题。")
        raise Exception(f"HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"URL error: {e.reason}")
    except Exception as e:
        raise Exception(f"Proxy fetch failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="CF Worker Proxy Fetch")
    parser.add_argument("url", help="Target URL to fetch")
    parser.add_argument(
        "--proxy",
        default="https://webproxy.stratosphericus.workers.dev",
        help="Cloudflare Worker proxy URL",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=50000,
        help="Max characters to return (default: 50000)",
    )
    args = parser.parse_args()

    try:
        content = proxy_fetch(args.url, args.proxy)
        truncated = content[: args.max_chars]
        if len(content) > args.max_chars:
            truncated += f"\n\n[Output truncated at {args.max_chars} chars, full content: {len(content)} chars]"
        print(truncated)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
