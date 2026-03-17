# Comparison Tables Reference

Templates for feature comparisons and product matrices.

---

## Feature Comparison Matrix (功能对比矩阵)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .container { max-width: 700px; margin: 0 auto; overflow-x: auto; }
  h3 { text-align: center; margin-bottom: 20px; }
  table { width: 100%; border-collapse: collapse; }
  th { padding: 12px 16px; text-align: center; font-size: 14px; font-weight: 600; }
  td { padding: 10px 16px; text-align: center; font-size: 13px; border-bottom: 1px solid #f1f5f9; }
  tr:hover td { background: #f8fafc; }
  .feature-name { text-align: left; font-weight: 500; color: #374151; }
  .check { color: #10b981; font-size: 18px; }
  .cross { color: #ef4444; font-size: 18px; }
  .partial { color: #f59e0b; font-size: 14px; }
  .plan-header { padding: 16px; border-radius: 12px 12px 0 0; }
  .plan-free { background: #f8fafc; color: #374151; }
  .plan-pro { background: #3b82f6; color: white; }
  .plan-enterprise { background: #1e293b; color: white; }
  .plan-name { font-size: 16px; font-weight: 700; }
  .plan-price { font-size: 13px; opacity: 0.8; margin-top: 4px; }
  .badge { display: inline-block; background: #fef3c7; color: #92400e; font-size: 11px; padding: 2px 8px; border-radius: 20px; margin-left: 6px; }
  .section-header td { background: #f1f5f9; font-weight: 600; font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; text-align: left; padding: 8px 16px; }
</style>
</head>
<body>
<div class="container">
  <h3>产品方案对比</h3>
  <table>
    <thead>
      <tr>
        <th style="width:40%"></th>
        <th><div class="plan-header plan-free"><div class="plan-name">免费版</div><div class="plan-price">¥0 / 月</div></div></th>
        <th><div class="plan-header plan-pro"><div class="plan-name">专业版 <span class="badge">推荐</span></div><div class="plan-price">¥99 / 月</div></div></th>
        <th><div class="plan-header plan-enterprise"><div class="plan-name">企业版</div><div class="plan-price">联系销售</div></div></th>
      </tr>
    </thead>
    <tbody>
      <tr class="section-header"><td colspan="4">基础功能</td></tr>
      <tr>
        <td class="feature-name">用户数量</td>
        <td>1 人</td>
        <td>5 人</td>
        <td>无限制</td>
      </tr>
      <tr>
        <td class="feature-name">存储空间</td>
        <td>1 GB</td>
        <td>50 GB</td>
        <td>无限制</td>
      </tr>
      <tr>
        <td class="feature-name">API 调用</td>
        <td>1,000 次/月</td>
        <td>100,000 次/月</td>
        <td>无限制</td>
      </tr>
      <tr class="section-header"><td colspan="4">高级功能</td></tr>
      <tr>
        <td class="feature-name">自定义域名</td>
        <td><span class="cross">✗</span></td>
        <td><span class="check">✓</span></td>
        <td><span class="check">✓</span></td>
      </tr>
      <tr>
        <td class="feature-name">SSO 登录</td>
        <td><span class="cross">✗</span></td>
        <td><span class="partial">部分支持</span></td>
        <td><span class="check">✓</span></td>
      </tr>
      <tr>
        <td class="feature-name">数据导出</td>
        <td><span class="cross">✗</span></td>
        <td><span class="check">✓</span></td>
        <td><span class="check">✓</span></td>
      </tr>
      <tr>
        <td class="feature-name">优先支持</td>
        <td><span class="cross">✗</span></td>
        <td><span class="check">✓</span></td>
        <td><span class="check">✓ 专属客服</span></td>
      </tr>
      <tr>
        <td class="feature-name">SLA 保障</td>
        <td><span class="cross">✗</span></td>
        <td>99.9%</td>
        <td>99.99%</td>
      </tr>
    </tbody>
  </table>
</div>
</body>
</html>
```

---

## Side-by-Side Comparison (并排对比)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .container { max-width: 700px; margin: 0 auto; }
  h3 { text-align: center; margin-bottom: 20px; }
  .comparison { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .card { border: 2px solid #e2e8f0; border-radius: 12px; overflow: hidden; }
  .card.winner { border-color: #3b82f6; }
  .card-header { padding: 16px; text-align: center; }
  .card-header.a { background: #eff6ff; }
  .card-header.b { background: #f0fdf4; }
  .card-name { font-size: 18px; font-weight: 700; }
  .card-subtitle { font-size: 13px; color: #64748b; margin-top: 4px; }
  .card-body { padding: 16px; }
  .metric { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f1f5f9; }
  .metric:last-child { border-bottom: none; }
  .metric-name { font-size: 13px; color: #64748b; }
  .metric-value { font-size: 14px; font-weight: 600; }
  .better { color: #10b981; }
  .worse { color: #ef4444; }
  .winner-badge { display: inline-block; background: #3b82f6; color: white; font-size: 11px; padding: 2px 8px; border-radius: 20px; margin-top: 8px; }
</style>
</head>
<body>
<div class="container">
  <h3>方案对比</h3>
  <div class="comparison">
    <div class="card">
      <div class="card-header a">
        <div class="card-name">方案 A</div>
        <div class="card-subtitle">传统架构</div>
      </div>
      <div class="card-body">
        <div class="metric">
          <span class="metric-name">性能</span>
          <span class="metric-value worse">1,000 QPS</span>
        </div>
        <div class="metric">
          <span class="metric-name">成本</span>
          <span class="metric-value better">¥500/月</span>
        </div>
        <div class="metric">
          <span class="metric-name">扩展性</span>
          <span class="metric-value worse">有限</span>
        </div>
        <div class="metric">
          <span class="metric-name">维护难度</span>
          <span class="metric-value better">低</span>
        </div>
        <div class="metric">
          <span class="metric-name">上手时间</span>
          <span class="metric-value better">1 周</span>
        </div>
      </div>
    </div>
    <div class="card winner">
      <div class="card-header b">
        <div class="card-name">方案 B</div>
        <div class="card-subtitle">微服务架构</div>
        <div class="winner-badge">推荐</div>
      </div>
      <div class="card-body">
        <div class="metric">
          <span class="metric-name">性能</span>
          <span class="metric-value better">10,000 QPS</span>
        </div>
        <div class="metric">
          <span class="metric-name">成本</span>
          <span class="metric-value worse">¥2,000/月</span>
        </div>
        <div class="metric">
          <span class="metric-name">扩展性</span>
          <span class="metric-value better">无限</span>
        </div>
        <div class="metric">
          <span class="metric-name">维护难度</span>
          <span class="metric-value worse">高</span>
        </div>
        <div class="metric">
          <span class="metric-name">上手时间</span>
          <span class="metric-value worse">1 个月</span>
        </div>
      </div>
    </div>
  </div>
</div>
</body>
</html>
```

---

## Tips

- Use ✓/✗ for binary features, text for quantitative values
- Highlight the recommended option with a distinct border/badge
- Use color coding: green=better, red=worse, yellow=partial
- Group related features with section headers
- Keep to 3-5 options max for readability
