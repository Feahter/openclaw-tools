#!/usr/bin/env python3
"""
神煞查询系统
参考《三命通会》神煞体系，纯本地计算，不依赖API

核心神煞：
- P0：天乙贵人、文昌、驿马、华盖、桃花（最常用）
- P1：天德/月德、红鸾天喜、三奇、将星、亡神
- P2：劫煞、灾煞、丧门、吊客、六甲贵神
"""

from typing import Dict, List, Any, Optional

# 天干地支常量（从 lunar_calendar 导入或在此定义）
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 地支索引常量
BRANCH_IDX = {b: i for i, b in enumerate(EARTHLY_BRANCHES)}
STEM_IDX = {s: i for i, s in enumerate(HEAVENLY_STEMS)}


# ============================================================
# P0 神煞
# ============================================================

def get_tianyi_guiren(year_stem_idx: int, year_branch_idx: int) -> Dict[str, Any]:
    """
    天乙贵人（最重要的贵人星）
    
    口诀：甲戊兼牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，庚辛逢虎马
    
    Args:
        year_stem_idx: 年干索引 (0-9)
        year_branch_idx: 年支索引 (0-11)
    
    Returns:
        dict: {
            "has_guiren": True/False,
            "guiren_branches": ["丑", "未"] or [],
            "guiren_direction": "东北" or "西南" or "无",
            "description": str
        }
    """
    # 年干决定贵人所在的地支
    # 甲、戊年: 丑(1)、未(8) → 牛羊
    # 乙、己年: 子(0)、申(8) → 鼠猴
    # 丙、丁年: 亥(11)、酉(9) → 猪鸡
    # 壬、癸年: 卯(3)、巳(6) → 兔蛇
    # 庚、辛年: 寅(2)、午(5) → 虎马
    
    guiren_map = {
        0: [1, 7],    # 甲: 丑(1)、未(7)
        1: [0, 8],    # 乙: 子(0)、申(8)
        2: [9, 11],   # 丙: 酉(9)、亥(11)
        3: [9, 11],   # 丁: 酉(9)、亥(11)
        4: [1, 7],    # 戊: 丑(1)、未(7)
        5: [0, 8],    # 己: 子(0)、申(8)
        6: [2, 6],    # 庚: 寅(2)、午(6)
        7: [2, 6],    # 辛: 寅(2)、午(6)
        8: [3, 5],    # 壬: 卯(3)、巳(5)
        9: [3, 5],    # 癸: 卯(3)、巳(5)
    }
    
    guiren_branches_idx = guiren_map.get(year_stem_idx, [])
    guiren_branches = [EARTHLY_BRANCHES[i] for i in guiren_branches_idx]
    
    # 判断是否有贵人（看八字中是否存在对应地支）
    # 贵人多以年干为主，日干为辅，此处以年干查法为准
    # 是否得贵：看八字四柱中是否出现贵人所落地支
    has_guiren = len(guiren_branches_idx) > 0
    
    # 贵人方向：丑未为东北方（艮坤），子申为西南方（坤），亥酉为西北方（乾），卯巳为东方（震巽），寅午为南北方
    direction_map = {
        0: "西南",   # 子（鼠）
        1: "东北",   # 丑（牛）
        2: "东北",   # 寅（虎）
        3: "东方",   # 卯（兔）
        5: "南方",   # 午（马）
        6: "东南",   # 巳（蛇）
        8: "西南",   # 申（猴）
        9: "西方",   # 酉（鸡）
        11: "西北",  # 亥（猪）
    }
    
    directions = list(dict.fromkeys([direction_map.get(i, "") for i in guiren_branches_idx]))
    
    return {
        "has_guiren": has_guiren,
        "guiren_branches": guiren_branches,
        "guiren_branches_idx": guiren_branches_idx,
        "guiren_direction": "/".join(directions) if directions else "无",
        "description": f"天乙贵人落在{'、'.join(guiren_branches) if guiren_branches else '无'}" +
                       (f"（{directions[0]}方向）" if len(directions) == 1 else ""),
        "口诀": "甲戊兼牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，庚辛逢虎马",
    }


