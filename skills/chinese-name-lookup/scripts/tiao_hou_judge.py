# -*- coding: utf-8 -*-
"""
调候优先级判定器
判断调候用神与扶抑用神冲突时，谁应该优先

核心逻辑：
1. 调候为急：命局寒热严重失调时，调候优先
2. 扶抑为急：日主过旺/过弱需要紧急平衡时，扶抑优先

数据来源：《穷通宝鉴》、《滴天髓》等经典
"""

from typing import Dict, List, Any, Tuple

# ============================================================
# 月令寒热属性表
# ============================================================

YUEZHI_HANRE: Dict[str, str] = {
    "寅": "微寒",
    "卯": "温",
    "辰": "寒湿",
    "巳": "微热",
    "午": "热",
    "未": "燥热",
    "申": "凉",
    "酉": "凉燥",
    "戌": "燥热",
    "亥": "寒",
    "子": "寒",
    "丑": "寒湿",
}

# 寒热强度分级
HAN_RE_LEVEL: Dict[str, int] = {
    "寒": 3,  # 最寒
    "寒湿": 3,
    "微寒": 2,
    "凉": 1,
    "凉燥": 1,
    "温": 0,  # 中性
    "微热": 1,
    "燥热": 2,
    "热": 3,  # 最热
}

# 日主寒热属性（天干对应的寒热本性）
STEM_HAN_RE: Dict[str, str] = {
    "甲": "温",   # 木性温和
    "乙": "温",
    "丙": "热",   # 火性热
    "丁": "热",
    "戊": "燥",   # 土性燥
    "己": "燥",
    "庚": "凉",   # 金性凉
    "辛": "凉",
    "壬": "寒",   # 水性寒
    "癸": "寒",
}


def get_han_re_for_month(yue_zhi: str) -> str:
    """
    获取月令的寒热属性
    
    Args:
        yue_zhi: 月令地支（寅、卯、辰、巳、午、未、申、酉、戌、亥、子、丑）
    
    Returns:
        寒热属性字符串
    """
    return YUEZHI_HANRE.get(yue_zhi, "温")


def get_han_re_level(yue_zhi: str) -> int:
    """
    获取月令寒热强度等级（-3到3，负数为寒，正数为热）
    
    Args:
        yue_zhi: 月令地支
    
    Returns:
        寒热强度等级
    """
    han_re = get_han_re_for_month(yue_zhi)
    return HAN_RE_LEVEL.get(han_re, 0)


def is_tiao_hou_urgent(
    yue_zhi: str,
    month_stem: str,
    rizhu: str,
    rizhu_strength: str,
) -> Tuple[bool, str]:
    """
    判断调候是否紧急（为急）

    规则（简化版，基于穷通宝鉴）：
    - 亥子丑月 + 日主为水木 → 寒气重，调候为急
    - 巳午未月 + 日主为火土 → 燥气重，调候为急
    - 申酉戌月 + 日主为金 → 凉燥，调候为急
    - 寅卯辰月 + 日主为木 → 温和，调候不急

    更精细的判断需要考虑：
    1. 月令寒热强度
    2. 日主本身的寒热属性
    3. 日主强弱（过旺/过弱时扶抑优先）

    Args:
        yue_zhi: 月令地支
        month_stem: 月干
        rizhu: 日主天干
        rizhu_strength: 日主强弱（"弱"、"中和"、"强"或"过弱"、"过强"）

    Returns:
        (是否紧急, 原因说明)
    """
    han_re = get_han_re_for_month(yue_zhi)
    han_re_lv = get_han_re_level(yue_zhi)
    rizhu_han_re = STEM_HAN_RE.get(rizhu, "温")

    # 极端寒热情况：调候必定为急
    if han_re in ["寒", "寒湿"] and rizhu in ["壬", "癸", "甲", "乙"]:
        return True, f"月令{han_re}({yue_zhi})，日主{rizhu}({rizhu_han_re})性寒，调候为急"
    if han_re == "热" and rizhu in ["丙", "丁", "戊", "己"]:
        return True, f"月令{han_re}({yue_zhi})，日主{rizhu}({rizhu_han_re})性热，调候为急"
    if han_re == "燥热" and rizhu in ["丙", "丁", "戊", "己", "辛"]:
        return True, f"月令{han_re}({yue_zhi})，燥气过重，调候为急"

    # 日主过弱/过强时：扶抑优先，调候让位
    if rizhu_strength in ["过弱", "过强"]:
        return False, f"日主{rizhu_strength}，扶抑为急，调候次之"

    # 日主偏寒/偏热 + 月令寒热明显：调候优先
    if han_re_lv >= 2:  # 寒热较重
        # 日主本性寒热与月令一致时，调候更急
        if (han_re_lv > 0 and rizhu_han_re in ["寒", "热", "燥"]) or \
           (han_re_lv < 0 and rizhu_han_re in ["寒"]):
            return True, f"月令{han_re}({yue_zhi})寒热明显，日主{rizhu}({rizhu_han_re})偏寒热，调候优先"

    # 一般情况：扶抑优先
    return False, f"月令{han_re}({yue_zhi})寒热基本平衡，扶抑用神为主"


