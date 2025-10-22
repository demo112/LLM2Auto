# -*- encoding=utf8 -*-
"""
质量监控配置模块

定义元素质量监控的各项配置参数
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class QualityThresholds:
    """质量阈值配置"""
    # 性能阈值
    response_time_threshold: float = 3.0  # 响应时间阈值(秒)
    success_rate_threshold: float = 0.95  # 成功率阈值
    stability_threshold: float = 0.90  # 稳定性阈值
    
    # 元素质量阈值
    element_visibility_threshold: float = 0.8  # 元素可见性阈值
    element_accessibility_threshold: float = 0.9  # 元素可访问性阈值
    element_reliability_threshold: float = 0.85  # 元素可靠性阈值
    
    # 异常检测阈值
    anomaly_detection_threshold: float = 2.0  # 异常检测标准差倍数
    trend_change_threshold: float = 0.1  # 趋势变化阈值


@dataclass
class MonitoringSettings:
    """监控设置配置"""
    # 监控频率
    monitoring_interval: int = 300  # 监控间隔(秒)
    data_retention_days: int = 30  # 数据保留天数
    
    # 监控范围
    monitor_performance: bool = True
    monitor_stability: bool = True
    monitor_accessibility: bool = True
    monitor_usability: bool = True
    
    # 报警设置
    enable_alerts: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ['email', 'log'])
    alert_threshold_breach_count: int = 3  # 连续阈值突破次数触发报警


@dataclass
class QualityConfig:
    """质量监控主配置类"""
    # 基础配置
    project_name: str = "youkey_life_element_exploration"
    version: str = "1.0.0"
    
    # 路径配置
    data_dir: Path = field(default_factory=lambda: Path("./data"))
    log_dir: Path = field(default_factory=lambda: Path("./logs"))
    report_dir: Path = field(default_factory=lambda: Path("./reports"))
    
    # 质量阈值
    thresholds: QualityThresholds = field(default_factory=QualityThresholds)
    
    # 监控设置
    monitoring: MonitoringSettings = field(default_factory=MonitoringSettings)
    
    # 扩展配置
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    plugins: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保路径为Path对象
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)
        if isinstance(self.log_dir, str):
            self.log_dir = Path(self.log_dir)
        if isinstance(self.report_dir, str):
            self.report_dir = Path(self.report_dir)
    
    def validate(self) -> bool:
        """验证配置有效性"""
        try:
            # 验证阈值范围
            if not (0 <= self.thresholds.success_rate_threshold <= 1):
                return False
            if not (0 <= self.thresholds.stability_threshold <= 1):
                return False
            if not (0 <= self.thresholds.element_visibility_threshold <= 1):
                return False
            
            # 验证监控间隔
            if self.monitoring.monitoring_interval <= 0:
                return False
            
            # 验证数据保留天数
            if self.monitoring.data_retention_days <= 0:
                return False
            
            return True
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'project_name': self.project_name,
            'version': self.version,
            'data_dir': str(self.data_dir),
            'log_dir': str(self.log_dir),
            'report_dir': str(self.report_dir),
            'thresholds': {
                'response_time_threshold': self.thresholds.response_time_threshold,
                'success_rate_threshold': self.thresholds.success_rate_threshold,
                'stability_threshold': self.thresholds.stability_threshold,
                'element_visibility_threshold': self.thresholds.element_visibility_threshold,
                'element_accessibility_threshold': self.thresholds.element_accessibility_threshold,
                'element_reliability_threshold': self.thresholds.element_reliability_threshold,
                'anomaly_detection_threshold': self.thresholds.anomaly_detection_threshold,
                'trend_change_threshold': self.thresholds.trend_change_threshold,
            },
            'monitoring': {
                'monitoring_interval': self.monitoring.monitoring_interval,
                'data_retention_days': self.monitoring.data_retention_days,
                'monitor_performance': self.monitoring.monitor_performance,
                'monitor_stability': self.monitoring.monitor_stability,
                'monitor_accessibility': self.monitoring.monitor_accessibility,
                'monitor_usability': self.monitoring.monitor_usability,
                'enable_alerts': self.monitoring.enable_alerts,
                'alert_channels': self.monitoring.alert_channels,
                'alert_threshold_breach_count': self.monitoring.alert_threshold_breach_count,
            },
            'custom_metrics': self.custom_metrics,
            'plugins': self.plugins,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualityConfig':
        """从字典创建配置对象"""
        thresholds_data = data.get('thresholds', {})
        monitoring_data = data.get('monitoring', {})
        
        thresholds = QualityThresholds(**thresholds_data)
        monitoring = MonitoringSettings(**monitoring_data)
        
        return cls(
            project_name=data.get('project_name', 'youkey_life_element_exploration'),
            version=data.get('version', '1.0.0'),
            data_dir=Path(data.get('data_dir', './data')),
            log_dir=Path(data.get('log_dir', './logs')),
            report_dir=Path(data.get('report_dir', './reports')),
            thresholds=thresholds,
            monitoring=monitoring,
            custom_metrics=data.get('custom_metrics', {}),
            plugins=data.get('plugins', []),
        )