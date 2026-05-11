# Diagram Type Layouts — 完整规范

> 详细 layout 规则 + ViewBox + 常见错误

---

## Architecture Diagram

**用途**：服务/组件/云基础设施

**Layout**：水平分层（top→bottom 或 left→right）
- 典型层次：Client → Gateway/LB → Services → Data/Storage
- 用 `<rect>` 虚线容器对同层服务分组
- 箭头方向跟随数据/请求流向
- **ViewBox**：`0 0 960 600`（标准）/ `0 0 960 800`（多层堆叠）

**Spacing**：
- 同层节点：x 间隔 80px
- 层间：y 间隔 120px
- 画布边距：min 40px，节点边缘间距 60px

---

## Data Flow Diagram

**用途**：强调数据在哪流转、怎么转换

**Layout**：
- 每条箭头必须标注数据类型（`embeddings`、`query`、`context`）
- 主数据路径用粗箭头（`stroke-width: 2.5`）
- 控制/触发流用虚线箭头
- 颜色按数据类别区分（不只是 Agent/RAG）

---

## Flowchart / Process Flow

**Layout**：从上到下（优先）或从左到右
- 决策：diamond
- 过程：rounded rect
- I/O：parallelogram
- 节点标签 ≤3 词，详细放 sub-label
- **对齐**：x 位置按 120px 间隔对齐，y 按 80px 对齐

---

## Agent Architecture Diagram

**用途**：AI Agent 如何推理、使用工具、管理记忆

**5层模型**（始终考虑）：
```
Input Layer → Agent Core → Memory Layer → Tool Layer → Output Layer
```

- **Input layer**：User, query, trigger
- **Agent core**：LLM, reasoning loop, planner
- **Memory layer**：Short-term (context window), Long-term (vector/graph DB), Episodic
- **Tool layer**：Tool calls, APIs, search, code execution
- **Output layer**：Response, action, side-effects

**关键**：用循环箭头（loop arcs）表示迭代推理；不同 memory 类型视觉上分开

---

## Memory Architecture Diagram（Mem0/MemGPT）

**用途**：Memory 操作路径

**Layout**：
- **读写路径分开**（不同箭头颜色）
- Memory 层：Working → Short-term → Long-term → External Store
- 标注操作：`store()`, `retrieve()`, `forget()`, `consolidate()`
- 用堆叠 rect 或分层 cylinder 表示存储层

---

## Sequence Diagram

**用途**：时间顺序的接口调用

**Layout**：
- 参与者 = 垂直 lifeline（顶标签 + 垂直虚线）
- 消息 = 水平箭头，lifeline 之间，从上到下时间顺序
- Activation boxes（lifeline 上的小实心 rect）表示处理中
- 用 `<rect>` loop/alt 帧分组，标签放左上角
- **ViewBox**：height = `80 + (num_messages × 50)`

---

## Comparison / Feature Matrix

**Layout**：
- 列头 = 系统，行头 = 属性
- 行高 40px；列宽 min 120px；表头行高 50px
- 有功能：tinted background（如 `#dcfce7`）+ `✓`
- 无功能：`#f9fafb` 填充
- 行交替填充（`#f9fafb` / `#ffffff`）
- **最多 5 列可读**；超过则拆成两个图

---

## Timeline / Gantt

**Layout**：
- X轴 = 时间（周/月/季度）；Y轴 = 项目/任务/阶段
- 条形：rounded rect，按类别着色，标签放内部或旁边
- 里程碑：diamond 或实心圆，x 位置 + 上方标签
- **ViewBox**：`0 0 960 400`（典型）；`0 0 1200 400`（多时间段）

---

## Mind Map / Concept Map

**Layout**：
- 中心节点：`cx=480, cy=280`
- 一级分支：从中心均匀分布（360/N 度）
- 二级分支：从一级分支以 30-45° 偏角伸出
- 分支用三次贝塞尔曲线 `<path>`（不是直线）

---

## UML Class Diagram

**Class box**（3格 rect）：
- 上格：类名，居中加粗（抽象 = *斜体*）
- 中格：属性，`+` public / `-` private / `#` protected
- 下格：方法签名，同上

**关系**：
| 关系 | 线型 + 箭头 |
|------|------------|
| 继承 | 实线 + 空心三角 |
| 实现接口 | 虚线 + 空心三角 |
| 关联 | 实线 + 空箭头 |
| 聚合 | 实线 + 空心菱形 |
| 组合 | 实线 + 实心菱形 |
| 依赖 | 虚线 + 空箭头 |

---

## UML State Machine

**State**：rounded rect，min 120×50px
- 内部活动：`entry/action`, `exit/action`, `do/activity`
- **初始状态**：实心黑圆（r=8），一条外出箭头
- **终态**：实心圆（r=8）套空心圆（r=12）
- **选择**：空心小菱形，守卫标签在外出箭头

**Transition**：箭头 + 可选标签 `event [guard] / action`

**Layout**：initial state 左上 → final state 右下，top-to-bottom

---

## ER Diagram

**Entity**：rect，表头 bold
- Primary key：下划线
- Foreign key：斜体或 `(FK)` 标记
- Min width：160px

**Relationship**：连接线上的菱形
- 标签：`has`, `belongs to`, `enrolls in`
- 基数标签：`1`, `N`, `0..1`, `0..*`, `1..*`

**Weak entity**：双线框 + 双菱形 relationship

---

## Network Topology

**设备**：
| 设备 | 形状 |
|------|------|
| Router | 圆 + 交叉箭头 |
| Switch | 矩形 + 箭头网格 |
| Server | 堆叠矩形（机架图标） |
| Firewall | 砖块矩形或盾形 |
| Load Balancer | 水平分割矩形 + 箭头 |
| Cloud | 重叠弧线组成的云形 |

**连接**：实线（有线）/ 虚线 + WiFi符号（无线）/ 虚线 + 锁（VPN）

**子网/区域**：虚线矩形容器 + 区域标签（DMZ, Internal, External）

---

## Jump-Over 交叉处理

**最重要也最常被忽略的规则**：

当两条箭头必须交叉时，**必须**用 jump-over arc 防止视觉重叠：
```xml
<!-- 白色背景弧线跳到上方 -->
<path d="M x,y-5 a 5,5 0 0,1 10,0" fill="none" stroke="white" stroke-width="3"/>
<!-- 实际箭头画在上方 -->
<path d="..." stroke="blue" marker-end="url(#arrowB)"/>
```

- 多个交叉：交错半径（5px, 7px, 9px）避免重叠
- 从不：让两条箭头直线段直接交叉而不加 arc
