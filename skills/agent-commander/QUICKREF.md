# Agent 指挥官 - 速查卡

## 🎯 核心场景

| 场景 | 解决方案 |
|------|----------|
| 上下文快满了 | → 检查 `session_status` → 建议新会话 |
| 需要并行任务 | → `sessions_spawn` 创建子会话 |
| 跨会话协作 | → `sessions_send` 发送消息 |
| 回顾之前对话 | → `sessions_history` 查看历史 |

## ⌨️ 常用命令速查

### 在 OpenClaw 中直接用
```
/status                    # 查看当前状态
/sessions list             # 列出所有会话
/sessions history <key>    # 查看会话历史
/sessions send <key> "msg" # 发送消息
/sessions spawn --task "..." --label "xxx"  # 创建子会话
```

### 上下文监控
```
# 检查当前上下文
session_status

# 解读输出
📚 Context: 14k/200k (7%)  ← 当前用了 7%，还很充裕
📚 Context: 150k/200k (75%) ← 超过 75%，建议新会话
📚 Context: 190k/200k (95%) ← 快满了，强制新会话
```

## 🚀 快速上手

### 场景 1：上下文告警
```
你: 检查上下文
AI: 📚 Context: 165k/200k (82%)
    ⚠️ 建议开启新会话继续任务
    是否需要我帮你创建？
```

### 场景 2：并行任务
```
你: 帮我同时搜索 GitHub 和处理文档
AI: 
→ sessions_spawn --task "搜索 GitHub issues" --label "github-search"
→ sessions_spawn --task "处理本地文档" --label "doc-processor"
→ 等待完成，汇总结果
```

### 场景 3：传递上下文
```
你: 把这个任务交给子会话处理
AI: sessions_spawn --task "处理用户请求: ..." --label "task-xxx"
```

## 📊 阈值建议

| 使用率 | 动作 |
|--------|------|
| 0-50% | ✅ 正常 |
| 50-75% | 💬 可提醒 |
| 75-90% | ⚠️ 建议新会话 |
| 90%+ | 🔴 必须新会话 |

## 🔗 相关文件

- `SKILL.md` - 完整文档
- `scripts/commander.sh` - CLI 辅助脚本