def judge_tiao_hou_priority(
    bazi: Dict[str, Any],
    rizhu_strength: Dict[str, Any],
    tiao_hou: Dict[str, Any],
) -> Dict[str, Any]:
    """
    判断调候是否应该优先于扶抑

    综合考虑：
    1. 月令寒热属性和强度
    2. 日主本身的寒热属性
    3. 日主强弱状态
    4. 调候用神与扶抑用神是否冲突

    Args:
        bazi: 八字完整分析结果
        rizhu_strength: 日主强弱分析结果 {"strength": str, "score": int, ...}
        tiao_hou: 调候分析结果 {"喜用": [...], "忌避": [...], ...}

    Returns:
        {
            "tiao_hou_priority": bool,       # True=调候优先
            "reason": str,                    # 判断原因
            "conflict_elements": list,        # 冲突的元素
            "urgency_level": int,             # 紧急程度 0-10
            "resolution": str,               # 解决建议
        }
    """
    # 提取关键信息
    bazi_detail = bazi.get("bazi", {})
    day_stem = bazi_detail.get("day", {}).get("stem", "")
    month_branch = bazi_detail.get("month", {}).get("branch", "")
    month_stem = bazi_detail.get("month", {}).get("stem", "")

    strength_str = rizhu_strength.get("strength", "中和")
    strength_score = rizhu_strength.get("score", 50)

    tiao_hou_xiyong = tiao_hou.get("喜用", [])
    fuyi_xiyong = bazi.get("xiyongshen", {}).get("xiyongshen", [])

    # 判断调候是否紧急
    is_urgent, urgency_reason = is_tiao_hou_urgent(
        month_branch, month_stem, day_stem, strength_str
    )

    # 分析冲突
    conflict_info = analyze_conflict(tiao_hou_xiyong, fuyi_xiyong)

    # 综合判断
    tiao_hou_priority = is_urgent or conflict_info["conflict_degree"] == "severe"

    # 计算紧急程度
    urgency_level = 0
    if is_urgent:
        urgency_level += 5
    if conflict_info["conflict_degree"] == "severe":
        urgency_level += 4
    elif conflict_info["conflict_degree"] == "moderate":
        urgency_level += 2
    urgency_level = min(urgency_level, 10)

    # 生成解决建议
    if tiao_hou_priority:
        resolution = f"调候优先：名字应优先满足{tiao_hou_xiyong}，扶抑用神{fuyi_xiyong}让位或降低权重"
    else:
        resolution = f"扶抑优先：名字应优先满足{fuyi_xiyong}，调候仅作参考"

    if conflict_info["conflict_degree"] == "severe":
        resolution += "（冲突严重，需权衡取舍）"
    elif conflict_info["overlap"] > 0:
        resolution += f"（部分重叠：{conflict_info['overlap_elements']}可兼顾）"

    return {
        "tiao_hou_priority": tiao_hou_priority,
        "reason": f"{urgency_reason}；调候用神={tiao_hou_xiyong}，扶抑用神={fuyi_xiyong}，冲突={conflict_info['conflict_degree']}",
        "conflict_elements": conflict_info["conflict_elements"],
        "conflict_degree": conflict_info["conflict_degree"],
        "overlap": conflict_info["overlap"],
        "overlap_elements": conflict_info["overlap_elements"],
        "urgency_level": urgency_level,
        "resolution": resolution,
    }


