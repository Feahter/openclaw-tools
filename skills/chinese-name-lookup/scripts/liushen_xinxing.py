#!/usr/bin/env python3
"""
六神心性速查
基于《千里命稿》十神心性映射表

十神性格、职业倾向、六亲关系查询。
"""

from typing import Dict, List, Any

# ============================================================
# 十神心性数据表（来源：《千里命稿》）
# ============================================================

# 十神心性主表
SHISHEN_XINXING_TABLE: Dict[str, Dict[str, Any]] = {
    "比肩": {
        "性别倾向": "中",
        "性格特点": ["独立", "自尊", "固执", "重朋友"],
        "职业倾向": ["自由职业者", "创业者"],
        "六亲关系": "兄弟",
        "性格解读": "比肩者，独立自主之人也。自尊心强，不喜依赖他人，行事果断有主见，广交天下友。然过刚则折，固执己见，不善变通。",
    },
    "劫财": {
        "性别倾向": "男重",
        "性格特点": ["义气", "不服输", "投机", "冲动"],
        "职业倾向": ["贸易", "投资", "运动员"],
        "六亲关系": "兄弟姐妹",
        "性格解读": "劫财者，义气豪爽之人也。见弱扶危，不畏强暴，不甘人后，敢于冒险。然性急冲动，好胜心强，财利上易有损耗。",
    },
    "食神": {
        "性别倾向": "女重",
        "性格特点": ["温和", "善良", "好吃懒做", "创新"],
        "职业倾向": ["餐饮", "演艺", "设计", "策划"],
        "六亲关系": "晚辈子女",
        "性格解读": "食神者，温和善良之人也。性善心宽，重精神轻物质，创意丰富，感受力强。然过于懒散，不喜约束，自由散漫。",
    },
    "伤官": {
        "性别倾向": "女重",
        "性格特点": ["聪明", "叛逆", "口才", "不服管"],
        "职业倾向": ["艺术", "律师", "记者", "自由职业"],
        "六亲关系": "祖父/子孙",
        "性格解读": "伤官者，聪明伶俐之人也。才华横溢，口才好，善表现，不畏权贵。然叛逆心强，不受约束，好胜心盛，易惹是非。",
    },
    "正财": {
        "性别倾向": "男重",
        "性格特点": ["务实", "节俭", "谨慎", "占有欲"],
        "职业倾向": ["财务", "会计", "金融", "贸易"],
        "六亲关系": "妻子",
        "性格解读": "正财者，务实勤俭之人也。脚踏实地，精打细算，谨慎行事，理财有方。然占有欲强，过于吝啬，情感上较保守。",
    },
    "偏财": {
        "性别倾向": "男重",
        "性格特点": ["慷慨", "交际", "投机", "圆滑"],
        "职业倾向": ["投资", "金融", "贸易", "企业"],
        "六亲关系": "父亲/妾",
        "性格解读": "偏财者，慷慨豪爽之人也。善交际，广结缘，敢于投机，头脑灵活。然来得快去也快，感情上易有波折，父缘较深。",
    },
    "正官": {
        "性别倾向": "女重",
        "性格特点": ["正直", "有责任心", "保守", "守法"],
        "职业倾向": ["公务员", "管理", "法律", "事业单位"],
        "六亲关系": "丈夫/官府",
        "性格解读": "正官者，正直守法之人也。为人光明磊落，有责任心，重名誉，守规矩。然过于保守，不善变通，官场上宜守成。",
    },
    "七杀": {
        "性别倾向": "男重",
        "性格特点": ["果断", "权威", "激进", "冒险"],
        "职业倾向": ["军警", "执法", "运动员", "企业家"],
        "六亲关系": "权威/压力",
        "性格解读": "七杀者，权威果断之人也。行事雷厉风行，不畏艰难，敢于冒险竞争，有领导力。然过刚易折，易树敌，压力大。",
    },
    "正印": {
        "性别倾向": "女重",
        "性格特点": ["仁慈", "有爱心", "依赖", "保守"],
        "职业倾向": ["教育", "医疗", "慈善", "文化"],
        "六亲关系": "母亲/文书",
        "性格解读": "正印者，仁慈博爱之人也。有爱心，善奉献，重名誉，依赖心强。然过于保守，不善竞争，宜做幕僚或服务类工作。",
    },
    "偏印": {
        "性别倾向": "中",
        "性格特点": ["悟性高", "孤独", "冷门", "创意"],
        "职业倾向": ["学术", "研究", "技艺", "医师"],
        "六亲关系": "继母/祖父",
        "性格解读": "偏印者，悟性极高之人也。思维敏锐，善于分析，喜静不喜动，多有技艺傍身。然性格孤僻，不善交际，多劳碌命。",
    },
}

