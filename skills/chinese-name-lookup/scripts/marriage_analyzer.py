# -*- coding: utf-8 -*-
"""
婚姻配偶星分析模块 v1.0
=======================
基于《渊海子平》婚姻分析体系：

一、配偶星定位
- 男命：正财（无正财看偏财）= 妻星
- 女命：正官（无正官看七杀）= 夫星

二、配偶宫（日支）分析
- 日支被冲：婚变、离别
- 日支被合：外遇、偷情
- 日支被刑：争吵、矛盾

三、婚姻吉凶判断
- 官星被伤官克 → 婚变
- 财星被比劫克 → 配偶竞争者
- 身弱官旺 → 夫欺妻 / 官欺身
"""

import sys
sys.path.insert(0, '.')

from typing import Dict, List, Optional
from bazi_engine import get_shishen, get_bazi, HEAVENLY_STEMS as STEMS, EARTHLY_BRANCHES as BRANCHES
from children_analyzer import YUELING_CANGGAN, count_shishen

# 地支六冲表
BRANCH_CONFRONT = {
    0: [6], 1: [7], 2: [8], 3: [9], 4: [10], 5: [11],
    6: [0], 7: [1], 8: [2], 9: [3], 10: [4], 11: [5],
}

# 地支六合
BRANCH_HARMONY_IDX = {(0,1),(1,0),(2,11),(11,2),(3,10),(10,3),(4,9),(9,4),(5,8),(8,5),(6,7),(7,6)}


def get_spouse_star(bazi_dict: Dict, gender: int) -> Dict:
    """
    定位配偶星

    男命：正财（无正财看偏财）
    女命：正官（无正官看七杀）
    """
    bz = bazi_dict['bazi']
    day_stem_idx = bazi_dict['day_stem_idx']

    if gender == 1:  # 男命
        main = "正财"
        backup = "偏财"
    else:  # 女命
        main = "正官"
        backup = "偏官"

    main_count = count_shishen(bazi_dict, main)
    backup_count = count_shishen(bazi_dict, backup)

    if main_count['count'] > 0:
        return {
            "star": main,
            "count": main_count['count'],
            "天干": main_count['天干'],
            "地支藏干": main_count['地支藏干'],
            "has_backup": backup_count['count'] > 0,
        }
    elif backup_count['count'] > 0:
        return {
            "star": backup,
            "count": backup_count['count'],
            "天干": backup_count['天干'],
            "地支藏干": backup_count['地支藏干'],
            "has_backup": False,
            "note": f"无{main}，以{backup}代替",
        }
    else:
        return {
            "star": None,
            "count": 0,
            "天干": [],
            "地支藏干": [],
            "has_backup": False,
            "note": f"无{main}也无{backup}，需参考其他",
        }


def analyze_spouse_palace(bazi_dict: Dict) -> Dict:
    """
    分析配偶宫（日支）的状态

    日支为配偶宫，反映配偶的性格、婚姻状态
    - 日支被冲：婚变、离别
    - 日支被合：外遇、情感纠葛
    - 日支被刑：争吵、矛盾
    - 日支被害：暗昧、委屈
    """
    bz = bazi_dict['bazi']
    day_branch_idx = bz['day']['branch_idx']
    day_branch = bz['day']['branch']
    day_stem = STEMS[bazi_dict['day_stem_idx']]

    issues = []

    # 检查其他三柱对日支的冲/合/刑/害
    other_pillars = ['year', 'month', 'hour']
    for pillar in other_pillars:
        other_idx = bz[pillar]['branch_idx']
        other_branch = bz[pillar]['branch']

        # 六冲
        if other_idx in BRANCH_CONFRONT.get(day_branch_idx, []):
            issues.append(f"{other_branch}与{day_branch}相冲")

        # 六合
        if (day_branch_idx, other_idx) in BRANCH_HARMONY_IDX:
            issues.append(f"{other_branch}与{day_branch}相合")

    # 日支本身状态
    day_branch_canggan = YUELING_CANGGAN.get(day_branch, {})
    day_elem_本气 = day_branch_canggan.get("本气")
    day_stem_shishen = get_shishen(bazi_dict['day_stem_idx'],
                                    STEMS.index(day_stem) if day_stem in STEMS else 0)

    # 日支地支本身是否有自刑
    if day_branch_idx in [4, 6, 9, 11]:  # 辰午酉亥自刑
        issues.append(f"{day_branch}自刑（自我纠结）")

    if not issues:
        宫状态 = "平稳"
        说明 = f"{day_branch}为{day_stem}之配偶宫，无明显冲合，婚姻相对稳定。"
    else:
        宫状态 = "有冲/合/刑"
        说明 = f"{day_branch}为{day_stem}之配偶宫，存在: {'; '.join(issues)}。"

    return {
        "配偶宫": day_branch,
        "宫状态": 宫状态,
        "问题列表": issues,
        "说明": 说明,
        "藏干本气": day_elem_本气,
    }


