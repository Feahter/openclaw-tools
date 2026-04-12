---
name: autonomous-skill-creator
description: >
  Hermes 风格自动 Skill 创建引擎——让龙虾主动发现值得固化的任务，
  自动生成 SKILL.md 草稿，并以 nudge 形式推送给用户审批。
  对标 Hermes Agent 的 on-demand skill creation 机制。
triggers:
  - keywords:
      - "自动创建skill"
      - "autonomous skill"
      - "自动生成skill"
      - "nudge"
    load: true
    priority: high
---

# 🦞 Autonomous Skill Creator

对标 Hermes Agent：复杂任务后自动检测 → 生成 SKILL.md → Nudge 推送

## 组件

| 脚本 | 职责 |
|------|------|
| complexity_detector.py | 检测候选（5+工具/3+步骤/3+次重复） |
| skill_generator.py | 从候选生成 SKILL.md 草稿 |
| nudge_engine.py | 达到 3 个高优先级触发飞书推送 |

## 触发条件

- 调用了 5+ 个不同工具
- 任务跨越 3+ 步骤
- 同一类型问题出现 3+ 次
- 用户显式说"记住这个"
- session-miner 高频模式 ≥5 次/周