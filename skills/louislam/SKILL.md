---
name: uptime-kuma
description: "A fancy self-hosted monitoring tool"
triggers:
  - "uptime-kuma"
  - "uptime kuma"
  - "uptime-kuma" if '/' in full else "uptime-kuma"
source:
  project: louislam/uptime-kuma
  url: https://github.com/louislam/uptime-kuma
  license: MIT
  auto_generated: false
  updated_at: 2026-02-11T13:50:07
---

# Uptime Kuma

A fancy self-hosted monitoring tool

## 项目信息

- **Stars**: 82,670
- **License**: MIT
- **语言**: JavaScript
- **GitHub**: [louislam/uptime-kuma](https://github.com/louislam/uptime-kuma)

## 核心功能

- Monitoring uptime for HTTP(s) / TCP / HTTP(s) Keyword / HTTP(s) Json Query / Websocket / Ping / DNS Record / Push / Steam Game Server / Docker Containers
- Fancy, Reactive, Fast UI/UX
- Notifications via Telegram, Discord, Gotify, Slack, Pushover, Email (SMTP), and [90+ notification services, click here for the full list](https://github.com/louislam/uptime-kuma/tree/master/src/components/notifications)
- 20-second intervals

## 适用场景

- 当用户需要 a fancy self-hosted monitoring tool 时
- 当用户想要自动化网页测试时
- 当用户需要跨浏览器测试时

## 常见用法

```bash
# 安装 Playwright
npm install -D @playwright/test

# 运行测试
npx playwright test
```
