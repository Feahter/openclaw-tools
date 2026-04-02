# MEMORY.md - 重要约定与记录

*Last Updated: 2026-04-02*

---

## 📔 日记机制
→ 详见 `memory/diary/`

## 🧠 思考者行为准则
→ 详见 `memory/evolution/thinking.md`

## 🚀 小说创作 SOP
→ 详见 `memory/creative/novel-sop.md`

## 🛠️ 浏览器工具规则
→ 详见 `memory/tasks/browser-rules.md`

## 💬 群聊礼仪
→ 详见 `memory/tasks/chat-etiquette.md`

## 🎨 品味与判断力持续进化研究
→ 详见 `memory/research/taste-and-judgment/README.md`
- 核心问题：建立 AI 与人类品味判断力共同提升的双向增强回路
- 四大机制假说：品味传染 / 判断过程显式化 / 品味冲突反思 / 预测追踪
- 五大研究方向：品味可语言化 / 判断偏差追踪 / 高质量暴露策展 / 决策框架 / AI vs 人类偏差对比
- 初始偏见假设：确认偏误 / 过度自信 / 可得性启发

## 🧠 AI 开发模式库
→ 详见 `memory/evolution/ai-development-patterns.md`
- 核心：文档是杠杆 + 禁止行为 > 最佳实践 + 身份转换
- LLM 机制：中间迷失 / 路径依赖 / 上下文污染
- 6 大上下文技巧：探针模式 + 谋定后动 + 锚点复用
- Spec 驱动开发：9 阶段 × 8 角色
- 竞态陷阱模式：Swift 并发三陷阱 + 异步状态清除顺序

## 🧠 Skills 进化体系
→ 详见 `memory/evolution/skills-knowledge.md`（全面认知体系，持续更新）

### 🎯 skill-tench-hunter（技术研究猎手，2026-03-20）
→ 详见 `skills/skill-tench-hunter/SKILL.md`
- 从 WebMCP 研究过程提取的完整技术调研管道
- 5 阶段：并行收集 → 合成判断 → 研究报告 → 最佳实践 → Git 归档
- 验证：WebMCP 研究（2 链接 → 2 份报告 → commit → push ✅）
→ 详见 `memory/evolution/skills-system.md`

## 🛠️ 本地核心技能
→ 详见 `memory/evolution/core-skills.md`

## ⚙️ 执行约束
→ 详见 `memory/execution-guidelines.md`

---

## 🔒 项目开源 - 个人信息保密策略

**防止网络恶意攻击和利用**：

| 类别 | 排除方式 |
|------|---------|
| 身份信息 | 使用匿名账号 (Arthur / Feather) |
| 联系方式 | 使用项目专用邮箱 |
| 位置信息 | 移除所有位置元数据 |
| 对话记录 | 不提交对话相关文件 |
| 密钥凭证 | 严格 .gitignore 排除 |
| 任务看板 | 仅本地保留 |

**GitHub 用户名**：Feahter（注册时手滑打错了，实际就是 "Feahter"）
**开源账号**：GitHub: Feahter | 邮箱: project@openclaw.ai

---

## 🦞 OpenClaw 当前状态（2026-03-24）

- **版本**：2026.3.23-1
- **飞书插件**：@larksuite/openclaw-lark@2026.3.25
- **当前模型**：anthropic/MiniMax-M2.7（主），fallbacks: MiniMax-M2.1, Kimi K2.5, MiniMax-M2.5
- **Provider**：`minimax`（已删除重复的 `anthropic`）
- **优化**：maxConcurrent=8, memorySearch=enabled, contextPruning=30m

## 🔐 凭证配置

| 凭证 | 路径 | 状态 |
|------|------|------|
| GitHub Token | `~/.openclaw/credentials/github.json` | ✅ 已配置 |

---

## 🛠️ opencode 使用方式
→ 详见 `memory/tasks/opencode-usage.md`

## 🖥️ 本地工具安装（2026-03-31）

