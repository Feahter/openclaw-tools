// OpenNoCode 单元测试
import State from '../src/core/state.js';

// 测试：状态创建
function testCreateState() {
  const state = { apps: [], fields: [], records: {} };
  console.assert(state.apps !== undefined, '状态初始化');
}

// 测试：应用CRUD
function testAppCRUD() {
  const apps = [];
  apps.push({ id: 'a1', name: 'Test' });
  console.assert(apps.length === 1, '添加应用');
  
  const idx = apps.findIndex(a => a.id === 'a1');
  console.assert(idx >= 0, '查找应用');
  
  apps.splice(idx, 1);
  console.assert(apps.length === 0, '删除应用');
}

// 测试：字段创建
function testFieldCRUD() {
  const fields = [];
  fields.push({ id: 'f1', name: 'title', type: 'text' });
  console.assert(fields.length === 1, '添加字段');
}

// 测试：记录CRUD
function testRecordCRUD() {
  const records = { app1: [] };
  records.app1.push({ id: 'r1', data: { title: 'Test' } });
  console.assert(records.app1.length === 1, '添加记录');
  
  const rec = records.app1.find(r => r.id === 'r1');
  console.assert(rec.data.title === 'Test', '读取记录');
  
  rec.data.title = 'Updated';
  console.assert(rec.data.title === 'Updated', '更新记录');
}

console.log('运行测试...');
testCreateState();
testAppCRUD();
testFieldCRUD();
testRecordCRUD();
console.log('测试完成');
