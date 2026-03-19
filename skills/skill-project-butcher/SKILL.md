---
name: skill-project-butcher
description: >
  GitHub 项目深度研究专家。当用户要分析、学习或理解一个 GitHub 项目时触发。
  触发条件：包含 "分析这个项目"、"研究一下"、"看看这个代码库"、"帮我理解"、
  "项目结构"、"怎么用"、"代码学习"、"技术调研"、"提取项目信息"、"项目概览"、
  "这个repo"、"clone了这个项目" 等，且涉及 GitHub URL 或本地代码路径。
  也适用于：克隆项目后结构分析、核心模块解读、技术选型理解。
---

# skill-project-butcher

GitHub 项目深度研究专家。帮你快速理解任意代码库的核心架构、技术选型和实现细节。

## 两种研究路径

### 路径 A：只有 GitHub URL（未克隆）
先用 GitHub API 拿基础信息，决定要不要深入。

```bash
# 1. 获取项目概览
curl -s "https://api.github.com/repos/<owner>/<repo>" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('名称:', d.get('name'))
print('描述:', d.get('description'))
print('语言:', d.get('language'))
print('Stars:', d.get('stargazers_count'))
print('主题:', d.get('topics'))
print('活跃度:', d.get('pushed_at'))
"

# 2. 获取语言占比
curl -s "https://api.github.com/repos/<owner>/<repo>/languages" | python3 -c "
import json,sys
d=json.load(sys.stdin)
total=sum(d.values())
for k,v in sorted(d.items(), key=lambda x:-x[1]):
    print(f'{k}: {v/total*100:.1f}%')
"

# 3. 获取顶级目录（不需要 clone）
curl -s "https://api.github.com/repos/<owner>/<repo>/contents/" | python3 -c "
import json,sys
items=json.load(sys.stdin)
for i in items:
    print(f'{i.get(\"type\"):4} {i.get(\"name\")}')
"

# 4. 获取 README 摘要
web_fetch("https://raw.githubusercontent.com/<owner>/<repo>/main/README.md", maxChars=5000)
# 如果 main 分支没有 README，试试 master
web_fetch("https://raw.githubusercontent.com/<owner>/<repo>/master/README.md", maxChars=5000)
```

**决策树：**
- Stars < 100 且最近 6 个月无更新 → 快速概览即可
- Stars > 1000 或 Monorepo → 建议 clone 后深度分析
- 用户明确说"分析这个项目" → clone 后走路径 B

### 路径 B：本地已有代码（已 clone 或给定路径）
适用于：已 clone 的项目、本地路径、克隆后继续分析。

