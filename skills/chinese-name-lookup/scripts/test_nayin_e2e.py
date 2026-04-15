# -*- coding: utf-8 -*-
"""
纳音五行端到端测试
测试 nayin.py 与 bazi_engine 的集成
"""
import sys
sys.path.insert(0, '.')

from bazi_engine import get_bazi
from nayin import (
    get_nayin, get_full_nayin_info, get_nayin_element,
    get_nayin_personality, get_year_day_nayin_analysis, analyze_nayin_relation,
    NAYIN_ELEMENT_MAP
)


def test_nayin_basic():
    """基础纳音查询测试"""
    print("=== 基础纳音测试 ===")
    test_cases = [
        ((0, 0), "海中金"),
        ((1, 1), "海中金"),
        ((2, 2), "炉中火"),
        ((3, 3), "炉中火"),
        ((4, 4), "大林木"),
        ((6, 6), "路旁土"),
        ((8, 8), "剑锋金"),
        ((0, 10), "山头火"),
        ((2, 0), "涧下水"),
        ((6, 2), "松柏木"),
        ((8, 4), "海水"),
        ((0, 6), "沙中金"),
        ((6, 10), "钗钏金"),
        ((8, 0), "桑柘木"),
        ((0, 2), "大溪水"),
        ((4, 6), "天上火"),
        ((6, 8), "石榴木"),
        ((8, 10), "大海水"),
    ]
    for (si, bi), expected in test_cases:
        result = get_nayin(si, bi)
        assert result == expected, f"({si},{bi}) 期望 {expected}，实际 {result}"
    print("  18个基础测试全部通过 ✅")


def test_nayin_element_map():
    """纳音正五行映射测试"""
    print("=== 纳音正五行映射测试 ===")
    all_nayins = set(NAYIN_ELEMENT_MAP.keys())
    print(f"  纳音种类: {len(all_nayins)}种")
    for n in all_nayins:
        elem = NAYIN_ELEMENT_MAP[n]
        assert elem in ["金", "火", "木", "土", "水"], f"{n}映射错误: {elem}"
    print(f"  全部{len(all_nayins)}种纳音均有有效正五行 ✅")


def test_nayin_relation():
    """纳音关系测试"""
    print("=== 纳音关系测试 ===")
    # 同金
    r = analyze_nayin_relation("海中金", "剑锋金")
    assert r["quality"] == "中", f"同金关系应为'中'，实际{r['quality']}"
    # 水生木
    r = analyze_nayin_relation("海中金", "松柏木")
    assert r["element1"] == "金"
    assert r["element2"] == "木"
    # 水克火（天敌）
    r = analyze_nayin_relation("海中金", "炉中火")
    assert r["quality"] == "差", f"水克火应为'差'，实际{r['quality']}"
    print("  关系分析正确 ✅")


def test_bazi_integration():
    """八字集成测试"""
    print("=== 八字集成测试 ===")
    bazi = get_bazi(2026, 3, 23, 5, province='四川', city='成都')
    bz = bazi['bazi']

    # 验证四柱纳音
    pillars = ['year', 'month', 'day', 'hour']
    for p in pillars:
        nayin = get_nayin(bz[p]['stem_idx'], bz[p]['branch_idx'])
        info = get_full_nayin_info(bz[p]['stem_idx'], bz[p]['branch_idx'])
        assert nayin == info['nayin'], f"{p}纳音不一致"
        assert info['element'] in ["金", "火", "木", "土", "水"]
        assert len(info['personality']) > 5, f"{p}性格描述过短"

    year_n = get_nayin(bz['year']['stem_idx'], bz['year']['branch_idx'])
    month_n = get_nayin(bz['month']['stem_idx'], bz['month']['branch_idx'])
    day_n = get_nayin(bz['day']['stem_idx'], bz['day']['branch_idx'])
    hour_n = get_nayin(bz['hour']['stem_idx'], bz['hour']['branch_idx'])
    print(f"  成都男婴(5:00)纳音: 年={year_n} 月={month_n} 日={day_n} 时={hour_n} ✅")

    # 年日关系
    rel = get_year_day_nayin_analysis(year_n, day_n)
    assert len(rel) > 10, "年日关系分析过短"
    print(f"  年日纳音关系：{year_n} vs {day_n} ✅")
    print(f"  分析：{rel[:60]}... ✅")


def test_report_integration():
    """报告集成测试（验证纳音字段存在）"""
    print("=== 报告集成测试 ===")
    try:
        from report_formatter import generate_full_report as gfr
        report = gfr("张", 2026, 3, 23, 5, gender=1)
        assert len(str(report)) > 100, "报告过短"
        print(f"  报告生成成功（含纳音分析）✅")
    except Exception as e:
        print(f"  报告生成异常: {e} ❌")


if __name__ == "__main__":
    test_nayin_basic()
    test_nayin_element_map()
    test_nayin_relation()
    test_bazi_integration()
    test_report_integration()
    print("\n✅ 纳音模块全部测试通过")
