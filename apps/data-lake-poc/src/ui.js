/**
 * UI - Data Lake POC 用户界面
 */

import { DataLake } from './core/datalake.js';
import { CSVAdapter } from './adapters/csv.js';
import { JSONAdapter } from './adapters/json.js';
import { SQLiteAdapter } from './adapters/sqlite.js';
import { IndexedDBStorage } from './storage/indexeddb.js';

class DataLakeUI {
  constructor() {
    this.lake = null;
    this.selectedDataset = null;
    this.adapters = {};
  }

  /**
   * 初始化应用
   */
  async init() {
    console.log('🚀 初始化 Data Lake POC...');

    // 初始化 DataLake
    this.lake = new DataLake({ name: 'Data Lake POC' });

    // 初始化适配器
    this.adapters = {
      csv: new CSVAdapter(this.lake),
      json: new JSONAdapter(this.lake),
      sqlite: new SQLiteAdapter(this.lake)
    };

    // 初始化存储
    try {
      const storage = new IndexedDBStorage('data-lake-poc');
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

    // 绑定 UI 事件
    this.bindEvents();

    // 更新 UI
    this.updateDatasetList();
    this.updateStats();

    console.log('✅ Data Lake POC 就绪');
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
        uploadZone.style.borderColor = 'var(--accent)';
      });

      uploadZone.addEventListener('dragleave', () => {
        uploadZone.style.borderColor = 'var(--border)';
      });

      uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = 'var(--border)';
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

