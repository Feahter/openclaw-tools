---
name: skill-tench-hunter
description: |
  技术研究猎手 — 从多源输入到结构化产出的完整管道。

  **触发条件（满足任一）：**
  - 用户说"研究下 XXX"、"深度分析 XXX"、"帮我了解 XXX 技术"
  - 用户给了链接（文章/GitHub/文档），要求"出一份技术报告"
  - 用户说"搜索下 XXX 的相关信息"、"调研 XXX 的生态"
  - 用户说"帮我写一个 XXX 的最佳实践"、"生成 XXX 技术指南"
  - 用户说"复盘这个过程，做成一个 skill"

  **不触发：**
  - 用户只给了一个简单问题，不需要深度调研 → 不触发
  - 用户问的是已有知识，不需要查找资料 → 不触发
  - 用户要的是纯代码实现，不是研究报告 → 不触发（用 coding-agent）
---

# 技术研究猎手 (skill-tench-hunter)

给定主题或链接，从多源并行抓取到结构化产出的完整管道。

## 工作流总览

```
用户输入（主题 + 可选链接）
  │
  ├─ 有链接 → 并行抓取所有链接内容
  │
  ├─ 无链接 → 搜索 GitHub + 官方文档
  │
  ↓
并行：内容抓取 + GitHub 项目 + 官方 Spec/Docs
  ↓
合成：判断需要几份输出
  ↓
产出：
  ├─ 技术研究报告（`reports/[topic]-research-YYYYMMDD.md`）
  └─ 最佳实践指南（如需要，`reports/[topic]-best-practices-YYYYMMDD.md`）
  ↓
Git 归档：git add → commit → push（如已有 remote）
```

---

## Phase 1：信息收集（并行）

### 1.1 链接内容抓取

对每个 URL 并行执行 `web_fetch`（`maxChars: 8000~10000`）：

```typescript
// 抓取策略
const strategies = {
  '公众号': { maxChars: 8000 },      // 公众号文章通常需要更多
  '掘金/知乎/CSDN': { maxChars: 10000 }, // 技术平台内容更丰富
  'GitHub README': { maxChars: 5000 },  // README 通常不长
  '官方文档': { maxChars: 8000 },      // 官方 Spec/Docs
  '通用网页': { maxChars: 6000 },       // 默认策略
};
```

### 1.2 GitHub 项目发现

```bash
# 搜索相关项目（并行多个 query）
gh search repos "$TOPIC" --sort=stars --limit=10
gh search repos "$TOPIC implementation" --sort=stars --limit=5
gh search repos "$TOPIC javascript OR typescript OR python" --sort=stars --limit=5

# 获取元数据
# jq '{name, full_name, description, stars: stargazers_count, language, updated_at}'
```

### 1.3 官方 Spec/Docs

```bash
# 尝试常见官方资源
# 官方 Spec: webmachinelearning.github.io/{topic}/
# 官方 GitHub: github.com/{org}/{topic}
# 官方文档: docs.{topic}.com
```

### 1.4 信息收集优先级

| 来源 | 优先级 | 说明 |
|------|--------|------|
| 用户提供的链接 | P0 | 直接相关，第一手资料 |
| GitHub 官方 Repo | P1 | 源码/Stars/Issues/原始 README |
| 官方 Spec/Docs | P1 | 最权威的技术定义 |
| 技术博客（掘金/知乎/CSDN）| P2 | 实战经验、中文解读 |
| 公众号文章 | P2 | 可能有较深的分析（但容易被微信墙）|

---

## Phase 2：合成判断

### 2.1 判断需要几份输出

```
产出类型判断：

只有 1 个链接 → 研究报告（聚焦）
  └─ 如技术较成熟，有开发者场景 → 追加最佳实践

多个链接 + 技术较新 → 研究报告（全面覆盖）
  └─ 如有"如何在项目中落地"需求 → 追加最佳实践

有代码库/框架 → 研究报告 + 最佳实践 + 项目分析附
```

### 2.2 报告定位

在写之前先确认：
```
## 报告定位（写给谁）

目标读者：[开发者 / 架构师 / 决策者 / ...]
读完能：[理解原理 / 知道怎么用 / 能做技术选型 / ...]
报告侧重点：[深度技术原理 / 实用性 / 生态全景 / ...]
```

---

## Phase 3：技术研究报告模板

文件命名：`reports/[topic]-research-YYYYMMDD.md`

