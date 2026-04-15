---
name: skill-agent-creator
description: |
  AI Agent 创建专家。基于全网最佳实践，帮助用户设计、构建和优化 AI Agent 系统。
  
  **触发场景**：
  - 用户说"创建/设计/构建 Agent"
  - 用户说"agent 怎么写"、"agent 架构"
  - 用户说"多 agent 系统"、"agent 设计模式"
  - 用户说"帮我做个 agent"
  
  **输出**：完整的 Agent 设计方案 + 代码框架
  
  **基于 docs/agent-creation/ 经验库**
---

# skill-agent-creator

AI Agent 创建专家 — 从设计到落地的完整方法论。

## 核心理念

**不做玩具 Agent，做生产级 Agent。**

每个 Agent 都应该能够：
- 🎯 **精准触发** — 只在被需要时激活
- 🧠 **记忆连续** — 跨会话保持上下文
- 🔄 **自进化** — 从错误中学习，持续改进
- 🛡️ **安全可控** — 边界清晰，危险操作需确认

---

## 核心能力

### 1. 需求分析

快速理解用户需求，推荐合适方案：

```typescript
interface AgentRequirement {
  // 任务类型
  taskType: 'single' | 'multi' | 'planning' | 'research';
  
  // 复杂度
  complexity: 'low' | 'medium' | 'high';
  
  // 是否需要外部工具
  needsTools: boolean;
  
  // 是否需要多 Agent
  needsMultiAgent: boolean;
  
  // 质量要求
  qualityPriority: 'speed' | 'quality' | 'balanced';
}
```

### 2. 架构设计

根据需求生成架构方案：

| 复杂度 | 推荐架构 |
|--------|---------|
| 低 | Single Agent + Tools |
| 中 | Single Agent + Memory |
| 高 | Multi-Agent + Planning |
| 研究级 | Multi-Agent + Memory + Self-Evolution |

### 3. 代码生成

生成生产级代码框架：
- TypeScript / Python
- 支持主流框架（OpenAI SDK, LangChain, AutoGen）
- 完整的错误处理
- 日志和可观测性

### 4. 自进化集成 ⭐

内置自进化机制，让 Agent 越用越聪明：

```typescript
// 自进化闭环
const selfEvolutionLoop = {
  trigger: ['error', 'correction', 'repeated_mistake'],
  
  actions: {
    log: '.learnings/ERRORS.md',
    analyze: 'extractPatterns()',
    promote: 'updateKnowledgeBase()'
  },
  
  promotion: {
    threshold: 3, // 出现3次晋升
    targets: ['SOUL.md', 'AGENTS.md', 'TOOLS.md']
  }
};
```

---

## 工作流程

### 阶段 1: 需求捕获 (5分钟)

```markdown
## 需求分析

1. **任务类型**：单 Agent / 多 Agent / 规划型
2. **核心能力**：要解决什么问题？
3. **触发场景**：什么时候激活？
4. **输入输出**：什么格式？
5. **质量要求**：速度优先 / 质量优先
6. **是否需要记忆**：跨会话上下文？
```

**追问清单**：
- [ ] Agent 需要访问外部 API/数据库吗？
- [ ] Agent 需要持久记忆吗？
- [ ] 是否需要多个 Agent 协作？
- [ ] 有什么安全边界需要设置？
- [ ] 如何评估 Agent 效果？

### 阶段 2: 架构设计 (10分钟)

**设计输出模板**：

```markdown
## Agent 架构设计

### 基本信息
- **名称**:
- **类型**:
- **核心能力**:

### 组件设计

#### Model
- **选择**:
- **理由**:

#### Tools
| 工具名 | 功能 | 触发条件 |
|--------|------|---------|
| | | |

#### Memory
| 类型 | 存储 | 生命周期 |
|------|------|---------|
| WAL | 当前操作 | 操作确认后删除 |
| Buffer | 危险区对话 | 下次压缩后清空 |
| Long-term | 重要决策/偏好 | 永久 |

#### Instructions
**系统提示**：...
**用户提示**：...

### 自进化配置
- [ ] 启用错误日志
- [ ] 启用模式检测
- [ ] 设置晋升规则
```

