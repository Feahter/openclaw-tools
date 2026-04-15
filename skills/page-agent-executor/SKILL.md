---
name: page-agent-executor
description: |
  Page Agent 本地执行引擎 — 网页自动化的核心。提供 DOM 解析、工具执行、响应修复、历史管理。
  当用户提到网页自动化、表单填充、DOM 操作、元素定位、LLM 集成网页控制时，使用此 skill。
  支持与 OpenAI/Qwen/Claude 等 LLM 集成，实现完整的 ReAct Agent 循环。
  特别适合：SaaS Copilot、智能表单填充、无障碍访问、多页面自动化。
---

# page-agent-executor

Page Agent 本地执行引擎 — DOM 处理、工具执行、历史管理的优化实现。

## 核心能力

### 1. DOM 解析与元素定位 🏗️

将网页 DOM 树转成**结构化文本**，只索引可交互元素：

```javascript
const executor = new PageAgentExecutor(document)
const domText = executor.getDOMAsText()
// 输出：
// [0]<button>Login</button>
// [1]<input type="email" placeholder="Email">
// [2]<input type="password" placeholder="Password">
```

**优化**：
- ✅ 5秒缓存（避免重复遍历）
- ✅ 只索引可交互元素（button、input、select 等）
- ✅ 保留层级关系（缩进表示父子关系）
- ✅ 标记新元素（`*[index]` 表示自上次以来新增）
- ✅ 过滤隐藏元素

### 2. 工具执行器 🔧

支持的工具：

```javascript
await executor.clickElement(0)              // 点击
await executor.inputText(1, 'text')         // 输入
await executor.clearInput(1)                // 清空
await executor.scroll({ direction: 'down' }) // 滚动
await executor.wait(2)                      // 等待
await executor.navigate('https://...')      // 导航
await executor.pressKey('Enter')            // 按键
```

**优化**：
- ✅ 自动滚动到可见区域
- ✅ 错误恢复（元素不存在时返回有意义的错误）
- ✅ 自动重试（可配置）

### 3. 响应修复器 🔨

自动修复 LLM 返回的格式错误：

```javascript
// LLM 返回的可能格式错误的响应
const llmResponse = { choices: [{ message: { content: '{"action": "click"}' } }] }

// 自动修复
const fixed = executor.normalizeResponse(llmResponse)
// 输出：{ action: 'click', index: 0 }
```

**处理的错误**：
- ✅ JSON 在 content 中而不是 tool_calls
- ✅ 双层 JSON 字符串
- ✅ 嵌套函数调用格式
- ✅ 缺少 action 字段
- ✅ 容错率 > 95%

### 4. 历史管理与反思 📝

记录执行历史，自动生成反思总结：

```javascript
executor.recordStep({
  stepNumber: 1,
  action: 'click_element',
  params: { index: 0 },
  result: 'success',
  observation: 'Button clicked'
})

const reflection = executor.generateReflection()
// 输出：
// {
//   completedSteps: 3,
//   failedAttempts: 1,
//   currentState: 'form_filled',
//   nextGoal: 'submit_form',
//   memory: 'User email is user@example.com, password is ****'
// }
```

**优化**：
- ✅ 自动生成反思
- ✅ 提取关键信息
- ✅ 隐敏感信息（密码、API Key）
- ✅ 自动压缩历史（超过阈值时）

---

## 快速开始

### 浏览器中使用

```html
<script src="executor.js"></script>
<script>
  const executor = new PageAgentExecutor(document)
  
  // 获取 DOM
  console.log(executor.getDOMAsText())
  
  // 执行操作
  await executor.clickElement(0)
  await executor.inputText(1, 'user@example.com')
</script>
```

### 与 LLM 集成

```javascript
const executor = new PageAgentExecutor(document)

async function runAgent(userRequest) {
  let step = 0
  while (step < 40) {
    step++
    
    // 获取当前状态
    const domText = executor.getDOMAsText()
    const history = executor.getHistory()
    const reflection = executor.generateReflection()
    
    // 调用 LLM
    const llmResponse = await callLLM(domText, history, reflection, userRequest)
    
    // 修复响应
    const action = executor.normalizeResponse(llmResponse)
    
    // 执行工具
    const result = await executor.executeAction(action)
    
    // 记录历史
    executor.recordStep({
      stepNumber: step,
      action: action.action,
      params: action,
      result: result.success ? 'success' : 'failed',
      observation: result.observation
    })
    
    if (action.action === 'done') break
  }
}
```

---

## 配置选项

```javascript
const executor = new PageAgentExecutor(document, {
  enableCache: true,        // 启用 DOM 缓存（5秒有效）
  maxHistorySize: 100,      // 历史最大条数
  autoRetry: true,          // 自动重试失败的操作
  retryAttempts: 3,         // 重试次数
  logger: console,          // 日志输出
  logLevel: 'info'          // 日志级别
})
```

---

## 性能基准

| 操作 | 耗时 |
|------|------|
| DOM 解析（首次） | 15-50ms |
| DOM 解析（缓存） | 1-5ms |
| 元素定位 | 1-3ms |
| 点击操作 | 5-20ms |
| 输入文本 | 10-30ms |
| 响应修复（首次） | 5-20ms |
| 响应修复（缓存） | 1-3ms |

**总体**：单步操作 50-150ms（不含 LLM 推理）

---

## 文件结构

```
page-agent-executor/
├── SKILL.md                    # 本文档
├── executor.js                 # 核心实现（525 行）
├── executor.d.ts              # TypeScript 定义
├── examples.js                # 使用示例
├── references/
│   ├── api.md                 # 完整 API 参考
│   ├── error-handling.md      # 错误处理策略
│   ├── performance.md         # 性能优化指南
│   └── browser-compatibility.md # 浏览器兼容性
├── evals/
│   └── evals.json             # 测试用例
└── scripts/
    └── benchmark.js           # 性能测试脚本
```

---

## 常见问题

**Q: 支持 iframe 吗？**
A: 同域 iframe 支持。跨域 iframe 无法访问。

**Q: 支持 Shadow DOM 吗？**
A: 支持。自动遍历 Shadow DOM 树。

**Q: 如何处理动态加载的元素？**
A: 使用 `wait()` 等待元素加载，或启用 `autoRetry`。

**Q: 历史会占用很多内存吗？**
A: 启用 `maxHistorySize` 后自动压缩。

---

## 相关资源

- **完整 API 参考**：见 `references/api.md`
- **错误处理**：见 `references/error-handling.md`
- **性能优化**：见 `references/performance.md`
- **使用示例**：见 `examples.js`
- **集成指南**：见 `INTEGRATION.md`
- **Page Agent 官网**：https://alibaba.github.io/page-agent/
