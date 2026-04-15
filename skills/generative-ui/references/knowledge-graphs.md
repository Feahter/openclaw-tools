# Knowledge Graphs Reference

Templates for concept relationships and mind maps.

## CDN

```html
<script src="https://d3js.org/d3.v7.min.js"></script>
```

---

## Force-Directed Knowledge Graph (力导向知识图谱)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  svg { width: 100%; max-width: 700px; height: 400px; display: block; margin: 0 auto; }
  .node circle { stroke: #fff; stroke-width: 2px; cursor: pointer; transition: all 0.2s; }
  .node circle:hover { stroke-width: 4px; }
  .node text { font-size: 12px; text-anchor: middle; dominant-baseline: middle; pointer-events: none; fill: white; font-weight: 500; }
  .link { stroke: #cbd5e1; stroke-width: 1.5; }
  .tooltip { position: absolute; background: #1e293b; color: white; padding: 8px 12px; border-radius: 6px; font-size: 12px; pointer-events: none; opacity: 0; transition: opacity 0.2s; }
</style>
</head>
<body>
<div id="tooltip" class="tooltip"></div>
<svg id="graph"></svg>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const nodes = [
  { id: "AI", group: 1, size: 30, desc: "人工智能总览" },
  { id: "ML", group: 2, size: 20, desc: "机器学习" },
  { id: "DL", group: 2, size: 20, desc: "深度学习" },
  { id: "NLP", group: 3, size: 18, desc: "自然语言处理" },
  { id: "CV", group: 3, size: 18, desc: "计算机视觉" },
  { id: "RL", group: 2, size: 18, desc: "强化学习" },
  { id: "GPT", group: 4, size: 15, desc: "生成式预训练模型" },
  { id: "BERT", group: 4, size: 15, desc: "双向编码器" },
  { id: "CNN", group: 5, size: 15, desc: "卷积神经网络" },
  { id: "Transformer", group: 4, size: 18, desc: "Transformer架构" }
];

const links = [
  { source: "AI", target: "ML" },
  { source: "AI", target: "DL" },
  { source: "AI", target: "RL" },
  { source: "ML", target: "NLP" },
  { source: "ML", target: "CV" },
  { source: "DL", target: "NLP" },
  { source: "DL", target: "CV" },
  { source: "NLP", target: "GPT" },
  { source: "NLP", target: "BERT" },
  { source: "CV", target: "CNN" },
  { source: "NLP", target: "Transformer" },
  { source: "GPT", target: "Transformer" },
  { source: "BERT", target: "Transformer" }
];

const colors = { 1: '#3b82f6', 2: '#10b981', 3: '#f59e0b', 4: '#8b5cf6', 5: '#ef4444' };

const svg = d3.select('#graph');
const width = 700, height = 400;
svg.attr('viewBox', `0 0 ${width} ${height}`);

const simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id).distance(80))
  .force('charge', d3.forceManyBody().strength(-300))
  .force('center', d3.forceCenter(width / 2, height / 2));

const link = svg.append('g').selectAll('line').data(links)
  .enter().append('line').attr('class', 'link');

const node = svg.append('g').selectAll('.node').data(nodes)
  .enter().append('g').attr('class', 'node')
  .call(d3.drag().on('start', dragstarted).on('drag', dragged).on('end', dragended));

node.append('circle')
  .attr('r', d => d.size)
  .attr('fill', d => colors[d.group]);

node.append('text')
  .text(d => d.id)
  .attr('dy', d => d.size > 20 ? 0 : 0);

const tooltip = d3.select('#tooltip');

node.on('mouseover', (e, d) => {
  tooltip.style('opacity', 1).style('left', e.pageX + 10 + 'px').style('top', e.pageY - 10 + 'px')
    .html(`<strong>${d.id}</strong><br/>${d.desc}`);
}).on('mouseout', () => tooltip.style('opacity', 0));

simulation.on('tick', () => {
  link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
  node.attr('transform', d => `translate(${d.x},${d.y})`);
});

function dragstarted(e, d) { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }
function dragged(e, d) { d.fx = e.x; d.fy = e.y; }
function dragended(e, d) { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }
</script>
</body>
</html>
```

---

## Mind Map (思维导图)

```html
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: var(--color-background, #fff); color: var(--color-text, #1f2937); }
  svg { width: 100%; max-width: 700px; height: 450px; display: block; margin: 0 auto; }
  .branch { fill: none; stroke-width: 2; }
  .node rect { rx: 6; ry: 6; }
  .node text { font-size: 12px; text-anchor: middle; dominant-baseline: middle; font-weight: 500; }
  .level-0 { fill: #3b82f6; }
  .level-1 { fill: #10b981; }
  .level-2 { fill: #f59e0b; }
  .level-3 { fill: #8b5cf6; }
</style>
</head>
<body>
<svg viewBox="0 0 700 450" xmlns="http://www.w3.org/2000/svg">
  <!-- Root -->
  <g class="node">
    <rect x="300" y="200" width="100" height="40" class="level-0"/>
    <text x="350" y="220" fill="white">前端开发</text>
  </g>
  
  <!-- Level 1 branches -->
  <path d="M 400 220 Q 450 220 480 120" class="branch" stroke="#10b981"/>
  <path d="M 400 220 Q 480 220 520 180" class="branch" stroke="#10b981"/>
  <path d="M 400 220 Q 480 220 520 260" class="branch" stroke="#10b981"/>
  <path d="M 400 220 Q 450 220 480 320" class="branch" stroke="#10b981"/>
  
  <g class="node">
    <rect x="480" y="100" width="80" height="36" class="level-1"/>
    <text x="520" y="118" fill="white">基础</text>
  </g>
  <g class="node">
    <rect x="520" y="160" width="80" height="36" class="level-1"/>
    <text x="560" y="178" fill="white">框架</text>
  </g>
  <g class="node">
    <rect x="520" y="240" width="80" height="36" class="level-1"/>
    <text x="560" y="258" fill="white">工具</text>
  </g>
  <g class="node">
    <rect x="480" y="300" width="80" height="36" class="level-1"/>
    <text x="520" y="318" fill="white">进阶</text>
  </g>
  
  <!-- Level 2 branches -->
  <path d="M 560 118 Q 600 118 620 70" class="branch" stroke="#f59e0b"/>
  <path d="M 560 118 Q 600 118 620 110" class="branch" stroke="#f59e0b"/>
  <path d="M 560 118 Q 600 118 620 150" class="branch" stroke="#f59e0b"/>
  
  <g class="node">
    <rect x="620" y="55" width="60" height="28" class="level-2"/>
    <text x="650" y="69" fill="white" style="font-size:11px">HTML</text>
  </g>
  <g class="node">
    <rect x="620" y="95" width="60" height="28" class="level-2"/>
    <text x="650" y="109" fill="white" style="font-size:11px">CSS</text>
  </g>
  <g class="node">
    <rect x="620" y="135" width="60" height="28" class="level-2"/>
    <text x="650" y="149" fill="white" style="font-size:11px">JS</text>
  </g>
  
  <path d="M 600 178 Q 630 178 650 160" class="branch" stroke="#f59e0b"/>
  <path d="M 600 178 Q 630 178 650 196" class="branch" stroke="#f59e0b"/>
  
  <g class="node">
    <rect x="650" y="145" width="60" height="28" class="level-2"/>
    <text x="680" y="159" fill="white" style="font-size:11px">React</text>
  </g>
  <g class="node">
    <rect x="650" y="181" width="60" height="28" class="level-2"/>
    <text x="680" y="195" fill="white" style="font-size:11px">Vue</text>
  </g>
  
  <path d="M 600 258 Q 630 258 650 240" class="branch" stroke="#f59e0b"/>
  <path d="M 600 258 Q 630 258 650 276" class="branch" stroke="#f59e0b"/>
  
  <g class="node">
    <rect x="650" y="225" width="60" height="28" class="level-2"/>
    <text x="680" y="239" fill="white" style="font-size:11px">Git</text>
  </g>
  <g class="node">
    <rect x="650" y="261" width="60" height="28" class="level-2"/>
    <text x="680" y="275" fill="white" style="font-size:11px">Webpack</text>
  </g>
  
  <path d="M 560 318 Q 600 318 620 300" class="branch" stroke="#f59e0b"/>
  <path d="M 560 318 Q 600 318 620 336" class="branch" stroke="#f59e0b"/>
  <path d="M 560 318 Q 600 318 620 372" class="branch" stroke="#f59e0b"/>
  
  <g class="node">
    <rect x="620" y="285" width="70" height="28" class="level-2"/>
    <text x="655" y="299" fill="white" style="font-size:11px">性能优化</text>
  </g>
  <g class="node">
    <rect x="620" y="321" width="70" height="28" class="level-2"/>
    <text x="655" y="335" fill="white" style="font-size:11px">工程化</text>
  </g>
  <g class="node">
    <rect x="620" y="357" width="70" height="28" class="level-2"/>
    <text x="655" y="371" fill="white" style="font-size:11px">TypeScript</text>
  </g>
</svg>
</body>
</html>
```

---

## Tips

- Use D3.js for dynamic, interactive graphs
- Use static SVG for simple, fixed-layout mind maps
- Limit nodes to 15-20 for readability
- Use color coding for different categories
- Add tooltips for additional context on hover
- Allow drag interaction for exploration
