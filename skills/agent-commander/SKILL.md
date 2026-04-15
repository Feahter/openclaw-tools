---
name: agent-commander
description: Agent 会话管理能力。用于创建子会话、发送消息、查看状态、管理多代理协作。触发场景：(1) 需要隔离上下文时创建新会话 (2) 向其他会话发送消息 (3) 查看/监控会话状态 (4) 多代理协作编排
---

# Agent 指挥官

## 快速使用

| 功能 | 命令 | 示例 |
|------|------|------|
| 查看会话状态 | `session_status` | `/status` |
| 列出所有会话 | `sessions_list` | 查看活跃会话 |
| 获取会话历史 | `sessions_history` | 查看对话记录 |
| 发送消息 | `sessions_send` | 向子会话发消息 |
| 创建子会话 | `sessions_spawn` | 启动新代理任务 |

## 核心工具

### 1. 会话状态
```bash
session_status [sessionKey]
```
查看当前或指定会话的：模型、Token 使用量、运行时间、成本。

**使用场景**：
- 监控上下文使用率（预防超出限制）
- 检查会话是否活跃
- 了解当前使用的模型

### 2. 会话列表
```bash
sessions_list [--activeMinutes 60] [--kinds main,sub-agent]
```
列出所有会话，支持过滤：
- `activeMinutes`: 过滤活跃时间窗口
- `kinds`: 筛选会话类型
- `limit`: 返回数量限制
- `messageLimit`: 每会话显示消息数

### 3. 会话历史
```bash
sessions_history <sessionKey> [--limit 50] [--includeTools false]
```
获取指定会话的消息历史，用于：
- 回顾之前对话
- 跨会话上下文传递
- 调试和排查

### 4. 发送消息
```bash
sessions_send <sessionKey> "消息内容" [--timeoutSeconds 30]
```
向指定会话发送消息，支持：
- 指定目标会话
- 设置响应超时
- 消息路由（跨会话协作）

### 5. 创建子会话
```bash
sessions_spawn --task "任务描述" --label "会话名称" [--model claude-sonnet-4] [--timeoutSeconds 3600]
```
启动新代理会话，用于：
- 隔离上下文的任务
- 并行处理多任务
- 专业化的代理（不同模型/Skills）

**参数**：
- `task`: 必填，任务描述
- `label`: 会话标识名
- `model`: 使用的模型（覆盖默认）
- `timeoutSeconds`: 超时时间
- `cleanup`: 结束后是否删除会话（delete/keep）

## 最佳实践

### 何时创建新会话

| 场景 | 操作 |
|------|------|
| 上下文 > 60% | 建议创建新会话 |
| 完全独立任务 | 必须新会话 |
| 需要不同模型 | 必须新会话 |
| 长期运行任务 | 推荐新会话 |
| 临时对话 | 可用当前会话 |

### 上下文监控策略

```javascript
// 检查时机
- 每 10 条消息检查一次
- 工具调用后检查
- 用户明确要求时

// 阈值动作
< 50%:  正常，无需提醒
50-75%: 轻微提示
75-90%: 强烈建议新会话
> 90%:  主动建议创建
```

### 多代理协作模式

**模式 1：主从协调**
```
主会话 → sessions_spawn(子任务) → 子会话执行 → sessions_send(结果)
```

**模式 2：流水线**
```
会话A → sessions_send(中间结果) → 会话B → sessions_send(输出)
```

**模式 3：监控**
```
主会话定期 → sessions_list → sessions_history → 监控状态
```

## 常见问题

**Q: 子会话如何与主会话通信？**
A: 使用 `sessions_send` 发送消息，主会话可随时获取子会话历史。

**Q: 子会话会共享主会话的上下文吗？**
A: 不会。每个会话有独立的上下文空间。

**Q: 如何选择 cleanup=delete？**
A: 临时任务用 delete，长期任务用 keep。

**Q: 能跨不同模型协作吗？**
A: 可以，在 `sessions_spawn` 时指定不同 model 即可。
