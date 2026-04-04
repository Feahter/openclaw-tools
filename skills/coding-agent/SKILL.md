---
name: coding-agent
description: >
  Autonomous coding execution engine — use whenever someone asks to code, build, create, implement,
  refactor, debug, fix, optimize, or ship software. Handles everything from one-liners to full
  application scaffolds. Triggers on: "帮我写代码/写个/写一个/做一个小工具/实现/开发/写个脚本/
  代码有问题/调试/bug/修复/重构/优化性能/迁移代码/搭建项目/初始化项目/add feature/
  implement/build this/create a script/write function/fix this bug/refactor/optimize".
  Not for: reading docs, explaining concepts, or answering questions — only for actually producing code.
triggers:
  - "帮我写代码"
  - "写个"
  - "写一个"
  - "做一个小工具"
  - "实现"
  - "开发"
  - "写个脚本"
  - "代码有问题"
  - "调试"
  - "有bug"
  - "修复"
  - "重构"
  - "优化性能"
  - "迁移代码"
  - "搭建项目"
  - "初始化项目"
  - "add feature"
  - "implement"
  - "build this"
  - "create a script"
  - "write function"
  - "fix this bug"
  - "refactor"
  - "optimize"
  - "帮我写"
  - "帮我做"
  - "能不能写"
  - "能不能做个"
  - "能帮我写"
  - "能帮我做"
  - "帮我生成"
  - "生成代码"
  - "写个函数"
  - "写个类"
  - "写个组件"
  - "写个工具"
  - "自动化"
  - "写个脚本"
  - "跑不起来"
  - "报错"
  - "出错了"
  - "不对"
  - "有问题"
  - "不工作"
metadata: {"clawdbot":{"emoji":"🧩","requires":{"anyBins":["claude","opencode"]}}}
pipeline:
  root: pipeline/
  state: .state/
---

# Coding Agent — 执行管道

> 当前支持：**Claude Code**（✅ 已安装 2.1.88）、**OpenCode**（✅ 已安装 1.3.0）

---

## 什么时候用这个 Skill

**毫不犹豫地用，当你听到：**
- "帮我写个..." / "帮我做..." / "帮我生成..."
- "能不能写个..." / "能不能做个..."
- "这个功能帮我实现一下"
- "代码跑不起来" / "报错了" / "有bug"
- "帮我调试一下" / "帮我看看哪里有问题"
- "重构一下这段代码"
- "优化一下性能"
- "搭建一个项目" / "初始化一个项目"
- "写个脚本自动化..."
- "把这个从X迁移到Y"
- "帮我在XXX基础上开发..."
- 任何提到具体编程语言 + "写/做/实现/开发"

**不用这个 Skill，当：**
- 只是问"怎么写"而不需要实际产出代码 → 用普通对话
- 只是读文档/查资料 → 用 web_search / web_fetch
- 只是解释代码逻辑 → 用普通对话
- 只是问概念 → 用普通对话

**一句话：** 要代码产出就用 coding-agent，别在普通对话里让它"试着写写"。

---

## 架构

```
coding-agent/
├── pipeline/
│   ├── run-task.sh          # 启动任务（bash + Claude Code CLI）
│   ├── check-progress.sh    # 监控进度（调用 check-progress.py）
│   ├── check-progress.py    # Python 版状态解析（处理 JSON）
│   ├── collect-results.sh   # 收集结果（调用 collect-results.py）
│   ├── collect-results.py   # Python 版：git diff + JSON 报告
│   ├── verify.sh            # 验证产出
│   └── list-sessions.sh     # 列出所有会话
├── .state/
│   ├── progress/            # 每个会话的 JSON 状态
│   ├── results/             # 收集后的完整 JSON 报告
│   ├── logs/                # 原始 stdout/stderr 日志
│   ├── pids/                # 进程 PID
│   ├── context.md           # 管道状态
│   └── learnings.md         # 执行积累
└── SKILL.md
```

**依赖**：`claude`（Claude Code CLI 2.1.88 ✅）、`opencode`（1.3.0 ✅）

---

## 快速开始

### 1. 启动一个编程任务

