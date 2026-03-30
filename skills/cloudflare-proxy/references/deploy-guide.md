# Cloudflare Worker 自建代理部署指南

## 为什么自建

| 项目 | 公共代理 | 自建 Worker |
|------|---------|-------------|
| 可用性 | 依赖作者维护 | 完全自控 |
| 速率限制 | 可能有 | 无（10万请求/天免费） |
| 自定义域名 | 不可 | 可 |
| 隐私 | 流量经过他人服务器 | 仅自己可见 |

## 前提条件

- Cloudflare 账号（免费即可）
- 一个托管在 Cloudflare 的域名（可选，用于自定义域名）

## 部署步骤

### 1. 安装 Wrangler CLI

```bash
npm install -g wrangler
wrangler login  # 用浏览器授权 Cloudflare
```

### 2. 创建 Worker 项目

```bash
mkdir my-proxy && cd my-proxy
npm init -y
npm install wrangler
```

### 3. 获取 Worker 脚本

从 https://github.com/BH3GEI/CloudflareWorkerProxy 获取 `WorkerProxy.js`。

### 4. 配置 wrangler.toml

```toml
name = "my-proxy"
main = "WorkerProxy.js"
compatibility_date = "2024-01-01"
```

### 5. 修改 Worker 配置（可选）

编辑 `WorkerProxy.js`，修改 `proxyDomains` 为你的 Worker 域名：

```javascript
const config = {
  proxyDomains: ['my-proxy.我的用户名.workers.dev'],  // 改这里
  separator: '------',
  homepage: true,
  allowedDomains: [],  // 空=允许所有
}
```

### 6. 部署

```bash
wrangler deploy
```

输出：
```
Uploaded my-proxy (1.42 MB)
  https://my-proxy.我的用户名.workers.dev
```

### 7. 配置自定义域名（可选）

Cloudflare Dashboard → Workers & Pages → my-proxy → Triggers → Custom Domains

## 与 web-access 集成

在 `TOOLS.md` 中记录你的 Worker URL：

```
### Cloudflare Proxy
proxy_url = https://my-proxy.我的用户名.workers.dev
```

使用优先级：
1. 先尝试 `web-access` 直接 fetch
2. 失败时 → 调用 CF Worker fetch 模式
3. 需要浏览器交互时 → 告知用户访问 Browse 模式 URL