```markdown
# [技术名] 技术深度研究报告

*Created: YYYY-MM-DD*
*Sources: [列出主要来源链接]*

## 1. 概述

### 1.1 一句话定性
[技术是什么] + [解决什么问题]

### 1.2 现状
- 项目/GitHub Stars
- 浏览器/框架支持情况
- 生态成熟度

## 2. 核心机制

### 2.1 工作原理
[技术的工作流程图（文字版）]

### 2.2 核心 API
[最重要的 2-3 个 API，代码示例]

### 2.3 与传统方案对比
| 维度 | 传统方案 | 本技术 |
|------|---------|--------|
|        |         |        |

## 3. 生态现状

### 3.1 关键项目
| 项目 | Stars | 用途 |
|------|-------|------|
|        |       |      |

### 3.2 工具链
| 工具 | 说明 |
|------|------|
|        |      |

## 4. 应用场景

| 场景 | 适用度 | 说明 |
|------|--------|------|
|        |        |      |

## 5. 局限性 / 风险

| 问题 | 影响 | 缓解方案 |
|------|------|---------|
|        |      |          |

## 6. 对 [当前项目/OpenClaw] 的意义

[具体能做什么]

## 7. 总结

| 维度 | 评分 | 说明 |
|------|------|------|
|        |      |      |

## 参考资料

[编号列表，含链接]
```

---

## Phase 4：最佳实践指南模板

文件命名：`reports/[topic]-best-practices-YYYYMMDD.md`

```markdown
# [技术名] 最佳实践指南
*Target: [目标读者]*
*[版本/日期]*

## 目录

[自动生成]

## 1. 快速入门

### 1.1 环境要求
[前置依赖]

### 1.2 安装配置
[关键安装步骤]

### 1.3 验证安装
[hello world 示例]

## 2. 核心设计原则

### 2.1 原则一
[原则名称]：[具体说明]

### 2.2 原则二
...

## 3. 实践示例

### 3.1 场景一
[完整可运行代码]

### 3.2 场景二
...

## 4. 安全 / 避坑

[常见错误 + 解决方案]

## 5. 上线前检查清单

- [ ] ...
- [ ] ...

## 参考资源

[官方文档 + 有价值的博客]
```

---

## Phase 5：Git 归档

### 5.1 判断是否已有 remote

```bash
cd $WORKSPACE
git remote -v  # 有输出则已有 remote
```

### 5.2 创建 reports 目录

```bash
mkdir -p $WORKSPACE/reports
```

### 5.3 检查 .gitignore

如果 `reports/` 被 `.gitignore` 忽略：
```bash
git add -f reports/  # 强制添加
```

### 5.4 提交并推送

```bash
git add reports/
git commit -m "feat(reports): [技术名] research and best practices

- reports/[技术名]-research-YYYYMMDD.md: 技术深度研究
- reports/[技术名]-best-practices-YYYYMMDD.md: 最佳实践指南"

# 如果有 remote
git push origin main
```

---

## 执行检查点

### Phase 1 完成后（信息收集）

- [ ] 所有链接内容已抓取（并行，无遗漏）
- [ ] GitHub 相关项目已发现（Stars 排序，取前 5-10）
- [ ] 官方 Spec/Docs 已抓取
- [ ] 关键信息已提取：Stars 数、版本、许可证、主要 API

### Phase 2 完成后（合成判断）

- [ ] 已确认输出份数（1份 or 2份）
- [ ] 已确认报告定位（读者 + 侧重点）

### Phase 3 完成后（研究报告）

- [ ] 技术一句话定性（闭眼能向非技术人员解释）
- [ ] 核心 API 代码示例可运行
- [ ] 竞品对比表完整
- [ ] 局限性不回避
- [ ] 参考资料含链接

### Phase 4 完成后（最佳实践，如需要）

- [ ] 快速入门可实际操作（不是泛泛而谈）
- [ ] 代码示例完整可复制
- [ ] 安全/避坑清单实用

### Phase 5 完成后（归档）

- [ ] 文件已写入 `reports/` 目录
- [ ] 已 commit（含清晰 commit message）
- [ ] 已 push（如果有 remote）

---

## 输出规范

**研究报告**：深度 + 准确 + 结构清晰，读者能向他人解释这项技术
**最佳实践**：可操作 + 可复制，读者能立即在项目中使用
**两份都写**：确保各自独立，不重复，侧重不同

---

## 注意事项

1. **并行优先**：Phase 1 全部并行，不串行等待
2. **不造轮子**：已有官方文档的不要自己重新解释，直接引用
3. **中文为主**：给中国开发者看，保留关键英文术语但加中文解释
4. **事实 vs 推断**：描述技术现状时区分"确定事实"和"推断/可能"
5. **Git commit 及时**：写完就 commit，不积压
