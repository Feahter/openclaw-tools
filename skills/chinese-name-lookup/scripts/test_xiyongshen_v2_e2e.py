#!/usr/bin/env python3
"""
喜用神 V2 端到端测试
5个核心测试用例覆盖调候/格局/月令场景
"""

import sys
from pathlib import Path

# 确保可以导入本地模块
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from bazi_engine import full_bazi_analysis, get_bazi
from xiyongshen_v2 import determine_xiyongshen_v2


# ============================================================
# 测试辅助
# ============================================================

def test_case(name: str, year: int, month: int, day: int, hour: int,
              expected_xiyong: list = None,
              expected_tiao_hou_urgent: bool = None,
              expected_pattern_cheng: str = None,
              expected_qiangruo: str = None,
              expected_tiao_hou: bool = None,
              strict: bool = False):
    """
    执行单个测试用例

    Args:
        name: 测试名称
        expected_xiyong: 期望的喜用神列表（五行）
        expected_tiao_hou_urgent: 期望的调候是否紧急
        expected_pattern_cheng: 期望的格局名称（若成格）
        expected_qiangruo: 期望的日主强弱
        expected_tiao_hou: 期望是否有调候数据
        strict: 是否严格匹配（否则只检查部分）
    """
    print(f"\n{'='*60}")
    print(f"【{name}】")
    print(f"{'='*60}")

    # Step 1: 获取八字完整分析
    bazi_full = full_bazi_analysis(year, month, day, hour)
    bazi = bazi_full["bazi"]

    print(f"  八字: {bazi_full['birth_chart']}")
    print(f"  日主: {bazi_full['rizhu_strength']['strength']} - {bazi_full['rizhu_strength']['reason']}")

    # Step 2: 调用 V2 喜用神判定
    v2_result = bazi_full["xiyongshen"]

    print(f"  V2喜用神: {v2_result['xiyongshen']}")
    print(f"  V2忌神: {v2_result['jishen']}")
    print(f"  调候紧急: {v2_result['tiao_hou_urgent']}")
    print(f"  格局: {v2_result['pattern_cheng']} ({v2_result.get('pattern_level', 'N/A')})")
    print(f"  透干级别: {v2_result.get('tou_level', 'N/A')}")
    print(f"  置信度: {v2_result['confidence']}")
    print(f"  分析: {v2_result['analysis'][:80]}...")

    # V1 对比
    v1_result = bazi_full.get("_xiyongshen_v1", {})
    if v1_result:
        print(f"  V1喜用神: {v1_result.get('xiyongshen', [])}")
        print(f"  V1忌神: {v1_result.get('jishen', [])}")

    # Step 3: 断言验证
    passed = []
    failed = []

    if expected_xiyong is not None:
        for elem in expected_xiyong:
            if elem in v2_result["xiyongshen"]:
                passed.append(f"✅ 喜用神包含「{elem}」")
            else:
                failed.append(f"❌ 喜用神应包含「{elem}」，实际：{v2_result['xiyongshen']}")

    if expected_tiao_hou_urgent is not None:
        if v2_result["tiao_hou_urgent"] == expected_tiao_hou_urgent:
            passed.append(f"✅ 调候紧急={v2_result['tiao_hou_urgent']}")
        else:
            failed.append(f"❌ 调候紧急应={expected_tiao_hou_urgent}，实际={v2_result['tiao_hou_urgent']}")

    if expected_pattern_cheng is not None:
        actual_geku = v2_result.get("pattern_cheng") or ""
        if expected_pattern_cheng in actual_geku or actual_geku in expected_pattern_cheng:
            passed.append(f"✅ 格局={actual_geku}（含「{expected_pattern_cheng}」）")
        else:
            failed.append(f"❌ 格局应含「{expected_pattern_cheng}」，实际={actual_geku}")

    if expected_qiangruo is not None:
        actual_qr = v2_result.get("qiangruo", "")
        if actual_qr == expected_qiangruo or expected_qiangruo in actual_qr:
            passed.append(f"✅ 日主{actual_qr}")
        else:
            failed.append(f"❌ 日主强弱应={expected_qiangruo}，实际={actual_qr}")

    if expected_tiao_hou is not None:
        has_tiao_hou = bool(bazi_full.get("tiao_hou", {}).get("喜用"))
        if has_tiao_hou == expected_tiao_hou:
            passed.append(f"✅ 调候数据{'有' if has_tiao_hou else '无'}")
        else:
            failed.append(f"❌ 调候数据应{'有' if expected_tiao_hou else '无'}")

    # 打印结果
    for p in passed:
        print(f"  {p}")
    for f in failed:
        print(f"  {f}")

    all_ok = len(failed) == 0
    print(f"\n  {'✅ PASS' if all_ok else '❌ FAIL'}")
    return all_ok


# ============================================================
# 测试用例
# ============================================================

