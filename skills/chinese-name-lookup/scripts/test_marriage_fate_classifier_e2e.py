# -*- coding: utf-8 -*-
"""女命婚姻贵贱格局分类测试"""
import sys
sys.path.insert(0, '.')

from bazi_engine import get_bazi
from marriage_fate_classifier import classify_female_marriage_fate, is_guan_sha_混杂


def test_female_fate():
    print("=== 女命婚姻格局测试 ===")
    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    result = classify_female_marriage_fate(bazi)

    assert result["category"] in ["富贵", "平常", "贫贱", "中上"]
    assert 0 <= result["score"] <= 100
    assert isinstance(result["matching_patterns"], list)
    assert isinstance(result["violating_patterns"], list)
    assert len(result["analysis"]) > 5

    print(f"  分类: {result['category']}（{result['score']}/100）✅")
    print(f"  富贵: {result['matching_patterns'] or '无'}")
    print(f"  不利: {result['violating_patterns'] or '无'}")


def test_guan_sha_混杂():
    print("\n=== 官杀混杂检测 ===")
    bazi = get_bazi(2026, 3, 23, 5)
    mixed = is_guan_sha_混杂(bazi)
    print(f"  丙申日: 官杀混杂={mixed} ✅")


if __name__ == "__main__":
    test_female_fate()
    test_guan_sha_混杂()
    print("\n✅ 女命婚姻格局全部测试通过")
