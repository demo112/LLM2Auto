# -*- encoding=utf8 -*-
"""
性能指标计算

提供各种性能相关指标的计算功能
"""

import time
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta


@dataclass
class PerformanceData:
    """性能数据"""
    timestamp: datetime
    response_time: float  # 响应时间（秒）
    load_time: float  # 加载时间（秒）
    render_time: float  # 渲染时间（秒）
    memory_usage: float  # 内存使用量（MB）
    cpu_usage: float  # CPU使用率（百分比）
    network_latency: float  # 网络延迟（毫秒）
    throughput: float  # 吞吐量（请求/秒）
    error_rate: float  # 错误率（百分比）
    availability: float  # 可用性（百分比）


@dataclass
class PerformanceScore:
    """性能分数"""
    overall_score: float  # 总体分数（0-1）
    response_time_score: float  # 响应时间分数
    load_time_score: float  # 加载时间分数
    render_time_score: float  # 渲染时间分数
    resource_usage_score: float  # 资源使用分数
    reliability_score: float  # 可靠性分数
    efficiency_score: float  # 效率分数
    details: Dict[str, Any] = field(default_factory=dict)  # 详细信息
    grade: str = "C"  # 等级（A+, A, B+, B, C+, C, D+, D, F）
    
    def __post_init__(self):
        """计算等级"""
        if self.overall_score >= 0.95:
            self.grade = "A+"
        elif self.overall_score >= 0.90:
            self.grade = "A"
        elif self.overall_score >= 0.85:
            self.grade = "B+"
        elif self.overall_score >= 0.80:
            self.grade = "B"
        elif self.overall_score >= 0.75:
            self.grade = "C+"
        elif self.overall_score >= 0.70:
            self.grade = "C"
        elif self.overall_score >= 0.60:
            self.grade = "D+"
        elif self.overall_score >= 0.50:
            self.grade = "D"
        else:
            self.grade = "F"


@dataclass
class PerformanceTrend:
    """性能趋势"""
    metric_name: str  # 指标名称
    trend_direction: str  # 趋势方向：improving, declining, stable
    trend_strength: float  # 趋势强度（0-1）
    slope: float  # 斜率
    correlation: float  # 相关系数
    prediction: Optional[float] = None  # 预测值
    confidence: float = 0.0  # 置信度


