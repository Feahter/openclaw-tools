/**
 * SQLite Adapter - SQLite 导入/导出适配器
 * 
 * 完整功能：
 * - 从文件导入 SQLite/创建新数据库
 * - 将 DataLake 数据导入 SQLite
 * - 执行 SQL 查询
 * - 导出为文件或 Blob
 * - IndexedDB 持久化
 * 
 * 依赖：sql.js (会自动从 CDN 加载)
 */

export class SQLiteAdapter {
  constructor(datalake = null) {
    this.datalake = datalake;
    this.type = 'sqlite';
    this.db = null;
    this.SQL = null;
    this.loaded = false;
  }

  /**
   * 初始化并加载 sql.js
   */
  async init() {
    if (this.loaded) return this;
    
    // 尝试获取全局 SQL 对象
    if (typeof window !== 'undefined' && window.SQL) {
      this.SQL = window.SQL;
      this.loaded = true;
      return this;
    }

    // 动态加载
    await this.loadSqlJsFromCDN();
    this.loaded = true;
    return this;
  }

  /**
   * 从 CDN 加载 sql.js
   */
  async loadSqlJsFromCDN() {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/sql-wasm.js';
      script.onload = async () => {
        try {
          this.SQL = await window.initSqlJs({
            locateFile: file => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/${file}`
          });
          resolve(this.SQL);
        } catch (e) {
          reject(e);
        }
      };
      script.onerror = () => reject(new Error('Failed to load sql.js'));
      document.body.appendChild(script);
    });
  }

  /**
   * 创建新数据库
   */
  async createDB(dbName = 'data-lake.db') {
    await this.init();
    this.db = new this.SQL.Database();
    return this.db;
  }

  /**
   * 从文件导入
   */
  async fromFile(file, options = {}) {
    await this.init();

    let data;
    if (file instanceof Blob || file instanceof ArrayBuffer) {
      const buffer = file instanceof Blob 
        ? new Uint8Array(await file.arrayBuffer()) 
        : new Uint8Array(file);
      this.db = new this.SQL.Database(buffer);
    } else if (typeof file === 'string') {
      // SQL 文件内容
      this.db = new this.SQL.Database(file);
    } else {
      throw new Error('Invalid file type');
    }

    return this.getTables();
  }

  /**
   * 从 DataLake 导入数据集
   */
  async fromDataLake(datasetId, tableName = null) {
    await this.init();

    if (!this.datalake) {
      throw new Error('DataLake not set');
    }

    const dataset = this.datalake.get(datasetId);
    if (!dataset) {
      throw new Error(`Dataset ${datasetId} not found`);
    }

    // 创建数据库（如果不存在）
    if (!this.db) {
      this.db = new this.SQL.Database();
    }

    const table = tableName || this.sanitizeTableName(dataset.name);
    this.createTableFromData(table, dataset.toArray());

    return table;
  }

  /**
   * 创建表并导入数据
   */
  createTableFromData(tableName, data) {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    if (data.length === 0) {
      console.warn('Empty data, creating empty table');
      this.db.run(`CREATE TABLE IF NOT EXISTS "${tableName}" (id INTEGER PRIMARY KEY)`);
      return;
    }

    // 分析数据列
    const columns = Object.keys(data[0]);
    const columnDefs = columns.map(col => {
      const sample = data[0][col];
      return `"${col}" ${this.inferSqlType(sample)}`;
    });

    // 创建表
    this.db.run(`CREATE TABLE IF NOT EXISTS "${tableName}" (${columnDefs.join(', ')})`);

    // 批量插入
    const placeholders = columns.map(() => '?').join(', ');
    const insertSQL = `INSERT INTO "${tableName}" (${columns.map(c => `"${c}"`).join(', ')}) VALUES (${placeholders})`;

    const stmt = this.db.prepare(insertSQL);
    
    this.db.exec('BEGIN TRANSACTION');
    try {
      for (const row of data) {
        const values = columns.map(col => row[col]);
        stmt.run(values);
      }
      this.db.exec('COMMIT');
    } catch (e) {
      this.db.exec('ROLLBACK');
      throw e;
    }
    stmt.free();
  }

  /**
   * SQL 类型推断
   */
  inferSqlType(value) {
    if (value === null || value === undefined) return 'TEXT';
    
    if (typeof value === 'number') {
      return Number.isInteger(value) ? 'INTEGER' : 'REAL';
    }
    
    if (typeof value === 'boolean') return 'INTEGER';
    if (value instanceof Date) return 'DATETIME';
    
    if (typeof value === 'string') {
      if (value.length > 10000) return 'TEXT';
      // 日期检测
      if (/^\d{4}-\d{2}-\d{2}/.test(value) && !isNaN(Date.parse(value))) {
        return 'DATETIME';
      }
      return 'TEXT';
    }

    if (typeof value === 'object') return 'TEXT';
    return 'TEXT';
  }

  /**
   * 执行查询
   */
  query(sql, params = []) {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    try {
      const result = this.db.exec(sql, params);
      
      if (result.length === 0) {
        return { columns: [], values: [], rowCount: 0 };
      }

      const { columns, values } = result[0];
      return {
        columns,
        values,
        rowCount: values.length,
        toArray: function() {
          return values.map(row => {
            const obj = {};
            for (let i = 0; i < columns.length; i++) {
              obj[columns[i]] = row[i];
            }
            return obj;
          });
        },
        toObjects: function() {
          return this.toArray();
        }
      };
    } catch (e) {
      throw new Error(`SQL Error: ${e.message}\nQuery: ${sql}`);
    }
  }

  /**
   * 执行查询并返回数组
   */
  async queryArray(sql, params = []) {
    const result = this.query(sql, params);
    return result.toArray();
  }

  /**
   * 获取所有表
   */
  getTables() {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const result = this.db.exec(`
      SELECT name FROM sqlite_master 
      WHERE type='table' AND name NOT LIKE 'sqlite_%'
      ORDER BY name
    `);
    
    if (result.length === 0) return [];
    return result[0].values.map(row => row[0]);
  }

  /**
   * 获取表信息
   */
  getTableInfo(tableName) {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const result = this.db.exec(`PRAGMA table_info("${tableName}")`);
    
    if (result.length === 0) return [];
    
    return result[0].values.map(row => ({
      cid: row[0],
      name: row[1],
      type: row[2],
      notnull: row[3],
      dflt_value: row[4],
      pk: row[5]
    }));
  }

  /**
   * 获取表行数
   */
  getTableCount(tableName) {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const result = this.db.exec(`SELECT COUNT(*) as cnt FROM "${tableName}"`);
    if (result.length === 0) return 0;
    return result[0].values[0][0];
  }

  /**
   * 获取表数据样本
   */
  sampleTable(tableName, limit = 10) {
    return this.query(`SELECT * FROM "${tableName}" LIMIT ${limit}`);
  }

  /**
   * 导出数据库
   */
  export() {
    if (!this.db) {
      throw new Error('Database not initialized');
    }
    return this.db.export();
  }

  /**
   * 导出为 Blob
   */
  async exportBlob() {
    const data = this.export();
    return new Blob([data], { type: 'application/x-sqlite3' });
  }

  /**
   * 生成下载链接
   */
  async createDownload(filename = 'database.sqlite') {
    const blob = await this.exportBlob();
    return URL.createObjectURL(blob);
  }

  /**
   * 保存到 IndexedDB
   */
  async saveToIndexedDB(dbName = 'data-lake-sqlite') {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const data = this.export();
    
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(dbName, 1);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction('databases', 'readwrite');
        const store = tx.objectStore('databases');
        store.put(data, 'main-db');
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
      };
      
      request.onupgradeneeded = (e) => {
        e.target.result.createObjectStore('databases');
      };
    });
  }

  /**
   * 从 IndexedDB 加载
   */
  async loadFromIndexedDB(dbName = 'data-lake-sqlite') {
    await this.init();
    
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(dbName, 1);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction('databases', 'readonly');
        const store = tx.objectStore('databases');
        const getRequest = store.get('main-db');
        
        getRequest.onsuccess = () => {
          if (getRequest.result) {
            this.db = new this.SQL.Database(getRequest.result);
            resolve(this.db);
          } else {
            resolve(null);
          }
        };
        getRequest.onerror = () => reject(getRequest.error);
      };
    });
  }

  /**
   * 关闭数据库
   */
  close() {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }

  /**
   * 清理表名
   */
  sanitizeTableName(name) {
    return name
      .replace(/[^a-zA-Z0-9_]/g, '_')
      .replace(/^_+/, '')
      .substring(0, 63);
  }

  /**
   * 批量执行多个查询
   */
  async execBatch(sql) {
    if (!this.db) {
      throw new Error('Database not initialized');
    }

    const results = [];
    const statements = sql.split(';').filter(s => s.trim());

    for (const stmt of statements) {
      if (stmt.trim()) {
        try {
          const result = this.db.exec(stmt);
          if (result.length > 0) {
            results.push(result[0]);
          }
        } catch (e) {
          console.warn(`Statement skipped: ${e.message}`);
        }
      }
    }

    return results;
  }

  /**
   * 获取数据库信息
   */
  getInfo() {
    if (!this.db) {
      return null;
    }

    return {
      tables: this.getTables(),
      size: this.export().length,
      filename: this.db.filename || 'in-memory'
    };
  }

  /**
   * 删除表
   */
  dropTable(tableName) {
    if (!this.db) {
      throw new Error('Database not initialized');
    }
    this.db.run(`DROP TABLE IF EXISTS "${tableName}"`);
  }

  /**
   * 清空表
   */
  truncateTable(tableName) {
    if (!this.db) {
      throw new Error('Database not initialized');
    }
    this.db.run(`DELETE FROM "${tableName}"`);
  }
}

/**
 * 便捷函数
 */
export async function createSqliteFromData(data, tableName = 'dataset') {
  const adapter = new SQLiteAdapter();
  await adapter.createDB();
  adapter.createTableFromData(tableName, data);
  return adapter;
}

export async function querySqlite(sql, data) {
  const adapter = await createSqliteFromData(data);
  return adapter.queryArray(sql);
}
