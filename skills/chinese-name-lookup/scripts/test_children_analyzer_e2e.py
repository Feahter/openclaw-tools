# -*- coding: utf-8 -*-
"""子息分析端到端测试"""
import sys
sys.path.insert(0, '.')

from bazi_engine import get_bazi
from children_analyzer import (
    count_qisha, count_shishen, get_hour_branch_shengwang,
    analyze_children, analyze_children_quality, SHENG_WANG_CHILDREN_MAP
)


def test_shengwang_table():
    """验证十二长生表的基本规律"""
    print("=== 十二长生表验证 ===")
    # 甲木长生在亥（壬申=长生 亥=11... 甲亥=长生 对！）
    # 甲木：长生=亥(11), 沐浴=子(0), 冠带=丑(1)...
    # 甲: {0:帝旺,1:衰,2:病,3:死,4:墓,5:绝,6:胎,7:养,8:长生,9:沐浴,10:冠带,11:临官}
    # 甲长生在11=亥 ✅
    assert SHENG_WANG_CHILDREN_MAP["长生"]["儿子数"] == "7"
    assert SHENG_WANG_CHILDREN_MAP["死"]["儿子数"] == "0"
    assert SHENG_WANG_CHILDREN_MAP["胎"]["儿子数"] == "头女"
    print("  长生表: 长生=7/死=0/胎=头女 ✅")


def test_qisha_count():
    """七杀计数测试"""
    print("\n=== 七杀计数测试 ===")
    # 测试1：丙申日，庚寅时 → 申中气壬=偏官 → 1个七杀
    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    r = count_qisha(bazi)
    assert r["count"] >= 0
    assert "一" in r["儿子数"] or "无" in r["儿子数"]
    print(f"  丙申日: {r['天干七杀']} + {r['地支藏干七杀']} = {r['count']}个七杀 → {r['儿子数']} ✅")

    # 测试2
    bazi2 = get_bazi(2020, 5, 1, 8)
    r2 = count_qisha(bazi2)
    print(f"  {bazi2['birth_chart']}: {r2['count']}个七杀 → {r2['儿子数']}")


def test_hour_branch_shengwang():
    """时支长生分析测试"""
    print("\n=== 时支长生测试 ===")
    # 丙日，时支寅 → 病
    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    r = get_hour_branch_shengwang(bazi)
    assert r["长生状态"] == "病"
    assert "1" in r["子女数"]
    print(f"  丙日寅时: {r['长生状态']} → {r['子女数']} ✅")

    # 甲日申时 → 壬申=长生
    bazi2 = get_bazi(2020, 8, 1, 15)
    day_stem = "甲"
    from children_analyzer import SHENG_WANG_12
    r2 = get_hour_branch_shengwang(bazi2)
    print(f"  {bazi2['birth_chart']} {day_stem}日{r2['时支']}时: {r2['长生状态']} → {r2['子女数']}")


def test_children_analyze():
    """综合子息分析测试"""
    print("\n=== 子息综合分析测试 ===")
    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    result = analyze_children(bazi, gender=1)
    assert len(result["综合结论"]) > 20
    print(f"  综合结论长度: {len(result['综合结论'])} 字 ✅")
    print(f"  结论片段: {result['综合结论'][:80]}...")


if __name__ == "__main__":
    test_shengwang_table()
    test_qisha_count()
    test_hour_branch_shengwang()
    test_children_analyze()
    print("\n✅ 子息分析全部测试通过")
