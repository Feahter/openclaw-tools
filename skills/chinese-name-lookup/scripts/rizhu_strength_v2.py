# -*- coding: utf-8 -*-
"""
日主强弱量化判定 v2 - 带权重算法
基于《千里命稿》《滴天髓》理论

权重分配：
- 月令旺相：40%（最重要）
- 地支通根：30%（是否得地）
- 天干比劫：20%（同类相助）
- 印星生助：10%

数据说明：
- 藏干表来源：yueling_canggan.py（已验证标准值）
- 长生表来源：shier_changsheng.py（已验证标准值）
"""

from typing import Dict, Any
from lunar_calendar import HEAVENLY_STEMS, EARTHLY_BRANCHES
from shier_changsheng import get_changsheng_state, CHANGSHENG_ORDER
from yueling_canggan import get_yueling_canggan

# ============================================================
# 五行天干地支常量（与 bazi_engine 保持一致）
# ============================================================
STEM_ELEMENTS = {
    0: 0,  # 甲 -> 木
    1: 0,  # 乙 -> 木
    2: 1,  # 丙 -> 火
    3: 1,  # 丁 -> 火
    4: 2,  # 戊 -> 土
    5: 2,  # 己 -> 土
    6: 3,  # 庚 -> 金
    7: 3,  # 辛 -> 金
    8: 4,  # 壬 -> 水
    9: 4,  # 癸 -> 水
}

ELEMENT_NAMES = ["木", "火", "土", "金", "水"]

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

# ============================================================
# 常量映射
# ============================================================
STEM_NAMES = HEAVENLY_STEMS
BRANCH_NAMES = EARTHLY_BRANCHES

TIAN_GAN_IDX = {name: i for i, name in enumerate(HEAVENLY_STEMS)}
ZHI_IDX = {name: i for i, name in enumerate(EARTHLY_BRANCHES)}


# ============================================================
# 月令权重表（十二长生状态 → 权重系数）
# ============================================================
# 临官/帝旺 = 1.0（最强）
# 长生/沐浴/冠带 = 0.7
# 临官附近 = 0.85
# 衰/病 = 0.4
# 死/墓/绝 = 0.2
# 胎/养 = 0.3
YUELING_WEIGHT_MAP = {
    "临官": 0.85,
    "帝旺": 1.0,
    "长生": 0.7,
    "沐浴": 0.7,
    "冠带": 0.7,
    "衰": 0.4,
    "病": 0.4,
    "死": 0.2,
    "墓": 0.2,
    "绝": 0.2,
    "胎": 0.3,
    "养": 0.3,
}

YUELING_MAX_SCORE = 40
TONGEN_MAX_SCORE = 30
LINGGONG_MAX_SCORE = 15  # 临宫bonus：帝旺临宫额外加分
BIJIE_MAX_SCORE = 20
YINXING_MAX_SCORE = 10

# 临宫权重表（十二长生状态 → 临宫加成系数，仅在无通根时生效）
# 帝旺=最强临宫位（给满分），临官/长生次之，其余不给分
LINGGONG_WEIGHT_MAP = {
    "帝旺": 1.0,
    "临官": 0.8,
    "长生": 0.5,
    "沐浴": 0.2,
    "冠带": 0.2,
    "衰": 0.1,
    "病": 0.0,
    "死": 0.0,
    "墓": 0.0,
    "绝": 0.0,
    "胎": 0.0,
    "养": 0.0,
}


