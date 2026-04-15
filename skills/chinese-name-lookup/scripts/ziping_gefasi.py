#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
子平格局法 · 格法（ziping_gefasi）
基于《子平真诠》深度融合 — 特殊格局检测 + 格局-日主配合 + 喜用神双轨修正

功能：
1. 特殊格局检测（从格、专旺格、化气格）
2. 格局-日主旺衰配合判定
3. 格局法喜用神输出
4. 与 xiyongshen_v2 喜用神双轨对比融合

核心概念（子平真诠）：
- 普通格局：日主为体，格局为用；日主强弱决定格局能否成立
- 特殊格局：日主从乎格局（从杀、从财、从儿、从印）
- 格局已成：格局用神方向不可损害，喜用神向格局靠拢
- 格局未成：回归日主旺衰，以扶抑为主
"""

from typing import Dict, List, Any, Tuple, Optional

# ============================================================
# 常量复用（与 bazi_engine / pattern_method 保持一致）
# ============================================================

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
STEM_ELEMENTS: Dict[str, str] = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}
STEM_IDX: Dict[str, int] = {g: i for i, g in enumerate(HEAVENLY_STEMS)}
ELEMENT_NAMES = ["木", "火", "土", "金", "水"]

# 天干相合表（化气格判定用）
HE_COMBINATIONS: Dict[Tuple[str, str], Tuple[str, str, str]] = {
    ("甲", "己"): ("甲", "己", "土"),   # 甲己合化土
    ("乙", "庚"): ("乙", "庚", "金"),   # 乙庚合化金
    ("丙", "辛"): ("丙", "辛", "水"),   # 丙辛合化水
    ("丁", "壬"): ("丁", "壬", "木"),   # 丁壬合化木
    ("戊", "癸"): ("戊", "癸", "火"),   # 戊癸合化火
}

# 十神表（复用 pattern_method）
SHISHEN_TABLE = [
    #        甲    乙    丙    丁    戊    己    庚    辛    壬    癸
    ["比肩", "劫财", "食神", "伤官", "偏财", "正财", "偏官", "正官", "偏印", "正印"],  # 甲
    ["劫财", "比肩", "伤官", "食神", "正财", "偏财", "正官", "偏官", "正印", "偏印"],  # 乙
    ["偏印", "正印", "比肩", "劫财", "食神", "伤官", "偏财", "正财", "偏官", "正官"],  # 丙
    ["正印", "偏印", "劫财", "比肩", "伤官", "食神", "正财", "偏财", "正官", "偏官"],  # 丁
    ["偏财", "正财", "偏印", "正印", "比肩", "劫财", "食神", "伤官", "偏官", "正官"],  # 戊
    ["正财", "偏财", "正印", "偏印", "劫财", "比肩", "伤官", "食神", "正官", "偏官"],  # 己
    ["偏官", "正官", "偏财", "正财", "偏印", "正印", "比肩", "劫财", "食神", "伤官"],  # 庚
    ["正官", "偏官", "正财", "偏财", "正印", "偏印", "劫财", "比肩", "伤官", "食神"],  # 辛
    ["食神", "伤官", "偏官", "正官", "偏财", "正财", "偏印", "正印", "比肩", "劫财"],  # 壬
    ["伤官", "食神", "正官", "偏官", "正财", "偏财", "正印", "偏印", "劫财", "比肩"],  # 癸
]
SHISHEN_NAMES = ["比肩", "劫财", "食神", "伤官", "偏财", "正财", "偏官", "正官", "偏印", "正印"]


def get_shishen(day_stem: str, other_stem: str) -> str:
    """获取十神关系"""
    di = STEM_IDX.get(day_stem, 0)
    oi = STEM_IDX.get(other_stem, 0)
    return SHISHEN_TABLE[di][oi]


def stem_to_elem(stem: str) -> str:
    """天干 → 五行"""
    return STEM_ELEMENTS.get(stem, "")


def elem_to_shishen(elem: str, is_positive: bool = True) -> str:
    """五行 → 十神名称（相对于日干，简化：印/枭/官/财/食/伤/比/劫）"""
    # 这是通用标签，不是具体十神，保留五行名称更通用
    return elem


# ============================================================
# 1. 特殊格局检测
# ============================================================

def detect_special_pattern(
    bazi: Dict[str, Any],
    rizhu_strength: Dict[str, Any],
    all_stems: List[Tuple[str, str]],  # [(位置, 天干), ...]
) -> Dict[str, Any]:
    """
    检测特殊格局（从格、专旺格、化气格）

    检测顺序：
    1. 专旺格（曲直、炎上、稼穑、从革、润下）
    2. 化气格（甲己合化土、乙庚合化金、丙辛合化水、丁壬合化木、戊癸合化火）
    3. 从格（从杀格、从财格、从儿格、从印格）

    判断依据：
    - 专旺格：月令为日干同气之五行，且全局该五行气势极旺
    - 化气格：月令本气不透，而合化成气，且化神得势
    - 从格：日主极弱无气，四柱克泄交加，日主不得不从

    Args:
        bazi: 八字字典
        rizhu_strength: 日主强弱结果
        all_stems: [(位置, 天干), ...] 全部天干

    Returns:
        {
            "type": "普通格局"/"专旺格"/"化气格"/"从格",
            "sub_type": str,          # 具体类型如"曲直格"、"从杀格"
            "hua_shen": Optional[str], # 化神（如"土"），仅化气格有
            "hua_condition": Optional[str],  # 合化条件描述
            "is_detected": bool,
            "confidence": float,      # 0-1
            "reason": str,
            "xiyong_by_pattern": List[str],  # 格局法喜用神（五行）
            "ji_by_pattern": List[str],      # 格局法忌神（五行）
        }
    """
    day_stem = bazi["day"]["stem"]
    month_branch = bazi["month"]["branch"]
    month_stem = bazi["month"]["stem"]
    day_elem = STEM_ELEMENTS.get(day_stem, "")

    # 收集四柱天干
    stems = [s for _, s in all_stems]
    stem_elems = [STEM_ELEMENTS.get(s, "") for s in stems]

    strength = rizhu_strength.get("strength", "")
    strength_score = rizhu_strength.get("score", 50)

    # -----------------------------------------------
    # 1. 专旺格检测
    # -----------------------------------------------
    # 专旺五局：曲直（木）、炎上（火）、稼穑（土）、从革（金）、润下（水）
    ZHUANWANG_RULES: Dict[str, Tuple[str, List[str]]] = {
        "曲直格": ("木", ["甲", "乙", "寅", "卯"]),
        "炎上格": ("火", ["丙", "丁", "巳", "午"]),
        "稼穑格": ("土", ["戊", "己", "辰", "戌", "丑", "未"]),
        "从革格": ("金", ["庚", "辛", "申", "酉"]),
        "润下格": ("水", ["壬", "癸", "亥", "子"]),
    }

    # 月令本气是否为日干同气
    BENQI_MAP: Dict[str, str] = {
        "子": "癸", "丑": "己", "寅": "甲", "卯": "乙",
        "辰": "戊", "巳": "丙", "午": "丁", "未": "己",
        "申": "庚", "酉": "辛", "戌": "戊", "亥": "壬",
    }
    yue_benqi = BENQI_MAP.get(month_branch, "")

    for pattern_name, (required_elem, marker_stems) in ZHUANWANG_RULES.items():
        if day_elem != required_elem:
            continue

        # 月令本气是日干同气五行
        marker_count = sum(1 for s in stems + [month_branch] if s in marker_stems)

        # 专旺格判定：月令本气为日干同气，且全局该五行强旺
        if month_branch in marker_stems or yue_benqi in marker_stems:
            # 全局同气数量
            tongqi = sum(1 for e in stem_elems if e == required_elem)
            # 如果月令本气就是日干同气，且日主本身偏旺或极旺
            is_strong_enough = strength in ["强", "过强", "极强", "旺", "偏旺"]
            if (tongqi >= 3 and is_strong_enough) or (tongqi >= 2 and is_strong_enough and strength_score >= 65):
                return {
                    "type": "专旺格",
                    "sub_type": pattern_name,
                    "hua_shen": None,
                    "hua_condition": None,
                    "is_detected": True,
                    "confidence": 0.85,
                    "reason": (
                        f"日主{day_stem}{day_elem}，月令{month_branch}本气{yue_benqi}属{required_elem}，"
                        f"全局{required_elem}气势强旺（{tongqi}个{required_elem}字），"
                        f"日主偏旺可任专旺之势，定为{pattern_name}"
                    ),
                    "xiyong_by_pattern": _get_zhuwan_xiyong(required_elem),
                    "ji_by_pattern": _get_zhuwan_ji(required_elem),
                }

    # -----------------------------------------------
    # 2. 化气格检测
    # -----------------------------------------------
    hua_result = _detect_huafa(bazi, stems, month_branch, yue_benqi)
    if hua_result["is_detected"]:
        return hua_result

    # -----------------------------------------------
    # 3. 从格检测
    # -----------------------------------------------
    cong_result = _detect_congge(bazi, stems, stem_elems, day_stem, day_elem, strength, strength_score)
    if cong_result["is_detected"]:
        return cong_result

    # 不是特殊格局
    return {
        "type": "普通格局",
        "sub_type": "",
        "hua_shen": None,
        "hua_condition": None,
        "is_detected": False,
        "confidence": 0.0,
        "reason": "全局气势未成专旺、化气、从格之特殊格局，按普通格局论",
        "xiyong_by_pattern": [],
        "ji_by_pattern": [],
    }


def _detect_huafa(
    bazi: Dict[str, Any],
    stems: List[str],
    month_branch: str,
    yue_benqi: str,
) -> Dict[str, Any]:
    """
    化气格检测

    化气格条件：
    1. 两干紧贴相合（月干与日干，或年干与月干）
    2. 化神得令（月令本气与化神一致）
    3. 化神旺而有力（全局化神气势强）
    4. 化神不能被破坏（无克化神之字）

    化气格列表：
    - 甲己合化土（得土月令）
    - 乙庚合化金（得金月令）
    - 丙辛合化水（得水月令）
    - 丁壬合化木（得木月令）
    - 戊癸合化火（得火月令）
    """
    day_stem = bazi["day"]["stem"]
    month_stem = bazi["month"]["stem"]

    # 检查日干-月干是否相合
    key = tuple(sorted([day_stem, month_stem]))
    day_idx = STEM_IDX.get(day_stem, 0)
    month_idx = STEM_IDX.get(month_stem, 0)

    # 直接查找合化
    for (g1, g2), (eg1, eg2, hua_elem) in HE_COMBINATIONS.items():
        if (day_stem == g1 and month_stem == g2) or (day_stem == g2 and month_stem == g1):
            # 找到合化
            # 化神得令：月令本气与化神一致
            hua_elem_in_month = (yue_benqi == eg1 or yue_benqi == eg2)
            huade = hua_elem_in_month

            # 化神是否被破坏
            # 找出克化神的天干（如化土则忌木克）
            KE_HUA: Dict[str, List[str]] = {
                "土": ["甲", "乙"],   # 木克土
                "金": ["丙", "丁"],   # 火克金
                "水": ["庚", "辛"],   # 金克水
                "木": ["戊", "己"],   # 土克木
                "火": ["壬", "癸"],   # 水克火
            }
            po_by = [s for s in stems if s in KE_HUA.get(hua_elem, [])]

            # 化神得势程度（全局化神五行数量）
            hua_elem_count = sum(1 for s in stems if STEM_ELEMENTS.get(s) == hua_elem)

            if huade and not po_by and hua_elem_count >= 2:
                pattern_name = f"化气格·{hua_elem}"
                return {
                    "type": "化气格",
                    "sub_type": pattern_name,
                    "hua_shen": hua_elem,
                    "hua_condition": f"{g1}{g2}合化{hua_elem}",
                    "is_detected": True,
                    "confidence": 0.80,
                    "reason": (
                        f"月令{month_branch}本气{yue_benqi}属{hua_elem}，"
                        f"日干{day_stem}与月干{month_stem}{g1}{g2}合化{hua_elem}，"
                        f"全局{hua_elem}气势有力（{hua_elem_count}字），"
                        f"化气格成，定为{pattern_name}"
                    ),
                    "xiyong_by_pattern": [hua_elem],  # 化神为用
                    "ji_by_pattern": _get_huafa_ji(hua_elem),
                }
            elif huade:
                pattern_name = f"化气格·{hua_elem}(欠纯)"
                return {
                    "type": "化气格",
                    "sub_type": pattern_name,
                    "hua_shen": hua_elem,
                    "hua_condition": f"{g1}{g2}合化{hua_elem}（欠纯）",
                    "is_detected": True,
                    "confidence": 0.55,
                    "reason": (
                        f"日干{day_stem}与月干{month_stem}有{g1}{g2}合化{hua_elem}之势，"
                        f"但{'化神被破坏（见' + '/'.join(po_by) + '）' if po_by else '化神欠纯（全局仅' + str(hua_elem_count) + '字）'}，"
                        f"化气格欠纯"
                    ),
                    "xiyong_by_pattern": [hua_elem],
                    "ji_by_pattern": _get_huafa_ji(hua_elem),
                }

    return {"is_detected": False}


def _detect_congge(
    bazi: Dict[str, Any],
    stems: List[str],
    stem_elems: List[str],
    day_stem: str,
    day_elem: str,
    strength: str,
    strength_score: int,
) -> Dict[str, Any]:
    """
    从格检测

    从格条件（子平真诠）：
    - 日主极弱无气（无根无印，比劫全无）
    - 四柱克泄交加（日主所不胜之字众多）
    - 日主不得不从

    从杀格：官杀太强，日主不得不从杀
    从财格：财星太强，日主不得不从财
    从儿格：食伤太强，日主不得不从儿
    从印格：印星太强，日主不得不从印
    """
    # 日主根：日支是否与日干同气
    day_branch = bazi["day"]["branch"]
    BENQI_MAP: Dict[str, str] = {
        "子": "癸", "丑": "己", "寅": "甲", "卯": "乙",
        "辰": "戊", "巳": "丙", "午": "丁", "未": "己",
        "申": "庚", "酉": "辛", "戌": "戊", "亥": "壬",
    }
    day_zhi_benqi = BENQI_MAP.get(day_branch, "")

    # 日主是否无根（同气）
    has_root = (day_zhi_benqi == day_stem)

    # 日主是否无印（正印/偏印）
    yin_stems = []
    day_idx = STEM_IDX.get(day_stem, 0)
    for stem in stems:
        si = STEM_IDX.get(stem, 0)
        ss = SHISHEN_TABLE[day_idx][si]
        if "印" in ss:
            yin_stems.append(stem)

    # 计算十神分布
    shishen_counts: Dict[str, int] = {}
    for stem in stems:
        si = STEM_IDX.get(stem, 0)
        ss = SHISHEN_TABLE[day_idx][si]
        shishen_counts[ss] = shishen_counts.get(ss, 0) + 1

    # 判断从格类型
    # 从杀格：官杀星极旺（>=3个官杀字）
    guasha = shishen_counts.get("正官", 0) + shishen_counts.get("七杀", 0)
    # 从财格：财星极旺
    cai = shishen_counts.get("正财", 0) + shishen_counts.get("偏财", 0)
    # 从儿格：食伤极旺
    ershang = shishen_counts.get("食神", 0) + shishen_counts.get("伤官", 0)
    # 从印格：印星极旺
    yin_count = shishen_counts.get("正印", 0) + shishen_counts.get("偏印", 0)

    # 比劫（帮身）
    bijie = shishen_counts.get("比肩", 0) + shishen_counts.get("劫财", 0)

    # 从格判定：日主极弱 + 无根无印 + 无比劫 + 某类十神极旺
    is_weak_ultra = strength in ["极弱", "过弱", "极弱", "弱"]
    is_score_low = strength_score < 30

    if is_weak_ultra and is_score_low and not has_root:
        if guasha >= 3 and bijie == 0:
            return _make_cong_result("从杀格", "七杀/正官", day_elem, guasha)
        if cai >= 3 and bijie == 0:
            return _make_cong_result("从财格", "财星", day_elem, cai)
        if ershang >= 3 and bijie <= 1:
            return _make_cong_result("从儿格", "食伤", day_elem, ershang)
        if yin_count >= 2 and cai >= 2:
            # 从印格通常需要财星坏印
            return _make_cong_result("从印格", "印星", day_elem, yin_count)

    return {"is_detected": False}


def _make_cong_result(
    pattern_name: str,
    reason_elem: str,
    day_elem: str,
    count: int,
) -> Dict[str, Any]:
    """构造从格结果"""
    if "杀" in pattern_name:
        cong_xiyong = ["金", "土"]  # 从杀：杀印相生为用
        cong_ji = ["木", "火"]       # 忌木火（生助日干）
    elif "财" in pattern_name:
        cong_xiyong = ["火", "金"]   # 从财：食伤生财为用
        cong_ji = ["木", "水"]       # 忌木水
    elif "儿" in pattern_name:
        cong_xiyong = ["金", "水"]   # 从儿：泄秀为用
        cong_ji = ["土", "火"]       # 忌土火
    else:  # 从印格
        cong_xiyong = ["火", "土"]   # 从印：财星坏印为用
        cong_ji = ["水", "木"]       # 忌水木

    return {
        "type": "从格",
        "sub_type": pattern_name,
        "hua_shen": None,
        "hua_condition": f"日主极弱不得不从{reason_elem}",
        "is_detected": True,
        "confidence": 0.80,
        "reason": f"日主{day_elem}极弱无气，四柱{reason_elem}强旺（{count}字），日主不得不从，定为{pattern_name}",
        "xiyong_by_pattern": cong_xiyong,
        "ji_by_pattern": cong_ji,
    }


def _get_zhuwan_xiyong(required_elem: str) -> List[str]:
    """专旺格喜用神（顺其旺势）"""
    return [required_elem, "水"]  # 专旺：喜生扶本气，忌克泄


def _get_zhuwan_ji(required_elem: str) -> List[str]:
    """专旺格忌神"""
    KE: Dict[str, str] = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}
    opposite = KE.get(required_elem, "")
    return [opposite, "水" if required_elem != "水" else "土"]


def _get_huafa_ji(hua_elem: str) -> List[str]:
    """化气格忌神"""
    KE: Dict[str, str] = {"土": "木", "金": "火", "水": "土", "木": "金", "火": "水"}
    return [KE.get(hua_elem, "")]


# ============================================================
# 2. 格局-日主旺衰配合判定（普通格局）
# ============================================================

def judge_pattern_day_strength(
    pattern_info: Dict[str, Any],
    cheng_info: Dict[str, Any],
    rizhu_strength: Dict[str, Any],
) -> Dict[str, Any]:
    """
    判定格局与日主旺衰的配合关系

    子平真诠核心：格局与日主是"体用"关系
    - 日主为体，格局为用
    - 普通格局：日主强方可任格局之用，格局成中日主须有气
    - 特殊格局：日主从乎格局，不以日主强弱论

    配合类型：
    - "体用相停"：日主旺衰与格局强弱相当，最为吉利
    - "体强用弱"：日主旺而格局弱——格局被日主拖累
    - "体弱用强"：日主弱而格局强——日主难任格局
    - "体用皆弱"：两者皆弱——格局难成，日主亦弱

    Args:
        pattern_info: determine_pattern() 返回的格局取用结果
        cheng_info: judge_pattern_cheng() 返回的格局成败结果
        rizhu_strength: 日主强弱结果 {"strength": str, "score": int, ...}

    Returns:
        {
            "peihe_type": str,          # 配合类型
            "peihe_level": str,         # 配合等级：上/中/下
            "score": int,               # 0-100
            "reason": str,
            "suggestion": str,          # 格局-日主配合建议
            "day_requirement": str,     # 对日主的最低要求
        }
    """
    strength = rizhu_strength.get("strength", "中")
    score = rizhu_strength.get("score", 50)
    cheng_level = cheng_info.get("level", "未知")
    is_cheng = cheng_info.get("is_cheng", False)
    geku_name = pattern_info.get("pattern", "")

    # 成格时对日主的要求
    # 上等成格：日主偏旺或身旺，任格局
    # 中等成格：日主中和偏旺
    # 下等成格：日主中和或偏弱
    day_strong_enough = strength in ["强", "过强", "极强", "旺", "偏旺", "偏强"]
    day_mid = strength in ["中", "中和", "偏弱"]
    day_weak = strength in ["弱", "过弱", "极弱"]

    if is_cheng:
        if cheng_level == "上等":
            if day_strong_enough:
                peihe_type = "体用相停"
                peihe_level = "上"
                peihe_score = 90
                reason = f"{geku_name}{cheng_level}成格，日主{strength}有力，可任格局，体用相停"
                suggestion = "格局上等成格，日主有力任事，最为吉利，名字宜保护格局用神"
                day_req = "日主身旺可任格局，最佳"
            elif day_mid:
                peihe_type = "体弱用强"
                peihe_level = "中"
                peihe_score = 70
                reason = f"{geku_name}{cheng_level}成格，但日主{strength}，格局稍强于日主"
                suggestion = "格局已成但日主偏弱，名字宜适当扶助日主，不宜过度克泄"
                day_req = "日主中和偏旺更佳"
            else:
                peihe_type = "体弱用强"
                peihe_level = "下"
                peihe_score = 50
                reason = f"{geku_name}{cheng_level}成格，但日主{strength}过弱，难任格局"
                suggestion = "格局成格但日主过弱，名字宜补日主之气，不宜过强克泄"
                day_req = "日主偏弱，格局难任"
        elif cheng_level == "中等":
            if day_strong_enough:
                peihe_type = "体强用弱"
                peihe_level = "中"
                peihe_score = 65
                reason = f"{geku_name}{cheng_level}成格，日主{strength}有力，但格局偏弱"
                suggestion = "格局中等成格，日主偏旺，名字宜扶助格局用神以补格局之不足"
                day_req = "日主偏旺，格局偏弱"
            elif day_mid:
                peihe_type = "体用相停"
                peihe_level = "中上"
                peihe_score = 75
                reason = f"{geku_name}{cheng_level}成格，日主{strength}配合格局，格局稳定"
                suggestion = "格局中等成格，日主配合，名字宜配合格局用神"
                day_req = "日主中和偏旺最佳"
            else:
                peihe_type = "体弱用强"
                peihe_level = "下"
                peihe_score = 45
                reason = f"{geku_name}{cheng_level}成格，日主{strength}弱，格局强于日主"
                suggestion = "格局中等但日主过弱，名字宜补日主，格局用神不宜过强"
                day_req = "日主过弱难任"
        else:  # 下等/破格
            if day_strong_enough:
                peihe_type = "体强用弱"
                peihe_level = "下"
                peihe_score = 40
                reason = f"{geku_name}{cheng_level}，日主{strength}但格局已成负担"
                suggestion = "格局下等或破格，日主偏旺但格局不足，名字宜化解破格因素"
                day_req = "日主旺，格局弱"
            else:
                peihe_type = "体用皆弱"
                peihe_level = "下"
                peihe_score = 30
                reason = f"{geku_name}{cheng_level}，日主{strength}，两者皆弱"
                suggestion = "格局未成，日主亦弱，名字宜以扶抑为主兼顾格局"
                day_req = "日主弱，格局亦弱"
    else:
        # 格局未成
        peihe_type = "格局未成"
        peihe_level = "下"
        peihe_score = 35
        reason = f"{geku_name}破格/未成，不以格局为主，以日主旺衰为主"
        suggestion = "格局未成，以扶抑喜用神为主，兼顾格局潜在用神"
        day_req = "格局未成，日主旺衰为主"

    return {
        "peihe_type": peihe_type,
        "peihe_level": peihe_level,
        "score": peihe_score,
        "reason": reason,
        "suggestion": suggestion,
        "day_requirement": day_req,
    }


# ============================================================
# 3. 格局法喜用神计算
# ============================================================

def get_xiyong_by_gefasi(
    pattern_info: Dict[str, Any],
    cheng_info: Dict[str, Any],
    special_pattern: Dict[str, Any],
    peihe_info: Dict[str, Any],
) -> Dict[str, Any]:
    """
    基于格局法计算喜用神

    子平真诠用神原则：
    1. 特殊格局（专旺/化气/从格）→ 顺格局气势，格局用神即为喜用
    2. 普通格局已成（上等/中等）→ 格局用神为重，兼顾日主
    3. 普通格局未成/破格 → 回归日主旺衰，格局辅助

    Args:
        pattern_info: 格局取用结果
        cheng_info: 格局成败结果
        special_pattern: 特殊格局检测结果
        peihe_info: 格局-日主配合结果

    Returns:
        {
            "xiyong": List[str],       # 格局法喜用（五行）
            "ji": List[str],           # 格局法忌神（五行）
            "source": str,              # 来源说明
            "principle": str,           # 判定原则
            "adjustment": str,         # 调整说明
        }
    """
    # 特殊格局：直接使用格局喜用
    if special_pattern.get("is_detected"):
        sub_type = special_pattern["sub_type"]
        xiyong = special_pattern.get("xiyong_by_pattern", [])
        ji = special_pattern.get("ji_by_pattern", [])

        if special_pattern["type"] == "专旺格":
            principle = (
                f"{sub_type}，日主率众而旺，顺其气势为用。"
                f"喜本气{xiyong[0] if xiyong else ''}扶助，忌金水克泄"
            )
        elif special_pattern["type"] == "化气格":
            hua_shen = special_pattern.get("hua_shen", "")
            principle = (
                f"{sub_type}，化神{hua_shen}为用，助化神为喜，"
                f"忌克化神之字"
            )
        else:  # 从格
            principle = (
                f"{sub_type}，日主无气不得不从，"
                f"顺从之势为用，忌助日主之字"
            )

        return {
            "xiyong": xiyong[:3],
            "ji": ji[:3],
            "source": f"特殊格局·{sub_type}",
            "principle": principle,
            "adjustment": f"特殊格局以格局为用，不受日主旺衰影响，喜用{xiyong}，忌{ji}",
        }

    # 普通格局
    geku_name = pattern_info.get("pattern", "")
    cheng_level = cheng_info.get("level", "未知")
    is_cheng = cheng_info.get("is_cheng", False)
    peihe_level = peihe_info.get("peihe_level", "下")
    peihe_type = peihe_info.get("peihe_type", "")

    # 格局已成：根据格局类型定喜用
    if is_cheng:
        xiyong = _get_geku_xiyong(geku_name)
        ji = _get_geku_ji(geku_name)

        if cheng_level == "上等":
            adjustment = (
                f"{geku_name}上等成格，以格局用神{xiyong}为主，"
                f"配合{peihe_type}，名字宜保护格局用神"
            )
        else:
            adjustment = (
                f"{geku_name}{cheng_level}成格，格局用神{xiyong}为重，"
                f"兼顾日主{peihe_type}，名字宜配合格局用神"
            )

        principle = (
            f"普通格局{geku_name}{cheng_level}成格，"
            f"格局为用，日主为体，"
            f"{peihe_type}（{peihe_level}等配合），"
            f"格局用神{xiyong}"
        )

        return {
            "xiyong": xiyong[:3],
            "ji": ji[:3],
            "source": f"普通格局·{geku_name}",
            "principle": principle,
            "adjustment": adjustment,
        }

    # 格局未成/破格：格局辅助，回归扶抑
    return {
        "xiyong": [],
        "ji": [],
        "source": "格局未成/破格",
        "principle": f"{geku_name}未成/破格，不以格局为主，回归日主旺衰判定",
        "adjustment": "格局破格，以扶抑喜用神为主，格局仅作辅助参考",
    }


def _get_geku_xiyong(geku_name: str) -> List[str]:
    """根据格局类型获取格局法喜用神"""
    GEKU_XIYONG: Dict[str, List[str]] = {
        "正官格": ["金", "土", "水"],
        "七杀格": ["金", "土", "水"],
        "正印格": ["金", "水", "火"],
        "偏印格": ["土", "金", "火"],
        "正财格": ["火", "金", "木"],
        "偏财格": ["火", "金", "木"],
        "食神格": ["土", "金", "水"],
        "伤官格": ["土", "金", "火"],
        "比肩格": ["金", "水", "土"],
        "劫财格": ["金", "水", "土"],
    }
    # 通用规则：取格局所成之十神对应的五行
    return GEKU_XIYONG.get(geku_name, ["土"])


def _get_geku_ji(geku_name: str) -> List[str]:
    """根据格局类型获取格局法忌神"""
    GEKU_JI: Dict[str, List[str]] = {
        "正官格": ["木", "火", "水"],
        "七杀格": ["木", "火", "金"],
        "正印格": ["木", "土", "金"],
        "偏印格": ["木", "水", "火"],
        "正财格": ["木", "水", "土"],
        "偏财格": ["木", "水", "土"],
        "食神格": ["木", "水", "金"],
        "伤官格": ["水", "木", "金"],
        "比肩格": ["木", "火", "水"],
        "劫财格": ["木", "火", "水"],
    }
    return GEKU_JI.get(geku_name, ["木"])


# ============================================================
# 4. 双轨法融合：格局法 vs 传统喜用神
# ============================================================

def merge_gefasi_xys(
    gefasi_result: Dict[str, Any],
    xiyongshen_v2_result: Dict[str, Any],
    special_pattern: Dict[str, Any],
) -> Dict[str, Any]:
    """
    双轨法融合：格局法喜用神 vs 传统喜用神（调候+扶抑）

    融合策略：
    1. 特殊格局 → 格局法为主，传统喜用神仅作辅助参考
    2. 普通格局已成 → 格局法优先，传统喜用神补充调候
    3. 普通格局未成 → 传统喜用神优先，格局法辅助

    Args:
        gefasi_result: get_xiyong_by_gefasi() 返回结果
        xiyongshen_v2_result: determine_xiyongshen_v2() 返回结果
        special_pattern: detect_special_pattern() 返回结果

    Returns:
        {
            "merged_xys": List[str],      # 融合后喜用神
            "merged_js": List[str],        # 融合后忌神
            "strategy": str,               # 融合策略
            "gefasi_weight": str,          # 格局法权重
            "xys_weight": str,             # 传统喜用权重
            "conflict": List[str],         # 冲突项
            "unified": List[str],          # 共识项（两者皆喜）
            "gefasi_only": List[str],     # 仅格局法认可
            "xys_only": List[str],        # 仅传统认可
            "reason": str,
        }
    """
    gefasi_xys = set(gefasi_result.get("xiyong", []))
    gefasi_js = set(gefasi_result.get("ji", []))
    xys_xys = set(xiyongshen_v2_result.get("xiyongshen", []))
    xys_js = set(xiyongshen_v2_result.get("jishen", []))

    # 共识 & 冲突
    unified = list(gefasi_xys & xys_xys)
    conflict = list((gefasi_xys & xys_js) | (gefasi_js & xys_xys))
    gefasi_only = list(gefasi_xys - xys_xys)
    xys_only = list(xys_xys - gefasi_xys)

    # 融合策略
    if special_pattern.get("is_detected"):
        strategy = "格局优先"
        gefasi_weight = "主导（特殊格局）"
        xys_weight = "辅助参考"
        merged_xys = list(gefasi_xys)
        merged_js = list(gefasi_js | xys_js)
        reason = (
            f"特殊格局（{special_pattern.get('sub_type','')}）已成立，"
            f"以格局法喜用{gefasi_xys}为主，传统喜用{xys_xys}仅供参考"
        )
    elif gefasi_result.get("source", "").startswith("普通格局"):
        cheng_level = gefasi_result.get("principle", "")
        if "上等" in gefasi_result.get("adjustment", ""):
            strategy = "格局主导"
            gefasi_weight = "主导"
            xys_weight = "辅助参考"
            merged_xys = list(gefasi_xys | set(xys_only[:1]))  # 取格局用神 + 传统补充1个
            merged_js = list(xys_js)
            reason = (
                f"普通格局上等成格，以格局法喜用{gefasi_xys}为主导，"
                f"传统喜用{xys_xys}中的{xys_only}可辅助补充"
            )
        else:
            strategy = "格局/传统均衡"
            gefasi_weight = "各半"
            xys_weight = "各半"
            merged_xys = list((gefasi_xys | xys_xys) - xys_js - gefasi_js)
            merged_js = list((xys_js | gefasi_js) - gefasi_xys - xys_xys)
            reason = (
                f"普通格局{cheng_level}成格，格局法{gefasi_xys}与传统{xys_xys}各有侧重，"
                f"取并集{merged_xys}，共识项{unified}"
            )
    else:
        strategy = "传统优先"
        gefasi_weight = "辅助参考"
        xys_weight = "主导"
        merged_xys = list(xys_xys)
        merged_js = list(xys_js)
        reason = (
            f"格局未成/破格，以传统喜用神{xys_xys}为主导，"
            f"格局法喜用{gefasi_xys}仅供参考"
        )

    # 去重、排序（优先格局法共识）
    merged_xys = _prioritize_xys(list(merged_xys), unified, gefasi_only, xys_only)
    merged_js = list(dict.fromkeys(merged_js))[:3]

    return {
        "merged_xys": merged_xys[:3],
        "merged_js": merged_js[:3],
        "strategy": strategy,
        "gefasi_weight": gefasi_weight,
        "xys_weight": xys_weight,
        "conflict": conflict,
        "unified": unified,
        "gefasi_only": gefasi_only,
        "xys_only": xys_only,
        "reason": reason,
    }


def _prioritize_xys(
    merged: List[str],
    unified: List[str],
    gefasi_only: List[str],
    xys_only: List[str],
) -> List[str]:
    """优先保留共识项，再加格局法独有，最后加传统独有"""
    result = []
    seen = set()

    # 先加共识
    for x in unified:
        if x not in seen:
            result.append(x)
            seen.add(x)

    # 再加格局法独有
    for x in gefasi_only:
        if x not in seen:
            result.append(x)
            seen.add(x)

    # 再加传统独有（降权）
    for x in xys_only:
        if x not in seen:
            result.append(x)
            seen.add(x)

    # 保留原 merged 顺序中非上述的
    for x in merged:
        if x not in seen:
            result.append(x)
            seen.add(x)

    return result[:3]


# ============================================================
# 5. 综合格局分析主函数
# ============================================================

def analyze_gefasi(
    bazi: Dict[str, Any],
    rizhu_strength: Dict[str, Any],
    pattern_result: Dict[str, Any],
    xiyongshen_v2_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    子平格局法综合分析

    输入：八字 + 日主强弱 + 格局分析结果 + （可选）喜用神V2结果

    输出：
    1. 特殊格局检测结果
    2. 普通格局信息（含格局法喜用神）
    3. 格局-日主配合判定
    4. 双轨融合结果
    5. 综合喜用神建议

    Args:
        bazi: 八字字典
        rizhu_strength: 日主强弱结果
        pattern_result: analyze_pattern() 返回结果（从 pattern_method.py）
        xiyongshen_v2_result: determine_xiyongshen_v2() 返回结果（可选）

    Returns:
        {
            "special_pattern": {...},    # 特殊格局检测
            "pattern_summary": {...},    # 普通格局摘要
            "peihe_info": {...},         # 格局-日主配合
            "gefasi_xys": {...},         # 格局法喜用神
            "merge_result": {...},       # 双轨融合结果
            "final_xys": List[str],      # 最终喜用神（五行）
            "final_js": List[str],       # 最终忌神（五行）
            "summary": str,             # 一句话总结
            "confidence": float,         # 置信度
        }
    """
    # 收集四柱天干
    all_stems = [
        ("年干", bazi["year"]["stem"]),
        ("月干", bazi["month"]["stem"]),
        ("日干", bazi["day"]["stem"]),
        ("时干", bazi["hour"]["stem"]),
    ]

    # 1. 特殊格局检测
    special_result = detect_special_pattern(bazi, rizhu_strength, all_stems)

    # 2. 普通格局信息
    pattern_info = pattern_result.get("pattern_info", {})
    cheng_info = pattern_result.get("cheng_info", {})

    # 3. 格局-日主配合判定（仅普通格局需要）
    if special_result["is_detected"]:
        peihe_info = {
            "peihe_type": "日主从格",
            "peihe_level": "不适用",
            "score": 100,
            "reason": f"特殊格局（{special_result['sub_type']}），日主从乎格局",
            "suggestion": "日主无独立旺衰，以格局气势为主",
            "day_requirement": "不适用（日主从格局）",
        }
    else:
        peihe_info = judge_pattern_day_strength(pattern_info, cheng_info, rizhu_strength)

    # 4. 格局法喜用神
    gefasi_xys = get_xiyong_by_gefasi(pattern_info, cheng_info, special_result, peihe_info)

    # 5. 双轨融合
    if xiyongshen_v2_result:
        merge_result = merge_gefasi_xys(gefasi_xys, xiyongshen_v2_result, special_result)
        final_xys = merge_result["merged_xys"]
        final_js = merge_result["merged_js"]
        strategy_desc = f"策略={merge_result['strategy']}，格局权重={merge_result['gefasi_weight']}，传统权重={merge_result['xys_weight']}"
    else:
        merge_result = {}
        final_xys = gefasi_xys["xiyong"]
        final_js = gefasi_xys["ji"]
        strategy_desc = "仅格局法（无传统喜用数据）"

    # 6. 置信度
    confidence = _calc_confidence(special_result, pattern_info, cheng_info, peihe_info)

    # 7. 总结
    if special_result["is_detected"]:
        summary = (
            f"{special_result['sub_type']}（{special_result['type']}），"
            f"格局法喜用{final_xys}，忌{final_js}。"
            f"{strategy_desc}。"
        )
    else:
        geku_name = pattern_info.get("pattern", "")
        cheng_level = cheng_info.get("level", "未知")
        summary = (
            f"普通格局{geku_name}{cheng_level}成格，"
            f"格局-日主{peihe_info['peihe_type']}（{peihe_info['peihe_level']}等配合），"
            f"格局法喜用{gefasi_xys['xiyong']}，"
            f"最终喜用{final_xys}，忌{final_js}。"
            f"{strategy_desc}。"
        )

    return {
        "special_pattern": special_result,
        "pattern_summary": {
            "pattern": pattern_info.get("pattern", ""),
            "pattern_type": pattern_info.get("pattern_type", ""),
            "tou_level": pattern_info.get("tou_level", ""),
            "reason": pattern_info.get("reason", ""),
            "cheng_level": cheng_info.get("level", "未知"),
            "is_cheng": cheng_info.get("is_cheng", False),
            "cheng_factors": cheng_info.get("factors", []),
            "poge_reason": cheng_info.get("poge_reason", ""),
        },
        "peihe_info": peihe_info,
        "gefasi_xys": gefasi_xys,
        "merge_result": merge_result,
        "final_xys": final_xys,
        "final_js": final_js,
        "summary": summary,
        "confidence": confidence,
    }


