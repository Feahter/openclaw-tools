# OpenNoCode

纯前端无代码系统 | Pure JS No-Code Platform

## 功能

- 字段系统（12种类型）
- 应用管理
- 数据 CRUD
- SQLite + localStorage 存储
- 表格/看板视图
- 公式字段
- 权限系统
- 状态机
- 模板引擎
- 回收站
- 导入/导出

## 使用

直接在浏览器打开 `index.html`

```bash
# 或启动本地服务器
npx serve .
```

## 开发

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build
```

## 架构

```
src/
├── core/       # 状态管理
├── ui/        # 渲染层
└── utils/     # 工具函数
```

## 许可

MIT
