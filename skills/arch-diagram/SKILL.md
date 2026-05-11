---
name: arch-diagram
description: >
  Generate architecture diagrams, flowcharts, UML, and technical visualizations from natural language.
  触发词：画图/架构图/流程图/UML/可视化/generate diagram/draw diagram/visualize/diagram/图表。
  支持三种引擎自动路由（原生SVG / draw.io / Kroki），根据图类型和复杂度自动选择最优输出路径。
  OpenClaw 专属：内置 feZ 本地架构模板，双 Gateway、Skills 系统、Memory 分层、Tool Call 流程的快速触发。
---

# Arch Diagram

自然语言 → 专业级图表（SVG + PNG）。三种引擎按需路由，质量闭环保证输出。

---

## 引擎选择决策树

**优先用 Native SVG（默认）** → 零依赖，最快，适合架构图、数据流、对比矩阵、时间线、思维导图、Mermaid 导出

**用 draw.io** → 当用户请求 ERD、UML类图、UML时序图、ML模型图，或要求"可编辑"、多格式输出（PNG+SVG+PDF），或需要迭代自检

**用 Kroki** → 当用户要求 Excalidraw 手绘风格，或只需要 SVG 且不想装 draw.io

```
用户描述 → 判断图类型
  ├─ ERD / UML类图 / UML时序图 / ML模型图 → draw.io
  ├─ "手绘风格" / "excalidraw" / "sketch" → Kroki
  ├─ OpenClaw专属描述（见"快速触发"节）→ Native SVG
  └─ 通用架构/流程/数据流/对比/时间/思维导图 → Native SVG（默认）
```

---

## 快速触发（Native SVG · OpenClaw 专属）

| 用户说 | 输出的图 |
|--------|---------|
| `OpenClaw 架构` | 双 Gateway + Agent Core + Skills + Memory + Tools（Style 6） |
| `OpenClaw 双 Gateway` | QClaw 28789 + npm 18789 双通道（Style 6） |
| `Skill 系统架构` | Orchestrator + Specialists 分层（Style 5） |
| `OpenClaw Memory` | Session/Daily/Long-term/Skill 四层（Style 3） |
| `OpenClaw Tool Call` | LLM → Tool Selector → MCP 循环（Style 2） |

快速触发时直接用 `scripts/generate-from-template.py`，抄 `references/openclaw-patterns.md` 模板。

---

## Native SVG 引擎（默认）

### 执行流程（4步）

1. **分类** → 判断图类型（architecture/dataflow/flowchart/sequence/comparison/timeline/mind-map 等）
2. **提取结构** → 识别节点、关系、层级、流向
3. **生成 SVG** → 抄 `references/recipes.md` 对应类型的最小可用 JSON，用 `generate-from-template.py` 渲染
4. **验证** → `rsvg-convert file.svg -o /dev/null`，导出 PNG

### 风格速查

| 场景 | 风格 | 图类型 |
|------|------|--------|
| OpenClaw 系统 / Agent | **Style 6** Claude Official（暖奶油色） | architecture/agent/memory |
| 暗黑极客风 | Style 2 Dark Terminal | tool-call/sequence |
| 微服务/架构文档 | Style 3 Blueprint | architecture |
| Multi-Agent 协作 | Style 5 Glass | agent |
| 对比矩阵 | Style 4 Notion Clean | comparison |
| 博客/轻量图 | Style 1 Flat Icon | flowchart/mind-map |
| 手绘风格 | Style 7 OpenAI | 通用 |

风格定义文件：`references/style-guides/index.md` + `references/style-N.md`

### 节点形状词汇

| 概念 | 形状 |
|------|------|
| User/Human | user_avatar |
| LLM/Model/Agent | rect（双边框）|
| Memory (long-term) | cylinder |
| Vector/Graph Store | cylinder / circle_cluster |
| Tool/Function | rect（gear）|
| Gateway/LB | hexagon |
| Decision | diamond |
| Queue/Stream | horizontal_tube |
| Database | cylinder3 |

### 箭头语义（必须指定）

`control` · `read` · `write` · `async` · `feedback` · `data`

### 生成命令

```bash
# 模板路径（最快）
python3 scripts/generate-from-template.py <type> <output.svg> '<JSON>'

# 示例：OpenClaw Agent 架构
python3 scripts/generate-from-template.py agent /tmp/diagram.svg '{
  "style": 6, "title": "OpenClaw Agent", "subtitle": "...",
  "nodes": [...], "arrows": [...]
}'

# 验证
rsvg-convert file.svg -o /dev/null 2>&1 && echo "✓ Valid"

# 导出 PNG（1920px = 2x retina）
rsvg-convert -w 1920 file.svg -o file.png
```

