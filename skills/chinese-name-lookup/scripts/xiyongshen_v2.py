#!/usr/bin/env python3
"""
喜用神判定 V2 - 本地综合判定（调候优先/格局已成/月令司令）
集成穷通宝鉴调候 + 子平格局法 + 扶抑综合判定

核心逻辑：
1. 调候是否紧急？ → 穷通宝鉴核心原则
2. 格局是否已成？ → 子平真诠核心
3. 藏干透出影响   → 月令司令分析
4. 剩余按调候+扶抑综合判定
"""

from typing import Dict, List, Any, Tuple, Optional

# 导入现有模块（不导入 bazi_engine 以避免循环依赖）
from tiao_hou_judge import (
    is_tiao_hou_urgent,
    resolve_conflict,
    judge_tiao_hou_priority,
)

# ============================================================
# 天干/地支/五行常量（从 bazi_engine.py 复制定义）
# ============================================================

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ELEMENT_NAMES = ["木", "火", "土", "金", "水"]

# 日干五行索引：0=木, 1=火, 2=土, 3=金, 4=水
# 天干→五行（字符=木,1=火,2=土,3=金,4=水）
STEM_ELEMENTS = {
    "甲": "木", "乙": "木",   # 木
    "丙": "火", "丁": "火",   # 火
    "戊": "土", "己": "土",   # 土
    "庚": "金", "辛": "金",   # 金
    "壬": "水", "癸": "水",   # 水
}

STEM_ELEM_IDX: Dict[str, int] = STEM_ELEMENTS  # str key 版本（用于天干字符串）
STEM_IDX: Dict[str, int] = {g: i for i, g in enumerate(HEAVENLY_STEMS)}

# 月支五行索引
BRANCH_ELEMENTS = {
    0: 4,  # 子 -> 水
    1: 2,  # 丑 -> 土
    2: 0,  # 寅 -> 木
    3: 0,  # 卯 -> 木
    4: 2,  # 辰 -> 土
    5: 1,  # 巳 -> 火
    6: 1,  # 午 -> 火
    7: 2,  # 未 -> 土
    8: 3,  # 申 -> 金
    9: 3,  # 酉 -> 金
    10: 2, # 戌 -> 土
    11: 4, # 亥 -> 水
}

WUXING_MAP: Dict[str, str] = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}


# ============================================================
# 1. 调候喜用神提取
# ============================================================

def get_tiao_hou_xiyong_wuxing(tiao_hou: Dict[str, Any]) -> List[str]:
    """
    从调候数据中提取五行层面的喜用神

    Args:
        tiao_hou: {"喜用": ["丙", "癸"], "忌避": [...], "原则": str}

    Returns:
        五行名称列表，如 ["火", "水"]
    """
    xiyong_gan = tiao_hou.get("喜用", [])
    wuxing_set = set()
    for g in xiyong_gan:
        w = WUXING_MAP.get(g)
        if w:
            wuxing_set.add(w)
    return list(wuxing_set)


def get_tiao_hou_jibi_wuxing(tiao_hou: Dict[str, Any]) -> List[str]:
    """从调候忌避中提取五行"""
    jibi_gan = tiao_hou.get("忌避", [])
    wuxing_set = set()
    for g in jibi_gan:
        w = WUXING_MAP.get(g)
        if w:
            wuxing_set.add(w)
    return list(wuxing_set)


# ============================================================
# 2. 扶抑喜用神计算（V1 核心逻辑，提取为独立函数）
# ============================================================

