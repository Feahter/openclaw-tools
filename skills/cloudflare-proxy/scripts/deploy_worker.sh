#!/usr/bin/env bash
# deploy-worker.sh — 自动化部署 Cloudflare Worker 代理
# 用法: ./deploy_worker.sh [project_name]
# 前提: wrangler login 已完成

set -e

PROJECT_NAME="${1:-my-proxy}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "📦 创建 Worker 项目: $PROJECT_NAME"
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# 如果已有 wrangler.toml，跳过初始化
if [ ! -f wrangler.toml ]; then
  echo "⚙️  初始化 Wrangler 项目..."
  echo "$PROJECT_NAME" | ~/.npm-global/bin/wrangler init "$PROJECT_NAME" --yes 2>/dev/null || true
fi

# 写入 Worker 脚本
cat > worker.js << 'WORKER_EOF'
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const config = {
  separator: '------',
  homepage: true,
  allowedDomains: [],
  browserEmulation: {
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    acceptLanguage: 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    acceptEncoding: 'gzip, deflate, br',
    connection: 'keep-alive',
    upgradeInsecureRequests: '1',
    secFetchDest: 'document',
    secFetchMode: 'navigate',
    secFetchSite: 'none',
    secFetchUser: '?1',
  }
}

async function handleRequest(request) {
  const url = new URL(request.url)

  // Homepage
  if (url.pathname === '/') {
    if (config.homepage && !url.search) {
      return getHomePage()
    }
    if (url.search) {
      const ref = request.headers.get('Referer') || ''
      try {
        const refURL = new URL(ref)
        const rawPath = refURL.pathname.substring(1)
        let path = rawPath.startsWith(config.separator) ? rawPath.substring(config.separator.length) : rawPath
        if (path.startsWith('http://') || path.startsWith('https://')) {
          const base = new URL(path)
          url.pathname = '/' + config.separator + base.origin + url.search
        }
      } catch (_) {}
    }
  }

  let targetURL

  // Extract target URL
  if (url.searchParams.has('url')) {
    // /proxy?url=... format
    try {
      targetURL = new URL(url.searchParams.get('url'))
    } catch {
      return new Response('Invalid URL', { status: 400 })
    }
  } else if (url.pathname.startsWith('/')) {
    // /------https://... format
    let path = url.pathname.substring(1)
    if (path.startsWith(config.separator)) {
      path = path.substring(config.separator.length)
    }
    if (path.startsWith('http://') || path.startsWith('https://')) {
      try {
        targetURL = new URL(path)
      } catch {
        return new Response('Invalid URL', { status: 400 })
      }
    } else {
      // Keyword search
      targetURL = new URL('https://duckduckgo.com/?q=' + encodeURIComponent(path))
    }
  } else {
    targetURL = url
  }

  // Build proxy fetch URL (用于 fetch 模式，返回原始 HTML)
  if (url.searchParams.has('_raw')) {
    return fetchTarget(targetURL, request, url.host)
  }

  // 默认：返回 HTMLrewrite 版本
  return fetchAndRewrite(targetURL, request, url.host)
}

async function fetchTarget(targetURL, request, proxyHost) {
  const newHeaders = new Headers()
  newHeaders.set('User-Agent', config.browserEmulation.userAgent)
  newHeaders.set('Accept', config.browserEmulation.accept)
  newHeaders.set('Accept-Language', config.browserEmulation.acceptLanguage)
  newHeaders.set('Accept-Encoding', 'gzip, deflate, br')
  newHeaders.set('Connection', 'keep-alive')
  newHeaders.set('Host', targetURL.host)
  newHeaders.set('Referer', targetURL.origin + '/')

  try {
    const newReq = new Request(targetURL, {
      method: request.method,
      headers: newHeaders,
      body: ['GET', 'HEAD'].includes(request.method) ? null : request.body,
      redirect: 'follow',
    })
    const resp = await fetch(newReq)
    const contentType = resp.headers.get('Content-Type') || ''
    const newRespHeaders = new Headers(resp.headers)
    newRespHeaders.set('Access-Control-Allow-Origin', '*')
    newRespHeaders.set('X-Proxy-Target', targetURL.href)
    return new Response(resp.body, {
      status: resp.status,
      statusText: resp.statusText,
      headers: newRespHeaders,
    })
  } catch (err) {
    return new Response('Proxy fetch error: ' + err.message, { status: 502 })
  }
}

