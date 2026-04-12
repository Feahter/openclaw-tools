# Errors

Command failures, exceptions, and tool errors captured during development.

**Area tags**: frontend | backend | infra | tests | docs | config
**Statuses**: pending | in_progress | resolved | wont_fix | promoted

## Status Definitions

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Actively being investigated |
| `resolved` | Issue fixed or worked around |
| `wont_fix` | Decided not to address (reason in Resolution) |
| `promoted` | Elevated to workspace files or documented as known limitation |

---

## 禁止行为（Prohibited Behaviors）

**原则**：禁止行为比最佳实践更容易被执行——明确禁止比模糊原则更有效。

| 禁止行为 | 正确做法 |
|---------|---------|
| ❌ 发现错误后立刻修复，不分析原因 | ✅ 先诊断原因，再提出方案 |
| ❌ 改完代码后不验证直接交付 | ✅ 改完后跑探针验证，再报告 |
| ❌ 读不懂的代码直接跳过或猜测 | ✅ 探针定位，逐段理解后再操作 |
| ❌ 多轮对话中冗余废话稀释关键信息 | ✅ 一次性给完背景，不要废话 |
| ❌ 修改了文件后不同步更新相关文档 | ✅ 改动完成后立即同步相关文档 |
| ❌ 未确认修改范围就执行批量操作 | ✅ 先 `git diff --stat` 列出影响范围，确认后再执行 |
| ❌ 在异步回调中先清除共享状态再使用 | ✅ 先保存到局部变量，再清 nil |

---


## [2026-04-11] session-miner.py _load_checkpoint NameError

**文件**: `scripts/evolution/session-miner.py`

**错误**: 
```
NameError: name '_load_checkpoint' is not defined
  at extract_from_lcm() line 108
```

**原因**: 函数定义顺序问题，`extract_from_lcm` 调用了后面定义的 `_load_checkpoint`

**状态**: pending

**修复方向**: 将 `_load_checkpoint` 定义移到 `extract_from_lcm` 之前
