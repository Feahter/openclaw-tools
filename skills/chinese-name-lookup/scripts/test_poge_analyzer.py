#!/usr/bin/env python3
"""
破格原因分析测试用例
测试 6 种破格类型 + 格局不成

运行方式：
    cd scripts/
    python test_poge_analyzer.py
"""

import sys
from pathlib import Path

# 确保可以导入本地模块（绕过 bazi_engine 的循环导入问题）
sys.path.insert(0, str(Path(__file__).parent))

from pattern_method import (
    determine_pattern, judge_pattern_cheng,
    HEAVENLY_STEMS, EARTHLY_BRANCHES, SHISHEN_TABLE,
)
from poge_analyzer import (
    analyze_poge_reasons, POGE_SHANGGUAN, POGE_CAISHUAI_YIN,
    POGE_GUANSHA_KESSHEN, POGE_BIJIE_ZHENCAI,
)


# ============================================================
# 测试数据构造辅助
# ============================================================

def make_bazi(ys, yb, ms, mb, ds, db, hs, hb):
    """用天干地支索引构造八字字典"""
    return {
        "year":  {"stem": HEAVENLY_STEMS[ys],  "branch": EARTHLY_BRANCHES[yb],
                  "stem_idx": ys,  "branch_idx": yb},
        "month": {"stem": HEAVENLY_STEMS[ms], "branch": EARTHLY_BRANCHES[mb],
                  "stem_idx": ms, "branch_idx": mb},
        "day":   {"stem": HEAVENLY_STEMS[ds],   "branch": EARTHLY_BRANCHES[db],
                  "stem_idx": ds,   "branch_idx": db},
        "hour":  {"stem": HEAVENLY_STEMS[hs],  "branch": EARTHLY_BRANCHES[hb],
                  "stem_idx": hs,  "branch_idx": hb},
    }


def get_shis(bazi_dict):
    """获取四柱十神"""
    day_idx = bazi_dict["day"]["stem_idx"]
    return [
        SHISHEN_TABLE[day_idx][bazi_dict["year"]["stem_idx"]],
        SHISHEN_TABLE[day_idx][bazi_dict["month"]["stem_idx"]],
        SHISHEN_TABLE[day_idx][bazi_dict["day"]["stem_idx"]],
        SHISHEN_TABLE[day_idx][bazi_dict["hour"]["stem_idx"]],
    ]


def format_bazi(b):
    """格式化八字为字符串"""
    return (f"{b['year']['stem']}{b['year']['branch']} "
            f"{b['month']['stem']}{b['month']['branch']} "
            f"{b['day']['stem']}{b['day']['branch']} "
            f"{b['hour']['stem']}{b['hour']['branch']}")


# ============================================================
# 测试用例定义
# ============================================================