def test_chengyue_han():
    """
    测试1: 辰月生人（寒湿）→ 喜火调候

    场景：2024年3月15日10点，辰月
    辰月：寒湿，本气戊土，中气乙木，余气癸水
    调候原则：辰月寒湿

    期望：
    - 调候不紧急（辰月非极寒/极热）
    - 喜用神按扶抑（身弱喜土金水）
    """
    return test_case(
        name="测试1：辰月生人（寒湿，调候不急）",
        year=2024, month=3, day=15, hour=10,
        expected_xiyong=["水", "木", "金"],  # 身弱，喜土金水，但木为调候相关
        expected_tiao_hou_urgent=False,
        expected_qiangruo="弱",
        expected_tiao_hou=True,
    )


def test_wuyue_re():
    """
    测试2: 夏月生人（热）→ 调候紧急，V2与V1差异明显

    场景：未月（燥热）或午月（热）
    未月/午月：燥热/热，调候为急

    期望：
    - 调候紧急=True
    - V2正确识别热燥
    - V2与V1喜用神有明显差异（调候优先时）
    """
    print(f"\n{'='*60}")
    print(f"【测试2：夏月生人（热/燥热，调候紧急）】")
    print(f"{'='*60}")

    # 找一个夏月（巳午未）生的八字
    # 2024年6月=未月，燥热
    # 2024年5月=午月，热
    year, month, day, hour = 2024, 5, 10, 12
    bazi_full = full_bazi_analysis(year, month, day, hour)
    bazi = bazi_full["bazi"]
    v2 = bazi_full["xiyongshen"]
    v1 = bazi_full.get("_xiyongshen_v1", {})
    tiao_hou = bazi_full.get("tiao_hou", {})

    print(f"  八字: {bazi_full['birth_chart']}")
    print(f"  日主: {bazi_full['rizhu_strength']['strength']}")
    print(f"  月令: {bazi['month']['branch']} (调候={tiao_hou.get('原则', 'N/A')})")
    print(f"  V2喜用神: {v2['xiyongshen']}")
    print(f"  V2忌神: {v2['jishen']}")
    print(f"  V1喜用神: {v1.get('xiyongshen', [])}")
    print(f"  V1忌神: {v1.get('jishen', [])}")
    print(f"  调候紧急: {v2['tiao_hou_urgent']}")
    print(f"  置信度: {v2['confidence']}")
    print(f"  分析: {v2['analysis'][:100]}...")

    passed = []
    failed = []

    # 调候紧急
    if v2['tiao_hou_urgent']:
        passed.append(f"✅ 调候紧急={v2['tiao_hou_urgent']}（夏月燥热）")
    else:
        failed.append(f"❌ 调候应紧急，实际={v2['tiao_hou_urgent']}")

    # 调候数据有
    if tiao_hou.get('喜用'):
        passed.append(f"✅ 调候数据有: 喜用={tiao_hou['喜用']}")
    else:
        failed.append(f"❌ 调候数据缺失")

    # V2处理了调候
    if v2.get('method') == 'v2_local':
        passed.append(f"✅ 使用V2算法")
    else:
        failed.append(f"❌ method={v2.get('method')}")

    # 夏月判断正确
    yue_zhi = bazi['month']['branch']
    if yue_zhi in ['巳', '午', '未']:
        passed.append(f"✅ 月令{yue_zhi}为夏月（热/燥热）")
    else:
        failed.append(f"❌ 月令{ yue_zhi}不是夏月")

    for p in passed:
        print(f"  {p}")
    for f in failed:
        print(f"  {f}")

    all_ok = len(failed) == 0
    print(f"\n  {'✅ PASS' if all_ok else '❌ FAIL'}")
    return all_ok


def test_guange_cheng():
    """
    测试3: 格局已成 → 格局信息完整

    场景：庚亥月（2024年10月1日12时）
    庚日干，亥月本气壬透出
    格局：食神格（庚日干，壬为食神）已成（中等）

    期望：
    - 格局已成
    - V2正确识别格局
    - 置信度较高（有格局加成）
    """
    return test_case(
        name="测试3：格局已成",
        year=2024, month=10, day=1, hour=12,
        expected_pattern_cheng="食神格",  # 庚亥月，食神格
        expected_qiangruo=None,  # 不强验证
        expected_tiao_hou=True,
    )


