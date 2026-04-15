/**
 * Page Agent Executor + Pretext 集成
 * 优化文本测量，减少 DOM reflow
 * 
 * 集成点：
 * 1. 元素文本宽度计算（无 DOM 测量）
 * 2. 元素文本高度计算
 * 3. 文本溢出检测
 * 4. 自适应布局支持
 */

/**
 * Pretext 文本测量集成
 * 
 * 使用方式：
 * const executor = new PageAgentExecutor(document, {
 *   enablePretext: true,
 *   pretextConfig: { ... }
 * })
 */
class PretextIntegration {
  constructor(options = {}) {
    this.enabled = options.enabled !== false
    this.cache = new Map()
    this.cacheSize = options.cacheSize || 500
    this.metrics = {
      calls: 0,
      cacheHits: 0,
      cacheMisses: 0
    }
  }

  /**
   * 计算文本宽度（无 DOM 测量）
   * 
   * @param {string} text - 文本内容
   * @param {string} font - CSS font 简写（如 "14px Inter"）
   * @param {number} maxWidth - 最大宽度（用于换行计算）
   * @returns {number} 文本宽度（像素）
   */
  async calculateTextWidth(text, font, maxWidth = Infinity) {
    if (!this.enabled) {
      return this._estimateWidth(text, font)
    }

    const cacheKey = `width:${text}|${font}|${maxWidth}`
    
    // 检查缓存
    if (this.cache.has(cacheKey)) {
      this.metrics.cacheHits++
      return this.cache.get(cacheKey)
    }

    this.metrics.cacheMisses++
    this.metrics.calls++

    try {
      // 调用 Pretext（需要在浏览器环境中）
      if (typeof window !== 'undefined' && window.Pretext) {
        const { prepare, layoutWithLines } = window.Pretext
        const prepared = prepare(text, font)
        const { lines } = layoutWithLines(prepared, maxWidth, 20)
        
        // 计算最大行宽
        let maxLineWidth = 0
        for (const line of lines) {
          if (line.width > maxLineWidth) {
            maxLineWidth = line.width
          }
        }

        this._cacheResult(cacheKey, maxLineWidth)
        return maxLineWidth
      } else {
        // 降级方案：估算宽度
        return this._estimateWidth(text, font)
      }
    } catch (error) {
      console.warn('Pretext 计算失败，使用估算方案:', error)
      return this._estimateWidth(text, font)
    }
  }

  /**
   * 计算文本高度（无 DOM 测量）
   * 
   * @param {string} text - 文本内容
   * @param {string} font - CSS font 简写
   * @param {number} maxWidth - 最大宽度
   * @param {number} lineHeight - 行高
   * @returns {number} 文本高度（像素）
   */
  async calculateTextHeight(text, font, maxWidth, lineHeight = 20) {
    if (!this.enabled) {
      return this._estimateHeight(text, maxWidth, lineHeight)
    }

    const cacheKey = `height:${text}|${font}|${maxWidth}|${lineHeight}`
    
    if (this.cache.has(cacheKey)) {
      this.metrics.cacheHits++
      return this.cache.get(cacheKey)
    }

    this.metrics.cacheMisses++
    this.metrics.calls++

    try {
      if (typeof window !== 'undefined' && window.Pretext) {
        const { prepare, layout } = window.Pretext
        const prepared = prepare(text, font)
        const { height } = layout(prepared, maxWidth, lineHeight)

        this._cacheResult(cacheKey, height)
        return height
      } else {
        return this._estimateHeight(text, maxWidth, lineHeight)
      }
    } catch (error) {
      console.warn('Pretext 计算失败，使用估算方案:', error)
      return this._estimateHeight(text, maxWidth, lineHeight)
    }
  }

  /**
   * 检测文本是否溢出
   * 
   * @param {string} text - 文本内容
   * @param {string} font - CSS font 简写
   * @param {number} maxWidth - 容器最大宽度
   * @param {number} maxHeight - 容器最大高度
   * @param {number} lineHeight - 行高
   * @returns {Object} { overflow: boolean, reason?: string }
   */
  async detectTextOverflow(text, font, maxWidth, maxHeight, lineHeight = 20) {
    try {
      const height = await this.calculateTextHeight(text, font, maxWidth, lineHeight)
      
      if (height > maxHeight) {
        return {
          overflow: true,
          reason: `文本高度 ${height}px 超过限制 ${maxHeight}px`,
          actualHeight: height
        }
      }

      return { overflow: false }
    } catch (error) {
      return {
        overflow: false,
        warning: `溢出检测失败: ${error.message}`
      }
    }
  }

