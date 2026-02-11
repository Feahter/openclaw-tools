/**
 * Data Lake - 统一数据湖管理
 * 
 * 核心功能：
 * - 数据集管理（CRUD）
 * - 数据导入/导出
 * - SQL 查询
 * - 持久化存储
 */

import { UnifiedData, SchemaInference } from './schema.js';
import { generateId } from './uuid.js';
import { Pipeline } from './etl.js';

export class DataLake {
  constructor(options = {}) {
    this.name = options.name || 'Data Lake';
    this.datasets = new Map(); // id -> UnifiedData
    this.metadata = new Map(); // id -> metadata
    this.storage = options.storage || null; // 持久化适配器
  }

  /**
   * 获取数据集
   */
  get(id) {
    return this.datasets.get(id);
  }

  /**
   * 获取所有数据集
   */
  list() {
    const list = [];
    for (const [id, data] of this.datasets) {
      const meta = this.metadata.get(id) || {};
      list.push({
        id,
        name: data.name,
        type: data.type,
        rowCount: data.getRowCount(),
        columnCount: data.getColumns().length,
        createdAt: meta.createdAt,
        updatedAt: meta.updatedAt
      });
    }
    return list;
  }

  /**
   * 创建数据集
   */
  async create(name, data, options = {}) {
    const unified = data instanceof UnifiedData 
      ? data 
      : new UnifiedData({
          name,
          type: options.type || 'array',
          schema: options.schema || SchemaInference.infer(data),
          data,
          metadata: options.metadata || {}
        });

    const id = unified.id || generateId('ds');
    unified.id = id;
    
    this.datasets.set(id, unified);
    this.metadata.set(id, {
      createdAt: Date.now(),
      updatedAt: Date.now(),
      version: 1,
      ...options.metadata
    });

    // 持久化
    if (this.storage) {
      await this.storage.save(id, unified);
    }

    return unified;
  }

  /**
   * 更新数据集
   */
  async update(id, data, options = {}) {
    const existing = this.datasets.get(id);
    if (!existing) {
      throw new Error(`Dataset ${id} not found`);
    }

    // 合并更新
    const updated = new UnifiedData({
      ...existing.toJSON(),
      ...data,
      id,
      metadata: {
        ...existing.metadata,
        ...options.metadata,
        version: (existing.metadata.version || 0) + 1,
        updatedAt: Date.now()
      }
    });

    this.datasets.set(id, updated);

    // 持久化
    if (this.storage) {
      await this.storage.save(id, updated);
    }

    return updated;
  }

  /**
   * 删除数据集
   */
  async delete(id) {
    this.datasets.delete(id);
    this.metadata.delete(id);

    if (this.storage) {
      await this.storage.delete(id);
    }

    return true;
  }

  /**
   * 克隆数据集
   */
  clone(id, newName = null) {
    const original = this.datasets.get(id);
    if (!original) {
      throw new Error(`Dataset ${id} not found`);
    }

    const cloned = original.clone();
    if (newName) cloned.name = newName;

    return this.create(cloned.name, cloned, {
      type: cloned.type,
      metadata: {
        cloned_from: id,
        ...cloned.metadata
      }
    });
  }

  /**
   * 合并数据集
   */
  async merge(datasets, options = {}) {
    // 假设所有数据集有相同结构
    const first = this.datasets.get(datasets[0]);
    if (!first) {
      throw new Error(`Dataset ${datasets[0]} not found`);
    }

    const allData = [];
    for (const id of datasets) {
      const data = this.datasets.get(id);
      if (data) {
        allData.push(...data.toArray());
      }
    }

    return this.create(options.name || `Merged ${datasets.length} datasets`, allData, {
      type: 'merged',
      metadata: {
        source_datasets: datasets,
        merged_at: Date.now()
      }
    });
  }

  /**
   * 创建查询管道
   */
  query(sql) {
    // 简化实现：支持基本 SQL 查询
    // 完整实现需要集成 sql.js
    return {
      where: (condition) => this,
      orderBy: (field, direction) => this,
      limit: (count) => this,
      execute: async () => {
        // TODO: 集成 sql.js 实现完整 SQL
        throw new Error('SQL query requires sql.js integration');
      }
    };
  }

