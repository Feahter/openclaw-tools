#!/usr/bin/env python3
"""
NoteRx 核心诊断引擎
调用 MiniMax API 对小红书笔记进行 AI 诊断

用法：
    python3 noterx_engine.py --text "标题\n正文\n#标签"
    python3 noterx_engine.py --interactive
    python3 noterx_engine.py --json < notes.json

输出：JSON 格式诊断结果
"""

import json
import os
import re
import sys
import asyncio
import httpx
from pathlib import Path

# CES 模块
sys.path.insert(0, str(Path(__file__).parent))
from ces_calc import calculate_ces, calculate_ces_breakdown, estimate_views, judge_er, predict_viral


# ============================================================================
# MiniMax API 调用
# ============================================================================

def get_minimax_credentials() -> dict:
    """
    从多个来源获取 MiniMax 凭证（按优先级尝试）：
    1. 环境变量 OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL
    2. OpenClaw 配置 ~/.openclaw/openclaw.json
    3. 项目 .env 文件
    """
    # 来源1：环境变量
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.minimaxi.com/anthropic/v1")
    model = os.environ.get("OPENAI_MODEL", "MiniMax-M2.7")

    # 来源2：OpenClaw 配置
    if not api_key:
        try:
            oc_cfg_path = Path.home() / ".openclaw" / "openclaw.json"
            if oc_cfg_path.exists():
                with open(oc_cfg_path) as f:
                    cfg = json.load(f)
                providers = cfg.get("models", {}).get("providers", {})
                mm = providers.get("minimax", {})
                api_key = mm.get("apiKey", "")
                base_url = mm.get("baseURL", base_url)
                model = mm.get("defaultModel", model)
        except Exception:
            pass

    # 来源3：项目 .env 文件
    if not api_key:
        for env_path in [
            Path(__file__).resolve().parent / ".env",
            Path.home() / ".openclaw" / "workspace" / "projects" / "noterx" / ".env",
        ]:
            if env_path.exists():
                try:
                    for line in env_path.read_text().splitlines():
                        if line.startswith("OPENAI_API_KEY="):
                            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        elif line.startswith("OPENAI_BASE_URL="):
                            base_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                        elif line.startswith("OPENAI_MODEL="):
                            model = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if api_key:
                        break
                except Exception:
                    pass

    return {"api_key": api_key, "base_url": base_url, "model": model}


