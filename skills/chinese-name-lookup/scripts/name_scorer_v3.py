#!/usr/bin/env python3
"""
名字推荐 V3：喜用神 + 生肖 + 十神/长生 三维评分
整合八字引擎 + 生肖宜忌 + 十神补益
"""

import random
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# 导入本地模块
import sys
sys.path.insert(0, str(Path(__file__).parent))

from bazi_engine import (
    full_bazi_analysis, get_rizhu_strength, get_shishen_list, get_shierzhang,
    STEM_ELEMENTS, ELEMENT_NAMES, HEAVENLY_STEMS
)
from zodiac_preferences import score_name_for_zodiac, get_zodiac_preferences
from wuge_calculator import calculate_wuge, get_char_wuxing, get_char_stroke

# 喜用神扩充字库
XIYONGSHEN_WORDS = {
    "金": ["铭", "锋", "锐", "锦", "鑫", "铎", "锡", "钧", "镇", "镕", "铠", "钱", "镜", "钻", "银", "锡", "钧", "钢", "镖", "镍"],
    "水": ["泽", "涵", "润", "清", "澜", "洁", "淳", "泉", "波", "涛", "瀚", "溪", "潮", "汐", "渊", "漾", "溢", "沐", "波", "洁"],
    "木": ["森", "林", "松", "柏", "桐", "梓", "榆", "楠", "栋", "梁", "柱", "杨", "柳", "枫", "槐", "杉", "彬", "楷", "贤", "栋"],
    "火": ["炎", "灿", "炜", "熠", "焕", "煌", "耀", "曦", "炫", "晟", "昭", "晖", "明", "旭", "辉", "昌", "哲", "晔", "昊", "朗"],
    "土": ["城", "垣", "培", "基", "坚", "坤", "厚", "坦", "增", "墨", "圣", "均", "堪", "塘", "境", "壁", "壤", "坛", "壑", "垢"],
}

# 常用好字
COMMON_GOOD_CHARS = [
    "安", "昂", "傲", "柏", "宝", "博", "才", "苍", "超", "琛", "晨", "成", "承", "诚", "城", "程", "崇", "川", "春",
    "慈", "聪", "丹", "道", "德", "鼎", "定", "东", "冬", "铎", "恩", "帆", "方", "芳", "飞", "风", "福", "刚", "高",
    "歌", "根", "功", "冠", "光", "广", "贵", "国", "海", "翰", "航", "浩", "和", "河", "荷", "恒", "弘", "红", "宏",
    "华", "怀", "辉", "汇", "慧", "嘉", "家", "建", "健", "洁", "锦", "进", "晋", "京", "经", "景", "静", "敬", "镜",
    "炯", "玖", "聚", "军", "俊", "峻", "康", "克", "宽", "葵", "来", "岚", "蓝", "朗", "乐", "磊", "理", "礼", "力",
    "立", "连", "良", "林", "临", "霖", "灵", "凌", "龙", "隆", "楼", "露", "路", "洛", "梅", "美", "孟", "民", "明",
    "鸣", "墨", "默", "沐", "娜", "宁", "培", "鹏", "平", "启", "谦", "强", "勤", "清", "晴", "庆", "秋", "全", "权",
    "泉", "然", "仁", "融", "如", "瑞", "睿", "润", "若", "森", "山", "善", "绍", "深", "生", "盛", "石", "时", "实",
    "书", "舒", "树", "帅", "双", "顺", "思", "硕", "松", "涛", "天", "亭", "通", "桐", "威", "文", "问", "西", "希",
    "惜", "熙", "夏", "先", "祥", "向", "晓", "笑", "效", "新", "心", "辛", "信", "兴", "星", "修", "旭", "栩", "轩",
    "宣", "学", "雪", "勋", "循", "雅", "亚", "彦", "曜", "耀", "烨", "伊", "依", "颐", "仪", "宜", "怡", "义", "艺",
    "易", "益", "逸", "毅", "翼", "英", "盈", "永", "咏", "泳", "勇", "用", "优", "悠", "游", "有", "于", "宇", "羽",
    "雨", "语", "玉", "裕", "预", "元", "圆", "远", "月", "岳", "云", "允", "运", "韵", "泽", "增", "昭", "哲", "振",
    "正", "政", "之", "知", "直", "植", "至", "致", "治", "智", "中", "仲", "舟", "州", "洲", "竹", "卓", "琢", "子",
    "紫", "自", "宗", "祖",
]

