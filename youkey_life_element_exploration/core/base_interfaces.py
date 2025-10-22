# -*- encoding=utf8 -*-
"""
基础接口定义

定义项目中各模块的标准接口，确保模块间的一致性和可扩展性
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from .unified_models import (
    ElementInfo, ActionInfo, ElementMapping, QualityMetrics, 
    AnalysisResult, OptimizationResult, OptimizationStrategy, Report
)


# ============================================================================
# 元素提取接口
# ============================================================================

class IElementExtractor(ABC):
    """元素提取器接口"""
    
    @abstractmethod
    def extract_elements(self, source: str) -> List[ElementInfo]:
        """
        从源文件中提取元素信息
        
        Args:
            source: 源文件路径或内容
            
        Returns:
            元素信息列表
        """
        pass
    
    @abstractmethod
    def extract_actions(self, source: str) -> List[ActionInfo]:
        """
        从源文件中提取操作信息
        
        Args:
            source: 源文件路径或内容
            
        Returns:
            操作信息列表
        """
        pass
    
    @abstractmethod
    def validate_source(self, source: str) -> bool:
        """
        验证源文件是否有效
        
        Args:
            source: 源文件路径或内容
            
        Returns:
            是否有效
        """
        pass


# ============================================================================
# 元素映射接口
# ============================================================================

class IElementMapper(ABC):
    """元素映射器接口"""
    
    @abstractmethod
    def create_mappings(self, airtest_elements: List[ElementInfo], 
                       poco_elements: List[ElementInfo]) -> List[ElementMapping]:
        """
        创建元素映射关系
        
        Args:
            airtest_elements: Airtest元素列表
            poco_elements: Poco元素列表
            
        Returns:
            映射关系列表
        """
        pass
    
    @abstractmethod
    def calculate_similarity(self, element1: ElementInfo, element2: ElementInfo) -> float:
        """
        计算两个元素的相似度
        
        Args:
            element1: 元素1
            element2: 元素2
            
        Returns:
            相似度分数 (0-1)
        """
        pass
    
    @abstractmethod
    def validate_mapping(self, mapping: ElementMapping) -> bool:
        """
        验证映射关系的有效性
        
        Args:
            mapping: 映射关系
            
        Returns:
            是否有效
        """
        pass


# ============================================================================
# 质量分析接口
# ============================================================================

class IQualityAnalyzer(ABC):
    """质量分析器接口"""
    
    @abstractmethod
    def analyze_element_quality(self, element_id: str, element_data: Dict[str, Any]) -> QualityMetrics:
        """
        分析元素质量
        
        Args:
            element_id: 元素ID
            element_data: 元素数据
            
        Returns:
            质量指标
        """
        pass
    
    @abstractmethod
    def calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """
        计算质量分数
        
        Args:
            metrics: 指标数据
            
        Returns:
            质量分数 (0-100)
        """
        pass
    
    @abstractmethod
    def get_quality_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """
        获取质量改进建议
        
        Args:
            metrics: 质量指标
            
        Returns:
            改进建议列表
        """
        pass


# ============================================================================
# 性能优化接口
# ============================================================================

class IPerformanceOptimizer(ABC):
    """性能优化器接口"""
    
    @abstractmethod
    def optimize_element(self, element_id: str, element_data: Dict[str, Any], 
                        strategies: List[OptimizationStrategy] = None) -> OptimizationResult:
        """
        优化元素性能
        
        Args:
            element_id: 元素ID
            element_data: 元素数据
            strategies: 优化策略列表
            
        Returns:
            优化结果
        """
        pass
    
    @abstractmethod
    def get_optimization_strategies(self, quality_metrics: QualityMetrics) -> List[OptimizationStrategy]:
        """
        获取优化策略
        
        Args:
            quality_metrics: 质量指标
            
        Returns:
            优化策略列表
        """
        pass
    
    @abstractmethod
    def validate_optimization(self, result: OptimizationResult) -> bool:
        """
        验证优化结果
        
        Args:
            result: 优化结果
            
        Returns:
            是否有效
        """
        pass


# ============================================================================
# 数据分析接口
# ============================================================================

class IDataAnalyzer(ABC):
    """数据分析器接口"""
    
    @abstractmethod
    def analyze_trends(self, element_id: str, time_range: int = 7) -> AnalysisResult:
        """
        分析趋势
        
        Args:
            element_id: 元素ID
            time_range: 时间范围（天）
            
        Returns:
            分析结果
        """
        pass
    
    @abstractmethod
    def detect_anomalies(self, metrics: List[QualityMetrics]) -> List[str]:
        """
        检测异常
        
        Args:
            metrics: 质量指标列表
            
        Returns:
            异常列表
        """
        pass
    
    @abstractmethod
    def predict_quality(self, element_id: str, forecast_days: int = 7) -> Dict[str, Any]:
        """
        预测质量趋势
        
        Args:
            element_id: 元素ID
            forecast_days: 预测天数
            
        Returns:
            预测结果
        """
        pass


# ============================================================================
# 报告生成接口
# ============================================================================

class IReportGenerator(ABC):
    """报告生成器接口"""
    
    @abstractmethod
    def generate_report(self, report_type: str, data: Dict[str, Any], 
                       output_path: str = None) -> Report:
        """
        生成报告
        
        Args:
            report_type: 报告类型
            data: 报告数据
            output_path: 输出路径
            
        Returns:
            报告对象
        """
        pass
    
    @abstractmethod
    def export_report(self, report: Report, format: str = "markdown") -> str:
        """
        导出报告
        
        Args:
            report: 报告对象
            format: 导出格式
            
        Returns:
            导出文件路径
        """
        pass
    
    @abstractmethod
    def validate_report_data(self, data: Dict[str, Any]) -> bool:
        """
        验证报告数据
        
        Args:
            data: 报告数据
            
        Returns:
            是否有效
        """
        pass


# ============================================================================
# 配置管理接口
# ============================================================================

class IConfigManager(ABC):
    """配置管理器接口"""
    
    @abstractmethod
    def load_config(self, config_type: str) -> Dict[str, Any]:
        """
        加载配置
        
        Args:
            config_type: 配置类型
            
        Returns:
            配置数据
        """
        pass
    
    @abstractmethod
    def save_config(self, config_type: str, config_data: Dict[str, Any]) -> bool:
        """
        保存配置
        
        Args:
            config_type: 配置类型
            config_data: 配置数据
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def validate_config(self, config_type: str, config_data: Dict[str, Any]) -> bool:
        """
        验证配置
        
        Args:
            config_type: 配置类型
            config_data: 配置数据
            
        Returns:
            是否有效
        """
        pass