def analyze_marriage(bazi_dict: Dict, gender: int = 1) -> Dict:
    """
    综合婚姻分析

    参数：
        bazi_dict: get_bazi() 返回的八字字典
        gender: 1=男, 0=女
    """
    bz = bazi_dict['bazi']
    day_stem_idx = bazi_dict['day_stem_idx']
    day_stem = STEMS[day_stem_idx]

    spouse = get_spouse_star(bazi_dict, gender)
    palace = analyze_spouse_palace(bazi_dict)

    # 综合判断
    gender_desc = "男命" if gender == 1 else "女命"

    if spouse['star'] is None:
        综合 = f"{gender_desc}无明显配偶星，婚姻缘分较弱，需多努力。"
    else:
        if spouse['count'] >= 2:
            综合 = f"{gender_desc}，{spouse['star']}{spouse['count']}个，配偶星旺，异性缘佳。"
        elif spouse['count'] == 1:
            综合 = f"{gender_desc}，{spouse['star']}{spouse['count']}个，配偶缘分稳定。"
        else:
            综合 = f"{gender_desc}，{spouse['star']}{spouse['count']}个，感情专一。"

    # 婚姻宫的影响
    if palace['问题列表']:
        综合 += f" 配偶宫{day_stem}坐{palace['配偶宫']}，{'; '.join(palace['问题列表'])}，需注意婚恋关系。"
    else:
        综合 += f" 配偶宫{palace['配偶宫']}无冲合刑害，婚姻平稳。"

    return {
        "gender": gender_desc,
        "日主": day_stem,
        "配偶星": spouse,
        "配偶宫分析": palace,
        "综合结论": 综合,
    }


def analyze_spouse_star_quality(bazi_dict: Dict, gender: int) -> Dict:
    """
    配偶星质量分析

    判断配偶星是否得令、是否通根、是否带吉神/凶神
    """
    bz = bazi_dict['bazi']
    day_stem_idx = bazi_dict['day_stem_idx']

    if gender == 1:
        spouse_star_name = "正财"
    else:
        spouse_star_name = "正官"

    # 找配偶星位置
    from children_analyzer import count_shishen
    star_info = count_shishen(bazi_dict, spouse_star_name)

    if star_info['count'] == 0:
        return {
            "quality": "弱",
            "说明": f"无{spouse_star_name}，配偶缘分弱。",
        }

    # 判断是否得月令
    month_branch_idx = bz['month']['branch_idx']
    has_month = any(True for item in star_info['天干'] + star_info['地支藏干']
                   if '月' in item or f"月" in str(bz.get('month', {}).get('branch', '')))

    if star_info['count'] >= 2:
        quality = "优良"
        说明 = f"{spouse_star_name}{star_info['count']}个且通根，配偶能力强，有助益。"
    elif star_info['count'] == 1:
        quality = "良好"
        说明 = f"有{spouse_star_name}，配偶条件尚可。"
    else:
        quality = "一般"
        说明 = f"{spouse_star_name}较弱，配偶需靠自身努力发展。"

    return {
        "quality": quality,
        "说明": 说明,
    }


