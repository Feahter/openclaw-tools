# Claude Code 源码吸收 (2026-04-01)

来源: [instructkr/claude-code](https://github.com/instructkr/claude-code) (Leak, 2026-03-31)

## 目录

| 文件 | 来源 | Tier | 说明 |
|------|------|------|------|
| `signal.ts` | `src/utils/signal.ts` | 1 | 纯事件信号，无状态，最小化事件系统 |
| `circular-buffer.ts` | `src/utils/CircularBuffer.ts` | 1 | 固定大小 Ring Buffer，Agent 消息历史管理 |
| `query-guard.ts` | `src/utils/QueryGuard.ts` | 1 | 异步查询生命周期状态机，兼容 React useSyncExternalStore |
| `abort-controller.ts` | `src/utils/abortController.ts` | 1 | 内存安全的父子 AbortController，WeakRef 防泄漏 |
| `lazy-lockfile.ts` | `src/utils/lockfile.ts` | 1 | proper-lockfile 延迟加载，避免 graceful-fs 启动开销 |
| `truncation.ts` | `src/memdir/memdir.ts` | 1 | MEMORY.md 截断（200行/25KB），防 Token 爆炸 |
| `permission-frame.ts` | `src/hooks/toolPermission/` | 1 | 工具权限框架（default/plan/auto/bypass 四模式）|
| `teammate-mailbox.ts` | `src/utils/teammateMailbox.ts` | 2 | 文件锁 + JSON 邮箱，Agent 群消息传递 |
| `hook-helpers.ts` | `src/utils/hooks/hookHelpers.ts` | 2 | LLM 验证 Hook 工具，结构化输出强制 |
| `tool-registry.ts` | `src/tools.ts` | 2 | 特性开关工具注册，适配 Bun bun:bundle DCE |

## Tier 定义

| Tier | 依赖 | 可移植性 |
|------|------|---------|
| 1 | 零依赖，纯 TypeScript | 100%，直接复制使用 |
| 2 | 少量外部依赖（zod, proper-lockfile）| 70-80%，需简单适配 |

## 未吸收（依赖过重或过于定制）

- `Shell.ts` / `ShellCommand.ts` — 依赖太重，需要完整 subprocess 环境
- `AsyncHookRegistry.ts` — 依赖 Agent SDK 类型
- `execAgentHook.ts` — 依赖 Agent SDK，600+ 行
- Bridge 协议 — 依赖 VS Code/JetBrains SDK

## 使用示例

```typescript
// 1. 事件信号
import { createSignal } from './signal'
const changed = createSignal<[string]>()
changed.subscribe((source) => console.log('changed:', source))
changed.emit('userSettings')

// 2. 环形缓冲区（Agent 消息窗口）
import { CircularBuffer } from './circular-buffer'
const buf = new CircularBuffer<string>(100)
buf.add('hello')
const recent = buf.getRecent(10)

// 3. 查询 Guard（防止并发）
import { QueryGuard } from './query-guard'
const guard = new QueryGuard()
if (guard.reserve()) {
  // queue processing
  const gen = guard.tryStart()
  if (gen !== null) {
    // run query
    guard.end(gen)
  }
}

// 4. 内存安全 AbortController
import { createChildAbortController } from './abort-controller'
const child = createChildAbortController(parentCtrl)
child.abort() // 仅终止 child，不影响 parent

// 5. MEMORY.md 截断
import { truncateEntrypointContent } from './truncation'
const result = truncateEntrypointContent(longContent)
if (result.wasTruncated) console.warn(result.content)

// 6. 工具权限
import { createPermissionSystem } from './permission-frame'
const perm = createPermissionSystem({ mode: 'default' })
const result = perm.check('BashTool', { command: 'ls' })
```
