# 泛用性分级标准与常见模式库

## 核心判断标准

```
泛用性 = 与业务解耦程度 × 解决问题的普遍性 × 实现质量
```

**硬标准：去掉所有业务 import 后，代码还能独立运行吗？**

---

## 分级标准

### ⭐⭐⭐⭐⭐ 直接可移植

**特征：**
- 文件顶部没有业务相关的 import（只有 Node.js 内置模块或通用库）
- 函数参数是通用类型（string、number、callback、interface），不是业务类型
- 解决的问题在任何同类项目中都会遇到
- 代码量小（< 200 行）但解决了一个完整问题
- 注释里有"为什么这么做"（说明踩过坑，经验沉淀）

**行动：** 直接复制，最多改 import 路径

---

### ⭐⭐⭐⭐ 改造后可移植

**特征：**
- 有少量业务 import，但核心逻辑与业务无关
- 函数参数中有 1-2 个业务类型，但可以替换为接口/回调
- 解决的问题普遍，但实现与特定框架/数据库耦合

**行动：** 将业务依赖抽象为回调函数或接口参数后移植

**改造模式：**
```typescript
// 改造前（与业务 DB 耦合）
private flushBuffer(messageId: string): void {
  const db = getDatabase(); // 业务依赖
  db.updateMessage(messageId, content); // 业务依赖
}

// 改造后（通过回调解耦）
constructor(private onFlush: (id: string, content: string) => void) {}
private flushBuffer(messageId: string): void {
  this.onFlush(messageId, this.buffers.get(messageId)!.content);
}
```

---

### ⭐⭐⭐ 思路参考

**特征：**
- 业务耦合较深，直接移植需要大量改造
- 但设计思路、算法或模式有参考价值
- 解决的问题有普遍性，但实现太特定

**行动：** 理解思路，在自己的项目中重新实现

---

## 常见高泛用性模式库

按领域分类，遇到这些场景时优先检查是否有可移植的实现：

### 进程通信

| 模式 | 描述 | 信号词 |
|------|------|--------|
| pipeId 请求-响应关联 | 用唯一 ID 关联异步请求和响应，无需状态机 | `pipeId`, `requestId`, `callbackKey` |
| 双向通信协议 | 主进程 ↔ 子进程双向消息传递 | `parentPort`, `postMessage`, `utilityProcess` |
| Deferred 模式 | 可外部 resolve/reject 的 Promise 包装 | `Deferred`, `resolve`, `reject` 作为属性 |

### LLM 集成

| 模式 | 描述 | 信号词 |
|------|------|--------|
| 推理标签过滤 | 过滤 `<think>`/`<thinking>` 标签 | `stripThinkTags`, `hasThinkTags` |
| 流式响应缓冲 | 批量写库，避免每个 chunk 都触发 DB 写入 | `streamBuffer`, `flushInterval`, `chunkBatchSize` |
| 结构化命令解析 | 解析 Agent 输出中的 `[TAG]...[/TAG]` 格式命令 | `detectCommands`, `stripCodeBlocks` |
| 渐进式知识注入 | 先注入索引，按需加载完整内容 | `skillsIndex`, `LOAD_SKILL`, `prepareFirstMessage` |
| 响应后处理管道 | 原始内容存库，清理后内容展示 | `rawContent`, `displayContent`, `systemResponses` |

### Electron 特有

| 模式 | 描述 | 信号词 |
|------|------|--------|
| Shell 环境继承 | 从登录 shell 加载 PATH，解决 Finder 启动时工具找不到的问题 | `loadShellEnvironment`, `shell -i -l -c env` |
| 子进程环境净化 | 删除 Electron 注入的干扰变量 | `prepareCleanEnv`, `NODE_OPTIONS`, `CLAUDECODE` |
| Node.js 版本修正 | 在 nvm/fnm/volta 中寻找满足最低版本要求的 Node | `findSuitableNodeBin`, `nvm`, `fnm`, `volta` |
| WASM 路径修正 | 打包环境中指向 `app.asar.unpacked` | `app.isPackaged`, `asar.unpacked` |

### 通用工程

| 模式 | 描述 | 信号词 |
|------|------|--------|
| stderr head+tail 收集 | 同时保留错误输出的头部和尾部，避免截断关键信息 | `stderrHead`, `stderrTail`, `STDERR_HEAD_MAX` |
| npm 缓存损坏自动修复 | 检测特定错误关键词，自动清理缓存后重试 | `notarget`, `_npx`, `npm cache clean` |
| 优雅关闭 + 硬超时 | 先尝试优雅停止，超时后强制 kill | `GRACE_PERIOD_MS`, `HARD_TIMEOUT_MS`, `doKill` |
| 防重入 kill 守卫 | 用 `killed` 标志防止 kill 被调用两次 | `let killed = false`, `if (killed) return` |

---

## 低泛用性的信号（快速排除）

遇到以下情况，直接跳过，不值得花时间评估：
- 文件名包含业务实体名（`UserService`、`OrderProcessor`、`ConversationManager`）
- 函数参数类型是项目特有的（`TMessage`、`ConversationId`、`AcpBackend`）
- 文件开头有 5+ 个业务模块 import
- 与数据库 schema 强耦合（直接操作表字段）
- 包含大量 UI 渲染逻辑

---

## 提取后的文件结构规范

```
workspace/code/<项目名>-patterns/
├── README.md              # 索引 + 快速上手示例
├── pipe.ts                # 功能名，不带项目前缀，用连字符
├── think-tag-detector.ts
├── streaming-buffer.ts
├── shell-env.ts
└── ...
```

每个文件顶部必须包含：
```typescript
/**
 * {功能名} — {一句话描述}
 *
 * 来源：{项目名} ({项目URL}) — {原始文件路径}
 * 许可：{许可证}
 *
 * 解决问题：
 *   {描述这段代码解决了什么普遍问题}
 *
 * 使用方式：
 *   {最简单的使用示例}
 *
 * 移植说明：
 *   {需要注意的依赖或改造点}
 */
```