async function fetchAndRewrite(targetURL, request, proxyHost) {
  const newHeaders = new Headers()
  newHeaders.set('User-Agent', config.browserEmulation.userAgent)
  newHeaders.set('Accept', config.browserEmulation.accept)
  newHeaders.set('Accept-Language', config.browserEmulation.acceptLanguage)
  newHeaders.set('Accept-Encoding', 'gzip, deflate, br')
  newHeaders.set('Connection', 'keep-alive')
  newHeaders.set('Host', targetURL.host)
  newHeaders.set('Referer', targetURL.origin + '/')

  try {
    const newReq = new Request(targetURL, {
      method: request.method,
      headers: newHeaders,
      body: ['GET', 'HEAD'].includes(request.method) ? null : request.body,
      redirect: 'follow',
    })
    const resp = await fetch(newReq)
    const contentType = resp.headers.get('Content-Type') || ''
    const newRespHeaders = new Headers(resp.headers)
    newRespHeaders.delete('Content-Security-Policy')
    newRespHeaders.delete('X-Frame-Options')
    newRespHeaders.set('Access-Control-Allow-Origin', '*')
    newRespHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    newRespHeaders.set('Access-Control-Allow-Headers', '*')

    if (contentType.includes('text/html')) {
      const rewriter = new HTMLRewriter()
        .on('a[href]', new LinkRewriter(targetURL, 'href', proxyHost, config.separator))
        .on('form[action]', new LinkRewriter(targetURL, 'action', proxyHost, config.separator))
        .on('img[src]', new LinkRewriter(targetURL, 'src', proxyHost, config.separator))
        .on('img[srcset]', new SrcsetRewriter(targetURL, proxyHost, config.separator))
        .on('link[href]', new LinkRewriter(targetURL, 'href', proxyHost, config.separator))
        .on('script[src]', new LinkRewriter(targetURL, 'src', proxyHost, config.separator))
        .on('iframe[src]', new LinkRewriter(targetURL, 'src', proxyHost, config.separator))
      return rewriter.transform(new Response(resp.body, { headers: newRespHeaders }))
    }

    return new Response(resp.body, {
      status: resp.status,
      headers: newRespHeaders,
    })
  } catch (err) {
    return new Response('Proxy error: ' + err.message, { status: 502 })
  }
}

class LinkRewriter {
  constructor(baseURL, attr, proxyHost, sep) {
    this.baseURL = baseURL; this.attr = attr; this.proxyHost = proxyHost; this.sep = sep
  }
  element(el) {
    const val = el.getAttribute(this.attr)
    if (!val || val.startsWith('data:') || val.startsWith('javascript:')) return
    if (val.startsWith(`https://${this.proxyHost}/`)) return
    try {
      const abs = new URL(val, this.baseURL)
      el.setAttribute(this.attr, `https://${this.proxyHost}/${this.sep}${abs.href}`)
    } catch (_) {}
  }
}

class SrcsetRewriter {
  constructor(baseURL, proxyHost, sep) {
    this.baseURL = baseURL; this.proxyHost = proxyHost; this.sep = sep
  }
  element(el) {
    const ss = el.getAttribute('srcset')
    if (!ss) return
    const parts = ss.split(/,\s+/).map(p => {
      const [u, sz] = p.trim().split(/\s+/)
      if (!u || u.startsWith('data:') || u.startsWith(`https://${this.proxyHost}/`)) return p
      try {
        const abs = new URL(u, this.baseURL)
        const rewritten = `https://${this.proxyHost}/${this.sep}${abs.href}`
        return sz ? `${rewritten} ${sz}` : rewritten
      } catch (_) { return p }
    }).join(', ')
    el.setAttribute('srcset', parts)
  }
}

function getHomePage() {
  return new Response(`<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>CF Proxy</title></head>
<body style="font-family:system-ui;max-width:600px;margin:40px auto;padding:20px">
<h1>🌐 Cloudflare Proxy</h1>
<p>用法：</p>
<ul>
<li>程序提取：<code>?url=https://example.com&amp;_raw=1</code></li>
<li>浏览模式：<code>/------https://example.com</code></li>
</ul>
<form onsubmit="location='/------'+this.q.value;return false">
<input name="q" placeholder="输入网址或关键词" style="width:300px;padding:8px">
<button>访问</button>
</form>
</body></html>`, {headers:{'Content-Type':'text/html'}})
}
WORKER_EOF

# 写入 wrangler.toml
cat > wrangler.toml << 'TOML_EOF'
name = "PROJ_NAME"
main = "worker.js"
compatibility_date = "2024-01-01"
TOML_EOF

sed -i '' "s/PROJ_NAME/$PROJECT_NAME/g" wrangler.toml

echo ""
echo "🚀 部署中..."
~/.npm-global/bin/wrangler deploy --dry-run 2>&1 | head -5 || true

echo ""
echo "⚠️  请先运行: ~/.npm-global/bin/wrangler login"
echo "   然后再运行: cd $PROJECT_NAME && ~/.npm-global/bin/wrangler deploy"
echo ""
echo "📋  或者手动部署："
echo "   cd $PROJECT_NAME"
echo "   ~/.npm-global/bin/wrangler deploy"
echo ""
echo "📄 Worker 脚本已生成在: $(pwd)/worker.js"
