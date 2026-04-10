// ============================================
// 存储引擎 - SQL.js (SQLite WASM)
// ============================================

import initSqlJs, { Database, SqlJsStatic } from 'sql.js';

let SQL: SqlJsStatic | null = null;
let db: Database | null = null;

// 初始化
export async function initStorage(): Promise<void> {
  SQL = await initSqlJs({
    locateFile: (file) => `https://sql.js.org/dist/${file}`,
  });
  
  // 尝试加载本地存储
  const saved = localStorage.getItem('opennocode_db');
  if (saved) {
    const data = Uint8Array.from(atob(saved), c => c.charCodeAt(0));
    db = new SQL.Database(data);
  } else {
    db = new SQL.Database();
    createTables();
  }
}

// 创建表
function createTables(): void {
  if (!db) return;
  
  // 字段表
  db.run(`
    CREATE TABLE IF NOT EXISTS fields (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      type TEXT NOT NULL,
      meta TEXT NOT NULL,
      permissions TEXT NOT NULL,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL
    )
  `);
  
  // 应用表
  db.run(`
    CREATE TABLE IF NOT EXISTS apps (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      type TEXT NOT NULL,
      description TEXT,
      fields TEXT NOT NULL,
      views TEXT NOT NULL,
      state_machine TEXT,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL
    )
  `);
  
  // 记录表
  db.run(`
    CREATE TABLE IF NOT EXISTS records (
      id TEXT PRIMARY KEY,
      app_id TEXT NOT NULL,
      data TEXT NOT NULL,
      state TEXT,
      created_by TEXT NOT NULL,
      created_at INTEGER NOT NULL,
      updated_by TEXT,
      updated_at INTEGER NOT NULL
    )
  `);
  
  // 状态机表
  db.run(`
    CREATE TABLE IF NOT EXISTS state_machines (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      states TEXT NOT NULL,
      transitions TEXT NOT NULL,
      initial TEXT NOT NULL
    )
  `);
  
  // 模板表
  db.run(`
    CREATE TABLE IF NOT EXISTS templates (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      type TEXT NOT NULL,
      content TEXT NOT NULL,
      placeholders TEXT NOT NULL,
      created_at INTEGER NOT NULL
    )
  `);
  
  // 角色表
  db.run(`
    CREATE TABLE IF NOT EXISTS roles (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      permissions TEXT NOT NULL
    )
  `);
  
  saveToLocal();
}

// 保存到 localStorage
export function saveToLocal(): void {
  if (!db) return;
  const data = db.export();
  const base64 = btoa(String.fromCharCode(...data));
  localStorage.setItem('opennocode_db', base64);
}

// ============================================
// 字段操作
// ============================================

export function createField(field: any): void {
  if (!db) return;
  db.run(
    `INSERT INTO fields (id, name, type, meta, permissions, created_at, updated_at)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
    [field.id, field.name, field.type, JSON.stringify(field.meta),
     JSON.stringify(field.permissions), field.created_at, field.updated_at]
  );
  saveToLocal();
}

export function getFields(): any[] {
  if (!db) return [];
  const results = db.exec('SELECT * FROM fields');
  if (!results[0]) return [];
  
  return results[0].values.map((row: any) => ({
    id: row[0],
    name: row[1],
    type: row[2],
    meta: JSON.parse(row[3]),
    permissions: JSON.parse(row[4]),
    created_at: row[5],
    updated_at: row[6],
  }));
}

export function updateField(id: string, updates: Partial<any>): void {
  if (!db) return;
  db.run(
    `UPDATE fields SET name = ?, type = ?, meta = ?, permissions = ?, updated_at = ?
     WHERE id = ?`,
    [updates.name, updates.type, JSON.stringify(updates.meta),
     JSON.stringify(updates.permissions), Date.now(), id]
  );
  saveToLocal();
}

export function deleteField(id: string): void {
  if (!db) return;
  db.run('DELETE FROM fields WHERE id = ?', [id]);
  saveToLocal();
}

// ============================================
// 应用操作
// ============================================

export function createApp(app: any): void {
  if (!db) return;
  db.run(
    `INSERT INTO apps (id, name, type, description, fields, views, state_machine, created_at, updated_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [app.id, app.name, app.type, app.description || '',
     JSON.stringify(app.fields), JSON.stringify(app.views),
     app.state_machine || '', app.created_at, app.updated_at]
  );
  saveToLocal();
}

export function getApps(): any[] {
  if (!db) return [];
  const results = db.exec('SELECT * FROM apps');
  if (!results[0]) return [];
  
  return results[0].values.map((row: any) => ({
    id: row[0],
    name: row[1],
    type: row[2],
    description: row[3],
    fields: JSON.parse(row[4]),
    views: JSON.parse(row[5]),
    state_machine: row[6],
    created_at: row[7],
    updated_at: row[8],
  }));
}

export function deleteApp(id: string): void {
  if (!db) return;
  db.run('DELETE FROM apps WHERE id = ?', [id]);
  saveToLocal();
}

// ============================================
// 记录操作
// ============================================

export function createRecord(record: any): void {
  if (!db) return;
  db.run(
    `INSERT INTO records (id, app_id, data, state, created_by, created_at, updated_at)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
    [record.id, record.app_id, JSON.stringify(record.data),
     record.state || '', record.created_by, record.created_at, record.updated_at]
  );
  saveToLocal();
}

export function getRecords(appId: string): any[] {
  if (!db) return [];
  const results = db.exec(`SELECT * FROM records WHERE app_id = '${appId}'`);
  if (!results[0]) return [];
  
  return results[0].values.map((row: any) => ({
    id: row[0],
    app_id: row[1],
    data: JSON.parse(row[2]),
    state: row[3],
    created_by: row[4],
    created_at: row[5],
    updated_by: row[6],
    updated_at: row[7],
  }));
}

export function updateRecord(id: string, data: any): void {
  if (!db) return;
  db.run(
    `UPDATE records SET data = ?, updated_at = ? WHERE id = ?`,
    [JSON.stringify(data), Date.now(), id]
  );
  saveToLocal();
}

export function deleteRecord(id: string): void {
  if (!db) return;
  db.run('DELETE FROM records WHERE id = ?', [id]);
  saveToLocal();
}

// ============================================
// 批量操作
// ============================================

export function bulkDeleteRecords(ids: string[]): void {
  if (!db || ids.length === 0) return;
  const placeholders = ids.map(() => '?').join(',');
  db.run(`DELETE FROM records WHERE id IN (${placeholders})`, ids);
  saveToLocal();
}

export function bulkUpdateState(ids: string[], newState: string): void {
  if (!db || ids.length === 0) return;
  const placeholders = ids.map(() => '?').join(',');
  db.run(
    `UPDATE records SET state = ?, updated_at = ? WHERE id IN (${placeholders})`,
    [newState, Date.now(), ...ids]
  );
  saveToLocal();
}

// ============================================
// 导出
// ============================================

export function exportSchema(): string {
  if (!db) return '{}';
  return JSON.stringify({
    fields: getFields(),
    apps: getApps(),
    roles: db.exec('SELECT * FROM roles')[0]?.values || [],
  }, null, 2);
}

export function importSchema(json: string): void {
  try {
    const data = JSON.parse(json);
    
    // 清空现有数据
    if (db) {
      db.run('DELETE FROM fields');
      db.run('DELETE FROM apps');
      db.run('DELETE FROM records');
    }
    
    // 导入字段
    data.fields?.forEach(createField);
    
    // 导入应用
    data.apps?.forEach(createApp);
    
    saveToLocal();
  } catch (e) {
    console.error('Import failed:', e);
    throw e;
  }
}