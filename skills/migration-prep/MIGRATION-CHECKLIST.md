# Migration Prep — OpenClaw → Hermes 迁移风险评估

## 目标

分析 `~/.openclaw/` 完整目录结构，识别迁移风险，为未来可能的 Hermes 迁移提供完整清单。

## 目录结构分析

```
~/.openclaw/
├── openclaw.json              ← ⚠️ CRITICAL：Gateway 配置，含所有 channel credentials
├── credentials/               ← 🔒 DANGEROUS：包含 secrets，不能直接迁移
│   ├── github.json
│   └── ...
├── identity/                  ← 🔒 DANGEROUS：身份凭证
├── extensions/                ← ⚠️ 需要重建：第三方插件（Hindsight, Lossless Claw 等）
├── lcm.db                      ← 🔒 BINARY：LCM 数据库，无法直接迁移
├── lcm.db-shm
├── lcm.db-wal
├── lcm-files/                 ← 🔒 BINARY：LCM 引用的文件
├── memory/                     ← ⚠️ IMPORTANT：memory-core 数据库
│   └── main.sqlite
├── data/                       ← ⚠️ IMPORTANT：agent-tasks.log 等运行时数据
├── logs/                       ← 可选：历史日志
├── workspace/                  ← ✅ SAFEST：纯文本文件，最适合迁移
│   ├── SOUL.md
│   ├── IDENTITY.md
│   ├── USER.md
│   ├── MEMORY.md
│   ├── AGENTS.md
│   ├── TOOLS.md
│   ├── HEARTBEAT.md
│   ├── skills/
│   └── memory/
└── .state/                     ← ⚠️ 运行时状态，可跳过
```

## 文件分类清单

### ✅ SAFEST — 直接 copy

| 文件 | 说明 | 风险 |
|------|------|------|
| workspace/SOUL.md | Agent persona | 无 |
| workspace/IDENTITY.md | Agent 身份 | 无 |
| workspace/USER.md | 用户信息 | 无 |
| workspace/MEMORY.md | 长期记忆 | 无 |
| workspace/AGENTS.md | Agent 配置 | 无 |
| workspace/TOOLS.md | 工具配置 | 无 |
| workspace/HEARTBEAT.md | 心跳配置 | 无 |
| workspace/skills/ | Skills 目录 | 无 |
| workspace/memory/ | 每日记忆 | 无 |
| workspace/.state/ | 状态文件 | 低 |

### ⚠️ IMPORTANT — 需要手动验证

| 文件 | 说明 | 风险 |
|------|------|------|
| openclaw.json | Gateway 配置 | 中：含 token，需提取后迁移 |
| extensions/ | 插件配置 | 中：需在 Hermes 重新安装 |
| memory/main.sqlite | 记忆数据库 | 中：schema 可能不兼容 |
| data/agent-tasks.log | 任务日志 | 低 |

### 🔒 DANGEROUS — 禁止直接迁移

| 文件 | 说明 | 风险 |
|------|------|------|
| credentials/ | 所有密钥 | 高：直接迁移会暴露 token |
| identity/ | 身份凭证 | 高：同上 |
| lcm.db | LCM 数据库 | 高：二进制，迁移会损坏 |
| lcm.db-shm | LCM 共享内存 | 高：同上 |
| lcm.db-wal | LCM WAL | 高：同上 |
| lcm-files/ | LCM 文件缓存 | 高：路径依赖 |

## 已知 Hermes 迁移 bug（需规避）

1. **openclaw.json 被 orphan**：migrate 不复制 config 文件
   - 修复：手动 `cp ~/.openclaw.pre-migration-*/openclaw.json ~/.openclaw/openclaw.json`

2. **Slack token 丢失**：`~/.hermes/.env` 不会自动写入
   - 修复：从 openclaw.json 提取 `channels.slack.accounts.*.botToken` → `SLACK_BOT_TOKEN`

3. **lcm.db 被移走但不报错**：runtime state 被 move 但 migration report 说"跳过"
   - 修复：迁移前备份整个 `~/.openclaw/` 到外部存储

4. **`hermes claw cleanup` 会炸掉正在运行的 OpenClaw Gateway**
   - 修复：**永远不要在 OpenClaw Gateway 运行时执行 cleanup**

5. **`openclaw doctor` 会静默删除插件配置**
   - 修复：迁移后**不要运行** openclaw doctor

## 迁移前检查清单

```bash
# 1. 确认 OpenClaw Gateway 已停止
openclaw gateway stop

# 2. 全量备份（到外部存储，不放在 ~/.openclaw/ 下）
cp -R ~/.openclaw ~/OPENCLAW_BACKUP_$(date +%Y%m%d)

# 3. 提取 secrets（只在离线环境）
jq '.channels.slack.accounts[0]' ~/.openclaw/openclaw.json

# 4. Dry-run 迁移
hermes claw migrate --dry-run

# 5. 迁移
hermes claw migrate

# 6. 验证 Hermes Gateway 能启动
hermes gateway start
hermes status

# 7. 手动恢复 critical 文件（Hermes migrate 会漏掉）
cp ~/OPENCLAW_BACKUP_*/openclaw.json ~/.openclaw/openclaw.json

# 8. 验证飞书/微信 channel 连通性
```

## 你的当前状态

- **Gateway 架构**：双 Gateway（QClaw 内置 28789 + npm 全局 18789）
- **Channel**：飞书（主要）+ 微信
- **Skills 数量**：176 个（⚠️ 迁移后会丢失，需要重新扫描）
- **内存系统**：memory-core + LCM（⚠️ LCM 数据库无法迁移）
- **自进化**：依赖 cron + skill-creator（⚠️ Hermes 有原生支持）

## 建议

1. **现在不要迁移** — 你的 skills 体系太复杂，等 Hermes 迁移工具更成熟
2. **先用 `hermes claw migrate --dry-run`** 了解会迁移什么
3. **等 fix**：issues #5190, #5191, #8596, #8901 都还是 open 状态
4. **备份优先**：任何迁移操作前，先 `cp -R ~/.openclaw ~/OPENCLAW_BACKUP_$(date +%Y%m%d)`
