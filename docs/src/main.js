/**
 * Main Entry - POC 入口文件
 */

import { DataLake } from './core/datalake.js';
import { CSVAdapter } from './adapters/csv.js';
import { JSONAdapter } from './adapters/json.js';
import { SQLiteAdapter } from './adapters/sqlite.js';
import { IndexedDBStorage } from './storage/indexeddb.js';

class DataLakeApp {
  constructor() {
    this.lake = new DataLake({
      name: 'Data Lake POC'
    });

    this.adapters = {
      csv: new CSVAdapter(this.lake),
      json: new JSONAdapter(this.lake),
      sqlite: new SQLiteAdapter(this.lake)
    };

    this.ui = null;
  }

  /**
   * 初始化
   */
  async init() {
    console.log('🚀 Data Lake POC 初始化...');

    // 初始化存储
    try {
      const storage = new IndexedDBStorage('data-lake-storage');
      await storage.init();
      this.lake.storage = storage;
      
      // 恢复数据
      const saved = await storage.loadAll();
      for (const data of saved) {
        this.lake.datasets.set(data.id, data);
      }
      
      console.log(`✅ 恢复 ${saved.length} 个数据集`);
    } catch (e) {
      console.warn('⚠️ 存储初始化失败，使用内存模式', e.message);
    }

    // 初始化 UI
    if (typeof document !== 'undefined') {
      this.initUI();
    }

    console.log('✅ Data Lake POC 就绪');
    return this;
  }

  /**
   * 初始化 UI 绑定
   */
  initUI() {
    // 绑定文件上传
    const uploadInput = document.getElementById('file-upload');
    if (uploadInput) {
      uploadInput.addEventListener('change', (e) => this.handleFileUpload(e));
    }

    // 绑定查询输入
    const queryInput = document.getElementById('query-input');
    if (queryInput) {
      queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') this.handleQuery(e.target.value);
      });
    }

    // 更新数据集列表
    this.updateDatasetList();
  }

  /**
   * 处理文件上传
   */
  async handleFileUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    console.log(`📤 处理 ${files.length} 个文件...`);

    for (const file of files) {
      try {
        const type = this.detectFileType(file);
        const adapter = this.adapters[type];
        
        if (!adapter) {
          console.warn(`⚠️ 不支持的格式: ${type}`);
          continue;
        }

        const data = await adapter.read(file);
        
        await this.lake.create(file.name, data, {
          type,
          metadata: { sourceFile: file.name }
        });

        console.log(`✅ 导入 ${file.name}: ${data.length} 行`);
      } catch (e) {
        console.error(`❌ 导入 ${file.name} 失败:`, e);
      }
    }

    this.updateDatasetList();
  }

  /**
   * 检测文件类型
   */
  detectFileType(file) {
    const name = file.name.toLowerCase();
    if (name.endsWith('.csv')) return 'csv';
    if (name.endsWith('.json')) return 'json';
    if (name.endsWith('.sqlite') || name.endsWith('.db')) return 'sqlite';
    return 'json';
  }

  /**
   * 处理查询
   */
  async handleQuery(query) {
    if (!query.trim()) return;

    console.log('🔍 执行查询:', query);

    try {
      // 简化实现：基本查询
      const result = await this.lake.query(query);
      console.log('📊 查询结果:', result);
      return result;
    } catch (e) {
      console.error('❌ 查询失败:', e);
      throw e;
    }
  }

  /**
   * 更新数据集列表 UI
   */
  updateDatasetList() {
    const list = document.getElementById('dataset-list');
    if (!list) return;

    const datasets = this.lake.list();
    
    list.innerHTML = datasets.map(ds => `
      <div class="dataset-item" data-id="${ds.id}">
        <div class="dataset-name">${ds.name}</div>
        <div class="dataset-info">${ds.rowCount} 行 | ${ds.columnCount} 列</div>
      </div>
    `).join('');
  }

  /**
   * 获取实例
   */
  static getInstance() {
    if (!DataLakeApp._instance) {
      DataLakeApp._instance = new DataLakeApp();
    }
    return DataLakeApp._instance;
  }
}

// 导出
export { DataLakeApp };
export default DataLakeApp;