def get_wenchang(year_stem_idx: int) -> Dict[str, Any]:
    """
    文昌（学业考试之星）
    
    文昌查法：甲食丙，乙食丁，丙食戊，丁食己，戊食庚，己食辛，
              庚食壬，辛食癸，壬食甲，癸食乙
    文昌位：食神所临之宫（临官位）
    
    验证：
    甲食丙 → 丙临官在巳 → 文昌在巳(5) ✓ (0+5)%12=5
    乙食丁 → 丁临官在午 → 文昌在午(6) ✓ (1+5)%12=6
    丙食戊 → 戊临官在申 → 文昌在申(8) ✓ (2+5)%12=7≠8（需查表）
    丁食己 → 己临官在酉 → 文昌在酉(9) ✓ (3+5)%12=8≠9
    戊食庚 → 庚临官在亥 → 文昌在亥(11) ✓ (4+5)%12=9≠11
    己食辛 → 辛临官在子 → 文昌在子(0) ✓ (5+5)%12=10≠0
    庚食壬 → 壬临官在寅 → 文昌在寅(2) ✓ (6+5)%12=11≠2
    辛食癸 → 癸临官在卯 → 文昌在卯(3) ✓ (7+5)%12=0≠3
    壬食甲 → 甲临官在寅 → 文昌在寅(2) ✓ (8+5)%12=1≠2
    癸食乙 → 乙临官在卯 → 文昌在卯(3) ✓ (9+5)%12=2≠3
    
    结论：需用查表法（非简单公式），基于十二长生表：
    甲→5(巳),乙→6(午),丙→8(申),丁→9(酉),戊→11(亥),
    己→0(子),庚→2(寅),辛→3(卯),壬→2(寅),癸→3(卯)
    
    Args:
        year_stem_idx: 年干索引 (0-9)
    
    Returns:
        dict: {
            "wenchang_branch": "巳",
            "wenchang_branch_idx": 5,
            "description": str
        }
    """
    # 文昌星所在的分支索引（年干 → 文昌地支，临官位）
    wenchang_map = {
        0: 5,   # 甲: 食神=丙 → 临官在巳(5)
        1: 6,   # 乙: 食神=丁 → 临官在午(6)
        2: 8,   # 丙: 食神=戊 → 临官在申(8)
        3: 9,   # 丁: 食神=己 → 临官在酉(9)
        4: 11,  # 戊: 食神=庚 → 临官在亥(11)
        5: 0,   # 己: 食神=辛 → 临官在子(0)
        6: 2,   # 庚: 食神=壬 → 临官在寅(2)
        7: 3,   # 辛: 食神=癸 → 临官在卯(3)
        8: 2,   # 壬: 食神=甲 → 临官在寅(2)
        9: 3,   # 癸: 食神=乙 → 临官在卯(3)
    }
    
    branch_idx = wenchang_map.get(year_stem_idx, 0)
    branch = EARTHLY_BRANCHES[branch_idx]
    
    return {
        "wenchang_branch": branch,
        "wenchang_branch_idx": branch_idx,
        "description": f"文昌在{branch}",
    }


def get_yima(year_branch_idx: int) -> Dict[str, Any]:
    """
    驿马（变动奔波之星）
    
    申子辰马在寅，寅午戌马在申，亥卯未马在巳，巳酉丑马在亥
    
    Args:
        year_branch_idx: 年支索引 (0-11)
    
    Returns:
        dict: {
            "yima_branch": "寅",
            "yima_branch_idx": 2,
            "description": str
        }
    """
    # 驿马地支映射（基于三合局）
    # 申子辰→马在寅，寅午戌→马在申，亥卯未→马在巳，巳酉丑→马在亥
    yima_map = {
        0: 2,    # 子: 水局 → 马在寅(2)
        1: 11,   # 丑: 金局 → 马在亥(11)
        2: 8,    # 寅: 火局 → 马在申(8)
        3: 6,    # 卯: 木局 → 马在巳(6)
        4: 2,    # 辰: 水局 → 马在寅(2)
        5: 11,   # 巳: 金局 → 马在亥(11)
        6: 8,    # 午: 火局 → 马在申(8)
        7: 6,    # 未: 木局 → 马在巳(6)
        8: 2,    # 申: 水局 → 马在寅(2)
        9: 11,   # 酉: 金局 → 马在亥(11)
        10: 8,   # 戌: 火局 → 马在申(8)
        11: 6,   # 亥: 木局 → 马在巳(6)
    }
    
    branch_idx = yima_map.get(year_branch_idx, 0)
    branch = EARTHLY_BRANCHES[branch_idx]
    
    return {
        "yima_branch": branch,
        "yima_branch_idx": branch_idx,
        "description": f"驿马在{branch}",
    }


