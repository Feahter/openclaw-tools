/**
 * Page Agent Executor - 本地执行引擎
 * 优化的 DOM 解析、工具执行、响应修复、历史管理
 */

class PageAgentExecutor {
  constructor(document, options = {}) {
    this.document = document
    this.options = {
      enableCache: options.enableCache !== false,
      maxHistorySize: options.maxHistorySize || 100,
      autoRetry: options.autoRetry !== false,
      retryAttempts: options.retryAttempts || 3,
      ...options
    }
    
    this.history = []
    this.domCache = null
    this.domCacheTime = 0
    this.elementIndexMap = new Map()
    this.normalizationCache = new Map()
  }

  /**
   * 获取结构化 DOM 文本
   * 优化：只索引可交互元素，保留层级关系
   */
  getDOMAsText() {
    const now = Date.now()
    
    // 缓存检查（5秒内有效）
    if (this.options.enableCache && this.domCache && now - this.domCacheTime < 5000) {
      return this.domCache
    }

    const interactiveSelectors = [
      'button', 'input', 'select', 'textarea', 'a[href]',
      '[role="button"]', '[role="link"]', '[onclick]'
    ]
    
    const elements = []
    const elementMap = new Map()
    let index = 0

    // 深度优先遍历
    const traverse = (node, depth = 0) => {
      if (node.nodeType !== 1) return // 非元素节点跳过

      const isInteractive = interactiveSelectors.some(sel => node.matches(sel))
      
      if (isInteractive) {
        // 检查是否隐藏
        const style = window.getComputedStyle(node)
        if (style.display === 'none' || style.visibility === 'hidden') {
          return
        }

        const text = this._getElementDescription(node)
        const indent = '\t'.repeat(depth)
        elements.push(`${indent}[${index}]${text}`)
        elementMap.set(index, node)
        index++
      }

      // 遍历子节点
      for (const child of node.children) {
        traverse(child, isInteractive ? depth + 1 : depth)
      }
    }

    traverse(this.document.body)

    this.elementIndexMap = elementMap
    const result = elements.join('\n')
    
    if (this.options.enableCache) {
      this.domCache = result
      this.domCacheTime = now
    }

    return result
  }

  /**
   * 获取元素描述
   */
  _getElementDescription(element) {
    const tag = element.tagName.toLowerCase()
    const attrs = []

    // 收集关键属性
    if (element.id) attrs.push(`id="${element.id}"`)
    if (element.className) attrs.push(`class="${element.className}"`)
    if (element.type) attrs.push(`type="${element.type}"`)
    if (element.placeholder) attrs.push(`placeholder="${element.placeholder}"`)
    if (element.value) attrs.push(`value="${element.value}"`)
    if (element.ariaLabel) attrs.push(`aria-label="${element.ariaLabel}"`)

    const attrStr = attrs.length > 0 ? ` ${attrs.join(' ')}` : ''
    const text = element.textContent?.trim().slice(0, 50) || ''
    const textStr = text ? `>${text}</${tag}` : `>`

    return `<${tag}${attrStr}${textStr}`
  }

  /**
   * 点击元素
   */
  async clickElement(index) {
    const element = this.elementIndexMap.get(index)
    if (!element) {
      throw new Error(`Element with index ${index} not found`)
    }

    // 检查是否可交互
    const style = window.getComputedStyle(element)
    if (style.pointerEvents === 'none' || element.disabled) {
      throw new Error(`Element ${index} is not interactive`)
    }

    // 滚动到可见区域
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    await this._wait(100)

    element.click()
    await this._wait(300)

    return { success: true, observation: `Clicked element ${index}` }
  }

  /**
   * 输入文本
   */
  async inputText(index, text) {
    const element = this.elementIndexMap.get(index)
    if (!element) {
      throw new Error(`Element with index ${index} not found`)
    }

    if (!['INPUT', 'TEXTAREA'].includes(element.tagName)) {
      throw new Error(`Element ${index} is not an input field`)
    }

    element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    await this._wait(100)

    element.focus()
    element.value = text
    element.dispatchEvent(new Event('input', { bubbles: true }))
    element.dispatchEvent(new Event('change', { bubbles: true }))
    await this._wait(200)

    return { success: true, observation: `Entered text into element ${index}` }
  }

