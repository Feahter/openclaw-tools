---
name: page-agent-research
description: |
  Page Agent 项目研究与集成指南。当用户提到 Page Agent、Alibaba Page Agent、
  浏览器 GUI Agent、网页自动化、DOM 操作 Agent、自然语言控制网页等场景时触发。
  包含项目分析、架构解读、集成方案、对标分析等内容。
---

# page-agent-research

Alibaba Page Agent 项目深度研究与集成指南。

## 项目概览

| 项 | 值 |
|---|---|
| **仓库** | alibaba/page-agent ⭐ 14,371 |
| **语言** | TypeScript 87% + JavaScript 12% |
| **许可** | MIT |
| **创建** | 2025-09-23 |
| **最后更新** | 2026-03-28（非常活跃） |
| **Fork** | 1,104 |
| **Open Issues** | 52 |

## 核心定位

> **Page Agent = 浏览器内的 GUI Agent，用自然语言控制网页**

**本质：**
- 纯 JavaScript 实现的客户端 Agent
- 基于 DOM 文本操作（不需要截图）
- 支持多个 LLM 模型
- 可选 Chrome 扩展用于多页面任务
- MCP Server 支持外部控制

**与 browser-use 的区别：**
- browser-use：服务端自动化（需要后端）
- Page Agent：客户端增强（直接嵌入网页）

## 架构

### Monorepo 结构

```
page-agent/
├── packages/        — 核心包（page-agent 主库）
├── docs/           — 文档（GitHub Pages）
├── scripts/        — 构建脚本
├── AGENTS.md       — Agent 集成指南
├── package.json    — npm workspaces 配置
└── tsconfig.json   — TypeScript 配置
```

### 技术栈

| 层 | 技术 |
|---|---|
| 语言 | TypeScript + JavaScript |
| 构建 | npm workspaces |
| 代码质量 | ESLint + Husky |
| 文档 | GitHub Pages |
| 测试 | Jest（推测） |

## 核心能力

### 1. 文本到 DOM 操作

```javascript
import { PageAgent } from 'page-agent'

const agent = new PageAgent({
    model: 'qwen3.5-plus',
    baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    apiKey: 'YOUR_API_KEY',
    language: 'en-US',
})

// 自然语言控制网页
await agent.execute('Click the login button')
await agent.execute('Fill in the email field with user@example.com')
await agent.execute('Submit the form')
```

### 2. 支持的 LLM

- **Qwen**（阿里云 DashScope）
- **OpenAI**（GPT-4 等）
- **自定义 API**（兼容 OpenAI 格式）

### 3. 集成方式

**方式 A：CDN（最快，用于演示）**
```html
<script src="https://cdn.jsdelivr.net/npm/page-agent@1.6.2/dist/iife/page-agent.demo.js" crossorigin="true"></script>
```

**方式 B：NPM（生产推荐）**
```bash
npm install page-agent
```

**方式 C：Chrome 扩展（多页面任务）**
- 支持跨标签页控制
- 需要单独安装扩展

**方式 D：MCP Server（外部控制）**
- 允许从 Agent 外部控制浏览器
- 支持 Model Context Protocol

## 使用场景

### 1. SaaS AI Copilot
在产品内嵌 AI 助手，无需后端改写。

```javascript
// 在你的 SaaS 应用中
const copilot = new PageAgent({
    model: 'your-model',
    apiKey: process.env.LLM_API_KEY,
})

// 用户说："帮我填充这个表单"
await copilot.execute(userCommand)
```

### 2. 智能表单填充
自动化 ERP/CRM 中的多步骤工作流。

```javascript
// 自动化 20 步的销售流程
await agent.execute('Create a new customer record with name "Acme Corp"')
await agent.execute('Fill in the address field')
await agent.execute('Set the contract amount to $50,000')
await agent.execute('Submit and send confirmation email')
```

### 3. 无障碍访问
为任何网页提供语音命令支持。

```javascript
// 语音输入 → 自然语言 → DOM 操作
const voiceCommand = await speechToText()
await agent.execute(voiceCommand)
```

### 4. 多页面 Agent（Chrome 扩展）
跨标签页自动化复杂工作流。

```javascript
// 在标签页 A 中登录
// 在标签页 B 中填充表单
// 在标签页 C 中提交
```

