---
name: agent-reach
description: "Web scraping and content extraction tool for AI agents. Use when the user needs to scrape Twitter/X, Reddit, YouTube transcripts, Bilibili, Xiaohongshu, or any web content. Provides unified interface for internet data access without API keys."
---

# Agent Reach

给你的 AI Agent 一键装上互联网能力。

## 功能

- 📺 YouTube/Bilibili 视频字幕提取
- 🐦 Twitter/X 内容抓取
- 📖 Reddit 帖子读取
- 📕 小红书内容获取
- 🔍 网页内容抓取和清洗
- 📦 GitHub 仓库信息
- 📡 RSS 订阅

## 使用方法

Agent Reach 安装后会提供 CLI 工具 `agent-reach` 和 `xreach`。

### 基本命令

```bash
# 抓取网页
xreach web <URL>

# 获取 YouTube 字幕
xreach youtube <VIDEO_URL>

# 获取 Bilibili 字幕
xreach bilibili <VIDEO_URL>

# 抓取 Twitter/X 帖子
xreach x <TWEET_URL>

# 抓取小红书
xreach xiaohongshu <NOTE_URL>

# 抓取 Reddit
xreach reddit <POST_URL>
```

## 依赖

- Python 3.10+
- 已安装包：requests, feedparser, python-dotenv, loguru, pyyaml, rich, yt-dlp
- 可选：playwright (浏览器自动化), browser-cookie3 (Cookie 导出)

## 安装路径

- 代码：`~/.openclaw/workspace/skills/agent-reach/`
- 配置：`~/.agent-reach/`
- 工具：`~/.agent-reach/tools/`

