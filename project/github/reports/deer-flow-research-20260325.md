# DeerFlow 2.0 技术深度研究报告

*Created: 2026-03-25*
*Sources: [GitHub](https://github.com/bytedance/deer-flow) | [官方文档](https://deerflow.tech) | [架构文档](project/github/deer-flow/backend/docs/ARCHITECTURE.md) | [Memory改进文档](project/github/deer-flow/backend/docs/MEMORY_IMPROVEMENTS.md)*

---

## 1. 概述

### 1.1 一句话定性

**DeerFlow = LangGraph Agent Runtime + 模块化 Sandbox + 可插拔 Skills + Memory 系统** 的超级 Agent 开发框架，ByteDance 出品，2026-02-28 登顶 GitHub Trending #1。

### 1.2 现状
- **Stars**: 43,980 ⭐（截至 2026-03-25）
- **今日增长**: 4,346 ⭐/天
- **语言**: Python (backend) + TypeScript/Next.js (frontend)
- **版本**: 2.0（完全重写，与 1.x 不兼容）
- **许可证**: MIT
- **推荐模型**: Doubao-Seed-2.0-Code, DeepSeek v3.2, Kimi 2.5

---

## 2. 核心架构

### 2.1 系统架构图

```
Client (Browser)
      │
      ▼
Nginx (Port 2026)
  ├─ /api/langgraph/* → LangGraph Server (2024)
  ├─ /api/*           → Gateway API (8001)
  └─ /*               → Frontend (3000)
```

**三个核心服务**：
| 服务 | Port | 职责 |
|------|------|------|
| LangGraph Server | 2024 | Agent 运行时、Thread 管理、SSE 流式输出 |
| Gateway API | 8001 | 模型 API、MCP 配置、Skills 管理、文件上传 |
| Frontend | 3000 | Next.js React UI |

### 2.2 Agent 运行时（核心创新点）

**`make_lead_agent` 是入口**，通过 Middleware Chain 处理请求：

```
┌────────────────────────────────────────────────────┐
│                  Middleware Chain                   │
├────────────────────────────────────────────────────┤
│ 1. ThreadDataMiddleware     - 初始化 workspace     │
│ 2. UploadsMiddleware        - 处理上传文件         │
│ 3. SandboxMiddleware        - 获取 Sandbox 环境    │
│ 4. SummarizationMiddleware  - 上下文压缩（超标时） │
│ 5. TitleMiddleware          - 自动生成标题         │
│ 6. TodoListMiddleware       - 任务跟踪（plan 模式）│
│ 7. ViewImageMiddleware      - Vision 模型支持      │
│ 8. ClarificationMiddleware  - 处理澄清请求         │
└────────────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────┐
│                 Agent Core                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Model   │  │  Tools   │  │  System Prompt   │ │
│  │ (工厂)   │  │ (可配置) │  │   (含 Skills)    │ │
│  └──────────┘  └──────────┘  └──────────────────┘ │
└────────────────────────────────────────────────────┘
```

**关键洞察**：
1. **Middleware Chain 模式**：和我们的 `agent-reach` 中间件设计思路一致，但 DeerFlow 更成熟
2. **ThreadState 扩展 LangGraph**：`sandbox`、`artifacts`、`todos` 等字段都是 DeerFlow 自己加的
3. **Context 压缩**：当 token 超限时通过 SummarizationMiddleware 压缩历史消息

### 2.3 Sandbox 系统

```
SandboxProvider (抽象基类)
       │
       ├── LocalSandboxProvider    # 开发环境，直接执行
       └── AioSandboxProvider      # 生产环境，Docker 容器隔离

虚拟路径映射：
/mnt/user-data/workspace  → .deer-flow/threads/{thread_id}/user-data/workspace
/mnt/user-data/uploads   → .deer-flow/threads/{thread_id}/user-data/uploads
/mnt/user-data/outputs   → .deer-flow/threads/{thread_id}/user-data/outputs
/mnt/skills              → deer-flow/skills/
```

**三种执行模式**：
| 模式 | 适用场景 | 隔离级别 |
|------|---------|---------|
| Local | 开发调试 | 无隔离 |
| Docker | 单机生产 | 容器级隔离 |
| K8s + Provisioner | 分布式生产 | Pod 级隔离 |

### 2.4 Tool 系统

**三层 Tool 架构**：
```
Built-in Tools (内置)
  - present_file, ask_clarification, view_image

Configured Tools (config.yaml)
  - web_search, web_fetch, bash, read_file, write_file, str_replace, ls

MCP Tools (extensions_config.json)
  - github, filesystem, postgres, brave-search, puppeteer...
```

**工具来源统一到 `get_available_tools()`**，支持 LangChain 生态 + MCP 协议扩展。

### 2.5 Model Factory

通过反射机制动态加载模型：

```python
# config.yaml 示例
models:
  - name: gpt-4
    use: langchain_openai:ChatOpenAI
    model: gpt-4
    supports_thinking: false
    supports_vision: true
```

**支持 Provider**：
- OpenAI / Azure OpenAI
- Anthropic (Claude Code OAuth)
- DeepSeek
- Codex CLI
- OpenRouter 兼容网关

**CLi 背书的模型**（如 Codex、Claude Code）通过 OAuth 或本地 auth.json 认证。

### 2.6 Skills 系统

**目录结构**：
```
skills/
├── public/           # 官方 Skill（提交到 repo）
│   ├── pdf-processing/
│   ├── frontend-design/
│   ├── deep-research/
│   └── ... (16 个官方 Skill)
└── custom/           # 用户自定义 Skill（gitignored）
```

**SKILL.md 格式**（与 OpenClaw Skills 完全一致）：
```yaml
---
name: PDF Processing
description: Handle PDF documents efficiently
license: MIT
allowed-tools:
  - read_file
  - write_file
  - bash
---
# Skill Instructions
Content injected into system prompt...
```

**洞察**：DeerFlow 的 Skills 格式和 OpenClaw Skills 高度相似，但 DeerFlow 多了 `allowed-tools` 白名单机制（安全控制）。

### 2.7 Memory 系统（当前状态）

**已实现**（截至 2026-03-10）：
- `tiktoken` 精确 token 计数
- Facts 按 confidence 排序注入
- `max_injection_tokens` 预算控制

**计划中（Roadmap）**：
- TF-IDF 相似度检索
- `current_context` 上下文感知评分
- 加权评分：`final_score = (similarity * 0.6) + (confidence * 0.4)`

**当前注入格式**：
```
User Context: {user.*.summary}
History: {history.*.summary}
Facts: [{facts[] 按 confidence 排序}]
```

---

## 3. 关键设计模式

### 3.1 Thread 模型

每个对话 = 一个 Thread，有独立状态：
```python
class ThreadState:
    messages: list[BaseMessage]      # 对话历史
    sandbox: dict                     # Sandbox 环境信息
    artifacts: list[str]              # 生成的文件路径
    thread_data: dict                 # {workspace, uploads, outputs}
    title: str | None                 # 自动标题
    todos: list[dict]                 # 任务列表
    viewed_images: dict               # Vision 数据
```

**文件上传流程**：
1. Client → Gateway 上传文件
2. Gateway 存储到 `uploads/`
3. 如果是文档，markitdown 转 Markdown
4. UploadsMiddleware 注入文件列表到消息
5. Agent 通过虚拟路径访问

### 3.2 MCP 集成

**支持三种传输协议**：stdio / SSE / HTTP

extensions_config.json 配置示例：
```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "$GITHUB_TOKEN"}
    }
  }
}
```

**动态重载**：MCP Manager 通过 mtime 检测配置文件变化，运行时重新初始化。

### 3.3 IM Channels（飞书支持）

| Channel | Transport | 难度 |
|---------|-----------|------|
| Telegram | Bot API (长轮询) | 简单 |
| Slack | Socket Mode | 中等 |
| **Feishu/Lark** | WebSocket | 中等 |

**配置在 `config.yaml`**：
```yaml
channels:
  langgraph_url: http://localhost:2024
  gateway_url: http://localhost:8001
  session:
    assistant_id: lead_agent
    config:
      recursion_limit: 100
    context:
      thinking_enabled: true
      is_plan_mode: false
      subagent_enabled: false
```

---

## 4. 与 OpenClaw 的对比

| 维度 | DeerFlow | OpenClaw |
|------|----------|----------|
| **定位** | Super Agent Harness | Agent 编排平台 |
| **Agent 架构** | LangGraph 单体 | 模块化多 Agent |
| **Sandbox** | Docker/K8s 隔离 | 暂无（？需要确认） |
| **Skills** | SKILL.md 格式 | SKILL.md 格式（一致） |
| **Memory** | TF-IDF Roadmap 中 | 待实现 |
| **MCP** | 支持 | 飞书插件支持 |
| **IM Channels** | 飞书/Slack/TG | 飞书为主 |
| **前端** | Next.js (自己造) | 飞书 |
| **语言** | Python + TS | Node.js |

**核心差距**：
1. DeerFlow 有完整的 **Sandbox 隔离执行**，OpenClaw 目前没有
2. DeerFlow 的 **Middleware Chain** 设计比我们的 Agent 更成熟
3. OpenClaw 的优势在于 **会话路由和多 Agent 协作**

---

## 5. 值得借鉴的设计

### 5.1 Middleware Chain（可借鉴）

把认证、上下文注入、压缩等横切关注点抽成 Middleware，Agent 核心只做推理。

**可应用到 OpenClaw**：
- 在 Agent 执行前插入 Memory Middleware
- 在 Tool 执行前插入 Sandbox Middleware

### 5.2 allowed-tools 白名单（可借鉴）

Skills 的 `allowed-tools` 限制 Skill 能调用的工具，防止恶意 Skill 执行危险操作。

### 5.3 Thread 隔离模型

每个对话有独立的文件系统空间（workspace/uploads/outputs），这比我们的全局文件空间更安全。

### 5.4 MCP 动态重载

MCP Manager 通过 mtime 检测配置文件变化，无需重启服务。

---

## 6. 局限性 / 风险

| 问题 | 影响 | 缓解方案 |
|------|------|---------|
| 2.0 完全重写 | 1.x 用户需迁移 | 维护 main-1.x 分支 |
| 依赖 ByteDance 生态 | 推荐 Doubao-Seed 模型 | 支持 OpenAI/Anthropic |
| Memory TF-IDF 尚未实现 | 长期记忆检索弱 | 参考 Roadmap 自行实现 |
| 需要自建前端 | UI 投入大 | 已有完整 Next.js UI |

---

## 7. 对 OpenClaw 的意义

1. **Sandbox 隔离**：可以作为 OpenClaw 未来安全执行单元的设计参考
2. **Middleware Chain**：可以引入到 OpenClaw Agent 执行管道
3. **Skills 格式**：`allowed-tools` 字段是 OpenClaw Skills 格式的有价值补充
4. **Memory Roadmap**：TF-IDF + confidence 混合评分值得研究

---

## 8. 核心价值验证

*验证方法：对照 README 声称，逐条检查源码实现位置*

### README 声称的 6 大核心价值

| 核心价值 | README 原文 | 代码实现位置 | 验证结果 |
|---------|------------|-------------|---------|
| Super Agent Harness | "orchestrates sub-agents, memory, and sandboxes" | `packages/harness/deerflow/agents/lead_agent/agent.py` | ✅ 完整实现 |
| Sub-agents | "handles different levels of tasks" | `agents/subagent/` | ✅ 完整实现，LangGraph Subgraph |
| Memory | "long-term memory" | `backend/docs/MEMORY_IMPROVEMENTS.md` | ⚠️ tiktoken 计数已实现，TF-IDF 在 Roadmap |
| Sandbox | "sandboxes for code execution" | `sandbox/local.py`, `community/aio_sandbox.py` | ✅ 三层隔离完整 |
| Skills | "powered by extensible skills" | `skills/public/`, `skills/loader.py` | ✅ public/custom 双目录，SKILL.md 格式 |
| MCP Integration | "MCP servers and skills to extend capabilities" | `mcp/manager.py` | ✅ 三协议支持，配置热重载 |

### 验证结论

README 声称的 6 项核心价值中：
- ✅ 完整实现：**5 项**
- ⚠️ 部分实现：**1 项**（Memory TF-IDF 在 Roadmap 中）
- ❌ 未实现：**0 项**

**总体评价**：README 声称基本属实，无虚标功能。Memory 系统相对较弱（TF-IDF 尚未实现），但已有 tiktoken 计数和 confidence 排序。

---

## 9. 泛用代码析出

*提取可移植到其他项目的通用模块*

### Tier 1 — 零依赖可直接移植

| 模块 | 文件 | 用途 |
|------|------|------|
| **Middleware Chain 模式** | `agents/lead_agent/middleware.py` | Agent 执行前横切关注点链，可直接搬入任何 Agent 框架 |
| **ThreadState 扩展** | `agents/lead_agent/state.py` | 在 LangGraph 状态上挂载 sandbox/todos/artifacts，扩展性强 |
| **虚拟路径映射** | `sandbox/path.py` | 逻辑路径 → 物理路径的映射表，隔离性好 |
| **Model Factory 反射** | `models/factory.py` | config.yaml → LangChain 实例的动态加载，配置驱动 |
| **allowed-tools 白名单** | `skills/loader.py` | Skill 能调用的工具白名单，安全机制可直接复用 |

### Tier 2 — 需简单适配后可移植

| 模块 | 文件 | 需适配部分 |
|------|------|---------|
| **MCP Manager 热重载** | `mcp/manager.py` | 需对接 OpenClaw 的 MCP 插件系统接口 |
| **Summarization 压缩** | `middleware/summarization.py` | 需对接 OpenClaw 的 context 管理（可能是 tiktoken 计数） |
| **Sandbox Provider 抽象** | `sandbox/base.py` | 需实现 Local/Docker/K8s 三种 Provider 接口 |

### Tier 3 — 强依赖需重构

| 模块 | 文件 | 依赖问题 |
|------|------|---------|
| **LangGraph Agent Runtime** | 整体架构 | 强耦合 LangGraph，换框架需重构 |
| **Next.js Frontend** | `frontend/` | 独立项目，不可单独移植 |

### 最高价值模块详解

**Middleware Chain（Tier 1）**：
```python
# 核心模式：Chain of Responsibility + 装饰器
class Middleware:
    def process(self, state, context, next_handler):
        # 前置处理
        result = next_handler()
        # 后置处理
        return result

# 使用示例
chain = ThreadDataMiddleware() | UploadsMiddleware() | SandboxMiddleware()
result = chain.execute(agent_state)
```

**价值**：零依赖，任何 Python Agent 框架都可直接借鉴此模式。

---

## 10. 总结

| 维度 | 评分 | 说明 |
|------|------|------|
| **架构完整性** | ★★★★★ | Sandbox + Skills + Memory + MCP + Channels 面面俱到 |
| **代码质量** | ★★★★☆ | 文档详尽，架构清晰，但作为框架学习曲线陡 |
| **可扩展性** | ★★★★★ | 一切皆可插拔 |
| **落地难度** | ★★★☆☆ | 需要自建前端（虽然官方提供了） |
| **对 OpenClaw 价值** | ★★★★☆ | Sandbox 和 Middleware Chain 设计值得借鉴 |

**一句话评价**：DeerFlow 是一个**工程化程度很高**的 Agent 开发框架，尤其在**安全隔离**和**模块化**方面领先。如果 OpenClaw 要做多 Agent 协作和长期记忆，可以从 DeerFlow 的 Middleware Chain 和 Memory Roadmap 中取经。

---

## 11. 参考资料

1. [DeerFlow GitHub](https://github.com/bytedance/deer-flow)
2. [DeerFlow 官网](https://deerflow.tech)
3. [Architecture Doc](project/github/deer-flow/backend/docs/ARCHITECTURE.md)
4. [Memory Improvements Doc](project/github/deer-flow/backend/docs/MEMORY_IMPROVEMENTS.md)
5. [InfoQuest (BytePlus 搜索工具)](https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest)
