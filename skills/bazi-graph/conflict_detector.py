#!/usr/bin/env python3
"""
八字冲突检测模块 v2
检测四大矛盾信号：官杀混杂、财星坏印、身旺财弱、枭神夺食

独立运行，不依赖 bazi_engine.py
"""

# ============================================================
# 基础数据
# ============================================================
STEM_NAMES = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCH_NAMES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ELEMENT_NAMES = ["木", "火", "土", "金", "水"]

# 0=比肩, 1=劫财, 2=食神, 3=伤官, 4=偏财, 5=正财, 6=七杀, 7=正官, 8=偏印, 9=正印
SHISHEN_NAMES = ["比", "劫", "食", "伤", "财", "才", "杀", "官", "枭", "印"]
SHISHEN_CATEGORIES = {
    "官杀": [6, 7],
    "财星": [4, 5],
    "食伤": [2, 3],
    "印星": [8, 9],
    "比劫": [0, 1],
}

# 天干五行
STEM_ELEM = {0:0, 1:0, 2:1, 3:1, 4:2, 5:2, 6:3, 7:3, 8:4, 9:4}
# 地支五行
BRANCH_ELEM = {0:4, 1:2, 2:0, 3:0, 4:2, 5:1, 6:1, 7:2, 8:3, 9:3, 10:2, 11:4}

# 得令表
STEM_LING_DEFU = {
    0: [2, 3], 1: [2, 3], 2: [5, 6], 3: [5, 6],
    4: [1, 4, 7, 10], 5: [1, 4, 7, 10],
    6: [8, 9], 7: [8, 9], 8: [0, 11], 9: [0, 11],
}

# 十神表（简化，假设 day_stem=0 即甲日）
SHISHEN_TABLE = [
    [0,1,2,3,4,5,6,7,8,9],
    [1,0,6,7,8,9,2,3,4,5],
    [3,2,0,1,8,9,4,5,6,7],
    [2,3,1,0,9,8,5,4,7,6],
    [5,6,3,4,0,1,2,3,8,9],
    [6,7,4,5,1,0,3,2,9,8],
    [7,8,5,6,3,4,0,1,2,9],
    [8,9,6,7,4,5,1,0,9,2],
    [9,0,7,8,5,6,9,0,0,1],
    [0,1,8,9,6,7,8,9,1,0],
]

# 地支藏干
BRANCH_ZANGCANG = {
    0: [9],       # 子：癸
    1: [4,9,0],   # 丑：戊癸甲
    2: [0,2,4],   # 寅：甲丙戊
    3: [1,3,4],   # 卯：乙丁己
    4: [4,1,9],   # 辰：戊乙癸
    5: [2,6,4],   # 巳：丙庚戊
    6: [3,7,5],   # 午：丁己辛
    7: [5,3,9],   # 未：己丁乙
    8: [6,8,2],   # 申：庚壬戊
    9: [7,3,1],   # 酉：辛丁乙
    10: [4,6,3],  # 戌：戊壬丁
    11: [8,6,0],  # 亥：壬甲戊
}


def calc_shishen(day_stem: int, target_stem: int) -> int:
    return SHISHEN_TABLE[day_stem][target_stem]


def get_bazi(year: int, month: int, day: int, hour: int) -> dict:
    """独立版八字排盘（简化，不做真太阳时矫正）。"""
    # 年干支
    year_stem = (year - 4) % 10
    year_branch = (year - 4) % 12
    
    # 日干支（JDN差值法，基准2000-01-01=戊午）
    import math
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    diff = jdn - 2451545
    day_stem = (4 + diff) % 10
    day_branch = (6 + diff) % 12
    
    # 月干支（五虎遁简化）
    offset = ((year_stem + 1) % 5) * 2
    month_stem = (offset + month - 1) % 10
    month_branch = (month + 1) % 12
    
    # 时干支（五鼠遁）
    hour_index = 0 if hour == 0 or hour == 23 else (hour + 1) // 2
    hour_branch = hour_index % 12
    hour_stem = (day_stem * 2 + hour_index) % 10
    
    return {
        "year": {"stem_idx": year_stem, "branch_idx": year_branch},
        "month": {"stem_idx": month_stem, "branch_idx": month_branch},
        "day": {"stem_idx": day_stem, "branch_idx": day_branch},
        "hour": {"stem_idx": hour_stem, "branch_idx": hour_branch},
        "birth_chart": f"{STEM_NAMES[year_stem]}{BRANCH_NAMES[year_branch]}年 "
                       f"{STEM_NAMES[month_stem]}{BRANCH_NAMES[month_branch]}月 "
                       f"{STEM_NAMES[day_stem]}{BRANCH_NAMES[day_branch]}日 "
                       f"{STEM_NAMES[hour_stem]}{BRANCH_NAMES[hour_branch]}时",
    }


