# agent-commander

Agent 会话管理技能包，封装 OpenClaw 的多会话管理能力。

## 功能

- 📊 **会话状态监控** - 实时查看上下文使用率
- 🚀 **子会话管理** - 创建、监控、销毁会话
- 📨 **跨会话通信** - 主从会话消息传递
- 🔄 **历史追溯** - 查看任意会话的对话历史
- 📋 **批量操作** - 并行启动多个代理任务

## 安装

```bash
# 方式1: 复制到 Skills 目录
cp -r agent-commander ~/.openclaw/workspace/skills/

# 方式2: 使用 clawdhub（如果已发布）
clawdhub install agent-commander
```

## 使用

在 OpenClaw 对话中直接使用工具命令，或参考：
- `QUICKREF.md` - 快速参考
- `SKILL.md` - 完整文档

## 文件结构

```
agent-commander/
├── SKILL.md          # 完整技能文档
├── QUICKREF.md       # 快速参考卡片
└── scripts/
    └── commander.sh  # CLI 辅助脚本（可选）
```
