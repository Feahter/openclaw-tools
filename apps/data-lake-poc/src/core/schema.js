/**
 * Unified Data Schema - 统一数据模型
 * 
 * 核心设计：
 * - 统一的数据表示格式
 * - 类型自动推断
 * - Schema 验证
 * - 元数据管理
 */

import { v4 as uuidv4 } from './uuid.js';

export class UnifiedData {
  constructor(options = {}) {
    this.id = options.id || uuidv4();
    this.type = options.type || 'custom';
    this.name = options.name || 'Untitled Dataset';
    this.timestamp = options.timestamp || Date.now();
    this.schema = options.schema || { columns: [] };
    this.data = options.data || [];
    this.metadata = options.metadata || {};
    this.version = options.version || '1.0.0';
  }

  /**
   * 获取列信息
   */
  getColumns() {
    return this.schema.columns || [];
  }

  /**
   * 获取列名列表
   */
  getColumnNames() {
    return this.getColumns().map(col => col.name);
  }

  /**
   * 获取行数
   */
  getRowCount() {
    return this.data.length;
  }

  /**
   * 获取数据样本（前N行）
   */
  sample(n = 5) {
    return this.data.slice(0, n);
  }

  /**
   * 获取完整数据
   */
  toArray() {
    return this.data;
  }

  /**
   * 转换为特定格式
   */
  toFormat(format) {
    switch (format) {
      case 'array':
        return this.data;
      case 'json':
        return JSON.stringify(this.data, null, 2);
      case 'object':
        return { schema: this.schema, data: this.data };
      default:
        return this.data;
    }
  }

  /**
   * 克隆
   */
  clone() {
    return new UnifiedData({
      id: uuidv4(),
      type: this.type,
      name: `${this.name} (copy)`,
      timestamp: Date.now(),
      schema: JSON.parse(JSON.stringify(this.schema)),
      data: JSON.parse(JSON.stringify(this.data)),
      metadata: { ...this.metadata, copied_from: this.id }
    });
  }

  /**
   * 转换为可序列化格式
   */
  toJSON() {
    return {
      id: this.id,
      type: this.type,
      name: this.name,
      timestamp: this.timestamp,
      schema: this.schema,
      data: this.data,
      metadata: this.metadata,
      version: this.version
    };
  }

  /**
   * 从 JSON 恢复
   */
  static fromJSON(json) {
    return new UnifiedData(json);
  }
}

/**
 * Schema 类型推断
 */
export class SchemaInference {
  /**
   * 从数据推断 Schema
   */
  static infer(data) {
    if (!data || data.length === 0) {
      return { columns: [] };
    }

    const columns = [];
    const firstRow = data[0];

    for (const [key, value] of Object.entries(firstRow)) {
      const column = {
        name: key,
        type: this.inferType(value),
        nullable: true
      };

      // 检查所有行的类型一致性
      const types = new Set(data.map(row => this.inferType(row[key])));
      if (types.size > 1) {
        column.type = 'mixed';
        column.nullable = true;
      }

      columns.push(column);
    }

    return { columns };
  }

  /**
   * 推断单个值的类型
   */
  static inferType(value) {
    if (value === null || value === undefined) {
      return 'null';
    }

    if (typeof value === 'number') {
      return Number.isInteger(value) ? 'integer' : 'float';
    }

    if (typeof value === 'boolean') {
      return 'boolean';
    }

    if (value instanceof Date) {
      return 'date';
    }

    if (Array.isArray(value)) {
      return 'array';
    }

    if (typeof value === 'object') {
      return 'json';
    }

    // 日期字符串检测
    if (typeof value === 'string') {
      const date = Date.parse(value);
      if (!isNaN(date) && value.length > 6 && /^\d{4}[-/]\d/.test(value)) {
        return 'date';
      }
    }

    return 'string';
  }

  /**
   * 转换为目标类型
   */
  static convert(value, targetType) {
    if (value === null || value === undefined) {
      return null;
    }

    try {
      switch (targetType) {
        case 'integer':
          return parseInt(value, 10);
        case 'float':
          return parseFloat(value);
        case 'boolean':
          return Boolean(value);
        case 'date':
          return new Date(value).toISOString();
        case 'json':
          return typeof value === 'string' ? JSON.parse(value) : value;
        default:
          return String(value);
      }
    } catch {
      return value; // 转换失败返回原值
    }
  }
}

/**
 * Schema 验证器
 */
export class SchemaValidator {
  constructor(schema) {
    this.schema = schema;
  }

  /**
   * 验证数据是否符合 Schema
   */
  validate(data) {
    const errors = [];
    const columns = this.schema.columns;

    for (let i = 0; i < data.length; i++) {
      const row = data[i];

      for (const col of columns) {
        const value = row[col.name];

        // 空值检查
        if (col.nullable === false && (value === null || value === undefined)) {
          errors.push({
            row: i,
            column: col.name,
            error: 'required value is null'
          });
          continue;
        }

        // 类型检查
        if (value !== null && value !== undefined) {
          const actualType = SchemaInference.inferType(value);
          if (!this.isCompatible(actualType, col.type)) {
            errors.push({
              row: i,
              column: col.name,
              error: `type mismatch: expected ${col.type}, got ${actualType}`
            });
          }
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      totalRows: data.length,
      errorRate: errors.length / data.length
    };
  }

  /**
   * 检查类型兼容性
   */
  isCompatible(actual, expected) {
    if (actual === expected) return true;
    if (expected === 'mixed') return true;
    if (actual === 'null' && expected !== 'string') return true;
    return false;
  }
}
