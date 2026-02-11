---
name: auto-knowledge-acquisition
description: 研究和发现 GitHub 高质量项目，记录学习笔记。不自动生成 Skills，仅提供研究数据和创建建议。
triggers:
  - "研究GitHub项目"
  - "发现新工具"
  - "知识探索"
---

# 自动知识获取系统（研究模式）

**设计目标**：发现和研究高质量项目，记录笔记供后续使用。

**不再自动生成 Skills**。发现高质量项目后，建议使用更专用的 Skill（如 `skill-from-github`）来创建可用的 Skill。

## 工作模式

```
心跳触发 → 搜索 → 评分 → 高分? → 是 → 记录笔记 + 标记"待创建"
                           ↓ 否
                      记录学习笔记
```

## 配置

`~/.openclaw/config/auto-knowledge.yaml`:

```yaml
search:
  keywords: [...]  # 搜索关键词池
  rotation: "round_robin"

quality_thresholds:
  min_score: 4.0        # 高分阈值（原来是3.5）
  min_stars: 500        # 至少500 stars（原来是100）
  max_age_months: 12    # 项目年龄限制

generation_rules:
  auto_generate: false   # 关闭自动生成！
  suggest_on_high_score: true  # 高分时建议创建
```

## 决策规则

| 场景 | 自动处理 |
|------|---------|
| 项目分数 < 4.0 | 记录学习笔记 |
| 项目分数 >= 4.0 | 记录笔记 + 标记"建议创建 Skill" |
| 项目有完整脚本 | 标记"可完整实现" |
| 项目是 example/模板 | 跳过 |

## 输出

研究结果保存到 `memory/auto-knowledge-notes/`：

```
memory/auto-knowledge-notes/
├── 2026-02/
│   ├── cli-tool-enhancer.md    # 笔记
│   └── data-validator.md        # 笔记
└── suggestions.json             # 待创建建议列表
```

## 与其他 Skills 的配合

| 场景 | 使用 Skill |
|------|-----------|
| 发现有趣的项目 | `auto-knowledge-acquisition` (只做研究) |
| 需要创建 Skill | `skill-from-github` (从项目创建完整 Skill) |
| 从零设计 Skill | `skill-creator` (手动设计) |
| 基于专家方法论 | `skill-from-masters` (专家方法) |

---

*本系统专注于研究和发现，不直接生成 Skills*
*高质量项目建议使用 `skill-from-github` 创建完整实现*
