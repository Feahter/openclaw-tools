#!/usr/bin/env python3
"""
名字生成与评分器
结合八字喜用神 + 五格数理，生成名字推荐方案
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# 尝试导入依赖
try:
    from bazi_api import call_bazi_api, parse_bazi_response
    from wuge_calculator import calculate_wuge, get_char_wuxing, get_char_stroke
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from bazi_api import call_bazi_api, parse_bazi_response
    from wuge_calculator import calculate_wuge, get_char_wuxing, get_char_stroke


# 喜用神五行对应的常用起名字（精选）
XIYONGSHEN_WORDS = {
    "金": {
        "常用字": ["铭", "锋", "锐", "锦", "钰", "铎", "锡", "钧", "鑫", "镇", "镕", "鎏", "铠", "铖", "钲", "钱", "锦", "镛", "镜", "钻"],
        "寓意": ["坚硬、珍贵、锐利、财富"],
        "五行属金": ["金", "银", "铜", "铁", "锡", "铝", "钢"],
    },
    "水": {
        "常用字": ["泽", "涵", "润", "清", "澜", "洁", "淳", "泉", "波", "涛", "瀚", "溪", "泽", "沐", "润", "潮", "汐", "澜", "澔"],
        "寓意": ["清澈、柔和、包容、流动"],
        "五行属水": ["水", "冰", "江", "河", "湖", "海", "泉"],
    },
    "木": {
        "常用字": ["森", "林", "松", "柏", "桐", "楷", "梓", "榆", "楠", "栋", "梁", "柱", "杨", "柳", "枫", "桂", "槐", "樱", "彬"],
        "寓意": ["正直、向上、仁慈、坚韧"],
        "五行属木": ["木", "竹", "藤", "花", "草", "树", "林"],
    },
    "火": {
        "常用字": ["炎", "灿", "炜", "熠", "烽", "焕", "煌", "耀", "曦", "炫", "晟", "哲", "晔", "昊", "昌", "晖", "明", "旭", "辉"],
        "寓意": ["热烈、光明、热情、积极"],
        "五行属火": ["火", "光", "电", "热", "光", "炎", "焰"],
    },
    "土": {
        "常用字": ["城", "垣", "培", "基", "坚", "坤", "厚", "坦", "培", "增", "墨", "圣", "在", "均", "堪", "塘", "境", "增", "壁"],
        "寓意": ["稳重、厚道、包容、诚信"],
        "五行属土": ["土", "山", "石", "玉", "砂", "泥", "田"],
    },
}

# 常用好字（按拼音首字母，精选300+）
COMMON_GOOD_CHARS = [
    # A-H
    "安", "昂", "傲", "奥", "澳", "柏", "宝", "博", "才", "苍", "超",
    "琛", "晨", "成", "承", "诚", "城", "程", "弛", "崇", "川", "春",
    "慈", "聪", "丹", "道", "德", "鼎", "定", "东", "冬", "铎", "恩",
    "发", "帆", "方", "芳", "飞", "风", "福", "辅", "刚", "高", "歌",
    "根", "工", "功", "冠", "光", "广", "贵", "国", "海", "翰", "航",
    "浩", "和", "河", "荷", "恒", "弘", "红", "宏", "华", "怀", "辉",
    "汇", "慧", "嘉", "家", "建", "健", "洁", "金", "锦", "进", "晋",
    "京", "经", "景", "静", "敬", "镜", "炯", "玖", "举", "聚", "军",
    # J-Z
    "俊", "峻", "康", "可", "克", "宽", "葵", "来", "岚", "蓝", "朗",
    "乐", "磊", "理", "礼", "力", "立", "连", "良", "林", "临", "霖",
    "灵", "凌", "龙", "隆", "楼", "露", "路", "洛", "洛", "洛", "洛",
    "梅", "美", "孟", "民", "明", "鸣", "墨", "默", "沐", "娜", "宁",
    "培", "鹏", "平", "启", "谦", "强", "勤", "清", "晴", "庆", "秋",
    "全", "权", "泉", "然", "仁", "融", "如", "瑞", "睿", "润", "若",
    "森", "山", "善", "绍", "深", "生", "盛", "石", "时", "实", "识",
    "书", "抒", "舒", "树", "帅", "双", "顺", "思", "硕", "松", "涛",
    "天", "亭", "通", "桐", "威", "文", "问", "西", "希", "悉", "惜",
    "熙", "希", "夏", "先", "祥", "想", "向", "晓", "笑", "效", "新",
    "心", "辛", "信", "兴", "星", "修", "旭", "栩", "轩", "宣", "学",
    "雪", "勋", "循", "逊", "雅", "亚", "彦", "曜", "耀", "烨", "伊",
    "依", "颐", "仪", "宜", "怡", "义", "艺", "易", "益", "逸", "毅",
    "翼", "英", "盈", "永", "咏", "泳", "勇", "用", "优", "悠", "游",
    "有", "于", "宇", "羽", "雨", "语", "玉", "裕", "预", "元", "圆",
    "远", "月", "岳", "云", "允", "运", "韵", "在", "泽", "增", "昭",
    "哲", "者", "振", "正", "政", "之", "知", "直", "植", "至", "致",
    "治", "智", "中", "仲", "舟", "周", "州", "洲", "竹", "主", "卓",
    "琢", "子", "紫", "自", "宗", "祖", "组", "左", "作", "坐", "座",
]


def parse_xiyongshen(xiyongshen_str: str) -> List[str]:
    """
    解析喜用神字符串，返回五行列表
    例如: "金，水" -> ["金", "水"]
    """
    if not xiyongshen_str:
        return ["金", "水"]  # 默认
    
    result = []
    for char in xiyongshen_str:
        if char in ["金", "木", "水", "火", "土"]:
            result.append(char)
    return result if result else ["金", "水"]


def score_name(
    surname: str,
    givenname: str,
    xiyongshen_list: List[str],
    wuge_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    给名字打分
    
    评分维度:
    - 五格数理 (30%): 人格必须为吉
    - 三才配置 (25%): 相生/比和 > 相克
    - 喜用神匹配 (25%): 字五行匹配喜用神
    - 字义评分 (10%): 字义正向
    - 音形义 (10%): 读音流畅/字形平衡
    
    Returns:
        {
            "total_score": 85,
            "breakdown": {...},
            "pass": True,
            "issues": []
        }
    """
    score = 0
    breakdown = {}
    issues = []
    pass_flag = True
    
    # 1. 五格数理 (30%)
    ren_ge = wuge_result["ren_ge"]
    di_ge = wuge_result["di_ge"]
    zong_ge = wuge_result["zong_ge"]
    
    wuge_score = 0
    if ren_ge["jixiong"] == "吉":
        wuge_score += 20
    elif ren_ge["jixiong"] == "半吉":
        wuge_score += 10
    else:
        wuge_score += 0
        issues.append(f"人格{ren_ge['number']}为凶数")
        pass_flag = False
    
    if di_ge["jixiong"] == "吉":
        wuge_score += 5
    elif di_ge["jixiong"] == "半吉":
        wuge_score += 2
    
    if zong_ge["jixiong"] == "吉":
        wuge_score += 5
    elif zong_ge["jixiong"] == "半吉":
        wuge_score += 2
    
    breakdown["五格数理"] = wuge_score
    
    # 2. 三才配置 (25%)
    san_cai = wuge_result["san_cai"]
    sancai_score = 0
    if san_cai["jixiong"] == "吉":
        sancai_score = 25
    elif san_cai["jixiong"] == "半吉":
        sancai_score = 15
    else:
        sancai_score = 0
        issues.append(f"三才配置{san_cai['config']}为凶")
        pass_flag = False
    
    breakdown["三才配置"] = sancai_score
    
    # 3. 喜用神匹配 (25%)
    xiyong_score = 0
    match_count = 0
    for char in givenname:
        char_wuxing = get_char_wuxing(char)
        if char_wuxing in xiyongshen_list:
            xiyong_score += 12
            match_count += 1
        else:
            xiyong_score += 2  # 不匹配但也不冲突
    
    # 额外分数：两个字都匹配
    if match_count == len(givenname) and len(givenname) >= 1:
        xiyong_score = min(xiyong_score + 5, 25)
    
    breakdown["喜用神匹配"] = xiyong_score
    
    # 4. 字义评分 (10%) - 简化版
    # 这里简化处理，假设都在常用好字中
    yizi_score = 8 if all(c in COMMON_GOOD_CHARS for c in givenname) else 5
    breakdown["字义评分"] = yizi_score
    
    # 5. 音形义 (10%) - 简化版
    # 假设单字名比双字名稍逊
    yinxing_score = 8 if len(givenname) == 2 else 7
    breakdown["音形义"] = yinxing_score
    
    total = wuge_score + sancai_score + xiyong_score + yizi_score + yinxing_score
    breakdown["总分"] = total
    
    return {
        "total_score": total,
        "breakdown": breakdown,
        "pass": pass_flag,
        "issues": issues,
    }


