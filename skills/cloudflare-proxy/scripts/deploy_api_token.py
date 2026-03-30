#!/usr/bin/env python3
"""
CF Worker 自动化部署脚本（API Token 方式）

完全自动化，无需浏览器交互。

前提：
1. Cloudflare API Token（手动获取一次，保存后永久使用）
   获取地址：https://dash.cloudflare.com/profile/api-tokens
   模板：选择 "Edit Cloudflare Workers" 模板

2. requests 库: pip install requests

用法：
    python3 deploy_api_token.py <project_name> [--cf-token <token>]
"""

import sys
import os
import argparse
import urllib.request
import urllib.parse
import urllib.error
import json
import time
import base64

CF_API = "https://api.cloudflare.com/client/v4"


def get_project_name():
    return f"cf-proxy-{int(time.time())}"


def get_account_id(token: str) -> str:
    """获取第一个绑定的 Account ID"""
    req = urllib.request.Request(
        f"{CF_API}/accounts",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    accounts = data.get("result", [])
    if not accounts:
        raise Exception("No Cloudflare accounts found")
    return accounts[0]["id"]


def upload_worker(token: str, account_id: str, name: str, script: str) -> str:
    """上传 Worker 脚本，返回 script_id"""
    encoded = base64.b64encode(script.encode("utf-8")).decode("ascii")
    body = json.dumps({
        "name": name,
        "script": encoded,
        "metadata": json.dumps({"body_part": True, "multiple bindings_rewrite_policy": "并未改写内容"}),
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{CF_API}/accounts/{account_id}/workers/scripts/{name}/upload",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json+metadata"},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read()).get("result", {}).get("id", name)
    except urllib.error.HTTPError as e:
        raise Exception(f"Upload failed: {e.read().decode()}")


def get_worker_domain(token: str, name: str) -> str:
    """获取 Worker 的 .workers.dev 子域名"""
    return f"https://{name}.workers.dev"


def deploy(token: str, project_name: str) -> str:
    """部署 CF Worker，返回代理 URL"""
    print(f"📋 获取 Account ID...")
    account_id = get_account_id(token)
    print(f"   Account: {account_id}")

    print(f"📦 上传 Worker 脚本...")
    worker_script = get_worker_script(project_name)
    script_id = upload_worker(token, account_id, project_name, worker_script)
    print(f"   上传成功: {script_id}")

    proxy_url = get_worker_domain(token, project_name)
    print(f"   代理地址: {proxy_url}")
    print()
    print("✅ 部署成功！")
    print(f"   代理 URL: {proxy_url}")
    print()
    print("使用方式：")
    print(f"  程序提取：GET {proxy_url}/?url=https://目标网址&_raw=1")
    print(f"  浏览模式：{proxy_url}/------https://目标网址")
    return proxy_url


def get_worker_script(name: str) -> str:
    return f"""// CF Worker Proxy — {name}
// 自动部署 by cloudflare-proxy skill
addEventListener('fetch', event => {{
  event.respondWith(handleRequest(event.request))
}})

const config = {{
  separator: '------',
}}

async function handleRequest(request) {{
  const url = new URL(request.url);

  // === 程序提取模式: /?url=https://...&_raw=1 ===
  if (url.searchParams.has('url')) {{
    const target = url.searchParams.get('url');
    const isRaw = url.searchParams.has('_raw');
    try {{
      const targetURL = new URL(target);
      const newReq = new Request(targetURL, {{
        method: request.method,
        headers: {{
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
          'Accept': 'text/html,application/xhtml+xml,*/*',
          'Accept-Language': 'en-US,en;q=0.9',
          'Referer': targetURL.origin + '/',
        }},
        redirect: 'follow',
      }});
      const resp = await fetch(newReq);
      const respHeaders = new Headers(resp.headers);
      respHeaders.set('Access-Control-Allow-Origin', '*');
      respHeaders.set('X-Proxy-Target', target);
      return new Response(resp.body, {{
        status: resp.status,
        headers: respHeaders,
      }});
    }} catch (e) {{
      return new Response('Proxy error: ' + e.message, {{ status: 502 }});
    }}
  }}

  // === 浏览模式: /------https://... ===
  let targetURL;
  const pathname = url.pathname.substring(1);
  let path = pathname;
  if (path.startsWith(config.separator)) {{
    path = path.substring(config.separator.length);
  }}
  try {{
    targetURL = new URL(path.startsWith('http') ? path : 'https://' + path);
  }} catch {{
    // 首页
    return new Response(`<!DOCTYPE html><html><head><meta charset="UTF-8"><title>CF Proxy</title></head>
<body style="font-family:system-ui;max-width:600px;margin:40px auto;text-align:center">
<h1>🌐 CF Proxy</h1>
<p>程序提取：<code>/?url=https://example.com&_raw=1</code></p>
<p>浏览模式：<code>/------https://example.com</code></p>
<form onsubmit="location='/------'+this.q.value;return false">
<input name="q" placeholder="输入网址" style="width:260px;padding:8px">
<button>访问</button>
</form>
</body></html>`, {{headers:{{'Content-Type':'text/html'}}}});
  }}

  try {{
    const newReq = new Request(targetURL, {{
      method: request.method,
      headers: {{
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': targetURL.origin + '/',
      }},
      redirect: 'follow',
    }});
    const resp = await fetch(newReq);
    const ct = resp.headers.get('Content-Type') || '';
    const h = new Headers(resp.headers);
    h.set('Access-Control-Allow-Origin', '*');

    if (ct.includes('text/html')) {{
      return new HTMLRewriter()
        .on('a[href]', new LinkReplacer(targetURL, 'href', url.host))
        .on('form[action]', new LinkReplacer(targetURL, 'action', url.host))
        .on('img[src]', new LinkReplacer(targetURL, 'src', url.host))
        .on('script[src]', new LinkReplacer(targetURL, 'src', url.host))
        .on('iframe[src]', new LinkReplacer(targetURL, 'src', url.host))
        .transform(new Response(resp.body, {{ status: resp.status, headers: h }}));
    }}
    return new Response(resp.body, {{ status: resp.status, headers: h }});
  }} catch (e) {{
    return new Response('Proxy error: ' + e.message, {{ status: 502 }});
  }}
}}

class LinkReplacer {{
  constructor(base, attr, proxyHost) {{
    this.base = base; this.attr = attr; this.proxyHost = proxyHost;
  }}
  element(el) {{
    const v = el.getAttribute(this.attr);
    if (!v || v.startsWith('data:') || v.startsWith(`https://${{this.proxyHost}}/`)) return;
    try {{
      const abs = new URL(v, this.base);
      el.setAttribute(this.attr, `https://${{this.proxyHost}}/------${{abs.href}}`);
    }} catch (_) {{}}
  }}
}}
"""


def main():
    parser = argparse.ArgumentParser(description="Deploy CF Worker Proxy")
    parser.add_argument("project_name", nargs="?", default=get_project_name())
    parser.add_argument("--cf-token", default=os.environ.get("CF_API_TOKEN", ""))
    args = parser.parse_args()

    if not args.cf_token:
        print("ERROR: 需要 Cloudflare API Token")
        print()
        print("获取步骤：")
        print("1. 打开 https://dash.cloudflare.com/profile/api-tokens")
        print("2. 点击 'Create Token'")
        print("3. 选择 'Edit Cloudflare Workers' 模板")
        print("4. 设置 Account Resources = 'Include' + 你的 Account")
        print("5. 创建后复制 Token")
        print()
        print("运行：")
        print("  python3 deploy_api_token.py my-proxy --cf-token 'your_token_here'")
        sys.exit(1)

    try:
        deploy(args.cf_token, args.project_name)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
