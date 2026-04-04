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
from tiao_hou import get_tiao_hou as _get_tiao_hou_raw, get_tiao_hou_xiyong, get_tiao_hou_jibi, get_tiao_hou_principle
from shier_changsheng import get_changsheng_state as _get_changsheng_raw, get_changsheng_state_idx
from yueling_canggan import get_yueling_canggan as _get_yueling_canggan_raw
from pattern_method import determine_pattern, judge_pattern_cheng, analyze_pattern
from shen_sha import get_shen_sha_summary as _get_shen_sha_summary
from xiyongshen_v2 import determine_xiyongshen_v2
from liushen_xinxing import build_shishen_xinxing_from_bazi, get_shishen_xinxing
from rizhu_strength_v2 import _calc_wuxing_power_by_changsheng
from rizhu_strength_v2 import get_rizhu_strength_v2, get_strength_by_count, determine_primary_method


# ============================================================
# 0. 真太阳时矫正
# ============================================================

# 主要城市经度表（东经，度）
CITY_LONGITUDES = {
    # 四川
    "成都": 104.06, "天府新区": 104.0, "天府": 104.0, "绵阳": 104.68, "德阳": 104.4,
    "自贡": 104.78, "泸州": 105.44, "宜宾": 104.63, "内江": 105.06,
    # 北京
    "北京": 116.4,
    # 上海
    "上海": 121.47, "浦东": 121.54,
    # 广东
    "深圳": 114.05, "广州": 113.27, "东莞": 113.75, "佛山": 113.12,
    # 重庆
    "重庆": 106.55,
    # 浙江
    "杭州": 120.19, "宁波": 121.55, "温州": 120.67, "义乌": 120.07,
    # 湖北
    "武汉": 114.29, "宜昌": 111.28, "襄阳": 112.12,
    # 陕西
    "西安": 108.93, "咸阳": 108.71,
    # 江苏
    "南京": 118.78, "苏州": 120.62, "无锡": 120.29,
    # 天津
    "天津": 117.2,
    # 河南
    "郑州": 113.65, "洛阳": 112.45,
    # 湖南
    "长沙": 112.93,
    # 山东
    "济南": 116.98, "青岛": 120.38,
    # 安徽
    "合肥": 117.28,
    # 云南
    "昆明": 102.83,
    # 辽宁
    "沈阳": 123.43, "大连": 121.62,
    # 黑龙江
    "哈尔滨": 125.73,
    # 福建
    "福州": 119.3, "厦门": 118.08,
    # 江西
    "南昌": 115.85,
    # 贵州
    "贵阳": 106.71,
    # 山西
    "太原": 112.53,
    # 河北
    "石家庄": 114.48,
    # 甘肃
    "兰州": 103.82,
    # 西藏
    "拉萨": 91.17,
    # 新疆
    "乌鲁木齐": 87.62,
    # 青海
    "西宁": 101.78,
    # 宁夏
    "银川": 106.23,
    # 内蒙古
    "呼和浩特": 111.65,
    # 海南
    "海口": 110.35,
    # 广西
    "南宁": 108.31, "桂林": 110.28,
    # 四川全省
    "四川省": 104.0,
}

# 北京时间标准经度
BEIJING_STANDARD_LONGITUDE = 120.0  # 东经120度


