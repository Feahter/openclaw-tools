---
name: oss-code-analysis
version: 2.0.0
description: >
  开源项目源码深度分析 Skill。当用户提到任何以下场景时，必须使用此 Skill：
  分析/读/研究某个开源项目或 GitHub 仓库的源码；评价代码质量或架构设计；
  做技术选型调研；想从开源项目中提取可复用代码；想了解某个项目"是怎么实现的"；
  说"帮我看看这个项目"、"这个项目代码怎么样"、"分析一下这个仓库"、
  "读一下源码"、"这个项目值得学习吗"、"有没有可以借鉴的代码"。
  即使用户只是随口说"看看这个项目"，也应触发此 Skill。
  输出三份文档：架构报告、代码质量评估（含评分）、泛用价值代码分析（含移植建议）。
author: extracted from AionUi analysis session, enhanced by skill-creator
---

# OSS Code Analysis Skill

对开源项目进行系统性源码分析。核心思路：**README 是合同，代码是履约证明**——
分析的本质是验证项目是否兑现了它的承诺，而不是泛泛评价代码好坏。

## 快速开始

拿到项目路径后，按以下五个阶段推进。每个阶段有明确的时间预算和产出物，
不要跳过阶段 0（定锚），它决定了后续所有分析的评判标准。

---

## 阶段 0：定锚（5 分钟）

**在读任何代码之前，先建立评判标准。**

读 README（优先中文版），提取项目的核心价值主张（通常 3-6 条），
然后把每条主张转化为一个可以在代码里验证的具体问题：

| 主张示例 | 转化为验证问题 |
|---------|-------------|
| "零配置" | 有没有默认配置文件？启动流程几步？ |
| "多 Agent 支持" | 有没有 AgentManager 或类似管理类？ |
| "24/7 自动化" | 有没有 Cron/Scheduler 相关代码？ |
| "插件化扩展" | 有没有 Plugin/Extension 注册机制？ |

把这些问题记下来，后续分析以此为导航。分析结束时，每个问题都应该有 ✅ 或 ❌ 的答案。

---

## 阶段 1：地图绘制（10 分钟）

**在读具体代码之前，先理解整体结构。目标是画出一张心智地图，而不是读懂每个文件。**

```bash
# 目录结构（只看第 2 层，不要深入）
find src -maxdepth 2 -type d | head -40

# 找出核心文件（行数最多的 ≠ 最重要的，但值得关注）
find src -name "*.ts" -o -name "*.py" -o -name "*.go" | xargs wc -l 2>/dev/null | sort -rn | head -20

# 找出被最多文件依赖的模块（这才是真正的核心）
# TypeScript/JS:
grep -rh "from ['\"]" src/ --include="*.ts" | grep -oP "(?<=from ['\"])[^'\"]+(?=['\"])" | sort | uniq -c | sort -rn | head -20

# 了解技术栈
cat package.json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); [print(k,v) for k,v in {**d.get('dependencies',{}), **d.get('devDependencies',{})}.items()]" | head -30
```

画出分层心智地图：
```
项目名
├── 层 A（如：进程层）→ 负责什么
├── 层 B（如：通信层）→ 负责什么
└── 层 C（如：业务层）→ 负责什么
```

---

## 阶段 2：核心路径追踪（30 分钟）

**找到"一条消息/请求从输入到输出"的完整链路。**

选择最能体现项目核心价值的一条主流程，从入口文件开始逐层追踪，
直到找到"真正干活"的代码。调用链不超过 7 层，超过说明需要重新选择追踪起点。

追踪时重点关注四个边界：
- **进程/线程边界**：IPC、Worker、子进程在哪里？
- **持久化边界**：数据在哪里写入 DB/文件？
- **错误边界**：try/catch 集中在哪里？
- **异步协调**：Promise.race、超时机制在哪里？

每个关键文件用一段话记录：职责是什么、最值得注意的设计决策是什么。

详细的追踪方法和记录模板见 `references/tracking-guide.md`。

---

## 阶段 3：代码质量评估（20 分钟）

**用数据说话，而不是主观印象。**

运行以下诊断命令（适配项目语言）：