def get_all_stems(bazi: dict) -> list:
    """获取所有天干（含藏干）及其十神。"""
    day_stem = bazi["day"]["stem_idx"]
    result = []
    
    for pillar in ["year", "month", "day", "hour"]:
        stem_idx = bazi[pillar]["stem_idx"]
        branch_idx = bazi[pillar]["branch_idx"]
        shishen_idx = calc_shishen(day_stem, stem_idx)
        result.append({
            "position": pillar, "stem_idx": stem_idx,
            "stem": STEM_NAMES[stem_idx], "branch_idx": branch_idx,
            "branch": BRANCH_NAMES[branch_idx], "shishen": SHISHEN_NAMES[shishen_idx],
            "shishen_idx": shishen_idx, "is_gan": True
        })
        # 地支藏干
        for zg in BRANCH_ZANGCANG.get(branch_idx, []):
            zg_shishen = calc_shishen(day_stem, zg)
            result.append({
                "position": pillar, "stem_idx": zg, "stem": STEM_NAMES[zg],
                "branch_idx": branch_idx, "branch": BRANCH_NAMES[branch_idx],
                "shishen": SHISHEN_NAMES[zg_shishen], "shishen_idx": zg_shishen,
                "is_gan": False
            })
    return result


def categorize_stems(all_stems: list) -> dict:
    cats = {k: [] for k in SHISHEN_CATEGORIES}
    for s in all_stems:
        for cat, idxs in SHISHEN_CATEGORIES.items():
            if s["shishen_idx"] in idxs:
                cats[cat].append(s)
                break
    return cats


def fmt(stems: list) -> list:
    """格式化输出（包含藏干）。"""
    result = []
    for s in stems:
        if s["is_gan"]:
            result.append(f"{s['position']}柱{s['branch']}{s['stem']}({s['shishen']})")
        else:
            result.append(f"{s['position']}支藏{s['stem']}({s['shishen']})")
    return result


def check_guan_sha_za_hun(cats: dict) -> dict:
    """官杀混杂：正官与七杀同现。"""
    guan = [s for s in cats["官杀"] if s["shishen"] == "官"]
    sha = [s for s in cats["官杀"] if s["shishen"] == "杀"]
    if guan and sha:
        return {
            "detected": True, "signal": "官杀混杂", "severity": "高",
            "description": "正官与七杀同透/并见，无制化",
            "evidence": {"正官": fmt(guan), "七杀": fmt(sha)},
            "interpretation": "权威与破坏并存。女命感情混乱（正缘+偏缘），男命上级与小人难辨。"
        }
    return {"detected": False}


def check_cai_huai_yin(cats: dict) -> dict:
    """财星坏印：财星克正印。"""
    yin = [s for s in cats["印星"] if s["shishen"] == "印"]
    if not yin:
        return {"detected": False}
    
    yin_elems = {STEM_ELEM[s["stem_idx"]] for s in yin}
    cai = cats["财星"]
    
    for c in cai:
        c_elem = STEM_ELEM[c["stem_idx"]]
        if c_elem == 2:  # 土克水？不对，应该是财克印
            for y in yin:
                y_elem = STEM_ELEM[y["stem_idx"]]
                # 简化：土（财）克水（印的五行要查）
                # 正印：甲庚的印是壬癸（水）
                if y["stem_idx"] in [8, 9]:  # 壬癸水
                    if c_elem == 2:  # 土克水
                        return {
                            "detected": True, "signal": "财星坏印", "severity": "中高",
                            "description": "财星过旺克制正印",
                            "evidence": {"财星": fmt(cai), "正印": fmt(yin)},
                            "interpretation": "物质与精神冲突。贪财坏印：为利弃义、学历中断、母亲多病。"
                        }
    return {"detected": False}


def check_shen_wang_cai_ruo(bazi: dict, cats: dict) -> dict:
    """身旺财弱：日主得令但财星弱/无。"""
    day_stem = bazi["day"]["stem_idx"]
    month_branch = bazi["month"]["branch_idx"]
    is_deling = month_branch in STEM_LING_DEFU.get(day_stem, [])
    
    cai_gan = [s for s in cats["财星"] if s["is_gan"]]
    
    if is_deling and len(cai_gan) == 0:
        return {
            "detected": True, "signal": "身旺无财", "severity": "中",
            "description": "日主得令，但全局无财星透干",
            "evidence": f"月令{BRANCH_NAMES[month_branch]}，日主{STEM_NAMES[day_stem]}得令有力，四柱无财星",
            "interpretation": "有能力但缺资源平台，求财辛苦或与财缘分浅。"
        }
    elif is_deling and len(cai_gan) <= 1:
        return {
            "detected": True, "signal": "身旺财弱（轻）", "severity": "低",
            "description": "日主得令，但财星较弱",
            "evidence": f"日主得令，财星仅{[s['stem'] for s in cai_gan]}",
            "interpretation": "能力与机遇不完全匹配，宜通过专业技能求财。"
        }
    return {"detected": False}


