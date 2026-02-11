---
name: data-lake
description: "浏览器端 SQLite + ETL 数据基座 - 统一数据存储、多格式导入导出、离线数据处理引擎"
triggers:
  - "data-lake"
  - "离线数据"
  - "浏览器sqlite"
  - "etl"
  - "数据导入导出"
source:
  project: data-lake-poc
  url: https://github.com/Feahter/openclaw-tools/tree/main/data-lake-poc
  license: MIT
---

# Data Lake - 浏览器端数据基座

离线优先的数据处理引擎，支持多格式导入导出、ETL 管道、SQL 查询。

## 核心能力

### 统一数据模型

```javascript
import { DataLake, UnifiedData } from './core/schema.js';

const lake = new DataLake({ name: 'My Data Lake' });

// 创建数据集
const dataset = await lake.create('sales_data', [
  { date: '2024-01-01', amount: 100, region: 'North' },
  { date: '2024-01-02', amount: 200, region: 'South' }
]);

// 查询数据集
const datasets = lake.list();
```

### 多格式导入导出

```javascript
// 导入 CSV
const csvData = await lake.import('data.csv');

// 导出为 JSON
await lake.export('dataset_id', 'json');

// 导出为 CSV
await lake.export('dataset_id', 'csv');
```

### ETL 管道

```javascript
// 创建 ETL 管道
const pipeline = lake.createPipeline('dataset_id')
  .filter(row => row.status === 'active')
  .map(row => ({
    ...row,
    processed_at: new Date().toISOString()
  }))
  .select(['id', 'name', 'processed_at'])
  .sort('name', 'asc');

// 执行管道
const result = await pipeline.execute();
await lake.save(result, 'cleaned_data');
```

### SQL 查询（集成 sql.js）

```javascript
// 需要先初始化 sql.js
import { SQLiteAdapter } from './adapters/sqlite.js';

const sqlite = new SQLiteAdapter();
await sqlite.init();

// 从 DataLake 获取数据并查询
const result = sqlite.query(`
  SELECT region, SUM(amount) as total
  FROM dataset
  GROUP BY region
  ORDER BY total DESC
`);
```

## 项目结构

```
data-lake-poc/
├── src/
│   ├── core/
│   │   ├── schema.js       # 统一数据模型
│   │   ├── etl.js          # ETL 管道引擎
│   │   ├── datalake.js     # 数据湖管理
│   │   └── uuid.js         # UUID 生成器
│   ├── adapters/
│   │   ├── csv.js          # CSV 导入导出
│   │   ├── json.js         # JSON 导入导出
│   │   └── sqlite.js       # SQLite 集成
│   ├── storage/
│   │   └── indexeddb.js    # IndexedDB 持久化
│   ├── ui/
│   │   ├── index.html      # Web UI
│   │   └── app.js         # UI 逻辑
│   └── main.js            # 入口
├── _meta.json            # 元数据
└── README.md
```

## 使用场景

### 1. 离线数据分析

```javascript
// 在没有网络的情况下处理数据
const lake = new DataLake({ name: 'Analytics' });
await lake.import('large_dataset.csv');
const pipeline = lake.createPipeline('large_dataset.csv')
  .filter(row => row.value > 1000)
  .aggregate({ total: 'SUM', count: 'COUNT' });
```

### 2. 数据清洗

```javascript
// 清洗和标准化数据
await lake.createPipeline('raw_data')
  .filter(row => row.date && row.amount)
  .map(row => ({
    ...row,
    date: new Date(row.date).toISOString().split('T')[0],
    amount: parseFloat(row.amount)
  }))
  .save('cleaned_data');
```

### 3. 多格式转换

```javascript
// JSON 转 CSV
await lake.import('data.json');
await lake.export('data_id', 'csv');

// CSV 转 SQLite
await lake.import('data.csv');
await lake.export('data_id', 'sqlite');
```

## 技术特点

| 特性 | 说明 |
|------|------|
| **离线优先** | 所有数据存储在本地 IndexedDB |
| **统一格式** | 单一数据模型适配多种格式 |
| **可扩展** | 适配器模式支持自定义格式 |
| **轻量** | 核心库 < 50KB |
| **安全** | 数据不出浏览器 |

## 依赖

- [sql.js](https://sql.js.org/) - SQLite Wasm（可选）

## 注意事项

*基于 Data Lake POC 项目生成*
*更新时间: 2025-02-11*
