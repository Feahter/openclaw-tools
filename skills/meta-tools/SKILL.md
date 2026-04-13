---
name: meta-tools
description: Agent 元工具（Meta-tools）设计指南——用"道法术器"框架梳理 CLI 元工具，帮助 Agent 构建世界模型（World Model）的最小可执行单元。用于设计 Agent 与数字环境交互的原子操作、评估工具是否为元工具、构建 Agent 元工具栈。触发：元工具、meta-tools、CLI 工具选择、Agent 工具栈设计、工具评估。
---

# Meta Tools - Agent 元工具设计指南

## 5秒决策口诀

```
感知用 rg，动作靠 bash，
状态问 git，隔离选 docker，
复杂管道 → 写成脚本
```

## 概述

元工具（Meta-tools）是构成 Agent 世界模型（World Model）的最小可执行单元，是 Agent 与数字环境交互的"原子操作"。

元工具必须满足四个元属性：
- **原子性**（不可再分）
- **通用性**（跨领域）
- **可组合性**（管道化）
- **可观测性**（退出码+stdout/stderr反馈闭环）

## 快速决策：任务→工具矩阵

| 任务类型 | 首选工具 | 备选方案 | 避免使用 |
|---------|---------|---------|---------|
| 代码搜索 | `rg` (ripgrep) | `git grep` | `find + grep` |
| 文件查找 | `fd` | `find` (复杂条件) | 递归 `ls` |
| JSON 处理 (<1MB) | `jq` | `python -m json.tool` | 手写解析 |
| JSON 处理 (>10MB) | `jq --stream` | `python` 脚本 | 普通 `jq` (内存爆炸) |
| YAML 处理 | `yq` | `python -c` | 正则匹配 |
| 进程查找 | `pgrep` | `ps + grep` | 裸 `ps` 人工筛选 |
| 磁盘清理 | `ncdu` | `du -sh */` | `du` 全盘扫描 |
| 网络调试 | `curl` | `httpie` | 浏览器手动测试 |
| 临时脚本 | `python -c` | `node -e` | 新建文件再执行 |
| 管道调试 | 拆成脚本 | `tee` 中间文件 | 5层+嵌套管道 |

**选择原则**：简单任务用简单工具，复杂任务写成脚本，不要为了用工具而用工具。

---

## 道法术器框架

### 道：环境抽象的底层接口

数字世界的触觉与视觉，构建工作记忆（Working Memory）的物理载体。

| 元能力 | 代表 CLI | Agentic 价值 |
|--------|----------|--------------|
| 文件系统映射 | `ls`, `cat`, `find`, `stat` | Agent 感知"自我存在"的基础 |
| 流式处理 | `grep`, `sed`, `awk`, `jq` | 信息熵的筛选与重组引擎，实现"注意力机制"的硬件层 |
| 进程执行 | `bash`, `exec`, `timeout` | 因果律的触发器，Agent 的"运动皮层" |
| 网络穿透 | `curl`, `nc` (netcat) | 打破封闭系统，引入外部熵减 |

### 法：状态管理与协作原语

| 元工具 | 核心 CLI | 元属性解析 |
|--------|----------|------------|
| 版本控制 | `git` | 时间旅行元器：Branch 是平行宇宙，Commit 是快照，Diff 是因果推断的输入。Agent 通过 git 获得"可逆性"，这是试错学习的前提 |
| 包管理 | `pip`, `npm`, `apt` | 能力扩展元器：Agent 自我进化的入口。安装新包 = 获得新感官/器官，是真正的 Meta-learning 硬件基础 |
| 容器化 | `docker`, `podman` | 环境隔离元器：保证动作的可复现性与无副作用（Pure Function），是 Agent 安全执行不可信代码的沙箱边界 |

### 术：自省与调试原语

Agent 的自我感知（Self-awareness）工具：

```bash
# 系统自省（生理指标监测）
ps, top, htop      # 进程意识：查看自己的"思维碎片"
df, du             # 资源意识：工作记忆的容量边界
env, printenv      # 上下文意识：当前所处的时间/空间坐标

# 网络拓扑感知
ip, netstat, ss    # 连接图谱：了解自己在网络中的节点位置
hostname, whoami   # 身份认同：确定执行主体的权限边界
```

**为何是元**：这些工具提供反馈闭环（Feedback Loop）的必需输入。没有 `ps`，Agent 无法确认自己的子进程是否存活；没有 `df`，Agent 可能因磁盘耗尽而"脑死亡"（无法写入记忆）。

