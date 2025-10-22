# -*- encoding=utf8 -*-
"""
Youkey Life 元素探索系统 - 元素质量监控与智能优化模块

这是一个独立的功能模块，专注于UI元素的质量监控、智能分析和性能优化。
该模块与现有的Airtest框架保持兼容，提供额外的质量保证和智能分析能力。

主要功能:
1. 元素质量监控 - 实时监控UI元素的质量指标
2. 智能分析器 - 基于历史数据进行趋势和模式分析
3. 性能优化器 - 提供自动化的性能优化建议
4. 异常检测器 - 检测和预警潜在的质量问题

作者: cooperd
版本: 1.0.0
创建日期: 2025-01-20
"""

__version__ = "1.0.0"
__author__ = "cooperd"
__email__ = "cooperd@example.com"

# 导入核心组件
from .core.quality_monitor import QualityMonitor, QualityMetrics
from .core.intelligent_analyzer import IntelligentAnalyzer, AnalysisResult
from .core.performance_optimizer import PerformanceOptimizer, OptimizationStrategy, OptimizationResult
from .core.anomaly_detector import AnomalyDetector, AnomalyAlert

# 导入配置管理
from .config.quality_config import QualityConfig, MonitoringSettings, QualityThresholds

# 导入分析器模块
from .analyzers import (
    QualityAnalyzer, TrendAnalyzer, PatternAnalyzer, PredictiveAnalyzer,
    QualityScore, TrendDirection, TrendAnalysisResult, PatternType,
    PatternAnalysisResult, PredictionResult, PredictionConfidence
)

# 导入优化器模块
from .optimizers import (
    ElementOptimizer, StrategyOptimizer, ResourceOptimizer,
    OptimizationType, OptimizationGoal, OptimizationConstraint,
    ElementOptimizationResult, StrategyType, StrategyScope, StrategyPhase,
    StrategyOptimizationResult, ResourceType, ResourcePriority, AllocationStrategy,
    ResourceOptimizationResult
)

# 导入报告生成器模块
from .reporters import (
    QualityReporter, OptimizationReporter,
    ReportFormat, ReportLevel, ReportScope, QualityReport,
    OptimizationReportType, ReportTimeframe, OptimizationReport
)

# 导入工具模块
from .utils import (
    DataProcessor, DataValidator, VisualizationUtils, ExportUtils,
    DataType, AggregationType, TransformationType, ValidationLevel,
    ValidationCategory, ChartType, ColorScheme, ExportFormat
)

# 导入映射器模块
from .mappers import (
    AirtestPocoMapper, AirtestElement, PocoElement, ElementMapping,
    ImprovedAirtestPocoMapper, PreciseAirtestPocoMapper
)

# 导入演示脚本模块
from .scripts import (
    ElementExtractionDemo, SimpleElementMapper, 
    CorrelationAnalyzer, ElementCorrelation
)

__all__ = [
    # 核心组件
    'QualityMonitor',
    'QualityMetrics', 
    'IntelligentAnalyzer',
    'AnalysisResult',
    'PerformanceOptimizer',
    'OptimizationStrategy',
    'OptimizationResult',
    'AnomalyDetector',
    'AnomalyAlert',
    
    # 配置管理
    'QualityConfig', 'MonitoringSettings', 'QualityThresholds',
    
    # 分析器模块
    'QualityAnalyzer',
    'TrendAnalyzer',
    'PatternAnalyzer',
    'PredictiveAnalyzer',
    'QualityScore',
    'TrendDirection',
    'TrendAnalysisResult',
    'PatternType',
    'PatternAnalysisResult',
    'PredictionResult',
    'PredictionConfidence',
    
    # 优化器模块
    'ElementOptimizer',
    'StrategyOptimizer',
    'ResourceOptimizer',
    'OptimizationType',
    'OptimizationGoal',
    'OptimizationConstraint',
    'ElementOptimizationResult',
    'StrategyType',
    'StrategyScope',
    'StrategyPhase',
    'StrategyOptimizationResult',
    'ResourceType',
    'ResourcePriority',
    'AllocationStrategy',
    'ResourceOptimizationResult',
    
    # 报告生成器模块
    'QualityReporter',
    'OptimizationReporter',
    'ReportFormat',
    'ReportLevel',
    'ReportScope',
    'QualityReport',
    'OptimizationReportType',
    'ReportTimeframe',
    'OptimizationReport',
    
    # 工具模块
    'DataProcessor',
    'DataValidator',
    'VisualizationUtils',
    'ExportUtils',
    'DataType',
    'AggregationType',
    'TransformationType',
    'ValidationLevel',
    'ValidationCategory',
    'ChartType',
    'ColorScheme',
    'ExportFormat',
    
    # 映射器模块
    'AirtestPocoMapper',
    'AirtestElement', 
    'PocoElement',
    'ElementMapping',
    'ImprovedAirtestPocoMapper',
    'PreciseAirtestPocoMapper',
    
    # 演示脚本模块
    'ElementExtractionDemo',
    'SimpleElementMapper',
    'CorrelationAnalyzer',
    'ElementCorrelation',
]


def get_version():
    """获取模块版本"""
    return __version__


def get_module_info():
    """获取模块信息"""
    return {
        'name': 'Youkey Life Element Exploration',
        'version': __version__,
        'author': __author__,
        'description': 'UI元素质量监控与智能优化模块',
        'components': len(__all__),
        'compatible_frameworks': ['Airtest', 'Poco', 'UIAutomator']
    }