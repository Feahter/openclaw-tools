---
name: smart-browser
description: AI增强的智能浏览器自动化 - 基于agent-browser，添加页面结构分析和智能数据提取
version: 1.0.0
triggers:
  - "智能抓取"
  - "AI爬虫"
  - "智能提取网页数据"
  - "browser ai"
metadata:
  emoji: 🧠
  requires:
    bins: ["node", "npm", "agent-browser"]
    skills: ["agent-browser-0"]
---

# Smart Browser - AI增强浏览器自动化

## 概述

在 agent-browser 基础上增加 AI 分析能力，实现"看见→理解→提取"的端到端自动化。

## 核心能力

| 能力 | 说明 |
|------|------|
| 页面结构分析 | 将DOM发送给LLM，识别数据容器、分页、字段映射 |
| 智能选择器 | AI生成最优CSS选择器 |
| 自适应爬取 | 自动处理懒加载、分页、多Tab |
| 结构化输出 | Markdown/JSON格式 |

## 安装

需要先安装 agent-browser:

```bash
npm install -g agent-browser
agent-browser install
```

## 使用方式

### 1. 智能抓取页面
```
"抓取 https://example.com/events，提取所有活动标题、时间、地点"
```

### 2. 智能提取数据
```
"分析当前页面结构，提取商品名称和价格"
```

### 3. 多Tab遍历
```
"遍历所有Tab页，提取每页的数据"
```

## 技术架构

### 模块结构

```
smart-browser/
├── index.js          # 主入口，暴露自然语言接口
├── analyzer.js       # 页面结构分析（LLM驱动）
├── extractor.js      # 数据提取器
├── crawler.js        # 多Tab/分页爬取
└── formatter.js      # 输出格式化
```

### 依赖

- agent-browser: 底层浏览器控制
- LLM API: 页面分析（调用OpenClaw内置LLM）

## 工作流程

1. **截图+DOM** → agent-browser获取页面快照
2. **AI分析** → LLM识别页面结构，生成提取计划
3. **执行提取** → 按计划提取数据
4. **格式化输出** → 返回Markdown/JSON

## 示例

```bash
# 通过OpenClaw调用
smart-browser.crawl url="https://example.com" intent="提取所有商品"
```

## 待实现

- [ ] index.js 主入口
- [ ] analyzer.js 页面分析
- [ ] extractor.js 数据提取
- [ ] crawler.js 多Tab爬取
- [ ] formatter.js 输出格式化