# 好听的名字组合
GOOD_NAME_EXAMPLES = [
    ("泽", "楷"), ("锦", "泽"), ("铭", "泽"), ("润", "泽"), ("思", "远"), ("景", "行"), ("明", "德"), ("文", "礼"),
    ("安", "然"), ("静", "好"), ("清", "欢"), ("时", "雨"), ("栀", "晴"), ("望", "晴"), ("言", "蹊"), ("知", "意"),
    ("沐", "晴"), ("子", "墨"), ("星", "然"), ("晚", "棠"), ("锦", "程"), ("安", "澜"), ("清", "欢"), ("知", "许"),
    ("言", "希"), ("林", "深"), ("鹿", "鸣"), ("青", "梧"), ("顾", "盼"), ("顾", "念"), ("言", "晚"), ("林", "染"),
]


# ============================================================
# 喜用神评分 (0-40分)
# ============================================================

def score_by_xiyongshen(name_chars: str, xiyongshen_list: List[str]) -> Dict[str, Any]:
    """
    喜用神评分：0-40分
    每个字匹配喜用神+10分，最高40分
    """
    if not xiyongshen_list:
        return {"score": 0, "matched": [], "reason": "未提供喜用神"}

    score = 0
    matched = []

    for char in name_chars:
        char_wuxing = get_char_wuxing(char)
        if char_wuxing in xiyongshen_list:
            score += 10
            matched.append({"char": char, "wuxing": char_wuxing})

    score = min(score, 40)  # 最高40分

    return {
        "score": score,
        "matched": matched,
        "reason": f"名字「{name_chars}」中{'有' if matched else '无'}喜用神字({','.join(xiyongshen_list)})",
    }


# ============================================================
# 生肖宜忌评分 (0-30分)
# ============================================================

def score_by_zodiac(name_chars: str, zodiac: str) -> Dict[str, Any]:
    """
    生肖宜忌评分：0-30分
    使用 zodiac_preferences 模块评分
    """
    if not zodiac:
        return {"score": 0, "reason": "未提供生肖"}

    result = score_name_for_zodiac(name_chars, zodiac)

    # 标准化到0-30
    raw = result.get("score", 0)
    # 原始评分0-30映射到0-30
    normalized = raw

    return {
        "score": normalized,
        "raw_score": result.get("raw_score", 0),
        "details": result.get("details", []),
        "reason": result.get("summary", ""),
        "lucky_numbers": result.get("lucky_numbers", []),
        "directions": result.get("directions", []),
    }


# ============================================================
# 十神/长生评分 (0-30分)
# ============================================================

