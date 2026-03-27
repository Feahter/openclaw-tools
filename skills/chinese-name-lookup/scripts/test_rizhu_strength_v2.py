#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日主强弱量化判定 v2 测试用例

4个核心测试：
1. 日主极强（帝旺+通根+比劫）
2. 日主极弱（失令+无根）
3. 日主中和（介于两者之间）
4. V1 vs V2 结果对比验证
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rizhu_strength_v2 import get_rizhu_strength_v2
from bazi_engine import get_bazi, get_rizhu_strength


def test_case(name, bazi, expected_label, expected_score_range, description):
    """执行单个测试用例"""
    v2 = get_rizhu_strength_v2(bazi)
    v1 = get_rizhu_strength(bazi)

    print(f"\n{'='*55}")
    print(f"  {name}")
    print(f"{'='*55}")
    print(f"  描述: {description}")
    print(f"  八字: "
          f"{'年'}{bazi['year']['stem_idx']:02d}{bazi['year']['branch_idx']:02d} "
          f"{'月'}{bazi['month']['stem_idx']:02d}{bazi['month']['branch_idx']:02d} "
          f"{'日'}{bazi['day']['stem_idx']:02d}{bazi['day']['branch_idx']:02d} "
          f"{'时'}{bazi['hour']['stem_idx']:02d}{bazi['hour']['branch_idx']:02d}")
    print(f"  日干={v2['day_stem']}({v2['day_element']}), 月令={v2['month_branch']}({v2['breakdown']['yueling']['state']})")
    print()
    print(f"  V2 结果: {v2['strength']} (score={v2['score']})")
    print(f"  V2 reason: {v2['reason']}")
    print(f"  V1 结果: {v1['strength']} - {v1['reason']}")
    print()
    print(f"  详细得分:")
    yl = v2['breakdown']['yueling']
    tg = v2['breakdown']['tongen']
    bj = v2['breakdown']['bijie']
    yx = v2['breakdown']['yinxing']
    print(f"    月令: {yl['state']}={yl['score']}分 (权重{yl['weight']})")
    print(f"    通根: {tg['score']}分 (count={tg['count']}, "
          f"full={tg['full_count']}, half={tg['half_count']}, weak={tg['weak_count']})")
    print(f"    比劫: {bj['score']}分 (count={bj['count']})")
    print(f"    印星: {yx['score']}分 (stem={yx['stem_count']}, branch={yx['branch_count']}, element={yx['yin_element']})")
    print(f"    合计: {yl['score']}+{tg['score']}+{bj['score']}+{yx['score']}={v2['score']}")
    print(f"    通根明细: {tg['details']}")

    # 验证
    passed = True
    checks = []

    if expected_label:
        if v2['strength'] == expected_label:
            checks.append(f"✓ strength={expected_label}")
        else:
            checks.append(f"✗ strength: 期望{expected_label}, 实际{v2['strength']}")
            passed = False

    if expected_score_range:
        lo, hi = expected_score_range
        if lo <= v2['score'] <= hi:
            checks.append(f"✓ score={v2['score']} in [{lo},{hi}]")
        else:
            checks.append(f"✗ score: 期望[{lo},{hi}], 实际{v2['score']}")
            passed = False

    if v2['method'] == 'v2_weighted':
        checks.append("✓ method=v2_weighted")
    else:
        checks.append(f"✗ method: {v2['method']}")
        passed = False

    print()
    for c in checks:
        print(f"  {c}")

    return passed, v2, v1


def test_1_extremely_strong():
    """测试1: 日主极强（帝旺+通根+比劫）

    构造条件：
    - 日干=甲，月令=卯（帝旺=1.0）
    - 多地支含甲木（本气或中气通根）
    - 年干/月干有比劫甲乙
    """
    bazi = {
        "year": {"stem_idx": 0, "branch_idx": 11},   # 甲子
        "month": {"stem_idx": 1, "branch_idx": 3},  # 乙卯（帝旺）
        "day": {"stem_idx": 0, "branch_idx": 2},    # 甲寅（临官）
        "hour": {"stem_idx": 1, "branch_idx": 0},   # 乙子
    }
    return test_case(
        "测试1: 日主极强",
        bazi,
        expected_label="强",  # 帝旺40+多通根+多比劫 → 强
        expected_score_range=(60, 85),  # 接近极强但印星少
        description="甲木日主，卯月帝旺，亥/寅/卯地支多通根，年/月干多比劫"
    )