async def call_minimax(prompt: str, creds: dict) -> str:
    """调用 MiniMax Anthropic API，返回文本响应"""
    if not creds["api_key"]:
        raise RuntimeError("未配置 OPENAI_API_KEY")

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{creds['base_url']}/messages",
            headers={
                "x-api-key": creds["api_key"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": creds["model"],
                "max_tokens": 2048,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        if resp.status_code != 200:
            raise RuntimeError(f"API 错误 {resp.status_code}: {resp.text[:200]}")
        result = resp.json()

    # 提取文本（跳过 thinking blocks）
    for block in result.get("content", []):
        if block.get("type") == "text":
            return block["text"]
    return ""


# ============================================================================
# 输入解析
# ============================================================================

def parse_raw_text(raw: str) -> dict:
    """
    解析原始文本输入，自动识别：
    - 标题（第一行或含"标题："的行）
    - 正文（中间段落）
    - 话题标签（#开头的词）
    """
    lines = raw.strip().split("\n")
    if not lines:
        return {"title": "", "content": "", "topics": []}

    topics = []
    title = ""
    content_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 话题标签
        tags = re.findall(r'#(\S+)', line)
        topics.extend(tags)

        # 标题格式
        if line.startswith("标题：") or line.startswith("标题:"):
            title = re.sub(r'^标题[：:]\s*', '', line)
            continue

        # 如果还没有标题，且第一行没有 #，把它当标题
        if not title and not line.startswith("#") and not line.startswith("正文"):
            title = line
            continue

        # 正文内容
        if line.startswith("正文：") or line.startswith("正文:"):
            content_lines.append(re.sub(r'^正文[：:]\s*', '', line))
        else:
            content_lines.append(line)

    # 去除重复 topics
    topics = list(dict.fromkeys(topics))

    return {
        "title": title,
        "content": "\n".join(content_lines),
        "topics": topics,
    }


# ============================================================================
# 诊断 Prompt
# ============================================================================

DIAGNOSIS_PROMPT = """你是一位专业的小红书内容诊断专家。

收到笔记信息后，从6个维度进行诊断（0-100分），最后给出爆款概率预测。

## 笔记信息

**标题**：{title}

**正文**：
{content}

**话题标签**：{topics}

## 诊断要求

1. 标题吸引力（CTR）：数字/情绪/悬念/场景感
2. 内容利他性（收藏）：干货密度/可复制性/实用价值
3. 标签策略（推荐）：长尾词/竞争度/精准度
4. 互动引导（CES高权重）：问句/征集/投票等钩子
5. 赛道竞争度（突围）：差异化/细分切入能力
6. 时效性（时机）：热点/节点/季节相关

## 评分原则

- 分数反映相对水平，不是绝对质量
- 无互动数据时，基于内容质量评分
- 重点关注：用户能否「抄作业」

严格输出 JSON：

{{{{
  "summary": "3句话总结最核心问题",
  "overall_score": 0-100整数,
  "dimensions": [
    {{
      "name": "标题吸引力",
      "score": 0-100整数,
      "analysis": "问题分析，30字以内",
      "suggestion": "具体修改建议，50字以内",
      "priority": 1-3
    }},
    {{
      "name": "内容利他性",
      "score": 0-100整数,
      "analysis": "30字以内",
      "suggestion": "50字以内",
      "priority": 1-3
    }},
    {{
      "name": "标签策略",
      "score": 0-100整数,
      "analysis": "30字以内",
      "suggestion": "50字以内",
      "priority": 1-3
    }},
    {{
      "name": "互动引导",
      "score": 0-100整数,
      "analysis": "30字以内",
      "suggestion": "50字以内",
      "priority": 1-3
    }},
    {{
      "name": "赛道竞争度",
      "score": 0-100整数,
      "analysis": "30字以内",
      "suggestion": "50字以内",
      "priority": 1-3
    }},
    {{
      "name": "时效性",
      "score": 0-100整数,
      "analysis": "30字以内",
      "suggestion": "50字以内",
      "priority": 1-3
    }}
  ],
  "viral_prediction": {{
    "probability": "0-100%字符串",
    "reasoning": "预测依据，50字以内",
    "time_to_wait": "预计见效时间"
  }},
  "top_3_priority": [
    "最优先修改（一句话）",
    "次优先",
    "第三优先"
  ]
}}}}"""


# ============================================================================
# JSON 提取
# ============================================================================

def extract_json(text: str) -> dict | None:
    """从 LLM 输出中提取 JSON"""
    text = text.strip()

    # 方法1：直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 方法2：从 markdown 代码块
    m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 方法3：找 { ... }
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    return None


# ============================================================================
# 报告生成
# ============================================================================

def build_report(note: dict, diagnosis: dict, ces_score: int = 0,
                 ces_breakdown: str = "", er: float = 0.0) -> str:
    """生成 Markdown 诊断报告"""

    overall = diagnosis.get("overall_score", "N/A")
    er_pct = f"{er:.2%}" if er > 0 else "未知"

    lines = [
        "# 📋 薯医 NoteRx — 笔记诊断报告",
        "",
        f"**标题**: {note.get('title', '无标题')}",
        f"**话题**: {', '.join('#'+t for t in note.get('topics', [])) or '无标签'}",
        "",
        "## 📊 CES 互动评分",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| CES总分 | **{ces_score}** |",
        f"| 互动率 | {er_pct} |",
    ]

    if ces_breakdown and ces_breakdown != "无互动数据":
        lines.append(f"| 公式 | {ces_breakdown} |")

    if diagnosis:
        lines.extend(["", "## 🎯 AI 综合诊断", ""])
        lines.append(f"> {diagnosis.get('summary', '暂无评语')}")
        lines.append(f"\n### 综合评分: **{overall}**/100\n")

        dims = diagnosis.get("dimensions", [])
        if dims:
            lines.extend(["| 维度 | 评分 | 问题 | 建议 |",
                         "|------|------|------|------|"])
            for d in dims:
                name = d.get("name", "")
                score = d.get("score", "?")
                anal = (d.get("analysis") or "")[:35].replace("|", "\\|")
                sugg = (d.get("suggestion") or "")[:45].replace("|", "\\|")
                lines.append(f"| {name} | {score} | {anal} | {sugg} |")

        vp = diagnosis.get("viral_prediction", {})
        if vp:
            lines.extend(["", "## 🔮 爆款预测", "",
                         f"| 项目 | 内容 |",
                         "|------|------|",
                         f"| 概率 | {vp.get('probability', '?')} |",
                         f"| 依据 | {vp.get('reasoning', '未知')} |",
                         f"| 见效 | {vp.get('time_to_wait', '未知')} |"])

        priorities = diagnosis.get("top_3_priority", [])
        if priorities:
            lines.extend(["", "## 🔑 Top3 优先改", ""])
            for i, p in enumerate(priorities, 1):
                lines.append(f"{i}. {p}")

    lines.extend(["", "---", "*薯医 NoteRx · AI 诊断*"])
    return "\n".join(lines)


# ============================================================================
# 主诊断流程
# ============================================================================

async def diagnose(raw_text: str) -> dict:
    """
    核心诊断流程
    返回: {
        "note": parsed_note,
        "diagnosis": llm_diagnosis,
        "ces_score": int,
        "report": markdown_string
    }
    """
    creds = get_minimax_credentials()

    # 解析输入
    note = parse_raw_text(raw_text)

    # CES 计算（无互动数据时 ces=0）
    ces_score = 0
    ces_breakdown = "无互动数据（手动输入模式）"
    er = 0.0

    # 构建 prompt
    prompt = DIAGNOSIS_PROMPT.format(
        title=note.get("title", ""),
        content=note.get("content", "")[:1500],
        topics=", ".join(f"#{t}" for t in note.get("topics", [])) or "无标签",
    )

    # 调用 LLM
    if not creds["api_key"]:
        diagnosis = None
        report = "[错误] 未配置 OPENAI_API_KEY，请联系管理员"
    else:
        raw_response = await call_minimax(prompt, creds)
        diagnosis = extract_json(raw_response)
        if diagnosis is None:
            diagnosis = {"error": "JSON解析失败", "raw": raw_response[:500]}
        report = build_report(note, diagnosis, ces_score, ces_breakdown, er)

    return {
        "note": note,
        "diagnosis": diagnosis,
        "ces_score": ces_score,
        "report": report,
    }


# ============================================================================
# CLI
# ============================================================================

async def main():
    if "--interactive" in sys.argv:
        print("🩺 薯医 NoteRx — 交互式诊断（输入笔记内容，Ctrl+D 结束）")
        print("-" * 40)
        raw = sys.stdin.read()
        result = await diagnose(raw)
        print("\n" + result["report"])
        return

    if "--json" in sys.argv:
        raw = sys.stdin.read()
    elif "--text" in sys.argv:
        idx = sys.argv.index("--text")
        raw = " ".join(sys.argv[idx+1:])
    else:
        # 默认：把所有参数当作文本
        raw = " ".join(sys.argv[1:])

    if not raw.strip():
        print("用法: python3 noterx_engine.py --text '标题\\n正文\\n#标签'")
        sys.exit(1)

    result = await diagnose(raw)
    print(result["report"])


if __name__ == "__main__":
    asyncio.run(main())
