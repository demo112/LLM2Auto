# -*- encoding=utf8 -*-
"""
分析器模块

提供统一的元素分析功能，包括质量分析、趋势分析等。
"""

# 统一分析器 - 集成了元素分析、质量分析等功能
from .unified_analyzer import (
    UnifiedAnalyzer,
    AnalysisType,
    AnalysisLevel,
    UnifiedAnalysisResult
)

# 简单趋势分析器
from .simple_trend_analyzer import (
    SimpleTrendAnalyzer,
    SimpleTrendResult
)

__all__ = [
    # 统一分析器
    "UnifiedAnalyzer",
    "AnalysisType",
    "AnalysisLevel",
    "UnifiedAnalysisResult",
    
    # 简单趋势分析器
    "SimpleTrendAnalyzer",
    "SimpleTrendResult"
]