# ============================================================
# 地支藏干表（索引版）- 来源：yueling_canggan.py（已验证）
# ============================================================
# 格式：[本气索引, 中气索引, 余气索引]  (None = 无此藏干)
# 天干索引：甲=0,乙=1,丙=2,丁=3,戊=4,己=5,庚=6,辛=7,壬=8,癸=9
#
# 验证数据（来源：yueling_canggan.py）:
# 子: 本气=癸(9), 中气=壬(8), 余气=None
# 丑: 本气=己(5), 中气=癸(9), 余气=辛(7)
# 寅: 本气=甲(0), 中气=丙(2), 余气=戊(4)
# 卯: 本气=乙(1), 中气=甲(0), 余气=None
# 辰: 本气=戊(4), 中气=乙(1), 余气=癸(9)
# 巳: 本气=丙(2), 中气=庚(6), 余气=戊(4)
# 午: 本气=丁(3), 中气=己(5), 余气=None
# 未: 本气=己(5), 中气=丁(3), 余气=乙(1)
# 申: 本气=庚(6), 中气=壬(8), 余气=戊(4)
# 酉: 本气=辛(7), 中气=庚(6), 余气=None
# 戌: 本气=戊(4), 中气=辛(7), 余气=丁(3)
# 亥: 本气=壬(8), 中气=甲(0), 余气=None
BRANCH_HIDDEN_STEMS = {
    0: [9, 8, None],    # 子：癸, 壬, 无
    1: [5, 9, 7],       # 丑：己, 癸, 辛
    2: [0, 2, 4],       # 寅：甲, 丙, 戊
    3: [1, 0, None],    # 卯：乙, 甲, 无
    4: [2, 1, 9],       # 辰：戊, 乙, 癸
    5: [2, 6, 4],       # 巳：丙, 庚, 戊
    6: [3, 5, None],   # 午：丁, 己, 无
    7: [5, 3, 1],       # 未：己, 丁, 乙
    8: [6, 8, 4],       # 申：庚, 壬, 戊
    9: [7, 6, None],    # 酉：辛, 庚, 无
    10: [4, 7, 3],     # 戌：戊, 辛, 丁
    11: [8, 0, None],  # 亥：壬, 甲, 无
}


def _get_branch_tongen(day_stem: str, branch_idx: int) -> Dict[str, Any]:
    """
    判断日干在某地支的通根强度 + 临宫状态

    通根判定（比较天干索引）：
    - 日干天干 == 地支本气天干 → 完全通根(×1.0)
    - 日干天干 == 地支中气天干 → 半通根(×0.5)
    - 日干天干 == 地支余气天干 → 微弱通根(×0.25)
    - 否则 → 无通根

    临宫判定：即使无通根，也按十二长生状态给临宫加成
    （滴天髓：临官/帝旺本身就是强，不依赖藏干）

    Returns:
        {
            "tongen": "full" | "half" | "weak" | "none",
            "score_mult": 1.0 | 0.5 | 0.25 | 0,
            "detail": str,
            "linggong_state": str,   # 临宫状态（帝旺/长生等）
            "linggong_mult": float,  # 临宫加成系数
        }
    """
    hidden = BRANCH_HIDDEN_STEMS.get(branch_idx, [None, None, None])
    benqi = hidden[0]    # 本气天干索引
    zhongqi = hidden[1]  # 中气天干索引
    yuzhi = hidden[2]    # 余气天干索引

    # 本气通根
    if benqi is not None and STEM_NAMES[benqi] == day_stem:
        tongen = "full"
        score_mult = 1.0
        detail = f"本气{STEM_NAMES[benqi]}"
    # 中气半通根
    elif zhongqi is not None and STEM_NAMES[zhongqi] == day_stem:
        tongen = "half"
        score_mult = 0.5
        detail = f"中气{STEM_NAMES[zhongqi]}"
    # 余气微弱通根
    elif yuzhi is not None and STEM_NAMES[yuzhi] == day_stem:
        tongen = "weak"
        score_mult = 0.25
        detail = f"余气{STEM_NAMES[yuzhi]}"
    else:
        tongen = "none"
        score_mult = 0.0
        detail = ""

    # 临宫状态（独立于通根）
    linggong_state = get_changsheng_state(day_stem, BRANCH_NAMES[branch_idx])
    linggong_mult = LINGGONG_WEIGHT_MAP.get(linggong_state, 0.0)

    return {
        "tongen": tongen,
        "score_mult": score_mult,
        "detail": detail,
        "linggong_state": linggong_state,
        "linggong_mult": linggong_mult,
    }


def _calc_yueling_score(day_stem: str, month_branch: str) -> Dict[str, Any]:
    """
    计算月令得分（40%权重）
    使用 shier_changsheng.get_changsheng_state 获取正确的十二长生状态
    """
    state = get_changsheng_state(day_stem, month_branch)
    weight = YUELING_WEIGHT_MAP.get(state, 0.0)
    score = YUELING_MAX_SCORE * weight

    state_idx = CHANGSHENG_ORDER.index(state) if state in CHANGSHENG_ORDER else -1

    return {
        "state": state,
        "state_idx": state_idx,
        "weight": weight,
        "score": round(score, 1),
        "max": YUELING_MAX_SCORE,
    }