# 所有十神名称列表（保持顺序）
ALL_SHISHEN = ["比肩", "劫财", "食神", "伤官", "正财", "偏财", "正官", "七杀", "正印", "偏印"]


# ============================================================
# 核心查询函数
# ============================================================

def get_shishen_xinxing(shishen_type: str) -> Dict[str, Any]:
    """
    查询单个十神的心性信息

    Args:
        shishen_type: 十神名称（如"比肩"、"食神"、"正官"等）

    Returns:
        包含心性信息的字典，字段：
        - exists: bool, 是否存在该十神
        - name: str, 十神名称
        - gender_tendency: str, 性别倾向
        - personality: List[str], 性格特点列表
        - career: List[str], 职业倾向列表
        - liuqin: str, 六亲关系
        - interpretation: str, 性格解读
    """
    info = SHISHEN_XINXING_TABLE.get(shishen_type)

    if info is None:
        return {
            "exists": False,
            "name": shishen_type,
            "error": f"未知的十神类型：{shishen_type}",
        }

    return {
        "exists": True,
        "name": shishen_type,
        "gender_tendency": info["性别倾向"],
        "personality": info["性格特点"],
        "career": info["职业倾向"],
        "liuqin": info["六亲关系"],
        "interpretation": info["性格解读"],
    }


def get_liuqin_relation(shishen_type: str, gender: int) -> str:
    """
    查询十神对应的六亲关系（考虑性别）

    Args:
        shishen_type: 十神名称
        gender: 性别 (1=男, 0=女)

    Returns:
        六亲关系描述字符串
    """
    info = SHISHEN_XINXING_TABLE.get(shishen_type)
    if info is None:
        return "未知"

    liuqin = info["六亲关系"]
    gender_tendency = info["性别倾向"]

    # 根据性别细化六亲关系
    # 有些十神的六亲关系与性别相关
    if "/" in liuqin:
        parts = liuqin.split("/")
        if gender == 1:  # 男
            return parts[0]
        else:  # 女
            return parts[1] if len(parts) > 1 else parts[0]

    return liuqin


def get_career_suggestion(shishen_list: List[Dict[str, str]]) -> List[str]:
    """
    根据十神列表生成职业建议

    Args:
        shishen_list: 十神字典列表，每个元素包含 "name" 和可选的 "role" 字段
                    例如：[{"name": "食神"}, {"name": "正印"}]
                    或 [{"name": "食神", "role": "用神"}, {"name": "七杀", "role": "忌神"}]

    Returns:
        去重排序后的职业建议列表
    """
    career_map = {}

    for item in shishen_list:
        name = item.get("name", "")
        role = item.get("role", "")  # 用神/忌神/中性

        info = SHISHEN_XINXING_TABLE.get(name)
        if info is None:
            continue

        # 权重：用神优先，忌神降权
        weight = 1.0
        if role == "用神":
            weight = 1.5
        elif role == "忌神":
            weight = 0.5

        for career in info["职业倾向"]:
            if career not in career_map:
                career_map[career] = 0.0
            career_map[career] += weight

    # 按权重排序
    sorted_careers = sorted(career_map.items(), key=lambda x: x[1], reverse=True)

    # 返回推荐职业（去重，权重 > 0.5）
    result = []
    for career, score in sorted_careers:
        if score >= 0.5:
            result.append(career)

    return result[:8]  # 最多返回8个