def compute_fuyi_xys(
    bazi: Dict[str, Any],
    rizhu_strength: Dict[str, Any],
) -> Tuple[List[str], List[str]]:
    """
    基于扶抑原则计算喜用神（V1 逻辑，五行层面）

    Args:
        bazi: 八字字典
        rizhu_strength: 日主强弱结果

    Returns:
        (xiyongshen_list, jishen_list)
    """
    day_stem = bazi["day"]["stem"]
    day_elem = STEM_ELEMENTS.get(day_stem, "木")  # 直接用字符串映射
    _ELEM_LIST = ["木", "火", "土", "金", "水"]
    day_elem_idx = _ELEM_LIST.index(day_elem) if day_elem in _ELEM_LIST else 0
    day_elem = STEM_ELEMENTS.get(day_stem, "木")  # 直接用字符串映射

    is_strong = rizhu_strength["strength"] in ["强", "过强", "偏旺", "旺"]
    is_weak = rizhu_strength["strength"] in ["弱", "过弱", "偏弱"]

    xiyongshen = []
    jishen = []

    if is_strong:
        # 身强：喜克/泄（官鬼、食伤、财）
        # 官鬼：克日干 → (day_elem_idx + 3) % 5
        guiji_idx = (day_elem_idx + 3) % 5
        xiyongshen.append(ELEMENT_NAMES[guiji_idx])

        # 食伤：日干所生 → (day_elem_idx + 1) % 5
        shishang_idx = (day_elem_idx + 1) % 5
        xiyongshen.append(ELEMENT_NAMES[shishang_idx])

        # 财：日干所克 → (day_elem_idx + 2) % 5
        cai_idx = (day_elem_idx + 2) % 5
        xiyongshen.append(ELEMENT_NAMES[cai_idx])

        # 印枭为忌
        yin_idx = (day_elem_idx + 4) % 5
        jishen.append(ELEMENT_NAMES[yin_idx])
        # 比劫也可能为忌（身强不需要比劫助）
        jishen.append(day_elem)  # 同气为忌

    elif is_weak:
        # 身弱：喜生扶（印枭、比劫）
        # 印枭：生我者 → (day_elem_idx + 4) % 5
        yin_idx = (day_elem_idx + 4) % 5
        xiyongshen.append(ELEMENT_NAMES[yin_idx])

        # 比劫：同我者
        xiyongshen.append(day_elem)

        # 官鬼、食伤、财为忌
        guiji_idx = (day_elem_idx + 3) % 5
        shishang_idx = (day_elem_idx + 1) % 5
        cai_idx = (day_elem_idx + 2) % 5
        jishen.extend([ELEMENT_NAMES[guiji_idx], ELEMENT_NAMES[shishang_idx], ELEMENT_NAMES[cai_idx]])

    else:
        # 中和：调候为主，扶抑为辅
        # 简化：取土（中性）或其他平衡五行
        # 日主偏旺时，优先考虑财星（泄日主）
        _elem_idx = ["木", "火", "土", "金", "水"].index(day_elem) if day_elem in ["木", "火", "土", "金", "水"] else 0
        cai_elem = ["木", "火", "土", "金", "水"][(_elem_idx + 2) % 5]
        xiyongshen = [day_elem, cai_elem]  # 日主 + 财
        jishen = []

    # 去重，保持顺序
    xiyongshen = list(dict.fromkeys(xiyongshen))
    jishen = list(dict.fromkeys(jishen))

    return xiyongshen, jishen


# ============================================================
# 3. 格局微调
# ============================================================