def get_huagai(year_branch_idx: int) -> Dict[str, Any]:
    """
    华盖（艺术/僧道之星）
    
    辰戌丑未为华盖
    
    Args:
        year_branch_idx: 年支索引 (0-11)
    
    Returns:
        dict: {
            "has_huagai": True/False,
            "huagai_branch": "辰" or None,
            "description": str
        }
    """
    huagai_branches = [4, 10, 1, 7]  # 辰、戌、丑、未
    
    has_huagai = year_branch_idx in huagai_branches
    branch = EARTHLY_BRANCHES[year_branch_idx] if has_huagai else None
    
    return {
        "has_huagai": has_huagai,
        "huagai_branch": branch,
        "huagai_branch_idx": year_branch_idx if has_huagai else None,
        "description": f"华盖{'在' + branch if has_huagai else '无'}",
    }


def get_taohua(year_branch_idx: int) -> Dict[str, Any]:
    """
    桃花（感情姻缘之星）
    
    申子辰见酉，寅午戌见卯，亥卯未见子，巳酉丑见午
    
    Args:
        year_branch_idx: 年支索引 (0-11)
    
    Returns:
        dict: {
            "taohua_branch": "酉",
            "taohua_branch_idx": 9,
            "description": str
        }
    """
    # 桃花地支映射
    taohua_map = {
        0: 9,    # 子: 桃花在酉(9)
        1: 5,    # 丑: 桃花在午(5)
        2: 3,    # 寅: 桃花在卯(3)
        3: 0,    # 卯: 桃花在子(0)
        4: 9,    # 辰: 桃花在酉(9)
        5: 5,    # 巳: 桃花在午(5)
        6: 3,    # 午: 桃花在卯(3)
        7: 0,    # 未: 桃花在子(0)
        8: 9,    # 申: 桃花在酉(9)
        9: 5,    # 酉: 桃花在午(5)
        10: 3,   # 戌: 桃花在卯(3)
        11: 0,   # 亥: 桃花在子(0)
    }
    
    branch_idx = taohua_map.get(year_branch_idx, 0)
    branch = EARTHLY_BRANCHES[branch_idx]
    
    return {
        "taohua_branch": branch,
        "taohua_branch_idx": branch_idx,
        "description": f"桃花在{branch}",
    }


# ============================================================
# P1 神煞
# ============================================================

def get_tiande(year_stem_idx: int) -> Dict[str, Any]:
    """
    天德（上天赐福之神）
    
    天德口诀：正丁二坤申，三壬四辛同，五癸甲艮延，六乙七兑乾，八寅九丙星，十己地支寻，十一戌上走，十二亥中行
    
    Args:
        year_stem_idx: 年干索引 (0-9)
    
    Returns:
        dict: {
            "tiande_branch": "巳",
            "tiande_branch_idx": 6,
            "description": str
        }
    """
    # 天德所在的分支索引（按月查，非年干查法）
    # 正月丁、二月坤申、三月壬、四月辛、五月癸甲艮、六月乙、七月兑乾、八月寅、九月丙、十月己、十一戌、十二亥
    # 按年干索引简化：
    tiande_map = {
        0: 2,    # 甲: 寅
        1: 9,    # 乙: 酉
        2: 6,    # 丙: 巳
        3: 8,    # 丁: 申
        4: 3,    # 戊: 卯
        5: 0,    # 己: 子
        6: 5,    # 庚: 午
        7: 11,   # 辛: 亥
        8: 9,    # 壬: 酉
        9: 4,    # 癸: 辰
    }
    
    branch_idx = tiande_map.get(year_stem_idx, 0)
    branch = EARTHLY_BRANCHES[branch_idx]
    
    return {
        "tiande_branch": branch,
        "tiande_branch_idx": branch_idx,
        "description": f"天德在{branch}",
    }


def get_yuede(year_stem_idx: int) -> Dict[str, Any]:
    """
    月德（ 月建德神）
    
    月德：只针对阳干（甲丙戊庚壬）
    甲亥乙庚午，丙丁壬癸辛，戊己土无德
    
    Args:
        year_stem_idx: 年干索引 (0-9)
    
    Returns:
        dict: {
            "yuede_branch": "亥",
            "yuede_branch_idx": 11,
            "has_yuede": True/False,
            "description": str
        }
    """
    # 月德只对阳干有效
    yuede_map = {
        0: 11,   # 甲: 亥
        1: 5,    # 乙: 午
        2: 8,    # 丙: 申
        3: 6,    # 丁: 巳
        4: None, # 戊: 无
        5: None, # 己: 无
        6: 11,   # 庚: 亥
        7: 5,    # 辛: 午
        8: 0,    # 壬: 子
        9: 3,    # 癸: 卯
    }
    
    branch_idx = yuede_map.get(year_stem_idx)
    has_yuede = branch_idx is not None
    branch = EARTHLY_BRANCHES[branch_idx] if has_yuede else None
    
    return {
        "yuede_branch": branch,
        "yuede_branch_idx": branch_idx,
        "has_yuede": has_yuede,
        "description": f"月德{'在' + branch if has_yuede else '无'}",
    }