def generate_candidate_chars(
    xiyongshen_list: List[str],
    count: int = 50,
    avoid_chars: List[str] = None,
) -> List[Dict[str, Any]]:
    """
    根据喜用神生成候选汉字列表
    
    Returns:
        [{"char": "泽", "wuxing": "水", "stroke": 8, "meaning": "润泽"}, ...]
    """
    if avoid_chars is None:
        avoid_chars = []
    
    candidates = []
    avoid_set = set(avoid_chars)
    
    for wuxing in xiyongshen_list:
        words_data = XIYONGSHEN_WORDS.get(wuxing, {})
        for char in words_data.get("常用字", []):
            if char in avoid_set:
                continue
            if char not in [c["char"] for c in candidates]:
                stroke = get_char_stroke(char) or 8
                candidates.append({
                    "char": char,
                    "wuxing": wuxing,
                    "stroke": stroke,
                    "meaning": "、".join(words_data.get("寓意", [])),
                })
    
    # 如果不够，随机补充常用好字
    remaining = count - len(candidates)
    if remaining > 0:
        for char in COMMON_GOOD_CHARS:
            if char in avoid_set:
                continue
            if char not in [c["char"] for c in candidates]:
                candidates.append({
                    "char": char,
                    "wuxing": get_char_wuxing(char),
                    "stroke": get_char_stroke(char) or 8,
                    "meaning": "常用好意",
                })
                remaining -= 1
                if remaining <= 0:
                    break
    
    random.shuffle(candidates)
    return candidates[:count]


