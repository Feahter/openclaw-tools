/**
 * SQLite Integration Tests - SQLite 集成测试
 */

import { SQLiteAdapter } from '../src/adapters/sqlite.js';
import { Pipeline } from '../src/core/etl.js';
import { DataLake } from '../src/core/datalake.js';

const log = console.log;
let tests = { passed: 0, failed: 0 };

function run(name, fn) {
  try {
    fn();
    log(`✅ ${name}`);
    tests.passed++;
  } catch (e) {
    log(`❌ ${name}: ${e.message}`);
    tests.failed++;
  }
}

function assertEqual(actual, expected, msg = '') {
  if (actual !== expected) {
    throw new Error(`${msg} Expected ${expected}, got ${actual}`);
  }
}

function assertArrayLength(arr, len, msg = '') {
  if (!Array.isArray(arr) || arr.length !== len) {
    throw new Error(`${msg} Expected array length ${len}`);
  }
}

// ============ 测试数据 ============

const testData = [
  { id: 1, name: 'Alice', amount: 1000, region: 'North', status: 'active' },
  { id: 2, name: 'Bob', amount: 2500, region: 'South', status: 'active' },
  { id: 3, name: 'Carol', amount: 500, region: 'East', status: 'inactive' },
  { id: 4, name: 'David', amount: 3000, region: 'West', status: 'active' },
  { id: 5, name: 'Eve', amount: 1500, region: 'North', status: 'pending' },
];

const largeTestData = Array.from({ length: 1000 }, (_, i) => ({
  id: i + 1,
  name: `User${i}`,
  amount: Math.floor(Math.random() * 10000),
  region: ['North', 'South', 'East', 'West'][i % 4],
  status: ['active', 'inactive', 'pending'][i % 3]
}));

// ============ 测试开始 ============

log('\n🧪 SQLite Adapter 测试\n');
log('='.repeat(50));

// 1. 初始化测试
log('\n📦 初始化测试\n');

run('SQLiteAdapter 创建', async () => {
  const adapter = new SQLiteAdapter();
  await adapter.init();
  assertEqual(adapter.loaded, true, 'Should be loaded');
  adapter.close();
});

run('从数据创建数据库', async () => {
  const adapter = new SQLiteAdapter();
  await adapter.createDB();
  adapter.createTableFromData('test_table', testData);
  
  const tables = adapter.getTables();
  assertArrayLength(tables, 1, 'Should have 1 table');
  
  adapter.close();
});

// 2. 查询测试
log('\n🔍 查询测试\n');

run('基本 SELECT 查询', async () => {
  const adapter = new SQLiteAdapter();
  await adapter.createDB();
  adapter.createTableFromData('dataset', testData);
  
  const result = adapter.query('SELECT * FROM dataset');
  assertArrayLength(result.values, 5, 'Should return 5 rows');
  
  adapter.close();
});

run('带 WHERE 条件的查询', async () => {
  const adapter = new SQLiteAdapter();
  await adapter.createDB();
  adapter.createTableFromData('dataset', testData);
  
  const result = adapter.query('SELECT * FROM dataset WHERE amount > 2000');
  assertArrayLength(result.values, 2, 'Should return 2 rows');
  
  adapter.close();
});

run('GROUP BY 聚合查询', async () => {
  const adapter = new SQLiteAdapter();
  await adapter.createDB();
  adapter.createTableFromData('dataset', testData);
  
  const result = adapter.query(`
    SELECT region, COUNT(*) as cnt, SUM(amount) as total
    FROM dataset
    GROUP BY region
    ORDER BY cnt DESC
  `);
  
  assertArrayLength(result.values, 4, 'Should return 4 regions');
  
  adapter.close();
});

run('JOIN 查询', async () => {
  const adapter = new SQLiteAdapter();
  await adapter.createDB();
  adapter.createTableFromData('users', [
    { id: 1, name: 'Alice', dept: 'Sales' },
    { id: 2, name: 'Bob', dept: 'Engineering' },
  ]);
  adapter.createTableFromData('orders', [
    { user_id: 1, amount: 100 },
    { user_id: 2, amount: 200 },
  ]);
  
  const result = adapter.query(`
    SELECT u.name, o.amount
    FROM users u
    JOIN orders o ON u.id = o.user_id
  `);
  
  assertArrayLength(result.values, 2, 'Should return 2 joined rows');
  
  adapter.close();
});

