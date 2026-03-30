"""
chinese-name-lookup scripts 包
主入口函数导出
"""

from .name_generator import (
    quick_generate,
    generate_name_recommendations,
    analyze_existing_name,
)

__all__ = [
    "quick_generate",
    "generate_name_recommendations",
    "analyze_existing_name",
]