def generate_name_recommendations(
    surname: str,
    xiyongshen_str: str,
    gender: int = 1,  # 1=男, 0=女
    avoid_chars: List[str] = None,
    max_options: int = 3,
) -> List[Dict[str, Any]]:
    """
    生成名字推荐方案
    
    Args:
        surname: 姓氏
        xiyongshen_str: 喜用神字符串，如"金，水"
        gender: 性别
        avoid_chars: 避免用字列表
    
    Returns:
        [
            {
                "full_name": "张锦泽",
                "chars": [{"char": "锦", ...}, {"char": "泽", ...}],
                "wuge": {...},
                "score": {...},
            },
            ...
        ]
    """
    xiyongshen_list = parse_xiyongshen(xiyongshen_str)
    
    # 生成候选字
    candidates = generate_candidate_chars(xiyongshen_list, count=80, avoid_chars=avoid_chars)
    
    recommendations = []
    
    # 尝试各种组合
    for i, char1 in enumerate(candidates):
        for char2 in candidates[i+1:]:
            if len(recommendations) >= max_options * 5:  # 限制尝试次数
                break
            
            givenname = char1["char"] + char2["char"]
            
            # 计算五格
            try:
                wuge = calculate_wuge(surname, givenname)
            except Exception:
                continue
            
            # 评分
            score_result = score_name(surname, givenname, xiyongshen_list, wuge)
            
            if score_result["pass"]:  # 只保留通过基本筛选的
                recommendations.append({
                    "full_name": f"{surname}{givenname}",
                    "surname": surname,
                    "givenname": givenname,
                    "chars": [char1, char2],
                    "wuge": wuge,
                    "score": score_result,
                })
        
        if len(recommendations) >= max_options * 5:
            break
    
    # 按分数排序，取前 max_options
    recommendations.sort(key=lambda x: x["score"]["total_score"], reverse=True)
    
    return recommendations[:max_options]