### 阶段 3: 代码实现 (按需)

**生成代码结构**：

```
agent-name/
├── SKILL.md              # Skill 定义
├── src/
│   ├── index.ts          # 入口
│   ├── agent.ts          # Agent 核心
│   ├── memory.ts         # 记忆管理
│   ├── tools/            # 工具集
│   │   ├── tool1.ts
│   │   └── tool2.ts
│   ├── prompts/          # 提示词
│   └── evolution/        # 自进化 ⭐
│       ├── logger.ts
│       └── pattern.ts
├── tests/
│   └── agent.test.ts
└── README.md
```

**核心代码模板**：

```typescript
// agent.ts
class Agent {
  private memory: Memory;
  private tools: ToolRegistry;
  private evolution: SelfEvolution;
  
  async run(input: string): Promise<string> {
    // 1. WAL 记录
    await this.wal.log({ type: 'input', data: input });
    
    // 2. 推理 + 工具选择
    const { thought, tool, args } = await this.reason(input);
    
    // 3. 执行
    const result = tool ? await tool.execute(args) : null;
    
    // 4. 观察 + 学习
    await this.evolve({ thought, tool, result, input });
    
    // 5. 返回
    return this.formatOutput(result);
  }
}
```

### 阶段 4: 测试验证

**测试用例**：

```typescript
const testCases = [
  // 正常流程
  { input: '标准查询', expected: '正确响应' },
  
  // 边界情况
  { input: '空输入', expected: '友好提示' },
  { input: '超长输入', expected: '截断处理' },
  
  // 错误处理
  { input: '触发错误工具', expected: '优雅降级' },
  
  // 安全
  { input: '越界请求', expected: '安全拒绝' }
];
```

---

## 自进化集成 ⭐⭐⭐

### 为什么要自进化？

```
传统 Agent：
用户: 第一次说错 → Agent 错了
用户: 第二次说错 → Agent 又错了
用户: 第三次说错 → Agent 又错了...

自进化 Agent：
用户: 第一次说错 → 记录 [ERR-001]
用户: 第二次说错 → 发现模式 → 记录 [LRN-001]
用户: 第三次说错 → 晋升规则 → "收到用户纠正时，优先从记忆查找"
```

### 自进化配置

```yaml
# agent.yaml
self_evolution:
  enabled: true
  
  logging:
    errors: .learnings/ERRORS.md
    learnings: .learnings/LEARNINGS.md
    features: .learnings/FEATURE_REQUESTS.md
  
  triggers:
    - type: error
      action: log
    - type: correction
      action: log + analyze
    - type: repeated_mistake
      action: log + pattern + promote
  
  promotion:
    threshold: 3              # 3次出现晋升
    time_window: 30d          # 30天内
    targets:
      skill: SOUL.md, AGENTS.md, TOOLS.md
      workspace: MEMORY.md
```

### WAL Protocol 实现

```typescript
class WALProtocol {
  // 触发词检测
  private triggers = [
    /不对|不是|实际是/,     // 纠正
    /\b[A-Z][a-z]+/,        // 专有名词
    /我喜欢|我想要/,         // 偏好
    /用.*吧|就.*了/,        // 决策
  ];
  
  async log(entry: Entry) {
    // 1. 检测触发
    if (this.isTriggered(entry.text)) {
      // 2. 写入 WAL
      await this.wal.append({
        ...entry,
        timestamp: Date.now(),
        status: 'pending'
      });
    }
    
    // 3. 执行操作
    await this.execute(entry.action);
    
    // 4. 确认后删除 WAL
    await this.wal.confirm(entry.id);
  }
}
```

### 模式提炼

```typescript
async function extractPattern(errorLogs: Error[]): Promise<Pattern> {
  // 1. 聚类相似错误
  const clusters = clusterBySimilarity(errorLogs);
  
  // 2. 提取共同特征
  const features = clusters.map(c => ({
    type: c.type,
    trigger: c.trigger,
    fix: c.fix,
    count: c.count
  }));
  
  // 3. 生成 Pattern
  return {
    key: features[0].type,
    description: summarize(features),
    prevention: generatePreventionRule(features),
    recurrence: features.length
  };
}
```

---

## 设计模式参考

