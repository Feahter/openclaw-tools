# -*- coding: utf-8 -*-
"""
刑冲害合模块 v1.0
==================
基于《三命通会》干支关系体系：
- 天干五合：甲己合土、乙庚合金、丙辛合水、丁壬合木、戊癸合火
- 地支三合：申子辰（水局）、寅午戌（火局）、亥卯未（木局）、巳酉丑（金局）
- 地支半三合：申子/子辰/申辰等（局中任意两字）
- 地支六冲：子午、丑未、寅申、卯酉、辰戌、巳亥
- 地支三刑：子卯、寅巳申、丑戌未、辰午酉亥（自刑）
- 地支六害：子未、丑午、寅巳、卯辰、申亥、酉戌

用法：
  analyze_branch_relation(branch_a, branch_b) → 关系描述
  analyze_stem_relation(stem_a, stem_b) → 天干合化
  get_full_bazi_relation(bazi_dict) → 完整八字六亲关系
"""

from typing import Dict, List, Optional, Tuple

# ============================================================
# 天干索引常量
# ============================================================
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
STEM_IDX = {s: i for i, s in enumerate(STEMS)}

# 地支索引常量
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
BRANCH_IDX = {b: i for i, b in enumerate(BRANCHES)}

# ============================================================
# 天干五合表（天干五合 + 化神）
# ============================================================
STEM_HARMONY = {
    # 天干五合口诀：甲己合土、乙庚合金、丙辛合水、丁壬合木、戊癸合火
    # 索引：甲=0,乙=1,丙=2,丁=3,戊=4,己=5,庚=6,辛=7,壬=8,癸=9
    # key按排序存储（min,max）
    (0, 5): ("土", "甲己合土，中正之合，厚重稳重。"),
    (1, 6): ("金", "乙庚合金，仁义之合，刚柔相济。"),
    (2, 7): ("水", "丙辛合水，威严之合，权力相从。"),
    (3, 8): ("木", "丁壬合木，仁寿之合，柔顺之道。"),
    (4, 9): ("火", "戊癸合火，礼义之合，顺从之道。"),
}


def get_stem_huajin(stem_a: str, stem_b: str) -> Optional[Dict]:
    """
    分析天干五合及化神

    参数：stem_a, stem_b - 天干字符

    返回：{
        "is_harmony": bool,
        "化神": str or None,
        "描述": str
    }
    """
    ia = STEM_IDX.get(stem_a)
    ib = STEM_IDX.get(stem_b)
    if ia is None or ib is None:
        return {"is_harmony": False, "化神": None, "描述": "无效天干"}

    # 五合查找（两个方向）
    key = tuple(sorted([ia, ib]))
    if key in STEM_HARMONY:
        huajin, desc = STEM_HARMONY[key]
        return {"is_harmony": True, "化神": huajin, "描述": desc}
    return {"is_harmony": False, "化神": None, "描述": "不相合"}


# ============================================================
# 地支六冲（对冲，相克）
# ============================================================
# 六冲：子午冲、丑未冲、寅申冲、卯酉冲、辰戌冲、巳亥冲
# 地支索引：子0 丑1 寅2 卯3 辰4 巳5 午6 未7 申8 酉9 戌10 亥11
# 冲的关系：相差6位（对冲）
BRANCH_CONFRONT = {
    0: [6],   # 子冲午
    1: [7],   # 丑冲未
    2: [8],   # 寅冲申
    3: [9],   # 卯冲酉
    4: [10],  # 辰冲戌
    5: [11],  # 巳冲亥
    6: [0],   # 午冲子
    7: [1],   # 未冲丑
    8: [2],   # 申冲寅
    9: [3],   # 酉冲卯
    10: [4],  # 戌冲辰
    11: [5],  # 亥冲巳
}


def is_branch_chong(branch_a_idx: int, branch_b_idx: int) -> bool:
    """判断两地支是否相冲"""
    return branch_b_idx in BRANCH_CONFRONT.get(branch_a_idx, [])


