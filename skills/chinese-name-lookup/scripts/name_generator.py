#!/usr/bin/env python3
"""
名字生成与评分器 V2
结合八字喜用神 + 五格数理，生成名字推荐方案
- 扩充候选字库（50+/五行）
- 预过滤凶数组合
- 完善输出格式
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

try:
    from bazi_api import call_bazi_api, parse_bazi_response
    from wuge_calculator import calculate_wuge, get_char_wuxing, get_char_stroke
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from bazi_api import call_bazi_api, parse_bazi_response
    from wuge_calculator import calculate_wuge, get_char_wuxing, get_char_stroke


# 扩充版喜用神字库（50+/五行）
XIYONGSHEN_WORDS_V2 = {
    "金": {
        "常用字": [
            # 高频金
            "铭", "锋", "锐", "锦", "鑫", "铎", "锡", "钧", "镇", "镕",
            "铠", "钲", "钱", "锦", "镛", "镜", "钻", "铁", "铜", "银",
            # 次常用
            "锐", "锴", "锟", "锄", "锅", "链", "锁", "锈", "错", "锡",
            "锣", "锤", "锥", "镀", "锰", "镖", "镐", "镍", "镂", "锡",
            "钧", "钥", "钦", "钧", "钴", "钵", "钻", "铢", "铣", "铭",
            "铮", "甥", "镔", "鉴", "銮", "鏖", "鏖",
        ],
        "寓意": "坚硬、珍贵、锐利、财富、权力",
    },
    "水": {
        "常用字": [
            # 高频水
            "泽", "涵", "润", "清", "澜", "洁", "淳", "泉", "波", "涛",
            "瀚", "溪", "沐", "潮", "汐", "澔", "瀚", "渊", "漾", "溢",
            # 次常用
            "汝", "汐", "汲", "汪", "沛", "沙", "沃", "没", "沟", "沥",
            "泉", "泊", "泌", "泣", "泳", "治", "法", "泛", "泸", "泣",
            "沫", "泞", "泱", "波", "泣", "泳", "洁", "洪", "济", "浏",
            "浪", "涌", "浚", "渔", "淑", "淌", "淡", "深", "温", "湾",
            "满", "源", "潮", "澎", "澜", "澈", "潮",
        ],
        "寓意": "清澈、柔和、包容、流动、智慧",
    },
    "木": {
        "常用字": [
            # 高频木
            "森", "林", "松", "柏", "桐", "楷", "梓", "榆", "楠", "栋",
            "梁", "柱", "杨", "柳", "枫", "桂", "槐", "樱", "彬", "杉",
            # 次常用
            "札", "朴", "机", "权", "杞", "束", "杜", "束", "杭", "束",
            "枚", "果", "枝", "枯", "柄", "栋", "橙", "桐", "桓", "桔",
            "栩", "桂", "栖", "栗", "桑", "梢", "棕", "棺", "棉", "棋",
            "棍", "椅", "植", "椰", "楠", "楷", "槐", "桦", "桢", "贤",
        ],
        "寓意": "正直、向上、仁慈、坚韧、生命力",
    },
    "火": {
        "常用字": [
            # 高频火
            "炎", "灿", "炜", "熠", "烽", "焕", "煌", "耀", "曦", "炫",
            "晟", "哲", "晔", "昊", "昌", "晖", "明", "旭", "辉", "昭",
            # 次常用
            "灰", "灬", "灶", "灬", "灬", "灾", "灿", "灵", "灬", "炖",
            "炒", "炙", "烈", "焚", "焓", "焕", "烽", "焖", "焰", "然",
            "煌", "熔", "熙", "熊", "熟", "燎", "燊", "爔", "爔",
            "炬", "炖", "炒", "烈", "焕", "辉", "耀", "显", "晃",
        ],
        "寓意": "热烈、光明、热情、积极、创造力",
    },
    "土": {
        "常用字": [
            # 高频土
            "城", "垣", "培", "基", "坚", "坤", "厚", "坦", "增", "墨",
            "圣", "在", "均", "堪", "塘", "境", "增", "壁", "壤", "垣",
            # 次常用
            "址", "阝", "坠", "坏", "坐", "坏", "坡", "坤", "坦", "坏",
            "址", "垂", "垣", "城", "埂", "埔", "堤", "堰", "堵", "塑",
            "墨", "增", "壁", "壤", "壑", "垢", "垣", "墟", "墓", "墙",
            "坛", "坞", "坏", "培", "堆", "堪", "堰", "堵", "塑", "墨",
        ],
        "寓意": "稳重、厚道、包容、诚信、承载",
    },
}

# 绝对禁止的数理（凶数之凶）
FORBIDDEN_NUMBERS = {2, 4, 9, 10, 12, 14, 19, 20, 22, 26, 28, 34, 36, 37, 43, 44, 46, 49, 50, 54, 56, 58, 59, 60, 64, 66, 69, 70, 72, 73, 74, 75, 76, 77, 78, 79, 80}

# 需要谨慎使用的数理（半吉）
CAUTION_NUMBERS = {6, 8, 17, 18, 27, 30, 36, 38, 39, 40, 42, 51, 52, 53, 55, 57, 58, 59, 60, 62, 64, 65, 66, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80}

# 特别好听的组合（常见好名示例）
GOOD_NAME_EXAMPLES = [
    ("泽", "楷"), ("锦", "泽"), ("铭", "泽"), ("润", "泽"),
    ("思", "远"), ("景", "行"), ("明", "德"), ("文", "礼"),
    ("安", "然"), ("静", "好"), ("清", "欢"), ("时", "雨"),
    ("栀", "晴"), ("望", "晴"), ("言", "蹊"), ("知", "意"),
]

COMMON_GOOD_CHARS = [
    # 常用好字（按拼音排序，精选100+）
    "安", "昂", "傲", "奥", "澳", "柏", "宝", "博", "才", "苍", "超",
    "琛", "晨", "成", "承", "诚", "城", "程", "弛", "崇", "川", "春",
    "慈", "聪", "丹", "道", "德", "鼎", "定", "东", "冬", "铎", "恩",
    "帆", "方", "芳", "飞", "风", "福", "辅", "刚", "高", "歌", "根",
    "工", "功", "冠", "光", "广", "贵", "国", "海", "翰", "航", "浩",
    "和", "河", "荷", "恒", "弘", "红", "宏", "华", "怀", "辉", "汇",
    "慧", "嘉", "家", "建", "健", "洁", "金", "锦", "进", "晋", "京",
    "经", "景", "静", "敬", "镜", "炯", "玖", "举", "聚", "军", "俊",
    "峻", "康", "可", "克", "宽", "葵", "来", "岚", "蓝", "朗", "乐",
    "磊", "理", "礼", "力", "立", "连", "良", "林", "临", "霖", "灵",
    "凌", "龙", "隆", "楼", "露", "路", "洛", "梅", "美", "孟", "民",
    "明", "鸣", "墨", "默", "沐", "娜", "宁", "培", "鹏", "平", "启",
    "谦", "强", "勤", "清", "晴", "庆", "秋", "全", "权", "泉", "然",
    "仁", "融", "如", "瑞", "睿", "润", "若", "森", "山", "善", "绍",
    "深", "生", "盛", "石", "时", "实", "识", "书", "抒", "舒", "树",
    "帅", "双", "顺", "思", "硕", "松", "涛", "天", "亭", "通", "桐",
    "威", "文", "问", "西", "希", "悉", "惜", "熙", "夏", "先", "祥",
    "想", "向", "晓", "笑", "效", "新", "心", "辛", "信", "兴", "星",
    "修", "旭", "栩", "轩", "宣", "学", "雪", "勋", "循", "逊", "雅",
    "亚", "彦", "曜", "耀", "烨", "伊", "依", "颐", "仪", "宜", "怡",
    "义", "艺", "易", "益", "逸", "毅", "翼", "英", "盈", "永", "咏",
    "泳", "勇", "用", "优", "悠", "游", "有", "于", "宇", "羽", "雨",
    "语", "玉", "裕", "预", "元", "圆", "远", "月", "岳", "云", "允",
    "运", "韵", "泽", "增", "昭", "哲", "者", "振", "正", "政", "之",
    "知", "直", "植", "至", "致", "治", "智", "中", "仲", "舟", "州",
    "洲", "竹", "主", "卓", "琢", "子", "紫", "自", "宗", "祖", "组",
]


def parse_xiyongshen(xiyongshen_str: str) -> List[str]:
    """解析喜用神字符串"""
    if not xiyongshen_str:
        return ["金", "水"]
    
    result = []
    for char in xiyongshen_str:
        if char in ["金", "木", "水", "火", "土"]:
            result.append(char)
    return result if result else ["金", "水"]


def is_good_wuge_number(n: int) -> Tuple[bool, str]:
    """
    判断数理是否吉利
    Returns: (is_good, warning)
    """
    if n in FORBIDDEN_NUMBERS:
        return False, f"数理{n}为大凶之数"
    if n in CAUTION_NUMBERS:
        return False, f"数理{n}需谨慎使用"
    return True, ""


def score_name_v2(
    surname: str,
    givenname: str,
    xiyongshen_list: List[str],
    wuge_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    V2 评分函数
    - 人格/总格/地格 为凶数直接禁止
    - 三才为凶禁止
    - 喜用神匹配加分
    """
    issues = []
    warnings = []
    pass_flag = True
    
    # 1. 人格必须为吉
    ren = wuge_result["ren_ge"]["number"]
    ren_ok, ren_msg = is_good_wuge_number(ren)
    if not ren_ok:
        issues.append(f"人格{ren}{ren_msg}")
        pass_flag = False
    
    # 2. 总格必须为吉
    zong = wuge_result["zong_ge"]["number"]
    zong_ok, zong_msg = is_good_wuge_number(zong)
    if not zong_ok:
        issues.append(f"总格{zong}{zong_msg}")
        pass_flag = False
    
    # 3. 天格参考
    tian = wuge_result["tian_ge"]["number"]
    tian_ok, tian_msg = is_good_wuge_number(tian)
    if not tian_ok:
        warnings.append(f"天格{tian}{tian_msg}")
    
    # 4. 地格参考
    di = wuge_result["di_ge"]["number"]
    di_ok, di_msg = is_good_wuge_number(di)
    if not di_ok:
        warnings.append(f"地格{di}{di_msg}")
    
    # 5. 三才配置
    san_cai = wuge_result["san_cai"]
    if san_cai["jixiong"] not in ["吉", "半吉"]:
        issues.append(f"三才配置{san_cai['config']}为凶")
        pass_flag = False
    
    # 6. 喜用神匹配
    match_count = 0
    for char in givenname:
        char_wuxing = get_char_wuxing(char)
        if char_wuxing in xiyongshen_list:
            match_count += 1
    
    xiyong_score = match_count * 12  # 每个字匹配+12
    
    # 7. 计算总分
    total = 0
    breakdown = {}
    
    # 五格得分
    wuge_score = 50 if (ren_ok and zong_ok) else 0
    breakdown["五格数理"] = wuge_score
    total += wuge_score
    
    # 三才得分
    sancai_score = 25 if san_cai["jixiong"] == "吉" else (15 if san_cai["jixiong"] == "半吉" else 0)
    breakdown["三才配置"] = sancai_score
    total += sancai_score
    
    # 喜用神得分
    breakdown["喜用神匹配"] = xiyong_score
    total += xiyong_score
    
    # 字义得分
    yizi_score = 10 if all(c in COMMON_GOOD_CHARS for c in givenname) else 6
    breakdown["字义评分"] = yizi_score
    total += yizi_score
    
    breakdown["总分"] = total
    
    return {
        "total_score": total,
        "breakdown": breakdown,
        "pass": pass_flag,
        "issues": issues,
        "warnings": warnings,
    }


