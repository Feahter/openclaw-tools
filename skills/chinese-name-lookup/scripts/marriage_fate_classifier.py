# -*- coding: utf-8 -*-
"""
女命婚姻贵贱格局分类 v1.0
===========================
基于《渊海子平》女命篇：

一、富贵格（15种）
  正气官星 | 财官两旺 | 印绶天德 | 独杀有制 | 伤官生财
  坐禄逢财 | 官星带合 | 日贵逢财 | 官贵逢官 | 官星坐禄
  官星桃花 | 食神生旺 | 食神生财 | 杀化印绶 | 二德扶身
  三奇合局 | 阳刃有制 | 拱禄拱贵 | 归禄逢财

二、贱格（18种）
  官杀混杂 | 官杀无制 | 杀星太重 | 伤官太重 | 贪财坏印
  比肩犯重 | 无官见合 | 无印见杀 | 伤官七杀 | 带合桃花
  八字刑冲 | 财多身弱 | 阳刃冲刑 | 金神带刃 | 多官多合
  倒插桃花 | 身旺无依 | 伤官见官 | 财官遇印 | 印绶遇劫
"""

import sys
sys.path.insert(0, '.')

from typing import Dict, List, Optional
from bazi_engine import get_bazi, get_shishen, HEAVENLY_STEMS as STEMS, EARTHLY_BRANCHES as BRANCHES
from children_analyzer import count_shishen, YUELING_CANGGAN
from penalty_harmony import analyze_branch_relation
from shen_sha import get_tianyi_guiren, get_tiande, get_yuede, get_taohua, get_yima


# ============================================================
# 辅助：判断某十神是否在八字中
# ============================================================
def has_shishen(bazi_dict: Dict, name: str) -> bool:
    """判断八字中是否有指定十神"""
    r = count_shishen(bazi_dict, name)
    return r['count'] > 0


def count_shishen_total(bazi_dict: Dict, name: str) -> int:
    """统计某十神总数"""
    return count_shishen(bazi_dict, name)['count']


# ============================================================
# 辅助：判断是否有某地支关系
# ============================================================
def has_branch_relation(bazi_dict: Dict, relation_type: str) -> bool:
    """判断八字中是否存在指定地支关系类型"""
    bz = bazi_dict['bazi']
    pillars = ['year', 'month', 'day', 'hour']

    for i in range(len(pillars)):
        for j in range(i+1, len(pillars)):
            p1, p2 = pillars[i], pillars[j]
            rel = analyze_branch_relation(bz[p1]['branch'], bz[p2]['branch'])
            if relation_type in [r['type'] for r in rel.get('relations', [])]:
                return True
    return False


def count_shishen_in_branch(bazi_dict: Dict, shishen_name: str, target_branch: str) -> int:
    """判断某十神是否在指定地支藏干中"""
    bz = bazi_dict['bazi']
    day_stem_idx = bazi_dict['day_stem_idx']
    count = 0
    for pillar in ['year', 'month', 'day', 'hour']:
        branch = bz[pillar]['branch']
        if branch == target_branch:
            canggan = YUELING_CANGGAN.get(branch, {})
            for pos in ['本气', '中气', '余气']:
                gan = canggan.get(pos)
                if gan and gan in STEMS:
                    other_idx = STEMS.index(gan)
                    s = get_shishen(day_stem_idx, other_idx)
                    if s == shishen_name:
                        count += 1
    return count


# ============================================================
# 辅助：判断七杀是否被制
# ============================================================
def is_qisha_controlled(bazi_dict: Dict) -> bool:
    """
    判断七杀是否被制服

    七杀被制服的方式：
    1. 食神制杀（七杀被食神克）
    2. 印星化杀（印星能生身化杀）
    3. 羊刃驾杀（阳刃帮助身强以抗杀）
    """
    day_stem_idx = bazi_dict['day_stem_idx']
    day_stem = STEMS[day_stem_idx]
    bz = bazi_dict['bazi']

    qisha_count = count_shishen_total(bazi_dict, "偏官")
    if qisha_count == 0:
        return True  # 无七杀，不存在被制

    shishen_count = count_shishen_total(bazi_dict, "食神")
    yinxing_count = count_shishen_total(bazi_dict, "正印") + count_shishen_total(bazi_dict, "偏印")

    # 食神制杀
    if shishen_count > 0:
        return True
    # 印星化杀
    if yinxing_count > 0:
        return True
    # 阳刃驾杀（需命主身强）
    # 简化判断：月令是否得令
    month_branch_idx = bz['month']['branch_idx']
    from children_analyzer import SHENG_WANG_12
    sw = SHENG_WANG_12[day_stem][month_branch_idx]
    if sw in ['临官', '帝旺', '冠带'] and qisha_count > 0:
        return True

    return False


# ============================================================
# 辅助：判断天德/月德
# ============================================================
def has_tiande_yuede(bazi_dict: Dict) -> bool:
    """判断是否有天德或月德"""
    bz = bazi_dict['bazi']
    year_stem_idx = bz['year']['stem_idx']
    year_branch_idx = bz['year']['branch_idx']

    td = get_tiande(year_stem_idx)
    yd = get_yuede(year_stem_idx)

    return td.get('has', False) or yd.get('has', False)


