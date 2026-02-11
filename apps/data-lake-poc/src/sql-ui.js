/**
 * SQL Query UI - SQL 查询界面
 */

import { DataLake } from './core/datalake.js';
import { CSVAdapter } from './adapters/csv.js';
import { JSONAdapter } from './adapters/json.js';
import { SQLiteAdapter } from './adapters/sqlite.js';
import { IndexedDBStorage } from './storage/indexeddb.js';
import { VirtualScroll, MemoryOptimizer } from './core/performance.js';

class SQLQueryUI {
  constructor() {
    this.lake = new DataLake({ name: 'Data Lake SQL' });
    this.sqlite = new SQLiteAdapter(this.lake);
    this.memory = new MemoryOptimizer();
    this.virtualScroll = null;
    this.currentResults = [];
    this.currentQuery = '';
  }

  /**
   * 初始化
   */
  async init() {
    console.log('🚀 SQL Query UI 初始化...');

    // 初始化存储
    try {
      const storage = new IndexedDBStorage('data-lake-sql');
      await storage.init();
      this.lake.storage = storage;

      // 恢复数据
      const datasets = await storage.loadAll();
      for (const ds of datasets) {
        this.lake.datasets.set(ds.id, ds);
      }
      console.log(`✅ 恢复 ${datasets.length} 个数据集`);
    } catch (e) {
      console.warn('⚠️ 存储初始化失败:', e.message);
    }

    // 绑定事件
    this.bindEvents();

    // 更新 UI
    this.updateDatasetList();
    this.updateStats();

    // 初始化虚拟滚动
    this.initVirtualScroll();

    // 更新内存状态
    this.updateMemory();

    console.log('✅ SQL Query UI 就绪');
    return this;
  }

