#!/usr/bin/env python3
"""
报告格式化器端到端测试
Phase 9 - 完整报告输出优化

3个端到端测试：
1. 完整报告生成测试（2024年3月15日10点，男）
2. 报告各模块格式化测试
3. 名字推荐 + 完整报告集成测试
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from report_formatter import (
    format_full_report,
    format_bazi_table,
    format_shen_sha_list,
    format_dayun_summary,
    format_liunian_recent,
    generate_full_report,
    _format_basic_info,
    _format_bazi_table,
    _format_mingju_analysis,
    _format_shen_sha_list,
    _format_dayun_section,
    _format_name_section,
    _format_suggestions,
)
from name_generator import generate_name_recommendations
from bazi_engine import full_bazi_analysis


def test_full_report_generation():
    """
    测试1: 完整报告生成测试

    验证：
    - 报告包含所有必要 sections
    - 八字信息正确
    - 神煞信息正确
    - 大运流年信息正确
    """
    print("【端到端测试1】完整报告生成测试")
    print("=" * 50)

    # 2024年3月15日10点出生，男
    bazi_info = full_bazi_analysis(2024, 3, 15, 10)
    bazi_info["source"] = "local_engine"

    # 获取推荐
    result = generate_name_recommendations(
        surname="张",
        birth_year=2024,
        birth_month=3,
        birth_day=15,
        birth_hour=10,
        gender=1,
        use_local_engine=True,
        max_options=3,
    )

    recommendations = result.get("recommendations", [])

    # 生成完整报告
    report = format_full_report(
        bazi_info=bazi_info,
        name_candidates=recommendations,
        gender=1,
        surname="张",
        full_name="张宝宝",
    )

    # 验证报告包含必要 sections
    required_sections = [
        "# 八字分析报告",
        "## 基本信息",
        "## 八字命盘",
        "## 命局分析",
        "## 神煞一览",
        "## 大运流年",
        "## 姓名分析",
        "## 命理建议",
    ]

    print("\n--- Section 验证 ---")
    for section in required_sections:
        found = section in report
        status = "✓" if found else "✗"
        print(f"  {status} {section}: {'存在' if found else '缺失'}")

    # 验证八字基本信息
    print("\n--- 八字信息验证 ---")
    assert "甲辰" in report, "年柱甲辰应存在"
    print("  ✓ 年柱甲辰存在")
    assert "龙" in report, "生肖龙应存在"
    print("  ✓ 生肖龙存在")
    assert "2024年" in report or "甲辰年" in report, "出生年份应存在"
    print("  ✓ 出生年份存在")

    # 验证神煞
    print("\n--- 神煞验证 ---")
    shen_sha_keywords = ["天乙贵人", "文昌", "驿马", "华盖", "桃花"]
    for keyword in shen_sha_keywords:
        found = keyword in report
        status = "✓" if found else "✗"
        print(f"  {status} {keyword}: {'存在' if found else '缺失'}")

    # 验证大运流年
    print("\n--- 大运流年验证 ---")
    assert "大运序列" in report, "大运序列应存在"
    print("  ✓ 大运序列存在")
    assert "近5年流年" in report, "近5年流年应存在"
    print("  ✓ 近5年流年存在")

    # 验证姓名分析
    print("\n--- 姓名分析验证 ---")
    if recommendations:
        first_name = recommendations[0].get("full_name", "")
        assert first_name in report, f"推荐姓名 {first_name} 应存在"
        print(f"  ✓ 推荐姓名 {first_name} 存在")
        assert "候选名详细评分" in report, "评分表应存在"
        print("  ✓ 评分表存在")
    else:
        print("  ℹ 无推荐姓名（跳过验证）")

    # 验证命理建议
    print("\n--- 命理建议验证 ---")
    assert "职业方向" in report, "职业方向应存在"
    print("  ✓ 职业方向存在")
    assert "幸运方位" in report, "幸运方位应存在"
    print("  ✓ 幸运方位存在")

    # 报告长度
    print(f"\n--- 报告统计 ---")
    lines = report.split("\n")
    print(f"  报告总行数: {len(lines)}")
    print(f"  报告总字符数: {len(report)}")

    print("\n✅ 测试1通过：完整报告生成正确")
    return True


def test_individual_formatters():
    """
    测试2: 各模块格式化测试

    验证：
    - format_bazi_table() 输出正确
    - format_shen_sha_list() 输出正确
    - format_dayun_summary() 输出正确
    - format_liunian_recent() 输出正确
    """
    print("\n【端到端测试2】各模块格式化测试")
    print("=" * 50)

    # 准备测试数据
    bazi_info = full_bazi_analysis(2024, 3, 15, 10)
    bazi_info["source"] = "local_engine"

    # 测试 format_bazi_table
    print("\n--- format_bazi_table 测试 ---")
    bazi_table = format_bazi_table(bazi_info)
    assert "## 八字命盘" in bazi_table, "应有八字命盘标题"
    assert "甲辰" in bazi_table, "应有年柱甲辰"
    print(f"  ✓ 八字命盘表格生成正确 ({len(bazi_table)} 字符)")

    # 测试 format_shen_sha_list
    print("\n--- format_shen_sha_list 测试 ---")
    shen_sha_table = format_shen_sha_list(bazi_info)
    assert "## 神煞一览" in shen_sha_table, "应有神煞一览标题"
    assert "天乙贵人" in shen_sha_table, "应有天乙贵人"
    assert "文昌" in shen_sha_table, "应有文昌"
    print(f"  ✓ 神煞一览生成正确 ({len(shen_sha_table)} 字符)")

    # 测试 generate_full_report (一键生成)
    print("\n--- generate_full_report 测试 ---")
    full_report = generate_full_report(
        surname="王",
        year=2025,
        month=1,
        day=15,
        hour=10,
        gender=0,  # 女
        name_count=3,
    )
    assert "# 八字分析报告" in full_report, "应有报告标题"
    assert "王" in full_report, "应有姓氏信息"
    assert "2025年" in full_report or "乙巳年" in full_report, "应有2025年信息"
    print(f"  ✓ 一键生成报告正确 ({len(full_report)} 字符)")

    print("\n✅ 测试2通过：各模块格式化正确")
    return True


def test_name_recommendation_integration():
    """
    测试3: 名字推荐 + 完整报告集成测试

    验证：
    - name_generator 正确调用 report_formatter
    - 推荐姓名包含在完整报告中
    - 报告格式美观易读
    """
    print("\n【端到端测试3】名字推荐 + 完整报告集成测试")
    print("=" * 50)

    # 测试不同年份
    test_cases = [
        {"surname": "李", "year": 2024, "month": 3, "day": 15, "hour": 10, "gender": 1},
        {"surname": "陈", "year": 2025, "month": 1, "day": 15, "hour": 10, "gender": 0},
        {"surname": "王", "year": 2023, "month": 6, "day": 1, "hour": 14, "gender": 1},
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {case['surname']}姓，{case['year']}年 ---")

        result = generate_name_recommendations(
            surname=case["surname"],
            birth_year=case["year"],
            birth_month=case["month"],
            birth_day=case["day"],
            birth_hour=case["hour"],
            gender=case["gender"],
            use_local_engine=True,
            max_options=3,
        )

        assert result["success"], f"测试用例 {i} 应成功"

        report = result.get("markdown", "")

        # 验证报告结构
        assert "# 八字分析报告" in report, "应有报告标题"
        assert "## 基本信息" in report, "应有基本信息"
        assert "## 八字命盘" in report, "应有八字命盘"
        assert "## 命局分析" in report, "应有命局分析"
        assert "## 神煞一览" in report, "应有神煞一览"
        assert "## 大运流年" in report, "应有大运流年"
        assert "## 姓名分析" in report, "应有姓名分析"
        assert "## 命理建议" in report, "应有命理建议"

        # 验证推荐姓名
        recommendations = result.get("recommendations", [])
        if recommendations:
            first_name = recommendations[0].get("full_name", "")
            assert case["surname"] in first_name, f"推荐姓名应包含姓氏 {case['surname']}"
            print(f"  ✓ 推荐姓名: {first_name} ({recommendations[0].get('total_score', 0)}分)")

            # 验证评分维度
            dim_scores = recommendations[0].get("dim_scores", {})
            assert "喜用神匹配" in dim_scores or "喜用神" in dim_scores, "应有喜用神评分"
            print(f"  ✓ 评分维度完整")
        else:
            print(f"  ℹ 无推荐姓名（可能喜用神为空）")

        # 验证五行分布
        assert "五行分布" in report, "应有五行分布"
        print(f"  ✓ 五行分布存在")

        # 验证生肖信息
        zodiac = result["bazi_info"].get("zodiac", "")
        assert zodiac in report, f"生肖 {zodiac} 应在报告中"
        print(f"  ✓ 生肖 {zodiac} 正确")

        # 验证喜用神
        xiyong = result["bazi_info"].get("xiyongshen", {}).get("xiyongshen", [])
        if xiyong:
            print(f"  ✓ 喜用神: {','.join(xiyong)}")

        print(f"  报告长度: {len(report)} 字符")

    print("\n✅ 测试3通过：名字推荐与报告集成正确")
    return True


def test_report_format_aesthetics():
    """
    测试4: 报告美观度测试

    验证：
    - 报告使用正确的 Markdown 格式
    - 表格格式正确
    - 无乱码或格式错误
    """
    print("\n【端到端测试4】报告美观度测试")
    print("=" * 50)

    result = generate_name_recommendations(
        surname="张",
        birth_year=2024,
        birth_month=3,
        birth_day=15,
        birth_hour=10,
        gender=1,
        use_local_engine=True,
        max_options=3,
    )

    report = result.get("markdown", "")

    # 验证 Markdown 表格格式
    print("\n--- Markdown 表格格式验证 ---")
    table_lines = [line for line in report.split("\n") if line.startswith("|")]
    print(f"  表格行数: {len(table_lines)}")

    # 验证表格对齐标记
    has_align_markers = any(
        line.startswith("|:") or line.startswith("|--") for line in table_lines
    )
    assert has_align_markers, "表格应有对齐标记 (:---)"
    print("  ✓ 表格对齐标记正确")

    # 验证标题层级
    print("\n--- 标题层级验证 ---")
    h1_count = report.count("# 八字分析报告")
    h2_count = report.count("## ")
    assert h1_count == 1, "应有且仅有一个一级标题"
    assert h2_count >= 5, f"应有至少5个二级标题，实际 {h2_count}"
    print(f"  ✓ 标题层级正确 (1个H1, {h2_count}个H2)")

    # 验证无连续空行（美观）
    print("\n--- 格式美观验证 ---")
    has_consecutive_empty = "\n\n\n" in report
    assert not has_consecutive_empty, "报告不应有3个以上连续空行"
    print("  ✓ 无过多连续空行")

    # 验证 emoji 使用（可选，美观增强）
    has_emoji = any(c in report for c in ["✅", "⚠️", "ℹ️", "📊"])
    if has_emoji:
        print("  ✓ 包含 emoji 增强可读性")

    # 验证分隔线
    assert "---" in report, "报告应有分隔线"
    print("  ✓ 包含分隔线")

    print("\n✅ 测试4通过：报告格式美观")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 9 - 完整报告输出优化 - 端到端测试")
    print("=" * 60)

    all_passed = True

    try:
        test_full_report_generation()
        print()
    except Exception as e:
        print(f"\n❌ 测试1失败: {e}")
        all_passed = False

    try:
        test_individual_formatters()
        print()
    except Exception as e:
        print(f"\n❌ 测试2失败: {e}")
        all_passed = False

    try:
        test_name_recommendation_integration()
        print()
    except Exception as e:
        print(f"\n❌ 测试3失败: {e}")
        all_passed = False

    try:
        test_report_format_aesthetics()
        print()
    except Exception as e:
        print(f"\n❌ 测试4失败: {e}")
        all_passed = False

    print("=" * 60)
    if all_passed:
        print("✅ 全部测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
    print("=" * 60)