```bash
SKILL_DIR=~/.openclaw/workspace/skills/coding-agent

# 方式 A：exec（推荐，自动处理后台）
exec bash $SKILL_DIR/pipeline/run-task.sh \
  "为 ~/project/myapp 添加用户认证模块" \
  "$HOME/project/myapp"

# 方式 B：使用 sessions_spawn（OpenClaw 原生子 session）
# 见下方「子 Session 模式」
```

### 2. 监控进度

```bash
bash $SKILL_DIR/pipeline/check-progress.sh <session_id> [tail_lines]
# 例如
bash $SKILL_DIR/pipeline/check-progress.sh 1745112345-12345 50
```

### 3. 收集结果

```bash
# 会话完成后
bash $SKILL_DIR/pipeline/collect-results.sh <session_id>
# 输出：JSON 报告，含 git diff + 完整日志
cat $SKILL_DIR/.state/results/<session_id>.json
```

### 4. 验证产出

```bash
bash $SKILL_DIR/pipeline/verify.sh <session_id>
# 自动检查：git diff / package.json / Cargo.toml / Makefile
```

### 5. 列出所有会话

```bash
bash $SKILL_DIR/pipeline/list-sessions.sh [running|completed|all]
```

---

## OpenClaw 原生模式（推荐）

用 `exec` 工具直接调用，不需要子 shell：

```bash
exec workdir:$PROJECT_DIR background:true \
  command:"claude -p '你的编程任务' --output-format stream-json --no-session-persistence"
```

**关键参数**：
- `-p` — 非交互打印模式
- `--output-format stream-json` — 流式 JSON 输出
- `--no-session-persistence` — 不保存会话到磁盘
- `--permission-mode bypassPermissions` — 跳过确认（仅在可信目录）

---

## 子 Session 模式（复杂任务）⭐

对于需要多轮迭代的复杂任务，用 `sessions_spawn` 启动专用子 session。**这是处理复杂编程任务的标准方式。**

### 为什么需要子 Session

普通 exec 调用的局限：
- 单次执行，无法多轮自我修正
- 无法中途读取代码决定下一步
- 任务失败无法重试

子 Session 的优势：
- 独立上下文，可多次执行 exec
- 可读取和分析代码
- 支持多轮自我修正
- 可访问完整工具集（不只是 exec）

### 标准调用方式

```bash
sessions_spawn(
  task="对 $PROJECT_DIR 进行以下改动：$TASK_DESCRIPTION",
  runtime="subagent",
  mode="session"
)
```

### 子 Session 任务模板

当需要子 session 时，使用以下模板描述任务：

```
## 目标
[具体要实现的功能或修复的问题]

## 项目上下文
- 项目路径：$PROJECT_DIR
- 技术栈：[如 Node.js + Express, Python + FastAPI 等]
- 现有文件：[相关文件列表]
- package.json / requirements.txt 存在：是/否

## 约束
- 不要删除现有功能（如果有）
- 如果涉及依赖，先检查 package.json / requirements.txt
- 完成后运行测试验证

## 验收标准
- [ ] [具体可检查的标准 1]
- [ ] [具体可检查的标准 2]
```

### 与主 Session 的协作模式

```
主 Session                          子 Session
    |                                  |
    |-- sessions_spawn -------------> |
    |    (task=完整任务描述)            |
    |                                  |--- 执行多次 exec
    |                                  |--- 读取代码
    |                                  |--- 写文件
    |                                  |--- 运行测试
    |                                  |
    |<-------- 子 Session 完成推送 -------|
    |    (包含 git diff + 验证结果)     |
    |                                  |
```

### 子 Session 生命周期管理

```bash
# 查看子 session 状态
bash $SKILL_DIR/pipeline/list-sessions.sh running

# 查看某个 session 的日志
cat $SKILL_DIR/.state/logs/<session_id>.log

# 强制终止卡住的 session
kill $(cat $SKILL_DIR/.state/pids/<session_id>.pid)
```

### 子 Session 典型场景

1. **大型功能开发**（超过 30 分钟工作量的任务）
   → 拆分成子 session，避免主 session 超时

2. **多文件重构**（涉及 5+ 文件）
   → 子 session 有完整上下文，跨文件修改更安全