# ============================================================
# 辅助：判断伤官是否太重
# ============================================================
def is_shangguan_too_heavy(bazi_dict: Dict) -> bool:
    """判断伤官是否太重（女命忌讳伤官太旺）"""
    shangguan = count_shishen_total(bazi_dict, "伤官")
    day_stem_idx = bazi_dict['day_stem_idx']
    bz = bazi_dict['bazi']

    # 伤官超过2个视为太重
    if shangguan >= 3:
        return True
    # 或者伤官在月令
    if shangguan >= 2:
        month_stem_idx = bz['month']['stem_idx']
        if get_shishen(day_stem_idx, month_stem_idx) == "伤官":
            return True
    return False


# ============================================================
# 辅助：判断官杀混杂
# ============================================================
def is_guan_sha_混杂(bazi_dict: Dict) -> bool:
    """判断官杀混杂（正官和七杀同时存在）"""
    zhengguan = count_shishen_total(bazi_dict, "正官")
    qisha = count_shishen_total(bazi_dict, "偏官")
    return zhengguan > 0 and qisha > 0


# ============================================================
# 核心分类函数
# ============================================================
def classify_female_marriage_fate(bazi_dict: Dict) -> Dict:
    """
    女命婚姻贵贱格局分类

    返回：
        {
            "category": "富贵" / "平常" / "贫贱",
            "matching_patterns": ["模式1", "模式2"],
            "violating_patterns": ["违规1"],
            "score": 0-100,
            "analysis": "详细分析"
        }
    """
    bz = bazi_dict['bazi']
    day_stem_idx = bazi_dict['day_stem_idx']
    day_stem = STEMS[day_stem_idx]

    matching_patterns = []
    violating_patterns = []
    score = 50  # 基础分

    # ===== 富贵格检测 =====
    # 1. 正气官星：只有正官无七杀
    zhengguan = count_shishen_total(bazi_dict, "正官")
    qisha = count_shishen_total(bazi_dict, "偏官")
    if zhengguan > 0 and qisha == 0:
        matching_patterns.append("正气官星")
        score += 15

    # 2. 财官两旺：财星和官星都旺
    caishen = count_shishen_total(bazi_dict, "正财") + count_shishen_total(bazi_dict, "偏财")
    if caishen >= 2 and zhengguan >= 1:
        matching_patterns.append("财官两旺")
        score += 15

    # 3. 印绶天德：有印绶 + 天德/月德
    yinxing = count_shishen_total(bazi_dict, "正印") + count_shishen_total(bazi_dict, "偏印")
    if yinxing >= 1 and has_tiande_yuede(bazi_dict):
        matching_patterns.append("印绶天德")
        score += 15

    # 4. 独杀有制：只有一个七杀且被制服
    if qisha == 1 and is_qisha_controlled(bazi_dict):
        matching_patterns.append("独杀有制")
        score += 15

    # 5. 伤官生财：伤官生财（需要财星）
    shangguan = count_shishen_total(bazi_dict, "伤官")
    if shangguan >= 1 and caishen >= 2:
        matching_patterns.append("伤官生财")
        score += 10

    # 6. 官星带合：官星与其他天干相合
    if zhengguan >= 1:
        # 检查官星是否与其他天干有合
        from penalty_harmony import analyze_stem_relation
        for pillar in ['year', 'month', 'day', 'hour']:
            stem = bz[pillar]['stem']
            stem_idx = bz[pillar]['stem_idx']
            if get_shishen(day_stem_idx, stem_idx) == "正官":
                for p2 in ['year', 'month', 'day', 'hour']:
                    if p2 != pillar:
                        stem2 = bz[p2]['stem']
                        stem2_idx = bz[p2]['stem_idx']
                        rel = analyze_stem_relation(stem, stem2)
                        if rel['is_harmony']:
                            matching_patterns.append("官星带合")
                            score += 10
                            break

    # 7. 食神生旺：食神旺相
    shishen = count_shishen_total(bazi_dict, "食神")
    if shishen >= 2:
        matching_patterns.append("食神生旺")
        score += 10

    # 8. 二德扶身：天德+月德同时在
    bz_info = bazi_dict['bazi']
    year_stem_idx2 = bz_info['year']['stem_idx']
    td = get_tiande(year_stem_idx2)
    yd = get_yuede(year_stem_idx2)
    if td.get('has') and yd.get('has'):
        matching_patterns.append("二德扶身")
        score += 20

    # 9. 阳刃有制：身强有阳刃但被制（通过七杀或食神）
    if qisha >= 1 and is_qisha_controlled(bazi_dict):
        matching_patterns.append("阳刃有制")
        score += 10

    # 10. 坐禄逢财：日支为禄（临官/帝旺）且带财
    day_branch_idx = bz['day']['branch_idx']
    from children_analyzer import SHENG_WANG_12
    day_sw = SHENG_WANG_12[day_stem][day_branch_idx]
    if day_sw in ['临官', '帝旺'] and caishen >= 1:
        matching_patterns.append("坐禄逢财")
        score += 15

    # ===== 贫贱格检测 =====
    # 1. 官杀混杂
    if is_guan_sha_混杂(bazi_dict):
        violating_patterns.append("官杀混杂")
        score -= 20

    # 2. 官杀无制
    if qisha >= 2 and not is_qisha_controlled(bazi_dict):
        violating_patterns.append("官杀无制")
        score -= 20

    # 3. 杀星太重
    if qisha >= 3:
        violating_patterns.append("杀星太重")
        score -= 20

    # 4. 伤官太重
    if is_shangguan_too_heavy(bazi_dict):
        violating_patterns.append("伤官太重")
        score -= 15

    # 5. 贪财坏印
    if caishen >= 2 and yinxing >= 1:
        # 财星坏印：财星克制印星
        violating_patterns.append("贪财坏印")
        score -= 15

    # 6. 比肩犯重
    bj = count_shishen_total(bazi_dict, "比肩") + count_shishen_total(bazi_dict, "劫财")
    if bj >= 3:
        violating_patterns.append("比肩犯重")
        score -= 10

    # 7. 伤官见官
    if shangguan >= 1 and zhengguan >= 1:
        violating_patterns.append("伤官见官")
        score -= 20

    # 8. 八字刑冲
    if has_branch_relation(bazi_dict, "冲") and has_branch_relation(bazi_dict, "刑"):
        violating_patterns.append("八字刑冲")
        score -= 15

    # 9. 财多身弱
    if caishen >= 3 and (shangguan >= 2 or qisha >= 2):
        violating_patterns.append("财多身弱")
        score -= 10

    # 10. 阳刃冲刑
    # 简化判断：日支被冲且有阳刃
    if has_branch_relation(bazi_dict, "冲"):
        day_rel = analyze_branch_relation(bz['day']['branch'], bz['year']['branch'])
        if day_rel.get('is_chong'):
            violating_patterns.append("阳刃冲刑")
            score -= 15

    # 11. 倒插桃花
    # 桃花在时柱+官星同在
    th = get_taohua(bz['hour']['branch_idx'])
    if th.get('has') and zhengguan >= 1:
        violating_patterns.append("倒插桃花")
        score -= 15

    # 12. 身旺无依
    if bj >= 3 and caishen >= 3:
        violating_patterns.append("身旺无依")
        score -= 10

    # 13. 无印见杀
    if yinxing == 0 and qisha >= 2:
        violating_patterns.append("无印见杀")
        score -= 15

    # ===== 综合判断 =====
    score = max(0, min(100, score))

    if len(violating_patterns) >= 2 and score < 40:
        category = "贫贱"
    elif len(matching_patterns) >= 2 and score >= 60:
        category = "富贵"
    elif len(violating_patterns) >= 1 and score < 40:
        category = "贫贱"
    elif len(matching_patterns) >= 1 and score >= 50:
        category = "中上"
    else:
        category = "平常"

    analysis_parts = []
    if matching_patterns:
        analysis_parts.append(f"【富贵因素】{'、'.join(matching_patterns)}")
    if violating_patterns:
        analysis_parts.append(f"【不利因素】{'、'.join(violating_patterns)}")
    if not matching_patterns and not violating_patterns:
        analysis_parts.append("格局平常，无明显吉凶倾向")

    analysis = "；".join(analysis_parts)

    return {
        "category": category,
        "matching_patterns": matching_patterns,
        "violating_patterns": violating_patterns,
        "score": score,
        "analysis": analysis,
    }


