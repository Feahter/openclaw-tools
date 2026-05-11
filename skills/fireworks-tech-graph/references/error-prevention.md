# Error Prevention — 常见错误 + 恢复协议

---

## 验证清单（每次生成后必做）

```bash
rsvg-convert output.svg -o /dev/null 2>&1 && echo "✓ Valid SVG" || echo "✗ Error found"
```

**4项必查**：
1. ✅ **箭头-节点碰撞**：箭头不能穿过节点内部（用正交路由绕行）
2. ✅ **文本溢出**：文字必须适配容器（估算：`text.length × 7px ≤ width - 16px`）
3. ✅ **箭头-文字对齐**：箭头端点连到形状边缘（不是悬空）；所有箭头标签有背景 rect
4. ✅ **容器边界**：箭头从分组容器的空隙进出，不穿内部节点

---

## 常见语法错误

| 错误 | 错误写法 | 正确写法 |
|------|---------|---------|
| 缺 y 属性 | `yt-anchor="middle"` | `y="60" text-anchor="middle"` |
| 缺 y 属性 | `x="390` | `x="390" y="250"` |
| 颜色无引号 | `fill=#fff` | `fill="#ffffff"` |
| marker 引用 | `marker-end=` | `marker-end="url(#arrow)"` |
| 路径数值 | `L 29450` | `L 290,220` |
| 缺闭合标签 | `...<svg>` 无 `</svg>` | 确认 `</svg>` 在文件末尾 |
| 颜色格式 | `stroke: 2px` | `stroke-width="2"`（XML 属性） |

---

## Jump-Over 交叉处理

**当两条箭头必须交叉时**：

```xml
<!-- 下层：白色背景弧线跳到上方 -->
<path d="M 300,200 a 6,6 0 0,1 12,0" 
      fill="none" stroke="white" stroke-width="4"/>
<!-- 上层：实际箭头 -->
<path d="M 300,200 L 400,300" 
      stroke="#2563eb" stroke-width="2" marker-end="url(#arrowB)"/>
```

**多个交叉**：交错半径（5px, 7px, 9px）避免重叠

---

## 错误恢复协议

### 失败时三步走

**第1次失败** → 根因分析，针对性修复
- 检查 `rsvg-convert` 报错的具体行号
- 对照常见语法错误表定位问题

**第2次失败** → 换方法
- Python list 方法 → 模板脚本
- 或反过来

**第3次失败** → 停止，报告用户
- 不要无限循环修复
- 简化为更小的图（少节点、少边）

---

## Python List 方法检查表

使用 `lines = []` 方法时：

- [ ] `<?xml version="1.0"?>` 在第一行
- [ ] `xmlns="http://www.w3.org/2000/svg"` 在 `<svg>` 标签
- [ ] `viewBox` 属性存在
- [ ] 每个 `lines.append()` 末尾有换行符（`'\n'.join` 时）
- [ ] `escape()` 处理所有用户输入文本（防止 XML 注入）
- [ ] `marker id` 在 `<defs>` 内
- [ ] `marker-end` 引用正确的 `url(#id)`
- [ ] `</svg>` 在最后一行