def _calc_tongen_score(day_stem: str, bazi: Dict) -> Dict[str, Any]:
    """
    计算通根得分（30%权重）+ 临宫bonus
    检查四柱地支是否有日干天干通根，以及各柱临宫状态

    通根得分 = 30 × min(总通根强度, 4.0) / 4.0
    临宫bonus：每个地支的临宫状态额外加权（帝旺/临官/长生等）
    临宫加分 = 15 × min(总临宫加成, 3.0) / 3.0（满分15分）

    临宫逻辑（滴天髓）：日干临帝旺/临官/长生等位置，本身就强，
    不依赖藏干里有没有同气天干。
    """
    branch_indices = [
        bazi["year"]["branch_idx"],
        bazi["month"]["branch_idx"],
        bazi["day"]["branch_idx"],
        bazi["hour"]["branch_idx"],
    ]

    total_mult = 0.0
    total_linggong = 0.0
    details = []
    linggong_details = []
    full_count = 0
    half_count = 0
    weak_count = 0

    for branch_idx in branch_indices:
        result = _get_branch_tongen(day_stem, branch_idx)
        branch_name = BRANCH_NAMES[branch_idx]

        if result["tongen"] != "none":
            details.append(f"{branch_name}({result['detail']},{result['tongen']})")
            total_mult += result["score_mult"]
            if result["tongen"] == "full":
                full_count += 1
            elif result["tongen"] == "half":
                half_count += 1
            else:
                weak_count += 1

        # 临宫加成（仅在无通根或通根极弱时生效，防止与通根重叠）
        # 例如：甲木在寅=临官(0.8)且本气通根(full=1.0)，只取max(0.8,1.0)=1.0
        # 例如：丙火在午=帝旺(1.0)但无通根，取临宫0.8=8.0分
        if result["linggong_mult"] > 0 and result["score_mult"] < 0.5:
            linggong_details.append(f"{branch_name}({result['linggong_state']},{result['linggong_mult']})")
            total_linggong += result["linggong_mult"]

    tongen_score = round(TONGEN_MAX_SCORE * min(total_mult, 4.0) / 4.0, 1)
    linggong_score = round(LINGGONG_MAX_SCORE * min(total_linggong, 3.0) / 3.0, 1)
    total_score = round(tongen_score + linggong_score, 1)

    return {
        "count": len(details),
        "full_count": full_count,
        "half_count": half_count,
        "weak_count": weak_count,
        "total_mult": round(total_mult, 2),
        "tongen_score": tongen_score,
        "linggong_score": linggong_score,
        "linggong_details": linggong_details,
        "score": total_score,
        "max": TONGEN_MAX_SCORE + LINGGONG_MAX_SCORE,
        "details": details,
    }


def _calc_bijie_score(day_stem_idx: int, day_element: int, bazi: Dict) -> Dict[str, Any]:
    """
    计算比劫得分（20%权重）
    天干比劫：年干、月干、时干与日干同五行（同我者）
    日干本身不算比劫
    """
    stem_indices = [
        bazi["year"]["stem_idx"],
        bazi["month"]["stem_idx"],
        bazi["day"]["stem_idx"],
        bazi["hour"]["stem_idx"],
    ]
    pillar_names = ["year", "month", "day", "hour"]

    # 排除日柱自身（仅位置判断，不排除同名天干）
    # 年干=日干 → 算比劫；月干=日干 → 算比劫
    bijie_count = sum(
        1 for p, si in zip(pillar_names, stem_indices)
        if p != "day" and STEM_ELEMENTS[si] == day_element
    )

    # 每比劫5分，最多4个，满分20分
    score = round(bijie_count * BIJIE_MAX_SCORE / 4, 1)

    return {
        "count": bijie_count,
        "score": score,
        "max": BIJIE_MAX_SCORE,
    }