### 支持的图类型

`architecture` · `data-flow` · `flowchart` · `sequence` · `comparison` · `timeline` · `mind-map` · `agent` · `memory` · `class-diagram` · `use-case` · `state-machine` · `er-diagram` · `network-topology`

---

## draw.io 引擎（ERD / UML / ML / 专业图）

当图类型命中决策树时，使用完整 draw.io 工作流。

### 工作流（7步）

1. **检查依赖** → `draw.io --version`（Linux 用 `xvfb-run -a draw.io`）
2. **询问明确**（如需要）→ 图类型、输出格式（PNG/SVG/PDF）、路径、复杂度
3. **生成 .drawio XML** → 写 `references/drawio-recipes.md` 中对应类型的 XML 模板
4. **导出预览 PNG**（无 `-e`，用于自检）→ `draw.io -x -f png -s 2 -o preview.png input.drawio`
5. **自检**（Vision 模型可用时）→ 读 preview.png，检查重叠/截断/缺失连接/跨形状箭头
6. **用户 Review** → 展示图片 → 用户反馈 → 精准 XML 编辑 → 循环（最多5轮）
7. **最终导出** → `-e` 嵌入 XML → `.drawio.png` → 跑 IEND repair → 交付所有格式

### draw.io 导出命令

```bash
# 预览 PNG（无 -e，用于自检）
draw.io -x -f png -s 2 -o preview.png input.drawio

# 最终 PNG（-e 嵌入，IEND repair 后才能被 vision API 读取）
draw.io -x -f png -e -s 2 -o diagram.drawio.png input.drawio

# SVG / PDF
draw.io -x -f svg -e -o diagram.svg input.drawio
draw.io -x -f pdf -e -o diagram.pdf input.drawio

# Linux 无头模式
xvfb-run -a draw.io -x -f png -e -s 2 -o diagram.drawio.png input.drawio --disable-gpu
```

### 自检规则

| 检查项 | 发现问题 | 自动修复 |
|--------|---------|---------|
| 重叠形状 | 两个形状叠在一起 | 移开 ≥200px |
| 标签截断 | 文字被形状边界切割 | 增大形状宽高 |
| 缺失连接 | 箭头没有连上形状 | 验证 source/target id |
| 形状出画布 | 坐标为负或远离主体 | 移到主体附近 |
| 箭头穿过形状 | 箭头与无关形状交叉 | 加 waypoints 或增大间距 |
| 堆叠边 | 多条边重叠在同一路径 | 分散 entry/exit 点 |

**最多 2 轮自检**；仍有问题则直接展示给用户。

### 迭代编辑规则

| 用户反馈 | XML 操作 |
|---------|---------|
| 改颜色 | 改 `fillColor`/`strokeColor` in `style` |
| 加节点 | 追加新 `mxCell`，id 递增 |
| 删除节点 | 删除该 `mxCell` 及相关 edge |
| 移动形状 | 改 `x`/`y` in `mxGeometry` |
| 改变大小 | 改 `width`/`height` in `mxGeometry` |
| 加箭头 | 追加 `mxCell` edge with `source`/`target` |
| 改文字 | 改 `value` attribute |
| 改布局方向 | **全量重建** |

### Post-export PNG IEND Repair（draw.io 必做）

draw.io CLI 的 `-e` PNG 缺少 8 字节 IEND chunk，导致 vision API 报 400。导出后立即运行：

```bash
python3 - "${output_png}" <<'PY'
import sys
p = sys.argv[1]
data = open(p, 'rb').read()
IEND = b'\x00\x00\x00\x00IEND\xaeB`\x82'
if not data.endswith(IEND):
    if data.endswith(b'\x00\x00\x00\x00'):
        data = data[:-4]
    open(p, 'wb').write(data + IEND)
    print(f"repaired {p}")
