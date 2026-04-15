---
name: ecology-monitor
description: >
  技能生态系统监测器 — 监控skill群体健康度、识别濒危/入侵物种、检测共生依赖。
  用于：定期评估skill生态、发现孤岛技能、识别技术债、追踪skill演化趋势。
  核心功能：生态健康度评估、濒危/入侵检测（共2种判断路径：usage频率 + file_size）、共生关系发现。
  内置 usage_tracker 记录真实调用，配合 ecology_monitor.py 输出准确报告。
triggers:
  - keywords: ["生态系统", "生态监测", "濒危", "入侵", "共生", "skill健康度", "skill演替", "技术生态", "代谢率"]
    load: true
    priority: high
---

# Ecology Monitor — 技能生态系统监测器

*将整个 OpenClaw skill 群体视为演化中的生态系统*

---

## 生态思维 vs 系统思维

| 维度 | 系统思维 | 生态思维 |
|------|---------|---------|
| 时间观 | 稳态维持（Homeostasis）| 共同演化（Co-evolution）|
| 空间观 | 边界清晰的系统 | 无边界渗透（Holon）|
| 成功标准 | 系统目标达成 | 生态位占据，共生可持续 |

---

## 生态指标体系

### 代谢率指标

| 指标 | 说明 | 健康值 |
|------|------|--------|
| **新增率** | 新skill数/周期 | 警戒线 > 5/周 |
| **淘汰率** | 废弃skill数/周期 | 警戒线 > 2/季度 |
| **净增率** | 新增 - 淘汰 | 健康: 0.5-2/月 |

### 多样性指标

| 指标 | 说明 | 健康值 |
|------|------|--------|
| **Shannon指数** | 技能分布均匀度 | > 3.5 优秀, < 2.0 危险 |
| **功能冗余** | 同功能skill数量 | 过多=冗余, 过少=脆弱 |
| **领域覆盖** | 覆盖领域数 | 越多越健康 |

---

## 濒危技能识别

### 濒危信号

| 濒危原因 | 表现 | 检测方法 |
|---------|------|---------|
| **无人使用** | 调用频率 < 1次/月 | session-miner数据 |
| **功能重叠** | 被其他skill完全覆盖 | 对比触发词 |
| **技术过时** | 依赖已废弃API | 检查兼容性 |
| **维护缺失** | 长时间无更新 | git日志 |

### 保护策略

```
濒危skill → 评估价值
  ├─ 高价值 + 低使用 → 重推广 + 更新文档
  ├─ 低价值 + 低使用 → 归档或合并
  └─ 高价值 + 可替代 → 迁移到活跃skill
```

---

## 入侵物种识别

### 入侵信号（2种判断路径）

**路径1：使用频率（更准确）**
```bash
python3 ~/.openclaw/workspace/skills/ecology-monitor/scripts/usage_tracker.py stats 30
```
调用频率 > 平均3倍 = 潜在入侵

**路径2：文件规模（备用）**
| 入侵原因 | 表现 | 检测方法 |
|---------|------|---------|
| **功能膨胀** | size > 50KB + 有scripts | 触发词重叠分析 |
| **依赖集中** | 大量skill依赖它 | 反向依赖分析 |
| **版本落后** | 长期不更新 | git日志 |

### 管控策略

```
入侵skill → 评估影响
  ├─ 拆分功能 → 拆分为多个专注skill
  ├─ 降低触发优先级 → 缩小触发词范围
  └─ 建立竞争 → 扶持替代skill
```

### 使用频率追踪

**记录使用**（建议在每次skill加载时调用）：
```bash
python3 ~/.openclaw/workspace/skills/ecology-monitor/scripts/usage_tracker.py record <skill-name> [trigger]
```

**查看统计**：
```bash
python3 ~/.openclaw/workspace/skills/ecology-monitor/scripts/usage_tracker.py
```

**数据位置**：`~/.openclaw/workspace/.state/skill-usage/usage.jsonl`

---

## 共生关系发现

### 共生类型

| 类型 | 说明 | 检测方法 |
|------|------|---------|
| **依赖共生** | A需要B才能工作 | 调用关系分析 |
| **触发共生** | A触发B的使用 | 共同出现频率 |
| **互补共生** | A+B > 2A+2B | 组合效果分析 |
| **竞争共生** | A替代B但也促使B进化 | 替代-促进关系 |

### 共生网络

```
技能A ──依赖──► 技能B
  │
  │─触发─► 技能C
  │
  └─互补──► 技能D + 技能E
```

---

## 使用工具

### 1. 生态健康度评估

```python
from ecology_monitor import assess_ecosystem_health

result = assess_ecosystem_health(
    skills_dir="~/.openclaw/workspace/skills",
    session_data="~/.openclaw/agents/main/sessions"
)
# 输出：{health_score, metrics, endangered, invasive, recommendations}
```

### 2. 濒危技能检测

```python
from ecology_monitor import detect_endangered

result = detect_endangered(
    skills=["skill-a", "skill-b"],
    usage_data={...}
)
# 输出：{endangered_skills, reasons, protection_priority}
```

### 3. 入侵检测

```python
from ecology_monitor import detect_invasive

result = detect_invasive(
    skills=["skill-x", "skill-y"],
    call_graph={...}
)
# 输出：{invasive_skills, spread_pattern, control_measures}
```

### 4. 共生网络分析

```python
from ecology_monitor import analyze_symbiosis

result = analyze_symbiosis(
    skills=["lobster-evolution", "session-miner", "skill-proposer"],
    call_data=[...]
)
# 输出：{symbiosis_pairs, network_graph, key_species}
```

---

## 输出格式

### 生态健康报告

```markdown
## 技能生态系统健康报告

**综合评分**：XX/100
**等级**：🟢优秀 | 🟡良好 | 🔴危险

### 代谢指标
| 指标 | 当前值 | 健康范围 |
|------|--------|---------|
| 新增率 | X/周 | < 5 |
| 淘汰率 | X/季度 | < 2 |
| 多样性 | X.XX | > 3.5 |

### 濒危技能（X个）
| Skill | 原因 | 保护优先级 |
|-------|------|-----------|
| skill-a | 无人使用 | 高 |

### 入侵技能（X个）
| Skill | 原因 | 控制措施 |
|-------|------|-----------|
| skill-x | 过度扩张 | 拆分 |

### 共生网络
- 关键物种：skill-a, skill-b
- 强依赖链：A→B→C

### 建议
1. ...
2. ...
```

---

## 与其他模块的集成

| 上游 | 下游 |
|------|------|
| session-miner（使用数据）| complexity-sensor（复杂度输入）|
| | lobster-evolution（进化决策）|

---

## 局限与警示

- **数据稀疏**：新skill缺乏使用数据，评估不准
- **定义主观**：濒危/入侵阈值需要校准
- **生态惯性**：生态系统变化缓慢，需要长期观察

**使用频率**：建议每月一次生态评估
