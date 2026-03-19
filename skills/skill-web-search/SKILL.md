---
name: skill-web-search
description: >
  网页正文提取与内容抓取。当用户要求读取URL、总结链接、抓取文章、提取网页内容、
  分析某篇文章时触发。专门解决微信公众号、知乎、GitHub 等平台的正文提取问题。
  触发条件：消息包含 URL 并要求「读取/总结/提取/抓取/分析/看看这篇文章」。
  不包括：仅搜索关键词（不用URL）、纯技术搜索（查bug/查文档）。
---

# skill-web-search — 网页内容抓取

## 能力

给一个 URL，返回干净的 Markdown 正文，保留标题层级、超链接、图片 URL、列表代码块。

## 提取策略（按顺序尝试，失败才换下一个）

### 策略 1：Jina Reader【首选】
```
web_fetch("https://r.jina.ai/<url>", maxChars=30000)
```
- 速度最快（~1.5s），格式最干净
- 适用：GitHub、技术博客、新闻、知乎（偶尔）、普通网页
- 限制：200次/天；Jina 对微信公众号通常返回 403，对部分国内平台可能返回乱码
- **只有微信公众号（mp.weixin.qq.com）直接跳过此策略**

### 策略 2：Scrapling + html2text【主力】
```
exec: python3 ~/.openclaw/workspace/skills/skill-web-search/scripts/fetch.py <url> 30000
```
- 无 API 限制，能绕过基础反爬，能读微信公众号
- 速度中等（~5-15s）
- 适用：微信公众号、知乎（Jina 失败时）、CSDN、掘金、小红书
- **依赖已安装的 scrapling + html2text + playwright**
- 微信文章自动用 `div#js_content` selector，图片 data-src 已处理

### 策略 3：Browser Reading Mode【最终手段】
```
agent-browser open "<url>"
agent-browser wait --load networkidle
agent-browser wait 2000
agent-browser get text "<selector>" --json 2>&1 | head -200
```
- 成功率最高，能读任何 JS 渲染页面
- 速度最慢（~15-30s），资源重
- 适用：策略 2 失败后的最终尝试，尤其动态渲染页面
- 微信文章 selector：`#js_content`
- 普通文章 selector：`article`、`main`、`.content`、`[class*="article"]`
- 用完必须 `agent-browser close`

### 策略 4：web_fetch 直接抓【静态兜底】
```
web_fetch(url, maxChars=30000)
```
- 策略 1-3 全部失败时的保底；纯静态页面也可以优先使用
- 返回原始 HTML，含导航/广告/页脚

## 域名推荐策略

| 域名 | 推荐 | 备选 |
|------|------|------|
| 普通网页（GitHub/博客/新闻） | Jina | web_fetch |
| 微信公众号 | Scrapling | Browser |
| 知乎 zhuanlan.zhihu.com | Jina → Scrapling | Browser |
| 掘金/小红书/CSDN | Scrapling | Jina |
| 需要登录的页面 | Browser | — |

## 防死循环

同一 URL 尝试策略 1-2 失败后，换策略 3。
策略 3 还失败则换策略 4。
策略 4 失败 → 告知用户「无法提取，建议手动复制内容」。

## 依赖（已安装）
```
scrapling, html2text, playwright
```
若 Scrapling 报错，检查：`playwright install chromium`

## 脚本
`scripts/fetch.py` — 策略 2 用，Scrapling + html2text 封装

## 质量标准
- 正文干净，无导航/广告/页脚
- 标题层级完整（# ## ###）
- 图片 URL 保留
- 微信懒加载图片（data-src）已自动处理
- 最大 30000 字符
