---
name: talent-mind
description: 天才思维方法论 - 三层递归操作系统。用于深度思考、问题分析、认知升级。触发：天才思维、talent-mind、思维升级、遇到难题、思维瓶颈。
triggers:
  - keywords: ["天才思维", "talent-mind", "思维升级", "深度思考", "如何像天才一样思考"]
    load: true
    priority: high
pipeline:
  root: pipeline/
---

# 天才思维方法论 — 三层递归操作系统

*基于三层递归操作系统的认知升级指南*

## Preamble

1. 读取 `MEMORY.md`
2. 读取 `memory/YYYY-MM-DD.md`（今日 + 昨日）
3. 读取 `memory/skills/talent-mind/context.md`（如存在）

---

## 两种执行模式

### 模式 A：交互式思维导引（推荐）

```bash
python3 ~/.openclaw/workspace/skills/talent-mind/pipeline/talent-mind.py
```

AI 引导你完成三层思考协议，全程问答交互。

### 模式 B：快速结构化分析

```bash
bash ~/.openclaw/workspace/skills/talent-mind/pipeline/talent-mind.sh "你的问题"
```

输出结构化 Markdown 模板到 `.state/talent-mind-YYYYMMDD-HHMMSS.md`。

### 模式 C：直接对话（最简）

直接对我说"用天才思维分析 XXX"，我来引导三层思考。

---

## 三层操作系统

### 第一层：认知架构（硬件层）

**系统A**（直觉）→ **系统B**（反例验证）

> 遇到"显然"的结论，强制问：反例是什么？

### 第二层：表征方式（软件层）

**三种语言强制切换**：数学精确 ↔ 几何视觉 ↔ 隐喻叙事

> 单一表征有盲区，切换才能看见

### 第三层：元认知协议（操作系统层）

**对象层** → **过程层** → **元层**（递归）

> 沉浸思考时强制跳出来，看自己用什么框架思考

---

## 快速执行口诀

```
直觉来 → 找反例
单一视角 → 切三种
沉浸思考 → 跳出来
理所当然 → 问负空间
```

---

## 执行后记录

每次完成天才思维分析后，将关键洞察追加到：

→ `memory/skills/talent-mind/context.md`
→ `memory/YYYY-MM-DD.md`
