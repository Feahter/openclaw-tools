#!/usr/bin/env python3
"""
大运流年推算系统
参考《千里命稿》《滴天髓》实现本地大运流年推算算法

核心功能：
1. 大运起法：阳男阴女顺行，阴男阳女逆行
2. 流年分析：与大运+命局综合判断生克冲合
3. 十年运势概述：给定大运干支+用神计算吉凶概要

纯本地计算，不依赖API
"""

from typing import Dict, Tuple, List, Any, Optional
from datetime import datetime
import sys
import os

# 导入八字引擎常量
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bazi_engine import (
    HEAVENLY_STEMS, EARTHLY_BRANCHES,
    STEM_ELEMENTS, ELEMENT_NAMES, BRANCH_ELEMENTS,
    get_shishen, STEM_LING_DEFU
)
try:
    from shier_changsheng import get_changsheng_state, CHANGSHENG_ORDER
except ImportError:
    get_changsheng_state = None
    CHANGSHENG_ORDER = ["长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养"]

# 导入节气计算（用于精确大运起始日期）
try:
    from lunar_calendar import get_next_jieqi_after_date, JIEQI_TABLE
except ImportError:
    get_next_jieqi_after_date = None
    JIEQI_TABLE = {}


# ============================================================
# 常量定义
# ============================================================

# 天干地支索引映射
STEM_IDX = {s: i for i, s in enumerate(HEAVENLY_STEMS)}
BRANCH_IDX = {b: i for i, b in enumerate(EARTHLY_BRANCHES)}

# 阳干列表
YANG_STEMS = {"甲", "丙", "戊", "庚", "壬"}
YANG_STEM_IDX = [0, 2, 4, 6, 8]  # 甲丙戊庚壬

# 地支顺序（用于顺逆计算）
BRANCH_ORDER = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五行相生：木生火→火生土→土生金→金生水→水生木
# 索引差1为相生
ELEMENT_BEATEN = {
    # 克我者为官鬼
    0: 3,  # 木被金克
    1: 4,  # 火被水克
    2: 0,  # 土被木克
    3: 1,  # 金被火克
    4: 2,  # 水被土克
}

# 五行相克
ELEMENT_RELATIONS = {
    # 我克者为财
    0: 2,  # 木克土为财
    1: 3,  # 火克金为财
    2: 4,  # 土克水为财
    3: 0,  # 金克木为财
    4: 1,  # 水克火为财
}

# 地支六冲（对冲的地支索引）
BRANCH_CHONGS = {
    0: 6,   # 子午冲
    1: 7,   # 丑未冲
    2: 8,   # 寅申冲
    3: 9,   # 卯酉冲
    4: 10,  # 辰戌冲
    5: 11,  # 巳亥冲
    6: 0,   # 午子冲
    7: 1,   # 未丑冲
    8: 2,   # 申寅冲
    9: 3,   # 酉卯冲
    10: 4,  # 戌辰冲
    11: 5,  # 亥巳冲
}

# 地支相合（可合化的地支对）
# 子丑合化土, 寅亥合化木, 卯戌合化火, 辰酉合化金, 巳申合化水, 午未合化火/土
BRANCH_HES = {
    0: {1: 2},   # 子丑合化土(寅)
    1: {0: 2},   # 丑子合化土(寅)
    2: {11: 0},  # 寅亥合化木(寅)
    3: {10: 1},  # 卯戌合化火(巳)
    4: {9: 3},   # 辰酉合化金(申)
    5: {8: 4},   # 巳申合化水(亥)
    6: {7: 2},   # 午未合化土(寅) 或合化火(午)
    7: {6: 2},   # 未午合化土(寅) 或合化火(午)
    8: {5: 4},   # 申巳合化水(亥)
    9: {4: 3},   # 酉辰合化金(申)
    10: {3: 1},  # 戌卯合化火(巳)
    11: {2: 0},  # 亥寅合化木(寅)
}

# 天干相合
# 甲己合土, 乙庚合金, 丙辛合水, 丁壬合木, 戊癸合火
STEM_HES = {
    0: {5: 2},   # 甲己合化土
    1: {6: 3},   # 乙庚合化金
    2: {7: 4},   # 丙辛合化水
    3: {8: 0},   # 丁壬合化木
    4: {9: 1},   # 戊癸合化火
    5: {0: 2},   # 己甲合化土
    6: {1: 3},   # 庚乙合化金
    7: {2: 4},   # 辛丙合化水
    8: {3: 0},   # 壬丁合化木
    9: {4: 1},   # 癸戊合化火
}


# ============================================================
# 1. 大运起法
# ============================================================

def is_yang_stem(stem_idx: int) -> bool:
    """判断天干阴阳（阳干：甲丙戊庚壬）"""
    return stem_idx in YANG_STEM_IDX


def is_shun(start_stem_idx: int, gender: str) -> bool:
    """
    判断大运顺逆
    阳男阴女顺行，阴男阳女逆行
    
    Args:
        start_stem_idx: 年干索引
        gender: "男" 或 "女"
    
    Returns:
        True=顺行, False=逆行
    """
    yang = is_yang_stem(start_stem_idx)
    if gender == "男":
        return yang  # 阳男顺，阴男逆
    else:
        return not yang  # 阴女顺，阳女逆


def get_next_branch(branch_idx: int, shun: bool, steps: int = 1) -> int:
    """
    计算下一个地支位置
    
    Args:
        branch_idx: 当前地支索引
        shun: True=顺行，False=逆行
        steps: 步数（通常为1或10）
    
    Returns:
        新的地支索引
    """
    if shun:
        return (branch_idx + steps) % 12
    else:
        return (branch_idx - steps) % 12


def get_month_stem_from_dayun(
    month_branch_idx: int,
    start_stem_idx: int,
    shun: bool,
    year_offset: int
) -> int:
    """
    计算大运月干
    
    大运月干的计算：每年大运走一柱，从月柱开始顺逆数
    简化算法：从月柱天干开始，按大运方向推算
    
    Args:
        month_branch_idx: 月支索引
        start_stem_idx: 大运起始天干索引
        shun: 是否顺行
        year_offset: 年偏移（0=第一个大运）
    
    Returns:
        大运天干索引
    """
    # 月干五虎遁：年干索引 * 2 + 月份(1-12) ≡ 月干索引 (mod 10)
    # 大运月干 = (起始月干 + 顺逆方向 * 年偏移) % 10
    # 月柱天干索引
    month_stem = (start_stem_idx * 2 + (month_branch_idx + 2)) % 10  # 月支寅=2
    
    # 根据大运方向推算
    # 从月柱开始，每10年一步运
    if shun:
        result = (month_stem + year_offset) % 10
    else:
        result = (month_stem - year_offset) % 10
    return result


