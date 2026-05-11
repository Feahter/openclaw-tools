# Excalidraw Recipes — Kroki 引擎用

> 用于 Kroki 引擎（手绘/草图风格，SVG 输出）。

---

## Excalidraw JSON 结构骨架

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude-code",
  "elements": [],
  "appState": { "viewBackgroundColor": "#ffffff" }
}
```

---

## 节点类型映射

| 用途 | type | 关键属性 |
|------|------|---------|
| 组件/模块 | `rectangle` | `backgroundColor`, `strokeColor` |
| 开始/结束 | `ellipse` | `backgroundColor: #dcfce7` |
| 决策点 | `diamond` | `backgroundColor: #fef9c3` |
| 文本标签 | `text` | `fontSize`, `fontFamily` |
| 有向连接 | `arrow` | `points`, `startBinding`, `endBinding` |
| 无向连接 | `line` | `points` |

---

## 基础节点模板

```json
{
  "id": "service_node",
  "type": "rectangle",
  "x": 100, "y": 100,
  "width": 160, "height": 60,
  "angle": 0,
  "strokeColor": "#1e40af",
  "backgroundColor": "#dbeafe",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 0,
  "opacity": 100,
  "seed": 100001,
  "groupIds": [],
  "boundElements": [{ "id": "label_1", "type": "text" }]
}
```

```json
{
  "id": "label_1",
  "type": "text",
  "text": "Auth Service",
  "fontSize": 20,
  "fontFamily": 2,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#1e293b",
  "containerId": "service_node",
  "boundElements": null,
  "seed": 100002
}
```

---

## 箭头模板

```json
{
  "id": "arrow_gw_to_auth",
  "type": "arrow",
  "points": [[0, 0], [200, 0]],
  "startBinding": { "elementId": "api_gateway", "gap": 5, "focus": 0 },
  "endBinding": { "elementId": "auth_service", "gap": 5, "focus": 0 },
  "strokeColor": "#1e40af",
  "backgroundColor": "transparent",
  "strokeWidth": 2,
  "roughness": 0,
  "seed": 200001
}
```

**箭头类型：**
- Solid（主路径）：`strokeStyle: null`
- Dashed（响应/异步）：`"strokeStyle": "dashed"`
- Dotted（可选/弱依赖）：`"strokeStyle": "dotted"`

---

## 字号层级

| 级别 | fontSize | 用途 |
|------|---------|------|
| Title | 28px | 图标题 |
| Header | 24px | 分组标题 |
| Label | 20px | 节点主标签 |
| Description | 16px | 次要文字 |
| Note | 14px | 标注 |

---

## 颜色语义（60-30-10 规则）

| 用途 | fill | stroke | 说明 |
|------|------|--------|------|
| Primary / Input | `#dbeafe` | `#1e40af` | 入口点，API |
| Success / Data | `#dcfce7` | `#166534` | 数据存储 |
| Warning / Decision | `#fef9c3` | `#854d0e` | 决策点 |
| Error / Critical | `#fee2e2` | `#991b1b` | 错误/告警 |
| External / Storage | `#f3e8ff` | `#6b21a8` | 外部服务/数据库 |
| Process | `#e0f2fe` | `#0369a1` | 标准处理步骤 |
| Trigger / Start | `#fed7aa` | `#c2410c` | 起始节点/触发器 |
| Container | `#f1f5f9` | `#475569` | 分组容器（opacity: 25-40）|

---

## 流程图模板（LR 布局）

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude-code",
  "elements": [
    { "id": "start", "type": "ellipse", "x": 40, "y": 200, "width": 100, "height": 50,
      "strokeColor": "#166534", "backgroundColor": "#dcfce7", "strokeWidth": 2, "roughness": 0, "seed": 1,
      "boundElements": [{ "id": "t_start", "type": "text" }] },
    { "id": "t_start", "type": "text", "text": "Start", "fontSize": 16, "fontFamily": 2,
      "textAlign": "center", "verticalAlign": "middle", "strokeColor": "#166534", "containerId": "start", "seed": 2 },
    { "id": "proc1", "type": "rectangle", "x": 200, "y": 195, "width": 140, "height": 60,
      "strokeColor": "#1e40af", "backgroundColor": "#dbeafe", "strokeWidth": 2, "roughness": 0, "seed": 3,
      "boundElements": [{ "id": "t_proc1", "type": "text" }] },
    { "id": "t_proc1", "type": "text", "text": "Process", "fontSize": 16, "fontFamily": 2,
      "textAlign": "center", "verticalAlign": "middle", "strokeColor": "#1e293b", "containerId": "proc1", "seed": 4 },
    { "id": "decision", "type": "diamond", "x": 400, "y": 180, "width": 140, "height": 90,
      "strokeColor": "#854d0e", "backgroundColor": "#fef9c3", "strokeWidth": 2, "roughness": 0, "seed": 5,
      "boundElements": [{ "id": "t_dec", "type": "text" }] },
    { "id": "t_dec", "type": "text", "text": "Valid?", "fontSize": 14, "fontFamily": 2,
      "textAlign": "center", "verticalAlign": "middle", "strokeColor": "#854d0e", "containerId": "decision", "seed": 6 },
    { "id": "arrow1", "type": "arrow", "points": [[0, 0], [160, 0]],
      "startBinding": { "elementId": "start", "gap": 5 }, "endBinding": { "elementId": "proc1", "gap": 5 },
      "strokeColor": "#1e40af", "strokeWidth": 2, "roughness": 0, "seed": 7 },
    { "id": "arrow2", "type": "arrow", "points": [[0, 0], [140, 0]],
      "startBinding": { "elementId": "proc1", "gap": 5 }, "endBinding": { "elementId": "decision", "gap": 5 },
      "strokeColor": "#1e40af", "strokeWidth": 2, "roughness": 0, "seed": 8 }
  ],
  "appState": { "viewBackgroundColor": "#ffffff" }
}
```

---

## Kroki 导出命令

```bash
# Excalidraw → SVG via Kroki
curl -s -X POST https://kroki.io/excalidraw/svg \
  -H "Content-Type: application/json" \
  --data-binary "@diagram.excalidraw" \
  -o diagram.svg

# PNG 需要本地 CLI（不推荐，优先用 Native SVG 或 draw.io）
```
