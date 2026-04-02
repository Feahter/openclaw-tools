# Coding-Agent Learnings

*每次执行后追加记录*

---

## 验证过的有效模式

### Claude Code -p 非交互模式
```bash
claude -p "task description" \
  --output-format stream-json \
  --no-session-persistence \
  --permission-mode bypassPermissions
```
- ✅ 单次任务，不需要 TTY
- ✅ 输出到 stdout，可以重定向
- ⚠️ 需要明确指定 `--permission-mode bypassPermissions` 否则会卡住

### 工作目录隔离
- `cd $WORKDIR && claude -p ...` — 进程在正确目录启动
- 绝对路径隔离：不同项目的 agent 不会互相干扰

---

## 踩过的坑

### Claude Code -p 模式没有 TTY 时的权限问题
- **现象**：`Permission to use tool Bash is required` 卡住
- **解法**：`--permission-mode bypassPermissions`
- **注意**：仅限可信目录（`/tmp`、`~/project/`）

### JSON 输出格式不稳定
- `--output-format json` 有时返回的不是合法 JSON（夹杂 ANSI color codes）
- **解法**：用 `--output-format text` 或管道处理 ANSI

### opencode run 非交互模式
- `opencode run "task"` — 有效，但需要检查版本
- 当前版本 1.3.0，测试可用

---

## 待验证

- [ ] OpenCode 非交互模式 vs Claude Code 的质量对比
- [ ] 多模型路由：何时用 Claude，何时用 OpenCode
- [ ] 子 session 的上下文保留效果

---

## 使用统计

| 日期 | Session数 | Agent | 任务类型 | 状态 |
|------|---------|-------|---------|------|