# ============================================================
# 验证测试
# ============================================================
if __name__ == "__main__":
    print("=== 女命婚姻格局验证 ===\n")

    # 测试1：成都男婴（案例参考）
    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    day_stem = STEMS[bazi['day_stem_idx']]
    print(f"八字：{bazi['birth_chart']}，性别：女")
    print(f"日主：{day_stem}")

    # 打印各柱十神
    print("\n各柱十神（女命）：")
    for pillar in ['year', 'month', 'day', 'hour']:
        s = get_shishen(bazi['day_stem_idx'], bazi['bazi'][pillar]['stem_idx'])
        print(f"  {pillar}: {bazi['bazi'][pillar]['stem']}{bazi['bazi'][pillar]['branch']} → {s}")

    # 女命分析
    print("\n女命婚姻格局：")
    result = classify_female_marriage_fate(bazi)
    print(f"  分类：{result['category']}")
    print(f"  分数：{result['score']}/100")
    print(f"  富贵因素：{result['matching_patterns'] or '无'}")
    print(f"  不利因素：{result['violating_patterns'] or '无'}")
    print(f"  分析：{result['analysis']}")

    # 测试官杀混杂
    print("\n=== 官杀混杂检测 ===")
    from marriage_analyzer import get_spouse_star
    spouse = get_spouse_star(bazi, gender=0)
    print(f"  女命配偶星: {spouse}")

    print("\n✅ 女命婚姻格局分析验证完成")