PY
```

### draw.io 降级链

| 场景 | 方案 |
|------|------|
| draw.io CLI 缺失 + Python 有 | 生成 browser fallback URL（diagrams.net URL encode）|
| draw.io CLI 缺失 + Python 无 | 只生成 .drawio XML，让用户手动打开 |
| Vision 不可用 | 跳过自检，直接展示给用户 |
| Linux 导出失败 | 依次尝试：`xvfb-run -a` → `--no-sandbox` → `--disable-gpu` → `HOME=/tmp` |

### Browser Fallback URL（零安装）

draw.io CLI 不可用时，用 Python 生成 client-side 编辑 URL：

```bash
python3 - <<'EOF'
import zlib, base64, urllib.parse, sys
xml = open(sys.argv[1]).read()
c = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
compressed = c.compress(xml.encode('utf-8')) + c.flush()
encoded = base64.b64encode(compressed).decode('utf-8').replace('\n', '')
print('https://viewer.diagrams.net/?lightbox=1&edit=_blank#R' + urllib.parse.quote(encoded, safe=''))
EOF
```

---

## Kroki 引擎（轻量 SVG / 手绘风格）

零安装，通过 Kroki.io API 生成 Excalidraw 风格 SVG。

### 工作流

1. **生成 .excalidraw JSON** → 抄 `references/excalidraw-recipes.md`
2. **发送到 Kroki** → `curl -X POST https://kroki.io/excalidraw/svg -H "Content-Type: application/json" --data-binary "@diagram.excalidraw" -o diagram.svg`
3. **验证并交付**

### Excalidraw 配色（60-30-10 规则）

| 用途 | fill | stroke |
|------|------|--------|
| Primary / Input | `#dbeafe` | `#1e40af` |
| Success / Data | `#dcfce7` | `#166534` |
| Warning / Decision | `#fef9c3` | `#854d0e` |
| Error / Critical | `#fee2e2` | `#991b1b` |
| External / Storage | `#f3e8ff` | `#6b21a8` |
| Process | `#e0f2fe` | `#0369a1` |
| Trigger / Start | `#fed7aa` | `#c2410c` |

### 字号层级

Title 28px → Header 24px → Label 20px → Description 16px → Note 14px

### 布局间距

| 场景 | 间距 |
|------|------|
| 标签箭头间隔 | 150-200px |
| 无标签箭头间隔 | 100-120px |
| 列间距（带标签）| 400px |
| 行间距 | 280-350px |
| Zone 容器内边距 | 50-60px |

---

## 通用设计原则

### 箭头语义（必须指定）

| 语义 | Native SVG | draw.io | Excalidraw |
|------|-----------|---------|-----------|
| Primary flow | `control` | solid | `strokeStyle: null` |
| Memory read | `read` | solid | solid |
| Memory write | `write` | dashed | dashed |
| Async/event | `async` | dashed | `"dashed"` |
| Feedback/loop | `feedback` | curved | `"roundness"` |
| Response | `data` | dashed | `"dotted"` |

### 排版黄金法则

- 形状间距随复杂度放大：简单 200px，复杂 350px
- 箭头路由留走廊（80px 空隙）
- 网格对齐：Native SVG 120px 间隔，draw.io 10px 倍数
- 高度连接的中心节点居中，边缘节点围绕
- 事件总线放中间（不是底部），消除交叉线

### 禁止事项

- ❌ 箭头穿过形状内部 → 用 waypoints 绕行
- ❌ 标签文字溢出形状 → 用背景 rect 衬底
- ❌ 多条边重叠 → 分散 entry/exit 点
- ❌ draw.io 自检阶段用 `-e` 导出 PNG（vision API 报 400）
- ❌ 同一 PNG 反复导出覆盖不上的，用 v1/v2/v3

---

## 输出

- **Native SVG / Kroki**：默认 `./diagram.svg` + `./diagram.png`
- **draw.io**：`.drawio` XML 源文件 + `.drawio.png`（嵌入 XML，可拖回 draw.io 编辑）+ 可选 `.svg` / `.pdf`
- **自定义路径**：用户指定则用用户路径（`mkdir -p` 先创建）

---

## 图类型与引擎映射速查

| 图类型 | 推荐引擎 | 格式 |
|--------|---------|------|
| 架构图（通用）| Native SVG | SVG + PNG |
| OpenClaw 专属 | Native SVG | SVG + PNG |
| 数据流图 | Native SVG | SVG + PNG |
| 对比矩阵 | Native SVG | SVG + PNG |
| 时间线 | Native SVG | SVG + PNG |
| 思维导图 | Native SVG | SVG + PNG |
| ERD | **draw.io** | .drawio.png + SVG + PDF |
| UML 类图 | **draw.io** | .drawio.png + SVG + PDF |
| UML 时序图 | **draw.io** | .drawio.png + SVG + PDF |
| ML/DL 模型图 | **draw.io** | .drawio.png + SVG + PDF |
| 流程图（精细）| **draw.io** | .drawio.png + SVG + PDF |
| 手绘/草图风格 | **Kroki** | SVG |
| Excalidraw 风格 | **Kroki** | SVG |