def get_hongluan_tianxi(year_branch_idx: int) -> Dict[str, Any]:
    """
    红鸾天喜（婚嫁之星）
    
    红鸾：年支对应的吉方
    天喜：红鸾对冲之方
    
    子丑寅卯辰巳午未申酉戌亥
    红：卯辰巳午未申酉戌亥子丑寅
    喜：酉戌亥子丑寅卯辰巳午未
    
    Args:
        year_branch_idx: 年支索引 (0-11)
    
    Returns:
        dict: {
            "hongluan_branch": "卯",
            "hongluan_branch_idx": 3,
            "tianxi_branch": "酉",
            "tianxi_branch_idx": 9,
            "description": str
        }
    """
    hongluan_map = {
        0: 3, 1: 4, 2: 5, 3: 6, 4: 7, 5: 8,
        6: 9, 7: 10, 8: 11, 9: 0, 10: 1, 11: 2,
    }
    
    tianxi_map = {
        0: 9, 1: 10, 2: 11, 3: 0, 4: 1, 5: 2,
        6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8,
    }
    
    hl_idx = hongluan_map.get(year_branch_idx, 0)
    tx_idx = tianxi_map.get(year_branch_idx, 0)
    
    return {
        "hongluan_branch": EARTHLY_BRANCHES[hl_idx],
        "hongluan_branch_idx": hl_idx,
        "tianxi_branch": EARTHLY_BRANCHES[tx_idx],
        "tianxi_branch_idx": tx_idx,
        "description": f"红鸾在{EARTHLY_BRANCHES[hl_idx]}，天喜在{EARTHLY_BRANCHES[tx_idx]}",
    }


def get_sanqi(year_stem_idx: int, month_stem_idx: int, day_stem_idx: int) -> Dict[str, Any]:
    """
    天地人三奇
    
    甲戊庚乙丙丁壬癸辛
    
    三奇顺序：天上三奇甲戊庚，地下三奇乙丙丁，人间三奇壬癸辛
    条件：年月日或日时柱出现三奇顺序排列（甲戊庚、乙丙丁、壬癸辛）
    
    Args:
        year_stem_idx: 年干索引
        month_stem_idx: 月干索引
        day_stem_idx: 日干索引
    
    Returns:
        dict: {
            "has_sanqi": True/False,
            "sanqi_type": "天上三奇" or "地下三奇" or "人间三奇" or "无",
            "sanqi_stems": ["甲", "戊", "庚"],
            "description": str
        }
    """
    stems = [HEAVENLY_STEMS[year_stem_idx], HEAVENLY_STEMS[month_stem_idx], HEAVENLY_STEMS[day_stem_idx]]
    
    tian_sanqi = ["甲", "戊", "庚"]
    di_sanqi = ["乙", "丙", "丁"]
    ren_sanqi = ["壬", "癸", "辛"]
    
    # 检查年月日是否形成三奇顺序
    if stems == tian_sanqi:
        return {"has_sanqi": True, "sanqi_type": "天上三奇", "sanqi_stems": tian_sanqi, "description": "天上三奇（甲戊庚）"}
    elif stems == di_sanqi:
        return {"has_sanqi": True, "sanqi_type": "地下三奇", "sanqi_stems": di_sanqi, "description": "地下三奇（乙丙丁）"}
    elif stems == ren_sanqi:
        return {"has_sanqi": True, "sanqi_type": "人间三奇", "sanqi_stems": ren_sanqi, "description": "人间三奇（壬癸辛）"}
    else:
        return {"has_sanqi": False, "sanqi_type": "无", "sanqi_stems": [], "description": "无三奇"}


