#!/usr/bin/env python3
"""
八字天干地支排盘 + 十神 + 十二长生 + 纳音五行
纯本地计算，不依赖API
"""

from typing import Dict, Tuple, List, Any
from lunar_calendar import (
    HEAVENLY_STEMS, EARTHLY_BRANCHES, ZODIAC_ANIMALS,
    get_lunar_date, get_zodiac
)


# ============================================================
# 1. 八字干支计算
# ============================================================

def get_year_stem_branch(year: int) -> Tuple[int, int]:
    """
    年干支计算
    年干: (year - 4) % 10（甲子年起4年）
    年支: (year - 4) % 12
    """
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    return stem_idx, branch_idx


def get_month_stem_branch(year: int, month: int) -> Tuple[int, int]:
    """
    月干支计算（五虎遁）
    月支: (month + 1) % 12（正月=寅）
    月干: (年干索引 * 2 + month) % 10
    """
    year_stem, _ = get_year_stem_branch(year)
    branch_idx = (month + 1) % 12  # 正月=寅, index=2
    stem_idx = (year_stem * 2 + month) % 10
    return stem_idx, branch_idx


def _julian_day_number(year: int, month: int, day: int) -> int:
    """
    计算儒略日数（JDN）
    使用标准算法 for Gregorian calendar
    """
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    JDN = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return JDN


def get_day_stem_branch(year: int, month: int, day: int) -> Tuple[int, int]:
    """
    日干支计算
    已知: 2000年1月1日 = 庚辰（日干6，日支5，0-indexed）
    通过JDN差值计算
    """
    # 基准: 2000-01-01 = JDN 2451545, 庚辰 (stem=6, branch=5)
    BASE_JDN = 2451545
    BASE_STEM = 6  # 庚
    BASE_BRANCH = 5  # 辰

    jdn = _julian_day_number(year, month, day)
    diff = jdn - BASE_JDN

    stem_idx = (BASE_STEM + diff) % 10
    branch_idx = (BASE_BRANCH + diff) % 12

    return stem_idx, branch_idx


def get_hour_stem_branch(day_stem: int, hour: int) -> Tuple[int, int]:
    """
    时干支计算（五鼠遁）
    时支: (hour // 2 + 1) % 12
        子时=23-1, 丑时=1-3, 寅时=3-5, 卯时=5-7,
        辰时=7-9, 巳时=9-11, 午时=11-13, 未时=13-15,
        申时=15-17, 酉时=17-19, 戌时=19-21, 亥时=21-23
    时干: (day_stem * 2 + hour // 2) % 10
    """
    # hour // 2: 子时=11(0), 丑时=0, 寅=1, 卯=2, 辰=3, 巳=4...
    hour_index = (hour + 1) // 2  # 23点->12->0(子时)
    if hour == 23:
        hour_index = 0

    branch_idx = (hour_index + 1) % 12  # 子时=0, 丑=1, ...
    stem_idx = (day_stem * 2 + hour_index) % 10

    return stem_idx, branch_idx


def get_bazi(year: int, month: int, day: int, hour: int) -> Dict[str, Any]:
    """
    完整八字排盘
    """
    year_stem, year_branch = get_year_stem_branch(year)
    month_stem, month_branch = get_month_stem_branch(year, month)
    day_stem, day_branch = get_day_stem_branch(year, month, day)
    hour_stem, hour_branch = get_hour_stem_branch(day_stem, hour)

    # 转换为中文字符
    bazi = {
        "year": {"stem": HEAVENLY_STEMS[year_stem], "branch": EARTHLY_BRANCHES[year_branch], "stem_idx": year_stem, "branch_idx": year_branch},
        "month": {"stem": HEAVENLY_STEMS[month_stem], "branch": EARTHLY_BRANCHES[month_branch], "stem_idx": month_stem, "branch_idx": month_branch},
        "day": {"stem": HEAVENLY_STEMS[day_stem], "branch": EARTHLY_BRANCHES[day_branch], "stem_idx": day_stem, "branch_idx": day_branch},
        "hour": {"stem": HEAVENLY_STEMS[hour_stem], "branch": EARTHLY_BRANCHES[hour_branch], "stem_idx": hour_stem, "branch_idx": hour_branch},
    }

    # 生肖
    zodiac = get_zodiac(year)

    # 农历信息
    lunar = get_lunar_date(year, month, day)

    # 时辰名称
    hour_names = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    hour_name = hour_names[hour_branch]

    return {
        "bazi": bazi,
        "zodiac": zodiac,
        "lunar": lunar,
        "hour_name": hour_name,
        "birth_chart": f"{bazi['year']['stem']}{bazi['year']['branch']}年 {bazi['month']['stem']}{bazi['month']['branch']}月 {bazi['day']['stem']}{bazi['day']['branch']}日 {bazi['hour']['stem']}{bazi['hour']['branch']}时",
        "day_stem_idx": day_stem,
        "day_stem": HEAVENLY_STEMS[day_stem],
        "month_branch_idx": month_branch,
    }