def get_full_xinxing_report(shishen_list: List[Dict[str, str]]) -> str:
    """
    生成完整的十神心性报告

    Args:
        shishen_list: 十神字典列表，每个元素包含:
                    - name: str, 十神名称
                    - role: str (optional), 角色：用神/忌神/中性
                    - pillar: str (optional), 所在柱：如"年干"、"月支"等

    Returns:
        Markdown 格式的心性报告字符串
    """
    if not shishen_list:
        return "*无十神数据*"

    lines = []
    lines.append("### 十神心性解读")
    lines.append("")

    # 统计各类十神数量
    shishen_count = {}
    for item in shishen_list:
        name = item.get("name", "")
        if name:
            shishen_count[name] = shishen_count.get(name, 0) + 1

    # 按十神分类输出
    # 核心用神优先输出
    yongshen_items = [item for item in shishen_list if item.get("role") == "用神"]
    jishen_items = [item for item in shishen_list if item.get("role") == "忌神"]
    other_items = [item for item in shishen_list if item.get("role") not in ("用神", "忌神")]

    # 用神解读
    if yongshen_items:
        lines.append("**【用神心性】**（命局所需，发挥正面作用）")
        lines.append("")
        for item in yongshen_items:
            name = item.get("name", "")
            pillar = item.get("pillar", "")
            info = SHISHEN_XINXING_TABLE.get(name)
            if info:
                pillar_str = f"（{pillar}）" if pillar else ""
                lines.append(f"- **{name}**{pillar_str}：{info['性格解读']}")
        lines.append("")

    # 忌神解读
    if jishen_items:
        lines.append("**【忌神心性】**（命局所忌，需要注意调和）")
        lines.append("")
        for item in jishen_items:
            name = item.get("name", "")
            pillar = item.get("pillar", "")
            info = SHISHEN_XINXING_TABLE.get(name)
            if info:
                pillar_str = f"（{pillar}）" if pillar else ""
                lines.append(f"- **{name}**{pillar_str}：{info['性格解读']}")
        lines.append("")

    # 其他十神解读
    if other_items:
        lines.append("**【命局十神】**")
        lines.append("")
        for item in other_items:
            name = item.get("name", "")
            pillar = item.get("pillar", "")
            info = SHISHEN_XINXING_TABLE.get(name)
            if info:
                pillar_str = f"（{pillar}）" if pillar else ""
                lines.append(f"- **{name}**{pillar_str}：{info['性格解读']}")
        lines.append("")

    # 性格特点总结
    all_traits = []
    for item in shishen_list:
        name = item.get("name", "")
        info = SHISHEN_XINXING_TABLE.get(name)
        if info:
            all_traits.extend(info["性格特点"])

    if all_traits:
        # 去重但保持顺序
        seen = set()
        unique_traits = []
        for t in all_traits:
            if t not in seen:
                seen.add(t)
                unique_traits.append(t)

        lines.append("**性格标签**：" + "、".join(unique_traits[:8]))
        lines.append("")

    # 职业建议
    career_suggestions = get_career_suggestion(shishen_list)
    if career_suggestions:
        lines.append("**职业建议**：" + "、".join(career_suggestions[:5]))

    return "\n".join(lines)