# 测试用例：(年干索引, 年支索引, 月干索引, 月支索引, 日干索引, 日支索引, 时干索引, 时支索引)
#           对应八字
#           破格类型/格局, 期望 poge_type, 期望 is_broken, 描述
TEST_CASES = [
    # -------------------------------------------------------------------------
    # 1. 伤官见官破格
    # 庚戌年 己辰月 丙巳日 癸午时
    # 月令辰本气戊土, 中气乙木, 余气癸水
    # 月干己=伤官(丙日己=伤官), 月令中气乙透=正官 → 正官格
    # 时干癸=正印, 伤官见官 → 破格
    # -------------------------------------------------------------------------
    dict(year_idx=6, year_zhi=10, month_idx=5, month_zhi=4,
         day_idx=2, day_zhi=5, hour_idx=9, hour_zhi=6,
         poge_type=POGE_SHANGGUAN, is_broken=True,
         desc="正官格 + 伤官透干 → 伤官见官破格"),

    # -------------------------------------------------------------------------
    # 2. 财星坏印破格
    # 庚申年 丁子月 甲卯日 己午时
    # 月令子本气癸水, 癸对甲=正印 → 正印格
    # 时干己=正财(甲日己=正财), 财克印 → 财星坏印
    # -------------------------------------------------------------------------
    dict(year_idx=6, year_zhi=8, month_idx=3, month_zhi=0,
         day_idx=0, day_zhi=3, hour_idx=5, hour_zhi=6,
         poge_type=POGE_CAISHUAI_YIN, is_broken=True,
         desc="正印格 + 财星透干 → 财星坏印破格"),

    # -------------------------------------------------------------------------
    # 3. 官杀克身为破
    # 癸丑年 丙巳月 癸辰日 丁午时
    # 月令巳本气丙火, 丙对癸=正官 → 正官格
    # 癸日在巳月失令(病地), 身弱官旺, 比劫透干, 无印化 → 官杀克身
    # -------------------------------------------------------------------------
    dict(year_idx=9, year_zhi=1, month_idx=2, month_zhi=5,
         day_idx=9, day_zhi=4, hour_idx=3, hour_zhi=6,
         poge_type=POGE_GUANSHA_KESSHEN, is_broken=True,
         desc="正官格 + 身弱无印化 + 比劫透干 → 官杀克身破格"),

    # -------------------------------------------------------------------------
    # 4. 格局不成（无破但也不成）
    # 辛戌年 壬巳月 壬巳日 乙午时
    # 月令巳本气丙火, 中气庚金, 余气戊土
    # 月干壬水, 壬对壬=比肩 → 比肩格
    # 月令本气丙不透, 中气庚不透, 余气戊不透 → 无透干
    # 格局下等但非破格
    # -------------------------------------------------------------------------
    dict(year_idx=7, year_zhi=10, month_idx=8, month_zhi=5,
         day_idx=8, day_zhi=5, hour_idx=1, hour_zhi=6,
         poge_type="格局不成", is_broken=False,
         desc="偏官格(无透) + 下等不成格 → 格局不成"),

    # -------------------------------------------------------------------------
    # 5. 比劫争财破格
    # 甲寅年 丙卯月 己戌日 己午时
    # 月令卯本气乙, 中气甲, 余气癸
    # 月干丙=食神(己日丙=食神) → 非财格
    # Wait... let me re-check
    # 甲寅年(0,2), 丙卯月(2,3), 己戌日(5,10), 己午时(5,6)
    # 月令卯本气乙, 己日干乙=正官? no, 己日干乙=正官 → 正官格
    # shis=['正财','正印','比肩','比肩']
    # 正官格, 无正官? wait 正印! 月令本气乙透?
    # 月干丙, 丙=食神(己日丙=食神), 月令本气乙不透
    # 中气甲=食神? 己日干甲=伤官
    # 这个八字的正官格需要重新验证

    # Let's use a simpler one: 甲寅年 丙卯月 己戌日 己午时
    # 月令卯本气乙(正官), 己日干乙=正官 → 正官格
    # Wait: 甲寅年 丙卯月 己戌日 己午时
    # day_idx=5=己, year_idx=0=甲
    # 甲日干己=正财? no: 己日干, 丙=食神, 丁=伤官, 戊=偏财, 己=正财, 庚=偏官, 辛=正官, 壬=偏印, 癸=正印, 甲=比肩, 乙=劫财
    # 月令卯本气乙, 乙对己=劫财 → 劫财格
    # shis: 年干甲=劫财, 月干丙=食神, 日干己=正财, 时干己=正财
    # 劫财格 + 财星 = 比劫争财 ✓

    # Actually let me use the found case: 甲寅年 丙卯月 己戌日 己午时
    # 月令卯: 本气乙, 中气甲, 余气无
    # 己日干: 乙=正官? no, 己日干, 乙=正官... wait:
    # 己日干: 甲=偏财, 乙=正财, 丙=食神, 丁=伤官, 戊=偏财, 己=比肩, 庚=劫财, 辛=偏印, 壬=正印, 癸=正印
    # 月令本气乙=正财 → 正财格 ✓
    # shis: 年干甲=正财, 月干丙=食神, 日干己=比肩, 时干己=比肩
    # 比肩×2 → 比劫争财 ✓
    # level=破格 ✓
    # -------------------------------------------------------------------------
    dict(year_idx=0, year_zhi=2, month_idx=2, month_zhi=3,
         day_idx=5, day_zhi=10, hour_idx=5, hour_zhi=6,
         poge_type=POGE_BIJIE_ZHENCAI, is_broken=True,
         desc="正财格 + 比劫透干 → 比劫争财破格"),

    # -------------------------------------------------------------------------
    # 6. 印星太重破格
    # 甲子年 甲寅月 丙子日 甲子时
    # 月令寅本气甲, 丙日干甲=偏印 → 偏印格
    # 年干甲=偏印, 月干甲=偏印, 时干甲=偏印 → 偏印×3
    # 无食伤, 无官杀 → 印星太重
    # -------------------------------------------------------------------------
    dict(year_idx=0, year_zhi=0, month_idx=0, month_zhi=2,
         day_idx=2, day_zhi=0, hour_idx=0, hour_zhi=0,
         poge_type="印星太重", is_broken=True,
         desc="偏印格 + 印星三重无泄 → 印星太重破格"),
]