### 1. Single Agent + Tools

```
用户 → Agent → [Tools: API/DB/File] → 响应
         ↑
      Memory (可选)
```

**适用**：单一领域任务、中等复杂度

### 2. ReAct (Reasoning + Acting)

```
输入 → 推理 → 工具调用 → 观察 → 继续推理 → 输出
```

**适用**：复杂推理、需要外部知识的任务

### 3. Multi-Agent 协作

```
Coordinator
├── Research Agent
├── Writer Agent
└── Review Agent
```

**适用**：跨领域任务、需要多专家协作

### 4. Planning + Memory

```
用户 → Planner → 分解任务 → 执行 → 验证 → 记忆 → 下次改进
```

**适用**：需要持续改进的复杂任务

---

## 安全护栏

### 必须配置

```typescript
const guardrails = {
  // 1. 危险操作需要确认
  dangerous_actions: {
    delete: { requires_confirmation: true },
    send: { requires_confirmation: true },
    payment: { requires_confirmation: true }
  },
  
  // 2. 权限分级
  permissions: {
    read: ['search', 'read', 'view'],
    write: ['create', 'update'],
    execute: ['execute', 'delete', 'send']
  },
  
  // 3. 审计日志
  audit: {
    log_all: true,
    include_context: true,
    retention_days: 90
  }
};
```

### 自进化安全边界

```typescript
const evolutionGuardrails = {
  // 禁止自动修改
  forbidden: [
    'credentials/*',
    'SOUL.md core section',
    'MEMORY.md long-term facts'
  ],
  
  // 需要确认
  require_confirmation: [
    '修改 AGENTS.md 工作流',
    '删除学习日志',
    '修改外部集成'
  ],
  
  // 自动执行（安全）
  safe_auto: [
    '追加 .learnings/*.md',
    '更新 SESSION-STATE.md',
    '创建 memory/*.md'
  ]
};
```

---

## 示例对话

### 示例 1: 创建客服 Agent

```
用户: 我想做个客服 Agent，帮用户查订单状态

Agent: 
好的！这是一个经典的单 Agent + Tools 场景。

【需求确认】
- 任务类型：单一（查询订单）
- 复杂度：低
- 需要工具：订单 API
- 需要记忆：用户偏好（可选）

【架构设计】
┌─────────────────────────────┐
│        Customer Agent         │
├─────────────────────────────┤
│ Model: GPT-4o               │
│ Tools:                      │
│   - search_order()         │
│   - get_order_detail()     │
│ Memory: User preferences    │
│ Guardrails: None needed    │
└─────────────────────────────┘

【代码框架】
要不要我生成完整代码？
```

### 示例 2: 创建研究 Agent

```
用户: 做一个能自动研究主题、写报告的 Agent

Agent:
这需要多 Agent 协作 + 记忆系统！

【架构设计】
┌──────────────────────────────────────┐
│           Research Coordinator         │
├──────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐      │
│ │  Researcher │  │    Writer  │      │
│ │  (搜索)     │→ │  (撰写)    │      │
│ └─────────────┘  └──────┬──────┘      │
│                         ↓              │
│ ┌─────────────┐  ┌─────────────┐      │
│ │  Memory     │← │  Reviewer   │      │
│ │  (存储)     │  │  (审核)     │      │
│ └─────────────┘  └─────────────┘      │
└──────────────────────────────────────┘

【自进化】
- [x] 启用错误日志
- [x] 模式检测
- [x] 研究质量评估晋升

【代码框架】
生成中...
```

---

## 参考文档

**docs/agent-creation/ 经验库**：

| 文档 | 内容 |
|------|------|
| [README](docs/agent-creation/README.md) | 概览、创建流程、检查清单 |
| [patterns](docs/agent-creation/patterns.md) | 8种核心设计模式 |
| [self-evolution](docs/agent-creation/self-evolution.md) | 自进化机制详解 |

---

## 版本历史

| 版本 | 日期 | 变化 |
|------|------|------|
| v1.0 | 2026-03-19 | 初始版本 |
| v1.1 | 2026-03-19 | 补充自进化机制、参考最新经验库 |

---

*基于 docs/agent-creation/ 全套经验库*
