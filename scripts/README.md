# Scripts Collection

> 从 GitHub 收集的实用脚本 | 更新时间：2026-03-19

---

## 脚本列表

| 脚本 | 来源 | Stars | 作用 |
|------|------|-------|------|
| `httpie-wrapper.py` | [httpie/httpie](https://github.com/httpie/httpie) | ⭐ 32K | 人类友好的 HTTP 客户端，curl 替代品 |
| `bash-functions` | [mathiasbynens/dotfiles](https://github.com/mathiasbynens/dotfiles) | - | Bash 函数库（包含 extract, mem, etc） |
| `tldr-curl.md` | [tldr-pages/tldr](https://github.com/tldr-pages/tldr) | ⭐ 48K | curl 命令简化示例 |

---

## 脚本详情

### httpie-wrapper.py
**Stars**: ⭐ 32,000+ | **语言**: Python

**作用**：人类友好的 HTTP 客户端，比 curl 更易用

**用法**：
```bash
# GET 请求
python httpie-wrapper.py GET https://api.github.com/users/octocat

# POST 请求
python httpie-wrapper.py POST https://httpbin.org/post name=John email=john@example.com

# JSON 格式输出
python httpie-wrapper.py --json https://api.example.com/data
```

**安装**：
```bash
pip install httpie
# 或直接运行
python httpie-wrapper.py
```

---

### bash-functions
**来源**: [mathiasbynens/dotfiles](https://github.com/mathiasbynens/dotfiles)

**作用**：常用的 Bash 函数集合

**包含函数**：
```bash
# 解压任意压缩包
extract <file>

# 显示文件/目录大小
ds <path>

# 创建目录并进入
mkcd <dir>

# Git 相关
gcd <branch>    # 切换分支
gcb             # 创建新分支

# 系统
mem             # 显示内存使用
psmem           # 按内存排序进程
```

**用法**：
```bash
# source 到当前 shell
source bash-functions

# 解压 tar.gz
extract file.tar.gz

# 创建目录并进入
mkcd new-project
```

---

### tldr-curl.md
**来源**: [tldr-pages/tldr](https://github.com/tldr-pages/tldr) | ⭐ 48K Stars

**作用**：curl 命令的简化和示例

**用法**：
```bash
# 下载文件
curl -L -o filename https://example.com/file

# 发送 POST 请求
curl -X POST -d "data=value" https://example.com/api

# 带认证的请求
curl -H "Authorization: Bearer TOKEN" https://api.example.com

# 下载并跟随重定向
curl -L https://example.com/redirect
```

---

## 采集标准

| 标准 | 要求 |
|------|------|
| Stars | > 100（工具类）/ 自定义脚本不限 |
| 近期更新 | 6 个月内 |
| 文档完整 | 有 README |
| License | 开源许可 |
| 实用性 | 能解决实际问题 |

---

## 下次采集目标

- [ ] `fzf` 相关脚本
- [ ] `zsh-autosuggestions`
- [ ] git-prompt 增强
- [ ] tmux 配置脚本
- [ ] 定时备份脚本

---

## 贡献指南

1. 脚本保存到 `scripts/` 目录
2. 命名规范：`[用途]-[作者].sh` 或 `[用途]-[作者].py`
3. 必须包含 shebang 或 python header
4. 更新此 README（名称 + 来源 + Stars + 作用）

---

## 心跳任务

此目录由心跳任务每小时检查更新。

**配置**：见 `HEARTBEAT.md` 中的 "GitHub 脚本收集" 规则。

---

---

### pure-zsh (sindresorhus/pure)
**Stars**: ⭐ 21K+ | **语言**: Zsh

**作用**：最流行的异步 Zsh 提示符，Fast, async, prompt

**文件**：
- `pure.zsh` — 主提示符脚本
- `async.zsh` — 异步工具库

**用法**：
```bash
# 添加到 .zshrc
fpath+=(~/path/to/pure-zsh)
autoload -U promptinit; promptinit
prompt pure

# 或使用 plugin manager
# zinit: wait'0' light-mode forasync
# zsh-users/zsh-autosuggestions
```

**特点**：
- 异步执行，不卡终端
- 显示 git 分支/状态/提交数
- 显示当前命令执行时间（>5s）
- 简洁优雅的视觉设计

---

*心跳任务每小时检查 GitHub，收集优质脚本*
*贵精不贵多，每次最多 3 个*
