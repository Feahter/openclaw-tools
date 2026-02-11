/**
 * IndexedDB Storage - IndexedDB 持久化存储适配器
 */

export class IndexedDBStorage {
  constructor(dbName = 'data-lake-storage', storeName = 'datasets') {
    this.dbName = dbName;
    this.storeName = storeName;
    this.db = null;
  }

  /**
   * 初始化
   */
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };

      request.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, { keyPath: 'id' });
        }
      };
    });
  }

  /**
   * 保存数据集
   */
  async save(id, data) {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(this.storeName, 'readwrite');
      const store = tx.objectStore(this.storeName);

      const serialized = {
        id,
        ...data.toJSON(),
        savedAt: Date.now()
      };

      const request = store.put(serialized);

      request.onsuccess = () => resolve(id);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * 加载数据集
   */
  async load(id) {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(this.storeName, 'readonly');
      const store = tx.objectStore(this.storeName);
      const request = store.get(id);

      request.onsuccess = () => {
        if (request.result) {
          // 恢复为 UnifiedData
          resolve(this.deserialize(request.result));
        } else {
          resolve(null);
        }
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * 删除数据集
   */
  async delete(id) {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(this.storeName, 'readwrite');
      const store = tx.objectStore(this.storeName);
      const request = store.delete(id);

      request.onsuccess = () => resolve(true);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * 列出所有数据集
   */
  async list() {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(this.storeName, 'readonly');
      const store = tx.objectStore(this.storeName);
      const request = store.getAll();

      request.onsuccess = () => {
        const results = request.result.map(item => ({
          id: item.id,
          name: item.name,
          type: item.type,
          savedAt: item.savedAt
        }));
        resolve(results);
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * 加载所有数据集
   */
  async loadAll() {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(this.storeName, 'readonly');
      const store = tx.objectStore(this.storeName);
      const request = store.getAll();

      request.onsuccess = () => {
        const results = request.result.map(item => this.deserialize(item));
        resolve(results);
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * 清空存储
   */
  async clear() {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(this.storeName, 'readwrite');
      const store = tx.objectStore(this.storeName);
      const request = store.clear();

      request.onsuccess = () => resolve(true);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * 获取存储使用量
   */
  async getUsage() {
    if (!navigator.storage) return null;

    if (navigator.storage.estimate) {
      const estimate = await navigator.storage.estimate();
      return {
        usage: estimate.usage,
        quota: estimate.quota,
        usagePercent: ((estimate.usage / estimate.quota) * 100).toFixed(2)
      };
    }

    return null;
  }

  /**
   * 序列化
   */
  serialize(data) {
    return {
      ...data.toJSON(),
      savedAt: Date.now()
    };
  }

  /**
   * 反序列化
   */
  deserialize(item) {
    // 恢复 UnifiedData
    const { UnifiedData } = require('./schema.js');
    return UnifiedData.fromJSON(item);
  }

  /**
   * 关闭连接
   */
  close() {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

/**
 * LocalStorage 简化存储（备用）
 */
export class LocalStorageBackup {
  constructor(key = 'data-lake-backup') {
    this.key = key;
  }

  async save(data) {
    const serialized = JSON.stringify(data);
    localStorage.setItem(this.key, serialized);
  }

  async load() {
    const serialized = localStorage.getItem(this.key);
    return serialized ? JSON.parse(serialized) : null;
  }

  async clear() {
    localStorage.removeItem(this.key);
  }
}
