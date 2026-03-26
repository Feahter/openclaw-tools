#!/usr/bin/env python3
"""
五格剖象计算器
基于康熙字典笔画数和81数理表计算天格/人格/地格/外格/总格
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# 五行偏旁表
WUXING_RADICALS = {
    "木": ["木", "艹", "忄", "讠", "耒", "矛", "松", "柏", "杉", "林", "森", "杨", "柳", "桂", "桐", "桃", "梅", "菊", "花", "草", "荣", "芸", "芽", "苓", "苟", "苒", "若", "荣", "茜", "莘", "莺", "萍", "萤", "营", "萧", "萨", "藤", "药", "藻", "GEM"],
    "火": ["火", "灬", "光", "灬", "灬", "灵", "炎", "炬", "炭", "炮", "炸", "炳", "炼", "炽", "烁", "烂", "烈", "焚", "焓", "焕", "焖", "焰", "然", "煌", "熔", "熙", "熟", "燎", "燃", "燊", "灿", "炜", "炫", "熠"],
    "土": ["土", "阝", "玉", "艸", "圭", "寺", "均", "坎", "坏", "坐", "址", "坏", "坡", "坤", "坦", "坪", "垂", "垣", "城", "埂", "埔", "堤", "堪", "堰", "堵", "塑", "墨", "增", "壁", "壤", "媛", "寺", "志", "地"],
    "金": ["金", "钅", "刂", "戈", "镐", "铁", "铜", "银", "铭", "铸", "铺", "链", "锁", "锅", "锋", "锦", "锯", "锤", "锥", "镀", "镇", "镜", "镯", "長", "镕", "鑫", "刚", "创", "利", "刮", "制", "前", "剃", "剑", "剥", "剧"],
    "水": ["氵", "冫", "氺", "冷", "雨", "冰", "凌", "准", "凋", "凉", "凛", "凝", "净", "凑", "减", "凛", "凝", "泽", "洁", "洪", "济", "浏", "浪", "涌", "浚", "渔", "淑", "淌", "淡", "深", "清", "温", "湾", "满", "源", "溪", "滨", "潮", "澎", "澜", "汉", "汗", "汝", "汐", "汲", "汪", "沛", "沙", "沃", "没", "沟", "沥", "泉", "泊", "泌", "泣", "泳", "治", "法", "波", "泛"],
}

# 五行天干地支对应
WUXING_TIANGAN = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}
WUXING_DIZHI = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}


def load_stroke_table() -> Dict[str, int]:
    """加载汉字笔画数表"""
    path = Path(__file__).parent.parent / "references" / "stroke_table.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("strokes", {})


def load_wuge_rules() -> Dict[str, Any]:
    """加载五格数理规则"""
    path = Path(__file__).parent.parent / "references" / "wuge_rules.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


STROKE_TABLE = None
WUXING_RULES = None


def get_stroke_table() -> Dict[str, int]:
    global STROKE_TABLE
    if STROKE_TABLE is None:
        STROKE_TABLE = load_stroke_table()
    return STROKE_TABLE


def get_wuge_rules() -> Dict[str, Any]:
    global WUXING_RULES
    if WUXING_RULES is None:
        WUXING_RULES = load_wuge_rules()
    return WUXING_RULES


def get_char_stroke(char: str) -> Optional[int]:
    """获取汉字笔画数"""
    strokes = get_stroke_table()
    return strokes.get(char)


def get_char_wuxing(char: str) -> str:
    """
    根据偏旁判断汉字五行
    返回: 木/火/土/金/水/未知
    """
    for wuxing, radicals in WUXING_RADICALS.items():
        for radical in radicals:
            if radical in char:
                return wuxing
    # 尝试直接匹配
    for wuxing, chars in [
        ("木", "木林森柳桂桐松柏杉梅桃竹"),
        ("火", "火炎灿煌炉灶烟烧烤烘煎炒煮炖"),
        ("土", "土址坟坠坤坦块坏培基堂堆堤墓"),
        ("金", "金铁铜银锡链锁锋锐铸锄铭镜"),
        ("水", "水泉河汉泪波涛浪涌潮洗泳灌"),
    ]:
        if char in chars:
            return wuxing
    return "土"  # 默认土（最中性）


def calculate_surname_strokes(surname: str) -> int:
    """
    计算姓的笔画数（单姓直接查表，复姓=两字笔画相加）
    """
    strokes = get_stroke_table()
    
    if len(surname) == 1:
        # 单姓
        return strokes.get(surname, 0) or len(surname) * 5  # 估算
    elif len(surname) == 2:
        # 复姓
        s1 = strokes.get(surname[0], 0)
        s2 = strokes.get(surname[1], 0)
        return s1 + s2
    else:
        # 超过2字视为名，取第一字
        return strokes.get(surname[0], 0)


def calculate_wuge(surname: str, givenname: str) -> Dict[str, Any]:
    """
    计算五格数理
    
    Args:
        surname: 姓氏
        givenname: 名字（不含姓氏）
    
    Returns:
        {
            "tian_ge": {"number": 5, "wuxing": "火", "jixiong": "吉"},
            "ren_ge": {"number": 11, "wuxing": "木", "jixiong": "吉"},
            "di_ge": {"number": 8, "wuxing": "金", "jixiong": "吉"},
            "wai_ge": {"number": 2, "wuxing": "木", "jixiong": "凶"},
            "zong_ge": {"number": 13, "wuxing": "火", "jixiong": "吉"},
            "san_cai": {"config": "火→木→金", "jixiong": "吉"},
        }
    """
    rules = get_wuge_rules()
    strokes = get_stroke_table()
    
    # 计算笔画数
    surname_strokes = calculate_surname_strokes(surname)
    
    # 名笔画数
    givenname_strokes = []
    for char in givenname:
        s = strokes.get(char)
        if s is None:
            s = 8  # 默认值
        givenname_strokes.append(s)
    
    if len(givenname_strokes) == 1:
        givenname_strokes.append(1)  # 单名加1
    
    first_name_stroke = givenname_strokes[0]
    second_name_stroke = givenname_strokes[1] if len(givenname_strokes) > 1 else 1
    
    # 计算五格
    # 天格：姓笔画数+1（单姓）；复姓=第一字+第二字
    if len(surname) == 1:
        tian_ge = surname_strokes + 1
    else:
        tian_ge = surname_strokes  # 复姓天格=姓笔画总数
    
    # 人格：姓笔画数+名第一字笔画
    ren_ge = surname_strokes + first_name_stroke
    
    # 地格：名笔画数+1（单名）；双名=两字笔画相加
    if len(givenname) == 1:
        di_ge = first_name_stroke + 1
    else:
        di_ge = sum(givenname_strokes)
    
    # 外格：总格-人格+1
    # 总格：天格+地格
    zong_ge = tian_ge + di_ge
    wai_ge = zong_ge - ren_ge + 1
    
    # 限制在1-81
    tian_ge = max(1, min(81, tian_ge))
    ren_ge = max(1, min(81, ren_ge))
    di_ge = max(1, min(81, di_ge))
    wai_ge = max(1, min(81, wai_ge))
    zong_ge = max(1, min(81, zong_ge))
    
    # 获取数理吉凶
    def get_number_info(n: int) -> Dict[str, str]:
        n_data = rules["wuge_numbers"].get(str(n), {"吉凶": "未知", "解释": "未收录", "暗示": ""})
        return {
            "number": n,
            "jixiong": n_data["吉凶"],
            "explain": n_data["解释"],
            "yushi": n_data["暗示"],
        }
    
    # 获取五行
    def get_wuxing_from_tiangan_dizhi(stroke_count: int) -> str:
        """根据笔画数推断五行（循环）"""
        wuxing_list = ["木", "火", "土", "金", "水"]
        return wuxing_list[(stroke_count - 1) % 5]
    
    tian_info = get_number_info(tian_ge)
    ren_info = get_number_info(ren_ge)
    di_info = get_number_info(di_ge)
    wai_info = get_number_info(wai_ge)
    zong_info = get_number_info(zong_ge)
    
    # 三才配置
    tian_wx = get_wuxing_from_tiangan_dizhi(tian_ge)
    ren_wx = get_wuxing_from_tiangan_dizhi(ren_ge)
    di_wx = get_wuxing_from_tiangan_dizhi(di_ge)
    
    sancai_key = f"{tian_wx}{ren_wx}{di_wx}"
    sancai_info = rules.get("三才配置", {}).get(sancai_key, {"吉凶": "未知", "解释": "未收录"})
    
    return {
        "surname_strokes": surname_strokes,
        "givenname_strokes": givenname_strokes,
        "tian_ge": {**tian_info, "wuxing": tian_wx},
        "ren_ge": {**ren_info, "wuxing": ren_wx},
        "di_ge": {**di_info, "wuxing": di_wx},
        "wai_ge": {**wai_info, "wuxing": get_wuxing_from_tiangan_dizhi(wai_ge)},
        "zong_ge": {**zong_info, "wuxing": get_wuxing_from_tiangan_dizhi(zong_ge)},
        "san_cai": {
            "config": sancai_key,
            "tian_ge": tian_wx,
            "ren_ge": ren_wx,
            "di_ge": di_wx,
            "jixiong": sancai_info["吉凶"],
            "explain": sancai_info["解释"],
        },
    }


def main():
    """测试五格计算"""
    test_cases = [
        ("张", "三"),
        ("李", "明"),
        ("王", "浩宇"),
        ("欧阳", "锋"),
        ("司马", "光"),
    ]
    
    print("=== 五格剖象计算测试 ===\n")
    
    for surname, givenname in test_cases:
        result = calculate_wuge(surname, givenname)
        full_name = f"{surname}{givenname}"
        print(f"姓名：{full_name}（姓={surname}, 名={givenname}）")
        print(f"  笔画：姓={result['surname_strokes']}, 名={result['givenname_strokes']}")
        print(f"  天格({result['tian_ge']['number']}): {result['tian_ge']['jixiong']} | 五行={result['tian_ge']['wuxing']}")
        print(f"  人格({result['ren_ge']['number']}): {result['ren_ge']['jixiong']} | 五行={result['ren_ge']['wuxing']}")
        print(f"  地格({result['di_ge']['number']}): {result['di_ge']['jixiong']} | 五行={result['di_ge']['wuxing']}")
        print(f"  外格({result['wai_ge']['number']}): {result['wai_ge']['jixiong']} | 五行={result['wai_ge']['wuxing']}")
        print(f"  总格({result['zong_ge']['number']}): {result['zong_ge']['jixiong']} | 五行={result['zong_ge']['wuxing']}")
        print(f"  三才配置：{result['san_cai']['config']} = {result['san_cai']['jixiong']}（{result['san_cai']['explain']}）")
        print()


if __name__ == "__main__":
    main()
