# WebMCP 最佳实践指南
## 为 Web 项目添加 WebMCP 支持

*Created: 2026-03-20*
*Target: 任意 Web 项目开发者*
*WebMCP 版本: Chrome 146+ 实验性, @mcp-b/webmcp-polyfill v1.x*

---

## 目录

1. [快速入门](#1-快速入门)
2. [Tool 设计原则](#2-tool-设计原则)
3. [项目集成模式](#3-项目集成模式)
4. [安全最佳实践](#4-安全最佳实践)
5. [框架集成示例](#5-框架集成示例)
6. [测试策略](#6-测试策略)
7. [AI Agent 接入](#7-ai-agent-接入)
8. [生命周期管理](#8-生命周期管理)
9. [调试与排错](#9-调试与排错)
10. [升级路线图](#10-升级路线图)

---

## 1. 快速入门

### 1.1 环境要求

| 环境 | 要求 |
|------|------|
| Node.js | ≥ 18 |
| 包管理器 | pnpm / npm / yarn |
| 浏览器 | Chrome 146+（开启 WebMCP Testing Flag）|
| HTTPS | 必须（localhost 除外）|

### 1.2 安装依赖

```bash
# 推荐：pnpm
pnpm add @mcp-b/webmcp-polyfill @mcp-b/webmcp-ts-sdk usewebmcp

# 仅 TypeScript 类型
pnpm add -D @mcp-b/webmcp-types
```

### 1.3 启用 Chrome WebMCP

1. 升级到 Chrome 146+
2. 访问 `chrome://flags/#enable-webmcp-testing`
3. 设为 **Enabled**
4. 重启 Chrome
5. 验证：`chrome://settings/help` 确认版本 ≥ 146

### 1.4 验证安装

```typescript
// main.tsx
import { initializeWebMCPPolyfill } from '@mcp-b/webmcp-polyfill';

initializeWebMCPPolyfill();

// 验证 API 可用
if ('modelContext' in navigator) {
  console.log('WebMCP ready');
  navigator.modelContext.registerTool({
    name: 'ping',
    description: 'Health check tool',
    inputSchema: { type: 'object', properties: {} },
    async execute() {
      return { content: [{ type: 'text', text: 'pong' }] };
    },
  });
}
```

---

## 2. Tool 设计原则

### 2.1 核心原则

**每 1 个 Tool = 1 个原子操作**

```
❌ 错误：tool 太大
name: 'process_order'
execute: async (args) => {
  // 校验库存 → 计算折扣 → 创建订单 → 发货通知 → 发送邮件
  // 5 个操作混在一起，AI 无法选择性调用其中一部分
}

✅ 正确：tool 拆分
name: 'check_inventory'
name: 'calculate_discount'
name: 'create_order'
name: 'send_shipping_notification'
name: 'send_order_email'
```

**每个 Tool 独立幂等**（除非明确设计为事务性）

### 2.2 命名规范

```
规则：
- 小写字母 + 下划线
- 动词开头（说明 action）
- 领域前缀（避免全局冲突）

示例：
  get_user_profile        ✅
  search_products        ✅
  submit_order           ✅
  list_user_orders       ✅

  userProfile           ❌（驼峰）
  getUser              ❌（无领域）
  profile              ❌（无动词）
  Everything           ❌（太大）
```

### 2.3 Description 写作规范

**Description = AI 的决策依据**，决定 AI 是否选择这个 Tool。

```typescript
// ❌ 模糊描述
description: 'Get user data'

// ✅ 具体描述：包含用途、参数含义、返回值
description: `
  Retrieves the authenticated user's profile information.
  Returns: user id, display name, email, account creation date.
  Requires: user is logged in.
  Does NOT modify any data (read-only).
`

// ✅ 带参数说明的描述
description: `
  Search products by keyword with optional filters.
  Required: query (string, min 1 char)
  Optional: category, minPrice, maxPrice, inStock, sortBy
  Returns: array of product objects with id, name, price, rating
`
```

### 2.4 inputSchema 设计

**原则：严格但不冗余**

```typescript
// ✅ 好的 schema：类型明确、有限枚举、必要约束
inputSchema: {
  type: 'object',
  properties: {
    status: {
      type: 'string',
      enum: ['pending', 'processing', 'shipped', 'delivered'],
      description: 'Order status filter'
    },
    limit: {
      type: 'integer',
      minimum: 1,
      maximum: 100,
      default: 20,
      description: 'Max number of results'
    }
  },
  required: ['status']  // 只标记真正必填的
}

// ❌ schema 太宽松
inputSchema: {
  type: 'object',
  properties: {
    data: { type: 'any' }  // AI 不知道该传什么
  }
}

// ❌ schema 太严格
inputSchema: {
  type: 'object',
  properties: {
    query: {
      type: 'string',
      minLength: 1,
      maxLength: 500,
      pattern: '^[a-zA-Z0-9 ]+$',  // 太细节，AI 可能填不对
      description: '...'
    }
  },
  required: ['query', 'page', 'limit', 'sort', 'filter', 'lang']
}
```

### 2.5 返回值规范

```typescript
// ✅ 标准化返回
async execute(args) {
  try {
    const result = await doSomething(args);
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          success: true,
          data: result,
          timestamp: new Date().toISOString()
        })
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          success: false,
          error: error.message
        })
      }]
    };
  }
}

// ✅ 返回结构化数据供 AI 解析
return {
  content: [{
    type: 'text',
    text: JSON.stringify({
      products: [
        { id: 'p1', name: 'Phone', price: 2999 },
        { id: 'p2', name: 'Laptop', price: 7999 }
      ],
      total: 2
    })
  }]
};
```

### 2.6 Tool 分类模式

| 类型 | 模式 | 示例 |
|------|------|------|
| **Query** | 只读，返回数据 | `get_user`, `search_products` |
| **Action** | 执行操作，可能改变状态 | `submit_order`, `cancel_order` |
| **Navigation** | 页面导航 | `go_to_checkout`, `open_order_detail` |
| **Form** | 数据填充/提交 | `fill_address`, `submit_review` |
| **Search** | 带筛选的查询 | `search_products`, `find_orders` |

---

## 3. 项目集成模式

### 3.1 独立模块化（推荐）

```typescript
// webmcp/tools/index.ts
import { registerTool } from '@mcp-b/webmcp-polyfill';

export function registerUserTools() {
  registerTool({
    name: 'get_user_profile',
    description: '...',
    // ...
  });
}

export function registerProductTools() {
  registerTool({
    name: 'search_products',
    description: '...',
    // ...
  });
}

// main.tsx
import { initializeWebMCPPolyfill } from '@mcp-b/webmcp-polyfill';
import { registerUserTools, registerProductTools } from './webmcp/tools';

initializeWebMCPPolyfill().then(() => {
  registerUserTools();
  registerProductTools();
});
```

### 3.2 按路由注册

```typescript
// webmcp/router.ts
import { registerTool, clearContext } from '@mcp-b/webmcp-polyfill';

export function setupWebMCPRouter() {
  // 路由变化时清理旧 tools
  const routes = {
    '/products': () => import('./tools/products'),
    '/cart': () => import('./tools/cart'),
    '/orders': () => import('./tools/orders'),
  };

  async function navigate(path: string) {
    clearContext();  // 清理上一个页面的 tools

    const loader = routes[path];
    if (loader) {
      const module = await loader();
      module.register();  // 注册当前页面的 tools
    }
  }

  return { navigate };
}
```

### 3.3 权限感知注册

```typescript
// webmcp/auth-aware.ts
import { registerTool } from '@mcp-b/webmcp-polyfill';

export function registerToolsForUser(user: User | null) {
  // 基础 tools（无需登录）
  registerPublicTools();

  if (user) {
    // 登录用户专属 tools
    registerAuthenticatedTools(user);

    if (user.role === 'admin') {
      registerAdminTools();
    }
  } else {
    // 未登录用户重定向到登录
    registerLoginRequiredTools();
  }
}
```

---

## 4. 安全最佳实践

### 4.1 身份验证与授权

```typescript
// ❌ 危险：tool 内部未校验用户身份
registerTool({
  name: 'delete_user_account',
  async execute({ userId }) {
    await db.users.delete(userId);  // 任何人可删除任何账户
    return { content: [{ type: 'text', text: 'Done' }] };
  }
});

// ✅ 安全：校验当前 session
registerTool({
  name: 'delete_user_account',
  description: 'Delete the current user account. Requires authentication.',
  inputSchema: {
    type: 'object',
    properties: {
      confirm: { type: 'boolean', description: 'Must be true' }
    },
    required: ['confirm']
  },
  async execute({ confirm }) {
    const session = getCurrentSession();  // 从 cookie/session 获取
    if (!session?.userId) {
      throw new Error('Authentication required');
    }
    if (!confirm) {
      throw new Error('Confirmation required');
    }
    await db.users.delete(session.userId);
    return { content: [{ type: 'text', text: 'Account deleted' }] };
  }
});
```

### 4.2 速率限制

```typescript
// webmcp/rate-limit.ts
const callCounts = new Map<string, number>();

registerTool({
  name: 'search_products',
  async execute(args) {
    const clientId = getClientId();  // 标识调用方
    const count = (callCounts.get(clientId) || 0) + 1;
    callCounts.set(clientId, count);

    if (count > 60) {  // 60 次/分钟
      throw new Error('Rate limit exceeded. Try again in a minute.');
    }

    return doSearch(args);
  }
});

// 定期清理（防止内存泄漏）
setInterval(() => callCounts.clear(), 60_000);
```

### 4.3 输入校验

```typescript
import { z } from 'zod';  // 推荐：schema 校验库

const SearchSchema = z.object({
  query: z.string().min(1).max(200),
  category: z.string().optional(),
  limit: z.number().int().min(1).max(100).default(20),
});

registerTool({
  name: 'search_products',
  inputSchema: {
    type: 'object',
    properties: {
      query: { type: 'string' },
      category: { type: 'string' },
      limit: { type: 'integer' }
    },
    required: ['query']
  },
  async execute(rawArgs) {
    // 用 Zod 做运行时校验
    const args = SearchSchema.parse(rawArgs);
    return doSearch(args);
  }
});
```

### 4.4 敏感数据脱敏

```typescript
async execute(args) {
  const data = await fetchUserData(args.userId);

  // 移除敏感字段再返回
  const sanitized = {
    id: data.id,
    name: data.name,
    email: data.email,
    // 不返回: passwordHash, ssn, creditCardNumber
    // 不返回: internalNotes, adminFlags
  };

  return { content: [{ type: 'text', text: JSON.stringify(sanitized) }] };
}
```

### 4.5 CSRF 保护

```typescript
registerTool({
  name: 'transfer_funds',
  async execute({ to, amount }) {
    // 验证 CSRF token
    const csrfToken = getCSRFTokenFromCookie();
    if (!verifyCSRFToken(csrfToken, 'transfer_funds')) {
      throw new Error('Invalid CSRF token');
    }
    // 执行操作...
  }
});
```

---

## 5. 框架集成示例

### 5.1 React + TypeScript（推荐）

```tsx
// webmcp/react.ts
import { useEffect, useRef } from 'react';
import { initializeWebMCPPolyfill, registerTool } from '@mcp-b/webmcp-polyfill';
import type { ModelContextTool } from '@mcp-b/webmcp-types';

let initialized = false;

export function useWebMCPTool<T extends object>(
  toolDef: Omit<ModelContextTool, 'execute'> & { execute: (args: T) => Promise<any> }
) {
  const toolRef = useRef(toolDef);
  toolRef.current = toolDef;

  useEffect(() => {
    if (!initialized) {
      initializeWebMCPPolyfill();
      initialized = true;
    }

    registerTool({
      ...toolDef,
      name: toolDef.name,
    });
  }, []);
}

// 使用
function ProductSearch() {
  useWebMCPTool({
    name: 'search_products',
    description: 'Search products with filters',
    inputSchema: { type: 'object', properties: { query: { type: 'string' } }, required: ['query'] },
    execute: async ({ query }) => {
      const results = await api.search(query);
      return { content: [{ type: 'text', text: JSON.stringify(results) }] };
    }
  });

  return <div>Product Search</div>;
}
```

### 5.2 Vue 3 + Composition API

```typescript
// webmcp/vue.ts
import { onMounted, onUnmounted } from 'vue';
import { registerTool, unregisterTool } from '@mcp-b/webmcp-polyfill';

export function useWebMCPTool(toolDef: any) {
  onMounted(() => {
    registerTool(toolDef);
  });

  onUnmounted(() => {
    unregisterTool(toolDef.name);
  });
}

// 使用
const searchTool = {
  name: 'search_products',
  description: 'Search products',
  inputSchema: { type: 'object', properties: { q: { type: 'string' } }, required: ['q'] },
  execute: async ({ q }: { q: string }) => {
    const r = await search(q);
    return { content: [{ type: 'text', text: JSON.stringify(r) }] };
  }
};

useWebMCPTool(searchTool);
```

### 5.3 状态同步（重要）

```typescript
// Tool 执行后必须同步 UI 状态
registerTool({
  name: 'add_to_cart',
  description: 'Add item to shopping cart',
  inputSchema: {
    type: 'object',
    properties: {
      productId: { type: 'string' },
      quantity: { type: 'integer', minimum: 1 }
    },
    required: ['productId', 'quantity']
  },
  async execute({ productId, quantity }) {
    // 1. 执行操作
    const cart = await cartStore.add(productId, quantity);

    // 2. 重要：触发 UI 更新（React/Vue 响应式）
    // 如果是原生 JS：
    window.dispatchEvent(new CustomEvent('cart-updated', { detail: cart }));

    // 3. 返回结果
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          success: true,
          cartItemCount: cart.itemCount,
          total: cart.total
        })
      }]
    };
  }
});
```

---

## 6. 测试策略

### 6.1 单元测试

```typescript
// __tests__/tools/product-search.test.ts
import { registerTool, unregisterTool } from '@mcp-b/webmcp-polyfill';
import { initializeWebMCPPolyfill } from '@mcp-b/webmcp-polyfill';

beforeAll(async () => {
  await initializeWebMCPPolyfill();
});

afterEach(() => {
  unregisterTool('search_products');
});

test('search_products returns structured data', async () => {
  registerTool(searchProductsTool);
  const result = await navigator.modelContextTesting?.executeTool(
    'search_products',
    JSON.stringify({ query: 'laptop' })
  );
  const parsed = JSON.parse(result);
  expect(parsed.products).toBeDefined();
  expect(Array.isArray(parsed.products)).toBe(true);
});

test('search_products validates required params', async () => {
  registerTool(searchProductsTool);
  await expect(
    navigator.modelContextTesting?.executeTool('search_products', JSON.stringify({}))
  ).rejects.toThrow();
});
```

### 6.2 集成测试（Playwright + Polyfill）

```typescript
// e2e/webmcp.spec.ts
import { test, expect } from '@playwright/test';

test.describe('WebMCP Tools', () => {
  test('AI Agent can discover and call search_products', async ({ page }) => {
    await page.goto('/products');
    await page.waitForFunction(() => 'modelContext' in navigator);

    // 验证 tool 已注册
    const tools = await page.evaluate(() =>
      navigator.modelContextTesting?.listTools()
    );
    expect(tools).toContainEqual(
      expect.objectContaining({ name: 'search_products' })
    );

    // 模拟 AI 调用
    const result = await page.evaluate(async () => {
      return navigator.modelContextTesting?.executeTool(
        'search_products',
        JSON.stringify({ query: 'phone' })
      );
    });
    const parsed = JSON.parse(result);
    expect(parsed.success).toBe(true);
  });
});
```

### 6.3 AI Agent 集成测试

```typescript
// e2e/ai-agent.spec.ts
test('Claude Code can call WebMCP tool through MCP bridge', async ({ page }) => {
  // 1. 启动 chrome-devtools-mcp 或 mcp-b local relay
  // 2. 连接 AI Agent
  // 3. 访问支持 WebMCP 的页面
  await page.goto('/products');
  await page.waitForFunction(() =>
    navigator.modelContextTesting?.listTools().then(t => t.length > 0)
  );

  // 4. AI Agent 执行任务
  const agent = new ClaudeCodeAgent();
  const result = await agent.execute(`
    Find products matching "laptop", filter by price < 5000,
    and return the top 3 results with prices.
  `);

  // 5. 验证结果
  expect(result).toContain('laptop');
  expect(result.products.length).toBeLessThanOrEqual(3);
});
```

---

## 7. AI Agent 接入

### 7.1 连接方案对比

| 方案 | 原理 | 适用场景 |
|------|------|---------|
| **chrome-devtools-mcp** | DevTools Protocol 连接 Chrome | 通用，推荐 |
| **mcp-b local relay** | MCP over stdio | 开发调试 |
| **BrowserMCP** | Chrome Extension | 快速尝鲜 |
| **mcp-chrome** | Chrome Extension MCP Server | 通用 |

### 7.2 chrome-devtools-mcp 配置

```bash
# 1. 安装 chrome-devtools-mcp
npm install -g chrome-devtools-mcp

# 2. 配置 MCP（Claude Code）
# ~/.claude/settings.json 或项目 .mcp.json
{
  "mcpServers": {
    "chrome": {
      "command": "chrome-devtools-mcp",
      "args": ["--browser", "chrome"]
    }
  }
}
```

### 7.3 AI Agent 调用流程

```
1. AI Agent 读取页面 WebMCP Tools
   → MCP ListTools → DevTools Protocol → navigator.modelContextTesting.listTools()

2. AI Agent 分析 Tools 描述，决定调用哪个
   → Claude Code 分析 description，选择 search_products

3. AI Agent 构造参数，调用 Tool
   → MCP CallTool → DevTools Protocol → navigator.modelContextTesting.executeTool()

4. Tool 执行 JS，返回 ContentBlock
   → 返回 { content: [{ type: 'text', text: '...' }] }

5. AI Agent 解析结果，继续对话或调用更多 Tools
```

---

## 8. 生命周期管理

### 8.1 注册与注销

```typescript
// 页面加载时注册
onMounted(() => {
  registerTool(productTool);
  registerTool(cartTool);
});

// 页面卸载时注销（避免内存泄漏）
onUnmounted(() => {
  unregisterTool('search_products');
  unregisterTool('add_to_cart');
  unregisterTool('view_cart');
});

// SPA 路由切换时
onRouteChange((newPath) => {
  clearContext();  // 注销所有 tools
  registerToolsForRoute(newPath);  // 注册新页面的 tools
});
```

### 8.2 动态注册

```typescript
// 延迟注册：等待数据加载后再注册
async function registerProductTools(productId: string) {
  const product = await fetchProduct(productId);

  registerTool({
    name: `get_product_${productId}`,
    description: `Get details for product ${product.name}`,
    // ...
  });
}
```

### 8.3 Tool 版本管理

```typescript
registerTool({
  name: 'get_user_profile',
  description: `
    [v2] Get user profile. Returns: id, name, email, createdAt.
    v1 deprecated: response format changed on 2026-04-01.
  `,
  inputSchema: { /* v2 schema */ },
  async execute(args) {
    // 实现...
  }
});
```

---

## 9. 调试与排错

### 9.1 Chrome DevTools 调试

```typescript
// 1. 打开 Chrome DevTools → Console
// 2. 检查 WebMCP 可用性
console.log(navigator.modelContext);        // ModelContext 对象
console.log(navigator.modelContextTesting?.listTools());  // 已注册 tools

// 3. 手动调用 tool
const result = await navigator.modelContextTesting?.executeTool(
  'my_tool',
  JSON.stringify({ arg: 'value' })
);
console.log(result);
```

### 9.2 Model Context Tool Inspector

安装 Chrome 插件：`Model Context Tool Inspector`

功能：
- 查看当前页面所有已注册 WebMCP Tools
- 查看每个 tool 的 name / description / inputSchema
- 手动执行 tool，查看参数和返回值
- 监听 tool 注册/注销事件

### 9.3 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `InvalidStateError: Tool already exists` | 同名 tool 已注册 | `unregisterTool()` 后重新 `registerTool()` |
| `SecurityError: Not in secure context` | 非 HTTPS（localhost 除外）| 改用 HTTPS |
| `TypeError: Cannot read properties of undefined` | polyfill 未初始化 | 确保 `initializeWebMCPPolyfill()` 先执行 |
| tool 返回 null | `execute` 函数未返回 | 确保 `execute` 返回 `{ content: [...] }` |
| AI 无法发现 tools | `chrome://flags/#enable-webmcp-testing` 未开启 | 开启 flag 并重启 Chrome |

### 9.4 权限问题排查

```typescript
// 检查当前页面是否有 modelContext
console.assert('modelContext' in navigator, 'WebMCP not available');

// 检查 tool 是否注册成功
const tools = navigator.modelContextTesting?.listTools();
console.log(`Registered ${tools?.length} tools:`, tools?.map(t => t.name));
```

---

## 10. 升级路线图

### Phase 1: MVP（当前阶段）

```
目标：在现有 Web 项目中最小成本添加 WebMCP 支持

步骤：
1. 安装 @mcp-b/webmcp-polyfill
2. 封装公共 initialize 函数
3. 选择 2-3 个核心 tools 实现（search_products, add_to_cart 等）
4. 使用 Model Context Tool Inspector 手动验证
5. 通过 chrome-devtools-mcp 连接 AI Agent 测试
```

### Phase 2: 生产准备

```
目标：具备生产环境条件

步骤：
1. 完善 inputSchema 校验（集成 Zod）
2. 添加速率限制和身份验证
3. 编写 E2E 测试（Playwright + WebMCP Testing API）
4. 准备 MCP Server 部署（chrome-devtools-mcp 或 mcp-b relay）
5. 制定 Tool 文档，供 AI Agent 开发者使用
```

### Phase 3: 生态扩展

```
目标：形成开发者生态

步骤：
1. 发布 Tool 发现 API（让 AI Agent 知道页面支持哪些 tools）
2. 支持 Declarative WebMCP（HTML 声明式 tool，减少 JS 依赖）
3. 建设 Tool 市场（让跨站 tool 发现成为可能）
4. 集成 Analytics（追踪 tool 调用频率、成功率）
```

---

## 检查清单

### 上线前必检

- [ ] `chrome://flags/#enable-webmcp-testing` 已开启（本地测试）
- [ ] 所有 tools 已通过 `navigator.modelContextTesting.listTools()` 验证
- [ ] inputSchema 通过 Zod 或等价校验库验证
- [ ] 所有需要认证的 tools 已校验 session
- [ ] 速率限制已实施
- [ ] 敏感数据已脱敏
- [ ] 返回值格式符合 `ContentBlock` 标准
- [ ] 页面卸载时所有 tools 已注销
- [ ] E2E 测试覆盖核心 tools
- [ ] Model Context Tool Inspector 手动验证通过

### 安全审计

- [ ] 无未授权操作风险（CRUD 操作已校验权限）
- [ ] CSRF token 验证（状态变更操作）
- [ ] 速率限制（防止 DoS）
- [ ] 输入校验（Zod 或等价方案）
- [ ] 敏感数据不泄露

---

## 参考资源

- [W3C WebMCP Spec](https://webmachinelearning.github.io/webmcp/)
- [MCP-B 官方文档](https://docs.mcp-b.ai/)
- [WebMCP Proposal (GitHub)](https://github.com/webmachinelearning/webmcp/blob/main/docs/proposal.md)
- [@mcp-b/webmcp-polyfill](https://www.npmjs.com/package/@mcp-b/webmcp-polyfill)
- [usewebmcp (React Hook)](https://www.npmjs.com/package/usewebmcp)
- [Model Context Tool Inspector (Chrome 插件)](https://chromewebstore.google.com/detail/model-context-tool-inspec/gbpdfapgefenggkahomfgkhfehlcenpd)
