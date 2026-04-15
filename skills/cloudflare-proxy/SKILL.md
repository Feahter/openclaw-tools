name: cloudflare-proxy
license: MIT
description:
  通过 Cloudflare Worker 代理访问被 GFW 屏蔽的网站。
  当 web-access 直接访问失败时，使用此 skill 作为网络代理层。
  支持两种模式：程序提取（fetch）和浏览器交互（browse）。
trigger:
  - 用户请求访问被屏蔽的网站（如 Twitter/X、t.co、Google 等）
  - web-access 直接 fetch 失败（返回 403/超时/blocked）
  - 用户说"翻墙"、"代理访问"

config:
  proxy_url:
    description: Cloudflare Worker 代理地址（程序提取模式）
    default: "https://arthur-proxy.frankfeahter.workers.dev"
    hint: "已部署到你的 CF 账号，可直接使用。自建参考 references/deploy-guide.md"

## 使用方式

### 方式一：程序提取（推荐）

```python
import subprocess
result = subprocess.run(
    ["python3", "scripts/proxy_fetch.py", target_url,
     "--proxy", config["proxy_url"]],
    capture_output=True, text=True, timeout=30
)
html = result.stdout
```

等价于直接调用：`fetch(proxy_url + "/?url=" + encoded_url + "&_raw=1")`

### 方式二：浏览器交互

告知用户访问：
```
{proxy_url}/------{target_url}
```
自动打开可交互的代理页面（链接已重写，适合手动浏览）。

## 部署自己的 Worker

参考 `references/deploy-guide.md`

快速部署（需要 CF API Token）：
```bash
cd ~/.openclaw/workspace/skills/cloudflare-proxy/scripts
python3 deploy_api_token.py cf-proxy-$(date +%s) \
    --cf-token 'your_cf_api_token_here'
```

获取 API Token：
1. https://dash.cloudflare.com/profile/api-tokens
2. 创建 Token → "Edit Cloudflare Workers" 模板
3. Account Resources = Include

## 与 web-access 集成

在 web-access skill 的联网工具选择流程中：

```
尝试 web-fetch / curl
    ↓ 失败（403/超时/blocked）
调用 cloudflare-proxy
    ↓
proxy_fetch(target_url, proxy_url)
    ↓
返回 HTML / 报错
```

配置优先级（从高到低）：
1. 用户自建的 CF Worker URL
2. 公共 Worker：`https://webproxy.stratosphericus.workers.dev`

## 已知限制

- Twitter/X 部分页面需要登录态，程序提取可能受限
- Google 服务有复杂的 JS 渲染，Browse 模式更可靠
- 公共 Worker 可能被 Cloudflare 验证墙拦截（首次需人机验证）
  → 推荐自建 Worker 避免此问题
