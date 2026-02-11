# Data Lake POC - 浏览器端 SQLite + ETL 数据基座

## 📊 项目统计

| 指标 | 数值 |
|------|------|
| **文件数** | 20 个 |
| **代码行数** | ~5500 行 |
| **项目大小** | 180 KB |
| **测试通过率** | 100% (25/25) |

---

## 🎯 核心功能

### 1. 统一数据模型
- `UnifiedData` - 统一的数据表示格式
- `SchemaInference` - 自动类型推断
- `SchemaValidator` - Schema 验证

### 2. ETL 管道引擎
- `Pipeline` - 链式 ETL 操作
- 支持：filter, map, select, sort, limit, aggregate 等
- 支持自定义转换函数

### 3. SQL 查询引擎 (sql.js)
- 完整 SQL 支持（SELECT, JOIN, GROUP BY 等）
- IndexedDB 持久化
- 大数据集性能优化

### 4. 性能优化
- `VirtualScroll` - 虚拟滚动（万级数据）
- `PageLoader` - 分页加载
- `Sampler` - 数据采样
- `StreamProcessor` - 流式处理
- `MemoryOptimizer` - 内存优化

### 5. 格式适配器
| 适配器 | 导入 | 导出 | 说明 |
|--------|------|------|------|
| CSV | ✅ | ✅ | 自动分隔符检测 |
| JSON | ✅ | ✅ | 支持 JSONL |
| SQLite | ✅ | ✅ | sql.js 集成 |

---

## 🚀 快速开始

### 方式一：Web UI
```bash
cd data-lake-poc
python3 -m http.server 8080
# 访问 http://localhost:8080/src/index.html
# 或 SQL 查询界面 http://localhost:8080/src/sql-query.html
```

### 方式二：Node.js
```javascript
import { DataLake, Pipeline, CSVAdapter } from './src/core/schema.js';

const lake = new DataLake({ name: 'My Data Lake' });

// 导入数据
const adapter = new CSVAdapter();
const data = adapter.parse(await fetch('data.csv').then(r => r.text()));
await lake.create('sales', data);

// ETL 处理
const result = await lake.createPipeline('sales')
  .filter(row => row.amount > 1000)
  .groupBy('region')
  .execute();

// SQL 查询
const sqlite = new SQLiteAdapter(lake);
await sqlite.init();
const results = sqlite.query('SELECT region, SUM(amount) FROM sales GROUP BY region');
```

---

## 📁 项目结构

```
data-lake-poc/
├── src/
│   ├── core/
│   │   ├── schema.js        # 统一数据模型
│   │   ├── etl.js           # ETL 管道引擎
│   │   ├── datalake.js      # 数据湖管理
│   │   ├── uuid.js          # UUID 生成
│   │   └── performance.js    # 性能优化
│   ├── adapters/
│   │   ├── csv.js           # CSV 适配器
│   │   ├── json.js          # JSON 适配器
│   │   └── sqlite.js        # SQLite 适配器
│   ├── storage/
│   │   └── indexeddb.js     # IndexedDB 持久化
│   ├── ui/
│   │   ├── index.html       # 主 UI
│   │   ├── ui.js            # UI 逻辑
│   │   ├── sql-query.html   # SQL 查询界面
│   │   └── sql-ui.js        # SQL UI 逻辑
│   └── main.js              # 入口
├── test/
│   ├── run.js              # 核心测试
│   └── sqlite.test.js       # SQLite 测试
├── _meta.json               # Skill 元数据
├── SKILL.md                 # Skill 说明
└── README.md
```

---

## 🧪 测试结果

### 核心测试 (13/13 通过)
```
✅ UnifiedData 创建
✅ Schema 推断
✅ 类型推断 (string/integer/float)
✅ Pipeline (filter/map/limit/sort)
✅ DataLake (CRUD)
✅ CSV Parse/Write
✅ JSON Write
```

### SQLite 测试 (12/12 通过)
```
✅ 初始化测试
✅ 查询测试 (SELECT/WHERE/JOIN/GROUP BY)
✅ 性能测试 (1000行导入+查询)
✅ DataLake 集成
✅ 导出测试
```

---

## 🔧 API 参考

### DataLake

```javascript
// 创建
const ds = await lake.create(name, data, options);

// 列表
const list = lake.list();

// 删除
await lake.delete(id);

// ETL 管道
const pipeline = lake.createPipeline(id)
  .filter(predicate)
  .map(transform)
  .select(fields)
  .sort(field, direction)
  .limit(count);
await pipeline.execute();
```

### Pipeline

```javascript
// 创建
const p = Pipeline.from(data, name);

// 链式操作
p.filter(row => row.status === 'active')
 .map(row => ({ ...row, processed: true }))
 .select(['id', 'name'])
 .sort('name', 'asc')
 .limit(100);

// 执行
const result = await p.execute();
```

### SQLite

```javascript
// 初始化
const sqlite = new SQLiteAdapter(lake);
await sqlite.init();

// 从 DataLake 导入
await sqlite.fromDataLake(datasetId, tableName);

// 查询
const result = sqlite.query('SELECT * FROM table LIMIT 100');

// 导出
const blob = await sqlite.exportBlob();
```

---

## 📈 性能基准

| 操作 | 数据量 | 耗时 |
|------|--------|------|
| CSV 解析 | 10,000 行 | ~50ms |
| Pipeline 处理 | 10,000 行 | ~30ms |
| SQLite 导入 | 1,000 行 | ~15ms |
| SQL GROUP BY | 1,000 行 | ~5ms |

---

## 🔜 下一步

- [ ] 集成 Apache Arrow 格式
- [ ] 支持 Parquet 文件
- [ ] 添加图表可视化
- [ ] 实现数据透视表
- [ ] 添加协作功能
- [ ] 性能优化（Web Worker）

---

## License

MIT
