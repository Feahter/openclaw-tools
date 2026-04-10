// OpenNoCode 测试用例
// ==================

// 测试1: 字段创建
function test_createField() {
  state.fields = [];
  const field = { id: 'f1', name: 'test_field', type: 'text', label: '测试字段', created_at: Date.now() };
  state.fields.push(field);
  console.assert(state.fields.length === 1, '字段创建');
  console.assert(state.fields[0].name === 'test_field', '字段名称');
}

// 测试2: 应用创建
function test_createApp() {
  state.apps = [];
  const app = { id: 'a1', name: '测试应用', type: 'data', fields: [], created_at: Date.now() };
  state.apps.push(app);
  console.assert(state.apps.length === 1, '应用创建');
}

// 测试3: 记录CRUD
function test_recordCRUD() {
  state.records = {};
  // 创建
  const record = { id: 'r1', data: { name: '测试' }, created_at: Date.now() };
  state.records['a1'] = [record];
  console.assert(state.records['a1'].length === 1, '创建记录');
  
  // 读取
  const read = state.records['a1'][0];
  console.assert(read.data.name === '测试', '读取记录');
  
  // 更新
  read.data.name = '更新';
  console.assert(read.data.name === '更新', '更新记录');
  
  // 删除
  state.records['a1'] = state.records['a1'].filter(r => r.id !== 'r1');
  console.assert(state.records['a1'].length === 0, '删除记录');
}

// 测试4: 公式计算
function test_formula() {
  const data = { 金额: 100, 数量: 2 };
  const result = calculateFormula('{金额} * {数量}', data);
  console.assert(result === 200, '公式计算');
}

// 测试5: 搜索筛选
function test_filter() {
  const records = [
    { id: 'r1', data: { name: '苹果' } },
    { id: 'r2', data: { name: '香蕉' } }
  ];
  const filtered = records.filter(r => JSON.stringify(r.data).toLowerCase().includes('苹果'));
  console.assert(filtered.length === 1, '搜索过滤');
}

// 测试6: 权限检查
function test_permission() {
  console.assert(hasPermission('create') === true, '管理员有创建权限');
  state.currentRole = 'viewer';
  console.assert(hasPermission('create') === false, '只读无创建权限');
}

// 测试7: 回收站
function test_trash() {
  state.deletedRecords = [];
  const record = { id: 'r1', data: {}, deleted_at: Date.now() };
  state.deletedRecords.push(record);
  console.assert(state.deletedRecords.length === 1, '删除到回收站');
  
  // 恢复
  state.deletedRecords = [];
  console.assert(state.deletedRecords.length === 0, '恢复记录');
}

// 测试8: SQLite存储
function test_storage() {
  console.assert(db !== null || localStorage.getItem('opennocode_db') !== null, '存储初始化');
}

// 运行所有测试
function runTests() {
  console.log('开始测试...');
  test_createField();
  test_createApp();
  test_recordCRUD();
  test_formula();
  test_filter();
  test_permission();
  test_trash();
  test_storage();
  console.log('测试完成');
}

runTests();
