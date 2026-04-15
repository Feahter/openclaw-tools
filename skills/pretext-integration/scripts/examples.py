#!/usr/bin/env python3
"""
Pretext 集成使用示例和测试
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from text_metrics import (
    get_metrics,
    calculate_height,
    calculate_line_count,
    calculate_metrics,
    validate_text_fit
)
from bazi_report_layout import BaziReportLayout


def example_1_basic_measurement():
    """示例 1: 基础文本测量"""
    print("=" * 60)
    print("示例 1: 基础文本测量")
    print("=" * 60)
    
    texts = [
        ('丙午辛卯丙申庚寅', '18px 宋体'),
        ('喜用水木，忌火金土', '14px 宋体'),
        ('AGI 春天到了. بدأت الرحلة 🚀', '16px Inter'),
    ]
    
    for text, font in texts:
        height = calculate_height(text, font, 300, 20)
        line_count = calculate_line_count(text, font, 300, 20)
        print(f"\n文本: {text}")
        print(f"字体: {font}")
        print(f"高度: {height}px")
        print(f"行数: {line_count}")


def example_2_metrics_calculation():
    """示例 2: 完整指标计算"""
    print("\n" + "=" * 60)
    print("示例 2: 完整指标计算")
    print("=" * 60)
    
    text = '此命格局平凡，需要通过后天努力来改善运势。建议加强水木元素的补充。'
    metrics = calculate_metrics(text, '14px 宋体', 300, 20)
    
    print(f"\n文本: {text}")
    print(f"高度: {metrics['height']}px")
    print(f"行数: {metrics['lineCount']}")
    print(f"密度: {metrics['density']:.3f} (高度/字符)")
    print(f"紧凑度: {metrics['compactness']:.3f} (字符/高度)")


def example_3_text_validation():
    """示例 3: 文本验证"""
    print("\n" + "=" * 60)
    print("示例 3: 文本验证")
    print("=" * 60)
    
    test_cases = [
        ('这是一个标题', '14px Inter', 200, 20, '按钮标题'),
        ('这是一个很长很长的标题文本，可能会溢出', '14px Inter', 200, 20, '长标题'),
        ('简短', '14px Inter', 200, 20, '短文本'),
    ]
    
    for text, font, max_width, max_height, desc in test_cases:
        valid, reason = validate_text_fit(text, font, max_width, max_height, 20)
        status = '✅ 通过' if valid else f'❌ 失败'
        print(f"\n{desc}: {status}")
        print(f"  文本: {text}")
        if not valid:
            print(f"  原因: {reason}")


def example_4_bazi_report_layout():
    """示例 4: 八字命理报告布局"""
    print("\n" + "=" * 60)
    print("示例 4: 八字命理报告布局")
    print("=" * 60)
    
    layout = BaziReportLayout()
    
    report_sections = [
        {
            'title': '基本信息',
            'content': '出生时间：1990年3月15日 14:30\n农历：庚午年 二月 初九 未时\n生肖：马\n纳音五行：路旁土'
        },
        {
            'title': '八字分析',
            'content': '日主：丙火\n格局：正官格\n身强弱：身弱\n喜用神：水、木\n忌神：火、土、金'
        },
        {
            'title': '运势分析',
            'content': '大运：从 10 岁开始进入丁未大运\n流年：2024 年为甲辰年，与八字相冲\n建议：加强水木元素的补充，避免火土过旺'
        }
    ]
    
    # 计算布局
    layout_result = layout.calculate_report_layout(report_sections)
    
    print(f"\n报告统计:")
    print(f"  总高度: {layout_result['total_height']}px")
    print(f"  页数: {layout_result['page_count']}")
    print(f"  分页位置: {layout_result['page_breaks']}")
    
    print(f"\n章节详情:")
    for section in layout_result['sections']:
        print(f"\n  {section['title']} (第 {section['page']} 页)")
        print(f"    标题: {section['title_height']}px ({section['line_count']['title']} 行)")
        print(f"    内容: {section['content_height']}px ({section['line_count']['content']} 行)")
        print(f"    总计: {section['total_height']}px")
    
    # 验证
    valid, issues = layout.validate_report_fit(report_sections)
    print(f"\n验证结果: {'✅ 通过' if valid else '❌ 失败'}")
    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")


def example_5_cache_performance():
    """示例 5: 缓存性能"""
    print("\n" + "=" * 60)
    print("示例 5: 缓存性能")
    print("=" * 60)
    
    metrics = get_metrics()
    text = '这是一个测试文本'
    font = '14px 宋体'
    
    # 第一次调用（无缓存）
    import time
    start = time.time()
    height1 = metrics.calculate_height(text, font, 300, 20)
    time1 = time.time() - start
    
    # 第二次调用（有缓存）
    start = time.time()
    height2 = metrics.calculate_height(text, font, 300, 20)
    time2 = time.time() - start
    
    print(f"\n文本: {text}")
    print(f"第一次调用: {height1}px ({time1*1000:.2f}ms)")
    print(f"第二次调用: {height2}px ({time2*1000:.2f}ms)")
    print(f"性能提升: {time1/time2:.1f}x")
    
    # 缓存统计
    stats = metrics.get_cache_stats()
    print(f"\n缓存统计:")
    print(f"  大小: {stats['size']}/{stats['max_size']}")
    print(f"  使用率: {stats['usage']}")


def example_6_multilingual():
    """示例 6: 多语言支持"""
    print("\n" + "=" * 60)
    print("示例 6: 多语言支持")
    print("=" * 60)
    
    texts = [
        ('中文文本测试', '14px 宋体', '中文'),
        ('日本語のテキスト', '14px 'Hiragino Sans'', '日文'),
        ('한국어 텍스트', '14px 'Noto Sans CJK'', '韩文'),
        ('النص العربي', '14px 'Arabic Typesetting'', '阿拉伯文'),
        ('Hello World 🌍', '14px Inter', '英文 + Emoji'),
    ]
    
    for text, font, lang in texts:
        try:
            height = calculate_height(text, font, 300, 20)
            line_count = calculate_line_count(text, font, 300, 20)
            print(f"\n{lang}: {text}")
            print(f"  高度: {height}px, 行数: {line_count}")
        except Exception as e:
            print(f"\n{lang}: {text}")
            print(f"  ⚠️  错误: {e}")


def main():
    """运行所有示例"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Pretext 集成使用示例".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        example_1_basic_measurement()
        example_2_metrics_calculation()
        example_3_text_validation()
        example_4_bazi_report_layout()
        example_5_cache_performance()
        example_6_multilingual()
        
        print("\n" + "=" * 60)
        print("✅ 所有示例执行完成")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
