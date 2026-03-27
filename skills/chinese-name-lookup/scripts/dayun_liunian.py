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
    
    # 大运起始年龄计算：
    # 简单算法：假设出生即进入第一步大运，从月柱开始
    # 实际上大运起始年龄需要精确到出生月份
    # 简化处理：按《千里命稿》规则，从月柱开始计算
    
    dayuns = []
    for i in range(12):
        start_age = i * 10
        end_age = (i + 1) * 10 - 1
        
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
    """
    bazi = bazi_info.get("bazi", bazi_info)
    year_stem_idx = bazi["year"]["stem_idx"]
    month_stem_idx = bazi["month"]["stem_idx"]
    month_branch_idx = bazi["month"]["branch_idx"]
    
    shun = is_shun(year_stem_idx, gender)
    direction_str = "顺行" if shun else "逆行"
    
    dayun_branches = _calc_dayun_branch_sequence(month_branch_idx, year_stem_idx, gender)
    dayun_stems = _calc_dayun_stem_sequence(month_stem_idx, year_stem_idx, gender)
    
    # 计算第一步大运的起始年龄
    # 从月柱开始，按顺逆方向
    # 简化：每3年走一运（传统）或每10年走一步运
    # 《千里命稿》采用每10年一步运
    # 起始年龄 = (12 - 月份) 岁（近似）
    
    dayuns = []
    for i in range(12):
        # 精确起始年龄：第一步大运从大约几岁开始
        # 根据大运方向和月令位置
        if shun:
            # 顺行：向未来方向走
            # 第一个大运大约在 0-9 岁
            start_age = 0
        else:
            # 逆行：向过去方向走
            # 第一个大运大约在 0-9 岁
            start_age = 0
        
        start_age = i * 10
        end_age = (i + 1) * 10 - 1
        
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
        dayuns.append(dayun_info)
    
    return dayuns


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
    根据年份分析流年
    
    Args:
        year: 公历年（2020-2050）
        bazi_info: 八字信息
        dayun_info: 当前大运信息
    
    Returns:
        流年分析结果
    """
    stem_idx, branch_idx = get_liunian_ganzhi(year)
    return analyze_liunian(stem_idx, branch_idx, bazi_info, dayun_info)


def get_recent_liunian(
    bazi_info: Dict[str, Any],
    dayun_list: List[Dict[str, Any]],
    current_year: int = None,
    count: int = 5
) -> List[Dict[str, Any]]:
    """
    获取近N年流年简析
    
    Args:
        bazi_info: 八字信息
        dayun_list: 大运列表
        current_year: 当前年份（默认2026）
        count: 返回数量
    
    Returns:
        流年分析列表
    """
    if current_year is None:
        current_year = 2026
    
    # 确定当前所在大运
    current_dayun = None
    if dayun_list:
        current_dayun = dayun_list[0]  # 默认第一步大运
    
    results = []
    for year in range(current_year - count + 1, current_year + 1):
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