  /**
   * 清空输入框
   */
  async clearInput(index) {
    const element = this.elementIndexMap.get(index)
    if (!element) {
      throw new Error(`Element with index ${index} not found`)
    }

    element.focus()
    element.value = ''
    element.dispatchEvent(new Event('input', { bubbles: true }))
    await this._wait(100)

    return { success: true, observation: `Cleared input ${index}` }
  }

  /**
   * 滚动页面
   */
  async scroll(options = {}) {
    const { direction = 'down', pages = 1 } = options
    const distance = pages * window.innerHeight

    if (direction === 'down') {
      window.scrollBy(0, distance)
    } else if (direction === 'up') {
      window.scrollBy(0, -distance)
    }

    await this._wait(500)
    return { success: true, observation: `Scrolled ${direction} by ${pages} pages` }
  }

  /**
   * 滚动特定元素
   */
  async scrollElement(index, options = {}) {
    const element = this.elementIndexMap.get(index)
    if (!element) {
      throw new Error(`Element with index ${index} not found`)
    }

    const { direction = 'down', distance = 200 } = options

    if (direction === 'down') {
      element.scrollTop += distance
    } else if (direction === 'up') {
      element.scrollTop -= distance
    }

    await this._wait(300)
    return { success: true, observation: `Scrolled element ${index}` }
  }

  /**
   * 等待
   */
  async wait(seconds) {
    await this._wait(seconds * 1000)
    return { success: true, observation: `Waited ${seconds} seconds` }
  }