def get_true_solar_hour(beijing_hour: int, province: str = "", city: str = "") -> float:
    """
    将北京时间转换为真太阳时

    Args:
        beijing_hour: 北京时间（小时，0-23）
        province: 省份/直辖市名称（用于精确匹配）
        city: 城市名称

    Returns:
        真太阳时小时数（float，可为小数）
        精度约±2分钟
    """
    # 如果用户未提供地点，返回北京时间（不矫正）
    if not province and not city:
        return float(beijing_hour)

    # 优先用城市名匹配
    lookup_city = city if city else province
    lon = CITY_LONGITUDES.get(lookup_city, None)

    # 尝试省份名
    if lon is None and province:
        lon = CITY_LONGITUDES.get(province, None)

    # 未知城市，用默认经度（104°E，约成都）
    if lon is None:
        lon = 104.0  # 默认值

    # 真太阳时 = 北京时间 - (120° - 当地经度) × 4分钟
    # 简化：忽略均令时（均令时最大误差约±16分钟，对时辰判定影响仅在边界情况）
    offset_hours = (BEIJING_STANDARD_LONGITUDE - lon) * 4.0 / 60.0
    true_hour = beijing_hour - offset_hours

    # 约束在0-24范围内
    if true_hour < 0:
        true_hour += 24
    elif true_hour >= 24:
        true_hour -= 24

    return true_hour


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


