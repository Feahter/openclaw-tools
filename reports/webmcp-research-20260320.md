# WebMCP 技术深度研究报告

*Created: 2026-03-20*
*Sources: W3C WebMCP Spec, MCP-B Docs, Juejin 技术博客, GitHub (webmachinelearning/webmcp)*

---

## 1. 概述

### 1.1 什么是 WebMCP

WebMCP（Web Machine Learning Context Protocol）是 Google 和 Microsoft 联合提出的 **W3C 标准化草案**，定义了浏览器原生 API，允许网页开发者将页面功能以 MCP Tools 的形式暴露给 AI Agent。

> 官方 Spec：`webmachinelearning.github.io/webmcp`
> GitHub：`github.com/webmachinelearning/webmcp`（⭐ 2.1K，122 forks）
> 当前状态：**实验性**，Chrome 146+ 可用

**一句话定性**：让 AI Agent 能够调用网页上由开发者定义的 JavaScript 函数，而不是自己去解析 DOM。

### 1.2 解决的问题

| 传统方式 | 问题 | WebMCP 方案 |
|---------|------|------------|
| AI 解析整个 DOM | token 消耗大 | 直接调用 tool，token 极低 |
| AI 操作 DOM 元素 | 步骤多、耗时长、容易出错 | 确定性 JS 执行，无耗时 |
| 滚动/隐藏元素 | 可能漏操作 | tool 由开发者保证正确性 |
| AI 猜测操作 | 不准确 | 开发者提供官方 tool |

---

## 2. 核心架构

### 2.1 定位关系图

```
AI Agent（Claude Code / Cursor / 等）
         │
         │ 通过 MCP 协议调用
         ▼
浏览器（Chrome 146+）
         │
         │ navigator.modelContext API
         ▼
网页（WebMCP Server）
         │
         │ registerTool() 暴露
         ▼
页面上的 WebMCP Tools（JS 函数）
```

Web 页面 = MCP Server（但用 client-side JS 实现，而非 backend）

### 2.2 与传统 MCP 的区别

| 维度 | 传统 MCP Server | WebMCP |
|------|----------------|--------|
| 实现位置 | Backend（Python/Node）| 前端 JavaScript |
| Tool 定义 | 代码中硬编码 | `registerTool()` 动态注册 |
| 访问方式 | MCP 协议直连 | 需要打开浏览器访问网页 |
| 适用场景 | API / 数据库 / 文件系统 | Web 页面交互 |
| 上下文 | MCP 协议传输 | 共享当前网页 session |

### 2.3 声明式 vs 命令式

WebMCP 支持两种 Tool 注册方式：

| 方式 | 说明 |
|------|------|
| **命令式（Imperative）** | 调用 `registerTool()`，传入完整 Tool 定义 JS 对象 |
| **声明式（Declarative）** | HTML 中声明 Tool，浏览器自动发现（PR #76，草案阶段）|

声明式仍在提案中，目前主流实现均为命令式。

---

## 3. API 详解

### 3.1 核心 API：`navigator.modelContext`

```typescript
// Navigator 接口扩展
partial interface Navigator {
  [SecureContext, SameObject] readonly attribute ModelContext modelContext;
};

interface ModelContext {
  undefined registerTool(ModelContextTool tool);   // 注册 tool
  undefined unregisterTool(DOMString name);        // 注销 tool
};
```

**Tool 定义结构（ModelContextTool）**：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 唯一标识tool，不能为空 |
| `description` | string | ✅ | 自然语言描述，供 AI 理解用途 |
| `inputSchema` | JSON Schema (string) | ✅ | 参数结构定义 |
| `execute` | ToolExecuteCallback | ✅ | 实际执行的 JS 函数 |
| `readOnlyHint` | boolean | ❌ | 是否只读工具（默认 false）|

**execute 返回格式**：

```typescript
// 返回 ContentBlock 数组
{
  content: [
    { type: 'text', text: '...' },      // 文本
    // { type: 'image', data: '...', mimeType: '...' }, // 图片（待定义）
    // { type: 'resource', ... }                      // 资源（待定义）
  ]
}
```

### 3.2 调试 API：`navigator.modelContextTesting`

Chrome 原生预览版提供，用于调试和测试：

