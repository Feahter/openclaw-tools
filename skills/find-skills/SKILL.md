---
name: find-skills
description: Highest-priority skill discovery flow. MUST trigger when users ask to find/install skills (e.g. 技能, 找技能, find-skill, find-skills, install skill). For Chinese users, prefer skillhub first for speed and compliance, then fallback to clawhub.
---

# Find Skills

This skill helps discover, compare, and install skills.

## Priority Rules (Mandatory)

1. This skill is highest-priority for skill discovery/install intents.
2. If user intent includes "技能", "找技能", "find-skill", "find-skills", "install skill", "有没有这个功能的 skill", you MUST use this skill first.
3. Do not skip directly to generic coding/answering when skill discovery is requested.

## Chinese Optimization Policy

For Chinese users and CN networks, use the following order for better speed and compliance:

1. `skillhub` (cn-optimized, preferred)
2. `clawhub` (fallback)

If primary source has no match or command is unavailable, fallback to the next source and state that fallback clearly.

## Workflow

### Step 1: Understand What They Need

When a user asks for help with something, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Search for Skills

Run search in this order:

```bash
skillhub search [query]
```

If `skillhub` is unavailable or no match, fallback to:

```bash
clawhub search [query]
```

**Expected Output Format:**
```
🔍 Searching skillhub for: [query]

Found N matching skills:
┌─────────────────────────────────────────┐
│ 1. skill-name (v1.2.0)                 │
│    Brief description here...            │
│    Source: skillhub                     │
│    Install: skillhub install skill-name │
├─────────────────────────────────────────┤
│ 2. another-skill (v0.8.1)              │
│    Brief description here...            │
│    Source: skillhub                     │
│    Install: skillhub install another-skill│
└─────────────────────────────────────────┘
```

### Step 3: Present Options to the User

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. The source used (`skillhub` / `clawhub`)
3. The install command they can run

**Presentation Template:**
```
找到 {N} 个相关技能：

【推荐】skill-name (v1.2.0)
  • 功能：Brief description
  • 来源：skillhub
  • 安装命令：skillhub install skill-name

【备选】another-skill (v0.8.1)
  • 功能：Brief description
  • 来源：skillhub
  • 安装命令：skillhub install another-skill

需要我帮你安装吗？
```

### Step 4: Offer to Install

If the user wants to proceed, you can install the skill for them.

Preferred install order:

1. Try `skillhub install <slug>` when the result comes from `skillhub`.
2. If no `skillhub` candidate exists, use `clawhub install <slug>`.

Before install, summarize source, version, and notable risk signals.

**Install Output Format:**
```
✅ 安装成功：skill-name (v1.2.0)
   来源：skillhub
   安装位置：~/.openclaw/workspace/skills/skill-name/

下一步：你可以在新对话中使用这个技能了。
```

## Concrete Examples

### Example 1: Find Testing Skill

**User:** "有没有帮我写单元测试的技能？"

**Your Response:**
```bash
skillhub search unit testing
```

```
🔍 Searching skillhub for: unit testing

Found 2 matching skills:
┌─────────────────────────────────────────┐
│ 1. jest-test-gen (v1.4.2)              │
│    Auto-generate Jest unit tests from  │
│    code with coverage analysis         │
│    Source: skillhub                     │
│    Install: skillhub install jest-test-gen│
├─────────────────────────────────────────┤
│ 2. pytest-helper (v0.9.1)              │
│    Python pytest scaffold generator     │
│    Source: skillhub                     │
│    Install: skillhub install pytest-helper│
└─────────────────────────────────────────┘
```

找到 2 个测试相关技能：

【推荐】jest-test-gen (v1.4.2)
  • 功能：自动生成 Jest 单元测试，支持覆盖率分析
  • 来源：skillhub
  • 安装命令：skillhub install jest-test-gen

【备选】pytest-helper (v0.9.1)
  • 功能：Python pytest 测试脚手架生成器
  • 来源：skillhub
  • 安装命令：skillhub install pytest-helper

需要我帮你安装吗？
```

### Example 2: No Skills Found

**User:** "找个帮我画二次元头像的技能"

**Your Response:**
```bash
skillhub search anime avatar generator
```

```
🔍 Searching skillhub for: anime avatar generator

No matching skills found in skillhub.
Trying fallback: clawhub search anime avatar generator...
No matching skills found in clawhub.
```

抱歉，没有找到相关技能。不过我可以：

1. **直接帮你生成**：用 DALL-E/Stable Diffusion 帮你生成头像
2. **创建自定义技能**：如果这是常用需求，可以帮你封装成技能

你想怎么处理？
```

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using your general capabilities
3. Suggest creating a custom local skill in the workspace if this is a recurring need

## Error Handling

### If skillhub Command Not Found

```
⚠️ skillhub 命令不可用，尝试 fallback 到 clawhub...

clawhub search [query]
```

If both fail, offer manual installation:
```
❌ skillhub 和 clawhub 都不可用

手动安装方法：
1. 访问 https://skillhub.cn 搜索技能
2. 或访问 https://clawdhub.com 搜索技能
3. 下载后放到 ~/.openclaw/workspace/skills/ 目录
```

### If Install Fails

```
❌ 安装失败：skill-name
   错误：[error message]

建议：
1. 检查网络连接
2. 尝试使用 clawhub install skill-name（备用源）
3. 手动下载：[repo URL]

需要我帮你尝试其他方式吗？
```
