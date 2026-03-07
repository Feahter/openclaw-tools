---
name: screenshot
description: "使用系统原生工具截取屏幕截图或窗口截图"
triggers:
  - "截图"
  - "screenshot"
  - "屏幕截图"
  - "截屏"
source:
  project: screenshot-skill
  url: https://github.com/Feahter/openclaw-tools
  license: MIT
---

# Screenshot Skill

使用 macOS 原生 `screencapture` 工具进行屏幕截图。

## 使用方式

### 截取整个屏幕

```bash
screenshot full
```

### 截取交互式区域（用户选择窗口/区域）

```bash
screenshot interactive
```

### 截取特定窗口

```bash
screenshot window <窗口名>
```

### 截取指定区域（交互式选择）

```bash
screenshot region
```

## 输出位置

| 类型 | 默认路径 |
|------|----------|
| 屏幕截图 | `~/Desktop/screenshot_YYYYMMDD_HHMMSS.png` |
| 临时文件 | `/tmp/screenshot_*.png` |

## 注意事项

- 首次使用需要授予屏幕录制权限
- macOS 会在首次弹窗请求权限
- 选择"系统偏好设置 > 安全性与隐私 > 隐私 > 屏幕录制"确保已授权

## 依赖

- macOS 系统
- `screencapture` 命令（macOS 原生）
