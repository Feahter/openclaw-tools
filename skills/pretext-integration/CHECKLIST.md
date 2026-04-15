# Pretext 集成检查清单

## 📋 安装与配置

- [ ] 安装 Pretext
  ```bash
  npm install @chenglou/pretext
  ```

- [ ] 验证安装
  ```bash
  npm list @chenglou/pretext
  ```

- [ ] 配置 Node.js 环境
  ```bash
  node --version  # 需要 v14+
  ```

---

## 🔧 集成步骤

### 第 1 步：基础集成

- [ ] 复制 `text_metrics.py` 到项目
- [ ] 复制 `bazi_report_layout.py` 到项目
- [ ] 运行示例
  ```bash
  python3 examples.py
  ```

### 第 2 步：八字命理系统集成

- [ ] 在 `report_formatter.py` 中导入 `text_metrics`
  ```python
  from text_metrics import calculate_metrics, validate_text_fit
  ```

- [ ] 修改报告生成函数
  ```python
  def format_full_report(...):
      # 使用 calculate_metrics 计算各部分高度
      title_height = calculate_metrics(title, '18px 宋体')['height']
      content_height = calculate_metrics(content, '14px 宋体')['height']
  ```

- [ ] 测试报告生成
  ```bash
  python3 -c "from report_formatter import format_full_report; ..."
  ```

### 第 3 步：Page Agent 集成

- [ ] 在 `page-agent-executor/executor.js` 中添加 Pretext 支持
  ```javascript
  import { prepare, layout } from '@chenglou/pretext'
  
  class PageAgentExecutor {
    async getElementTextWidth(index) {
      const element = this.elementIndexMap.get(index)
      const text = element.textContent
      const font = window.getComputedStyle(element).font
      
      const prepared = prepare(text, font)
      const { width } = layoutWithLines(prepared, Infinity, 20)
      return width
    }
  }
  ```

- [ ] 测试 Page Agent 优化
  ```bash
  npm test  # 在 page-agent-executor 目录
  ```

### 第 4 步：AI 内容验证集成

- [ ] 创建验证模块
  ```python
  from text_metrics import validate_text_fit
  
  def validate_ai_content(text, font, max_width, max_height):
      valid, reason = validate_text_fit(text, font, max_width, max_height)
      return valid
  ```

- [ ] 集成到 Skill 中
  ```python
  # skills/pretext-integration/validate.py
  ```

---

## ✅ 功能验证

### 基础功能

- [ ] 文本高度计算
  ```python
  from text_metrics import calculate_height
  height = calculate_height('测试文本', '14px 宋体', 300, 20)
  assert height > 0
  ```

- [ ] 文本行数计算
  ```python
  from text_metrics import calculate_line_count
  lines = calculate_line_count('测试文本', '14px 宋体', 300, 20)
  assert lines > 0
  ```

- [ ] 文本验证
  ```python
  from text_metrics import validate_text_fit
  valid, reason = validate_text_fit('测试', '14px Inter', 200, 20)
  assert valid
  ```

### 八字命理集成

- [ ] 报告布局计算
  ```python
  from bazi_report_layout import BaziReportLayout
  layout = BaziReportLayout()
  result = layout.calculate_report_layout([...])
  assert result['total_height'] > 0
  ```

- [ ] 报告验证
  ```python
  valid, issues = layout.validate_report_fit([...])
  assert valid
  ```

### 多语言支持

- [ ] 中文文本
  ```python
  height = calculate_height('中文测试', '14px 宋体', 300, 20)
  assert height > 0
  ```

- [ ] 英文 + Emoji
  ```python
  height = calculate_height('Hello 🌍', '14px Inter', 300, 20)
  assert height > 0
  ```

- [ ] 混合文本
  ```python
  height = calculate_height('AGI 春天到了. بدأت الرحلة 🚀', '14px Inter', 300, 20)
  assert height > 0
  ```

---

## 📊 性能基准

- [ ] 测试 prepare() 性能
  ```bash
  python3 -c "
  import time
  from text_metrics import get_metrics
  m = get_metrics()
  start = time.time()
  for i in range(100):
      m.calculate_height('测试文本', '14px 宋体', 300, 20)
  print(f'100 次调用: {(time.time()-start)*1000:.2f}ms')
  "
  ```

- [ ] 测试缓存效果
  ```bash
  python3 -c "
  from text_metrics import get_metrics
  m = get_metrics()
  # 第一次
  h1 = m.calculate_height('测试', '14px 宋体', 300, 20)
  # 第二次（缓存）
  h2 = m.calculate_height('测试', '14px 宋体', 300, 20)
  print(f'缓存命中: {h1 == h2}')
  "
  ```

---

## 🐛 故障排查

### 问题 1: Pretext 未安装

**症状**：`ModuleNotFoundError: No module named '@chenglou/pretext'`

**解决**：
```bash
npm install @chenglou/pretext
```

### 问题 2: Node.js 不可用

**症状**：`FileNotFoundError: [Errno 2] No such file or directory: 'node'`

**解决**：
```bash
# 检查 Node.js
which node
node --version

# 如果未安装，使用 Homebrew
brew install node
```

### 问题 3: 字体不支持

**症状**：文本高度计算不准确

**解决**：
- 确保字体名称正确（如 "宋体" vs "SimSun"）
- 在 macOS 上使用 "Hiragino Sans" 而不是 "system-ui"
- 测试字体可用性

### 问题 4: 缓存溢出

**症状**：内存占用不断增加

**解决**：
```python
from text_metrics import get_metrics
m = get_metrics()
m.clear_cache()  # 清空缓存
```

---

## 📈 优化建议

### 1. 缓存策略

- [ ] 定期清空缓存（每小时）
  ```python
  import schedule
  schedule.every().hour.do(metrics.clear_cache)
  ```

- [ ] 监控缓存大小
  ```python
  stats = metrics.get_cache_stats()
  if stats['usage'] > 80:
      metrics.clear_cache()
  ```

### 2. 性能优化

- [ ] 批量计算
  ```python
  # 不好
  for text in texts:
      height = calculate_height(text, font, width, line_height)
  
  # 更好
  metrics = get_metrics()
  for text in texts:
      height = metrics.calculate_height(text, font, width, line_height)
  ```

- [ ] 复用 prepared 对象
  ```python
  from text_metrics import PretextMetrics
  m = PretextMetrics()
  prepared = m.prepare(text, font)
  # 多次使用 prepared
  ```

### 3. 错误处理

- [ ] 添加异常处理
  ```python
  try:
      height = calculate_height(text, font, width, line_height)
  except Exception as e:
      logger.error(f"文本测量失败: {e}")
      height = estimate_height(text)  # 降级方案
  ```

---

## 📚 文档更新

- [ ] 更新 README.md
  - 添加 Pretext 集成说明
  - 添加使用示例
  - 添加性能基准

- [ ] 更新 DEVELOPMENT.md
  - 添加开发环境配置
  - 添加测试命令

- [ ] 更新 API 文档
  - 记录新增的文本测量 API
  - 添加参数说明

---

## 🚀 部署检查

- [ ] 生产环境测试
  ```bash
  npm run build
  npm run test:prod
  ```

- [ ] 性能监控
  - 监控 Pretext 调用次数
  - 监控缓存命中率
  - 监控内存占用

- [ ] 回滚计划
  - 如果出现问题，可以禁用 Pretext
  - 保留降级方案（估算高度）

---

## 📝 完成标记

- [ ] 所有检查项完成
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] 性能基准已验证
- [ ] 部署已完成

**完成日期**：_______________

**负责人**：_______________

**备注**：
