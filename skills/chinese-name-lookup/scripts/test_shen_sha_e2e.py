#!/usr/bin/env python3
"""
神煞系统端到端测试
Phase 7 - 神煞查询系统
"""

import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")

from bazi_engine import full_bazi_analysis, get_bazi
from shen_sha import (
    get_tianyi_guiren, get_wenchang, get_yima,
    get_huagai, get_taohua, get_shen_sha_summary,
    get_tiande, get_yuede, get_hongluan_tianxi,
    get_jiangxing, get_wangshen, get_jiesha, get_zaisha,
    get_sangmen, get_diaoke, get_liujia_guishen, get_sanqi
)


def test_tianyi_guiren():
    """测试1：天乙贵人口诀验证"""
    print("【端到端测试1】天乙贵人")
    
    # 甲辰年: 甲戊兼牛羊 → 贵人: 丑(1)、未(8)
    bazi1 = get_bazi(2024, 3, 15, 10)
    result1 = get_tianyi_guiren(bazi1["bazi"]["year"]["stem_idx"], bazi1["bazi"]["year"]["branch_idx"])
    assert "丑" in result1["guiren_branches"], f"甲年贵人应有丑, got {result1['guiren_branches']}"
    assert "未" in result1["guiren_branches"], f"甲年贵人应有未, got {result1['guiren_branches']}"
    print(f"  甲辰年: 贵人{result1['guiren_branches']} ✓")
    
    # 庚午年: 庚辛逢虎马 → 贵人: 寅(2)、午(6)
    bazi2 = get_bazi(1990, 5, 15, 10)  # 庚午年
    result2 = get_tianyi_guiren(bazi2["bazi"]["year"]["stem_idx"], bazi2["bazi"]["year"]["branch_idx"])
    assert "寅" in result2["guiren_branches"], f"庚年贵人应有寅, got {result2['guiren_branches']}"
    assert "午" in result2["guiren_branches"], f"庚年贵人应有午, got {result2['guiren_branches']}"
    print(f"  庚午年: 贵人{result2['guiren_branches']} ✓")
    
    # 癸卯年: 壬癸兔蛇藏 → 贵人: 卯(3)、巳(5)
    bazi3 = get_bazi(2023, 4, 10, 10)  # 癸卯年
    result3 = get_tianyi_guiren(bazi3["bazi"]["year"]["stem_idx"], bazi3["bazi"]["year"]["branch_idx"])
    assert "卯" in result3["guiren_branches"], f"癸年贵人应有卯, got {result3['guiren_branches']}"
    assert "巳" in result3["guiren_branches"], f"癸年贵人应有巳, got {result3['guiren_branches']}"
    print(f"  癸卯年: 贵人{result3['guiren_branches']} ✓")
    print("  ✓ 天乙贵人口诀全部验证通过\n")


def test_yima_taohua_huagai():
    """测试2：驿马、桃花、华盖口诀验证"""
    print("【端到端测试2】驿马/桃花/华盖")
    
    # 驿马
    # 申子辰马在寅 → 辰(4)年马在寅(2)
    yima1 = get_yima(4)  # 辰年
    assert yima1["yima_branch_idx"] == 2, f"辰年马应在寅, got {yima1['yima_branch']}"
    print(f"  辰年驿马: {yima1['yima_branch']} ✓")
    
    # 寅午戌马在申 → 寅(2)年马在申(8)
    yima2 = get_yima(2)  # 寅年
    assert yima2["yima_branch_idx"] == 8, f"寅年马应在申, got {yima2['yima_branch']}"
    print(f"  寅年驿马: {yima2['yima_branch']} ✓")
    
    # 亥卯未马在巳 → 亥(11)年马在巳(6)
    yima3 = get_yima(11)  # 亥年
    assert yima3["yima_branch_idx"] == 6, f"亥年马应在巳, got {yima3['yima_branch']}"
    print(f"  亥年驿马: {yima3['yima_branch']} ✓")
    
    # 桃花
    # 申子辰见酉 → 辰(4)年桃花在酉(9)
    taohua1 = get_taohua(4)
    assert taohua1["taohua_branch_idx"] == 9, f"辰年桃花应在酉, got {taohua1['taohua_branch']}"
    print(f"  辰年桃花: {taohua1['taohua_branch']} ✓")
    
    # 寅午戌见卯 → 寅(2)年桃花在卯(3)
    taohua2 = get_taohua(2)
    assert taohua2["taohua_branch_idx"] == 3, f"寅年桃花应在卯, got {taohua2['taohua_branch']}"
    print(f"  寅年桃花: {taohua2['taohua_branch']} ✓")
    
    # 亥卯未见子 → 亥(11)年桃花在子(0)
    taohua3 = get_taohua(11)
    assert taohua3["taohua_branch_idx"] == 0, f"亥年桃花应在子, got {taohua3['taohua_branch']}"
    print(f"  亥年桃花: {taohua3['taohua_branch']} ✓")
    
    # 华盖：辰戌丑未为华盖
    huagai_chen = get_huagai(4)  # 辰年
    assert huagai_chen["has_huagai"] == True, "辰年应有华盖"
    print(f"  辰年华盖: {huagai_chen['huagai_branch']} ✓")
    
    huagai_yin = get_huagai(2)  # 寅年
    assert huagai_yin["has_huagai"] == False, "寅年无华盖"
    print(f"  寅年华盖: 无 ✓")
    
    huagai_chou = get_huagai(1)  # 丑年
    assert huagai_chou["has_huagai"] == True, "丑年应有华盖"
    print(f"  丑年华盖: {huagai_chou['huagai_branch']} ✓")
    
    print("  ✓ 驿马/桃花/华盖全部验证通过\n")