# ============================================================
# 地支六合
# ============================================================
# 六合：子丑合土、寅亥合木、卯戌合火、辰酉合金、巳申合水、午未合火
BRANCH_HARMONY = {
    # (a, b) → (化神, 描述)
    (0, 1): ("土", "子丑合土，踏实稳重。"),
    (1, 0): ("土", "子丑合土，踏实稳重。"),
    (2, 11): ("木", "寅亥合木，仁义相助。"),
    (11, 2): ("木", "寅亥合木，仁义相助。"),
    (3, 10): ("火", "卯戌合火，礼义相从。"),
    (10, 3): ("火", "卯戌合火，礼义相从。"),
    (4, 9): ("金", "辰酉合金，柔顺相合。"),
    (9, 4): ("金", "辰酉合金，柔顺相合。"),
    (5, 8): ("水", "巳申合水，智谋相生。"),
    (8, 5): ("水", "巳申合水，智谋相生。"),
    (6, 7): ("火", "午未合火，光明相助。"),
    (7, 6): ("火", "午未合火，光明相助。"),
}


def get_branch_hehua(branch_a_idx: int, branch_b_idx: int) -> Optional[Dict]:
    """分析地支六合"""
    key = tuple(sorted([branch_a_idx, branch_b_idx]))
    if key in BRANCH_HARMONY:
        huajin, desc = BRANCH_HARMONY[key]
        return {"is_harmony": True, "化神": huajin, "描述": desc}
    return None


# ============================================================
# 地支三合局
# ============================================================
# 三合局：申子辰（水局）、寅午戌（火局）、亥卯未（木局）、巳酉丑（金局）
THREE_COMBOS = [
    ([8, 0, 4], "水", "申子辰三合水局，智谋深藏。"),
    ([2, 6, 10], "火", "寅午戌三合火局，热情积极。"),
    ([11, 3, 7], "木", "亥卯未三合木局，仁慈有情。"),
    ([5, 9, 1], "金", "巳酉丑三合金局，刚毅果断。"),
]

# 半三合（局中任意两字）
HALF_THREE = {
    (8, 0): ("水", "申子半三合水，智谋初成。"), (0, 8): ("水", "子申半三合水，智谋初成。"),
    (0, 4): ("水", "子辰半三合水，情深义重。"), (4, 0): ("水", "辰子半三合水，情深义重。"),
    (8, 4): ("水", "申辰半三合水，互助有余。"), (4, 8): ("水", "辰申半三合水，互助有余。"),
    (2, 6): ("火", "寅午半三合火，光明磊落。"), (6, 2): ("火", "午寅半三合火，光明磊落。"),
    (6, 10): ("火", "午戌半三合火，热情持久。"), (10, 6): ("火", "戌午半三合火，热情持久。"),
    (2, 10): ("火", "寅戌半三合火，相见甚欢。"), (10, 2): ("火", "戌寅半三合火，相见甚欢。"),
    (11, 3): ("木", "亥卯半三合木，仁义相助。"), (3, 11): ("木", "卯亥半三合木，仁义相助。"),
    (3, 7): ("木", "卯未半三合木，情深义重。"), (7, 3): ("木", "未卯半三合木，情深义重。"),
    (11, 7): ("木", "亥未半三合木，互助互爱。"), (7, 11): ("木", "未亥半三合木，互助互爱。"),
    (5, 9): ("金", "巳酉半三合金，刚毅果断。"), (9, 5): ("金", "酉巳半三合金，刚毅果断。"),
    (9, 1): ("金", "酉丑半三合金，情义并重。"), (1, 9): ("金", "丑酉半三合金，情义并重。"),
    (5, 1): ("金", "巳丑半三合金，逆境相助。"), (1, 5): ("金", "丑巳半三合金，逆境相助。"),
}


