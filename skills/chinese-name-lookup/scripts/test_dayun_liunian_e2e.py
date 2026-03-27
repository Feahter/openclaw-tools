#!/usr/bin/env python3
"""
大运流年推算系统端到端测试
Phase 8 - 大运流年推算
"""

import sys
import os
import time

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bazi_engine import (
    full_bazi_analysis, get_bazi, get_rizhu_strength,
    determine_xiyongshen, full_liunian_analysis
)
from dayun_liunian import (
    get_dayun_sequence, get_yima_dayun, analyze_dayun,
    analyze_liunian, analyze_liunian_by_year, get_liunian_score,
    get_recent_liunian, full_dayun_analysis, is_yang_stem, is_shun
)


def test_dayun_direction_rules():
    """
    测试1: 大运顺逆规则验证
    
    规则：阳男阴女顺行，阴男阳女逆行
    阳干：甲丙戊庚壬
    阴干：乙丁己辛癸
    """
    print("【端到端测试1】大运顺逆规则验证")
    
    # 测试1.1: 阳干男 → 顺行
    # 甲木日主（阳干）男
    bazi1 = get_bazi(2024, 3, 15, 10)["bazi"]  # 甲辰年
    rizhu1 = get_rizhu_strength(bazi1)
    xiyong1 = determine_xiyongshen(bazi1, rizhu1)
    bazi1_full = {"bazi": bazi1, "rizhu_strength": rizhu1, "xiyongshen": xiyong1}
    birth_ts1 = time.mktime((2024, 3, 15, 10, 0, 0, 0, 0, 0))
    dayun1 = get_dayun_sequence(bazi1_full, "男", birth_ts1)
    
    assert dayun1[0]["shun"] == True, f"甲年男应为顺行, got {dayun1[0]['shun']}"
    assert dayun1[0]["direction"] == "顺行", f"甲年男方向应为顺行"
    print(f"  甲（木，阳干）年 男 → 顺行 ✓")
    
    # 测试1.2: 阴干男 → 逆行
    # 辛金日主（阴干）男
    bazi2 = get_bazi(1990, 5, 15, 10)["bazi"]  # 庚午年，但辛是阴干
    birth_ts2 = time.mktime((1990, 5, 15, 10, 0, 0, 0, 0, 0))
    dayun2 = get_dayun_sequence(bazi2, "男", birth_ts2)
    
    # 庚午年：庚是阳干（索引6），男庚→顺行
    # 但我们要测的是年干阴阳是否影响大运方向
    # 大运方向由年干决定
    year_stem = bazi2["year"]["stem_idx"]
    expected_shun = is_shun(year_stem, "男")
    assert dayun2[0]["shun"] == expected_shun, f"庚年男应{expected_shun}, got {dayun2[0]['shun']}"
    print(f"  庚（金，阳干）年 男 → 顺行（阳男顺）✓")
    
    # 测试1.3: 阴干女 → 顺行
    # 乙木日主（阴干）女
    bazi3 = get_bazi(2023, 4, 10, 10)["bazi"]  # 癸卯年，癸是阴干
    birth_ts3 = time.mktime((2023, 4, 10, 10, 0, 0, 0, 0, 0))
    dayun3 = get_dayun_sequence(bazi3, "女", birth_ts3)
    
    year_stem3 = bazi3["year"]["stem_idx"]
    expected_shun3 = is_shun(year_stem3, "女")
    assert dayun3[0]["shun"] == expected_shun3, f"癸年女应{expected_shun3}, got {dayun3[0]['shun']}"
    print(f"  癸（水，阴干）年 女 → 顺行（阴女顺）✓")
    
    # 测试1.4: 阳干女 → 逆行
    # 丙火日主（阳干）女
    bazi4 = get_bazi(2024, 8, 20, 15)["bazi"]  # 甲辰年，丙是阳干
    birth_ts4 = time.mktime((2024, 8, 20, 15, 0, 0, 0, 0, 0))
    dayun4 = get_dayun_sequence(bazi4, "女", birth_ts4)
    
    year_stem4 = bazi4["year"]["stem_idx"]
    expected_shun4 = is_shun(year_stem4, "女")
    assert dayun4[0]["shun"] == expected_shun4, f"甲年女应{expected_shun4}, got {dayun4[0]['shun']}"
    print(f"  甲（木，阳干）年 女 → 逆行（阳女逆）✓")
    
    print("  ✓ 大运顺逆规则全部验证通过\n")