  /**
   * 创建 ETL 管道
   */
  createPipeline(sourceId) {
    const source = this.datasets.get(sourceId);
    if (!source) {
      throw new Error(`Dataset ${sourceId} not found`);
    }
    return Pipeline.from(source);
  }

  /**
   * 导入数据（自动识别格式）
   */
  async import(file, options = {}) {
    const adapter = this.getAdapter(options.type || this.detectType(file));
    if (!adapter) {
      throw new Error(`No adapter for type: ${options.type || this.detectType(file)}`);
    }

    const data = await adapter.read(file, options);
    
    return this.create(
      options.name || file.name || 'Imported Data',
      data,
      {
        type: adapter.type,
        metadata: {
          source_file: file.name || 'unknown',
          source_size: file.size,
          imported_at: Date.now()
        }
      }
    );
  }

  /**
   * 导出数据
   */
  async export(id, format = 'json', options = {}) {
    const data = this.datasets.get(id);
    if (!data) {
      throw new Error(`Dataset ${id} not found`);
    }

    const adapter = this.getAdapter(format);
    if (!adapter) {
      throw new Error(`No adapter for format: ${format}`);
    }

    return adapter.write(data, options);
  }

  /**
   * 检测文件类型
   */
  detectType(file) {
    const name = file.name || '';
    const type = file.type || '';
    
    if (name.endsWith('.csv') || type === 'text/csv') return 'csv';
    if (name.endsWith('.json') || type === 'application/json') return 'json';
    if (name.endsWith('.sqlite') || name.endsWith('.db')) return 'sqlite';
    if (name.endsWith('.parquet')) return 'parquet';
    if (name.endsWith('.arrow')) return 'arrow';
    
    return 'json'; // 默认
  }

  /**
   * 获取适配器
   */
  getAdapter(type) {
    const adapters = {
      csv: null, // 延迟加载
      json: null,
      sqlite: null,
      arrow: null,
      parquet: null
    };

    // 动态导入适配器
    switch (type) {
      case 'csv':
        return adapters.csv || import('./adapters/csv.js').then(m => m.CSVAdapter ? new m.CSVAdapter(this) : null);
      case 'json':
        return adapters.json || import('./adapters/json.js').then(m => m.JSONAdapter ? new m.JSONAdapter(this) : null);
      case 'sqlite':
        return adapters.sqlite || import('./adapters/sqlite.js').then(m => m.SQLiteAdapter ? new m.SQLiteAdapter(this) : null);
      case 'arrow':
        return adapters.arrow || import('./adapters/arrow.js').then(m => m.ArrowAdapter ? new m.ArrowAdapter(this) : null);
      default:
        return null;
    }
  }

  /**
   * 注册适配器
   */
  registerAdapter(type, adapter) {
    this.adapters = this.adapters || {};
    this.adapters[type] = adapter;
  }

  /**
   * 序列化（持久化）
   */
  async serialize() {
    const serialized = {
      name: this.name,
      datasets: []
    };

    for (const [id, data] of this.datasets) {
      serialized.datasets.push({
        id,
        ...data.toJSON(),
        metadata: this.metadata.get(id)
      });
    }

    return serialized;
  }

  /**
   * 从序列化恢复
   */
  static async deserialize(data, options = {}) {
    const lake = new DataLake({ name: data.name });
    
    for (const ds of data.datasets || []) {
      const unified = UnifiedData.fromJSON(ds);
      lake.datasets.set(ds.id, unified);
      lake.metadata.set(ds.id, ds.metadata || {});
    }

    return lake;
  }

  /**
   * 获取统计信息
   */
  stats() {
    let totalRows = 0;
    let totalSize = 0;
    const typeCounts = {};

    for (const [id, data] of this.datasets) {
      totalRows += data.getRowCount();
      totalSize += JSON.stringify(data.toArray()).length;
      typeCounts[data.type] = (typeCounts[data.type] || 0) + 1;
    }

    return {
      datasetCount: this.datasets.size,
      totalRows,
      totalSizeMB: (totalSize / 1024 / 1024).toFixed(2),
      typeCounts
    };
  }
}

/**
 * Storage Adapter Interface
 */
export class StorageAdapter {
  async save(id, data) { throw new Error('Not implemented'); }
  async load(id) { throw new Error('Not implemented'); }
  async delete(id) { throw new Error('Not implemented'); }
  async list() { throw new Error('Not implemented'); }
}
