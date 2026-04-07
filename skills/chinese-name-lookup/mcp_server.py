#!/usr/bin/env python3
"""
八字引擎 MCP Server (bazi_mcp)

通过 Model Context Protocol (MCP) 暴露八字分析功能，
可被 Claude Desktop、Cursor、Cline 等 MCP Client 调用。

用法:
    # 直接运行（stdio 模式）
    python mcp_server.py

    # 或使用 mcp 工具测试
    python mcp_server.py --inspect
"""

import sys
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

# 确保 scripts 目录在 sys.path 中（scripts/ 是顶级模块目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(SCRIPT_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# MCP SDK
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, ConfigDict

# 导入八字引擎
from scripts.bazi_engine import full_bazi_analysis as _full_bazi_analysis
from scripts.dayun_liunian import full_dayun_analysis as _full_dayun_analysis

# ============================================================
# MCP Server 初始化
# ============================================================

mcp = FastMCP("bazi_mcp")

# ============================================================
# Pydantic 输入模型
# ============================================================


class BaziAnalysisInput(BaseModel):
    """八字排盘输入参数"""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    birth_time: str = Field(
        ...,
        description="出生时间，格式为 'YYYY-MM-DD HH:MM'（24小时制），例如 '2024-03-15 10:30'"
    )
    gender: str = Field(
        ...,
        description="性别，'男' 或 '女'"
    )
    province: Optional[str] = Field(
        default="",
        description="出生省份/直辖市，用于真太阳时矫正，例如 '四川'、'北京'。不填则默认北京时间"
    )
    city: Optional[str] = Field(
        default="",
        description="出生城市，用于真太阳时矫正，例如 '成都'、'上海'。不填则默认北京时间"
    )

    @field_validator("birth_time")
    @classmethod
    def validate_birth_time(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError(
                "无效的时间格式: '{}'，期望格式为 'YYYY-MM-DD HH:MM'，例如 '2024-03-15 10:30'".format(v)
            )
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ("男", "女"):
            raise ValueError("性别必须为 '男' 或 '女'，实际为: '{}'".format(v))
        return v


class DayunAnalysisInput(BaseModel):
    """大运流年分析输入参数"""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    birth_time: str = Field(
        ...,
        description="出生时间，格式为 'YYYY-MM-DD HH:MM'（24小时制），例如 '2024-03-15 10:30'"
    )
    gender: str = Field(
        ...,
        description="性别，'男' 或 '女'"
    )
    province: Optional[str] = Field(
        default="",
        description="出生省份/直辖市，用于真太阳时矫正"
    )
    city: Optional[str] = Field(
        default="",
        description="出生城市，用于真太阳时矫正"
    )

    @field_validator("birth_time")
    @classmethod
    def validate_birth_time(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError(
                "无效的时间格式: '{}'，期望格式为 'YYYY-MM-DD HH:MM'".format(v)
            )
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ("男", "女"):
            raise ValueError("性别必须为 '男' 或 '女'，实际为: '{}'".format(v))
        return v


# ============================================================
# 工具函数：格式化输出
# ============================================================


def _g(d: Dict, *keys, default: str = "N/A") -> str:
    """Safely get nested dict value, always returns string."""
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
        else:
            return default
    if d is None:
        return default
    return str(d)


def _format_bazi_markdown(result: Dict[str, Any]) -> str:
    """将八字分析结果格式化为 Markdown 报告"""
    bazi = result.get("bazi", {})
    rizhu = result.get("rizhu_strength", {})
    xiyong = result.get("xiyongshen", {})
    shishen = result.get("shishen", {})
    shierzhang = result.get("shierzhang", {})
    minggong = result.get("minggong_shengong", {})
    tiao_hou = result.get("tiao_hou", {})
    shen_sha = result.get("shen_sha", {})
    lunar = result.get("lunar", {})
    primary_method = result.get("primary_method", {})

    lines = [
        "# 八字命盘分析",
        "",
        "**出生时间**: " + _g(result, "birth_chart"),
        "**性别**: " + _g(result, "gender"),
        "**生肖**: " + _g(result, "zodiac"),
        "**农历**: " + _g(lunar, "year") + "年" + _g(lunar, "month") + "月" + _g(lunar, "day") + "日",
        "",
        "## 八字命盘",
        "",
        "| 年柱 | 月柱 | 日柱 | 时柱 |",
        "|:---:|:---:|:---:|:---:|",
        "| **"
        + _g(bazi, "year", "stem") + _g(bazi, "year", "branch") + "** | **"
        + _g(bazi, "month", "stem") + _g(bazi, "month", "branch") + "** | **"
        + _g(bazi, "day", "stem") + _g(bazi, "day", "branch") + "** | **"
        + _g(bazi, "hour", "stem") + _g(bazi, "hour", "branch") + "** |",
        "",
        "## 日主强弱",
        "",
        "- **日主**: " + _g(rizhu, "day_stem") + "（" + _g(rizhu, "day_element") + "）",
        "- **月令**: " + _g(rizhu, "month_branch"),
        "- **强弱**: " + _g(rizhu, "strength") + " — " + _g(rizhu, "reason"),
        "- **主推方法**: " + primary_method.get("primary", "N/A") if isinstance(primary_method, dict) else "N/A",
        "",
        "## 喜用神",
        "",
        "- **喜用神**: " + "，".join(xiyong.get("xiyongshen") or []),
        "- **忌神**: " + "，".join(xiyong.get("jishen") or []),
        "",
    ]

    # 十神
    if shishen:
        lines.extend([
            "## 十神",
            "",
            "- **年干**: " + _g(shishen, "year_stem") + " · 年支: " + _g(shishen, "year_branch"),
            "- **月干**: " + _g(shishen, "month_stem") + " · 月支: " + _g(shishen, "month_branch"),
            "- **时干**: " + _g(shishen, "hour_stem") + " · 时支: " + _g(shishen, "hour_branch"),
            "",
        ])

    # 十二长生
    if shierzhang:
        lines.extend([
            "## 十二长生",
            "",
            "- 年支: " + _g(shierzhang, "year_branch")
            + " · 月支: " + _g(shierzhang, "month_branch")
            + " · 日支: " + _g(shierzhang, "day_branch")
            + " · 时支: " + _g(shierzhang, "hour_branch"),
            "",
        ])

    # 命宫身宫
    if minggong:
        mg = minggong.get("命宫", {})
        sg = minggong.get("身宫", {})
        lines.extend([
            "## 命宫 · 身宫",
            "",
            "- **命宫**: " + _g(mg, "stem") + _g(mg, "branch")
            + "（" + _g(mg, "element") + "，" + _g(mg, "shishen") + "，" + _g(mg, "changsheng") + "）",
            "- **身宫**: " + _g(sg, "stem") + _g(sg, "branch")
            + "（" + _g(sg, "element") + "，" + _g(sg, "shishen") + "，" + _g(sg, "changsheng") + "）",
            "",
        ])

    # 纳音
    year_nayin = result.get("year_nayin")
    if year_nayin:
        lines.append("**年柱纳音**: " + year_nayin)
        lines.append("")

    # 调候
    if tiao_hou and tiao_hou.get("喜用"):
        lines.extend([
            "## 穷通宝鉴调候",
            "",
            "- **喜用**: " + "，".join(tiao_hou.get("喜用", [])),
            "- **忌避**: " + "，".join(tiao_hou.get("忌避", [])),
            "",
        ])

    # 神煞
    if shen_sha and isinstance(shen_sha, dict) and len(shen_sha) > 0:
        # 神煞详情在 summary 字段（dict），每个值是 string
        shen_summary = shen_sha.get("summary", {})
        shen_items = []
        for k, v in shen_summary.items():
            if not v:
                continue
            shen_items.append("- **{}:** {}".format(k, v))
        if shen_items:
            lines.extend(["## 神煞", ""] + shen_items + [""])
        # 胎元、命宫也附上（用 description 字段）
        if shen_sha.get("胎元"):
            ty = shen_sha["胎元"]
            ty_desc = ty.get("description", "") if isinstance(ty, dict) else str(ty)
            if ty_desc:
                lines.append("**胎元**: " + ty_desc)
        if shen_sha.get("命宫"):
            mg = shen_sha["命宫"]
            mg_desc = mg.get("description", "") if isinstance(mg, dict) else str(mg)
            if mg_desc:
                lines.append("**命宫神煞**: " + mg_desc)
        if shen_items or shen_sha.get("胎元") or shen_sha.get("命宫"):
            lines.append("")

    lines.append("*本报告由本地八字引擎生成，仅供参考。*")
    return "\n".join(lines)


def _format_dayun_markdown(result: Dict[str, Any]) -> str:
    """将大运流年结果格式化为 Markdown"""
    lines = [
        "# 大运流年分析",
        "",
        "**方向规则**: " + _g(result, "direction_rule", default="N/A"),
        "",
    ]

    # 大运列表
    dayun_list = result.get("dayun_list", [])
    if dayun_list:
        lines.append("## 大运序列")
        lines.append("")
        for d in dayun_list:
            lines.append(
                "- **" + str(_g(d, "start_age"))
                + "-" + str(_g(d, "end_age")) + "岁**: "
                + _g(d, "ganzhi")
                + " 【" + _g(d, "direction") + "】"
            )
        lines.append("")

    # 近五年流年
    recent = result.get("recent_liunian", [])
    if recent:
        lines.append("## 近5年流年")
        lines.append("")
        for r in recent:
            lines.append(
                "- **" + str(r.get("year", "N/A")) + "**（" + r.get("ganzhi", "N/A") + "）"
                ": " + (r.get("analysis") or r.get("luck", "N/A"))
            )
        lines.append("")

    # 驿马运
    yima = result.get("yima")
    if yima and isinstance(yima, dict):
        yima_desc = yima.get("description", "") or str(yima)
        if yima_desc:
            lines.append("**驿马运**: " + yima_desc)
            lines.append("")

    lines.append("*本报告由本地八字引擎生成，仅供参考。*")
    return "\n".join(lines)


# ============================================================
# MCP 工具
# ============================================================


@mcp.tool(
    name="bazi_full_analysis",
    annotations={
        "title": "八字完整排盘分析",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def bazi_full_analysis(params: BaziAnalysisInput) -> str:
    """
    完整八字分析排盘。

    输入出生时间和性别，返回完整八字命盘，包含：
    - 八字干支（年、月、日、时柱）
    - 日主强弱判定（千里命稿法 + 滴天髓法，自动判断主推）
    - 喜用神 / 忌神
    - 十神 / 十二长生
    - 命宫 / 身宫
    - 穷通宝鉴调候喜忌
    - 神煞（含空亡/桃花/驿马等）
    - 纳音五行

    所有计算完全本地化，无需 API。

    Args:
        params: 包含 birth_time (YYYY-MM-DD HH:MM)、gender (男/女)、province、city

    Returns:
        Markdown 格式的完整八字命盘分析报告

    Example:
        输入: birth_time='2024-03-15 10:30', gender='男'
        输出: 包含年柱甲辰、月柱丁辰、日柱庚子、时柱辛巳的完整八字报告
    """
    try:
        dt = datetime.strptime(params.birth_time, "%Y-%m-%d %H:%M")
        year, month, day, hour = dt.year, dt.month, dt.day, dt.hour

        result = _full_bazi_analysis(
            year=year,
            month=month,
            day=day,
            hour=hour,
            province=params.province or "",
            city=params.city or "",
        )
        result["gender"] = params.gender
        return _format_bazi_markdown(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return "八字分析失败: {}: {}".format(type(e).__name__, e)


@mcp.tool(
    name="bazi_dayun_analysis",
    annotations={
        "title": "大运流年分析",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def bazi_dayun_analysis(params: DayunAnalysisInput) -> str:
    """
    大运流年分析。

    输入出生时间和性别，返回：
    - 大运序列（每步大运的干支、起止年龄、方向）
    - 近5年流年简析（含十神、流年评分、吉凶判断）
    - 驿马运节点
    - 精确大运起始年龄

    大运规则：阳男阴女顺行（从月柱向下排），阴男阳女逆行。

    Args:
        params: 包含 birth_time (YYYY-MM-DD HH:MM)、gender (男/女)、province、city

    Returns:
        Markdown 格式的大运流年分析报告

    Example:
        输入: birth_time='2024-03-15 10:30', gender='男'
        输出: 大运序列 + 近5年流年分析
    """
    try:
        dt = datetime.strptime(params.birth_time, "%Y-%m-%d %H:%M")
        year, month, day, hour = dt.year, dt.month, dt.day, dt.hour

        bazi_result = _full_bazi_analysis(
            year=year,
            month=month,
            day=day,
            hour=hour,
            province=params.province or "",
            city=params.city or "",
        )

        bazi = bazi_result["bazi"]
        rizhu = bazi_result["rizhu_strength"]
        xiyong = bazi_result["xiyongshen"]

        bazi_with_xiyong = {
            "bazi": bazi,
            "rizhu_strength": rizhu,
            "xiyongshen": xiyong,
        }

        birth_timestamp = time.mktime((year, month, day, hour, 0, 0, 0, 0, 0))

        dayun_result = _full_dayun_analysis(
            bazi_info=bazi_with_xiyong,
            gender=params.gender,
            birth_timestamp=birth_timestamp,
            birth_year=year,
            birth_month=month,
        )

        dayun_result["birth_chart"] = bazi_result["birth_chart"]
        dayun_result["gender"] = params.gender
        return _format_dayun_markdown(dayun_result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return "大运流年分析失败: {}: {}".format(type(e).__name__, e)


# ============================================================
# stdio 入口
# ============================================================

if __name__ == "__main__":
    if "--inspect" in sys.argv:
        import subprocess
        subprocess.run([
            sys.executable, "-m", "mcp.server.fastmcp",
            "inspect", __file__
        ])
    else:
        mcp.run()
