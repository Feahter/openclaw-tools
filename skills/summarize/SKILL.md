---
name: summarize
description: Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube).
homepage: https://summarize.sh
metadata: {"clawdbot":{"emoji":"🧾","requires":{"bins":["summarize"]},"install":[{"id":"brew","kind":"brew","formula":"steipete/tap/summarize","bins":["summarize"],"label":"Install summarize (brew)"}]}}
---

# Summarize

Fast CLI to summarize URLs, local files, and YouTube links.

## Trigger Rules

**应触发的场景**（用户意图 = 需要摘要/总结内容）：
- 用户提供 URL 并要求总结/摘要
- 用户提供本地文件路径（PDF、图片、音频、文本等）并要求总结
- 用户提供 YouTube 链接并要求总结视频内容
- 用户提到"这篇文章"、"这个PDF"、"这个视频"、"帮我看看这个链接"等

**不应触发的场景**：
- 纯知识问答（如"什么是量子力学"）→ 用搜索/知识库
- 要求翻译、续写、翻译+摘要混合 → 评估是否由 summarize 处理
- 仅要求下载文件 → 不触发

## Quick start

```bash
summarize "https://example.com" --model google/gemini-3-flash-preview
summarize "/path/to/file.pdf" --model google/gemini-3-flash-preview
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto
```

## 参数验证

调用前请检查以下参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `target` | URL / 文件路径 / YouTube链接 | ✅ | 要摘要的内容 |
| `--model` | string | ❌ | 默认 `google/gemini-3-flash-preview` |
| `--length` | short / medium / long / xl / xxl / `<N>` | ❌ | 摘要长度 |
| `--max-output-tokens` | integer | ❌ | 最大输出 token 数 |
| `--extract-only` | flag | ❌ | 仅提取内容，不摘要（URL 专用）|
| `--json` | flag | ❌ | JSON 格式输出 |
| `--firecrawl` | auto / off / always | ❌ | 高级网页抓取 |
| `--youtube` | auto | ❌ | YouTube 转录 |

**参数组合注意事项**：
- `--extract-only` 仅对 URL 有效，用于纯内容提取（跳过 AI 摘要）
- `--json` 用于程序解析，返回结构化 JSON
- `--length <N>` 接受任意整数，表示最大字符数
- `--max-output-tokens` 与 `--length` 不可同时使用

## Model + API Keys

必须设置对应模型的 API key 环境变量：

| 模型厂商 | 环境变量 |
|----------|----------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| xAI | `XAI_API_KEY` |
| Google | `GEMINI_API_KEY`（别名：`GOOGLE_GENERATIVE_AI_API_KEY`、`GOOGLE_API_KEY`）|

> 默认模型：`google/gemini-3-flash-preview`（需 `GEMINI_API_KEY`）

## Optional Services

| 服务 | 环境变量 | 用途 |
|------|----------|------|
| Firecrawl | `FIRECRAWL_API_KEY` | 访问被屏蔽的网站 |
| Apify | `APIFY_API_TOKEN` | YouTube 转录 fallback |

## Config

可选配置文件：`~/.summarize/config.json`

```json
{
  "model": "openai/gpt-4o-mini"
}
```

## Error Handling

### 1. API Key 缺失

**症状**：报错包含 `401 Unauthorized`、`api key`、`missing api key` 等关键词

**处理步骤**：
1. 根据当前 `--model` 判断所需 key 类型（见上方表格）
2. 告知用户需要设置哪个环境变量，并提供设置命令
3. 示例修复：
   ```bash
   # macOS/Linux
   export GEMINI_API_KEY="your-key-here"
   
   # Windows PowerShell
   $env:GEMINI_API_KEY="your-key-here"
   ```
4. 重试命令

### 2. 文件不存在

**症状**：报错包含 `No such file or directory`、`file not found`、`path does not exist`

**处理步骤**：
1. 检查文件路径是否正确（绝对路径 vs 相对路径）
2. 确认文件是否存在：
   ```bash
   ls -la "/path/to/file.pdf"
   ```
3. 常见错误：
   - 路径含空格未加引号
   - 使用了 `~` 但 shell 未展开
   - 文件已删除或移动

### 3. 网络错误 / URL 不可访问

**症状**：报错包含 `connection refused`、`timeout`、`network error`、`403 Forbidden`、`404 Not Found`

**处理步骤**：
1. 确认 URL 可通过浏览器访问
2. 某些网站（Cloudflare 保护、反爬等）需要 Firecrawl fallback：
   ```bash
   export FIRECRAWL_API_KEY="your-key"
   summarize "https://blocked-site.com" --firecrawl auto
   ```
3. 超时重试（可指定更长超时）
4. 如持续失败，建议用户直接提供页面内容文本

### 4. 模型不可用 / 配额超限

**症状**：报错包含 `model not found`、`quota exceeded`、`rate limit`、`429`

**处理步骤**：
1. 确认 model 名称拼写正确（格式：`provider/model-name`，如 `google/gemini-3-flash-preview`）
2. 检查 API 配额：
   - Google: [ai.google.dev quotas](https://ai.google.dev/gemini-api/docs/rate-limits)
   - OpenAI: [platform.openai.com](https://platform.openai.com)
3. 尝试降级模型或等待后重试：
   ```bash
   summarize "https://example.com" --model openai/gpt-4o-mini
   ```

### 5. YouTube 视频不可用

**症状**：YouTube 链接报错 `video unavailable`、`private video`、`region locked`

**处理步骤**：
1. 确认视频是否公开、可访问
2. 设置 Apify token 启用转录 fallback：
   ```bash
   export APIFY_API_TOKEN="your-token"
   summarize "https://youtu.be/xxx" --youtube auto
   ```
3. 如仍不可用，建议用户直接粘贴视频字幕或描述文本

### 6. 文件类型不支持

**症状**：报错包含 `unsupported file type`、`cannot process`

**当前支持的文件类型**：PDF、图片（JPG/PNG/GIF/WebP）、音频（MP3/WAV/M4A）、纯文本、视频（MP4 等）

**处理步骤**：
1. 确认文件格式是否在支持列表内
2. 如为图片/音频，可直接传入 summarize
3. 如为其他格式，考虑转为文本或 PDF 后处理

## Exit Codes

| Code | 含义 |
|------|------|
| 0 | 成功 |
| 1 | 通用错误（参数错误、文件不存在等）|
| 2 | API 错误（key 缺失、配额超限）|
| 3 | 网络错误（超时、无法连接）|
| 127 | 命令未找到（summarize 未安装）|

## Tips

- **长文本**：使用 `--length long` 或 `--length xxl` 获取更详细的摘要
- **程序调用**：使用 `--json` 获取结构化输出，便于解析
- **快速预览**：URL 使用 `--extract-only` 直接获取原文，不做摘要
- **调试**：在命令前加 `SUMMARIZE_DEBUG=1` 查看详细日志
