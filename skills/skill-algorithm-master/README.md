# skill-algorithm-master

算法全能工具箱。Lookup 秒级响应，Research 深度剖析。

## 文件结构

```
skill-algorithm-master/
├── SKILL.md                      # 主文件：决策树 + 快速参考（186行）
└── references/
    ├── algorithms.md            # 全部算法代码库（572行）
    ├── research-sop.md          # 完整7步研究SOP（~200行）
    └── evaluation.md           # 量化评价体系（~100行）
```

## 三种工作模式

| 模式 | 触发条件 | 输出 |
|------|---------|------|
| **LOOKUP** | 知道算法名，查代码/复杂度 | 算法 + 代码 + 复杂度 |
| **ANALYZE** | 不知道用什么，要分析推荐 | 问题分类 + 推荐算法 + 理由 |
| **RESEARCH** | 要研究/理解/对比算法 | 完整7步研究报告 |

## 来源

合并自：
- `algorithm-toolkit` — lookup 能力 + 代码库
- `skill-algo-researcher` — research 深度研究流程
- `memory/research/algorithm-sop.md` — 归档模板

## 使用

- LOOKUP：直接读 SKILL.md 快速决策表，从 references/algorithms.md 提取代码
- ANALYZE：读 SKILL.md 问题类型识别，从 references/algorithms.md 推荐算法
- RESEARCH：读 references/research-sop.md，执行 7 步研究，结果归档到 references/algorithms.md
