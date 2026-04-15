/**
 * 小说创作 Canvas 渲染模块
 * 使用 Pretext 进行精确文本布局和 Canvas 渲染
 * 
 * 功能：
 * 1. 精确文本布局
 * 2. Canvas 渲染
 * 3. 多语言支持
 * 4. 自定义样式
 */

/**
 * 小说文本渲染器
 */
class NovelTextRenderer {
  constructor(canvas, options = {}) {
    this.canvas = canvas
    this.ctx = canvas.getContext('2d')
    this.options = {
      font: options.font || '16px 宋体',
      lineHeight: options.lineHeight || 28,
      maxWidth: options.maxWidth || canvas.width - 40,
      padding: options.padding || 20,
      textColor: options.textColor || '#000',
      backgroundColor: options.backgroundColor || '#fff',
      enablePretext: options.enablePretext !== false,
      ...options
    }
    
    this.lines = []
    this.metrics = {}
  }

  /**
   * 渲染文本
   * 
   * @param {string} text - 要渲染的文本
   * @returns {Object} 渲染结果
   */
  async render(text) {
    // 清空画布
    this.ctx.fillStyle = this.options.backgroundColor
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height)

    // 布局文本
    const lines = await this._layoutText(text)
    this.lines = lines

    // 计算总高度
    const totalHeight = lines.length * this.options.lineHeight + this.options.padding * 2

    // 调整画布高度
    if (totalHeight > this.canvas.height) {
      this.canvas.height = totalHeight
    }

    // 渲染背景
    this.ctx.fillStyle = this.options.backgroundColor
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height)

    // 渲染文本
    this.ctx.fillStyle = this.options.textColor
    this.ctx.font = this.options.font

    let y = this.options.padding + this.options.lineHeight
    for (const line of lines) {
      this.ctx.fillText(line, this.options.padding, y)
      y += this.options.lineHeight
    }

    return {
      success: true,
      lineCount: lines.length,
      totalHeight,
      canvasHeight: this.canvas.height
    }
  }

  /**
   * 布局文本（使用 Pretext）
   */
  async _layoutText(text) {
    if (!this.options.enablePretext || !window.Pretext) {
      // 降级方案：简单分行
      return this._simpleLayout(text)
    }

    try {
      const { prepareWithSegments, layoutWithLines } = window.Pretext
      const prepared = prepareWithSegments(text, this.options.font)
      const { lines } = layoutWithLines(
        prepared,
        this.options.maxWidth,
        this.options.lineHeight
      )

      return lines.map(line => line.text)
    } catch (error) {
      console.warn('Pretext 布局失败，使用降级方案:', error)
      return this._simpleLayout(text)
    }
  }

  /**
   * 简单布局（降级方案）
   */
  _simpleLayout(text) {
    const lines = []
    const chars = text.split('')
    let currentLine = ''

    for (const char of chars) {
      const testLine = currentLine + char
      const width = this.ctx.measureText(testLine).width

      if (width > this.options.maxWidth && currentLine) {
        lines.push(currentLine)
        currentLine = char
      } else {
        currentLine = testLine
      }
    }

    if (currentLine) {
      lines.push(currentLine)
    }

    return lines
  }

  /**
   * 获取渲染指标
   */
  getMetrics() {
    return {
      lineCount: this.lines.length,
      totalHeight: this.lines.length * this.options.lineHeight + this.options.padding * 2,
      canvasHeight: this.canvas.height,
      canvasWidth: this.canvas.width,
      font: this.options.font,
      lineHeight: this.options.lineHeight
    }
  }

  /**
   * 导出为图片
   */
  exportAsImage(filename = 'novel.png') {
    const link = document.createElement('a')
    link.href = this.canvas.toDataURL('image/png')
    link.download = filename
    link.click()
  }

  /**
   * 导出为 PDF（需要 jsPDF）
   */
  async exportAsPDF(filename = 'novel.pdf') {
    if (typeof jsPDF === 'undefined') {
      console.error('jsPDF 未加载')
      return
    }

    const { jsPDF } = window
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    const imgData = this.canvas.toDataURL('image/png')
    const imgWidth = 210  // A4 宽度
    const imgHeight = (this.canvas.height / this.canvas.width) * imgWidth

    pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight)
    pdf.save(filename)
  }
}

/**
 * 小说编辑器
 */
class NovelEditor {
  constructor(containerSelector, options = {}) {
    this.container = document.querySelector(containerSelector)
    this.options = options

    // 创建编辑器 UI
    this._createUI()
  }

  /**
   * 创建编辑器 UI
   */
  _createUI() {
    this.container.innerHTML = `
      <div class="novel-editor">
        <div class="editor-toolbar">
          <button id="render-btn">渲染预览</button>
          <button id="export-png-btn">导出 PNG</button>
          <button id="export-pdf-btn">导出 PDF</button>
          <button id="clear-btn">清空</button>
        </div>
        <div class="editor-content">
          <textarea id="text-input" placeholder="输入小说文本..."></textarea>
          <canvas id="preview-canvas"></canvas>
        </div>
      </div>
    `

    // 添加样式
    const style = document.createElement('style')
    style.textContent = `
      .novel-editor {
        display: flex;
        flex-direction: column;
        height: 100%;
        font-family: 宋体, serif;
      }
      
      .editor-toolbar {
        display: flex;
        gap: 10px;
        padding: 10px;
        background: #f5f5f5;
        border-bottom: 1px solid #ddd;
      }
      
      .editor-toolbar button {
        padding: 8px 16px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
      }
      
      .editor-toolbar button:hover {
        background: #0056b3;
      }
      
      .editor-content {
        display: flex;
        flex: 1;
        gap: 10px;
        padding: 10px;
      }
      
      #text-input {
        flex: 1;
        padding: 10px;
        font-family: 宋体, serif;
        font-size: 16px;
        line-height: 1.8;
        border: 1px solid #ddd;
        border-radius: 4px;
        resize: none;
      }
      
      #preview-canvas {
        flex: 1;
        border: 1px solid #ddd;
        border-radius: 4px;
        background: white;
      }
    `
    document.head.appendChild(style)

    // 绑定事件
    this._bindEvents()
  }

  /**
   * 绑定事件
   */
  _bindEvents() {
    const textInput = document.getElementById('text-input')
    const canvas = document.getElementById('preview-canvas')
    const renderBtn = document.getElementById('render-btn')
    const exportPngBtn = document.getElementById('export-png-btn')
    const exportPdfBtn = document.getElementById('export-pdf-btn')
    const clearBtn = document.getElementById('clear-btn')

    this.renderer = new NovelTextRenderer(canvas, this.options)

    renderBtn.addEventListener('click', async () => {
      const text = textInput.value
      if (text) {
        await this.renderer.render(text)
      }
    })

    exportPngBtn.addEventListener('click', () => {
      this.renderer.exportAsImage('novel.png')
    })

    exportPdfBtn.addEventListener('click', async () => {
      await this.renderer.exportAsPDF('novel.pdf')
    })

    clearBtn.addEventListener('click', () => {
      textInput.value = ''
      const ctx = canvas.getContext('2d')
      ctx.fillStyle = '#fff'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
    })

    // 自动渲染
    textInput.addEventListener('input', async () => {
      const text = textInput.value
      if (text) {
        await this.renderer.render(text)
      }
    })
  }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    NovelTextRenderer,
    NovelEditor
  }
}