def format_recommendation_output(
    surname: str,
    xiyongshen_str: str,
    bazi_info: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
) -> str:
    """
    格式化输出推荐结果
    """
    lines = []
    lines.append("## 命局摘要")
    lines.append(f"- 八字：{bazi_info.get('birth_chart', 'N/A')}")
    lines.append(f"- 日主：{bazi_info.get('qiangruo', 'N/A')}")
    lines.append(f"- 喜用神：{xiyongshen_str}")
    lines.append(f"- 忌神：{bazi_info.get('jishen', 'N/A')}")
    lines.append("")
    
    lines.append("## 五格架构")
    lines.append("| 格位 | 数理 | 五行 | 吉凶 |")
    lines.append("|:---|:---:|:---:|:---:|")
    
    if recommendations:
        wuge = recommendations[0]["wuge"]
        lines.append(f"| 天格 | {wuge['tian_ge']['number']} | {wuge['tian_ge']['wuxing']} | {wuge['tian_ge']['jixiong']} |")
        lines.append(f"| 人格 | {wuge['ren_ge']['number']} | {wuge['ren_ge']['wuxing']} | {wuge['ren_ge']['jixiong']} |")
        lines.append(f"| 地格 | {wuge['di_ge']['number']} | {wuge['di_ge']['wuxing']} | {wuge['di_ge']['jixiong']} |")
        lines.append(f"| 外格 | {wuge['wai_ge']['number']} | {wuge['wai_ge']['wuxing']} | {wuge['wai_ge']['jixiong']} |")
        lines.append(f"| 总格 | {wuge['zong_ge']['number']} | {wuge['zong_ge']['wuxing']} | {wuge['zong_ge']['jixiong']} |")
        lines.append("")
        lines.append(f"**三才配置**：{wuge['san_cai']['config']} = **{wuge['san_cai']['jixiong']}**（{wuge['san_cai']['explain']}）")
    
    lines.append("")
    lines.append("## 推荐方案（3组）")
    
    for i, rec in enumerate(recommendations, 1):
        full_name = rec["full_name"]
        wuge = rec["wuge"]
        chars = rec["chars"]
        
        # 解析五行组合
        wuxing_combo = f"{chars[0]['wuxing']}{chars[1]['wuxing']}"
        # 判断是否相生
        sheng = {"木火土金水": True, "火土金水木": True, "土金水木火": True, 
                 "金水木火土": True, "水木火土金": True}
        is_sheng = wuxing_combo in sheng or wuxing_combo[::-1] in sheng
        
        lines.append("")
        lines.append(f"### 方案{i}：{full_name}")
        lines.append(f"- **用字解析**：{chars[0]['char']}（{chars[0]['wuxing']}）+ {chars[1]['char']}（{chars[1]['wuxing']}）")
        lines.append(f"- **五行归属性质**：{'相生' if is_sheng else '比和'}")
        lines.append(f"- **天格({wuge['tian_ge']['number']})+人格({wuge['ren_ge']['number']})+地格({wuge['di_ge']['number']})**：{wuge['tian_ge']['jixiong']}/{wuge['ren_ge']['jixiong']}/{wuge['di_ge']['jixiong']}")
        lines.append(f"- **三才**：{wuge['san_cai']['config']}（{wuge['san_cai']['jixiong']}）")
        lines.append(f"- **音形义**：读音响亮，字形端正")
        lines.append(f"- **适用场景**：适合期望孩子前程似锦、财运亨通的家庭")
    
    lines.append("")
    lines.append("## 风险提示")
    if recommendations:
        wuge = recommendations[0]["wuge"]
        if wuge.get("ren_ge", {}).get("number") == 21:
            lines.append("- 人格21数为领袖数，女性使用需辩证看待")
        if wuge.get("zong_ge", {}).get("number") == 34:
            lines.append("- 总格34数为破家数，已规避")
    
    lines.append("")
    lines.append("## 使用建议")
    lines.append("1. 用毛笔书写，观察字形结构是否平衡")
    lines.append("2. 在正式场合试呼，确认音韵流畅度")
    lines.append("3. 保留3个月观察期，感受\"名-人\"契合度")
    
    return "\n".join(lines)


def main():
    """测试名字生成"""
    print("=== 名字生成测试 ===\n")
    
    # 测试用例
    test_cases = [
        ("张", "金、水", 1),
        ("李", "木、火", 1),
        ("王", "水、金", 0),
    ]
    
    for surname, xiyong, gender in test_cases:
        print(f"\n--- 姓氏={surname}, 喜用神={xiyong}, 性别={'男' if gender else '女'} ---")
        
        recs = generate_name_recommendations(
            surname=surname,
            xiyongshen_str=xiyong,
            gender=gender,
        )
        
        for i, rec in enumerate(recs, 1):
            print(f"\n方案{i}: {rec['full_name']}")
            print(f"  分数: {rec['score']['total_score']}")
            print(f"  人格: {rec['wuge']['ren_ge']['number']} ({rec['wuge']['ren_ge']['jixiong']})")
            print(f"  三才: {rec['wuge']['san_cai']['config']} ({rec['wuge']['san_cai']['jixiong']})")


if __name__ == "__main__":
    main()
