/**
 * ETL Pipeline Engine - ETL 管道引擎
 * 
 * 轻量级、可组合的数据转换管道
 * 
 * 使用方式：
 *   const pipeline = new Pipeline(source)
 *     .filter(row => row.status === 'active')
 *     .map(row => ({ ...row, processed: true }))
 *     .aggregate({ count: 'COUNT(*)' });
 */

import { UnifiedData, SchemaInference } from './schema.js';
import { generateId } from './uuid.js';

export class Pipeline {
  constructor(source = null) {
    this.source = source;
    this.steps = [];
    this.result = null;
  }

  /**
   * 创建新管道
   */
  static from(data, name = 'Pipeline Output') {
    const unified = data instanceof UnifiedData 
      ? data 
      : new UnifiedData({
          name,
          schema: SchemaInference.infer(data),
          data
        });
    return new Pipeline(unified);
  }

  /**
   * 添加过滤步骤
   */
  filter(predicate) {
    this.steps.push({
      type: 'filter',
      predicate,
      execute: (data) => data.filter(this.steps[this.steps.length - 1].predicate)
    });
    return this;
  }

  /**
   * 添加映射/转换步骤
   */
  map(transform) {
    this.steps.push({
      type: 'map',
      transform,
      execute: (data) => data.map(this.steps[this.steps.length - 1].transform)
    });
    return this;
  }

  /**
   * 添加字段选择步骤
   */
  select(fields) {
    this.steps.push({
      type: 'select',
      fields,
      execute: (data) => data.map(row => {
        const newRow = {};
        for (const field of fields) {
          if (field in row) {
            newRow[field] = row[field];
          }
        }
        return newRow;
      })
    });
    return this;
  }

  /**
   * 添加字段排除步骤
   */
  exclude(fields) {
    this.steps.push({
      type: 'exclude',
      fields,
      execute: (data) => data.map(row => {
        const newRow = { ...row };
        for (const field of fields) {
          delete newRow[field];
        }
        return newRow;
      })
    });
    return this;
  }

  /**
   * 添加重命名字段步骤
   */
  rename(mapping) {
    this.steps.push({
      type: 'rename',
      mapping,
      execute: (data) => data.map(row => {
        const newRow = { ...row };
        for (const [oldName, newName] of Object.entries(mapping)) {
          if (oldName in newRow) {
            newRow[newName] = newRow[oldName];
            delete newRow[oldName];
          }
        }
        return newRow;
      })
    });
    return this;
  }

  /**
   * 添加排序步骤
   */
  sort(field, direction = 'asc') {
    this.steps.push({
      type: 'sort',
      field,
      direction,
      execute: (data) => [...data].sort((a, b) => {
        const aVal = a[field];
        const bVal = b[field];
        const modifier = direction === 'desc' ? -1 : 1;
        if (aVal < bVal) return -1 * modifier;
        if (aVal > bVal) return 1 * modifier;
        return 0;
      })
    });
    return this;
  }

  /**
   * 添加去重步骤
   */
  distinct(field = null) {
    this.steps.push({
      type: 'distinct',
      field,
      execute: (data) => {
        if (field) {
          const seen = new Set();
          return data.filter(row => {
            const key = String(row[field]);
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
          });
        }
        return [...new Set(data.map(JSON.stringify))].map(JSON.parse);
      }
    });
    return this;
  }

  /**
   * 添加限制行数步骤
   */
  limit(count, offset = 0) {
    this.steps.push({
      type: 'limit',
      count,
      offset,
      execute: (data) => data.slice(offset, offset + count)
    });
    return this;
  }

  /**
   * 添加聚合步骤
   */
  aggregate(aggregations, groupBy = null) {
    this.steps.push({
      type: 'aggregate',
      aggregations,
      groupBy,
      execute: (data) => {
        if (groupBy) {
          // 分组聚合
          const groups = new Map();
          for (const row of data) {
            const key = groupBy.map(f => row[f]).join('|||');
            if (!groups.has(key)) {
              groups.set(key, []);
            }
            groups.get(key).push(row);
          }
          
          const result = [];
          for (const [key, rows] of groups) {
            const groupedRow = {};
            const keyParts = key.split('|||');
            for (let i = 0; i < groupBy.length; i++) {
              groupedRow[groupBy[i]] = keyParts[i];
            }
            
            for (const [aggName, aggFunc] of Object.entries(aggregations)) {
              groupedRow[aggName] = aggFunc(rows);
            }
            result.push(groupedRow);
          }
          return result;
        } else {
          // 全局聚合
          const result = {};
          for (const [aggName, aggFunc] of Object.entries(aggregations)) {
            result[aggName] = aggFunc(data);
          }
          return [result];
        }
      }
    });
    return this;
  }