| 方法 | 用途 |
|------|------|
| `listTools()` | 获取所有已注册 tool 的元数据（不含 execute） |
| `executeTool(name, argsJson)` | 执行指定 tool（JSON 字符串传参） |
| `executeTool(name, source)` | 流式执行（ReadableStream + args Promise）|
| `registerToolsChangedCallback(cb)` | 监听 tool 注册/注销事件 |
| `getCrossDocumentScriptToolResult()` | 跨文档声明式 tool 的结果 |

**注意事项**：
- `listTools()` 返回的 `inputSchema` 是序列化后的 JSON 字符串，不是对象
- `executeTool()` 的 `argsJson` 参数必须是 JSON 字符串，不是对象
- 此 API 属于实验性，Chrome 原生和 polyfill 行为略有差异（见下表）

### 3.3 Polyfill vs 原生 vs MCP-B 扩展

| 能力 | Chrome 原生 | @mcp-b/webmcp-polyfill | mcp-b 扩展 |
|------|------------|----------------------|-----------|
| `navigator.modelContext` | ✅ | ✅ | ✅ |
| `navigator.modelContextTesting` | ✅ | 可选安装 | ✅ |
| 声明式 Tool 可见性 | ✅ | ❌ | ❌ |
| `inputSchema` 格式 | JSON string | JSON string | JSON string |
| TypeScript 类型 | ❌ | ✅ @mcp-b/webmcp-types | ✅ |
| MCP 协议传输层 | ❌ | ❌ | ✅ @mcp-b/global |

**选型建议**：
- 当前阶段最佳选择：`@mcp-b/webmcp-polyfill` + TypeScript SDK
- 纯研究/尝鲜：Chrome 146 + `chrome://flags/#enable-webmcp-testing`
- 生产环境：等待 spec 稳定

---

## 4. 工作流程

### 4.1 完整交互链路

```
1. 网页加载 → WebMCP polyfill 初始化
                    ↓
2. 开发者调用 registerTool() → Tool 注册到 navigator.modelContext
                    ↓
3. AI Agent 通过 chrome-devtools-mcp 等连接浏览器
                    ↓
4. AI Agent 读取页面所有 WebMCP Tools（通过 MCP ListTools）
                    ↓
5. AI Agent 根据工具描述和参数 schema，选择调用某个 Tool
                    ↓
6. Tool 在浏览器 context 执行 JS → 返回 ContentBlock 结果
                    ↓
7. AI Agent 根据结果继续对话或操作
```

### 4.2 AI Agent 调用 WebMCP 的 Skill

`SublimeCT/webmcp-agent`（⭐ 3）是专门为 AI Agent 编写的 WebMCP 调用 Skill：

```
px skills add SublimeCT/webmcp-agent

安装目标：Claude Code / Cursor / Cline / Gemini CLI / Codex 等
功能：根据 mcp-b 文档引导 AI Agent 正确调用 WebMCP Tools
```

---

## 5. 技术实现示例

### 5.1 React + Polyfill 最小示例

```tsx
// main.tsx
import { initializeWebMCPPolyfill } from '@mcp-b/webmcp-polyfill';
initializeWebMCPPolyfill();

// App.tsx
import { useWebMCP } from 'usewebmcp';

const INPUT_SCHEMA = {
  type: 'object',
  properties: { name: { type: 'string' } },
} as const;

function App() {
  const helloTool = useWebMCP({
    name: 'say_hello',
    description: 'Returns a hello message',
    inputSchema: INPUT_SCHEMA,
    execute: async (args) => ({
      content: [{ type: 'text', text: `Hello ${args?.name ?? 'world'}!` }],
    }),
  });

  return (
    <div>
      <p>Tool registered: say_hello</p>
      <p>Execution count: {helloTool.state.executionCount}</p>
      <button onClick={() => helloTool.execute({ name: 'React' })}>
        Run Tool
      </button>
    </div>
  );
}
```

### 5.2 购物搜索场景

```javascript
// 购物网站注册搜索工具
navigator.modelContext.registerTool({
  name: 'search_products',
  description: 'Search products with filters: query, minPrice, maxPrice, inStock, sortBy',
  inputSchema: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Search keyword' },
      minPrice: { type: 'number' },
      maxPrice: { type: 'number' },
      inStock: { type: 'boolean' },
      sortBy: { type: 'string', enum: ['price', 'rating', 'relevance'] },
    },
  },
  async execute({ query, minPrice, maxPrice, inStock, sortBy }) {
    // 调用页面已有搜索逻辑
    const results = await pageSearch({ query, minPrice, maxPrice, inStock, sortBy });
    return { content: [{ type: 'text', text: JSON.stringify(results) }] };
  },
});
```