### 器：特定领域的元工具实例

基于 Claude Code / OpenClaw 生态，这些 CLI 构成了 Skills 的底层能力基座：

| 类别 | 元工具链 | 在 Agent 中的角色 |
|------|----------|-------------------|
| 代码理解 | `tree`, `rg` (ripgrep), `fd` | 代码库的空间导航，替代盲目的 `find` |
| 语义解析 | `jq`, `yq`, `xq` | 结构化数据的"格式塔"转换器 |
| 动态执行 | `python -c`, `node -e` | 临时逻辑的快速验证，"思维实验"的执行器 |
| 安全沙箱 | `firejail`, `bwrap` | 比 Docker 更轻量的原子级隔离 |

## 常见误用（反模式）

### ❌ 过度管道化
```bash
# 错误：调试困难，失败点不明
cat file | grep pattern | sed 's/old/new/' | awk '{print $1}' | sort | uniq -c

# 正确：拆成脚本，添加检查点
./process.sh  # 内部有日志和错误处理
```

### ❌ 工具选择不当
```bash
# 错误：jq 处理超大 JSON 会内存爆炸
jq '.' 10gb-file.json

# 正确：流式处理
jq --stream 'select(.[0][0]=="target")' 10gb-file.json
```

### ❌ 忽视退出码
```bash
# 错误：管道失败被忽略
cat file | grep pattern | process

# 正确：检查每一步
set -euo pipefail
```

### ❌ 元工具迷信
> "元工具"不是绝对的好。`ffmpeg` 对视频 Agent 就是元工具，对普通 Agent 是领域工具。
> **核心标准：是否适合当前任务**，而非是否符合定义。

## 灰色地带

以下工具边界模糊，需根据上下文判断：

| 工具 | 元工具属性 | 争议点 |
|------|-----------|--------|
| `docker` | Effectors✓ | Composition✗（输出难管道化） |
| `make` | 可组合✓ | 领域特定（构建系统） |
| `ssh` | 网络穿透✓ | 状态ful，难观测 |

**判断建议**：如果工具改变的是"外部环境"而非"数据流"，它可能是"法"层而非"术"层。

## 关键判别标准：元工具 vs 普通工具

一个 CLI 要成为 Agent 元工具，必须通过以下三层测试：

1. **Oracles 测试**：能否回答"世界现在是什么状态"？（如 `ls` 回答文件存在性）
2. **Effectors 测试**：能否改变"世界状态"？（如 `rm` 删除记忆）
3. **Composition 测试**：能否通过管道 `|` 组合出新能力？（如 `cat file | grep pattern | wc -l` 形成复杂感知）

**反例**：`ffmpeg` 虽然是强大工具，但属于领域专用工具（音视频处理），不是元工具——它无法被 Agent 用来管理自身状态或感知通用环境。

**正例**：`curl` 是元工具，因为它既是感知器（获取 API 数据）又是效应器（POST 提交），且输出可被 `jq` 继续处理，形成感知链。

## 工程化建议：构建你的 Agent 元工具栈

按以下优先级封装 Skills：

- **Layer 0（感知层）**：`rg` + `fd` + `jq`（快速环境扫描）
- **Layer 1（动作层）**：`bash` + `git` + `docker`（安全执行与回滚）
- **Layer 2（扩展层）**：`pip` + `npm`（动态能力获取）
- **Layer 3（元认知层）**：自定义 `doctor` 脚本（封装 `df`/`ps` 等健康检查，实现自诊断）

**核心原则**：元工具的组合应当遵循 Pipe-and-Filter 架构，让每个 CLI 的输出成为下一个的输入，形成认知流水线（Cognitive Pipeline），这是 Agent 实现复杂推理的物理基础。

## 快速参考

### 元工具三层测试清单

```
□ Oracles: 能否感知世界状态？
□ Effectors: 能否改变世界状态？
□ Composition: 能否管道组合？

全通过 = 元工具
任一失败 = 领域工具
```

### 常用元工具速查

| 场景 | 推荐工具 |
|------|----------|
| 快速搜索代码 | `rg` (ripgrep) |
| 快速查找文件 | `fd` |
| JSON 处理 | `jq` |
| YAML 处理 | `yq` |
| 文件树查看 | `tree` |
| 进程监控 | `htop` / `btm` |
| 磁盘使用 | `du -sh` / `ncdu` |
| 网络调试 | `curl` / `httpie` |
