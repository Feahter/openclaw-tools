#!/usr/bin/env python3
"""
八字分析报告格式化器
Phase 9 - 完整报告输出优化

将所有模块整合，输出格式优美、信息完整的 Markdown 格式八字分析报告。
纯本地计算，不依赖 API。
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 导入本地模块
sys.path.insert(0, str(Path(__file__).parent))

from bazi_engine import (
    full_bazi_analysis, get_bazi, get_rizhu_strength,
    HEAVENLY_STEMS, EARTHLY_BRANCHES, STEM_ELEMENTS, ELEMENT_NAMES,
    BRANCH_ELEMENTS, get_shishen, get_shierzhang,
    determine_xiyongshen, get_nayin,
)
from lunar_calendar import (
    get_lunar_date, get_zodiac, format_lunar_date,
    get_chinese_year_name,
)
from dayun_liunian import (
    get_dayun_sequence, get_dayun_summary, get_recent_liunian,
    analyze_liunian_by_year, full_dayun_analysis, is_shun, is_yang_stem,
)
from shen_sha import get_shen_sha_summary, get_tianyi_guiren, get_wenchang, get_yima, get_huagai, get_taohua
from zodiac_preferences import get_zodiac_preferences
from liushen_xinxing import get_full_xinxing_report


# ============================================================
# 报告格式化主函数
# ============================================================

def format_full_report(
    bazi_info: Dict[str, Any],
    name_candidates: List[Dict[str, Any]],
    gender: int = 1,
    surname: str = "",
    full_name: Optional[str] = None,
) -> str:
    """
    生成完整的八字分析 Markdown 报告

    Args:
        bazi_info: 八字分析结果（来自 full_bazi_analysis 或 generate_name_recommendations）
        name_candidates: 推荐姓名列表
        gender: 性别 (1=男, 0=女)
        surname: 姓氏
        full_name: 姓名（如果已有）

    Returns:
        Markdown 格式的完整报告
    """
    lines = []

    # ===== 基本信息 =====
    lines.extend(_format_basic_info(bazi_info, surname, full_name, gender))

    lines.append("")
    lines.append("---")
    lines.append("")

    # ===== 八字命盘 =====
    lines.extend(_format_bazi_table(bazi_info))

    lines.append("")
    lines.append("---")
    lines.append("")

    # ===== 命局分析 =====
    lines.extend(_format_mingju_analysis(bazi_info))

    lines.append("")
    lines.append("---")
    lines.append("")

    # ===== 神煞一览 =====
    lines.extend(_format_shen_sha_list(bazi_info))

    lines.append("")
    lines.append("---")
    lines.append("")

    # ===== 大运流年 =====
    lines.extend(_format_dayun_section(bazi_info, gender))

    lines.append("")
    lines.append("---")
    lines.append("")

    # ===== 姓名分析 =====
    lines.extend(_format_name_section(bazi_info, name_candidates, surname))
    lines.append("")
    lines.append("---")
    lines.append("")

    # ===== 命理建议 =====
    lines.extend(_format_suggestions(bazi_info))

    return "\n".join(lines)


def _format_basic_info(
    bazi_info: Dict[str, Any],
    surname: str,
    full_name: Optional[str],
    gender: int,
) -> List[str]:
    """格式化基本信息 section"""
    lines = []

    # 标题
    lines.append("# 八字分析报告")
    lines.append("")

    # 信息来源标记
    source = bazi_info.get("source", "unknown")
    is_fallback = bazi_info.get("is_fallback", False)
    if source == "api":
        lines.append("✅ **数据来源：八字精算API**（最准确）")
    elif is_fallback or source == "local_engine":
        lines.append("⚠️ **数据来源：本地八字引擎**（估算值，建议配置八字API获取更精确的结果）")
    elif source == "user_prefer":
        lines.append("ℹ️ **喜用神：用户指定**")
    else:
        lines.append("⚠️ **数据来源：默认值（建议配置八字API）**")
    lines.append("")

    # 基本信息表格
    lines.append("## 基本信息")
    lines.append("")

    zodiac = bazi_info.get("zodiac", "未知")
    lunar = bazi_info.get("lunar", {})
    lunar_str = bazi_info.get("lunar_str", "")
    birth_chart = bazi_info.get("birth_chart", "")

    # 出生时间解析
    birth_time_str = ""
    if birth_chart:
        # birth_chart format: "甲辰年 丁卯月 庚午日 辛巳时"
        parts = birth_chart.replace("年", " ").replace("月", " ").replace("日", " ").replace("时", " ").split()
        if len(parts) >= 4:
            year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi = parts[:4]
            birth_time_str = f"{year_ganzhi}年 {month_ganzhi}月 {day_ganzhi}日 {hour_ganzhi}时"

    gender_str = "男" if gender == 1 else "女"

    # 提取农历年月日
    if lunar:
        lunar_year = lunar.get("year", "")
        lunar_month = lunar.get("month", "")
        lunar_day = lunar.get("day", "")
        is_leap = lunar.get("is_leap", False)
        leap_str = "（闰月）" if is_leap else ""
        lunar_date_str = f"农历{lunar_year}年{leap_str}{lunar_month}月{lunar_day}日"
    else:
        lunar_date_str = lunar_str or "未知"

    lines.append("| 项目 | 内容 |")
    lines.append("|:---|:---|")
    lines.append(f"| 姓名 | {full_name or surname or '待输入'} |")
    lines.append(f"| 性别 | {gender_str} |")
    lines.append(f"| 出生时间 | {birth_time_str or birth_chart} |")
    lines.append(f"| 农历 | {lunar_date_str} |")
    lines.append(f"| 生肖 | {zodiac} |")

    return lines


def format_bazi_table(bazi_info: Dict[str, Any]) -> str:
    """格式化八字命盘表格（供外部调用）"""
    lines = _format_bazi_table(bazi_info)
    return "\n".join(lines)


def _format_bazi_table(bazi_info: Dict[str, Any]) -> List[str]:
    """格式化八字命盘表格"""
    lines = []
    lines.append("## 八字命盘")
    lines.append("")

    bazi = bazi_info.get("bazi", {})
    if not bazi:
        lines.append("*八字信息不可用*")
        return lines

    year_p = bazi.get("year", {})
    month_p = bazi.get("month", {})
    day_p = bazi.get("day", {})
    hour_p = bazi.get("hour", {})

    # 表头
    lines.append("| 年柱 | 月柱 | 日柱 | 时柱 |")
    lines.append("|:---|:---|:---|:---|")

    # 天干地支行
    year_ganzhi = f"{year_p.get('stem', '')}{year_p.get('branch', '')}"
    month_ganzhi = f"{month_p.get('stem', '')}{month_p.get('branch', '')}"
    day_ganzhi = f"{day_p.get('stem', '')}{day_p.get('branch', '')}"
    hour_ganzhi = f"{hour_p.get('stem', '')}{hour_p.get('branch', '')}"

    lines.append(f"| **{year_ganzhi}** | **{month_ganzhi}** | **{day_ganzhi}** | **{hour_ganzhi}** |")
    lines.append("")

    # 十神行
    shishen = bazi_info.get("shishen", {})
    year_shishen = shishen.get("year_stem", "") + shishen.get("year_branch", "")
    month_shishen = shishen.get("month_stem", "") + shishen.get("month_branch", "")
    day_shishen = shishen.get("day_branch", "")  # 日支无天干
    hour_shishen = shishen.get("hour_stem", "") + shishen.get("hour_branch", "")

    lines.append("| *十神* | *十神* | *日主* | *十神* |")
    lines.append(f"| {year_shishen} | {month_shishen} | {day_p.get('stem', '')} | {hour_shishen} |")
    lines.append("")

    # 十二长生行
    shierzhang = bazi_info.get("shierzhang", {})
    year_cs = shierzhang.get("year_branch", "")
    month_cs = shierzhang.get("month_branch", "")
    day_cs = shierzhang.get("day_branch", "")
    hour_cs = shierzhang.get("hour_branch", "")

    lines.append("| *长生* | *长生* | *长生* | *长生* |")
    lines.append(f"| {year_cs} | {month_cs} | {day_cs} | {hour_cs} |")

    # 年柱纳音
    year_nayin = bazi_info.get("year_nayin", "")
    if year_nayin:
        lines.append("")
        lines.append(f"**年柱纳音**：{year_nayin}")

    return lines


def _format_mingju_analysis(bazi_info: Dict[str, Any]) -> List[str]:
    """格式化命局分析 section"""
    lines = []

    lines.append("## 命局分析")
    lines.append("")

    xiyongshen = bazi_info.get("xiyongshen", {})
    xiyong_list = xiyongshen.get("xiyongshen", [])
    jishen_list = xiyongshen.get("jishen", [])
    qiangruo = xiyongshen.get("qiangruo", "未知")

    # 日主强弱（优先使用v2量化结果）
    rizhu_strength = bazi_info.get("rizhu_strength", {})
    strength = rizhu_strength.get("strength", qiangruo)
    reason = rizhu_strength.get("reason", xiyongshen.get("analysis", ""))

    day_stem = rizhu_strength.get("day_stem", "")
    day_element = rizhu_strength.get("day_element", "")

    # v2 量化结果显示（子平真诠派）
    v2_score = rizhu_strength.get("score", None)
    v2_breakdown = rizhu_strength.get("breakdown", None)
    if v2_score is not None:
        lines.append(f"- **日主**：{day_stem}{day_element}，**{strength}**（子平法：{v2_score}/100）")
        if v2_breakdown:
            yueling_state = v2_breakdown.get("yueling", {}).get("state", "")
            yueling_score = v2_breakdown.get("yueling", {}).get("score", 0)
            tonggen_score = v2_breakdown.get("tongen", {}).get("tongen_score", 0)
            lg_score = v2_breakdown.get("tongen", {}).get("linggong_score", 0)
            bijie_count = v2_breakdown.get("bijie", {}).get("count", 0)
            bijie_score = v2_breakdown.get("bijie", {}).get("score", 0)
            yinxing_score = v2_breakdown.get("yinxing", {}).get("score", 0)
            lg_info = f"+临宫{lg_score}分" if lg_score > 0 else ""
            lines.append(f"  - 月令{yueling_state} {yueling_score}分 + 通根 {tonggen_score}分{lg_info} + 比劫×{bijie_count} {bijie_score}分 + 印星 {yinxing_score}分")
    else:
        lines.append(f"- **日主**：{day_stem}{day_element}，**{strength}**，{reason}")

    # 全藏干计数法结果（滴天髓派）
    rizhu_by_count = bazi_info.get("rizhu_by_count", None)
    if rizhu_by_count:
        count_strength = rizhu_by_count.get("strength", "")
        count_ratio = rizhu_by_count.get("score_ratio", 0)
        count_xiyong = rizhu_by_count.get("xiyongshen_by_count", [])
        count_ji = rizhu_by_count.get("jishen_by_count", [])
        count_analysis = rizhu_by_count.get("analysis", "")
        wx_counts = rizhu_by_count.get("wx_counts", {})
        lines.append(f"- **日主**（滴天髓法）：{count_strength}（比例 {count_ratio}，同类7 vs 克泄耗7）")
        lines.append(f"  - 五行分布：木{wx_counts.get('木',0)} 火{wx_counts.get('火',0)} 土{wx_counts.get('土',0)} 金{wx_counts.get('金',0)} 水{wx_counts.get('水',0)}")
        lines.append(f"  - 喜用神：{'、'.join(count_xiyong) if count_xiyong else '待定'}，忌神：{'、'.join(count_ji) if count_ji else '无'}")
        lines.append(f"  - 注：{count_analysis}")
    lines.append("")

    # 喜用神
    xiyong_str = "、".join(xiyong_list) if xiyong_list else "待定"
    lines.append(f"- **用神**：**{xiyong_str}**")
    lines.append("")

    # 忌神
    jishen_str = "、".join(jishen_list) if jishen_list else "待定"
    lines.append(f"- **忌神**：{jishen_str}")
    lines.append("")

    # 五行分布
    wx_counts = xiyongshen.get("wx_counts", {})
    if wx_counts:
        lines.append("**五行分布**：")
        bars = []
        max_count = max(wx_counts.values()) if wx_counts else 1
        for elem in ["木", "火", "土", "金", "水"]:
            cnt = wx_counts.get(elem, 0)
            bar_len = int(cnt / max_count * 10) if max_count > 0 else 0
            bars.append(f"  {elem} `{'█' * bar_len}{'░' * (10 - bar_len)}` {cnt}个")
        lines.extend(bars)
        lines.append("")

    # 格局
    pattern = bazi_info.get("pattern", {})
    pattern_cheng = bazi_info.get("pattern_cheng", {})
    if pattern:
        pattern_name = pattern.get("pattern", "待定")
        pattern_type = pattern.get("pattern_type", "")
        lines.append(f"- **格局**：**{pattern_name}**（{pattern_type}）")
        if pattern_cheng:
            is_cheng = pattern_cheng.get("is_cheng", False)
            cheng_level = pattern_cheng.get("level", "未知")
            cheng_str = "成格" if is_cheng else "破格/未成"
            lines.append(f"  - 成败：**{cheng_str}**（{cheng_level}）")
            poge_reason = pattern_cheng.get("poge_reason", "")
            if poge_reason:
                lines.append(f"  - 破格原因：{poge_reason}")
            suggestion = pattern_cheng.get("suggestion", "")
            if suggestion:
                lines.append(f"  - 建议：{suggestion}")
        reason_text = pattern.get("reason", "")
        if reason_text:
            lines.append(f"  - 分析：{reason_text[:60]}...")

    # 十神心性解读
    xinxing = bazi_info.get("xinxing", [])
    if xinxing:
        lines.append("")
        lines.append(get_full_xinxing_report(xinxing))

    return lines


def format_shen_sha_list(shen_sha_dict: Dict[str, Any]) -> str:
    """格式化神煞一览（供外部调用）"""
    lines = _format_shen_sha_list(shen_sha_dict)
    return "\n".join(lines)


def _format_shen_sha_list(bazi_info: Dict[str, Any]) -> List[str]:
    """格式化神煞一览 section"""
    lines = []

    lines.append("## 神煞一览")
    lines.append("")

    # 获取神煞数据
    shen_sha = bazi_info.get("shen_sha", {})
    if not shen_sha:
        # 如果 bazi_info 中没有神煞，从八字中获取
        bazi = bazi_info.get("bazi", bazi_info)
        year_stem_idx = bazi.get("year", {}).get("stem_idx", 0)
        year_branch_idx = bazi.get("year", {}).get("branch_idx", 0)
        month_stem_idx = bazi.get("month", {}).get("stem_idx", 0)
        day_stem_idx = bazi.get("day", {}).get("stem_idx", 0)

        # 导入P1神煞函数
        from shen_sha import (
            get_tiande, get_yuede, get_hongluan_tianxi,
            get_sanqi, get_jiangxing, get_wangshen as _get_wangshen
        )

        tianyi = get_tianyi_guiren(year_stem_idx, year_branch_idx)
        wenchang = get_wenchang(year_stem_idx)
        yima = get_yima(year_branch_idx)
        huagai = get_huagai(year_branch_idx)
        taohua = get_taohua(year_branch_idx)

        tiande = get_tiande(year_stem_idx)
        yuede = get_yuede(year_stem_idx)
        hongluan = get_hongluan_tianxi(year_branch_idx)
        sanqi = get_sanqi(year_stem_idx, month_stem_idx, day_stem_idx)
        jiangxing = get_jiangxing(year_branch_idx)
        wangshen = _get_wangshen(year_branch_idx)

        shen_sha = {
            "P0": {
                "天乙贵人": tianyi,
                "文昌": wenchang,
                "驿马": yima,
                "华盖": huagai,
                "桃花": taohua,
            },
            "P1": {
                "天德": tiande,
                "月德": yuede,
                "红鸾天喜": hongluan,
                "三奇": sanqi,
                "将星": jiangxing,
                "亡神": wangshen,
            }
        }

    # P0 神煞（最重要）
    p0 = shen_sha.get("P0", {})
    if p0:
        items = []
        for name in ["天乙贵人", "文昌", "驿马", "华盖", "桃花"]:
            data = p0.get(name, {})
            desc = data.get("description", "")
            if desc:
                items.append(f"- **{name}**：{desc}")
            else:
                items.append(f"- **{name}**：无")

        if items:
            lines.append("### P0 主要神煞")
            lines.append("")
            lines.extend(items)
            lines.append("")

    # P1 神煞（重要）
    p1 = shen_sha.get("P1", {})
    if p1:
        items = []
        for name in ["天德", "月德", "红鸾天喜", "三奇", "将星", "亡神"]:
            data = p1.get(name, {})
            desc = data.get("description", "")
            if desc:
                items.append(f"- **{name}**：{desc}")

        if items:
            lines.append("### P1 辅助神煞")
            lines.append("")
            lines.extend(items)

    return lines


def _format_dayun_section(bazi_info: Dict[str, Any], gender: int) -> List[str]:
    """格式化大运流年 section"""
    lines = []

    lines.append("## 大运流年")
    lines.append("")

    # 计算大运
    bazi = bazi_info.get("bazi", bazi_info)
    year_stem_idx = bazi.get("year", {}).get("stem_idx", 0)
    gender_str = "男" if gender == 1 else "女"

    # 出生时间戳（简化处理，使用默认值）
    birth_year = 2024  # 默认
    birth_month = 3
    birth_timestamp = time.mktime((birth_year, birth_month, 15, 10, 0, 0, 0, 0, 0))

    dayun_list = get_dayun_sequence(bazi_info, gender_str, birth_timestamp)

    # ===== 大运序列 =====
    lines.append("### 大运序列")
    lines.append("")

    if dayun_list:
        for i, dayun in enumerate(dayun_list[:8]):  # 只显示前8步大运
            start_age = dayun.get("start_age", 0)
            end_age = dayun.get("end_age", 0)
            ganzhi = dayun.get("ganzhi", "")
            direction = dayun.get("direction", "")

            # 获取大运概述
            summary = get_dayun_summary(dayun, bazi_info)
            # 简化摘要
            analysis = analyze_dayun(dayun.get("stem_idx", 0), dayun.get("branch_idx", 0), bazi_info)
            luck = analysis.get("luck", "")

            lines.append(f"{i+1}. **{start_age}-{end_age}岁**：{ganzhi} {direction} 【{luck}】")
    else:
        lines.append("*大运信息不可用*")

    lines.append("")

    # ===== 近5年流年 =====
    lines.append("### 近5年流年")
    lines.append("")

    current_year = 2026
    recent_liunian = get_recent_liunian(bazi_info, dayun_list, current_year, 5)

    if recent_liunian:
        for liunian in recent_liunian:
            year = liunian.get("year", "")
            ganzhi = liunian.get("ganzhi", "")
            luck = liunian.get("luck", "")
            factors = liunian.get("factors", [])
            factor_str = "；".join(factors[:2]) if factors else "无特殊"

            lines.append(f"- **{year}**（{ganzhi}）：【{luck}】{factor_str}")
    else:
        lines.append("*流年信息不可用*")

    return lines


def _analyze_dayun_simple(stem_idx: int, branch_idx: int, bazi_info: Dict[str, Any]) -> Dict[str, Any]:
    """简化的大运分析（不依赖完整 dayun_info）"""
    from dayun_liunian import analyze_dayun

    # 构造简化 dayun_info
    dayun_info = {
        "stem_idx": stem_idx,
        "branch_idx": branch_idx,
        "stem": HEAVENLY_STEMS[stem_idx] if 0 <= stem_idx < 10 else "?",
        "branch": EARTHLY_BRANCHES[branch_idx] if 0 <= branch_idx < 12 else "?",
    }
    return analyze_dayun(stem_idx, branch_idx, bazi_info)


def analyze_dayun(stem_idx: int, branch_idx: int, bazi_info: Dict[str, Any]) -> Dict[str, Any]:
    """公开的 analyze_dayun 函数（供外部调用）"""
    return _analyze_dayun_simple(stem_idx, branch_idx, bazi_info)


def format_dayun_summary(dayun_list: List[Dict[str, Any]]) -> str:
    """格式化大运摘要（供外部调用）"""
    lines = []
    for i, dayun in enumerate(dayun_list[:8]):
        start_age = dayun.get("start_age", 0)
        end_age = dayun.get("end_age", 0)
        ganzhi = dayun.get("ganzhi", "")
        direction = dayun.get("direction", "")
        lines.append(f"{i+1}. {start_age}-{end_age}岁：{ganzhi} {direction}")
    return "\n".join(lines)


def format_liunian_recent(recent_list: List[Dict[str, Any]]) -> str:
    """格式化近5年流年（供外部调用）"""
    lines = []
    for liunian in recent_list:
        year = liunian.get("year", "")
        ganzhi = liunian.get("ganzhi", "")
        luck = liunian.get("luck", "")
        factors = liunian.get("factors", [])
        factor_str = "；".join(factors[:2]) if factors else ""
        lines.append(f"- {year}（{ganzhi}）：【{luck}】{factor_str}")
    return "\n".join(lines)


def _format_name_section(
    bazi_info: Dict[str, Any],
    name_candidates: List[Dict[str, Any]],
    surname: str,
) -> List[str]:
    """格式化姓名分析 section"""
    lines = []

    lines.append("## 姓名分析")
    lines.append("")

    zodiac = bazi_info.get("zodiac", "")
    xiyongshen = bazi_info.get("xiyongshen", {})
    xiyong_list = xiyongshen.get("xiyongshen", [])

    # ===== 推荐候选名 =====
    lines.append("### 推荐候选名")
    lines.append("")

    if not name_candidates:
        lines.append("*未找到符合条件的名字*")
        return lines

    prefs = get_zodiac_preferences(zodiac) if zodiac else {}

    for i, rec in enumerate(name_candidates[:3], 1):
        full_name = rec.get("full_name", f"{surname}某")
        total_score = rec.get("total_score", 0)
        dim_scores = rec.get("dim_scores", {})

        # 五格信息
        wuge_details = rec.get("details", {}).get("五格", {}).get("wuge", {})
        if wuge_details:
            ren_ge = wuge_details.get("ren_ge", {})
            zong_ge = wuge_details.get("zong_ge", {})
            san_cai = wuge_details.get("san_cai", {})
            ren_num = ren_ge.get("number", "?")
            zong_num = zong_ge.get("number", "?")
            san_cai_config = san_cai.get("config", "?-?-?")
        else:
            ren_num = "?"
            zong_num = "?"
            san_cai_config = "?-?-?"

        lines.append(f"**{i}. {full_name}**（人格{ren_num}/总格{zong_num}/三才{san_cai_config}）")
        lines.append("")

        # 喜用神匹配
        xiyong_details = rec.get("details", {}).get("喜用神", {})
        matched = xiyong_details.get("matched", [])
        if matched:
            matched_str = "、".join([f"「{m['char']}」({m['wuxing']})" for m in matched])
            lines.append(f"  - 五行：喜用神「{'、'.join(xiyong_list)}」匹配 {matched_str}")
        else:
            lines.append(f"  - 五行：喜用神「{'、'.join(xiyong_list)}」无直接匹配字")

        # 生肖宜忌
        zodiac_details = rec.get("details", {}).get("生肖", {})
        zodiac_detail_list = zodiac_details.get("details", [])
        if zodiac_detail_list:
            lines.append(f"  - 生肖：{zodiac_detail_list[0] if zodiac_detail_list else ''}")
        else:
            lines.append(f"  - 生肖：未发现明显宜忌")

        # 寓意
        reasons = rec.get("reasons", [])
        if reasons:
            lines.append(f"  - 寓意：{reasons[0] if reasons else '名字寓意良好'}")

        lines.append("")

    # ===== 候选名详细评分表 =====
    lines.append("### 候选名详细评分")
    lines.append("")

    lines.append("| 姓名 | 总分 | 喜用神 | 生肖 | 十神 | 五格 | 三才 |")
    lines.append("|:---|:---:|:---:|:---:|:---:|:---:|:---:|")

    for rec in name_candidates[:5]:
        full_name = rec.get("full_name", "??")
        total_score = rec.get("total_score", 0)
        dim_scores = rec.get("dim_scores", {})

        xiyong_score = dim_scores.get("喜用神匹配", dim_scores.get("喜用神", 0))
        zodiac_score = dim_scores.get("生肖宜忌", dim_scores.get("生肖", 0))
        shishen_score = dim_scores.get("十神/长生", dim_scores.get("十神", 0))
        wuge_score = dim_scores.get("五格数理", dim_scores.get("五格", 0))

        wuge_details = rec.get("details", {}).get("五格", {}).get("wuge", {})
        san_cai_config = "?-?-?"
        if wuge_details:
            san_cai = wuge_details.get("san_cai", {})
            san_cai_config = san_cai.get("config", "?-?-?")

        lines.append(f"| {full_name} | **{total_score}** | {xiyong_score}/40 | {zodiac_score}/30 | {shishen_score}/30 | {wuge_score}/25 | {san_cai_config} |")

    return lines


def _format_suggestions(bazi_info: Dict[str, Any]) -> List[str]:
    """格式化命理建议 section"""
    lines = []

    lines.append("## 命理建议")
    lines.append("")

    zodiac = bazi_info.get("zodiac", "")
    xiyongshen = bazi_info.get("xiyongshen", {})
    xiyong_list = xiyongshen.get("xiyongshen", [])
    pattern = bazi_info.get("pattern", {})
    tiao_hou = bazi_info.get("tiao_hou", {})

    # ===== 职业方向 =====
    lines.append("### 职业方向")
    lines.append("")

    # 根据喜用神推断职业方向
    career_hints = []
    if "金" in xiyong_list:
        career_hints.append("金融、财务、法律、工程")
    if "水" in xiyong_list:
        career_hints.append("贸易、物流、航运、水利")
    if "木" in xiyong_list:
        career_hints.append("教育、文化、出版、林业")
    if "火" in xiyong_list:
        career_hints.append("能源、电器、IT、餐饮")
    if "土" in xiyong_list:
        career_hints.append("房地产、建筑、农业、矿产")

    if career_hints:
        lines.append(f"- 喜用神为「{'、'.join(xiyong_list)}」，适合领域：")
        for hint in career_hints[:3]:
            lines.append(f"  - {hint}")
    else:
        lines.append("- 建议结合个人兴趣和专长选择职业")

    # 格局相关的职业提示
    if pattern:
        pattern_name = pattern.get("pattern", "")
        if "官" in pattern_name or "杀" in pattern_name:
            lines.append("- 命带官杀，适合管理、行政类岗位")
        elif "财" in pattern_name:
            lines.append("- 命带财星，适合经营、投资类岗位")
        elif "印" in pattern_name:
            lines.append("- 命带印星，适合学术、研究类岗位")

    lines.append("")

    # ===== 幸运方位/颜色 =====
    lines.append("### 幸运方位与颜色")
    lines.append("")

    prefs = get_zodiac_preferences(zodiac) if zodiac else {}
    directions = prefs.get("directions", [])
    lucky_colors = prefs.get("lucky_colors", [])

    if directions:
        lines.append(f"- **吉祥方位**：{', '.join(directions)}")
    if lucky_colors:
        lines.append(f"- **幸运颜色**：{', '.join(lucky_colors)}")

    # 根据喜用神推荐方位和颜色
    elem_directions = {
        "木": ["东方", "东南"],
        "火": ["南方", "东南"],
        "土": ["东北", "西南"],
        "金": ["西方", "西北"],
        "水": ["北方", "西南"],
    }
    elem_colors = {
        "木": ["绿色", "青色"],
        "火": ["红色", "紫色"],
        "土": ["黄色", "棕色"],
        "金": ["白色", "金色"],
        "水": ["黑色", "蓝色"],
    }

    for elem in xiyong_list[:2]:
        if elem in elem_directions:
            lines.append(f"- 喜用「{elem}」助运方位：{', '.join(elem_directions[elem])}")
        if elem in elem_colors:
            lines.append(f"- 喜用「{elem}」助运颜色：{', '.join(elem_colors[elem])}")

    lines.append("")

    # ===== 注意事项 =====
    lines.append("### 注意事项")
    lines.append("")

    jishen_list = xiyongshen.get("jishen", [])
    if jishen_list:
        avoid_elems = "、".join(jishen_list)
        lines.append(f"- 忌神为「{avoid_elems}」，注意避免相关行业的过度投入")

    # 生肖注意事项
    if zodiac:
        avoid_chars = prefs.get("avoid_chars", [])
        if avoid_chars:
            avoid_str = "".join(avoid_chars[:5])
            lines.append(f"- 生肖「{zodiac}」用字宜避免偏旁：{avoid_str}等")

    # 调候注意事项
    if tiao_hou:
        principle = tiao_hou.get("原则", "")
        if principle:
            lines.append(f"- 调候提示：{principle[:40]}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本报告由本地八字引擎生成，仅供参考。精确喜用神判断建议使用专业八字API。*")

    return lines


# ============================================================
# 便捷入口函数
# ============================================================

def generate_full_report(
    surname: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: int = 1,
    name_count: int = 3,
) -> str:
    """
    一键生成完整八字分析报告

    Args:
        surname: 姓氏
        year, month, day, hour: 出生时间
        gender: 性别 (1=男, 0=女)
        name_count: 推荐名字数量

    Returns:
        Markdown 格式完整报告
    """
    # 导入名字生成器
    try:
        from name_generator import generate_name_recommendations
        result = generate_name_recommendations(
            surname=surname,
            birth_year=year,
            birth_month=month,
            birth_day=day,
            birth_hour=hour,
            gender=gender,
            use_local_engine=True,
            max_options=name_count,
        )
        bazi_info = result.get("bazi_info", {})
        name_candidates = result.get("recommendations", [])
    except Exception as e:
        # 如果名字生成失败，只生成八字分析
        bazi_info = full_bazi_analysis(year, month, day, hour)
        bazi_info["source"] = "local_engine"
        bazi_info["is_fallback"] = True
        name_candidates = []

    full_name = f"{surname}宝宝" if surname else "待输入"

    return format_full_report(
        bazi_info=bazi_info,
        name_candidates=name_candidates,
        gender=gender,
        surname=surname,
        full_name=full_name,
    )


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=== 报告格式化器测试 ===\n")

    # 测试1: 2024年3月15日10点
    print("【测试1】2024年3月15日10点 - 本地引擎")
    report = generate_full_report(
        surname="张",
        year=2024,
        month=3,
        day=15,
        hour=10,
        gender=1,
        name_count=3,
    )
    print(report[:2000])
    print("\n... (报告已截断) ...\n")

    # 测试2: 单独格式化各部分
    print("【测试2】单独格式化测试")
    bazi_info = full_bazi_analysis(2024, 3, 15, 10)
    bazi_info["source"] = "local_engine"

    print("\n--- 八字命盘 ---")
    print(format_bazi_table(bazi_info))

    print("\n--- 神煞一览 ---")
    print(format_shen_sha_list(bazi_info))