def score_by_shishen(bazi_info: Dict[str, Any], name_chars: str) -> Dict[str, Any]:
    """
    十神/长生评分：0-30分
    基于八字喜用神和十神关系给分
    """
    bazi = bazi_info.get("bazi", {})
    xiyongshen_list = bazi_info.get("xiyongshen", {}).get("xiyongshen", [])

    if not bazi or not xiyongshen_list:
        return {"score": 0, "reason": "八字信息不完整"}

    day_stem_idx = bazi.get("day", {}).get("stem_idx", 0)
    day_stem = HEAVENLY_STEMS[day_stem_idx]

    score = 0
    details = []

    # 分析名字中每个字的五行对应的十神
    for char in name_chars:
        char_wuxing = get_char_wuxing(char)

        # 找到喜用神对应的十神
        # 食神、伤官：我生者
        # 财：我克者
        # 官：克我者
        # 印：生我者

        xiyong_wuxing_set = set(xiyongshen_list)

        if char_wuxing in xiyong_wuxing_set:
            # 喜用神五行在名字中
            # 找到char_wuxing对应的十神
            for i, e in enumerate(ELEMENT_NAMES):
                if e == char_wuxing:
                    diff = (i - STEM_ELEMENTS[day_stem_idx] + 5) % 5
                    if diff == 1:
                        shishen = "食神" if day_stem_idx % 2 == 0 else "伤官"
                        score += 8
                        details.append(f"「{char}」（{char_wuxing}）为喜用{shishen}，+8分")
                    elif diff == 2:
                        shishen = "偏财" if day_stem_idx % 2 == 0 else "正财"
                        score += 8
                        details.append(f"「{char}」（{char_wuxing}）为喜用{shishen}，+8分")
                    elif diff == 3:
                        shishen = "偏官" if day_stem_idx % 2 == 0 else "正官"
                        score += 8
                        details.append(f"「{char}」（{char_wuxing}）为喜用{shishen}，+8分")
                    elif diff == 4:
                        shishen = "偏印" if day_stem_idx % 2 == 0 else "正印"
                        score += 8
                        details.append(f"「{char}」（{char_wuxing}）为喜用{shishen}，+8分")
                    break

    score = min(score, 30)

    return {
        "score": score,
        "details": details,
        "reason": f"名字中含喜用神对应的十神配置" if details else "名字中无明显十神补益",
    }


# ============================================================
# 五格评分 (辅助)
# ============================================================

def score_by_wuge(surname: str, givenname: str) -> Dict[str, Any]:
    """
    五格数理评分（辅助）：主要看人格和总格
    """
    try:
        wuge = calculate_wuge(surname, givenname)
    except Exception as e:
        return {"score": 0, "wuge": None, "reason": f"五格计算失败: {e}"}

    ren = wuge["ren_ge"]["number"]
    zong = wuge["zong_ge"]["number"]

    # 凶数列表
    FORBIDDEN = {2, 4, 9, 10, 12, 14, 19, 20, 22, 26, 28, 34, 36, 37, 43, 44, 46, 49, 50, 54, 56, 58, 59, 60, 64, 66, 69, 70, 72, 73, 74, 75, 76, 77, 78, 79, 80}

    score = 0
    issues = []

    if ren in FORBIDDEN:
        issues.append(f"人格{ren}为凶数")
        score -= 20
    if zong in FORBIDDEN:
        issues.append(f"总格{zong}为凶数")
        score -= 20

    san_cai = wuge["san_cai"]
    if san_cai["jixiong"] == "吉":
        score += 15
    elif san_cai["jixiong"] == "半吉":
        score += 8
    else:
        score -= 10
        issues.append(f"三才{san_cai['config']}为凶")

    score = max(0, min(score, 25))

    return {
        "score": score,
        "wuge": wuge,
        "issues": issues,
        "reason": f"人格{ren}({wuge['ren_ge']['jixiong']})/总格{zong}({wuge['zong_ge']['jixiong']})" + (f", 三才{san_cai['jixiong']}" if san_cai else ""),
    }


# ============================================================
# 总评分
# ============================================================

