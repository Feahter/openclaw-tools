#!/usr/bin/env python3
"""
AI 内容验证集成模块
使用 Pretext 验证 AI 生成的内容是否适应容器

集成点：
1. 标题验证（不溢出按钮）
2. 描述验证（不溢出卡片）
3. 多语言验证
4. 批量验证
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / 'pretext-integration'))

from text_metrics import validate_text_fit, calculate_metrics


class AIContentValidator:
    """AI 生成内容验证器"""
    
    def __init__(self):
        # 预定义的容器规格
        self.containers = {
            'button_title': {
                'font': '14px Inter',
                'max_width': 150,
                'max_height': 20,
                'line_height': 20,
                'description': '按钮标题'
            },
            'card_title': {
                'font': '16px Inter',
                'max_width': 300,
                'max_height': 40,
                'line_height': 24,
                'description': '卡片标题'
            },
            'card_description': {
                'font': '14px Inter',
                'max_width': 300,
                'max_height': 60,
                'line_height': 20,
                'description': '卡片描述'
            },
            'modal_title': {
                'font': '18px Inter',
                'max_width': 400,
                'max_height': 50,
                'line_height': 28,
                'description': '模态框标题'
            },
            'modal_content': {
                'font': '14px Inter',
                'max_width': 400,
                'max_height': 200,
                'line_height': 20,
                'description': '模态框内容'
            },
            'chinese_title': {
                'font': '16px 宋体',
                'max_width': 300,
                'max_height': 40,
                'line_height': 24,
                'description': '中文标题'
            },
            'chinese_content': {
                'font': '14px 宋体',
                'max_width': 300,
                'max_height': 80,
                'line_height': 20,
                'description': '中文内容'
            }
        }
    
    def validate_content(
        self,
        text: str,
        container: str = 'card_title'
    ) -> Dict:
        """
        验证内容是否适应容器
        
        Args:
            text: 要验证的文本
            container: 容器类型（见 self.containers）
        
        Returns:
            {
                'valid': bool,
                'container': str,
                'text': str,
                'reason': str (如果不适应),
                'metrics': { height, lineCount, ... }
            }
        """
        if container not in self.containers:
            return {
                'valid': False,
                'reason': f'未知容器类型: {container}',
                'available_containers': list(self.containers.keys())
            }
        
        spec = self.containers[container]
        
        # 验证
        valid, reason = validate_text_fit(
            text,
            spec['font'],
            spec['max_width'],
            spec['max_height'],
            spec['line_height']
        )
        
        # 获取指标
        metrics = calculate_metrics(
            text,
            spec['font'],
            spec['max_width'],
            spec['line_height']
        )
        
        return {
            'valid': valid,
            'container': container,
            'container_description': spec['description'],
            'text': text,
            'reason': reason if not valid else None,
            'metrics': {
                'height': metrics['height'],
                'lineCount': metrics['lineCount'],
                'density': metrics['density'],
                'compactness': metrics['compactness']
            },
            'constraints': {
                'max_width': spec['max_width'],
                'max_height': spec['max_height'],
                'font': spec['font']
            }
        }
    
    def validate_batch(
        self,
        items: List[Dict],
        container: str = 'card_title'
    ) -> Dict:
        """
        批量验证内容
        
        Args:
            items: [
                { 'text': '...', 'id': '...' },
                ...
            ]
            container: 容器类型
        
        Returns:
            {
                'total': int,
                'valid': int,
                'invalid': int,
                'results': [...]
            }
        """
        results = []
        valid_count = 0
        
        for item in items:
            result = self.validate_content(item['text'], container)
            result['id'] = item.get('id', len(results))
            results.append(result)
            
            if result['valid']:
                valid_count += 1
        
        return {
            'total': len(items),
            'valid': valid_count,
            'invalid': len(items) - valid_count,
            'valid_rate': f"{valid_count / len(items) * 100:.1f}%",
            'results': results
        }
    
    def suggest_fix(self, validation_result: Dict) -> str:
        """
        建议修复方案
        
        Args:
            validation_result: validate_content() 的返回值
        
        Returns:
            修复建议
        """
        if validation_result['valid']:
            return "✅ 内容适应容器，无需修改"
        
        metrics = validation_result['metrics']
        constraints = validation_result['constraints']
        text = validation_result['text']
        
        suggestions = []
        
        # 高度溢出
        if metrics['height'] > constraints['max_height']:
            overflow = metrics['height'] - constraints['max_height']
            suggestions.append(f"❌ 高度溢出 {overflow:.0f}px")
            
            # 建议
            if metrics['lineCount'] > 1:
                suggestions.append(f"   💡 缩短文本或增加容器高度")
                suggestions.append(f"   💡 当前 {metrics['lineCount']} 行，建议 {int(metrics['lineCount'] * 0.7)} 行以内")
            else:
                suggestions.append(f"   💡 文本过长，建议缩短到 {int(len(text) * 0.7)} 字符以内")
        
        return '\n'.join(suggestions)
    
    def add_custom_container(
        self,
        name: str,
        font: str,
        max_width: int,
        max_height: int,
        line_height: float = 20,
        description: str = ''
    ):
        """添加自定义容器规格"""
        self.containers[name] = {
            'font': font,
            'max_width': max_width,
            'max_height': max_height,
            'line_height': line_height,
            'description': description or name
        }


# 全局实例
_validator_instance: Optional[AIContentValidator] = None


def get_validator() -> AIContentValidator:
    """获取全局验证器实例"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = AIContentValidator()
    return _validator_instance