def build_shishen_xinxing_from_bazi(bazi_info: Dict[str, Any], xiyongshen: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """
    从八字分析结果构建十神心性数据

    Args:
        bazi_info: 八字分析结果（来自 full_bazi_analysis）
        xiyongshen: 喜用神信息

    Returns:
        包含各柱十神及其心性信息的字典
    """
    shishen_data = bazi_info.get("shishen", {})
    xiyong_list = xiyongshen.get("xiyongshen", [])
    jishen_list = xiyongshen.get("jishen", [])

    def get_role(name: str) -> str:
        if name in xiyong_list:
            return "用神"
        elif name in jishen_list:
            return "忌神"
        return "中性"

    result = []

    # 年柱
    for key, pillar_name in [("year_stem", "年干"), ("year_branch", "年支")]:
        name = shishen_data.get(key, "")
        if name:
            result.append({"name": name, "role": get_role(name), "pillar": pillar_name})

    # 月柱
    for key, pillar_name in [("month_stem", "月干"), ("month_branch", "月支")]:
        name = shishen_data.get(key, "")
        if name:
            result.append({"name": name, "role": get_role(name), "pillar": pillar_name})

    # 日支
    day_branch = shishen_data.get("day_branch", "")
    if day_branch:
        result.append({"name": day_branch, "role": get_role(day_branch), "pillar": "日支"})

    # 时柱
    for key, pillar_name in [("hour_stem", "时干"), ("hour_branch", "时支")]:
        name = shishen_data.get(key, "")
        if name:
            result.append({"name": name, "role": get_role(name), "pillar": pillar_name})

    return result


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=== 六神心性速查测试 ===\n")

    # 测试1: 单个十神查询
    print("【测试1】食神心性查询")
    info = get_shishen_xinxing("食神")
    print(f"  名称: {info['name']}")
    print(f"  性别倾向: {info['gender_tendency']}")
    print(f"  性格特点: {'、'.join(info['personality'])}")
    print(f"  职业倾向: {'、'.join(info['career'])}")
    print(f"  六亲关系: {info['liuqin']}")
    print(f"  性格解读: {info['interpretation']}")
    print()

    # 测试2: 六亲关系（男/女）
    print("【测试2】偏财六亲关系")
    print(f"  男性: {get_liuqin_relation('偏财', 1)}")
    print(f"  女性: {get_liuqin_relation('偏财', 0)}")
    print()

    # 测试3: 职业建议
    print("【测试3】职业建议（食神+正印为用神）")
    shishen_list = [
        {"name": "食神", "role": "用神"},
        {"name": "正印", "role": "用神"},
        {"name": "七杀", "role": "忌神"},
    ]
    careers = get_career_suggestion(shishen_list)
    print(f"  建议职业: {'、'.join(careers)}")
    print()

    # 测试4: 完整心性报告
    print("【测试4】完整心性报告")
    report = get_full_xinxing_report(shishen_list)
    print(report)
    print()

    # 测试5: 测试用例：食神为用——艺术气质
    print("=" * 40)
    print("【测试用例1】食神为用：艺术气质")
    shishen_shigin = [{"name": "食神", "role": "用神", "pillar": "月干"}]
    info = get_shishen_xinxing("食神")
    print(f"  性格特点: {'、'.join(info['personality'])}")
    print(f"  职业倾向: {'、'.join(info['career'])}")
    print(f"  → 推断: 艺术气质、创新能力强，适合创意类工作")
    print()

    # 测试6: 测试用例：官杀旺——事业心强
    print("【测试用例2】官杀旺：事业心强")
    shishen_guansha = [
        {"name": "七杀", "role": "用神", "pillar": "年干"},
        {"name": "正官", "role": "忌神", "pillar": "月干"},
    ]
    for name in ["七杀", "正官"]:
        info = get_shishen_xinxing(name)
        print(f"  {name}: {'、'.join(info['personality'])}")
    print(f"  → 推断: 事业心强，有领导力，敢于竞争")
    print()

    # 测试7: 测试用例：印星为用——学业运佳
    print("【测试用例3】印星为用：学业运佳")
    shishen_yin = [
        {"name": "正印", "role": "用神", "pillar": "年干"},
        {"name": "偏印", "role": "忌神", "pillar": "月支"},
    ]
    for name in ["正印", "偏印"]:
        info = get_shishen_xinxing(name)
        print(f"  {name}: {'、'.join(info['personality'])}")
    print(f"  → 推断: 学业运佳，有学术研究天赋，宜教育文化类工作")
    print()