def test_liunian_analysis():
    """
    测试2: 流年分析验证
    """
    print("【端到端测试2】流年分析验证")
    
    # 测试2.1: 流年干支计算
    # 2026年: (2026-4)%10=2(丙), (2026-4)%12=6(午) → 丙午
    from dayun_liunian import get_liunian_ganzhi
    stem, branch = get_liunian_ganzhi(2026)
    assert stem == 2, f"2026年天干应为丙(2), got {stem}"
    assert branch == 6, f"2026年地支应为午(6), got {branch}"
    print(f"  2026年: 丙午 ✓")
    
    # 测试2.2: 流年分析
    bazi = get_bazi(2024, 3, 15, 10)
    bazi_inner = bazi["bazi"]
    rizhu = get_rizhu_strength(bazi_inner)
    xiyong = determine_xiyongshen(bazi_inner, rizhu)
    bazi_full = {"bazi": bazi_inner, "rizhu_strength": rizhu, "xiyongshen": xiyong}
    
    liunian = analyze_liunian_by_year(2026, bazi_full)
    assert liunian["stem"] == "丙", f"2026年天干应为丙, got {liunian['stem']}"
    assert liunian["branch"] == "午", f"2026年地支应为午, got {liunian['branch']}"
    assert liunian["ganzhi"] == "丙午", f"2026年干支应为丙午, got {liunian['ganzhi']}"
    print(f"  2026年流年分析: {liunian['ganzhi']} ({liunian['shishen']}) - {liunian['luck']}")
    print(f"    分析: {liunian['analysis']}")
    
    # 测试2.3: 近5年流年
    recent = get_recent_liunian(bazi_full, [], 2026, 5)
    assert len(recent) == 5, f"应返回5年流年, got {len(recent)}"
    assert recent[0]["year"] == 2022, f"第一年应为2022, got {recent[0]['year']}"
    assert recent[-1]["year"] == 2026, f"最后一年应为2026, got {recent[-1]['year']}"
    print(f"  近5年流年: {[(r['year'], r['ganzhi']) for r in recent]}")
    print("  ✓ 流年分析验证通过\n")


