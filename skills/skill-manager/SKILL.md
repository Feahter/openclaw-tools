---
name: skill-manager
description: GitHub Skills 生命周期管理器。用于扫描 Skills 目录、检查 GitHub 更新、批量升级 Skill 包装器。当用户想"检查更新"、"列出 Skills"或"删除 Skill"时触发。
---

# Skill 生命周期管理器

管理 GitHub 封装的 Skills 库，自动化检测更新和辅助重构。

## 核心能力

| 能力 | 功能 |
|------|------|
| **审计** | 扫描本地 Skills 目录，识别 GitHub 封装的 Skills |
| **检查** | 通过 GitHub API 对比本地 commit hash 与远程 |
| **报告** | 生成状态报告（过期/当前） |
| **更新** | 提供结构化流程升级 Skill |
| **清单** | 列出所有 Skills，支持删除 |

## 使用方式

| 命令 | 触发词 | 说明 |
|------|--------|------|
| `/skill-manager check` | "检查更新" | 扫描所有 Skills 的更新 |
| `/skill-manager list` | "列出 Skills" | 列出所有本地 Skills |
| `/skill-manager delete <name>` | "删除 Skill xxx" | 删除指定 Skill |

## 工作流程

### 检查更新

1. **运行扫描**：
   ```bash
   python scripts/scan_and_check.py
   ```

2. **查看报告**：
   ```
   输出 JSON 摘要，例如：
   - yt-dlp: 过期（落后 50 commits）
   - ffmpeg-tool: 过期（落后 2 commits）
   - 其他: 当前
   ```

3. **用户选择更新**：
   ```
   你: "更新 yt-dlp"
   ```

### 更新 Skill

1. **获取新上下文**：拉取远程最新 README
2. **差异分析**：
   - 对比新版 README 与旧版 `SKILL.md`
   - 识别新功能、废弃参数、用法变化
3. **重构**：
   - 重写 `SKILL.md` 反映新功能
   - 更新 frontmatter 中的 `github_hash`
   - 更新 `wrapper.py`（如 CLI 参数变化）
4. **验证**：运行快速验证

## 元数据依赖

此管理器依赖 `github-to-skills` 的元数据标准：

```yaml
---
github_url: <原始仓库URL>
github_hash: <本地commit-hash>
version: <标签>
---
```

**检查逻辑**：如果 `remote_hash != local_hash` → 标记为过期

## 脚本说明

| 脚本 | 用途 |
|------|------|
| `scripts/scan_and_check.py` | 扫描目录、解析 frontmatter、获取远程版本、返回状态 |
| `scripts/list_skills.py` | 列出所有已安装 Skills（含类型和版本） |
| `scripts/delete_skill.py` | 永久删除 Skill 文件夹 |
| `scripts/update_helper.py` | （可选）更新前备份文件 |

## 使用示例

```
你: "检查我的 Skills 有什么更新"
AI: → 运行 scan_and_check.py
    → 报告：
       • yt-dlp: 过期 (v2024.01.01 → v2024.02.15)
       • ffmpeg: 当前
       • 其他 5 个 Skills: 当前
    → "需要我更新哪个？"

你: "更新 yt-dlp"
AI: → 获取远程最新 README
    → 对比变更：发现新增 --sleep-requests 参数
    → 更新 SKILL.md
    → 更新 github_hash
    → 完成
```

## 最佳实践

| 场景 | 建议 |
|------|------|
| **批量检查** | 定期（如每周）运行 check |
| **更新前** | 先看 changelog，了解breaking changes |
| **更新后** | 运行 `skill-evolution-manager` 还原用户偏好 |
| **删除前** | 确认不再需要，避免误删 |

## 与其他 Skill 配合

| 场景 | 工作流 |
|------|--------|
| 创建新 Skill | `github-to-skills` → 安装 → `skill-manager` 监控 |
| 检查更新 | `skill-manager check` → `skill-manager update` |
| 保留用户偏好 | `skill-manager update` → `skill-evolution-manager align` |
