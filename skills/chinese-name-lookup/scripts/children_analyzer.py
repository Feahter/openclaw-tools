# -*- coding: utf-8 -*-
"""
子息分析模块 v1.0
=================
基于《渊海子平》子息判断体系：

一、子息数量规则
1. "八字有一杀一子，二杀二子，无杀无子"（七杀个数 → 儿子数）
2. 时支十二长生 → 子女数量映射

二、子女质量判断
- 子女星带吉神 → 子女有出息
- 子女星带凶神 → 子女贫贱/孤苦

三、男命子女星：七杀（偏官）；女命：食神（女）/ 伤官（子）
"""

import sys
sys.path.insert(0, '.')

from typing import Dict, List
from bazi_engine import get_shishen, get_bazi
from bazi_engine import STEM_ELEMENTS, HEAVENLY_STEMS as STEMS, EARTHLY_BRANCHES as BRANCHES


# ============================================================
# 十二长生 → 子女数映射（渊海子平原文）
# ============================================================
# 原文："长生=7子, 沐浴=2子, 冠带=3子, 临官=3子, 帝旺=5子,
#        衰=2子, 病=1子, 死=0子(没儿郎), 墓=难保双, 绝=1子, 胎=头女, 养=3子留2"
SHENG_WANG_CHILDREN_MAP = {
    "长生": {"儿子数": "7", "说明": "旬中半合，主七子"},
    "沐浴": {"儿子数": "2", "说明": "一双，保养吉康"},
    "冠带": {"儿子数": "3", "说明": "三子位，活泼可爱"},
    "临官": {"儿子数": "3", "说明": "三子位，成家立业"},
    "帝旺": {"儿子数": "5", "说明": "五子，自成行"},
    "衰": {"儿子数": "2", "说明": "二子，中等"},
    "病": {"儿子数": "1", "说明": "一子，需注意健康"},
    "死": {"儿子数": "0", "说明": "没儿郎（或独子难养）"},
    "墓": {"儿子数": "难定", "说明": "难保双，子女缘分浅"},
    "绝": {"儿子数": "1", "说明": "绝处逢生，子女缘薄"},
    "胎": {"儿子数": "头女", "说明": "头胎生女居多"},
    "养": {"儿子数": "3(留2)", "说明": "三子只留二"},
}

# 地支藏干表（来自 yueling_canggan.py）
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

# 十二长生表（天干在各地支的状态）
SHENG_WANG_12 = {
    "甲": {0:"帝旺",1:"衰",2:"病",3:"死",4:"墓",5:"绝",6:"胎",7:"养",8:"长生",9:"沐浴",10:"冠带",11:"临官"},
    "乙": {0:"临官",1:"帝旺",2:"衰",3:"病",4:"死",5:"墓",6:"绝",7:"胎",8:"养",9:"长生",10:"沐浴",11:"冠带"},
    "丙": {0:"帝旺",1:"衰",2:"病",3:"死",4:"墓",5:"绝",6:"胎",7:"养",8:"长生",9:"沐浴",10:"冠带",11:"临官"},
    "丁": {0:"临官",1:"帝旺",2:"衰",3:"病",4:"死",5:"墓",6:"绝",7:"胎",8:"养",9:"长生",10:"沐浴",11:"冠带"},
    "戊": {0:"帝旺",1:"衰",2:"病",3:"死",4:"墓",5:"绝",6:"胎",7:"养",8:"长生",9:"沐浴",10:"冠带",11:"临官"},
    "己": {0:"临官",1:"帝旺",2:"衰",3:"病",4:"死",5:"墓",6:"绝",7:"胎",8:"养",9:"长生",10:"沐浴",11:"冠带"},
    "庚": {0:"帝旺",1:"衰",2:"病",3:"死",4:"墓",5:"绝",6:"胎",7:"养",8:"长生",9:"沐浴",10:"冠带",11:"临官"},
    "辛": {0:"临官",1:"帝旺",2:"衰",3:"病",4:"死",5:"墓",6:"绝",7:"胎",8:"养",9:"长生",10:"沐浴",11:"冠带"},
    "壬": {0:"帝旺",1:"衰",2:"病",3:"死",4:"墓",5:"绝",6:"胎",7:"养",8:"长生",9:"沐浴",10:"冠带",11:"临官"},
    "癸": {0:"临官",1:"帝旺",2:"衰",3:"病",4:"死",5:"墓",6:"绝",7:"胎",8:"养",9:"长生",10:"沐浴",11:"冠带"},
}