def score_name_v3(
    surname: str,
    name_chars: str,
    bazi_info: Dict[str, Any],
) -> Dict[str, Any]:
    """
    三维评分 + 五格辅助 = 总评分
    满分: 喜用神(40) + 生肖(30) + 十神(30) + 五格(25) = 125分制
    标准化到100分制输出
    """
    zodiac = bazi_info.get("zodiac", "")
    xiyongshen_list = bazi_info.get("xiyongshen", {}).get("xiyongshen", [])

    # 三维评分
    xiyong_result = score_by_xiyongshen(name_chars, xiyongshen_list)
    zodiac_result = score_by_zodiac(name_chars, zodiac)
    shishen_result = score_by_shishen(bazi_info, name_chars)
    wuge_result = score_by_wuge(surname, name_chars)

    # 各维度得分
    dim_scores = {
        "喜用神匹配": xiyong_result["score"],
        "生肖宜忌": zodiac_result["score"],
        "十神/长生": shishen_result["score"],
        "五格数理": wuge_result["score"],
    }

    total_raw = sum(dim_scores.values())
    # 标准化到100分
    total_score = int(total_raw * 100 / 125)

    # ============================================================
    # 冲突检测与调整
    # ============================================================
    # 当喜用神与生肖冲突时（如喜用神=水，但生肖=蛇忌水），
    # 降低生肖权重，提高喜用神权重，确保有意义的推荐能通过
    xiyongshen_list = bazi_info.get("xiyongshen", {}).get("xiyongshen", [])
    zodiac = bazi_info.get("zodiac", "")

    zodiac_conflict = False
    if zodiac and xiyongshen_list:
        # 检测生肖与喜用神是否冲突
        # 生肖忌水，喜用神是水 → 冲突
        zodiac_avoids = set()
        prefs = get_zodiac_preferences(zodiac)
        if prefs:
            for item in prefs.get("avoid_chars", []):
                if item in ["水", "氵"]:
                    zodiac_avoids.add("水")
                elif item in ["木"]:
                    zodiac_avoids.add("木")
                elif item in ["火", "灬"]:
                    zodiac_avoids.add("火")
                elif item in ["土"]:
                    zodiac_avoids.add("土")
                elif item in ["金", "钅"]:
                    zodiac_avoids.add("金")

        xiyongset = set(xiyongshen_list)
        if zodiac_avoids & xiyongset:  # 有交集 = 冲突
            zodiac_conflict = True

    # 冲突时：生肖分数按原样+5加成（喜用神override生肖）
    if zodiac_conflict:
        adj_zodiac = zodiac_result["score"] + 5
        adj_zodiac = min(30, adj_zodiac)  # 上限30
    else:
        adj_zodiac = zodiac_result["score"]

    adj_dim_scores = {
        "喜用神匹配": xiyong_result["score"],
        "生肖宜忌": adj_zodiac,
        "十神/长生": shishen_result["score"],
        "五格数理": wuge_result["score"],
    }
    adj_total_raw = sum(adj_dim_scores.values())
    adj_total = int(adj_total_raw * 100 / 125)

    # 判断是否通过
    # 条件：总分≥42 且 五格无大凶（人格/总格为凶数）
    has_big_wuge_issue = any("人格" in i and "凶数" in i for i in wuge_result.get("issues", [])) or \
                         any("总格" in i and "凶数" in i for i in wuge_result.get("issues", []))

    # 有冲突时更宽松：总分≥38即可
    pass_threshold = 38 if zodiac_conflict else 45
    pass_flag = adj_total >= pass_threshold and not has_big_wuge_issue

    total_score = adj_total
    dim_scores = adj_dim_scores

    # 收集所有理由
    reasons = []
    if xiyong_result["matched"]:
        reasons.append(f"喜用神「{','.join(xiyongshen_list)}」匹配{len(xiyong_result['matched'])}字")
    if zodiac_result.get("details"):
        reasons.append(f"生肖「{zodiac}」{'宜' if zodiac_result['score'] >= 15 else '欠'}佳")
    if shishen_result.get("details"):
        reasons.append("十神配置良好")
    if wuge_result.get("issues"):
        reasons.extend(wuge_result["issues"])

    return {
        "full_name": f"{surname}{name_chars}",
        "surname": surname,
        "name_chars": name_chars,
        "total_score": total_score,
        "dim_scores": dim_scores,
        "details": {
            "喜用神": xiyong_result,
            "生肖": zodiac_result,
            "十神": shishen_result,
            "五格": wuge_result,
        },
        "pass": pass_flag,
        "reasons": reasons,
        "zodiac": zodiac,
        "xiyongshen": xiyongshen_list,
    }


