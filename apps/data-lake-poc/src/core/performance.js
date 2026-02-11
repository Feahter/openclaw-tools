/**
 * Performance - 性能优化模块
 * 
 * 功能：
 * - 大数据集分页加载
 * - 虚拟滚动支持
 * - 数据采样
 * - 流式处理
 * - 内存优化
 */

export class VirtualScroll {
  constructor(options = {}) {
    this.itemHeight = options.itemHeight || 40;
    this.containerHeight = options.containerHeight || 400;
    this.buffer = options.buffer || 5;
    this.totalItems = 0;
    this.scrollTop = 0;
  }

  /**
   * 设置总数据量
   */
  setTotalItems(count) {
    this.totalItems = count;
  }

  /**
   * 计算可见范围
   */
  getVisibleRange() {
    const startIndex = Math.floor(this.scrollTop / this.itemHeight);
    const visibleCount = Math.ceil(this.containerHeight / this.itemHeight);
    
    const renderStart = Math.max(0, startIndex - this.buffer);
    const renderEnd = Math.min(this.totalItems, startIndex + visibleCount + this.buffer);
    
    return {
      start: renderStart,
      end: renderEnd,
      offsetY: renderStart * this.itemHeight,
      totalHeight: this.totalItems * this.itemHeight
    };
  }

  /**
   * 更新滚动位置
   */
  updateScrollTop(scrollTop) {
    this.scrollTop = scrollTop;
  }

  /**
   * 生成占位符 HTML
   */
  renderPlaceholder() {
    const range = this.getVisibleRange();
    const visibleItems = range.end - range.start;
    
    return {
      outerHeight: range.totalHeight,
      innerHTML: '',
      startIndex: range.start,
      visibleCount: visibleItems
    };
  }
}

/**
 * 分页加载器
 */
export class PageLoader {
  constructor(options = {}) {
    this.pageSize = options.pageSize || 1000;
    this.cacheSize = options.cacheSize || 3; // 缓存页数
    this.dataLoader = options.dataLoader; // async function(index, size)
    this.cache = new Map(); // pageIndex -> { data, timestamp }
    this.loadedPages = new Set();
    this.loadingPages = new Set();
  }

  /**
   * 加载指定页
   */
  async loadPage(pageIndex) {
    if (this.loadedPages.has(pageIndex)) {
      return this.cache.get(pageIndex);
    }

    if (this.loadingPages.has(pageIndex)) {
      // 等待正在加载的页
      while (this.loadingPages.has(pageIndex)) {
        await this.sleep(50);
      }
      return this.cache.get(pageIndex);
    }

    this.loadingPages.add(pageIndex);
    
    try {
      const data = await this.dataLoader(pageIndex, this.pageSize);
      this.cache.set(pageIndex, { 
        data, 
        timestamp: Date.now(),
        pageIndex 
      });
      this.loadedPages.add(pageIndex);
      
      // 清理旧缓存
      this.cleanupCache(pageIndex);
      
      return data;
    } finally {
      this.loadingPages.delete(pageIndex);
    }
  }

  /**
   * 清理缓存
   */
  cleanupCache(currentPage) {
    const pagesToKeep = new Set([
      currentPage - 1,
      currentPage,
      currentPage + 1
    ]);

    for (const [pageIndex, entry] of this.cache) {
      if (!pagesToKeep.has(pageIndex)) {
        this.cache.delete(pageIndex);
        this.loadedPages.delete(pageIndex);
      }
    }
  }

  /**
   * 预加载相邻页
   */
  async prefetch(pageIndex) {
    const prevPage = pageIndex - 1;
    const nextPage = pageIndex + 1;
    
    if (prevPage >= 0) {
      this.loadPage(prevPage).catch(() => {});
    }
    if (nextPage >= 0) {
      this.loadPage(nextPage).catch(() => {});
    }
  }

  /**
   * 获取总页数
   */
  getTotalPages(totalItems) {
    return Math.ceil(totalItems / this.pageSize);
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 清空缓存
   */
  clear() {
    this.cache.clear();
    this.loadedPages.clear();
    this.loadingPages.clear();
  }
}

/**
 * 数据采样器
 */
export class Sampler {
  /**
   * 简单随机采样
   */
  static randomSample(data, sampleSize) {
    if (data.length <= sampleSize) return data;
    
    const indices = new Set();
    while (indices.size < sampleSize) {
      indices.add(Math.floor(Math.random() * data.length));
    }
    
    return Array.from(indices).map(i => data[i]);
  }

  /**
   * 系统采样（均匀分布）
   */
  static systematicSample(data, sampleSize) {
    if (data.length <= sampleSize) return data;
    
    const step = data.length / sampleSize;
    const sample = [];
    
    for (let i = 0; i < sampleSize; i++) {
      const index = Math.floor(i * step);
      sample.push(data[index]);
    }
    
    return sample;
  }

