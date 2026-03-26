#!/usr/bin/env python3
"""
子平格局法：格局取用 + 成败判定
基于《子平真诠》《千里命稿》实现

核心原则：
- 月令是八字之"纲领"，取格以月令为主
- 月令所藏天干为主气，再看透干
- 透出什么十神，就是什么格
"""

from typing import Dict, List, Any, Optional, Tuple

# ============================================================
# 1. 天干地支常量
# ============================================================

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ZHI_IDX = {z: i for i, z in enumerate(EARTHLY_BRANCHES)}
GAN_IDX = {g: i for i, g in enumerate(HEAVENLY_STEMS)}

# 天干五行属性 (index -> element)
STEM_ELEMENTS = ["木", "火", "土", "金", "水"]
STEM_ELEM_IDX = {g: i for i, g in enumerate(HEAVENLY_STEMS)}  # 甲->0, 乙->0, 丙->1...

# ============================================================
# 2. 十神索引表
# ============================================================

# 十神表：以日干为基准，天干与日干的关系
# SHISHEN_TABLE[日干_idx][天干_idx] = 十神名称
SHISHEN_TABLE = [
    #        甲    乙    丙    丁    戊    己    庚    辛    壬    癸
    ["比肩", "劫财", "食神", "伤官", "偏财", "正财", "偏官", "正官", "偏印", "正印"],  # 日干=甲
    ["劫财", "比肩", "伤官", "食神", "正财", "偏财", "正官", "偏官", "正印", "偏印"],  # 日干=乙
    ["偏印", "正印", "比肩", "劫财", "食神", "伤官", "偏财", "正财", "偏官", "正官"],  # 日干=丙
    ["正印", "偏印", "劫财", "比肩", "伤官", "食神", "正财", "偏财", "正官", "偏官"],  # 日干=丁
    ["偏财", "正财", "偏印", "正印", "比肩", "劫财", "食神", "伤官", "偏官", "正官"],  # 日干=戊
    ["正财", "偏财", "正印", "偏印", "劫财", "比肩", "伤官", "食神", "正官", "偏官"],  # 日干=己
    ["偏官", "正官", "偏财", "正财", "偏印", "正印", "比肩", "劫财", "食神", "伤官"],  # 日干=庚
    ["正官", "偏官", "正财", "偏财", "正印", "偏印", "劫财", "比肩", "伤官", "食神"],  # 日干=辛
    ["食神", "伤官", "偏官", "正官", "偏财", "正财", "偏印", "正印", "比肩", "劫财"],  # 日干=壬
    ["伤官", "食神", "正官", "偏官", "正财", "偏财", "正印", "偏印", "劫财", "比肩"],  # 日干=癸
]

# 十神名称列表（用于查表索引）
SHISHEN_NAMES = ["比肩", "劫财", "食神", "伤官", "偏财", "正财", "偏官", "正官", "偏印", "正印"]


def get_shishen(day_stem_idx: int, other_stem_idx: int) -> str:
    """获取十神关系（查表法）"""
    return SHISHEN_TABLE[day_stem_idx % 10][other_stem_idx % 10]