def adjust_by_pattern(
    xiyong: List[str],
    jishen: List[str],
    pattern_result: Dict[str, Any],
    day_stem: str,
) -> Tuple[List[str], List[str], str]:
    """
    根据格局情况微调喜用神

    规则（子平真诠）：
    - 格局已成 → 格局用神方向不可损害，喜用神向格局靠拢
    - 官格成且无破 → 官星为用，印星次之
    - 食神格 → 喜财星
    - 印格成 → 喜官杀或食伤泄秀
    - 格局未成或破格 → 回归扶抑原则

    Args:
        xiyong: 原始喜用神列表（五行）
        jishen: 原始忌神列表（五行）
        pattern_result: 格局分析结果
        day_stem: 日干

    Returns:
        (adjusted_xys, adjusted_js, pattern_direction)
    """
    if not pattern_result:
        return xiyong, jishen, ""

    pattern_info = pattern_result.get("pattern_info", {})
    cheng_info = pattern_result.get("cheng_info", {})

    geku_name = pattern_info.get("pattern", "")
    is_cheng = cheng_info.get("is_cheng", False)
    level = cheng_info.get("level", "未知")

    if not geku_name or not is_cheng:
        return xiyong, jishen, "格局未成/破格，维持扶抑"

    # 格局已成的微调规则
    direction = ""

    if "官格" in geku_name:
        # 正官/七杀格：官星为用，印星护官
        if "金" not in xiyong and "金" in ELEMENT_NAMES:
            # 官星对应的五行
            xiyong_adj = [w for w in xiyong if w != "木"]  # 官格忌木
            xiyong_adj = list(dict.fromkeys(xiyong_adj + ["金", "土"]))
            xiyong = xiyong_adj
        direction = "官格已成，顺官星用事"

    elif "食神格" in geku_name:
        # 食神格：喜财星泄食
        if "土" not in xiyong:
            xiyong = list(dict.fromkeys(["土"] + xiyong))
        direction = "食神格已成，喜财星泄秀"

    elif "印格" in geku_name or "偏印格" in geku_name:
        # 印格：喜官杀生印，或食伤泄秀
        direction = "印格已成，喜官杀或泄秀"

    elif "财格" in geku_name:
        # 财格：身旺任财
        direction = "财格已成，身旺任财"

    elif "伤官格" in geku_name:
        # 伤官格：喜配印或财星
        direction = "伤官格已成，喜配印或财星"

    else:
        direction = f"{geku_name}{level}，格局已定"

    # 忌神调整：格局已成时，忌神不应破坏格局核心
    # 如果忌神中有破坏格局的字，适当调整
    # 这里简化处理：如果格局成且level较高，忌神范围缩小
    if level == "上等":
        # 上等格局，忌神应避开破坏格局的因素
        jishen_adj = [w for w in jishen if w not in xiyong]
        jishen = list(dict.fromkeys(jishen_adj))

    return xiyong, jishen, direction


# ============================================================
# 4. 调候融合
# ============================================================

def merge_by_tiao_hou(
    xiyong_fuyi: List[str],
    jishen_fuyi: List[str],
    tiao_hou: Dict[str, Any],
    is_tiao_hou_urgent_flag: bool,
    priority_info: Dict[str, Any],
    wuxing_power: Optional[Dict[str, float]] = None,
) -> Tuple[List[str], List[str], str]:
    """
    融合调候用神与扶抑用神

    Args:
        xiyong_fuyi: 扶抑喜用神（五行）
        jishen_fuyi: 扶抑忌神（五行）
        tiao_hou: 穷通宝鉴调候数据
        is_tiao_hou_urgent_flag: 调候是否紧急
        priority_info: judge_tiao_hou_priority 返回的详细信息

    Returns:
        (merged_xys, merged_js, merge_reason)
    """
    if not tiao_hou:
        return xiyong_fuyi, jishen_fuyi, "无调候数据，维持扶抑"

    tiao_hou_xiyong = get_tiao_hou_xiyong_wuxing(tiao_hou)
    tiao_hou_jibi = get_tiao_hou_jibi_wuxing(tiao_hou)

    if not tiao_hou_xiyong:
        return xiyong_fuyi, jishen_fuyi, "调候数据为空，维持扶抑"

    # 使用 resolve_conflict 进行融合
    if is_tiao_hou_urgent_flag:
        conflict_result = resolve_conflict(tiao_hou_xiyong, xiyong_fuyi, "tiao_hou")
    else:
        conflict_result = resolve_conflict(tiao_hou_xiyong, xiyong_fuyi, "fuyi")

    preferred = conflict_result["preferred"]
    secondary = conflict_result["secondary"]
    strategy = conflict_result["strategy"]

    # 合并：优先满足 preferred
    # 对于 fuyi_first（调候不紧急），secondary 仅取有力量者（>=15分），避免引入弱五行
    if strategy == "fuyi_first" and wuxing_power:
        secondary_filtered = [s for s in secondary if wuxing_power.get(s, 0) >= 15]
    else:
        secondary_filtered = secondary
    merged_xys = list(dict.fromkeys(preferred + [s for s in secondary_filtered if s not in preferred]))
    merged_xys = merged_xys[:3]  # 最多3个

    # 忌神：调候忌避 + 扶抑忌神（去掉已被喜用神覆盖的）
    merged_js = list(dict.fromkeys(jishen_fuyi + [j for j in tiao_hou_jibi if j not in merged_xys]))
    merged_js = [j for j in merged_js if j not in merged_xys]  # 排除喜用
    merged_js = merged_js[:3]

    merge_reason = (
        f"调候{'紧急' if is_tiao_hou_urgent_flag else '不紧急'}，"
        f"策略={strategy}，"
        f"调候喜用{tiao_hou_xiyong}，扶抑喜用{xiyong_fuyi}，"
        f"融合后喜用{merged_xys}，忌神{merged_js}"
    )

    return merged_xys, merged_js, merge_reason


