import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import * as storage from './core/storage';
import type { App, Field, Record, FieldType } from './types';

export function App() {
  const [apps, setApps] = useState<App[]>([]);
  const [fields, setFields] = useState<Field[]>([]);
  const [selectedApp, setSelectedApp] = useState<App | null>(null);
  const [records, setRecords] = useState<Record[]>([]);
  const [view, setView] = useState<'apps' | 'fields' | 'data'>('apps');
  const [showModal, setShowModal] = useState<'app' | 'field' | null>(null);

  useEffect(() => {
    storage.initStorage().then(() => {
      setApps(storage.getApps());
      setFields(storage.getFields());
    });
  }, []);

  // 创建应用
  const handleCreateApp = (name: string, description: string) => {
    const app: App = {
      id: uuidv4(),
      name,
      type: 'data',
      description,
      fields: [],
      views: [{ id: uuidv4(), type: 'table', name: '默认表格', config: {} }],
      created_at: Date.now(),
      updated_at: Date.now(),
    };
    storage.createApp(app);
    setApps([...apps, app]);
    setShowModal(null);
  };

  // 创建字段
  const handleCreateField = (name: string, type: FieldType, label: string) => {
    const field: Field = {
      id: uuidv4(),
      name,
      type,
      meta: { label },
      permissions: [],
      created_at: Date.now(),
      updated_at: Date.now(),
    };
    storage.createField(field);
    setFields([...fields, field]);
    setShowModal(null);
  };

  // 选择应用
  const handleSelectApp = (app: App) => {
    setSelectedApp(app);
    setRecords(storage.getRecords(app.id));
    setView('data');
  };

  // 创建记录
  const handleCreateRecord = (data: Record<string, unknown>) => {
    const record: Record = {
      id: uuidv4(),
      app_id: selectedApp!.id,
      data,
      created_by: 'user',
      created_at: Date.now(),
      updated_at: Date.now(),
    };
    storage.createRecord(record);
    setRecords([...records, record]);
  };

  return (
    <div className="app-container">
      {/* 侧边栏 */}
      <div className="sidebar">
        <h1 style={{ fontSize: 18, fontWeight: 700, marginBottom: 24 }}>OpenNoCode</h1>
        
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <button
            onClick={() => setView('apps')}
            style={{
              padding: '8px 12px',
              borderRadius: 6,
              background: view === 'apps' ? '#dbeafe' : 'transparent',
              color: view === 'apps' ? '#1d4ed8' : '#374151',
              textAlign: 'left',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            应用管理
          </button>
          <button
            onClick={() => setView('fields')}
            style={{
              padding: '8px 12px',
              borderRadius: 6,
              background: view === 'fields' ? '#dbeafe' : 'transparent',
              color: view === 'fields' ? '#1d4ed8' : '#374151',
              textAlign: 'left',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            字段管理
          </button>
        </nav>

        {/* 应用列表 */}
        <div style={{ marginTop: 24 }}>
          <div style={{ fontSize: 13, color: '#6b7280', marginBottom: 8 }}>我的应用</div>
          {apps.map(app => (
            <div
              key={app.id}
              onClick={() => handleSelectApp(app)}
              className="list-item"
            >
              <span style={{ fontSize: 14 }}>{app.name}</span>
              <span className="tag tag-blue" style={{ marginLeft: 'auto' }}>
                {app.type}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* 主内容区 */}
      <div className="main-content">
        {view === 'apps' && (
          <div>
            <div className="toolbar">
              <button className="btn btn-primary" onClick={() => setShowModal('app')}>
                + 新建应用
              </button>
            </div>
            <div className="card">
              <table className="table">
                <thead>
                  <tr>
                    <th>名称</th>
                    <th>类型</th>
                    <th>字段数</th>
                    <th>创建时间</th>
                  </tr>
                </thead>
                <tbody>
                  {apps.map(app => (
                    <tr key={app.id} onClick={() => handleSelectApp(app)} style={{ cursor: 'pointer' }}>
                      <td>{app.name}</td>
                      <td>
                        <span className="tag tag-gray">{app.type}</span>
                      </td>
                      <td>{app.fields.length}</td>
                      <td>{new Date(app.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                  {apps.length === 0 && (
                    <tr>
                      <td colSpan={4} style={{ textAlign: 'center', color: '#9ca3af', padding: 24 }}>
                        暂无应用，点击"新建应用"开始
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {view === 'fields' && (
          <div>
            <div className="toolbar">
              <button className="btn btn-primary" onClick={() => setShowModal('field')}>
                + 新建字段
              </button>
            </div>
            <div className="card">
              <table className="table">
                <thead>
                  <tr>
                    <th>标识</th>
                    <th>名称</th>
                    <th>类型</th>
                    <th>创建时间</th>
                  </tr>
                </thead>
                <tbody>
                  {fields.map(field => (
                    <tr key={field.id}>
                      <td>{field.name}</td>
                      <td>{field.meta.label}</td>
                      <td>
                        <span className="tag tag-gray">{field.type}</span>
                      </td>
                      <td>{new Date(field.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                  {fields.length === 0 && (
                    <tr>
                      <td colSpan={4} style={{ textAlign: 'center', color: '#9ca3af', padding: 24 }}>
                        暂无字段，点击"新建字段"开始
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {view === 'data' && selectedApp && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <button className="btn btn-secondary" onClick={() => setView('apps')}>
                ← 返回
              </button>
              <span style={{ marginLeft: 16, fontSize: 18, fontWeight: 600 }}>
                {selectedApp.name}
              </span>
            </div>
            <div className="toolbar">
              <button className="btn btn-primary" onClick={() => handleCreateRecord({})}>
                + 新建数据
              </button>
            </div>
            <div className="card">
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>数据</th>
                    <th>创建时间</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map(record => (
                    <tr key={record.id}>
                      <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{record.id.slice(0, 8)}</td>
                      <td>{JSON.stringify(record.data)}</td>
                      <td>{new Date(record.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                  {records.length === 0 && (
                    <tr>
                      <td colSpan={3} style={{ textAlign: 'center', color: '#9ca3af', padding: 24 }}>
                        暂无数据，点击"新建数据"开始
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* 模态框 */}
      {showModal === 'app' && (
        <div className="modal-overlay" onClick={() => setShowModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ marginBottom: 16 }}>新建应用</h2>
            <input
              id="appName"
              className="input"
              placeholder="应用名称"
              style={{ marginBottom: 12 }}
            />
            <input
              id="appDesc"
              className="input"
              placeholder="描述（可选）"
              style={{ marginBottom: 16 }}
            />
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-primary" onClick={() => {
                const name = (document.getElementById('appName') as HTMLInputElement).value;
                const desc = (document.getElementById('appDesc') as HTMLInputElement).value;
                if (name) handleCreateApp(name, desc);
              }}>
                创建
              </button>
              <button className="btn btn-secondary" onClick={() => setShowModal(null)}>
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      {showModal === 'field' && (
        <div className="modal-overlay" onClick={() => setShowModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ marginBottom: 16 }}>新建字段</h2>
            <input
              id="fieldName"
              className="input"
              placeholder="字段标识（英文）"
              style={{ marginBottom: 12 }}
            />
            <input
              id="fieldLabel"
              className="input"
              placeholder="字段名称（中文）"
              style={{ marginBottom: 12 }}
            />
            <select id="fieldType" className="input" style={{ marginBottom: 16 }}>
              <option value="text">文本</option>
              <option value="number">数字</option>
              <option value="select">单选</option>
              <option value="date">日期</option>
            </select>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-primary" onClick={() => {
                const name = (document.getElementById('fieldName') as HTMLInputElement).value;
                const label = (document.getElementById('fieldLabel') as HTMLInputElement).value;
                const type = (document.getElementById('fieldType') as HTMLSelectElement).value as FieldType;
                if (name && label) handleCreateField(name, type, label);
              }}>
                创建
              </button>
              <button className="btn btn-secondary" onClick={() => setShowModal(null)}>
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}