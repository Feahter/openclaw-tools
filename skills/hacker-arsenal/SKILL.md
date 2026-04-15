---
name: hacker-arsenal
description: 基于PTES、OWASP Testing Guide、MITRE ATT&CK等权威框架构建的全面黑客攻防技术参考。涵盖渗透测试全生命周期(侦察→扫描→漏洞分析→利用→后渗透)、Web应用测试、CTF竞赛技巧。提供可直接使用的命令、工具和攻防技术速查，用于合法安全测试、红队演练、安全研究和CTF竞赛。
---

# Hacker Arsenal - 黑客攻防武器库

> ⚠️ **法律声明**: 本 Skill 仅供**合法授权**的安全测试、渗透测试、CTF竞赛、安全研究和教育目的使用。未经授权访问计算机系统属违法行为。使用前应确保获得书面授权。
> > **方法论基础**: PTES | OWASP Testing Guide | MITRE ATT&CK | NIST SP 800-115

## 何时使用此 Skill

- ✅ 获得授权的渗透测试
- ✅ CTF (Capture The Flag) 竞赛
- ✅ 安全研究与漏洞分析
- ✅ 红队演练 (Red Team)
- ✅ 漏洞赏金计划 (Bug Bounty)
- ✅ 网络安全培训与学习
- ✅ 应急响应与取证分析

## 渗透测试方法论

本 Skill 基于以下权威框架构建：

| 框架 | 描述 | 来源 |
|------|------|------|
| **PTES** | 渗透测试执行标准，7阶段标准化流程 | pentest-standard.org |
| **OWASP Testing Guide** | Web应用安全测试权威指南 | owasp.org |
| **MITRE ATT&CK** | 威胁行为知识库，红蓝队通用 | attack.mitre.org |
| **NIST SP 800-115** | 信息安全测试技术指南 | NIST |

### PTES 七阶段流程

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ 1. 预交互阶段    │────>│ 2. 情报收集      │────>│ 3. 威胁建模      │
│ Pre-Engagement  │     │ Intelligence    │     │ Threat Modeling │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
┌─────────────────┐     ┌─────────────────┐     ┌───────┘
│ 7. 报告阶段      │<────│ 6. 后渗透阶段    │<────│ 4. 漏洞分析      │
│ Reporting       │     │ Post Exploitation│     │ Vulnerability   │
└─────────────────┘     └─────────────────┘     │ Analysis        │
                                                └─────────────────┘
                                                        │
                                                ┌───────┘
                                                │ 5. 利用阶段
                                                │ Exploitation
                                                └──────────────