// 3. 性能测试
log('\n⚡ 性能测试\n');

run('大数据集导入', async () => {
  const adapter = new SQLiteAdapter();
  await adapter.createDB();
  
  const start = performance.now();
  adapter.createTableFromData('large_dataset', largeTestData);
  const elapsed = performance.now() - start;
  
  log(`   导入 1000 行耗时: ${elapsed.toFixed(2)}ms`);
  
  const count = adapter.getTableCount('large_dataset');
  assertEqual(count, 1000, 'Should have 1000 rows');
  
  adapter.close();
}, 10000); // 10秒超时

run('大数据集查询', async () => {
  const adapter = new SQLiteAdapter();
  await adapter.createDB();
  adapter.createTableFromData('large_dataset', largeTestData);
  
  const start = performance.now();
  const result = adapter.query('SELECT region, COUNT(*) as cnt FROM large_dataset GROUP BY region');
  const elapsed = performance.now() - start;
  
  log(`   分组查询耗时: ${elapsed.toFixed(2)}ms`);
  assertArrayLength(result.values, 4, 'Should return 4 regions');
  
  adapter.close();
});

// 4. DataLake 集成测试
log('\n🔗 DataLake 集成测试\n');

run('DataLake 数据同步到 SQLite', async () => {
  const lake = new DataLake({ name: 'Test' });
  const sqlite = new SQLiteAdapter(lake);
  
  // 创建数据集
  const ds = await lake.create('Test Data', testData);
  
  // 同步到 SQLite
  await sqlite.init();
  sqlite.createDB();
  await sqlite.fromDataLake(ds.id, 'synced_table');
  
  // 验证
  const result = sqlite.query('SELECT * FROM synced_table');
  assertArrayLength(result.values, 5, 'Should have 5 rows');
  
  sqlite.close();
});

run('Pipeline 结果导出到 SQLite', async () => {
  const lake = new DataLake({ name: 'Test' });
  await lake.create('Raw Data', testData);
  
  // 创建 ETL 管道
  const pipeline = lake.createPipeline('Raw Data')
    .filter(row => row.amount > 1000)
    .select(['id', 'name', 'amount']);
  
  const result = await pipeline.execute();
  
  // 导出到 SQLite
  const sqlite = new SQLiteAdapter(lake);
  await sqlite.init();
  sqlite.createDB();
  sqlite.createTableFromData('filtered_data', result.toArray());
  
  const count = sqlite.getTableCount('filtered_data');
  assertEqual(count, 3, 'Should have 3 filtered rows');
  
  sqlite.close();
});

// 5. 导出测试
log('\n💾 导出测试\n');

run('导出数据库', async () => {
  const adapter = new SQLiteAdapter();
  await adapter.createDB();
  adapter.createTableFromData('test', testData);
  
  const data = adapter.export();
  assertEqual(data instanceof Uint8Array, true, 'Should export as Uint8Array');
  assertEqual(data.length > 0, true, 'Should have data');
  
  adapter.close();
});

run('表信息查询', async () => {
  const adapter = new SQLiteAdapter();
  await adapter.createDB();
  adapter.createTableFromData('test', testData);
  
  const info = adapter.getTableInfo('test');
  assertArrayLength(info, 5, 'Should have 5 columns');
  
  const columnNames = info.map(c => c.name);
  assertEqual(columnNames.includes('id'), true, 'Should have id column');
  assertEqual(columnNames.includes('name'), true, 'Should have name column');
  
  adapter.close();
});

// ============ 测试结果 ============

log('\n' + '='.repeat(50));
log(`\n📊 测试结果: ${tests.passed} 通过, ${tests.failed} 失败\n`);

if (tests.failed > 0) {
  log('❌ 有测试失败');
  process.exit(1);
} else {
  log('✅ 全部测试通过');
  process.exit(0);
}