  /**
   * 绑定事件
   */
  bindEvents() {
    // 文件上传
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-upload');

    if (uploadZone && fileInput) {
      uploadZone.addEventListener('click', () => fileInput.click());
      uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
      });
      uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
      });
      uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
          this.handleFiles(e.dataTransfer.files);
        }
      });
      fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
          this.handleFiles(e.target.files);
        }
      });
    }

    // SQL 执行
    const runBtn = document.getElementById('btn-run');
    const editor = document.getElementById('sql-editor');

    if (runBtn) {
      runBtn.addEventListener('click', () => this.runQuery());
    }

    if (editor) {
      // Ctrl+Enter 执行
      editor.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
          e.preventDefault();
          this.runQuery();
        }
      });
    }

    // 按钮事件
    document.getElementById('btn-clear')?.addEventListener('click', () => {
      document.getElementById('sql-editor').value = '';
    });

    document.getElementById('btn-sample')?.addEventListener('click', () => {
      this.insertSampleQuery();
    });

    document.getElementById('btn-explain')?.addEventListener('click', () => {
      this.explainQuery();
    });

    document.getElementById('btn-export-csv')?.addEventListener('click', () => {
      this.exportResults('csv');
    });

    document.getElementById('btn-export-json')?.addEventListener('click', () => {
      this.exportResults('json');
    });
  }

  /**
   * 处理文件上传
   */
  async handleFiles(files) {
    console.log(`📤 处理 ${files.length} 个文件...`);

    for (const file of files) {
      try {
        const type = this.detectType(file);
        let adapter;
        
        if (type === 'csv') {
          adapter = new CSVAdapter();
        } else if (type === 'json') {
          adapter = new JSONAdapter();
        } else {
          this.showToast(`不支持的格式: ${type}`, 'error');
          continue;
        }

        this.showToast(`正在导入 ${file.name}...`);

        const data = await adapter.read(file);
        const dataset = await this.lake.create(file.name, data, {
          type,
          metadata: { sourceFile: file.name }
        });

        // 同步到 SQLite
        await this.sqlite.fromDataLake(dataset.id, this.sanitizeTableName(file.name));

        this.showToast(`✅ ${file.name}: ${data.length} 行`, 'success');
        console.log(`✅ 导入 ${file.name}: ${data.length} 行`);
      } catch (e) {
        console.error(`❌ 导入 ${file.name} 失败:`, e);
        this.showToast(`❌ ${file.name} 导入失败`, 'error');
      }
    }

    this.updateDatasetList();
    this.updateStats();
  }

  /**
   * 检测文件类型
   */
  detectType(file) {
    const name = file.name.toLowerCase();
    if (name.endsWith('.csv')) return 'csv';
    if (name.endsWith('.json') || name.endsWith('.jsonl')) return 'json';
    return 'json';
  }

  /**
   * 表名清理
   */
  sanitizeTableName(name) {
    return name
      .replace(/[^a-zA-Z0-9_]/g, '_')
      .replace(/^_+/, '')
      .substring(0, 63) || 'dataset';
  }

  /**
   * 执行查询
   */
  async runQuery() {
    const editor = document.getElementById('sql-editor');
    const query = editor.value.trim();

    if (!query) {
      this.showToast('请输入 SQL 查询', 'error');
      return;
    }

    this.currentQuery = query;
    this.showToast('执行中...', 'info');

    const startTime = performance.now();

    try {
      // 确保 SQLite 已初始化
      await this.sqlite.init();

      // 执行查询
      const result = this.sqlite.query(query);
      
      const elapsed = (performance.now() - startTime).toFixed(2);
      this.currentResults = result.toArray();

      // 显示结果
      this.renderResults(this.currentResults);

      // 更新状态
      document.getElementById('result-count').textContent = 
        `(${this.currentResults.length} 行, ${elapsed}ms)`;

      this.showToast(`✅ ${this.currentResults.length} 行, ${elapsed}ms`, 'success');
      
      // 更新内存
      this.updateMemory();

    } catch (e) {
      console.error('查询失败:', e);
      this.showToast(`❌ ${e.message}`, 'error');
      this.renderError(e.message);
    }
  }

  /**
   * 渲染结果
   */
  renderResults(data) {
    const emptyEl = document.getElementById('results-empty');
    const tableEl = document.getElementById('results-table');
    const theadEl = document.getElementById('results-head');
    const tbodyEl = document.getElementById('results-body');

    if (!data || data.length === 0) {
      emptyEl.style.display = 'flex';
      tableEl.style.display = 'none';
      return;
    }

    emptyEl.style.display = 'none';
    tableEl.style.display = 'table';

    // 表头
    const columns = Object.keys(data[0]);
    theadEl.innerHTML = '<tr>' + columns.map(c => `<th>${c}</th>`).join('') + '</tr>';

    // 初始化虚拟滚动
    this.virtualScroll.setTotalItems(data.length);
    const range = this.virtualScroll.getVisibleRange();

    // 渲染可见行
    let html = '';
    for (let i = range.start; i < range.end && i < data.length; i++) {
      const row = data[i];
      html += '<tr>';
      for (const col of columns) {
        const value = row[col];
        let display = '';
        
        if (value === null || value === undefined) {
          display = '<span style="color: var(--text-secondary);">NULL</span>';
        } else if (typeof value === 'object') {
          display = '<span style="color: var(--accent);">{object}</span>';
        } else {
          display = String(value);
        }
        html += `<td title="${String(value).replace(/"/g, '&quot;')}">${display}</td>`;
      }
      html += '</tr>';
    }

    tbodyEl.innerHTML = html;

    // 绑定滚动事件
    const wrapper = document.getElementById('results-wrapper');
    const updateScroll = () => {
      const scrollTop = wrapper.scrollTop;
      this.virtualScroll.updateScrollTop(scrollTop);
      const range = this.virtualScroll.getVisibleRange();
      
      // 只重新渲染可见区域
      let html = '';
      for (let i = range.start; i < range.end && i < data.length; i++) {
        const row = data[i];
        html += '<tr>';
        for (const col of columns) {
          const value = row[col];
          html += `<td>${value !== null && value !== undefined ? String(value) : 'NULL'}</td>`;
        }
        html += '</tr>';
      }
      tbodyEl.innerHTML = html;
    };

    // 移除旧监听器
    const newWrapper = wrapper.cloneNode(true);
    wrapper.parentNode.replaceChild(newWrapper, wrapper);
    document.getElementById('results-wrapper').addEventListener('scroll', updateScroll);
  }

  /**
   * 渲染错误
   */
  renderError(message) {
    const emptyEl = document.getElementById('results-empty');
    const tableEl = document.getElementById('results-table');

    emptyEl.style.display = 'flex';
    emptyEl.innerHTML = `
      <div class="icon">❌</div>
      <div>查询错误</div>
      <div style="font-size: 12px; margin-top: 8px; color: var(--error);">${message}</div>
    `;
    tableEl.style.display = 'none';
  }

  /**
   * 插入示例查询
   */
  insertSampleQuery() {
    const queries = [
      `-- 基本查询
SELECT * FROM dataset LIMIT 100`,
      
      `-- 分组统计
SELECT region, COUNT(*) as count, SUM(amount) as total
FROM dataset
GROUP BY region
ORDER BY count DESC`,
      
      `-- 条件过滤
SELECT * FROM dataset
WHERE status = 'active'
  AND amount > 1000
ORDER BY date DESC
LIMIT 50`,
      
      `-- 聚合分析
SELECT 
  region,
  COUNT(*) as cnt,
  AVG(amount) as avg_amount,
  MIN(amount) as min_amount,
  MAX(amount) as max_amount
FROM dataset
GROUP BY region`
    ];

    const query = queries[Math.floor(Math.random() * queries.length)];
    document.getElementById('sql-editor').value = query;
  }

  /**
   * 解释查询
   */
  explainQuery() {
    const query = document.getElementById('sql-editor').value.trim();
    if (!query) {
      this.showToast('请先输入查询', 'error');
      return;
    }

    const explanation = this.parseQueryExplanation(query);
    this.showToast(explanation, 'info');
  }

  /**
   * 解析查询解释
   */
  parseQueryExplanation(query) {
    const upper = query.toUpperCase();
    const parts = [];

    if (upper.includes('SELECT')) {
      parts.push('📖 这是 SELECT 查询，会返回数据');
    }
    if (upper.includes('WHERE')) {
      parts.push('🔍 包含 WHERE 条件过滤');
    }
    if (upper.includes('GROUP BY')) {
      parts.push('📊 会按分组聚合数据');
    }
    if (upper.includes('ORDER BY')) {
      parts.push('🔢 结果会排序');
    }
    if (upper.includes('LIMIT')) {
      parts.push('✂️ 有 LIMIT 限制返回行数');
    }
    if (upper.includes('JOIN')) {
      parts.push('🔗 涉及表连接');
    }

    if (parts.length === 0) {
      return '💡 简单查询';
    }
    return parts.join(' | ');
  }

  /**
   * 导出结果
   */
  async exportResults(format) {
    if (this.currentResults.length === 0) {
      this.showToast('无数据可导出', 'error');
      return;
    }

    let content, mime, filename;

    if (format === 'csv') {
      const headers = Object.keys(this.currentResults[0]);
      content = headers.join(',') + '\n';
      content += this.currentResults.map(row => 
        headers.map(h => {
          const v = row[h];
          if (v === null || v === undefined) return '';
          if (typeof v === 'string' && (v.includes(',') || v.includes('"'))) {
            return `"${v.replace(/"/g, '""')}"`;
          }
          return v;
        }).join(',')
      ).join('\n');
      mime = 'text/csv';
      filename = 'query_results.csv';
    } else {
      content = JSON.stringify(this.currentResults, null, 2);
      mime = 'application/json';
      filename = 'query_results.json';
    }

    // 下载
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);

    this.showToast(`✅ 已导出 ${filename}`, 'success');
  }

  /**
   * 初始化虚拟滚动
   */
  initVirtualScroll() {
    const wrapper = document.getElementById('results-wrapper');
    this.virtualScroll = new VirtualScroll({
      itemHeight: 36,
      containerHeight: wrapper?.clientHeight || 400,
      buffer: 10
    });
  }

  /**
   * 更新数据集列表
   */
  updateDatasetList() {
    const listEl = document.getElementById('dataset-list');
    if (!listEl) return;

    const datasets = this.lake.list();

    if (datasets.length === 0) {
      listEl.innerHTML = `
        <div class="empty-state" style="padding: 20px;">
          <div>暂无数据</div>
        </div>
      `;
      return;
    }

    listEl.innerHTML = datasets.map(ds => `
      <div class="dataset-item" data-id="${ds.id}">
        <div class="name">${ds.name}</div>
        <div class="meta">${ds.rowCount.toLocaleString()} 行</div>
      </div>
    `).join('');

    // 绑定点击事件
    listEl.querySelectorAll('.dataset-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = item.dataset.id;
        document.getElementById('sql-editor').value = 
          `-- 查询: ${item.querySelector('.name').textContent}\nSELECT * FROM "${this.sanitizeTableName(item.querySelector('.name').textContent)}" LIMIT 100`;
        
        // 高亮选中
        listEl.querySelectorAll('.dataset-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
      });
    });
  }

  /**
   * 更新统计
   */
  updateStats() {
    const stats = this.lake.stats();
    
    document.getElementById('stat-datasets').textContent = stats.datasetCount;
    document.getElementById('stat-rows').textContent = 
      Number(stats.totalRows).toLocaleString();
  }

  /**
   * 更新内存状态
   */
  updateMemory() {
    const info = this.memory.getMemoryInfo();
    if (info) {
      document.getElementById('stat-memory').textContent = info.used;
    }
  }

  /**
   * 显示提示
   */
  showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
      toast.classList.remove('show');
    }, 3000);
  }
}

// 初始化
let sqlUI;
document.addEventListener('DOMContentLoaded', async () => {
  sqlUI = new SQLQueryUI();
  await sqlUI.init();
});

export { SQLQueryUI };
