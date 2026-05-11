# SVG Generation — 策略与方法

> 优先使用 `generate-from-template.py` 脚本，复杂图用 Python list 方法

---

## 方式A：模板脚本（推荐）

```bash
python3 scripts/generate-from-template.py <type> <output.svg> '<json>'
```

**优点**：自动处理：
- 节点对齐和边界
- 正交箭头路由（orthogonal routing）
- 箭头跳过交叉（jump-over arcs）
- 箭头标签 badge
- Legend 自动布局

**JSON 关键字段**：
```json
{
  "style": 6,
  "title": "标题",
  "subtitle": "副标题",
  "nodes": [
    {
      "id": "unique-id",
      "kind": "rect|cylinder|user_avatar|hexagon|...",
      "x": 100,
      "y": 100,
      "width": 160,
      "height": 70,
      "label": "主标签",
      "sublabel": "副标签",
      "type_label": "顶层分类"
    }
  ],
  "arrows": [
    {
      "source": "node-id-1",
      "target": "node-id-2",
      "label": "箭头标签",
      "flow": "control|read|write|async|feedback|data"
    }
  ],
  "legend": [
    {"flow": "control", "label": "控制流"}
  ]
}
```

**支持模板类型**：
`architecture` · `data-flow` · `flowchart` · `sequence` · `comparison`
`timeline` · `mind-map` · `agent` · `memory` · `use-case`
`class` · `state-machine` · `er-diagram` · `network-topology`

---

## 方式B：Python List 方法（手动 SVG）

用于：模板不支持的布局、完全自定义形状

```python
python3 << 'EOF'
from xml.sax.saxutils import escape

lines = []
SVG_W = 960
SVG_H = 600

lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}">')

# DEFS: markers, filters, styles
lines.append('  <defs>')
lines.append('    <marker id="arrowA" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
lines.append('      <polygon points="0 0, 10 3.5, 0 7" fill="#5a5a5a"/>')
lines.append('    </marker>')
lines.append('    <style>')
lines.append('      text { font-family: -apple-system, BlinkMacSystemFont, sans-serif; }')
lines.append('    </style>')
lines.append('  </defs>')

# Background
lines.append(f'  <rect width="{SVG_W}" height="{SVG_H}" fill="#f8f6f3"/>')

# Title
lines.append(f'  <text x="48" y="48" font-size="24" font-weight="700" fill="#141413">Agent Architecture</text>')
lines.append(f'  <line x1="48" y1="62" x2="912" y2="62" stroke="#ded8cf" stroke-width="1"/>')

# Node helper
def node(x, y, w, h, label, fill="#fffcf7", stroke="#ded0c3"):
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    cx = x + w//2
    lines.append(f'  <text x="{cx}" y="{y+h//2-4}" text-anchor="middle" font-size="16" font-weight="700" fill="#141413">{escape(label)}</text>')

# Arrow helper
def arrow(x1, y1, x2, y2, label="", color="#5a5a5a"):
    lines.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" marker-end="url(#arrowA)"/>')
    if label:
        mx = (x1+x2)//2
        my = (y1+y2)//2 - 8
        lines.append(f'  <rect x="{mx-30}" y="{my-8}" width="60" height="18" rx="4" fill="#f8f6f3" opacity="0.96"/>')
        lines.append(f'  <text x="{mx}" y="{my+4}" text-anchor="middle" font-size="11" fill="#6b6257">{escape(label)}</text>')

# Nodes
node(60, 180, 160, 80, "User", "#fce7d6", "#d97757")    # Input
node(280, 180, 180, 80, "LLM Core", "#e8f5e3", "#7b8b5c")  # Agent
node(540, 160, 160, 120, "Memory", "#f4e4c1", "#d97757")   # Storage
node(540, 340, 160, 70, "Tools", "#fffcf7", "#ded0c3")    # Tool
node(760, 180, 160, 80, "Output", "#fffcf7", "#ded0c3")   # Output

# Arrows
arrow(220, 220, 280, 220, "Query", "#d97757")
arrow(460, 220, 540, 220, "Read", "#8c6f5a")
arrow(460, 260, 560, 340, "Invoke", "#d97757")
arrow(700, 220, 760, 220, "Response", "#5a5a5a")

lines.append('</svg>')

with open('/tmp/diagrams/agent-arch.svg', 'w') as f:
    f.write('\n'.join(lines))
print("✓ SVG generated")
EOF
```

---

## SVG 技术规范

| 项目 | 规范 |
|------|------|
| ViewBox | `0 0 960 600`（标准）/ `0 0 960 800`（高）/ `0 0 1200 600`（宽） |
| 字体 | 内联 `<style>`，禁止 `@import`（rsvg 不支持） |
| 文字 min | 12px，标签 13-14px，子标签 11px，标题 24-30px |
| 箭头 marker | `markerWidth="10" markerHeight="7"`，`markerEnd` |
| 阴影 | `<feDropShadow>` 慎用，只用在关键节点 |
| 曲线 | 三次贝塞尔 `M x1,y1 C cx1,cy1 cx2,cy2 x2,y2` |
| 文本溢出 | 用 `<clipPath>` 或限制 `text.length × 7px ≤ width - 16px` |

---

## ViewBox 速查

| 用途 | ViewBox |
|------|---------|
| 标准架构图 | `0 0 960 600` |
| 多层架构 | `0 0 960 800` |
| 宽架构图 | `0 0 1200 600` |
| 序列图 | `0 0 960 700`（+ 80×消息数） |
| Memory 图 | `0 0 960 720` |
| Timeline | `0 0 960 400` / `0 0 1200 400` |
| 复杂 ER | `0 0 1200 600` |
