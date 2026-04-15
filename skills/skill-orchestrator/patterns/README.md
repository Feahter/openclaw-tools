# Skills 组合模式库

> 已知高效组合的固化模板

## 格式

```yaml
name: pattern-name
description: 组合做什么
skills:
  - skill-a
  - skill-b
trigger: 触发条件
emergence: 涌现描述
metrics:
  frequency: 使用频率
  value_add: 价值增量
```

## 规则

1. 高频组合（≥3次使用）可提交
2. 必须包含 emergence 说明
3. 价值需高于各 skill 独立使用之和

## 维护

- 来源1：session-miner 自动提取
- 来源2：用户手动添加
- 每周汇总更新