def analyze_conflict(
    tiao_hou_xiyong: List[str],
    fuyi_xiyong: List[str],
) -> Dict[str, Any]:
    """
    分析调候用神与扶抑用神的冲突程度

    Args:
        tiao_hou_xiyong: 调候喜用神列表
        fuyi_xiyong: 扶抑喜用神列表

    Returns:
        {
            "conflict_degree": str,      # "severe"(完全冲突) / "moderate"(部分冲突) / "mild"(轻微) / "none"(无冲突)
            "conflict_elements": list,   # 冲突的元素
            "overlap": int,              # 重叠数量
            "overlap_elements": list,   # 重叠的元素
        }
    """
    t_set = set(tiao_hou_xiyong)
    f_set = set(fuyi_xiyong)

    # 五行映射
    WUXING_MAP = {
        "甲": "木", "乙": "木",
        "丙": "火", "丁": "火",
        "戊": "土", "己": "土",
        "庚": "金", "辛": "金",
        "壬": "水", "癸": "水",
    }

    # 转换为五行集合
    t_wuxing = set(WUXING_MAP.get(x, x) for x in t_set)
    f_wuxing = set(WUXING_MAP.get(x, x) for x in f_set)

    # 天干层面的冲突（直接冲突）
    direct_conflict = t_set & f_set  # 完全一致 → 无冲突
    t_only = t_set - f_set
    f_only = f_set - t_set

    # 五行层面的冲突
    wuxing_conflict = t_wuxing & f_wuxing  # 重叠

    # 判断冲突程度
    # 完全冲突：调候要A五行，扶抑要B五行，且AB互不相容
    # 常见冲突：调候要水火，扶抑要土金（互相克制）

    conflict_elements = list(t_only | f_only)

    # 计算冲突分数
    # 完全冲突（无重叠）：100分
    # 部分重叠：按重叠比例减分
    if wuxing_conflict:
        overlap = len(wuxing_conflict)
        overlap_elements = list(wuxing_conflict)
        conflict_degree = "mild" if overlap >= 2 else "moderate"
    else:
        overlap = 0
        overlap_elements = []
        # 无重叠 = 完全冲突
        conflict_degree = "severe"

    # 如果调候和扶抑完全不同，且五行也互克 → 严重冲突
    # 如果调候和扶抑完全不同，但五行有相生关系 → 中度冲突
    if overlap == 0 and t_wuxing and f_wuxing:
        # 检查是否有相生关系
        has_mutual_support = False
        for te in t_wuxing:
            for fe in f_wuxing:
                if (te == "木" and fe == "火") or (te == "火" and fe == "土") or \
                   (te == "土" and fe == "金") or (te == "金" and fe == "水") or \
                   (te == "水" and fe == "木"):
                    has_mutual_support = True
                    break

        if not has_mutual_support:
            conflict_degree = "severe"
        else:
            conflict_degree = "moderate"

    return {
        "conflict_degree": conflict_degree,
        "conflict_elements": conflict_elements,
        "overlap": overlap,
        "overlap_elements": overlap_elements,
    }