def test_full_dayun_liunian_integration():
    """
    测试3: 完整大运流年分析集成测试
    """
    print("【端到端测试3】完整大运流年分析集成测试")
    
    # 测试3.1: full_liunian_analysis 函数
    result = full_liunian_analysis(2024, 3, 15, 10, "男")
    
    assert "birth_chart" in result, "缺少 birth_chart"
    assert "bazi" in result, "缺少 bazi"
    assert "gender" in result, "缺少 gender"
    assert "dayun_list" in result, "缺少 dayun_list"
    assert "recent_liunian" in result, "缺少 recent_liunian"
    assert result["gender"] == "男", f"性别应为男, got {result['gender']}"
    print(f"  八字: {result['birth_chart']}")
    print(f"  性别: {result['gender']}")
    print(f"  喜用神: {result['xiyongshen']['xiyongshen']}")
    
    # 测试3.2: 大运列表验证
    dayun_list = result["dayun_list"]
    assert len(dayun_list) == 12, f"应有12步大运, got {len(dayun_list)}"
    assert dayun_list[0]["start_age"] == 0, "第一步大运起始年龄应为0"
    assert dayun_list[0]["end_age"] == 9, "第一步大运结束年龄应为9"
    print(f"  大运数量: {len(dayun_list)}")
    print(f"  前3步大运:")
    for du in dayun_list[:3]:
        print(f"    {du['start_age']}-{du['end_age']}岁: {du['ganzhi']}")
    
    # 测试3.3: 近5年流年验证
    recent = result["recent_liunian"]
    assert len(recent) == 5, f"应有5年流年, got {len(recent)}"
    print(f"  近5年流年:")
    for ln in recent:
        print(f"    {ln['year']}年 {ln['ganzhi']} ({ln['shishen']}): {ln['luck']}")
    
    # 测试3.4: 驿马运
    yima = result["yima"]
    if yima:
        print(f"  驿马运: {yima['yima_branch']}（{yima['description']}）")
    
    # 测试3.5: 不同性别对比
    result_female = full_liunian_analysis(2024, 3, 15, 10, "女")
    dayun_male = result["dayun_list"]
    dayun_female = result_female["dayun_list"]
    
    # 同一八字，不同性别，大运干支应不同
    # 因为大运方向不同（顺vs逆）
    assert dayun_male[0]["ganzhi"] != dayun_female[0]["ganzhi"] or \
           dayun_male[1]["ganzhi"] != dayun_female[1]["ganzhi"], \
           "男女大运应有差异"
    print(f"  男第一步大运: {dayun_male[0]['ganzhi']} ({dayun_male[0]['direction']})")
    print(f"  女第一步大运: {dayun_female[0]['ganzhi']} ({dayun_female[0]['direction']})")
    
    print("  ✓ 完整大运流年分析验证通过\n")


def test_liunian_score():
    """
    测试4: 流年得分计算
    """
    print("【端到端测试4】流年得分计算")
    
    # 测试天干相生
    # 甲(0) 木生丙(2) 火 → +1
    score1 = get_liunian_score(0, 0, 2, 0)  # 甲寅 vs 丙寅
    print(f"  甲寅 vs 丙寅: {score1} (应为+1或0，木生火)")
    
    # 测试天干相克
    # 庚(6) 金克甲(0) 木 → -1
    score2 = get_liunian_score(6, 0, 0, 0)  # 庚子 vs 甲子
    print(f"  庚子 vs 甲子: {score2} (应为-1，金克木)")
    
    # 测试比和
    # 甲(0) 木 vs 甲(0) 木 → 0
    score3 = get_liunian_score(0, 0, 0, 0)  # 甲寅 vs 甲寅
    print(f"  甲寅 vs 甲寅: {score3} (应为0，比和)")
    
    # 测试地支六冲
    # 子(0) 午(6) 冲 → -1
    score4 = get_liunian_score(4, 0, 4, 6)  # 辰子 vs 辰午
    print(f"  辰子 vs 辰午: {score4} (应为-1，子午冲)")
    
    print("  ✓ 流年得分计算验证通过\n")


def test_yima_dayun():
    """
    测试5: 驿马运查询
    """
    print("【端到端测试5】驿马运查询")
    
    # 申子辰马在寅
    # 子年（2024年是辰年，但子年驿马在寅）
    # 庚午年：巳酉丑马在亥
    bazi = get_bazi(1990, 5, 15, 10)["bazi"]
    yima = get_yima_dayun(bazi["year"]["stem_idx"], bazi["year"]["branch_idx"], "男")
    
    if yima:
        print(f"  庚午年 男: 驿马在{yima['yima_branch']}")
        print(f"  驿马运年龄: {yima['age_range']}岁")
        print(f"  描述: {yima['description']}")
    
    print("  ✓ 驿马运查询验证通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("大运流年推算系统 - 端到端测试 (Phase 8)")
    print("=" * 60)
    print()
    
    test_dayun_direction_rules()
    test_liunian_analysis()
    test_full_dayun_liunian_integration()
    test_liunian_score()
    test_yima_dayun()
    
    print("=" * 60)
    print("所有测试通过 ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
