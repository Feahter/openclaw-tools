#!/usr/bin/env python3
"""
流年分析框架 v1 验证测试
测试目标八字：2026-03-23 出生
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bazi_engine import get_bazi, get_rizhu_strength, determine_xiyongshen
from dayun_liunian import (
    get_dayun_sequence, analyze_liunian_by_year, get_recent_liunian,
    generate_liunian_text, analyze_liunian
)


def test_liunian_v1():
    """验证流年分析框架 v1"""
    print("=" * 60)
    print("流年分析框架 v1 验证测试")
    print("=" * 60)
    
    # 目标八字：2026-03-23 辰时（早8点）男命
    birth_year, birth_month, birth_day = 2026, 3, 23
    birth_hour = 8
    gender = "男"
    
    # 1. 获取八字
    bazi_result = get_bazi(birth_year, birth_month, birth_day, birth_hour)
    bazi = bazi_result["bazi"]
    
    # 2. 判断日主强弱
    rizhu = get_rizhu_strength(bazi)
    
    # 3. 确定喜用神
    xiyong = determine_xiyongshen(bazi, rizhu)
    
    # 组合八字信息
    bazi_full = {
        "bazi": bazi,
        "rizhu_strength": rizhu,
        "xiyongshen": xiyong,
    }
    
    print(f"\n【八字信息】")
    print(f"  年柱: {HEAVENLY_STEMS[bazi['year']['stem_idx']]}{EARTHLY_BRANCHES[bazi['year']['branch_idx']]}")
    print(f"  月柱: {HEAVENLY_STEMS[bazi['month']['stem_idx']]}{EARTHLY_BRANCHES[bazi['month']['branch_idx']]}")
    print(f"  日柱: {HEAVENLY_STEMS[bazi['day']['stem_idx']]}{EARTHLY_BRANCHES[bazi['day']['branch_idx']]}")
    print(f"  时柱: {HEAVENLY_STEMS[bazi['hour']['stem_idx']]}{EARTHLY_BRANCHES[bazi['hour']['branch_idx']]}")
    print(f"  日主: {HEAVENLY_STEMS[bazi['day']['stem_idx']]} ({ELEMENT_NAMES[STEM_ELEMENTS[bazi['day']['stem_idx']]]})")
    print(f"  月令: {EARTHLY_BRANCHES[bazi['month']['branch_idx']]} ({ELEMENT_NAMES[BRANCH_ELEMENTS[bazi['month']['branch_idx']]]})")
    print(f"  日主强弱: {rizhu.get('strength', '未知')}")
    print(f"  喜用神: {xiyong.get('xiyongshen', [])}")
    print(f"  忌神: {xiyong.get('jishen', [])}")
    print(f"  格局: {xiyong.get('pattern', '未知')}")
    
    # 4. 获取大运序列
    birth_ts = time.mktime((birth_year, birth_month, birth_day, birth_hour, 0, 0, 0, 0, 0))
    dayun_list = get_dayun_sequence(bazi_full, gender, birth_ts)
    
    print(f"\n【大运序列（前3步）】")
    for i, dy in enumerate(dayun_list[:3]):
        print(f"  {dy['start_age']}-{dy['end_age']}岁: {dy['ganzhi']} {dy['direction']}")
    
    current_dayun = dayun_list[0] if dayun_list else None
    
    # 5. 流年分析 v1 - 近5年
    print(f"\n【流年分析 v1（近5年）】")
    print(f"{'年':<6} {'干支':<6} {'十神':<6} {'五行':<4} {'吉凶':<6} {'评分':<6} {'简析'}")
    print("-" * 80)
    
    current_year = 2026
    for year in range(current_year - 4, current_year + 1):
        # 跳过出生年前
        if year < birth_year:
            continue
        
        # 使用增强版 analyze_liunian_by_year
        liunian = analyze_liunian_by_year(year, bazi_full, current_dayun)
        
        print(f"{year:<6} {liunian['ganzhi']:<6} {liunian['shishen']:<6} {liunian.get('element', '?'):<4} "
              f"{liunian['luck']:<6} {liunian['score']:<6} {liunian['analysis'][:30]}...")
    
    # 6. 详细分析2026年
    print(f"\n【2026年流年详细分析】")
    liunian_2026 = analyze_liunian_by_year(2026, bazi_full, current_dayun)
    print(f"  流年干支: {liunian_2026['ganzhi']}")
    print(f"  五行: {liunian_2026.get('element', '?')}")
    print(f"  十神: {liunian_2026['shishen']}")
    print(f"  吉凶: {liunian_2026['luck']} (评分: {liunian_2026['score']})")
    print(f"  大运叠加: {liunian_2026.get('dayun_ganzhi', '无')}")
    print(f"  影响因素:")
    for f in liunian_2026.get("factors", []):
        print(f"    - {f}")
    print(f"  分析: {liunian_2026['analysis']}")
    
    # 7. 验证 generate_liunian_text 独立使用
    print(f"\n【generate_liunian_text 独立测试】")
    test_info = {
        "shishen": "正财",
        "score": 55,
        "luck": "小吉",
        "stem": "戊",
        "branch": "子",
        "xiyong_in_stem": True,
        "jishen_in_stem": False,
    }
    test_text = generate_liunian_text(test_info, xiyong, rizhu)
    print(f"  正财流年 + 喜用神: {test_text}")
    
    print("\n" + "=" * 60)
    print("✓ 流年分析框架 v1 验证完成")
    print("=" * 60)


if __name__ == "__main__":
    from bazi_engine import HEAVENLY_STEMS, EARTHLY_BRANCHES, STEM_ELEMENTS, ELEMENT_NAMES, BRANCH_ELEMENTS
    test_liunian_v1()
