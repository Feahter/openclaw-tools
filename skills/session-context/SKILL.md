---
name: session-context
description: |
  显示当前 OpenClaw Session 的上下文使用状况。
  
  触发场景：
  - 用户问"上下文用了多少"、"session 状态"、"/context"
  - 用户想了解当前对话消耗了多少 token、还有多少剩余
  - 用户想查看当前加载了哪些 Skills、内存使用情况
  - 用户问"我的 session 还能输入多少"

  等价于 Claude Code 的 /context 命令。
---

# Session Context Skill

## 功能

生成当前 Session 的上下文使用报告，包含：
1. Token 使用估算（总 context、已用、剩余）
2. 当前加载的 Skills 列表及来源
3. 关键配置参数（compaction 模式、maxConcurrent、memorySearch 等）
4. 上下文压缩状态

## 执行步骤

### Step 1: 获取 Session 状态

执行 `session_status` 工具，获取当前 session 的 token 使用数据。

### Step 2: 获取配置参数

执行以下命令获取关键配置：

```bash
openclaw config get agents.defaults.compaction
openclaw config get agents.defaults.maxConcurrent
openclaw config get agents.defaults.memorySearch
openclaw config get agents.defaults.contextPruning
openclaw config get models
```

### Step 3: 获取 Skills 列表

```bash
openclaw skills list 2>&1 | grep -v "^\[plugins\]"
```

### Step 4: 格式化输出

生成如下格式的报告：

```
## Session Context Report

⏱ Session 运行时长: X小时 X分钟
📊 Token 使用: ~XXXk / XXXk (XX%)

### 配置参数
| 参数 | 当前值 | 说明 |
|------|--------|------|
| compaction | balanced | 上下文压缩频率 |
| maxConcurrent | 8 | 最大并发数 |
| memorySearch | enabled | 记忆搜索 |
| contextPruning.ttl | 30m | 热上下文保留时间 |

### Skills 加载状态
[列出所有已加载的 skills 及来源]

### 上下文状态
- Memory Buffer: XXXk
- Free Space: XXXk (XX%)
```

## 输出要求

- 报告用中文输出
- 包含实际数据，无数据则标注"未知"
- 如发现配置异常（如 memorySearch disabled），在报告中以 ⚠️ 提示
- 总 token 估算以 session_status 返回的数值为准

## 触发方式

用户发送以下内容时触发此 skill：
- "/context"
- "上下文状态"
- "session 用了多少"
- "token 剩余"
- "我的 session 还能输入多少"
- 任何询问当前对话上下文消耗的问题
