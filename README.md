# OpenClaw Skills

> 146+ AI Agent Skills for OpenClaw | Last updated: 2026-04-03

## 📦 安装

```bash
# 方式1: 从 ClawdHub 安装
clawdhub install <skill-name>

# 方式2: 从 GitHub 克隆
git clone https://github.com/Feather/openclaw-tools.git
```

## 🗂️ 分类索引

### 🔧 开发工具 (Development)
| Skill | 描述 |
|-------|------|
| `coding-agent` | 多 CLI Agent 协调（Codex/Claude/OpenCode） |
| `github` | GitHub CLI 操作 |
| `github-to-skills` | GitHub 仓库转 Skill |
| `git` | Git 工作流规范 |
| `skill-creator` | 创建和优化 Skills |
| `skill-from-github` | 从 GitHub 项目创建 Skill |
| `skill-from-notebook` | 从文档提取方法论创建 Skill |
| `skill-orchestrator` | 技能编排器 |
| `skill-evolution-manager` | Skill 迭代改进管理 |
| `skill-manager` | Skills 生命周期管理 |
| `skill-vetter` | Skills 安全审核 |
| `openclaw-agent-optimize` | OpenClaw 代理优化 |
| `openclaw-token-optimizer` | Token 用量优化 |
| `agent-dispatch` | Agent 注册与路由 |
| `agent-commander` | Agent 会话管理 |
| `rescueclaw` | 操作回滚安全系统 |
| `chinese-name-lookup` | 八字喜用神 + 生肖 + 神煞 + 大运流年姓名分析 |
| `skill-tench-hunter` | 技术研究猎手 — 多源输入到结构化报告 |
| `skill-project-butcher` | GitHub 项目深度分析 |
| `skill-from-masters` | 基于专家方法论创建高质量 Skills |
| `skill-agent-creator` | Skill 创建与编排 |
| `skill-algo-researcher` | 算法研究助手 |
| `skill-algorithm-master` | 算法工具 — 查/实现算法和数据结构 |
| `skill-taste-calibrator` | AI 品味校准与判断力进化 |
| `skill-template-layered-retrieval` | 文档分层检索模板 |
| `test-driven-development` | TDD — RED-GREEN-REFACTOR 流程 |
| `finishing-a-development-branch` | 分支完成决策指导 |
| `using-git-worktrees` | Git Worktree 隔离开发 |
| `code-review-expert` | 专家级代码审查 |
| `db-query` | 数据库查询 + SSH 隧道管理 |
| `task-workflow` | 复杂任务规划 + 子Agent + 进度报告工作流 |

### 🌐 浏览器 & 自动化 (Browser & Automation)
| Skill | 描述 |
|-------|------|
| `browser-automation` | CLI 浏览器自动化 |
| `stagehand-browser-cli` | Stagehand 浏览器自动化 |
| `agent-browser` | Rust 无头浏览器 CLI |
| `agent-browser-clawdbot` | agent-browser 的 Clawdbot 适配 |
| `smart-browser` | AI 增强浏览器 |
| `playwright-scraper-skill` | Playwright 爬虫 |
| `playwright-browser-automation` | Playwright API 调用 |
| `computer-use` | 桌面自动化 (Linux/Xvfb/XFCE) |
| `mac-use` | macOS GUI 操控 |
| `screenshot` | 截图工具 |
| `bb-browser` | 浏览器命令行 — 36平台 103命令 |
| `lightpanda` | 轻量级浏览器替代 Chrome/OpenClaw 默认 |
| `webapp-testing` | Playwright 本地 Web 应用测试 |

### 📄 文档处理 (Documents)
| Skill | 描述 |
|-------|------|
| `pdf` | PDF 全功能（读取/合并/拆分/OCR/水印） |
| `docx` | Word 文档全功能 |
| `pptx` | PPT 全功能 |
| `xlsx` | Excel 全功能 |
| `frontend-slides` | HTML 演示文稿生成 |
| `generative-ui` | 交互式 HTML 组件/可视化 |
| `svg-card-generator` | SVG 卡片可视化 |
| `pdf-text-extractor` | PDF 文本提取 |
| `anthropics-pdf` | Anthropic 官方 PDF 处理 |
| `anthropics-docx` | Anthropic 官方 Word 处理 |
| `anthropics-pptx` | Anthropic 官方 PPT 处理 |
| `anthropics-xlsx` | Anthropic 官方 Excel 处理 |
| `ppt-design-guide` | PPT 制作完整指南 |
| `qmd` | 本地搜索/索引 CLI（BM25 + vectors + rerank）+ MCP 模式 |
| `pretext-integration` | Pretext 集成 |

