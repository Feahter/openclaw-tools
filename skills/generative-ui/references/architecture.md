# Architecture Diagrams Reference

Templates for system architecture and flow diagrams using SVG.

---

## System Architecture Diagram (系统架构图)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  svg { width: 100%; max-width: 700px; display: block; margin: 0 auto; }
  .node { cursor: pointer; transition: opacity 0.2s; }
  .node:hover { opacity: 0.85; }
  .node rect { rx: 8; ry: 8; }
  .label { font-size: 13px; font-weight: 600; fill: white; text-anchor: middle; dominant-baseline: middle; }
  .sublabel { font-size: 11px; fill: rgba(255,255,255,0.8); text-anchor: middle; dominant-baseline: middle; }
  .arrow { stroke: #94a3b8; stroke-width: 1.5; fill: none; marker-end: url(#arrowhead); }
  .layer-label { font-size: 12px; fill: #94a3b8; font-weight: 500; }
</style>
</head>
<body>
<svg viewBox="0 0 700 400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8"/>
    </marker>
  </defs>
  
  <!-- Layer labels -->
  <text x="20" y="80" class="layer-label">客户端</text>
  <text x="20" y="200" class="layer-label">服务层</text>
  <text x="20" y="320" class="layer-label">数据层</text>
  
  <!-- Client Layer -->
  <g class="node">
    <rect x="100" y="55" width="120" height="50" fill="#3b82f6"/>
    <text x="160" y="78" class="label">Web App</text>
    <text x="160" y="93" class="sublabel">React / Vue</text>
  </g>
  <g class="node">
    <rect x="280" y="55" width="120" height="50" fill="#3b82f6"/>
    <text x="340" y="78" class="label">Mobile App</text>
    <text x="340" y="93" class="sublabel">iOS / Android</text>
  </g>
  <g class="node">
    <rect x="460" y="55" width="120" height="50" fill="#3b82f6"/>
    <text x="520" y="78" class="label">API Client</text>
    <text x="520" y="93" class="sublabel">Third Party</text>
  </g>
  
  <!-- Arrows to API Gateway -->
  <line x1="160" y1="105" x2="250" y2="165" class="arrow"/>
  <line x1="340" y1="105" x2="340" y2="165" class="arrow"/>
  <line x1="520" y1="105" x2="430" y2="165" class="arrow"/>
  
  <!-- API Gateway -->
  <g class="node">
    <rect x="200" y="165" width="280" height="50" fill="#8b5cf6"/>
    <text x="340" y="188" class="label">API Gateway</text>
    <text x="340" y="203" class="sublabel">认证 / 限流 / 路由</text>
  </g>
  
  <!-- Arrows to services -->
  <line x1="260" y1="215" x2="160" y2="275" class="arrow"/>
  <line x1="340" y1="215" x2="340" y2="275" class="arrow"/>
  <line x1="420" y1="215" x2="520" y2="275" class="arrow"/>
  
  <!-- Service Layer -->
  <g class="node">
    <rect x="80" y="275" width="120" height="50" fill="#10b981"/>
    <text x="140" y="298" class="label">用户服务</text>
    <text x="140" y="313" class="sublabel">User Service</text>
  </g>
  <g class="node">
    <rect x="280" y="275" width="120" height="50" fill="#10b981"/>
    <text x="340" y="298" class="label">业务服务</text>
    <text x="340" y="313" class="sublabel">Business Service</text>
  </g>
  <g class="node">
    <rect x="480" y="275" width="120" height="50" fill="#10b981"/>
    <text x="540" y="298" class="label">通知服务</text>
    <text x="540" y="313" class="sublabel">Notification</text>
  </g>
  
  <!-- Arrows to DB -->
  <line x1="140" y1="325" x2="200" y2="365" class="arrow"/>
  <line x1="340" y1="325" x2="340" y2="365" class="arrow"/>
  <line x1="540" y1="325" x2="480" y2="365" class="arrow"/>
  
  <!-- Data Layer -->
  <g class="node">
    <rect x="160" y="365" width="120" height="25" fill="#f59e0b"/>
    <text x="220" y="380" class="label" style="font-size:11px">MySQL</text>
  </g>
  <g class="node">
    <rect x="300" y="365" width="80" height="25" fill="#ef4444"/>
    <text x="340" y="380" class="label" style="font-size:11px">Redis</text>
  </g>
  <g class="node">
    <rect x="400" y="365" width="120" height="25" fill="#f59e0b"/>
    <text x="460" y="380" class="label" style="font-size:11px">MongoDB</text>
  </g>
</svg>
</body>
</html>
```

---

## API Flow Diagram (API 流程图)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  svg { width: 100%; max-width: 600px; display: block; margin: 0 auto; }
  .box { rx: 8; ry: 8; }
  .label { font-size: 13px; font-weight: 600; fill: white; text-anchor: middle; dominant-baseline: middle; }
  .step-label { font-size: 12px; fill: #64748b; text-anchor: middle; }
  .arrow { stroke: #3b82f6; stroke-width: 2; fill: none; marker-end: url(#blue-arrow); stroke-dasharray: 5,3; }
  .solid-arrow { stroke: #10b981; stroke-width: 2; fill: none; marker-end: url(#green-arrow); }
</style>
</head>
<body>
<svg viewBox="0 0 600 500" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="blue-arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#3b82f6"/>
    </marker>
    <marker id="green-arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#10b981"/>
    </marker>
  </defs>
  
  <!-- Step 1: Client -->
  <rect x="200" y="20" width="200" height="50" class="box" fill="#3b82f6"/>
  <text x="300" y="48" class="label">客户端请求</text>
  
  <line x1="300" y1="70" x2="300" y2="110" class="arrow"/>
  <text x="320" y="95" class="step-label">① HTTP Request</text>
  
  <!-- Step 2: Auth -->
  <rect x="200" y="110" width="200" height="50" class="box" fill="#8b5cf6"/>
  <text x="300" y="138" class="label">身份验证</text>
  
  <line x1="300" y1="160" x2="300" y2="200" class="arrow"/>
  <text x="320" y="185" class="step-label">② JWT Verify</text>
  
  <!-- Step 3: Business Logic -->
  <rect x="200" y="200" width="200" height="50" class="box" fill="#10b981"/>
  <text x="300" y="228" class="label">业务逻辑处理</text>
  
  <line x1="300" y1="250" x2="300" y2="290" class="arrow"/>
  <text x="320" y="275" class="step-label">③ Query DB</text>
  
  <!-- Step 4: Database -->
  <rect x="200" y="290" width="200" height="50" class="box" fill="#f59e0b"/>
  <text x="300" y="318" class="label">数据库操作</text>
  
  <line x1="300" y1="340" x2="300" y2="380" class="solid-arrow"/>
  <text x="320" y="365" class="step-label">④ Return Data</text>
  
  <!-- Step 5: Response -->
  <rect x="200" y="380" width="200" height="50" class="box" fill="#3b82f6"/>
  <text x="300" y="408" class="label">返回响应</text>
  
  <!-- Side annotations -->
  <rect x="20" y="110" width="140" height="30" rx="6" fill="#fef3c7"/>
  <text x="90" y="129" class="step-label" style="fill:#92400e">Token 过期 → 401</text>
  <line x1="200" y1="125" x2="160" y2="125" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="3,2"/>
  
  <rect x="440" y="200" width="140" height="30" rx="6" fill="#dcfce7"/>
  <text x="510" y="219" class="step-label" style="fill:#166534">缓存命中 → 跳过</text>
  <line x1="400" y1="215" x2="440" y2="215" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3,2"/>
</svg>
</body>
</html>
```

---

## Tips

- Use consistent color coding: blue=client, purple=gateway/auth, green=service, yellow=data
- Add hover effects for interactive exploration
- Keep labels short (≤10 characters)
- Use dashed lines for optional/conditional flows
- Add side annotations for error cases and edge conditions
