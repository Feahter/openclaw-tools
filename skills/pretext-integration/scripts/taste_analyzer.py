#!/usr/bin/env python3
"""
品味研究数据化模块
使用 Pretext 量化文本特征，支持品味判断的数据分析

集成点：
1. 文本特征量化
2. 品味判断记录
3. 数据分析与可视化
4. 品味演变追踪
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'pretext-integration'))

from text_metrics import calculate_metrics


class TasteAnalyzer:
    """品味分析器 - 量化文本特征"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / '.openclaw' / 'workspace' / 'memory' / 'research' / 'taste-judgement'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.judgements = []
    
    def analyze_text(self, text: str, font: str = '16px Inter', max_width: int = 300) -> Dict:
        """
        分析文本特征
        
        Returns:
            {
                'text': str,
                'length': int,
                'height': float,
                'lineCount': int,
                'density': float,
                'compactness': float,
                'complexity': float,  # 基于长度和行数
                'readability': float,  # 基于行高和密度
                'features': {
                    'has_punctuation': bool,
                    'has_emoji': bool,
                    'has_chinese': bool,
                    'has_english': bool,
                    'avg_word_length': float
                }
            }
        """
        metrics = calculate_metrics(text, font, max_width, 20)
        
        # 提取特征
        has_punctuation = any(c in '，。！？；：' for c in text)
        has_emoji = any('\U0001F300' <= c <= '\U0001F9FF' for c in text)
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
        has_english = any(c.isalpha() and ord(c) < 128 for c in text)
        
        # 计算复杂度
        complexity = (
            metrics['lineCount'] * 0.3 +  # 行数
            (len(text) / 100) * 0.3 +      # 长度
            (1 if has_punctuation else 0) * 0.2 +  # 标点
            (1 if has_emoji else 0) * 0.2  # emoji
        )
        
        # 计算可读性
        readability = 1.0 / (metrics['density'] + 0.1)
        
        return {
            'text': text,
            'length': len(text),
            'height': metrics['height'],
            'lineCount': metrics['lineCount'],
            'density': metrics['density'],
            'compactness': metrics['compactness'],
            'complexity': min(complexity, 1.0),
            'readability': min(readability, 1.0),
            'features': {
                'has_punctuation': has_punctuation,
                'has_emoji': has_emoji,
                'has_chinese': has_chinese,
                'has_english': has_english,
                'avg_word_length': len(text) / max(metrics['lineCount'], 1)
            }
        }
    
    def record_judgement(
        self,
        text: str,
        judgement: str,
        rating: float = 0.5,  # 0-1 之间
        category: str = 'general',
        tags: List[str] = None,
        notes: str = ''
    ) -> Dict:
        """
        记录品味判断
        
        Args:
            text: 被评判的文本
            judgement: 判断内容（如"这个设计很优雅"）
            rating: 评分（0-1）
            category: 分类（general, design, writing, etc）
            tags: 标签列表
            notes: 备注
        
        Returns:
            记录的判断数据
        """
        analysis = self.analyze_text(text)
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'text': text,
            'judgement': judgement,
            'rating': rating,
            'category': category,
            'tags': tags or [],
            'notes': notes,
            'analysis': analysis
        }
        
        self.judgements.append(record)
        return record
    
    def get_statistics(self) -> Dict:
        """获取统计数据"""
        if not self.judgements:
            return {'total': 0}
        
        ratings = [j['rating'] for j in self.judgements]
        complexities = [j['analysis']['complexity'] for j in self.judgements]
        readabilities = [j['analysis']['readability'] for j in self.judgements]
        
        return {
            'total': len(self.judgements),
            'avg_rating': sum(ratings) / len(ratings),
            'avg_complexity': sum(complexities) / len(complexities),
            'avg_readability': sum(readabilities) / len(readabilities),
            'categories': self._count_by_field('category'),
            'tags': self._count_tags(),
            'date_range': {
                'first': self.judgements[0]['timestamp'],
                'last': self.judgements[-1]['timestamp']
            }
        }
    
    def _count_by_field(self, field: str) -> Dict:
        """统计字段值"""
        counts = {}
        for j in self.judgements:
            value = j.get(field, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def _count_tags(self) -> Dict:
        """统计标签"""
        counts = {}
        for j in self.judgements:
            for tag in j.get('tags', []):
                counts[tag] = counts.get(tag, 0) + 1
        return counts
    
    def find_similar_judgements(
        self,
        text: str,
        similarity_threshold: float = 0.8
    ) -> List[Dict]:
        """
        找到相似的判断
        
        Args:
            text: 参考文本
            similarity_threshold: 相似度阈值
        
        Returns:
            相似的判断列表
        """
        ref_analysis = self.analyze_text(text)
        similar = []
        
        for j in self.judgements:
            # 计算相似度（基于文本特征）
            similarity = self._calculate_similarity(ref_analysis, j['analysis'])
            
            if similarity >= similarity_threshold:
                similar.append({
                    'judgement': j,
                    'similarity': similarity
                })
        
        return sorted(similar, key=lambda x: x['similarity'], reverse=True)
    
    def _calculate_similarity(self, analysis1: Dict, analysis2: Dict) -> float:
        """计算两个文本分析的相似度"""
        # 基于特征的相似度计算
        features1 = analysis1['features']
        features2 = analysis2['features']
        
        # 计算特征匹配度
        matches = sum(1 for k in features1 if features1[k] == features2[k])
        total_features = len(features1)
        
        # 计算数值特征的相似度
        complexity_diff = abs(analysis1['complexity'] - analysis2['complexity'])
        readability_diff = abs(analysis1['readability'] - analysis2['readability'])
        
        feature_similarity = matches / total_features
        numeric_similarity = 1.0 - (complexity_diff + readability_diff) / 2
        
        return (feature_similarity + numeric_similarity) / 2
    
    def export_data(self, filename: str = 'taste_judgements.json'):
        """导出数据"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.judgements, f, ensure_ascii=False, indent=2)
        return filepath
    
    def import_data(self, filename: str = 'taste_judgements.json'):
        """导入数据"""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                self.judgements = json.load(f)
        return len(self.judgements)


# 全局实例
_analyzer_instance: Optional[TasteAnalyzer] = None


def get_analyzer() -> TasteAnalyzer:
    """获取全局分析器实例"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = TasteAnalyzer()
    return _analyzer_instance


# 示例用法
if __name__ == '__main__':
    analyzer = get_analyzer()
    
    print("=" * 60)
    print("品味研究数据化示例")
    print("=" * 60)
    
    # 示例 1: 文本分析
    print("\n示例 1: 文本特征分析")
    print("-" * 60)
    
    text = "这个设计很优雅，简洁而不失力量感。"
    analysis = analyzer.analyze_text(text)
    
    print(f"文本: {text}")
    print(f"长度: {analysis['length']} 字符")
    print(f"高度: {analysis['height']:.1f}px")
    print(f"行数: {analysis['lineCount']}")
    print(f"复杂度: {analysis['complexity']:.2f}")
    print(f"可读性: {analysis['readability']:.2f}")
    print(f"特征: {analysis['features']}")
    
    # 示例 2: 记录判断
    print("\n\n示例 2: 记录品味判断")
    print("-" * 60)
    
    judgements = [
        {
            'text': '这个界面设计很简洁',
            'judgement': '简洁而优雅',
            'rating': 0.9,
            'category': 'design',
            'tags': ['简洁', '现代']
        },
        {
            'text': '这个文案写得很生动',
            'judgement': '生动有趣',
            'rating': 0.8,
            'category': 'writing',
            'tags': ['生动', '有趣']
        },
        {
            'text': '这个排版很舒适',
            'judgement': '舒适易读',
            'rating': 0.85,
            'category': 'design',
            'tags': ['舒适', '易读']
        }
    ]
    
    for j in judgements:
        record = analyzer.record_judgement(
            text=j['text'],
            judgement=j['judgement'],
            rating=j['rating'],
            category=j['category'],
            tags=j['tags']
        )
        print(f"✅ 记录: {j['judgement']} (评分: {j['rating']})")
    
    # 示例 3: 统计数据
    print("\n\n示例 3: 统计分析")
    print("-" * 60)
    
    stats = analyzer.get_statistics()
    print(f"总判断数: {stats['total']}")
    print(f"平均评分: {stats['avg_rating']:.2f}")
    print(f"平均复杂度: {stats['avg_complexity']:.2f}")
    print(f"平均可读性: {stats['avg_readability']:.2f}")
    print(f"分类分布: {stats['categories']}")
    print(f"标签分布: {stats['tags']}")
    
    # 示例 4: 相似判断
    print("\n\n示例 4: 相似判断查询")
    print("-" * 60)
    
    query_text = "这个设计很简洁"
    similar = analyzer.find_similar_judgements(query_text, similarity_threshold=0.6)
    
    print(f"查询文本: {query_text}")
    print(f"找到 {len(similar)} 个相似判断:")
    
    for item in similar:
        j = item['judgement']
        print(f"  相似度 {item['similarity']:.2f}: {j['judgement']} (评分: {j['rating']})")
    
    # 示例 5: 导出数据
    print("\n\n示例 5: 数据导出")
    print("-" * 60)
    
    filepath = analyzer.export_data()
    print(f"✅ 数据已导出到: {filepath}")