# ============================================================
# 候选字生成
# ============================================================

def generate_candidates(xiyongshen_list: List[str], count: int = 150) -> List[Dict[str, Any]]:
    """生成候选汉字列表"""
    candidates = []
    seen = set()

    # 优先从喜用神字库取
    for wuxing in xiyongshen_list:
        words = XIYONGSHEN_WORDS.get(wuxing, [])
        for char in words:
            if char not in seen:
                stroke = get_char_stroke(char) or 8
                candidates.append({"char": char, "wuxing": wuxing, "stroke": stroke})
                seen.add(char)

    # 补充常用好字
    for char in COMMON_GOOD_CHARS:
        if char not in seen:
            stroke = get_char_stroke(char) or 8
            candidates.append({"char": char, "wuxing": get_char_wuxing(char), "stroke": stroke})
            seen.add(char)

    random.shuffle(candidates)
    return candidates[:count]


# ============================================================
# V3 名字推荐生成
# ============================================================

def generate_names_v3(
    surname: str,
    bazi_info: Dict[str, Any],
    gender: int = 1,
    max_options: int = 3,
) -> List[Dict[str, Any]]:
    """
    生成名字推荐 V3
    三维评分 + 五格辅助
    """
    xiyongshen_list = bazi_info.get("xiyongshen", {}).get("xiyongshen", [])
    zodiac = bazi_info.get("zodiac", "")

    if not xiyongshen_list:
        xiyongshen_list = ["金", "水"]  # 默认

    # 生成候选字
    candidates = generate_candidates(xiyongshen_list, count=200)

    recommendations = []
    tried = set()

    # 尝试各种组合
    for i, c1 in enumerate(candidates):
        for c2 in candidates[i+1:]:
            pair_key = f"{c1['char']}_{c2['char']}"
            if pair_key in tried:
                continue
            tried.add(pair_key)

            givenname = c1["char"] + c2["char"]
            result = score_name_v3(surname, givenname, bazi_info)

            if result["pass"]:
                recommendations.append(result)

            if len(tried) >= 5000:
                break
        if len(tried) >= 5000:
            break

    # 按分数排序
    recommendations.sort(key=lambda x: x["total_score"], reverse=True)
    return recommendations[:max_options]


# ============================================================
# 格式化输出
# ============================================================

