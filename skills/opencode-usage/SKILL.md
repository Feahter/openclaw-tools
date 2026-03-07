# opencode-usage

使用 opencode CLI 进行代码维护和任务执行。

## 快速开始

### 1. 安装 opencode

```bash
brew install opencode
```

### 2. 基本使用

```bash
# 进入项目目录
cd /path/to/project

# 运行任务（默认 Sisyphus 模式）
opencode "修复 index.ts 的 bug"

# 指定 Agent 模式
opencode --agent Prometheus "规划新功能"
opencode --agent Hephaestus "修改某方法"
opencode --agent Atlas "继续执行之前计划"
```

## Agent 模式

| Agent | 用途 | 特点 |
|-------|------|------|
| **Sisyphus** | 默认，日常通用 | 多 Agent 协作，端到端完成 |
| **Hephaestus** | 明确目标修改 | 快速省钱，少编排 |
| **Prometheus** | 规划模式 | 只读生成计划，等待确认 |
| **Atlas** | 恢复执行 | 继续中断的计划 |

## oh-my-opencode 封装

推荐使用 `oh-my-opencode` 封装工具（v3.10.0+）：

```bash
# 安装
npm install -g oh-my-opencode@latest

# 基本使用
oh-my-opencode run "任务描述"
oh-my-opencode run --agent Prometheus --directory /path/to/project "规划任务"

# 其他命令
oh-my-opencode version          # 查看版本
oh-my-opencode doctor            # 诊断问题
oh-my-opencode install           # 交互式安装配置
```

## 常见问题

### sysctl 找不到

如果遇到 `sysctl` 错误：
```bash
sudo ln -sf /usr/sbin/sysctl /usr/local/bin/sysctl
```

### Agent 优先级

1. `--agent` 参数
2. `OPENCODE_DEFAULT_AGENT` 环境变量
3. `oh-my-opencode.json` 配置
4. Sisyphus（默认）

### 工作目录

使用 `--directory` 或 `-d` 指定：
```bash
oh-my-opencode run --directory /path/to/project "任务"
```

## 使用场景

| 场景 | 推荐 Agent |
|------|------------|
| 日常代码修改、调试 | Sisyphus |
| 明确目标的微调 | Hephaestus |
| 复杂功能规划、多文件重构 | Prometheus |
| 继续之前的计划 | Atlas |