```

## 快速导航

根据当前阶段或场景选择参考文件：

| 阶段 | 参考文件 | 内容 |
|------|---------|------|
| Phase 1-2 | [01-reconnaissance.md](references/01-reconnaissance.md) | 被动/主动信息收集、DNS枚举、端口扫描 |
| Phase 3-4 | [02-vulnerability-analysis.md](references/02-vulnerability-analysis.md) | 漏洞扫描、SQLi/XSS/RCE检测 |
| Phase 5 | [03-exploitation.md](references/03-exploitation.md) | 权限提升、横向移动、隧道技术 |
| Phase 6 | [04-post-exploitation.md](references/04-post-exploitation.md) | 凭证收集、持久化、数据提取 |
| Web专项 | [05-web-pentest.md](references/05-web-pentest.md) | OWASP测试、API测试、业务逻辑 |
| CTF专项 | [06-ctf-cheatsheet.md](references/06-ctf-cheatsheet.md) | 隐写术、密码学、逆向、Pwn |
| 工具速查 | [07-tools-reference.md](references/07-tools-reference.md) | Nmap/SQLMap/Hydra/MSF等速查 |

## 攻击向量速查

### Web应用漏洞

| 漏洞 | 检测Payload | 工具 |
|------|------------|------|
| SQL注入 | `' OR '1'='1` | SQLMap, 手工 |
| XSS | `<script>alert(1)</script>` | XSStrike, Burp |
| 命令注入 | `; id` | Commix, 手工 |
| 路径遍历 | `../../../etc/passwd` | 手工 |
| 文件上传 | `shell.php%00.jpg` | Burp |
| 反序列化 | `O:4:"Test":0:{}` | ysoserial |

### 网络服务漏洞

| 服务 | 常见漏洞 | 检测 |
|------|---------|------|
| SMB | 未授权、MS17-010 | enum4linux, nmap |
| SSH | 弱密码 | hydra, nmap |
| FTP | 匿名访问 | nmap |
| RDP | BlueKeep | nmap |
| Redis | 未授权访问 | redis-cli |
| MySQL | 弱密码、SQLi | nmap, sqlmap |

## 工具分类

### 信息收集
```
Nmap         - 端口扫描之王
Masscan      - 高速异步扫描
Gobuster     - 目录/子域名爆破
Subfinder    - 子域名枚举
WhatWeb      - Web技术识别
Shodan       - 互联网设备搜索引擎
```

### 漏洞扫描
```
Burp Suite   - Web渗透测试套件
SQLMap       - SQL注入自动化
Nuclei       - 快速漏洞扫描
Nikto        - Web漏洞扫描
OpenVAS      - 开源漏洞扫描器
```

### 利用框架
```
Metasploit   - 渗透测试框架
Cobalt Strike - 红队工具 (商业)
Sliver       - 开源C2框架
Impacket     - Python网络协议套件
```

### 密码攻击
```
Hydra        - 在线暴力破解
John         - 离线哈希破解
Hashcat      - GPU加速破解
Mimikatz     - Windows凭证提取
```

## CTF专项

### 题型与工具

| 题型 | 核心技能 | 推荐工具 |
|------|---------|---------|
| Crypto | 编码识别、密码学 | CyberChef, RsaCtfTool |
| Web | Web漏洞利用 | Burp, SQLMap |
| Pwn | 二进制利用 | Pwntools, GDB |
| Reverse | 逆向分析 | IDA, Ghidra |
| Forensics | 流量/文件分析 | Wireshark, Binwalk |
| Misc | 杂项 | Python, CyberChef |

### 在线资源

- [CTFtime](https://ctftime.org/) - CTF日历与排名
- [CyberChef](https://gchq.github.io/CyberChef/) - 万能编码解码
- [CrackStation](https://crackstation.net/) - 在线哈希破解
- [GTFOBins](https://gtfobins.github.io/) - Unix提权速查
- [LOLBAS](https://lolbas-project.github.io/) - Windows利用速查

## 防御视角

### 日志监控重点

- 异常登录 (时间、来源IP、频率)
- 特权命令执行
- 文件完整性变化
- 异常网络连接
- 进程创建异常

### 加固措施

**认证**
- 强密码策略 + MFA
- 账户锁定机制
- 会话管理安全

**网络**
- 最小端口暴露原则
- 网络分段隔离
- 防火墙规则审计

**应用**
- 输入验证与过滤
- 参数化查询
- 最小权限原则

## 学习资源

### 在线练习平台

| 平台 | 特点 |
|------|------|
| Hack The Box | 实战靶机 |
| TryHackMe | 结构化学习路径 |
| VulnHub | 离线靶机 |
| PentesterLab | Web专项 |

### 靶机推荐

- **DVWA** - Web漏洞学习
- **Metasploitable** - 综合漏洞
- **WebGoat** - OWASP项目
- **Juice Shop** - 现代Web应用

### 认证推荐

- **OSCP** - Offensive Security Certified Professional
- **CEH** - Certified Ethical Hacker
- **GPEN** - GIAC Penetration Tester

## 注意事项

1. **合法授权**: 始终确保获得书面授权
2. **范围控制**: 严格遵守测试范围边界
3. **数据保护**: 妥善保管敏感信息
4. **最小影响**: 避免对生产系统造成影响
5. **及时报告**: 发现高危漏洞立即报告

## 参考文件使用指南

根据当前任务选择相应的参考文件：

- 需要**扫描目标** → [01-reconnaissance.md](references/01-reconnaissance.md)
- 需要**检测漏洞** → [02-vulnerability-analysis.md](references/02-vulnerability-analysis.md)
- 需要**利用漏洞** → [03-exploitation.md](references/03-exploitation.md)
- 需要**维持访问** → [04-post-exploitation.md](references/04-post-exploitation.md)
- 针对**Web应用** → [05-web-pentest.md](references/05-web-pentest.md)
- 参加**CTF比赛** → [06-ctf-cheatsheet.md](references/06-ctf-cheatsheet.md)
- 查询**工具用法** → [07-tools-reference.md](references/07-tools-reference.md)

---

> **最后更新**: 基于 PTES v1.0, OWASP Testing Guide v4.2, MITRE ATT&CK v14
> 
> **推荐专家著作**:
> - Georgia Weidman - "Penetration Testing: A Hands-On Introduction to Hacking"
> - Peter Kim - "The Hacker Playbook" 系列
> - Offensive Security - OSCP/PEN-200
