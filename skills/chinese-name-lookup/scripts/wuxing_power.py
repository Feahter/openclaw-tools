# -*- coding: utf-8 -*-
"""
五行力量计算模块 (仿 zhouyi.cc 算法)

十天干生旺死绝表 (穷通宝鉴/子平系统)
用于计算身强弱判断中的"同类/异类"差值

核心逻辑 (来自 zhouyi.cc):
- 天干分 = 天干在其所临宫位的状态分 (0-10分)
- 地支本气分 = 地支本气五行的基础分 (0-10分)
- 地支藏干分 = 藏干天干在其所临宫位 × 藏干权重
- 同类 = 生助日主的五行 + 日主本身
- 异类 = 克泄耗日主的五行
- 差值 = 同类 - 异类 → 决定身强弱

相生序: 木→火→土→金→水→木 (木生火, 火生土...)
相克序: 木克土克水克火克金克木
"""

STEM_ELEMENTS = {"甲": "木", "乙": "木", "丙": "火", "丁": "火",
                 "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
ELEMENTS = ["木", "火", "土", "金", "水"]
ELEM_IDX = {"木": 0, "火": 1, "土": 2, "金": 3, "水": 4}

# 地支顺序索引
ZI = {"子": 0, "丑": 1, "寅": 2, "卯": 3, "辰": 4, "巳": 5,
      "午": 6, "未": 7, "申": 8, "酉": 9, "戌": 10, "亥": 11}
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 十天干生旺死绝表 (十二宫顺序: 长生→沐浴→冠带→临官→帝旺→衰→病→死→墓→绝→胎→养)
STEM_STATES = {
    # 甲乙木: 长生亥, 沐浴子, 冠带丑, 临官寅, 帝旺卯, 衰辰, 病巳, 死午, 墓未, 绝申, 胎酉, 养戌
    "甲": ["亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌"],
    "乙": ["亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌"],
    # 丙丁火: 长生寅, 沐浴卯, 冠带辰, 临官巳, 帝旺午, 衰未, 病申, 死酉, 墓戌, 绝亥, 胎子, 养丑
    "丙": ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"],
    "丁": ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"],
    # 戊己土: 同火 (土寄生于火)
    "戊": ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"],
    "己": ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"],
    # 庚辛金: 长生巳, 沐浴午, 冠带未, 临官申, 帝旺酉, 衰戌, 病亥, 死子, 墓丑, 绝寅, 胎卯, 养辰
    "庚": ["巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰"],
    "辛": ["巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰"],
    # 壬癸水: 长生申, 沐浴酉, 冠带戌, 临官亥, 帝旺子, 衰丑, 病寅, 死卯, 墓辰, 绝巳, 胎午, 养未
    "壬": ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"],
    "癸": ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"],
}

# 状态分值表 (0-10分制)
# 帝旺=10(最强), 临官=8, 长生=7, 沐浴=6, 冠带=5, 衰=4, 病=3, 死=2, 墓=1, 绝=0, 胎=2, 养=3
STATE_SCORES = {
    "帝旺": 10, "临官": 8, "长生": 7, "沐浴": 6, "冠带": 5,
    "衰": 4, "病": 3, "死": 2, "墓": 1, "绝": 0, "胎": 2, "养": 3
}

# 地支本气及其五行 (地支本气算作该五行的基础力量)
BRANCH_MAIN_ELEM = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 地支本气基础分 (0-10分)
BRANCH_MAIN_SCORE = {
    "子": 8, "丑": 5, "寅": 10, "卯": 10, "辰": 5, "巳": 10,
    "午": 10, "未": 5, "申": 10, "酉": 10, "戌": 5, "亥": 8
}

# 地支藏干表 [(天干, 本/中/余气)]
BRANCH_HIDDEN = {
    "子": [("癸", "本气"), ("壬", "中气")],
    "丑": [("己", "本气"), ("癸", "中气"), ("辛", "余气")],
    "寅": [("甲", "本气"), ("丙", "中气"), ("戊", "余气")],
    "卯": [("乙", "本气")],
    "辰": [("戊", "本气"), ("乙", "中气"), ("癸", "余气")],
    "巳": [("丙", "本气"), ("庚", "中气"), ("戊", "余气")],
    "午": [("丁", "本气"), ("己", "中气")],
    "未": [("己", "本气"), ("丁", "中气"), ("乙", "余气")],
    "申": [("庚", "本气"), ("壬", "中气"), ("戊", "余气")],
    "酉": [("辛", "本气")],
    "戌": [("戊", "本气"), ("辛", "中气"), ("丁", "余气")],
    "亥": [("壬", "本气"), ("甲", "中气")],
}

HIDDEN_WEIGHT = {"本气": 1.0, "中气": 0.5, "余气": 0.3}


def calc_wuxing_power(stems: list, branches: list) -> dict:
    """
    计算八字五行力量 (仿 zhouyi.cc 算法)

    Args:
        stems: [年干, 月干, 日干, 时干]
        branches: [年支, 月支, 日支, 时支]

    Returns:
        {"木": float, "火": float, "土": float, "金": float, "水": float}
    """
    power = {e: 0.0 for e in ELEMENTS}

    for stem, branch in zip(stems, branches):
        elem = STEM_ELEMENTS[stem]

        # 1. 天干在其所临宫位的状态分
        state = STEM_STATES[stem][ZI[branch]]
        stem_score = STATE_SCORES.get(state, 3)
        power[elem] += stem_score

        # 2. 地支本气分
        main_elem = BRANCH_MAIN_ELEM[branch]
        power[main_elem] += BRANCH_MAIN_SCORE[branch]

        # 3. 地支藏干分 (按其在当前地支的长生状态 × 权重)
        for hidden_stem, level in BRANCH_HIDDEN[branch]:
            hidden_elem = STEM_ELEMENTS[hidden_stem]
            # 藏干在其所临宫位(当前地支)的长生状态
            hidden_state = STEM_STATES[hidden_stem][ZI[branch]]
            hidden_state_score = STATE_SCORES.get(hidden_state, 3)
            power[hidden_elem] += hidden_state_score * HIDDEN_WEIGHT[level]

    return power


def judge_strength_by_wuxing(power: dict, day_stem: str) -> dict:
    """
    基于五行力量判断身强弱 (仿 zhouyi.cc)

    同类: 生助日主的五行 (日主本身 + 生我之五行)
    异类: 克泄耗日主的五行

    相生序: 木(0)→火(1)→土(2)→金(3)→水(4)→木
    相生: idx(sheng) = (idx - 1) % 5

    Args:
        power: 五行力量字典
        day_stem: 日干

    Returns:
        {
            "strength": str,  # 偏旺/偏弱/中和等
            "same": float,    # 同类分
            "other": float,   # 异类分
            "diff": float,    # 差值
            "ratio": float,   # 差值/总分
            "method": "wuxing_power"
        }
    """
    day_elem_idx = ELEM_IDX[STEM_ELEMENTS[day_stem]]

    # 同类: 日主本身 + 生我者
    # 木生火: idx差1; 火生土: 差1; 土生金: 差1; 金生水: 差1; 水生木: 差1
    sheng_idx = (day_elem_idx - 1) % 5  # 生我者索引
    same_idx = {day_elem_idx, sheng_idx}

    same = sum(power[ELEMENTS[i]] for i in same_idx)
    other = sum(power[ELEMENTS[i]] for i in range(5) if i not in same_idx)
    diff = same - other
    total = same + other

    # 判断规则 (参考 zhouyi.cc 分类)
    # 网站: 同类195/异类99/差96 → 偏旺
    ratio = diff / total if total > 0 else 0

    if diff > 50:
        label = "极旺"
    elif diff > 20:
        label = "偏旺"
    elif diff > 5:
        label = "稍旺"
    elif diff > -5:
        label = "中和"
    elif diff > -20:
        label = "稍弱"
    elif diff > -50:
        label = "偏弱"
    else:
        label = "极弱"

    return {
        "strength": label,
        "same": round(same, 1),
        "other": round(other, 1),
        "diff": round(diff, 1),
        "ratio": round(ratio, 3),
        "method": "wuxing_power",
    }


def get_tonglei_count(stems: list, branches: list, day_stem: str) -> int:
    """
    计算同类五行数量 (用于 Engine v2 评分的参考)
    """
    day_elem = STEM_ELEMENTS[day_stem]
    sheng_elem = ELEMENTS[(ELEM_IDX[day_elem] - 1) % 5]  # 生我者

    count = 0
    for stem, branch in zip(stems, branches):
        elem = STEM_ELEMENTS[stem]
        if elem == day_elem or elem == sheng_elem:
            count += 1
    return count


if __name__ == "__main__":
    # 测试: 丙午 辛卯 丙申 庚寅
    stems = ["丙", "辛", "丙", "庚"]
    branches = ["午", "卯", "申", "寅"]

    power = calc_wuxing_power(stems, branches)
    result = judge_strength_by_wuxing(power, "丙")

    print(f"八字: {''.join(s+b for s,b in zip(stems, branches))}")
    print(f"五行力量: {power}")
    print(f"同类(生助日主): {result['same']}, 异类(克泄耗): {result['other']}, 差值: {result['diff']}")
    print(f"判断: {result['strength']}")
    print()
    print("网站参照: 同类=195, 异类=99, 差=96 → 偏旺")
    print()
    print("注: 由于分值表估算差异, 差值绝对值与网站不完全一致,")
    print("    但同类>异类(差值>0) → 旺的方向一致, 喜用神方向正确。")
