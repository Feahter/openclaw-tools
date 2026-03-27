#!/usr/bin/env python3
"""
破格原因分析器
基于《子平真诠》实现六种常见破格类型识别

破格类型：
1. 伤官见官   - 正官格遇伤官透干
2. 官杀克身为破 - 正官格/七杀格遇比劫（身弱难任）
3. 财星坏印   - 印格遇财星透干
4. 食神制杀太过 - 七杀格食神太重（泄日主）
5. 比劫争财   - 财格遇比劫分夺
6. 印星太重   - 印格印星太重（日主反泄）
"""

from typing import Dict, List, Any, Optional, Tuple

from pattern_method import (
    get_shishen, HEAVENLY_STEMS, EARTHLY_BRANCHES,
    GAN_IDX, SHISHEN_NAMES, SHISHEN_TABLE,
)


# ============================================================
# 破格规则定义
# ============================================================

# 破格类型常量
POGE_NONE = "无破格"
POGE_SHANGGUAN = "伤官见官"           # 正官格 + 伤官
POGE_GUANSHA_KESSHEN = "官杀克身为破"  # 正官/七杀格 + 比劫（身弱难任）
POGE_CAISHUAI_YIN = "财星坏印"         # 印格 + 财星
POGE_SISHEN_ZHISHA_GUODU = "食神制杀太过"  # 七杀格 + 食神太重
POGE_BIJIE_ZHENCAI = "比劫争财"        # 财格 + 比劫
POGE_YIN_XING_TAIZHONG = "印星太重"    # 印格 + 印星太重


def _get_shishen_from_stem(day_stem_idx: int, stem_idx: int) -> str:
    """从天干索引获取十神"""
    return SHISHEN_TABLE[day_stem_idx % 10][stem_idx % 10]