def count_qisha(bazi_dict: Dict) -> Dict:
    """
    统计八字中七杀（偏官）的个数

    《渊海子平》："八字有一杀一子，二杀二子，无杀无子。"

    七杀 = 偏官（七杀 only counts as the 克我阳干）
    - 天干七杀：直接在天干四柱中查找偏官
    - 地支七杀：地支藏干中的本气/中气/余气为偏官
    """
    bz = bazi_dict['bazi']
    day_stem_idx = bazi_dict['day_stem_idx']
    day_stem = STEMS[day_stem_idx]

    tian_gan_qisha = []
    zi_zhi_qisha = []

    # 天干七杀
    for pillar in ['year', 'month', 'day', 'hour']:
        stem_idx = bz[pillar]['stem_idx']
        shishen = get_shishen(day_stem_idx, stem_idx)
        if shishen == "偏官":
            tian_gan_qisha.append(f"{bz[pillar]['stem']}{bz[pillar]['branch']}偏官")

    # 地支藏干七杀
    for pillar in ['year', 'month', 'day', 'hour']:
        branch = bz[pillar]['branch']
        canggan = YUELING_CANGGAN.get(branch, {})
        for pos in ['本气', '中气', '余气']:
            gan = canggan.get(pos)
            if gan:
                gan_idx = STEMS.index(gan) if gan in STEMS else None
                if gan_idx is not None:
                    # 注意：藏干的天干索引用STEMS.index
                    other_idx = STEMS.index(gan) if gan in STEMS else None
                    if other_idx is not None:
                        shishen = get_shishen(day_stem_idx, other_idx)
                        if shishen == "偏官":
                            zi_zhi_qisha.append(f"{branch}{pos}{gan}{shishen}")

    total_count = len(tian_gan_qisha) + len(zi_zhi_qisha)

    # 渊海子平口诀
    if total_count == 0:
        儿子数 = "0（无杀无子）"
        说明 = "八字无七杀，按口诀'无杀无子'，子女缘分较弱。"
    elif total_count == 1:
        儿子数 = "1（一杀一子）"
        说明 = "有一七杀，按口诀'一杀一子'，主有一子。"
    else:
        儿子数 = f"{total_count}（{total_count}杀{total_count}子）"
        说明 = f"有{total_count}个七杀，按口诀'{total_count}杀{total_count}子'。"

    return {
        "count": total_count,
        "天干七杀": tian_gan_qisha,
        "地支藏干七杀": zi_zhi_qisha,
        "儿子数": 儿子数,
        "说明": 说明,
        "口诀来源": "渊海子平·论子息",
    }


def count_shishen(bazi_dict: Dict, target_shishen: str) -> Dict:
    """
    统计八字中指定十神的个数（通用版本）

    参数：target_shishen = "偏官"/"食神"/"伤官" 等
    """
    bz = bazi_dict['bazi']
    day_stem_idx = bazi_dict['day_stem_idx']

    tian_gan = []
    zi_zhi = []

    # 天干
    for pillar in ['year', 'month', 'day', 'hour']:
        stem_idx = bz[pillar]['stem_idx']
        shishen = get_shishen(day_stem_idx, stem_idx)
        if shishen == target_shishen:
            tian_gan.append(f"{bz[pillar]['stem']}{bz[pillar]['branch']}{target_shishen}")

    # 地支藏干
    for pillar in ['year', 'month', 'day', 'hour']:
        branch = bz[pillar]['branch']
        canggan = YUELING_CANGGAN.get(branch, {})
        for pos in ['本气', '中气', '余气']:
            gan = canggan.get(pos)
            if gan and gan in STEMS:
                other_idx = STEMS.index(gan)
                shishen = get_shishen(day_stem_idx, other_idx)
                if shishen == target_shishen:
                    zi_zhi.append(f"{branch}{pos}{gan}{target_shishen}")

    total_count = len(tian_gan) + len(zi_zhi)

    return {
        "count": total_count,
        "天干": tian_gan,
        "地支藏干": zi_zhi,
    }


def get_hour_branch_shengwang(bazi_dict: Dict) -> Dict:
    """
    获取时支的十二长生状态及子女数映射
    """
    bz = bazi_dict['bazi']
    hour_branch = bz['hour']['branch']
    hour_branch_idx = bz['hour']['branch_idx']
    day_stem = STEMS[bazi_dict['day_stem_idx']]

    shengwang = SHENG_WANG_12[day_stem][hour_branch_idx]
    children_info = SHENG_WANG_CHILDREN_MAP.get(shengwang, {"儿子数": "难定", "说明": "无法判断"})

    return {
        "时支": hour_branch,
        "时支索引": hour_branch_idx,
        "日干": day_stem,
        "长生状态": shengwang,
        "子女数": children_info["儿子数"],
        "说明": children_info["说明"],
    }