```bash
# 超大文件（> 500 行通常是职责过多的信号）
find src -name "*.ts" | xargs wc -l | sort -rn | awk '$1 > 500 {print}'

# 错误处理质量（三类 catch 的比例）
echo "静默 catch:" && grep -rn "} catch {" src/ --include="*.ts" | wc -l
echo "warn catch:" && grep -rn -A1 "} catch" src/ --include="*.ts" | grep "console.warn" | wc -l
echo "throw/reject:" && grep -rn -A1 "} catch" src/ --include="*.ts" | grep -E "throw|reject" | wc -l

# 历史债务
grep -rn "TODO\|FIXME\|HACK\|legacy\|backward compat\|deprecated" src/ --include="*.ts" | wc -l

# 单例数量（过多是耦合信号）
grep -rn "static instance" src/ --include="*.ts" | wc -l

# 测试覆盖
echo "测试文件:" && find . -name "*.test.ts" -o -name "*.spec.ts" | wc -l
echo "源码文件:" && find src -name "*.ts" | grep -v "\.test\.\|\.spec\." | wc -l
```

评分标准和 7 维度评分模板见 `references/quality-rubric.md`。

---

## 阶段 4：泛用价值识别（15 分钟）

**找出可以直接移植到其他项目的代码。**

泛用性的核心判断标准：**去掉所有业务 import 后，代码还能独立运行吗？**

高泛用性的信号：
- 文件顶部没有业务相关的 import
- 函数参数是通用类型（string、callback、interface），不是业务类型
- 代码量小（< 200 行）但解决了一个完整问题
- 注释里有"为什么这么做"（说明踩过坑，经验沉淀）

分级标准和常见高泛用性模式见 `references/portability-guide.md`。

---

## 阶段 5：代码提取（可选，60 分钟）

当发现 ⭐⭐⭐⭐⭐ 级别的可移植代码时，按以下步骤提取：

1. **解耦**：将业务依赖替换为回调函数或接口参数
2. **泛化**：将业务特有类型替换为通用类型
3. **注释**：顶部写来源、解决的问题、使用方式；关键逻辑写"为什么"而不是"是什么"
4. **示例**：文件底部附上可运行的使用示例
5. **存放**：`workspace/code/<项目名>-patterns/` 目录

---

## 输出文档

分析结束后，在 `workspace/docs/` 目录生成三份文档：

**文档 1：`{项目名}-源码分析报告.md`**
- 项目定位（README 主张 + 验证结论对照表）
- 架构全景（分层图 + 每层职责）
- 核心模块分析（关键文件的职责和设计决策）
- 数据流（一条请求的完整生命周期）

**文档 2：`{项目名}-代码质量评估.md`**
- 总分（X.X / 10）
- README vs 代码实现对照表（每条主张 ✅/❌）
- 优点（3-5 条，有代码证据）
- 主要问题（按 P0/P1/P2 分级，有文件路径）
- 7 维度分项评分表

**文档 3：`{项目名}-泛用价值代码分析.md`**
- ⭐⭐⭐⭐⭐ 直接可移植（文件路径、解决问题、核心设计、移植建议）
- ⭐⭐⭐⭐ 改造后可移植
- ⭐⭐⭐ 思路参考
- 总览表

完整的文档模板见 `references/output-templates.md`。

---

## 时间分配

| 阶段 | 时间 | 产出 |
|------|------|------|
| 0. 定锚 | 5 min | 验证问题清单 |
| 1. 地图绘制 | 10 min | 架构心智地图 |
| 2. 核心路径追踪 | 30 min | 关键模块笔记 |
| 3. 质量评估 | 20 min | 评分 + 问题列表 |
| 4. 泛用价值识别 | 15 min | 可移植代码清单 |
| 5. 代码提取（可选） | 60 min | 独立可用的代码文件 |
| **总计** | **~80 min** | **3 份文档** |

---

## 参考文件

- `references/tracking-guide.md` — 核心路径追踪方法和记录模板
- `references/quality-rubric.md` — 代码质量评分标准（7 维度）
- `references/portability-guide.md` — 泛用性分级标准和常见模式库
- `references/output-templates.md` — 三份输出文档的完整模板