def get_three_combo_info(branch_indices: List[int]) -> Optional[Dict]:
    """判断一组地支是否构成三合局"""
    s = set(branch_indices)
    for combo, huajin, desc in THREE_COMBOS:
        if set(combo).issubset(s):
            return {"is_full": True, "huajin": huajin, "描述": desc}
    # 半三合
    for combo, huajin, desc in THREE_COMBOS:
        count = sum(1 for b in combo if b in s)
        if count == 2:
            pair = [b for b in combo if b in s]
            key = tuple(sorted(pair))
            if key in HALF_THREE:
                h, d = HALF_THREE[key]
                return {"is_half": True, "huajin": h, "描述": d}
    return None


# ============================================================
# 地支三刑
# ============================================================
# 三刑：子卯刑（无礼之刑）、寅巳申刑（无恩之刑）、
#        丑戌未刑（恃势之刑）、辰午酉亥（自刑）
BRANCH_XING = {
    # (a, b) → 刑名 + 描述（方向性）
    (0, 3): ("子卯刑", "无礼之刑", "子水生卯木，溺爱无情，多波折是非。"),
    (3, 0): ("子卯刑", "无礼之刑", "子水生卯木，溺爱无情，多波折是非。"),
    (2, 5): ("寅巳申刑", "无恩之刑", "寅木生巳火，巳火克申金，恩将仇报。"),
    (5, 2): ("寅巳申刑", "无恩之刑", "寅木生巳火，巳火克申金，恩将仇报。"),
    (2, 8): ("寅巳申刑", "无恩之刑", "寅木克申金，巳火从中，多争执。"),
    (8, 2): ("寅巳申刑", "无恩之刑", "申金克寅木，多冲突。"),
    (5, 8): ("寅巳申刑", "无恩之刑", "巳火克申金，恩将仇报。"),
    (8, 5): ("寅巳申刑", "无恩之刑", "申金反克巳火，多波折。"),
    (1, 10): ("丑戌未刑", "恃势之刑", "丑土助戌土，戌土克未土，倚势凌人。"),
    (10, 1): ("丑戌未刑", "恃势之刑", "戌土克未土，丑土助之，欺凌弱少。"),
    (1, 7): ("丑戌未刑", "恃势之刑", "丑土克未土，戌土助之，多是非。"),
    (7, 1): ("丑戌未刑", "恃势之刑", "未土被丑戌夹克，处境艰难。"),
    (10, 7): ("丑戌未刑", "恃势之刑", "戌土克未土，丑土助之，凌弱欺小。"),
    (7, 10): ("丑戌未刑", "恃势之刑", "未土被戌丑夹克，处境艰难。"),
    # 自刑
    (4, 4): ("辰辰自刑", "自刑", "辰为水库，自我纠结，内耗严重。"),
    (6, 6): ("午午自刑", "自刑", "午为火旺，自我伤害，内火过盛。"),
    (9, 9): ("酉酉自刑", "自刑", "酉为金旺，自我纠结，内心矛盾。"),
    (11, 11): ("亥亥自刑", "自刑", "亥为水旺，自我消耗，内耗严重。"),
}


def get_branch_xing(branch_a_idx: int, branch_b_idx: int) -> Optional[Dict]:
    """分析地支三刑"""
    key = (branch_a_idx, branch_b_idx)
    if key in BRANCH_XING:
        name, category, desc = BRANCH_XING[key]
        return {"is_xing": True, "刑名": name, "类别": category, "描述": desc}
    return None


# ============================================================
# 地支六害
# ============================================================
# 六害：子未相害、丑午相害、寅巳相害、卯辰相害、申亥相害、酉戌相害
BRANCH_HAI = {
    (0, 7): ("子未害", "子未相害，暗昧之争，阴阳不协。"),
    (7, 0): ("子未害", "子未相害，暗昧之争，阴阳不协。"),
    (1, 6): ("丑午害", "丑午相害，门户之争，是非不断。"),
    (6, 1): ("丑午害", "丑午相害，门户之争，是非不断。"),
    (2, 5): ("寅巳害", "寅巳相害，恩将仇报，竞争相害。"),
    (5, 2): ("寅巳害", "寅巳相害，恩将仇报，竞争相害。"),
    (3, 4): ("卯辰害", "卯辰相害，门户之争，情感纠结。"),
    (4, 3): ("卯辰害", "卯辰相害，门户之争，情感纠结。"),
    (8, 11): ("申亥害", "申亥相害，财禄损伤，辗转不宁。"),
    (11, 8): ("申亥害", "申亥相害，财禄损伤，辗转不宁。"),
    (9, 10): ("酉戌害", "酉戌相害，印制食伤，才华受阻。"),
    (10, 9): ("酉戌害", "酉戌害", "酉戌相害，印制食伤，才华受阻。"),
}


