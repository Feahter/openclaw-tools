# -*- coding: utf-8 -*-
"""
神煞质量评估模块 v1.0
=====================
基于《渊海子平》神煞激活原则：

神煞需要满足以下条件才有效：
1. 【旺相判断】神煞所在宫位处于长生/临官/帝旺/冠带状态 → 强力
2. 【空亡判断】神煞落空亡（旬空）→ 无效
3. 【死绝判断】神煞落死/绝/墓 → 效力大减
4. 【刑冲判断】神煞被刑/冲/害 → 失效或减弱

评估体系：
- 强力（★★★★★）：神煞得令且无空亡刑冲
- 有效（★★★）：神煞得令但有轻微损害
- 弱效（★★）：神煞失令但无空亡
- 无效（✗）：神煞落空亡或死绝
"""

import sys
sys.path.insert(0, '.')

from typing import Dict, List, Optional
from bazi_engine import get_bazi, HEAVENLY_STEMS as STEMS, EARTHLY_BRANCHES as BRANCHES
from penalty_harmony import analyze_branch_relation, is_branch_chong
from children_analyzer import SHENG_WANG_12, YUELING_CANGGAN

# ============================================================
# 空亡表
# ============================================================
# 60甲子中，每旬有2个地支落空亡
# 空亡口诀：甲子旬中戌亥空，甲寅旬中子丑空，甲辰旬中寅卯空，
#          甲午旬中辰巳空，甲申旬中午未空，甲戌旬中申酉空
# 地支索引：子0 丑1 寅2 卯3 辰4 巳5 午6 未7 申8 酉9 戌10 亥11

KONGWANG = {
    # 甲子旬（年支/日支在以下范围时，查空亡）
    # 简化版：按日柱查空亡
    # 以日干为主，查该旬的空亡地支
}

# 完整空亡表：60组干支对应的空亡
# 规律：日和年的空亡查法相同，以日干所在旬判断
# 以日干索引+日支索引确定旬
_XUN_INFO = [
    # 旬首(天干索引), 旬下地支集合
    (0, {0,1,2,3,4,5,6,7,8,9}),   # 甲子旬：子-酉（子丑寅卯辰巳午未申酉，戌亥空）
    (2, {2,3,4,5,6,7,8,9,10,11}), # 甲寅旬：寅-亥（寅卯辰巳午未申酉戌亥，子丑空）
    (4, {4,5,6,7,8,9,10,11,0,1}), # 甲辰旬：辰-丑（辰巳午未申酉戌亥子丑，寅卯空）
    (6, {6,7,8,9,10,11,0,1,2,3}), # 甲午旬：午-子（午未申酉戌亥子丑寅卯，辰巳空）
    (8, {8,9,10,11,0,1,2,3,4,5}), # 甲申旬：申-巳（申酉戌亥子丑寅卯辰巳，午未空）
    (10,{10,11,0,1,2,3,4,5,6,7}),  # 甲戌旬：戌-卯（戌亥子丑寅卯辰巳午未，申酉空）
]

# 每个天干索引对应的旬首
# 正确的旬首映射（口诀：甲己起甲子，乙庚起甲寅，丙辛起甲辰，丁壬起甲午，戊癸起甲申）
STEM_XUN_LEADERS = {
    0: 0,   # 甲 → 甲子旬
    1: 0,   # 己 → 甲子旬（甲己起甲子）
    2: 4,   # 丙 → 甲辰旬
    3: 2,   # 乙 → 甲寅旬
    4: 8,   # 戊 → 甲申旬
    5: 0,   # 己 → 甲子旬
    6: 2,   # 庚 → 甲寅旬
    7: 4,   # 辛 → 甲辰旬
    8: 6,   # 壬 → 甲午旬
    9: 8,   # 癸 → 甲申旬
}