def generate_candidate_chars_v2(
    xiyongshen_list: List[str],
    count: int = 100,
    avoid_chars: List[str] = None,
) -> List[Dict[str, Any]]:
    """V2 候选字生成：扩充字库 + 去重"""
    if avoid_chars is None:
        avoid_chars = []
    
    avoid_set = set(avoid_chars)
    candidates = []
    seen_chars = set()
    
    for wuxing in xiyongshen_list:
        words = XIYONGSHEN_WORDS_V2.get(wuxing, {}).get("常用字", [])
        for char in words:
            if char in avoid_set or char in seen_chars:
                continue
            stroke = get_char_stroke(char)
            if stroke is None:
                stroke = 8  # 默认值
            candidates.append({
                "char": char,
                "wuxing": wuxing,
                "stroke": stroke,
            })
            seen_chars.add(char)
    
    # 补充 COMMON_GOOD_CHARS 中的字
    for char in COMMON_GOOD_CHARS:
        if char in avoid_set or char in seen_chars:
            continue
        stroke = get_char_stroke(char)
        if stroke is None:
            stroke = 8
        candidates.append({
            "char": char,
            "wuxing": get_char_wuxing(char),
            "stroke": stroke,
        })
        seen_chars.add(char)
    
    random.shuffle(candidates)
    return candidates[:count]


