# OpenClaw 语音方案 A - 完整指南

## 你需要什么

- macOS 12.6+
- 终端（Terminal.app 或 iTerm）
- 可选：Raycast/Alfred（用于快捷键）

---

## 安装依赖

```bash
# 安装 sox（用于录音）
brew install sox

# 给脚本执行权限
chmod +x ~/.openclaw/workspace/tools/voice-quick.sh
chmod +x ~/.openclaw/workspace/tools/voice-reader.sh
```

---

## 使用方法

### 第 1 步：启动语音回复监听

在一个终端窗口保持运行：

```bash
~/.openclaw/workspace/tools/voice-reader.sh
```

这个窗口会：
- 自动检测我给你的新回复并朗读
- 也可以直接输入文字让它朗读

**保持这个窗口开着！**

---

### 第 2 步：语音输入

**方式 A：直接运行**

```bash
~/.openclaw/workspace/tools/voice-quick.sh
```

**方式 B：绑定到快捷键（推荐）**

#### 用 Raycast 设置快捷键：

1. 安装 [Raycast](https://raycast.com/)（免费）
2. 打开 Raycast → 设置 → Extensions
3. 点击 "+" → "Add Script Command"
4. 配置：
   - 标题：语音问 OpenClaw
   - 命令：`~/.openclaw/workspace/tools/voice-quick.sh`
   - 快捷键：`⌃⌥Space`（或其他你喜欢的组合）

#### 或用 macOS Automator：

1. 打开 Automator.app
2. 新建「快速操作」
3. 左侧搜索「运行 Shell 脚本」
4. 输入：`~/.openclaw/workspace/tools/voice-quick.sh`
5. 保存为「OpenClaw Voice」
6. 系统设置 → 键盘 → 键盘快捷键 → 服务 → 找到「OpenClaw Voice」→ 设置快捷键

---

### 第 3 步：完整流程

1. **按快捷键** `⌃⌥Space`
2. **听到「叮」一声** → 开始说话
3. **按 Enter 停止** → 听到「咚」一声
4. **弹出对话框** 显示识别的文字（或让你手动输入）
5. **点击「发送」** → 文字已复制到剪贴板
6. **粘贴到这里发给我**
7. **我回复后**，语音监听窗口自动朗读

---

## 快速测试

不装任何东西，先测试语音效果：

```bash
# 测试 say 命令
say -v "Ting-Ting" "你好，这是测试语音"

# 启动语音监听（保持运行）
~/.openclaw/workspace/tools/voice-reader.sh
```

然后在另一个终端：

```bash
# 模拟我给你的回复
echo "这是 OpenClaw 的回复，你听到了吗？" > ~/.openclaw/workspace/data/voice-response.txt
```

如果听到朗读，说明系统正常！

---

## 进阶：安装 Whisper（更好的语音识别）

```bash
# 等网络好的时候再装
brew install whisper.cpp

# 下载中文模型（约 150MB）
whisper --model small --language Chinese --download-model-only
```

装好后，`voice-quick.sh` 会自动使用 Whisper 识别，准确率更高。

---

## 问题排查

### "sox 未安装"
```bash
brew install sox
```

### "没有权限"
```bash
chmod +x ~/.openclaw/workspace/tools/*.sh
```

### "听不到声音"
- 检查系统音量
- 试试：`say "测试"`
- 检查语音监听窗口是否在运行

---

## 简化版（不想折腾）

如果你不想装 sox 或设置快捷键：

**只运行语音监听：**
```bash
~/.openclaw/workspace/tools/voice-reader.sh
```

然后：
1. 用 macOS 自带「听写」按 Fn-Fn 说话
2. 把识别结果复制给我
3. 我把回复保存到文件，自动朗读

这是最简化的方案，5 分钟就能用。

---

## 下一步

准备好了吗？
1. 先运行 `say -v "Ting-Ting" "测试语音"` 确认能出声
2. 启动语音监听：`~/.openclaw/workspace/tools/voice-reader.sh`
3. 告诉我你想绑定什么快捷键，我帮你配置