# ============================================================================
# 数据存储接口
# ============================================================================

class IDataStorage(ABC):
    """数据存储接口"""
    
    @abstractmethod
    def save_metrics(self, metrics: QualityMetrics) -> bool:
        """
        保存质量指标
        
        Args:
            metrics: 质量指标
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def load_metrics(self, element_id: str, time_range: int = 7) -> List[QualityMetrics]:
        """
        加载质量指标
        
        Args:
            element_id: 元素ID
            time_range: 时间范围（天）
            
        Returns:
            质量指标列表
        """
        pass
    
    @abstractmethod
    def save_analysis_result(self, result: AnalysisResult) -> bool:
        """
        保存分析结果
        
        Args:
            result: 分析结果
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def load_analysis_results(self, element_id: str, analysis_type: str = None) -> List[AnalysisResult]:
        """
        加载分析结果
        
        Args:
            element_id: 元素ID
            analysis_type: 分析类型
            
        Returns:
            分析结果列表
        """
        pass


# ============================================================================
# 监控接口
# ============================================================================

class IMonitor(ABC):
    """监控器接口"""
    
    @abstractmethod
    def start_monitoring(self, element_ids: List[str] = None) -> str:
        """
        开始监控
        
        Args:
            element_ids: 要监控的元素ID列表
            
        Returns:
            监控会话ID
        """
        pass
    
    @abstractmethod
    def stop_monitoring(self, session_id: str) -> Dict[str, Any]:
        """
        停止监控
        
        Args:
            session_id: 监控会话ID
            
        Returns:
            监控结果
        """
        pass
    
    @abstractmethod
    def get_monitoring_status(self, session_id: str) -> Dict[str, Any]:
        """
        获取监控状态
        
        Args:
            session_id: 监控会话ID
            
        Returns:
            监控状态
        """
        pass


# ============================================================================
# 工厂接口
# ============================================================================

class IComponentFactory(ABC):
    """组件工厂接口"""
    
    @abstractmethod
    def create_extractor(self, extractor_type: str) -> IElementExtractor:
        """创建元素提取器"""
        pass
    
    @abstractmethod
    def create_mapper(self, mapper_type: str) -> IElementMapper:
        """创建元素映射器"""
        pass
    
    @abstractmethod
    def create_analyzer(self, analyzer_type: str) -> IQualityAnalyzer:
        """创建质量分析器"""
        pass
    
    @abstractmethod
    def create_optimizer(self, optimizer_type: str) -> IPerformanceOptimizer:
        """创建性能优化器"""
        pass
    
    @abstractmethod
    def create_reporter(self, reporter_type: str) -> IReportGenerator:
        """创建报告生成器"""
        pass