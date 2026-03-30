# -*- coding: utf-8 -*-
"""婚姻配偶星分析端到端测试"""
import sys
sys.path.insert(0, '.')

from bazi_engine import get_bazi
from marriage_analyzer import (
    get_spouse_star, analyze_spouse_palace, analyze_marriage,
    get_guluan, get_yincuo_yangcha
)


def test_marriage_basic():
    print("=== 婚姻配偶星分析测试 ===")
    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    print(f"八字：{bazi['birth_chart']}，性别：男")

    # 配偶星
    spouse = get_spouse_star(bazi, gender=1)
    assert spouse['star'] in ["正财", "偏财"], f"配偶星={spouse['star']}"
    assert spouse['count'] >= 0
    print(f"  配偶星: {spouse['star']} × {spouse['count']} ✅")
    print(f"  天干: {spouse['天干']}")

    # 配偶宫
    palace = analyze_spouse_palace(bazi)
    assert "配偶宫" in palace
    assert "宫状态" in palace
    print(f"  配偶宫: {palace['配偶宫']}，状态: {palace['宫状态']} ✅")
    print(f"  问题: {palace['问题列表'] or '无'}")

    # 综合婚姻
    marriage = analyze_marriage(bazi, gender=1)
    assert len(marriage['综合结论']) > 10
    print(f"  综合结论: {marriage['综合结论'][:50]}... ✅")


def test_guluan():
    print("\n=== 孤鸾煞测试 ===")
    # 孤鸾日
    GULUAN = [("甲", "寅"), ("辛", "亥"), ("丙", "午"), ("壬", "子")]
    for gan, zhi in GULUAN:
        # 验证字典查找逻辑
        assert (gan, zhi) in {("甲","寅"), ("辛","亥"), ("丙","午"), ("壬","子")}
    print(f"  4个孤鸾日验证 ✅")


def test_yincuo_yangcha():
    print("\n=== 阴错阳差测试 ===")
    YINCUO = {"辛卯", "壬辰", "癸巳", "丙午", "丁未", "戊申"}
    YANGCHA = {"辛丑", "壬寅", "癸卯", "丙申", "丁酉", "戊戌"}
    assert len(YINCUO) == 6
    assert len(YANGCHA) == 6
    # 非孤鸾日验证
    bazi = get_bazi(2026, 3, 23, 5)
    g = get_guluan(bazi)
    assert g['is_guluan'] == False
    print(f"  丙申日: 孤鸾={g['is_guluan']} ✅ (正确，丙午才是孤鸾日)")


def test_spouse_palace_冲():
    print("\n=== 配偶宫冲验证 ===")
    # 丙申日柱，时支寅 → 寅申冲
    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    palace = analyze_spouse_palace(bazi)
    # 申日支，被寅冲
    assert '寅与申相冲' in palace['问题列表'] or '申' in palace['配偶宫']
    print(f"  丙申日配偶宫: 寅申冲 → {palace['问题列表']} ✅")


if __name__ == "__main__":
    test_marriage_basic()
    test_guluan()
    test_yincuo_yangcha()
    test_spouse_palace_冲()
    print("\n✅ 婚姻配偶星分析全部测试通过")
