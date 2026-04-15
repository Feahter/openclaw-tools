---
name: complexity-sensor
description: >
  复杂性思维传感器 — 检测 skill 组合的复杂度、相变临界点、涌现信号。
  用于：当技能组合产生意外结果时、故障排查时、系统行为异常时、技术架构评审时。
  核心功能：监控 skill 组合的复杂度、检测相变临界点、识别涌现行为。
triggers:
  - keywords: ["复杂度", "complexity", "涌现", "emergence", "相变", "混沌边缘", "非线性", "系统异常", "skill组合"]
    load: true
    priority: high
---

# Complexity Sensor — 复杂性思维传感器

*监控 skill 组合的复杂度，检测相变临界点，识别涌现行为*

## 复杂性 vs 系统思维

| 维度 | 系统思维 | 复杂性思维 |
|------|---------|-----------|
| 核心关注 | 结构平衡（输入=输出）| 相变临界点（秩序/混沌边缘）|
| 关键指标 | 稳定性、鲁棒性 | 适应力、创新性、反脆弱性 |
| 操作工具 | 存量-流量图、反馈回路 | 幂律分布、小世界网络、自组织临界性 |

**判断信号**：优化某个子系统反而导致整体性能下降（如过度优化局部缓存导致全局一致性问题）

---

## 复杂度检测框架

### 1. 复杂度指标

```
复杂度 = Σ(skill数量 × 连接数) + Σ(依赖深度) + 非线性项
```

**三个关键指标**：

| 指标 | 计算方式 | 阈值 |
|------|---------|------|
| **连接密度** | 实际连接数 / 可能连接数 | >0.3 高风险 |
| **依赖深度** | 最大调用链长度 | >5层 预警 |
| **非线性项** | 循环依赖 + 反馈回路 | 存在即高风险 |

### 2. 相变临界点检测

**相变信号**：
- 某 skill 触发频率突然增加 > 3x
- Skill 组合出现从未出现的搭配
- 系统响应时间出现非线性增长
- 用户反馈模式发生质变

**临界点判断**：
```
IF (连接密度 > 0.3) AND (反馈回路存在)
THEN 触发「混沌边缘」预警
```

### 3. 涌现行为识别

**涌现类型**：

| 类型 | 表现 | 检测方法 |
|------|------|---------|
| 顺序涌现 | 组合效果 > 各部分之和 | diff(组合效果, Σ独立效果) |
| 抑制涌现 | 某 skill 压制其他 skill | 检测调用频率异常 |
| 跨域涌现 | 不同领域 skill 组合产生新能力 | 领域标签交叉分析 |

---

## 使用场景

### 场景1：技能组合异常检测

当多个 skills 被同时调用时，检测是否会触发高复杂度：

```python
from complexity_sensor import assess_complexity

result = assess_complexity(
    skills=["lobster-evolution", "session-miner", "skill-proposer"],
    context={"task": "自主进化"}
)
# 输出：{complexity_score, phase_transition_risk, emergent_signals}
```

### 场景2：故障排查

当系统行为异常时，识别是否是复杂性导致：

```
问题：优化了 session-miner，反而导致 lobster-evolution 效果下降
分析：发现两者共享状态 → 优化触发反馈回路 → 相变
建议：回滚 or 解除共享状态
```

### 场景3：架构评审

定期扫描 skill 群体的复杂度：

| 指标 | 当前值 | 风险等级 |
|------|--------|---------|
| 平均连接密度 | 0.15 | 🟢 低 |
| 最大依赖深度 | 4 | 🟡 中 |
| 反馈回路数 | 2 | 🔴 高 |
| 濒危 skill 数 | 3 | 🟡 中 |

---

## 检测算法

### 复杂度评分函数

```python
def complexity_score(skills: list[str], calls: list[tuple]) -> dict:
    """
    返回：
    {
        score: 0-100,  # 复杂度得分
        level: "low" | "medium" | "high" | "critical",
        factors: [贡献最大的因素],
        warnings: [需要关注的信号],
        recommendations: [缓解建议]
    }
    """
```

### 相变检测

```python
def detect_phase_transition(
    current_metrics: dict,
    historical_metrics: list[dict],
    threshold: float = 0.3
) -> dict:
    """
    检测是否接近相变临界点
    返回：{is_near_transition, risk_level, triggering_factors}
    """
```

---

## 与其他模块的集成

| 上游 | 下游 |
|------|------|
| session-miner（观察）| lobster-evolution（执行）|
| | metacognition-auditor（审计）|

---

## 输出格式

每次检测输出：

```markdown
## 复杂度分析报告

**综合得分**：XX/100
**等级**：🟢低 | 🟡中 | 🔴高 | ⚫临界

### 关键指标
- 连接密度：X.X
- 依赖深度：X层
- 反馈回路：X个

### 相变风险
[是/否] 接近临界点
触发因素：...

### 涌现信号
- 检测到X个潜在涌现行为
- 最值得关注：...

### 建议
1. ...
2. ...
```
