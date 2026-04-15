#!/usr/bin/env python3
"""
五行力量计算模块 (仿 zhouyi.cc 算法)

十天干生旺死绝表 (穷通宝鉴/子平系统)
"""

STEM_ELEMENTS = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
ELEMENTS = ["木", "火", "土", "金", "水"]

# 地支顺序索引
ZI = {"子":0,"丑":1,"寅":2,"卯":3,"辰":4,"巳":5,"午":6,"未":7,"申":8,"酉":9,"戌":10,"亥":11}

# 十天干生旺死绝表 (长生十二宫顺序)
# 甲乙木: 长生亥→子→丑→寅(临官)→卯(帝旺)→辰(衰)→巳(病)→午(死)→未(墓)→申(绝)→酉(胎)→戌(养)
# 丙丁火: 长生寅→卯→辰→巳(临官)→午(帝旺)→未(衰)→申(病)→酉(死)→戌(墓)→亥(绝)→子(胎)→丑(养)
# 庚辛金: 长生巳→午→未→申(临官)→酉(帝旺)→戌(衰)→亥(病)→子(死)→丑(墓)→寅(绝)→卯(胎)→辰(养)
# 壬癸水: 长生申→酉→戌→亥(临官)→子(帝旺)→丑(衰)→寅(病)→卯(死)→辰(墓)→巳(绝)→午(胎)→未(养)

STEM_STATES = {
    "甲": ["亥","子","丑","寅","卯","辰","巳","午","未","申","酉","戌"],
    "乙": ["亥","子","丑","寅","卯","辰","巳","午","未","申","酉","戌"],
    "丙": ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"],
    "丁": ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"],
    "戊": ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"],
    "己": ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"],
    "庚": ["巳","午","未","申","酉","戌","亥","子","丑","寅","卯","辰"],
    "辛": ["巳","午","未","申","酉","戌","亥","子","丑","寅","卯","辰"],
    "壬": ["申","酉","戌","亥","子","丑","寅","卯","辰","巳","午","未"],
    "癸": ["申","酉","戌","亥","子","丑","寅","卯","辰","巳","午","未"],
}

# 状态分值 (0-10, 帝旺=10最强)
STATE_SCORES = {
    "帝旺": 10, "临官": 8, "长生": 7, "沐浴": 6, "冠带": 5,
    "衰": 4, "病": 3, "死": 2, "墓": 1, "绝": 0, "胎": 2, "养": 3
}

# 地支本气及其五行 (用于地支本气计分)
BRANCH_MAIN = {
    "子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火",
    "午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"
}

# 地支本气基础分 (简化)
BRANCH_MAIN_SCORE = {
    "子":8,"丑":5,"寅":10,"卯":10,"辰":5,"巳":10,
    "午":10,"未":5,"申":10,"酉":10,"戌":5,"亥":8
}

# 地支藏干表 [(天干, 本/中/余气)]
BRANCH_HIDDEN = {
    "子":[("癸","本气"),("壬","中气")],
    "丑":[("己","本气"),("癸","中气"),("辛","余气")],
    "寅":[("甲","本气"),("丙","中气"),("戊","余气")],
    "卯":[("乙","本气")],
    "辰":[("戊","本气"),("乙","中气"),("癸","余气")],
    "巳":[("丙","本气"),("庚","中气"),("戊","余气")],
    "午":[("丁","本气"),("己","中气")],
    "未":[("己","本气"),("丁","中气"),("乙","余气")],
    "申":[("庚","本气"),("壬","中气"),("戊","余气")],
    "酉":[("辛","本气")],
    "戌":[("戊","本气"),("辛","中气"),("丁","余气")],
    "亥":[("壬","本气"),("甲","中气")],
}

HIDDEN_WEIGHT = {"本气": 1.0, "中气": 0.5, "余气": 0.3}

