# -*- encoding=utf8 -*-
"""
简化异常检测器

提供核心异常检测功能，减少复杂度
"""

import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import statistics

from ..config.quality_config import QualityConfig


@dataclass
class SimpleAnomalyAlert:
    """简化异常告警"""
    alert_id: str
    element_id: str
    timestamp: datetime
    anomaly_type: str
    severity: str  # low, medium, high, critical
    confidence: float
    description: str
    affected_metrics: List[str] = field(default_factory=list)
    immediate_actions: List[str] = field(default_factory=list)
    status: str = "active"


@dataclass
class AnomalyStats:
    """异常统计"""
    total_anomalies: int = 0
    anomaly_rate: float = 0.0
    type_distribution: Dict[str, int] = field(default_factory=dict)
    severity_distribution: Dict[str, int] = field(default_factory=dict)


class SimpleAnomalyDetector:
    """简化异常检测器"""
    
    def __init__(self, config: QualityConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metric_history = defaultdict(list)
        self.alerts = []
        self.stats = defaultdict(AnomalyStats)
        
        # 简化的阈值配置
        self.thresholds = {
            'performance_score': {'min': 0.7, 'max': 1.0},
            'visibility_score': {'min': 0.8, 'max': 1.0},
            'interaction_score': {'min': 0.75, 'max': 1.0},
            'stability_score': {'min': 0.8, 'max': 1.0}
        }
    
    def detect_anomalies(self, element_id: str, metrics: Dict[str, Any]) -> List[SimpleAnomalyAlert]:
        """检测异常"""
        alerts = []
        
        # 更新历史数据
        self._update_history(element_id, metrics)
        
        # 检测阈值异常
        alerts.extend(self._detect_threshold_anomalies(element_id, metrics))
        
        # 检测统计异常
        alerts.extend(self._detect_statistical_anomalies(element_id, metrics))
        
        # 去重和排序
        alerts = self._deduplicate_alerts(alerts)
        
        # 更新统计
        self._update_stats(element_id, alerts)
        
        return alerts
    
    def get_active_alerts(self, element_id: Optional[str] = None) -> List[SimpleAnomalyAlert]:
        """获取活跃告警"""
        active_alerts = [alert for alert in self.alerts if alert.status == "active"]
        
        if element_id:
            active_alerts = [alert for alert in active_alerts if alert.element_id == element_id]
        
        return active_alerts
    
    def resolve_alert(self, alert_id: str) -> bool:
        """解决告警"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.status = "resolved"
                return True
        return False
    
    def get_stats(self, element_id: str) -> AnomalyStats:
        """获取统计信息"""
        return self.stats[element_id]
    
    def _update_history(self, element_id: str, metrics: Dict[str, Any]) -> None:
        """更新历史数据"""
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                history = self.metric_history[f"{element_id}_{metric_name}"]
                history.append((datetime.now(), value))
                
                # 保持最近100个数据点
                if len(history) > 100:
                    history.pop(0)
    
    def _detect_threshold_anomalies(self, element_id: str, metrics: Dict[str, Any]) -> List[SimpleAnomalyAlert]:
        """检测阈值异常"""
        alerts = []
        
        for metric_name, value in metrics.items():
            if metric_name in self.thresholds and isinstance(value, (int, float)):
                threshold = self.thresholds[metric_name]
                
                if value < threshold['min']:
                    alert = self._create_alert(
                        element_id, metric_name, "threshold_low",
                        f"{metric_name} 低于阈值: {value:.3f} < {threshold['min']}",
                        self._determine_severity(metric_name, value, threshold['min'])
                    )
                    alerts.append(alert)
                elif value > threshold['max']:
                    alert = self._create_alert(
                        element_id, metric_name, "threshold_high", 
                        f"{metric_name} 超过阈值: {value:.3f} > {threshold['max']}",
                        "medium"
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _detect_statistical_anomalies(self, element_id: str, metrics: Dict[str, Any]) -> List[SimpleAnomalyAlert]:
        """检测统计异常"""
        alerts = []
        
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                history_key = f"{element_id}_{metric_name}"
                history = self.metric_history[history_key]
                
                if len(history) >= 10:  # 需要足够的历史数据
                    values = [v for _, v in history]
                    mean = statistics.mean(values)
                    std = statistics.stdev(values) if len(values) > 1 else 0
                    
                    # Z-score异常检测
                    if std > 0:
                        z_score = abs(value - mean) / std
                        if z_score > 2.5:  # 2.5个标准差
                            alert = self._create_alert(
                                element_id, metric_name, "statistical",
                                f"{metric_name} 统计异常: Z-score={z_score:.2f}",
                                "high" if z_score > 3 else "medium"
                            )
                            alerts.append(alert)
        
        return alerts
    
    def _create_alert(self, element_id: str, metric_name: str, anomaly_type: str, 
                     description: str, severity: str) -> SimpleAnomalyAlert:
        """创建告警"""
        alert_id = f"{element_id}_{metric_name}_{anomaly_type}_{int(datetime.now().timestamp())}"
        
        # 简化的建议措施
        actions = self._get_simple_actions(anomaly_type, metric_name)
        
        return SimpleAnomalyAlert(
            alert_id=alert_id,
            element_id=element_id,
            timestamp=datetime.now(),
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=0.8,  # 简化的置信度
            description=description,
            affected_metrics=[metric_name],
            immediate_actions=actions
        )
    
    def _get_simple_actions(self, anomaly_type: str, metric_name: str) -> List[str]:
        """获取简化的建议措施"""
        action_map = {
            "threshold_low": [
                f"检查{metric_name}相关配置",
                "优化元素定位策略",
                "检查测试环境"
            ],
            "threshold_high": [
                f"调整{metric_name}阈值",
                "检查数据异常"
            ],
            "statistical": [
                "分析历史趋势",
                "检查环境变化",
                "验证数据准确性"
            ]
        }
        return action_map.get(anomaly_type, ["检查相关配置"])
    
    def _determine_severity(self, metric_name: str, value: float, threshold: float) -> str:
        """确定严重程度"""
        ratio = value / threshold if threshold > 0 else 0
        
        if ratio < 0.5:
            return "critical"
        elif ratio < 0.7:
            return "high"
        elif ratio < 0.9:
            return "medium"
        else:
            return "low"
    
    def _deduplicate_alerts(self, alerts: List[SimpleAnomalyAlert]) -> List[SimpleAnomalyAlert]:
        """去重告警"""
        seen = set()
        unique_alerts = []
        
        for alert in alerts:
            key = (alert.element_id, alert.anomaly_type, tuple(alert.affected_metrics))
            if key not in seen:
                seen.add(key)
                unique_alerts.append(alert)
        
        return sorted(unique_alerts, key=lambda x: x.severity, reverse=True)
    
    def _update_stats(self, element_id: str, alerts: List[SimpleAnomalyAlert]) -> None:
        """更新统计信息"""
        stats = self.stats[element_id]
        stats.total_anomalies += len(alerts)
        
        for alert in alerts:
            stats.type_distribution[alert.anomaly_type] = \
                stats.type_distribution.get(alert.anomaly_type, 0) + 1
            stats.severity_distribution[alert.severity] = \
                stats.severity_distribution.get(alert.severity, 0) + 1
        
        # 计算异常率（简化）
        total_checks = stats.total_anomalies + 100  # 假设基数
        stats.anomaly_rate = stats.total_anomalies / total_checks
        
        # 保存告警
        self.alerts.extend(alerts)