def test_full_shen_sha_integration():
    """测试3：综合神煞与八字引擎集成"""
    print("【端到端测试3】综合神煞与八字引擎集成")
    
    # 2024年3月15日10点（甲辰年）
    result = full_bazi_analysis(2024, 3, 15, 10)
    assert "shen_sha" in result, "结果应包含shen_sha字段"
    
    shen = result["shen_sha"]
    assert "P0" in shen, "应有P0神煞"
    assert "P1" in shen, "应有P1神煞"
    assert "P2" in shen, "应有P2神煞"
    assert "summary" in shen, "应有summary字段"
    
    # 验证P0神煞
    p0 = shen["P0"]
    assert "天乙贵人" in p0, "应有天乙贵人"
    assert "文昌" in p0, "应有文昌"
    assert "驿马" in p0, "应有驿马"
    assert "华盖" in p0, "应有华盖"
    assert "桃花" in p0, "应有桃花"
    
    # 甲辰年验证
    assert "丑" in p0["天乙贵人"]["guiren_branches"], f"甲年贵人应有丑, got {p0['天乙贵人']['guiren_branches']}"
    print(f"  甲辰年天乙贵人: {p0['天乙贵人']['guiren_branches']} ✓")
    
    assert p0["华盖"]["has_huagai"] == True, "辰年应有华盖"
    assert p0["华盖"]["huagai_branch"] == "辰", f"辰年华盖应在辰, got {p0['华盖']['huagai_branch']}"
    print(f"  甲辰年华盖: {p0['华盖']['huagai_branch']} ✓")
    
    assert p0["桃花"]["taohua_branch"] == "酉", f"辰年桃花应在酉, got {p0['桃花']['taohua_branch']}"
    print(f"  甲辰年桃花: {p0['桃花']['taohua_branch']} ✓")
    
    assert p0["驿马"]["yima_branch"] == "寅", f"辰年驿马应在寅, got {p0['驿马']['yima_branch']}"
    print(f"  甲辰年驿马: {p0['驿马']['yima_branch']} ✓")
    
    # 验证P1神煞
    p1 = shen["P1"]
    assert "天德" in p1, "应有天德"
    assert "月德" in p1, "应有月德"
    assert "红鸾天喜" in p1, "应有红鸾天喜"
    assert "将星" in p1, "应有将星"
    assert "亡神" in p1, "应有亡神"
    print(f"  甲辰年天德: {p1['天德']['tiande_branch']} ✓")
    print(f"  甲辰年月德: {p1['月德'].get('yuede_branch', '无')} ✓")
    
    # 验证P2神煞
    p2 = shen["P2"]
    assert "劫煞" in p2, "应有劫煞"
    assert "灾煞" in p2, "应有灾煞"
    print(f"  甲辰年劫煞: {p2['劫煞']['jiesha_branch']} ✓")
    print(f"  甲辰年灾煞: {p2['灾煞']['zaisha_branch']} ✓")
    
    # 验证summary
    summary = shen["summary"]
    assert "tianyi_guiren" in summary, "summary应有tianyi_guiren"
    assert "yima" in summary, "summary应有yima"
    assert "taohua" in summary, "summary应有taohua"
    print(f"  神煞summary包含所有关键字段 ✓")
    
    # 另一个日期验证
    result2 = full_bazi_analysis(1990, 5, 15, 10)  # 庚午年
    shen2 = result2["shen_sha"]
    p0_2 = shen2["P0"]
    
    # 庚午年：庚辛逢虎马 → 贵人寅、午
    assert "寅" in p0_2["天乙贵人"]["guiren_branches"], f"庚年贵人应有寅"
    assert "午" in p0_2["天乙贵人"]["guiren_branches"], f"庚年贵人应有午"
    print(f"  庚午年天乙贵人: {p0_2['天乙贵人']['guiren_branches']} ✓")
    
    # 庚午年：寅午戌 → 马在申
    assert p0_2["驿马"]["yima_branch"] == "申", f"寅午戌年驿马应在申"
    print(f"  庚午年驿马: {p0_2['驿马']['yima_branch']} ✓")
    
    # 庚午年：寅午戌 → 桃花在卯
    assert p0_2["桃花"]["taohua_branch"] == "卯", f"寅午戌年桃花应在卯"
    print(f"  庚午年桃花: {p0_2['桃花']['taohua_branch']} ✓")
    
    # 庚午年无华盖
    assert p0_2["华盖"]["has_huagai"] == False, "午年无华盖"
    print(f"  庚午年华盖: 无 ✓")
    
    print("  ✓ 综合神煞集成测试全部通过\n")


if __name__ == "__main__":
    print("=" * 60)
    print("神煞系统端到端测试 - Phase 7")
    print("=" * 60 + "\n")
    
    test_tianyi_guiren()
    test_yima_taohua_huagai()
    test_full_shen_sha_integration()
    
    print("=" * 60)
    print("所有端到端测试通过！✓")
    print("=" * 60)
