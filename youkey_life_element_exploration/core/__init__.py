# -*- encoding=utf8 -*-
"""
核心模块

提供统一的、内聚的核心功能接口
"""

# 导入统一的数据模型
from .unified_models import (
    # 枚举类型
    ElementType, ActionType, CorrelationType, QualityLevel,
    
    # 核心数据模型
    AirtestElement, PocoElement, ElementInfo, ActionInfo,
    ElementMapping, QualityScore, QualityMetrics,
    OptimizationStrategy, OptimizationResult,
    AnalysisResult, ReportSection, Report,
    
    # 工具函数
    get_quality_level, create_quality_score,
    generate_element_id, generate_mapping_id
)

# 导入基础接口
from .base_interfaces import (
    IElementExtractor, IElementMapper, IQualityAnalyzer,
    IPerformanceOptimizer, IDataAnalyzer, IReportGenerator,
    IConfigManager, IDataStorage, IMonitor, IComponentFactory
)

# 导入统一的核心组件
from .unified_element_mapper import UnifiedElementExtractor, UnifiedElementMapper
from .unified_analyzer import UnifiedQualityAnalyzer, UnifiedDataAnalyzer
from .unified_reporter import UnifiedReportGenerator
from .unified_config import (
    UnifiedConfigManager, MappingConfig, QualityConfig,
    ReportConfig, AnalysisConfig, SystemConfig, UnifiedConfig,
    get_config_manager, get_config, set_config
)
from .unified_optimizer import UnifiedPerformanceOptimizer, PerformanceMetrics, OptimizationPlan
from .unified_monitor import (
    UnifiedMonitor, MonitoringEvent, PerformanceSnapshot,
    QualitySnapshot, AlertRule
)

# 保持向后兼容性 - 导入原有组件
try:
    from .element_mapper import ElementMapper
    from .performance_optimizer import PerformanceOptimizer
    from .quality_monitor import QualityMonitor
    _legacy_components_available = True
except ImportError:
    _legacy_components_available = False


# 版本信息
__version__ = "1.0.0"
__author__ = "YouKey Life Element Exploration Team"


# 导出的公共接口
__all__ = [
    # 数据模型
    'ElementType', 'ActionType', 'CorrelationType', 'QualityLevel',
    'AirtestElement', 'PocoElement', 'ElementInfo', 'ActionInfo',
    'ElementMapping', 'QualityScore', 'QualityMetrics',
    'OptimizationStrategy', 'OptimizationResult',
    'AnalysisResult', 'ReportSection', 'Report',
    
    # 工具函数
    'get_quality_level', 'create_quality_score',
    'generate_element_id', 'generate_mapping_id',
    
    # 基础接口
    'IElementExtractor', 'IElementMapper', 'IQualityAnalyzer',
    'IPerformanceOptimizer', 'IDataAnalyzer', 'IReportGenerator',
    'IConfigManager', 'IDataStorage', 'IMonitor', 'IComponentFactory',
    
    # 核心组件
    'UnifiedElementExtractor', 'UnifiedElementMapper',
    'UnifiedQualityAnalyzer', 'UnifiedDataAnalyzer',
    'UnifiedReportGenerator',
    'UnifiedConfigManager', 'MappingConfig', 'QualityConfig',
    'ReportConfig', 'AnalysisConfig', 'SystemConfig', 'UnifiedConfig',
    'UnifiedPerformanceOptimizer', 'PerformanceMetrics', 'OptimizationPlan',
    'UnifiedMonitor', 'MonitoringEvent', 'PerformanceSnapshot',
    'QualitySnapshot', 'AlertRule',
    
    # 便捷函数
    'get_config_manager', 'get_config', 'set_config',
]

# 如果原有组件可用，也导出它们以保持向后兼容性
if _legacy_components_available:
    __all__.extend(['ElementMapper', 'PerformanceOptimizer', 'QualityMonitor'])


def create_unified_system(config_file: str = None) -> dict:
    """
    创建统一的系统组件
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        包含所有核心组件的字典
    """
    # 创建配置管理器
    config_manager = UnifiedConfigManager(config_file)
    
    # 获取配置
    mapping_config = config_manager.get_mapping_config()
    system_config = config_manager.get_system_config()
    
    # 创建核心组件
    element_extractor = UnifiedElementExtractor()
    element_mapper = UnifiedElementMapper(
        similarity_weights=mapping_config.similarity_weights,
        confidence_threshold=mapping_config.confidence_threshold
    )
    quality_analyzer = UnifiedQualityAnalyzer(
        quality_weights=config_manager.get_quality_config().quality_weights
    )
    data_analyzer = UnifiedDataAnalyzer()
    report_generator = UnifiedReportGenerator(
        output_formats=config_manager.get_report_config().output_formats
    )
    performance_optimizer = UnifiedPerformanceOptimizer(
        max_workers=system_config.max_workers
    )
    monitor = UnifiedMonitor()
    
    return {
        'config_manager': config_manager,
        'element_extractor': element_extractor,
        'element_mapper': element_mapper,
        'quality_analyzer': quality_analyzer,
        'data_analyzer': data_analyzer,
        'report_generator': report_generator,
        'performance_optimizer': performance_optimizer,
        'monitor': monitor
    }


def get_system_info() -> dict:
    """
    获取系统信息
    
    Returns:
        系统信息字典
    """
    return {
        'version': __version__,
        'author': __author__,
        'components': [
            'UnifiedElementExtractor',
            'UnifiedElementMapper', 
            'UnifiedQualityAnalyzer',
            'UnifiedDataAnalyzer',
            'UnifiedReportGenerator',
            'UnifiedConfigManager',
            'UnifiedPerformanceOptimizer',
            'UnifiedMonitor'
        ],
        'features': [
            '统一的数据模型',
            '标准化的接口',
            '高性能的元素映射',
            '全面的质量分析',
            '灵活的报告生成',
            '智能的性能优化',
            '实时的系统监控',
            '可配置的参数管理'
        ],
        'legacy_support': _legacy_components_available
    }