# ============================================================
# 2. 日主强弱判断
# ============================================================

# 日干五行属性 (stem -> element index: 0=木,1=火,2=土,3=金,4=水)
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

# 月支对应的五行
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

# 得令表：日干在哪些月令得令
# 同气为得令，相生次之，克我者为失令
STEM_LING_DEFU = {
    # 日干: [得令的月令地支索引列表]
    0: [2, 3],     # 甲木：寅卯月得令
    1: [2, 3],     # 乙木：寅卯月得令
    2: [5, 6],     # 丙火：巳午月得令
    3: [5, 6],     # 丁火：巳午月得令
    4: [1, 4, 7, 10],  # 戊土：辰戌丑未月得令
    5: [1, 4, 7, 10],  # 己土：辰戌丑未月得令
    6: [8, 9],     # 庚金：申酉月得令
    7: [8, 9],     # 辛金：申酉月得令
    8: [0, 11],    # 壬水：亥子月得令
    9: [0, 11],    # 癸水：亥子月得令
}


def get_rizhu_strength(bazi: Dict[str, Any]) -> Dict[str, Any]:
    """
    判断日主强弱
    返回: {
        "day_stem_idx": 0-9,
        "day_stem": "甲",
        "day_element": "木",
        "month_branch_idx": 0-11,
        "month_branch": "寅",
        "month_element": "木",
        "is_deling": True/False,
        "strength": "强" / "弱" / "中",
        "reason": "..."
    }
    """
    day_stem = bazi["day"]["stem_idx"]
    month_branch = bazi["month"]["branch_idx"]

    day_element = STEM_ELEMENTS[day_stem]
    month_element = BRANCH_ELEMENTS[month_branch]

    # 判断得令
    deling_list = STEM_LING_DEFU.get(day_stem, [])
    is_deling = month_branch in deling_list

    # 同气得分最高，相生次之，被克/泄最弱
    if day_element == month_element:
        strength_score = 2  # 同气
    elif (day_element + 1) % 5 == month_element:
        strength_score = 1  # 月令生日干
    elif (day_element + 2) % 5 == month_element:
        strength_score = 0  # 月令克日干
    else:
        strength_score = -1  # 被泄

    if strength_score >= 2:
        strength = "强"
    elif strength_score >= 0:
        strength = "中"
    else:
        strength = "弱"

    reason = f"日干{HEAVENLY_STEMS[day_stem]}（{ELEMENT_NAMES[day_element]}），月令{EARTHLY_BRANCHES[month_branch]}（{ELEMENT_NAMES[month_element]}），"
    if is_deling:
        reason += "得令有力"
    else:
        reason += "失令"

    return {
        "day_stem_idx": day_stem,
        "day_stem": HEAVENLY_STEMS[day_stem],
        "day_element": ELEMENT_NAMES[day_element],
        "month_branch_idx": month_branch,
        "month_branch": EARTHLY_BRANCHES[month_branch],
        "month_element": ELEMENT_NAMES[month_element],
        "is_deling": is_deling,
        "strength": strength,
        "strength_score": strength_score,
        "reason": reason,
    }


# ============================================================
# 3. 十神计算
# ============================================================