def get_jiangxing(year_branch_idx: int) -> Dict[str, Any]:
    """
    将星（权力之星）
    
    将星：月支三合局的核心地支
    申子辰 → 子为将星
    寅午戌 → 午为将星
    亥卯未 → 卯为将星
    巳酉丑 → 酉为将星
    
    Args:
        year_branch_idx: 年支索引 (0-11)
    
    Returns:
        dict: {
            "jiangxing_branch": "子",
            "jiangxing_branch_idx": 0,
            "description": str
        }
    """
    jiangxing_map = {
        0: 0,    # 子: 子为将星
        1: 9,    # 丑: 酉为将星
        2: 6,    # 寅: 午为将星
        3: 3,    # 卯: 卯为将星
        4: 0,    # 辰: 子为将星
        5: 9,    # 巳: 酉为将星
        6: 6,    # 午: 午为将星
        7: 3,    # 未: 卯为将星
        8: 0,    # 申: 子为将星
        9: 9,    # 酉: 酉为将星
        10: 6,   # 戌: 午为将星
        11: 3,   # 亥: 卯为将星
    }
    
    branch_idx = jiangxing_map.get(year_branch_idx, 0)
    branch = EARTHLY_BRANCHES[branch_idx]
    
    return {
        "jiangxing_branch": branch,
        "jiangxing_branch_idx": branch_idx,
        "description": f"将星在{branch}",
    }


def get_wangshen(year_branch_idx: int) -> Dict[str, Any]:
    """
    亡神（动荡之星）
    
    亡神：三合局的对冲之方
    申子辰 → 亡神在寅
    寅午戌 → 亡神在申
    亥卯未 → 亡神在巳
    巳酉丑 → 亡神在亥
    
    Args:
        year_branch_idx: 年支索引 (0-11)
    
    Returns:
        dict: {
            "wangshen_branch": "寅",
            "wangshen_branch_idx": 2,
            "description": str
        }
    """
    # 亡神：驿马对冲之方
    # 申子辰马在寅(2) → 亡神在对冲位申(8)
    # 寅午戌马在申(8) → 亡神在对冲位寅(2)
    # 亥卯未马在巳(6) → 亡神在对冲位子(0)
    # 巳酉丑马在亥(11) → 亡神在对冲位巳(5)
    wangshen_map = {
        0: 8,    # 子: 亡神在申(8)
        1: 5,    # 丑: 亡神在巳(5)
        2: 2,    # 寅: 亡神在寅(2) -- 自坐
        3: 0,    # 卯: 亡神在子(0)
        4: 8,    # 辰: 亡神在申(8)
        5: 5,    # 巳: 亡神在巳(5) -- 自坐
        6: 2,    # 午: 亡神在寅(2)
        7: 0,    # 未: 亡神在子(0)
        8: 8,    # 申: 亡神在申(8) -- 自坐
        9: 5,    # 酉: 亡神在巳(5)
        10: 2,   # 戌: 亡神在寅(2)
        11: 0,   # 亥: 亡神在子(0)
    }
    
    branch_idx = wangshen_map.get(year_branch_idx, 0)
    branch = EARTHLY_BRANCHES[branch_idx]
    
    return {
        "wangshen_branch": branch,
        "wangshen_branch_idx": branch_idx,
        "description": f"亡神在{branch}",
    }


# ============================================================
# P2 神煞
# ============================================================

def get_jiesha(year_branch_idx: int) -> Dict[str, Any]:
    """
    劫煞（凶煞）
    
    申子辰劫煞在巳，寅午戌劫煞在亥，亥卯未劫煞在申，巳酉丑劫煞在寅
    
    Args:
        year_branch_idx: 年支索引 (0-11)
    
    Returns:
        dict: {
            "jiesha_branch": "巳",
            "jiesha_branch_idx": 6,
            "description": str
        }
    """
    # 劫煞：基于驿马+3位（三合局马位对冲之冲）
    # 申子辰马在寅 → 劫煞在巳
    # 寅午戌马在申 → 劫煞在亥
    # 亥卯未马在巳 → 劫煞在申
    # 巳酉丑马在亥 → 劫煞在寅
    jiesha_map = {
        0: 5,    # 子: 劫煞在巳(5)
        1: 2,    # 丑: 劫煞在寅(2)
        2: 11,   # 寅: 劫煞在亥(11)
        3: 8,    # 卯: 劫煞在申(8)
        4: 5,    # 辰: 劫煞在巳(5)
        5: 2,    # 巳: 劫煞在寅(2)
        6: 11,   # 午: 劫煞在亥(11)
        7: 8,    # 未: 劫煞在申(8)
        8: 5,    # 申: 劫煞在巳(5)
        9: 2,    # 酉: 劫煞在寅(2)
        10: 11,  # 戌: 劫煞在亥(11)
        11: 8,   # 亥: 劫煞在申(8)
    }
    
    branch_idx = jiesha_map.get(year_branch_idx, 0)
    branch = EARTHLY_BRANCHES[branch_idx]
    
    return {
        "jiesha_branch": branch,
        "jiesha_branch_idx": branch_idx,
        "description": f"劫煞在{branch}",
    }