# 十神索引：某天干对于某日干是什么十神
# SHISHEN_IDX[日干][十神] = 天干
SHISHEN_IDX: Dict[str, Dict[str, str]] = {
    "甲": {"正官": "辛", "七杀": "庚", "正印": "癸", "偏印": "壬",
           "正财": "己", "偏财": "戊", "食神": "丙", "伤官": "丁",
           "比肩": "甲", "劫财": "乙"},
    "乙": {"正官": "庚", "七杀": "辛", "正印": "壬", "偏印": "癸",
           "正财": "戊", "偏财": "己", "食神": "丁", "伤官": "丙",
           "比肩": "乙", "劫财": "甲"},
    "丙": {"正官": "壬", "七杀": "癸", "正印": "甲", "偏印": "乙",
           "正财": "庚", "偏财": "辛", "食神": "戊", "伤官": "己",
           "比肩": "丙", "劫财": "丁"},
    "丁": {"正官": "癸", "七杀": "壬", "正印": "乙", "偏印": "甲",
           "正财": "辛", "偏财": "庚", "食神": "己", "伤官": "戊",
           "比肩": "丁", "劫财": "丙"},
    "戊": {"正官": "甲", "七杀": "乙", "正印": "丙", "偏印": "丁",
           "正财": "壬", "偏财": "癸", "食神": "庚", "伤官": "辛",
           "比肩": "戊", "劫财": "己"},
    "己": {"正官": "乙", "七杀": "甲", "正印": "丁", "偏印": "丙",
           "正财": "癸", "偏财": "壬", "食神": "辛", "伤官": "庚",
           "比肩": "己", "劫财": "戊"},
    "庚": {"正官": "丙", "七杀": "丁", "正印": "戊", "偏印": "己",
           "正财": "甲", "偏财": "乙", "食神": "壬", "伤官": "癸",
           "比肩": "庚", "劫财": "辛"},
    "辛": {"正官": "丁", "七杀": "丙", "正印": "己", "偏印": "戊",
           "正财": "乙", "偏财": "甲", "食神": "癸", "伤官": "壬",
           "比肩": "辛", "劫财": "庚"},
    "壬": {"正官": "戊", "七杀": "己", "正印": "庚", "偏印": "辛",
           "正财": "丙", "偏财": "丁", "食神": "甲", "伤官": "乙",
           "比肩": "壬", "劫财": "癸"},
    "癸": {"正官": "己", "七杀": "戊", "正印": "辛", "偏印": "庚",
           "正财": "丁", "偏财": "丙", "食神": "乙", "伤官": "甲",
           "比肩": "癸", "劫财": "壬"},
}

# 十神到天干的反向索引（用于判断某天干是否代表某十神）
def get_stems_for_shishen(day_stem: str, shishen: str) -> List[str]:
    """获取日干对应的某十神的天干列表"""
    return [SHISHEN_IDX[day_stem][shishen]]


# ============================================================
# 3. 格局类型（内十八格）
# ============================================================

GEKU_TYPES = [
    "正官格", "七杀格", "正印格", "偏印格",
    "正财格", "偏财格", "食神格", "伤官格",
    "比肩格", "劫财格",
    "从杀格", "从财格", "从儿格", "从印格",
    "化气格", "建禄格", "月刃格", "专旺格"
]

# 外格（杂格）
GEKU_TYPES_OUTER = [
    "杂气格", "拱禄格", "夹禄格", "趋乾格", "趋艮格",
    "飞禄格", "倒禄格", "合禄格", "井栏格", "曲直格",
    "炎上格", "稼穑格", "从革格", "润下格"
]


# ============================================================
# 4. 月令藏干表（与 yueling_canggan.py 保持一致）
# ============================================================

YUELING_CANGGAN = {
    "子": {"本气": "癸", "中气": "壬", "余气": None},
    "丑": {"本气": "己", "中气": "癸", "余气": "辛"},
    "寅": {"本气": "甲", "中气": "丙", "余气": "戊"},
    "卯": {"本气": "乙", "中气": "甲", "余气": None},
    "辰": {"本气": "戊", "中气": "乙", "余气": "癸"},
    "巳": {"本气": "丙", "中气": "庚", "余气": "戊"},
    "午": {"本气": "丁", "中气": "己", "余气": None},
    "未": {"本气": "己", "中气": "丁", "余气": "乙"},
    "申": {"本气": "庚", "中气": "壬", "余气": "戊"},
    "酉": {"本气": "辛", "中气": "庚", "余气": None},
    "戌": {"本气": "戊", "中气": "辛", "余气": "丁"},
    "亥": {"本气": "壬", "中气": "甲", "余气": None},
}


# ============================================================
# 5. 分析四柱透干情况
# ============================================================