# ============================================================
# 运行单个测试
# ============================================================

def run_test(tc):
    bazi = make_bazi(
        tc["year_idx"], tc["year_zhi"],
        tc["month_idx"], tc["month_zhi"],
        tc["day_idx"], tc["day_zhi"],
        tc["hour_idx"], tc["hour_zhi"],
    )

    pattern_info = determine_pattern(bazi)
    cheng_info = judge_pattern_cheng(pattern_info["pattern"], bazi, pattern_info)
    poge_result = analyze_poge_reasons(bazi, cheng_info)

    shis = get_shis(bazi)

    ok_type = poge_result["poge_type"] == tc["poge_type"]
    ok_broken = poge_result["is_broken"] == tc["is_broken"]

    status = "PASS" if (ok_type and ok_broken) else "FAIL"

    print(f"\n{'='*55}")
    print(f"[{status}] {tc['desc']}")
    print(f"  八字: {format_bazi(bazi)}")
    print(f"  十神: {shis}")
    print(f"  格局: {pattern_info['pattern']} ({pattern_info['tou_level']})")
    print(f"  成败: {cheng_info['level']} | is_cheng={cheng_info['is_cheng']}")
    print(f"  --- 破格分析 ---")
    print(f"  is_broken:  expected={tc['is_broken']}  got={poge_result['is_broken']}")
    print(f"  poge_type:  expected={tc['poge_type']}  got={poge_result['poge_type']}")
    if poge_result['poge_reason']:
        print(f"  poge_reason: {poge_result['poge_reason']}")
    if poge_result['poge_stars']:
        print(f"  poge_stars: {poge_result['poge_stars']}")
    if not ok_type:
        print(f"  ❌ FAIL: poge_type mismatch")
    if not ok_broken:
        print(f"  ❌ FAIL: is_broken mismatch")

    return ok_type and ok_broken


# ============================================================
# 主入口
# ============================================================

def main():
    print("=" * 55)
    print("  破格原因分析测试套件")
    print("  feat(chinese-name-lookup): 破格原因识别")
    print("=" * 55)

    results = []
    for tc in TEST_CASES:
        results.append((tc["desc"], run_test(tc)))

    # 汇总
    print("\n" + "=" * 55)
    print("  测试结果汇总")
    print("=" * 55)

    all_pass = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")
        if not passed:
            all_pass = False

    print()
    if all_pass:
        print("  🎉 所有测试通过！")
    else:
        print("  ⚠️  部分测试失败，请检查逻辑")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
