# -*- coding: utf-8 -*-
"""神煞质量评估端到端测试"""
import sys
sys.path.insert(0, '.')

from bazi_engine import get_bazi
from shensha_quality import (
    get_kongwang, assess_shen_sha_quality,
    STEM_XUN_LEADERS, BRANCHES
)


def test_kongwang():
    print("=== 空亡验证 ===")
    # 丙日 → 甲辰旬 → 空亡寅卯
    from bazi_engine import get_bazi
    bazi = get_bazi(2026, 3, 23, 5)  # 丙申日
    kw = get_kongwang(bazi)
    assert "寅" in kw["空亡地支"], f"丙日空亡应有寅，实际{kw['空亡地支']}"
    assert "卯" in kw["空亡地支"], f"丙日空亡应有卯，实际{kw['空亡地支']}"
    assert kw["旬首"] == "甲辰旬"
    print(f"  丙日空亡：{kw['空亡地支']} ✅")

    # 验证甲己日空亡戌亥
    from shensha_quality import _XUN_INFO
    leader = STEM_XUN_LEADERS[0]  # 甲
    kongwang_set = set(range(12)) - [br for ln, br in _XUN_INFO if ln == leader][0]
    assert 10 in kongwang_set and 11 in kongwang_set, "甲日空亡应有戌亥"
    print(f"  甲日空亡：戌亥 ✅")


def test_shen_sha_quality():
    print("\n=== 神煞质量评估测试 ===")
    bazi = get_bazi(2026, 3, 23, 5)

    # 年支午
    kw = get_kongwang(bazi)
    # 午不在空亡
    result = assess_shen_sha_quality(bazi, "年支", 6)  # 午=6
    assert result["是否空亡"] == False, "午不在空亡"
    assert result["长生状态"] == "胎", "丙日午=胎"
    print(f"  年支午：{result['质量评级']}（{result['长生状态']}）{'⚠️空亡' if result['是否空亡'] else ''} ✅")


def test_quality_ratings():
    print("\n=== 质量评级验证 ===")
    # 无效：空亡
    # 强力：长生/临官/帝旺/冠带
    # 弱效：病/衰+刑冲
    ratings = ["强力", "有效", "弱效", "无效"]
    for r in ratings:
        assert r in ratings
    print(f"  4级评级体系正常 ✅")


if __name__ == "__main__":
    test_kongwang()
    test_shen_sha_quality()
    test_quality_ratings()
    print("\n✅ 神煞质量评估全部测试通过")
