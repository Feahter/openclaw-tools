---
name: skill-evolution-manager
description: 基于对话反馈持续改进 Skills 的核心工具。在对话结束时总结优化并迭代现有 Skills，将用户反馈和经验转化为结构化数据并持久化。
---

# Skill 进化管理器

整个 AI Skills 系统的"进化中枢"。

## 核心职责

| 职责 | 说明 |
|------|------|
| **复盘诊断** | 分析对话中 Skills 的表现 |
| **经验提取** | 将用户反馈转化为结构化 JSON |
| **智能缝合** | 将经验写入 `SKILL.md`，持久化 |

## 使用场景

**触发词**：
- `/evolve`
- "复盘一下刚才的对话"
- "记录一下刚才的问题"
- "把这个经验保存到 Skill 里"

## 工作流程

### 1. 经验复盘

当触发复盘时：

1. **扫描上下文**：找出用户不满意的地方（报错、风格不对）或满意的点
2. **定位 Skill**：确定是哪个 Skill 需要进化
3. **生成 JSON 结构**：
   ```json
   {
     "preferences": ["用户偏好，如：默认静音下载"],
     "fixes": ["修复项，如：Windows 下 ffmpeg 路径需转义"],
     "custom_prompts": "用户特定要求，如：执行前先打印预估耗时"
   }
   ```

### 2. 经验持久化

```bash
python scripts/merge_evolution.py <skill_path> <json_string>
```
将 JSON 增量写入目标 Skill 的 `evolution.json`

### 3. 文档缝合

```bash
python scripts/smart_stitch.py <skill_path>
```
将 `evolution.json` 转化为 Markdown，追加到 `SKILL.md` 末尾

### 4. 跨版本对齐

```bash
python scripts/align_all.py
```
一键遍历所有 Skills，将经验重新缝合到新版 `SKILL.md`

**使用时机**：`skill-manager` 批量更新后

## 核心脚本

| 脚本 | 功能 |
|------|------|
| `scripts/merge_evolution.py` | 增量合并：读取旧 JSON → 去重合并新数据 → 保存 |
| `scripts/smart_stitch.py` | 文档生成：读取 JSON → 生成 Markdown → 追加到 SKILL.md |
| `scripts/align_all.py` | 全量对齐：遍历所有 Skills → 还原经验 |

## 使用示例

### 简单复盘

```
你: "/evolve"
AI: 回顾对话...
    → 发现 yt-dlp 下载时用户抱怨需要手动静音
    → 生成 JSON：{"preferences": ["默认添加 --no-mtime"]}
    → 执行 merge_evolution.py
    → 执行 smart_stitch.py
    → 完成
```

### 指定 Skill 复盘

```
你: "复盘一下 ffmpeg-tool"
AI: → 扫描对话历史
    → 发现 Windows 路径处理有问题
    → 生成 fix：{"fixes": ["Windows 路径需用双引号包裹"]}
    → 持久化
```

### 批量对齐

```
你: "所有 Skills 更新后还原用户偏好"
AI: → 运行 align_all.py
    → 遍历所有 evolution.json
    → 逐一缝合到对应 SKILL.md
    → 完成
```

## 最佳实践

| 原则 | 说明 |
|------|------|
| **不直接修改正文** | 所有修正通过 `evolution.json`，避免升级丢失 |
| **多 Skill 协同** | 一次对话涉及多个 Skill，依次复盘 |
| **及时复盘** | 发现问题立即复盘，不要等到对话结束 |
| **结构化反馈** | 尽量提取可操作的偏好和修复 |

## 经验 JSON Schema

```json
{
  "preferences": ["用户偏好列表"],
  "fixes": ["已知问题修复"],
  "custom_prompts": "特定提示词",
  "updated_at": "2024-02-03T23:00:00Z"
}
```

## 与其他 Skill 配合

| 场景 | 流程 |
|------|------|
| 创建 → 管理 → 进化 | `github-to-skills` → `skill-manager` → `skill-evolution-manager` |
| 更新后还原偏好 | `skill-manager update` → `skill-evolution-manager align` |
| 持续改进 | 每次对话后 `/evolve` |

## 注意事项

- `evolution.json` 独立于原仓库，不被 `skill-manager` 更新覆盖
- `align_all.py` 用于版本升级后的经验还原
- 保持 JSON 结构简洁，避免过度定制