---

## 6. 竞品对比

### 6.1 浏览器操控方案

| 方案 | 实现方式 | Token 消耗 | 准确性 | 速度 | 生态成熟度 |
|------|---------|-----------|--------|------|----------|
| **WebMCP** | 开发者注册 tool | ⭐⭐⭐⭐⭐ 极低 | ⭐⭐⭐⭐⭐ 开发者保证 | ⭐⭐⭐⭐⭐ 即时 | ⭐⭐ 刚起步 |
| **chrome-devtools-mcp** | DevTools Protocol | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 高 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 成熟 |
| **browser-tools-mcp** | DevTools Protocol | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 高 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 成熟 |
| **mcp-chrome 扩展** | Chrome Extension | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 高 | ⭐⭐⭐ 中等 | ⭐⭐⭐ 中等 |
| **OpenCode / pi-agent** | 直接操控 DOM | ⭐⭐ 低 | ⭐⭐ 依赖 AI | ⭐⭐⭐⭐ 较快 | ⭐⭐⭐⭐ 成熟 |

### 6.2 各方案适用场景

| 场景 | 推荐方案 |
|------|---------|
| 开发者已注册 WebMCP Tools | WebMCP |
| 通用网页操控 | chrome-devtools-mcp |
| 需要监控浏览器日志 | browser-tools-mcp |
| 已有 MCP Server 后端 | 传统 MCP |
| AI 自己解析页面 | screenshot + LLM |

---

## 7. 安全模型

### 7.1 已知风险

| 风险 | 描述 | 缓解措施 |
|------|------|---------|
| **权限滥用** | 注册了用户无权操作的 tool | 权限边界需由开发者和浏览器共同保证 |
| **Tool 未清理** | 应移除的 tool 没有 unregister | 使用 `clearContext()` 统一清理 |
| **恶意网页** | 恶意网页注册假的 tool 误导 AI | AI Agent 应验证 tool 来源和签名 |
| **Token 注入** | Tool 返回内容注入恶意 token | 输入输出需做边界处理 |

### 7.2 安全设计

```javascript
// 1. SecureContext 必须
// WebMCP 仅在 HTTPS 或 localhost 下可用

// 2. Tool 只读提示
navigator.modelContext.registerTool({
  name: 'get_user_profile',
  description: 'Read current user profile',
  readOnlyHint: true,  // 提示 AI 此 tool 不会修改状态
  // ...
});

// 3. 主动清理
navigator.modelContext.clearContext(); // 注销所有 tool
```

---

## 8. 局限性

| 局限性 | 说明 |
|--------|------|
| **依赖开发者提供 Tool** | 如果任务没有对应 tool 则无法使用 |
| **必须打开浏览器** | 无法像传统 MCP 那样远程调用 |
| **兼容性问题** | 目前只有 Chrome 146+ 支持，需要 polyfill 兼容旧版 |
| **Spec 仍在变** | 实验性 API，接口可能变化 |
| **调试工具匮乏** | 现有只有 `Model Context Tool Inspector` 插件 |
| **Declarative API 未定** | 声明式 tool 发现仍在草案阶段 |

---

## 9. 应用场景

### 9.1 用户侧场景

| 场景 | 说明 |
|------|------|
| **复杂表单填写** | 几十上百个字段的表单，AI 调用 tool 精确填充 |
| **需要用户确认的生成** | AI 生成数据 → 填入表单 → 用户确认 |
| **多步骤引导操作** | 开发者定义每步 tool，AI 按序调用 |

### 9.2 AI Agent 侧场景

| 场景 | 说明 |
|------|------|
| **节省 token** | 直接调用 tool 而非解析 DOM |
| **100% 准确性** | 复杂操作（如滚动后可见元素）由 tool 保证 |
| **购物/预订** | AI 读取商品列表 → 筛选 → 自动下单 |

### 9.3 软件测试场景

