# Flowcharts Reference

Templates for process flowcharts using Mermaid.js or custom SVG.

## CDN

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
```

---

## Mermaid Flowchart (业务流程图)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  .mermaid { display: flex; justify-content: center; }
</style>
</head>
<body>
<div class="mermaid">
flowchart TD
    A[用户下单] --> B{库存检查}
    B -->|库存充足| C[扣减库存]
    B -->|库存不足| D[提示缺货]
    C --> E[生成订单]
    E --> F[支付]
    F -->|支付成功| G[发货]
    F -->|支付失败| H[取消订单]
    G --> I[完成]
    H --> J[恢复库存]
    J --> K[订单关闭]
    D --> L[结束]
    I --> L
    K --> L
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({ startOnLoad: true, theme: 'default' });</script>
</body>
</html>
```

---

## Decision Tree (决策树)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  svg { width: 100%; max-width: 700px; display: block; margin: 0 auto; }
  .node rect, .node circle { rx: 6; ry: 6; }
  .node text { font-size: 12px; text-anchor: middle; dominant-baseline: middle; }
  .decision { fill: #fef3c7; stroke: #f59e0b; stroke-width: 2; }
  .action { fill: #dbeafe; stroke: #3b82f6; stroke-width: 2; }
  .result { fill: #dcfce7; stroke: #10b981; stroke-width: 2; }
  .edge { stroke: #94a3b8; stroke-width: 1.5; fill: none; marker-end: url(#arrow); }
  .edge-label { font-size: 11px; fill: #64748b; text-anchor: middle; }
</style>
</head>
<body>
<svg viewBox="0 0 700 400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#94a3b8"/>
    </marker>
  </defs>
  
  <!-- Decision 1 -->
  <g class="node">
    <polygon points="350,30 400,60 350,90 300,60" class="decision"/>
    <text x="350" y="63" style="font-size:11px">预算充足?</text>
  </g>
  
  <!-- Yes branch -->
  <line x1="400" y1="60" x2="480" y2="60" class="edge"/>
  <text x="440" y="55" class="edge-label">是</text>
  
  <g class="node">
    <rect x="480" y="35" width="100" height="50" class="action"/>
    <text x="530" y="60" style="font-size:11px">考虑高端产品</text>
  </g>
  
  <line x1="530" y1="85" x2="530" y2="130" class="edge"/>
  
  <g class="node">
    <polygon points="530,130 580,160 530,190 480,160" class="decision"/>
    <text x="530" y="163" style="font-size:11px">性能需求高?</text>
  </g>
  
  <line x1="580" y1="160" x2="620" y2="160" class="edge"/>
  <text x="600" y="155" class="edge-label">是</text>
  
  <g class="node">
    <rect x="620" y="135" width="70" height="50" class="result"/>
    <text x="655" y="160" style="font-size:11px">旗舰版</text>
  </g>
  
  <line x1="480" y1="160" x2="400" y2="160" class="edge"/>
  <text x="440" y="155" class="edge-label">否</text>
  
  <g class="node">
    <rect x="330" y="135" width="70" height="50" class="result"/>
    <text x="365" y="160" style="font-size:11px">标准版</text>
  </g>
  
  <!-- No branch -->
  <line x1="300" y1="60" x2="220" y2="60" class="edge"/>
  <text x="260" y="55" class="edge-label">否</text>
  
  <g class="node">
    <rect x="120" y="35" width="100" height="50" class="action"/>
    <text x="170" y="60" style="font-size:11px">考虑性价比</text>
  </g>
  
  <line x1="170" y1="85" x2="170" y2="130" class="edge"/>
  
  <g class="node">
    <polygon points="170,130 220,160 170,190 120,160" class="decision"/>
    <text x="170" y="163" style="font-size:11px">有促销?</text>
  </g>
  
  <line x1="220" y1="160" x2="260" y2="160" class="edge"/>
  <text x="240" y="155" class="edge-label">是</text>
  
  <g class="node">
    <rect x="260" y="135" width="70" height="50" class="result"/>
    <text x="295" y="160" style="font-size:11px">促销款</text>
  </g>
  
  <line x1="120" y1="160" x2="80" y2="160" class="edge"/>
  <text x="100" y="155" class="edge-label">否</text>
  
  <g class="node">
    <rect x="10" y="135" width="70" height="50" class="result"/>
    <text x="45" y="160" style="font-size:11px">基础版</text>
  </g>
</svg>
</body>
</html>
```

---

## Sequence Diagram (时序图)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  svg { width: 100%; max-width: 600px; display: block; margin: 0 auto; }
  .actor { font-size: 13px; font-weight: 600; text-anchor: middle; }
  .lifeline { stroke: #cbd5e1; stroke-width: 1; stroke-dasharray: 4,2; }
  .message { stroke: #3b82f6; stroke-width: 1.5; marker-end: url(#arrow); }
  .message-label { font-size: 11px; fill: #475569; }
  .activation { fill: #e0e7ff; stroke: #6366f1; stroke-width: 1; }
</style>
</head>
<body>
<svg viewBox="0 0 600 350" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#3b82f6"/>
    </marker>
  </defs>
  
  <!-- Actors -->
  <rect x="50" y="20" width="80" height="30" rx="6" fill="#3b82f6"/>
  <text x="90" y="40" class="actor" fill="white">用户</text>
  
  <rect x="250" y="20" width="80" height="30" rx="6" fill="#10b981"/>
  <text x="290" y="40" class="actor" fill="white">前端</text>
  
  <rect x="450" y="20" width="80" height="30" rx="6" fill="#f59e0b"/>
  <text x="490" y="40" class="actor" fill="white">后端</text>
  
  <!-- Lifelines -->
  <line x1="90" y1="50" x2="90" y2="320" class="lifeline"/>
  <line x1="290" y1="50" x2="290" y2="320" class="lifeline"/>
  <line x1="490" y1="50" x2="490" y2="320" class="lifeline"/>
  
  <!-- Messages -->
  <line x1="90" y1="80" x2="290" y2="80" class="message"/>
  <text x="190" y="75" class="message-label">点击登录</text>
  
  <line x1="290" y1="110" x2="490" y2="110" class="message"/>
  <text x="390" y="105" class="message-label">POST /login</text>
  
  <rect x="470" y="110" width="40" height="40" class="activation"/>
  
  <line x1="490" y1="150" x2="290" y2="150" class="message"/>
  <text x="390" y="145" class="message-label">返回 Token</text>
  
  <rect x="270" y="150" width="40" height="30" class="activation"/>
  
  <line x1="290" y1="180" x2="90" y2="180" class="message"/>
  <text x="190" y="175" class="message-label">登录成功</text>
  
  <line x1="90" y1="210" x2="290" y2="210" class="message"/>
  <text x="190" y="205" class="message-label">请求数据</text>
  
  <line x1="290" y1="240" x2="490" y2="240" class="message"/>
  <text x="390" y="235" class="message-label">GET /data</text>
  
  <line x1="490" y1="270" x2="290" y2="270" class="message"/>
  <text x="390" y="265" class="message-label">返回数据</text>
  
  <line x1="290" y1="300" x2="90" y2="300" class="message"/>
  <text x="190" y="295" class="message-label">展示数据</text>
</svg>
</body>
</html>
```

---

## Tips

- Use Mermaid for complex flows (it auto-layouts)
- Use custom SVG for precise control over styling
- Keep flowcharts under 10 nodes for readability
- Use consistent shapes: diamond=decision, rectangle=action, circle=start/end
- Add color coding for different types of steps
