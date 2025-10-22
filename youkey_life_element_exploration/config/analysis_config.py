# -*- encoding=utf8 -*-
"""
分析配置

定义智能分析相关的配置参数
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class AnalysisMethod(Enum):
    """分析方法枚举"""
    STATISTICAL = "statistical"
    MACHINE_LEARNING = "machine_learning"
    RULE_BASED = "rule_based"
    HYBRID = "hybrid"


class TrendAnalysisMethod(Enum):
    """趋势分析方法枚举"""
    LINEAR_REGRESSION = "linear_regression"
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"


@dataclass
class StatisticalConfig:
    """统计分析配置"""
    # 基本参数
    confidence_level: float = 0.95  # 置信水平
    significance_level: float = 0.05  # 显著性水平
    
    # 异常检测
    outlier_detection_method: str = "z_score"  # 异常值检测方法
    outlier_threshold: float = 3.0  # 异常值阈值
    
    # 分布分析
    distribution_tests: List[str] = field(default_factory=lambda: ["normality", "stationarity"])
    
    # 相关性分析
    correlation_methods: List[str] = field(default_factory=lambda: ["pearson", "spearman"])
    correlation_threshold: float = 0.7  # 相关性阈值
    
    # 时间序列
    time_series_window: int = 50  # 时间序列窗口大小
    seasonal_period: int = 24  # 季节性周期（小时）


@dataclass
class TrendAnalysisConfig:
    """趋势分析配置"""
    # 分析方法
    primary_method: TrendAnalysisMethod = TrendAnalysisMethod.LINEAR_REGRESSION
    fallback_methods: List[TrendAnalysisMethod] = field(default_factory=lambda: [
        TrendAnalysisMethod.MOVING_AVERAGE,
        TrendAnalysisMethod.EXPONENTIAL_SMOOTHING
    ])
    
    # 数据要求
    min_data_points: int = 10  # 最少数据点
    max_data_points: int = 1000  # 最多数据点
    data_quality_threshold: float = 0.8  # 数据质量阈值
    
    # 趋势检测
    trend_threshold: float = 0.1  # 趋势阈值
    change_point_detection: bool = True  # 变点检测
    change_point_sensitivity: float = 0.5  # 变点敏感度
    
    # 预测配置
    prediction_horizon: int = 24  # 预测时间范围（小时）
    prediction_confidence: float = 0.8  # 预测置信度
    
    # 平滑参数
    moving_average_window: int = 5  # 移动平均窗口
    exponential_alpha: float = 0.3  # 指数平滑参数


@dataclass
class PatternRecognitionConfig:
    """模式识别配置"""
    # 模式类型
    enabled_patterns: List[str] = field(default_factory=lambda: [
        "periodic", "spike", "dip", "trend", "anomaly"
    ])
    
    # 周期性模式
    periodic_detection: bool = True
    min_period: int = 2  # 最小周期
    max_period: int = 168  # 最大周期（小时）
    period_confidence: float = 0.7  # 周期置信度
    
    # 峰值检测
    spike_detection: bool = True
    spike_threshold: float = 2.0  # 峰值阈值（标准差倍数）
    spike_min_duration: int = 1  # 最小持续时间
    
    # 低谷检测
    dip_detection: bool = True
    dip_threshold: float = -2.0  # 低谷阈值
    dip_min_duration: int = 1  # 最小持续时间
    
    # 模式匹配
    pattern_similarity_threshold: float = 0.8  # 模式相似度阈值
    template_matching: bool = True  # 模板匹配
    
    # 聚类分析
    clustering_enabled: bool = True
    clustering_method: str = "kmeans"  # 聚类方法
    max_clusters: int = 10  # 最大聚类数


@dataclass
class CorrelationAnalysisConfig:
    """相关性分析配置"""
    # 分析范围
    max_variables: int = 50  # 最大变量数
    min_correlation: float = 0.3  # 最小相关性
    
    # 分析方法
    methods: List[str] = field(default_factory=lambda: [
        "pearson", "spearman", "kendall"
    ])
    
    # 滞后分析
    lag_analysis: bool = True
    max_lag: int = 24  # 最大滞后（小时）
    
    # 因果分析
    causality_analysis: bool = True
    causality_method: str = "granger"  # 因果分析方法
    
    # 网络分析
    network_analysis: bool = True
    network_threshold: float = 0.5  # 网络阈值
    
    # 多重比较校正
    multiple_comparison_correction: bool = True
    correction_method: str = "bonferroni"  # 校正方法


@dataclass
class MachineLearningConfig:
    """机器学习配置"""
    # 基本配置
    enabled: bool = False  # 默认禁用，需要额外依赖
    auto_feature_selection: bool = True  # 自动特征选择
    
    # 模型配置
    models: List[str] = field(default_factory=lambda: [
        "linear_regression", "random_forest", "gradient_boosting"
    ])
    
    # 训练配置
    train_test_split: float = 0.8  # 训练测试分割比例
    cross_validation_folds: int = 5  # 交叉验证折数
    
    # 特征工程
    feature_scaling: bool = True  # 特征缩放
    feature_selection_method: str = "recursive"  # 特征选择方法
    max_features: int = 20  # 最大特征数
    
    # 模型评估
    evaluation_metrics: List[str] = field(default_factory=lambda: [
        "mse", "mae", "r2", "accuracy"
    ])
    
    # 超参数优化
    hyperparameter_tuning: bool = True
    tuning_method: str = "grid_search"  # 调优方法
    max_iterations: int = 100  # 最大迭代次数


@dataclass
class AnalysisConfig:
    """分析配置"""
    # 基本配置
    enabled: bool = True
    analysis_method: AnalysisMethod = AnalysisMethod.STATISTICAL
    
    # 子配置
    statistical: StatisticalConfig = field(default_factory=StatisticalConfig)
    trend_analysis: TrendAnalysisConfig = field(default_factory=TrendAnalysisConfig)
    pattern_recognition: PatternRecognitionConfig = field(default_factory=PatternRecognitionConfig)
    correlation_analysis: CorrelationAnalysisConfig = field(default_factory=CorrelationAnalysisConfig)
    machine_learning: MachineLearningConfig = field(default_factory=MachineLearningConfig)
    
    # 数据处理
    data_preprocessing: bool = True  # 数据预处理
    missing_value_strategy: str = "interpolation"  # 缺失值处理策略
    outlier_handling: str = "remove"  # 异常值处理方式
    
    # 分析范围
    analysis_window_hours: int = 168  # 分析窗口（小时）
    min_data_quality: float = 0.7  # 最小数据质量
    
    # 结果配置
    result_confidence_threshold: float = 0.8  # 结果置信度阈值
    max_insights: int = 10  # 最大洞察数量
    
    # 缓存配置
    cache_results: bool = True  # 缓存结果
    cache_duration_hours: int = 24  # 缓存持续时间
    
    # 并行处理
    parallel_processing: bool = True  # 并行处理
    max_workers: int = 4  # 最大工作线程数
    
    def validate(self) -> bool:
        """
        验证配置
        
        Returns:
            bool: 配置是否有效
        """
        try:
            # 验证基本配置
            if not isinstance(self.enabled, bool):
                return False
            
            if not isinstance(self.analysis_method, AnalysisMethod):
                return False
            
            # 验证统计配置
            if not (0.0 < self.statistical.confidence_level < 1.0):
                return False
            
            if not (0.0 < self.statistical.significance_level < 1.0):
                return False
            
            # 验证趋势分析配置
            if self.trend_analysis.min_data_points <= 0:
                return False
            
            if self.trend_analysis.min_data_points >= self.trend_analysis.max_data_points:
                return False
            
            # 验证模式识别配置
            if self.pattern_recognition.min_period >= self.pattern_recognition.max_period:
                return False
            
            # 验证相关性分析配置
            if not (0.0 <= self.correlation_analysis.min_correlation <= 1.0):
                return False
            
            # 验证机器学习配置
            if not (0.0 < self.machine_learning.train_test_split < 1.0):
                return False
            
            # 验证分析范围
            if self.analysis_window_hours <= 0:
                return False
            
            if not (0.0 <= self.min_data_quality <= 1.0):
                return False
            
            return True
            
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return {
            'enabled': self.enabled,
            'analysis_method': self.analysis_method.value,
            'statistical': {
                'confidence_level': self.statistical.confidence_level,
                'significance_level': self.statistical.significance_level,
                'outlier_detection_method': self.statistical.outlier_detection_method,
                'outlier_threshold': self.statistical.outlier_threshold,
                'distribution_tests': self.statistical.distribution_tests,
                'correlation_methods': self.statistical.correlation_methods,
                'correlation_threshold': self.statistical.correlation_threshold,
                'time_series_window': self.statistical.time_series_window,
                'seasonal_period': self.statistical.seasonal_period
            },
            'trend_analysis': {
                'primary_method': self.trend_analysis.primary_method.value,
                'fallback_methods': [m.value for m in self.trend_analysis.fallback_methods],
                'min_data_points': self.trend_analysis.min_data_points,
                'max_data_points': self.trend_analysis.max_data_points,
                'data_quality_threshold': self.trend_analysis.data_quality_threshold,
                'trend_threshold': self.trend_analysis.trend_threshold,
                'change_point_detection': self.trend_analysis.change_point_detection,
                'change_point_sensitivity': self.trend_analysis.change_point_sensitivity,
                'prediction_horizon': self.trend_analysis.prediction_horizon,
                'prediction_confidence': self.trend_analysis.prediction_confidence,
                'moving_average_window': self.trend_analysis.moving_average_window,
                'exponential_alpha': self.trend_analysis.exponential_alpha
            },
            'pattern_recognition': {
                'enabled_patterns': self.pattern_recognition.enabled_patterns,
                'periodic_detection': self.pattern_recognition.periodic_detection,
                'min_period': self.pattern_recognition.min_period,
                'max_period': self.pattern_recognition.max_period,
                'period_confidence': self.pattern_recognition.period_confidence,
                'spike_detection': self.pattern_recognition.spike_detection,
                'spike_threshold': self.pattern_recognition.spike_threshold,
                'spike_min_duration': self.pattern_recognition.spike_min_duration,
                'dip_detection': self.pattern_recognition.dip_detection,
                'dip_threshold': self.pattern_recognition.dip_threshold,
                'dip_min_duration': self.pattern_recognition.dip_min_duration,
                'pattern_similarity_threshold': self.pattern_recognition.pattern_similarity_threshold,
                'template_matching': self.pattern_recognition.template_matching,
                'clustering_enabled': self.pattern_recognition.clustering_enabled,
                'clustering_method': self.pattern_recognition.clustering_method,
                'max_clusters': self.pattern_recognition.max_clusters
            },
            'correlation_analysis': {
                'max_variables': self.correlation_analysis.max_variables,
                'min_correlation': self.correlation_analysis.min_correlation,
                'methods': self.correlation_analysis.methods,
                'lag_analysis': self.correlation_analysis.lag_analysis,
                'max_lag': self.correlation_analysis.max_lag,
                'causality_analysis': self.correlation_analysis.causality_analysis,
                'causality_method': self.correlation_analysis.causality_method,
                'network_analysis': self.correlation_analysis.network_analysis,
                'network_threshold': self.correlation_analysis.network_threshold,
                'multiple_comparison_correction': self.correlation_analysis.multiple_comparison_correction,
                'correction_method': self.correlation_analysis.correction_method
            },
            'machine_learning': {
                'enabled': self.machine_learning.enabled,
                'auto_feature_selection': self.machine_learning.auto_feature_selection,
                'models': self.machine_learning.models,
                'train_test_split': self.machine_learning.train_test_split,
                'cross_validation_folds': self.machine_learning.cross_validation_folds,
                'feature_scaling': self.machine_learning.feature_scaling,
                'feature_selection_method': self.machine_learning.feature_selection_method,
                'max_features': self.machine_learning.max_features,
                'evaluation_metrics': self.machine_learning.evaluation_metrics,
                'hyperparameter_tuning': self.machine_learning.hyperparameter_tuning,
                'tuning_method': self.machine_learning.tuning_method,
                'max_iterations': self.machine_learning.max_iterations
            },
            'data_preprocessing': self.data_preprocessing,
            'missing_value_strategy': self.missing_value_strategy,
            'outlier_handling': self.outlier_handling,
            'analysis_window_hours': self.analysis_window_hours,
            'min_data_quality': self.min_data_quality,
            'result_confidence_threshold': self.result_confidence_threshold,
            'max_insights': self.max_insights,
            'cache_results': self.cache_results,
            'cache_duration_hours': self.cache_duration_hours,
            'parallel_processing': self.parallel_processing,
            'max_workers': self.max_workers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisConfig':
        """
        从字典创建配置
        
        Args:
            data: 配置字典
            
        Returns:
            AnalysisConfig: 分析配置实例
        """
        # 创建子配置对象
        statistical_data = data.get('statistical', {})
        statistical = StatisticalConfig(
            confidence_level=statistical_data.get('confidence_level', 0.95),
            significance_level=statistical_data.get('significance_level', 0.05),
            outlier_detection_method=statistical_data.get('outlier_detection_method', "z_score"),
            outlier_threshold=statistical_data.get('outlier_threshold', 3.0),
            distribution_tests=statistical_data.get('distribution_tests', ["normality", "stationarity"]),
            correlation_methods=statistical_data.get('correlation_methods', ["pearson", "spearman"]),
            correlation_threshold=statistical_data.get('correlation_threshold', 0.7),
            time_series_window=statistical_data.get('time_series_window', 50),
            seasonal_period=statistical_data.get('seasonal_period', 24)
        )
        
        trend_data = data.get('trend_analysis', {})
        trend_analysis = TrendAnalysisConfig(
            primary_method=TrendAnalysisMethod(trend_data.get('primary_method', 'linear_regression')),
            fallback_methods=[
                TrendAnalysisMethod(m) for m in trend_data.get('fallback_methods', ['moving_average', 'exponential_smoothing'])
            ],
            min_data_points=trend_data.get('min_data_points', 10),
            max_data_points=trend_data.get('max_data_points', 1000),
            data_quality_threshold=trend_data.get('data_quality_threshold', 0.8),
            trend_threshold=trend_data.get('trend_threshold', 0.1),
            change_point_detection=trend_data.get('change_point_detection', True),
            change_point_sensitivity=trend_data.get('change_point_sensitivity', 0.5),
            prediction_horizon=trend_data.get('prediction_horizon', 24),
            prediction_confidence=trend_data.get('prediction_confidence', 0.8),
            moving_average_window=trend_data.get('moving_average_window', 5),
            exponential_alpha=trend_data.get('exponential_alpha', 0.3)
        )
        
        pattern_data = data.get('pattern_recognition', {})
        pattern_recognition = PatternRecognitionConfig(
            enabled_patterns=pattern_data.get('enabled_patterns', ["periodic", "spike", "dip", "trend", "anomaly"]),
            periodic_detection=pattern_data.get('periodic_detection', True),
            min_period=pattern_data.get('min_period', 2),
            max_period=pattern_data.get('max_period', 168),
            period_confidence=pattern_data.get('period_confidence', 0.7),
            spike_detection=pattern_data.get('spike_detection', True),
            spike_threshold=pattern_data.get('spike_threshold', 2.0),
            spike_min_duration=pattern_data.get('spike_min_duration', 1),
            dip_detection=pattern_data.get('dip_detection', True),
            dip_threshold=pattern_data.get('dip_threshold', -2.0),
            dip_min_duration=pattern_data.get('dip_min_duration', 1),
            pattern_similarity_threshold=pattern_data.get('pattern_similarity_threshold', 0.8),
            template_matching=pattern_data.get('template_matching', True),
            clustering_enabled=pattern_data.get('clustering_enabled', True),
            clustering_method=pattern_data.get('clustering_method', "kmeans"),
            max_clusters=pattern_data.get('max_clusters', 10)
        )
        
        correlation_data = data.get('correlation_analysis', {})
        correlation_analysis = CorrelationAnalysisConfig(
            max_variables=correlation_data.get('max_variables', 50),
            min_correlation=correlation_data.get('min_correlation', 0.3),
            methods=correlation_data.get('methods', ["pearson", "spearman", "kendall"]),
            lag_analysis=correlation_data.get('lag_analysis', True),
            max_lag=correlation_data.get('max_lag', 24),
            causality_analysis=correlation_data.get('causality_analysis', True),
            causality_method=correlation_data.get('causality_method', "granger"),
            network_analysis=correlation_data.get('network_analysis', True),
            network_threshold=correlation_data.get('network_threshold', 0.5),
            multiple_comparison_correction=correlation_data.get('multiple_comparison_correction', True),
            correction_method=correlation_data.get('correction_method', "bonferroni")
        )
        
        ml_data = data.get('machine_learning', {})
        machine_learning = MachineLearningConfig(
            enabled=ml_data.get('enabled', False),
            auto_feature_selection=ml_data.get('auto_feature_selection', True),
            models=ml_data.get('models', ["linear_regression", "random_forest", "gradient_boosting"]),
            train_test_split=ml_data.get('train_test_split', 0.8),
            cross_validation_folds=ml_data.get('cross_validation_folds', 5),
            feature_scaling=ml_data.get('feature_scaling', True),
            feature_selection_method=ml_data.get('feature_selection_method', "recursive"),
            max_features=ml_data.get('max_features', 20),
            evaluation_metrics=ml_data.get('evaluation_metrics', ["mse", "mae", "r2", "accuracy"]),
            hyperparameter_tuning=ml_data.get('hyperparameter_tuning', True),
            tuning_method=ml_data.get('tuning_method', "grid_search"),
            max_iterations=ml_data.get('max_iterations', 100)
        )
        
        return cls(
            enabled=data.get('enabled', True),
            analysis_method=AnalysisMethod(data.get('analysis_method', 'statistical')),
            statistical=statistical,
            trend_analysis=trend_analysis,
            pattern_recognition=pattern_recognition,
            correlation_analysis=correlation_analysis,
            machine_learning=machine_learning,
            data_preprocessing=data.get('data_preprocessing', True),
            missing_value_strategy=data.get('missing_value_strategy', "interpolation"),
            outlier_handling=data.get('outlier_handling', "remove"),
            analysis_window_hours=data.get('analysis_window_hours', 168),
            min_data_quality=data.get('min_data_quality', 0.7),
            result_confidence_threshold=data.get('result_confidence_threshold', 0.8),
            max_insights=data.get('max_insights', 10),
            cache_results=data.get('cache_results', True),
            cache_duration_hours=data.get('cache_duration_hours', 24),
            parallel_processing=data.get('parallel_processing', True),
            max_workers=data.get('max_workers', 4)
        )