# ============================================================
# 5. 置信度评估
# ============================================================

def calculate_confidence(
    result: Dict[str, Any],
    bazi: Dict[str, Any],
    pattern_result: Optional[Dict[str, Any]],
    tiao_hou: Optional[Dict[str, Any]],
) -> float:
    """
    计算喜用神判定的置信度（0-1）

    评估因素：
    1. 格局是否已成（+0.2）
    2. 调候是否紧急（+0.1）
    3. 调候数据是否完整（+0.15）
    4. 藏干透出级别（本气+0.1, 中气+0.05, 余气+0）
    5. 格局level（上等+0.15, 中等+0.1, 下等+0.05, 破格+0）
    6. 冲突程度（无/轻+0.15, 中+0.1, 重+0）

    Args:
        result: 当前判定结果
        bazi: 八字字典
        pattern_result: 格局分析结果
        tiao_hou: 调候数据

    Returns:
        置信度 0.0-1.0
    """
    score = 0.0

    # 基础分：V1 算法基础
    base = 0.25
    score += base

    # 格局加成
    if pattern_result:
        cheng_info = pattern_result.get("cheng_info", {})
        is_cheng = cheng_info.get("is_cheng", False)
        level = cheng_info.get("level", "未知")

        if is_cheng:
            score += 0.20  # 格局已成
            if level == "上等":
                score += 0.15
            elif level == "中等":
                score += 0.10
            elif level == "下等":
                score += 0.05

        # 透干级别加成
        pattern_info = pattern_result.get("pattern_info", {})
        tou_level = pattern_info.get("tou_level", "")
        if tou_level == "本气":
            score += 0.10
        elif tou_level == "中气":
            score += 0.05
        # 余气/无透 不加分

    # 调候加成
    if tiao_hou and tiao_hou.get("喜用"):
        score += 0.15  # 有完整调候数据
        if result.get("tiao_hou_urgent"):
            score += 0.10  # 调候紧急，更有把握

    # 无冲突或轻微冲突加成
    if result.get("tiao_hou_urgent"):
        # 有调候优先的情况，置信度更高
        score += 0.05

    # 约束：最高1.0
    return min(round(score, 2), 1.0)


# ============================================================
# 6. 主判定函数
# ============================================================