  /**
   * 分层采样（按字段分层）
   */
  static stratifiedSample(data, stratumField, sampleSize) {
    if (data.length <= sampleSize) return data;
    
    // 分组
    const strata = new Map();
    for (const row of data) {
      const key = String(row[stratumField] || 'unknown');
      if (!strata.has(key)) {
        strata.set(key, []);
      }
      strata.get(key).push(row);
    }

    // 每个分层采样
    const sample = [];
    const samplePerStratum = Math.max(1, Math.floor(sampleSize / strata.size));
    
    for (const [, rows] of strata) {
      const stratumSample = this.systematicSample(rows, samplePerStratum);
      sample.push(...stratumSample);
    }

    return sample.slice(0, sampleSize);
  }

  /**
   * 百分比采样
   */
  static percentSample(data, percent) {
    return this.systematicSample(data, Math.ceil(data.length * percent / 100));
  }
}

/**
 * 流式处理器
 */
export class StreamProcessor {
  constructor(options = {}) {
    this.chunkSize = options.chunkSize || 1000;
    this.onChunk = options.onChunk || (() => {});
    this.onComplete = options.onComplete || (() => {});
    this.onError = options.onError || ((e) => { throw e; });
  }

  /**
   * 处理数据流
   */
  async process(data, options = {}) {
    const total = data.length;
    let processed = 0;
    const results = [];

    for (let i = 0; i < total; i += this.chunkSize) {
      const chunk = data.slice(i, i + this.chunkSize);
      const result = await this.onChunk(chunk, i, total);
      
      if (result !== undefined) {
        results.push(...(Array.isArray(result) ? result : [result]));
      }

      processed += chunk.length;
      
      // 报告进度
      if (options.onProgress) {
        options.onProgress({
          processed,
          total,
          percent: Math.round(processed / total * 100)
        });
      }

      // 让出主线程
      if (options.yield !== false) {
        await this.yield();
      }
    }

    await this.onComplete(results);
    return results;
  }

  /**
   * 让出主线程
   */
  async yield() {
    return new Promise(resolve => setTimeout(resolve, 0));
  }

  /**
   * 从生成器处理
   */
  async *generatorProcess(generator) {
    let chunk = [];
    
    for await (const item of generator) {
      chunk.push(item);
      
      if (chunk.length >= this.chunkSize) {
        const result = await this.onChunk(chunk);
        if (result !== undefined) {
          yield* Array.isArray(result) ? result : [result];
        }
        chunk = [];
      }
    }

    // 处理剩余数据
    if (chunk.length > 0) {
      const result = await this.onChunk(chunk);
      if (result !== undefined) {
        yield* Array.isArray(result) ? result : [result];
      }
    }
  }
}

/**
 * 内存优化器
 */
export class MemoryOptimizer {
  constructor() {
    this.threshold = 50 * 1024 * 1024; // 50MB
    this.gcCallback = null;
  }

  /**
   * 设置 GC 阈值
   */
  setThreshold(bytes) {
    this.threshold = bytes;
  }

  /**
   * 检查是否需要 GC
   */
  shouldGC() {
    if (typeof performance !== 'undefined' && performance.memory) {
      const used = performance.memory.usedJSHeapSize;
      return used > this.threshold;
    }
    return false;
  }

  /**
   * 执行弱引用清理
   */
  async gc() {
    if (this.shouldGC()) {
      // 强制垃圾回收（如果浏览器支持）
      if (typeof window !== 'undefined') {
        // 清理大型对象
        if (window.gc) {
          window.gc();
        }
      }
      
      if (this.gcCallback) {
        await this.gcCallback();
      }
    }
  }

  /**
   * 设置 GC 回调
   */
  onGC(callback) {
    this.gcCallback = callback;
  }

  /**
   * 获取内存使用情况
   */
  getMemoryInfo() {
    if (typeof performance !== 'undefined' && performance.memory) {
      return {
        used: (performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(2) + ' MB',
        total: (performance.memory.totalJSHeapSize / 1024 / 1024).toFixed(2) + ' MB',
        limit: (performance.memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2) + ' MB'
      };
    }
    return null;
  }
}

/**
 * 压缩工具
 */
export class Compression {
  /**
   * 使用 LZ-String 压缩（如果可用）
   */
  static async compress(data) {
    const str = typeof data === 'string' ? data : JSON.stringify(data);
    
    if (typeof window !== 'undefined' && window.LZString) {
      return window.LZString.compressToUTF16(str);
    }
    
    // 简单压缩：移除空白
    return str
      .replace(/\s+/g, ' ')
      .replace(/\s*([{}:,])\s*/g, '$1');
  }

  /**
   * 解压
   */
  static async decompress(compressed) {
    if (typeof window !== 'undefined' && window.LZString) {
      const str = window.LZString.decompressFromUTF16(compressed);
      try {
        return JSON.parse(str);
      } catch {
        return str;
      }
    }
    
    return compressed;
  }

  /**
   * 对象序列化优化
   */
  static optimizeForSerialization(obj) {
    // 移除 undefined 和函数
    return JSON.parse(JSON.stringify(obj, (key, value) => {
      if (typeof value === 'function') {
        return value.toString();
      }
      if (value === undefined) {
        return null;
      }
      return value;
    }));
  }
}