  /**
   * 添加自定义步骤
   */
  custom(name, fn) {
    this.steps.push({
      type: 'custom',
      name,
      execute: fn
    });
    return this;
  }

  /**
   * 执行管道
   */
  async execute() {
    if (!this.source) {
      throw new Error('Pipeline has no source data');
    }

    let data = this.source.toArray();
    const schema = { ...this.source.schema };

    for (const step of this.steps) {
      data = await step.execute(data);
    }

    // 重新推断 Schema
    schema.columns = SchemaInference.infer(data).columns;

    this.result = new UnifiedData({
      id: generateId('result'),
      name: `${this.source.name} (transformed)`,
      type: 'transformed',
      schema,
      data,
      metadata: {
        source_id: this.source.id,
        steps_count: this.steps.length,
        transformed_at: Date.now()
      }
    });

    return this.result;
  }

  /**
   * 获取管道预览（只执行前几步或采样数据）
   */
  async preview(maxRows = 10) {
    if (!this.source) {
      throw new Error('Pipeline has no source data');
    }

    let data = this.source.toArray().slice(0, maxRows);
    
    for (const step of this.steps) {
      data = step.execute(data);
    }

    return {
      steps: this.steps.map(s => s.type),
      sample: data,
      totalSteps: this.steps.length,
      estimatedRows: this.source.getRowCount()
    };
  }

  /**
   * 生成管道配置（可序列化）
   */
  toConfig() {
    return {
      steps: this.steps.map(s => ({
        type: s.type,
        ...(s.predicate && { predicate: s.predicate.toString() }),
        ...(s.transform && { transform: s.transform.toString() }),
        ...(s.fields && { fields: s.fields }),
        ...(s.field && { field: s.field }),
        ...(s.direction && { direction: s.direction }),
        ...(s.count && { count: s.count }),
        ...(s.aggregations && { aggregations: Object.keys(s.aggregations) }),
        ...(s.groupBy && { groupBy: s.groupBy }),
        ...(s.mapping && { mapping: s.mapping })
      }))
    };
  }

  /**
   * 从配置创建管道
   */
  static fromConfig(config, source) {
    const pipeline = new Pipeline(source);
    // 注意：函数需要重新定义，这里简化处理
    return pipeline;
  }
}

/**
 * 常用聚合函数
 */
export const Aggregators = {
  COUNT: (rows) => rows.length,
  SUM: (field) => rows.reduce((sum, row) => sum + (Number(row[field]) || 0), 0),
  AVG: (field) => {
    const values = rows.map(r => Number(r[field])).filter(v => !isNaN(v));
    return values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
  },
  MIN: (field) => Math.min(...rows.map(r => Number(r[field])).filter(v => !isNaN(v))),
  MAX: (field) => Math.max(...rows.map(r => Number(r[field])).filter(v => !isNaN(v))),
  FIRST: (field) => rows[0]?.[field],
  LAST: (field) => rows[rows.length - 1]?.[field],
  ARRAY: (field) => rows.map(r => r[field]),
  DISTINCT: (field) => [...new Set(rows.map(r => r[field]))]
};

/**
 * ETL 管道工厂
 */
export class PipelineFactory {
  static createCleanPipeline(sourceField, targetField = null) {
    return Pipeline.from(sourceField)
      .filter(row => row[sourceField] !== null && row[sourceField] !== undefined)
      .map(row => ({
        ...row,
        [targetField || `${sourceField}_clean`]: String(row[sourceField]).trim()
      }));
  }

  static createDateParsePipeline(dateFields, targetFormat = 'iso') {
    return Pipeline.from(dateFields)
      .custom('date_parse', rows => {
        return rows.map(row => {
          const newRow = { ...row };
          for (const field of [].concat(dateFields)) {
            if (newRow[field]) {
              newRow[field] = new Date(newRow[field]).toISOString();
            }
          }
          return newRow;
        });
      });
  }

  static createAggregationPipeline(groupBy, metrics) {
    const aggregations = {};
    for (const [name, field] of Object.entries(metrics)) {
      aggregations[name] = Aggregators[field] || Aggregators.SUM;
    }
    
    return Pipeline.from(groupBy)
      .aggregate(aggregations, Object.keys(metrics));
  }
}