def resolve_conflict(
    tiao_hou_xiyong: List[str],
    fuyi_xiyong: List[str],
    priority: str,
) -> Dict[str, Any]:
    """
    解决调候用神与扶抑用神的冲突

    Args:
        tiao_hou_xiyong: 调候喜用神列表
        fuyi_xiyong: 扶抑喜用神列表
        priority: 优先级策略，"tiao_hou" 或 "fuyi"

    Returns:
        {
            "preferred": list,      # 优先满足的用神
            "secondary": list,      # 次要满足的用神
            "conflict_score": int, # 0-100, 冲突程度（0=完全一致，100=完全冲突）
            "strategy": str,        # "tiao_hou_first" / "fuyi_first"
            "suggestion": str,      # 建议说明
        }
    """
    conflict_info = analyze_conflict(tiao_hou_xiyong, fuyi_xiyong)

    if priority == "tiao_hou":
        preferred = list(tiao_hou_xiyong)
        secondary = list(fuyi_xiyong)
        strategy = "tiao_hou_first"
    else:
        preferred = list(fuyi_xiyong)
        secondary = list(tiao_hou_xiyong)
        strategy = "fuyi_first"

    # 计算冲突分数
    # 基于overlap计算，overlap越多冲突越少
    if conflict_info["overlap"] >= 3:
        conflict_score = 20  # 大部分重叠，轻微冲突
    elif conflict_info["overlap"] >= 1:
        conflict_score = 50  # 部分重叠
    elif conflict_info["conflict_degree"] == "severe":
        conflict_score = 100  # 完全冲突
    else:
        conflict_score = 70  # 中度冲突

    # 建议
    if conflict_score <= 20:
        suggestion = "调候与扶抑基本一致，无需特别处理"
    elif conflict_score <= 50:
        suggestion = "部分重叠，优先满足preferred，同时兼顾secondary"
    elif conflict_score <= 80:
        suggestion = "存在明显冲突，优先满足preferred，secondary降低权重"
    else:
        if priority == "tiao_hou":
            suggestion = "严重冲突，调候优先，扶抑用神仅作辅助参考"
        else:
            suggestion = "严重冲突，扶抑优先，调候仅作辅助参考"

    return {
        "preferred": preferred,
        "secondary": secondary,
        "conflict_score": conflict_score,
        "strategy": strategy,
        "suggestion": suggestion,
        "overlap": conflict_info["overlap"],
        "overlap_elements": conflict_info["overlap_elements"],
    }


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=== 调候优先级判定 测试 ===\n")

    # 测试用例1: 亥子丑月寒气重
    print("【测试1】甲辰年 丁辰月 庚丑日 辛午时")
    print("  扶抑用神: 土金（日主弱）")
    print("  调候用神: 丙丁己（火）")
    print()

    # 模拟数据
    bazi_test = {
        "bazi": {
            "day": {"stem": "庚"},
            "month": {"stem": "丁", "branch": "辰"},
        },
        "xiyongshen": {"xiyongshen": ["土", "金"]},
    }
    rizhu_strength_test = {"strength": "弱", "score": 35}
    tiao_hou_test = {"喜用": ["丙", "丁", "己"], "忌避": ["壬"]}

    result = judge_tiao_hou_priority(bazi_test, rizhu_strength_test, tiao_hou_test)
    print(f"  调候优先: {result['tiao_hou_priority']}")
    print(f"  原因: {result['reason']}")
    print(f"  冲突程度: {result['conflict_degree']}")
    print(f"  冲突元素: {result['conflict_elements']}")
    print(f"  重叠: {result['overlap']} ({result['overlap_elements']})")
    print(f"  紧急程度: {result['urgency_level']}/10")
    print(f"  建议: {result['resolution']}")
    print()

    # 冲突解决
    resolution = resolve_conflict(
        tiao_hou_test["喜用"],
        bazi_test["xiyongshen"]["xiyongshen"],
        "tiao_hou" if result["tiao_hou_priority"] else "fuyi"
    )
    print(f"  冲突解决策略: {resolution['strategy']}")
    print(f"  优先满足: {resolution['preferred']}")
    print(f"  次要满足: {resolution['secondary']}")
    print(f"  冲突分数: {resolution['conflict_score']}")
    print(f"  建议: {resolution['suggestion']}")
    print()

    # 测试用例2: 寅卯辰月木
    print("【测试2】甲寅年 乙卯月 甲辰日")
    bazi_test2 = {
        "bazi": {
            "day": {"stem": "甲"},
            "month": {"stem": "乙", "branch": "卯"},
        },
        "xiyongshen": {"xiyongshen": ["水", "木"]},
    }
    rizhu_strength_test2 = {"strength": "中和", "score": 55}
    tiao_hou_test2 = {"喜用": ["丙", "癸"], "忌避": ["辛"]}

    result2 = judge_tiao_hou_priority(bazi_test2, rizhu_strength_test2, tiao_hou_test2)
    print(f"  调候优先: {result2['tiao_hou_priority']}")
    print(f"  原因: {result2['reason']}")
    print(f"  紧急程度: {result2['urgency_level']}/10")
    print()

    # 测试用例3: 巳午未月热燥
    print("【测试3】丙午年 戊午月 丁未日")
    bazi_test3 = {
        "bazi": {
            "day": {"stem": "丁"},
            "month": {"stem": "戊", "branch": "午"},
        },
        "xiyongshen": {"xiyongshen": ["土", "金"]},
    }
    rizhu_strength_test3 = {"strength": "强", "score": 70}
    tiao_hou_test3 = {"喜用": ["壬", "庚", "甲"], "忌避": ["丙", "丁", "戊", "己"]}

    result3 = judge_tiao_hou_priority(bazi_test3, rizhu_strength_test3, tiao_hou_test3)
    print(f"  调候优先: {result3['tiao_hou_priority']}")
    print(f"  原因: {result3['reason']}")
    print(f"  冲突程度: {result3['conflict_degree']}")
    print(f"  紧急程度: {result3['urgency_level']}/10")
    print()

    print("✓ 测试完成！")
