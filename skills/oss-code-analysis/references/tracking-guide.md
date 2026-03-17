# 核心路径追踪指南

## 什么是"核心路径"

核心路径是项目最能体现其价值的一条主流程。选择标准：
- 覆盖 README 中最重要的那条价值主张
- 从用户可感知的输入开始，到用户可感知的输出结束
- 不超过 7 层调用深度（超过说明需要重新选择起点）

**示例：**
- 聊天应用：用户发消息 → Agent 处理 → 回复展示
- 数据管道：文件上传 → 解析 → 存储 → 查询返回
- CLI 工具：命令输入 → 参数解析 → 核心逻辑 → 输出

---

## 追踪步骤

### Step 1：找入口

```bash
# 常见入口文件
cat src/main.ts
cat src/index.ts
cat src/app.ts
cat main.py
cat cmd/main.go

# 或者从 package.json 的 main/scripts 字段找
cat package.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('main',''), d.get('scripts',{}))"
```

### Step 2：找第一个关键分叉

入口文件通常是初始化代码，真正的业务逻辑在第一个"分叉点"之后。
分叉点的特征：根据输入类型/状态决定走哪条路。

### Step 3：逐层追踪，记录边界

每遇到以下情况，停下来记录：
- **进程边界**：`fork()`、`spawn()`、`Worker`、`utilityProcess`
- **网络边界**：HTTP 请求、WebSocket、IPC
- **持久化边界**：DB 写入、文件写入
- **异步边界**：`Promise.race()`、`setTimeout()`、超时机制
- **错误边界**：`try/catch` 块，特别是有业务逻辑的 catch

### Step 4：画调用链

```
用户输入
  └─ ChannelPlugin.onMessage()          [channels/plugins/]
       └─ SessionManager.dispatch()      [channels/core/]
            └─ WorkerManage.create()     [process/]
                 └─ AcpAgentManager()    [process/task/]  ← 进程边界
                      └─ AcpConnection.sendPrompt()       [agent/acp/]
                           └─ ChildProcess (claude CLI)   ← 子进程边界
```

---

## 关键文件记录模板

每个关键文件用以下格式记录（保持简洁，一个文件不超过 5 行）：

```
文件：src/agent/acp/AcpConnection.ts（1051 行）
职责：管理与 ACP CLI 子进程的 JSON-RPC 通信
关键设计：
  - pendingRequests Map 关联请求-响应（requestId 模式）
  - 区分"启动阶段"和"运行阶段"的进程退出，分别处理
  - npm 缓存损坏自动检测 + 清理重试
依赖：child_process, AcpBackend（接口）
```

---

## 四个边界的重点检查项

### 进程/线程边界
- 通信协议是什么（JSON-RPC、自定义协议、共享内存）？
- 进程崩溃时如何恢复？
- 有没有超时保护？

### 持久化边界
- 写库频率（每条消息？批量？定时？）
- 流式数据如何缓冲（防止每个 chunk 都写库）？
- 事务边界在哪里？

### 错误边界
- catch 后是静默吞掉、打日志、还是向上抛？
- 有没有重试机制？重试几次？退避策略？
- 用户能感知到错误吗？

### 异步协调
- 有没有 `Promise.race()` 实现超时？
- 有没有并发控制（防止同时发起太多请求）？
- 有没有取消机制（用户中断时能停止吗）？