def _calc_dayun_branch_sequence(
    month_branch_idx: int,
    year_stem_idx: int,
    gender: str
) -> List[int]:
    """
    计算大运地支序列（从月柱开始）
    
    阳男阴女顺行，阴男阳女逆行
    """
    shun = is_shun(year_stem_idx, gender)
    
    # 12个大运地支（除去重复）
    branches = []
    current = month_branch_idx
    for i in range(12):
        branches.append(current)
        current = get_next_branch(current, shun, 1)
    
    return branches


def _calc_dayun_stem_sequence(
    month_stem_idx: int,
    year_stem_idx: int,
    gender: str
) -> List[int]:
    """
    计算大运天干序列
    """
    shun = is_shun(year_stem_idx, gender)
    
    stems = []
    current = month_stem_idx
    for i in range(12):
        stems.append(current)
        if shun:
            current = (current + 1) % 10
        else:
            current = (current - 1) % 10
    
    return stems


def get_dayun_sequence(
    bazi_info: Dict[str, Any],
    gender: str,
    birth_timestamp: float
) -> List[Dict[str, Any]]:
    """
    获取大运序列
    
    Args:
        bazi_info: 八字信息，包含 bazi dict 和 day_stem_idx 等
        gender: "男" 或 "女"
        birth_timestamp: 出生时间戳（秒，UTC epoch）
    
    Returns:
        大运列表，每步运包含：start_age, end_age, stem, branch, ganzhi
    """
    bazi = bazi_info.get("bazi", bazi_info)
    year_stem_idx = bazi["year"]["stem_idx"]
    month_stem_idx = bazi["month"]["stem_idx"]
    month_branch_idx = bazi["month"]["branch_idx"]
    
    # 判断顺逆
    shun = is_shun(year_stem_idx, gender)
    direction_str = "顺行" if shun else "逆行"
    
    # 计算大运地支序列
    dayun_branches = _calc_dayun_branch_sequence(month_branch_idx, year_stem_idx, gender)
    dayun_stems = _calc_dayun_stem_sequence(month_stem_idx, year_stem_idx, gender)
    
    # 计算起始年龄
    # 出生后多久进入第一步大运（通常从几岁开始）
    birth_dt = datetime.fromtimestamp(birth_timestamp)
    
    # 计算精确大运起始年龄（基于节气）
    dayun_start_exact = get_dayun_start_age_exact(birth_dt.year, birth_dt.month, birth_dt.day)
    first_start_age = dayun_start_exact["years"]
    
    dayuns = []
    for i in range(12):
        start_age = first_start_age + i * 10
        end_age = start_age + 9
        
        dayun_info = {
            "index": i,
            "start_age": start_age,
            "end_age": end_age,
            "start_age_exact": dayun_start_exact if i == 0 else None,  # Only first entry has exact age
            "stem_idx": dayun_stems[i],
            "branch_idx": dayun_branches[i],
            "stem": HEAVENLY_STEMS[dayun_stems[i]],
            "branch": EARTHLY_BRANCHES[dayun_branches[i]],
            "ganzhi": HEAVENLY_STEMS[dayun_stems[i]] + EARTHLY_BRANCHES[dayun_branches[i]],
            "direction": direction_str,
            "shun": shun,
        }
        dayuns.append(dayun_info)
    
    return dayuns


def get_dayun_with_exact_age(
    bazi_info: Dict[str, Any],
    gender: str,
    birth_year: int,
    birth_month: int
) -> List[Dict[str, Any]]:
    """
    获取精确起始年龄的大运序列

    根据出生月份计算第一步大运的起始年龄
    大运起始年龄公式（传统《千里命稿》）：
    - 第一步大运起始年龄 ≈ (12 - 出生农历月) ÷ 3 ≈ 3岁（以月令为起点）
    - 每10年走一步大运
    """
    bazi = bazi_info.get("bazi", bazi_info)
    year_stem_idx = bazi["year"]["stem_idx"]
    month_stem_idx = bazi["month"]["stem_idx"]
    month_branch_idx = bazi["month"]["branch_idx"]
    day_stem_idx = bazi["day"]["stem_idx"]

    shun = is_shun(year_stem_idx, gender)
    direction_str = "顺行" if shun else "逆行"

    dayun_branches = _calc_dayun_branch_sequence(month_branch_idx, year_stem_idx, gender)
    dayun_stems = _calc_dayun_stem_sequence(month_stem_idx, year_stem_idx, gender)

    # 第一步大运起始年龄：
    # 传统公式: (12 - 农历月) ÷ 3，向上取整
    # 出生农历月通常从1(寅月)到12(丑月)
    # 例如：月2(卯月) → (12-2)÷3 = 3.3 → 取整为3岁
    import math
    first_start_age = max(0, math.ceil((12 - birth_month) / 3))

    dayuns = []
    for i in range(12):
        start_age = first_start_age + i * 10
        end_age = start_age + 9

        dayun_info = {
            "index": i,
            "start_age": start_age,
            "end_age": end_age,
            "stem_idx": dayun_stems[i],
            "branch_idx": dayun_branches[i],
            "stem": HEAVENLY_STEMS[dayun_stems[i]],
            "branch": EARTHLY_BRANCHES[dayun_branches[i]],
            "ganzhi": HEAVENLY_STEMS[dayun_stems[i]] + EARTHLY_BRANCHES[dayun_branches[i]],
            "direction": direction_str,
            "shun": shun,
        }

        # 计算大运地支的十二长生状态（日干在该地支的长生状态）
        if get_changsheng_state is not None:
            dayun_branch_name = EARTHLY_BRANCHES[dayun_branches[i]]
            dayun_stem_name = HEAVENLY_STEMS[day_stem_idx]  # 日干名
            state = get_changsheng_state(dayun_stem_name, dayun_branch_name)
            dayun_info["changsheng"] = state

        dayuns.append(dayun_info)

    return dayuns


