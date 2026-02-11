# 🧰 OpenClaw 小工具合集

## 工具列表

### 1. 🌅 晨间简报 (morning-briefing.py)
每天早上生成今日摘要页面。

**功能：**
- 🌤️ 天气信息（上海）
- 📋 待办任务统计
- 💬 每日励志语录

**使用：**
```bash
python tools/morning-briefing.py
# 输出: public/morning-briefing-YYYY-MM-DD.html
```

### 2. 📊 系统仪表盘 (system-dashboard.py)
实时监控系统资源使用情况。

**功能：**
- 🖥️ CPU 使用率
- 🧠 内存使用率  
- 💾 磁盘空间
- 🌐 网络流量
- ⚡ Top 进程

**使用：**
```bash
# 交互模式（自动刷新 + 浏览器打开）
python tools/system-dashboard.py

# 静态模式（生成单页 HTML）
python tools/system-dashboard.py --static
# 访问: http://localhost:8765
```

### 3. 🎁 每日惊喜 (daily-surprise.py)
随机获取鼓励语、功能提示、彩蛋。

**功能：**
- 随机鼓励语
- OpenClaw 使用技巧
- 有趣的彩蛋
- 冷知识分享

**使用：**
```bash
# 单次惊喜
python tools/daily-surprise.py

# 带系统通知
python tools/daily-surprise.py --notify

# 循环模式（每小时一次）
python tools/daily-surprise.py --loop
```

### 4. 🚀 工具合集 (tools-suite.py)
统一管理所有小工具。

**使用：**
```bash
python tools/tools-suite.py
```

---

## 📅 自动运行设置

### 每天早上 7 点生成晨间简报
```bash
crontab -e
# 添加：
0 7 * * * cd ~/.openclaw/workspace && python tools/morning-briefing.py
```

### 每小时随机惊喜
```bash
crontab -e
# 添加：
0 * * * * cd ~/.openclaw/workspace && python tools/daily-surprise.py --notify
```

---

## 📁 输出文件

| 工具 | 输出位置 |
|------|---------|
| 晨间简报 | `public/morning-briefing-YYYY-MM-DD.html` |
| 系统仪表盘 | `public/dashboard.html` (静态模式) |

---

## 🔧 依赖

- Python 3.10+
- psutil (`pip install psutil`)

```bash
pip install psutil
```

---

*生成时间: 2026-02-10*
