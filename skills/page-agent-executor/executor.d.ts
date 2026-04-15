/**
 * Page Agent Executor - TypeScript 类型定义
 */

// ============================================================
// 配置类型
// ============================================================

export interface PageAgentExecutorOptions {
  /** 是否启用 DOM 缓存（默认 true，5秒有效期） */
  enableCache?: boolean
  /** 历史记录最大条数（默认 100） */
  maxHistorySize?: number
  /** 是否自动重试（默认 true） */
  autoRetry?: boolean
  /** 重试次数（默认 3） */
  retryAttempts?: number
}

export interface PageAgentExecutorWithPretextOptions extends PageAgentExecutorOptions {
  /** 是否启用 Pretext 文本测量（默认 true） */
  enablePretext?: boolean
  /** Pretext 缓存大小（默认 500） */
  pretextCacheSize?: number
}

// ============================================================
// DOM 解析类型
// ============================================================

export interface DOMElement {
  index: number
  tag: string
  text: string
  role?: string
  type?: string
  placeholder?: string
  href?: string
  depth: number
}

// ============================================================
// 工具执行类型
// ============================================================

export type ToolName =
  | 'click'
  | 'input'
  | 'scroll'
  | 'hover'
  | 'select'
  | 'submit'
  | 'wait'
  | 'navigate'

export interface ToolCall {
  tool: ToolName
  index?: number
  value?: string
  direction?: 'up' | 'down'
  url?: string
  ms?: number
}

export interface ToolResult {
  success: boolean
  message?: string
  error?: string
}

// ============================================================
// 响应修复类型
// ============================================================

export interface NormalizeOptions {
  strict?: boolean
}

// ============================================================
// 历史管理类型
// ============================================================

export interface HistoryEntry {
  timestamp: number
  domSnapshot: string
  toolCall: ToolCall
  result: ToolResult
  reflection?: string
}

// ============================================================
// Pretext 集成类型
// ============================================================

export interface PretextMetrics {
  calls: number
  cacheHits: number
  cacheMisses: number
  hitRate: string
  cacheSize: number
}

export interface OverflowResult {
  overflow: boolean
  reason?: string
  actualHeight?: number
  warning?: string
}

// ============================================================
// 主类定义
// ============================================================

export declare class PageAgentExecutor {
  constructor(document: Document, options?: PageAgentExecutorOptions)

  /** 获取结构化 DOM 文本（带缓存） */
  getDOMAsText(): string

  /** 执行工具调用 */
  executeTool(toolCall: ToolCall): Promise<ToolResult>

  /** 修复/规范化 LLM 响应 */
  normalizeResponse(response: string, options?: NormalizeOptions): ToolCall | null

  /** 添加历史记录 */
  addHistory(entry: Omit<HistoryEntry, 'timestamp'>): void

  /** 获取历史摘要（用于 LLM 上下文） */
  getHistorySummary(maxEntries?: number): string

  /** 反思历史，生成改进建议 */
  reflectOnHistory(): string

  /** 清空 DOM 缓存 */
  clearDOMCache(): void

  /** 清空历史 */
  clearHistory(): void
}

export declare class PageAgentExecutorWithPretext extends PageAgentExecutor {
  constructor(document: Document, options?: PageAgentExecutorWithPretextOptions)

  /** 获取元素文本宽度（无 DOM 测量） */
  getElementTextWidth(index: number): Promise<number>

  /** 获取元素文本高度（无 DOM 测量） */
  getElementTextHeight(index: number, maxWidth: number): Promise<number>

  /** 检测元素文本是否溢出 */
  detectElementTextOverflow(index: number, maxWidth: number, maxHeight: number): Promise<OverflowResult>

  /** 获取 Pretext 性能指标 */
  getPretextMetrics(): PretextMetrics

  /** 清空 Pretext 缓存 */
  clearPretextCache(): void
}

export declare class PretextIntegration {
  constructor(options?: { enabled?: boolean; cacheSize?: number })

  calculateTextWidth(text: string, font: string, maxWidth?: number): Promise<number>
  calculateTextHeight(text: string, font: string, maxWidth: number, lineHeight?: number): Promise<number>
  detectTextOverflow(text: string, font: string, maxWidth: number, maxHeight: number, lineHeight?: number): Promise<OverflowResult>
  getMetrics(): PretextMetrics
  clearCache(): void
}