def _calc_yinxing_score(day_element: int, bazi: Dict) -> Dict[str, Any]:
    """
    计算印星生助得分（10%权重）
    印星：生我者之五行 = (日干五行 + 4) % 5

    统计天干印星和地支印星：
    - 天干印星：每个3分
    - 地支本气印星：每个2分
    - 最高10分
    """
    yin_element = (day_element + 4) % 5  # 印星五行索引

    stem_indices = [
        bazi["year"]["stem_idx"],
        bazi["month"]["stem_idx"],
        bazi["day"]["stem_idx"],
        bazi["hour"]["stem_idx"],
    ]

    yin_stem_count = sum(
        1 for si in stem_indices
        if STEM_ELEMENTS[si] == yin_element
    )

    branch_indices = [
        bazi["year"]["branch_idx"],
        bazi["month"]["branch_idx"],
        bazi["day"]["branch_idx"],
        bazi["hour"]["branch_idx"],
    ]

    yin_branch_count = sum(
        1 for bi in branch_indices
        if BRANCH_ELEMENTS[bi] == yin_element
    )

    yin_score = yin_stem_count * 3 + yin_branch_count * 2
    score = round(min(yin_score, YINXING_MAX_SCORE), 1)

    return {
        "stem_count": yin_stem_count,
        "branch_count": yin_branch_count,
        "yin_element": ELEMENT_NAMES[yin_element],
        "score": score,
        "max": YINXING_MAX_SCORE,
    }


def _score_to_strength_label(score: float) -> str:
    """将0-100的得分转换为强弱标签"""
    if score >= 85:
        return "极强"
    elif score >= 65:
        return "强"
    elif score >= 40:
        return "中"
    elif score >= 20:
        return "弱"
    else:
        return "极弱"


def get_rizhu_strength_v2(bazi: Dict) -> Dict[str, Any]:
    """
    日主强弱量化判定 v2 - 带权重算法

    基于《千里命稿》《滴天髓》：
    - 月令旺相（40%）：根据十二长生状态加权
    - 地支通根（30%）：本气/中气/余气通根强度叠加
    - 天干比劫（20%）：同五行天干计数
    - 印星生助（10%）：生我者五行天干地支计数

    Args:
        bazi: 八字字典 {year/month/day/hour: {stem_idx, branch_idx, ...}}

    Returns:
        {
            "strength": "极强/强/中/弱/极弱",
            "score": 0-100,
            "breakdown": {
                "yueling": {"state": "帝旺", "score": 40, "weight": 0.4, ...},
                "tongen": {"score": 15, "weight": 0.3, ...},
                "bijie": {"count": 1, "score": 8, "weight": 0.2},
                "yinxing": {"count": 0, "score": 0, "weight": 0.1},
            },
            "reason": "月令帝旺40分+通根辰丑15分+比劫甲8分...",
            "method": "v2_weighted",
        }
    """
    day_stem_idx = bazi["day"]["stem_idx"]
    day_stem_name = STEM_NAMES[day_stem_idx]
    day_element = STEM_ELEMENTS[day_stem_idx]
    month_branch_name = BRANCH_NAMES[bazi["month"]["branch_idx"]]

    # 1. 月令得分（40%）
    yueling = _calc_yueling_score(day_stem_name, month_branch_name)

    # 2. 通根得分（30%）
    tongen = _calc_tongen_score(day_stem_name, bazi)

    # 3. 比劫得分（20%）
    bijie = _calc_bijie_score(day_stem_idx, day_element, bazi)

    # 4. 印星得分（10%）
    yinxing = _calc_yinxing_score(day_element, bazi)

    # 总分
    total_score = round(
        yueling["score"] + tongen["score"] + bijie["score"] + yinxing["score"], 1
    )

    # 强弱判定
    strength = _score_to_strength_label(total_score)

    # 生成 reason 字符串
    reason_parts = []
    if yueling["score"] > 0:
        reason_parts.append(f"月令{yueling['state']}{yueling['score']}分")
    if tongen["count"] > 0 or tongen.get("linggong_details"):
        tongen_details = ",".join(tongen["details"]) if tongen["details"] else "无"
        lg_details = ",".join(tongen["linggong_details"]) if tongen.get("linggong_details") else ""
        lg_str = f"[临宫{lg_details}(+{tongen['linggong_score']})]" if lg_details else ""
        reason_parts.append(f"通根{tongen_details}({tongen['tongen_score']}){lg_str}")
    if bijie["count"] > 0:
        reason_parts.append(f"比劫×{bijie['count']}个({bijie['score']}分)")
    if yinxing["stem_count"] > 0 or yinxing["branch_count"] > 0:
        reason_parts.append(
            f"印星(天干{yinxing['stem_count']}+地支{yinxing['branch_count']}){yinxing['score']}分"
        )
    if not reason_parts:
        reason_parts = ["无明显助力"]

    return {
        "strength": strength,
        "score": total_score,
        "breakdown": {
            "yueling": {
                "state": yueling["state"],
                "state_idx": yueling["state_idx"],
                "score": yueling["score"],
                "weight": 0.4,
            },
            "tongen": {
                "score": tongen["score"],
                "tongen_score": tongen["tongen_score"],
                "linggong_score": tongen["linggong_score"],
                "linggong_details": tongen.get("linggong_details", []),
                "weight": 0.3,
                "count": tongen["count"],
                "full_count": tongen["full_count"],
                "half_count": tongen["half_count"],
                "weak_count": tongen["weak_count"],
                "total_mult": tongen["total_mult"],
                "details": tongen["details"],
            },
            "bijie": {
                "count": bijie["count"],
                "score": bijie["score"],
                "weight": 0.2,
            },
            "yinxing": {
                "stem_count": yinxing["stem_count"],
                "branch_count": yinxing["branch_count"],
                "yin_element": yinxing["yin_element"],
                "score": yinxing["score"],
                "weight": 0.1,
            },
        },
        "reason": " + ".join(reason_parts),
        "method": "v2_weighted",
        "day_stem": day_stem_name,
        "day_element": ELEMENT_NAMES[day_element],
        "month_branch": month_branch_name,
    }