# 便捷函数
def validate_content(text: str, container: str = 'card_title') -> Dict:
    """验证内容"""
    return get_validator().validate_content(text, container)


def validate_batch(items: List[Dict], container: str = 'card_title') -> Dict:
    """批量验证"""
    return get_validator().validate_batch(items, container)


def suggest_fix(validation_result: Dict) -> str:
    """获取修复建议"""
    return get_validator().suggest_fix(validation_result)


# 示例用法
if __name__ == '__main__':
    validator = get_validator()
    
    print("=" * 60)
    print("AI 内容验证示例")
    print("=" * 60)
    
    # 示例 1: 单个验证
    print("\n示例 1: 单个内容验证")
    print("-" * 60)
    
    result = validator.validate_content('这是一个很长的标题文本', 'button_title')
    print(f"验证结果: {'✅ 通过' if result['valid'] else '❌ 失败'}")
    print(f"容器: {result['container_description']}")
    print(f"文本: {result['text']}")
    if not result['valid']:
        print(f"原因: {result['reason']}")
    print(f"指标: 高度 {result['metrics']['height']}px, {result['metrics']['lineCount']} 行")
    print(f"修复建议:\n{validator.suggest_fix(result)}")
    
    # 示例 2: 批量验证
    print("\n\n示例 2: 批量内容验证")
    print("-" * 60)
    
    items = [
        {'text': '短标题', 'id': 1},
        {'text': '这是一个很长很长的标题文本', 'id': 2},
        {'text': '中等长度标题', 'id': 3},
    ]
    
    batch_result = validator.validate_batch(items, 'card_title')
    print(f"总数: {batch_result['total']}")
    print(f"通过: {batch_result['valid']}")
    print(f"失败: {batch_result['invalid']}")
    print(f"通过率: {batch_result['valid_rate']}")
    
    print("\n详细结果:")
    for result in batch_result['results']:
        status = '✅' if result['valid'] else '❌'
        print(f"  {status} [{result['id']}] {result['text'][:20]}...")
    
    # 示例 3: 多语言验证
    print("\n\n示例 3: 多语言内容验证")
    print("-" * 60)
    
    multilingual_items = [
        {'text': '这是中文标题', 'id': 'cn1'},
        {'text': '这是一个很长很长的中文标题文本', 'id': 'cn2'},
        {'text': 'English Title', 'id': 'en1'},
        {'text': 'This is a very long English title text', 'id': 'en2'},
        {'text': 'AGI 春天到了 🌸', 'id': 'mixed1'},
    ]
    
    for item in multilingual_items:
        # 根据语言选择容器
        container = 'chinese_title' if any('\u4e00' <= c <= '\u9fff' for c in item['text']) else 'card_title'
        result = validator.validate_content(item['text'], container)
        status = '✅' if result['valid'] else '❌'
        print(f"{status} [{item['id']}] {item['text']}")
    
    # 示例 4: 自定义容器
    print("\n\n示例 4: 自定义容器验证")
    print("-" * 60)
    
    validator.add_custom_container(
        'custom_banner',
        font='20px Inter',
        max_width=500,
        max_height=60,
        line_height=30,
        description='自定义横幅'
    )
    
    result = validator.validate_content('这是一个自定义横幅标题', 'custom_banner')
    print(f"验证结果: {'✅ 通过' if result['valid'] else '❌ 失败'}")
    print(f"容器: {result['container_description']}")
    print(f"指标: 高度 {result['metrics']['height']}px")