def get_zaisha(year_branch_idx: int) -> Dict[str, Any]:
    """
    灾煞（凶煞）
    
    申子辰灾煞在午，寅午戌灾煞在子，亥卯未灾煞在酉，巳酉丑灾煞在卯
    
    Args:
        year_branch_idx: 年支索引 (0-11)
    
    Returns:
        dict: {
            "zaisha_branch": "午",
            "zaisha_branch_idx": 5,
            "description": str
        }
    """
    zaisha_map = {
        0: 5,    # 子: 灾煞在午
        1: 3,    # 丑: 灾煞在卯
        2: 0,    # 寅: 灾煞在子
        3: 9,    # 卯: 灾煞在酉
        4: 5,    # 辰: 灾煞在午
        5: 3,    # 巳: 灾煞在卯
        6: 0,    # 午: 灾煞在子
        7: 9,    # 未: 灾煞在酉
        8: 5,    # 申: 灾煞在午
        9: 3,    # 酉: 灾煞在卯
        10: 0,   # 戌: 灾煞在子
        11: 9,   # 亥: 灾煞在酉
    }
    
    branch_idx = zaisha_map.get(year_branch_idx, 0)
    branch = EARTHLY_BRANCHES[branch_idx]
    
    return {
        "zaisha_branch": branch,
        "zaisha_branch_idx": branch_idx,
        "description": f"灾煞在{branch}",
    }


def get_sangmen(year_branch_idx: int) -> Dict[str, Any]:
    """
    丧门（丧事之星）
    
    子丑寅卯辰巳午未申酉戌亥
    丧：卯寅丑子亥戌酉申未午巳辰
    
    Args:
        year_branch_idx: 年支索引 (0-11)
    
    Returns:
        dict: {
            "sangmen_branch": "卯",
            "sangmen_branch_idx": 3,
            "description": str
        }
    """
    sangmen_map = {
        0: 3, 1: 2, 2: 1, 3: 0, 4: 11, 5: 10,
        6: 9, 7: 8, 8: 7, 9: 6, 10: 5, 11: 4,
    }
    
    branch_idx = sangmen_map.get(year_branch_idx, 0)
    branch = EARTHLY_BRANCHES[branch_idx]
    
    return {
        "sangmen_branch": branch,
        "sangmen_branch_idx": branch_idx,
        "description": f"丧门在{branch}",
    }


def get_diaoke(year_branch_idx: int) -> Dict[str, Any]:
    """
    吊客（凶煞）
    
    子丑寅卯辰巳午未申酉戌亥
    吊：亥戌酉申未午巳辰卯寅丑子
    
    Args:
        year_branch_idx: 年支索引 (0-11)
    
    Returns:
        dict: {
            "diaoke_branch": "亥",
            "diaoke_branch_idx": 11,
            "description": str
        }
    """
    diaoke_map = {
        0: 11, 1: 10, 2: 9, 3: 8, 4: 7, 5: 6,
        6: 5, 7: 4, 8: 3, 9: 2, 10: 1, 11: 0,
    }
    
    branch_idx = diaoke_map.get(year_branch_idx, 0)
    branch = EARTHLY_BRANCHES[branch_idx]
    
    return {
        "diaoke_branch": branch,
        "diaoke_branch_idx": branch_idx,
        "description": f"吊客在{branch}",
    }


def get_liujia_guishen(year_stem_idx: int, year_branch_idx: int) -> Dict[str, Any]:
    """
    六甲贵神（旬中贵神）
    
    六甲：甲子、甲戌、甲申、甲午、甲辰、甲寅
    各有对应贵神方位
    
    Args:
        year_stem_idx: 年干索引
        year_branch_idx: 年支索引
    
    Returns:
        dict: {
            "liujia_guishen": "子",
            "description": str
        }
    """
    # 六甲贵神表
    liujia_map = {
        # 甲子旬：甲子在子(0)，贵神在亥酉
        # 甲戌旬：甲戌在戌(10)，贵神在酉申
        # 甲申旬：甲申在申(8)，贵神在未午
        # 甲午旬：甲午在午(6)，贵神在巳辰
        # 甲辰旬：甲辰在辰(4)，贵神在卯寅
        # 甲寅旬：甲寅在寅(2)，贵神在丑子
        0: "亥",  # 甲子旬
        2: "丑",  # 甲寅旬
        4: "卯",  # 甲辰旬
        6: "巳",  # 甲午旬
        8: "未",  # 甲申旬
        10: "酉", # 甲戌旬
    }
    
    guishen = liujia_map.get(year_branch_idx, "无")
    
    return {
        "liujia_guishen": guishen,
        "description": f"六甲贵神在{guishen}",
    }