### bb-browser + web-access（CDP 浏览器）
- `bb-browser` skill（v0.6.0）+ `bb-browser-sites` 扩展（106 站点）
- `web-access` skill（eze-is/web-access，⭐2,146）— Node.js CDP proxy（端口 3456→9222）
- 实测可用：Wikipedia、B站热门、36氪快讯、雪球、百度搜索、Product Hunt
- ⚠️ 需登录站点（知乎/GitHub/HackerNews）暂不可用
- CDP Proxy 手动启动：`node ~/.openclaw/workspace/skills/web-access/scripts/cdp-proxy.mjs &`

### Ghostty 终端（2026-03-31）
- DMG 安装到 `/Applications/Ghostty.app`，配置 `~/.config/ghostty/config`
- 参考 Boris Cherny（Claude Code 之父）工作流配置
- 主题：Catppuccin Mocha/Latte

### Claude Code 源码吸收（2026-03-31/04-01）
- `instructkr/claude-code` Leak 源码克隆到 `~/project/github/claude-code/`
- 10 个 Tier 1/2 脚本吸收到 `~/.openclaw/workspace/scripts/claude-code-absorbed/`
- 最佳可移植：truncation.ts / abort-controller.ts / signal.ts / circular-buffer.ts
- 技术栈：Bun + TS strict + React/Ink + Commander.js + Zod v4 + MCP
- 新建薄编排 `skill-repo-research/`：统一入口路由屠夫/猎手

## 🔧 本地语义搜索
→ 详见 `memory/tasks/vector-search.md`

## 🚀 MVP 1.0.0 发布记录
→ 详见 `memory/archive/mvp-release.md`

---

## 🧠 SPEN 算法研究 (2026-03-13)

**SPEN = Spatial-Temporal Encoding / 空间-时间编码**

### 核心思想
- 联合表示空间和时间信息
- 3D 卷积或联合注意力同时建模时空依赖
- 可学习位置编码 vs 固定 sinusoidal

### 分析项目
- **TASED-Net** (ICCV 2019): 视频显著性检测，3D CNN Encoder-Decoder
- **L-STEP** (ICML 2025): 时序知识图谱链接预测，可学习时空位置编码

### MRI 加速应用
- 核心：时空联合编码 + 压缩采样 + 智能重建
- 效果：千万级 → 13万采样 (70-100x 加速)
- 优势：抗畸变、适合便携式设备

### Agent 记忆系统创新
- **Agent-SPEN 架构设计** (原创)
- 核心：时空联合编码 + 可学习压缩 + 推理重建
- 预期：5-10x 压缩比、100K+ 上下文、强时序推理
- 论文方向：将信号处理 SPEN 思想引入 Agent 记忆

### 文档
→ 详见 `memory/research/algorithms/spatial-temporal-encoding/`

### Leiden 算法 (2026-03-20)
→ 详见 `memory/research/algorithms/leiden/`
- Louvain 改进版：三阶段（移动→精细化→缩放）保证社区连通性
- 源码：graphologycommunities-leiden（MIT），vendored 于 GitNexus
- 核心：SparseMap + SparseQueueSet + 节点排序数组

---

## 🚀 算法研究 SOP
→ 详见 `memory/research/algorithm-sop.md`

## 🌐 墙内搜索策略
- 百度搜索 (首选)
- 必应 (国际版)
- GitHub API (无需翻墙)

---

## 🎯 Skills 组合玩法 (2026-03-19)

### 1. 内容生产线
| 组合 | 功能 |
|------|------|
| `skill-web-search` + `skill-project-butcher` | 读取文章（含URL）→ 分析文中提到的 GitHub 项目 |
| `skill-web-search` + `summarize` | 读取文章 → 摘要总结 |
| `agent-reach` + `baoyu-format-markdown` + `baoyu-post-to-x` | 抓取 → 格式化 → 自动发推 |
| `web_fetch` + `baoyu-markdown-to-html` + `baoyu-post-to-wechat` | 网页 → HTML → 发公众号 |
| `summarize` + `anthropics-pptx` + `baoyu-slide-deck` | 摘要 → PPT → 生成幻灯片 |
| `fast-edit` + `skill-project-butcher` | 大文件编辑 → 批量修改项目文件 |