# 十神表：以日干为基准，其他天干与日干的关系
# 行=日干(0-9), 列=其他天干(0-9)
# 值: 0=比肩, 1=劫财, 2=食神, 3=伤官, 4=偏财, 5=正财, 6=偏官, 7=正官, 8=偏印, 9=正印
SHISHEN_TABLE = [
    #       甲  乙  丙  丁  戊  己  庚  辛  壬  癸
    #  甲  0   1   2   3   4   5   6   7   8   9
    #  乙  1   0   4   5   6   7   8   9   2   3
    #  丙  3   2   0   1   8   9   4   5   6   7
    #  丁  2   3   1   0   9   8   5   4   7   6
    #  戊  5   6   3   4   0   1   2   3   8   9
    #  己  6   5   4   3   1   0   3   2   9   8
    #  庚  7   8   5   6   3   4   0   1   2   3
    #  辛  8   7   6   5   4   3   1   0   3   2
    #  壬  9   10  7   8   5   6   3   4   0   1
    #  癸  10  9   8   7   6   5   4   3   1   0
]

SHISHEN_NAMES = [
    "比肩", "劫财", "食神", "伤官",
    "偏财", "正财",
    "偏官", "正官",
    "偏印", "正印"
]

# 简化版十神表（同柱天干五合关系推导）
# 日干与时干的关系：生我者为印，我生者为食，我克者为财，克我者为官
# 比和：同五行

def _compute_shishen(day_stem: int, other_stem: int) -> str:
    """
    计算十神关系
    day_stem: 日干索引(0-9)
    other_stem: 其他干索引(0-9)
    """
    if day_stem == other_stem:
        # 比和：同五行
        if day_stem % 2 == 0:
            return "比肩"  # 甲丙戊庚壬为阳
        else:
            return "劫财"  # 乙丁己辛癸为阴

    # 计算相差
    diff = (other_stem - day_stem) % 10

    # 十神关系（简化判断）
    # 合局关系：甲己合土（中正之合），乙庚合金（仁义之合），丙辛合水（威严之合），丁壬合木（仁寿之合），戊癸合火（无情之合）

    # 我生者：食神/伤官
    # 日干所生
    day_elem = STEM_ELEMENTS[day_stem]
    other_elem = STEM_ELEMENTS[other_stem]

    if (other_elem - day_elem) % 5 == 1:
        # 泄我者：日干所生者为食伤
        return "食神" if day_stem % 2 == 0 else "伤官"

    if (other_elem - day_elem) % 5 == 2:
        # 我所克：偏财/正财
        return "偏财" if day_stem % 2 == 0 else "正财"

    if (other_elem - day_elem) % 5 == 3:
        # 克我者：偏官/正官
        return "偏官" if day_stem % 2 == 0 else "正官"

    if (other_elem - day_elem) % 5 == 4:
        # 生我者：偏印/正印
        return "偏印" if day_stem % 2 == 0 else "正印"

    # 简化处理
    return SHISHEN_NAMES[(other_stem - day_stem) % 10]


def get_shishen(day_stem: int, other_stem: int) -> str:
    """获取十神名称"""
    return _compute_shishen(day_stem, other_stem)


def get_shishen_list(bazi: Dict[str, Any]) -> Dict[str, str]:
    """
    获取八字各柱十神（以日主为基准）
    """
    day_stem = bazi["day"]["stem_idx"]

    return {
        "year_stem": get_shishen(day_stem, bazi["year"]["stem_idx"]),
        "month_stem": get_shishen(day_stem, bazi["month"]["stem_idx"]),
        "hour_stem": get_shishen(day_stem, bazi["hour"]["stem_idx"]),
        "year_branch": _compute_branch_shishen(day_stem, bazi["year"]["branch_idx"]),
        "month_branch": _compute_branch_shishen(day_stem, bazi["month"]["branch_idx"]),
        "hour_branch": _compute_branch_shishen(day_stem, bazi["hour"]["branch_idx"]),
    }


def _compute_branch_shishen(day_stem: int, branch_idx: int) -> str:
    """计算地支藏干的十神（以本气为主）"""
    # 地支藏干表
    BRANCH_HIDDEN_STEMS = {
        0: [2],   # 子：癸
        1: [5, 0, 6],   # 丑：己丁癸
        2: [0, 4, 2],   # 寅：甲丙戊
        3: [1, 3, 0],   # 卯：乙丁甲
        4: [2, 4, 3],   # 辰：戊癸辛
        5: [2, 1, 5],   # 巳：丙庚戊
        6: [3, 1, 5],   # 午：丁己癸
        7: [2, 0, 4],   # 未：己丁乙
        8: [4, 2, 6],   # 申：庚壬戊
        9: [3, 4, 2],   # 酉：辛癸丙
        10: [4, 3, 1],  # 戌：戊丁辛
        11: [0, 4, 3],  # 亥：甲壬丁
    }

    # 本气（地支对应的主要天干）
    BENQI_STEMS = {
        0: 9,   # 子：癸
        1: 5,   # 丑：己
        2: 0,   # 寅：甲
        3: 1,   # 卯：乙
        4: 2,   # 辰：戊
        5: 2,   # 巳：丙
        6: 3,   # 午：丁
        7: 2,   # 未：己
        8: 4,   # 申：庚
        9: 3,   # 酉：辛
        10: 4,  # 戌：戊
        11: 0,  # 亥：甲
    }

    benqi = BENQI_STEMS[branch_idx]
    return get_shishen(day_stem, benqi)