### 5. MCP 集成
从外部 Agent 控制浏览器。

```bash
# 启动 MCP Server
page-agent --mcp-server

# 外部 Agent 可以调用
agent.call('page-agent', 'execute', { command: 'Click button' })
```

## 快速集成

### 最小化示例

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/page-agent@1.6.2/dist/iife/page-agent.demo.js"></script>
</head>
<body>
    <button id="start">Start Agent</button>
    <script>
        document.getElementById('start').addEventListener('click', async () => {
            const agent = new PageAgent({
                model: 'qwen3.5-plus',
                baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                apiKey: 'YOUR_API_KEY',
            })
            
            await agent.execute('Fill in the form and submit')
        })
    </script>
</body>
</html>
```

### 生产级集成

```typescript
import { PageAgent } from 'page-agent'

class MyAppCopilot {
    private agent: PageAgent
    
    constructor(apiKey: string) {
        this.agent = new PageAgent({
            model: 'gpt-4',
            baseURL: 'https://api.openai.com/v1',
            apiKey: apiKey,
            language: 'en-US',
        })
    }
    
    async handleUserCommand(command: string) {
        try {
            const result = await this.agent.execute(command)
            return { success: true, result }
        } catch (error) {
            return { success: false, error: error.message }
        }
    }
}
```

## 对标分析

| 项目 | 类型 | 部署 | 优势 | 劣势 |
|------|------|------|------|------|
| **Page Agent** | 客户端 Agent | 网页内嵌 | 无需后端，轻量级 | 只能控制当前页面 |
| **browser-use** | 服务端自动化 | 后端服务 | 功能完整，跨页面 | 需要后端改写 |
| **Playwright** | 浏览器控制库 | 后端/CLI | 精细控制，稳定 | 不是 AI 驱动 |
| **Selenium** | 测试框架 | 后端/CLI | 跨浏览器，成熟 | 不是 AI 驱动 |

## 架构亮点

### 1. 极简集成
- 一行 CDN 脚本即可试用
- 无需复杂配置
- 支持多种 LLM

### 2. 轻量级
- 纯 JavaScript
- 无重依赖
- 包体积小

### 3. 灵活
- 支持任何兼容 OpenAI 格式的 LLM API
- 可自定义 prompt
- 支持多种集成方式

### 4. 活跃社区
- 最近更新 2026-03-28
- 1,100+ fork
- 52 个 open issues（说明在积极维护）

## 学习路径

### 初级：快速体验
1. 打开 https://alibaba.github.io/page-agent/
2. 在演示页面试用
3. 用 CDN 脚本在自己的网页上试

### 中级：集成到产品
1. 安装 npm 包
2. 配置 LLM API Key
3. 在应用中创建 PageAgent 实例
4. 处理用户命令

### 高级：扩展功能
1. 研究 packages/ 源码
2. 自定义 prompt 和 DOM 解析
3. 集成 Chrome 扩展
4. 部署 MCP Server

## 常见问题

**Q: Page Agent 能做什么？**
A: 用自然语言控制网页 DOM 操作。比如"点击登录按钮"、"填充表单"、"提交表单"等。

**Q: 需要后端吗？**
A: 不需要。Page Agent 运行在浏览器中，只需要 LLM API Key。

**Q: 支持哪些 LLM？**
A: 任何兼容 OpenAI API 格式的 LLM，包括 Qwen、GPT-4、Claude 等。

**Q: 能跨页面操作吗？**
A: 单页面不行，但可以用 Chrome 扩展实现多页面。

**Q: 性能如何？**
A: 取决于 LLM 响应速度，通常 1-5 秒完成一个操作。

**Q: 安全性？**
A: 代码运行在用户浏览器中，API Key 不会泄露到第三方。

## 资源链接

- **官网**：https://alibaba.github.io/page-agent/
- **GitHub**：https://github.com/alibaba/page-agent
- **文档**：https://alibaba.github.io/page-agent/docs/introduction/overview
- **NPM**：https://www.npmjs.com/package/page-agent
- **HN 讨论**：https://news.ycombinator.com/item?id=47264138

## 版本信息

- **当前版本**：1.6.2
- **发布日期**：2026-03-28
- **License**：MIT