    // 查询执行
    const queryBtn = document.querySelector('.panel-header .btn');
    if (queryBtn) {
      queryBtn.addEventListener('click', () => this.runQuery());
    }
  }

  /**
   * 处理文件上传
   */
  async handleFiles(files) {
    console.log(`📤 处理 ${files.length} 个文件...`);

    for (const file of files) {
      try {
        const type = this.detectType(file);
        const adapter = this.adapters[type];

        if (!adapter) {
          this.showToast(`不支持的格式: ${type}`, 'error');
          continue;
        }

        // 显示加载状态
        this.showToast(`正在导入 ${file.name}...`);

        const data = await adapter.read(file);
        
        const dataset = await this.lake.create(file.name, data, {
          type,
          metadata: {
            sourceFile: file.name,
            sourceSize: file.size
          }
        });

        this.showToast(`✅ ${file.name}: ${data.length} 行`, 'success');
        console.log(`✅ 导入 ${file.name}: ${data.length} 行`);
      } catch (e) {
        console.error(`❌ 导入 ${file.name} 失败:`, e);
        this.showToast(`❌ ${file.name} 导入失败: ${e.message}`, 'error');
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
    if (name.endsWith('.sqlite') || name.endsWith('.db')) return 'sqlite';
    return 'json';
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
        <div class="empty-state">
          <div>暂无数据</div>
          <div style="font-size: 12px; margin-top: 8px;">上传文件开始使用</div>
        </div>
      `;
      return;
    }

    listEl.innerHTML = datasets.map(ds => `
      <div class="dataset-item ${this.selectedDataset === ds.id ? 'active' : ''}" 
           data-id="${ds.id}">
        <div class="name">${ds.name}</div>
        <div class="meta">${ds.rowCount} 行 | ${ds.columnCount} 列</div>
      </div>
    `).join('');

    // 绑定点击事件
    listEl.querySelectorAll('.dataset-item').forEach(item => {
      item.addEventListener('click', () => {
        this.selectDataset(item.dataset.id);
      });
    });
  }

  /**
   * 选择数据集
   */
  selectDataset(id) {
    this.selectedDataset = id;
    
    // 更新列表高亮
    document.querySelectorAll('.dataset-item').forEach(item => {
      item.classList.toggle('active', item.dataset.id === id);
    });

    // 显示数据预览
    this.previewDataset(id);

    // 显示 Schema
    this.showSchema(id);

    // 显示操作按钮
    document.getElementById('dataset-actions').style.display = 'flex';
  }

  /**
   * 预览数据集
   */
  previewDataset(id) {
    const dataset = this.lake.get(id);
    if (!dataset) return;

    const previewEl = document.getElementById('data-preview');
    if (!previewEl) return;

    const data = dataset.toArray();
    if (data.length === 0) {
      previewEl.innerHTML = '<div class="empty-state"><div>数据集为空</div></div>';
      return;
    }

    const headers = dataset.getColumnNames();
    const rows = data.slice(0, 100); // 只显示前100行

    let html = '<div class="data-preview"><table><thead><tr>';
    
    // 表头
    for (const header of headers) {
      html += `<th>${header}</th>`;
    }
    html += '</tr></thead><tbody>';

    // 数据行
    for (const row of rows) {
      html += '<tr>';
      for (const header of headers) {
        const value = row[header];
        let displayValue = '';
        
        if (value === null || value === undefined) {
          displayValue = '<span style="color: var(--text-secondary);">NULL</span>';
        } else if (typeof value === 'object') {
          displayValue = '<span style="color: var(--accent);">{object}</span>';
        } else {
          displayValue = String(value).substring(0, 100);
        }
        
        html += `<td>${displayValue}</td>`;
      }
      html += '</tr>';
    }

    html += '</tbody></table>';
    
    if (data.length > 100) {
      html += `<div style="padding: 12px; color: var(--text-secondary); font-size: 12px;">
        显示前 100 行，共 ${data.length} 行
      </div>`;
    }

    html += '</div>';
    previewEl.innerHTML = html;
  }

  /**
   * 显示 Schema
   */
  showSchema(id) {
    const dataset = this.lake.get(id);
    if (!dataset) return;

    const schemaEl = document.getElementById('schema-info');
    if (!schemaEl) return;

    const columns = dataset.getColumns();

    let html = '<div style="display: flex; flex-wrap: wrap; gap: 8px;">';
    
    for (const col of columns) {
      const typeColors = {
        'string': '#22c55e',
        'integer': '#6366f1',
        'float': '#f59e0b',
        'boolean': '#ec4899',
        'date': '#06b6d4',
        'array': '#8b5cf6',
        'json': '#f97316'
      };

      const color = typeColors[col.type] || '#64748b';
      
      html += `
        <div class="schema-badge" style="border-left: 3px solid ${color};">
          <strong>${col.name}</strong>
          <span style="color: var(--text-secondary); margin-left: 4px;">${col.type}</span>
        </div>
      `;
    }

    html += '</div>';
    schemaEl.innerHTML = html;
  }

  /**
   * 执行查询
   */
  async runQuery() {
    const queryInput = document.getElementById('query-input');
    const resultEl = document.getElementById('query-result');
    
    if (!queryInput || !resultEl) return;

    const query = queryInput.value.trim();
    if (!query) {
      this.showToast('请输入查询语句', 'error');
      return;
    }

    this.showToast('正在执行查询...');

    try {
      // 简化实现：只支持基本过滤
      let result;
      
      if (!this.selectedDataset) {
        throw new Error('请先选择数据集');
      }

      const dataset = this.lake.get(this.selectedDataset);
      const data = dataset.toArray();

      // 简单查询解析（WHERE clause）
      if (query.toLowerCase().startsWith('select')) {
        // 简化处理：只支持 LIMIT
        const limitMatch = query.match(/limit\s+(\d+)/i);
        const limit = limitMatch ? parseInt(limitMatch[1]) : 100;
        
        result = data.slice(0, limit);
      } else {
        // 其他操作
        result = data;
      }

      // 显示结果
      if (result.length === 0) {
        resultEl.innerHTML = '<div class="empty-state"><div>查询结果为空</div></div>';
      } else {
        const headers = Object.keys(result[0]);
        
        let html = '<div class="data-preview"><table><thead><tr>';
        for (const header of headers) {
          html += `<th>${header}</th>`;
        }
        html += '</tr></thead><tbody>';

        for (const row of result.slice(0, 50)) {
          html += '<tr>';
          for (const header of headers) {
            const value = row[header];
            html += `<td>${value !== null && value !== undefined ? String(value).substring(0, 100) : 'NULL'}</td>`;
          }
          html += '</tr>';
        }

        html += '</tbody></table></div>';
        resultEl.innerHTML = html;
      }

      this.showToast(`✅ 查询完成: ${result.length} 行`, 'success');
    } catch (e) {
      console.error('查询失败:', e);
      resultEl.innerHTML = `<div style="color: var(--error);">查询失败: ${e.message}</div>`;
      this.showToast(`❌ 查询失败: ${e.message}`, 'error');
    }
  }

  /**
   * 导出数据
   */
  async exportData(format) {
    if (!this.selectedDataset) {
      this.showToast('请先选择数据集', 'error');
      return;
    }

    const dataset = this.lake.get(this.selectedDataset);
    const adapter = this.adapters[format];
    
    if (!adapter) {
      this.showToast(`不支持的格式: ${format}`, 'error');
      return;
    }

    const data = dataset.toArray();
    const content = await adapter.write(data);
    
    // 创建下载
    const blob = new Blob([content], { 
      type: format === 'csv' ? 'text/csv' : 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${dataset.name}.${format}`;
    a.click();
    
    URL.revokeObjectURL(url);
    this.showToast(`✅ 已导出 ${dataset.name}.${format}`, 'success');
  }

  /**
   * 清空数据
   */
  async clearData() {
    if (!confirm('确定要清空所有数据吗？')) return;

    // 清空数据集
    for (const id of this.lake.datasets.keys()) {
      await this.lake.delete(id);
    }

    this.selectedDataset = null;
    this.updateDatasetList();
    this.updateStats();
    
    document.getElementById('data-preview').innerHTML = `
      <div class="empty-state">
        <div class="icon">📊</div>
        <div>数据已清空</div>
      </div>
    `;
    document.getElementById('schema-info').innerHTML = '';
    document.getElementById('dataset-actions').style.display = 'none';
    
    this.showToast('✅ 数据已清空', 'success');
  }

  /**
   * 更新统计信息
   */
  updateStats() {
    const stats = this.lake.stats();
    
    const datasetsEl = document.getElementById('stat-datasets');
    const rowsEl = document.getElementById('stat-rows');
    
    if (datasetsEl) datasetsEl.textContent = stats.datasetCount;
    if (rowsEl) rowsEl.textContent = stats.totalRows.toLocaleString();
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
let app;
document.addEventListener('DOMContentLoaded', async () => {
  app = new DataLakeUI();
  await app.init();
});

export { DataLakeUI };