def test_2_extremely_weak():
    """测试2: 日主极弱（失令+无根）

    构造条件：
    - 日干=甲，月令=午（死=0.2）
    - 四地支无甲木通根
    - 天干地支无比劫印星
    """
    bazi = {
        "year": {"stem_idx": 2, "branch_idx": 6},   # 丙午
        "month": {"stem_idx": 3, "branch_idx": 6},  # 丁午（死）
        "day": {"stem_idx": 0, "branch_idx": 5},   # 甲巳（病）
        "hour": {"stem_idx": 4, "branch_idx": 8},  # 戊申（金）
    }
    return test_case(
        "测试2: 日主极弱",
        bazi,
        expected_label="极弱",
        expected_score_range=(0, 20),
        description="甲木日主，午月死，无通根，无比劫，无印星"
    )


def test_3_neutral():
    """测试3: 日主中和

    构造条件：
    - 日干=丁，月令=寅（衰=0.4）
    - 有少量通根和比劫
    """
    bazi = {
        "year": {"stem_idx": 6, "branch_idx": 10},  # 庚戌
        "month": {"stem_idx": 0, "branch_idx": 2},  # 甲寅（衰）
        "day": {"stem_idx": 3, "branch_idx": 3},   # 丁卯
        "hour": {"stem_idx": 2, "branch_idx": 5},  # 丙巳
    }
    return test_case(
        "测试3: 日主中和",
        bazi,
        expected_label="弱",  # 中和偏弱
        expected_score_range=(20, 50),
        description="丁火日主，寅月衰，少量通根和比劫"
    )


def test_4_v1_v2_comparison():
    """测试4: V1 vs V2 对比

    对比真实八字数据的判定差异
    """
    print(f"\n{'='*55}")
    print(f"  测试4: V1 vs V2 全面对比")
    print(f"{'='*55}")

    test_dates = [
        (2024, 3, 15, 10, "甲辰月庚丑日"),
        (2025, 1, 15, 14, "丙寅月丁亥日"),
        (1990, 8, 15, 8, "甲申月戊辰日"),
        (1987, 6, 20, 12, "丁未月戊午日"),
    ]

    all_pass = True
    for y, m, d, h, desc in test_dates:
        bazi = get_bazi(y, m, d, h)["bazi"]
        v2 = get_rizhu_strength_v2(bazi)
        v1 = get_rizhu_strength(bazi)

        yl = v2['breakdown']['yueling']
        tg = v2['breakdown']['tongen']
        bj = v2['breakdown']['bijie']
        yx = v2['breakdown']['yinxing']

        match = "✓" if v1['strength'] == v2['strength'] else "△"
        print(f"\n  {match} {y}-{m:02d}-{d:02d} {h:02d}:00 ({desc})")
        print(f"     V1={v1['strength']} | V2={v2['strength']}({v2['score']})")
        print(f"     月令:{yl['state']}({yl['score']}) + "
              f"通根:{tg['score']}({tg['count']}个) + "
              f"比劫:{bj['score']}({bj['count']}个) + "
              f"印星:{yx['score']} = {v2['score']}")
        print(f"     V2 reason: {v2['reason']}")

        if v2['method'] != 'v2_weighted':
            all_pass = False
            print(f"     ✗ method错误: {v2['method']}")

        # V2 score应该和各项相加一致
        calc_sum = round(yl['score'] + tg['score'] + bj['score'] + yx['score'], 1)
        if abs(calc_sum - v2['score']) > 0.1:
            all_pass = False
            print(f"     ✗ 分数不一致: {calc_sum} != {v2['score']}")

    return all_pass, None, None


def main():
    print("="*55)
    print("  日主强弱量化判定 v2 - 测试套件")
    print("="*55)

    results = []

    p1, v2_1, v1_1 = test_1_extremely_strong()
    results.append(("极强测试", p1))

    p2, v2_2, v1_2 = test_2_extremely_weak()
    results.append(("极弱测试", p2))

    p3, v2_3, v1_3 = test_3_neutral()
    results.append(("中和测试", p3))

    p4, _, _ = test_4_v1_v2_comparison()
    results.append(("V1V2对比", p4))

    # 总结
    print(f"\n{'='*55}")
    print("  测试总结")
    print(f"{'='*55}")
    all_ok = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}  {name}")
        if not passed:
            all_ok = False

    print()
    if all_ok:
        print("✓ 所有测试通过！")
    else:
        print("✗ 存在失败的测试")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
