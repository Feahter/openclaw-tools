# -*- coding: utf-8 -*-
"""
小儿关煞系统 v1.0
==================
基于《渊海子平》《三命通会》小儿关煞体系：

一、激活条件类型
  - 四季诗关：按季节（春申/夏子/秋寅/冬午）
  - 天德/月德：按日柱纳音或天干方位
  - 鬼门关：农历七月生，时支见寅
  - 百日关：午年午月生
  - 阎王关：辰戌丑未年，日时冲破
  - 断桥关：卯酉月生，午卯时
  - 夜关煞：子午卯酉时生，逢六甲

二、化解方法
  - 祭祀、佩符、拜祭、诵经等

用法：
  from xiaor_xiansha import check_xiaor_xiansha
  result = check_xiaor_xiansha(bazi_dict)
"""

import sys
sys.path.insert(0, '.')

from typing import Dict, List, Optional, Any
from bazi_engine import get_bazi, get_nayin
from bazi_engine import HEAVENLY_STEMS as STEMS, EARTHLY_BRANCHES as BRANCHES


# ============================================================
# 工具函数
# ============================================================

def _stem_idx(stem_str: str) -> int:
    """天干字符串 → 索引 0-9"""
    return STEMS.index(stem_str) if stem_str in STEMS else -1


def _branch_idx(branch_str: str) -> int:
    """地支字符串 → 索引 0-11"""
    return BRANCHES.index(branch_str) if branch_str in BRANCHES else -1


def _branch_zodiac(branch_str: str) -> str:
    """地支 → 生肖"""
    zodiac_map = {
        "子": "鼠", "丑": "牛", "寅": "虎", "卯": "兔",
        "辰": "龙", "巳": "蛇", "午": "马", "未": "羊",
        "申": "猴", "酉": "鸡", "戌": "狗", "亥": "猪",
    }
    return zodiac_map.get(branch_str, "")


def _dayun_to_year_gans(yeardan: int, monthgan: int) -> int:
    """
    大运干支换算：以年干为基准，按阴阳排。
    这里用于判断年干阴阳，以确定某些关煞的阴阳属性。
    """
    stems = STEMS
    yang = [0, 2, 4, 6, 8]  # 甲丙戊庚壬
    yin = [1, 3, 5, 7, 9]  # 乙丁己辛癸
    if yeardan in yang:
        # 阳干：大运从月干起，顺排
        # 大运干 = (monthgan_idx + offset) % 10
        # 简化：返回年干阴阳
        return 0  # 阳
    return 1  # 阴


def _has_branch(bazi_dict: Dict, pillar: str, branch: str) -> bool:
    """判断某柱地支是否为指定地支"""
    return bazi_dict.get(pillar, {}).get("branch", "") == branch


def _has_stem(bazi_dict: Dict, pillar: str, stem: str) -> bool:
    """判断某柱天干是否为指定天干"""
    return bazi_dict.get(pillar, {}).get("stem", "") == stem


def _is_branch_in(bazi_dict: Dict, pillar: str, branches: List[str]) -> bool:
    """判断某柱地支是否在指定列表中"""
    b = bazi_dict.get(pillar, {}).get("branch", "")
    return b in branches


def _is_stem_in(bazi_dict: Dict, pillar: str, stems: List[str]) -> bool:
    """判断某柱天干是否在指定列表中"""
    s = bazi_dict.get(pillar, {}).get("stem", "")
    return s in stems


def _is_month_branch(bazi_dict: Dict, branch: str) -> bool:
    return bazi_dict.get("month", {}).get("branch", "") == branch


def _is_hour_branch(bazi_dict: Dict, branch: str) -> bool:
    return bazi_dict.get("hour", {}).get("branch", "") == branch


# ============================================================
# 关煞规则定义
# ============================================================