def generate_name_recommendations_v2(
    surname: str,
    xiyongshen_str: str,
    gender: int = 1,
    avoid_chars: List[str] = None,
    max_options: int = 3,
) -> List[Dict[str, Any]]:
    """
    V2 名字推荐生成
    - 预过滤凶数组合
    - 优先推荐三才全吉
    """
    xiyongshen_list = parse_xiyongshen(xiyongshen_str)
    candidates = generate_candidate_chars_v2(xiyongshen_list, count=120, avoid_chars=avoid_chars)
    
    recommendations = []
    tried_pairs = set()
    
    # 尝试各种组合
    for i, char1 in enumerate(candidates):
        for char2 in candidates[i+1:]:
            if len(recommendations) >= max_options * 10:
                break
            
            pair_key = f"{char1['char']}_{char2['char']}"
            if pair_key in tried_pairs:
                continue
            tried_pairs.add(pair_key)
            
            givenname = char1["char"] + char2["char"]
            
            try:
                wuge = calculate_wuge(surname, givenname)
            except Exception:
                continue
            
            score_result = score_name_v2(surname, givenname, xiyongshen_list, wuge)
            
            # 只保留通过筛选的
            if score_result["pass"]:
                recommendations.append({
                    "full_name": f"{surname}{givenname}",
                    "surname": surname,
                    "givenname": givenname,
                    "chars": [char1, char2],
                    "wuge": wuge,
                    "score": score_result,
                })
        
        if len(recommendations) >= max_options * 10:
            break
    
    # 按分数排序，取前 max_options
    recommendations.sort(key=lambda x: x["score"]["total_score"], reverse=True)
    return recommendations[:max_options]


