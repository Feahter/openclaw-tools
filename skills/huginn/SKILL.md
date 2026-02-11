---
name: huginn
description: "Create agents that monitor and act on your behalf.  Your agents are standing by!"
triggers:
  - "huginn"
  - "huginn"
  - "huginn" if '/' in full else "huginn"
source:
  project: huginn/huginn
  url: https://github.com/huginn/huginn
  license: MIT
  auto_generated: false
  enhanced_via: skill-creator
  updated_at: 2026-02-11T14:09:59
---

# Huginn

Create agents that monitor and act on your behalf.  Your agents are standing by!

## 项目信息

- **Stars**: 48,677
- **License**: MIT
- **语言**: Ruby
- **GitHub**: [huginn/huginn](https://github.com/huginn/huginn)

## 核心功能

- Track the weather and get an email when it's going to rain (or snow) tomorrow ("Don't forget your umbrella!")
- List terms that you care about and receive email when their occurrence on Twitter changes.  (For example, want to know when something interesting has happened in the world of Machine Learning?  Huginn will watch the term "machine learning" on Twitter and tell you when there is a spike in discussion.)
- Watch for air travel or shopping deals
- Follow your project names on Twitter and get updates when people mention them
- Scrape websites and receive email when they change
- Connect to Adioso, HipChat, FTP, IMAP, Jabber, JIRA, MQT

## 快速开始

```bash
docker run -p 3000:3000 huginn/huginn
```

## 适用场景

- 自动化任务时
- 数据抓取时
- 事件驱动流程
## 注意事项

*基于 huginn/huginn 官方文档生成*
*更新时间: 2026-02-11*