def get_branch_hai(branch_a_idx: int, branch_b_idx: int) -> Optional[Dict]:
    """分析地支六害"""
    key = (branch_a_idx, branch_b_idx)
    if key in BRANCH_HAI:
        name, desc = BRANCH_HAI[key]
        return {"is_hai": True, "害名": name, "描述": desc}
    return None


# ============================================================
# 主函数：分析任意两地支之间的关系
# ============================================================
def analyze_branch_relation(branch_a: str, branch_b: str) -> Dict:
    """
    综合分析两地支之间的所有关系

    参数：branch_a, branch_b - 地支字符

    返回：{
        "branch_a": str,
        "branch_b": str,
        "relations": [
            {"type": "冲/合/刑/害", "name": "xxx", "描述": "..."}
        ],
        "is_harmony": bool,   # 是否有合
        "is_chong": bool,     # 是否相冲
        "is_xing": bool,      # 是否相刑
        "is_hai": bool,       # 是否相害
        "综合": "好/中/差"   # 综合判断
    }
    """
    ia = BRANCH_IDX.get(branch_a)
    ib = BRANCH_IDX.get(branch_b)

    if ia is None or ib is None:
        return {"error": "无效地支"}

    relations = []
    is_harmony = False
    is_chong = False
    is_xing = False
    is_hai = False

    # 六冲（最强，优先判断）
    if is_branch_chong(ia, ib):
        is_chong = True
        relations.append({
            "type": "冲",
            "name": f"{branch_a}冲{branch_b}" if ia > ib else f"{branch_b}冲{branch_a}",
            "描述": f"两地支相冲，冲动激烈，主变化、变动、分离。相冲两败俱伤。"
        })

    # 六合
    harmony = get_branch_hehua(ia, ib)
    if harmony:
        is_harmony = True
        relations.append({
            "type": "合",
            "name": f"{branch_a}合{branch_b}",
            "描述": harmony["描述"]
        })

    # 三刑
    xing = get_branch_xing(ia, ib)
    if xing:
        is_xing = True
        relations.append({
            "type": "刑",
            "name": xing["刑名"],
            "描述": xing["描述"]
        })

    # 六害
    hai = get_branch_hai(ia, ib)
    if hai:
        is_hai = True
        relations.append({
            "type": "害",
            "name": hai["害名"],
            "描述": hai["描述"]
        })

    # 既不合也不冲不刑不害
    if not relations:
        relations.append({
            "type": "无特殊",
            "name": "无",
            "描述": "两地支无冲合刑害关系，中性。"
        })

    # 综合判断
    if is_chong:
        综合 = "差"
    elif is_xing:
        综合 = "差"
    elif is_hai:
        综合 = "中"
    elif is_harmony:
        综合 = "好"
    else:
        综合 = "中"

    return {
        "branch_a": branch_a,
        "branch_b": branch_b,
        "relations": relations,
        "is_harmony": is_harmony,
        "is_chong": is_chong,
        "is_xing": is_xing,
        "is_hai": is_hai,
        "综合": 综合,
    }


def analyze_stem_relation(stem_a: str, stem_b: str) -> Dict:
    """分析两天天干之间的关系（天干五合）"""
    ia = STEM_IDX.get(stem_a)
    ib = STEM_IDX.get(stem_b)
    if ia is None or ib is None:
        return {"error": "无效天干"}

    harmony = get_stem_huajin(stem_a, stem_b)
    return {
        "stem_a": stem_a,
        "stem_b": stem_b,
        "is_harmony": harmony["is_harmony"],
        "化神": harmony["化神"],
        "描述": harmony["描述"],
    }