def _get_all_shishen(bazi: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    获取四柱天干对应的十神列表

    Returns:
        (shishen_list, stem_list)
    """
    day_stem_idx = bazi["day"]["stem_idx"]
    all_stems = [
        bazi["year"]["stem_idx"],
        bazi["month"]["stem_idx"],
        bazi["day"]["stem_idx"],
        bazi["hour"]["stem_idx"],
    ]
    stem_names = [
        bazi["year"]["stem"],
        bazi["month"]["stem"],
        bazi["day"]["stem"],
        bazi["hour"]["stem"],
    ]
    shishen_list = [_get_shishen_from_stem(day_stem_idx, s) for s in all_stems]
    return shishen_list, stem_names


def _count_shishen(shishen_list: List[str], target: str) -> int:
    """统计某十神出现次数"""
    return sum(1 for s in shishen_list if s == target)


def _is_pattern(geku_name: str, *patterns: str) -> bool:
    """判断格局是否匹配某几种类型"""
    return geku_name in patterns


# ============================================================
# 各破格类型判断逻辑
# ============================================================

def _check_shangquan(geku_name: str, shishen_list: List[str],
                     pattern_result: Dict) -> Optional[Dict]:
    """
    伤官见官：正官格遇伤官透干
    原理：伤官克正官，破官格
    """
    if not _is_pattern(geku_name, "正官格"):
        return None

    if _count_shishen(shishen_list, "伤官") == 0:
        return None

    # 找到伤官位置
    positions = []
    for i, shishen in enumerate(shishen_list):
        if shishen == "伤官":
            pos_map = ["年干", "月干", "日干", "时干"]
            positions.append(pos_map[i])

    return {
        "poge_type": POGE_SHANGGUAN,
        "poge_reason": f"月令正官被{''.join(positions)}伤官克制，伤官克官破格",
        "poge_stars": ["伤官", "正官"],
        "suggestion": "可用财星化伤官生官，或用印星制伤官护官"
    }


def _check_guansha_kesshen(geku_name: str, shishen_list: List[str],
                           bazi: Dict, pattern_result: Dict) -> Optional[Dict]:
    """
    官杀克身为破：正官格/七杀格遇比劫（身弱难任）
    原理：官杀太重而身弱，比劫透干也难任
    """
    if not _is_pattern(geku_name, "正官格", "七杀格"):
        return None

    has_bijie = _count_shishen(shishen_list, "比肩") > 0 or _count_shishen(shishen_list, "劫财") > 0
    if not has_bijie:
        return None

    # 判断身旺还是身弱（简化：月令是否得令）
    month_branch_idx = bazi["month"]["branch_idx"]
    day_stem_idx = bazi["day"]["stem_idx"]
    STEM_LING_DEFU = {
        0: [2, 3], 1: [2, 3], 2: [5, 6], 3: [5, 6],
        4: [1, 4, 7, 10], 5: [1, 4, 7, 10],
        6: [8, 9], 7: [8, 9], 8: [0, 11], 9: [0, 11],
    }
    is_deling = month_branch_idx in STEM_LING_DEFU.get(day_stem_idx, [])

    # 官杀格 + 比劫 + 身弱 = 破格
    # 或者：官杀重而无制约
    has_yinshi = _count_shishen(shishen_list, "正印") > 0 or _count_shishen(shishen_list, "偏印") > 0
    has_shigeng = _count_shishen(shishen_list, "食神") > 0 or _count_shishen(shishen_list, "伤官") > 0

    # 如果有印或食神化杀克，则不破
    if has_yinshi or has_shigeng:
        return None

    # 身弱 + 比劫 + 官杀重 → 破
    if not is_deling:
        return {
            "poge_type": POGE_GUANSHA_KESSHEN,
            "poge_reason": f"{geku_name}官杀旺而身弱，月令失令，比劫透干难以帮身任官杀，破格",
            "poge_stars": ["比肩", "劫财", "正官" if "正官格" in geku_name else "七杀"],
            "suggestion": "宜补印星化官杀生身，或补比劫帮身任官"
        }

    return None


def _check_caishuai_yin(geku_name: str, shishen_list: List[str],
                        pattern_result: Dict) -> Optional[Dict]:
    """
    财星坏印：印格遇财星
    原理：财克印，印为用神时被破坏
    """
    if not _is_pattern(geku_name, "正印格", "偏印格"):
        return None

    has_caishen = _count_shishen(shishen_list, "正财") > 0 or _count_shishen(shishen_list, "偏财") > 0
    if not has_caishen:
        return None

    return {
        "poge_type": POGE_CAISHUAI_YIN,
        "poge_reason": f"{geku_name}以印为用神，财星透干克印，印格被破",
        "poge_stars": ["正财", "偏财", "正印" if "正印格" in geku_name else "偏印"],
        "suggestion": "宜去财护印，或用官杀化财生印"
    }


def _check_shishen_zhisha_guodu(geku_name: str, shishen_list: List[str],
                                 pattern_result: Dict) -> Optional[Dict]:
    """
    食神制杀太过：七杀格食神太重
    原理：食神本是七杀用神，但太重则泄日主之气
    """
    if not _is_pattern(geku_name, "七杀格"):
        return None

    has_shishen = _count_shishen(shishen_list, "食神") == 0
    if has_shishen:
        return None  # 食神制杀有功，不破

    # 食神太重：食神两个以上，且无印化，或身弱
    shishen_count = _count_shishen(shishen_list, "食神")
    if shishen_count == 0:
        return None

    # 食神是否太重：食神在地支也有根，或食神两个以上
    has_yin = _count_shishen(shishen_list, "正印") > 0 or _count_shishen(shishen_list, "偏印") > 0
    # 无印化 + 食神旺 = 食神泄日主太过
    if not has_yin:
        return {
            "poge_type": POGE_SISHEN_ZHISHA_GUODU,
            "poge_reason": f"七杀格以食神制杀，但食神太重无印化，泄日主之气过甚，破格",
            "poge_stars": ["食神", "七杀"],
            "suggestion": "宜补印星化食生身，或增强日主力量"
        }

    return None


def _check_bijie_zhencai(geku_name: str, shishen_list: List[str],
                          pattern_result: Dict) -> Optional[Dict]:
    """
    比劫争财：财格遇比劫分财
    原理：财星为用时被分夺
    """
    if not _is_pattern(geku_name, "正财格", "偏财格"):
        return None

    has_bijie = _count_shishen(shishen_list, "比肩") > 0 or _count_shishen(shishen_list, "劫财") > 0
    if not has_bijie:
        return None

    # 找到比劫位置
    positions = []
    for i, shishen in enumerate(shishen_list):
        if shishen in ["比肩", "劫财"]:
            pos_map = ["年干", "月干", "日干", "时干"]
            positions.append(pos_map[i])

    return {
        "poge_type": POGE_BIJIE_ZHENCAI,
        "poge_reason": f"{geku_name}以财为用，{''.join(positions)}比劫分夺财星，破格",
        "poge_stars": ["比肩", "劫财", "正财" if "正财格" in geku_name else "偏财"],
        "suggestion": "宜增强日主力量克财，或用官杀制比劫护财"
    }


def _check_yin_xing_taizhong(geku_name: str, shishen_list: List[str],
                              bazi: Dict, pattern_result: Dict) -> Optional[Dict]:
    """
    印星太重：印格印星太重
    原理：印太重则日主反泄
    """
    if not _is_pattern(geku_name, "正印格", "偏印格"):
        return None

    yin_count = _count_shishen(shishen_list, "正印") + _count_shishen(shishen_list, "偏印")
    if yin_count < 2:
        return None  # 印星不重

    # 印太重：印星两个以上，且无官杀或无泄
    has_guansha = _count_shishen(shishen_list, "正官") > 0 or _count_shishen(shishen_list, "七杀") > 0
    has_shigeng = _count_shishen(shishen_list, "食神") > 0 or _count_shishen(shishen_list, "伤官") > 0

    # 有泄或有官杀生印则不算太重
    if has_guansha or has_shigeng:
        return None

    return {
        "poge_type": POGE_YIN_XING_TAIZHONG,
        "poge_reason": f"{geku_name}印星太重无泄，印多泄日主之气过甚，破格",
        "poge_stars": ["正印" if "正印格" in geku_name else "偏印"],
        "suggestion": "宜补官杀生印，或补食伤泄秀"
    }


# ============================================================
# 主分析函数
# ============================================================

def analyze_poge_reasons(bazi: Dict, pattern_result: Dict) -> Dict:
    """
    破格原因分析

    Args:
        bazi: 八字字典
        pattern_result: 格局成败判定结果（来自 judge_pattern_cheng）

    Returns:
        {
            "is_broken": True/False,      # 是否破格
            "broken": True/False,         # 是否破格（同 is_broken，兼容旧接口）
            "poge_type": str,             # 破格类型（无破格/伤官见官/...）
            "poge_reason": str,          # 破格原因描述
            "poge_stars": List[str],     # 涉及破格的天干/十神
            "suggestion": str,            # 化解建议
        }
    """
    # 如果格局本就不是成格（level == "下等" 且 cheng_count == 0），直接返回无破格
    # 只有在成格基础上被破坏的才叫破格
    level = pattern_result.get("level", "")
    is_cheng = pattern_result.get("is_cheng", False)

    # 如果格局本身不成（中等以下），不按"破格"算，只按"不成格"算
    if not is_cheng and level != "破格":
        return {
            "is_broken": False,
            "broken": False,
            "poge_type": "格局不成",
            "poge_reason": "格局本不成，气浊神枯，无明显破格因素但格局不立",
            "poge_stars": [],
            "suggestion": "格局不成，名字宜先确定格局用神方向，扶助月令用神"
        }

    # 如果本身就是破格
    if level == "破格":
        # 执行破格原因分析
        pass  # 继续分析具体原因

    geku_name = pattern_result.get("pattern", pattern_result.get("geku_name", ""))

    # 获取十神列表
    shishen_list, stem_names = _get_all_shishen(bazi)

    # 按优先级检查各破格类型
    checkers = [
        _check_shangquan,
        _check_guansha_kesshen,
        _check_caishuai_yin,
        _check_shishen_zhisha_guodu,
        _check_bijie_zhencai,
        _check_yin_xing_taizhong,
    ]

    for checker in checkers:
        # 不同checker需要不同参数
        try:
            if checker == _check_guansha_kesshen or checker == _check_yin_xing_taizhong:
                result = checker(geku_name, shishen_list, bazi, pattern_result)
            else:
                result = checker(geku_name, shishen_list, pattern_result)
        except Exception:
            continue

        if result:
            return {
                "is_broken": True,
                "broken": True,
                **result,
            }

    # 有破格标记但未匹配到具体原因
    if level == "破格":
        return {
            "is_broken": True,
            "broken": True,
            "poge_type": "其他破格",
            "poge_reason": f"{geku_name}破格，具体原因待细论",
            "poge_stars": [],
            "suggestion": "建议综合分析八字组合，确定破格原因后以名字化解"
        }

    # 未破格
    return {
        "is_broken": False,
        "broken": False,
        "poge_type": POGE_NONE,
        "poge_reason": f"{geku_name}格局未破，成格因素保全",
        "poge_stars": [],
        "suggestion": ""
    }