3. **测试驱动开发**（TDD）
   → 子 session 内可运行多次测试-修改循环

4. **迁移项目**（如 React → Vue）
   → 子 session 可逐步验证每个模块

---

## Session 状态机

```
pending → running → completed
                      ↘ failed
```

### 状态说明

| 状态 | 含义 | 处理方式 |
|------|------|---------|
| pending | 任务已创建，还没启动 | 等待或检查 pid |
| running | 执行中 | 监控进度或等待完成 |
| completed | 正常完成 | 收集结果并验证 |
| failed | 执行失败 | 查看日志，分析原因，重试或手动修复 |

### 状态文件位置

```
.state/progress/<session_id>.json   # 实时状态
.state/results/<session_id>.json    # 完成后的完整报告
.state/logs/<session_id>.log        # 原始日志
.state/pids/<session_id>.pid        # 进程 PID
```

---

## 失败处理（Best Practices）

### 常见失败原因及对策

#### 1. 权限被拒绝（Permission denied）

```
症状：bypassPermissions 仍然被拒绝
原因：目录不在信任列表中
解决：
  - 确认 PROJECT_DIR 在 ~/project/ 或 /tmp/
  - 或手动 chmod +x 需要的脚本
  - 或在终端先手动 claude 确认一次
```

#### 2. 进程卡住（不输出也不结束）

```
症状：session 一直处于 running 状态
原因：
  - AI 在等待某个输入
  - 网络问题导致 API 无响应
  - 进入了需要确认的死循环

处理流程：
  1. 查看实时日志：
     tail -f $SKILL_DIR/.state/logs/<session_id>.log
  2. 检查进程：
     ps aux | grep claude
  3. 手动发信号终止：
     kill -9 $(cat $SKILL_DIR/.state/pids/<session_id>.pid)
  4. 将状态标记为 failed：
     echo '{"status":"failed","reason":"timeout_killed"}' \
       > $SKILL_DIR/.state/progress/<session_id>.json
  5. 分析日志找原因，重试
```

#### 3. 依赖安装失败

```
症状：npm install / pip install 报错
常见原因：
  - 网络问题（国内访问 npm/pypi 慢）
  - 版本冲突
  - 权限问题

解决：
  1. 先检查是否有网络问题：
     npm install --registry https://registry.npmmirror.com
  2. 检查 package.json 语法
  3. 删除 node_modules 重新安装
  4. 手动在项目目录运行一次，确认可以成功
```

#### 4. 测试失败（AI 写的代码跑不通测试）

```
这是正常情况，需要多轮修正：

1. 查看测试输出：
   cd $PROJECT_DIR && npm test

2. 定位失败原因：
   - 语法错误 → AI 漏看了
   - 逻辑错误 → AI 的实现思路不对
   - 测试本身写错了 → 测试需要修正

3. 启动子 session 修正：
   sessions_spawn(
     task="测试失败了，以下是测试输出：
     [粘贴测试输出]
     
     请：
     1. 分析失败原因
     2. 修正代码
     3. 重新运行测试
     4. 直到全部通过",
     runtime="subagent",
     mode="session"
   )
```

#### 5. Git 冲突或脏状态

```
症状：AI 提交失败 / diff 异常
解决：
  1. 检查 git 状态：
     cd $PROJECT_DIR && git status
  2. 处理冲突或 stash
  3. 重试任务
```

### 自动重试机制

对于非致命错误，建议自动重试：

```bash
MAX_RETRIES=3
RETRY_DELAY=10

for i in $(seq 1 $MAX_RETRIES); do
  echo "Attempt $i of $MAX_RETRIES"
  bash $SKILL_DIR/pipeline/run-task.sh "$TASK" "$PROJECT_DIR"
  
  # 检查结果
  STATUS=$(cat $SKILL_DIR/.state/progress/<session_id>.json | jq -r '.status')
  if [ "$STATUS" = "completed" ]; then
    echo "Success!"
    break
  elif [ "$STATUS" = "failed" ]; then
    REASON=$(cat $SKILL_DIR/.state/progress/<session_id>.json | jq -r '.reason // "unknown"')
    if [ "$REASON" = "timeout" ] || [ "$REASON" = "network" ]; then
      echo "Retrying after $RETRY_DELAY seconds..."
      sleep $RETRY_DELAY
      RETRY_DELAY=$((RETRY_DELAY * 2))
    else
      echo "Non-retryable failure: $REASON"
      break
    fi
  fi
done
```