def analyze_children_quality(bazi_dict: Dict, gender: int = 1) -> Dict:
    """
    分析子女质量

    男命：七杀=儿子，食神=女儿
    女命：食神=女儿，伤官=儿子

    渊海子平："杀临长生月德天德，所临之地，贵人、禄马、食神、财乡，言有强父贵子。"
    """
    bz = bazi_dict['bazi']

    if gender == 1:
        son_shishen = "偏官"  # 男命七杀=儿子
        daughter_shishen = "食神"  # 男命食神=女儿
    else:
        son_shishen = "伤官"  # 女命伤官=儿子
        daughter_shishen = "食神"  # 女命食神=女儿

    sons = count_shishen(bazi_dict, son_shishen)
    daughters = count_shishen(bazi_dict, daughter_shishen)

    if sons['count'] == 0 and daughters['count'] == 0:
        return {
            "has_children_stars": False,
            "quality": "一般",
            "说明": "无明显子女星，子女缘分需参考其他因素。",
        }

    # 判断七杀是否通根
    sons_has_root = sons['count'] > 0

    # 质量判断
    if sons['count'] >= 2 and sons_has_root:
        quality = "优良"
        说明 = f"{son_shishen}{sons['count']}个且通根，子女能力强，有出息。"
    elif sons_has_root:
        quality = "良好"
        说明 = f"有{son_shishen}通根，子女有能力，得父母或祖辈之力。"
    else:
        quality = "一般"
        说明 = f"{son_shishen}数量少或失令，子女需靠自身努力。"

    return {
        "gender": "男命" if gender == 1 else "女命",
        "has_children_stars": True,
        f"{son_shishen}儿子": sons,
        f"{daughter_shishen}女儿": daughters,
        "quality": quality,
        "说明": 说明,
    }


def analyze_children(bazi_dict: Dict, gender: int = 1) -> Dict:
    """
    综合子息分析主函数

    返回：
        - 七杀计数分析（渊海子平口诀）
        - 时支长生分析（子女数量映射）
        - 子女质量分析
        - 综合结论
    """
    qisha_analysis = count_qisha(bazi_dict)
    hour_analysis = get_hour_branch_shengwang(bazi_dict)
    quality = analyze_children_quality(bazi_dict, gender)

    # 综合结论（融合两个体系）
    综合结论 = (
        f"【渊海子平口诀】{qisha_analysis['说明']}；"
        f"【时支长生】时支{hour_analysis['时支']}={hour_analysis['长生状态']}，"
        f"主{str(hour_analysis['子女数'])}。；"
        f"【子女质量】{quality['说明']}"
    )

    return {
        "gender": "男命" if gender == 1 else "女命",
        "七杀计数分析": qisha_analysis,
        "时支长生分析": hour_analysis,
        "子女质量": quality,
        "综合结论": 综合结论,
    }


# ============================================================
# 验证测试
# ============================================================
if __name__ == "__main__":
    print("=== 子息分析验证 ===\n")

    # 测试1：2026-03-23 05:00（成都天府新区）
    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    day_stem = STEMS[bazi['day_stem_idx']]
    print(f"八字：{bazi['birth_chart']}，日干：{day_stem}，性别：男")

    # 打印各柱十神（用引擎函数）
    print("\n各柱天干十神：")
    for pillar in ['year', 'month', 'day', 'hour']:
        s = get_shishen(bazi['day_stem_idx'], bazi['bazi'][pillar]['stem_idx'])
        print(f"  {pillar}: {bazi['bazi'][pillar]['stem']}{bazi['bazi'][pillar]['branch']} → {s}")

    print("\n子息分析结果：")
    result = analyze_children(bazi, gender=1)
    qa = result['七杀计数分析']
    print(f"  天干七杀: {qa['天干七杀']}")
    print(f"  地支藏干七杀: {qa['地支藏干七杀']}")
    print(f"  七杀总数: {qa['count']}")
    print(f"  儿子数: {qa['儿子数']}")
    print(f"  时支: {result['时支长生分析']['时支']}={result['时支长生分析']['长生状态']} → {result['时支长生分析']['子女数']}")
    print(f"  子女质量: {result['子女质量']['quality']}")
    print(f"\n综合结论：{result['综合结论']}")

    # 测试2：经典命例 - 七杀多的命
    print("\n\n=== 测试2: 七杀计数验证 ===")
    # 壬水日，七杀多
    bazi2 = get_bazi(2000, 1, 1, 3)  # 假设2000-01-01 03:00
    print(f"八字：{bazi2['birth_chart']}，日干：{STEMS[bazi2['day_stem_idx']]}")
    for pillar in ['year', 'month', 'day', 'hour']:
        s = get_shishen(bazi2['day_stem_idx'], bazi2['bazi'][pillar]['stem_idx'])
        print(f"  {pillar}: {bazi2['bazi'][pillar]['stem']}{bazi2['bazi'][pillar]['branch']} → {s}")
    qa2 = count_qisha(bazi2)
    print(f"七杀总数: {qa2['count']} → {qa2['儿子数']}")