def get_kongwang(bazi_dict: Dict) -> Dict:
    """
    计算八字中的空亡地支

    空亡 = 甲子旬中戌亥空，甲寅旬中子丑空，甲辰旬中寅卯空，
            甲午旬中辰巳空，甲申旬中午未空，甲戌旬中申酉空

    返回：{"空亡地支": [列表], "空亡说明": str}
    """
    bz = bazi_dict['bazi']

    # 以日干查旬首
    day_stem_idx = bazi_dict['day_stem_idx']
    xun_leader = STEM_XUN_LEADERS.get(day_stem_idx, 0)

    # 找到该旬包含的地支
    xun_branches = None
    for leader, branches in _XUN_INFO:
        if leader == xun_leader:
            xun_branches = branches
            break

    if xun_branches is None:
        return {"空亡地支": [], "空亡说明": "无法判断"}

    # 排除的地支 = 空亡
    all_branches = set(range(12))
    kongwang = all_branches - xun_branches
    kongwang_names = [BRANCHES[i] for i in kongwang]

    # 旬首名称
    xun_names = {
        0: "甲子旬", 2: "甲寅旬", 4: "甲辰旬",
        6: "甲午旬", 8: "甲申旬", 10: "甲戌旬"
    }

    return {
        "旬首": xun_names.get(xun_leader, "未知"),
        "旬中地支": [BRANCHES[i] for i in xun_branches],
        "空亡地支": kongwang_names,
        "空亡说明": f"日干{STEMS[day_stem_idx]}属{xun_names.get(xun_leader, '未知')}，空亡为{'、'.join(kongwang_names)}",
    }


def get_branch_state(branch_idx: int, stem_char: str) -> str:
    """
    判断某地支相对于某天干的长生状态

    stem_char: 该天干（用于计算长生）
    """
    if stem_char not in SHENG_WANG_12:
        return "未知"
    return SHENG_WANG_12[stem_char].get(branch_idx, "未知")


def assess_shen_sha_quality(bazi_dict: Dict, target_shensha: str, target_branch_idx: int) -> Dict:
    """
    评估某个神煞在某地支的质量

    《渊海子平》核心原则：
    1. 神煞落长生/临官/帝旺/冠带 → 强力
    2. 神煞落空亡 → 无效
    3. 神煞落死/绝/墓 → 效力大减
    4. 神煞被刑/冲 → 失效或减弱

    参数：
        target_shensha: 神煞名称（如"天乙贵人"）
        target_branch_idx: 神煞所在的地支索引

    返回：
        {
            "神煞": str,
            "地支": str,
            "是否空亡": bool,
            "长生状态": str,
            "是否被冲": bool,
            "是否被刑": bool,
            "质量评级": "强力"/"有效"/"弱效"/"无效",
            "综合评估": str
        }
    """
    bz = bazi_dict['bazi']
    day_stem = STEMS[bazi_dict['day_stem_idx']]
    day_branch_idx = bz['day']['branch_idx']

    # 1. 空亡判断
    kw = get_kongwang(bazi_dict)
    is_kongwang = target_branch_idx not in [
        BRANCHES.index(b) for b in BRANCHES if b in [BRANCHES[i] for i in range(12)]
    ]
    # 更精确的判断
    kongwang_set = set()
    for leader, branches in _XUN_INFO:
        if leader == STEM_XUN_LEADERS.get(bazi_dict['day_stem_idx'], 0):
            all12 = set(range(12))
            kongwang_set = all12 - branches
            break
    is_kongwang = target_branch_idx in kongwang_set

    # 2. 长生状态判断（以日干为基准）
    target_branch_state = get_branch_state(target_branch_idx, day_stem)

    # 3. 刑冲判断
    is_chong = False
    is_xing = False
    is_hai = False
    for pillar in ['year', 'month', 'hour']:
        rel = analyze_branch_relation(
            BRANCHES[target_branch_idx],
            bz[pillar]['branch']
        )
        if rel.get('is_chong'):
            is_chong = True
        if rel.get('is_xing'):
            is_xing = True
        if rel.get('is_hai'):
            is_hai = True

    # 4. 综合质量评级
    if is_kongwang:
        rating = "无效"
        综合 = f"落空亡（{kw['空亡说明']}），神煞无效。"
    elif target_branch_state in ["死", "绝", "墓"]:
        rating = "无效"
        综合 = f"落{target_branch_state}地，神煞效力大减。"
    elif target_branch_state in ["病", "衰"]:
        if is_chong or is_xing:
            rating = "无效"
            综合 = f"落{target_branch_state}地且被刑冲，效力丧失。"
        else:
            rating = "弱效"
            综合 = f"落{target_branch_state}地，效力较弱。"
    elif is_chong:
        rating = "弱效"
        综合 = f"得令但被冲，效力减弱。"
    elif is_xing:
        rating = "弱效"
        综合 = f"得令但被刑，效力减弱。"
    elif target_branch_state in ["长生", "临官", "帝旺", "冠带"]:
        if is_kongwang:
            rating = "无效"
            综合 = "虽然得令但落空亡，效力不显。"
        else:
            rating = "强力"
            综合 = f"处于{target_branch_state}状态，神煞强力。"
    elif target_branch_state in ["沐浴", "胎", "养"]:
        rating = "有效"
        综合 = f"处于{target_branch_state}状态，效力正常。"
    else:
        rating = "有效"
        综合 = f"处于{target_branch_state}状态，效力正常。"

    return {
        "神煞": target_shensha,
        "地支": BRANCHES[target_branch_idx],
        "长生状态": target_branch_state,
        "是否空亡": is_kongwang,
        "是否被冲": is_chong,
        "是否被刑": is_xing,
        "是否被害": is_hai,
        "质量评级": rating,
        "综合评估": 综合,
    }


