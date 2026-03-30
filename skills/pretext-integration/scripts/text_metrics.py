#!/usr/bin/env python3
"""
Pretext 文本测量集成模块
用于八字命理报告、AI 内容验证等场景

支持：
- 文本高度计算
- 文本宽度计算
- 多语言支持（中文、emoji 等）
- 缓存机制
"""

import subprocess
import json
import hashlib
from typing import Dict, Tuple, Optional
from pathlib import Path


class PretextMetrics:
    """Pretext 文本测量工具"""
    
    def __init__(self, cache_size: int = 1000):
        self.cache: Dict[str, Dict] = {}
        self.cache_size = cache_size
        self._check_pretext_installed()
    
    def _check_pretext_installed(self):
        """检查 Pretext 是否已安装"""
        try:
            result = subprocess.run(
                ['npm', 'list', '@chenglou/pretext'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print("⚠️  Pretext 未安装，请运行: npm install @chenglou/pretext")
        except Exception as e:
            print(f"⚠️  无法检查 Pretext 安装状态: {e}")
    
    def _get_cache_key(self, text: str, font: str, max_width: int) -> str:
        """生成缓存键"""
        key_str = f"{text}|{font}|{max_width}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _call_pretext(self, text: str, font: str, max_width: int, line_height: float) -> Dict:
        """调用 Pretext 计算文本指标"""
        js_code = f"""
const {{ prepare, layout }} = require('@chenglou/pretext')
const text = {json.dumps(text)}
const font = {json.dumps(font)}
const maxWidth = {max_width}
const lineHeight = {line_height}

const prepared = prepare(text, font)
const result = layout(prepared, maxWidth, lineHeight)
console.log(JSON.stringify(result))
"""
        
        try:
            result = subprocess.run(
                ['node', '-e', js_code],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Pretext 计算失败: {result.stderr}")
            
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"无法解析 Pretext 输出: {e}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Pretext 计算超时")
    
    def calculate_height(
        self,
        text: str,
        font: str = '14px 宋体',
        max_width: int = 300,
        line_height: float = 20
    ) -> float:
        """
        计算文本高度
        
        Args:
            text: 要测量的文本
            font: CSS font 简写（如 "14px 宋体"）
            max_width: 最大宽度（像素）
            line_height: 行高（像素）
        
        Returns:
            文本高度（像素）
        """
        cache_key = self._get_cache_key(text, font, max_width)
        
        # 检查缓存
        if cache_key in self.cache:
            return self.cache[cache_key]['height']
        
        # 调用 Pretext
        result = self._call_pretext(text, font, max_width, line_height)
        
        # 缓存结果
        if len(self.cache) >= self.cache_size:
            # 简单的 FIFO 清理
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[cache_key] = result
        return result['height']
    
    def calculate_line_count(
        self,
        text: str,
        font: str = '14px 宋体',
        max_width: int = 300,
        line_height: float = 20
    ) -> int:
        """
        计算文本行数
        
        Args:
            text: 要测量的文本
            font: CSS font 简写
            max_width: 最大宽度（像素）
            line_height: 行高（像素）
        
        Returns:
            行数
        """
        cache_key = self._get_cache_key(text, font, max_width)
        
        if cache_key in self.cache:
            return self.cache[cache_key]['lineCount']
        
        result = self._call_pretext(text, font, max_width, line_height)
        
        if len(self.cache) >= self.cache_size:
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[cache_key] = result
        return result['lineCount']
    
    def calculate_metrics(
        self,
        text: str,
        font: str = '14px 宋体',
        max_width: int = 300,
        line_height: float = 20
    ) -> Dict:
        """
        计算完整的文本指标
        
        Returns:
            {
                'height': float,
                'lineCount': int,
                'density': float,  # 高度 / 文本长度
                'compactness': float  # 文本长度 / 高度
            }
        """
        cache_key = self._get_cache_key(text, font, max_width)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self._call_pretext(text, font, max_width, line_height)
        
        # 添加额外指标
        result['density'] = result['height'] / max(len(text), 1)
        result['compactness'] = max(len(text), 1) / result['height']
        
        if len(self.cache) >= self.cache_size:
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[cache_key] = result
        return result
    
    def validate_text_fit(
        self,
        text: str,
        font: str,
        max_width: int,
        max_height: int,
        line_height: float = 20
    ) -> Tuple[bool, Optional[str]]:
        """
        验证文本是否适应容器
        
        Args:
            text: 要验证的文本
            font: CSS font 简写
            max_width: 容器最大宽度
            max_height: 容器最大高度
            line_height: 行高
        
        Returns:
            (是否适应, 错误信息)
        """
        try:
            height = self.calculate_height(text, font, max_width, line_height)
            
            if height > max_height:
                return False, f"文本高度 {height}px 超过限制 {max_height}px"
            
            return True, None
        except Exception as e:
            return False, f"验证失败: {str(e)}"
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            'size': len(self.cache),
            'max_size': self.cache_size,
            'usage': f"{len(self.cache) / self.cache_size * 100:.1f}%"
        }


# 全局实例
_metrics_instance: Optional[PretextMetrics] = None


def get_metrics() -> PretextMetrics:
    """获取全局 PretextMetrics 实例"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PretextMetrics()
    return _metrics_instance


# 便捷函数
def calculate_height(
    text: str,
    font: str = '14px 宋体',
    max_width: int = 300,
    line_height: float = 20
) -> float:
    """计算文本高度"""
    return get_metrics().calculate_height(text, font, max_width, line_height)


def calculate_line_count(
    text: str,
    font: str = '14px 宋体',
    max_width: int = 300,
    line_height: float = 20
) -> int:
    """计算文本行数"""
    return get_metrics().calculate_line_count(text, font, max_width, line_height)


def calculate_metrics(
    text: str,
    font: str = '14px 宋体',
    max_width: int = 300,
    line_height: float = 20
) -> Dict:
    """计算完整的文本指标"""
    return get_metrics().calculate_metrics(text, font, max_width, line_height)


def validate_text_fit(
    text: str,
    font: str,
    max_width: int,
    max_height: int,
    line_height: float = 20
) -> Tuple[bool, Optional[str]]:
    """验证文本是否适应容器"""
    return get_metrics().validate_text_fit(text, font, max_width, max_height, line_height)


# 示例用法
if __name__ == '__main__':
    metrics = get_metrics()
    
    # 测试中文文本
    print("=== 中文文本测试 ===")
    text = '丙午辛卯丙申庚寅'
    result = metrics.calculate_metrics(text, '18px 宋体', 300, 24)
    print(f"文本: {text}")
    print(f"高度: {result['height']}px")
    print(f"行数: {result['lineCount']}")
    print(f"密度: {result['density']:.2f}")
    print()
    
    # 测试长文本
    print("=== 长文本测试 ===")
    text = '喜用水木，忌火金土。此命格局平凡，需要通过后天努力来改善运势。'
    result = metrics.calculate_metrics(text, '14px 宋体', 300, 20)
    print(f"文本: {text}")
    print(f"高度: {result['height']}px")
    print(f"行数: {result['lineCount']}")
    print()
    
    # 测试验证
    print("=== 文本验证测试 ===")
    text = 'AGI 春天到了. بدأت الرحلة 🚀'
    valid, reason = metrics.validate_text_fit(text, '16px Inter', 200, 40, 20)
    print(f"文本: {text}")
    print(f"验证结果: {'✅ 通过' if valid else f'❌ 失败: {reason}'}")
    print()
    
    # 缓存统计
    print("=== 缓存统计 ===")
    stats = metrics.get_cache_stats()
    print(f"缓存大小: {stats['size']}/{stats['max_size']}")
    print(f"使用率: {stats['usage']}")