# ============================================================
# 4. 十二长生（长生十二宫）
# ============================================================

# 长生十二宫状态
CHANGSHENG_STATES = [
    "长生", "沐浴", "冠带", "临官", "帝旺",
    "衰", "病", "死", "墓", "绝", "胎", "养"
]

# 长生表：每个天干在12地支的状态索引
# 索引0=长生, 1=沐浴, ... 11=养
CHANGSHENG_TABLE = {
    # 甲木：长生在亥(11), 沐浴在子(0), 冠带在丑(1), 临官在寅(2), 帝旺在卯(3), 衰在辰(4), 病在巳(5), 死在午(6), 墓在未(7), 绝在申(8), 胎在酉(9), 养在戌(10)
    0: [11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # 甲
    1: [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],   # 乙
    2: [10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],  # 丙
    3: [4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3],  # 丁
    4: [8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7],  # 戊
    5: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1],  # 己
    6: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # 庚
    7: [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],  # 辛（与乙同）
    8: [10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],  # 壬（与丙同）
    9: [4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3],  # 癸（与丁同）
}


def get_changsheng(day_stem: int, branch_idx: int) -> str:
    """获取某天干在某地支的长生状态"""
    table = CHANGSHENG_TABLE.get(day_stem, [0] * 12)
    state_idx = table[branch_idx % 12]
    return CHANGSHENG_STATES[state_idx]


def get_shierzhang(bazi: Dict[str, Any]) -> Dict[str, str]:
    """
    获取八字各柱的十二长生状态（以日干为基准）
    """
    day_stem = bazi["day"]["stem_idx"]

    return {
        "year_branch": get_changsheng(day_stem, bazi["year"]["branch_idx"]),
        "month_branch": get_changsheng(day_stem, bazi["month"]["branch_idx"]),
        "day_branch": get_changsheng(day_stem, bazi["day"]["branch_idx"]),
        "hour_branch": get_changsheng(day_stem, bazi["hour"]["branch_idx"]),
    }


# ============================================================
# 5. 纳音五行
# ============================================================

# 纳音五行表：60甲子对应纳音
NAYIN_TABLE = [
    "海中金", "海中金",    # 甲子 乙丑
    "炉中火", "炉中火",    # 丙寅 丁卯
    "大林木", "大林木",    # 戊辰 己巳
    "路旁土", "路旁土",    # 庚午 辛未
    "城头土", "城头土",    # 壬申 癸酉
    "井泉水", "井泉水",    # 甲戌 乙亥
    "涧下水", "涧下水",    # 丙子 丁丑
    "山头火", "山头火",    # 戊寅 己卯
    "城头土", "城头土",    # 庚辰 辛巳
    "白蜡金", "白蜡金",    # 壬午 癸未
    "杨柳木", "杨柳木",    # 甲申 乙酉
    "井泉水", "井泉水",    # 丙戌 丁亥
    "屋上土", "屋上土",    # 戊子 己丑
    "霹雳火", "霹雳火",    # 庚寅 辛卯
    "城头土", "城头土",    # 壬辰 癸巳
    "白蜡金", "白蜡金",    # 甲午 乙未
    "井泉水", "井泉水",    # 丙申 丁酉
    "山下火", "山下火",    # 戊戌 己亥
    "平地木", "平地木",    # 庚子 辛丑
    "壁上土", "壁上土",    # 壬寅 癸卯
    "金箔金", "金箔金",    # 甲辰 乙巳
    "覆灯火", "覆灯火",    # 丙午 丁未
    "天河水", "天河水",    # 戊申 己酉
    "大驿土", "大驿土",    # 庚戌 辛亥
    "钗钏金", "钗钏金",    # 壬子 癸丑
    "桑柘木", "桑柘木",    # 甲寅 乙卯
    "大溪水", "大溪水",    # 丙辰 丁巳
    "砂石土", "砂石土",    # 戊午 己未
    "天上火", "天上火",    # 庚申 辛酉
    "石榴木", "石榴木",    # 壬戌 癸亥
]