def check_xiao_duo_shi(cats: dict) -> dict:
    """枭神夺食：偏印克制食神。"""
    shi = [s for s in cats["食伤"] if s["shishen"] == "食" and s["is_gan"]]
    xiao = [s for s in cats["印星"] if s["shishen"] == "枭" and s["is_gan"]]
    
    if xiao and shi:
        return {
            "detected": True, "signal": "枭神夺食", "severity": "中高",
            "description": "偏印与食神同透，枭神夺食",
            "evidence": {"偏印": fmt(xiao), "食神": fmt(shi)},
            "interpretation": "福气被夺。主抑郁、食禄受损、子女缘薄、想法极端。"
        }
    return {"detected": False}


def analyze_bazi(year: int, month: int, day: int, hour: int) -> dict:
    """主函数。"""
    bazi = get_bazi(year, month, day, hour)
    all_stems = get_all_stems(bazi)
    cats = categorize_stems(all_stems)
    
    day_stem = bazi["day"]["stem_idx"]
    month_branch = bazi["month"]["branch_idx"]
    
    conflicts = []
    conflicts.append(check_guan_sha_za_hun(cats))
    conflicts.append(check_cai_huai_yin(cats))
    conflicts.append(check_shen_wang_cai_ruo(bazi, cats))
    conflicts.append(check_xiao_duo_shi(cats))
    
    valid = [c for c in conflicts if c.get("detected")]
    sev_order = {"高": 3, "中高": 2.5, "中": 2, "低": 1}
    highest = max(valid, key=lambda x: sev_order.get(x.get("severity", "低"), 0)).get("severity", "无") if valid else "无"
    
    return {
        "四柱": f"{STEM_NAMES[bazi['year']['stem_idx']]}{BRANCH_NAMES[bazi['year']['branch_idx']]} "
                f"{STEM_NAMES[bazi['month']['stem_idx']]}{BRANCH_NAMES[bazi['month']['branch_idx']]} "
                f"{STEM_NAMES[bazi['day']['stem_idx']]}{BRANCH_NAMES[bazi['day']['branch_idx']]} "
                f"{STEM_NAMES[bazi['hour']['stem_idx']]}{BRANCH_NAMES[bazi['hour']['branch_idx']]}",
        "日主": STEM_NAMES[day_stem],
        "日主五行": ELEMENT_NAMES[STEM_ELEM[day_stem]],
        "月令": BRANCH_NAMES[month_branch],
        "得令": month_branch in STEM_LING_DEFU.get(day_stem, []),
        "天干十神": {
            "年": SHISHEN_NAMES[calc_shishen(day_stem, bazi["year"]["stem_idx"])],
            "月": SHISHEN_NAMES[calc_shishen(day_stem, bazi["month"]["stem_idx"])],
            "日": SHISHEN_NAMES[calc_shishen(day_stem, bazi["day"]["stem_idx"])],
            "时": SHISHEN_NAMES[calc_shishen(day_stem, bazi["hour"]["stem_idx"])],
        },
        "矛盾信号": valid,
        "信号数": len(valid),
        "最高严重度": highest,
    }


def print_report(r: dict):
    print("=" * 52)
    print(f"  八字矛盾检测报告")
    print("=" * 52)
    print(f"  四柱：{r['四柱']}")
    print(f"  日主：{r['日主']}（{r['日主五行']}）{'✓得令' if r['得令'] else '✗失令'} | 月令：{r['月令']}")
    print("-" * 52)
    print(f"  十神：年{r['天干十神']['年']} 月{r['天干十神']['月']} 日{r['天干十神']['日']} 时{r['天干十神']['时']}")
    print("-" * 52)
    print(f"  矛盾信号：{r['信号数']}个  {'最高严重度：'+r['最高严重度'] if r['矛盾信号'] else '✅ 无明显矛盾信号'}")
    for c in r["矛盾信号"]:
        sev = {"高": "🔴", "中高": "🟠", "中": "🟡", "低": "🟢"}.get(c.get("severity", ""), "⚪")
        print(f"\n  {sev} [{c['severity']}] {c['signal']}")
        print(f"     {c['description']}")
        if "evidence" in c:
            ev = c["evidence"]
            if isinstance(ev, str):
                print(f"     {ev}")
            elif isinstance(ev, dict):
                for k, v in ev.items():
                    if isinstance(v, list):
                        print(f"     {k}：{', '.join(v)}")
                    else:
                        print(f"     {k}：{v}")
        if "interpretation" in c:
            print(f"     → {c['interpretation']}")
    print("=" * 52)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 5:
        r = analyze_bazi(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        print_report(r)
    else:
        print("用法: python3 conflict_detector.py <年> <月> <日> <时>")
        print("示例: python3 conflict_detector.py 1990 3 15 14")