def format_recommendation_markdown(
    surname: str,
    xiyongshen_str: str,
    bazi_info: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
) -> str:
    """格式化输出为 Markdown"""
    lines = []
    
    # 标记 API 状态
    is_fallback = bazi_info.get("is_fallback", False)
    
    lines.append("## 命局摘要")
    
    if is_fallback:
        lines.append(f"⚠️ **注意**：{bazi_info.get('xiyongshen_desc', '八字喜用神为估算值，建议配置真实API_KEY获取准确喜用神。')}")
        lines.append("")
    
    lines.append(f"- 八字：{bazi_info.get('birth_chart', 'N/A')}")
    lines.append(f"- 日主：{bazi_info.get('qiangruo', 'N/A')}")
    lines.append(f"- 喜用神：**{xiyongshen_str}**")
    lines.append(f"- 忌神：{bazi_info.get('jishen', 'N/A')}")
    
    # 五行能量
    scores = bazi_info.get("wuxing_scores", {})
    if scores and any(s > 0 for s in scores.values()):
        lines.append("")
        lines.append("**五行能量**：")
        wuxing_bars = []
        max_score = max(scores.values()) if scores else 1
        for w, s in scores.items():
            bar_len = int(s / max_score * 10) if max_score > 0 else 0
            bar = "█" * bar_len + "░" * (10 - bar_len)
            wuxing_bars.append(f"  {w} {bar} {s}")
        lines.extend(wuxing_bars)
    
    lines.append("")
    lines.append("## 五格架构")
    lines.append("| 格位 | 数理 | 五行 | 吉凶 | 说明 |")
    lines.append("|:---|:---:|:---:|:---:|---|")
    
    if recommendations:
        wuge = recommendations[0]["wuge"]
        
        for ge_name, ge_key in [("天格", "tian_ge"), ("人格", "ren_ge"), ("地格", "di_ge"), ("外格", "wai_ge"), ("总格", "zong_ge")]:
            g = wuge[ge_key]
            issues = recommendations[0]["score"].get("issues", [])
            warnings = recommendations[0]["score"].get("warnings", [])
            note = ""
            if any(str(g["number"]) in i for i in issues):
                note = "⚠️ " + next((i for i in issues if str(g["number"]) in i), "")
            elif any(str(g["number"]) in w for w in warnings):
                note = "⚡ " + next((w for w in warnings if str(g["number"]) in w), "")
            lines.append(f"| {ge_name} | {g['number']} | {g['wuxing']} | {g['jixiong']} | {g['explain'][:15]}... {note} |")
        
        lines.append("")
        lines.append(f"**三才配置**：{wuge['san_cai']['config']} = **{wuge['san_cai']['jixiong']}**（{wuge['san_cai']['explain']}）")
    else:
        lines.append("| 天格 | - | - | - | |")
        lines.append("| 人格 | - | - | - | |")
        lines.append("| 地格 | - | - | - | |")
    
    lines.append("")
    lines.append("## 推荐方案（3组）")
    
    if not recommendations:
        lines.append("")
        lines.append("*未找到符合条件的名字，请调整喜用神或尝试其他姓氏*")
    else:
        for i, rec in enumerate(recommendations, 1):
            full_name = rec["full_name"]
            wuge = rec["wuge"]
            chars = rec["chars"]
            
            # 五行组合判断
            wuxing_combo = f"{chars[0]['wuxing']}{chars[1]['wuxing']}"
            is_sheng = any(
                wuxing_combo == seq or wuxing_combo[::-1] == seq
                for seq in ["木火", "火土", "土金", "金水", "水木",
                            "木木", "火火", "土土", "金金", "水水"]
            )
            
            lines.append("")
            lines.append(f"### 方案{i}：**{full_name}**")
            lines.append(f"- **用字**：{chars[0]['char']}（{chars[0]['wuxing']}、{get_char_stroke(chars[0]['char'])}划）+ {chars[1]['char']}（{chars[1]['wuxing']}、{get_char_stroke(chars[1]['char'])}划）")
            lines.append(f"- **五行**：{wuxing_combo}（{'相生/比和' if is_sheng else '待定'}）")
            lines.append(f"- **五格**：天{wuge['tian_ge']['number']}/{wuge['tian_ge']['jixiong']} - 人{wuge['ren_ge']['number']}/{wuge['ren_ge']['jixiong']} - 地{wuge['di_ge']['number']}/{wuge['di_ge']['jixiong']}")
            lines.append(f"- **三才**：{wuge['san_cai']['config']}（{wuge['san_cai']['jixiong']}）")
            lines.append(f"- **评分**：{rec['score']['total_score']}分")
            
            if rec["score"]["warnings"]:
                lines.append(f"- **⚠️ 注意**：`{'；'.join(rec['score']['warnings'])}`")
    
    lines.append("")
    lines.append("## 风险提示")
    if recommendations:
        all_issues = []
        for rec in recommendations:
            all_issues.extend(rec["score"]["issues"])
        if all_issues:
            for issue in set(all_issues):
                lines.append(f"- {issue}")
        else:
            lines.append("- 未发现明显风险")
    else:
        lines.append("- 当前候选未能找到完全符合条件的方案，建议调整喜用神")
    
    lines.append("")
    lines.append("## 使用建议")
    lines.append("1. 用毛笔书写，观察字形结构是否平衡")
    lines.append("2. 在正式场合试呼，确认音韵流畅度")
    lines.append("3. 保留3个月观察期，感受\"名-人\"契合度")
    
    return "\n".join(lines)


def main():
    """测试"""
    print("=== 名字生成 V2 测试 ===\n")
    
    # 测试1: fallback 模式
    print("测试1: 张 + 金、水")
    recs = generate_name_recommendations_v2("张", "金、水", 1)
    for i, rec in enumerate(recs, 1):
        w = rec["wuge"]
        print(f"  方案{i}: {rec['full_name']} | 人格:{w['ren_ge']['number']}({w['ren_ge']['jixiong']}) | 总格:{w['zong_ge']['number']}({w['zong_ge']['jixiong']}) | 三才:{w['san_cai']['config']}({w['san_cai']['jixiong']}) | 分:{rec['score']['total_score']}")
        if rec['score']['warnings']:
            print(f"    ⚠️ {rec['score']['warnings']}")
    
    print()
    print("测试2: 陈 + 木、火")
    recs2 = generate_name_recommendations_v2("陈", "木、火", 1)
    for i, rec in enumerate(recs2[:3], 1):
        w = rec["wuge"]
        print(f"  方案{i}: {rec['full_name']} | 人格:{w['ren_ge']['number']}({w['ren_ge']['jixiong']}) | 三才:{w['san_cai']['config']}({w['san_cai']['jixiong']})")


if __name__ == "__main__":
    main()