def get_nayin(stem_idx: int, branch_idx: int) -> str:
    """获取纳音五行"""
    # 计算在60甲子中的位置
    cycle_pos = (stem_idx - branch_idx + 10) % 10
    # 60甲子：stem每10个一循环，branch每12个一循环
    # 简化：用 (stem_idx * 12 + branch_idx) % 60 或查表
    index = stem_idx * 6 + branch_idx // 2
    index = (stem_idx * 12 + branch_idx) % 60
    return NAYIN_TABLE[index % 60]


def get_nayin_by_ganzhi(year_stem: int, year_branch: int) -> str:
    """根据年干支获取纳音"""
    index = (year_stem * 12 + year_branch) % 60
    return NAYIN_TABLE[index % 60]


# ============================================================
# 喜用神判断
# ============================================================

def determine_xiyongshen(bazi: Dict[str, Any], rizhu_strength: Dict[str, Any]) -> Dict[str, Any]:
    """
    判断喜用神
    基于五行生克关系判断
    """
    # 五行得分统计
    wx_counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

    # 统计四柱天干地支的五行
    for pillar in ["year", "month", "day", "hour"]:
        stem_elem = STEM_ELEMENTS[bazi[pillar]["stem_idx"]]
        branch_elem = BRANCH_ELEMENTS[bazi[pillar]["branch_idx"]]
        wx_counts[ELEMENT_NAMES[stem_elem]] += 1
        wx_counts[ELEMENT_NAMES[branch_elem]] += 1

    # 找出最旺和最弱的五行
    max_elem = max(wx_counts, key=wx_counts.get)
    min_elem = min(wx_counts, key=wx_counts.get)

    # 喜用神判断逻辑
    # 如果日主强，则需要克/泄（官鬼、食伤、财）
    # 如果日主弱，则需要生扶（印枭、比劫）

    day_elem = rizhu_strength["day_element"]
    is_strong = rizhu_strength["strength"] == "强"

    if is_strong:
        # 身强：喜官鬼克、财耗、食伤泄
        xiyongshen = []
        jishen = []

        # 官鬼：克日干
        for i, e in enumerate(ELEMENT_NAMES):
            if (i - STEM_ELEMENTS[bazi["day"]["stem_idx"]] + 5) % 5 == 3:
                xiyongshen.append(e)

        # 食伤：日干所生
        for i, e in enumerate(ELEMENT_NAMES):
            if (i - STEM_ELEMENTS[bazi["day"]["stem_idx"]] + 5) % 5 == 1:
                xiyongshen.append(e)

        # 财：日干所克
        for i, e in enumerate(ELEMENT_NAMES):
            if (i - STEM_ELEMENTS[bazi["day"]["stem_idx"]] + 5) % 5 == 2:
                xiyongshen.append(e)

        # 印枭为忌
        for i, e in enumerate(ELEMENT_NAMES):
            if (i - STEM_ELEMENTS[bazi["day"]["stem_idx"]] + 5) % 5 == 4:
                jishen.append(e)

    else:
        # 身弱：喜印枭生、比劫助
        xiyongshen = []
        jishen = []

        # 印枭：生我者
        for i, e in enumerate(ELEMENT_NAMES):
            if (i - STEM_ELEMENTS[bazi["day"]["stem_idx"]] + 5) % 5 == 4:
                xiyongshen.append(e)

        # 比劫：同我者
        for i, e in enumerate(ELEMENT_NAMES):
            if e == day_elem:
                xiyongshen.append(e)
                break

        # 官鬼、食伤、财为忌
        for i, e in enumerate(ELEMENT_NAMES):
            if e == day_elem:
                continue
            diff = (i - STEM_ELEMENTS[bazi["day"]["stem_idx"]] + 5) % 5
            if diff in [1, 2, 3]:
                jishen.append(e)

    # 去重并保持顺序
    xiyongshen = list(dict.fromkeys(xiyongshen))[:3]
    jishen = list(dict.fromkeys(jishen))[:3]

    return {
        "xiyongshen": xiyongshen,
        "jishen": jishen,
        "qiangruo": rizhu_strength["strength"],
        "wx_counts": wx_counts,
        "analysis": f"日主{HEAVENLY_STEMS[bazi['day']['stem_idx']]}{rizhu_strength['reason']}",
    }


