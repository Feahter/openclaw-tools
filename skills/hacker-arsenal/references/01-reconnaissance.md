# Phase 1-2: 侦察与扫描

> **PTES 对应阶段**: 情报收集 (Intelligence Gathering)
> 
> **MITRE ATT&CK**: Reconnaissance [TA0043], Resource Development [TA0042]

## 被动信息收集 (Passive Reconnaissance)

### 域名与IP情报

**WHOIS查询**
```bash
whois example.com
# 在线: whois.domaintools.com
```

**DNS枚举**
```bash
# 基础查询
dig example.com ANY
dig example.com NS +short
dig example.com MX +short

# 区域传输测试 (AXFR)
dig @ns1.example.com example.com AXFR
dnsrecon -d example.com -t axfr

# 子域名枚举
subfinder -d example.com -o subdomains.txt
amass enum -d example.com -o amass.txt
assetfinder --subs-only example.com
chaos -d example.com

# 组合使用
cat domains.txt | subfinder | anew all-subs.txt
```

**证书透明度日志**
```bash
curl -s "https://crt.sh/?q=%.example.com&output=json" | jq .
# 或使用: https://sslmate.com/certspotter/
```

### 在线情报平台

| 平台 | 用途 | 查询示例 |
|------|------|---------|
| **Shodan** | 互联网设备搜索 | `shodan host <ip>` |
| **Censys** | 主机与证书搜索 | `censys search "services.port: 443"` |
| **FOFA** | 资产搜索引擎 | `fofa "app=Apache-Shiro"` |
| **VirusTotal** | 域名/IP信誉 | `virustotal.com/gui/domain/example.com` |
| **SecurityTrails** | 历史DNS/Whois | 查看历史IP解析 |
| **BinaryEdge** | 互联网扫描数据 | 端口与服务信息 |

### 代码仓库与泄露

**GitHub敏感信息**
```bash
# 搜索语法
org:target-org password
org:target-org api_key
org:target-org token
filename:.env DB_PASSWORD
extension:sql INSERT INTO

# 工具
git-dumper https://example.com/.git/ ./dump
gitleaks detect -v -s ./dump
trufflehog filesystem ./dump
```

**Google Dorking**
```
site:example.com filetype:pdf
site:example.com inurl:admin
site:example.com intitle:"index of"
site:example.com ext:log
site:github.com "example.com" "password"
```

## 主动信息收集 (Active Reconnaissance)

### 主机发现

```bash
# Ping扫描
nmap -sn 192.168.1.0/24
fping -a -g 192.168.1.0/24 2>/dev/null

# ARP扫描 (本地网络)
arp-scan -l
netdiscover -r 192.168.1.0/24
```

### 端口扫描

**Nmap 扫描策略**
```bash
# 快速扫描 Top 1000
nmap -F target.com

# 全端口扫描
nmap -p- --min-rate 1000 target.com

# 综合扫描 (服务版本 + 默认脚本 + OS检测)
nmap -sV -sC -O target.com

# 深度扫描
nmap -sS -sV -sC -O -p- --script=vuln -oN full_scan.txt target.com

# UDP扫描
nmap -sU --top-ports 100 target.com
```

**高速扫描工具**
```bash
# Masscan (异步扫描)
masscan -p1-65535 192.168.1.0/24 --rate=10000

# Rustscan (先Rustscan后Nmap)
rustscan -a target.com -- -sV -sC
```

### 服务枚举

**SMB枚举**
```bash
enum4linux -a target.com
smbmap -H target.com
smbclient -L //target.com -N
nmap -p445 --script=smb-enum-shares,smb-enum-users target.com
nmap -p445 --script=smb-vuln* target.com
```

**SNMP枚举**
```bash
snmpwalk -c public -v1 target.com
onesixtyone -c community.txt -i hosts.txt
snmp-check target.com
```

**LDAP枚举**
```bash
ldapsearch -x -h target.com -s base namingcontexts
nmap -p389 --script=ldap-search target.com
```

### Web技术识别

```bash
# 技术栈识别
whatweb target.com
wappalyzer target.com

# 目录与文件爆破
gobuster dir -u http://target.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html,js,bak
ffuf -u http://target.com/FUZZ -w wordlist.txt -mc 200,301,302
feroxbuster -u http://target.com -w wordlist.txt

# 虚拟主机发现
gobuster vhost -u http://target.com -w subdomains.txt
```

## 威胁建模基础

### 识别攻击面

| 攻击面 | 收集内容 | 工具 |
|--------|---------|------|
| 外部网络 | IP、开放端口、服务 | Nmap, Shodan |
| Web应用 | 技术栈、端点、参数 | Gobuster, WhatWeb |
| 人员 | 员工邮箱、社交媒体 | theHarvester, Sherlock |
| 供应链 | 第三方服务、CDN | 在线工具 |

### 信息整理模板

```
target-recon/
├── 00-scope.txt          # 授权范围
├── 01-domains.txt        # 主域名
├── 02-subdomains.txt     # 子域名列表
├── 03-ips.txt           # IP地址
├── 04-ports/            # 端口扫描结果
│   ├── tcp-all.txt
│   └── udp-top100.txt
├── 05-services/         # 服务详情
├── 06-web/              # Web应用截图与目录
└── 07-notes.md          # 观察笔记
```

## 注意事项

1. **合法授权**: 确保所有主动扫描已获得书面授权
2. **范围控制**: 严格遵守测试范围，不越界扫描
3. **日志记录**: 记录所有操作以备审计
4. **数据保护**: 妥善保管收集的敏感信息

## 参考资源

- [PTES Technical Guidelines](http://www.pentest-standard.org/index.php/Main_Page)
- [OWASP Testing Guide v4.2](https://owasp.org/www-project-web-security-testing-guide/)
- [MITRE ATT&CK - Reconnaissance](https://attack.mitre.org/tactics/TA0043/)
