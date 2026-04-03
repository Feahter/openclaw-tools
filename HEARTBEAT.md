# HEARTBEAT.md - 心跳任务清单

*这是实际执行的心跳任务列表*

---

## 默认行为

收到心跳轮询时，别只回 `HEARTBEAT_OK`。用好这段时间。

**触发条件**：
- 消息匹配配置的心跳 prompt
- `HEARTBEAT.md` 存在则读取并严格执行

---

## Heartbeat vs Cron：什么时候用哪个

**用心跳：**
- 多个检查可以批量处理（邮箱 + 日历 + 通知）
- 需要对话上下文
- 时间可以稍微浮动（~30分钟误差ok）
- 减少 API 调用

**用 cron：**
- 精确时间很重要（周一早上9点整）
- 任务需要独立于主会话
- 想用不同的模型或思考级别
- 一次性提醒
- 输出直接发到渠道，不经过主会话

**建议**：把相似的定期检查合并到 `HEARTBEAT.md`，别建一堆 cron 任务。

---

## 检查什么（每天 2-4 次轮换）

- 📧 **邮箱** — 有急件吗？
- 📅 **日历** — 未来 24-48 小时有事吗？
- 🐦 **社交@提及**
- 🌤️ **天气** — 主人可能出门吗？

---

## 什么时候主动联系

- 重要邮件到了
- 日历事件快到了（<2小时）
- 发现了有趣的东西
- 超过 8 小时没说话

---

## 什么时候安静（HEARTBEAT_OK）

- 深夜（23:00-08:00），除非紧急
- 主人明显很忙
- 没什么新情况
- 30 分钟内刚检查过

---

## 主动可以做的事（不需要问）

- 读取整理 memory 文件
- 检查项目状态（git status）— **结合 timestamp 判断，无变化不重复报**
- 更新文档
- 提交推送自己的改动
- **检查并更新 MEMORY.md**（见下文）

---

## 🔄 记忆维护（心跳期间）

每隔几天用心跳做：
1. 浏览最近的 `memory/YYYY-MM-DD.md`
2. 挑出值得长期记住的事
3. 更新 `MEMORY.md`
4. 删除过时的内容

目标是：**有用但不烦人**。

---

## 🧠 Skills 进化审计（每 7 天）

*在 heartbeat-state.json 记录 `lastChecks.skillsAudit`，每 7 天触发一次*

**检查内容**：
1. 列出 skills 目录最近改动的 skill（`find ~/.openclaw/workspace/skills -name SKILL.md -mtime -7`）
2. 如果有新增/修改的 skill → 追加记录到 `memory/evolution/skill-log.md`
3. 检查 skill-log.md 最近条目，如果距今 > 30 天 → 提醒用户做季度内省

**洞察捕获原则**：
- 不记流水账，只记**违反直觉的发现**
- 格式：背景 → 改动 → 洞察 → 下次注意
- 触发条件：**新建 skill**、**重大重构**、**踩坑修复**、**认知升级**

---

## 🗑️ 回收站清理（每月一次）

*在 heartbeat-state.json 记录 `lastChecks.trashCleanup`，每月触发一次*

**任务**：
```bash
find ~/.openclaw/workspace/.trash -maxdepth 1 -type d -mtime +30
```
1. 检查是否有超过 30 天的文件
2. 有 → 汇报文件名和大小，询问是否清理
3. 无 → 安静

---

## 📜 GitHub 脚本收集（每小时）

**任务**：收集 GitHub 上好用的脚本，存到 `scripts/` 目录

**规则**：
- 每次心跳最多收集 **3 个**脚本
- 贵精不贵多，只收集有价值的
- 采集后立即在 `scripts/README.md` 更新说明

**工作流**：
```
1. 用 gh search 搜索高质量脚本
2. 筛选标准：stars > 100, 近期更新, 有清晰 README
3. 下载脚本到 scripts/
4. 更新 scripts/README.md（脚本名称 + 作用 + 来源链接）
```