| 场景 | 说明 |
|------|------|
| **E2E 测试** | WebMCP tool = 确定性测试操作，降低 flaky test |
| **复杂表单测试** | tool 直接操作，无需等待 DOM ready |
| **AI 辅助调试** | AI 读取 browser console tool，分析测试失败原因 |

---

## 10. 生态现状

### 10.1 关键项目

| 项目 | Stars | 用途 |
|------|-------|------|
| webmachinelearning/webmcp | ⭐ 2.1K | 官方 W3C Spec |
| chrome-devtools-mcp | 活跃 | DevTools Protocol MCP Server |
| mcp-chrome | ⭐ 10.8K | Chrome Extension MCP Server |
| BrowserMCP/mcp | ⭐ 6.1K | 浏览器 MCP Server |
| SublimeCT/webmcp-agent | ⭐ 3 | AI Agent WebMCP Skill |

### 10.2 相关工具链

| 工具 | 说明 |
|------|------|
| `@mcp-b/webmcp-polyfill` | Polyfill，兼容旧版 Chrome |
| `@mcp-b/webmcp-ts-sdk` | TypeScript SDK，类型安全 |
| `@mcp-b/webmcp-types` | 类型定义包 |
| `usewebmcp` | React Hook for WebMCP |
| `Model Context Tool Inspector` | Chrome 插件，调试工具 |

### 10.3 浏览器支持

| 浏览器 | 支持状态 |
|--------|---------|
| Chrome 146+ | ✅ 原生支持（需开启 flag）|
| Chrome < 146 | ❌ → 需要 polyfill |
| Firefox | ❌ 暂无计划 |
| Safari | ❌ 暂无计划 |
| Edge | 基于 Chromium → 同 Chrome |

---

## 11. 对 OpenClaw 的意义

### 11.1 集成可能性

| 组件 | 如何集成 WebMCP |
|------|----------------|
| **browser tool** | 增强：WebMCP Tool 识别 + 调用 |
| **agent-reach** | 社媒抓取：部分平台可提供 WebMCP Tool |
| **自动化** | 替代部分 DevTools Protocol 操作 |

### 11.2 潜在 Skill 机会

| Skill 名称 | 功能 |
|------------|------|
| `webmcp-discover` | 自动发现网页上的 WebMCP Tools |
| `webmcp-inject` | 在任意网页注入 WebMCP Tools |
| `webmcp-debug` | 调试 WebMCP Tool 注册和调用 |

### 11.3 当前行动建议

1. **观望**：Spec 仍在实验阶段，不建议生产环境使用
2. **尝鲜**：Chrome 146 + polyfill + SublimeCT/webmcp-agent skill
3. **跟进**：关注 W3C Spec 进展，特别是 Declarative API 和安全模型
4. **对比**：与 chrome-devtools-mcp 对比，确认 WebMCP 的实际优势

---

## 12. 总结

| 维度 | 评价 |
|------|------|
| **创新性** | ⭐⭐⭐⭐⭐ 重新定义 AI 与 Web 的交互范式 |
| **成熟度** | ⭐⭐ 早期草案，API 可能变化 |
| **实用性** | ⭐⭐⭐ 特定场景（开发者已提供 tool）非常强，通用场景暂不如 DevTools MCP |
| **标准化** | ⭐⭐⭐⭐ W3C 背书，Chrome + 浏览器厂商支持 |
| **生态潜力** | ⭐⭐⭐⭐⭐ 有望成为 Web AI Agent 的基础设施 |

**一句话总结**：WebMCP 是 AI × Web 的正确方向，但目前还处于"早起"阶段——Spec 不稳、工具链匮乏、浏览器支持有限。真正的价值释放在 Declarative API 定稿 + 主流浏览器跟进之后。

---

## 参考资料

1. W3C WebMCP Spec: https://webmachinelearning.github.io/webmcp/
2. GitHub: https://github.com/webmachinelearning/webmcp
3. MCP-B 文档: https://docs.mcp-b.ai/
4. Juejin 实战指南: https://juejin.cn/post/7618060828450095145
5. chrome-devtools-mcp: https://github.com/ChromeDevTools/chrome-devtools-mcp
6. mcp-chrome: https://github.com/hangwin/mcp-chrome
7. BrowserMCP: https://github.com/BrowserMCP/mcp
8. webmcp-agent Skill: https://github.com/SublimeCT/webmcp-agent
