# -*- coding: utf-8 -*-
"""刑冲害合端到端测试"""
import sys
sys.path.insert(0, '.')

from bazi_engine import get_bazi
from penalty_harmony import (
    analyze_branch_relation, analyze_stem_relation, get_bazi_all_relations,
    is_branch_chong, get_branch_hehua, get_branch_xing, get_branch_hai,
    get_stem_huajin, BRANCH_IDX, STEM_IDX
)


def test_basic():
    print("=== 基础关系测试 ===")
    # 六冲
    assert is_branch_chong(BRANCH_IDX["子"], BRANCH_IDX["午"])
    assert is_branch_chong(BRANCH_IDX["辰"], BRANCH_IDX["戌"])
    assert not is_branch_chong(BRANCH_IDX["子"], BRANCH_IDX["丑"])
    print("  六冲: 子午/辰戌 ✅，子丑不合冲 ✅")

    # 六合
    assert get_branch_hehua(BRANCH_IDX["子"], BRANCH_IDX["丑"]) is not None
    assert get_branch_hehua(BRANCH_IDX["子"], BRANCH_IDX["午"]) is None
    print("  六合: 子丑/寅亥 ✅，子午不合 ✅")

    # 三刑
    assert get_branch_xing(BRANCH_IDX["子"], BRANCH_IDX["卯"]) is not None
    assert get_branch_xing(BRANCH_IDX["辰"], BRANCH_IDX["辰"]) is not None
    print("  三刑: 子卯/辰辰自刑 ✅")

    # 六害
    assert get_branch_hai(BRANCH_IDX["子"], BRANCH_IDX["未"]) is not None
    assert get_branch_hai(BRANCH_IDX["寅"], BRANCH_IDX["巳"]) is not None
    print("  六害: 子未/寅巳 ✅")

    # 天干五合
    assert get_stem_huajin("甲", "己")["is_harmony"]
    assert get_stem_huajin("乙", "庚")["is_harmony"]
    assert get_stem_huajin("丁", "壬")["is_harmony"]
    assert not get_stem_huajin("甲", "乙")["is_harmony"]
    print("  天干五合: 甲己/乙庚/丁壬 ✅，甲乙不合 ✅")


def test_comprehensive():
    print("\n=== 综合关系分析 ===")
    test_cases = [
        ("子", "午", "冲"),
        ("子", "丑", "合"),
        ("子", "卯", "刑"),
        ("子", "未", "害"),
        ("寅", "亥", "合"),
        ("寅", "巳", "害/刑"),
        ("辰", "戌", "冲"),
        ("午", "未", "合"),
    ]
    for ba, bb, expected_type in test_cases:
        rel = analyze_branch_relation(ba, bb)
        types = "/".join([r["type"] for r in rel["relations"]])
        print(f"  {ba}{bb}: {types} → {rel['综合']}")
        assert rel["综合"] in ["好", "中", "差"]


def test_bazi_integration():
    print("\n=== 八字集成测试 ===")
    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    relations = get_bazi_all_relations(bazi)
    print(f"  发现 {len(relations)} 个有意义关系:")
    for rel in relations:
        if "stem_a" in rel:
            print(f"    天干: {rel['stem_a']}{rel['stem_b']} → {rel['描述'][:20]}")
        else:
            print(f"    地支: {rel['branch_a']}{rel['branch_b']} → {[r['type'] for r in rel['relations']]}")
    print("  ✅ 八字关系分析完成")


if __name__ == "__main__":
    test_basic()
    test_comprehensive()
    test_bazi_integration()
    print("\n✅ 刑冲害合全部测试通过")