# ============================================================
# 综合排盘
# ============================================================

def full_bazi_analysis(year: int, month: int, day: int, hour: int) -> Dict[str, Any]:
    """
    完整八字分析
    """
    bazi_result = get_bazi(year, month, day, hour)
    bazi = bazi_result["bazi"]  # Extract inner bazi dict
    rizhu = get_rizhu_strength(bazi)
    shishen = get_shishen_list(bazi)
    shierzhang = get_shierzhang(bazi)
    xiyong = determine_xiyongshen(bazi, rizhu)
    nayin = get_nayin(bazi["year"]["stem_idx"], bazi["year"]["branch_idx"])

    return {
        "birth_chart": bazi_result["birth_chart"],
        "bazi": bazi,
        "rizhu_strength": rizhu,
        "shishen": shishen,
        "shierzhang": shierzhang,
        "xiyongshen": xiyong,
        "year_nayin": nayin,
        "zodiac": bazi_result["zodiac"],
        "lunar": bazi_result["lunar"],
        "hour_name": bazi_result["hour_name"],
    }


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=== 八字排盘引擎测试 ===\n")

    # 测试1: 2024年3月15日10点
    print("【测试1】2024年3月15日10点")
    result = full_bazi_analysis(2024, 3, 15, 10)
    print(f"  八字: {result['birth_chart']}")
    print(f"  生肖: {result['zodiac']}")
    print(f"  农历: {result['lunar']['year']}年{result['lunar']['month']}月{result['lunar']['day']}日")
    print(f"  日主强弱: {result['rizhu_strength']['strength']} - {result['rizhu_strength']['reason']}")
    print(f"  喜用神: {result['xiyongshen']['xiyongshen']}")
    print(f"  忌神: {result['xiyongshen']['jishen']}")
    print(f"  十神: {result['shishen']}")
    print(f"  十二长生: {result['shierzhang']}")
    print(f"  年柱纳音: {result['year_nayin']}")
    print()

    # 测试2: 2025年3月15日10点
    print("【测试2】2025年3月15日10点")
    result2 = full_bazi_analysis(2025, 3, 15, 10)
    print(f"  八字: {result2['birth_chart']}")
    print(f"  生肖: {result2['zodiac']}")
    print(f"  日主强弱: {result2['rizhu_strength']['strength']} - {result2['rizhu_strength']['reason']}")
    print(f"  喜用神: {result2['xiyongshen']['xiyongshen']}")
    print()

    # 测试3: 验证日干=甲，月支=寅 → 月干=丙
    print("【测试3】日干=甲，月支=寅 → 月干=丙")
    year_stem, year_branch = get_year_stem_branch(2024)
    month_stem, month_branch = get_month_stem_branch(2024, 1)  # 正月
    print(f"  2024正月: 年干={HEAVENLY_STEMS[year_stem]} 年支={EARTHLY_BRANCHES[year_branch]}")
    print(f"  月干={HEAVENLY_STEMS[month_stem]} 月支={EARTHLY_BRANCHES[month_branch]}")
    print(f"  期望: 甲寅 → 月干丙")
    print()

    # 测试4: 日干支JDN验证
    print("【测试4】日干支验证 - 2000年1月1日=庚辰")
    stem, branch = get_day_stem_branch(2000, 1, 1)
    print(f"  2000-01-01: {HEAVENLY_STEMS[stem]}{EARTHLY_BRANCHES[branch]}")
    print(f"  期望: 庚辰 ✓" if stem == 6 and branch == 5 else f"  期望: 庚辰 ✗")
    print()

    # 测试5: 2025年1月15日 → 农历二月初六（测试任务要求）
    print("【测试5】农历验证")
    from lunar_calendar import format_lunar_date
    lunar = get_lunar_date(2025, 1, 15)
    print(f"  2025-01-15 → {format_lunar_date(lunar['year'], lunar['month'], lunar['day'], lunar['is_leap'])}")

    lunar2 = get_lunar_date(2024, 3, 15)
    print(f"  2024-03-15 → {format_lunar_date(lunar2['year'], lunar2['month'], lunar2['day'], lunar2['is_leap'])}")