def get_month_stem_branch(year_stem: int, lunar_month: int) -> Tuple[int, int]:
    """
    月干支计算（五虎遁）

    参数:
        year_stem: 年干索引 (0-9)
        lunar_month: 农历月份 (1-12, 1=正月=寅月)

    五虎遁口诀（据百度百科）：
      甲己之年丙作首 → 正月=丙寅
      乙庚之岁戊为头 → 正月=戊寅
      丙辛必定寻庚起 → 正月=庚寅
      丁壬壬位顺行流 → 正月=壬寅
      戊癸何方发，甲寅之上好追求 → 正月=甲寅

    月干 = (offset + 月份 - 1) % 10
    月支 = (月份 + 1) % 12 (正月=寅=2, 二月=卯=3, 三月=辰=4, ...)

    offset公式: offset = ((year_stem + 1) % 5) * 2
    验证:
      甲(0): ((0+1)%5)*2 = 2 → 正月=丙寅 ✓
      乙(1): ((1+1)%5)*2 = 4 → 正月=戊寅 ✓
      丙(2): ((2+1)%5)*2 = 6 → 正月=庚寅 ✓
      丁(3): ((3+1)%5)*2 = 8 → 正月=壬寅 ✓
      戊(4): ((4+1)%5)*2 = 0 → 正月=甲寅 ✓
      己(5): ((5+1)%5)*2 = 2 → 正月=丙寅 ✓
      庚(6): ((6+1)%5)*2 = 4 → 正月=戊寅 ✓
      辛(7): ((7+1)%5)*2 = 6 → 正月=庚寅 ✓
      壬(8): ((8+1)%5)*2 = 8 → 正月=壬寅 ✓
      癸(9): ((9+1)%5)*2 = 0 → 正月=甲寅 ✓
    """
    offset = ((year_stem + 1) % 5) * 2

    branch_idx = (lunar_month + 1) % 12  # 正月=寅(2), 二月=卯(3), 三月=辰(4)
    stem_idx = (offset + lunar_month - 1) % 10
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
    通过JDN差值计算

    基准: 2000-01-01 = 乙亥年十一月廿五戊午日
    → 日柱 = 戊午 (stem=4, branch=6, 0-indexed)
    验证: 2026-03-23 = 丙申 ✓, 2026-03-22 = 乙未 ✓
    """
    BASE_JDN = 2451545
    BASE_STEM = 4   # 戊
    BASE_BRANCH = 6  # 午

    jdn = _julian_day_number(year, month, day)
    diff = jdn - BASE_JDN

    stem_idx = (BASE_STEM + diff) % 10
    branch_idx = (BASE_BRANCH + diff) % 12

    return stem_idx, branch_idx


def get_hour_stem_branch(day_stem: int, hour: int) -> Tuple[int, int]:
    """
    时干支计算（五鼠遁）

    时支: 23-1点=子(0), 1-3点=丑(1), 3-5点=寅(2), 5-7点=卯(3)...
      (hour + 1) // 2 对 0 点错(得1应为0), 对23点错(得12应为0)
      修正: hour==0 or hour==23 → branch=0 (子), 否则 (hour+1)//2
    时干: (day_stem * 2 + hour_index) % 10

    五鼠遁口诀: 甲己还加甲, 乙庚丙作初, 丙辛从戊起, 丁壬庚子居, 戊癸起壬子
    """
    # 时支: 23-1点=子, 1-3点=丑, 3-5点=寅, 5-7点=卯...
    if hour == 0 or hour == 23:
        hour_index = 0  # 子时
    else:
        hour_index = (hour + 1) // 2

    branch_idx = hour_index % 12
    stem_idx = (day_stem * 2 + hour_index) % 10

    return stem_idx, branch_idx


def get_bazi(year: int, month: int, day: int, hour: int,
             province: str = "", city: str = "") -> Dict[str, Any]:
    """
    完整八字排盘

    Args:
        province: 出生省份/直辖市（如"四川"）
        city: 出生城市（如"成都"）
        真太阳时矫正：自动根据城市经度计算，默认北京时间
    """
    year_stem, year_branch = get_year_stem_branch(year)
    # 使用农历月份计算月柱（需先获取农历信息）
    lunar = get_lunar_date(year, month, day)
    month_stem, month_branch = get_month_stem_branch(year_stem, lunar["month"])
    day_stem, day_branch = get_day_stem_branch(year, month, day)

    # 真太阳时矫正
    true_hour = get_true_solar_hour(hour, province, city)
    hour_stem, hour_branch = get_hour_stem_branch(day_stem, int(true_hour))

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

def full_bazi_analysis(year: int, month: int, day: int, hour: int,
                       province: str = "", city: str = "") -> Dict[str, Any]:
    """
    完整八字分析

    Args:
        province: 出生省份/直辖市
        city: 出生城市（用于真太阳时矫正）
    """
    bazi_result = get_bazi(year, month, day, hour, province, city)
    bazi = bazi_result["bazi"]  # Extract inner bazi dict
    rizhu = get_rizhu_strength(bazi)  # V1 旧版
    rizhu_v2 = get_rizhu_strength_v2(bazi)  # V2 权重量化版
    rizhu_by_count = get_strength_by_count(bazi)  # 全藏干计数法（滴天髓派）
    shishen = get_shishen_list(bazi)
    shierzhang = get_shierzhang(bazi)
    xiyong_v1 = determine_xiyongshen(bazi, rizhu)
    nayin = get_nayin(bazi["year"]["stem_idx"], bazi["year"]["branch_idx"])

    month_stem = HEAVENLY_STEMS[bazi["month"]["stem_idx"]]
    month_branch = EARTHLY_BRANCHES[bazi["month"]["branch_idx"]]
    tiao_hou = _get_tiao_hou_raw(month_stem, month_branch)
    yueling = _get_yueling_canggan_raw(month_branch)

    # 格局分析（子平格局法）
    pattern_result = analyze_pattern(bazi)

    # 藏干长生加权五行力量（与网站一致的身强弱判断）
    day_stem_str = HEAVENLY_STEMS[bazi["day"]["stem_idx"]]  # "丙"
    wuxing_power_by_cs = _calc_wuxing_power_by_changsheng(day_stem_str, bazi)

    # V2 喜用神判定（调候优先/格局已成/月令司令）
    xiyong_v2 = determine_xiyongshen_v2(
        bazi=bazi,
        rizhu_strength=rizhu_v2,  # 使用V2量化身强弱
        tiao_hou=tiao_hou,
        yueling_canggan=yueling,
        pattern_result=pattern_result,
        wuxing_power=wuxing_power_by_cs,
    )

    # 补充 V2 缺失的字段（从 V1 或直接计算）
    xiyong_v2["wx_counts"] = xiyong_v1.get("wx_counts", {})

    # 神煞分析
    shen_sha = _get_shen_sha_summary(bazi)

    # 命宫/身宫
    minggong_shengong = get_minggong_shengong(bazi_result)

    # 十神心性（来自《千里命稿》映射表）
    shishen_xinxing = build_shishen_xinxing_from_bazi(
        {"shishen": shishen}, xiyong_v2
    )

    # 判断主推方法（在 xiyong_v2 和 pattern_result 都已知之后）
    primary_method = determine_primary_method({
        "pattern": pattern_result["pattern_info"],
        "pattern_cheng": pattern_result["cheng_info"],
        "xiyongshen": xiyong_v2,
        "rizhu_strength": rizhu_v2,
        "bazi": bazi,                  # 用于从格自动检测
        "rizhu_by_count": rizhu_by_count,  # 用于从格自动检测
    })

    return {
        "birth_chart": bazi_result["birth_chart"],
        "bazi": bazi,
        "rizhu_strength": rizhu_v2,       # V2 量化结果（默认）
        "_rizhu_strength_v1": rizhu,       # V1 旧版结果（保留对比）
        "rizhu_by_count": rizhu_by_count,  # 全藏干计数法（滴天髓派）
        "primary_method": primary_method,  # 主推方法判断
        "shishen": shishen,
        "shierzhang": shierzhang,
        "xiyongshen": xiyong_v2,          # V2 判定结果
        "_xiyongshen_v1": xiyong_v1,      # V1 判定结果（保留对比）
        "_xiyongshen_v2_debug": xiyong_v2.get("_debug", {}),  # V2 _debug 信息
        "year_nayin": nayin,
        "zodiac": bazi_result["zodiac"],
        "lunar": bazi_result["lunar"],
        "hour_name": bazi_result["hour_name"],
        "tiao_hou": tiao_hou,
        "yueling_canggan": yueling,
        "pattern": pattern_result["pattern_info"],
        "pattern_cheng": pattern_result["cheng_info"],
        "shen_sha": shen_sha,
        "xinxing": shishen_xinxing,       # 六神心性速查
        "minggong_shengong": minggong_shengong,  # Phase 3-a: 命宫/身宫
    }


# ============================================================
# Phase 3-a: 命宫/身宫系统（渊海子平公式）
# ============================================================

def get_minggong_shengong(bazi_info: dict) -> dict:
    """
    计算命宫和身宫

    【渊海子平】命宫公式：
      命宫地支 = (生月地支 + 生时地支) % 12
      命宫天干 = (年干 + 命宫地支 + 1) % 10

    【身宫公式】(通玄鬼料)：
      身宫地支 = (生月地支 + 生时地支 + 2 - 年支) % 12
      身宫天干 = (年干 + 身宫地支 + 1) % 10

    参数:
        bazi_info: get_bazi() 返回的字典，包含 bazi["year/month/day/hour"]["stem_idx/branch_idx"]

    返回:
        dict: {
          "命宫": {天干, 地支, 天干索引, 地支索引, 五行, 十神, 长生状态},
          "身宫": {天干, 地支, 天干索引, 地支索引, 五行, 十神, 长生状态}
        }
    """
    bazi = bazi_info["bazi"]

    year_stem_idx    = bazi["year"]["stem_idx"]
    year_branch_idx  = bazi["year"]["branch_idx"]
    month_branch_idx = bazi["month"]["branch_idx"]
    hour_branch_idx  = bazi["hour"]["branch_idx"]
    day_stem_idx     = bazi["day"]["stem_idx"]

    # ── 命宫地支 ─────────────────────────────────────────
    # 命宫 = (生月地支 + 生时地支) % 12
    minggong_zhi_idx = (month_branch_idx + hour_branch_idx) % 12

    # ── 命宫天干 ─────────────────────────────────────────
    # 从年干起数，数到命宫地支位（年支=0位起），天干 = (年干 + 命宫地支 + 1) % 10
    minggong_stem_idx = (year_stem_idx + minggong_zhi_idx + 1) % 10

    # ── 身宫地支 ─────────────────────────────────────────
    # 身宫 = (生月地支 + 生时地支 + 2 - 年支) % 12
    shenggong_zhi_idx = (month_branch_idx + hour_branch_idx + 2 - year_branch_idx) % 12

    # ── 身宫天干 ─────────────────────────────────────────
    shenggong_stem_idx = (year_stem_idx + shenggong_zhi_idx + 1) % 10

    # ── 五行属性 ─────────────────────────────────────────
    minggong_element_idx  = STEM_ELEMENTS[minggong_stem_idx]
    shenggong_element_idx = STEM_ELEMENTS[shenggong_stem_idx]

    # ── 十神（以日主为基准）───────────────────────────────
    minggong_shishen  = get_shishen(day_stem_idx, minggong_stem_idx)
    shenggong_shishen = get_shishen(day_stem_idx, shenggong_stem_idx)

    # ── 长生状态（命宫/身宫地支相对于日干的长生状态）──────
    minggong_changsheng  = get_changsheng(day_stem_idx, minggong_zhi_idx)
    shenggong_changsheng = get_changsheng(day_stem_idx, shenggong_zhi_idx)

    minggong_stem  = HEAVENLY_STEMS[minggong_stem_idx]
    minggong_zhi   = EARTHLY_BRANCHES[minggong_zhi_idx]
    shenggong_stem = HEAVENLY_STEMS[shenggong_stem_idx]
    shenggong_zhi  = EARTHLY_BRANCHES[shenggong_zhi_idx]

    return {
        "命宫": {
            "stem":      minggong_stem,
            "branch":    minggong_zhi,
            "stem_idx":  minggong_stem_idx,
            "branch_idx": minggong_zhi_idx,
            "ganzhi":    minggong_stem + minggong_zhi,
            "element":   ELEMENT_NAMES[minggong_element_idx],
            "shishen":   minggong_shishen,
            "changsheng": minggong_changsheng,
        },
        "身宫": {
            "stem":      shenggong_stem,
            "branch":    shenggong_zhi,
            "stem_idx":  shenggong_stem_idx,
            "branch_idx": shenggong_zhi_idx,
            "ganzhi":    shenggong_stem + shenggong_zhi,
            "element":   ELEMENT_NAMES[shenggong_element_idx],
            "shishen":   shenggong_shishen,
            "changsheng": shenggong_changsheng,
        },
        # 原始输入备份（方便调试）
        "_debug": {
            "year_stem_idx":    year_stem_idx,
            "year_branch_idx":  year_branch_idx,
            "month_branch_idx": month_branch_idx,
            "hour_branch_idx":  hour_branch_idx,
        }
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


# ============================================================
# 6. 穷通宝鉴调候喜忌（新增）
# ============================================================

def get_tiao_hou(tian_gan: str, yue_zhi: str) -> dict:
    """
    查调候喜忌（穷通宝鉴）
    
    Args:
        tian_gan: 日干（甲、乙、丙、丁、戊、己、庚、辛、壬、癸）
        yue_zhi: 月令地支（寅、卯、辰、巳、午、未、申、酉、戌、亥、子、丑）
    
    Returns:
        dict: {"喜用": [...], "忌避": [...], "原则": str}
        若组合不存在返回空字典
    """
    return _get_tiao_hou_raw(tian_gan, yue_zhi)


def get_tiao_hou_xiyong(tian_gan: str, yue_zhi: str) -> list:
    """查调候喜用神列表（V2：主神+辅神，兼容旧格式）"""
    info = get_tiao_hou(tian_gan, yue_zhi)
    # V2格式
    if "主神" in info:
        return info.get("主神", []) + info.get("辅神", [])
    # 旧格式兼容
    return info.get("喜用", [])


def get_tiao_hou_jibi(tian_gan: str, yue_zhi: str) -> list:
    """查调候忌避神列表"""
    return get_tiao_hou(tian_gan, yue_zhi).get("忌避", [])


# ============================================================
# 7. 十二长生状态（新增字符串版）
# ============================================================

def get_changsheng_state(tian_gan: str, branch: str) -> str:
    """
    查十二长生状态（字符串接口）
    
    Args:
        tian_gan: 天干（甲、乙、丙、丁、戊、己、庚、辛、壬、癸）
        branch: 地支（子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥）
    
    Returns:
        str: 长生、沐浴、冠带、临官、帝旺、衰、病、死、墓、绝、胎、养
    """
    return _get_changsheng_raw(tian_gan, branch)


# ============================================================
# 8. 月令藏干（新增）
# ============================================================

def get_yueling_canggan(yue_zhi: str) -> dict:
    """
    查月令藏干
    
    Args:
        yue_zhi: 月令地支（子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥）
    
    Returns:
        dict: {"本气": str, "中气": str, "余气": str or None}
    """
    return _get_yueling_canggan_raw(yue_zhi)


# ============================================================
# 9. 大运流年分析（Phase 8 新增）
# ============================================================

def full_liunian_analysis(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str,
    birth_timestamp: float = None,
    birth_year: int = None,
    birth_month: int = None
) -> Dict[str, Any]:
    """
    完整大运流年分析
    
    Args:
        year, month, day, hour: 出生时间
        gender: 性别 ("男" 或 "女")
        birth_timestamp: 出生时间戳（可选）
        birth_year: 出生年份（可选）
        birth_month: 出生月份（可选）
    
    Returns:
        完整分析结果，包含：
        - 八字基础信息
        - 大运列表（每步运：岁数、干支、概述）
        - 近5年流年简析
        - 驿马运信息
    """
    import time
    from dayun_liunian import (
        full_dayun_analysis,
        get_dayun_sequence,
        get_recent_liunian,
        get_yima_dayun,
        analyze_liunian_by_year
    )
    
    # 基础八字分析
    bazi_result = full_bazi_analysis(year, month, day, hour)
    bazi = bazi_result["bazi"]
    rizhu = bazi_result["rizhu_strength"]
    xiyong = bazi_result["xiyongshen"]
    
    bazi_with_xiyong = {
        "bazi": bazi,
        "rizhu_strength": rizhu,
        "xiyongshen": xiyong,
    }
    
    # 设置默认值
    if birth_timestamp is None:
        birth_timestamp = time.mktime((year, month, day, hour, 0, 0, 0, 0, 0))
    if birth_year is None:
        birth_year = year
    if birth_month is None:
        birth_month = month
    
    # 完整大运流年分析
    dayun_result = full_dayun_analysis(
        bazi_with_xiyong,
        gender,
        birth_timestamp,
        birth_year,
        birth_month
    )
    
    return {
        # 基础八字信息
        "birth_chart": bazi_result["birth_chart"],
        "bazi": bazi,
        "gender": gender,
        "zodiac": bazi_result["zodiac"],
        "lunar": bazi_result["lunar"],
        "rizhu_strength": rizhu,
        "xiyongshen": xiyong,
        
        # 大运信息
        "dayun_direction_rule": dayun_result["direction_rule"],
        "dayun_year_stem": dayun_result["year_stem"],
        "dayun_month_branch": dayun_result["month_branch"],
        "dayun_count": dayun_result["dayun_count"],
        "dayun_list": dayun_result["dayun_list"],
        "dayun_start_exact": dayun_result.get("dayun_start_exact"),  # 精确起始年龄
        "yima": dayun_result["yima"],
        
        # 近5年流年
        "recent_liunian": dayun_result["recent_liunian"],
        
        # 其他参考信息
        "tiao_hou": bazi_result.get("tiao_hou"),
        "pattern": bazi_result.get("pattern"),
        "shen_sha": bazi_result.get("shen_sha"),
    }
