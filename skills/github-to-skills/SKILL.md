---
name: github-to-skills
description: GitHub 操作中心：转换仓库为 Skills + gh CLI 操作。触发场景：(1) 打包 GitHub 仓库为 Skill (2) GitHub PR/CI/API 操作 (3) 检查更新、列出/删除 Skills。
---

# GitHub 操作中心

GitHub 相关操作的全能工具箱。

## Part A: GitHub 转 Skills 工厂

自动将 GitHub 仓库转换为可用的 AI Skills。

### 核心功能

1. **分析**：获取仓库元数据（描述、README、最新 commit hash）
2. **脚手架**：创建标准化 Skill 目录结构
3. **元数据注入**：生成带扩展 frontmatter 的 `SKILL.md`
4. **包装器生成**：创建调用脚本

### 使用方式

**触发**：`/github-to-skills <github_url>` 或 "把这个仓库打包成 Skill: <url>"

### 工作流程

1. **获取信息**：`python scripts/fetch_github_info.py <repo_url>`
2. **分析规划**：阅读 README，理解调用方式
3. **生成 Skill**：创建 `SKILL.md` + `scripts/wrapper.py`
4. **验证**：确认 commit hash 正确

### 必需元数据 Schema

```yaml
---
name: <kebab-case-repo-name>
description: <简洁描述>
github_url: <原始仓库URL>
github_hash: <创建时的commit-hash>
version: <标签或 0.1.0>
created_at: <ISO-8601日期>
entry_point: scripts/wrapper.py
dependencies: [<主要依赖>]
---
```

---

## Part B: GitHub CLI 操作（gh）

使用 `gh` CLI 与 GitHub 交互。

### 使用原则

- 不在 git 目录时，**必须**用 `--repo owner/repo` 指定仓库
- 或直接使用 URL

### Pull Requests

| 操作 | 命令 |
|------|------|
| 检查 PR CI 状态 | `gh pr checks <PR号> --repo owner/repo` |
| 列出最近 workflow | `gh run list --repo owner/repo --limit 10` |
| 查看运行详情 | `gh run view <run-id> --repo owner/repo` |
| 查看失败日志 | `gh run view <run-id> --repo owner/repo --log-failed` |

### API 高级查询

使用 `gh api` 获取其他子命令不支持的数据：

```bash
# 获取 PR 特定字段
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'

# 列出 issues
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```

### JSON 输出

大多数命令支持 `--json` 结构化输出，用 `--jq` 过滤：

```bash
gh issue list --repo owner/repo --json state,title --jq '.[] | select(.state == "open")'
```

---

## 脚本工具

| 脚本 | 用途 |
|------|------|
| `scripts/fetch_github_info.py` | 获取仓库信息（README、hash） |
| `scripts/scan_and_check.py` | 检查 Skills 更新（来自 skill-manager） |
| `scripts/list_skills.py` | 列出所有 Skills |

---

## 与其他 Skill 配合

| 场景 | 工作流 |
|------|--------|
| 创建 Skill | `github-to-skills` → 安装 |
| 检查更新 | `skill-manager check` |
| 持续改进 | `skill-evolution-manager` |

---

## 注意事项

- 确保 `gh` CLI 已安装且认证
- 确保 Git 可用（用于获取 commit hash）
- 操作前确认仓库路径正确
