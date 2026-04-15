# Page Agent + Pretext 集成指南

> 详细 API 文档见 `~/.openclaw/workspace/skills/pretext-integration/references/api.md`

## 快速开始

```bash
npm install @chenglou/pretext
```

```javascript
// 加载脚本
// <script src="https://cdn.jsdelivr.net/npm/@chenglou/pretext"></script>
// <script src="pretext-integration.js"></script>

const executor = new PageAgentExecutorWithPretext(document, {
  enablePretext: true,
  pretextCacheSize: 500   // 可选，默认 500
})
```

---

## 核心用法

```javascript
// 1. 获取元素文本宽度（无 DOM 测量）
const width = await executor.getElementTextWidth(0)

// 2. 获取元素文本高度
const height = await executor.getElementTextHeight(0, 300)

// 3. 检测文本溢出
const { overflow, reason } = await executor.detectElementTextOverflow(0, 150, 20)
if (overflow) console.warn(reason)

// 4. 查看性能指标
const { hitRate, cacheSize } = executor.getPretextMetrics()
```

---

## 典型场景

### 自适应布局（二分查找最优宽度）

```javascript
async function findOptimalWidth(index, targetHeight) {
  let lo = 100, hi = 800
  while (lo < hi) {
    const mid = (lo + hi) >> 1
    const h = await executor.getElementTextHeight(index, mid)
    h > targetHeight ? lo = mid + 1 : hi = mid
  }
  return lo
}
```

### 批量溢出检测

```javascript
for (let i = 0; i < 10; i++) {
  const r = await executor.detectElementTextOverflow(i, 200, 20)
  if (r.overflow) console.warn(`[${i}] ${r.reason}`)
}
```

---

## 性能

| 操作 | 首次 | 缓存命中 |
|------|------|---------|
| 文本宽度/高度 | 1-5ms | 0.01ms |
| 溢出检测 | 2-8ms | 0.02ms |

缓存命中时性能提升 **100-500 倍**。

---

## 故障排查

| 问题 | 解决 |
|------|------|
| `window.Pretext is undefined` | 确认 CDN script 已加载 |
| `Element with index N not found` | 先调用 `getDOMAsText()` 建立索引 |
| 内存持续增长 | `setInterval(() => executor.clearPretextCache(), 60000)` |

---

## 运行性能测试

```bash
node performance-test.js
```