def _calc_confidence(
    special_pattern: Dict[str, Any],
    pattern_info: Dict[str, Any],
    cheng_info: Dict[str, Any],
    peihe_info: Dict[str, Any],
) -> float:
    """计算格局法置信度"""
    score = 0.3  # 基础

    if special_pattern["is_detected"]:
        score += special_pattern.get("confidence", 0.8)

    if pattern_info.get("tou_level") == "本气":
        score += 0.15
    elif pattern_info.get("tou_level") == "中气":
        score += 0.08
    else:
        score += 0.0

    if cheng_info.get("is_cheng"):
        score += 0.15
        if cheng_info.get("level") == "上等":
            score += 0.1

    if peihe_info.get("peihe_level") in ["上", "中上"]:
        score += 0.1

    return min(round(score, 2), 1.0)


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    import sys
    sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
    try:
        from bazi_engine import get_bazi
        from pattern_method import analyze_pattern
        from xiyongshen_v2 import determine_xiyongshen_v2
        from rizhu_strength_v2 import get_rizhu_strength_v2
    except ImportError:
        print("(import skipped in minimal env)")
        get_bazi = None

    if get_bazi:
        print("=" * 60)
        print("子平格局法 · 格法测试")
        print("=" * 60)

        # 测试1：普通格局（正官格）
        print("\n【测试1】普通格局 — 壬寅年 辛亥月 甲午日 甲子时")
        bazi1 = get_bazi(2024, 11, 15, 23)["bazi"]
        strength1 = get_rizhu_strength_v2(bazi1)
        pattern1 = analyze_pattern(bazi1)
        result1 = analyze_gefasi(bazi1, strength1, pattern1)
        print(f"  特殊格局: {result1['special_pattern']['type']} {result1['special_pattern']['sub_type']}")
        print(f"  普通格局: {result1['pattern_summary']['pattern']} "
              f"{result1['pattern_summary']['tou_level']}透 "
              f"{result1['pattern_summary']['cheng_level']}成")
        print(f"  格局-日主配合: {result1['peihe_info']['peihe_type']} "
              f"({result1['peihe_info']['peihe_level']}等)")
        print(f"  格局法喜用: {result1['gefasi_xys']['xiyong']} "
              f"忌: {result1['gefasi_xys']['ji']}")
        print(f"  最终喜用: {result1['final_xys']} 忌: {result1['final_js']}")
        print(f"  置信度: {result1['confidence']}")
        print(f"  总结: {result1['summary']}")

        # 测试2：曲直格（专旺格）
        print("\n【测试2】专旺格 — 甲寅年 壬寅月 甲寅日 乙亥时")
        bazi2 = get_bazi(2024, 2, 15, 22)["bazi"]
        strength2 = get_rizhu_strength_v2(bazi2)
        pattern2 = analyze_pattern(bazi2)
        result2 = analyze_gefasi(bazi2, strength2, pattern2)
        print(f"  特殊格局: {result2['special_pattern']['type']} {result2['special_pattern']['sub_type']}")
        print(f"  检测置信度: {result2['special_pattern']['confidence']}")
        print(f"  格局法喜用: {result2['gefasi_xys']['xiyong']} "
              f"忌: {result2['gefasi_xys']['ji']}")
        print(f"  总结: {result2['summary']}")

        # 测试3：化气格
        print("\n【测试3】化气格候选 — 己丑年 甲戌月 己丑日 甲戌时（甲己合化土）")
        bazi3 = get_bazi(2024, 9, 15, 12)["bazi"]
        strength3 = get_rizhu_strength_v2(bazi3)
        pattern3 = analyze_pattern(bazi3)
        result3 = analyze_gefasi(bazi3, strength3, pattern3)
        print(f"  特殊格局: {result3['special_pattern']['type']} "
              f"{result3['special_pattern']['sub_type']}")
        print(f"  检测置信度: {result3['special_pattern']['confidence']}")
        print(f"  格局法喜用: {result3['gefasi_xys']['xiyong']} "
              f"忌: {result3['gefasi_xys']['ji']}")
        print(f"  总结: {result3['summary']}")

        # 测试4：配合主函数输出
        print("\n【测试4】双轨融合 — 与 xiyongshen_v2 联合输出")
        try:
            tiao_hou = {}  # 简化：无调候数据
            from yueling_canggan import get_yueling_canggan
            ylcg = get_yueling_canggan(bazi1)
            xys2 = determine_xiyongshen_v2(bazi1, strength1, tiao_hou, ylcg, pattern1)
            result4 = analyze_gefasi(bazi1, strength1, pattern1, xys2)
            print(f"  传统喜用神V2: {xys2.get('xiyongshen', [])}")
            print(f"  融合策略: {result4['merge_result'].get('strategy', 'N/A')}")
            print(f"  共识项: {result4['merge_result'].get('unified', [])}")
            print(f"  冲突项: {result4['merge_result'].get('conflict', [])}")
            print(f"  格局权重: {result4['merge_result'].get('gefasi_weight', 'N/A')}")
            print(f"  最终喜用: {result4['final_xys']}")
            print(f"  最终忌神: {result4['final_js']}")
        except Exception as e:
            print(f"  (联合测试跳过: {e})")

        print("\n" + "=" * 60)
        print("测试完成")
