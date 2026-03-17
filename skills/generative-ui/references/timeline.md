# Timeline & Gantt Charts

Templates for project schedules and time-based visualizations.

---

## Horizontal Timeline (水平时间线)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .container { max-width: 700px; margin: 0 auto; }
  h3 { text-align: center; margin-bottom: 24px; }
  .timeline { position: relative; padding: 20px 0; }
  .timeline::before { content: ''; position: absolute; top: 50%; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #3b82f6, #8b5cf6); border-radius: 2px; }
  .events { display: flex; justify-content: space-between; position: relative; }
  .event { text-align: center; flex: 1; position: relative; }
  .event::before { content: ''; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 16px; height: 16px; background: white; border: 3px solid #3b82f6; border-radius: 50%; z-index: 1; }
  .event.completed::before { background: #3b82f6; }
  .event.milestone::before { background: #f59e0b; border-color: #f59e0b; }
  .date { font-size: 12px; color: #64748b; margin-top: 24px; font-weight: 500; }
  .title { font-size: 13px; font-weight: 600; margin-top: 4px; }
  .desc { font-size: 11px; color: #94a3b8; margin-top: 2px; }
</style>
</head>
<body>
<div class="container">
  <h3>项目里程碑</h3>
  <div class="timeline">
    <div class="events">
      <div class="event completed">
        <div class="date">1月</div>
        <div class="title">需求分析</div>
        <div class="desc">已完成</div>
      </div>
      <div class="event completed">
        <div class="date">3月</div>
        <div class="title">设计阶段</div>
        <div class="desc">已完成</div>
      </div>
      <div class="event milestone">
        <div class="date">6月</div>
        <div class="title">MVP发布</div>
        <div class="desc">当前</div>
      </div>
      <div class="event">
        <div class="date">9月</div>
        <div class="title">公测</div>
        <div class="desc">待开始</div>
      </div>
      <div class="event">
        <div class="date">12月</div>
        <div class="title">正式上线</div>
        <div class="desc">待开始</div>
      </div>
    </div>
  </div>
</div>
</body>
</html>
```

---

## Vertical Timeline (垂直时间线)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .container { max-width: 600px; margin: 0 auto; }
  h3 { text-align: center; margin-bottom: 24px; }
  .timeline { position: relative; padding-left: 30px; }
  .timeline::before { content: ''; position: absolute; left: 8px; top: 0; bottom: 0; width: 2px; background: #e2e8f0; }
  .item { position: relative; margin-bottom: 24px; padding-left: 24px; }
  .item::before { content: ''; position: absolute; left: -26px; top: 4px; width: 12px; height: 12px; background: #3b82f6; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 0 2px #3b82f6; }
  .item.highlight::before { background: #f59e0b; box-shadow: 0 0 0 2px #f59e0b; }
  .date { font-size: 12px; color: #64748b; font-weight: 500; }
  .title { font-size: 15px; font-weight: 600; margin: 4px 0; }
  .desc { font-size: 13px; color: #64748b; line-height: 1.5; }
  .tag { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 12px; background: #dbeafe; color: #1d4ed8; margin-top: 8px; }
</style>
</head>
<body>
<div class="container">
  <h3>版本发布历史</h3>
  <div class="timeline">
    <div class="item highlight">
      <div class="date">2024年3月15日</div>
      <div class="title">v2.5.0 重大更新</div>
      <div class="desc">新增 AI 助手功能，支持自然语言查询和智能推荐</div>
      <span class="tag">最新</span>
    </div>
    <div class="item">
      <div class="date">2024年2月1日</div>
      <div class="title">v2.4.0 性能优化</div>
      <div class="desc">页面加载速度提升 40%，支持离线模式</div>
    </div>
    <div class="item">
      <div class="date">2024年1月10日</div>
      <div class="title">v2.3.0 移动端适配</div>
      <div class="desc">全新移动端界面，支持 PWA 安装</div>
    </div>
    <div class="item">
      <div class="date">2023年12月1日</div>
      <div class="title">v2.0.0 正式发布</div>
      <div class="desc">全新架构重构，API 兼容性升级</div>
    </div>
  </div>
</div>
</body>
</html>
```

---

## Gantt Chart (甘特图)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .container { max-width: 700px; margin: 0 auto; overflow-x: auto; }
  h3 { text-align: center; margin-bottom: 20px; }
  .gantt { display: grid; grid-template-columns: 120px repeat(12, 1fr); gap: 1px; background: #e2e8f0; border-radius: 8px; overflow: hidden; }
  .gantt > div { background: white; padding: 8px; font-size: 12px; }
  .header { background: #f8fafc; font-weight: 600; text-align: center; color: #64748b; }
  .task-name { font-weight: 500; color: #374151; display: flex; align-items: center; }
  .bar { background: #3b82f6; border-radius: 4px; height: 20px; position: relative; }
  .bar.design { background: #8b5cf6; }
  .bar.dev { background: #3b82f6; }
  .bar.test { background: #f59e0b; }
  .bar.deploy { background: #10b981; }
  .bar.partial { background: linear-gradient(90deg, #3b82f6 50%, #e2e8f0 50%); }
  .legend { display: flex; gap: 16px; justify-content: center; margin-top: 16px; font-size: 12px; }
  .legend-item { display: flex; align-items: center; gap: 6px; }
  .legend-color { width: 12px; height: 12px; border-radius: 3px; }
</style>
</head>
<body>
<div class="container">
  <h3>Q2 项目进度</h3>
  <div class="gantt">
    <!-- Header -->
    <div class="header">任务</div>
    <div class="header">4月</div>
    <div class="header">5月</div>
    <div class="header">6月</div>
    <div class="header" style="grid-column: 5">7月</div>
    <div class="header" style="grid-column: 6">8月</div>
    <div class="header" style="grid-column: 7">9月</div>
    <div class="header" style="grid-column: 8">10月</div>
    <div class="header" style="grid-column: 9">11月</div>
    <div class="header" style="grid-column: 10">12月</div>
    <div class="header" style="grid-column: 11">1月</div>
    <div class="header" style="grid-column: 12">2月</div>
    <div class="header" style="grid-column: 13">3月</div>
    
    <!-- Task 1 -->
    <div class="task-name">需求分析</div>
    <div style="grid-column: 2 / 4"><div class="bar design" style="width: 100%"></div></div>
    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>
    
    <!-- Task 2 -->
    <div class="task-name">UI设计</div>
    <div></div>
    <div style="grid-column: 3 / 5"><div class="bar design" style="width: 100%"></div></div>
    <div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div>
    
    <!-- Task 3 -->
    <div class="task-name">前端开发</div>
    <div></div><div></div>
    <div style="grid-column: 4 / 7"><div class="bar dev" style="width: 100%"></div></div>
    <div></div><div></div><div></div><div></div><div></div><div></div>
    
    <!-- Task 4 -->
    <div class="task-name">后端开发</div>
    <div></div><div></div>
    <div style="grid-column: 4 / 7"><div class="bar dev" style="width: 100%"></div></div>
    <div></div><div></div><div></div><div></div><div></div><div></div>
    
    <!-- Task 5 -->
    <div class="task-name">测试</div>
    <div></div><div></div><div></div><div></div>
    <div style="grid-column: 6 / 8"><div class="bar test" style="width: 100%"></div></div>
    <div></div><div></div><div></div><div></div>
    
    <!-- Task 6 -->
    <div class="task-name">部署上线</div>
    <div></div><div></div><div></div><div></div><div></div><div></div>
    <div style="grid-column: 8"><div class="bar deploy" style="width: 100%"></div></div>
    <div></div><div></div><div></div><div></div>
  </div>
  
  <div class="legend">
    <div class="legend-item"><div class="legend-color" style="background:#8b5cf6"></div>设计</div>
    <div class="legend-item"><div class="legend-color" style="background:#3b82f6"></div>开发</div>
    <div class="legend-item"><div class="legend-color" style="background:#f59e0b"></div>测试</div>
    <div class="legend-item"><div class="legend-color" style="background:#10b981"></div>部署</div>
  </div>
</div>
</body>
</html>
```

---

## Tips

- Use horizontal timeline for 3–6 milestones with equal spacing
- Use vertical timeline for chronological lists with descriptions
- Use Gantt for project schedules with dependencies
- Color-code by status: completed (green), current (amber), future (gray)
