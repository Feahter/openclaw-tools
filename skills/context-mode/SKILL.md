# context-mode

**用途**：本地上下文工具集，压缩输出 + 沙箱执行 + 智能搜索

## 快速开始

```bash
# 简写命令
ctx help          # 查看帮助
ctx search <query>   # 搜索 (s)
ctx exec <code> [lang]  # 执行代码 (x)
ctx filter <content> [intent]  # 过滤大输出 (f)
ctx index         # 重建索引 (i)
```

## 功能

| 命令 | 功能 | 示例 |
|------|------|------|
| `ctx s <query>` | FTS5 智能搜索 | `ctx s 小说创作` |
| `ctx x <code>` | 沙箱执行代码 | `ctx x "print(2+2)" python` |
| `ctx f <content>` | 大输出过滤 | `ctx f "$(cat log)" error` |
| `ctx i` | 重建搜索索引 | `ctx i` |

## 效果

| 场景 | 压缩前 | 压缩后 |
|------|--------|--------|
| 大日志过滤 | 50KB | <500B (99%) |
| 代码执行 | 原始输出 | 仅 stdout |
| 搜索 | 全文件 | 相关片段 |

## 技术

- **搜索**：SQLite FTS5 + Porter 词干 + 模糊匹配
- **执行**：临时文件 + 隔离进程 + stdout 捕获
- **过滤**：意图匹配 + 上下文提取

## 文件

- `tools/context-tools.py` - 核心工具
- `tools/ctx` - 命令行包装器
- `data/context-tools.db` - 搜索索引

## 使用场景

1. **搜索本地知识**：用 `ctx s`
2. **安全执行代码**：用 `ctx x`
3. **处理大输出**：用 `ctx f`
