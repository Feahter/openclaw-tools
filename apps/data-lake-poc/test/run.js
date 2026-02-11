/**
 * Test Runner - 核心功能测试
 */

import { UnifiedData, SchemaInference, SchemaValidator } from '../src/core/schema.js';
import { Pipeline, Aggregators } from '../src/core/etl.js';
import { DataLake } from '../src/core/datalake.js';
import { CSVAdapter } from '../src/adapters/csv.js';
import { JSONAdapter } from '../src/adapters/json.js';

const log = console.log;
const pass = () => log('✅ 通过');
const fail = (msg) => log(`❌ 失败: ${msg}`);

// 测试计数
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

async function runAsync(name, fn) {
  try {
    await fn();
    log(`✅ ${name}`);
    tests.passed++;
  } catch (e) {
    log(`❌ ${name}: ${e.message}`);
    tests.failed++;
  }
}

// ============ 测试开始 ============

log('\n🧪 Data Lake POC 测试\n');
log('='.repeat(50));

// 1. Schema 测试
log('\n📦 Schema 测试\n');

run('UnifiedData 创建', () => {
  const data = new UnifiedData({
    name: 'Test Data',
    data: [{ a: 1, b: 2 }]
  });
  if (data.name !== 'Test Data') throw new Error('name mismatch');
});

run('Schema 推断', () => {
  const data = [
    { name: 'Alice', age: 25, active: true },
    { name: 'Bob', age: 30, active: false }
  ];
  const schema = SchemaInference.infer(data);
  if (schema.columns.length !== 3) throw new Error('columns count mismatch');
});

run('类型推断 string', () => {
  const type = SchemaInference.inferType('hello');
  if (type !== 'string') throw new Error(`expected string, got ${type}`);
});

run('类型推断 integer', () => {
  const type = SchemaInference.inferType(42);
  if (type !== 'integer') throw new Error(`expected integer, got ${type}`);
});

run('类型推断 float', () => {
  const type = SchemaInference.inferType(3.14);
  if (type !== 'float') throw new Error(`expected float, got ${type}`);
});

// 2. Pipeline 测试
log('\n🔄 Pipeline 测试\n');

run('Pipeline.from 创建', () => {
  const data = [{ status: 'active' }, { status: 'inactive' }];
  const p = Pipeline.from(data, 'Test');
  if (p.source.getRowCount() !== 2) throw new Error('data count mismatch');
});

run('Pipeline.filter', async () => {
  const data = [{ status: 'active' }, { status: 'inactive' }];
  const p = Pipeline.from(data, 'Test')
    .filter(row => row.status === 'active');
  const result = await p.execute();
  if (result.getRowCount() !== 1) throw new Error('filter failed');
});

run('Pipeline.map', async () => {
  const data = [{ value: 1 }, { value: 2 }];
  const p = Pipeline.from(data, 'Test')
    .map(row => ({ ...row, doubled: row.value * 2 }));
  const result = await p.execute();
  if (result.toArray()[0].doubled !== 2) throw new Error('map failed');
});

run('Pipeline.limit', async () => {
  const data = [{ n: 1 }, { n: 2 }, { n: 3 }];
  const p = Pipeline.from(data, 'Test').limit(2);
  const result = await p.execute();
  if (result.getRowCount() !== 2) throw new Error('limit failed');
});

run('Pipeline.sort', async () => {
  const data = [{ v: 3 }, { v: 1 }, { v: 2 }];
  const p = Pipeline.from(data, 'Test').sort('v', 'asc');
  const result = await p.execute();
  if (result.toArray()[0].v !== 1) throw new Error('sort failed');
});

// 3. DataLake 测试
log('\n🗄️ DataLake 测试\n');

run('DataLake 创建', () => {
  const lake = new DataLake({ name: 'Test Lake' });
  if (lake.name !== 'Test Lake') throw new Error('name mismatch');
});

runAsync('DataLake 创建数据集', async () => {
  const lake = new DataLake({ name: 'Test' });
  const ds = await lake.create('Test Data', [{ a: 1 }]);
  if (ds.getRowCount() !== 1) throw new Error('create failed');
});

runAsync('DataLake 列表', async () => {
  const lake = new DataLake({ name: 'Test' });
  await lake.create('DS1', [{ a: 1 }]);
  await lake.create('DS2', [{ b: 2 }]);
  const list = lake.list();
  if (list.length !== 2) throw new Error('list count mismatch');
});

runAsync('DataLake 删除', async () => {
  const lake = new DataLake({ name: 'Test' });
  const ds = await lake.create('DS1', [{ a: 1 }]);
  const id = ds.id;
  await lake.delete(id);
  if (lake.get(id)) throw new Error('delete failed');
});

// 4. 适配器测试
log('\n🔌 适配器测试\n');

run('CSV Parse', () => {
  const csv = `name,age\nAlice,25\nBob,30`;
  const adapter = new CSVAdapter();
  const data = adapter.parse(csv);
  if (data.length !== 2) throw new Error('parse count mismatch');
});

runAsync('CSV Write', async () => {
  const adapter = new CSVAdapter();
  const csv = await adapter.write([{ name: 'Alice', age: 25 }]);
  if (!csv.includes('Alice')) throw new Error('write failed');
});

run('JSON Write', () => {
  const adapter = new JSONAdapter();
  const json = adapter.write([{ a: 1, b: 2 }]);
  if (!json.includes('"a": 1')) throw new Error('json write failed');
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