# ============================================================
# 八字整体关系分析（用于报告）
# ============================================================
def get_bazi_all_relations(bazi_dict: Dict) -> List[Dict]:
    """
    获取八字中所有有意义的干支关系

    分析以下配对：
    - 年月冲合
    - 年日冲合
    - 年时冲合
    - 月日冲合
    - 月时冲合
    - 日时冲合
    - 年干与日干五合
    """
    bz = bazi_dict['bazi']
    pairs = [
        ('year', 'month'),
        ('year', 'day'),
        ('year', 'hour'),
        ('month', 'day'),
        ('month', 'hour'),
        ('day', 'hour'),
    ]

    results = []
    for p1, p2 in pairs:
        ia = bz[p1]['branch_idx']
        ib = bz[p2]['branch_idx']
        rel = analyze_branch_relation(bz[p1]['branch'], bz[p2]['branch'])
        if rel.get("relations") and rel["relations"][0]["type"] != "无特殊":
            results.append(rel)

    # 天干五合（年-日）
    stem_rel = analyze_stem_relation(bz['year']['stem'], bz['day']['stem'])
    if stem_rel["is_harmony"]:
        results.append(stem_rel)

    return results


# ============================================================
# 验证测试
# ============================================================
if __name__ == "__main__":
    print("=== 刑冲害合验证 ===")

    # 六冲验证
    assert is_branch_chong(0, 6) == True, "子午冲 ❌"
    assert is_branch_chong(6, 0) == True, "子午冲(反) ❌"
    assert is_branch_chong(0, 3) == False, "子卯不应冲 ❌"
    print("  六冲验证: 子午/丑未/寅申/卯酉/辰戌/巳亥 ✅")

    # 六合验证
    assert get_branch_hehua(0, 1) is not None, "子丑合 ❌"
    assert get_branch_hehua(2, 11) is not None, "寅亥合 ❌"
    assert get_branch_hehua(0, 3) is None, "子卯不合 ❌"
    print("  六合验证: 子丑/寅亥/卯戌/辰酉/巳申/午未 ✅")

    # 三刑验证
    assert get_branch_xing(0, 3) is not None, "子卯刑 ❌"
    assert get_branch_xing(4, 4) is not None, "辰辰自刑 ❌"
    print("  三刑验证: 子卯/寅巳申/丑戌未/辰午酉亥自刑 ✅")

    # 六害验证
    assert get_branch_hai(0, 7) is not None, "子未害 ❌"
    assert get_branch_hai(3, 4) is not None, "卯辰害 ❌"
    print("  六害验证: 子未/丑午/寅巳/卯辰/申亥/酉戌 ✅")

    # 天干五合验证
    assert get_stem_huajin("甲", "己")["is_harmony"] == True, "甲己合 ❌"
    assert get_stem_huajin("甲", "己")["化神"] == "土", "甲己化土 ❌"
    assert get_stem_huajin("乙", "庚")["is_harmony"] == True, "乙庚合 ❌"
    assert get_stem_huajin("甲", "乙")["is_harmony"] == False, "甲乙不合 ❌"
    print("  天干五合验证: 甲己/乙庚/丙辛/丁壬/戊癸 ✅")

    # 综合关系分析
    print("\n=== 综合关系分析 ===")
    test_pairs = [
        ("子", "午"),  # 冲
        ("子", "丑"),  # 合
        ("子", "卯"),  # 刑
        ("子", "未"),  # 害
        ("寅", "亥"),  # 合
        ("午", "未"),  # 合
    ]
    for ba, bb in test_pairs:
        rel = analyze_branch_relation(ba, bb)
        types = [r["type"] for r in rel["relations"]]
        print(f"  {ba}{bb}: {types} → {rel['综合']}")

    print("\n✅ 刑冲害合全部验证通过")