def calc_wuxing_power(stems: list, branches: list) -> dict:
    """
    计算八字五行力量 (仿 zhouyi.cc)
    
    Args:
        stems: [年干, 月干, 日干, 时干]
        branches: [年支, 月支, 日支, 时支]
    
    Returns:
        {"木": float, "火": float, "土": float, "金": float, "水": float}
    """
    power = {"木":0.0, "火":0.0, "土":0.0, "金":0.0, "水":0.0}
    
    for stem, branch in zip(stems, branches):
        elem = STEM_ELEMENTS[stem]
        
        # 1. 天干分 = 天干在其所临宫位的状态分
        state = STEM_STATES[stem][ZI[branch]]
        stem_score = STATE_SCORES.get(state, 3)
        power[elem] += stem_score
        
        # 2. 地支本气分 = 地支本气五行 × 地支本气基础分
        main_elem = BRANCH_MAIN[branch]
        main_score = BRANCH_MAIN_SCORE[branch]
        power[main_elem] += main_score
        
        # 3. 地支藏干分 = 藏干在其所临宫位 × 权重
        for hidden_stem, level in BRANCH_HIDDEN[branch]:
            hidden_elem = STEM_ELEMENTS[hidden_stem]
            # 藏干在当前地支的长生状态
            hidden_state = STEM_STATES[hidden_stem][ZI[branch]]
            hidden_state_score = STATE_SCORES.get(hidden_state, 3)
            power[hidden_elem] += hidden_state_score * HIDDEN_WEIGHT[level]
    
    return power


def judge_strength_by_wuxing(power: dict, day_stem: str) -> dict:
    """
    基于五行力量判断身强弱 (仿 zhouyi.cc)
    
    同类: 生助日主的五行 (日主本身 + 生日主之五行)
    异类: 克泄耗日主的五行 (克日主之五行 + 日主所克之五行 + 耗日主之五行)
    
    相生: 木→火→土→金→水→木
    相克: 木克土克水克火克金克木
    
    Args:
        power: 五行力量字典
        day_stem: 日干
    
    Returns:
        {"strength": str, "diff": float, "same": float, "other": float, "ratio": float}
    """
    elem_idx = {"木":0, "火":1, "土":2, "金":3, "水":4}
    day_elem_idx = elem_idx[STEM_ELEMENTS[day_stem]]
    
    # 同类: 日主本身 + 生我者
    # 木生火: idx 0生1; 火生土: 1生2; 土生金: 2生3; 金生水: 3生4; 水生木: 4生0
    same_elem_idx = {day_elem_idx}  # 自身
    sheng_idx = (day_elem_idx - 1) % 5  # 生我者
    same_elem_idx.add(sheng_idx)
    
    same = sum(power[ELEMENTS[i]] for i in same_elem_idx)
    other = sum(power[ELEMENTS[i]] for i in range(5) if i not in same_elem_idx)
    diff = same - other
    total = same + other
    
    # 判断规则 (基于 zhouyi.cc)
    ratio = diff / total if total > 0 else 0
    
    if diff > 50:
        label = "极旺"
    elif diff > 30:
        label = "偏旺"
    elif diff > 10:
        label = "稍旺"
    elif diff > -10:
        label = "中和"
    elif diff > -30:
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
        "method": "wuxing_power"
    }


if __name__ == "__main__":
    # 测试: 丙午 辛卯 丙申 庚寅
    stems = ["丙", "辛", "丙", "庚"]
    branches = ["午", "卯", "申", "寅"]
    
    power = calc_wuxing_power(stems, branches)
    result = judge_strength_by_wuxing(power, "丙")
    
    print(f"八字: {''.join(s+b for s,b in zip(stems,branches))}")
    print(f"五行力量: {power}")
    print(f"同类: {result['same']}, 异类: {result['other']}, 差值: {result['diff']}")
    print(f"判断: {result['strength']}")
    print(f"网站参照: 同类=195, 异类=99, 差=96 → 偏旺")
