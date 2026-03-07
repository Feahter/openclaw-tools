# OpenClaw Siri 语音助手配置指南

## 效果
- 说："嘿 Siri，问 OpenClaw"
- 弹出语音输入框 → 你说话
- Siri 把我的回复朗读出来

---

## 第一步：创建 Shortcuts

1. 打开 **Shortcuts.app**（快捷指令）
2. 点击右上角 **+** 创建新快捷指令
3. 点击顶部重命名为：**"问 OpenClaw"**

---

## 第二步：添加动作

### 动作 1：获取输入
1. 搜索添加 **"听写文本"**
2. 设置：
   - 语言：**中文（普通话）**
   - 停止聆听：**在暂停之后**

### 动作 2：发送到 OpenClaw
1. 搜索添加 **"运行 Shell 脚本"**
2. 输入以下代码：

```bash
# 发送消息给 OpenClaw 并获取回复
MESSAGE="$1"

# 方式1: 使用 openclaw CLI（如果有）
# REPLY=$(openclaw send "$MESSAGE" 2>/dev/null)

# 方式2: 写入文件触发（更稳定）
TIMESTAMP=$(date +%s)
LOG_FILE="/Users/$USER/.openclaw/workspace/data/siri-requests.log"
echo "[$TIMESTAMP] $MESSAGE" >> "$LOG_FILE"

# 模拟回复（实际使用时需要轮询或 WebSocket）
echo "收到: $MESSAGE"
```

### 动作 3：朗读回复
1. 搜索添加 **"朗读文本"**
2. 设置为上一个动作的输出

---

## 第三步：设置 Siri 触发

1. 点击右上角 **...**
2. 点击 **"设置"**
3. 打开 **"使用 Siri 运行"**
4. 设置短语：**"问 OpenClaw"**

---

## 第四步：测试

1. 说：**"嘿 Siri，问 OpenClaw"**
2. 弹出输入框后说话
3. 等待 Siri 朗读回复

---

## 进阶：真正的实时对话

上面的方案只能单次问答。要实现连续对话，需要：

### 方案 A：Shortcuts 循环（推荐）
在快捷指令中添加 **"重复"** 动作，让用户选择是否继续对话。

### 方案 B：专用 App/ menubar
用 Swift 写一个菜单栏应用，常驻后台，监听全局快捷键。

---

## 替代方案：直接用 AppleScript

更简单的方案 - 保存为 `ask-openclaw.scpt`：

```applescript
-- 请求语音输入
set userInput to text returned of (display dialog "请说话:" default answer "" buttons {"取消", "发送"} default button "发送")

-- 调用 OpenClaw（需要安装 openclaw CLI）
do shell script "openclaw send '" & userInput & "'"

-- 显示回复（需要实现获取回复的逻辑）
display notification "消息已发送" with title "OpenClaw"
```

运行：`osascript ask-openclaw.scpt`

---

## 需要我帮你实现哪个？

1. **基础版**：上面的 Shortcuts 配置（5 分钟）
2. **进阶版**：带循环的连续对话（10 分钟）
3. **高级版**：菜单栏应用（需要写 Swift 代码，30 分钟）
