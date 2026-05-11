# 架构图 Skills 三者比较 & 合成报告

**日期**: 2026-05-02
**合成来源**: fireworks-tech-graph (本地 v1.0.4) + drawio-skill (928⭐) + excalidraw-skill (54⭐)

---

## 一、引擎能力对比

| 维度 | fireworks-tech-graph | drawio-skill | excalidraw-skill |
|------|---------------------|--------------|------------------|
| **输出格式** | SVG + PNG | .drawio XML + PNG + SVG + PDF | .excalidraw JSON + SVG |
| **导出方式** | Python SVG 生成器 | draw.io CLI | Kroki API / Local CLI |
| **零依赖** | ✅ | ❌ 需要 draw.io | ✅ Kroki 零安装 |
| **可编辑输出** | ❌ | ✅ .drawio.png 嵌入 XML | ❌ |
| **图类型覆盖** | 14种（含独特类型）| ERD/UML/Sequence/ML专精 | 通用流程/架构 |
| **视觉风格** | 7种预设 | 用户自定义预设+学习 | 60-30-10配色规则 |

---

## 二、质量保证机制

| 机制 | fireworks-tech-graph | drawio-skill | excalidraw-skill |
|------|---------------------|--------------|------------------|
| **自检** | Python rsvg 验证 | Vision API 自检（2轮）| 无 |
| **迭代编辑** | 全量重建 | 精准 XML 编辑规则 | 无 |
| **Review 循环** | 无 | 5轮用户反馈 | 无 |
| **IEND Repair** | N/A | ✅ PNG -e 修复 | N/A |
| **降级链** | 基础 | 完整（Browser→CLI→手动）| 基础 |
| **浏览器Fallback** | 无 | ✅ diagrams.net URL | ✅ Kroki |

---

## 三、OpenClaw 集成

| 功能 | fireworks-tech-graph | drawio-skill | excalidraw-skill |
|------|---------------------|--------------|------------------|
| **专属快速触发** | ✅ 6种模式 | ❌ | ❌ |
| **OpenClaw 模板** | ✅ 6套 | ❌ | ❌ |
| **双 Gateway 图** | ✅ | ❌ | ❌ |
| **feZ 定制差异图** | ✅ | ❌ | ❌ |

---

## 四、合成决策

### 保留的核心优势

**从 fireworks-tech-graph（本地）：**
- ✅ Native SVG 引擎（零依赖，最快路径）
- ✅ 7种预设视觉风格 + 完整 Style Guide
- ✅ 14种图类型全覆盖
- ✅ OpenClaw 专属快速触发模板
- ✅ feZ 本地架构（双 Gateway/Skills/Memory/ToolCall）
- ✅ Python SVG 生成验证管道

**从 drawio-skill（928⭐）：**
- ✅ Vision 自检 + Review 循环（质量保证机制）
- ✅ 精准 XML 迭代编辑规则
- ✅ Style Presets 系统 + Learn-from-example
- ✅ ERD/UML/ML 专业模板
- ✅ IEND PNG repair（细节魔鬼）
- ✅ 完整降级链（Browser/CLI/手动）
- ✅ 排版布局知识（事件总线模式、hub路由走廊等）

**从 excalidraw-skill（54⭐）：**
- ✅ Kroki API（零安装 SVG）
- ✅ 60-30-10 配色规则
- ✅ 字号层级体系
- ✅ 手绘/草图风格支持
- ✅ Section-by-section 大图构建

### 新增的合成创新

1. **引擎决策树**：根据图类型自动路由到最优引擎（Native SVG / draw.io / Kroki）
2. **三层输出策略**：快速草稿（SVG）→ 专业版（draw.io PNG+SVG+PDF）→ 轻量分享（Kroki SVG）
3. **OpenClaw 专属 + 差异化**：保留 fireworks 的本地定制模板，同时引入 drawio 的专业质量机制
4. **统一 Skill 接口**：用户感知为一个 skill，内部自动分发

---

## 五、文件结构

```
arch-diagram/
├── SKILL.md                      # 主入口（引擎决策 + 工作流）
├── package.json                  # 元数据
├── SYNTHESIS.md                  # 本文件
├── scripts/
│   └── generate-from-template.py # Native SVG 渲染器（from fireworks）
└── references/
    ├── openclaw-patterns.md      # feZ 本地架构模板（6套）
    ├── recipes.md                # Native SVG 各类型 JSON 模板
    ├── drawio-recipes.md         # draw.io ERD/UML/ML XML 模板
    ├── excalidraw-recipes.md     # Excalidraw JSON 结构
    └── style-guides/             # 7种视觉风格定义
        └── index.md
```
