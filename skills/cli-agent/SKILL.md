---
name: cli-agent
description: Unix哲学AI Agent - 一个run()命令比15个function calling更有效。基于Shell命令流执行任务，发挥LLM对CLI的天然理解优势。
---

# CLI Agent - Unix哲学AI执行器

> "一个 run(command="...") 比15个function calling工具效果好得多。"
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

## 使用场景

### 1. 代码搜索与分析
```
搜索包含"TODO"的TypeScript文件：
find . -name "*.ts" -exec grep -l "TODO" {} \;
```

### 2. 日志分析
```
提取ERROR日志并统计：
grep ERROR app.log | awk '{print $4}' | sort | uniq -c | sort -rn
```

### 3. 数据处理
```
CSV转JSON：
cat data.csv | head -1 && cat data.csv | tail -n +2 | while read line; do echo "$line" | awk -F',' '{print "{"$1"}"}'; done
```

### 4. 批量操作
```
重命名文件：
ls *.txt | sed 's/\(.*\)\.txt/mv & \1.bak/' | sh
```

### 5. API调用
```
curl + jq 组合：
curl -s API_URL | jq '.results[] | {name: .name, value: .price}'
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

## 示例工作流

### 完整任务：分析项目结构
```
1. find . -type f -name "*.ts" | wc -l
2. find . -type f -name "*.ts" -exec wc -l {} + | sort -n | tail -5
3. grep -r "import" --include="*.ts" . | wc -l
```

### 完整任务：监控系统状态
```
1. top -bn1 | head -15
2. df -h
3. free -m
4. ps aux --sort=-%mem | head -6
```

---

**哲学**：让LLM做它最擅长的事——理解和生成命令行。