---

## 超时处理（Best Practices）

### 超时场景分类

| 场景 | 默认超时 | 处理方式 |
|------|---------|---------|
| 简单单文件修改 | 60s | 不需要超时保护 |
| 中等任务（3-5 文件） | 180s | 设置 exec timeout |
| 大型任务（10+ 文件） | 无限制 | 用子 session |
| 依赖安装 | 300s | 单独处理 |

### 超时预防策略

1. **任务太大时先拆解**
   ```
   ❌ "帮我做一个完整的后台管理系统"
   ✅ "先帮我搭建项目结构和用户认证模块"
      → 完成后再继续 "接下来添加文章管理模块"
   ```

2. **用子 session 处理长时间任务**
   ```bash
   # 大任务不设置超时上限
   sessions_spawn(
     task="...",
     runtime="subagent",
     mode="session"
     # 不传 timeout，让它自己完成
   )
   ```

3. **分阶段验收**
   ```bash
   # 每个阶段完成后验证，再继续
   # 阶段1：项目初始化
   # 验证：package.json 存在，npm install 成功
   # 阶段2：基础功能
   # 验证：主要文件存在，测试通过
   # ...
   ```

### 超时后的处理

```bash
# 1. 立即保存现场
cp -r $PROJECT_DIR $PROJECT_DIR.backup-$(date +%s)

# 2. 查看最后日志
tail -100 $SKILL_DIR/.state/logs/<session_id>.log

# 3. 评估损失
# - 如果只有部分文件修改 → git diff 查看，手动继续
# - 如果大量修改 → 看 backup，继续修复
# - 如果修改损坏 → 恢复 backup，报告问题

# 4. 决定是否重试
# - 如果是简单超时 → 可以重试
# - 如果是逻辑问题 → 需要先修复任务描述
```

---

## 结果验证（Standard Procedure）

### 验证清单（必须逐项检查）

```bash
# 基础检查：文件是否被创建/修改
cd $PROJECT_DIR
git status

# 检查改动范围
git diff --stat

# 检查具体改动内容
git diff

# 语言/框架特定检查
```

### 按项目类型的验证重点

#### Node.js / npm 项目

```bash
# 1. 检查 package.json 是否更新
cat package.json | jq '.dependencies, .devDependencies'

# 2. 检查依赖是否安装
ls node_modules/.package-lock.json 2>/dev/null && echo "deps installed"

# 3. 运行测试
npm test

# 4. 检查语法（可选）
node --check src/index.js 2>&1 | head -20
```

#### Python 项目

```bash
# 1. 检查 requirements.txt / pyproject.toml
cat requirements.txt 2>/dev/null || cat pyproject.toml 2>/dev/null | head -30

# 2. 检查语法
python -m py_compile src/*.py

# 3. 运行测试
pytest tests/ -v 2>&1 | tail -30

# 4. 检查虚拟环境（如果有）
[ -f venv/bin/activate ] && echo "venv found"
```

#### Rust 项目

```bash
# 1. 检查 Cargo.toml
cat Cargo.toml

# 2. 运行 cargo check
cargo check 2>&1 | tail -20

# 3. 运行测试
cargo test 2>&1 | tail -30

# 4. 编译（release 模式）
cargo build --release 2>&1 | tail -10
```

#### Go 项目

```bash
# 1. 检查 go.mod
cat go.mod

# 2. 运行 go vet
go vet ./...

# 3. 运行测试
go test -v ./... 2>&1 | tail -30

# 4. 尝试构建
go build -o output ./...
```

### 自动验证脚本

```bash
# 使用 verify.sh（已在 pipeline 中）
bash $SKILL_DIR/pipeline/verify.sh <session_id>

# 验证后会输出类似：
# {
#   "session_id": "1745112345-12345",
#   "git_diff": { "files_changed": 5, "additions": 120, "deletions": 10 },
#   "tests_passed": true,
#   "syntax_ok": true,
#   "warnings": []
# }
```