# 四季诗关：春关生人（生于春月），地支见申 → 凶
#          夏关生人（生于夏月），地支见子 → 凶
#          秋关生人（生于秋月），地支见寅 → 凶
#          冬关生人（生于冬月），地支见午 → 凶
XIAOR_RULES: List[Dict[str, Any]] = [

    # ---------- 1. 四季诗关 ----------
    {
        "id": "siji_shiguan",
        "name": "四季诗关",
        "alias": ["四季天关"],
        "severity": "重",
        "activation": {
            "春关": "春月（寅卯辰）生人，地支带申",
            "夏关": "夏月（巳午未）生人，地支带子",
            "秋关": "秋月（申酉戌）生人，地支带寅",
            "冬关": "冬月（亥子丑）生人，地支带午",
        },
        "check_fn": lambda b: _check_siji_shiguan(b),
        "化解": "春季挂ixon符，夏季挂太上符，秋季挂金光符，冬季挂玄元符；诵《太上老君说常清静经》",
        "note": "四季诗关以季节配地支，犯者读书聪明但妨读书运",
    },

    # ---------- 2. 天德 ----------
    {
        "id": "tiande",
        "name": "天德",
        "alias": ["天德吉星"],
        "severity": "吉",
        "activation": {
            "正月": "丁", "二月": "申", "三月": "丁",
            "四月": "亥", "五月": "壬", "六月": "寅",
            "七月": "癸", "八月": "丑", "九月": "艮",
            "十月": "甲", "十一月": "卯", "十二月": "戌",
        },
        "check_fn": lambda b: _check_tiande(b),
        "化解": "天德为吉星，逢凶化吉；生人带玉佩，行善积德即可",
        "note": "天德是吉星，入命主一生安稳，逢凶化吉",
    },

    # ---------- 3. 月德 ----------
    {
        "id": "yuede",
        "name": "月德",
        "alias": ["月德吉星"],
        "severity": "吉",
        "activation": {
            "寅午戌月": "丙",
            "申子辰月": "壬",
            "亥卯未月": "甲",
            "巳酉丑月": "庚",
        },
        "check_fn": lambda b: _check_yuede(b),
        "化解": "月德入命，化灾增福；行善布施，谨言慎行",
        "note": "月德与天德合用，化解百祸",
    },

    # ---------- 4. 鬼门关 ----------
    {
        "id": "guimen_guan",
        "name": "鬼门关",
        "alias": ["鬼门"],
        "severity": "重",
        "activation": {
            "条件": "午月（农历五月）生，时支见寅；或生于农历七月申时",
        },
        "check_fn": lambda b: _check_guimen_guan(b),
        "化解": "端午挂艾草、穿五色线；或请道观安魂符",
        "note": "鬼门关为凶关，犯者易被阴邪侵扰，须谨慎",
    },

    # ---------- 5. 百日关 ----------
    {
        "id": "bairi_guan",
        "name": "百日关",
        "alias": [],
        "severity": "重",
        "activation": {
            "条件": "午年（马年）生，又值午月；或甲戌年辛未月生",
        },
        "check_fn": lambda b: _check_bairi_guan(b),
        "化解": "百日关：以红绳系手腕，百日内不串门；诵《地藏经》",
        "note": "百日关需度过百日方解",
    },

    # ---------- 6. 阎王关 ----------
    {
        "id": "yanwang_guan",
        "name": "阎王关",
        "alias": ["阎罗关"],
        "severity": "重",
        "activation": {
            "条件": "辰、戌、丑、未年（龙/狗/牛/羊年）生，日时冲破",
        },
        "check_fn": lambda b: _check_yanwang_guan(b),
        "化解": "安太岁、拜土地公；或请地藏王菩萨符",
        "note": "阎王关犯者须早积阴德，成年后渐解",
    },

    # ---------- 7. 断桥关 ----------
    {
        "id": "duanqiao_guan",
        "name": "断桥关",
        "alias": [],
        "severity": "中",
        "activation": {
            "条件": "卯酉月生，时支午或子；或日柱为辛亥，时支子",
        },
        "check_fn": lambda b: _check_duanqiao_guan(b),
        "化解": "断桥关：拜桥神；或以木板造小桥模型供奉",
        "note": "断桥关主幼年行路跌仆，注意安全",
    },

    # ---------- 8. 夜关煞 ----------
    {
        "id": "yeguan_sha",
        "name": "夜关煞",
        "alias": ["夜关"],
        "severity": "中",
        "activation": {
            "条件": "子午卯酉时（夜23-1/11-13/5-7/17-19）生，见六甲",
        },
        "check_fn": lambda b: _check_yeguan_sha(b),
        "化解": "夜关煞：夜间不外出；床头放朱砂或桃木剑",
        "note": "夜关煞夜间宜静不宜动",
    },

    # ---------- 9. 短命关 ----------
    {
        "id": "duanming_guan",
        "name": "短命关",
        "alias": [],
        "severity": "重",
        "activation": {
            "条件": "年干为癸，地支为酉，时支为卯",
        },
        "check_fn": lambda b: _check_duanming_guan(b),
        "化解": "积德行善，佩带玉佩；成年后渐解",
        "note": "短命关为极凶关煞，须特别化解",
    },

    # ---------- 10. 鬼怪关 ----------
    {
        "id": "guiguai_guan",
        "name": "鬼怪关",
        "alias": [],
        "severity": "中",
        "activation": {
            "条件": "壬癸日生，地支见亥子；时支为丑",
        },
        "check_fn": lambda b: _check_guiguai_guan(b),
        "化解": "鬼怪关：端午烧纸钱、挂艾草；诵《金刚经》",
        "note": "鬼怪关犯者易见异梦",
    },

    # ---------- 11. 雷公关 ----------
    {
        "id": "leigong_guan",
        "name": "雷公关",
        "alias": [],
        "severity": "中",
        "activation": {
            "条件": "甲乙日生，时支见卯；或春月生卯时",
        },
        "check_fn": lambda b: _check_leigong_guan(b),
        "化解": "雷公关：打雷时躲室内；床头挂铜铃",
        "note": "雷公关主雷电之灾",
    },

    # ---------- 12. 汤火关 ----------
    {
        "id": "tanghuo_guan",
        "name": "汤火关",
        "alias": [],
        "severity": "中",
        "activation": {
            "条件": "丙丁日生，或地支见巳午；时支见卯",
        },
        "check_fn": lambda b: _check_tanghuo_guan(b),
        "化解": "汤火关：远离火源；随身带水，床头放水杯",
        "note": "汤火关主火热水烫之灾",
    },

    # ---------- 13. 翻身关 ----------
    {
        "id": "fanshen_guan",
        "name": "翻身关",
        "alias": [],
        "severity": "轻",
        "activation": {
            "条件": "丑未年日生，时支见子",
        },
        "check_fn": lambda b: _check_fanshen_guan(b),
        "化解": "翻身关：农历三月初三祭祖；拜土地公",
        "note": "翻身关幼年多灾，成年后渐顺",
    },

    # ---------- 14. 取命关 ----------
    {
        "id": "quming_guan",
        "name": "取命关",
        "alias": [],
        "severity": "重",
        "activation": {
            "条件": "年支为亥，日支为巳，时支为亥",
        },
        "check_fn": lambda b: _check_quming_guan(b),
        "化解": "取命关：请道士作福；佩带护身符",
        "note": "取命关为极凶关，务必化解",
    },

    # ---------- 15. 白虎关 ----------
    {
        "id": "baihu_guan",
        "name": "白虎关",
        "alias": [],
        "severity": "重",
        "activation": {
            "条件": "庚辛日生，地支见申酉；时支见卯",
        },
        "check_fn": lambda b: _check_baihu_guan(b),
        "化解": "白虎关：安奉白虎符；行善积德",
        "note": "白虎为凶神，犯者多血光之灾",
    },

    # ---------- 16. 铁蛇关 ----------
    {
        "id": "tieshe_guan",
        "name": "铁蛇关",
        "alias": [],
        "severity": "中",
        "activation": {
            "条件": "辛丑日生，时支见辰；或壬癸日生",
        },
        "check_fn": lambda b: _check_tieshe_guan(b),
        "化解": "铁蛇关：带铁器；床头放剪刀",
        "note": "铁蛇关主金属伤灾",
    },

    # ---------- 17. 将军关 ----------
    {
        "id": "jiangjun_guan",
        "name": "将军关",
        "alias": [],
        "severity": "重",
        "activation": {
            "条件": "甲戊年日生，时支见丑；或丙丁日生时支午",
        },
        "check_fn": lambda b: _check_jiangjun_guan(b),
        "化解": "将军关：安奉关帝符；行善积德，谨言慎行",
        "note": "将军关犯者多官非口舌",
    },

    # ---------- 18. 丧门关 ----------
    {
        "id": "sangmen_guan",
        "name": "丧门关",
        "alias": [],
        "severity": "重",
        "activation": {
            "条件": "子年正月生；或丑年寅月生，时支见卯",
        },
        "check_fn": lambda b: _check_sangmen_guan(b),
        "化解": "丧门关：当年不探病、送葬；带孝化解",
        "note": "丧门关主丧孝之事，犯年应避",
    },

    # ---------- 19. 桃花关 ----------
    {
        "id": "taohua_guan",
        "name": "桃花关",
        "alias": [],
        "severity": "轻",
        "activation": {
            "条件": "日支为亥卯未之一，时支见子；或日支为子午卯酉之一",
        },
        "check_fn": lambda b: _check_taohua_guan(b),
        "化解": "桃花关：感情顺利；积德行善",
        "note": "桃花关主幼年感情早现",
    },

    # ---------- 20. 天狗关 ----------
    {
        "id": "tiangou_guan",
        "name": "天狗关",
        "alias": [],
        "severity": "中",
        "activation": {
            "条件": "酉年酉月酉日生；或午年子月生",
        },
        "check_fn": lambda b: _check_tiangou_guan(b),
        "化解": "天狗关：逢酉年躲星；诵《太上三元赐福消灾经》",
        "note": "天狗关主口舌官非",
    },
]


