# OpenClaw Skills

> 200+ AI Agent Skills for OpenClaw

## 📦 安装

```bash
# 方式1: 从 ClawdHub 安装
clawdhub install <skill-name>

# 方式2: 从 GitHub 克隆
git clone https://github.com/Feahter/openclaw-tools.git
```

## 🗂️ 分类索引

### 🔧 开发工具 (Development)
| Skill | 描述 |
|-------|------|
| `coding-agent` | 运行 Codex / Claude Code / OpenCode |
| `github` | GitHub CLI 操作 |
| `github-to-skills` | GitHub 仓库转 Skill |
| `git-workflow-master` | Git 工作流专家 |
| `code-review-expert` | 代码审查专家 |
| `skill-creator` | 创建和优化 Skills |
| `skill-manager` | Skills 生命周期管理 |
| `skill-vetter` | Skills 安全审核 |

### 🌐 浏览器 & 自动化 (Browser & Automation)
| Skill | 描述 |
|-------|------|
| `browser` | 浏览器自动化 |
| `agent-browser` | Headless 浏览器 |
| `playwright` | Playwright 自动化 |
| `smart-browser` | AI 增强浏览器 |
| `computer-use` | 桌面自动化 (Linux) |
| `mac-use` | macOS GUI 自动化 |

### 📄 文档处理 (Documents)
| Skill | 描述 |
|-------|------|
| `pdf` | PDF 处理 |
| `docx` | Word 文档 |
| `pptx` | PPT 演示文稿 |
| `xlsx` | Excel 表格 |
| `canvas-design` | Canvas 视觉设计 |
| `frontend-slides` | HTML 幻灯片 |

### 🧠 AI & 机器学习 (AI/ML)
| Skill | 描述 |
|-------|------|
| `ai-rag-pipeline` | RAG 流水线 |
| `agency-model-qa` | ML 模型质量审计 |
| `agency-data-engineer` | 数据工程 |
| `mcp-builder` | MCP 服务器开发 |
| `mcporter` | MCP 工具调用 |

### ☁️ DevOps & 运维 (DevOps)
| Skill | 描述 |
|-------|------|
| `agency-devops-automator` | DevOps 自动化 |
| `server-health` | 服务器健康检查 |
| `security-monitor` | 安全监控 |
| `cron-scheduling` | Cron 任务管理 |
| `database` | 数据库管理 |
| `db-query` | 数据库查询 |

### 📱 平台集成 (Integrations)
| Skill | 描述 |
|-------|------|
| `feishu` | 飞书机器人 |
| `apple-notes` | Apple Notes |
| `sonoscli` | Sonos 音响控制 |
| `obsidian` | Obsidian 笔记 |
| `a2achat` | Agent 消息通讯 |

### 🧠 记忆 & 认知 (Memory & Cognition)
| Skill | 描述 |
|-------|------|
| `spen-memory` | SPEN 记忆系统 |
| `context-manager` | 上下文管理 |
| `para-second-brain` | 第二大脑 |
| `infinite-memory` | 无限记忆 |
| `agent-autonomy-kit` | 自主 Agent 套件 |

### ✍️ 创作 & 写作 (Creative)
| Skill | 描述 |
|-------|------|
| `novel-writing-sop` | 小说创作 SOP |
| `novel-quality-guardian` | 小说质量守护 |
| `story-architect` | 故事架构师 |
| `one-sentence-novel` | 一句话小说 |
| `content-editor` | 内容审稿 |
| `folk-marketing` | 民间营销文案 |

### 🧩 思维模型 (Thinking)
| Skill | 描述 |
|-------|------|
| `six-thinking-hats` | 六顶思考帽 |
| `blade-of-logic` | 逻辑之刃 |
| `hammer-of-questions` | 问题之锤 |
| `ladder-of-abstraction` | 抽象之梯 |
| `mirror-of-perspectives` | 视角之镜 |
| `talent-mind` | 天才思维 |

### 📊 数据分析 (Data)
| Skill | 描述 |
|-------|------|
| `data-analyst` | 数据分析 |
| `performance-optimizer` | 性能优化 |
| `jq-json-processor` | JSON 处理 |
| `dash-cog` | 数据可视化仪表盘 |

---

## 🔄 更新

```bash
# 生成 marketplace
python3 scripts/generate-marketplace.py

# 推送到 GitHub
git add -A && git commit -m "chore: update skills" && git push
```

## 📝 添加新 Skill

1. 在 `skills/` 下创建目录
2. 添加 `SKILL.md` (含 name/description frontmatter)
3. 提交并推送

---
Generated: 2026-03-13 | Total: 200+ Skills
