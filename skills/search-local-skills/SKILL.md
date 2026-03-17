---
name: search-local-skills
description: |
  本地 Skills 按需检索工具。当你不确定是否有某个能力、需要查找某类任务对应的 skill、
  或想知道本地安装了哪些相关工具时，使用此 skill 搜索本地索引。
  
  触发场景：
  - "有没有能做 X 的 skill？"
  - "我想 [做某件事]，有对应工具吗？"
  - 任何需要某种专项能力但不确定是否已安装对应 skill 时
  - 作为 skills 按需加载的中继入口：先搜索，再读取匹配 skill 的 SKILL.md 执行
  
  注意：这是本地已安装 skills 的搜索，不是从网络安装新 skill。
metadata:
  openclaw:
    emoji: "🔍"
---

# Search Local Skills

本地 skills 按需检索中继。用于在不全量加载所有 skills 描述的前提下，按需找到并激活正确的 skill。

## 工作流程

```
用户需求 → search-local-skills 搜索 → 找到匹配 skill → read SKILL.md → 按 skill 指令执行
```

## 第一步：构建/更新索引

索引文件位于 `{SKILL_DIR}/scripts/skills-index.json`。首次使用或 skills 有变化时需重建：

```bash
{NODE} {SKILL_DIR}/scripts/build-index.js
```

其中 `{NODE}` 为可用的 node 路径（见下方"查找 Node"），`{SKILL_DIR}` 为本 SKILL.md 所在目录。

### 查找 Node

```bash
# 按优先级尝试
which node 2>/dev/null || \
ls ~/.nvm/versions/node/*/bin/node 2>/dev/null | sort -V | tail -1
```

## 第二步：搜索

```bash
{NODE} {SKILL_DIR}/scripts/search.js "<查询词>" [--top 8]
```

**示例：**
```bash
node scripts/search.js "翻译"
node scripts/search.js "image generation" --top 5
node scripts/search.js "pdf 提取"
node scripts/search.js "小红书"
node scripts/search.js "excel 数据分析"
```

**输出格式：**
```json
{
  "query": "翻译",
  "totalSkills": 185,
  "matches": [
    {
      "name": "baoyu-translate",
      "skillMd": "/path/to/baoyu-translate/SKILL.md",
      "dir": "/path/to/baoyu-translate",
      "score": 24,
      "description": "Translates articles and documents...",
      "triggers": []
    }
  ]
}
```

## 第三步：加载并执行匹配的 Skill

找到匹配结果后，读取对应的 `skillMd` 路径：

```
read {matches[0].skillMd}
```

然后按该 skill 的指令完成用户任务。

## 索引自动同步（无需手动维护）

`search.js` 在每次搜索前自动检测索引是否过期，触发条件：

| 触发条件 | 说明 |
|---------|------|
| 索引文件不存在 | 首次使用 |
| 任意 SKILL.md 的 mtime > 索引 builtAt | skill 内容被修改 |
| 当前 skill 目录数 ≠ 索引记录数 | skill 被安装或卸载 |
| 传入 `--force-rebuild` 参数 | 手动强制刷新 |

检测到变化时自动调用 `build-index.js` 重建，整个过程对调用方透明（重建信息输出到 stderr，不影响 stdout 的 JSON 结果）。

**手动强制重建：**
```bash
{NODE} {SKILL_DIR}/scripts/search.js "任意查询" --force-rebuild
```

## 搜索技巧

| 场景 | 推荐查询词 |
|------|-----------|
| 文档处理 | `pdf`, `docx`, `xlsx`, `pptx` |
| 图像生成 | `image generation`, `生图`, `画图` |
| 翻译 | `translate`, `翻译` |
| 社交媒体 | `小红书`, `微博`, `twitter`, `wechat` |
| 代码/开发 | `code review`, `git`, `devops` |
| 数据分析 | `data`, `excel`, `csv`, `分析` |
| 网页/浏览器 | `browser`, `url`, `web` |

## 无匹配时的处理

如果搜索无结果或分数很低（< 5），说明本地没有对应 skill：
1. 告知用户当前没有匹配的本地 skill
2. 尝试用通用能力直接完成任务
3. 可建议用 clawdhub skill 搜索安装新 skill

## 路径变量说明

在实际执行命令时，替换以下占位符：
- `{SKILL_DIR}` → 本 SKILL.md 所在的目录绝对路径（即 `~/.openclaw/workspace/skills/search-local-skills`）
- `{NODE}` → 实际可用的 node 二进制路径
