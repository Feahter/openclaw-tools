---
name: ppt-design-guide
description: "PPT 制作完整指南。覆盖从入门到专业的全场景需求，入门5步法 + 深度6阶段法 + 工具链 + 避坑指南。触发场景：'帮我做PPT'、'怎么做PPT'、'PPT入门'、'技术分享PPT'、'商业计划书'等。"
---

# PPT 设计指南

> 入门到专业，一个 Skill 就够了。

## 0. 快速选择

| 场景 | 推荐 | 工具 |
|------|------|------|
| 临时需要/入门 | 快速5步法 | Canva/Gamma |
| 工作汇报/培训 | 标准8页 | PPT/Canva |
| 技术分享/深度 | 专业6阶段 | Slidev/python-pptx |
| 高端发布/路演 | 黄金圈+设计 | Figma/Keynote |

---

## 第一部分：快速5步法（10分钟）

### Step 1: 明确内容（3分钟）

| 问题 | 答案 |
|------|------|
| 时长？ | 10分钟 = 8-10页 |
| 听众？ | 决定专业程度 |
| 目标？ | 讲清楚一件事 |

### Step 2: 选模板（2分钟）

**推荐网站**：

| 网站 | 特点 | 免费 |
|------|------|------|
| Canva | 好看简单 | ✅ |
| Gamma.app | AI生成 | ✅ |
| 优品PPT | 国内模板 | ✅ |
| OfficePlus | 微软官方 | ✅ |

### Step 3: 写内容（10分钟）

**单页万能公式**：
```
1个标题 + 3个要点 + 1个图表/数字
```

**万能5页结构**：
```
P1: 封面（标题 + 副标题）
P2: 问题（为什么做这件事）
P3: 方案（我们怎么做）
P4: 成果（数据/案例）
P5: 结尾（谢谢 + 联系方式）
```

### Step 4: 排版（5分钟）

**核心原则**：
- **留白**：页面边缘留 2cm
- **对齐**：文字/图片边缘对齐
- **对比**：重点用颜色/加粗/加大

### Step 5: 优化（5分钟）

**检查清单**：
```
□ 10-20-30 法则：
  - 10 页以内
  - 20 分钟以内
  - 30 号字体以上

□ 3 秒原则：3 秒能看懂这页说什么

□ 一页一观点：去掉标题还知道重点吗？
```

---

## 第二部分：专业6阶段法

### Phase 1: 需求分析

**必须收集**：

| 问题 | 目的 |
|------|------|
| 演讲时长？ | 控制页数（1分钟/页） |
| 听众是谁？ | 确定专业度和术语 |
| 核心目标？ | 说服/告知/激励/行动 |
| 交付形式？ | 现场 / 异步 / PDF |

### Phase 2: 结构选型

**内容类型 → 叙事模型**：

| 类型 | 模型 | 适用场景 |
|------|------|----------|
| 问题解决 | SCQA | 技术转型、问题排查 |
| 理念传播 | 黄金圈 | 产品发布、团队文化 |
| 复杂系统 | ZUI缩放 | 系统架构、技术全景 |
| 培训教学 | 洋葱结构 | 内部分享、技能培训 |
| 工作汇报 | 总分总 | 季度总结、成果汇报 |

**SCQA 模板**：

```markdown
- [S] Situation - 共识背景
- [C] Complication - 冲突/变化  
- [Q] Question - 核心疑问
- [A] Answer - 解决方案
```

**黄金圈模板**：

```markdown
- [WHY] 信念/动机
- [HOW] 方法/差异
- [WHAT] 产品/成果
```

### Phase 3: 内容工程

**黄金3原则**：
1. **一页一观点** — 去掉标题，内容仍支撑同一论点
2. **3秒可理解** — 关键信息3秒内传达
3. **少即是多** — 能删则删

**数据叙事三要素**：
- 时间轴：展示变化过程
- 对比锚："相当于XX个..."
- 交互点：二维码链接详情

### Phase 4: 视觉设计

**设计系统**：

```yaml
colors:
  primary: "#007AFF"   # 主色
  secondary: "#34C759" # 正向
  accent: "#FF9500"    # 强调
  bg_light: "#FFFFFF"
  bg_dark: "#1a1a2e"

typography:
  heading: "Inter Bold"
  body: "Inter Regular"
  min_size: 24  # 中文最小24pt
```

