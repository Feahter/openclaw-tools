// 状态层 - 单一数据源
const State = {
  apps: [],
  fields: [],
  records: {},
  deletedRecords: [],
  stateMachines: {},
  roles: ['admin', 'editor', 'viewer'],
  currentRole: 'admin',
  currentView: 'apps',
  selectedApp: null,
  
  // 状态更新
  setView(view) { this.currentView = view; },
  setRole(role) { this.currentRole = role; },
  selectApp(app) { this.selectedApp = app; },
  
  // 应用 CRUD
  addApp(app) { this.apps.push(app); },
  updateApp(id, data) {
    const idx = this.apps.findIndex(a => a.id === id);
    if (idx >= 0) this.apps[idx] = { ...this.apps[idx], ...data };
  },
  deleteApp(id) {
    this.apps = this.apps.filter(a => a.id !== id);
  },
  
  // 字段 CRUD
  addField(field) { this.fields.push(field); },
  updateField(id, data) {
    const idx = this.fields.findIndex(f => f.id === id);
    if (idx >= 0) this.fields[idx] = { ...this.fields[idx], ...data };
  },
  deleteField(id) {
    this.fields = this.fields.filter(f => f.id !== id);
  },
  
  // 记录 CRUD
  addRecord(appId, record) {
    if (!this.records[appId]) this.records[appId] = [];
    this.records[appId].push(record);
  },
  updateRecord(appId, id, data) {
    const recs = this.records[appId];
    if (!recs) return;
    const idx = recs.findIndex(r => r.id === id);
    if (idx >= 0) recs[idx] = { ...recs[idx], ...data, updated_at: Date.now() };
  },
  deleteRecord(appId, id) {
    if (!this.records[appId]) return;
    const rec = this.records[appId].find(r => r.id === id);
    if (rec) {
      this.records[appId] = this.records[appId].filter(r => r.id !== id);
      rec.deleted_at = Date.now();
      this.deletedRecords.push(rec);
    }
  },
  
  // 回收站
  restoreRecord(id) {
    const idx = this.deletedRecords.findIndex(r => r.id === id);
    if (idx >= 0) {
      const rec = this.deletedRecords.splice(idx, 1)[0];
      if (!this.records[rec.app_id]) this.records[rec.app_id] = [];
      this.records[rec.app_id].push(rec);
    }
  },
  permanentDelete(id) {
    this.deletedRecords = this.deletedRecords.filter(r => r.id !== id);
  },
  
  // 序列化
  toJSON() {
    return JSON.stringify({
      apps: this.apps,
      fields: this.fields,
      records: this.records,
      deletedRecords: this.deletedRecords,
      stateMachines: this.stateMachines
    });
  },
  
  fromJSON(json) {
    try {
      const data = JSON.parse(json);
      this.apps = data.apps || [];
      this.fields = data.fields || [];
      this.records = data.records || {};
      this.deletedRecords = data.deletedRecords || [];
      this.stateMachines = data.stateMachines || {};
    } catch (e) {
      console.error('State Load Error:', e);
    }
  }
};

export default State;