def test_shishenge():
    """
    测试4: 食神格已成 → 格局已成，置信度高

    场景：庚亥月已验证为食神格中等成格

    期望：
    - 格局level为"中等"或"上等"
    - 置信度显著高于无格局情况
    """
    print(f"\n{'='*60}")
    print(f"【测试4：食神格已成（置信度加成）】")
    print(f"{'='*60}")

    year, month, day, hour = 2024, 10, 1, 12
    bazi_full = full_bazi_analysis(year, month, day, hour)
    bazi = bazi_full["bazi"]
    v2 = bazi_full["xiyongshen"]
    cheng = bazi_full.get("pattern_cheng", {})
    pattern = bazi_full.get("pattern", {})

    print(f"  八字: {bazi_full['birth_chart']}")
    print(f"  日主: {bazi_full['rizhu_strength']['strength']}")
    print(f"  格局: {pattern.get('pattern')} {cheng.get('level')} (已成={cheng.get('is_cheng')})")
    print(f"  V2喜用神: {v2['xiyongshen']}")
    print(f"  V2忌神: {v2['jishen']}")
    print(f"  置信度: {v2['confidence']}")

    passed = []
    failed = []

    # 格局应为食神格
    if pattern.get('pattern') == '食神格':
        passed.append(f"✅ 格局=食神格")
    else:
        failed.append(f"❌ 格局应为食神格，实际={pattern.get('pattern')}")

    # 格局已成
    if cheng.get('is_cheng'):
        passed.append(f"✅ 格局已成 (level={cheng.get('level')})")
    else:
        failed.append(f"❌ 格局未成")

    # 置信度应有格局加成（> 0.5）
    if v2['confidence'] >= 0.5:
        passed.append(f"✅ 置信度={v2['confidence']}（有格局加成）")
    else:
        failed.append(f"❌ 置信度={v2['confidence']}偏低，应有格局加成")

    # V2算法使用
    if v2.get('method') == 'v2_local':
        passed.append(f"✅ 使用V2算法")
    else:
        failed.append(f"❌ method={v2.get('method')}")

    for p in passed:
        print(f"  {p}")
    for f in failed:
        print(f"  {f}")

    all_ok = len(failed) == 0
    print(f"\n  {'✅ PASS' if all_ok else '❌ FAIL'}")
    return all_ok


def test_putong_qiangruo():
    """
    测试5: 普通日主强弱 → V2与V1一致

    场景：无特殊调候/格局因素时
    V2应与V1结果基本一致

    期望：
    - V2与V1喜用神有重叠（五行层面）
    - 置信度中等（无特殊因素）
    """
    print(f"\n{'='*60}")
    print(f"【测试5：普通日主强弱（V2与V1一致性）】")
    print(f"{'='*60}")

    # 用一个普通月份
    year, month, day, hour = 2024, 4, 10, 8
    bazi_full = full_bazi_analysis(year, month, day, hour)
    bazi = bazi_full["bazi"]
    v2 = bazi_full["xiyongshen"]
    v1 = bazi_full.get("_xiyongshen_v1", {})

    print(f"  八字: {bazi_full['birth_chart']}")
    print(f"  日主: {bazi_full['rizhu_strength']['strength']}")
    print(f"  V2喜用神: {v2['xiyongshen']}")
    print(f"  V1喜用神: {v1.get('xiyongshen', [])}")
    print(f"  V2忌神: {v2['jishen']}")
    print(f"  V1忌神: {v1.get('jishen', [])}")
    print(f"  调候紧急: {v2['tiao_hou_urgent']}")
    print(f"  置信度: {v2['confidence']}")

    # 检查一致性：V2和V1喜用神至少有一个重叠五行
    v2_set = set(v2['xiyongshen'])
    v1_list = v1.get('xiyongshen', [])
    v1_set = set(v1_list)
    overlap = v2_set & v1_set

    # 检查忌神重叠
    v2_js = set(v2['jishen'])
    v1_js = set(v1.get('jishen', []))
    js_overlap = v2_js & v1_js

    passed = []
    failed = []

    if overlap:
        passed.append(f"✅ V1/V2喜用神重叠：{overlap}")
    else:
        failed.append(f"❌ V1/V2喜用神无重叠（V2={v2_set}, V1={v1_set}）")

    # 忌神也应有重叠
    if js_overlap:
        passed.append(f"✅ V1/V2忌神重叠：{js_overlap}")

    # 调候不紧急（普通月份）
    if not v2['tiao_hou_urgent']:
        passed.append(f"✅ 调候不紧急（普通月份）")
    else:
        failed.append(f"⚠️ 调候紧急（{bazi['month']['branch']}月）")

    # method = v2_local
    if v2.get('method') == 'v2_local':
        passed.append(f"✅ 使用V2算法")
    else:
        failed.append(f"❌ method={v2.get('method')}，期望v2_local")

    for p in passed:
        print(f"  {p}")
    for f in failed:
        print(f"  {f}")

    all_ok = len(failed) == 0
    print(f"\n  {'✅ PASS' if all_ok else '❌ FAIL'}")
    return all_ok


# ============================================================
# 主测试入口
# ============================================================

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  喜用神 V2 端到端测试套件")
    print("="*60)

    results = []

    results.append(("辰月生人（寒湿）", test_chengyue_han()))
    results.append(("午月生人（热）", test_wuyue_re()))
    results.append(("官格已成", test_guange_cheng()))
    results.append(("食神格", test_shishenge()))
    results.append(("普通强弱(V1一致性)", test_putong_qiangruo()))

    print("\n" + "="*60)
    print("  测试汇总")
    print("="*60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查输出")

    return all_passed


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
