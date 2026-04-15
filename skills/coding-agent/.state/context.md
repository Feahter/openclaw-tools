# Coding-Agent 执行管道状态

**最后更新**: 2026-04-02

## 管道架构

```
pipeline/
├── run-task.sh        # 启动编程任务，返回 session_id
├── check-progress.sh # 检查会话进度，读取日志尾
├── collect-results.sh # 收集完成会话的 git diff + 输出
├── verify.sh         # 验证产出（文件变化/测试/lint）
└── list-sessions.sh   # 列出所有会话

.state/
├── progress/         # 每个会话的 JSON 状态文件
├── results/          # collect 后生成的完整报告
├── logs/             # 每个会话的标准输出日志
└── pids/             # 进程 PID 文件
```

## Session 状态机

```
pending → running → completed
                    ↘ failed
```

## 当前会话

（无活跃会话）

## 已知问题

- [ ] Claude Code CLI 可能未安装（需要 `claude` 命令）
- [ ] Codex CLI 需要配置 API key
- [ ] 无自动重试机制

## 依赖检查

```bash
# Claude Code
command -v claude && claude --version

# Codex CLI
command -v codex && codex --version

# opencode
command -v opencode && opencode --version
```
