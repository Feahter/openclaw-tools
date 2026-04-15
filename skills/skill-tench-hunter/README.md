# skill-tench-hunter

技术研究猎手。给定主题或链接，从多源并行抓取到结构化产出的完整管道。

## 来源

从 WebMCP 研究过程（2026-03-20）提取：
- 用户给链接 → 并行抓取 → GitHub 搜索 → 合成报告 → 归档推送

## 文件结构

```
skill-tench-hunter/
├── SKILL.md                 # 主文件（5阶段工作流 + 模板）
└── references/
    ├── templates.md        # 参考模板（GitHub Query、并行抓取、Checkpoints）
    └── examples/           # （可选）示例报告
```

## 工作流

```
Phase 1: 信息收集（并行）
  └─ 链接 + GitHub + 官方 Spec/Docs

Phase 2: 合成判断
  └─ 决定输出 1 份还是 2 份

Phase 3: 技术研究报告
  └─ 13 个 section 标准模板

Phase 4: 最佳实践指南（如需要）
  └─ 6 个 section 标准模板

Phase 5: Git 归档
  └─ reports/ → commit → push
```

## 使用

触发后直接读 SKILL.md，按 5 个 Phase 执行。
