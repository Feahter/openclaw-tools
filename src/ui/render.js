// 渲染层 - UI = f(state)
import State from '../core/state.js';

// 应用列表渲染
function renderApps() {
  const apps = State.apps;
  if (!apps.length) {
    return '<div class="empty">暂无应用</div>';
  }
  return `<table><thead><tr><th>名称</th><th>类型</th><th>字段数</th><th>创建时间</th></tr></thead>
    <tbody>${apps.map(a => `<tr onclick="selectApp('${a.id}')" style="cursor:pointer">
      <td>${a.name}</td>
      <td><span class="tag">${a.type}</span></td>
      <td>${a.fields?.length || 0}</td>
      <td>${new Date(a.created_at).toLocaleDateString()}</td>
    </tr>`).join('')}</tbody></table>`;
}

// 字段列表渲染
function renderFields() {
  const fields = State.fields;
  if (!fields.length) {
    return '<div class="empty">暂无字段</div>';
  }
  return `<table><thead><tr><th>标识</th><th>名称</th><th>类型</th></tr></thead>
    <tbody>${fields.map(f => `<tr>
      <td>${f.name}</td>
      <td>${f.label}</td>
      <td><span class="tag">${f.type}</span></td>
    </tr>`).join('')}</tbody></table>`;
}

// 数据视图渲染
function renderData(appId) {
  const records = State.records[appId] || [];
  const appFields = State.fields;
  
  // 表头
  const headers = ['<th>ID</th>'];
  appFields.forEach(f => headers.push(`<th>${f.label}</th>`));
  headers.push('<th>创建时间</th><th>操作</th>');
  
  // 行
  const rows = records.length ? records.map(r => {
    const cells = appFields.map(f => {
      const val = r.data?.[f.name];
      if (f.type === 'boolean') return val ? '<td>✓</td>' : '<td></td>';
      return `<td>${val || '-'}</td>`;
    }).join('');
    return `<tr data-id="${r.id}">
      <td>${r.id.slice(0, 8)}</td>${cells}
      <td>${new Date(r.created_at).toLocaleString()}</td>
      <td>
        <button class="btn-sm" onclick="editRecord('${r.id}')">编辑</button>
        <button class="btn-sm" onclick="deleteRecord('${r.id}')">删除</button>
      </td>
    </tr>`;
  }).join('') : `<tr><td colspan="${appFields.length + 3}" class="empty">暂无数据</td></tr>`;
  
  return `<div class="toolbar">
    <input class="input" placeholder="搜索" oninput="filterData(this.value)">
    <button class="btn btn-primary" onclick="showModal('record')">+ 新建</button>
  </div>
  <table><thead><tr>${headers.join('')}</tr></thead><tbody>${rows}</tbody></table>`;
}

// 看板视图
function renderKanban(appId) {
  const records = State.records[appId] || [];
  const statuses = State.stateMachines[appId]?.states || ['待处理', '进行中', '已完成'];
  
  return `<div class="kanban">${statuses.map(status => {
    const colRecords = records.filter(r => r.data?.status === status);
    return `<div class="kanban-col">
      <div class="kanban-header">${status} (${colRecords.length})</div>
      <div class="kanban-body">${colRecords.map(r => `<div class="kanban-card" draggable="true" data-id="${r.id}">
        ${r.data?.title || r.id.slice(0, 8)}
      </div>`).join('')}</div>
    </div>`;
  }).join('')}</div>`;
}

// 回收站渲染
function renderTrash() {
  const records = State.deletedRecords;
  if (!records.length) {
    return '<div class="empty">回收站为空</div>';
  }
  return `<table><thead><tr><th>ID</th><th>删除时间</th><th>操作</th></tr></thead>
    <tbody>${records.map(r => `<tr>
      <td>${r.id.slice(0, 8)}</td>
      <td>${new Date(r.deleted_at).toLocaleString()}</td>
      <td>
        <button class="btn-sm" onclick="restoreRecord('${r.id}')">恢���</button>
        <button class="btn-sm" onclick="permanentDelete('${r.id}')">彻底删除</button>
      </td>
    </tr>`).join('')}</tbody></table>`;
}

// 主渲染入口
function render() {
  const container = document.getElementById('content');
  if (!container) return;
  
  switch (State.currentView) {
    case 'apps':
      container.innerHTML = renderApps();
      break;
    case 'fields':
      container.innerHTML = renderFields();
      break;
    case 'data':
      if (State.selectedApp) {
        container.innerHTML = renderData(State.selectedApp.id);
      }
      break;
    case 'kanban':
      if (State.selectedApp) {
        container.innerHTML = renderKanban(State.selectedApp.id);
      }
      break;
    case 'trash':
      container.innerHTML = renderTrash();
      break;
  }
}

// 过滤
function filterData(query) {
  // 实现过滤逻辑
  render();
}

export default { renderApps, renderFields, renderData, renderKanban, renderTrash, render, filterData };
