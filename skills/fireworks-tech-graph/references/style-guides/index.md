# Style Guides — 7种视觉风格

> 具体颜色 tokens 和 SVG patterns 见各风格文件：
> `style-1-flat-icon.md` · `style-2-dark-terminal.md` · `style-3-blueprint.md`
> `style-4-notion-clean.md` · `style-5-glassmorphism.md`
> `style-6-claude-official.md` · `style-7-openai.md`

---

## 风格速查

| # | 名称 | 背景 | 字体 | 最适合 |
|---|------|------|------|--------|
| 1 | Flat Icon | `#ffffff` | Helvetica | 博客、演示、文档 |
| 2 | Dark Terminal | `#0f0f1a` | SF Mono / Fira Code | GitHub README、开发文章 |
| 3 | Blueprint | `#0a1628` | Courier New | 架构文档、工程图 |
| 4 | Notion Clean | `#ffffff` | system-ui | Notion、Confluence、wiki |
| 5 | Glassmorphism | `#0f172a` 渐变 | Inter | 产品站点、keynote 演示 |
| 6 | Claude Official | `#f8f6f3` 暖奶油 | system-ui | Anthropic 风格、技术博客 |
| 7 | OpenAI Official | `#ffffff` | system-ui | OpenAI 风格、现代简约 |

---

## 风格选择矩阵

### 图类型 → 推荐风格

| 图类型 | 首选 | 备选 |
|--------|------|------|
| Architecture | Style 3 Blueprint | Style 6 Claude Official |
| Data Flow | Style 2 Dark Terminal | Style 5 Glass |
| Flowchart | Style 1 Flat Icon | Style 4 Notion |
| Agent Architecture | Style 5 Glass | Style 2 Dark Terminal |
| Memory Architecture | Style 3 Blueprint | Style 1 Flat Icon |
| Sequence | Style 2 Dark Terminal | Style 3 Blueprint |
| Comparison | Style 4 Notion | Style 1 Flat Icon |
| Mind Map | Style 1 Flat Icon | Style 6 Claude Official |
| UML Class | Style 1 Flat Icon | Style 4 Notion |
| UML State | Style 2 Dark Terminal | Style 3 Blueprint |
| Timeline | Style 1 Flat Icon | Style 4 Notion |

### 场景 → 推荐风格

| 场景 | 推荐风格 | 原因 |
|------|---------|------|
| Internal docs | Style 4 Notion Clean | 最小化、wiki 友好 |
| Blog posts | Style 1 Flat Icon | 彩色、有吸引力 |
| GitHub README | Style 2 Dark Terminal | 匹配暗色主题 |
| Presentations | Style 5 Glassmorphism | 抛光、视觉冲击 |
| Anthropic/Claude 项目 | Style 6 Claude Official | 暖奶油背景、品牌色 |
| OpenAI 项目 | Style 7 OpenAI | 干净白色、OpenAI 风格 |
| 架构文档 | Style 3 Blueprint | 工程美学 |

---

## Semantic Node Colors（各风格通用映射）

| 语义 | Style 1 | Style 2 | Style 3 | Style 4 | Style 5 | Style 6 | Style 7 |
|------|---------|---------|---------|---------|---------|---------|---------|
| Input/Source | `#a8c5e6` | `#38bdf8` | `#38bdf8` | `#3b82f6` | `#60a5fa` | `#a8c5e6` | `#0891b2` |
| Agent/Core | `#7c3aed` | `#a855f7` | `#67e8f9` | `#3b82f6` | `#c084fc` | `#9dd4c7` | `#10a37f` |
| Storage/Memory | `#10b981` | `#22c55e` | `#22d3ee` | `#3b82f6` | `#34d399` | `#e8e6e3` | `#0f766e` |
| Tool/Function | `#f97316` | `#fb923c` | `#fde047` | `#3b82f6` | `#fb923c` | `#f4e4c1` | `#f59e0b` |
| Output/Delivery | `#2563eb` | `#38bdf8` | `#67e8f9` | `#3b82f6` | `#60a5fa` | `#fffcf7` | `#10a37f` |

---

## Semantic Arrow Colors（各风格通用映射）

| Flow | Style 1 | Style 2 | Style 3 | Style 4 | Style 5 | Style 6 | Style 7 |
|------|---------|---------|---------|---------|---------|---------|---------|
| control | `#7c3aed` | `#a855f7` | `#67e8f9` | `#3b82f6` | `#c084fc` | `#d97757` | `#10a37f` |
| write | `#10b981` | `#22c55e` | `#22d3ee` | `#3b82f6` | `#34d399` | `#7b8b5c` | `#0f766e` |
| read | `#2563eb` | `#38bdf8` | `#38bdf8` | `#3b82f6` | `#60a5fa` | `#8c6f5a` | `#0891b2` |
| data | `#f97316` | `#fb7185` | `#fde047` | `#3b82f6` | `#fb923c` | `#b45309` | `#f59e0b` |
| async | `#7c3aed` | `#f59e0b` | `#c084fc` | `#9ca3af` | `#f472b6` | `#9a6fb0` | `#64748b` |
| feedback | `#ef4444` | `#f97316` | `#fb7185` | `#9ca3af` | `#f59e0b` | `#d97757` | `#10a37f` |