```bash
# === Step 1: 项目概览 ===
cd <project_path>
echo "=== 基本信息 ==="
ls -la
cat README.md 2>/dev/null | head -80 || cat READEME.md 2>/dev/null | head -80

echo "=== Star 和更新时间 ==="
git log -1 --format="最后更新: %ai" 2>/dev/null
git remote -v 2>/dev/null | head -1

echo "=== 语言占比（通过代码行数）==="
find . -not -path '*/node_modules/*' -not -path '*/.git/*' \
  -not -path '*/vendor/*' -not -path '*/__pycache__/*' \
  -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/target/*' \
  -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.go" \
     -o -name "*.rs" -o -name "*.java" -o -name "*.rb" -o -name "*.php" \
     -o -name "*.c" -o -name "*.cpp" -o -name "*.h" -o -name "*.md" \) \
  | xargs wc -l 2>/dev/null | sort -rn | head -10

# === Step 2: 目录结构（防卡死） ===
echo "=== 核心目录 ==="
find . -maxdepth 3 -type d \
  -not -path '*/node_modules/*' \
  -not -path '*/.git/*' \
  -not -path '*/vendor/*' \
  -not -path '*/__pycache__/*' \
  -not -path '*/dist/*' \
  -not -path '*/build/*' \
  -not -path '*/coverage/*' \
  -not -path '*/target/*' \
  | sort | head -40

# === Step 3: 项目类型识别 ===
echo "=== 依赖管理文件 ==="
ls package.json pyproject.toml Cargo.toml go.mod requirements.txt Gemfile pom.xml build.gradle 2>/dev/null

echo "=== 构建系统 ==="
ls Makefile CMakeLists.txt Dockerfile docker-compose.yml 2>/dev/null

echo "=== 前端配置 ==="
ls tsconfig.json vite.config.js next.config.js vue.config.js 2>/dev/null

# === Step 4: Monorepo 检测 ===
echo "=== Monorepo 检测 ==="
if ls pnpm-workspace.yaml lerna.json rush.json nx.json 2>/dev/null | grep -q .; then
  echo "发现 Monorepo 配置"
  find . -maxdepth 3 -name "package.json" -exec dirname {} \; 2>/dev/null | sort
elif cat package.json 2>/dev/null | grep -q '"workspaces"'; then
  echo "发现 npm/yarn workspaces"
  cat package.json | python3 -c "import json,sys; d=json.load(sys.stdin); ws=d.get('workspaces',{}); print(ws)"
fi

# === Step 5: 技术栈指纹 ===
echo "=== 依赖分析（package.json 为例）==="
if [ -f package.json ]; then
  cat package.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
deps={**d.get('dependencies',{}), **d.get('devDependencies',{})}
# 框架
frameworks=['react','vue','angular','svelte','next','nuxt','remix','express','fastify','koa','nestjs','electron']
pkgs=list(deps.keys())
for fw in frameworks:
    matches=[p for p in pkgs if fw in p.lower()]
    if matches: print(f'框架: {matches}')
# 数据库
dbs=['prisma','mongoose','sequelize','typeorm','drizzle','pg','mysql','redis','mongodb']
for db in dbs:
    matches=[p for p in pkgs if db in p.lower()]
    if matches: print(f'数据库: {matches}')
# AI/ML
ai=['openai','anthropic','langchain','huggingface','transformers','ollama']
for a in ai:
    matches=[p for p in pkgs if a in p.lower()]
    if matches: print(f'AI: {matches}')
" 2>/dev/null
fi

echo "=== 框架检测（关键词）==="
grep -r -l --include="*.py" -e "^import (fastapi|flask|django|torch|transformers)" . 2>/dev/null | head -3
grep -r -l --include="*.go" -e "^package main" . 2>/dev/null | head -3
grep -r -l --include="*.rs" -e "^fn main" . 2>/dev/null | head -3

# === Step 6: 核心模块定位 ===
echo "=== 入口文件 ==="
ls index.js index.ts main.go main.rs main.py app.py server.js 2>/dev/null
find . -maxdepth 2 -name "main.*" -o -name "app.*" -o -name "server.*" 2>/dev/null | grep -v node_modules | head -10

echo "=== API 和核心逻辑目录 ==="
ls -d src/api src/routes src/controllers src/core src/services cmd/ cmd/pkg 2>/dev/null

# === Step 7: README 深度提取 ===
echo "=== README 关键信息 ==="
cat README.md 2>/dev/null | grep -iE "(install|setup|usage|quick.start|getting.started|requirement|dependency)" | head -15
echo "---徽章---"
cat README.md 2>/dev/null | grep -oE "!\[.*?\]\(https://img\.shields\.io/[^)]+\)" | head -10
echo "---安装命令---"
cat README.md 2>/dev/null | grep -oE "```\w*\n[^`]+```" | head -5

# === Step 8: 关键文件内容（按类型） ===
echo "=== 构建配置示例 ==="
if [ -f package.json ]; then echo "---scripts---"; cat package.json | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f'{k}: {v}') for k,v in d.get('scripts',{}).items()]"; fi
if [ -f Makefile ]; then echo "---Makefile targets---"; grep -E "^[a-z].*:" Makefile | head -10; fi

# === Step 9: 测试文件定位 ===
echo "=== 测试目录 ==="
find . -maxdepth 3 -type d \( -name "tests" -o -name "__tests__" -o -name "spec" -o -name "test" \) -not -path './node_modules/*' 2>/dev/null | head -5
```

## 输出规范

**快速概览**（GitHub API 直接可用时）：
```markdown
## [owner/repo] 概览

**描述**：...
**语言**：[占比]
**Stars**：xxx | **最近更新**：xxxx-xx-xx
**主题**：tag1, tag2
**架构**：单体 / Monorepo（N 个包）
**技术栈**：框架 + 数据库 + 关键依赖

## 值得注意
- [亮点1]
- [亮点2]
```

**深度分析**（clone 后完整报告）：
```markdown
# [项目名称] 深度分析报告

## 基本信息
- **类型**：单体 / Monorepo（N 个包）
- **语言**：[占比]
- **Stars**：xxx
- **技术栈**：框架 + 数据库 + 工具链
- **最近更新**：xxxx-xx-xx

## 架构解读

### 核心目录结构
[目录树 + 功能说明]

### 主要模块
[模块名：功能]

### 数据流 / 执行流程
[关键路径描述]

## 技术亮点
[3-5 个值得学习的设计/实现]

## 快速上手
```bash
[安装/运行命令]
```

## 注意事项
[踩坑点、版本要求等]
```

## 常见问题处理

| 场景 | 解决方案 |
|------|---------|
| 大仓库 clone 太慢 | 先用 API 路径拿信息，按需 clone |
| README 名字不统一 | 试试 README.md / README.rst / README |
| 目录太深太乱 | maxdepth 限制 3 层 |
| node_modules 卡死 | 所有 find 命令加 `-not -path '*/node_modules/*'` |
| 框架识别不准 | 看 package.json 的 dependencies 最准 |
| 没 clone 只有 URL | 走路径 A，用 GitHub API |

## 依赖工具
- `curl` / `web_fetch` — GitHub API
- `git` — 版本控制
- `find` / `grep` / `xargs` — 文件搜索
- `python3` — JSON 解析（jq 也可）
- `wc` — 代码行数统计