class PerformanceMetrics:
    """性能指标计算器"""
    
    def __init__(self):
        """初始化性能指标计算器"""
        self.performance_history: List[PerformanceData] = []
        self.baseline_metrics: Optional[Dict[str, float]] = None
        self.thresholds = {
            'response_time': {'excellent': 0.5, 'good': 1.0, 'acceptable': 2.0},
            'load_time': {'excellent': 1.0, 'good': 2.0, 'acceptable': 3.0},
            'render_time': {'excellent': 0.2, 'good': 0.5, 'acceptable': 1.0},
            'memory_usage': {'excellent': 50, 'good': 100, 'acceptable': 200},
            'cpu_usage': {'excellent': 30, 'good': 50, 'acceptable': 80},
            'network_latency': {'excellent': 50, 'good': 100, 'acceptable': 200},
            'error_rate': {'excellent': 0.1, 'good': 1.0, 'acceptable': 5.0},
            'availability': {'excellent': 99.9, 'good': 99.5, 'acceptable': 99.0}
        }
    
    def add_performance_data(self, data: PerformanceData) -> None:
        """
        添加性能数据
        
        Args:
            data: 性能数据
        """
        self.performance_history.append(data)
        
        # 保持历史数据在合理范围内（最近1000条记录）
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
    
    def calculate_performance_score(self, data: PerformanceData) -> PerformanceScore:
        """
        计算性能分数
        
        Args:
            data: 性能数据
            
        Returns:
            PerformanceScore: 性能分数
        """
        # 计算各项分数
        response_time_score = self._calculate_time_score(
            data.response_time, self.thresholds['response_time']
        )
        
        load_time_score = self._calculate_time_score(
            data.load_time, self.thresholds['load_time']
        )
        
        render_time_score = self._calculate_time_score(
            data.render_time, self.thresholds['render_time']
        )
        
        # 资源使用分数（内存和CPU的综合）
        memory_score = self._calculate_resource_score(
            data.memory_usage, self.thresholds['memory_usage']
        )
        cpu_score = self._calculate_resource_score(
            data.cpu_usage, self.thresholds['cpu_usage']
        )
        resource_usage_score = (memory_score + cpu_score) / 2
        
        # 可靠性分数（错误率和可用性的综合）
        error_rate_score = self._calculate_error_rate_score(
            data.error_rate, self.thresholds['error_rate']
        )
        availability_score = self._calculate_availability_score(
            data.availability, self.thresholds['availability']
        )
        reliability_score = (error_rate_score + availability_score) / 2
        
        # 效率分数（吞吐量和网络延迟的综合）
        throughput_score = min(data.throughput / 100, 1.0)  # 假设100 req/s为满分
        latency_score = self._calculate_latency_score(
            data.network_latency, self.thresholds['network_latency']
        )
        efficiency_score = (throughput_score + latency_score) / 2
        
        # 计算总体分数（加权平均）
        weights = {
            'response_time': 0.25,
            'load_time': 0.20,
            'render_time': 0.15,
            'resource_usage': 0.15,
            'reliability': 0.15,
            'efficiency': 0.10
        }
        
        overall_score = (
            response_time_score * weights['response_time'] +
            load_time_score * weights['load_time'] +
            render_time_score * weights['render_time'] +
            resource_usage_score * weights['resource_usage'] +
            reliability_score * weights['reliability'] +
            efficiency_score * weights['efficiency']
        )
        
        # 详细信息
        details = {
            'weights': weights,
            'raw_metrics': {
                'response_time': data.response_time,
                'load_time': data.load_time,
                'render_time': data.render_time,
                'memory_usage': data.memory_usage,
                'cpu_usage': data.cpu_usage,
                'network_latency': data.network_latency,
                'throughput': data.throughput,
                'error_rate': data.error_rate,
                'availability': data.availability
            },
            'individual_scores': {
                'memory_score': memory_score,
                'cpu_score': cpu_score,
                'error_rate_score': error_rate_score,
                'availability_score': availability_score,
                'throughput_score': throughput_score,
                'latency_score': latency_score
            }
        }
        
        return PerformanceScore(
            overall_score=overall_score,
            response_time_score=response_time_score,
            load_time_score=load_time_score,
            render_time_score=render_time_score,
            resource_usage_score=resource_usage_score,
            reliability_score=reliability_score,
            efficiency_score=efficiency_score,
            details=details
        )
    
    def calculate_performance_trends(self, days: int = 7) -> List[PerformanceTrend]:
        """
        计算性能趋势
        
        Args:
            days: 分析天数
            
        Returns:
            List[PerformanceTrend]: 性能趋势列表
        """
        if len(self.performance_history) < 2:
            return []
        
        # 获取指定天数内的数据
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_data = [
            data for data in self.performance_history
            if data.timestamp >= cutoff_time
        ]
        
        if len(recent_data) < 2:
            return []
        
        trends = []
        
        # 分析各项指标的趋势
        metrics = [
            'response_time', 'load_time', 'render_time',
            'memory_usage', 'cpu_usage', 'network_latency',
            'throughput', 'error_rate', 'availability'
        ]
        
        for metric in metrics:
            values = [getattr(data, metric) for data in recent_data]
            timestamps = [data.timestamp.timestamp() for data in recent_data]
            
            trend = self._calculate_trend(metric, values, timestamps)
            if trend:
                trends.append(trend)
        
        return trends
    
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        获取性能摘要
        
        Args:
            days: 分析天数
            
        Returns:
            Dict[str, Any]: 性能摘要
        """
        if not self.performance_history:
            return {}
        
        # 获取指定天数内的数据
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_data = [
            data for data in self.performance_history
            if data.timestamp >= cutoff_time
        ]
        
        if not recent_data:
            return {}
        
        # 计算统计信息
        response_times = [data.response_time for data in recent_data]
        load_times = [data.load_time for data in recent_data]
        render_times = [data.render_time for data in recent_data]
        memory_usage = [data.memory_usage for data in recent_data]
        cpu_usage = [data.cpu_usage for data in recent_data]
        
        # 计算最新分数
        latest_score = self.calculate_performance_score(recent_data[-1])
        
        # 计算趋势
        trends = self.calculate_performance_trends(days)
        
        return {
            'period': f"最近{days}天",
            'data_points': len(recent_data),
            'latest_score': latest_score,
            'statistics': {
                'response_time': {
                    'avg': statistics.mean(response_times),
                    'min': min(response_times),
                    'max': max(response_times),
                    'p95': self._percentile(response_times, 95),
                    'p99': self._percentile(response_times, 99)
                },
                'load_time': {
                    'avg': statistics.mean(load_times),
                    'min': min(load_times),
                    'max': max(load_times),
                    'p95': self._percentile(load_times, 95),
                    'p99': self._percentile(load_times, 99)
                },
                'render_time': {
                    'avg': statistics.mean(render_times),
                    'min': min(render_times),
                    'max': max(render_times),
                    'p95': self._percentile(render_times, 95),
                    'p99': self._percentile(render_times, 99)
                },
                'memory_usage': {
                    'avg': statistics.mean(memory_usage),
                    'min': min(memory_usage),
                    'max': max(memory_usage),
                    'p95': self._percentile(memory_usage, 95),
                    'p99': self._percentile(memory_usage, 99)
                },
                'cpu_usage': {
                    'avg': statistics.mean(cpu_usage),
                    'min': min(cpu_usage),
                    'max': max(cpu_usage),
                    'p95': self._percentile(cpu_usage, 95),
                    'p99': self._percentile(cpu_usage, 99)
                }
            },
            'trends': trends,
            'alerts': self._generate_performance_alerts(recent_data[-1])
        }
    
    def set_baseline(self, data: PerformanceData) -> None:
        """
        设置基线指标
        
        Args:
            data: 基线性能数据
        """
        self.baseline_metrics = {
            'response_time': data.response_time,
            'load_time': data.load_time,
            'render_time': data.render_time,
            'memory_usage': data.memory_usage,
            'cpu_usage': data.cpu_usage,
            'network_latency': data.network_latency,
            'throughput': data.throughput,
            'error_rate': data.error_rate,
            'availability': data.availability
        }
    
    def compare_with_baseline(self, data: PerformanceData) -> Dict[str, float]:
        """
        与基线比较
        
        Args:
            data: 当前性能数据
            
        Returns:
            Dict[str, float]: 与基线的差异百分比
        """
        if not self.baseline_metrics:
            return {}
        
        comparison = {}
        
        for metric, baseline_value in self.baseline_metrics.items():
            if baseline_value > 0:
                current_value = getattr(data, metric)
                # 对于错误率，值越小越好；对于其他指标，需要具体分析
                if metric in ['error_rate', 'response_time', 'load_time', 'render_time', 'memory_usage', 'cpu_usage', 'network_latency']:
                    # 值越小越好的指标
                    change_percent = ((current_value - baseline_value) / baseline_value) * 100
                else:
                    # 值越大越好的指标（如throughput, availability）
                    change_percent = ((current_value - baseline_value) / baseline_value) * 100
                
                comparison[metric] = change_percent
        
        return comparison
    
    def _calculate_time_score(self, value: float, thresholds: Dict[str, float]) -> float:
        """计算时间相关指标分数（值越小越好）"""
        if value <= thresholds['excellent']:
            return 1.0
        elif value <= thresholds['good']:
            # 在excellent和good之间线性插值
            ratio = (value - thresholds['excellent']) / (thresholds['good'] - thresholds['excellent'])
            return 1.0 - ratio * 0.2  # 从1.0降到0.8
        elif value <= thresholds['acceptable']:
            # 在good和acceptable之间线性插值
            ratio = (value - thresholds['good']) / (thresholds['acceptable'] - thresholds['good'])
            return 0.8 - ratio * 0.3  # 从0.8降到0.5
        else:
            # 超过acceptable阈值，分数快速下降
            excess_ratio = min((value - thresholds['acceptable']) / thresholds['acceptable'], 2.0)
            return max(0.5 - excess_ratio * 0.25, 0.0)  # 最低0分
    
    def _calculate_resource_score(self, value: float, thresholds: Dict[str, float]) -> float:
        """计算资源使用指标分数（值越小越好）"""
        return self._calculate_time_score(value, thresholds)
    
    def _calculate_error_rate_score(self, value: float, thresholds: Dict[str, float]) -> float:
        """计算错误率分数（值越小越好）"""
        return self._calculate_time_score(value, thresholds)
    
    def _calculate_availability_score(self, value: float, thresholds: Dict[str, float]) -> float:
        """计算可用性分数（值越大越好）"""
        if value >= thresholds['excellent']:
            return 1.0
        elif value >= thresholds['good']:
            # 在good和excellent之间线性插值
            ratio = (thresholds['excellent'] - value) / (thresholds['excellent'] - thresholds['good'])
            return 1.0 - ratio * 0.2  # 从1.0降到0.8
        elif value >= thresholds['acceptable']:
            # 在acceptable和good之间线性插值
            ratio = (thresholds['good'] - value) / (thresholds['good'] - thresholds['acceptable'])
            return 0.8 - ratio * 0.3  # 从0.8降到0.5
        else:
            # 低于acceptable阈值，分数快速下降
            deficit_ratio = min((thresholds['acceptable'] - value) / thresholds['acceptable'], 2.0)
            return max(0.5 - deficit_ratio * 0.25, 0.0)  # 最低0分
    
    def _calculate_latency_score(self, value: float, thresholds: Dict[str, float]) -> float:
        """计算延迟分数（值越小越好）"""
        return self._calculate_time_score(value, thresholds)
    
    def _calculate_trend(self, metric_name: str, values: List[float], timestamps: List[float]) -> Optional[PerformanceTrend]:
        """计算趋势"""
        if len(values) < 2:
            return None
        
        try:
            # 简单线性回归
            n = len(values)
            sum_x = sum(timestamps)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(timestamps, values))
            sum_x2 = sum(x * x for x in timestamps)
            
            # 计算斜率和截距
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # 计算相关系数
            mean_x = sum_x / n
            mean_y = sum_y / n
            
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(timestamps, values))
            denominator_x = sum((x - mean_x) ** 2 for x in timestamps)
            denominator_y = sum((y - mean_y) ** 2 for y in values)
            
            if denominator_x > 0 and denominator_y > 0:
                correlation = numerator / (denominator_x * denominator_y) ** 0.5
            else:
                correlation = 0.0
            
            # 确定趋势方向
            if abs(slope) < 0.001:  # 几乎没有变化
                trend_direction = "stable"
                trend_strength = 0.0
            elif slope > 0:
                # 对于错误率、响应时间等，增长是坏事
                if metric_name in ['error_rate', 'response_time', 'load_time', 'render_time', 'memory_usage', 'cpu_usage', 'network_latency']:
                    trend_direction = "declining"
                else:
                    trend_direction = "improving"
                trend_strength = min(abs(correlation), 1.0)
            else:
                # 对于错误率、响应时间等，下降是好事
                if metric_name in ['error_rate', 'response_time', 'load_time', 'render_time', 'memory_usage', 'cpu_usage', 'network_latency']:
                    trend_direction = "improving"
                else:
                    trend_direction = "declining"
                trend_strength = min(abs(correlation), 1.0)
            
            # 预测下一个值
            next_timestamp = timestamps[-1] + (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)
            prediction = slope * next_timestamp + intercept
            
            return PerformanceTrend(
                metric_name=metric_name,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                slope=slope,
                correlation=correlation,
                prediction=prediction,
                confidence=abs(correlation)
            )
            
        except (ZeroDivisionError, ValueError):
            return None
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            
            if upper_index < len(sorted_values):
                return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
            else:
                return sorted_values[lower_index]
    
    def _generate_performance_alerts(self, data: PerformanceData) -> List[Dict[str, Any]]:
        """生成性能告警"""
        alerts = []
        
        # 检查各项指标是否超过阈值
        if data.response_time > self.thresholds['response_time']['acceptable']:
            alerts.append({
                'type': 'performance',
                'severity': 'high',
                'metric': 'response_time',
                'value': data.response_time,
                'threshold': self.thresholds['response_time']['acceptable'],
                'message': f"响应时间过长: {data.response_time:.2f}s (阈值: {self.thresholds['response_time']['acceptable']}s)"
            })
        
        if data.load_time > self.thresholds['load_time']['acceptable']:
            alerts.append({
                'type': 'performance',
                'severity': 'high',
                'metric': 'load_time',
                'value': data.load_time,
                'threshold': self.thresholds['load_time']['acceptable'],
                'message': f"加载时间过长: {data.load_time:.2f}s (阈值: {self.thresholds['load_time']['acceptable']}s)"
            })
        
        if data.memory_usage > self.thresholds['memory_usage']['acceptable']:
            alerts.append({
                'type': 'resource',
                'severity': 'medium',
                'metric': 'memory_usage',
                'value': data.memory_usage,
                'threshold': self.thresholds['memory_usage']['acceptable'],
                'message': f"内存使用过高: {data.memory_usage:.1f}MB (阈值: {self.thresholds['memory_usage']['acceptable']}MB)"
            })
        
        if data.cpu_usage > self.thresholds['cpu_usage']['acceptable']:
            alerts.append({
                'type': 'resource',
                'severity': 'medium',
                'metric': 'cpu_usage',
                'value': data.cpu_usage,
                'threshold': self.thresholds['cpu_usage']['acceptable'],
                'message': f"CPU使用率过高: {data.cpu_usage:.1f}% (阈值: {self.thresholds['cpu_usage']['acceptable']}%)"
            })
        
        if data.error_rate > self.thresholds['error_rate']['acceptable']:
            alerts.append({
                'type': 'reliability',
                'severity': 'high',
                'metric': 'error_rate',
                'value': data.error_rate,
                'threshold': self.thresholds['error_rate']['acceptable'],
                'message': f"错误率过高: {data.error_rate:.2f}% (阈值: {self.thresholds['error_rate']['acceptable']}%)"
            })
        
        if data.availability < self.thresholds['availability']['acceptable']:
            alerts.append({
                'type': 'reliability',
                'severity': 'critical',
                'metric': 'availability',
                'value': data.availability,
                'threshold': self.thresholds['availability']['acceptable'],
                'message': f"可用性过低: {data.availability:.2f}% (阈值: {self.thresholds['availability']['acceptable']}%)"
            })
        
        return alerts