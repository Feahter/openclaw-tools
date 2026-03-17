# Dashboard Reference

Templates for KPI dashboards and metric overviews.

---

## KPI Dashboard (KPI 仪表盘)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #f8fafc); color: var(--color-text, #1f2937); }
  .container { max-width: 700px; margin: 0 auto; }
  h3 { text-align: center; margin-bottom: 20px; }
  .kpi-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 20px; }
  .kpi-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .kpi-label { font-size: 13px; color: #64748b; font-weight: 500; }
  .kpi-value { font-size: 28px; font-weight: 700; margin: 8px 0 4px; }
  .kpi-change { font-size: 13px; display: flex; align-items: center; gap: 4px; }
  .up { color: #10b981; }
  .down { color: #ef4444; }
  .kpi-bar { height: 4px; background: #f1f5f9; border-radius: 2px; margin-top: 12px; }
  .kpi-bar-fill { height: 100%; border-radius: 2px; }
  .chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .chart-card { background: white; padding: 16px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .chart-title { font-size: 13px; font-weight: 600; margin-bottom: 12px; color: #374151; }
</style>
</head>
<body>
<div class="container">
  <h3>业务概览 · 本月</h3>
  
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">总收入</div>
      <div class="kpi-value" style="color:#3b82f6">¥248,500</div>
      <div class="kpi-change up">↑ 12.5% 较上月</div>
      <div class="kpi-bar"><div class="kpi-bar-fill" style="width:78%;background:#3b82f6"></div></div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">新增用户</div>
      <div class="kpi-value" style="color:#10b981">1,284</div>
      <div class="kpi-change up">↑ 8.3% 较上月</div>
      <div class="kpi-bar"><div class="kpi-bar-fill" style="width:64%;background:#10b981"></div></div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">订单量</div>
      <div class="kpi-value" style="color:#f59e0b">3,672</div>
      <div class="kpi-change down">↓ 2.1% 较上月</div>
      <div class="kpi-bar"><div class="kpi-bar-fill" style="width:55%;background:#f59e0b"></div></div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">客户满意度</div>
      <div class="kpi-value" style="color:#8b5cf6">4.8 / 5</div>
      <div class="kpi-change up">↑ 0.2 较上月</div>
      <div class="kpi-bar"><div class="kpi-bar-fill" style="width:96%;background:#8b5cf6"></div></div>
    </div>
  </div>
  
  <div class="chart-row">
    <div class="chart-card">
      <div class="chart-title">收入趋势（近7天）</div>
      <canvas id="trendChart" height="120"></canvas>
    </div>
    <div class="chart-card">
      <div class="chart-title">流量来源</div>
      <canvas id="sourceChart" height="120"></canvas>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
new Chart(document.getElementById('trendChart'), {
  type: 'line',
  data: {
    labels: ['周一','周二','周三','周四','周五','周六','周日'],
    datasets: [{
      data: [8200, 9100, 7800, 10200, 11500, 13200, 9800],
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59,130,246,0.1)',
      tension: 0.4, fill: true, pointRadius: 3
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false } },
      y: { ticks: { callback: v => '¥' + (v/1000).toFixed(0) + 'K' } }
    }
  }
});

new Chart(document.getElementById('sourceChart'), {
  type: 'doughnut',
  data: {
    labels: ['搜索', '直接', '社交', '推荐'],
    datasets: [{
      data: [42, 28, 18, 12],
      backgroundColor: ['#3b82f6','#10b981','#f59e0b','#8b5cf6'],
      borderWidth: 0
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 11 } } }
    }
  }
});
</script>
</body>
</html>
```

---

## Progress Dashboard (进度仪表盘)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .container { max-width: 600px; margin: 0 auto; }
  h3 { text-align: center; margin-bottom: 20px; }
  .progress-item { margin-bottom: 20px; }
  .progress-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .progress-name { font-size: 14px; font-weight: 600; }
  .progress-meta { font-size: 13px; color: #64748b; }
  .progress-bar { height: 10px; background: #f1f5f9; border-radius: 5px; overflow: hidden; }
  .progress-fill { height: 100%; border-radius: 5px; transition: width 0.8s ease; }
  .progress-detail { font-size: 12px; color: #94a3b8; margin-top: 4px; }
  .status-badge { font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 500; }
  .on-track { background: #dcfce7; color: #166534; }
  .at-risk { background: #fef3c7; color: #92400e; }
  .delayed { background: #fee2e2; color: #991b1b; }
</style>
</head>
<body>
<div class="container">
  <h3>Q2 目标完成进度</h3>
  
  <div class="progress-item">
    <div class="progress-header">
      <span class="progress-name">年度营收目标</span>
      <span class="status-badge on-track">进展顺利</span>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" style="width:68%;background:linear-gradient(90deg,#3b82f6,#10b981)"></div>
    </div>
    <div class="progress-detail">¥680万 / ¥1000万 · 68% · 预计12月达成</div>
  </div>
  
  <div class="progress-item">
    <div class="progress-header">
      <span class="progress-name">用户增长目标</span>
      <span class="status-badge on-track">进展顺利</span>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" style="width:82%;background:linear-gradient(90deg,#10b981,#3b82f6)"></div>
    </div>
    <div class="progress-detail">82,000 / 100,000 用户 · 82%</div>
  </div>
  
  <div class="progress-item">
    <div class="progress-header">
      <span class="progress-name">产品功能交付</span>
      <span class="status-badge at-risk">存在风险</span>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" style="width:45%;background:linear-gradient(90deg,#f59e0b,#ef4444)"></div>
    </div>
    <div class="progress-detail">9 / 20 功能 · 45% · 落后计划2周</div>
  </div>
  
  <div class="progress-item">
    <div class="progress-header">
      <span class="progress-name">NPS 净推荐值</span>
      <span class="status-badge delayed">已延期</span>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" style="width:30%;background:#ef4444"></div>
    </div>
    <div class="progress-detail">当前 NPS: 30 / 目标: 60 · 需要重点关注</div>
  </div>
</div>
</body>
</html>
```

---

## Tips

- Use KPI cards for 4–8 key metrics with trend indicators
- Always show change vs. previous period (↑/↓ with %)
- Use color coding: blue=revenue, green=growth, amber=warning, purple=quality
- Combine mini-charts with KPI cards for richer context
- Progress bars work well for goal tracking with clear targets