# ============================================================
# 测试
# ============================================================

def run_tests():
    """运行4个测试用例"""
    from bazi_engine import get_bazi, get_rizhu_strength

    print("=" * 60)
    print("日主强弱量化判定 v2 - 测试")
    print("=" * 60)

    # -----------------------------------------------
    # 测试1: 日主极强（帝旺 + 通根 + 比劫）
    # 甲日主，月令卯（帝旺），多地支木通根，多天干比劫
    # -----------------------------------------------
    print("\n【测试1】日主极强（帝旺+通根+比劫）")
    # 构造：甲日，卯月（帝旺），亥子丑寅地支多木
    # 用 get_bazi 构造一个卯月八字再调整
    bazi1 = get_bazi(2024, 3, 15, 10)["bazi"]
    # 2024年3月15日10点 = 甲辰月，非卯月
    # 手动构造极强八字
    # 甲日，卯月，多木地支
    bazi1 = {
        "year": {"stem_idx": 0, "branch_idx": 11},   # 甲子
        "month": {"stem_idx": 1, "branch_idx": 3},  # 乙卯（帝旺）
        "day": {"stem_idx": 0, "branch_idx": 2},    # 甲寅（临官）
        "hour": {"stem_idx": 1, "branch_idx": 0},   # 乙子
    }
    day_stem1 = STEM_NAMES[bazi1["day"]["stem_idx"]]
    month_br1 = BRANCH_NAMES[bazi1["month"]["branch_idx"]]
    state1 = get_changsheng_state(day_stem1, month_br1)
    print(f"  八字: {STEM_NAMES[bazi1['year']['stem_idx']]}{BRANCH_NAMES[bazi1['year']['branch_idx']]} "
          f"{STEM_NAMES[bazi1['month']['stem_idx']]}{BRANCH_NAMES[bazi1['month']['branch_idx']]} "
          f"{STEM_NAMES[bazi1['day']['stem_idx']]}{BRANCH_NAMES[bazi1['day']['branch_idx']]} "
          f"{STEM_NAMES[bazi1['hour']['stem_idx']]}{BRANCH_NAMES[bazi1['hour']['branch_idx']]}")
    print(f"  日干={day_stem1}, 月令={month_br1}, 长生状态={state1}")

    v2_1 = get_rizhu_strength_v2(bazi1)
    v1_1 = get_rizhu_strength(bazi1)

    print(f"  V2结果: {v2_1['strength']} (score={v2_1['score']})")
    print(f"  V2详情: {v2_1['reason']}")
    print(f"  V1结果: {v1_1['strength']} - {v1_1['reason']}")
    print(f"  各项: 月令={v2_1['breakdown']['yueling']['score']}({v2_1['breakdown']['yueling']['state']}) + "
          f"通根={v2_1['breakdown']['tongen']['score']}({v2_1['breakdown']['tongen']['count']}个) + "
          f"比劫={v2_1['breakdown']['bijie']['score']}({v2_1['breakdown']['bijie']['count']}个) + "
          f"印星={v2_1['breakdown']['yinxing']['score']} = {v2_1['score']}")
    print(f"  通根明细: {v2_1['breakdown']['tongen']['details']}")

    # -----------------------------------------------
    # 测试2: 日主极弱（失令+无根）
    # -----------------------------------------------
    print("\n【测试2】日主极弱（失令+无根）")
    # 甲日，午月（死），无木地支，无比劫
    bazi2 = {
        "year": {"stem_idx": 2, "branch_idx": 6},   # 丙午
        "month": {"stem_idx": 3, "branch_idx": 6},  # 丁午（死）
        "day": {"stem_idx": 0, "branch_idx": 5},   # 甲巳（病）
        "hour": {"stem_idx": 4, "branch_idx": 8},  # 戊申（金）
    }
    day_stem2 = STEM_NAMES[bazi2["day"]["stem_idx"]]
    month_br2 = BRANCH_NAMES[bazi2["month"]["branch_idx"]]
    state2 = get_changsheng_state(day_stem2, month_br2)
    print(f"  八字: {STEM_NAMES[bazi2['year']['stem_idx']]}{BRANCH_NAMES[bazi2['year']['branch_idx']]} "
          f"{STEM_NAMES[bazi2['month']['stem_idx']]}{BRANCH_NAMES[bazi2['month']['branch_idx']]} "
          f"{STEM_NAMES[bazi2['day']['stem_idx']]}{BRANCH_NAMES[bazi2['day']['branch_idx']]} "
          f"{STEM_NAMES[bazi2['hour']['stem_idx']]}{BRANCH_NAMES[bazi2['hour']['branch_idx']]}")
    print(f"  日干={day_stem2}, 月令={month_br2}, 长生状态={state2}")

    v2_2 = get_rizhu_strength_v2(bazi2)
    v1_2 = get_rizhu_strength(bazi2)

    print(f"  V2结果: {v2_2['strength']} (score={v2_2['score']})")
    print(f"  V2详情: {v2_2['reason']}")
    print(f"  V1结果: {v1_2['strength']} - {v1_2['reason']}")
    print(f"  通根明细: {v2_2['breakdown']['tongen']['details']}")

    # -----------------------------------------------
    # 测试3: 日主中和
    # -----------------------------------------------
    print("\n【测试3】日主中和")
    # 丁日，寅月（长生0.7），有通根但不多
    bazi3 = {
        "year": {"stem_idx": 6, "branch_idx": 10},  # 庚戌
        "month": {"stem_idx": 0, "branch_idx": 2},  # 甲寅（长生）
        "day": {"stem_idx": 3, "branch_idx": 3},   # 丁卯
        "hour": {"stem_idx": 2, "branch_idx": 5},  # 丙巳
    }
    day_stem3 = STEM_NAMES[bazi3["day"]["stem_idx"]]
    month_br3 = BRANCH_NAMES[bazi3["month"]["branch_idx"]]
    state3 = get_changsheng_state(day_stem3, month_br3)
    print(f"  八字: {STEM_NAMES[bazi3['year']['stem_idx']]}{BRANCH_NAMES[bazi3['year']['branch_idx']]} "
          f"{STEM_NAMES[bazi3['month']['stem_idx']]}{BRANCH_NAMES[bazi3['month']['branch_idx']]} "
          f"{STEM_NAMES[bazi3['day']['stem_idx']]}{BRANCH_NAMES[bazi3['day']['branch_idx']]} "
          f"{STEM_NAMES[bazi3['hour']['stem_idx']]}{BRANCH_NAMES[bazi3['hour']['branch_idx']]}")
    print(f"  日干={day_stem3}, 月令={month_br3}, 长生状态={state3}")

    v2_3 = get_rizhu_strength_v2(bazi3)
    v1_3 = get_rizhu_strength(bazi3)

    print(f"  V2结果: {v2_3['strength']} (score={v2_3['score']})")
    print(f"  V2详情: {v2_3['reason']}")
    print(f"  V1结果: {v1_3['strength']} - {v1_3['reason']}")

    # -----------------------------------------------
    # 测试4: V1 vs V2 对比
    # -----------------------------------------------
    print("\n【测试4】V1 vs V2 全面对比")
    test_cases = [
        ("2024-03-15 10:00", 2024, 3, 15, 10),
        ("2025-01-15 14:00", 2025, 1, 15, 14),
        ("1990-08-15 08:00", 1990, 8, 15, 8),
        ("1987-06-20 12:00", 1987, 6, 20, 12),
    ]

    for label, y, m, d, h in test_cases:
        b = get_bazi(y, m, d, h)["bazi"]
        v2 = get_rizhu_strength_v2(b)
        v1 = get_rizhu_strength(b)
        match = "✓" if v1["strength"] == v2["strength"] else "✗"
        print(f"  {match} {label}: V1={v1['strength']}, V2={v2['strength']}({v2['score']}) "
              f"| {v2['breakdown']['yueling']['state']} "
              f"月令={v2['breakdown']['yueling']['score']} "
              f"通根={v2['breakdown']['tongen']['score']} "
              f"比劫={v2['breakdown']['bijie']['score']} "
              f"印星={v2['breakdown']['yinxing']['score']}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


# ============================================================
# 全藏干计数法（兼容派系1：滴天髓/气势派）
# ============================================================

def get_strength_by_count(bazi: Dict[str, Any]) -> Dict[str, Any]:
    """
    全藏干计数法 - 统计八字中所有五行的数量来判断身强身弱

    方法来源：滴天髓"气势"思维，网络平台（卜知排盘、好赞易学等）常用简化版
    原理：计算日主同类（五行相同）总数量 vs 克泄耗日主的五行数量

    评分标准：
    - 同类 > 克泄耗 → 身强
    - 同类 < 克泄耗 → 身弱
    - 接近平衡 → 中和

    Args:
        bazi: 八字字典，包含 year/month/day/hour 四柱，每柱有 stem_idx 和 branch_idx

    Returns:
        {
            "method": "全藏干计数法",
            "method_desc": "统计天干+地支藏干（本气+中气+余气）的五行数量",
            "strength": "强/中/弱",
            "day_element_count": int,   # 日主同类数量
            "oppose_count": int,       # 克日主数量
            "drain_count": int,        # 泄日主数量
            "restrict_count": int,     # 耗日主数量
            "wx_counts": {"木":0,"火":0,"土":0,"金":0,"水":0},
            "analysis": str,
            "xiyongshen_by_count": [str],  # 此方法下的喜用神
            "jishen_by_count": [str],        # 此方法下的忌神
        }
    """
    day_stem_idx = bazi["day"]["stem_idx"]
    day_elem_idx = STEM_ELEMENTS[day_stem_idx]
    day_elem = ELEMENT_NAMES[day_elem_idx]

    # 五行相生相克关系（按index: 木0 火1 土2 金3 水4）
    # 生我者(印枭)：(idx+4)%5，如火(1)+4=5%5=0=木
    # 我生者(食伤)：(idx+1)%5，如火(1)+1=2=土
    # 我克者(财)：  (idx+2)%5，如火(1)+2=3=金
    # 克我者(官鬼)：(idx+3)%5，如火(1)+3=4=水
    sheng_idx = (day_elem_idx + 4) % 5  # 生我者（印枭）
    xie_idx = (day_elem_idx + 1) % 5    # 我生者（食伤）
    hao_idx = (day_elem_idx + 2) % 5    # 我克者（财）
    ke_idx = (day_elem_idx + 3) % 5     # 克我者（官鬼）

    # 统计
    wx_counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    details = []

    # 处理四柱（天干 + 地支藏干）
    for pillar_name, pillar in [("年", bazi["year"]), ("月", bazi["month"]),
                                 ("日", bazi["day"]), ("时", bazi["hour"])]:
        stem_idx = pillar["stem_idx"]
        branch_idx = pillar["branch_idx"]

        # 天干
        stem_elem_idx = STEM_ELEMENTS[stem_idx]
        stem_elem = ELEMENT_NAMES[stem_elem_idx]
        wx_counts[stem_elem] += 1

        # 地支藏干（本气+中气+余气）
        hidden = BRANCH_HIDDEN_STEMS.get(branch_idx, [None, None, None])
        for h in hidden:
            if h is not None:
                h_elem = ELEMENT_NAMES[STEM_ELEMENTS[h]]
                wx_counts[h_elem] += 1

        details.append(f"{pillar_name}:{stem_elem}")

    day_elem_count = wx_counts[day_elem]
    sheng_count = wx_counts[ELEMENT_NAMES[sheng_idx]]  # 印星（生我）
    xie_count = wx_counts[ELEMENT_NAMES[xie_idx]]       # 食伤（我生）
    hao_count = wx_counts[ELEMENT_NAMES[hao_idx]]      # 财（我克）
    ke_count = wx_counts[ELEMENT_NAMES[ke_idx]]        # 官（克我）

    # 同类：天干同五行 + 印星（生助日主）
    tonglei_count = day_elem_count + sheng_count
    # 克泄耗：食伤 + 财 + 官
    ke_xie_hao_count = xie_count + hao_count + ke_count

    # 强弱判定（简化版）
    ratio = tonglei_count / max(ke_xie_hao_count, 1)
    if ratio >= 1.3:
        strength = "强"
    elif ratio >= 0.8:
        strength = "中"
    else:
        strength = "弱"

    # 喜忌判断
    if strength == "强":
        # 身强喜克泄：官、财、食伤
        xiyong = [ELEMENT_NAMES[ke_idx], ELEMENT_NAMES[hao_idx], ELEMENT_NAMES[xie_idx]]
        ji = [day_elem, ELEMENT_NAMES[sheng_idx]]
    elif strength == "弱":
        # 身弱喜生扶：印、比劫
        xiyong = [ELEMENT_NAMES[sheng_idx], day_elem]
        ji = [ELEMENT_NAMES[ke_idx], ELEMENT_NAMES[hao_idx], ELEMENT_NAMES[xie_idx]]
    else:
        # 中和态细分（比例~1.0）：
        # - 比例>1.1：同类明显偏强 → 日主偏旺 → 忌同类，喜克抑（水+金）
        # - 比例<0.9：克泄耗明显偏强 → 日主偏弱 → 喜扶抑（木+火+水），忌克泄（土+金）
        # - 比例0.9-1.1：严格平衡 → 喜忌温和，取财（金泄土克木）为主
        if ratio > 1.1:
            xiyong = [ELEMENT_NAMES[hao_idx], ELEMENT_NAMES[ke_idx]]  # 财+官
            ji = [day_elem, ELEMENT_NAMES[sheng_idx]]  # 日主+印
        elif ratio < 0.9:
            xiyong = [day_elem, ELEMENT_NAMES[sheng_idx], ELEMENT_NAMES[hao_idx]]  # 日主+印+财
            ji = [ELEMENT_NAMES[ke_idx], ELEMENT_NAMES[xie_idx]]  # 官+食伤
        else:
            xiyong = [ELEMENT_NAMES[hao_idx]]  # 财（金）
            ji = [day_elem, ELEMENT_NAMES[sheng_idx]]  # 日主+印

    xiyong = list(dict.fromkeys(xiyong))
    ji = list(dict.fromkeys(ji))

    return {
        "method": "全藏干计数法",
        "method_desc": "统计天干+地支藏干（本气+中气+余气）的五行数量",
        "strength": strength,
        "score_ratio": round(ratio, 2),
        "day_element": day_elem,
        "day_element_count": day_elem_count,
        "tonglei_count": tonglei_count,
        "ke_xie_hao_count": ke_xie_hao_count,
        "sheng_count": sheng_count,
        "xie_count": xie_count,
        "hao_count": hao_count,
        "ke_count": ke_count,
        "wx_counts": wx_counts,
        "details": details,
        "analysis": (f"日主{day_elem}共{day_elem_count}个，印星{sheng_count}个，"
                    f"同类{tonglei_count}；食伤{xie_count}个，财{hao_count}个，官{ke_count}个，"
                    f"克泄耗{ke_xie_hao_count}个。比例{tonglei_count}:{ke_xie_hao_count}={ratio:.2f}"),
        "xiyongshen_by_count": xiyong,
        "jishen_by_count": ji,
    }


if __name__ == "__main__":
    run_tests()
