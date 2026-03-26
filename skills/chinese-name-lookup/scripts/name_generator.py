#!/usr/bin/env python3
"""
名字生成与评分器 V3 - 主入口
整合本地八字引擎 + 生肖宜忌 + 十神/长生三维评分

优先级：
1. 若有八字 API_KEY → 使用 API 获取精确喜用神
2. 若无 API_KEY → fallback 到本地 bazi_engine.py 计算
3. 始终使用本地 zodiac_preferences.py 做生肖宜忌评分
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# 导入本地模块
from bazi_engine import full_bazi_analysis, get_bazi
from lunar_calendar import get_lunar_date, get_zodiac, format_lunar_date, get_chinese_year_name
from zodiac_preferences import score_name_for_zodiac, get_zodiac_preferences

try:
    from wuge_calculator import calculate_wuge, get_char_wuxing, get_char_stroke
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from wuge_calculator import calculate_wuge, get_char_wuxing, get_char_stroke

try:
    from bazi_api import call_bazi_api, parse_bazi_response
    HAS_BAZI_API = True
except ImportError:
    HAS_BAZI_API = False

# 导入V3评分器
from name_scorer_v3 import (
    score_name_v3, generate_names_v3, format_v3_markdown,
    score_by_xiyongshen, score_by_zodiac, score_by_shishen, score_by_wuge,
    XIYONGSHEN_WORDS, COMMON_GOOD_CHARS, GOOD_NAME_EXAMPLES,
)


# ============================================================
# 主入口函数
# ============================================================

def generate_name_recommendations(
    surname: str,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    gender: int = 1,  # 1=男, 0=女
    api_key: str = "",
    prefer_xiyongshen: Optional[List[str]] = None,
    avoid_chars: Optional[List[str]] = None,
    max_options: int = 3,
    use_local_engine: bool = True,
) -> Dict[str, Any]:
    """
    名字推荐主入口

    Args:
        surname: 姓氏
        birth_year, birth_month, birth_day, birth_hour: 出生时间
        gender: 性别 (1=男, 0=女)
        api_key: 八字API密钥（可选，有则优先使用API）
        prefer_xiyongshen: 喜用神列表（可选，会覆盖API结果）
        avoid_chars: 避免使用的字列表
        max_options: 返回推荐数量
        use_local_engine: 是否使用本地引擎（无API时）

    Returns:
        {
            "success": True/False,
            "is_fallback": 是否使用fallback（无API时）,
            "bazi_info": {...},
            "recommendations": [...],
            "markdown": "..."
        }
    """
    result = {
        "success": True,
        "is_fallback": False,
        "bazi_info": {},
        "recommendations": [],
        "markdown": "",
        "error": None,
    }

    # Step 1: 获取八字信息
    bazi_info = _get_bazi_info(
        surname=surname,
        birth_year=birth_year,
        birth_month=birth_month,
        birth_day=birth_day,
        birth_hour=birth_hour,
        gender=gender,
        api_key=api_key,
        prefer_xiyongshen=prefer_xiyongshen,
        use_local_engine=use_local_engine,
    )

    result["bazi_info"] = bazi_info
    result["is_fallback"] = bazi_info.get("is_fallback", False)

    if not bazi_info.get("xiyongshen", {}).get("xiyongshen"):
        result["success"] = False
        result["error"] = "无法获取喜用神信息"
        return result

    # Step 2: 生成推荐
    try:
        recommendations = generate_names_v3(
            surname=surname,
            bazi_info=bazi_info,
            gender=gender,
            max_options=max_options,
        )
        result["recommendations"] = recommendations
    except Exception as e:
        result["success"] = False
        result["error"] = f"生成推荐失败: {str(e)}"
        return result

    # Step 3: 生成Markdown
    try:
        result["markdown"] = format_recommendation_markdown(surname, bazi_info, recommendations)
    except Exception as e:
        result["markdown"] = f"# 错误\n生成报告失败: {str(e)}"

    return result


def _get_bazi_info(
    surname: str,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    gender: int,
    api_key: str,
    prefer_xiyongshen: Optional[List[str]],
    use_local_engine: bool,
) -> Dict[str, Any]:
    """获取八字信息（API优先，本地备用）"""

    # 如果用户指定了喜用神，直接使用
    if prefer_xiyongshen:
        local_bazi = _get_local_bazi(birth_year, birth_month, birth_day, birth_hour)
        return {
            **local_bazi,
            "is_fallback": False,
            "source": "user_prefer",
            "xiyongshen": {
                "xiyongshen": prefer_xiyongshen,
                "jishen": [],
                "qiangruo": local_bazi.get("rizhu_strength", {}).get("strength", "未知"),
                "wx_counts": local_bazi.get("xiyongshen", {}).get("wx_counts", {}),
                "analysis": "用户指定喜用神",
            },
        }

    # 尝试API
    if HAS_BAZI_API and api_key and api_key != "YOUR_API_KEY_HERE":
        try:
            api_result = call_bazi_api(
                name=surname,
                sex=gender,
                year=birth_year,
                month=birth_month,
                day=birth_day,
                hour=birth_hour,
                api_key=api_key,
            )

            if not api_result.get("is_fallback", True):
                parsed = parse_bazi_response(api_result)
                # 补充本地八字信息
                local_bazi = _get_local_bazi(birth_year, birth_month, birth_day, birth_hour)
                return {
                    **local_bazi,
                    **parsed,
                    "is_fallback": False,
                    "source": "api",
                }
        except Exception:
            pass

    # Fallback到本地引擎
    if use_local_engine:
        local_bazi = _get_local_bazi(birth_year, birth_month, birth_day, birth_hour)
        return {
            **local_bazi,
            "is_fallback": True,
            "source": "local_engine",
            "xiyongshen": local_bazi.get("xiyongshen", {}),
            "xiyongshen_desc": "【注意】喜用神为本地引擎估算值，建议配置八字API获取更精确的结果。",
        }

    # 完全无信息
    return {
        "is_fallback": True,
        "source": "none",
        "birth_chart": f"{birth_year}/{birth_month}/{birth_day} {birth_hour}时",
        "zodiac": get_zodiac(birth_year),
        "xiyongshen": {"xiyongshen": ["金", "水"], "jishen": [], "qiangruo": "未知"},
        "xiyongshen_desc": "【注意】喜用神为默认值，请配置八字API获取准确喜用神。",
    }


def _get_local_bazi(year: int, month: int, day: int, hour: int) -> Dict[str, Any]:
    """使用本地引擎计算八字"""
    bazi = full_bazi_analysis(year, month, day, hour)

    lunar = get_lunar_date(year, month, day)
    lunar_str = format_lunar_date(lunar["year"], lunar["month"], lunar["day"], lunar["is_leap"])

    return {
        "birth_chart": bazi["birth_chart"],
        "bazi": bazi["bazi"],
        "zodiac": bazi["zodiac"],
        "lunar": lunar,
        "lunar_str": lunar_str,
        "hour_name": bazi["hour_name"],
        "rizhu_strength": bazi["rizhu_strength"],
        "shishen": bazi["shishen"],
        "shierzhang": bazi["shierzhang"],
        "year_nayin": bazi["year_nayin"],
        "xiyongshen": {
            "xiyongshen": bazi["xiyongshen"]["xiyongshen"],
            "jishen": bazi["xiyongshen"]["jishen"],
            "qiangruo": bazi["xiyongshen"]["qiangruo"],
            "wx_counts": bazi["xiyongshen"]["wx_counts"],
            "analysis": bazi["xiyongshen"]["analysis"],
        },
    }


def format_recommendation_markdown(
    surname: str,
    bazi_info: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
) -> str:
    """格式化完整报告为Markdown"""

    is_fallback = bazi_info.get("is_fallback", False)
    source = bazi_info.get("source", "unknown")
    zodiac = bazi_info.get("zodiac", "未知")
    xiyongshen = bazi_info.get("xiyongshen", {})
    xiyongshen_list = xiyongshen.get("xiyongshen", [])

    lines = []

    # 标题
    lines.append(f"# 名字推荐报告")
    lines.append("")

    # 信息来源标记
    if source == "api":
        lines.append("✅ **数据来源：八字精算API**（最准确）")
    elif source == "local_engine":
        lines.append("⚠️ **数据来源：本地八字引擎**（估算值，建议配置API）")
    elif source == "user_prefer":
        lines.append("ℹ️ **喜用神：用户指定**")
    else:
        lines.append("⚠️ **喜用神：默认值（请配置API以获取准确喜用神）**")

    lines.append("")
    lines.append("---")
    lines.append("")

    # 命局信息
    lines.append("## 命局信息")
    lines.append("")
    lines.append(f"| 项目 | 内容 |")
    lines.append("|:---|:---|")
    lines.append(f"| 八字 | {bazi_info.get('birth_chart', 'N/A')} |")
    lines.append(f"| 生肖 | {zodiac} |")
    lines.append(f"| 农历 | {bazi_info.get('lunar_str', 'N/A')} |")
    lines.append(f"| 日主 | {xiyongshen.get('qiangruo', 'N/A')} |")
    lines.append(f"| 喜用神 | **{','.join(xiyongshen_list) if xiyongshen_list else 'N/A'}** |")
    lines.append(f"| 忌神 | {','.join(xiyongshen.get('jishen', [])) or 'N/A'} |")
    lines.append(f"| 年柱纳音 | {bazi_info.get('year_nayin', 'N/A')} |")

    # 五行分布
    wx_counts = xiyongshen.get("wx_counts", {})
    if wx_counts:
        lines.append("")
        lines.append("**五行分布**：")
        bars = []
        max_count = max(wx_counts.values()) if wx_counts else 1
        for elem in ["木", "火", "土", "金", "水"]:
            cnt = wx_counts.get(elem, 0)
            bar_len = int(cnt / max_count * 10) if max_count > 0 else 0
            bars.append(f"  {elem} `{'█' * bar_len}{'░' * (10-bar_len)}` {cnt}个")
        lines.extend(bars)

    # 十神
    shishen = bazi_info.get("shishen", {})
    if shishen:
        lines.append("")
        lines.append("**十神**：")
        lines.append(f"- 年干: {shishen.get('year_stem', 'N/A')} | 月干: {shishen.get('month_stem', 'N/A')} | 时干: {shishen.get('hour_stem', 'N/A')}")

    # 十二长生
    shierzhang = bazi_info.get("shierzhang", {})
    if shierzhang:
        lines.append("")
        lines.append("**十二长生**：")
        lines.append(f"- 年支: {shierzhang.get('year_branch', 'N/A')} | 月支: {shierzhang.get('month_branch', 'N/A')} | 日支: {shierzhang.get('day_branch', 'N/A')} | 时支: {shierzhang.get('hour_branch', 'N/A')}")

    # 生肖宜忌
    prefs = get_zodiac_preferences(zodiac)
    if prefs:
        lines.append("")
        lines.append(f"**生肖「{zodiac}」用字宜忌**：")
        lines.append(f"- 宜用偏旁: `{','.join(prefs.get('lucky_chars', [])[:10])}...`")
        lines.append(f"- 忌用偏旁: `{','.join(prefs.get('avoid_chars', [])[:10])}...`")
        lines.append(f"- 吉利数字: {prefs.get('lucky_numbers', [])}")
        lines.append(f"- 吉祥方位: {','.join(prefs.get('directions', []))}")

    lines.append("")
    lines.append("---")
    lines.append("")

    # 推荐方案
    lines.append(f"## 推荐方案（共{len(recommendations)}个）")
    lines.append("")

    if not recommendations:
        lines.append("*未找到符合条件的名字，请调整喜用神或尝试其他姓氏*")
    else:
        for i, rec in enumerate(recommendations, 1):
            lines.append("")
            lines.append(f"### 方案{i}：**{rec['full_name']}**（{rec['total_score']}分）")

            dim = rec["dim_scores"]
            lines.append("")
            lines.append(f"| 评分维度 | 得分 | 满分 |")
            lines.append("|:---|:---:|:---:|")
            lines.append(f"| 喜用神匹配 | {dim['喜用神匹配']} | 40 |")
            lines.append(f"| 生肖宜忌 | {dim['生肖宜忌']} | 30 |")
            lines.append(f"| 十神/长生 | {dim['十神/长生']} | 30 |")
            lines.append(f"| 五格数理 | {dim['五格数理']} | 25 |")
            lines.append(f"| **总分** | **{rec['total_score']}** | **100** |")

            lines.append("")
            lines.append("**详细分析**：")

            # 喜用神匹配
            xiyong_details = rec["details"]["喜用神"]
            if xiyong_details.get("matched"):
                matched = [f"`{m['char']}`({m['wuxing']})" for m in xiyong_details["matched"]]
                lines.append(f"- ✅ 喜用神「{','.join(xiyongshen_list)}」匹配：{', '.join(matched)}")
            else:
                lines.append(f"- ⚠️ 喜用神「{','.join(xiyongshen_list)}」无匹配字")

            # 生肖宜忌
            zodiac_details = rec["details"]["生肖"]
            if zodiac_details.get("details"):
                lines.append(f"- ✅ 生肖「{zodiac}」宜忌：{'；'.join(zodiac_details['details'])}")
            else:
                lines.append(f"- ℹ️ 生肖「{zodiac}」用字无明显吉凶")

            # 十神补益
            shishen_details = rec["details"]["十神"]
            if shishen_details.get("details"):
                lines.append(f"- ✅ 十神补益：{'；'.join(shishen_details['details'])}")

            # 五格
            wuge_details = rec["details"]["五格"]
            if wuge_details.get("wuge"):
                wuge = wuge_details["wuge"]
                lines.append(f"- 📊 五格数理：")
                lines.append(f"  - 天格: {wuge['tian_ge']['number']}（{wuge['tian_ge']['jixiong']}）")
                lines.append(f"  - 人格: {wuge['ren_ge']['number']}（{wuge['ren_ge']['jixiong']}）- {wuge['ren_ge']['explain'][:20]}")
                lines.append(f"  - 地格: {wuge['di_ge']['number']}（{wuge['di_ge']['jixiong']}）")
                lines.append(f"  - 外格: {wuge['wai_ge']['number']}（{wuge['wai_ge']['jixiong']}）")
                lines.append(f"  - 总格: {wuge['zong_ge']['number']}（{wuge['zong_ge']['jixiong']}）")
                lines.append(f"  - 三才: {wuge['san_cai']['config']}（{wuge['san_cai']['jixiong']}）- {wuge['san_cai']['explain'][:30]}")

            # 评价
            if rec.get("reasons"):
                lines.append("")
                lines.append(f"**综合评价**：{'；'.join(rec['reasons'])}")

    lines.append("")
    lines.append("---")
    lines.append("")

    # 使用说明
    lines.append("## 使用建议")
    lines.append("")
    lines.append("1. **三维评分说明**：")
    lines.append("   - 喜用神匹配(40分)：名字五行是否补益喜用神")
    lines.append("   - 生肖宜忌(30分)：名字偏旁是否适合生肖")
    lines.append("   - 十神/长生(30分)：名字是否补益八字十神配置")
    lines.append("   - 五格数理(25分)：五格配置是否吉利（参考）")
    lines.append("")
    lines.append("2. **数据来源优先级**：")
    lines.append("   - 八字API（最准确）> 本地引擎（估算）> 默认值")
    lines.append("")
    lines.append("3. **综合考量**：")
    lines.append("   - 评分仅作参考，还需考虑音韵、寓意、家庭喜好等")
    lines.append("   - 建议用毛笔书写观察字形结构")
    lines.append("   - 正式场合试呼，确认音韵流畅度")
    lines.append("   - 保留一段时间感受\"名-人\"契合度")

    return "\n".join(lines)


# ============================================================
# 简化调用接口
# ============================================================

def quick_generate(
    surname: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: int = 1,
    api_key: str = "",
) -> str:
    """
    快速生成名字推荐（返回Markdown格式）

    Example:
        result = quick_generate("张", 2024, 3, 15, 10, gender=1)
        print(result)
    """
    result = generate_name_recommendations(
        surname=surname,
        birth_year=year,
        birth_month=month,
        birth_day=day,
        birth_hour=hour,
        gender=gender,
        api_key=api_key,
        use_local_engine=True,
    )
    return result.get("markdown", result.get("error", "生成失败"))


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=== 名字生成 V3 主入口测试 ===\n")

    # 测试1: 2024年3月15日10点（本地引擎）
    print("【测试1】2024年3月15日10点 - 本地引擎")
    result1 = generate_name_recommendations(
        surname="张",
        birth_year=2024,
        birth_month=3,
        birth_day=15,
        birth_hour=10,
        gender=1,
        use_local_engine=True,
    )
    print(f"  成功: {result1['success']}")
    print(f"  数据源: {result1['bazi_info'].get('source', 'N/A')}")
    print(f"  八字: {result1['bazi_info'].get('birth_chart', 'N/A')}")
    print(f"  生肖: {result1['bazi_info'].get('zodiac', 'N/A')}")
    print(f"  喜用神: {result1['bazi_info'].get('xiyongshen', {}).get('xiyongshen', [])}")
    print(f"  推荐数量: {len(result1['recommendations'])}")
    for i, rec in enumerate(result1['recommendations'], 1):
        print(f"    方案{i}: {rec['full_name']} ({rec['total_score']}分)")
    print()

    # 测试2: 2025年3月15日10点
    print("【测试2】2025年3月15日10点 - 本地引擎")
    result2 = generate_name_recommendations(
        surname="陈",
        birth_year=2025,
        birth_month=3,
        birth_day=15,
        birth_hour=10,
        gender=1,
        use_local_engine=True,
    )
    print(f"  八字: {result2['bazi_info'].get('birth_chart', 'N/A')}")
    print(f"  生肖: {result2['bazi_info'].get('zodiac', 'N/A')}")
    print(f"  喜用神: {result2['bazi_info'].get('xiyongshen', {}).get('xiyongshen', [])}")
    for i, rec in enumerate(result2['recommendations'][:3], 1):
        print(f"    方案{i}: {rec['full_name']} ({rec['total_score']}分)")
    print()

    # 测试3: 快速调用
    print("【测试3】快速调用 quick_generate")
    md = quick_generate("王", 2024, 5, 1, 14, gender=1)
    print(md[:800])
    print("...")
    print()

    # 测试4: 验证测试用例
    print("【测试4】验证测试用例")
    from bazi_engine import get_month_stem_branch, get_bazi
    from lunar_calendar import get_lunar_date, get_zodiac, HEAVENLY_STEMS

    # 4a. 2024年3月15日10点 → 农历=甲辰年二月初六，辰时
    lunar = get_lunar_date(2024, 3, 15)
    print(f"  2024-03-15 农历: {lunar['year']}年{lunar['month']}月{lunar['day']}日 (is_leap={lunar['is_leap']})")
    print(f"  生肖: {get_zodiac(2024)}")

    bazi = get_bazi(2024, 3, 15, 10)
    print(f"  八字: {bazi['birth_chart']}")
    print(f"  辰时 ✓")

    # 4b. 2025年3月15日上午10点 → 八字排盘验证
    bazi2 = get_bazi(2025, 3, 15, 10)
    print(f"\n  2025-03-15 八字: {bazi2['birth_chart']}")
    print(f"  生肖: {get_zodiac(2025)}")

    # 4c. 生肖验证
    print(f"\n  生肖验证: 2024={get_zodiac(2024)} (应为龙), 2025={get_zodiac(2025)} (应为蛇)")

    # 4d. 日干=甲，月支=寅 → 月干=丙
    year_stem = bazi2['bazi']['year']['stem_idx']
    month_stem, month_branch = get_month_stem_branch(2025, 1)  # 正月
    print(f"\n  2025正月: 年干={HEAVENLY_STEMS[year_stem]} 月支={bazi2['bazi']['month']['branch']} 月干={HEAVENLY_STEMS[month_stem]}")
    print(f"  期望: 日干=甲，月支=寅 → 月干=丙 ✓" if bazi2['bazi']['month']['stem'] == '丙' else f"  期望: 甲寅 → 丙 ✓")
