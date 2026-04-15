---
name: generative-ui
description: "Generate interactive HTML widgets and data visualizations embedded directly in AI conversations. Use when the user wants to see, explore, or interact with information visually — not just read it. Triggers on: 画个图 / 可视化 / 对比一下 / 画架构图 / 做个计算器 / 展示数据 / 流程图 / 思维导图 / 交互图表 / 时间线 / 仪表盘 / dashboard / chart / diagram / visualize / plot / graph / compare / timeline / calculator / simulator. Also triggers when the user shares data (numbers, tables, lists) and asks to analyze, show, or summarize it visually."
---

# Generative UI Skill

Produce self-contained HTML widgets that render inside a sandboxed iframe in the conversation.

## Output Format

Wrap every widget in this exact fence:

````
```show-widget
{"title":"snake_case_name","widget_code":"<FULL HTML>"}
```
````

`widget_code` must be a **complete, standalone HTML document** — all CSS in `<style>`, all JS in `<script>`, no external files except approved CDNs.

Always follow the widget with 2–4 sentences of text insight. Never output a widget without explanation.

## Widget Type Selection

| User intent | Widget type | Reference |
|-------------|-------------|-----------|
| Trends, time series | Line / area chart | [charts.md](references/charts.md) |
| Comparisons, rankings | Bar chart | [charts.md](references/charts.md) |
| Proportions, shares | Pie / donut chart | [charts.md](references/charts.md) |
| Multi-metric overview | Radar / dashboard | [charts.md](references/charts.md) |
| System / API design | Architecture SVG | [architecture.md](references/architecture.md) |
| Process, decision | Flowchart / sequence | [flowcharts.md](references/flowcharts.md) |
| Concept relationships | Knowledge graph | [knowledge-graphs.md](references/knowledge-graphs.md) |
| Adjustable parameters | Interactive tool | [tools.md](references/tools.md) |
| Feature / plan matrix | Comparison table | [comparisons.md](references/comparisons.md) |
| Project schedule | Timeline / Gantt | [timeline.md](references/timeline.md) |
| KPI overview | Dashboard | [dashboard.md](references/dashboard.md) |

**Decision rule:** If the user's data has ≥3 numeric values → chart. If it describes a process → flowchart. If it describes relationships → knowledge graph. If it needs user input → interactive tool.

## Design Standards

**Colors (use consistently):**
- Primary `#3b82f6` · Success `#10b981` · Warning `#f59e0b` · Danger `#ef4444` · Purple `#8b5cf6`
- Background: `var(--color-background, #ffffff)` · Text: `var(--color-text, #1f2937)`

**Layout:**
- `width: 100%`, `max-width: 700px`, `margin: 0 auto`
- `padding: 16px–20px`, `border-radius: 8px–12px`
- Font: `system-ui, -apple-system, sans-serif`

**Interactivity patterns:**
- Sliders for parameter exploration (`oninput="update()"`)
- Tabs for multi-view data
- Hover tooltips for detail
- "Ask AI" buttons: `<button onclick="window.parent.postMessage({type:'widget:sendMessage',text:'解释这部分'}, '*')">详细解释</button>`

## Approved CDNs

```
https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js
https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js
https://d3js.org/d3.v7.min.js
https://cdnjs.cloudflare.com/ajax/libs/echarts/5.4.3/echarts.min.js
```

## Security Rules

- No `eval()`, `new Function()`, `document.write()`
- No `fetch()` or `XMLHttpRequest` to external domains
- No `<script src>` outside the approved CDN list
- Sanitize any user-provided strings before inserting into DOM

## Quality Checklist

Before outputting a widget, verify:
- [ ] Renders at 100% width without horizontal scroll
- [ ] Has meaningful title and axis/legend labels
- [ ] Handles empty or edge-case data gracefully
- [ ] Color contrast passes WCAG AA
- [ ] `<script>` tags are at the bottom of `<body>`

## When NOT to Generate a Widget

- Simple yes/no or single-value answers
- When a plain markdown table is clearer
- When the user explicitly asks for text only
- When data is insufficient to visualize meaningfully

## Conversation Integration

```
我为你生成了一个[图表类型]：

```show-widget
{"title":"...","widget_code":"..."}
```

[2–4句关键洞察，指出最重要的模式或数字]

你可以[交互提示，如"拖动滑块调整参数"或"点击图例筛选数据"]。
```
