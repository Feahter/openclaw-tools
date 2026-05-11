# 技术说明 — NoteRx Skill

## API Key 自动发现

引擎自动从 3 个位置获取 MiniMax API key（无需手动配置）：

1. **环境变量** — `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL`
2. **OpenClaw 配置** — `~/.openclaw/openclaw.json` → models.providers.minimax
3. **项目 .env** — `~/.openclaw/workspace/projects/noterx/.env`

---

## 核心脚本

### scripts/noterx_engine.py

核心诊断引擎（437 行），调用 MiniMax API。

```python
# 调用方式
from pathlib import Path
import subprocess

skill_dir = Path("~/.openclaw/workspace/skills/noterx").expanduser()
result = subprocess.run(
    ["python3", "scripts/noterx_engine.py", "--text", raw_text],
    capture_output=True, text=True, cwd=skill_dir
)
print(result.stdout)  # Markdown 诊断报告
```

### scripts/ces_calc.py

CES 评分计算（145 行），纯本地无 API 依赖。

```python
from ces_calc import calculate_ces, estimate_views, judge_er, predict_viral

# CES 计算
ces = calculate_ces(liked=100, collected=50, commented=10, shared=5)
# CES = 100*1 + 50*1 + 10*4 + 5*4 = 210

# 互动率判断
er = 100 / estimate_views(100)  # ER ≈ 3%
print(judge_er(er))  # ✅ 达标（ER>3%，有爆款潜力）

# 爆款预测
v = predict_viral(ces, er)
# {'probability': '10-20%', 'reasoning': '...', 'time_to_wait': '3-5天'}
```

---

## 依赖

- **Python**: 系统 Python 3（已安装 httpx/click/pydantic）
- **HTTP 客户端**: httpx（异步 HTTP）
- **API**: MiniMax Anthropic API 格式

---

## OpenClaw 集成

### 调用流程

```
用户: 帮我看看这篇笔记能爆吗
AI:   [触发 noterx skill] → 调用 scripts/noterx_engine.py → 返回诊断报告
```

### 快速测试

```bash
cd ~/.openclaw/workspace/skills/noterx

# 无需配置环境变量，引擎自动获取 API key
python3 scripts/noterx_engine.py --text '标题\n正文\n#标签'
```

---

## 输入解析

引擎自动解析原始文本：

| 输入格式 | 解析结果 |
|---------|---------|
| 第一行无 # | → 标题 |
| `标题：xxx` | → 标题 |
| `正文：xxx` | → 正文 |
| `#标签` | → 话题标签 |

---

## 输出格式

Markdown 诊断报告：

```markdown
# 📋 薯医 NoteRx — 笔记诊断报告

**标题**: xxx
**话题**: #xxx, #xxx

## 📊 CES 互动评分
| 指标 | 数值 |
|CES总分 | 0 |

## 🎯 AI 综合诊断
> 总结评语

### 综合评分: XX/100

| 维度 | 评分 | 问题 | 建议 |
|------|------|------|------|

## 🔮 爆款预测
| 项目 | 内容 |
|概率 | XX% |

## 🔑 Top3 优先改
1. 建议1
2. 建议2
3. 建议3
```
