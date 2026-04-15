# 性能基准

## 测试环境

- 设备：MacBook Pro 15,2，Intel i7-8569U @ 2.80GHz，16GB RAM
- Node.js：v22.x
- Python：3.14
- @chenglou/pretext：latest

---

## JavaScript 性能

| 操作 | 首次 | 缓存命中 | 提升倍数 |
|------|------|---------|---------|
| `prepare()` × 500 文本 | ~19ms | — | — |
| `layout()` 单次 | ~0.09ms | ~0.01ms | 9x |
| `layoutWithLines()` | ~1-5ms | ~0.01ms | 100-500x |
| `detectTextOverflow()` | ~2-8ms | ~0.02ms | 100-400x |
| 长文本（500+ 字符） | ~5-15ms | ~0.01ms | 500-1500x |
| 多语言文本 | ~2-8ms | ~0.01ms | 200-800x |

## Python 性能

| 操作 | 首次 | 缓存命中 | 提升倍数 |
|------|------|---------|---------|
| `calculate_height()` | ~5-15ms | ~0.01ms | 500-1500x |
| `validate_text_fit()` | ~5-15ms | ~0.01ms | 500-1500x |
| `calculate_metrics()` | ~8-20ms | ~0.01ms | 800-2000x |
| Node.js 进程启动 | ~50-100ms（首次） | — | — |

> **注意**：Python 端通过 subprocess 调用 Node.js，首次调用包含进程启动开销（~50-100ms）。建议使用缓存减少调用次数。

---

## 缓存效果

| 场景 | 命中率 | 说明 |
|------|--------|------|
| 重复文本（如报告标题） | 90%+ | 效果最佳 |
| 八字命理报告 | 60-80% | 固定格式文本 |
| AI 内容验证 | 30-50% | 文本多样性高 |
| 品味研究 | 20-40% | 每次文本不同 |

---

## 优化建议

### 1. 复用实例（最重要）

```python
# ✅ 好：复用实例，缓存有效
from scripts.text_metrics import get_metrics_instance
metrics = get_metrics_instance()
for text in texts:
    height = metrics.calculate_height(text, '14px 宋体', 300, 20)

# ❌ 差：每次创建新实例，缓存失效
for text in texts:
    from scripts.text_metrics import PretextMetrics
    m = PretextMetrics()
    height = m.calculate_height(text, '14px 宋体', 300, 20)
```

### 2. 批量验证

```python
# ✅ 好：批量验证，减少调用
from scripts.ai_content_validator import validate_batch
result = validate_batch(items, 'card_title')

# ❌ 差：逐个验证
for item in items:
    result = validate_content(item['text'], 'card_title')
```

### 3. 合理设置缓存大小

```javascript
// 小应用（<100 种文本）
const pretext = new PretextIntegration({ cacheSize: 100 })

// 中等应用（100-500 种文本）
const pretext = new PretextIntegration({ cacheSize: 500 })  // 默认

// 大应用（500+ 种文本）
const pretext = new PretextIntegration({ cacheSize: 2000 })
```

### 4. 监控缓存命中率

```javascript
// 定期检查
setInterval(() => {
    const metrics = pretext.getMetrics()
    if (parseFloat(metrics.hitRate) < 30) {
        console.warn('缓存命中率低，考虑增加缓存大小')
    }
}, 60000)
```

---

## 运行性能测试

```bash
cd ~/.openclaw/workspace/skills/page-agent-executor
node performance-test.js
```
