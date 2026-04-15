# API 参考

## PageAgentExecutor 类

### 构造函数

```javascript
new PageAgentExecutor(document, options?)
```

**参数**：
- `document` (Document) - DOM 文档对象
- `options` (Object, 可选)
  - `enableCache` (boolean, 默认 true) - 启用 DOM 缓存
  - `maxHistorySize` (number, 默认 100) - 历史最大条数
  - `autoRetry` (boolean, 默认 true) - 自动重试
  - `retryAttempts` (number, 默认 3) - 重试次数
  - `logger` (Console, 默认 console) - 日志输出
  - `logLevel` (string, 默认 'info') - 日志级别

---

## DOM 操作方法

### getDOMAsText()

获取结构化 DOM 文本。

```javascript
const domText = executor.getDOMAsText()
```

**返回值**：string - 结构化 DOM 文本

**示例**：
```
[0]<button>Login</button>
[1]<input type="email" placeholder="Email">
[2]<input type="password" placeholder="Password">
[3]<button>Submit</button>
```

---

## 工具执行方法

### clickElement(index)

点击指定索引的元素。

```javascript
await executor.clickElement(0)
```

**参数**：
- `index` (number) - 元素索引

**返回值**：Promise<ExecutionResult>

**异常**：
- `Element with index {index} not found`
- `Element {index} is not interactive`

---

### inputText(index, text)

在指定索引的输入框中输入文本。

```javascript
await executor.inputText(1, 'user@example.com')
```

**参数**：
- `index` (number) - 元素索引
- `text` (string) - 要输入的文本

**返回值**：Promise<ExecutionResult>

**异常**：
- `Element with index {index} not found`
- `Element {index} is not an input field`

---

### clearInput(index)

清空指定索引的输入框。

```javascript
await executor.clearInput(1)
```

**参数**：
- `index` (number) - 元素索引

**返回值**：Promise<ExecutionResult>

---

### scroll(options)

滚动页面。

```javascript
await executor.scroll({ direction: 'down', pages: 1 })
```

**参数**：
- `options` (Object)
  - `direction` (string) - 'up' 或 'down'
  - `pages` (number, 默认 1) - 滚动页数

**返回值**：Promise<ExecutionResult>

---

### scrollElement(index, options)

滚动特定元素。

```javascript
await executor.scrollElement(5, { direction: 'down', distance: 200 })
```

**参数**：
- `index` (number) - 元素索引
- `options` (Object)
  - `direction` (string) - 'up' 或 'down'
  - `distance` (number, 默认 200) - 滚动距离（像素）

**返回值**：Promise<ExecutionResult>

---

### wait(seconds)

等待指定秒数。

```javascript
await executor.wait(2)
```

**参数**：
- `seconds` (number) - 等待秒数

**返回值**：Promise<ExecutionResult>

---

### navigate(url, options?)

导航到指定 URL。

```javascript
await executor.navigate('https://example.com', { timeout: 10000 })
```

**参数**：
- `url` (string) - 目标 URL
- `options` (Object, 可选)
  - `timeout` (number, 默认 10000) - 超时时间（毫秒）

**返回值**：Promise<ExecutionResult>

**异常**：
- `Navigation timeout after {timeout}ms`

---

### pressKey(key)

按下指定按键。

```javascript
await executor.pressKey('Enter')
```

**参数**：
- `key` (string) - 按键名称
  - 'Enter', 'Escape', 'Tab', 'Backspace', 'Delete'
  - 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'

**返回值**：Promise<ExecutionResult>

---

### getCurrentURL()

获取当前页面 URL。

```javascript
const url = executor.getCurrentURL()
```

**返回值**：string - 当前 URL

---

### getPageTitle()

获取当前页面标题。

```javascript
const title = executor.getPageTitle()
```

**返回值**：string - 页面标题

---

### getElementText(index)

获取指定元素的文本内容。

```javascript
const text = executor.getElementText(0)
```

**参数**：
- `index` (number) - 元素索引

**返回值**：string - 元素文本

**异常**：
- `Element with index {index} not found`

---

### getElementAttribute(index, attr)

获取指定元素的属性值。

```javascript
const href = executor.getElementAttribute(0, 'href')
```

**参数**：
- `index` (number) - 元素索引
- `attr` (string) - 属性名

**返回值**：string - 属性值

**异常**：
- `Element with index {index} not found`

---

## 响应处理方法

### normalizeResponse(response)

修复 LLM 返回的格式错误。

```javascript
const action = executor.normalizeResponse(llmResponse)
```

**参数**：
- `response` (Object) - LLM 返回的响应对象

**返回值**：Object - 标准化后的 action 对象

**处理的错误类型**：
- JSON 在 content 中而不是 tool_calls
- 双层 JSON 字符串
- 嵌套函数调用格式
- 缺少 action 字段
- 原始值作为参数

---

## 历史管理方法

### recordStep(step)

记录一个执行步骤。

```javascript
executor.recordStep({
  stepNumber: 1,
  action: 'click_element',
  params: { index: 0 },
  result: 'success',
  observation: 'Button clicked'
})
```

**参数**：
- `step` (Object)
  - `stepNumber` (number) - 步骤号
  - `action` (string) - 操作名称
  - `params` (Object) - 操作参数
  - `result` (string) - 'success' 或 'failed'
  - `observation` (string) - 观察结果
  - `timestamp` (number, 可选) - 时间戳

---

### recordSystemMessage(msg)

记录系统消息。

```javascript
executor.recordSystemMessage({
  type: 'error',
  message: 'Element not found'
})
```

**参数**：
- `msg` (Object)
  - `type` (string) - 消息类型
  - `message` (string) - 消息内容
  - `timestamp` (number, 可选) - 时间戳

---

### getHistory()

获取完整的执行历史。

```javascript
const history = executor.getHistory()
```

**返回值**：Array - 历史事件数组

---

### generateReflection()

生成反思总结。

```javascript
const reflection = executor.generateReflection()
```

**返回值**：Object
- `completedSteps` (number) - 完成的步骤数
- `failedAttempts` (number) - 失败的尝试数
- `totalSteps` (number) - 总步骤数
- `currentState` (string) - 当前状态推断
- `nextGoal` (string) - 下一个目标推断
- `memory` (string) - 提取的记忆（隐敏感信息）

---

### clearHistory()

清空执行历史。

```javascript
executor.clearHistory()
```

---

## 类型定义

### ExecutionResult

```typescript
interface ExecutionResult {
  success: boolean
  observation: string
  error?: string
}
```

### PageAgentExecutorOptions

```typescript
interface PageAgentExecutorOptions {
  enableCache?: boolean
  maxHistorySize?: number
  autoRetry?: boolean
  retryAttempts?: number
  logger?: Console
  logLevel?: 'debug' | 'info' | 'warn' | 'error'
}
```

### HistoryEvent

```typescript
interface HistoryEvent {
  stepNumber?: number
  action?: string
  params?: any
  result?: 'success' | 'failed'
  observation?: string
  type?: string
  message?: string
  timestamp: number
}
```

### Reflection

```typescript
interface Reflection {
  completedSteps: number
  failedAttempts: number
  totalSteps: number
  currentState: string
  nextGoal: string
  memory: string
}
```