def format_v3_markdown(
    surname: str,
    bazi_info: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
) -> str:
    """格式化输出为 Markdown"""
    lines = []

    lines.append("## 命局分析（本地引擎）")

    birth_chart = bazi_info.get("birth_chart", "N/A")
    zodiac = bazi_info.get("zodiac", "N/A")
    xiyongshen = bazi_info.get("xiyongshen", {})
    xiyongshen_list = xiyongshen.get("xiyongshen", [])

    lines.append(f"- 八字：{birth_chart}")
    lines.append(f"- 生肖：{zodiac}")
    lines.append(f"- 日主：{xiyongshen.get('qiangruo', 'N/A')}")
    lines.append(f"- 喜用神：**{'、'.join(xiyongshen_list)}**")
    lines.append(f"- 忌神：{'、'.join(xiyongshen.get('jishen', []))}")

    # 五行统计
    wx_counts = xiyongshen.get("wx_counts", {})
    if wx_counts:
        lines.append("")
        lines.append("**五行分布**：")
        bars = []
        max_count = max(wx_counts.values()) if wx_counts else 1
        for elem, cnt in wx_counts.items():
            bar_len = int(cnt / max_count * 10) if max_count > 0 else 0
            bars.append(f"  {elem} {'█' * bar_len}{'░' * (10-bar_len)} {cnt}个")
        lines.extend(bars)

    lines.append("")
    lines.append("## 推荐方案（V3三维评分）")

    if not recommendations:
        lines.append("")
        lines.append("*未找到符合条件的名字，请调整参数*")
    else:
        for i, rec in enumerate(recommendations, 1):
            lines.append("")
            lines.append(f"### 方案{i}：**{rec['full_name']}** ({rec['total_score']}分)")

            dim = rec["dim_scores"]
            lines.append(f"- 喜用神: {dim['喜用神匹配']}/40 | 生肖: {dim['生肖宜忌']}/30 | 十神: {dim['十神/长生']}/30 | 五格: {dim['五格数理']}/25")

            # 用字分析
            details = rec["details"]
            if details["喜用神"].get("matched"):
                matched = [f"{m['char']}({m['wuxing']})" for m in details["喜用神"]["matched"]]
                lines.append(f"- 喜用神匹配：{', '.join(matched)}")
            if details["生肖"].get("details"):
                lines.append(f"- 生肖宜忌：{'；'.join(details['生肖']['details'])}")
            if details["十神"].get("details"):
                lines.append(f"- 十神补益：{'；'.join(details['十神']['details'])}")
            if details["五格"].get("wuge"):
                wuge = details["五格"]["wuge"]
                lines.append(f"- 五格：人{wuge['ren_ge']['number']}({wuge['ren_ge']['jixiong']})/总{wuge['zong_ge']['number']}({wuge['zong_ge']['jixiong']})/三才{wuge['san_cai']['config']}({wuge['san_cai']['jixiong']})")

            if rec.get("reasons"):
                lines.append(f"- 评价：{'；'.join(rec['reasons'])}")

    lines.append("")
    lines.append("## 使用建议")
    lines.append("1. 以上为纯本地计算结果，可作为参考")
    lines.append("2. 建议配合八字API获取更精确的喜用神")
    lines.append("3. 最终取名还需结合音韵、寓意、家庭喜好等因素")

    return "\n".join(lines)


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=== 名字评分 V3 测试 ===\n")

    # 测试八字分析
    from bazi_engine import full_bazi_analysis

    # 测试1: 2024年3月15日10点
    print("【测试1】2024年3月15日10点")
    bazi = full_bazi_analysis(2024, 3, 15, 10)
    print(f"  八字: {bazi['birth_chart']}")
    print(f"  生肖: {bazi['zodiac']}")
    print(f"  喜用神: {bazi['xiyongshen']['xiyongshen']}")
    print(f"  日主强弱: {bazi['rizhu_strength']['strength']}")
    print()

    # 测试2: 评分
    test_name = "铭泽"
    result = score_name_v3("张", test_name, bazi)
    print(f"【测试2】名字「{test_name}」评分")
    print(f"  总分: {result['total_score']}/100")
    print(f"  维度: 喜用神={result['dim_scores']['喜用神匹配']}/40 | 生肖={result['dim_scores']['生肖宜忌']}/30 | 十神={result['dim_scores']['十神/长生']}/30 | 五格={result['dim_scores']['五格数理']}/25")
    print(f"  通过: {result['pass']}")
    if result.get("reasons"):
        print(f"  理由: {'；'.join(result['reasons'])}")
    print()

    # 测试3: 生成推荐
    print("【测试3】生成推荐（姓氏=张）")
    recs = generate_names_v3("张", bazi, max_options=3)
    for i, rec in enumerate(recs, 1):
        print(f"  方案{i}: {rec['full_name']} ({rec['total_score']}分)")
        print(f"    维度: 喜用={rec['dim_scores']['喜用神匹配']} 生肖={rec['dim_scores']['生肖宜忌']} 十神={rec['dim_scores']['十神/长生']} 五格={rec['dim_scores']['五格数理']}")
    print()

    # 测试4: Markdown格式化
    print("【测试4】Markdown格式化输出")
    md = format_v3_markdown("张", bazi, recs)
    print(md[:500] + "...")