### 验证通过标准

以下全部满足才算验证通过：

- [ ] `git diff` 显示有实际代码改动（不只是格式调整）
- [ ] 新增/修改的文件语法正确
- [ ] 依赖正确添加到 package.json / requirements.txt 等
- [ ] 运行 `npm test` / `pytest` 等测试（如果项目有测试）
- [ ] 测试通过（如果项目有测试）
- [ ] 没有引入明显的安全问题（如 hardcode 密码等）

### 验证失败的处理

```bash
# 1. 收集失败信息
cat $SKILL_DIR/.state/results/<session_id>.json | jq '.errors'

# 2. 分类问题
# - 语法错误 → 需要重新调用 AI 修复
# - 测试失败 → 需要修正逻辑
# - 依赖问题 → 手动安装或修正 package.json

# 3. 启动修正 session
sessions_spawn(
  task="验证失败了，以下是失败信息：
  [粘贴失败信息]
  
  请修复问题并重新验证。",
  runtime="subagent",
  mode="session"
)
```

---

## 执行参数参考

| 参数 | Claude Code | OpenCode |
|------|------------|---------|
| 非交互模式 | `-p "task"` | `opencode run "task"` |
| 输出格式 | `--output-format json` | 默认 JSON |
| 禁止持久化 | `--no-session-persistence` | — |
| 跳过确认 | `--permission-mode bypassPermissions` | — |
| 指定 model | `--model <id>` | `--provider <name>` |
| 追加 system prompt | `--append-system-prompt <text>` | — |
| 流式输出 | `--output-format stream-json` | — |

### 常用 Claude Code 命令示例

```bash
# 基础用法（简单任务）
claude -p "在当前目录创建一个 README.md" --no-session-persistence

# 指定 model
claude -p "优化这个函数的性能" --model sonnet-4 --no-session-persistence

# 添加 system prompt
claude -p "写一个 CLI 工具" \
  --append-system-prompt "这个工具需要在 Linux 和 macOS 上都能运行" \
  --no-session-persistence

# 流式 JSON 输出（用于解析 AI 的思考过程）
claude -p "重构 src/ 目录" \
  --output-format stream-json \
  --no-session-persistence

# 跳过所有确认（在可信目录）
claude -p "..." --permission-mode bypassPermissions --no-session-persistence
```

---

## 信任目录规则

| 目录 | 可用工具 |
|------|---------|
| `~/project/` | 全部工具 |
| `/tmp/` | 有限（文件操作）|
| `~/.openclaw/` | 仅读取 |
| 工作区根目录 | 不启动（会读取 SOUL/MEMORY）|

### 信任目录设置

如果需要在非信任目录工作：

```bash
# 方案 1：在 ~/project/ 下创建软链接
ln -s /path/to/your/project ~/project/yourproject

# 方案 2：手动确认（不推荐，每次都会暂停）
claude -p "..."  # 不带 --permission-mode

# 方案 3：在项目目录下先运行一次 claude（建立信任）
cd /path/to/project && claaude
# 看到提示后选择 "Always allow in this directory"
```

---

## 常见使用场景示例

### 场景 1：快速生成一个脚本

**用户说：** "帮我写一个 Python 脚本，监控文件夹变化，有新文件就打印文件名"

**处理：**
```bash
exec workdir:$HOME \
  command:"claude -p 'Write a Python script that monitors a directory for file changes and prints the filename when a new file is created. Use watchdog library. Save to monitor.py' --output-format stream-json --no-session-persistence --permission-mode bypassPermissions"
```

**不需要子 session，简单任务直接执行。**

---

### 场景 2：实现一个完整功能模块

**用户说：** "帮我做一个用户认证模块，用 JWT，包含注册、登录、token 刷新"

**处理：**
```bash
exec background:true \
  command:"claude -p '实现用户认证模块：注册、登录、JWT token 刷新。技术栈：Node.js + Express + MongoDB。包含完整验证、中间件、最小测试。' --output-format stream-json --no-session-persistence --permission-mode bypassPermissions"
```

