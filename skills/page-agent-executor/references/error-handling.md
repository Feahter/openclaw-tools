# 错误处理指南

## 常见错误类型

### 1. 元素不存在

**错误**：`Element with index {index} not found`

**原因**：
- 元素索引超出范围
- 元素被删除或隐藏
- DOM 结构改变

**解决方案**：
```javascript
try {
  await executor.clickElement(999)
} catch (error) {
  if (error.message.includes('not found')) {
    // 重新获取 DOM
    const domText = executor.getDOMAsText()
    console.log('Updated DOM:', domText)
    
    // 重试
    await executor.clickElement(0)
  }
}
```

---

### 2. 元素不可交互

**错误**：`Element {index} is not interactive`

**原因**：
- 元素被禁用（disabled）
- 元素的 pointer-events 为 none
- 元素被其他元素遮挡

**解决方案**：
```javascript
try {
  await executor.clickElement(0)
} catch (error) {
  if (error.message.includes('not interactive')) {
    // 尝试滚动到可见区域
    await executor.scroll({ direction: 'up', pages: 1 })
    await executor.wait(1)
    
    // 重试
    await executor.clickElement(0)
  }
}
```

---

### 3. 输入框类型错误

**错误**：`Element {index} is not an input field`

**原因**：
- 尝试在非输入框元素上输入文本
- 元素类型不是 INPUT 或 TEXTAREA

**解决方案**：
```javascript
try {
  await executor.inputText(0, 'text')
} catch (error) {
  if (error.message.includes('not an input field')) {
    // 检查元素类型
    const text = executor.getElementText(0)
    console.log('Element text:', text)
    
    // 找到正确的输入框
    const domText = executor.getDOMAsText()
    console.log('Available elements:', domText)
  }
}
```

---

### 4. 导航超时

**错误**：`Navigation timeout after {timeout}ms`

**原因**：
- 页面加载太慢
- 网络连接不稳定
- 页面陷入加载循环

**解决方案**：
```javascript
try {
  await executor.navigate('https://example.com', { timeout: 5000 })
} catch (error) {
  if (error.message.includes('timeout')) {
    // 增加超时时间
    await executor.navigate('https://example.com', { timeout: 15000 })
  }
}
```

---

## 自动重试机制

### 启用自动重试

```javascript
const executor = new PageAgentExecutor(document, {
  autoRetry: true,
  retryAttempts: 3
})
```

### 自定义重试策略

```javascript
class CustomExecutor extends PageAgentExecutor {
  async clickElement(index) {
    let lastError
    
    for (let attempt = 0; attempt < this.options.retryAttempts; attempt++) {
      try {
        return await super.clickElement(index)
      } catch (error) {
        lastError = error
        
        if (attempt < this.options.retryAttempts - 1) {
          // 指数退避
          const delay = Math.pow(2, attempt) * 100
          await this._wait(delay)
          
          // 重新获取 DOM
          this.domCache = null
        }
      }
    }
    
    throw lastError
  }
}
```

---

## 错误恢复策略

### 策略 1: 重新获取 DOM

当元素不存在时，重新获取 DOM 并重试：

```javascript
async function robustClickElement(executor, index, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await executor.clickElement(index)
    } catch (error) {
      if (error.message.includes('not found')) {
        // 清除缓存，重新获取 DOM
        executor.domCache = null
        await executor.wait(0.5)
      } else {
        throw error
      }
    }
  }
}
```

### 策略 2: 滚动到可见区域

当元素不可交互时，尝试滚动：

```javascript
async function scrollAndClick(executor, index) {
  try {
    return await executor.clickElement(index)
  } catch (error) {
    if (error.message.includes('not interactive')) {
      // 尝试向上滚动
      await executor.scroll({ direction: 'up', pages: 1 })
      await executor.wait(1)
      return await executor.clickElement(index)
    }
    throw error
  }
}
```

### 策略 3: 等待元素加载

当元素不存在时，等待后重试：

```javascript
async function waitAndClick(executor, index, maxWait = 5) {
  const startTime = Date.now()
  
  while (Date.now() - startTime < maxWait * 1000) {
    try {
      return await executor.clickElement(index)
    } catch (error) {
      if (error.message.includes('not found')) {
        await executor.wait(0.5)
      } else {
        throw error
      }
    }
  }
  
  throw new Error(`Element ${index} not found after ${maxWait}s`)
}
```

---

## 日志和调试

### 启用调试日志

```javascript
const executor = new PageAgentExecutor(document, {
  logLevel: 'debug'
})
```

### 自定义日志输出

```javascript
const executor = new PageAgentExecutor(document, {
  logger: {
    debug: (msg, data) => console.log(`[DEBUG] ${msg}`, data),
    info: (msg, data) => console.log(`[INFO] ${msg}`, data),
    warn: (msg, data) => console.warn(`[WARN] ${msg}`, data),
    error: (msg, data) => console.error(`[ERROR] ${msg}`, data)
  },
  logLevel: 'debug'
})
```

### 记录错误上下文

```javascript
async function executeWithContext(executor, action) {
  try {
    return await executor.executeAction(action)
  } catch (error) {
    // 记录错误上下文
    const context = {
      action: action,
      domText: executor.getDOMAsText(),
      history: executor.getHistory(),
      reflection: executor.generateReflection(),
      error: error.message
    }
    
    console.error('Execution failed:', context)
    throw error
  }
}
```

---

## 常见问题排查

### 问题 1: 元素索引不稳定

**症状**：同一个元素的索引在不同时间不同

**原因**：DOM 结构改变，新元素被添加或删除

**解决**：
```javascript
// 每次操作前重新获取 DOM
const domText = executor.getDOMAsText()

// 或者禁用缓存
const executor = new PageAgentExecutor(document, {
  enableCache: false
})
```

### 问题 2: 响应修复失败

**症状**：normalizeResponse 返回错误的 action

**原因**：LLM 返回的格式不在预期范围内

**解决**：
```javascript
// 添加自定义修复规则
function customNormalize(response) {
  const result = executor.normalizeResponse(response)
  
  // 如果修复失败，尝试自定义规则
  if (!result.action) {
    // 自定义逻辑
    result.action = 'wait'
  }
  
  return result
}
```

### 问题 3: 历史占用过多内存

**症状**：长时间运行后内存占用不断增加

**原因**：历史记录没有被压缩

**解决**：
```javascript
const executor = new PageAgentExecutor(document, {
  maxHistorySize: 50  // 减小历史大小
})

// 或者手动清理
if (executor.getHistory().length > 100) {
  executor.clearHistory()
}
```

---

## 最佳实践

1. **总是使用 try-catch**：捕获所有可能的错误
2. **实现重试逻辑**：对于临时错误（超时、元素不存在）
3. **记录错误上下文**：便于调试
4. **定期清理历史**：避免内存泄漏
5. **监控性能指标**：及时发现问题
6. **测试边界情况**：iframe、Shadow DOM、动态加载等
