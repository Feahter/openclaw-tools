# OpenClaw Tools & Skills

我的个人 AI Agent 工作空间工具集和 Skills 库。

## 📦 目录结构

```
openclaw-tools/
├── tools/           # 实用工具脚本
│   ├── morning-briefing.py     # 晨间简报生成器
│   ├── system-dashboard.py     # 系统仪表盘
│   ├── daily-surprise.py       # 每日惊喜
│   ├── skill-quality-manager.py # Skills 质量管理
│   ├── aqa-auto-decider.py     # AQA 自动决策器
│   └── ...
├── skills/          # Skills 集合
│   ├── autonomous-brain/       # 自主 AI 大脑
│   ├── skill-creator/         # 技能创建器
│   ├── data-analyst/           # 数据分析
│   ├── ai-rag-pipeline/        # RAG 管道
│   └── ...
├── HEARTBEAT.md     # 心跳任务配置
└── README.md        # 本文件
```

## 🛠️ 工具说明

| 工具 | 功能 | 使用 |
|------|------|------|
| `morning-briefing.py` | 生成今日天气+任务摘要 | `python tools/morning-briefing.py` |
| `system-dashboard.py` | 实时系统监控 | `python tools/system-dashboard.py` |
| `skill-quality-manager.py` | Skills 评分与优化 | `python tools/skill-quality-manager.py --dry-run` |
| `aqa-auto-decider.py` | 自动决策创建 Skills | `python tools/aqa-auto-decider.py` |

## 🧠 Skills 分类

- **核心代理**: autonomous-brain, agent-autonomy-kit, reflect-learn
- **开发工具**: skill-creator, skill-from-github, coding-agent
- **数据分析**: data-analyst, data-visualization, big-data-analysis
- **自动化**: automation-workflows, workflow-automation, cron-scheduling
- **系统监控**: system-monitor, process-monitor, server-health

## 🔄 心跳任务

每小时自动执行：
1. Skills 维护
2. 自动知识获取
3. 进化分析
4. 质量管理 (SQM)
5. AQA 自动决策

## 🚀 快速开始

```bash
# 安装依赖
pip install psutil aiohttp

# 运行工具
python tools/tools-suite.py

# 心跳任务
python tools/unified-heartbeat.py
```

---

*Last Updated: 2026-02-11*