### 🧠 AI & 机器学习 (AI/ML)
| Skill | 描述 |
|-------|------|
| `ai-rag-pipeline` | RAG 管道（Tavily/Exa/Claude/GPT-4） |
| `mcp-builder` | MCP Server 开发完整指南 |
| `mcporter` | MCP Server CLI 管理 |
| `agency-mcp-builder` | MCP 开发 agent 角色卡 |
| `chromadb` | ChromaDB 向量数据库 |
| `tavily-search` | Tavily AI 搜索 |
| `rag-search` | 最小化 RAG 搜索 |
| `deepset-ai` | Haystack AI 编排框架 |
| `auto-knowledge-acquisition` | GitHub 高质量项目发现与笔记 |
| `oss-code-analysis` | 开源项目源码分析 |
| `sw-data-scientist` | 结构化数据分析工作流 |
| `autoresearch-skill` | 自动优化 Skill — Karpathy autoresearch 方法 |
| `find-skills` | 技能发现与安装 |
| `skillhub-preference` | SkillHub 优先 + ClawdHub fallback |
| `model-usage` | CodexBar 模型用量/成本分析 |
| `r-wmi` | Rokid 智能眼镜控制 |

### ☁️ DevOps & 运维 (DevOps)
| Skill | 描述 |
|-------|------|
| `proxmox-ops` | Proxmox VE 管理 |
| `cron-scheduling` | Cron + systemd 定时任务 |
| `cron-mastery` | OpenClaw Cron/Heartbeat 系统 |
| `cron-writer` | 自然语言 → cron 表达式 |
| `automation-workflows` | 自动化工作流设计 |
| `server-health` | 服务器健康监控 |
| `security-monitor` | 安全监控告警 |
| `process-monitor` | 进程监控 |
| `tmux` | tmux 远程控制 |
| `macbook-optimizer` | MacBook 全面优化 |
| `system-health-reporter` | 系统健康报告 |
| `cloudflare-proxy` | Cloudflare GFW 穿透 |
| `openclaw-auto-updater` | OpenClaw & Skill 自动更新 |
| `workflow-automation` | ETL 流水线 & DAG 工作流自动化 |

### 📱 平台集成 (Integrations)
| Skill | 描述 |
|-------|------|
| `feishu` | 飞书 AI 机器人 |
| `feishu-debug` | 飞书机器人故障排查 |
| `apple-notes` | Apple Notes CLI 管理 |
| `obsidian` | Obsidian 笔记管理 |
| `a2achat` | Agent-to-Agent 消息通信 |
| `clawdhub` | ClawdHub 技能市场 CLI |
| `summarize` | URL/文件/音频摘要 |
| `tapestry` | 知识图谱构建 |
| `openai-whisper` | 本地语音转文字 |
| `sonoscli` | Sonos 音箱控制 |
| `agent-reach` | Web 抓取 — Twitter/Reddit/YouTube/Bilibili 等 |
| `fast-edit` | 大文件编辑、批量修改、剪贴板粘贴 |
| `navclaw` | AI 导航 — 路线/堵车查询 |
| `session-context` | 会话上下文管理 |
| `session-insights` | 会话洞察分析 |

### 🧠 记忆 & 认知 (Memory & Cognition)
| Skill | 描述 |
|-------|------|
| `lobster-evolution` | Skill 自动进化引擎 — 探针→提案→实施→自愈 |
| `spen-memory` | SPEN 时空记忆系统 |
| `para-second-brain` | PARA 知识管理 + 语义搜索 |
| `basal-ganglia-memory` | 习惯形成/程序性学习 |
| `memory-on-demand` | 按需记忆检索 |
| `attention-system` | 注意力分析与正反馈捕获 |
| `agent-autonomy-kit` | Agent 自主执行工具包 |
| `reflect-learn` | 对话分析自我改进 |
| `self-improving-agent` | 自我改进系统 |
| `proactive-agent` | Agent 主动性增强 |

### ✍️ 创作 & 写作 (Creative)
| Skill | 描述 |
|-------|------|
| `novel-writing-sop` | 小说创作 SOP |
| `novel-quality-guardian` | 小说质量守护 |
| `story-architect` | 世界观/情节/人物创作 |
| `content-editor` | 审稿润色系统 |
| `auto-content-creator` | 多平台内容自动生成 |
| `writer` | 修正 AI 写作模式 |
| `game-engine` | HTML5/Canvas/WebGL 游戏引擎 |
| `game-designer-toolkit` | GDD/系统设计/关卡设计 |
| `text-game-dev` | 文字游戏/视觉小说开发 |
| `nyx-archive-game-design-philosophy` | 游戏设计哲学 |
| `Humanizer-zh` | 中文文本人性化改写 |
| `ltx-video-generator` | LTX 视频生成 |
| `macos-image-generation` | macOS 本地 Stable Diffusion 图像生成 |

