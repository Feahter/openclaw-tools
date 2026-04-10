import './index.css';
import { App } from './App';

// 初始化并渲染
document.getElementById('root')!.innerHTML = '<div style="padding:20px">加载中...</div>';

import('./core/storage').then(({ initStorage }) => {
  initStorage().then(() => {
    // 存储初始化成功，渲染 App
    const root = document.getElementById('root')!;
    root.innerHTML = '';
    // @ts-ignore
    const app = new App();
    // 简单渲染
    import('react-dom').then(({ createRoot }) => {
      createRoot(root).render(app.render());
    });
  }).catch(err => {
    console.error('初始化失败:', err);
    document.getElementById('root')!.innerHTML = '<div style="padding:20px;color:red">初始化失败: ' + err.message + '</div>';
  });
});