def get_dayun_start_age_exact(year: int, month: int, day: int) -> Dict[str, Any]:
    """
    精确计算大运起始年龄（岁+月+天）
    
    基于节气的大运起法公式（传统《千里命稿》改进版）：
    - 找到出生日期之后的第一个节气
    - 计算天数
    - days / 3.65 ≈ 起始岁数(小数)
    - 转换为 Y岁M个月D天
    
    注意: 实际命理网站可能有微小差异(使用3.75-4.0作为除数)，
    这取决于具体派别的计算方法。本函数使用3.65作为标准值。
    
    Args:
        year: 出生公历年
        month: 出生公历月
        day: 出生公历日
    
    Returns:
        {
            "years": N,           # 起始岁数(整数年)
            "months": M,           # 剩余月数
            "days": D,            # 剩余天数
            "decimal_years": X.X, # 小数岁数
            "days_total": N,      # 到节气总天数
            "next_jieqi": "清明", # 下一个节气名
            "next_jieqi_date": "4/5", # 下一个节气月/日
        }
    """
    if get_next_jieqi_after_date is None:
        # Fallback: use simple formula
        import math
        return {
            "years": 0, "months": 0, "days": 0,
            "decimal_years": 0.0, "days_total": 0,
            "next_jieqi": "N/A", "next_jieqi_date": "N/A",
        }
    
    jieqi_name, jieqi_date, days = get_next_jieqi_after_date(year, month, day)
    
    if jieqi_date is None or days >= 999:
        return {
            "years": 0, "months": 0, "days": 0,
            "decimal_years": 0.0, "days_total": days,
            "next_jieqi": "N/A", "next_jieqi_date": "N/A",
        }
    
    # Formula: days / 3.65 ≈ decimal years
    # 3.65 accounts for 365.25 days/year and the traditional 大运 counting
    decimal_years = days / 3.65
    
    # Convert to years + months + days
    total_months = int(decimal_years * 12)
    years = total_months // 12
    remaining_months = total_months % 12
    # remaining days: fractional part of decimal_years converted to days
    remaining_days = int((decimal_years - int(decimal_years)) * 30)
    
    return {
        "years": years,
        "months": remaining_months,
        "days": remaining_days,
        "decimal_years": round(decimal_years, 2),
        "days_total": days,
        "next_jieqi": jieqi_name,
        "next_jieqi_date": f"{jieqi_date.month}/{jieqi_date.day}",
    }


# ============================================================
# 2. 驿马运（特殊大运）
# ============================================================

def get_yima_dayun(year_stem_idx: int, year_branch_idx: int, gender: str) -> Optional[Dict[str, Any]]:
    """
    计算驿马运所在的大运
    
    驿马口诀（年支为主）：
    申子辰马在寅（寅申冲）
    亥卯未马在巳（巳亥冲）
    寅午戌马在申（寅申冲）
    巳酉丑马在亥（巳亥冲）
    
    Args:
        year_stem_idx: 年干索引
        year_branch_idx: 年支索引
        gender: 性别
    
    Returns:
        驿马运信息，包含驿马地支和大运索引，或None
    """
    # 驿马地支（基于年支）
    YIMA_BRANCH = {
        0: 3,   # 子年马在寅
        1: 4,   # 丑年马在辰
        2: 5,   # 寅年马在巳
        3: 0,   # 卯年马在子
        4: 1,   # 辰年马在丑
        5: 2,   # 巳年马在寅
        6: 3,   # 午年马在寅
        7: 4,   # 未年马在辰
        8: 5,   # 申年马在巳
        9: 0,   # 酉年马在子
        10: 1,  # 戌年马在丑
        11: 2,  # 亥年马在寅
    }
    
    yima_branch_idx = YIMA_BRANCH.get(year_branch_idx)
    if yima_branch_idx is None:
        return None
    
    yima_branch = EARTHLY_BRANCHES[yima_branch_idx]
    
    # 计算大运序列，找到驿马所在的大运索引
    shun = is_shun(year_stem_idx, gender)
    month_branch_idx = 2  # 默认月支为寅
    
    # 从月柱地支开始找
    dayun_branches = _calc_dayun_branch_sequence(month_branch_idx, year_stem_idx, gender)
    
    for i, branch_idx in enumerate(dayun_branches):
        if branch_idx == yima_branch_idx:
            return {
                "yima_branch": yima_branch,
                "yima_branch_idx": yima_branch_idx,
                "dayun_index": i,
                "dayun_ganzhi": HEAVENLY_STEMS[0] + yima_branch,  # 简化，天干需要计算
                "age_range": f"{i*10}-{(i+1)*10-1}",
                "description": f"驿马运，奔波走动之象",
            }
    
    return None


# ============================================================
# 3. 大运吉凶分析
# ============================================================

