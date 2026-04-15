---
name: pretext-integration
description: |
  Pretext 文本测量与布局集成。当用户需要精确计算文本高度/宽度、验证文本不溢出容器、
  生成 PDF/HTML 报告布局、Canvas/SVG 渲染、或说"计算这段文字高度"、"验证标题不溢出"、
  "文本自适应布局"、"八字报告分页"时使用。
  支持多语言（中文、emoji 等），无需 DOM 测量，避免 layout reflow。
---

# pretext-integration

精确文本测量，无 DOM reflow。封装 `@chenglou/pretext`，提供 Python + JavaScript 双端集成。

## 快速开始

```bash
npm install @chenglou/pretext
```

```python
# Python 端（通过 subprocess 调用 Node.js）
from scripts.text_metrics import calculate_height, validate_text_fit

height = calculate_height('丙午辛卯丙申庚寅', '18px 宋体', 300, 24)
valid, reason = validate_text_fit('AI生成标题', '14px Inter', 200, 20)
```

```javascript
// JavaScript 端
const { PretextIntegration } = require('./scripts/pretext-integration.js')
const pretext = new PretextIntegration()
const height = await pretext.calculateTextHeight('测试文本', '14px 宋体', 300, 20)
```

---

## 5 大应用场景

| 场景 | 脚本 | 说明 |
|------|------|------|
| 文本高度/宽度计算 | `scripts/text_metrics.py` | 核心测量工具，带缓存 |
| 八字命理报告布局 | `scripts/bazi_report_layout.py` | 精确分页，避免溢出 |
| AI 内容验证 | `scripts/ai_content_validator.py` | 验证标题/描述不溢出容器 |
| 品味研究数据化 | `scripts/taste_analyzer.py` | 量化文本特征，记录判断 |
| 小说创作 Canvas 渲染 | `scripts/novel-renderer.js` | 精确布局 + PDF 导出 |

---

## 核心 API（Python）

```python
from scripts.text_metrics import calculate_height, validate_text_fit, calculate_metrics

# 计算高度
height = calculate_height('文本', '14px 宋体', max_width=300, line_height=20)

# 验证是否溢出
valid, reason = validate_text_fit('文本', '14px Inter', max_width=200, max_height=20)

# 完整指标
metrics = calculate_metrics('文本', '14px 宋体', max_width=300, line_height=20)
# → { height, lineCount, density, compactness }
```

## 核心 API（JavaScript）

```javascript
const { PretextIntegration, PageAgentExecutorWithPretext } = require('./scripts/pretext-integration.js')

// 独立使用
const pretext = new PretextIntegration({ enabled: true, cacheSize: 500 })
const width  = await pretext.calculateTextWidth('文本', '14px Inter')
const height = await pretext.calculateTextHeight('文本', '14px Inter', 300, 20)
const result = await pretext.detectTextOverflow('文本', '14px Inter', 200, 20, 20)

// Page Agent 集成
const executor = new PageAgentExecutorWithPretext(document, { enablePretext: true })
const w = await executor.getElementTextWidth(0)
const overflow = await executor.detectElementTextOverflow(0, 200, 20)
```

---

## 运行示例

```bash
cd ~/.openclaw/workspace/skills/pretext-integration
python3 scripts/examples.py          # Python 示例
node scripts/performance-test.js     # 性能测试（需要 Node.js）
```

---

## 详细文档

- **API 完整参考** → `references/api.md`
- **错误处理** → `references/error-handling.md`
- **集成检查清单** → `CHECKLIST.md`
- **性能基准** → `references/performance.md`

---

## 文件结构

```
pretext-integration/
├── SKILL.md                    # 本文件（入口）
├── CHECKLIST.md               # 集成检查清单
├── scripts/
│   ├── text_metrics.py         # 核心 Python 测量工具
│   ├── bazi_report_layout.py   # 八字报告布局
│   ├── ai_content_validator.py # AI 内容验证
│   ├── taste_analyzer.py       # 品味研究数据化
│   ├── novel-renderer.js       # Canvas 渲染
│   └── examples.py             # 使用示例
└── references/
    ├── api.md                  # 完整 API 参考
    ├── error-handling.md       # 错误处理指南
    └── performance.md          # 性能基准
```
