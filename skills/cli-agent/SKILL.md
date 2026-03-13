---
name: cli-agent
description: Unix哲学AI执行器 - 用Shell命令流而非Function Calling完成任务。LLM对cat|grep|wc的理解远超自定义API。触发：命令行、Shell、管道、CLI、终端、脚本、bash、awk、sed、grep、find、运维、监控、日志分析
---

# CLI Agent - Unix哲学AI执行器

> "一个 run(command='...') 比15个function calling工具效果好得多。"
> — Manus 前后端负责人（Meta收购后离职）

## 核心理念

### Unix收敛定律

```
50年前：Unix设计 → 一切皆文本流
50年后：LLM设计 → 一切皆token
         殊途同归
```

### 为什么1个run > 15个function calling？

1. **LLM对CLI的理解远超自定义schema**
   - GitHub数十亿行CLI命令
   - `cat | grep | wc` 是LLM的母语

2. **选择减少 = 准确率提升**
   - 15个工具 = AI要"选API"
   - 1个run命令 = AI只需"组合字符串"

3. **文本流统一接口**
   - 一切输入输出都是文本
   - 无需复杂的schema映射

## 执行模型

### 输入
- **任务描述**（自然语言）
- **工作目录**（可选，默认当前）

### 过程
1. 解析任务，转换为Shell命令链
2. 组合Unix命令（grep, awk, sed, find, xargs...）
3. 流式执行，实时反馈
4. 管道连接多个命令

### 输出
- 命令执行结果
- 错误诊断与修复建议

## 工具集（通过Shell实现）

| 任务 | Unix命令 | 示例 |
|------|----------|------|
| 文件搜索 | `find`, `grep` | `find . -name "*.ts" \| xargs grep "interface"` |
| 文本处理 | `cat`, `awk`, `sed` | `cat log.txt \| grep ERROR \| awk '{print $1}'` |
| 数据统计 | `wc`, `sort`, `uniq` | `wc -l *.csv \| sort -n` |
| 远程操作 | `ssh`, `curl`, `wget` | `curl -s API_URL \| jq '.data'` |
| 文件操作 | `cp`, `mv`, `rm`, `tar` | `tar -czf backup.tar.gz dir/` |
| 进程管理 | `ps`, `kill`, `top` | `ps aux \| grep node` |
| 网络诊断 | `ping`, `netstat`, `nslookup` | `netstat -an \| grep LISTEN` |
| JSON处理 | `jq` | `cat data.json \| jq '.users[].name'` |
| 压缩解压 | `gzip`, `zip`, `tar` | `tar -xzvf file.tar.gz` |

## 触发场景

当用户说/问以下内容时，激活此Skill：

- "用命令行处理"
- "写个shell脚本"
- "帮我grep一下"
- "分析这个日志"
- "批量重命名"
- "查进程"
- "监控CPU/内存"
- "用curl调API"
- "管道组合"
- "awk处理"
- "sed批量替换"
- "find查找"
- "运维任务"
- "写个脚本自动化"

## 常用命令速查

### 文件操作
```bash
# 查找并删除
find . -name "*.tmp" -delete

# 按大小查找
find . -size +100M -ls

# 查找修改时间
find . -mtime -7
```

### 文本处理
```bash
# 提取列
awk -F',' '{print $1 $2}' file.csv

# 替换
sed -i 's/old/new/g' file.txt

# 去重
sort file.txt | uniq -c
```

### 数据统计
```bash
# 行数统计
wc -l *.log

# 排序统计
cat data.txt | sort | uniq -c | sort -rn

# 求和
awk '{sum+=$1} END {print sum}' file.txt
```

### 网络API
```bash
# GET请求
curl -s https://api.example.com/data

# POST请求
curl -X POST -d '{"key":"value"}' https://api.example.com

# 带Header
curl -H "Authorization: Bearer token" https://api.example.com
```

### 进程与系统
```bash
# Top进程
ps aux --sort=-%mem | head -10

# 端口占用
lsof -i :8080

# 系统资源
df -h && free -m && uptime
```

## 命令构建原则

### 1. 管道优先
```bash
# ❌ 不好 - 多个独立命令
command1
command2
command3

# ✅ 好 - 管道连接
command1 | command2 | command3
```

### 2. 原子化输出
```bash
# ❌ 不好 - 输出冗余
ls -l file.txt

# ✅ 好 - 精确输出
wc -l file.txt
```

### 3. 错误处理
```bash
# ✅ 好 - 带错误检查
command || echo "Error: $?"
```

### 4. 安全优先
```bash
# ✅ 好 - 预览操作
ls *.txt  # 先列出
mv *.txt backup/  # 再移动

# 危险操作需确认
rm -rf /tmp/test  # 避免
```

## 错误恢复

当命令失败时：
1. 分析错误信息
2. 分解命令为更小单元
3. 逐个调试
4. 提供替代方案

## 与传统Function Calling对比

| 维度 | Function Calling | CLI Agent |
|------|-----------------|-----------|
| 工具数量 | 15+ | 1 |
| 学习成本 | 高（需定义schema） | 低（LLM天生会） |
| 灵活性 | 受限于预定义API | 无限组合 |
| 错误率 | 选错工具 | 组合错误 |
| 调试 | 需查看API文档 | 命令即文档 |

## 完整工作流示例

### 场景1：日志分析
```
1. tail -f app.log                    # 实时查看日志
2. grep ERROR app.log | wc -l         # 统计错误数
3. grep -A5 ERROR app.log             # 查看错误上下文
4. awk '/ERROR/{print $4}' app.log | sort | uniq -c | sort -rn  # 错误分类
```

### 场景2：代码库分析
```
1. find . -name "*.ts" | wc -l        # 统计TS文件数
2. find . -name "*.ts" -exec wc -l {} + | sort -n | tail -10  # 最大文件
3. grep -r "TODO" --include="*.ts" .  # 查找TODO
4. git log --oneline -20              # 最近提交
```

### 场景3：系统监控
```
1. top -bn1 | head -20                # CPU/内存
2. df -h                              # 磁盘空间
3. ps aux --sort=-%cpu | head -10     # Top进程
4. netstat -an | grep ESTABLISHED     # 网络连接
```

### 场景4：数据处理
```
1. head -1 data.csv                   # 查看表头
2. wc -l data.csv                     # 行数
3. awk -F',' '{print NF}' data.csv | sort -rn | head -1  # 最大列数
4. cut -d',' -f1 data.csv | sort | uniq  # 提取第一列去重
```

---

**哲学**：让LLM做它最擅长的事——理解和生成命令行。

**精髓**：
- 管道 > 单独命令
- 组合 > 分离
- 文本流统一一切