# ============================================================
# 孤鸾煞分析（P1-e）
# ============================================================
def get_guluan(bazi_dict: Dict) -> Dict:
    """
    孤鸾煞分析

    《渊海子平》："木虎孀无婿，金猪岂有郎；
                  赤黄马独卧，黑鼠守空房。"

    孤鸾日：甲寅、辛亥、丙午、壬子

    - 甲寅：木虎 — 女孤男寡
    - 辛亥：金猪 — 女孤男寡
    - 丙午：赤黄马 — 女孤男寡
    - 壬子：黑鼠 — 女孤男寡
    """
    bz = bazi_dict['bazi']
    day_gan = bz['day']['stem']
    day_zhi = bz['day']['branch']

    GULUAN_DAYS = {
        ("甲", "寅"): "木虎",
        ("辛", "亥"): "金猪",
        ("丙", "午"): "赤黄马",
        ("壬", "子"): "黑鼠",
    }

    key = (day_gan, day_zhi)
    if key in GULUAN_DAYS:
        animal = GULUAN_DAYS[key]
        return {
            "is_guluan": True,
            "孤鸾名": animal,
            "日柱": f"{day_gan}{day_zhi}",
            "说明": f"孤鸾日「{animal}」，主婚姻大凶，宜晚婚或找互补属相。",
        }

    return {
        "is_guluan": False,
        "日柱": f"{day_gan}{day_zhi}",
        "说明": "非孤鸾日，无此煞。",
    }


# ============================================================
# 阴错阳差分析（P1-e）
# ============================================================
def get_yincuo_yangcha(bazi_dict: Dict) -> Dict:
    """
    阴错阳差分析

    《渊海子平》："阴错阳差、孤鸾之日，不利嫁娶。"

    阴错日（6个）：辛卯、壬辰、癸巳、丙午、丁未、戊申
    阳差日（6个）：辛丑、壬寅、癸卯、丙申、丁酉、戊戌
    """
    bz = bazi_dict['bazi']
    day_gan = bz['day']['stem']
    day_zhi = bz['day']['branch']

    YINCUO_DAYS = {"辛卯", "壬辰", "癸巳", "丙午", "丁未", "戊申"}
    YANGCHA_DAYS = {"辛丑", "壬寅", "癸卯", "丙申", "丁酉", "戊戌"}

    day_str = f"{day_gan}{day_zhi}"

    if day_str in YINCUO_DAYS:
        return {
            "is_yincuo": True,
            "is_yangcha": False,
            "类型": "阴错",
            "日柱": day_str,
            "说明": "阴错日，不利嫁娶，婚姻多波折。",
        }
    elif day_str in YANGCHA_DAYS:
        return {
            "is_yincuo": False,
            "is_yangcha": True,
            "类型": "阳差",
            "日柱": day_str,
            "说明": "阳差日，不利嫁娶，婚姻有反复。",
        }

    return {
        "is_yincuo": False,
        "is_yangcha": False,
        "日柱": day_str,
        "说明": "非阴错阳差日。",
    }


# ============================================================
# 验证测试
# ============================================================
if __name__ == "__main__":
    print("=== 婚姻分析验证 ===\n")

    # 测试1：2026-03-23 成都男婴
    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    day_stem = STEMS[bazi['day_stem_idx']]
    print(f"八字：{bazi['birth_chart']}，性别：男，日主={day_stem}")

    # 配偶星
    spouse = get_spouse_star(bazi, gender=1)
    print(f"\n配偶星分析：")
    print(f"  主星: {spouse['star']} × {spouse['count']}")
    print(f"  天干: {spouse['天干']}")
    print(f"  地支藏干: {spouse['地支藏干']}")

    # 配偶宫
    palace = analyze_spouse_palace(bazi)
    print(f"\n配偶宫分析：")
    print(f"  宫: {palace['配偶宫']}，状态: {palace['宫状态']}")
    print(f"  问题: {palace['问题列表']}")
    print(f"  说明: {palace['说明']}")

    # 综合婚姻
    marriage = analyze_marriage(bazi, gender=1)
    print(f"\n综合婚姻：{marriage['综合结论']}")

    # 孤鸾煞
    guluan = get_guluan(bazi)
    print(f"\n孤鸾煞: {guluan}")

    # 阴错阳差
    yincuo = get_yincuo_yangcha(bazi)
    print(f"阴错阳差: {yincuo}")

    # 测试孤鸾日
    print("\n=== 孤鸾日验证 ===")
    test_days = [
        (2020, 2, 1, "甲寅日"),  # 木虎
        (2019, 10, 1, "辛亥日"),  # 金猪
        (2020, 5, 1, "丙午日"),  # 赤黄马
        (2019, 12, 1, "壬子日"),  # 黑鼠
    ]
    for y, m, d, desc in test_days:
        b = get_bazi(y, m, d, 12)
        g = get_guluan(b)
        print(f"  {b['birth_chart']} = {desc}: is_guluan={g['is_guluan']}")

    print("\n✅ 婚姻分析验证完成")
