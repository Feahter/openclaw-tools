#!/usr/bin/env python3
"""
八字命理报告 + Pretext 集成
用于精确计算报告各部分的文本高度，避免 PDF 生成时的溢出问题

集成点：
1. 报告标题高度计算
2. 各部分内容高度计算
3. 总体报告高度规划
4. PDF 分页优化
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 导入本地模块
sys.path.insert(0, str(Path(__file__).parent.parent / 'chinese-name-lookup' / 'scripts'))
sys.path.insert(0, str(Path(__file__).parent))

from text_metrics import get_metrics, calculate_metrics, validate_text_fit


class BaziReportLayout:
    """八字命理报告布局优化"""
    
    def __init__(self):
        self.metrics = get_metrics()
        
        # 默认字体配置
        self.fonts = {
            'title': '20px 宋体',      # 报告标题
            'section': '16px 宋体',    # 章节标题
            'content': '14px 宋体',    # 正文内容
            'label': '12px 宋体',      # 标签
        }
        
        # 默认尺寸配置
        self.sizes = {
            'page_width': 800,         # 页面宽度
            'content_width': 700,      # 内容宽度
            'line_height': 24,         # 行高
            'margin_top': 40,
            'margin_bottom': 40,
            'section_gap': 20,
        }
    
    def calculate_title_height(self, title: str) -> float:
        """计算标题高度"""
        return self.metrics.calculate_height(
            title,
            self.fonts['title'],
            self.sizes['content_width'],
            self.sizes['line_height']
        )
    
    def calculate_section_height(self, section_title: str, content: str) -> Dict:
        """计算章节高度（标题 + 内容）"""
        title_height = self.metrics.calculate_height(
            section_title,
            self.fonts['section'],
            self.sizes['content_width'],
            self.sizes['line_height']
        )
        
        content_height = self.metrics.calculate_height(
            content,
            self.fonts['content'],
            self.sizes['content_width'],
            self.sizes['line_height']
        )
        
        return {
            'title_height': title_height,
            'content_height': content_height,
            'total_height': title_height + content_height + self.sizes['section_gap'],
            'line_count': {
                'title': self.metrics.calculate_line_count(
                    section_title,
                    self.fonts['section'],
                    self.sizes['content_width'],
                    self.sizes['line_height']
                ),
                'content': self.metrics.calculate_line_count(
                    content,
                    self.fonts['content'],
                    self.sizes['content_width'],
                    self.sizes['line_height']
                )
            }
        }
    
    def calculate_report_layout(self, report_sections: List[Dict]) -> Dict:
        """
        计算完整报告的布局
        
        Args:
            report_sections: [
                {
                    'title': '基本信息',
                    'content': '...'
                },
                ...
            ]
        
        Returns:
            {
                'sections': [...],
                'total_height': float,
                'page_count': int,
                'page_breaks': [...]
            }
        """
        sections = []
        total_height = self.sizes['margin_top']
        page_height = 1000  # A4 页面高度（像素）
        page_breaks = [0]
        current_page_height = self.sizes['margin_top']
        
        for section in report_sections:
            section_layout = self.calculate_section_height(
                section['title'],
                section['content']
            )
            
            section_height = section_layout['total_height']
            
            # 检查是否需要分页
            if current_page_height + section_height > page_height - self.sizes['margin_bottom']:
                page_breaks.append(total_height)
                current_page_height = self.sizes['margin_top'] + section_height
            else:
                current_page_height += section_height
            
            total_height += section_height
            sections.append({
                **section,
                **section_layout,
                'page': len(page_breaks)
            })
        
        total_height += self.sizes['margin_bottom']
        page_count = len(page_breaks)
        
        return {
            'sections': sections,
            'total_height': total_height,
            'page_count': page_count,
            'page_breaks': page_breaks,
            'pages': [
                {
                    'page_num': i + 1,
                    'start_height': page_breaks[i],
                    'end_height': page_breaks[i + 1] if i + 1 < len(page_breaks) else total_height
                }
                for i in range(page_count)
            ]
        }
    
    def validate_report_fit(self, report_sections: List[Dict]) -> Tuple[bool, List[str]]:
        """
        验证报告内容是否适应页面
        
        Returns:
            (是否适应, 问题列表)
        """
        issues = []
        
        for section in report_sections:
            # 验证标题
            valid, reason = validate_text_fit(
                section['title'],
                self.fonts['section'],
                self.sizes['content_width'],
                self.sizes['line_height'] * 2,
                self.sizes['line_height']
            )
            if not valid:
                issues.append(f"标题溢出: {section['title'][:20]}... - {reason}")
            
            # 验证内容
            valid, reason = validate_text_fit(
                section['content'],
                self.fonts['content'],
                self.sizes['content_width'],
                self.sizes['line_height'] * 20,  # 允许多行
                self.sizes['line_height']
            )
            if not valid:
                issues.append(f"内容溢出: {section['title']} - {reason}")
        
        return len(issues) == 0, issues
    
    def optimize_report_sections(self, report_sections: List[Dict]) -> List[Dict]:
        """
        优化报告章节（如果内容过长，自动分割）
        
        Args:
            report_sections: 原始章节列表
        
        Returns:
            优化后的章节列表
        """
        optimized = []
        max_content_height = self.sizes['line_height'] * 15  # 最多 15 行
        
        for section in report_sections:
            content_height = self.metrics.calculate_height(
                section['content'],
                self.fonts['content'],
                self.sizes['content_width'],
                self.sizes['line_height']
            )
            
            if content_height > max_content_height:
                # 内容过长，需要分割
                # 这里简化处理，实际应该按句子或段落分割
                lines = section['content'].split('\n')
                current_content = []
                
                for line in lines:
                    current_content.append(line)
                    current_height = self.metrics.calculate_height(
                        '\n'.join(current_content),
                        self.fonts['content'],
                        self.sizes['content_width'],
                        self.sizes['line_height']
                    )
                    
                    if current_height > max_content_height:
                        # 保存当前部分
                        optimized.append({
                            'title': section['title'],
                            'content': '\n'.join(current_content[:-1])
                        })
                        current_content = [line]
                
                # 保存剩余部分
                if current_content:
                    optimized.append({
                        'title': section['title'],
                        'content': '\n'.join(current_content)
                    })
            else:
                optimized.append(section)
        
        return optimized


# 示例用法
if __name__ == '__main__':
    layout = BaziReportLayout()
    
    # 示例报告章节
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
    
    print("=== 八字命理报告布局优化 ===\n")
    
    # 计算报告布局
    layout_result = layout.calculate_report_layout(report_sections)
    print(f"总高度: {layout_result['total_height']}px")
    print(f"页数: {layout_result['page_count']}")
    print(f"分页位置: {layout_result['page_breaks']}\n")
    
    # 验证报告
    valid, issues = layout.validate_report_fit(report_sections)
    print(f"验证结果: {'✅ 通过' if valid else '❌ 失败'}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    print()
    
    # 显示详细布局
    print("=== 详细布局 ===")
    for section in layout_result['sections']:
        print(f"\n{section['title']} (第 {section['page']} 页)")
        print(f"  标题高度: {section['title_height']}px ({section['line_count']['title']} 行)")
        print(f"  内容高度: {section['content_height']}px ({section['line_count']['content']} 行)")
        print(f"  总高度: {section['total_height']}px")
