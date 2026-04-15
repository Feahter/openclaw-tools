---
name: secret-knowledge
description: |
  系统管理员、DevOps、安全研究员的知识宝库。当用户询问以下主题时触发：
  - Linux/Unix 系统管理工具和命令
  - 网络安全工具（扫描、审计、渗透测试）
  - DevOps 和运维工具
  - 性能监控和诊断工具
  - CLI 工具推荐和替代方案
  - SSL/TLS、DNS、HTTP 相关工具
  - 数据库 CLI 工具
  - 日志分析和监控工具
  
  提供精选的工具推荐、使用场景说明和官方链接。
---

# Secret Knowledge - 系统与安全工具宝库

基于 [The Book of Secret Knowledge](https://github.com/trimstray/the-book-of-secret-knowledge) 的精选知识库。

## 使用方式

当用户询问特定领域的工具时，从对应分类中提取相关工具推荐。

## 工具分类

### 1. 网络工具 (Network)

#### DNS 工具
- **dnsdiag** - DNS 诊断和性能测量工具
- **subfinder** - 子域名发现工具
- **amass** - 通过多个数据源获取子域名
- **massdns** - 高性能 DNS stub resolver
- **dnstwist** - 检测域名仿冒和网络钓鱼

#### HTTP 工具
- **curl** - 数据传输命令行工具
- **HTTPie** - 用户友好的 HTTP 客户端
- **wrk/wrk2** - HTTP 基准测试工具
- **vegeta** - HTTP 负载测试工具
- **gobuster** - 目录/文件和 DNS 爆破工具
- **Hurl** - 使用纯文本运行和测试 HTTP 请求

#### SSL/TLS 工具
- **openssl** - TLS/SSL 协议工具包
- **sslyze** - SSL/TLS 服务器扫描库
- **testssl.sh** - 测试 TLS/SSL 加密
- **mkcert** - 生成本地信任的开发证书
- **Certbot** - Let's Encrypt 证书获取工具

### 2. 安全工具 (Security)

#### 审计工具
- **Lynis** - Linux/macOS/Unix 安全审计工具
- **auditd** - 系统审计守护进程
- **LinEnum** - Linux 本地枚举和权限提升检查
- **PEASS** - 权限提升工具套件

#### 系统监控
- **SELinux** - 强制访问控制系统
- **AppArmor** - 应用安全系统
- **grapheneX** - 自动化系统加固框架

### 3. 系统诊断 (System Diagnostics)

#### 性能监控
- **htop** - 交互式进程查看器
- **glances** - 跨平台系统监控工具
- **sysdig** - 系统探索和故障排查工具
- **bpftrace** - Linux eBPF 高级跟踪语言

#### 调试工具
- **strace** - 系统调用跟踪器
- **ltrace** - 库调用跟踪器
- **Valgrind** - 动态分析工具框架
- **FlameGraph** - 堆栈跟踪可视化工具

#### 日志分析
- **lnav** - 日志文件导航器
- **GoAccess** - 实时 Web 日志分析器
- **angle-grinder** - 命令行日志分析工具

### 4. 数据库工具 (Databases)

- **usql** - 通用 SQL 数据库命令行接口
- **pgcli** - PostgreSQL CLI（支持自动补全）
- **mycli** - MySQL CLI（支持自动补全）
- **litecli** - SQLite CLI（支持自动补全）
- **iredis** - Redis 终端客户端
- **OSQuery** - SQL 驱动的操作系统监控框架

### 5. 生产力工具 (Productivity)

- **tldr** - 简化的社区驱动 man pages
- **gron** - 让 JSON 可 grep
- **tig** - Git 文本模式界面
- **taskwarrior** - 任务管理系统

### 6. 容器和编排 (Containers)

- **dive** - 探索 Docker 镜像每一层的内容

## 响应格式

当用户询问工具推荐时，按以下格式回复：

```
## [分类] 推荐工具

### 主要推荐
1. **工具名** - 一句话描述
   - 适用场景：xxx
   - 链接：[官网/GitHub]

2. **工具名** - ...

### 备选方案
- 工具A - 简要说明
- 工具B - 简要说明

### 使用示例
```bash
# 常用命令示例
```
```

## 触发关键词

| 主题 | 关键词 |
|------|--------|
| DNS | dns, 子域名, subdomain, dns扫描 |
| HTTP | http, curl, 请求, api测试, 压测 |
| SSL | ssl, tls, 证书, https, cert |
| 安全审计 | 审计, audit, 安全扫描, 加固 |
| 性能监控 | 监控, top, 性能, cpu, 内存 |
| 日志 | 日志, log, 分析, nginx日志 |
| 数据库 | sql, mysql, postgres, redis, cli |
| 调试 | 调试, debug, 跟踪, trace |

## 参考资料

- 完整知识库：https://github.com/trimstray/the-book-of-secret-knowledge
- 更新频率：定期同步上游更新