**返璞归真检查**：
- [ ] 色彩：只用1个强调色？
- [ ] 字体：单一家族？
- [ ] 留白：内容<50%？
- [ ] 动画：仅"出现/平滑"？

### Phase 5: 工具链

**工具矩阵**：

| 场景 | 首选 | 备选 |
|------|------|------|
| 快速生成 | Gamma.app | Canva |
| 专业设计 | Figma | Sketch |
| 代码演示 | Slidev | Reveal.js |
| 数据图表 | Flourish | D3.js |
| 架构图 | Mermaid | PlantUML |
| 程序化生成 | python-pptx | - |

**Python-pptx 核心模板**：

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

class PPTBuilder:
    def __init__(self):
        self.prs = Presentation()
        self.blue = RGBColor(0, 122, 255)
        
    def title_slide(self, title, subtitle=None):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        # 标题
        box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(1))
        p = box.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(54)
        p.font.bold = True
        p.alignment = PP_ALIGN.CENTER
        return slide
        
    def content_slide(self, title, bullets):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        # 标题
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.8))
        title_box.text_frame.paragraphs[0].text = title
        title_box.text_frame.paragraphs[0].font.size = Pt(40)
        title_box.text_frame.paragraphs[0].font.bold = True
        
        # 要点
        top = Inches(1.8)
        for bullet in bullets[:3]:
            box = slide.shapes.add_textbox(Inches(0.5), top, Inches(9), Inches(0.6))
            box.text_frame.paragraphs[0].text = f"• {bullet}"
            box.text_frame.paragraphs[0].font.size = Pt(24)
            top += Inches(0.7)
        return slide
        
    def save(self, filename):
        self.prs.save(filename)
        print(f"✅ 已保存: {filename}")

# 使用
ppt = PPTBuilder()
ppt.title_slide("标题", "副标题")
ppt.content_slide("核心观点", ["要点1", "要点2", "要点3"])
ppt.save("output.pptx")
```

### Phase 6: 质量核查

**AQAL 四象限**：

| 象限 | 检查项 | 自检问题 |
|------|--------|----------|
| 内容 | 单页单观点 | 去掉标题还知道说什么？ |
| 逻辑 | 页间过渡 | 上页和下页什么关系？ |
| 视觉 | 3米测试 | 站在门口能看到什么？ |
| 技术 | 故障降级 | 断网还能看吗？ |

---

## 第三部分：避坑指南

### 新手常犯错误

| 错误 | 结果 | 修正 |
|------|------|------|
| 字太多 | 没人看 | 每页 ≤ 6 行 |
| 花哨动画 | 显业余 | 最多 2 种 |
| 颜色乱 | 廉价感 | 最多 2 种 |
| 没重点 | 记不住 | 每页 1 个重点 |

### 避坑清单

- ❌ 别用宋体 → ✅ 微软雅黑/Inter
- ❌ 别用艺术字 → ✅ 干净简洁
- ❌ 别用彩色背景 → ✅ 深色/浅色
- ❌ 别超过 10 页 → ✅ 精简精简
- ❌ 别用衬线字体 → ✅ 无衬线

---

## 第四部分：模板库

### 快速模板（5页）

```
P1: 封面 → 标题 + 副标题
P2: 问题 → 为什么做
P3: 方案 → 怎么做
P4: 成果 → 数据/案例
P5: 结尾 → 谢谢 + 联系方式
```

### 标准模板（8页）

```
P1: 封面
P2: 背景/问题
P3: 解决方案
P4: 方案详情
P5: 数据/成果
P6: 对比/优势
P7: 总结/行动
P8: Q&A
```

### SCQA 模板（10页）

```
P1: 封面
P2-3: S 背景共识
P4-5: C 冲突挑战
P6: Q 核心问题
P7-8: A 解决方案
P9: 总结 + 行动
P10: Q&A
```

---

## 输出格式

用户说"帮我做PPT"时：

```markdown
## PPT 设计指南

### 模式选择
[快速5步法 / 专业6阶段法]

### 建议结构
- P1: {封面}
- P2: {背景/问题}
...

### 工具推荐
- {Canva / PPT / Slidev / python-pptx}

### 避坑提醒
- 别超过 {X} 页
- 每页 ≤ {X} 个要点

---
### 生成内容
[具体代码/模板]
```
