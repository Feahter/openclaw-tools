# Claude Code 开源代码深度分析报告

*Repo: instructkr/claude-code（Leak Snapshot, 2026-03-31）*
*研究时间: 2026-04-01*
*子 Skill: skill-project-butcher（代码分析） + skill-tench-hunter（技术情报）*

---

## 一、项目基本信息

| 维度 | 数据 |
|------|------|
| **性质** | Claude Code CLI 源码镜像（泄露）|
| **泄露方式** | npm 包中暴露 `.map` 文件 → R2 存储桶未混淆 TypeScript 源码 |
| **研究者** | instructkr（大学生），安全研究用 |
| **规模** | src/ 下 55 个子目录，143 个工具文件，111 个组件 |
| **语言** | TypeScript（strict mode）|
| **运行时** | Bun |
| **终端 UI** | React + Ink（vadimdemedes/ink）|
| **许可证** | Anthropic 版权，非开源 |

---

## 二、代码架构分析

### 2.1 核心目录结构

```
src/
├── main.tsx              # 入口（4683行！），并行预取优化启动
├── query.ts              # 查询管道（1729行）
├── QueryEngine.ts        # LLM 调用引擎（1295行）
├── Tool.ts               # 工具基类（792行）
├── commands.ts           # 命令注册（754行）
│
├── bootstrap/            # 启动初始化
├── tools/                # 40+ 工具实现（143文件）
├── commands/             # ~90 条 slash 命令
├── components/           # 111 个 React/Ink 组件
├── hooks/                # 79 个 React Hooks
├── services/             # API / MCP / OAuth / Analytics
├── bridge/               # IDE 集成桥接
├── coordinator/           # 多 Agent 协调
├── skills/               # Skill 系统
├── plugins/              # 插件架构
├── memdir/               # 持久记忆目录
├── ink/                  # 终端渲染引擎
├── vim/                  # Vim 模式
├── voice/                # 语音输入
├── remote/               # 远程会话
├── server/               # 服务模式
├── state/                # 状态管理
├── migrations/           # 配置迁移
├── schemas/              # Zod Schema
├── native-ts/            # 原生 TS 工具
├── upstreamproxy/         # 上游代理
└── utils/                # 工具函数（大量）
```

### 2.2 关键模块

#### main.tsx（4683 行）

启动流程优化：并行触发 MDM 设置读取 + Keychain 预取 + API 预连接，比串行节省 ~200ms。

```typescript
// 入口的并行预取（side-effects 在所有 import 前）
profileCheckpoint('main_tsx_entry')
startMdmRawRead()          // MDM 子进程并行
startKeychainPrefetch()    // macOS Keychain 并行读取
// 然后才开始加载 ~135ms 的模块导入
```

#### QueryEngine.ts（1295 行）

Agent Loop 核心：
- 流式响应处理
- 工具调用循环
- 思考模式（thinking mode）
- 重试逻辑
- Token 计数

#### tools/（143 文件）

每个工具独立模块，基类 `Tool.ts` 定义输入 Schema + 权限模型。

#### hooks/（79 个 Hook）

大量 React Hook，每个专注一个功能：
- `useCanUseTool.tsx` — 工具权限检查
- `useMergedTools.ts` — 工具合并
- `useQueueProcessor.ts` — 队列处理
- `useSwarmInitialization.ts` — Swarm 初始化
- `useMemoryUsage.ts` — 内存监控

#### memdir/（记忆目录系统）

文件基础的持久记忆：
- `memdir.ts` — 入口点管理
- `memoryTypes.ts` — 记忆类型定义
- `findRelevantMemories.ts` — 相关记忆检索
- `teamMemPrompts.ts` — 团队记忆 prompt

---

## 三、技术栈全景

