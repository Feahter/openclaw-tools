# -*- coding: utf-8 -*-
"""
十二地支藏干表（月令藏干）
月令（出生月份地支）的本气、中气、余气

数据来源：《子平真诠》《三命通会》
地支藏人元，以本气为主，中气次之，余气又次之。
"""

# 地支索引映射
ZHI_IDX = {
    "子": 0, "丑": 1, "寅": 2, "卯": 3, "辰": 4,
    "巳": 5, "午": 6, "未": 7, "申": 8, "酉": 9,
    "戌": 10, "亥": 11
}

# 十二地支藏干表
# 本气：地支主要五行所含天干
# 中气：本气所生之天干
# 余气：本气所克/泄之天干
YUELING_CANGGAN = {
    "子": {"本气": "癸", "中气": "壬", "余气": None},
    "丑": {"本气": "己", "中气": "癸", "余气": "辛"},
    "寅": {"本气": "甲", "中气": "丙", "余气": "戊"},
    "卯": {"本气": "乙", "中气": "甲", "余气": None},
    "辰": {"本气": "戊", "中气": "乙", "余气": "癸"},
    "巳": {"本气": "丙", "中气": "庚", "余气": "戊"},
    "午": {"本气": "丁", "中气": "己", "余气": None},
    "未": {"本气": "己", "中气": "丁", "余气": "乙"},
    "申": {"本气": "庚", "中气": "壬", "余气": "戊"},
    "酉": {"本气": "辛", "中气": "庚", "余气": None},
    "戌": {"本气": "戊", "中气": "辛", "余气": "丁"},
    "亥": {"本气": "壬", "中气": "甲", "余气": None},
}

# 本气表（便于快速查询）
BENQI_STEM = {
    "子": "癸",
    "丑": "己",
    "寅": "甲",
    "卯": "乙",
    "辰": "戊",
    "巳": "丙",
    "午": "丁",
    "未": "己",
    "申": "庚",
    "酉": "辛",
    "戌": "戊",
    "亥": "壬",
}

# 中气表
ZHONGQI_STEM = {
    "子": "壬",
    "丑": "癸",
    "寅": "丙",
    "卯": "甲",
    "辰": "乙",
    "巳": "庚",
    "午": "己",
    "未": "丁",
    "申": "壬",
    "酉": "庚",
    "戌": "辛",
    "亥": "甲",
}

# 余气表
YUZHI_STEM = {
    "子": None,
    "丑": "辛",
    "寅": "戊",
    "卯": None,
    "辰": "癸",
    "巳": "戊",
    "午": None,
    "未": "乙",
    "申": "戊",
    "酉": None,
    "戌": "丁",
    "亥": None,
}


def get_yueling_canggan(yue_zhi: str) -> dict:
    """
    查询月令藏干（本气、中气、余气）
    
    Args:
        yue_zhi: 月令地支（子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥）
    
    Returns:
        dict: {"本气": str, "中气": str, "余气": str or None}
    """
    return YUELING_CANGGAN.get(yue_zhi, {"本气": None, "中气": None, "余气": None})


def get_benqi(yue_zhi: str) -> str:
    """获取月令本气"""
    return BENQI_STEM.get(yue_zhi, "")


def get_zhongqi(yue_zhi: str) -> str:
    """获取月中气"""
    return ZHONGQI_STEM.get(yue_zhi, "")


def get_yuzhi(yue_zhi: str) -> str:
    """获取月余气"""
    return YUZHI_STEM.get(yue_zhi, "")


def get_all_stems(yue_zhi: str) -> list:
    """获取月令所有藏干（本气、中气、余气，去除None）"""
    info = get_yueling_canggan(yue_zhi)
    result = []
    for key in ["本气", "中气", "余气"]:
        val = info.get(key)
        if val:
            result.append(val)
    return result


# ============================================================
# 验证测试
# ============================================================

if __name__ == "__main__":
    print("=== 月令藏干表 测试 ===\n")

    # 验证
    tests = [
        ("寅", "本气", "甲"),
        ("寅", "中气", "丙"),
        ("寅", "余气", "戊"),
        ("子", "本气", "癸"),
        ("子", "中气", "壬"),
        ("子", "余气", None),
        ("卯", "本气", "乙"),
        ("午", "本气", "丁"),
        ("午", "中气", "己"),
        ("申", "本气", "庚"),
        ("亥", "本气", "壬"),
    ]

    all_pass = True
    for zhi, key, expected in tests:
        info = get_yueling_canggan(zhi)
        result = info.get(key)
        ok = result == expected
        status = "✓" if ok else "✗"
        if not ok:
            all_pass = False
            print(f"  {status} {zhi}.{key}: 期望「{expected}」, 实际「{result}」")
        else:
            print(f"  {status} {zhi}.{key}: {result}")

    print()
    if all_pass:
        print("✓ 所有测试通过！")

    # 打印完整藏干表
    print("\n【十二地支藏干表】")
    for zhi in ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]:
        info = get_yueling_canggan(zhi)
        all_stems = get_all_stems(zhi)
        print(f"  {zhi}: 本气{info['本气']}, 中气{info['中气']}, 余气{info['余气'] or '无'} → 含干: {', '.join(all_stems)}")
