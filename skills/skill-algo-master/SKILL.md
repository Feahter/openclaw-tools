---
name: skill-algo-master
description: |
  算法全能工具箱 — LOOKUP 秒查 / ANALYZE 问题推荐 / RESEARCH 深度研究。

  **LOOKUP 触发（满足任一）：**
  - 用户问"用什么算法"、"有没有现成的"、"XXX 复杂度"
  - 用户要求"实现 LRU"、"写个堆"、"并查集怎么写"
  - 用户问数据结构（堆、线段树、哈希表、并查集）
  - 用户说"太慢了"、"O(n²)"、"优化这段代码"

  **ANALYZE 触发（满足任一）：**
  - 用户没有给出算法名，需要分析问题类型再推荐
  - 用户问"这种情况用什么算法好"
  - 用户描述问题但不确认算法

  **RESEARCH 触发（满足任一）：**
  - 用户说"研究这个算法"、"帮我理解 XXX 算法原理"
  - 用户问"这个算法和 XXX 有什么区别"
  - 用户要求"分析下这个算法"、"算法论文解读"

  **不触发：**
  - 用户在描述业务逻辑，无性能/算法问题 → 不触发
  - 用户要求完整系统设计 → 用 system-design skill
  - 用户要的是数据库/操作系统/网络协议 → 用对应 skill

  **两种风格**：竞赛版（最短最快）vs 工程版（健壮可维护）
  **支持语言**：Python / JavaScript / TypeScript / Rust / Go / C++
---

# skill-algo-master — 算法全能工具箱

LOOKUP 模式秒级响应，ANALYZE 模式定向推荐，RESEARCH 模式深度剖析。

---

## 决策树

```
用户问题
  │
  ├─ 已有算法名 → LOOKUP → 从 references/algorithms.md 提取代码
  │
  ├─ 无算法名，描述问题 → ANALYZE → 判断问题类型 → 推荐算法
  │
  └─ 要深入理解/对比/研究 → RESEARCH → 7步深度研究报告
```

---

## LOOKUP 模式：快速决策表

根据关键词直接匹配，跳转到 `references/algorithms.md` 提取代码。

### 竞赛算法口诀（OI/ACM 高频）

| 口诀 | 算法 | 复杂度 | 代码位置 |
|------|------|--------|---------|
| 区间更新线段树 | 线段树 + 懒标记 | O(log n) | references/algorithms.md |
| 连通分量并查集 | Union-Find | O(α(n)) | references/algorithms.md |
| 缩点重建强连通 | Tarjan SCC | O(V+E) | references/algorithms.md |
| 有序问题上二分 | 二分查找 | O(log n) | references/algorithms.md |
| 最长回文马拉车 | Manacher | O(n) | references/algorithms.md |
| 字符串匹配KMP | KMP | O(n+m) | references/algorithms.md |
| 无序查找哈希表 | Hash Map | O(1) | references/algorithms.md |
| 有序离散化树状数组 | BIT + 离散化 | O(log n) | references/algorithms.md |
| 区间求和削缀和 | 前缀和 + 差分 | O(n)/O(1) | references/algorithms.md |
| 最值问题搞个堆 | 堆 / 单调栈 | O(log n)/O(n) | references/algorithms.md |
| 递归爆栈改迭代 | 显式栈 / Morris | O(n) | references/algorithms.md |
| 大数越界高精度 | 字符串竖式运算 | O(n²) | references/algorithms.md |

### 通用数据结构速查

| 问题 | 推荐算法 | 复杂度 | 风格 |
|------|---------|--------|------|
| 第 K 大/小 | 快速选择 | O(n) | 竞赛 |
| 频繁查找 O(1) | 哈希表 | O(1) | 工程 |
| 范围查询 | 线段树 | O(log n) | 工程 |
| 前缀和动态更新 | 树状数组 BIT | O(log n) | 工程 |
| 去重/存在性判断 | 布隆过滤器 | O(k) 空间 | 工程 |
| 最短路径 | Dijkstra | O(E log V) | 工程 |
| 最小生成树 | Kruskal / Prim | O(E log E) | 工程 |
| 排行榜 Top-K | 堆 / 快速选择 | O(n log k) | 视场景 |
| LRU 缓存 | 双向链表+哈希 | O(1) | 工程 |
| 图社区检测 | Leiden / Louvain | O(n log n) | 工程 |

**选风格**：生产环境默认工程版，追求极限性能用竞赛版。

### references/algorithms.md 当前内容

