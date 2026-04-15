---
name: spen-memory
description: Agent 动态按需记忆系统 - 基于 SPEN 思想的轻量级记忆存储与检索。用于需要持久记忆、长程对话上下文管理的场景。支持多路检索、自动压缩、归档恢复、向量语义。
metadata:
  emoji: 🧠
  os: ["darwin", "linux"]
  requires:
    bins: ["node"]
  install:
    - id: local
      kind: local
      label: 本地安装 (Node.js 14+)
---

# SPEN-Memory v1.2.0

Agent 动态按需记忆系统 - 基于 SPEN (Spatio-Temporal Encoding) 思想的轻量级记忆存储与检索。

## 触发条件

当用户提到以下关键词时触发：
- `记忆` / `memory` / `记住` / `记得`
- `上下文` / `context` / `对话历史`
- `spen` / `时空编码`

或需要：
- 为 Agent 添加持久记忆能力
- 实现动态按需加载的记忆系统
- 长程对话上下文管理

## 功能

### 1. 记忆存储
- 事件序列存储 (对话、工具、用户等)
- 时空联合编码 (时间位置 + 空间/内容特征)
- 自动重要性评估
- 自动压缩 (超过阈值时保留关键事件)

### 2. 按需检索
- 多路检索: 时间 + 语义 + 重要性 + 向量
- 懒加载: 只加载相关记忆
- 上下文组装: 智能重建完整上下文

### 3. 归档系统
- 自动归档: 压缩时保留元信息
- 归档检索: 从归档中恢复
- 智能建议: 基于检索结果提供建议

### 4. 向量语义 (v1.2.0 新增)
- 支持多种 embedding 提供商
- 本地向量 (无需 API)
- 余弦相似度检索

## 向量语义配置

### 方式一: 本地向量 (推荐，无 API 成本)

```javascript
const memory = new SPENMemory({
    useLocalEmbedding: true,  // 无需 API
    embeddingDim: 512         // 向量维度
});
```

```bash
node cli.js init --max-size 500 --local-embedding
```

### 方式二: OpenAI

```javascript
const memory = new SPENMemory({
    enableEmbedding: true,
    embeddingProvider: 'openai',
    embeddingKey: 'sk-xxx',
    embeddingModel: 'text-embedding-3-small'
});
```

```bash
node cli.js init --max-size 500 --embedding --provider openai --api-key sk-xxx
```

### 方式三: Cohere

```javascript
const memory = new SPENMemory({
    enableEmbedding: true,
    embeddingProvider: 'cohere',
    embeddingKey: 'xxx',
    embeddingModel: 'embed-english-v3.0'
});
```

### 方式四: 本地 Ollama

```javascript
const memory = new SPENMemory({
    enableEmbedding: true,
    embeddingProvider: 'local',
    embeddingAPI: 'http://localhost:11434/api/embeddings',
    embeddingModel: 'nomic-embed-text'
});
```

## 使用方式

### 命令行

```bash
cd ~/.openclaw/workspace/skills/spen-memory

# 基础初始化
node cli.js init --max-size 500

# 启用归档
node cli.js init --max-size 500 --archive

# 启用本地向量 (推荐)
node cli.js init --max-size 500 --local-embedding

# 启用 OpenAI 向量
node cli.js init --max-size 500 --embedding --api-key your-key

# 添加记忆
node cli.js add --type "对话" --content "用户要订机票" --importance 0.9

# 检索
node cli.js retrieve --query "机票"

# 归档检索
node cli.js archive --query "机票"

# 统计
node cli.js stats
```

### 编程接口

```javascript
import SPENMemory from './spen-memory.js';

// 方式一: 本地向量 (推荐)
const memory = new SPENMemory({
    maxMemorySize: 500,
    compressionRatio: 0.3,
    enableArchive: true,
    useLocalEmbedding: true,
    persist: true
});

// 方式二: OpenAI 向量
const memory = new SPENMemory({
    maxMemorySize: 500,
    enableEmbedding: true,
    embeddingProvider: 'openai',
    embeddingKey: process.env.OPENAI_API_KEY,
    embeddingModel: 'text-embedding-3-small'
});

// 添加记忆
memory.addEvent({
    type: '对话',
    content: '用户说：帮我订机票',
    importance: 0.9
});

// 检索
const result = await memory.retrieve({
    text: '机票',
    maxResults: 5
});

console.log(result.context.text);
console.log(result.context.suggestions);
```

## 核心参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `maxMemorySize` | 1000 | 最大记忆数 |
| `compressionRatio` | 0.3 | 压缩保留比例 |
| `importanceThreshold` | 0.3 | 最低重要性 |
| `timeDecayFactor` | 0.95 | 时间衰减因子 |
| `maxRetrieve` | 5 | 最大检索数 |
| `enableArchive` | true | 启用归档 |
| `useLocalEmbedding` | false | 本地向量 |
| `enableEmbedding` | false | 向量语义 |

## 向量参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `embeddingProvider` | openai | 提供商 |
| `embeddingModel` | text-embedding-3-small | 模型 |
| `embeddingDim` | 1536 | 向量维度 |

## 检索权重配置

| 权重 | 默认值 | 说明 |
|------|--------|------|
| `semanticWeight` | 0.5 | 语义匹配权重 |
| `temporalWeight` | 0.3 | 时间接近权重 |
| `importanceWeight` | 0.2 | 重要性权重 |

## 新增功能详解

### 本地向量 (推荐)

```
优点:
• 无需 API 费用
• 完全离线可用
• 响应速度快
• 隐私安全

原理:
• 基于词 hash 的简单向量
• TF-IDF 加权
• 归一化处理
```

### 向量检索流程

```
Query → 向量化
   │
   ├─→ 本地: hash → 简单向量
   │
   └─→ API: 调用 embedding 服务
   │
   ↓
与存储的向量计算余弦相似度 → Top-k
```

## 与现有机制对比

| 特性 | memory-manager | SPEN-Memory |
|------|---------------|-------------|
| 检索方式 | 字符串匹配 | 多路索引检索 |
| 懒加载 | ❌ 全量 | ✅ 按需加载 |
| 压缩机制 | ❌ | ✅ 自动压缩 |
| 归档恢复 | ❌ | ✅ |
| 智能建议 | ❌ | ✅ |
| 向量语义 | ❌ | ✅ |
| 时间感知 | ❌ | ✅ 时间衰减 |

## 技术细节

### 时空编码

- **时间编码**: 周期性特征 (小时/星期) + 绝对时间戳
- **空间编码**: 关键词提取 + 语义 Hash + 意图推断

### 多路检索

```
Query → 编码
   │
   ├─→ 时间检索 → 时间衰减分数
   │
   ├─→ 语义检索 → 关键词重叠分数
   │
   ├─→ 重要性检索 → 重要性分数
   │
   └─→ 向量检索 → 余弦相似度
   │
   ↓
加权融合 → Top-k 选择 → 懒加载 → 上下文组装
```

## 依赖

- Node.js 14+
- 无外部依赖 (纯 JavaScript)

## 文件结构

```
spen-memory/
├── SKILL.md           # Skill 定义
├── spen-memory.js    # 核心库 (v1.2.0)
├── cli.js             # 命令行工具 (v1.2.0)
├── test.js           # 测试
└── package.json     # 包配置
```

---

*Last Updated: 2026-03-13 v1.2.0*
