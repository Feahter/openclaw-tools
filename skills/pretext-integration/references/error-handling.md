# 错误处理指南

## Python 端

### 常见错误

#### Node.js 未安装

```
FileNotFoundError: [Errno 2] No such file or directory: 'node'
```

**解决**：
```bash
brew install node  # macOS
# 或
nvm install 18
```

#### @chenglou/pretext 未安装

```
Error: Cannot find module '@chenglou/pretext'
```

**解决**：
```bash
npm install @chenglou/pretext
# 或全局安装
npm install -g @chenglou/pretext
```

#### 字体名称不正确

```python
# ❌ 错误
height = calculate_height('文本', 'system-ui', 300, 20)

# ✅ 正确
height = calculate_height('文本', '14px 宋体', 300, 20)
height = calculate_height('文本', '14px "PingFang SC"', 300, 20)
```

**规则**：font 参数必须是完整的 CSS font 简写，包含字体大小。

#### subprocess 超时

```python
# text_metrics.py 默认超时 5 秒
# 如果 Node.js 启动慢，可以增加超时
result = subprocess.run(['node', '-e', js_code], 
                       capture_output=True, text=True, 
                       timeout=10)  # 增加到 10 秒
```

---

## JavaScript 端

### Pretext 未加载

```javascript
// 症状：window.Pretext is undefined
// 解决：确保脚本已加载
```

```html
<!-- 方式 1：CDN -->
<script src="https://cdn.jsdelivr.net/npm/@chenglou/pretext"></script>

<!-- 方式 2：本地 -->
<script src="node_modules/@chenglou/pretext/dist/pretext.js"></script>
```

### 降级方案

`PretextIntegration` 在 Pretext 不可用时自动降级为估算方案：

```javascript
const pretext = new PretextIntegration({ enabled: true })

// 如果 window.Pretext 不存在，自动使用估算
// 估算精度：±20%（够用于布局验证）
const height = await pretext.calculateTextHeight('文本', '14px Inter', 300, 20)
```

### 缓存溢出

```javascript
// 症状：内存占用持续增加
// 解决：定期清空缓存
setInterval(() => {
  pretext.clearCache()
}, 60000)  // 每分钟清空

// 或减小缓存大小
const pretext = new PretextIntegration({ cacheSize: 100 })
```

---

## 错误码速查

| 错误 | 原因 | 解决 |
|------|------|------|
| `node: command not found` | Node.js 未安装 | `brew install node` |
| `Cannot find module '@chenglou/pretext'` | npm 包未安装 | `npm install @chenglou/pretext` |
| `window.Pretext is undefined` | 脚本未加载 | 检查 script 标签 |
| `Element with index N not found` | 元素索引无效 | 先调用 parseDom() |
| `timeout` | Node.js 启动慢 | 增加 subprocess timeout |
| 高度计算不准 | 字体未加载 | 等待字体加载后再调用 |
