#!/usr/bin/env python3
"""
日柱回归测试 — 用已知锚点防止 JDN 公式退化

锚点来源：用户万年历（2026-03-29 交叉验证）
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from bazi_engine import get_day_stem_branch

STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

ANCHORS = [
    # (year, month, day, expected_stem_branch, note)
    (2000,  1,  1, '戊午', 'BASE锚点：2000-01-01'),
    (2026,  3, 22, '乙未', '用户万年历验证 2026-03-22'),
    (2026,  3, 23, '丙申', '用户万年历验证 2026-03-23（成都05:00出生日期）'),
    (2026,  3, 24, '丁酉', '用户万年历验证 2026-03-24'),
]

def test_day_stem_branch():
    failed = 0
    for y, m, d, expected, note in ANCHORS:
        s, b = get_day_stem_branch(y, m, d)
        result = STEMS[s] + BRANCHES[b]
        ok = result == expected
        status = '✅' if ok else '❌'
        print(f"  {y}-{m:02d}-{d:02d}: {result} (exp:{expected}) {status} | {note}")
        if not ok:
            failed += 1
    print()
    if failed:
        print(f"❌ {failed}/{len(ANCHORS)} 失败 — JDN 公式已退化！")
        sys.exit(1)
    else:
        print(f"✅ 全部 {len(ANCHORS)} 个锚点通过")
        sys.exit(0)

if __name__ == '__main__':
    test_day_stem_branch()