# ============================================================
# 具体检查函数
# ============================================================

def _check_siji_shiguan(b: Dict) -> Optional[Dict]:
    """四季诗关：春关申、夏关子、秋关寅、冬关午"""
    month_branch = b.get("month", {}).get("branch", "")
    branches = [
        b.get("year", {}).get("branch", ""),
        b.get("month", {}).get("branch", ""),
        b.get("day", {}).get("branch", ""),
        b.get("hour", {}).get("branch", ""),
    ]
    season_map = {
        "寅": ("卯", "辰"),  # 春
        "巳": ("午", "未"),  # 夏
        "申": ("酉", "戌"),  # 秋
        "亥": ("子", "丑"),  # 冬
    }
    for season_branch, season_siblings in season_map.items():
        if month_branch == season_branch or month_branch in season_siblings:
            # 春月见申、夏月见子、秋月见寅、冬月见午
            trigger_map = {"寅": "申", "卯": "申", "辰": "申",
                           "巳": "子", "午": "子", "未": "子",
                           "申": "寅", "酉": "寅", "戌": "寅",
                           "亥": "午", "子": "午", "丑": "午"}
            if month_branch in trigger_map:
                trigger = trigger_map[month_branch]
                if trigger in branches:
                    season_names = {"寅": "春关", "卯": "春关", "辰": "春关",
                                    "巳": "夏关", "午": "夏关", "未": "夏关",
                                    "申": "秋关", "酉": "秋关", "戌": "秋关",
                                    "亥": "冬关", "子": "冬关", "丑": "冬关"}
                    return {"active": True, "name": f"四季诗关-{season_names[month_branch]}", "trigger": f"地支见{trigger}"}
    return None


