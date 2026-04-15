---
name: task-workflow
description: Standardized Planning + Subagent + Progress Report workflow for complex tasks
author: Galatea
version: 1.0.0
---

# Task Execution Workflow

标准化任务执行流程，适用于复杂多步骤任务（>5 tool calls）。

## 触发条件

当任务满足以下任一条件时，**必须**使用此工作流：
- 预计需要 >5 个 tool calls
- 涉及多个子任务或并行处理
- 执行时间 >10 分钟
- 需要 subagent 协作

## 工作流程

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: Planning (2-3 min)                              │
│  • 创建 task_plan.md                                     │
│  • 拆分任务为可并行批次                                    │
│  • 预估每批次时间                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 2: Subagent Dispatch (并行)                         │
│  • 每批次派独立 subagent                                  │
│  • 设置 timeout 和 label                                 │
│  • Main agent 保持响应                                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 3: Progress Tracking                               │
│  • 每 5 分钟自动汇报                                      │
│  • 更新 task_plan.md 进度                                │
│  • 异常时立即通知                                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 4: Integration & Report (3-5 min)                  │
│  • 收集 subagent 结果                                     │
│  • 整合为统一报告                                         │
│  • 更新 MEMORY.md                                         │
└─────────────────────────────────────────────────────────┘
```

## 工具使用规范

### Planning
```bash
# 使用 planning-with-files skill
bash ~/.openclaw/workspace/skills/planning-with-files/scripts/init-session.sh
```

### Subagent Dispatch
```javascript
// 并行派多个 subagent
const tasks = [
  { label: "research-part1", task: "..." },
  { label: "research-part2", task: "..." }
];

for (const t of tasks) {
  sessions_spawn({
    label: t.label,
    task: t.task,
    timeoutSeconds: 300
  });
}
```

### Progress Reporting
```javascript
// 设置定时汇报 cron
cron.add({
  name: `progress-${taskId}`,
  schedule: { kind: "every", everyMs: 300000 }, // 5分钟
  payload: {
    kind: "systemEvent",
    text: "📊 进度检查 - 读取 task_plan.md 并汇报"
  }
});
```

## Task Plan 模板

```markdown
# Task Plan - [任务名称]

**启动时间**: YYYY-MM-DD HH:MM  
**预计时长**: XX 分钟  
**汇报间隔**: 5 分钟

---

## 批次清单

| 批次 | 任务 | 负责 | 预估时间 | 状态 |
|------|------|------|----------|------|
| 1 | [具体任务] | subagent-1 | 5min | ⏳ |
| 2 | [具体任务] | subagent-2 | 5min | ⏳ |
| 3 | [具体任务] | galatea | 5min | ⏳ |

---

## 进度追踪

| 时间 | 批次 | 状态 | 备注 |
|------|------|------|------|
| HH:MM | 1 | ✅ | 完成 |
| HH:MM | 2 | 🔄 | 进行中 |

---

## 风险与阻塞

- [ ] 风险1: [描述] → 应对方案: [方案]
- [ ] 阻塞点: [描述] → 需要 Master 决策

---

*最后更新: HH:MM*
```

## 汇报模板

### 定时汇报消息
```
📊 进度汇报 #[N] - HH:MM

**已完成**: [X/Y] 批次
- ✅ 批次1: [简述]
- 🔄 批次2: [进度%]
- ⏳ 批次3: 等待中

**下一步**: [计划]
**预计完成**: [时间]

[如有异常，在此标注]
```

### 完成汇报消息
```
✅ 任务完成 - HH:MM

**总耗时**: [X] 分钟
**完成批次**: [Y/Z]

**关键成果**:
- [成果1]
- [成果2]

**生成文件**:
- [文件1]
- [文件2]

**待办**:
- [ ] [后续任务]
```

## 异常处理

| 场景 | 处理方式 |
|------|----------|
| Subagent 超时 | 自动重试1次，仍失败则切换为 Galatea 执行 |
| API 限流 | 指数退避（1s → 2s → 4s → 8s） |
| 任务阻塞 | 立即发送消息通知 Master，等待决策 |
| 进度落后 | 调整批次优先级，先完成核心任务 |

## 示例: 复杂调研任务

**任务**: "调研 A、B、C 三个方案的可行性"

**执行**:
1. **Planning** (2min): 创建 task_plan.md，拆分为 3 个并行调研批次
2. **Dispatch** (1min): 同时派 3 个 subagent，各负责一个方案
3. **Tracking** (15min): 每 5 分钟汇报进度
4. **Integration** (3min): 汇总 3 份报告，生成对比分析

**总耗时**: ~21 分钟（vs 串行 ~45 分钟）

## 注意事项

1. **不要过度拆分**: 批次粒度以 5-10 分钟为宜
2. **保持响应**: Main agent 始终在线，秒回简单询问
3. **及时同步**: 有重要发现立即汇报，不等待定时汇报
4. **文档优先**: 所有成果必须落盘，不依赖内存

---

*Workflow Version: 1.0.0*  
*Last Updated: 2026-02-10*