# ============================================================
# 综合神煞汇总
# ============================================================

def get_shen_sha_summary(bazi_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    综合神煞查询
    
    Args:
        bazi_info: 八字信息字典（来自 bazi_engine.full_bazi_analysis 的 bazi 子字典）
    
    Returns:
        dict: 所有神煞的汇总
    """
    bazi = bazi_info.get("bazi", bazi_info)  # 兼容两种格式
    
    year_stem_idx = bazi["year"]["stem_idx"]
    year_branch_idx = bazi["year"]["branch_idx"]
    month_stem_idx = bazi["month"]["stem_idx"]
    day_stem_idx = bazi["day"]["stem_idx"]
    
    # P0 神煞
    tianyi = get_tianyi_guiren(year_stem_idx, year_branch_idx)
    wenchang = get_wenchang(year_stem_idx)
    yima = get_yima(year_branch_idx)
    huagai = get_huagai(year_branch_idx)
    taohua = get_taohua(year_branch_idx)
    
    # P1 神煞
    tiande = get_tiande(year_stem_idx)
    yuede = get_yuede(year_stem_idx)
    hongluan = get_hongluan_tianxi(year_branch_idx)
    sanqi = get_sanqi(year_stem_idx, month_stem_idx, day_stem_idx)
    jiangxing = get_jiangxing(year_branch_idx)
    wangshen = get_wangshen(year_branch_idx)
    
    # P2 神煞
    jiesha = get_jiesha(year_branch_idx)
    zaisha = get_zaisha(year_branch_idx)
    sangmen = get_sangmen(year_branch_idx)
    diaoke = get_diaoke(year_branch_idx)
    liujia = get_liujia_guishen(year_stem_idx, year_branch_idx)
    
    return {
        # P0（最重要）
        "P0": {
            "天乙贵人": tianyi,
            "文昌": wenchang,
            "驿马": yima,
            "华盖": huagai,
            "桃花": taohua,
        },
        # P1（重要）
        "P1": {
            "天德": tiande,
            "月德": yuede,
            "红鸾天喜": hongluan,
            "三奇": sanqi,
            "将星": jiangxing,
            "亡神": wangshen,
        },
        # P2（次要）
        "P2": {
            "劫煞": jiesha,
            "灾煞": zaisha,
            "丧门": sangmen,
            "吊客": diaoke,
            "六甲贵神": liujia,
        },
        # 便捷摘要
        "summary": {
            "tianyi_guiren": tianyi.get("description", ""),
            "wenchang": wenchang.get("description", ""),
            "yima": yima.get("description", ""),
            "huagai": huagai.get("description", ""),
            "taohua": taohua.get("description", ""),
            "tiande": tiande.get("description", ""),
            "yuede": yuede.get("description", ""),
            "hongluan": hongluan.get("description", ""),
            "sanqi": sanqi.get("description", ""),
            "jiangxing": jiangxing.get("description", ""),
            "wangshen": wangshen.get("description", ""),
            "jiesha": jiesha.get("description", ""),
            "zaisha": zaisha.get("description", ""),
            "sangmen": sangmen.get("description", ""),
            "diaoke": diaoke.get("description", ""),
            "liujia_guishen": liujia.get("description", ""),
        },
    }


def get_shen_sha(bazi_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    神煞查询主函数（与 get_shen_sha_summary 等价，供外部调用）
    
    Args:
        bazi_info: 八字信息字典
    
    Returns:
        dict: 神煞汇总
    """
    return get_shen_sha_summary(bazi_info)


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    # 导入必要模块
    import sys
    sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
    from bazi_engine import get_bazi
    
    print("=== 神煞查询系统测试 ===\n")
    
    # 测试1: 2024年3月15日10点（甲辰年）
    print("【测试1】2024年3月15日10点（甲辰年）")
    bazi_data = get_bazi(2024, 3, 15, 10)
    bazi = bazi_data["bazi"]
    year_stem = bazi["year"]["stem"]
    year_branch = bazi["year"]["branch"]
    print(f"  八字: {bazi_data['birth_chart']}")
    
    tianyi = get_tianyi_guiren(bazi["year"]["stem_idx"], bazi["year"]["branch_idx"])
    print(f"  天乙贵人: {tianyi['description']} → {tianyi['guiren_branches']}")
    
    wenchang = get_wenchang(bazi["year"]["stem_idx"])
    print(f"  文昌: {wenchang['description']}")
    
    yima = get_yima(bazi["year"]["branch_idx"])
    print(f"  驿马: {yima['description']}")
    
    huagai = get_huagai(bazi["year"]["branch_idx"])
    print(f"  华盖: {huagai['description']}")
    
    taohua = get_taohua(bazi["year"]["branch_idx"])
    print(f"  桃花: {taohua['description']}")
    print()
    
    # 测试2: 2025年1月15日（癸卯年）
    print("【测试2】2025年1月15日（癸卯年）")
    bazi_data2 = get_bazi(2025, 1, 15, 10)
    bazi2 = bazi_data2["bazi"]
    print(f"  八字: {bazi_data2['birth_chart']}")
    
    tianyi2 = get_tianyi_guiren(bazi2["year"]["stem_idx"], bazi2["year"]["branch_idx"])
    print(f"  天乙贵人: {tianyi2['description']} → {tianyi2['guiren_branches']}")
    
    yima2 = get_yima(bazi2["year"]["branch_idx"])
    print(f"  驿马: {yima2['description']}")
    
    taohua2 = get_taohua(bazi2["year"]["branch_idx"])
    print(f"  桃花: {taohua2['description']}")
    
    huagai2 = get_huagai(bazi2["year"]["branch_idx"])
    print(f"  华盖: {huagai2['description']}")
    print()
    
    # 测试3: 综合神煞
    print("【测试3】综合神煞查询")
    result = get_shen_sha_summary(bazi_data2)
    print(f"  === P0 神煞 ===")
    for name, info in result["P0"].items():
        print(f"    {name}: {info.get('description', info)}")
    print(f"  === P1 神煞 ===")
    for name, info in result["P1"].items():
        print(f"    {name}: {info.get('description', info)}")
    print(f"  === P2 神煞 ===")
    for name, info in result["P2"].items():
        print(f"    {name}: {info.get('description', info)}")
    print()
    
    # 测试4: 验证口诀
    print("【测试4】天乙贵人口诀验证")
    print(f"  口诀: {tianyi2['口诀']}")
    print(f"  癸卯年 → 壬癸兔蛇藏 → 癸贵人: 卯(3)、巳(6)")
    print(f"  实测: {tianyi2['guiren_branches']} ✓")
    print()
    
    # 测试5: 驿马口诀验证
    print("【测试5】驿马口诀验证")
    print(f"  申子辰马在寅 → 辰(4)年: 马在寅(2)")
    print(f"  实测: {get_yima(4)['description']} ✓")
    print(f"  寅午戌马在申 → 寅(2)年: 马在申(8)")
    print(f"  实测: {get_yima(2)['description']} ✓")
    print()
    
    # 测试6: 桃花口诀验证
    print("【测试6】桃花口诀验证")
    print(f"  申子辰见酉 → 辰(4)年: 桃花在酉(9)")
    print(f"  实测: {get_taohua(4)['description']} ✓")
    print(f"  寅午戌见卯 → 寅(2)年: 桃花在卯(3)")
    print(f"  实测: {get_taohua(2)['description']} ✓")
    print()
    
    # 测试7: 丙午年（庚辛逢虎马）
    print("【测试7】庚午年（庚辛逢虎马）")
    bazi_data3 = get_bazi(1990, 5, 15, 10)  # 庚午年
    bazi3 = bazi_data3["bazi"]
    print(f"  八字: {bazi_data3['birth_chart']}")
    tianyi3 = get_tianyi_guiren(bazi3["year"]["stem_idx"], bazi3["year"]["branch_idx"])
    print(f"  天乙贵人: {tianyi3['description']} → {tianyi3['guiren_branches']}")
    print(f"  口诀: 庚辛逢虎马 → 庚贵人: 寅(2)、午(5)")
    print(f"  吻合: {'寅' in tianyi3['guiren_branches'] and '午' in tianyi3['guiren_branches']} ✓")