def assess_all_shensha(bazi_dict: Dict) -> List[Dict]:
    """
    评估八字中所有出现的神煞质量

    返回各神煞的质量评估列表
    """
    bz = bazi_dict['bazi']
    year_stem_idx = bz['year']['stem_idx']
    year_branch_idx = bz['year']['branch_idx']

    assessments = []

    # 天乙贵人
    from shen_sha import get_tianyi_guiren
    tianyi = get_tianyi_guiren(year_stem_idx, year_branch_idx)
    for branch_name in tianyi.get('贵人', []):
        if branch_name in BRANCHES:
            idx = BRANCHES.index(branch_name)
            assessments.append(assess_shen_sha_quality(bazi_dict, "天乙贵人", idx))

    # 文昌
    from shen_sha import get_wenchang
    wenchang = get_wenchang(year_stem_idx)
    if wenchang.get('has'):
        branch_name = wenchang.get('文昌', '')
        if branch_name and branch_name in BRANCHES:
            idx = BRANCHES.index(branch_name)
            assessments.append(assess_shen_sha_quality(bazi_dict, "文昌贵人", idx))

    # 驿马
    from shen_sha import get_yima
    yima = get_yima(year_branch_idx)
    if yima.get('has'):
        for bn in yima.get('驿马', []):
            if bn in BRANCHES:
                idx = BRANCHES.index(bn)
                assessments.append(assess_shen_sha_quality(bazi_dict, "驿马", idx))

    # 桃花
    from shen_sha import get_taohua
    taohua = get_taohua(year_branch_idx)
    if taohua.get('has'):
        for bn in taohua.get('桃花', []):
            if bn in BRANCHES:
                idx = BRANCHES.index(bn)
                assessments.append(assess_shen_sha_quality(bazi_dict, "桃花", idx))

    return assessments


# ============================================================
# 验证测试
# ============================================================
if __name__ == "__main__":
    print("=== 神煞质量评估验证 ===\n")

    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    day_stem = STEMS[bazi['day_stem_idx']]
    print(f"八字：{bazi['birth_chart']}，日干：{day_stem}")

    # 空亡判断
    kw = get_kongwang(bazi)
    print(f"\n空亡判断：")
    print(f"  {kw['空亡说明']}")
    print(f"  旬中地支: {kw['旬中地支']}")
    print(f"  空亡地支: {kw['空亡地支']}")

    # 神煞质量评估
    print(f"\n神煞质量评估（年柱神煞）：")
    assessments = assess_all_shensha(bazi)
    if assessments:
        for a in assessments:
            print(f"  {a['神煞']}在{a['地支']}：{a['质量评级']}（{a['长生状态']}）{'⚠️空亡' if a['是否空亡'] else ''} {'⚠️被冲' if a['是否被冲'] else ''} {'⚠️被刑' if a['是否被刑'] else ''}")
    else:
        print("  无神煞在四柱中")

    # 单个神煞测试
    print(f"\n=== 单个神煞评估测试 ===")
    # 年支午（午是年支=午）
    year_branch_idx = bazi['bazi']['year']['branch_idx']
    print(f"年支：{BRANCHES[year_branch_idx]}（{year_branch_idx}）")
    result = assess_shen_sha_quality(bazi, "年支本气", year_branch_idx)
    print(f"  年支状态：{result}")

    print("\n✅ 神煞质量评估验证完成")