  /**
   * 导航
   */
  async navigate(url, options = {}) {
    const { timeout = 10000 } = options

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Navigation timeout after ${timeout}ms`))
      }, timeout)

      window.location.href = url
      window.addEventListener('load', () => {
        clearTimeout(timer)
        resolve({ success: true, observation: `Navigated to ${url}` })
      }, { once: true })
    })
  }

  /**
   * 获取当前 URL
   */
  getCurrentURL() {
    return window.location.href
  }

  /**
   * 获取页面标题
   */
  getPageTitle() {
    return document.title
  }

  /**
   * 按键
   */
  async pressKey(key) {
    const keyMap = {
      'Enter': 'Enter',
      'Escape': 'Escape',
      'Tab': 'Tab',
      'Backspace': 'Backspace',
      'Delete': 'Delete',
      'ArrowUp': 'ArrowUp',
      'ArrowDown': 'ArrowDown',
      'ArrowLeft': 'ArrowLeft',
      'ArrowRight': 'ArrowRight'
    }

    const keyCode = keyMap[key] || key
    const event = new KeyboardEvent('keydown', {
      key: keyCode,
      code: keyCode,
      bubbles: true
    })

    document.activeElement?.dispatchEvent(event)
    await this._wait(100)

    return { success: true, observation: `Pressed key ${key}` }
  }

  /**
   * 获取元素文本
   */
  getElementText(index) {
    const element = this.elementIndexMap.get(index)
    if (!element) {
      throw new Error(`Element with index ${index} not found`)
    }
    return element.textContent?.trim() || ''
  }

  /**
   * 获取元素属性
   */
  getElementAttribute(index, attr) {
    const element = this.elementIndexMap.get(index)
    if (!element) {
      throw new Error(`Element with index ${index} not found`)
    }
    return element.getAttribute(attr) || ''
  }

  /**
   * 修复 LLM 响应
   * 处理常见的格式错误
   */
  normalizeResponse(response) {
    // 缓存检查
    const cacheKey = JSON.stringify(response)
    if (this.normalizationCache.has(cacheKey)) {
      return this.normalizationCache.get(cacheKey)
    }

    let result = null

    try {
      // 情况 1: tool_calls 中有 arguments
      const toolCall = response?.choices?.[0]?.message?.tool_calls?.[0]
      if (toolCall?.function?.arguments) {
        result = this._safeJsonParse(toolCall.function.arguments)
        if (toolCall.function.name && toolCall.function.name !== 'AgentOutput') {
          result = { action: result }
        }
      }

      // 情况 2: content 中有 JSON
      if (!result) {
        const content = response?.choices?.[0]?.message?.content
        if (content) {
          const json = this._extractJson(content)
          if (json) {
            result = this._safeJsonParse(json)
            
            // 处理嵌套包装
            if (result?.name === 'AgentOutput') {
              result = this._safeJsonParse(result.arguments)
            }
            if (result?.type === 'function') {
              result = this._safeJsonParse(result.function.arguments)
            }
            
            // 如果没有 action 字段，假设整个对象就是 action
            if (!result?.action && !result?.evaluation_previous_goal) {
              result = { action: result }
            }
          }
        }
      }

      // 默认为 wait
      if (!result) {
        result = { action: 'wait', seconds: 1 }
      }

      // 缓存结果
      if (this.normalizationCache.size < 100) {
        this.normalizationCache.set(cacheKey, result)
      }

      return result
    } catch (error) {
      console.error('Failed to normalize response:', error)
      return { action: 'wait', seconds: 1 }
    }
  }

  /**
   * 安全的 JSON 解析
   */
  _safeJsonParse(str) {
    if (typeof str !== 'string') return str
    
    try {
      return JSON.parse(str)
    } catch {
      // 尝试去掉转义字符
      try {
        return JSON.parse(str.replace(/\\"/g, '"'))
      } catch {
        return str
      }
    }
  }

  /**
   * 从字符串中提取 JSON
   */
  _extractJson(str) {
    const match = str.match(/\{[\s\S]*\}/)
    return match ? match[0] : null
  }

  /**
   * 记录步骤
   */
  recordStep(step) {
    this.history.push({
      ...step,
      timestamp: step.timestamp || Date.now()
    })

    // 历史压缩
    if (this.history.length > this.options.maxHistorySize) {
      this._compressHistory()
    }
  }

  /**
   * 记录系统消息
   */
  recordSystemMessage(msg) {
    this.history.push({
      type: 'system',
      ...msg,
      timestamp: msg.timestamp || Date.now()
    })
  }

  /**
   * 获取历史
   */
  getHistory() {
    return this.history
  }

  /**
   * 生成反思
   */
  generateReflection() {
    const steps = this.history.filter(h => h.stepNumber)
    const successSteps = steps.filter(s => s.result === 'success').length
    const failedSteps = steps.filter(s => s.result === 'failed').length

    return {
      completedSteps: successSteps,
      failedAttempts: failedSteps,
      totalSteps: steps.length,
      currentState: this._inferState(),
      nextGoal: this._inferNextGoal(),
      memory: this._extractMemory()
    }
  }

  /**
   * 清空历史
   */
  clearHistory() {
    this.history = []
    this.domCache = null
    this.elementIndexMap.clear()
  }

  /**
   * 推断当前状态
   */
  _inferState() {
    if (this.history.length === 0) return 'initial'
    
    const lastStep = this.history[this.history.length - 1]
    if (lastStep.action === 'input_text') return 'form_filling'
    if (lastStep.action === 'click_element') return 'interacting'
    if (lastStep.action === 'scroll') return 'scrolling'
    
    return 'unknown'
  }

  /**
   * 推断下一个目标
   */
  _inferNextGoal() {
    const state = this._inferState()
    
    if (state === 'form_filling') return 'submit_form'
    if (state === 'interacting') return 'wait_for_response'
    if (state === 'scrolling') return 'find_target_element'
    
    return 'continue_task'
  }

  /**
   * 提取记忆（隐敏感信息）
   */
  _extractMemory() {
    const memory = []
    
    for (const step of this.history) {
      if (step.action === 'input_text' && step.params?.text) {
        // 隐敏感信息
        const text = step.params.text
        if (text.includes('@')) {
          memory.push(`Email: ${text.split('@')[0]}@***`)
        } else if (text.length > 10) {
          memory.push(`Text: ${text.slice(0, 10)}...`)
        } else {
          memory.push(`Text: ${text}`)
        }
      }
    }
    
    return memory.join(', ')
  }

  /**
   * 压缩历史
   */
  _compressHistory() {
    // 保留最后 50 步，删除中间的冗余步骤
    if (this.history.length > this.options.maxHistorySize) {
      const toRemove = this.history.length - this.options.maxHistorySize
      this.history.splice(0, toRemove)
    }
  }

  /**
   * 内部等待函数
   */
  _wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PageAgentExecutor
}