### 2. AI 研究助手
| 组合 | 功能 |
|------|------|
| `tavily-search` + `ai-rag-pipeline` + `chromadb` | 搜索 → RAG 向量存储 → 问答 |
| `skill-project-butcher` + `agent-reach` | 深度研究 GitHub 项目 → 补充网络资料 |

### 3. Skills 工程化
| 组合 | 功能 |
|------|------|
| `skill-creator` + `skill-project-butcher` | 创建 Skill → 分析同类项目参考架构 |
| `find-skills` + `skill-project-butcher` | 发现有趣项目 → 深度分析 → 决定是否做成 Skill |

### 3. 自动化工作流
| 组合 | 功能 |
|------|------|
| `cron-mastery` + `workflow-automation` | 定时任务 + 工作流编排 |
| `automation-workflows` + `feishu` | 自动化 → 飞书通知/任务 |

### 4. 开发闭环
| 组合 | 功能 |
|------|------|
| `coding-agent` + `test-driven-development` + `github` | 编码 → 测试 → 提交 |
| `algorithm-toolkit` + `performance-optimizer` | 算法 → 性能优化 |

### 5. 多模态创作
| 组合 | 功能 |
|------|------|
| `baoyu-image-gen` + `baoyu-cover-image` + `anthropics-frontend-design` | 生成配图 → 封面 → 前端页面 |
| `baoyu-comic` + `baoyu-article-illustrator` | 漫画 → 文章配图 |

### 6. Skills 生成
| 组合 | 功能 |
|------|------|
| `skill-creator` + `skill-orchestrator` | 创建 → 编排新 Skills |
| `skill-from-github` + `github-to-skills` | GitHub 项目 → 转换为 Skills |
| `find-skills` + `search-local-skills` | 发现 → 本地搜索已有 Skills |

### 7. 小说创作
| 组合 | 功能 |
|------|------|
| `one-sentence-novel` + `baoyu-image-gen` | 一句话小说 → AI 生成配图 |
| `one-sentence-novel` + `baoyu-comic` | → 生成漫画版 |
| `baoyu-article-illustrator` + `anthropics-pptx` | 小说配图 → PPT 演示 |
| `mirror-of-perspectives` + `text-game-dev` | 多视角叙事 → 文字游戏 |

### 8. 进阶元技能
| 组合 | 功能 |
|------|------|
| `skill-orchestrator` + 任意 Skills | 元技能：调用其他 Skills |
| `agent-commander` + `sessions_spawn` | 多代理协作 |
| `context-manager` + `memory` | 长期记忆管理 |
| `self-improving-agent` + `reflect-learn` | 自我优化循环 |

### 9. 轻量级浏览器
| 组合 | 功能 |
|------|------|
| `lightpanda` + `browser` | 替代 OpenClaw 默认浏览器，资源占用更低 |
| `lightpanda` + `agent-reach` | 社媒平台抓取（配合 CDP）|

### 🔄 self-improving-agent（错误捕获循环）
| 组件 | 说明 |
|------|------|
| `.learnings/LEARNINGS.md` | 修正、洞察、最佳实践 |
| `.learnings/ERRORS.md` | 命令失败、工具异常 |
| `.learnings/FEATURE_REQUESTS.md` | 缺失的能力 |
| Promotion 路径 | 频繁(≥3) → SOUL/TOOLS/AGENTS |
| Skill 抽取 | 足够通用 → extract-skill.sh → 独立 Skill |

**核心设计**：Pattern-Key + Recurrence-Count 去重，频繁错误自动升级为永久记忆。
| 组合 | 功能 |
|------|------|
| `lightpanda` + `browser` | 替代 OpenClaw 默认浏览器，资源占用更低 |
| `lightpanda` + `agent-reach` | 社媒平台抓取（配合 CDP） |