def _check_tiande(b: Dict) -> Optional[Dict]:
    """天德：正月丁、二三月申/丁、四月亥/壬、五月子、六月寅/癸、七八月丑/艮、九十月卯/甲、十一十二月戌/辛"""
    month_branch = b.get("month", {}).get("branch", "")
    month_stem = b.get("month", {}).get("stem", "")
    month_branch_idx = _branch_idx(month_branch)
    # 天德表：按月支索引（0=子...11=亥）
    tiande_map = {
        0: "丁",   # 子月
        2: "申",   # 寅月
        3: "丁",   # 卯月
        4: "亥",   # 辰月
        5: "壬",   # 巳月
        7: "癸",   # 午月（实际是6=午，但按传统这里用7=未的替代）
        9: "丑",   # 申月
        10: "艮",  # 酉月
        11: "卯",  # 戌月
        1: "甲",   # 丑月
    }
    # 更准确的天德表（按十二宫）
    tiande_correct = {
        "子": "丁", "丑": "癸", "寅": "申", "卯": "丁",
        "辰": "亥", "巳": "壬", "午": "寅", "未": "癸",
        "申": "丑", "酉": "艮", "戌": "甲", "亥": "辛",
    }
    expected = tiande_correct.get(month_branch, "")
    if not expected:
        return None
    # 检查日柱天干是否为天德天干（简化：直接查月支）
    day_stem = b.get("day", {}).get("stem", "")
    day_branch = b.get("day", {}).get("branch", "")
    # 天德查日干，以月支为主
    # 原文："天德在丁" 即月支为子时，日干为丁 → 激活
    # 简化：月支为子且日干为丁 → 天德
    if month_branch == "子" and day_stem == "丁":
        return {"active": True, "name": "天德", "trigger": f"子月日干为丁"}
    if month_branch == "寅" and day_stem == "甲":
        return {"active": True, "name": "天德", "trigger": f"寅月日干为甲"}
    if month_branch == "卯" and day_stem == "丁":
        return {"active": True, "name": "天德", "trigger": f"卯月日干为丁"}
    if month_branch == "辰" and day_stem == "壬":
        return {"active": True, "name": "天德", "trigger": f"辰月日干为壬"}
    if month_branch == "巳" and day_stem == "丙":
        return {"active": True, "name": "天德", "trigger": f"巳月日干为丙"}
    if month_branch == "午" and day_stem == "寅":
        return {"active": True, "name": "天德", "trigger": f"午月日干为寅"}
    if month_branch == "未" and day_stem == "己":
        return {"active": True, "name": "天德", "trigger": f"未月日干为己"}
    if month_branch == "申" and day_stem == "庚":
        return {"active": True, "name": "天德", "trigger": f"申月日干为庚"}
    if month_branch == "酉" and day_stem == "丁":
        return {"active": True, "name": "天德", "trigger": f"酉月日干为丁"}
    if month_branch == "戌" and day_stem == "辛":
        return {"active": True, "name": "天德", "trigger": f"戌月日干为辛"}
    if month_branch == "亥" and day_stem == "甲":
        return {"active": True, "name": "天德", "trigger": f"亥月日干为甲"}
    if month_branch == "丑" and day_stem == "癸":
        return {"active": True, "name": "天德", "trigger": f"丑月日干为癸"}
    return None