### 🧩 思维模型 (Thinking)
| Skill | 描述 |
|-------|------|
| `six-thinking-hats` | 六顶思考帽 |
| `blade-of-logic` | 逻辑拆解与论证验证 |
| `hammer-of-questions` | 苏格拉底式追问 |
| `ladder-of-abstraction` | 具象↔抽象层级转换 |
| `mirror-of-perspectives` | 多视角分析 |
| `branch-of-disciplines` | 学科派别与核心理念 |
| `talent-mind` | 天才思维三层递归方法论 |
| `musk-business-framework` | 马斯克第一性原理商业决策 |
| `checklist-manager` | 结构化清单管理 |

### 📊 数据分析 (Data)
| Skill | 描述 |
|-------|------|
| `data-analyst` | 数据可视化 + 报表 + SQL |
| `data-visualization` | Matplotlib/Seaborn/Plotly 图表 |
| `big-data-analysis` | 大规模数据集分析 |
| `dash-cog` | CellCog 交互式 Dashboard |
| `performance-optimizer` | 性能优化框架 |
| `perf-profiler` | 火焰图/CPU/内存 profiling |
| `acm-master-skill` | 多语言算法代码库 |
| `jq-json-processor` | JSON 处理 |
| `planning-with-files` | Manus 风格文件规划 — 多步骤任务组织与进度追踪 |
| `remotion-best-practices` | Remotion 视频创作最佳实践 |

### 🔐 安全 & 渗透 (Security)
| Skill | 描述 |
|-------|------|
| `hacker-arsenal` | PTES/OWASP/MITRE ATT&CK 全栈攻防 |
| `the-book-of-secret-knowledge` | 系统管理员/安全研究员知识库 |

### 🎨 前端开发 (Frontend)
| Skill | 描述 |
|-------|------|
| `vercel-react-best-practices` | React 19 + Next.js 最佳实践 |
| `generative-ui` | 交互式 HTML 组件生成 |
| `frontend-slides` | HTML 演示文稿 |
| `anthropics-canvas-design` | Canvas 画布设计 |
| `anthropics-frontend-design` | 前端界面设计 |
| `web-artifacts-builder` | React + Tailwind artifact 构建 |
| `vercel-react-native` | React Native + Expo |
| `sw-mobile-debugging` | React Native 调试 |
| `kj-web-design-guidelines` | Web 界面设计合规审查 |
| `web-design-guidelines` | Web 设计指南 |
| `tools-ui` | Agent 工具调用 UI 组件 |
| `vercel-composition-patterns` | React 组合模式 |

### 🔍 搜索 & 知识获取 (Search)
| Skill | 描述 |
|-------|------|
| `multi-search-engine` | 17 个搜索引擎集成 |
| `oss-code-analysis` | 开源项目源码分析 |
| `hn-extract` | HackerNews 帖子提取 |
| `download-waytoagi-prompts` | WayToAGI 提示词下载 |
| `folk-marketing` | 民间风格营销文案 |
| `x-post-automation` | X/Twitter 内容自动发布 |
| `skill-web-search` | 网页正文提取与内容抓取 |
| `web-access` | Web 访问工具 |
| `web-content-fetcher` | 网页内容提取 |

### 🛠️ 硬件 & IoT
| Skill | 描述 |
|-------|------|
| `r-wmi` | Rokid 智能眼镜控制 |
| `sonoscli` | Sonos 音箱控制 |

### 🤖 Agent 角色卡 (Agency)
| Skill | 描述 |
|-------|------|
| `agency-code-reviewer` | 代码审查 |
| `agency-data-engineer` | 数据工程 |
| `agency-devops-automator` | DevOps 自动化 |
| `agency-document-generator` | 文档生成 |
| `agency-git-workflow-master` | Git 工作流 |
| `agency-senior-developer` | 全栈开发（Laravel/Three.js） |
| `agency-model-qa` | 模型 QA |
| `zeroclaw-driver` | ZeroClaw Rust 运行时驱动 |
| `consensus-interact` | Consensus.tools 投票与协作 |
| `claude-code-commander` | Claude Code 命令执行器 |
| `page-agent-executor` | Page Agent 执行器 |
| `page-agent-research` | Page Agent 研究助手 |
| `ima-skill` | IMA 多模态技能 |

---

## 🔄 更新

```bash
# 推送到 GitHub
git add -A && git commit -m "chore: cleanup and update skills" && git push
```

## 📝 添加新 Skill

1. 在 `skills/` 下创建目录
2. 添加 `SKILL.md` (含 name/description frontmatter)
3. 提交并推送

---

**质量等级说明**：
- S 级：>20K，内容完整，可直接上手
- A 级：>5K，描述清晰，覆盖核心场景
- B 级：1K-5K，轻量但特定场景有效
- C 级：<1K，需补充或仅占位

---
Generated: 2026-04-03 | Total: 146 Skills
