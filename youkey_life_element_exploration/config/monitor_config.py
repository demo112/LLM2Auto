# -*- encoding=utf8 -*-
"""
监控配置

定义监控相关的配置参数
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import timedelta


@dataclass
class MonitoringSchedule:
    """监控调度配置"""
    # 基本调度
    enabled: bool = True
    interval_seconds: int = 60  # 监控间隔（秒）
    batch_size: int = 10  # 批处理大小
    
    # 时间窗口
    active_hours: List[int] = field(default_factory=lambda: list(range(24)))  # 活跃小时
    active_days: List[int] = field(default_factory=lambda: list(range(7)))   # 活跃天数（0=周一）
    
    # 自适应调度
    adaptive_interval: bool = True  # 自适应间隔
    min_interval: int = 30  # 最小间隔
    max_interval: int = 300  # 最大间隔
    
    # 负载控制
    max_concurrent: int = 5  # 最大并发数
    timeout_seconds: int = 30  # 超时时间
    retry_count: int = 3  # 重试次数


@dataclass
class DataRetention:
    """数据保留配置"""
    # 原始数据保留
    raw_data_days: int = 7  # 原始数据保留天数
    aggregated_data_days: int = 30  # 聚合数据保留天数
    summary_data_days: int = 90  # 摘要数据保留天数
    
    # 异常数据保留
    anomaly_data_days: int = 30  # 异常数据保留天数
    alert_data_days: int = 60  # 告警数据保留天数
    
    # 自动清理
    auto_cleanup: bool = True  # 自动清理
    cleanup_interval_hours: int = 24  # 清理间隔（小时）
    
    # 压缩配置
    enable_compression: bool = True  # 启用压缩
    compression_threshold_days: int = 3  # 压缩阈值天数


@dataclass
class AlertingConfig:
    """告警配置"""
    # 基本告警
    enabled: bool = True
    channels: List[str] = field(default_factory=lambda: ["log", "email"])  # 告警渠道
    
    # 告警级别
    severity_levels: List[str] = field(default_factory=lambda: ["low", "medium", "high", "critical"])
    min_severity: str = "medium"  # 最小告警级别
    
    # 告警频率控制
    rate_limit_enabled: bool = True  # 启用频率限制
    max_alerts_per_hour: int = 10  # 每小时最大告警数
    duplicate_suppression_minutes: int = 30  # 重复告警抑制时间（分钟）
    
    # 告警聚合
    aggregation_enabled: bool = True  # 启用告警聚合
    aggregation_window_minutes: int = 15  # 聚合窗口（分钟）
    max_aggregated_alerts: int = 5  # 最大聚合告警数
    
    # 自动恢复
    auto_resolve_enabled: bool = True  # 自动解决告警
    auto_resolve_timeout_hours: int = 24  # 自动解决超时（小时）
    
    # 通知配置
    notification_templates: Dict[str, str] = field(default_factory=dict)
    escalation_rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PerformanceConfig:
    """性能配置"""
    # 采样配置
    sampling_enabled: bool = True  # 启用采样
    sampling_rate: float = 1.0  # 采样率（0.0-1.0）
    adaptive_sampling: bool = True  # 自适应采样
    
    # 缓存配置
    cache_enabled: bool = True  # 启用缓存
    cache_size_mb: int = 100  # 缓存大小（MB）
    cache_ttl_seconds: int = 300  # 缓存TTL（秒）
    
    # 并发控制
    max_workers: int = 4  # 最大工作线程数
    queue_size: int = 1000  # 队列大小
    
    # 资源限制
    memory_limit_mb: int = 500  # 内存限制（MB）
    cpu_limit_percent: int = 80  # CPU限制（百分比）
    
    # 优化选项
    enable_profiling: bool = False  # 启用性能分析
    profile_sample_rate: float = 0.01  # 性能分析采样率


@dataclass
class MonitorConfig:
    """监控配置"""
    # 基本配置
    enabled: bool = True
    name: str = "element_monitor"
    version: str = "1.0.0"
    
    # 子配置
    schedule: MonitoringSchedule = field(default_factory=MonitoringSchedule)
    retention: DataRetention = field(default_factory=DataRetention)
    alerting: AlertingConfig = field(default_factory=AlertingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # 监控目标
    target_elements: List[str] = field(default_factory=list)  # 目标元素选择器
    exclude_elements: List[str] = field(default_factory=list)  # 排除元素选择器
    
    # 监控指标
    enabled_metrics: List[str] = field(default_factory=lambda: [
        "performance", "visibility", "accessibility", "stability", "interaction"
    ])
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # 数据输出
    output_formats: List[str] = field(default_factory=lambda: ["json", "csv"])
    output_directory: str = "./monitoring_data"
    
    # 集成配置
    integrations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """
        验证配置
        
        Returns:
            bool: 配置是否有效
        """
        try:
            # 验证基本配置
            if not self.name or not self.version:
                return False
            
            # 验证调度配置
            if self.schedule.interval_seconds <= 0:
                return False
            
            if self.schedule.min_interval >= self.schedule.max_interval:
                return False
            
            # 验证保留配置
            if any(days <= 0 for days in [
                self.retention.raw_data_days,
                self.retention.aggregated_data_days,
                self.retention.summary_data_days
            ]):
                return False
            
            # 验证告警配置
            if self.alerting.min_severity not in self.alerting.severity_levels:
                return False
            
            # 验证性能配置
            if not (0.0 <= self.performance.sampling_rate <= 1.0):
                return False
            
            if self.performance.max_workers <= 0:
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
            'name': self.name,
            'version': self.version,
            'schedule': {
                'enabled': self.schedule.enabled,
                'interval_seconds': self.schedule.interval_seconds,
                'batch_size': self.schedule.batch_size,
                'active_hours': self.schedule.active_hours,
                'active_days': self.schedule.active_days,
                'adaptive_interval': self.schedule.adaptive_interval,
                'min_interval': self.schedule.min_interval,
                'max_interval': self.schedule.max_interval,
                'max_concurrent': self.schedule.max_concurrent,
                'timeout_seconds': self.schedule.timeout_seconds,
                'retry_count': self.schedule.retry_count
            },
            'retention': {
                'raw_data_days': self.retention.raw_data_days,
                'aggregated_data_days': self.retention.aggregated_data_days,
                'summary_data_days': self.retention.summary_data_days,
                'anomaly_data_days': self.retention.anomaly_data_days,
                'alert_data_days': self.retention.alert_data_days,
                'auto_cleanup': self.retention.auto_cleanup,
                'cleanup_interval_hours': self.retention.cleanup_interval_hours,
                'enable_compression': self.retention.enable_compression,
                'compression_threshold_days': self.retention.compression_threshold_days
            },
            'alerting': {
                'enabled': self.alerting.enabled,
                'channels': self.alerting.channels,
                'severity_levels': self.alerting.severity_levels,
                'min_severity': self.alerting.min_severity,
                'rate_limit_enabled': self.alerting.rate_limit_enabled,
                'max_alerts_per_hour': self.alerting.max_alerts_per_hour,
                'duplicate_suppression_minutes': self.alerting.duplicate_suppression_minutes,
                'aggregation_enabled': self.alerting.aggregation_enabled,
                'aggregation_window_minutes': self.alerting.aggregation_window_minutes,
                'max_aggregated_alerts': self.alerting.max_aggregated_alerts,
                'auto_resolve_enabled': self.alerting.auto_resolve_enabled,
                'auto_resolve_timeout_hours': self.alerting.auto_resolve_timeout_hours,
                'notification_templates': self.alerting.notification_templates,
                'escalation_rules': self.alerting.escalation_rules
            },
            'performance': {
                'sampling_enabled': self.performance.sampling_enabled,
                'sampling_rate': self.performance.sampling_rate,
                'adaptive_sampling': self.performance.adaptive_sampling,
                'cache_enabled': self.performance.cache_enabled,
                'cache_size_mb': self.performance.cache_size_mb,
                'cache_ttl_seconds': self.performance.cache_ttl_seconds,
                'max_workers': self.performance.max_workers,
                'queue_size': self.performance.queue_size,
                'memory_limit_mb': self.performance.memory_limit_mb,
                'cpu_limit_percent': self.performance.cpu_limit_percent,
                'enable_profiling': self.performance.enable_profiling,
                'profile_sample_rate': self.performance.profile_sample_rate
            },
            'target_elements': self.target_elements,
            'exclude_elements': self.exclude_elements,
            'enabled_metrics': self.enabled_metrics,
            'custom_metrics': self.custom_metrics,
            'output_formats': self.output_formats,
            'output_directory': self.output_directory,
            'integrations': self.integrations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MonitorConfig':
        """
        从字典创建配置
        
        Args:
            data: 配置字典
            
        Returns:
            MonitorConfig: 监控配置实例
        """
        # 创建子配置对象
        schedule_data = data.get('schedule', {})
        schedule = MonitoringSchedule(
            enabled=schedule_data.get('enabled', True),
            interval_seconds=schedule_data.get('interval_seconds', 60),
            batch_size=schedule_data.get('batch_size', 10),
            active_hours=schedule_data.get('active_hours', list(range(24))),
            active_days=schedule_data.get('active_days', list(range(7))),
            adaptive_interval=schedule_data.get('adaptive_interval', True),
            min_interval=schedule_data.get('min_interval', 30),
            max_interval=schedule_data.get('max_interval', 300),
            max_concurrent=schedule_data.get('max_concurrent', 5),
            timeout_seconds=schedule_data.get('timeout_seconds', 30),
            retry_count=schedule_data.get('retry_count', 3)
        )
        
        retention_data = data.get('retention', {})
        retention = DataRetention(
            raw_data_days=retention_data.get('raw_data_days', 7),
            aggregated_data_days=retention_data.get('aggregated_data_days', 30),
            summary_data_days=retention_data.get('summary_data_days', 90),
            anomaly_data_days=retention_data.get('anomaly_data_days', 30),
            alert_data_days=retention_data.get('alert_data_days', 60),
            auto_cleanup=retention_data.get('auto_cleanup', True),
            cleanup_interval_hours=retention_data.get('cleanup_interval_hours', 24),
            enable_compression=retention_data.get('enable_compression', True),
            compression_threshold_days=retention_data.get('compression_threshold_days', 3)
        )
        
        alerting_data = data.get('alerting', {})
        alerting = AlertingConfig(
            enabled=alerting_data.get('enabled', True),
            channels=alerting_data.get('channels', ["log", "email"]),
            severity_levels=alerting_data.get('severity_levels', ["low", "medium", "high", "critical"]),
            min_severity=alerting_data.get('min_severity', "medium"),
            rate_limit_enabled=alerting_data.get('rate_limit_enabled', True),
            max_alerts_per_hour=alerting_data.get('max_alerts_per_hour', 10),
            duplicate_suppression_minutes=alerting_data.get('duplicate_suppression_minutes', 30),
            aggregation_enabled=alerting_data.get('aggregation_enabled', True),
            aggregation_window_minutes=alerting_data.get('aggregation_window_minutes', 15),
            max_aggregated_alerts=alerting_data.get('max_aggregated_alerts', 5),
            auto_resolve_enabled=alerting_data.get('auto_resolve_enabled', True),
            auto_resolve_timeout_hours=alerting_data.get('auto_resolve_timeout_hours', 24),
            notification_templates=alerting_data.get('notification_templates', {}),
            escalation_rules=alerting_data.get('escalation_rules', [])
        )
        
        performance_data = data.get('performance', {})
        performance = PerformanceConfig(
            sampling_enabled=performance_data.get('sampling_enabled', True),
            sampling_rate=performance_data.get('sampling_rate', 1.0),
            adaptive_sampling=performance_data.get('adaptive_sampling', True),
            cache_enabled=performance_data.get('cache_enabled', True),
            cache_size_mb=performance_data.get('cache_size_mb', 100),
            cache_ttl_seconds=performance_data.get('cache_ttl_seconds', 300),
            max_workers=performance_data.get('max_workers', 4),
            queue_size=performance_data.get('queue_size', 1000),
            memory_limit_mb=performance_data.get('memory_limit_mb', 500),
            cpu_limit_percent=performance_data.get('cpu_limit_percent', 80),
            enable_profiling=performance_data.get('enable_profiling', False),
            profile_sample_rate=performance_data.get('profile_sample_rate', 0.01)
        )
        
        return cls(
            enabled=data.get('enabled', True),
            name=data.get('name', "element_monitor"),
            version=data.get('version', "1.0.0"),
            schedule=schedule,
            retention=retention,
            alerting=alerting,
            performance=performance,
            target_elements=data.get('target_elements', []),
            exclude_elements=data.get('exclude_elements', []),
            enabled_metrics=data.get('enabled_metrics', [
                "performance", "visibility", "accessibility", "stability", "interaction"
            ]),
            custom_metrics=data.get('custom_metrics', {}),
            output_formats=data.get('output_formats', ["json", "csv"]),
            output_directory=data.get('output_directory', "./monitoring_data"),
            integrations=data.get('integrations', {})
        )