| 类别 | 技术 |
|------|------|
| 运行时 | Bun |
| 语言 | TypeScript strict |
| CLI 解析 | Commander.js |
| 终端 UI | React + Ink |
| Schema 验证 | Zod v4 |
| 代码搜索 | ripgrep |
| 协议 | MCP SDK, LSP |
| API | Anthropic SDK |
| 遥测 | OpenTelemetry + gRPC |
| 特性开关 | GrowthBook |
| 认证 | OAuth 2.0, JWT, macOS Keychain |

---

## 四、工具系统详解

### 4.1 全部工具（40+）

| 工具 | 说明 |
|------|------|
| BashTool | Shell 命令执行 |
| FileReadTool | 读文件（支持图片/PDF/Notebook）|
| FileWriteTool | 文件创建/覆盖 |
| FileEditTool | 字符串替换编辑 |
| GlobTool / GrepTool | 文件搜索 + 内容搜索 |
| WebFetchTool / WebSearchTool | 网络访问 |
| AgentTool | 子 Agent 生成 |
| SkillTool | Skill 执行 |
| MCPTool | MCP 服务器调用 |
| LSPTool | 语言服务器协议 |
| TaskCreateTool / TaskUpdateTool | 任务管理 |
| EnterPlanModeTool / ExitPlanModeTool | 计划模式 |
| EnterWorktreeTool / ExitWorktreeTool | Git Worktree |
| TeamCreateTool / TeamDeleteTool | 多 Agent 团队 |
| CronCreateTool / CronDeleteTool | 定时触发 |
| SleepTool | 主动等待模式 |
| AskUserQuestionTool | 向用户提问 |

### 4.2 特色：特性开关 DCE

```typescript
import { feature } from 'bun:bundle'
const cronTools = feature('AGENT_TRIGGERS')
  ? [CronCreateTool, CronDeleteTool, CronListTool]
  : []
```

未激活特性在编译时完全剔除，实现零开销特性开关。

---

## 五、命令系统（~90 条 slash 命令）

| 命令 | 说明 |
|------|------|
| `/commit` | Git 提交 |
| `/review` | 代码审查 |
| `/compact` | 上下文压缩 |
| `/mcp` | MCP 管理 |
| `/config` | 设置管理 |
| `/doctor` | 环境诊断 |
| `/memory` | 记忆管理 |
| `/skills` | Skill 管理 |
| `/tasks` | 任务管理 |
| `/vim` | Vim 模式 |
| `/diff` | 查看变更 |
| `/cost` | 费用查看 |
| `/context` | 上下文可视化 |
| `/pr_comments` | PR 评论 |
| `/resume` | 恢复会话 |
| `/share` | 分享会话 |
| `/plan` | 进入计划模式 |
| `/mobile` / `/desktop` | 跨设备交接 |

---

## 六、记忆系统（MEMDIR）

### 6.1 设计理念

每个项目有 `.claude/` 目录，其中 `MEMORY.md` 作为入口点（类似 OpenClaw 的 AGENTS.md）。

```typescript
const MAX_ENTRYPOINT_LINES = 200
const MAX_ENTRYPOINT_BYTES = 25_000
```

超过上限自动截断，append 警告防止 Token 爆炸。

### 6.2 记忆类型

- **INDEX**：主入口点 MEMORY.md
- **TOPIC**：子话题文件
- **AUTO**：自动记忆（Assistant 模式）

### 6.3 团队记忆

`teamMemPrompts.ts` 支持团队级记忆同步，每个 teammate 有独立 inbox。

---

## 七、安全设计

### 7.1 权限系统

四模式权限控制：
- `default` — 每次工具调用前询问
- `plan` — 计划模式跳过
- `auto` — 自动判断可信任操作
- `bypassPermissions` — CI 模式，全跳过

### 7.2 认证

- OAuth 2.0（第三方登录）
- JWT（会话令牌）
- macOS Keychain（凭证安全存储）
- Trusted Device（桥接模式）

### 7.3 IDE 桥接安全

- JWT 双向认证
- Session runner 隔离
- Permission callbacks

---

## 八、核心价值验证（README vs 代码）