- 并查集 / 线段树 / 树状数组 / 堆 / LRU
- KMP / Manacher / Dijkstra / Kruskal
- Leiden / Louvain 社区检测
- **新增**：Tarjan SCC / 拓扑排序 / 高精度 / 递归改迭代 / 平衡 BST
- **新增**：字符串算法（KMP/AC自动机/SAM）/ DP优化四件套 / 计算几何 / 网络流 / 数论

---

## ANALYZE 模式：问题类型 → 算法推荐

当用户没有给出具体算法名时，分析问题类型再推荐。

### 问题类型识别

| 问题模式 | 推荐算法 | 推荐理由 |
|---------|---------|---------|
| "从 N 个里找 Top-K" | 堆 or 快速选择 | 堆适合实时，QuickSelect 适合一次性 |
| "有重复要去重" | 哈希表 or 布隆过滤器 | 数据小用哈希，数据极大用布隆 |
| "要快速判断存不存在" | 布隆过滤器 or 哈希 | 布隆省空间，哈希精确 |
| "要算区间和" | BIT or 线段树 | 简单前缀和用 BIT，复杂合并用线段树 |
| "最短路径/最优解" | Dijkstra / A* / DP | 权值非负用 Dijkstra，有启发用 A* |
| "字符串匹配" | KMP / AC自动机 / Manacher | 单模式用 KMP，多模式用 AC，回文用 Manacher |
| "图连通性" | 并查集 / SCC | 简单连通用并查集，强连通用 Tarjan |
| "字符串子串问题" | SAM 后缀自动机 | O(n) 处理所有子串 |
| "滑动窗口最值" | 单调队列 | 双端队列，均摊 O(1) |
| "离线区间查询" | 莫队算法 | O(n√n) |

### 推荐输出格式

```
## 分析结论

**问题类型**：[分类]
**推荐算法**：[名字]
**复杂度**：[时间] / [空间]
**不适合场景**：[如果有]
**选择原因**：[一句话]
```

---

## RESEARCH 模式：7步深度研究

**完整 SOP 在** `references/research-sop.md`。

触发 RESEARCH 模式后：

```
1. 定性 → 一句话定位算法本质
2. 对比 → 找家族，理解改进了什么
3. 公式 → 提取核心数学公式
4. 代码 → 定位核心文件，逐段解读
5. 优化 → 分析可优化方向
6. 迁移 → 应用到具体场景
7. 实现 → 输出基础版 + 优化版
```

**RESEARCH 7步核心模板**（详见 `references/research-sop.md`）：

```markdown
## 1. 算法定性
| 维度 | 分析 |
|------|------|
| 本质 | |
| 核心思想 | |
| 时间复杂度 | O(?) |
| 空间复杂度 | O(?) |

## 2. 与经典算法对比
| 经典算法 | 共同点 | 本算法改进点 |

## 3. 核心公式
[公式 + 变量说明]

## 4. 关键代码解析
[分阶段代码解读]

## 5. 优化方向
| 当前 | 可优化 | 适用场景 |

## 6. 应用场景迁移
| 场景 | 应用方式 | 注意事项 |

## 7. 实现
基础版（50-150行） + 优化版（150-400行）
```

---

## 快速参考

### 数据结构 5 问

| 问题 | 答案 |
|------|------|
| 查「是否存在」→ 精确 | 哈希表 |
| 查「是否存在」→ 可能误判 | 布隆过滤器 |
| 查「Top-K」→ 实时 | 堆 |
| 查「Top-K」→ 一次性 | 快速选择 |
| 查「区间和」→ 简单 | BIT |
| 查「区间和」→ 复杂合并 | 线段树 |
| 合并「集合」+ 查「连通」 | 并查集 |

### 复杂度直观对照（n = 10⁶）

| 复杂度 | 实际感受 |
|--------|---------|
| O(1) | 瞬间 |
| O(log n) | ~20 步 |
| O(n) | 10⁶ 步，可接受 |
| O(n log n) | ~2×10⁷ 步，边缘 |
| O(n²) | 10¹² 步，不可行 |

---

## 参考文件

| 文件 | 内容 |
|------|------|
| `references/algorithms.md` | 全部算法代码库（808行）|
| `references/research-sop.md` | 完整 7步 RESEARCH SOP + 模板 |

---

## 如何新增算法

1. RESEARCH 模式研究新算法
2. 追加到 `references/algorithms.md`（格式模板在 research-sop.md）
3. 在本 SKILL.md 快速决策表追加一行

---

## 输出规范

| 模式 | 输出要求 |
|------|---------|
| LOOKUP | 算法名 + 复杂度 + 代码（竞赛版 + 工程版）+ 适用/不适用 |
| ANALYZE | 问题分类 + 推荐算法 + 推荐理由 + 一句话定性 |
| RESEARCH | 完整 7步报告（详见 research-sop.md）|
