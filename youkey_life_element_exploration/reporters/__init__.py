# -*- encoding=utf8 -*-
"""
报告生成模块

提供质量报告和优化建议报告的生成功能
"""

# 质量报告生成器
from .quality_reporter import (
    QualityReporter,
    ReportFormat,
    ReportLevel,
    ReportScope,
    ReportSection,
    ReportMetadata,
    QualityReport
)

# 优化报告生成器
from .optimization_reporter import (
    OptimizationReporter,
    OptimizationReportType,
    ReportTimeframe,
    OptimizationMetrics,
    OptimizationTrend,
    OptimizationInsight,
    OptimizationReportData,
    OptimizationReport
)

__all__ = [
    # 质量报告生成器
    'QualityReporter',
    'ReportFormat',
    'ReportLevel',
    'ReportScope',
    'ReportSection',
    'ReportMetadata',
    'QualityReport',
    
    # 优化报告生成器
    'OptimizationReporter',
    'OptimizationReportType',
    'ReportTimeframe',
    'OptimizationMetrics',
    'OptimizationTrend',
    'OptimizationInsight',
    'OptimizationReportData',
    'OptimizationReport'
]