| README 声称 | 代码验证 | 结果 |
|------------|---------|------|
| CLI 工具 | `main.tsx` + Commander.js | ✅ |
| 文件编辑 | `tools/FileEditTool/` | ✅ |
| 命令执行 | `tools/BashTool/` | ✅ |
| 搜索代码库 | `tools/GrepTool/` | ✅ |
| 工作流协调 | `coordinator/` + `AgentTool/` | ✅ |
| ~1900 文件 | 实际 55 个 src 子目录 | ⚠️ 目录多但文件数未验证 |
| 512,000+ 行 | 主要模块总计 ~12K 行 | ❌ **严重夸大** |
| QueryEngine 46K 行 | 实际 1295 行 | ❌ **严重夸大** |
| Rust 重写（dev/rust）| 分支不存在 | ❌ **未实现** |

**结论**：README 大幅注水，实际代码质量需实测。

---

## 九、泛用代码析出

### Tier 1（零依赖，可直接复用）

| 代码 | 位置 | 用途 |
|------|------|------|
| `signal.ts`（事件信号）| utils/signal.ts | 3行替代 15 处 Set+listener 样板 |
| `CircularBuffer.ts`（环形缓冲）| utils/CircularBuffer.ts | 固定窗口消息历史 |
| `QueryGuard.ts`（状态机）| utils/QueryGuard.ts | 防止并发 re-entry |
| `abort-controller.ts` | utils/abortController.ts | WeakRef 内存安全 AbortController |
| `lockfile.ts`（懒加载）| utils/lockfile.ts | 延迟加载 proper-lockfile，省 8ms |
| `memdir truncation` | memdir/memdir.ts | MEMORY.md 200行/25KB 截断 |
| `permission-frame` | hooks/toolPermission/ | 工具权限四模式 |

### Tier 2（轻量依赖，需适配）

| 代码 | 位置 | 用途 |
|------|------|------|
| Bridge 消息协议 | bridge/bridgeMessaging.ts | IDE-CLI 双向通信 |
| Worktree 隔离 | utils/worktree.ts | Git 并行开发 |
| Hook 系统 | utils/hooks/ | Prompt/Agent Hook 链 |

---

## 十、对 OpenClaw 的意义

| Claude Code 特性 | OpenClaw 可借鉴 | 难度 |
|-----------------|----------------|------|
| MEMDIR 记忆截断 | 直接复用 truncation 逻辑 | ⭐ |
| 并发 Guard | 防止 subagent 与主 session 打架 | ⭐ |
| AbortController WeakRef | 更健壮的超时终止 | ⭐ |
| 事件信号 | HEARTBEAT 状态通知 | ⭐ |
| 工具注册 DCE | skill 懒加载 | ⭐⭐ |
| 79 个 Hook | Hook 化架构 | ⭐⭐⭐ |
| Bridge 协议 | IDE 集成参考 | ⭐⭐⭐ |
| MCP 集成 | OpenClaw 已有 | ⭐ |

---

## 十一、总结

| 维度 | 评分 |
|------|------|
| 架构设计 | ★★★★★ 模块化程度极高，目录职责单一 |
| 代码规模 | 参考有限，README 注水严重 |
| 可移植性 | ★★★★☆ Tier 1 模块可直接借鉴 |
| 安全设计 | ★★★★☆ 权限模型完善 |
| 创新点 | ★★★☆☆ 核心仍是 Tool-use Agent 范式 |
| 研究价值 | ★★★★★ 真实生产级 Agent CLI 全架构 |

**最大收获**：记忆系统设计（truncation + memdir）和 WeakRef AbortController 是最容易移植到 OpenClaw 的高价值模块。

---

## 参考资料

- [Leak 来源 @Fried_rice](https://x.com/Fried_rice/status/2038894956459290963)
- [instructkr/claude-code](https://github.com/instructkr/claude-code)
- [Ink - React for CLI](https://github.com/vadimdemedes/ink)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Anthropic Claude Code](https://docs.anthropic.com/en/docs/claude-code)
