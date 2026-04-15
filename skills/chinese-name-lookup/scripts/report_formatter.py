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
    get_dayun_sequence, get_dayun_with_exact_age, get_dayun_summary,
    get_recent_liunian, analyze_liunian_by_year, full_dayun_analysis,
    is_shun, is_yang_stem,
)
from shen_sha import get_shen_sha_summary, get_tianyi_guiren, get_wenchang, get_yima, get_huagai, get_taohua
from marriage_fate_classifier import classify_female_marriage_fate
from shensha_quality import assess_all_shensha
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

    # ===== 女命婚姻格局（P2-a）=====
    if gender == 0:  # 女命
        lines.extend(_format_female_marriage_section(bazi_info))
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

    # 判断主推方法
    primary_method_info = bazi_info.get("primary_method", {})
    primary = primary_method_info.get("primary", "千里命稿")
    secondary = primary_method_info.get("secondary", "滴天髓")
    pm_analysis = primary_method_info.get("analysis", "")
    pm_reasons = primary_method_info.get("reasons", [])

    # 日主强弱
    rizhu_strength = bazi_info.get("rizhu_strength", {})
    strength = rizhu_strength.get("strength", qiangruo)
    day_stem = rizhu_strength.get("day_stem", "")
    day_element = rizhu_strength.get("day_element", "")

    # 根据主推方法决定显示顺序
    if primary == "千里命稿":
        # 主推千里命稿，参考滴天髓
        lines.append(f"**【主推】千里命稿法**（适合常规命盘）")
        v2_score = rizhu_strength.get("score", None)
        v2_breakdown = rizhu_strength.get("breakdown", None)
        if v2_score is not None:
            lines.append(f"- **日主**：{day_stem}{day_element}，**{strength}**（{v2_score}/100）")
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
            lines.append(f"  - {pm_analysis}")
        lines.append("")
        lines.append(f"**【参考】滴天髓法**（适合特殊命盘）")
        rizhu_by_count = bazi_info.get("rizhu_by_count", None)
        if rizhu_by_count:
            wx_counts = rizhu_by_count.get("wx_counts", {})
            lines.append(f"- 日主{day_element}，{rizhu_by_count.get('strength')}（比例{rizhu_by_count.get('score_ratio')}）")
            lines.append(f"  - 五行：木{wx_counts.get('木',0)} 火{wx_counts.get('火',0)} 土{wx_counts.get('土',0)} 金{wx_counts.get('金',0)} 水{wx_counts.get('水',0)}")
            lines.append(f"  - 喜用：{'、'.join(rizhu_by_count.get('xiyongshen_by_count',[]))}，忌：{'、'.join(rizhu_by_count.get('jishen_by_count',[]))}")
            lines.append(f"  - {rizhu_by_count.get('analysis', '')}")
    else:
        # 主推滴天髓，参考千里命稿
        lines.append(f"**【主推】滴天髓法**（适合特殊命盘）")
        rizhu_by_count = bazi_info.get("rizhu_by_count", None)
        if rizhu_by_count:
            wx_counts = rizhu_by_count.get("wx_counts", {})
            lines.append(f"- 日主{day_element}，{rizhu_by_count.get('strength')}（比例{rizhu_by_count.get('score_ratio')}）")
            lines.append(f"  - 五行：木{wx_counts.get('木',0)} 火{wx_counts.get('火',0)} 土{wx_counts.get('土',0)} 金{wx_counts.get('金',0)} 水{wx_counts.get('水',0)}")
            lines.append(f"  - 喜用：{'、'.join(rizhu_by_count.get('xiyongshen_by_count',[]))}，忌：{'、'.join(rizhu_by_count.get('jishen_by_count',[]))}")
            lines.append(f"  - {rizhu_by_count.get('analysis', '')}")
        lines.append("")
        lines.append(f"**【参考】千里命稿法**（适合常规命盘）")
        v2_score = rizhu_strength.get("score", None)
        if v2_score is not None:
            lines.append(f"- **日主**：{day_stem}{day_element}，**{strength}**（{v2_score}/100）")
            lines.append(f"  - {pm_analysis}")

    # 特殊命盘原因
    if pm_reasons:
        lines.append(f"- 特殊命盘原因：{'；'.join(pm_reasons)}")

    lines.append("")

    # 喜用神/忌神（根据主推方法 + 从格翻转）
    con_pattern = primary_method_info.get("con_pattern")
    is_con = con_pattern.get("is_con", False) if con_pattern else False

    if is_con and con_pattern:
        # 从格喜忌翻转
        xiyong_str = "、".join(con_pattern.get("xiyongshen_flip", [])) if con_pattern.get("xiyongshen_flip") else "待定"
        jishen_str = "、".join(con_pattern.get("jishen_flip", [])) if con_pattern.get("jishen_flip") else "待定"
        con_reason = con_pattern.get("reason", "")
        lines.append(f"- **用神**（从格翻转）：**{xiyong_str}**")
        lines.append(f"  - {con_reason}")
        lines.append(f"- **忌神**：{jishen_str}")
    elif primary == "千里命稿":
        xiyong_str = "、".join(xiyong_list) if xiyong_list else "待定"
        jishen_str = "、".join(jishen_list) if jishen_list else "待定"
        lines.append(f"- **用神**（{primary}）：**{xiyong_str}**")
        lines.append(f"- **忌神**：{jishen_str}")
    else:
        rc = bazi_info.get("rizhu_by_count", {})
        xiyong_str = "、".join(rc.get("xiyongshen_by_count", [])) if rc.get("xiyongshen_by_count") else "待定"
        jishen_str = "、".join(rc.get("jishen_by_count", [])) if rc.get("jishen_by_count") else "待定"
        lines.append(f"- **用神**（{primary}）：**{xiyong_str}**")
        lines.append(f"- **忌神**：{jishen_str}")
    lines.append("")

    # 五行分布
    wx_counts = xiyongshen.get("wx_counts", {})
    # --- 两法喜用神冲突检测 ---
    # v2_xs = 主推方法 result, v1_xs = 参考方法 result
    # 标签根据实际主推方法动态切换
    v2_xs = xiyongshen.get("xiyongshen", [])
    v1_xs = xiyongshen.get("_v1", {}).get("xiyongshen", [])
    if v2_xs and v1_xs and set(v2_xs) != set(v1_xs):
        primary_label = "千里命稿法" if primary == "千里命稿" else "滴天髓法"
        secondary_label = "滴天髓法" if primary == "千里命稿" else "千里命稿法"
        overlap = set(v2_xs) & set(v1_xs)
        if overlap:
            lines.append("⚠️ **两法喜用神存在分歧**：")
            lines.append(f"  - {primary_label}（主推）：**{'、'.join(v2_xs)}**")
            lines.append(f"  - {secondary_label}（参考）：**{'、'.join(v1_xs)}**")
            lines.append(f"  - 重叠（两法共识）：{'、'.join(overlap)}")
            lines.append(f"  - 结论：以{primary_label}为准（{primary_label}适合此命盘类型），参考方法仅作对比")

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

    # 格局四等（真/清/浊/破）
    try:
        from pattern_method import evaluate_pattern_class
        pattern_result_for_class = {
            "pattern_info": pattern,
            "cheng_info": pattern_cheng,
        }
        pattern_class_result = evaluate_pattern_class(bazi_info.get("bazi", {}), pattern_result_for_class)
        if pattern_class_result:
            pc = pattern_class_result
            lines.append(f"- **格局等级**：{pc['level']}")
            if pc.get("reasons"):
                for r in pc["reasons"]:
                    lines.append(f"  - {r}")
    except Exception:
        pass  # 格局四等评定失败不影响报告生成

    # 喜用神/忌神 + 调候调试信息
    # 读取 V2 _debug 信息（藏在 xiyongshen._debug 里）
    xiyong_v2 = bazi_info.get("xiyongshen", {})
    xiyong_v2_debug = xiyong_v2.get("_debug", {})
    huanre_zagan = xiyong_v2.get("huanre_zagan", {})
    tongguan = xiyong_v2.get("tongguan", {})
    tiao_hou_reason = xiyong_v2_debug.get("tiao_hou_reason", "")
    priority_info = xiyong_v2_debug.get("priority_info", {})
    merge_reason = xiyong_v2_debug.get("merge_reason", "")
    tiao_hou_xiyong = xiyong_v2_debug.get("tiao_hou_xiyong", [])
    fuyi_xiyong = xiyong_v2_debug.get("fuyi_xiyong", [])

    # 寒热燥湿判定
    if huanre_zagan:
        huanre_level = huanre_zagan.get("level", "未知")
        huanre_suggestion = huanre_zagan.get("suggestion", "")
        lines.append(f"- **寒热燥湿**：【{huanre_level}】")
        lines.append(f"  - 火气:{huanre_zagan.get('火热',0)}个，寒气:{huanre_zagan.get('水寒',0)}个，燥:{huanre_zagan.get('燥',0)}个，湿:{huanre_zagan.get('湿',0)}个")
        if huanre_suggestion:
            lines.append(f"  - 建议：{huanre_suggestion}")

    # 四大用神体系
    if priority_info or merge_reason:
        analysis_method = xiyong_v2.get("method", "v2_local")
        tiao_hou_priority = priority_info.get("tiao_hou_priority", False)
        priority_reason = priority_info.get("reason", "")
        priority_reason_first = priority_reason.split("；")[0] if priority_reason else ""
        tongguan_indicator = "是" if tongguan.get("needs_tongguan", False) else "否"
        tongguan_suggestion = tongguan.get("suggestion", "") if tongguan.get("needs_tongguan", False) else ""

        lines.append(f"- **用神体系**：【格局法用神】")
        if priority_reason_first:
            lines.append(f"  - 调候是否优先：{'是' if tiao_hou_priority else '否'}（{priority_reason_first}）")
        else:
            lines.append(f"  - 调候是否优先：{'是' if tiao_hou_priority else '否'}")
        if tiao_hou_xiyong:
            lines.append(f"  - 调候用神：{'、'.join(tiao_hou_xiyong) if tiao_hou_xiyong else '无'}")
        if fuyi_xiyong:
            lines.append(f"  - 扶抑用神：{'、'.join(fuyi_xiyong) if fuyi_xiyong else '无'}")
        final_xs = xiyong_v2.get("xiyongshen", xiyong_list)
        lines.append(f"  - 融合结果：{'、'.join(final_xs) if final_xs else '待定'}（{merge_reason[:50]}...）" if len(merge_reason) > 50 else f"  - 融合结果：{'、'.join(final_xs) if final_xs else '待定'}（{merge_reason}）")
        if tongguan.get("needs_tongguan", False):
            lines.append(f"  - 通关用神：{tongguan_suggestion}（需通关冲突：{'、'.join(tongguan.get('conflict',[]))}）")


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
        # 获取神煞质量评估
        if 'day_stem_idx' not in bazi_info:
            bazi_info['day_stem_idx'] = bazi_info['bazi']['day']['stem_idx']
        quality_list = assess_all_shensha(bazi_info)
        # 构建质量查找表：{shensha_name: {branch: quality_info}}
        quality_map: Dict[str, Dict[str, Dict]] = {}
        for q in quality_list:
            ss_name = q.get("神煞", "")
            if ss_name not in quality_map:
                quality_map[ss_name] = {}
            branch = q.get("地支", "")
            quality_map[ss_name][branch] = q

        items = []
        for name in ["天乙贵人", "文昌", "驿马", "华盖", "桃花"]:
            data = p0.get(name, {})
            desc = data.get("description", "")
            if desc:
                # 为每个地支标注质量
                parts = desc.replace('落在', ' ').replace('、', ' ').replace('在', ' ').split()
                branches = [p for p in parts if p in EARTHLY_BRANCHES]
                annotated = []
                for b in branches:
                    q_info = quality_map.get(name, {}).get(b, {})
                    grade = q_info.get("质量评级", "")
                    notes = q_info.get("综合评估", "").rstrip("。")
                    if grade == "强力":
                        suffix = "★"
                    elif grade == "有效":
                        suffix = "★★★"
                    elif grade == "弱效":
                        suffix = "★★"
                    elif grade == "无效":
                        suffix = "✗"
                    else:
                        suffix = ""
                    # 质量注释仅用于debug inline 不展示完整说明
                    annotated.append(f"{b}（{grade}{suffix}）" if suffix else b)
                items.append(f"- **{name}**：{' '.join(annotated)}")
            else:
                items.append(f"- **{name}**：无")

        if items:
            lines.append("### P0 主要神煞")
            lines.append("")
            lines.extend(items)
            lines.append("")
            lines.append("> 质量评级说明：★=强力（得令无损害） ★★★=有效 ★★=弱效（失令或被刑冲） ✗=无效（落空亡或死绝）")
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
            # 不加空行，让 format_full_report 的统一分隔处理

        # 新增 P1 神煞（太极贵人、咸池、绞煞、十恶大败、元辰、大耗）
        new_p1_items = []
        for name in ["太极贵人", "咸池", "绞煞", "十恶大败", "元辰", "大耗"]:
            data = p1.get(name, {})
            desc = data.get("description", "")
            if desc:
                new_p1_items.append(f"- **{name}**：{desc}")

        if new_p1_items:
            lines.append("### P1 其他神煞")
            lines.append("")
            lines.extend(new_p1_items)
            # 不加空行，让 format_full_report 的统一分隔处理

    # ===== 胎元神煞 =====
    taiyuan = shen_sha.get("胎元", {})
    if taiyuan:
        lines.append("### 胎元神煞")
        lines.append("")
        desc = taiyuan.get("description", "")
        if desc:
            lines.append(f"- **{taiyuan.get('taiyuan_stem', '')}{taiyuan.get('taiyuan_branch', '')}**：{desc}")

    # ===== 命宫神煞 =====
    minggong = shen_sha.get("命宫", {})
    if minggong:
        lines.append("### 命宫神煞")
        lines.append("")
        desc = minggong.get("description", "")
        if desc:
            lines.append(f"- **{minggong.get('minggong_stem', '')}{minggong.get('minggong_branch', '')}**：{desc}")

    # ===== P2 次要神煞 =====
    p2 = shen_sha.get("P2", {})
    if p2:
        items2 = []
        for name, data in p2.items():
            desc = data.get("description", "") if isinstance(data, dict) else ""
            if desc:
                items2.append(f"- **{name}**：{desc}")
        if items2:
            lines.append("### P2 次要神煞")
            lines.append("")
            lines.extend(items2)

    return lines