**搜索关键词轮换**：
```
- "useful script" "stars:>100" language:python
- "CLI tool" "stars:>200" 
- "automation script" "stars:>100" 
- "devops script" "stars:>150"
- "productivity script" "stars:>100"
```

**状态追踪**：在 `memory/heartbeat-state.json` 的 `lastChecks.scriptCollection` 记录时间戳

**注意**：此任务适合 cron 触发，不依赖消息。如果 OpenClaw 支持定时心跳，配置每小时一次；否则在有外部触发时执行。

---

## 🔍 Session 模式挖掘（每日心跳执行）

*在 heartbeat-state.json 记录 `lastChecks.sessionMining`，每天首次心跳触发*

**执行逻辑**：
1. 运行 `~/.openclaw/workspace/scripts/evolution/session-miner.py`（最近7天）
2. 读取 `.state/evolution/daily-mining.md`，与上周对比
3. 如发现新的高频模式（出现次数突增 ≥3）→ 生成**技能提案**
4. 输出：本周新模式 + 技能提案（如有）

**技能提案触发条件**：
- 某高频短Query（≤15字）连续出现 ≥5次
- 或某意图领域词（如"八字"、"新闻"、"天气"）连续出现 ≥10次

**技能提案格式**：
```
🎯 新技能候选：<skill-name>
- 触发原因：<具体Query示例>
- 出现频次：<N>次/7天
- 建议：调用 skillhub_install install_skill <name>
```

---

## 🩺 错误自愈循环（心跳执行）

*检测 .learnings/ERRORS.md 中的 pending 条目，尝试自动修复*

**自愈流程**：
1. 读取 `.learnings/ERRORS.md` 的 pending 条目
2. 如是已知可修复模式（如路径错误、参数错误）→ 自动修复
3. 修复后更新状态为 resolved
4. 如是未知错误 → 保持 pending，提示用户

**已知自愈模式**：
- skill 路径错误 → 更新 .learnings/ERRORS.md + 修正路径
- 脚本编码错误 → 用 qclaw-text-file 重写
- 命令路径变化 → 更新 TOOLS.md

---

## 状态追踪

在 `memory/heartbeat-state.json` 记录检查状态：

```json
{
  "lastChecks": {
    "email": 1703275200,
    "calendar": 1703260800,
    "weather": null,
    "gitStatus": 1703275200,
    "memoryUpdate": "2026-03-10"
  }
}
```

---

## 🔍 重大操作前：先打探针

执行以下操作之前，**先跑探针验证上下文**，确认目标正确再执行：

| 操作类型 | 探针动作 |
|---------|---------|
| 改文件之前 | `git status` + `grep` 定位目标路径 |
| 批量删除/移动 | 先列出受影响文件（`git ls-files` / `find`）|
| git commit / push | 先 `git diff --stat` 确认改动范围 |
| 读他人代码 | 先输出目标文件的绝对路径 + 关键函数名 |
| 执行脚本 | 先 dry-run 或 `-n` 模拟模式 |

**原理**：极简单的探针任务强制 AI 把注意力集中在"定位"，成功后输出变成后续的"强上下文锚点"，避免在错误位置写入。

---

## ⚡ 输出去重优化

### 原则
- **合并检查**：一个命令能搞定的不拆成多个
- **只报变化**：无变化时不重复输出
- **状态记忆**：用 timestamp 判断是否需要重复检查
- **精简结论**：用一句总结替代详细罗列

### 实践
```
❌ 重复: git status → 发现变化 → cd 到目录 → git status 再次确认
✅ 优化: 一次 git status 获取全部，结合 timestamp 判断

❌ 重复: 检查 A → 输出 A → 检查 B → 输出 B → 总结
✅ 优化: 先收集全部 → 判断是否有必要输出 → 简洁总结

❌ 重复: 每天报 "项目正常运行"
✅ 优化: 有变化才报，无变化则 HEARTBEAT_OK
```

### 判断标准
| 情况 | 输出 |
|------|------|
| 有实质变化 | 简洁描述变化内容 |
| 无变化 | HEARTBEAT_OK |
| 需要提醒 | 单独提醒事项 |