## 🚀 chinese-name-lookup 八字命理 skill (2026-03-30)

### 状态
- **Phase 1-6**: ✅ 调候表/长生表/藏干/格局法/调候判定/喜用神/身强弱 v2
- **Phase 7**: ✅ 神煞查询系统（15个神煞）
- **Phase 8**: ✅ 大运流年推算
- **Phase 9**: ✅ 完整报告格式化
- **P1-a**: ✅ 纳音五行（60组纳音+性格+年日关系分析）
- **P1-b**: ✅ 刑冲害合（六冲/六合/三刑/六害/天干五合）
- **P1-c**: ✅ 子息数量规则（渊海子平"一杀一子"+时支长生子女数）
- **P1-d**: ✅ 婚姻配偶星系统（男正财/女正官+配偶宫）
- **P1-e**: ✅ 孤鸾煞+阴错阳差（甲寅/辛亥/丙午/壬子 + 阴错阳差12日）
- **P2-a**: ✅ 女命婚姻贵贱格局（模块+报告集成，2026-03-31）
- **P2-b**: ✅ 神煞质量评估（模块+报告集成，2026-03-31）
- **P0喜用神收敛**: ✅ 极强/极弱加is_strong/is_weak判断，修复千里命稿法对极强日主的错误推导；两法在核心共识上收敛（2026-03-31）
- **P1神煞补全**: ✅ 太极贵人/咸池/绞煞/十恶大败/元辰/大耗(P1)+灾煞/劫煞/丧门/吊客/六甲贵神(P2)+胎元神煞+命宫神煞（2026-03-31）
- **结构修复**: ✅ 调候优先级/寒热燥湿(穷通宝鉴)+通关用神(子平真诠)+格局四等(真/清/浊/破)+用神体系展示（2026-03-31）
- **本地引擎**: ✅ 已完成（无外部API依赖）

### 关键文件
- `scripts/bazi_engine.py` — 核心引擎（JDN 公式已验证正确，2026-03-29 锚点确认）
- `scripts/xiyongshen_v2.py` — 本地喜用神 v2
- `scripts/rizhu_strength_v2.py` — 身强弱量化 v2
- `scripts/poge_analyzer.py` — 破格原因识别
- `scripts/liushen_xinxing.py` — 六神心性速查
- `scripts/nayin.py` — 纳音五行（P1-a，2026-03-30）
- `scripts/penalty_harmony.py` — 刑冲害合（P1-b，2026-03-30）
- `scripts/children_analyzer.py` — 子息分析（P1-c，渊海子平口诀，2026-03-30）
- `scripts/marriage_analyzer.py` — 婚姻配偶星+孤鸾煞/阴错阳差（P1-d/e，2026-03-30）
- `scripts/marriage_fate_classifier.py` — 女命贵贱格局（P2-a，2026-03-30）
- `scripts/shensha_quality.py` — 神煞质量评估+空亡（P2-b，2026-03-30）
- `scripts/report_formatter.py` — 报告格式化
- `scripts/name_generator.py` — 姓名生成


---

## 🌐 cloudflare-proxy 网络穿透 skill (2026-03-30)

### 背景
GFW 内 GitHub/HuggingFace/Twitter 等站点无法直接访问，web-access 失败后需降级。

### 关键发现
- **公共 CF Worker 被自身验证墙拦**：Turnstile 触发条件不明，curl 能用但 Python urllib 403
- **wrangler login 需要浏览器**：无法无头自动化 → API Token 方式兜底
- **自建 Worker 是唯一可靠方案**：免费 10 万请求/天

### 关键文件
- `skills/cloudflare-proxy/scripts/proxy_fetch.py` — 程序提取模式
- `skills/cloudflare-proxy/scripts/deploy_api_token.py` — CF API Token 全自动部署
- `skills/cloudflare-proxy/scripts/deploy_worker.sh` — Wrangler OAuth 部署

### 待完成
- 用户需要提供 CF API Token 才能激活 cloudflare-proxy
