---
name: lobster-evolution
description: >
  龙虾（OpenClaw）自动进化引擎——观察→判断→执行→验证闭环。
  利用 session-miner 跨Session模式挖掘、skill-proposer 技能提案、
  self-improving 错误自愈、skill-evolution-manager 经验缝合，
  实现无需外部训练管道的能力自动增长。
  
  触发：自动进化、龙虾如何进化、lobster-evolution、session挖掘、技能提案、
  模式发现、自动成长、能力提升。
triggers:
  - keywords: ["自动进化", "龙虾进化", "lobster evolution", "session挖掘", "技能提案", "模式发现", "能力成长"]
    load: true
    priority: high
---

# 🦞 Lobster Evolution — 龙虾自动进化引擎

*让龙虾自己变强*

## 核心理念

**进化的上限是行为适应，进化的深度是自动化程度。**

在"不能改模型权重"的硬约束下，最大化进化 = **最大化自动化适应循环的闭环程度**。

---

## 进化闭环架构

```
[观察层] session日志 + daily-mining
    ↓
[判断层] skill-proposer → 模式识别 → 技能提案
    ↓
[执行层] skillhub_install + skill-evolution-manager + 文件写入
    ↓
[验证层] 下次心跳验证效果 → 强化/回滚
```

---

## 核心组件

| 组件 | 位置 | 职责 |
|------|------|------|
| session-miner | scripts/evolution/session-miner.py | 跨Session Query提取+统计 |
| skill-proposer | scripts/evolution/skill-proposer.py | 模式分析+技能提案生成 |
| daily-mining | .state/evolution/daily-mining.md | 当日挖掘结果 |
| proposals | .state/evolution/proposals/ | 待审批技能提案 |

---

## 快速执行

### 手动触发完整进化周期

```bash
# Step 1: 挖掘最近7天模式
python3 ~/.openclaw/workspace/scripts/evolution/session-miner.py 7

# Step 2: 生成技能提案
python3 ~/.openclaw/workspace/scripts/evolution/skill-proposer.py

# Step 3: 查看提案
cat ~/.openclaw/workspace/.state/evolution/proposals/proposals-*.md
```

### 查看当前进化状态

```bash
# 最近挖掘报告
cat ~/.openclaw/workspace/.state/evolution/daily-mining.md

# 活跃提案
ls ~/.openclaw/workspace/.state/evolution/proposals/

# Skills审计状态
cat ~/.openclaw/workspace/memory/heartbeat-state.json | jq .lastChecks
```

---

## 五大进化维度

### 维度1：跨Session模式挖掘 ✅ 已部署

**现状**：每日心跳自动执行，结果存 `daily-mining.md`

**数据源**：`~/.openclaw/agents/main/sessions/*.jsonl`

**输出**：
- 高频短Query（≤15字）= 具体指令意图
- 高频中Query（16-40字）= 描述性请求
- 高频中文词 = 领域热度

**触发频率**：每天首次心跳

---

### 维度2：自动技能提案生成 ✅ 已部署

**现状**：基于挖掘结果自动生成提案，存 `proposals/`

**提案类型**：

| 类型 | 触发条件 | 优先级 |
|------|---------|--------|
| 高频领域 | 中文词≥10次/7天 | high |
| 高频指令 | 短Query≥5次/7天 | high |
| 意图趋势 | 某领域词出现次数突增≥3 | medium |

**当前活跃提案**：
- 节气×73（🔴 high）→ chinese-name-lookup 已覆盖
- high_freq_query×多种（🔴 high）→ 子Session 代码片段，需优化上下文
- 命理×10, 搜索×14（🟡 medium）

---

### 维度3：错误自愈循环 🚧 待增强

**现状**：self-improving-agent 已部署，`.learnings/` 记录错误

**自愈流程**：
1. 心跳读取 `.learnings/ERRORS.md` 的 pending 条目
2. 如是已知可修复模式 → 自动修复
3. 修复后更新状态

**已知自愈模式**：
- skill路径错误 → 修正路径
- 脚本编码错误 → qclaw-text-file 重写
- 命令路径变化 → 更新 TOOLS.md

**待实现**：LLM判断自动修复更多未知错误模式

---

### 维度4：行为策略动态调整 🚧 待实现

**目标**：根据用户反馈自动调整行为策略

**实现路径**：
1. 记录用户每次纠正（correction）时的行为模式
2. 生成用户偏好 profile（存 `.state/evolution/user-preferences.json`）
3. 下次同类场景自动应用偏好

**数据来源**：
- `.learnings/LEARNINGS.md` 的 correction 条目
- session 中的用户纠正信号

---

### 维度5：技能健康度监测 🚧 待实现

**目标**：跟踪 skill 使用频率，识别废弃技能

**指标**：
- skill 最后使用时间
- skill 在挖掘报告中的出现频率
- 用户显式抱怨/纠正 skill 输出

**动作**：
- 使用频率<1次/月 → 提示用户是否卸载
- 用户抱怨 → 自动复盘并生成修复提案

---

## 与其他 Skills 的协同

| 组合 | 进化效果 |
|------|---------|
| lobster-evolution + session-miner | 观察层自动化 |
| lobster-evolution + skill-proposer | 判断层自动化 |
| lobster-evolution + self-improving | 自愈层自动化 |
| lobster-evolution + skill-evolution-manager | 记忆层自动化 |
| lobster-evolution + basal-ganglia-memory | 习惯层自动化（长期偏好）|

---

## HEARTBEAT 集成

在心跳中执行，步骤：

1. **Session挖掘**：运行 `session-miner.py 7`
2. **提案生成**：如有新高频模式 → 运行 `skill-proposer.py`
3. **提案推送**：如有 high 优先级提案 → 主动告知用户
4. **自愈检查**：读取 `.learnings/ERRORS.md` → 自动修复已知模式
5. **更新状态**：写 `heartbeat-state.json`

---

## 进化状态追踪

文件：`.state/evolution/evolution-state.json`

```json
{
  "lastMining": "2026-04-03",
  "lastProposal": "2026-04-03",
  "activeProposals": [
    {"domain": "节气", "priority": "high", "status": "已有chinese-name-lookup覆盖"}
  ],
  "resolvedFeedback": 3,
  "selfHealedErrors": 0
}
```

---

## 安全边界

**允许**（文件级操作）：
- 读写 `.state/evolution/` 目录
- 读写 `.learnings/` 目录
- 读写 `memory/` 目录
- 调用 `skillhub_install`

**需审批**（高风险操作）：
- 创建新 Skill（调用 skill-creator）
- 修改核心配置（SOUL.md, IDENTITY.md）
- 删除 Skill
- 修改 `MEMORY.md`

**禁止**：
- 修改模型权重
- 修改 OpenClaw 核心代码
- 绕过审批机制

---

## 使用示例

### 龙虾，我需要什么新技能？

```
我：帮我看看最近有什么进化信号
龙虾：
🦞 进化诊断报告（2026-04-03）

🔴 高频信号：
- 节气 ×73（7天）→ chinese-name-lookup 已覆盖 ✅
- high_freq_query ×多种 → 子Session代码优化
  - "do not busy-poll" ×12
  - "month" ×7

🟡 待观察：
- 命理 ×10（中等，建议观察2周）
- 搜索 ×14（通用能力，已覆盖）

💡 技能提案：
- 暂无高优先级新提案

✅ 系统状态：已部署维度1+2
🚧 待部署：维度3(自愈增强)+4(用户偏好)+5(技能健康度)
```
