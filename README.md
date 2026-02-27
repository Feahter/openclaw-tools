# OpenClaw Tools & Skills

我的个人 AI Agent 工作空间工具集和 Skills 库。

## 📦 目录结构

```
openclaw-tools/
├── tools/              # 实用工具脚本 (74个)
│   ├── INDEX.md        # 工具索引
│   ├── unified-heartbeat.py    # 统一心跳任务
│   ├── auto-knowledge-pipeline.py  # 自动知识获取
│   ├── aqa-auto-decider.py      # AQA 自动决策
│   ├── skill-quality-manager.py  # Skills 质量管理
│   ├── health-check.py           # 健康检查
│   ├── auto-backup.py            # 自动备份
│   └── ...
├── skills/             # Skills 集合 (78个)
│   ├── fast-edit/     # AI 文件编辑
│   ├── pdf/           # PDF 处理
│   ├── docx/          # Word 文档
│   ├── xlsx/          # Excel 处理
│   ├── pptx/          # PPT 制作
│   ├── gitnexus/      # 代码知识图谱
│   └── ...
└── HEARTBEAT.md       # 心跳任务配置
```

## 🛠️ 核心工具

### 心跳/调度
| 工具 | 功能 |
|------|------|
| `unified-heartbeat.py` | 统一心跳任务 (每小时) |
| `event-scheduler.py` | 事件驱动调度器 |
| `health-check.py` | 系统健康检查 |

### 知识获取
| 工具 | 功能 |
|------|------|
| `auto-knowledge-pipeline.py` | 自动从 GitHub 获取高分项目 |
| `aqa-auto-decider.py` | 自动决策创建 Skills |

### 质量管理
| 工具 | 功能 |
|------|------|
| `skill-quality-manager.py` | Skills 评分与优化 |
| `auto-backup.py` | 关键数据自动备份 |

## 🧠 Skills 分类

### 文档/媒体处理 (9)
pdf, docx, xlsx, pptx, pdfcpu, ImageToolbox, bat, nodeppt, fast-edit

### AI/LLM (10)
llm-app, llmware, pydantic, valibot, superstruct, composio, tavily-search, memory-on-demand, proactive-agent, qmd

### 系统/运维 (9)
kubernetes, airflow, prometheus, coroot, uptime-kuma, telegraf, dive, ohmyzsh, thingsboard

### 开发工具 (6)
fastapi, gin, gatsby, prettier, playwright, puppeteer

### API/集成 (5)
mcp-builder, apollo-client, openapi-generator, redis, redisson

### 数据分析 (5)
spark, datasets, mage-ai, haystack, langflow

### DevOps/工具 (8)
computer-use, agent-browser-0, dive, ModSecurity, skill-vetter, tools, repomix, whatsapp-web.js

### 测试/编辑 (5)
playwright, puppeteer, lint-staged, fast-edit

### 自动化/工作流 (4)
huginn, insomnia, workflow-automation

### 专业工具 (6)
algorithm-toolkit, design-resources-for-developers, the-book-of-secret-knowledge, markitdown, writer, memvid

### 开发框架 (6)
gitnexus, gitnexus-debugging, gitnexus-exploring, gitnexus-impact-analysis, gitnexus-refactoring

### 知识/研究 (4)
auto-knowledge-acquisition, deer-flow, memvid, qmd

## 🔄 心跳任务

每小时自动执行：
1. **Skills 维护** - 检查更新、发现新技能
2. **知识获取** - 自动搜索 GitHub 高分项目
3. **进化分析** - 记录成功模式、追踪改进
4. **质量管理 (SQM)** - 评分、优化 Skills
5. **AQA 自动决策** - 决策是否创建新 Skills

每天 9:00 自动执行：
- **财富研究** - 搜索被动收入模式
- **健康研究** - 搜索抗衰老前沿

## 📊 统计

- **工具**: 74 个 Python 脚本
- **Skills**: 78 个
- **有心跳任务**: 3 个

## 🔗 相关链接

- [OpenClaw 文档](https://docs.openclaw.ai)
- [ClawHub](https://clawhub.com)
