# Charts Reference

Templates for data visualization widgets using Chart.js.

## CDN

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

---

## Line Chart (趋势图)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 16px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .chart-container { position: relative; width: 100%; max-width: 700px; margin: 0 auto; }
  h3 { text-align: center; margin: 0 0 16px; font-size: 16px; }
</style>
</head>
<body>
<div class="chart-container">
  <h3>标题</h3>
  <canvas id="chart"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
new Chart(document.getElementById('chart'), {
  type: 'line',
  data: {
    labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
    datasets: [{
      label: '数据系列',
      data: [65, 78, 90, 81, 95, 110],
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59,130,246,0.1)',
      tension: 0.4,
      fill: true
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { position: 'top' } },
    scales: { y: { beginAtZero: false } }
  }
});
</script>
</body>
</html>
```

---

## Bar Chart (柱状图)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 16px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .chart-container { position: relative; width: 100%; max-width: 700px; margin: 0 auto; }
  h3 { text-align: center; margin: 0 0 16px; font-size: 16px; }
</style>
</head>
<body>
<div class="chart-container">
  <h3>标题</h3>
  <canvas id="chart"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
new Chart(document.getElementById('chart'), {
  type: 'bar',
  data: {
    labels: ['A', 'B', 'C', 'D', 'E'],
    datasets: [{
      label: '数值',
      data: [42, 78, 55, 91, 63],
      backgroundColor: ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6'],
      borderRadius: 6
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true } }
  }
});
</script>
</body>
</html>
```

---

## Pie / Donut Chart (饼图/环形图)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 16px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .chart-container { position: relative; width: 100%; max-width: 400px; margin: 0 auto; }
  h3 { text-align: center; margin: 0 0 16px; font-size: 16px; }
</style>
</head>
<body>
<div class="chart-container">
  <h3>标题</h3>
  <canvas id="chart"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
new Chart(document.getElementById('chart'), {
  type: 'doughnut',
  data: {
    labels: ['类别A', '类别B', '类别C', '类别D'],
    datasets: [{
      data: [35, 25, 25, 15],
      backgroundColor: ['#3b82f6','#10b981','#f59e0b','#ef4444'],
      borderWidth: 2,
      borderColor: '#fff'
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'bottom' },
      tooltip: { callbacks: { label: ctx => `${ctx.label}: ${ctx.parsed}%` } }
    }
  }
});
</script>
</body>
</html>
```

---

## Multi-Dataset Line Chart (多系列对比)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 16px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .chart-container { position: relative; width: 100%; max-width: 700px; margin: 0 auto; }
  h3 { text-align: center; margin: 0 0 16px; font-size: 16px; }
</style>
</head>
<body>
<div class="chart-container">
  <h3>多系列对比</h3>
  <canvas id="chart"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
new Chart(document.getElementById('chart'), {
  type: 'line',
  data: {
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    datasets: [
      { label: '系列A', data: [65, 78, 90, 110], borderColor: '#3b82f6', tension: 0.4 },
      { label: '系列B', data: [45, 60, 75, 88], borderColor: '#10b981', tension: 0.4 },
      { label: '系列C', data: [30, 45, 55, 70], borderColor: '#f59e0b', tension: 0.4 }
    ]
  },
  options: {
    responsive: true,
    plugins: { legend: { position: 'top' } }
  }
});
</script>
</body>
</html>
```

---

## Tips

- Replace placeholder data with actual values from user context
- Adjust colors to match the data's semantic meaning (red for negative, green for positive)
- Add `onClick` handlers to enable drill-down interactions
- Use `animation: false` for large datasets to improve performance