def _check_yuede(b: Dict) -> Optional[Dict]:
    """月德：寅午戌月→丙，申子辰月→壬，亥卯未月→甲，巳酉丑月→庚"""
    month_branch = b.get("month", {}).get("branch", "")
    day_stem = b.get("day", {}).get("stem", "")
    yuede_map = {
        "寅": "丙", "午": "丙", "戌": "丙",
        "申": "壬", "子": "壬", "辰": "壬",
        "亥": "甲", "卯": "甲", "未": "甲",
        "巳": "庚", "酉": "庚", "丑": "庚",
    }
    expected_stem = yuede_map.get(month_branch, "")
    if expected_stem and day_stem == expected_stem:
        return {"active": True, "name": "月德", "trigger": f"{month_branch}月日干为{day_stem}"}
    return None


def _check_guimen_guan(b: Dict) -> Optional[Dict]:
    """鬼门关：午月生，时支见寅；或农历七月申时"""
    month_branch = b.get("month", {}).get("branch", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    year_branch = b.get("year", {}).get("branch", "")
    # 条件1：午月（农历五月）生，时支见寅
    if month_branch == "午" and hour_branch == "寅":
        return {"active": True, "name": "鬼门关", "trigger": "午月生时支见寅"}
    # 条件2：七月申时生
    if month_branch == "申" and hour_branch == "申":
        return {"active": True, "name": "鬼门关", "trigger": "申月申时生"}
    # 条件3：申年申月申时（特殊）→ 鬼门关三重
    if year_branch == "申" and month_branch == "申" and hour_branch == "申":
        return {"active": True, "name": "鬼门关", "trigger": "申年申月申时，三申鬼门"}
    return None


def _check_bairi_guan(b: Dict) -> Optional[Dict]:
    """百日关：午年（马年）生，又值午月"""
    year_branch = b.get("year", {}).get("branch", "")
    month_branch = b.get("month", {}).get("branch", "")
    if year_branch == "午" and month_branch == "午":
        return {"active": True, "name": "百日关", "trigger": "午年午月生"}
    # 补充：甲戌年辛未月
    year_stem = b.get("year", {}).get("stem", "")
    month_stem = b.get("month", {}).get("stem", "")
    if year_stem == "甲" and year_branch == "戌" and month_stem == "辛" and month_branch == "未":
        return {"active": True, "name": "百日关", "trigger": "甲戌年辛未月生"}
    return None


def _check_yanwang_guan(b: Dict) -> Optional[Dict]:
    """阎王关：辰戌丑未年，日时冲破"""
    year_branch = b.get("year", {}).get("branch", "")
    day_branch = b.get("day", {}).get("branch", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if year_branch not in ("辰", "戌", "丑", "未"):
        return None
    # 冲破：日支与时支相冲（子午冲、丑未冲、寅申冲、卯酉冲、辰戌冲、巳亥冲）
    clash_map = {
        "子": "午", "午": "子",
        "丑": "未", "未": "丑",
        "寅": "申", "申": "寅",
        "卯": "酉", "酉": "卯",
        "辰": "戌", "戌": "辰",
        "巳": "亥", "亥": "巳",
    }
    if clash_map.get(day_branch) == hour_branch:
        return {"active": True, "name": "阎王关", "trigger": f"{year_branch}年日时冲破"}
    # 辰戌丑未年，日支为辰戌丑未，时支为丑未辰戌 → 阎王关
    if day_branch in ("辰", "戌", "丑", "未") and hour_branch in ("辰", "戌", "丑", "未"):
        return {"active": True, "name": "阎王关", "trigger": f"{year_branch}年日时皆为墓库"}
    return None


def _check_duanqiao_guan(b: Dict) -> Optional[Dict]:
    """断桥关：卯酉月生，时支午或子"""
    month_branch = b.get("month", {}).get("branch", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if month_branch in ("卯", "酉") and hour_branch in ("午", "子"):
        return {"active": True, "name": "断桥关", "trigger": f"{month_branch}月{hour_branch}时"}
    # 补充：日柱辛亥，时支子
    day_stem = b.get("day", {}).get("stem", "")
    day_branch = b.get("day", {}).get("branch", "")
    if day_stem == "辛" and day_branch == "亥" and hour_branch == "子":
        return {"active": True, "name": "断桥关", "trigger": "辛亥日子时"}
    return None


def _check_yeguan_sha(b: Dict) -> Optional[Dict]:
    """夜关煞：子午卯酉时生，见六甲"""
    hour_branch = b.get("hour", {}).get("branch", "")
    hour_stem = b.get("hour", {}).get("stem", "")
    year_stem = b.get("year", {}).get("stem", "")
    if hour_branch in ("子", "午", "卯", "酉"):
        # 逢六甲（年干为甲）
        if year_stem == "甲":
            return {"active": True, "name": "夜关煞", "trigger": f"{hour_branch}时生逢六甲"}
        # 子午卯酉时生 + 夜关
        return {"active": True, "name": "夜关煞", "trigger": f"{hour_branch}时生（夜时）"}
    return None


def _check_duanming_guan(b: Dict) -> Optional[Dict]:
    """短命关：年干为癸，地支为酉"""
    year_stem = b.get("year", {}).get("stem", "")
    year_branch = b.get("year", {}).get("branch", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if year_stem == "癸" and year_branch == "酉" and hour_branch == "卯":
        return {"active": True, "name": "短命关", "trigger": "癸酉年卯时"}
    if year_stem == "癸" and year_branch == "酉":
        return {"active": True, "name": "短命关", "trigger": "癸酉年生"}
    return None


def _check_guiguai_guan(b: Dict) -> Optional[Dict]:
    """鬼怪关：壬癸日生，地支见亥子；时支为丑"""
    day_stem = b.get("day", {}).get("stem", "")
    day_branch = b.get("day", {}).get("branch", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if day_stem in ("壬", "癸") and day_branch in ("亥", "子") and hour_branch == "丑":
        return {"active": True, "name": "鬼怪关", "trigger": f"{day_stem}{day_branch}日子时"}
    return None


def _check_leigong_guan(b: Dict) -> Optional[Dict]:
    """雷公关：甲乙日生，时支见卯"""
    day_stem = b.get("day", {}).get("stem", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    month_branch = b.get("month", {}).get("branch", "")
    if day_stem in ("甲", "乙") and hour_branch == "卯":
        return {"active": True, "name": "雷公关", "trigger": f"{day_stem}日卯时"}
    if month_branch in ("寅", "卯", "辰") and hour_branch == "卯":
        return {"active": True, "name": "雷公关", "trigger": f"春月卯时"}
    return None


def _check_tanghuo_guan(b: Dict) -> Optional[Dict]:
    """汤火关：丙丁日生，时支见卯"""
    day_stem = b.get("day", {}).get("stem", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if day_stem in ("丙", "丁") and hour_branch == "卯":
        return {"active": True, "name": "汤火关", "trigger": f"{day_stem}日卯时"}
    day_branch = b.get("day", {}).get("branch", "")
    if day_branch in ("巳", "午") and hour_branch == "卯":
        return {"active": True, "name": "汤火关", "trigger": f"火日{day_branch}生卯时"}
    return None


def _check_fanshen_guan(b: Dict) -> Optional[Dict]:
    """翻身关：丑未年日生，时支见子"""
    year_branch = b.get("year", {}).get("branch", "")
    day_branch = b.get("day", {}).get("branch", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if year_branch in ("丑", "未") and hour_branch == "子":
        return {"active": True, "name": "翻身关", "trigger": f"{year_branch}年子时生"}
    if day_branch in ("丑", "未") and hour_branch == "子":
        return {"active": True, "name": "翻身关", "trigger": f"日支{day_branch}子时"}
    return None


def _check_quming_guan(b: Dict) -> Optional[Dict]:
    """取命关：年支为亥，日支为巳，时支为亥"""
    year_branch = b.get("year", {}).get("branch", "")
    day_branch = b.get("day", {}).get("branch", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if year_branch == "亥" and day_branch == "巳" and hour_branch == "亥":
        return {"active": True, "name": "取命关", "trigger": "亥年巳日亥时，三刑全"}
    if year_branch == "亥" and hour_branch == "亥":
        return {"active": True, "name": "取命关", "trigger": "亥年亥时"}
    return None


def _check_baihu_guan(b: Dict) -> Optional[Dict]:
    """白虎关：庚辛日生，地支见申酉；时支见卯"""
    day_stem = b.get("day", {}).get("stem", "")
    day_branch = b.get("day", {}).get("branch", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if day_stem in ("庚", "辛") and day_branch in ("申", "酉") and hour_branch == "卯":
        return {"active": True, "name": "白虎关", "trigger": f"{day_stem}{day_branch}日卯时"}
    return None


def _check_tieshe_guan(b: Dict) -> Optional[Dict]:
    """铁蛇关：辛丑日生，时支见辰；壬癸日生"""
    day_stem = b.get("day", {}).get("stem", "")
    day_branch = b.get("day", {}).get("branch", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if day_stem == "辛" and day_branch == "丑" and hour_branch == "辰":
        return {"active": True, "name": "铁蛇关", "trigger": "辛丑日辰时"}
    if day_stem in ("壬", "癸") and hour_branch == "辰":
        return {"active": True, "name": "铁蛇关", "trigger": f"{day_stem}日辰时"}
    return None


def _check_jiangjun_guan(b: Dict) -> Optional[Dict]:
    """将军关：甲戊年日生，时支见丑；丙丁日生时支午"""
    year_stem = b.get("year", {}).get("stem", "")
    day_stem = b.get("day", {}).get("stem", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if year_stem in ("甲", "戊") and hour_branch == "丑":
        return {"active": True, "name": "将军关", "trigger": f"{year_stem}年丑时生"}
    if day_stem in ("丙", "丁") and hour_branch == "午":
        return {"active": True, "name": "将军关", "trigger": f"{day_stem}日午时"}
    return None


def _check_sangmen_guan(b: Dict) -> Optional[Dict]:
    """丧门关：子年正月生；丑年寅月生，时支见卯"""
    year_branch = b.get("year", {}).get("branch", "")
    month_branch = b.get("month", {}).get("branch", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if year_branch == "子" and month_branch == "寅":
        return {"active": True, "name": "丧门关", "trigger": "子年寅月生"}
    if year_branch == "丑" and month_branch == "寅" and hour_branch == "卯":
        return {"active": True, "name": "丧门关", "trigger": "丑年寅月卯时"}
    return None


def _check_taohua_guan(b: Dict) -> Optional[Dict]:
    """桃花关：日支为亥卯未之一，时支见子；或日支为子午卯酉之一"""
    day_branch = b.get("day", {}).get("branch", "")
    hour_branch = b.get("hour", {}).get("branch", "")
    if day_branch in ("亥", "卯", "未") and hour_branch == "子":
        return {"active": True, "name": "桃花关", "trigger": f"{day_branch}日子时，桃花入命"}
    if day_branch in ("子", "午", "卯", "酉"):
        return {"active": True, "name": "桃花关", "trigger": f"日支{day_branch}，四桃花"}
    return None


def _check_tiangou_guan(b: Dict) -> Optional[Dict]:
    """天狗关：酉年酉月酉日生；午年子月生"""
    year_branch = b.get("year", {}).get("branch", "")
    month_branch = b.get("month", {}).get("branch", "")
    day_branch = b.get("day", {}).get("branch", "")
    if year_branch == "酉" and month_branch == "酉" and day_branch == "酉":
        return {"active": True, "name": "天狗关", "trigger": "酉年酉月酉日，三酉天狗"}
    if year_branch == "午" and month_branch == "子":
        return {"active": True, "name": "天狗关", "trigger": "午年子月生"}
    return None


# ============================================================
# 主函数
# ============================================================

def check_xiaor_xiansha(birth_info: Dict) -> List[Dict]:
    """
    检查小儿关煞

    参数:
        birth_info: 八字排盘字典，包含 year/month/day/hour 四柱，
                    每柱有 stem（天干）、branch（地支）、stem_idx、branch_idx

    返回:
        list[dict]: 激活的关煞列表，每项包含：
            - id: 关煞ID
            - name: 关煞名称
            - severity: 轻重（重/中/轻/吉）
            - trigger: 触发说明
            - 化解: 化解方法
            - note: 备注
    """
    active_list: List[Dict] = []

    for rule in XIAOR_RULES:
        result = rule["check_fn"](birth_info)
        if result and result.get("active"):
            active_list.append({
                "id": rule["id"],
                "name": result.get("name", rule["name"]),
                "severity": rule["severity"],
                "trigger": result.get("trigger", ""),
                "化解": rule["化解"],
                "note": rule["note"],
            })

    # 按 severity 排序：重 > 中 > 轻 > 吉
    severity_order = {"重": 0, "中": 1, "轻": 2, "吉": 3}
    active_list.sort(key=lambda x: severity_order.get(x["severity"], 9))

    return active_list


def check_xiaor_xiansha_from_birthtime(
    year: int, month: int, day: int, hour: int,
    gender: str = "男",
    lunar: bool = False,
    province: str = "北京",
    city: str = "北京",
) -> Dict:
    """
    从出生时间直接检查小儿关煞（与八字系统集成）

    参数:
        year/month/day/hour: 出生时间
        gender: 性别（男/女）
        lunar: 是否农历
        province/city: 出生地区（用于真太阳时计算）

    返回:
        dict: 包含 bazi（八字信息）和 xiansha（关煞列表）
    """
    bazi_data = get_bazi(year, month, day, hour,
                          province=province, city=city)
    bazi_inner = bazi_data["bazi"]
    xiansha = check_xiaor_xiansha(bazi_inner)

    return {
        "birth_chart": bazi_data.get("birth_chart", ""),
        "gender": gender,
        "bazi": {
            "year": f"{bazi_inner['year']['stem']}{bazi_inner['year']['branch']}",
            "month": f"{bazi_inner['month']['stem']}{bazi_inner['month']['branch']}",
            "day": f"{bazi_inner['day']['stem']}{bazi_inner['day']['branch']}",
            "hour": f"{bazi_inner['hour']['stem']}{bazi_inner['hour']['branch']}",
        },
        "xiansha": xiansha,
        "summary": _build_summary(xiansha),
    }


def _build_summary(xiansha: List[Dict]) -> str:
    """生成关煞摘要"""
    if not xiansha:
        return "无小儿关煞，根基平稳。"
    severe = [s for s in xiansha if s["severity"] == "重"]
    medium = [s for s in xiansha if s["severity"] == "中"]
    light = [s for s in xiansha if s["severity"] == "轻"]
    lucky = [s for s in xiansha if s["severity"] == "吉"]

    parts = []
    if severe:
        parts.append(f"【重关】{'、'.join(s['name'] for s in severe)}")
    if medium:
        parts.append(f"【中关】{'、'.join(s['name'] for s in medium)}")
    if light:
        parts.append(f"【轻关】{'、'.join(s['name'] for s in light)}")
    if lucky:
        parts.append(f"【吉星】{'、'.join(s['name'] for s in lucky)}")

    return "；".join(parts)


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=== 小儿关煞测试 ===\n")

    # 测试1：普通情况
    result = check_xiaor_xiansha_from_birthtime(2021, 6, 12, 14, province="四川", city="成都")
    print(f"八字: {result['birth_chart']}")
    print(f"四柱: {result['bazi']}")
    print(f"关煞摘要: {result['summary']}")
    if result["xiansha"]:
        print("小儿关煞一览：")
        for s in result["xiansha"]:
            print(f"  [{s['severity']}] {s['name']} — {s['trigger']}")
            print(f"       化解：{s['化解']}")
    else:
        print("无小儿关煞")
    print()

    # 测试2：癸酉年（短命关测试）
    result2 = check_xiaor_xiansha_from_birthtime(1933, 9, 23, 5)
    print(f"癸酉年测试: {result2['summary']}")
    if result2["xiansha"]:
        for s in result2["xiansha"]:
            print(f"  [{s['severity']}] {s['name']} — {s['trigger']}")
    print()

    # 测试3：午年午月（百日关测试）
    result3 = check_xiaor_xiansha_from_birthtime(2026, 6, 1, 10)
    print(f"午年午月测试: {result3['summary']}")
    if result3["xiansha"]:
        for s in result3["xiansha"]:
            print(f"  [{s['severity']}] {s['name']} — {s['trigger']}")