def _format_female_marriage_section(bazi_info: Dict[str, Any]) -> List[str]:
    """格式化女命婚姻格局 section（P2-a）"""
    lines = []
    lines.append("## 女命婚姻格局")
    lines.append("")

    if 'day_stem_idx' not in bazi_info:
        bazi_info['day_stem_idx'] = bazi_info['bazi']['day']['stem_idx']
    result = classify_female_marriage_fate(bazi_info)
    category = result.get("category", "未知")
    score = result.get("score", 0)
    matching = result.get("matching_patterns", [])
    violating = result.get("violating_patterns", [])
    analysis = result.get("analysis", "")

    # 评分条
    bar_len = int(score / 10)
    bar = "█" * bar_len + "░" * (10 - bar_len)
    lines.append(f"**评分**：{bar} {score}/100")
    lines.append("")

    # 格局类别
    if category == "富贵":
        lines.append(f"🏆 **格局：富贵**")
    elif category == "中上":
        lines.append(f"✨ **格局：中上**")
    elif category == "贫贱":
        lines.append(f"⚠️ **格局：贫贱**")
    else:
        lines.append(f"➖ **格局：平常**")
    lines.append("")

    # 富贵因素
    if matching:
        lines.append("**【富贵因素】**")
        for p in matching:
            lines.append(f"- {p}")
        lines.append("")

    # 不利因素
    if violating:
        lines.append("**【不利因素】**")
        for p in violating:
            lines.append(f"- {p}")
        lines.append("")

    # 分析说明
    if analysis:
        lines.append(f"*{analysis}*")

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

    # 从bazi_info获取出生年月（农历）
    lunar = bazi_info.get("lunar", {})
    birth_year = lunar.get("year", 2024)
    birth_month = lunar.get("month", 1)
    birth_timestamp = time.mktime((birth_year, birth_month, 15, 10, 0, 0, 0, 0, 0))

    # 使用精确起始年龄的大运计算（含十二长生轮转）
    dayun_list = get_dayun_with_exact_age(bazi_info, gender_str, birth_year, birth_month)

    # ===== 大运序列 =====
    lines.append("### 大运序列")
    lines.append("")

    if dayun_list:
        for i, dayun in enumerate(dayun_list[:8]):  # 只显示前8步大运
            start_age = dayun.get("start_age", i * 10)
            end_age = dayun.get("end_age", i * 10 + 9)
            ganzhi = dayun.get("ganzhi", "")
            direction = dayun.get("direction", "")
            changsheng = dayun.get("changsheng", "")

            # 获取大运概述
            analysis = analyze_dayun(dayun.get("stem_idx", 0), dayun.get("branch_idx", 0), bazi_info)
            luck = analysis.get("luck", "")

            cs_part = f"（{changsheng}）" if changsheng else ""
            lines.append(f"{i+1}. **{start_age}-{end_age}岁**：{ganzhi} {direction} {cs_part}【{luck}】")
    else:
        lines.append("*大运信息不可用*")

    lines.append("")

    # ===== 近5年流年 =====
    lines.append("### 近5年流年")
    lines.append("")

    lunar = bazi_info.get("lunar", {})
    birth_year = lunar.get("year", 2026)
    current_year = 2026
    recent_liunian = get_recent_liunian(bazi_info, dayun_list, current_year, 5, birth_year)

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