def determine_xiyongshen_v2(
    bazi: Dict[str, Any],
    rizhu_strength: Dict[str, Any],
    tiao_hou: Dict[str, Any],
    yueling_canggan: Dict[str, Any],
    pattern_result: Dict[str, Any],
    wuxing_power: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    综合喜用神判定 V2

    判定顺序：
    1. 调候是否紧急？（穷通宝鉴核心原则）
    2. 格局是否已成？（子平真诠核心）
    3. 藏干透出影响
    4. 剩余按调候+扶抑综合判定

    Args:
        bazi: 八字字典（包含 year/month/day/hour 四柱）
        rizhu_strength: 日主强弱结果
            {"strength": "强"/"弱"/"中", "score": int, ...}
        tiao_hou: 穷通宝鉴调候数据
            {"喜用": [...], "忌避": [...], "原则": str}
        yueling_canggan: 月令藏干
            {"本气": str, "中气": str, "余气": str}
        pattern_result: 格局分析结果
            {"pattern_info": {...}, "cheng_info": {...}}

    Returns:
        {
            "xiyongshen": ["金", "水"],
            "jishen": ["木", "火"],
            "qiangruo": "弱",
            "tiao_hou_urgent": True,
            "pattern_cheng": "官格",
            "analysis": "辰月子月生，寒水进气...",
            "method": "v2_local",
            "confidence": 0.75
        }
    """
    # 提取关键信息
    day_stem = bazi["day"]["stem"]
    month_branch = bazi["month"]["branch"]
    month_stem = bazi["month"]["stem"]
    # 使用 wuxing_power_strength 覆盖 rizhu_strength，以获得更准确的用神判定
    # "偏旺"应视为身强处理（需抑），而非中和
    _wx_strength = wuxing_power.get("strength") if wuxing_power else None
    if _wx_strength in ["偏旺", "旺", "过旺", "强", "过强"]:
        _effective_strength = "强"
    elif _wx_strength in ["偏弱", "弱", "过弱"]:
        _effective_strength = "弱"
    else:
        _effective_strength = "中"
    strength_str = _effective_strength

    # ---------- Step 1: 调候是否紧急 ----------
    tiao_hou_urgent, tiao_hou_reason = is_tiao_hou_urgent(
        yue_zhi=month_branch,
        month_stem=month_stem,
        rizhu=day_stem,
        rizhu_strength=strength_str,
    )

    # ---------- Step 2: 格局分析 ----------
    pattern_info = pattern_result.get("pattern_info", {}) if pattern_result else {}
    cheng_info = pattern_result.get("cheng_info", {}) if pattern_result else {}

    geku_name = pattern_info.get("pattern", "未知")
    is_cheng = cheng_info.get("is_cheng", False)
    pattern_level = cheng_info.get("level", "未知")
    tou_level = pattern_info.get("tou_level", "无透")
    tougan = pattern_info.get("tou_stem")  # 透出之干

    # ---------- Step 3: 扶抑用神 ----------
    # 使用有效强度（wuxing_power_strength 覆盖后的）来计算扶抑用神
    _rizhu_for_fuyi = dict(rizhu_strength, strength=_effective_strength)
    xiyong_fuyi, jishen_fuyi = compute_fuyi_xys(bazi, _rizhu_for_fuyi)

    # 偏旺时：同类木火已旺，官鬼水力极弱（<15分）且对木旺无益，从喜用移除
    # 同时同类木从食伤位加入忌神
    if _effective_strength == "强" and wuxing_power and _wx_strength in ["偏旺", "旺"]:
        day_elem = STEM_ELEMENTS.get(bazi["day"]["stem"], "木")
        elem_idx = ["木", "火", "土", "金", "水"].index(day_elem) if day_elem in ["木", "火", "土", "金", "水"] else 0
        guiji_elem = ["木", "火", "土", "金", "水"][(elem_idx + 3) % 5]  # 官鬼
        sheng_elem = ["木", "火", "土", "金", "水"][(elem_idx + 1) % 5]  # 食伤
        # 官鬼极弱则移除
        if guiji_elem in xiyong_fuyi and wuxing_power.get(guiji_elem, 0) < 15:
            xiyong_fuyi = [e for e in xiyong_fuyi if e != guiji_elem]
        # 同类（木/火）从食伤位加入忌神（偏旺时比劫为忌）
        if sheng_elem in xiyong_fuyi and wuxing_power.get(sheng_elem, 0) >= wuxing_power.get(day_elem, 0) * 0.8:
            xiyong_fuyi = [e for e in xiyong_fuyi if e != sheng_elem]
            if sheng_elem not in jishen_fuyi:
                jishen_fuyi.append(sheng_elem)

    # ---------- Step 4: 调候优先判断 ----------
    # 构造 judge_tiao_hou_priority 需要的数据格式
    bazi_for_priority = {
        "bazi": {
            "day": {"stem": day_stem},
            "month": {"stem": month_stem, "branch": month_branch},
        },
        "xiyongshen": {"xiyongshen": xiyong_fuyi},
    }
    priority_info = judge_tiao_hou_priority(bazi_for_priority, rizhu_strength, tiao_hou)

    # ---------- Step 5: 格局微调 ----------
    xiyong_after_pattern, jishen_after_pattern, pattern_direction = adjust_by_pattern(
        xiyong_fuyi, jishen_fuyi, pattern_result, day_stem
    )

    # ---------- Step 6: 调候融合 ----------
    merged_xys, merged_js, merge_reason = merge_by_tiao_hou(
        xiyong_after_pattern,
        jishen_after_pattern,
        tiao_hou,
        tiao_hou_urgent,
        priority_info,
        wuxing_power,
    )

    # ---------- Step 7: 组装分析说明 ----------
    # 生成详细的分析说明
    analysis_parts = []

    # 月令描述
    yueling_desc = f"月令{month_branch}"
    if yueling_canggan:
        bq = yueling_canggan.get("本气", "")
        zq = yueling_canggan.get("中气", "")
        yz = yueling_canggan.get("余气")
        yz_str = f"、余气{yz}" if yz else ""
        yueling_desc += f"（本气{bq}、中气{zq}{yz_str}）"

    analysis_parts.append(f"{yueling_desc}生，")

    # 调候
    if tiao_hou and tiao_hou.get("原则"):
        tiao_princ = tiao_hou.get("原则", "")
        analysis_parts.append(f"调候：{tiao_princ}。")

    if tiao_hou_urgent:
        analysis_parts.append(f"调候紧急（{tiao_hou_reason[:20]}），调候用神优先。")
    else:
        analysis_parts.append(f"调候不紧急，以扶抑为主。")

    # 格局
    if geku_name != "未知":
        cheng_str = "已成" if is_cheng else "未成/破格"
        analysis_parts.append(f"格局：{geku_name}{cheng_str}（{pattern_level}，{tou_level}透干）。")

    # 藏干透出
    if tougan:
        wuxing_tg = WUXING_MAP.get(tougan, tougan)
        analysis_parts.append(f"月令{tougan}（{wuxing_tg}）透出，影响格局力度。")

    # 融合结果
    analysis_parts.append(
        f"喜用神：{','.join(merged_xys) or '待定'}；忌神：{','.join(merged_js) or '无明显忌神'}。"
    )

    analysis = "".join(analysis_parts)

    # ---------- Step 8: 置信度 ----------
    confidence = calculate_confidence(
        result={
            "tiao_hou_urgent": tiao_hou_urgent,
            "pattern_cheng": geku_name if is_cheng else "未成",
        },
        bazi=bazi,
        pattern_result=pattern_result,
        tiao_hou=tiao_hou,
    )

    # ---------- Step 9: 组装结果 ----------
    result = {
        "xiyongshen": merged_xys,
        "jishen": merged_js,
        "qiangruo": strength_str,
        "tiao_hou_urgent": tiao_hou_urgent,
        "pattern_cheng": geku_name if is_cheng else None,
        "pattern_level": pattern_level if is_cheng else None,
        "tou_level": tou_level,
        "analysis": analysis,
        "method": "v2_local",
        "confidence": confidence,
        # 内部参考（调试用）
        "_debug": {
            "tiao_hou_reason": tiao_hou_reason,
            "tiao_hou_xiyong": get_tiao_hou_xiyong_wuxing(tiao_hou) if tiao_hou else [],
            "fuyi_xiyong": xiyong_fuyi,
            "priority_info": priority_info,
            "merge_reason": merge_reason,
            "pattern_direction": pattern_direction,
        },
    }

    return result


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    from bazi_engine import full_bazi_analysis, get_bazi

    print("=== 喜用神 V2 判定 测试 ===\n")

    # 测试1: 2024年3月15日10点（辰月，非寒热，调候不急）
    print("【测试1】2024年3月15日10点（辰月）")
    bazi_raw = full_bazi_analysis(2024, 3, 15, 10)
    bazi = bazi_raw["bazi"]
    print(f"  八字: {bazi_raw['birth_chart']}")
    print(f"  日主: {bazi_raw['rizhu_strength']['strength']} - {bazi_raw['rizhu_strength']['reason']}")

    result1 = determine_xiyongshen_v2(
        bazi=bazi,
        rizhu_strength=bazi_raw["rizhu_strength"],
        tiao_hou=bazi_raw.get("tiao_hou", {}),
        yueling_canggan=bazi_raw.get("yueling_canggan", {}),
        pattern_result={"pattern_info": bazi_raw.get("pattern", {}), "cheng_info": bazi_raw.get("pattern_cheng", {})},
    )
    print(f"  V2喜用神: {result1['xiyongshen']}")
    print(f"  V2忌神: {result1['jishen']}")
    print(f"  调候紧急: {result1['tiao_hou_urgent']}")
    print(f"  格局: {result1['pattern_cheng']} ({result1['pattern_level']})")
    print(f"  透干级别: {result1['tou_level']}")
    print(f"  置信度: {result1['confidence']}")
    print(f"  分析: {result1['analysis']}")
    print()

    # 对比V1
    print(f"  V1喜用神: {bazi_raw['xiyongshen']['xiyongshen']}")
    print(f"  V1忌神: {bazi_raw['xiyongshen']['jishen']}")
    print()

    # 测试2: 亥月生人（寒，调候紧急）
    print("【测试2】甲亥月生（亥月，寒，调候紧急）")
    # 模拟一个亥月生的八字
    bazi_test2 = {
        "day": {"stem": "甲", "stem_idx": 0},
        "month": {"stem": "壬", "branch": "亥", "stem_idx": 8, "branch_idx": 11},
        "year": {"stem": "丙", "stem_idx": 2},
        "hour": {"stem": "庚", "stem_idx": 6},
    }
    rizhu_test2 = {"strength": "弱", "score": 30}
    tiao_hou_test2 = {"喜用": ["庚", "辛", "戊", "丁"], "忌避": ["丙"], "原则": "水木司令用庚辛发水"}
    yueling_test2 = {"本气": "壬", "中气": "甲", "余气": None}
    pattern_test2 = {
        "pattern_info": {"pattern": "偏印格", "tou_level": "本气", "tou_stem": "壬"},
        "cheng_info": {"is_cheng": True, "level": "中等"},
    }

    result2 = determine_xiyongshen_v2(
        bazi=bazi_test2,
        rizhu_strength=rizhu_test2,
        tiao_hou=tiao_hou_test2,
        yueling_canggan=yueling_test2,
        pattern_result=pattern_test2,
    )
    print(f"  V2喜用神: {result2['xiyongshen']}")
    print(f"  调候紧急: {result2['tiao_hou_urgent']}")
    print(f"  分析: {result2['analysis']}")
    print(f"  置信度: {result2['confidence']}")
    print()

    # 测试3: 午月生人（热，调候紧急）
    print("【测试3】丙午月生（午月，热，调候紧急）")
    bazi_test3 = {
        "day": {"stem": "丙", "stem_idx": 2},
        "month": {"stem": "丁", "branch": "午", "stem_idx": 3, "branch_idx": 6},
        "year": {"stem": "庚", "stem_idx": 6},
        "hour": {"stem": "壬", "stem_idx": 8},
    }
    rizhu_test3 = {"strength": "强", "score": 70}
    tiao_hou_test3 = {"喜用": ["壬", "庚", "癸"], "忌避": ["丙", "丁", "己"], "原则": "水最急"}
    yueling_test3 = {"本气": "丁", "中气": "己", "余气": None}
    pattern_test3 = {
        "pattern_info": {"pattern": "食神格", "tou_level": "本气", "tou_stem": "丁"},
        "cheng_info": {"is_cheng": True, "level": "中等"},
    }

    result3 = determine_xiyongshen_v2(
        bazi=bazi_test3,
        rizhu_strength=rizhu_test3,
        tiao_hou=tiao_hou_test3,
        yueling_canggan=yueling_test3,
        pattern_result=pattern_test3,
    )
    print(f"  V2喜用神: {result3['xiyongshen']}")
    print(f"  调候紧急: {result3['tiao_hou_urgent']}")
    print(f"  分析: {result3['analysis']}")
    print(f"  置信度: {result3['confidence']}")
    print()

    print("=== 测试完成 ===")
