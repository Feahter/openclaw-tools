# Pretext API 完整参考

## JavaScript API（@chenglou/pretext）

### prepare(text, font, options?)

一次性文本分析 + 测量。

```typescript
const prepared = prepare('测试文本', '16px 宋体', {
  whiteSpace: 'normal'  // 或 'pre-wrap'
})
```

**参数**：
- `text` (string) — 要测量的文本
- `font` (string) — CSS font 简写（如 "16px Inter"）
- `options.whiteSpace` ('normal' | 'pre-wrap') — 空白处理方式

**返回值**：PreparedText（不透明值，传给 layout()）

---

### layout(prepared, maxWidth, lineHeight)

计算文本高度（快速路径）。

```typescript
const { height, lineCount } = layout(prepared, 300, 20)
```

**返回值**：
```typescript
{ height: number, lineCount: number }
```

---

### prepareWithSegments(text, font, options?)

详细分析（用于手动布局）。

---

### layoutWithLines(prepared, maxWidth, lineHeight)

获取所有行信息。

```typescript
const { lines, height, lineCount } = layoutWithLines(prepared, 300, 20)
// lines: [{ text: '...', width: 100, start, end }, ...]
```

---

### walkLineRanges(prepared, maxWidth, onLine)

遍历行宽（无字符串构建，性能最优）。

```typescript
let maxW = 0
walkLineRanges(prepared, 300, line => {
  if (line.width > maxW) maxW = line.width
})
```

---

### layoutNextLine(prepared, cursor, maxWidth)

逐行布局（宽度可变）。

```typescript
let cursor = { segmentIndex: 0, graphemeIndex: 0 }
while (true) {
  const line = layoutNextLine(prepared, cursor, width)
  if (line === null) break
  cursor = line.end
}
```

---

## Python API（scripts/text_metrics.py）

### calculate_height(text, font, max_width, line_height)

```python
from scripts.text_metrics import calculate_height
height = calculate_height('测试文本', '14px 宋体', 300, 20)
# → float（像素）
```

### validate_text_fit(text, font, max_width, max_height, line_height)

```python
from scripts.text_metrics import validate_text_fit
valid, reason = validate_text_fit('标题', '14px Inter', 200, 20, 20)
# → (bool, str | None)
```

### calculate_metrics(text, font, max_width, line_height)

```python
from scripts.text_metrics import calculate_metrics
metrics = calculate_metrics('文本', '14px 宋体', 300, 20)
# → { height, lineCount, density, compactness }
```

---

## Python API（scripts/ai_content_validator.py）

### validate_content(text, container)

```python
from scripts.ai_content_validator import validate_content
result = validate_content('AI生成标题', 'button_title')
# → { valid, container, text, reason, metrics, constraints }
```

**内置容器规格**：

| 容器名 | 字体 | 最大宽度 | 最大高度 |
|--------|------|---------|---------|
| button_title | 14px Inter | 150px | 20px |
| card_title | 16px Inter | 300px | 40px |
| card_description | 14px Inter | 300px | 60px |
| modal_title | 18px Inter | 400px | 50px |
| modal_content | 14px Inter | 400px | 200px |
| chinese_title | 16px 宋体 | 300px | 40px |
| chinese_content | 14px 宋体 | 300px | 80px |

### validate_batch(items, container)

```python
from scripts.ai_content_validator import validate_batch
result = validate_batch([
    {'text': '标题1', 'id': 1},
    {'text': '标题2', 'id': 2},
], 'card_title')
# → { total, valid, invalid, valid_rate, results }
```

---

## Python API（scripts/taste_analyzer.py）

### analyze_text(text, font, max_width)

```python
from scripts.taste_analyzer import get_analyzer
analyzer = get_analyzer()
analysis = analyzer.analyze_text('这个设计很优雅')
# → { text, length, height, lineCount, density, compactness, complexity, readability, features }
```

### record_judgement(text, judgement, rating, category, tags, notes)

```python
analyzer.record_judgement(
    text='这个界面设计很简洁',
    judgement='简洁而优雅',
    rating=0.9,
    category='design',
    tags=['简洁', '现代']
)
```

### get_statistics()

```python
stats = analyzer.get_statistics()
# → { total, avg_rating, avg_complexity, avg_readability, categories, tags }
```

---

## JavaScript API（scripts/novel-renderer.js）

### NovelTextRenderer

```javascript
const renderer = new NovelTextRenderer(canvas, {
  font: '16px 宋体',
  lineHeight: 28,
  maxWidth: canvas.width - 40,
  padding: 20,
  textColor: '#000',
  backgroundColor: '#fff',
  enablePretext: true
})

await renderer.render('小说文本...')
renderer.exportAsImage('novel.png')
await renderer.exportAsPDF('novel.pdf')  // 需要 jsPDF
```

---

## 性能基准

| 操作 | 首次 | 缓存命中 | 提升 |
|------|------|---------|------|
| prepare()（500文本） | ~19ms | — | — |
| layout()（单次） | ~0.09ms | ~0.01ms | 9x |
| layoutWithLines() | ~1-5ms | ~0.01ms | 100-500x |
| Python calculate_height() | ~5-15ms | ~0.01ms | 500-1500x |

---

## 支持的语言

中文（简繁）、日文、韩文、阿拉伯文、希伯来文、泰文、印度文字、Emoji