**中等复杂度，可用 exec 背景执行，等待完成。**

---

### 场景 3：大型重构（需要子 session）

**用户说：** "把我们前端的 Redux 状态管理迁移到 Zustand，涉及 50+ 文件"

**处理：**
```bash
sessions_spawn(
  task="## 任务
把 ~/project/frontend/src 下的 Redux 状态管理迁移到 Zustand。

## 技术栈
- React 18
- 当前使用 @reduxjs/toolkit
- 迁移目标：zustand

## 具体要求
1. 分析现有 Redux store 结构
2. 逐步迁移每个模块（保持功能不变）
3. 更新所有 connect() / useSelector() / useDispatch() 调用
4. 移除旧的 Redux 相关代码
5. 运行测试确保功能正常

## 验收标准
- [ ] 所有组件使用 Zustand
- [ ] 测试全部通过
- [ ] 移除 @reduxjs/toolkit 依赖",
  runtime="subagent",
  mode="session"
)
```

---

### 场景 4：调试疑难问题

**用户说：** "这个 API 偶尔会返回 500，但日志里看不出原因"

**处理：**
```bash
sessions_spawn(
  task="## 任务
调试 ~/project/backend/api.py 中的一个偶发性 500 错误。

## 问题描述
- 错误不是每次都发生，大概 10% 概率
- 日志里只有 'Internal Server Error'，没有 stack trace
- 涉及用户并发时更容易出现

## 已尝试
- 检查了数据库连接池（应该够用）
- 查了最近代码改动（没有问题）
- 在本地无法复现

## 要求
1. 添加更详细的错误追踪
2. 找出根本原因
3. 修复并验证",
  runtime="subagent",
  mode="session"
)
```

---

### 场景 5：快速修复 Bug

**用户说：** "帮我修一下这个 bug：登录按钮点了没反应"

**处理：**
```bash
exec workdir:$HOME/project/frontend \
  command:"claude -p '修复登录按钮点击无反应的问题。项目在当前目录，使用 React。检查按钮 onClick 绑定、事件处理函数、是否有条件渲染导致按钮实际被禁用。' --output-format stream-json --no-session-persistence --permission-mode bypassPermissions"
```

**简单 bug 直接修复，不需要子 session。**

---

### 场景 6：初始化新项目

**用户说：** "帮我初始化一个 FastAPI 项目，包含用户认证、数据库连接、RESTful API 结构"

**处理：**
```bash
exec background:true \
  command:"claude -p 'Initialize a FastAPI project with:
1. SQLAlchemy + PostgreSQL connection
2. User authentication (JWT)
3. RESTful API structure with routers
4. Docker setup
5. Basic test structure with pytest

Use modern Python best practices. Save to current directory.' --output-format stream-json --no-session-persistence --permission-mode bypassPermissions"
```

---

### 场景 7：自动化脚本

**用户说：** "写个脚本帮我每天自动备份数据库到阿里云 OSS"

**处理：**
```bash
exec workdir:/tmp \
  command:"claude -p 'Write a bash script that:
1. Dumps a PostgreSQL database
2. Uploads the dump to Aliyun OSS using ossutil
3. Keeps only the last 7 days of backups
4. Sends a notification to Slack on failure
5. Has proper error handling and logging

Save as backup.sh and make it executable.' --output-format stream-json --no-session-persistence --permission-mode bypassPermissions"
```

---

## Learnings（积累）

每次编程任务后，将结果记录到 learnings：

→ 见 `.state/learnings.md`

---

## 故障排除速查

| 问题 | 快速检查 | 解决方案 |
|------|---------|---------|
| 进程无响应 | `tail -f .state/logs/<id>.log` | kill pid，检查网络 |
| 权限报错 | `ls -la` 检查目录权限 | 改用信任目录 |
| 依赖安装失败 | `npm install` 手动运行 | 检查网络/换源 |
| 测试失败 | `npm test 2>&1` | 分析错误，子 session 修正 |
| 文件没变化 | `git status` | AI 可能理解错了，重新描述任务 |
| 内存爆了 | `top` 看进程 | 减少并发/简化任务 |
| API 超限 | 检查 API key | 等一段时间再试 |