  /**
   * 估算文本宽度（降级方案）
   * 基于字符数和字体大小的粗略估算
   */
  _estimateWidth(text, font) {
    // 从 font 字符串中提取字体大小
    const sizeMatch = font.match(/(\d+)px/)
    const fontSize = sizeMatch ? parseInt(sizeMatch[1]) : 14

    // 粗略估算：平均字符宽度 = 字体大小 * 0.6
    const avgCharWidth = fontSize * 0.6
    return text.length * avgCharWidth
  }

  /**
   * 估算文本高度（降级方案）
   */
  _estimateHeight(text, maxWidth, lineHeight) {
    const avgCharWidth = 8  // 假设平均字符宽度
    const charsPerLine = Math.max(1, Math.floor(maxWidth / avgCharWidth))
    const lineCount = Math.ceil(text.length / charsPerLine)
    return lineCount * lineHeight
  }

  /**
   * 缓存结果
   */
  _cacheResult(key, value) {
    if (this.cache.size >= this.cacheSize) {
      // FIFO 清理
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }
    this.cache.set(key, value)
  }

  /**
   * 获取性能指标
   */
  getMetrics() {
    const hitRate = this.metrics.calls > 0 
      ? (this.metrics.cacheHits / this.metrics.calls * 100).toFixed(1)
      : 0
    
    return {
      ...this.metrics,
      hitRate: `${hitRate}%`,
      cacheSize: this.cache.size
    }
  }

  /**
   * 清空缓存
   */
  clearCache() {
    this.cache.clear()
  }
}

/**
 * 扩展 PageAgentExecutor 以支持 Pretext
 */
class PageAgentExecutorWithPretext {
  constructor(document, options = {}) {
    this.document = document
    this.options = {
      enableCache: options.enableCache !== false,
      maxHistorySize: options.maxHistorySize || 100,
      autoRetry: options.autoRetry !== false,
      retryAttempts: options.retryAttempts || 3,
      enablePretext: options.enablePretext !== false,
      ...options
    }
    
    this.history = []
    this.domCache = null
    this.domCacheTime = 0
    this.elementIndexMap = new Map()
    this.normalizationCache = new Map()
    
    // 初始化 Pretext 集成
    this.pretext = new PretextIntegration({
      enabled: this.options.enablePretext,
      cacheSize: options.pretextCacheSize || 500
    })
  }

  /**
   * 获取元素的文本宽度（无 DOM 测量）
   * 
   * @param {number} index - 元素索引
   * @returns {Promise<number>} 文本宽度
   */
  async getElementTextWidth(index) {
    const element = this.elementIndexMap.get(index)
    if (!element) {
      throw new Error(`Element with index ${index} not found`)
    }

    const text = element.textContent || ''
    const font = window.getComputedStyle(element).font
    
    return this.pretext.calculateTextWidth(text, font, Infinity)
  }

  /**
   * 获取元素的文本高度（无 DOM 测量）
   * 
   * @param {number} index - 元素索引
   * @param {number} maxWidth - 最大宽度
   * @returns {Promise<number>} 文本高度
   */
  async getElementTextHeight(index, maxWidth) {
    const element = this.elementIndexMap.get(index)
    if (!element) {
      throw new Error(`Element with index ${index} not found`)
    }

    const text = element.textContent || ''
    const font = window.getComputedStyle(element).font
    const lineHeight = parseFloat(window.getComputedStyle(element).lineHeight)

    return this.pretext.calculateTextHeight(text, font, maxWidth, lineHeight)
  }

  /**
   * 检测元素文本是否溢出
   * 
   * @param {number} index - 元素索引
   * @param {number} maxWidth - 容器最大宽度
   * @param {number} maxHeight - 容器最大高度
   * @returns {Promise<Object>} 溢出检测结果
   */
  async detectElementTextOverflow(index, maxWidth, maxHeight) {
    const element = this.elementIndexMap.get(index)
    if (!element) {
      throw new Error(`Element with index ${index} not found`)
    }

    const text = element.textContent || ''
    const font = window.getComputedStyle(element).font
    const lineHeight = parseFloat(window.getComputedStyle(element).lineHeight)

    return this.pretext.detectTextOverflow(text, font, maxWidth, maxHeight, lineHeight)
  }

  /**
   * 获取 Pretext 性能指标
   */
  getPretextMetrics() {
    return this.pretext.getMetrics()
  }

  /**
   * 清空 Pretext 缓存
   */
  clearPretextCache() {
    this.pretext.clearCache()
  }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    PretextIntegration,
    PageAgentExecutorWithPretext
  }
}
