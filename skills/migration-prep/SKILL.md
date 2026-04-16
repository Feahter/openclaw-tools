# migration-prep

## 描述

OpenClaw → Hermes 迁移风险评估工具。分析 `~/.openclaw/` 目录结构，识别迁移风险，生成检查清单。在你决定是否迁移 Hermes 前必读。

## 核心文档

- `MIGRATION-CHECKLIST.md` — 完整迁移清单和已知 bug
- `ANALYSIS.md` — 目录结构分析

## 主要功能

1. **目录结构分析** — 每个文件的用途、是否含 secrets、是否可迁移
2. **风险分级** — ✅ SAFEST / ⚠️ IMPORTANT / 🔒 DANGEROUS
3. **已知 Hermes 迁移 bug** — 5 个 open issues 的 workaround
4. **迁移前检查清单** — 步骤化指引

## 关键风险

| 风险 | 描述 | 影响 |
|------|------|------|
| `openclaw.json` 被 orphan | Hermes migrate 不复制 config | Gateway 启动后无配置 |
| `lcm.db` 被静默移走 | 1.2GB 记忆数据库丢失 | Agent 失去所有历史记忆 |
| `hermes claw cleanup` 炸掉运行中的 Gateway | 正在运行的 OpenClaw 被改名 | 24 小时无感知降级 |
| `openclaw doctor` 删插件配置 | doctor 发现不一致就清空 | 15 个 agent defaults 全丢 |

## 建议

**现在不要迁移**，理由：
1. 5 个 critical migration bugs 还 open（issues #5190, #5191, #8596, #8901）
2. 你的 176 个 skills 需要手动重建
3. LCM 数据库无法迁移
4. 飞书/微信插件在 Hermes 上需要社区版

**如果坚持要试：**
```bash
# 1. 永远先 dry-run
hermes claw migrate --dry-run

# 2. 永远先全量备份
cp -R ~/.openclaw ~/OPENCLAW_BACKUP_$(date +%Y%m%d)

# 3. 永远不要在 Gateway 运行时执行 cleanup
```