def analyze_tougan(bazi: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析四柱透干情况

    Args:
        bazi: 八字字典，包含 year/month/day/hour 四柱

    Returns:
        {
            "tougan": {"甲": ["年干", "月干"], ...},  # 哪些天干透出了
            "butong": {"甲": True, ...},              # 某天干是否不透
            "all_stems": ["甲", "丁", "庚", "辛"],   # 全部天干列表
        }
    """
    # 收集四柱天干
    stems = [
        ("年干", bazi["year"]["stem"]),
        ("月干", bazi["month"]["stem"]),
        ("日干", bazi["day"]["stem"]),
        ("时干", bazi["hour"]["stem"]),
    ]

    tougan: Dict[str, List[str]] = {}  # 天干 -> [透出位置]
    for pos, stem in stems:
        if stem not in tougan:
            tougan[stem] = []
        tougan[stem].append(pos)

    all_stems = [s for _, s in stems]
    butong = {stem: (stem not in all_stems) for stem in HEAVENLY_STEMS}

    return {
        "tougan": tougan,
        "butong": butong,
        "all_stems": all_stems,
    }


# ============================================================
# 6. 月令藏干与透干分析
# ============================================================

def get_yue_pattern_stems(bazi: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析月令藏干与透干

    规则：
    - 本气在月干 → 月令本气透干
    - 本气未透，看中气是否透
    - 本气中气皆未透，看余气是否透

    Args:
        bazi: 八字字典

    Returns:
        {
            "yue_zhi": "辰",
            "benqi": "戊",
            "zhongqi": "乙",
            "yuzhi": "癸",
            "benqi_tou": True/False,     # 本气是否透干
            "zhongqi_tou": True/False,   # 中气是否透干
            "yuzhi_tou": True/False,     # 余气是否透干
            "tou_detail": {
                "戊": ["月干"],
                "乙": ["年干"],
            },
            "tou_level": "本气"/"中气"/"余气"/"无透",
        }
    """
    month_branch = bazi["month"]["branch"]
    yue_info = YUELING_CANGGAN.get(month_branch, {})
    benqi = yue_info.get("本气")
    zhongqi = yue_info.get("中气")
    yuzhi = yue_info.get("余气")

    # 收集四柱天干
    all_stems = [
        bazi["year"]["stem"],
        bazi["month"]["stem"],
        bazi["day"]["stem"],
        bazi["hour"]["stem"],
    ]

    tougan: Dict[str, List[str]] = {}
    stem_positions = [
        ("年干", bazi["year"]["stem"]),
        ("月干", bazi["month"]["stem"]),
        ("日干", bazi["day"]["stem"]),
        ("时干", bazi["hour"]["stem"]),
    ]
    for pos, stem in stem_positions:
        if stem not in tougan:
            tougan[stem] = []
        tougan[stem].append(pos)

    benqi_tou = benqi in all_stems
    zhongqi_tou = zhongqi and zhongqi in all_stems
    yuzhi_tou = yuzhi and yuzhi in all_stems

    # 透干级别（本气>中气>余气）
    if benqi_tou:
        tou_level = "本气"
        tou_stem = benqi
    elif zhongqi_tou:
        tou_level = "中气"
        tou_stem = zhongqi
    elif yuzhi_tou:
        tou_level = "余气"
        tou_stem = yuzhi
    else:
        tou_level = "无透"
        tou_stem = None

    # 透干详情
    tou_detail = {stem: pos for stem, pos in tougan.items() if stem in [benqi, zhongqi, yuzhi] and stem}

    return {
        "yue_zhi": month_branch,
        "benqi": benqi,
        "zhongqi": zhongqi,
        "yuzhi": yuzhi,
        "benqi_tou": benqi_tou,
        "zhongqi_tou": zhongqi_tou,
        "yuzhi_tou": yuzhi_tou,
        "tou_detail": tou_detail,
        "tou_level": tou_level,
        "tou_stem": tou_stem,
    }


# ============================================================
# 7. 格局取用判定
# ============================================================

def determine_pattern(bazi: Dict[str, Any], yueling_canggan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    判定格局

    步骤：
    1. 取月令本气
    2. 看月干是否透出本气相同之十神
    3. 若不透，看其他天干是否透出
    4. 判定成格/破格/变格

    Args:
        bazi: 八字字典
        yueling_canggan: 月令藏干字典（可选，从 yueling_canggan.py 获取）

    Returns:
        {
            "pattern": str,           # 格局名称
            "pattern_type": str,      # "内格" / "外格"
            "tougan": list,           # 透干列表
            "qiling": str,            # 起源（哪柱）
            "is_cheng": bool,         # 是否成格（初步判定）
            "tou_level": str,         # 透干级别
            "reason": str,            # 判断原因
        }
    """
    day_stem = bazi["day"]["stem"]
    day_stem_idx = GAN_IDX.get(day_stem, 0)
    month_branch = bazi["month"]["branch"]

    # 分析月令藏干
    yue_pattern = get_yue_pattern_stems(bazi)
    benqi = yue_pattern["benqi"]       # 本气天干（如"戊"）
    zhongqi = yue_pattern["zhongqi"]   # 中气天干
    yuzhi = yue_pattern["yuzhi"]       # 余气天干

    # 收集四柱天干
    all_stems = [
        ("年干", bazi["year"]["stem"], bazi["year"]["stem_idx"]),
        ("月干", bazi["month"]["stem"], bazi["month"]["stem_idx"]),
        ("日干", bazi["day"]["stem"], bazi["day"]["stem_idx"]),
        ("时干", bazi["hour"]["stem"], bazi["hour"]["stem_idx"]),
    ]

    # ============================================================
    # 核心逻辑：月令本气透干定格局
    # ============================================================

    # 情况1：本气透干 → 以本气透干取格
    if yue_pattern["benqi_tou"]:
        tou_stem = benqi
        # 找谁透出了本气
        qiling_pos = None
        for pos, stem, _ in all_stems:
            if stem == benqi:
                qiling_pos = pos
                break

        # 将本气天干转换为日干对应的十神
        shishen = get_shishen(day_stem_idx, GAN_IDX.get(benqi, 0))
        pattern = f"{shishen}格"
        pattern_type = "内格"
        reason = f"月令{month_branch}本气{benqi}透出，{qiling_pos}见{shishen}，取为{pattern}"

    # 情况2：本气不透，中气透 → 以中气取格
    elif yue_pattern["zhongqi_tou"] and zhongqi:
        tou_stem = zhongqi
        qiling_pos = None
        for pos, stem, _ in all_stems:
            if stem == zhongqi:
                qiling_pos = pos
                break

        shishen = get_shishen(day_stem_idx, GAN_IDX.get(zhongqi, 0))
        pattern = f"{shishen}格"
        pattern_type = "内格"
        reason = f"月令{month_branch}本气{benqi}未透，中气{zhongqi}透出，{qiling_pos}见{shishen}，取为{pattern}"

    # 情况3：本气中气皆不透，余气透 → 以余气取格
    elif yue_pattern["yuzhi_tou"] and yuzhi:
        tou_stem = yuzhi
        qiling_pos = None
        for pos, stem, _ in all_stems:
            if stem == yuzhi:
                qiling_pos = pos
                break

        shishen = get_shishen(day_stem_idx, GAN_IDX.get(yuzhi, 0))
        pattern = f"{shishen}格"
        pattern_type = "内格"
        reason = f"月令{month_branch}本气{benqi}、中气{zhongqi}皆未透，余气{yuzhi}透出，{qiling_pos}见{shishen}，取为{pattern}"

    # 情况4：月令所藏皆不透（本气、中气、余气都不见于四柱天干）
    # → 取月令本气为格（伏吟格）
    else:
        # 所有藏干都不见于四柱，以本气为格
        # 如果本气恰好就是日干自身 → 比肩格/劫财格
        shishen_for_benqi = get_shishen(day_stem_idx, GAN_IDX.get(benqi, 0))
        pattern = f"{shishen_for_benqi}格"
        pattern_type = "内格"
        reason = (f"月令{month_branch}本气{benqi}、中气{zhongqi}、余气{yuzhi}皆未透干，"
                  f"取本气{benqi}为{pattern}（伏吟格）")
        tou_stem = benqi
        qiling_pos = "月令本气"

    # ============================================================
    # 透干列表
    # ============================================================
    all_tougan = yue_pattern["tou_detail"]

    # ============================================================
    # 初步成格判定（后续由 judge_pattern_cheng 详细判定）
    # ============================================================
    # 初步：透干级别为本气或中气 → 初步成格
    is_cheng = yue_pattern["tou_level"] in ["本气", "中气"]

    return {
        "pattern": pattern,
        "pattern_type": pattern_type,
        "tougan": all_tougan,
        "tou_level": yue_pattern["tou_level"],
        "tou_stem": yue_pattern.get("tou_stem"),
        "qiling": qiling_pos,
        "is_cheng": is_cheng,
        "yue_zhi": month_branch,
        "benqi": benqi,
        "zhongqi": zhongqi,
        "yuzhi": yuzhi,
        "reason": reason,
    }


# ============================================================
# 8. 格局成败判定
# ============================================================

# 格局成败规则
CHENG_RULES: Dict[str, Dict[str, Any]] = {
    "正官格": {
        "成": ["配印", "财生", "身旺", "官星清纯"],
        "破": ["伤官", "七杀", "冲", "刑", "官星混杂"],
        "上等": ["官印相生", "财官两旺", "身旺任官"],
        "中等": ["身旺官轻", "财星生官"],
        "下等": ["官轻身弱", "伤官见官"],
    },
    "七杀格": {
        "成": ["配印", "食神制", "羊刃", "杀印相生"],
        "破": ["财生", "杀轻身弱", "杀重无制"],
        "上等": ["杀印相生", "食神制杀", "羊刃合杀"],
        "中等": ["身旺杀轻", "财星生杀"],
        "下等": ["杀重身轻", "无食无印"],
    },
    "正印格": {
        "成": ["官杀生印", "身旺印轻", "印星清纯"],
        "破": ["财星坏印", "偏印混杂", "印星太多"],
        "上等": ["官印相生", "杀印相生", "身旺印轻"],
        "中等": ["印星清纯", "食伤泄秀"],
        "下等": ["财星坏印", "印多害日"],
    },
    "偏印格": {
        "成": ["食神制化", "财星制偏印"],
        "破": ["无食神（枭神夺食）", "偏印太旺"],
        "上等": ["有食神制化", "财星破偏印"],
        "中等": ["偏印有制"],
        "下等": ["枭神夺食", "偏印无制"],
    },
    "正财格": {
        "成": ["身旺", "配印", "财星得位"],
        "破": ["被劫", "冲", "财星太多"],
        "上等": ["身旺任财", "财官相生"],
        "中等": ["身旺财轻", "食伤生财"],
        "下等": ["身弱财旺", "比劫夺财"],
    },
    "偏财格": {
        "成": ["身旺", "食伤生财", "偏财入库"],
        "破": ["被劫", "冲", "偏财太旺"],
        "上等": ["身旺偏财旺", "偏财入库逢冲开"],
        "中等": ["食伤生财"],
        "下等": ["身弱财旺", "比劫分夺"],
    },
    "食神格": {
        "成": ["身旺", "配印", "食神有力"],
        "破": ["枭神夺食", "伤官泄食", "冲"],
        "上等": ["食神生财", "食神制杀"],
        "中等": ["身旺食神旺"],
        "下等": ["枭神夺食", "食神泄尽"],
    },
    "伤官格": {
        "成": ["配印", "财星相辅", "身旺"],
        "破": ["见官", "冲", "刑"],
        "上等": ["伤官生财", "伤官配印"],
        "中等": ["身旺伤官旺"],
        "下等": ["伤官见官", "伤官泄尽"],
    },
    "比肩格": {
        "成": ["官杀克比", "食伤泄秀", "身旺"],
        "破": ["比劫分夺", "财星被劫"],
        "上等": ["比肩护财", "官杀制比"],
        "中等": ["身旺比多"],
        "下等": ["比劫分夺", "财星被劫"],
    },
    "劫财格": {
        "成": ["官杀克劫", "食伤泄秀", "配印"],
        "破": ["劫财太旺", "财星被劫"],
        "上等": ["官杀制劫", "劫财护印"],
        "中等": ["身旺劫财旺"],
        "下等": ["劫财分夺", "财星被劫"],
    },
}


def judge_pattern_cheng(geku_name: str, bazi: Dict[str, Any],
                        pattern_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    判定格局成败

    Args:
        geku_name: 格局名称，如"正官格"
        bazi: 八字字典
        pattern_info: 格局判定结果（可选，用于辅助判断）

    Returns:
        {
            "is_cheng": bool,
            "level": str,        # "上等" / "中等" / "下等" / "破格"
            "factors": list,     # 成/破因素列表
            "suggestion": str,   # 建议
        }
    """
    rules = CHENG_RULES.get(geku_name, {})

    day_stem = bazi["day"]["stem"]
    day_stem_idx = GAN_IDX.get(day_stem, 0)
    month_branch = bazi["month"]["branch"]

    # 收集四柱天干
    all_stems = [
        bazi["year"]["stem"],
        bazi["month"]["stem"],
        bazi["day"]["stem"],
        bazi["hour"]["stem"],
    ]
    all_branch_idx = [
        bazi["year"]["branch_idx"],
        bazi["month"]["branch_idx"],
        bazi["day"]["branch_idx"],
        bazi["hour"]["branch_idx"],
    ]

    factors: List[str] = []
    cheng_factors: List[str] = []
    po_factors: List[str] = []

    # ============================================================
    # 1. 基础判断：透干级别
    # ============================================================
    if pattern_info:
        tou_level = pattern_info.get("tou_level", "")
        if tou_level == "本气":
            cheng_factors.append("本气透干，格局纯粹")
        elif tou_level == "中气":
            cheng_factors.append("中气透干，格局较纯")
        elif tou_level == "余气":
            po_factors.append("余气透干，格局较浊")
        else:
            po_factors.append("无透干，伏吟格（格局较弱）")

    # ============================================================
    # 2. 根据格局类型判断成破
    # ============================================================

    if geku_name == "正官格":
        # 正官格忌：伤官透出、七杀混杂、冲刑
        shishen_list = [get_shishen(day_stem_idx, GAN_IDX.get(s, 0)) for s in all_stems]

        # 伤官破官
        if "伤官" in shishen_list:
            po_factors.append("伤官透出克正官，破格")
        # 七杀混杂
        if shishen_list.count("七杀") > 0:
            po_factors.append("七杀混杂攻官，破格")
        # 官星本身
        if shishen_list.count("正官") >= 1:
            cheng_factors.append("正官星清纯")
        # 财星生官
        if "正财" in shishen_list or "偏财" in shishen_list:
            cheng_factors.append("财星生官")

        # 身旺任官
        month_branch_idx = bazi["month"]["branch_idx"]
        # 简单判断得令
        STEM_LING_DEFU = {
            0: [2, 3], 1: [2, 3], 2: [5, 6], 3: [5, 6],
            4: [1, 4, 7, 10], 5: [1, 4, 7, 10],
            6: [8, 9], 7: [8, 9], 8: [0, 11], 9: [0, 11],
        }
        if month_branch_idx in STEM_LING_DEFU.get(day_stem_idx, []):
            cheng_factors.append("身旺得令，可任官")
        else:
            po_factors.append("身弱官旺，难任官")

    elif geku_name == "七杀格":
        shishen_list = [get_shishen(day_stem_idx, GAN_IDX.get(s, 0)) for s in all_stems]

        # 配印
        if "正印" in shishen_list or "偏印" in shishen_list:
            cheng_factors.append("杀印相生")
        # 食神制杀
        if "食神" in shishen_list:
            cheng_factors.append("食神制杀")
        # 羊刃
        if "劫财" in shishen_list:  # 简化：劫财旺可能为羊刃
            cheng_factors.append("羊刃合杀")
        # 财生杀
        if "正财" in shishen_list or "偏财" in shishen_list:
            if not ("正印" in shishen_list or "偏印" in shishen_list or "食神" in shishen_list):
                po_factors.append("财星生杀，身弱难任")

    elif geku_name == "正印格":
        shishen_list = [get_shishen(day_stem_idx, GAN_IDX.get(s, 0)) for s in all_stems]

        # 财星坏印
        if "正财" in shishen_list or "偏财" in shishen_list:
            po_factors.append("财星坏印")
        # 偏印混杂
        if "偏印" in shishen_list:
            po_factors.append("偏印混杂，印格不纯")
        # 官杀生印
        if "七杀" in shishen_list or "正官" in shishen_list:
            cheng_factors.append("官杀生印")

    elif geku_name == "偏印格":
        shishen_list = [get_shishen(day_stem_idx, GAN_IDX.get(s, 0)) for s in all_stems]

        # 枭神夺食
        if "食神" not in shishen_list and "偏印" in shishen_list:
            po_factors.append("无食神，枭神夺食（潜在破格）")
        # 食神制化
        if "食神" in shishen_list:
            cheng_factors.append("食神制化偏印")

    elif geku_name == "正财格":
        shishen_list = [get_shishen(day_stem_idx, GAN_IDX.get(s, 0)) for s in all_stems]

        # 被劫
        if "劫财" in shishen_list:
            po_factors.append("劫财分夺，破格")
        # 身旺
        month_branch_idx = bazi["month"]["branch_idx"]
        STEM_LING_DEFU = {
            0: [2, 3], 1: [2, 3], 2: [5, 6], 3: [5, 6],
            4: [1, 4, 7, 10], 5: [1, 4, 7, 10],
            6: [8, 9], 7: [8, 9], 8: [0, 11], 9: [0, 11],
        }
        if month_branch_idx in STEM_LING_DEFU.get(day_stem_idx, []):
            cheng_factors.append("身旺，可任财")
        else:
            po_factors.append("身弱，难任财")

    elif geku_name == "偏财格":
        shishen_list = [get_shishen(day_stem_idx, GAN_IDX.get(s, 0)) for s in all_stems]

        # 被劫
        if "劫财" in shishen_list:
            po_factors.append("劫财分夺，破格")

    elif geku_name == "食神格":
        shishen_list = [get_shishen(day_stem_idx, GAN_IDX.get(s, 0)) for s in all_stems]

        # 枭神夺食
        if "偏印" in shishen_list:
            po_factors.append("偏印夺食，破格")
        # 伤官泄食
        if "伤官" in shishen_list:
            po_factors.append("伤官泄食，制秀无力")

    elif geku_name == "伤官格":
        shishen_list = [get_shishen(day_stem_idx, GAN_IDX.get(s, 0)) for s in all_stems]

        # 见官
        if "正官" in shishen_list or "七杀" in shishen_list:
            po_factors.append("伤官见官，破格")

    # ============================================================
    # 3. 综合定级
    # ============================================================
    factors = cheng_factors + po_factors

    if not rules:
        # 无具体规则时，按透干级别简单判定
        if pattern_info and pattern_info.get("tou_level") in ["本气", "中气"]:
            level = "中等"
            is_cheng = True
        else:
            level = "下等"
            is_cheng = False
    else:
        # 有具体规则时，优先检查破格因素
        if po_factors:
            level = "破格"
            is_cheng = False
        elif len(cheng_factors) >= 2:
            level = "上等"
            is_cheng = True
        elif len(cheng_factors) == 1:
            level = "中等"
            is_cheng = True
        else:
            level = "下等"
            is_cheng = False

    # ============================================================
    # 4. 建议
    # ============================================================
    if level == "上等":
        suggestion = f"{geku_name}成格，宜保护格局不被破坏，名字宜辅佐格局"
    elif level == "中等":
        suggestion = f"{geku_name}中等成格，名字宜补足短板助益格局"
    elif level == "下等":
        suggestion = f"{geku_name}格局较弱，名字宜扶助格局核心用神"
    else:
        suggestion = f"{geku_name}破格，需化解破格因素，名字宜补足关键用神"

    return {
        "is_cheng": is_cheng,
        "level": level,
        "factors": factors,
        "cheng_count": len(cheng_factors),
        "po_count": len(po_factors),
        "suggestion": suggestion,
    }


# ============================================================
# 9. 格局综合分析
# ============================================================

def analyze_pattern(bazi: Dict[str, Any]) -> Dict[str, Any]:
    """
    完整格局分析（格局取用 + 成败判定）

    Args:
        bazi: 八字字典

    Returns:
        {
            "pattern_info": {...},   # determine_pattern 结果
            "cheng_info": {...},     # judge_pattern_cheng 结果
        }
    """
    pattern_info = determine_pattern(bazi)
    cheng_info = judge_pattern_cheng(pattern_info["pattern"], bazi, pattern_info)

    return {
        "pattern_info": pattern_info,
        "cheng_info": cheng_info,
    }


# ============================================================
# 10. 格局评分（名字对格局的影响）
# ============================================================

def score_by_pattern(name_chars: str,
                     pattern_info: Dict[str, Any],
                     cheng_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    格局评分：名字是否助益格局

    规则：
    - 格局已成 → 名字不宜破坏格局
    - 格局未成 → 名字宜成全格局

    Args:
        name_chars: 名字字符串
        pattern_info: 格局取用结果
        cheng_info: 格局成败结果

    Returns:
        {
            "score": int,    # 0-30
            "factors": list,  # 加分/减分因素
            "reason": str,
        }
    """
    if not pattern_info or not cheng_info:
        return {"score": 0, "factors": [], "reason": "格局信息不完整"}

    geku_name = pattern_info["pattern"]
    level = cheng_info["level"]
    is_cheng = cheng_info["is_cheng"]

    # 十神关键字
    shishen_in_name: Dict[str, int] = {}

    # 分析名字中每个字的五行和十神
    factors = []
    score = 0

    # 如果格局破格，名字中最好不要出现破格因素
    if not is_cheng or level == "破格":
        # 破格时，名字应避开破格因素
        po_factors = cheng_info.get("factors", [])
        for pf in po_factors:
            # 检查名字中是否有相关字（简化处理：检查字的五行/天干）
            pass  # 简化版暂不实现

    # 中等及以上成格：名字宜助益格局
    if is_cheng and level in ["上等", "中等"]:
        # 格局已成，名字宜配合格局核心
        # 这里简化处理：给正向评分
        score += 10
        factors.append(f"{geku_name}{level}成格，名字配合格局+{10}分")

    return {
        "score": min(score, 30),
        "factors": factors,
        "reason": f"格局{geku_name}{level}，{'已成' if is_cheng else '未成或破格'}，{'; '.join(factors) if factors else '名字对格局影响中性'}",
    }


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    from bazi_engine import get_bazi

    print("=== 子平格局法测试 ===\n")

    # 测试用例：甲辰年 丁辰月 庚丑日 辛午时
    # 月令辰：本气戊土，中气乙木，余气癸水
    # 月干丁：丁火克庚金 → 伤官（但月令本气是戊，不是丁）
    # 格局？
    print("【测试1】甲辰年 丁辰月 庚丑日 辛午时")
    bazi_raw = get_bazi(2024, 3, 15, 10)
    bazi = bazi_raw["bazi"]  # get_bazi returns wrapper dict
    print(f"  八字: {bazi_raw['birth_chart']}")

    pattern_info = determine_pattern(bazi)
    print(f"  格局: {pattern_info['pattern']}")
    print(f"  类型: {pattern_info['pattern_type']}")
    print(f"  透干级别: {pattern_info['tou_level']}")
    print(f"  判断原因: {pattern_info['reason']}")

    cheng_info = judge_pattern_cheng(pattern_info["pattern"], bazi, pattern_info)
    print(f"  成败: {cheng_info['level']}")
    print(f"  因素: {', '.join(cheng_info['factors'])}")
    print(f"  建议: {cheng_info['suggestion']}")
    print()

    # 测试用例2：正官格验证
    print("【测试2】壬寅年 辛亥月 甲午日 甲子时（官格）")
    bazi2_raw = get_bazi(2024, 11, 15, 23)
    bazi2 = bazi2_raw["bazi"]
    print(f"  八字: {bazi2_raw['birth_chart']}")

    pattern_info2 = determine_pattern(bazi2)
    print(f"  格局: {pattern_info2['pattern']}")
    print(f"  透干级别: {pattern_info2['tou_level']}")
    print(f"  判断原因: {pattern_info2['reason']}")

    cheng_info2 = judge_pattern_cheng(pattern_info2["pattern"], bazi2, pattern_info2)
    print(f"  成败: {cheng_info2['level']}")
    print(f"  因素: {', '.join(cheng_info2['factors'])}")
    print()

    # 测试用例3：食神格
    print("【测试3】甲子年 丙寅月 乙酉日 丁亥时（食神格）")
    bazi3_raw = get_bazi(2024, 2, 15, 21)
    bazi3 = bazi3_raw["bazi"]
    print(f"  八字: {bazi3_raw['birth_chart']}")

    pattern_info3 = determine_pattern(bazi3)
    print(f"  格局: {pattern_info3['pattern']}")
    print(f"  判断原因: {pattern_info3['reason']}")

    cheng_info3 = judge_pattern_cheng(pattern_info3["pattern"], bazi3, pattern_info3)
    print(f"  成败: {cheng_info3['level']}")
    print(f"  因素: {', '.join(cheng_info3['factors'])}")
    print()

    # 测试用例4：壬辰月令（本气戊，中气乙，余气癸）
    print("【测试4】壬辰月令验证")
    for year, month in [(2024, 4), (2024, 5)]:
        bazi_t_raw = get_bazi(year, month, 1, 12)
        bazi_t = bazi_t_raw["bazi"]
        pattern = determine_pattern(bazi_t)
        print(f"  {year}-{month:02d}: 月令={bazi_t['month']['branch']} {pattern['pattern']} ({pattern['tou_level']})")
    print()

    # 测试透干分析
    print("【测试5】透干分析")
    bazi5_raw = get_bazi(2024, 3, 15, 10)
    bazi5 = bazi5_raw["bazi"]
    tougan = analyze_tougan(bazi5)
    print(f"  四柱天干: {tougan['all_stems']}")
    print(f"  透干: {tougan['tougan']}")
    print()

    yue_pattern = get_yue_pattern_stems(bazi5)
    month_branch_val = bazi5['month']['branch']
    print(f"  月令{month_branch_val}藏干: 本气{yue_pattern['benqi']}, 中气{yue_pattern['zhongqi']}, 余气{yue_pattern['yuzhi']}")
    print(f"  透干级别: {yue_pattern['tou_level']}")
    print(f"  透干详情: {yue_pattern['tou_detail']}")
    print()

    print("=== 测试完成 ===")