def analyze_dayun(
    dayun_stem_idx: int,
    dayun_branch_idx: int,
    bazi_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    分析单步大运的吉凶
    
    Args:
        dayun_stem_idx: 大运天干索引
        dayun_branch_idx: 大运地支索引
        bazi_info: 八字信息（包含 xiyongshen 等）
    
    Returns:
        大运分析结果
    """
    bazi = bazi_info.get("bazi", bazi_info)
    xiyong = bazi_info.get("xiyongshen", {})
    xiyong_list = xiyong.get("xiyongshen", [])
    jishen_list = xiyong.get("jishen", [])
    day_stem_idx = bazi["day"]["stem_idx"]
    day_elem = STEM_ELEMENTS[day_stem_idx]
    day_stem_name = HEAVENLY_STEMS[day_stem_idx]
    
    dayun_stem_elem = STEM_ELEMENTS[dayun_stem_idx]
    dayun_branch_elem = BRANCH_ELEMENTS[dayun_branch_idx]
    dayun_stem_name = HEAVENLY_STEMS[dayun_stem_idx]
    dayun_branch_name = EARTHLY_BRANCHES[dayun_branch_idx]
    
    # 计算大运天干与日主的关系
    shishen_stem = get_shishen(day_stem_idx, dayun_stem_idx)
    
    # 评分计算
    score = 0
    factors = []
    
    # 天干评分
    # 生助用神则吉，克泄用神则凶
    if dayun_stem_name in xiyong_list:
        score += 2
        factors.append(f"大运天干{dayun_stem_name}为喜用神（{shishen_stem}），+2分")
    elif dayun_stem_name in jishen_list:
        score -= 2
        factors.append(f"大运天干{dayun_stem_name}为忌神（{shishen_stem}），-2分")
    else:
        # 中性，看十神关系
        if shishen_stem in ["正官", "七杀", "正印", "偏印"]:
            score += 0
            factors.append(f"大运天干{dayun_stem_name}为{shishen_stem}，中性")
        elif shishen_stem in ["食神", "伤官"]:
            score += 0
            factors.append(f"大运天干{dayun_stem_name}为{shishen_stem}，中性偏泄")
        else:
            score += 0
            factors.append(f"大运天干{dayun_stem_name}为{shishen_stem}")
    
    # 地支评分（简化，主要看地支藏干）
    # 地支与日支的关系
    day_branch_idx = bazi["day"]["branch_idx"]
    if dayun_branch_idx == day_branch_idx:
        # 伏吟，大运与日柱相同，运势反复
        score -= 1
        factors.append(f"地支{dayun_branch_name}伏吟日支，运势反复，-1分")
    
    # 地支六冲（与命局地支）
    chong_count = 0
    for pillar in ["year", "month", "hour"]:
        pillar_branch_idx = bazi[pillar]["branch_idx"]
        if BRANCH_CHONGS.get(dayun_branch_idx) == pillar_branch_idx:
            chong_count += 1
            factors.append(f"大运地支{dayun_branch_name}与{EARTHLY_BRANCHES[pillar_branch_idx]}相冲")
            break
    
    if chong_count > 0:
        score -= chong_count
        factors.append(f"大运地支{dayun_branch_name}冲命局{'' if chong_count==1 else str(chong_count)+'个'}地支，{'动荡' if chong_count==1 else '多动'}")
    
    # 五行生克评分
    # 大运地支五行对日主的影响
    elem_relation = (dayun_branch_elem - day_elem) % 5
    if elem_relation == 1:  # 大运地支生日主
        if dayun_branch_name in xiyong_list:
            score += 1
            factors.append(f"大运地支{ELEMENT_NAMES[dayun_branch_elem]}生日主，得地支之助，+1分")
    elif elem_relation == 2:  # 大运地支泄日主
        if dayun_branch_name in jishen_list:
            score -= 1
            factors.append(f"大运地支{ELEMENT_NAMES[dayun_branch_elem]}泄日主，-1分")
    elif elem_relation == 3:  # 大运地支克日主
        if shishen_stem in ["正官", "七杀"]:
            score += 1 if dayun_branch_name in xiyong_list else -1
            factors.append(f"大运地支{ELEMENT_NAMES[dayun_branch_elem]}为官杀之地")
    elif elem_relation == 4:  # 日主克大运地支
        if dayun_branch_name in xiyong_list:
            score += 1
            factors.append(f"日主克大运地支财，得财之象")
    
    # 判断吉凶
    if score >= 3:
        luck = "大吉"
    elif score >= 1:
        luck = "小吉"
    elif score >= -1:
        luck = "平"
    elif score >= -3:
        luck = "小凶"
    else:
        luck = "大凶"
    
    return {
        "dayun_stem": dayun_stem_name,
        "dayun_branch": dayun_branch_name,
        "shishen": shishen_stem,
        "score": score,
        "luck": luck,
        "factors": factors,
        "analysis": "；".join(factors) if factors else "无特殊影响",
    }


def get_dayun_summary(
    dayun_info: Dict[str, Any],
    bazi_info: Dict[str, Any]
) -> str:
    """
    获取大运十年运势概述
    
    参考《千里命稿》大运判断原则
    """
    analysis = analyze_dayun(
        dayun_info["stem_idx"],
        dayun_info["branch_idx"],
        bazi_info
    )
    
    age_range = f"{dayun_info['start_age']}-{dayun_info['end_age']}岁"
    luck = analysis["luck"]
    stem = analysis["dayun_stem"]
    branch = analysis["dayun_branch"]
    shishen = analysis["shishen"]
    analysis_text = analysis["analysis"]
    
    summary = f"{age_range}岁大运【{stem}{branch}】{shishen}，{luck}。{analysis_text}"
    
    return summary


# ============================================================
# 4. 流年分析
# ============================================================

def get_liunian_ganzhi(year: int) -> Tuple[int, int]:
    """
    计算某年的流年干支
    
    流年地支=年支（固定）
    流年天干=(年干索引 * 2 + 流年) % 10
    """
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    return stem_idx, branch_idx


def get_liunian_score(
    stem1_idx: int, branch1_idx: int,
    stem2_idx: int, branch2_idx: int
) -> int:
    """
    计算两组干支的生克得分（+1/-1/0）
    
    比较stem1-branch1组合与stem2-branch2组合的生克关系
    
    Args:
        stem1_idx, branch1_idx: 第一组干支索引
        stem2_idx, branch2_idx: 第二组干支索引
    
    Returns:
        得分：+1（生助）, -1（克泄）, 0（中性/比和）
    """
    elem1 = STEM_ELEMENTS[stem1_idx]
    elem2 = STEM_ELEMENTS[stem2_idx]
    branch_elem1 = BRANCH_ELEMENTS[branch1_idx]
    branch_elem2 = BRANCH_ELEMENTS[branch2_idx]
    
    score = 0
    
    # 天干生克
    # elem1 生 elem2
    if (elem2 - elem1) % 5 == 1:
        score += 1  # 第一组天干生第二组
    # elem1 克 elem2
    elif (elem1 - elem2) % 5 in [1, 2]:  # 木克土/土克水等
        score -= 1
    # 同五行（比和）
    elif elem1 == elem2:
        score += 0
    
    # 地支生克
    # branch1 生 branch2
    if (branch_elem2 - branch_elem1) % 5 == 1:
        score += 1
    # branch1 克 branch2
    elif (branch_elem1 - branch_elem2) % 5 in [1, 2]:
        score -= 1
    # 同五行
    elif branch_elem1 == branch_elem2:
        score += 0
    
    # 六冲关系
    if BRANCH_CHONGS.get(branch1_idx) == branch2_idx:
        score -= 1  # 相冲减分
    
    # 六合关系
    if branch1_idx in BRANCH_HES and branch2_idx in BRANCH_HES[branch1_idx]:
        score += 1  # 相合加分
    
    return score


def analyze_liunian(
    liunian_stem_idx: int,
    liunian_branch_idx: int,
    bazi_info: Dict[str, Any],
    dayun_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    分析单个流年
    
    Args:
        liunian_stem_idx: 流年天干索引
        liunian_branch_idx: 流年地支索引
        bazi_info: 八字信息
        dayun_info: 当前大运信息（可选）
    
    Returns:
        流年分析结果
    """
    bazi = bazi_info.get("bazi", bazi_info)
    xiyong = bazi_info.get("xiyongshen", {})
    xiyong_list = xiyong.get("xiyongshen", [])
    jishen_list = xiyong.get("jishen", [])
    
    day_stem_idx = bazi["day"]["stem_idx"]
    day_branch_idx = bazi["day"]["branch_idx"]
    day_elem = STEM_ELEMENTS[day_stem_idx]
    
    liunian_stem = HEAVENLY_STEMS[liunian_stem_idx]
    liunian_branch = EARTHLY_BRANCHES[liunian_branch_idx]
    liunian_elem = STEM_ELEMENTS[liunian_stem_idx]
    
    # 流年十神
    liunian_shishen = get_shishen(day_stem_idx, liunian_stem_idx)
    
    # 评分
    score = 0
    factors = []
    
    # 1. 流年天干与日主的关系
    if liunian_stem in xiyong_list:
        score += 1
        factors.append(f"流年天干{liunian_stem}为喜用神")
    elif liunian_stem in jishen_list:
        score -= 1
        factors.append(f"流年天干{liunian_stem}为忌神")
    
    # 2. 流年天干与用神的生克
    for xy in xiyong_list:
        xy_idx = STEM_IDX.get(xy)
        if xy_idx is not None:
            xy_elem = STEM_ELEMENTS[xy_idx]
            if (xy_elem - liunian_elem) % 5 == 1:  # 流年生用神
                score += 1
                factors.append(f"流年天干{liunian_stem}生助喜用神{xy}")
            elif (xy_elem - liunian_elem) % 5 in [1, 2]:  # 流年克用神
                score -= 1
                factors.append(f"流年天干{liunian_stem}克喜用神{xy}")
    
    # 3. 流年地支与命局的冲合
    dayun_impact = 0
    if dayun_info:
        dayun_branch_idx = dayun_info.get("branch_idx")
        if dayun_branch_idx is not None:
            # 大运地支与流年地支的冲合
            if BRANCH_CHONGS.get(dayun_branch_idx) == liunian_branch_idx:
                score -= 1
                factors.append(f"流年{liunian_branch}冲大运{EARTHLY_BRANCHES[dayun_branch_idx]}，动荡")
            elif liunian_branch_idx in BRANCH_HES.get(dayun_branch_idx, {}):
                score += 1
                factors.append(f"流年{liunian_branch}合大运{EARTHLY_BRANCHES[dayun_branch_idx]}，吉")
            
            dayun_impact = get_liunian_score(
                liunian_stem_idx, liunian_branch_idx,
                dayun_info.get("stem_idx", 0), dayun_branch_idx
            )
            score += dayun_impact
    
    # 4. 流年地支与日支的关系
    if BRANCH_CHONGS.get(liunian_branch_idx) == day_branch_idx:
        score -= 1
        factors.append(f"流年{liunian_branch}冲日支{EARTHLY_BRANCHES[day_branch_idx]}，自身动荡")
    elif liunian_branch_idx in BRANCH_HES.get(day_branch_idx, {}):
        score += 1
        factors.append(f"流年{liunian_branch}合日支{EARTHLY_BRANCHES[day_branch_idx]}，人缘相助")
    
    # 5. 流年与小运的关系（简化处理）
    # 流年本身与命局的十神关系
    if liunian_shishen == "正官" and day_elem in [0, 1]:  # 木火日主见官
        score += 1
        factors.append("正官流年，有官运之象")
    elif liunian_shishen == "七杀" and day_elem in [0, 1]:
        score -= 1
        factors.append("七杀流年，需注意小人是非")
    elif liunian_shishen == "食神":
        score += 0
        factors.append("食神流年，创造力发挥")
    elif liunian_shishen == "伤官":
        score -= 0
        factors.append("伤官流年，注意表达方式")
    elif liunian_shishen == "正财":
        score += 1
        factors.append("正财流年，财运稳定")
    elif liunian_shishen == "偏财":
        score += 0
        factors.append("偏财流年，财运起伏")
    
    # 判断吉凶
    if score >= 2:
        luck = "大吉"
    elif score >= 1:
        luck = "小吉"
    elif score >= 0:
        luck = "平"
    elif score >= -1:
        luck = "小凶"
    else:
        luck = "大凶"
    
    return {
        "stem": liunian_stem,
        "branch": liunian_branch,
        "ganzhi": liunian_stem + liunian_branch,
        "shishen": liunian_shishen,
        "score": score,
        "luck": luck,
        "factors": factors,
        "analysis": "；".join(factors) if factors else "无特殊影响",
        "dayun_impact": dayun_impact,
    }


def analyze_liunian_by_year(
    year: int,
    bazi_info: Dict[str, Any],
    dayun_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    根据年份分析流年（增强版）
    
    包含：
    - 流年干支 + 五行
    - 流年与命局的生克关系
    - 流年与大运的叠加效果
    - 简单的吉凶判断 (score: -100 to 100)
    - 简要分析文字 (2-3 sentences)
    
    Args:
        year: 公历年（2020-2050）
        bazi_info: 八字信息（包含 bazi dict, xiyongshen, rizhu_strength 等）
        dayun_info: 当前大运信息（可选）
    
    Returns:
        流年分析结果（增强版）
    """
    stem_idx, branch_idx = get_liunian_ganzhi(year)
    
    # 获取八字基础信息
    bazi = bazi_info.get("bazi", bazi_info)
    xiyong = bazi_info.get("xiyongshen", {})
    rizhu = bazi_info.get("rizhu_strength", {})
    xiyong_list = xiyong.get("xiyongshen", [])
    jishen_list = xiyong.get("jishen", [])
    
    day_stem_idx = bazi["day"]["stem_idx"]
    day_branch_idx = bazi["day"]["branch_idx"]
    day_elem = STEM_ELEMENTS[day_stem_idx]
    day_stem_name = HEAVENLY_STEMS[day_stem_idx]
    day_branch_name = EARTHLY_BRANCHES[day_branch_idx]
    
    liunian_stem_name = HEAVENLY_STEMS[stem_idx]
    liunian_branch_name = EARTHLY_BRANCHES[branch_idx]
    liunian_elem = STEM_ELEMENTS[stem_idx]
    liunian_branch_elem = BRANCH_ELEMENTS[branch_idx]
    
    # 流年十神
    liunian_shishen = get_shishen(day_stem_idx, stem_idx)
    
    # ========== 评分计算 (base: -100 to 100) ==========
    score = 0
    factors = []
    
    # 1. 流年天干是否为喜用神/忌神
    if liunian_stem_name in xiyong_list:
        score += 20
        factors.append(f"流年天干{liunian_stem_name}为喜用神，+20分")
    elif liunian_stem_name in jishen_list:
        score -= 20
        factors.append(f"流年天干{liunian_stem_name}为忌神，-20分")
    
    # 2. 流年天干生助/克泄日主
    # (other_elem - day_elem) % 5 == 1 表示 生我者
    # (other_elem - day_elem) % 5 == 4 表示 我生者
    # (other_elem - day_elem) % 5 == 2 表示 我克者
    # (other_elem - day_elem) % 5 == 3 表示 克我者
    elem_diff = (liunian_elem - day_elem) % 5
    
    is_sheng = elem_diff == 1  # 流年天干生助日主
    isKe = elem_diff in [2, 3]  # 流年天干克泄日主
    
    # 获取身强身弱
    is_strong = rizhu.get("strength") in ["强", "旺"] if rizhu else False
    
    if is_sheng:
        if is_strong:
            score -= 10  # 身旺再得生助则过旺
            factors.append(f"流年天干{liunian_stem_name}生助日主，身旺则不吉，-10分")
        else:
            score += 10  # 身弱得生助则有力
            factors.append(f"流年天干{liunian_stem_name}生助日主，身弱得扶，+10分")
    elif isKe:
        if is_strong:
            score += 10  # 身旺见克泄可平衡
            factors.append(f"流年天干{liunian_stem_name}克泄日主，身旺则可平衡，+10分")
        else:
            score -= 10  # 身弱再被克泄则更弱
            factors.append(f"流年天干{liunian_stem_name}克泄日主，身弱则不利，-10分")
    
    # 3. 流年与大运的叠加效果
    dayun_impact = 0
    if dayun_info:
        dayun_stem_idx_val = dayun_info.get("stem_idx")
        dayun_branch_idx_val = dayun_info.get("branch_idx")
        
        if dayun_stem_idx_val is not None and dayun_branch_idx_val is not None:
            dayun_stem_name_val = HEAVENLY_STEMS[dayun_stem_idx_val]
            dayun_branch_name_val = EARTHLY_BRANCHES[dayun_branch_idx_val]
            
            # 大运天干是否为喜用神/忌神
            if dayun_stem_name_val in xiyong_list:
                score += 15
                factors.append(f"大运天干{dayun_stem_name_val}为喜用神，叠加流年，+15分")
            elif dayun_stem_name_val in jishen_list:
                score -= 15
                factors.append(f"大运天干{dayun_stem_name_val}为忌神，叠加流年，-15分")
            
            # 大运地支与流年地支的冲合
            if BRANCH_CHONGS.get(dayun_branch_idx_val) == branch_idx:
                score -= 20
                factors.append(f"流年{liunian_branch_name}冲大运{dayun_branch_name_val}，动荡不安，-20分")
            elif branch_idx in BRANCH_HES.get(dayun_branch_idx_val, {}):
                score += 20
                factors.append(f"流年{liunian_branch_name}合大运{dayun_branch_name_val}，诸事顺遂，+20分")
            
            # 获取大运对流年的影响分
            dayun_impact = get_liunian_score(stem_idx, branch_idx, dayun_stem_idx_val, dayun_branch_idx_val)
            score += dayun_impact * 5  # 放大倍数（原有分值范围[-2,2]）
    
    # 4. 流年地支与日支的冲合
    if BRANCH_CHONGS.get(branch_idx) == day_branch_idx:
        score -= 15
        factors.append(f"流年{liunian_branch_name}冲日支{day_branch_name}，自身动荡，-15分")
    elif branch_idx in BRANCH_HES.get(day_branch_idx, {}):
        score += 15
        factors.append(f"流年{liunian_branch_name}合日支{day_branch_name}，人缘相助，+15分")
    
    # 5. 流年十神专项判断
    shishen_score, shishen_factor = _get_shishen_liunian_score(liunian_shishen, day_elem, is_strong)
    score += shishen_score
    if shishen_factor:
        factors.append(shishen_factor)
    
    # 6. 流年地支五行专项
    branch_elem_diff = (liunian_branch_elem - day_elem) % 5
    if branch_elem_diff == 1:  # 地支生日主
        if not is_strong:
            score += 5
            factors.append(f"流年地支{ELEMENT_NAMES[liunian_branch_elem]}气助日主，+5分")
    elif branch_elem_diff in [2, 3]:  # 地支克泄日主
        if is_strong:
            score += 5
            factors.append(f"流年地支{ELEMENT_NAMES[liunian_branch_elem]}气利身旺，+5分")
    
    # 限制在 -100 到 100 之间
    score = max(-100, min(100, score))
    
    # 判断吉凶
    if score > 60:
        luck = "大吉"
    elif score >= 40:
        luck = "小吉"
    elif score >= 20:
        luck = "平"
    elif score >= 0:
        luck = "小凶"
    else:
        luck = "大凶"
    
    # 生成简要分析文字
    analysis_text = generate_liunian_text(
        {"shishen": liunian_shishen, "score": score, "luck": luck,
         "stem": liunian_stem_name, "branch": liunian_branch_name,
         "xiyong_in_stem": liunian_stem_name in xiyong_list,
         "jishen_in_stem": liunian_stem_name in jishen_list},
        xiyong,
        rizhu
    )
    
    return {
        "year": year,
        "stem": liunian_stem_name,
        "branch": liunian_branch_name,
        "ganzhi": liunian_stem_name + liunian_branch_name,
        "element": ELEMENT_NAMES[liunian_elem],
        "shishen": liunian_shishen,
        "score": score,
        "luck": luck,
        "factors": factors,
        "analysis": analysis_text,
        "dayun_impact": dayun_impact,
        "dayun_ganzhi": (HEAVENLY_STEMS[dayun_info.get("stem_idx")] + EARTHLY_BRANCHES[dayun_info.get("branch_idx")]) if dayun_info and dayun_info.get("stem_idx") is not None else None,
    }


def _get_shishen_liunian_score(shishen: str, day_elem: int, is_strong: bool) -> Tuple[int, str]:
    """
    根据流年十神返回专项评分和说明
    
    Returns:
        (score_adjustment, factor_text)
    """
    factor = ""
    
    if shishen == "正官":
        if day_elem in [0, 1]:  # 木火日主
            factor = "正官流年，有官运之象"
            return (5, factor)
        else:
            factor = "正官流年，运势平稳"
            return (0, factor)
    elif shishen == "七杀":
        if not is_strong:
            factor = "七杀流年，压力与挑战并存"
            return (-5, factor)
        else:
            factor = "七杀流年，身旺可担"
            return (5, factor)
    elif shishen == "正印":
        factor = "正印流年，利于学业名声"
        return (5, factor)
    elif shishen == "偏印":
        factor = "偏印流年，需防小人是非"
        return (-3, factor)
    elif shishen == "食神":
        factor = "食神流年，创造力发挥，财运渐入"
        return (5, factor)
    elif shishen == "伤官":
        if day_elem in [0, 1]:  # 木火日主
            factor = "伤官流年，才华显露但需注意表达"
            return (-3, factor)
        else:
            factor = "伤官流年，财运有变化"
            return (0, factor)
    elif shishen == "正财":
        factor = "正财流年，财运稳定，积累为宜"
        return (5, factor)
    elif shishen == "偏财":
        factor = "偏财流年，财运起伏，投资需谨慎"
        return (0, factor)
    elif shishen == "比肩":
        if is_strong:
            factor = "比肩流年，竞争较多"
            return (-3, factor)
        else:
            factor = "比肩流年，朋友相助"
            return (3, factor)
    elif shishen == "劫财":
        factor = "劫财流年，财运有损，防小人破财"
        return (-5, factor)
    
    return (0, "")


def generate_liunian_text(
    liunian_info: Dict[str, Any],
    xiyongshen: Dict[str, Any],
    pattern_info: Dict[str, Any]
) -> str:
    """
    根据流年信息生成简要分析文字（2-3句）
    
    Args:
        liunian_info: 流年分析结果（包含 shishen, score, luck, stem, branch, xiyong_in_stem, jishen_in_stem）
        xiyongshen: 喜用神信息
        pattern_info: 格局信息（来自 rizhu_strength）
    
    Returns:
        2-3句流年分析文字
    """
    score = liunian_info.get("score", 0)
    luck = liunian_info.get("luck", "平")
    shishen = liunian_info.get("shishen", "")
    stem = liunian_info.get("stem", "")
    branch = liunian_info.get("branch", "")
    xiyong_in = liunian_info.get("xiyong_in_stem", False)
    jishen_in = liunian_info.get("jishen_in_stem", False)
    
    xiyong_list = xiyongshen.get("xiyongshen", []) if xiyongshen else []
    jishen_list = xiyongshen.get("jishen", []) if xiyongshen else []
    
    sentences = []
    
    # 第一句：年份干支 + 十神
    if shishen:
        sentences.append(f"{stem}{branch}年，流年十神为{shishen}。")
    else:
        sentences.append(f"{stem}{branch}年。")
    
    # 第二句：吉凶判断
    if score > 60:
        sentences.append(f"此年{luck}，运势旺盛，宜把握机遇，积极进取。")
    elif score >= 40:
        sentences.append(f"此年{luck}，运势平稳，若能顺势而为，当有所成。")
    elif score >= 20:
        sentences.append(f"此年运势平平，宜守成蓄势，不宜冒进。")
    elif score >= 0:
        sentences.append(f"此年{luck}，运势略显低迷，宜谨慎行事，韬光养晦。")
    else:
        sentences.append(f"此年{luck}，运势低迷，宜静不宜动，蓄势待发。")
    
    # 第三句：喜忌神补充说明
    if xiyong_in:
        xy_names = ",".join(xiyong_list) if xiyong_list else stem
        sentences.append(f"流年天干为喜用神，多有助力；{xy_names}为用神所在之年，宜把握。")
    elif jishen_in:
        ji_names = ",".join(jishen_list) if jishen_list else stem
        sentences.append(f"流年天干为忌神，需防阻滞；{ji_names}为忌神所在之年，宜谨慎。")
    else:
        # 补充十神方向的提示
        if shishen in ["正财", "偏财"]:
            sentences.append("财星流年，财运为重，宜关注财务收支。")
        elif shishen in ["正官", "七杀"]:
            sentences.append("官杀流年，事业为重，宜积极进取但防小人。")
        elif shishen in ["食神", "伤官"]:
            sentences.append("食伤流年，才华为用，宜发挥特长、展示自我。")
        elif shishen in ["正印", "偏印"]:
            sentences.append("印星流年，学业名声为重，宜学习积累。")
    
    return "".join(sentences)


def get_recent_liunian(
    bazi_info: Dict[str, Any],
    dayun_list: List[Dict[str, Any]],
    current_year: int = None,
    count: int = 5,
    birth_year: int = None
) -> List[Dict[str, Any]]:
    """
    获取近N年流年简析

    Args:
        bazi_info: 八字信息
        dayun_list: 大运列表
        current_year: 当前年份（默认2026）
        count: 返回数量
        birth_year: 出生年份（用于过滤，只显示出生后的流年）

    Returns:
        流年分析列表
    """
    if current_year is None:
        current_year = 2026
    if birth_year is None:
        # 从 bazi_info 尝试获取（支持 {"lunar":{}} 或 {"bazi":{"year":{}} } 两种格式）
        lunar = bazi_info.get("lunar", {})
        if not lunar:
            # 尝试从 bazi 内部获取农历信息
            bazi = bazi_info.get("bazi", {})
            lunar = bazi.get("lunar", {}) if isinstance(bazi, dict) else {}
        birth_year = lunar.get("year", None) if lunar else None

    # 确定当前所在大运
    current_dayun = None
    if dayun_list:
        current_dayun = dayun_list[0]  # 默认第一步大运

    results = []
    for year in range(current_year - count + 1, current_year + 1):
        if birth_year is not None and year < birth_year:
            continue  # 跳过出生年前的流年
        analysis = analyze_liunian_by_year(year, bazi_info, current_dayun)
        analysis["year"] = year
        results.append(analysis)

    return results


# ============================================================
# 5. 完整大运流年分析
# ============================================================

def full_dayun_analysis(
    bazi_info: Dict[str, Any],
    gender: str,
    birth_timestamp: float,
    birth_year: int,
    birth_month: int
) -> Dict[str, Any]:
    """
    完整大运流年分析
    
    Args:
        bazi_info: 八字信息（包含 bazi dict 和 xiyongshen 等）
        gender: 性别
        birth_timestamp: 出生时间戳
        birth_year: 出生年份
        birth_month: 出生月份
    
    Returns:
        完整分析结果
    """
    # 获取大运序列
    dayun_list = get_dayun_sequence(bazi_info, gender, birth_timestamp)
    
    # 计算精确大运起始年龄
    birth_dt = datetime.fromtimestamp(birth_timestamp)
    dayun_start_exact = get_dayun_start_age_exact(birth_dt.year, birth_dt.month, birth_dt.day)
    
    # 分析每步大运
    dayun_summaries = []
    for dayun in dayun_list:
        summary = get_dayun_summary(dayun, bazi_info)
        dayun_summaries.append({
            "index": dayun["index"],
            "start_age": dayun["start_age"],
            "end_age": dayun["end_age"],
            "ganzhi": dayun["ganzhi"],
            "direction": dayun["direction"],
            "summary": summary,
        })
    
    # 获取近5年流年
    current_year = 2026
    recent_liunian = get_recent_liunian(bazi_info, dayun_list, current_year, 5)
    
    # 驿马运
    bazi = bazi_info.get("bazi", bazi_info)
    yima = get_yima_dayun(bazi["year"]["stem_idx"], bazi["year"]["branch_idx"], gender)
    
    return {
        "gender": gender,
        "direction_rule": "阳男阴女顺行，阴男阳女逆行",
        "year_stem": HEAVENLY_STEMS[bazi["year"]["stem_idx"]],
        "month_branch": EARTHLY_BRANCHES[bazi["month"]["branch_idx"]],
        "dayun_count": len(dayun_list),
        "dayun_list": dayun_summaries,
        "dayun_start_exact": dayun_start_exact,  # 精确起始年龄: {years, months, days, decimal_years, next_jieqi, ...}
        "yima": yima,
        "recent_liunian": [
            {
                "year": r["year"],
                "ganzhi": r["ganzhi"],
                "shishen": r["shishen"],
                "luck": r["luck"],
                "score": r["score"],
                "analysis": r["analysis"],
            }
            for r in recent_liunian
        ],
    }


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=== 大运流年推算测试 ===\n")
    
    # 导入八字引擎
    from bazi_engine import full_bazi_analysis, get_bazi, determine_xiyongshen, get_rizhu_strength
    
    # 测试1: 2024年3月15日10点出生 男
    print("【测试1】2024年3月15日10点 男")
    birth_year, birth_month, birth_day, birth_hour = 2024, 3, 15, 10
    bazi_result = full_bazi_analysis(birth_year, birth_month, birth_day, birth_hour)
    bazi = bazi_result["bazi"]
    rizhu = bazi_result["rizhu_strength"]
    xiyong = bazi_result["xiyongshen"]
    
    bazi_with_xiyong = {
        "bazi": bazi,
        "rizhu_strength": rizhu,
        "xiyongshen": xiyong,
    }
    
    import time
    birth_ts = time.mktime((birth_year, birth_month, birth_day, birth_hour, 0, 0, 0, 0, 0))
    
    dayun_list = get_dayun_sequence(bazi_with_xiyong, "男", birth_ts)
    print(f"  八字: {bazi_result['birth_chart']}")
    print(f"  性别: 男, 喜用神: {xiyong['xiyongshen']}")
    print(f"  大运方向: {dayun_list[0]['direction']}")
    print(f"  前3步大运:")
    for du in dayun_list[:3]:
        print(f"    {du['start_age']}-{du['end_age']}岁: {du['ganzhi']}")
    print()
    
    # 测试2: 流年分析
    print("【测试2】2026年流年分析")
    liunian_2026 = analyze_liunian_by_year(2026, bazi_with_xiyong, dayun_list[0])
    print(f"  2026年: {liunian_2026['ganzhi']} ({liunian_2026['shishen']})")
    print(f"  吉凶: {liunian_2026['luck']} (得分: {liunian_2026['score']})")
    print(f"  分析: {liunian_2026['analysis']}")
    print()
    
    # 测试3: 近5年流年
    print("【测试3】近5年流年")
    recent = get_recent_liunian(bazi_with_xiyong, dayun_list, 2026, 5)
    for r in recent:
        print(f"  {r['year']}年 {r['ganzhi']} ({r['shishen']}): {r['luck']} - {r['analysis']}")
    print()
    
    # 测试4: 完整大运分析
    print("【测试4】完整大运分析")
    full_result = full_dayun_analysis(bazi_with_xiyong, "男", birth_ts, birth_year, birth_month)
    print(f"  大运数量: {full_result['dayun_count']}")
    print(f"  驿马运: {full_result['yima']}")
    print()
    
    # 测试5: 驿马运
    print("【测试5】驿马运查询")
    bazi2_result = get_bazi(1990, 5, 15, 10)  # 庚午年
    bazi2 = bazi2_result["bazi"]  # extract inner bazi dict
    rizhu2 = get_rizhu_strength(bazi2)
    xiyong2 = determine_xiyongshen(bazi2, rizhu2)
    bazi2_full = {"bazi": bazi2, "rizhu_strength": rizhu2, "xiyongshen": xiyong2}
    birth_ts2 = time.mktime((1990, 5, 15, 10, 0, 0, 0, 0, 0))
    yima_result = get_yima_dayun(bazi2["year"]["stem_idx"], bazi2["year"]["branch_idx"], "男")
    print(f"  庚午年 男: 驿马在寅")
    print(f"  驿马运结果: {yima_result}")
    print()
    
    # 测试6: 阴男逆行验证
    print("【测试6】阴男逆行 - 辛金日主（阴干）男命")
    bazi3_result = get_bazi(1991, 8, 20, 15)  # 辛未年
    bazi3 = bazi3_result["bazi"]  # extract inner bazi dict
    rizhu3 = get_rizhu_strength(bazi3)
    xiyong3 = determine_xiyongshen(bazi3, rizhu3)
    bazi3_full = {"bazi": bazi3, "rizhu_strength": rizhu3, "xiyongshen": xiyong3}
    birth_ts3 = time.mktime((1991, 8, 20, 15, 0, 0, 0, 0, 0))
    dayun3 = get_dayun_sequence(bazi3_full, "男", birth_ts3)
    print(f"  年干: 辛（阴干）")
    print(f"  性别: 男")
    print(f"  大运方向: {dayun3[0]['direction']}")
    print(f"  期望: 逆行（阴男逆）")
    print(f"  验证: {'✓' if not dayun3[0]['shun'] else '✗'}")
    print()
    
    print("=== 测试完成 ===")
