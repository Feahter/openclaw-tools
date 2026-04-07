---
name: llm-wiki-agent
description: >
  LLM 编译的个人知识库。投入原始资料 → 自动构建结构化 wiki → 知识复利增长。
  基于 Karpathy 的 LLM Wiki 方法论，每次摄入新来源都会自动创建/更新实体页、概念页、交叉引用，并在摄入时标记矛盾。
  
  触发场景：知识管理、论文阅读、读书笔记、竞品分析、长期追踪某领域、构建个人知识库。
  
  关键词：wiki, 知识库, knowledge base, 摄入, ingest, 文献管理, 笔记, obsidian, karpathy

metadata:
  openclaw:
    homepage: https://github.com/SamurAIGPT/llm-wiki-agent
---

# LLM Wiki Agent — OpenClaw Skill

**核心理念**：让 LLM 把原始资料编译成结构化 wiki，实现知识复利。不是每次查询都重新推理，而是编译一次、持续更新。

## 与 RAG 的区别

| RAG | LLM Wiki |
|-----|----------|
| 每次查询重新检索 chunks | 编译一次，持续更新 |
| 检索单位是原始片段 | 检索单位是结构化 wiki 页面 |
| 无交叉引用 | 预建 `[[wikilink]]` 交叉引用 |
| 矛盾可能在查询时才发现 | **摄入时就标记矛盾** |
| 无积累效应 | 每个新来源让 wiki 更丰富 |

---

## 目录结构

```
{openclaw_skill_dir}/llm-wiki-agent/
├── raw/              # 原始资料（只读，永不修改）
├── wiki/             # LLM 维护的结构化 wiki
│   ├── index.md      # 所有页面目录
│   ├── log.md        # 操作日志（append-only）
│   ├── overview.md   # 活综述（每次摄入更新）
│   ├── sources/      # 每篇来源的摘要页
│   ├── entities/     # 人物、公司、项目
│   ├── concepts/     # 概念、框架、方法
│   └── syntheses/    # 保存的查询答案
├── graph/            # 知识图谱数据
│   ├── graph.json    # 节点/边数据
│   └── graph.html    # vis.js 可视化
└── tools/            # Python 独立脚本（可选）
```

---

## 核心工作流

### 1. 摄入（Ingest）

**触发**：`/wiki-ingest raw/paper.md` 或 "摄入这个文件：raw/paper.md"

**步骤**：
1. 读取原始文件
2. 读取 `wiki/index.md` 和 `wiki/overview.md` 获取当前上下文
3. 写入 `wiki/sources/<slug>.md`（来源摘要页）
4. 更新 `wiki/index.md`（添加到 Sources 列表）
5. 更新 `wiki/overview.md`（修订综述）
6. 创建/更新实体页（`wiki/entities/`）
7. 创建/更新概念页（`wiki/concepts/`）
8. 标记与现有内容的矛盾
9. 追加到 `wiki/log.md`

**来源页格式**：
```markdown
---
title: "Source Title"
type: source
tags: []
date: YYYY-MM-DD
source_file: raw/...
---

## Summary
2-4 句摘要。

## Key Claims
- 主张 1
- 主张 2

## Key Quotes
> "引用内容" — 上下文

## Connections
- [[EntityName]] — 关系说明
- [[ConceptName]] — 关联说明

## Contradictions
- 与 [[OtherPage]] 矛盾：...
```

---

### 2. 查询（Query）

**触发**：`/wiki-query "主题"` 或 "wiki 对 X 有什么看法？"

**步骤**：
1. 读取 `wiki/index.md` 定位相关页面
2. 读取相关页面
3. 综合回答，内联 `[[wikilink]]` 引用
4. 询问是否保存到 `wiki/syntheses/<slug>.md`

---

### 3. 审计（Lint）

**触发**：`/wiki-lint` 或 "审计 wiki"

**检查项**：
- 孤立页面（无入链）
- 断链（指向不存在的页面）
- 矛盾（跨页冲突）
- 过时摘要（有新来源但未更新）
- 缺失实体页（被 3+ 页面提及但无独立页）
- 数据缺口（wiki 无法回答的问题）

---

### 4. 图谱（Graph）

**触发**：`/wiki-graph` 或 "构建知识图谱"

**输出**：
- `graph/graph.json`：节点/边数据
- `graph/graph.html`：vis.js 可视化（浏览器打开）

---

## 页面命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 来源页 | `kebab-case.md` | `attention-is-all-you-need.md` |
| 实体页 | `TitleCase.md` | `OpenAI.md`, `SamAltman.md` |
| 概念页 | `TitleCase.md` | `RAG.md`, `ReinforcementLearning.md` |

---

## 使用示例

### 研究某领域
```
/wiki-ingest raw/papers/attention-is-all-you-need.md
/wiki-ingest raw/papers/llama2.md
/wiki-ingest raw/papers/rag-survey.md

/wiki-query "减少幻觉的主要方法有哪些？"
/wiki-query "上下文窗口大小如何演进？"

/wiki-lint
# → "缺少 mixture-of-experts 相关来源，建议摄入 Mixtral 论文"
```

### 读书笔记
```
/wiki-ingest raw/book/chapter-01.md
/wiki-ingest raw/book/chapter-02.md

/wiki-query "主角的动机如何演进？"
/wiki-query "作者论证中有哪些矛盾？"

/wiki-graph  # → 查看人物/主题关系图
```

### 个人知识库
```
/wiki-ingest raw/journal/2026-01-week1.md
/wiki-ingest raw/articles/huberman-sleep-protocol.md

/wiki-query "我的日志中关于精力的模式有哪些？"
```

---

## 初始化

首次使用需要初始化 wiki 结构：

```bash
# 确保 wiki 目录存在
mkdir -p {openclaw_skill_dir}/llm-wiki-agent/wiki/{sources,entities,concepts,syntheses}
mkdir -p {openclaw_skill_dir}/llm-wiki-agent/raw
mkdir -p {openclaw_skill_dir}/llm-wiki-agent/graph
```

或者直接说："初始化 llm-wiki"

---

## 与 Obsidian 联用

- 用 Obsidian 打开 `llm-wiki-agent/wiki/` 目录
- 利用 Obsidian 的图谱视图、Dataview 插件
- 使用 Obsidian Web Clipper 剪藏网页到 `raw/`

---

## 相关链接

- [GitHub](https://github.com/SamurAIGPT/llm-wiki-agent)
- [Karpathy LLM Wiki 原始讨论](https://x.com/karpathy/status/...)
