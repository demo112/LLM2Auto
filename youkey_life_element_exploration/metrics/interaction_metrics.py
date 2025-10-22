"""
交互性指标计算模块

提供元素交互性相关的指标计算、分析和评估功能。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import statistics
import numpy as np
from enum import Enum


class InteractionType(Enum):
    """交互类型"""
    CLICK = "click"
    HOVER = "hover"
    FOCUS = "focus"
    SCROLL = "scroll"
    DRAG = "drag"
    TOUCH = "touch"
    KEYBOARD = "keyboard"
    GESTURE = "gesture"


class InteractionQuality(Enum):
    """交互质量等级"""
    EXCELLENT = "excellent"  # 优秀 (90-100)
    GOOD = "good"           # 良好 (70-89)
    FAIR = "fair"           # 一般 (50-69)
    POOR = "poor"           # 较差 (30-49)
    CRITICAL = "critical"   # 严重 (0-29)


@dataclass
class InteractionEvent:
    """交互事件数据"""
    timestamp: datetime
    element_id: str
    interaction_type: InteractionType
    
    # 响应时间指标
    response_time: float = 0.0  # 毫秒
    processing_time: float = 0.0  # 毫秒
    render_time: float = 0.0  # 毫秒
    
    # 交互成功性
    success: bool = True
    error_message: str = ""
    retry_count: int = 0
    
    # 用户体验指标
    user_satisfaction: float = 0.0  # 0-10评分
    ease_of_use: float = 0.0  # 0-10评分
    
    # 技术指标
    cpu_usage: float = 0.0  # 百分比
    memory_usage: float = 0.0  # MB
    network_latency: float = 0.0  # 毫秒
    
    # 交互上下文
    device_type: str = "desktop"  # desktop, mobile, tablet
    input_method: str = "mouse"  # mouse, touch, keyboard
    screen_size: Tuple[int, int] = (1920, 1080)
    
    # 可访问性相关
    keyboard_accessible: bool = True
    screen_reader_compatible: bool = True
    
    # 自定义属性
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InteractionData:
    """交互数据汇总"""
    timestamp: datetime
    element_id: str
    
    # 基础交互指标
    total_interactions: int = 0
    successful_interactions: int = 0
    failed_interactions: int = 0
    
    # 响应时间统计
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    p95_response_time: float = 0.0
    
    # 交互频率
    interactions_per_minute: float = 0.0
    peak_interaction_rate: float = 0.0
    
    # 用户体验指标
    avg_satisfaction: float = 0.0
    avg_ease_of_use: float = 0.0
    bounce_rate: float = 0.0  # 快速离开率
    
    # 错误统计
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    retry_rate: float = 0.0
    
    # 性能指标
    avg_cpu_usage: float = 0.0
    avg_memory_usage: float = 0.0
    avg_network_latency: float = 0.0
    
    # 可访问性指标
    keyboard_usage_rate: float = 0.0
    screen_reader_usage_rate: float = 0.0
    
    # 设备分布
    device_distribution: Dict[str, int] = field(default_factory=dict)
    input_method_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class InteractionScore:
    """交互性评分"""
    overall_score: float
    quality: InteractionQuality
    details: Dict[str, float] = field(default_factory=dict)
    percentage: float = 0.0
    grade: str = ""
    
    def __post_init__(self):
        self.percentage = self.overall_score
        if self.overall_score >= 90:
            self.grade = "A+"
            self.quality = InteractionQuality.EXCELLENT
        elif self.overall_score >= 80:
            self.grade = "A"
            self.quality = InteractionQuality.GOOD
        elif self.overall_score >= 70:
            self.grade = "B"
            self.quality = InteractionQuality.GOOD
        elif self.overall_score >= 60:
            self.grade = "C"
            self.quality = InteractionQuality.FAIR
        elif self.overall_score >= 50:
            self.grade = "D"
            self.quality = InteractionQuality.FAIR
        else:
            self.grade = "F"
            self.quality = InteractionQuality.POOR


@dataclass
class InteractionTrend:
    """交互性趋势分析"""
    element_id: str
    period_days: int
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # 0-1, 趋势强度
    average_score: float
    score_variance: float
    improvement_rate: float  # 每天的改进率
    regression_slope: float
    regression_r_squared: float
    
    # 具体趋势指标
    response_time_trend: str
    success_rate_trend: str
    satisfaction_trend: str
    
    recommendations: List[str] = field(default_factory=list)


class InteractionMetrics:
    """交互性指标计算器"""
    
    def __init__(self):
        self.interaction_events: Dict[str, List[InteractionEvent]] = {}
        self.interaction_data: Dict[str, List[InteractionData]] = {}
        self.baseline_scores: Dict[str, InteractionScore] = {}
        
        # 交互性权重配置
        self.weights = {
            'responsiveness': 0.25,      # 响应性
            'reliability': 0.20,         # 可靠性
            'user_experience': 0.20,     # 用户体验
            'performance': 0.15,         # 性能
            'accessibility': 0.10,       # 可访问性
            'frequency': 0.10           # 交互频率
        }
        
        # 评分阈值
        self.thresholds = {
            'response_time_excellent': 100,    # 毫秒
            'response_time_good': 300,         # 毫秒
            'response_time_poor': 1000,        # 毫秒
            'success_rate_excellent': 0.99,    # 99%
            'success_rate_good': 0.95,         # 95%
            'success_rate_poor': 0.90,         # 90%
            'satisfaction_excellent': 8.0,     # 8/10
            'satisfaction_good': 6.0,          # 6/10
            'satisfaction_poor': 4.0           # 4/10
        }
    
    def add_interaction_event(self, event: InteractionEvent) -> None:
        """添加交互事件"""
        if event.element_id not in self.interaction_events:
            self.interaction_events[event.element_id] = []
        self.interaction_events[event.element_id].append(event)
    
    def calculate_interaction_data(self, element_id: str, time_window: timedelta = timedelta(hours=1)) -> Optional[InteractionData]:
        """计算指定时间窗口内的交互数据"""
        if element_id not in self.interaction_events:
            return None
        
        now = datetime.now()
        cutoff_time = now - time_window
        
        # 获取时间窗口内的事件
        recent_events = [
            event for event in self.interaction_events[element_id]
            if event.timestamp >= cutoff_time
        ]
        
        if not recent_events:
            return None
        
        # 计算基础统计
        total_interactions = len(recent_events)
        successful_interactions = sum(1 for event in recent_events if event.success)
        failed_interactions = total_interactions - successful_interactions
        
        # 响应时间统计
        response_times = [event.response_time for event in recent_events if event.response_time > 0]
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = np.percentile(response_times, 95)
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = 0.0
        
        # 交互频率
        time_span_minutes = time_window.total_seconds() / 60
        interactions_per_minute = total_interactions / time_span_minutes if time_span_minutes > 0 else 0
        
        # 用户体验指标
        satisfaction_scores = [event.user_satisfaction for event in recent_events if event.user_satisfaction > 0]
        ease_scores = [event.ease_of_use for event in recent_events if event.ease_of_use > 0]
        
        avg_satisfaction = statistics.mean(satisfaction_scores) if satisfaction_scores else 0.0
        avg_ease_of_use = statistics.mean(ease_scores) if ease_scores else 0.0
        
        # 错误统计
        error_rate = failed_interactions / total_interactions if total_interactions > 0 else 0.0
        retry_events = [event for event in recent_events if event.retry_count > 0]
        retry_rate = len(retry_events) / total_interactions if total_interactions > 0 else 0.0
        
        # 性能指标
        cpu_usages = [event.cpu_usage for event in recent_events if event.cpu_usage > 0]
        memory_usages = [event.memory_usage for event in recent_events if event.memory_usage > 0]
        network_latencies = [event.network_latency for event in recent_events if event.network_latency > 0]
        
        avg_cpu_usage = statistics.mean(cpu_usages) if cpu_usages else 0.0
        avg_memory_usage = statistics.mean(memory_usages) if memory_usages else 0.0
        avg_network_latency = statistics.mean(network_latencies) if network_latencies else 0.0
        
        # 可访问性指标
        keyboard_events = sum(1 for event in recent_events if event.input_method == "keyboard")
        keyboard_usage_rate = keyboard_events / total_interactions if total_interactions > 0 else 0.0
        
        screen_reader_events = sum(1 for event in recent_events if event.screen_reader_compatible)
        screen_reader_usage_rate = screen_reader_events / total_interactions if total_interactions > 0 else 0.0
        
        # 设备分布
        device_distribution = {}
        input_method_distribution = {}
        for event in recent_events:
            device_distribution[event.device_type] = device_distribution.get(event.device_type, 0) + 1
            input_method_distribution[event.input_method] = input_method_distribution.get(event.input_method, 0) + 1
        
        return InteractionData(
            timestamp=now,
            element_id=element_id,
            total_interactions=total_interactions,
            successful_interactions=successful_interactions,
            failed_interactions=failed_interactions,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            interactions_per_minute=interactions_per_minute,
            avg_satisfaction=avg_satisfaction,
            avg_ease_of_use=avg_ease_of_use,
            error_rate=error_rate,
            retry_rate=retry_rate,
            avg_cpu_usage=avg_cpu_usage,
            avg_memory_usage=avg_memory_usage,
            avg_network_latency=avg_network_latency,
            keyboard_usage_rate=keyboard_usage_rate,
            screen_reader_usage_rate=screen_reader_usage_rate,
            device_distribution=device_distribution,
            input_method_distribution=input_method_distribution
        )
    
    def add_interaction_data(self, data: InteractionData) -> None:
        """添加交互数据"""
        if data.element_id not in self.interaction_data:
            self.interaction_data[data.element_id] = []
        self.interaction_data[data.element_id].append(data)
    
    def calculate_interaction_score(self, element_id: str) -> Optional[InteractionScore]:
        """计算交互性评分"""
        # 首先尝试计算最新的交互数据
        latest_data = self.calculate_interaction_data(element_id)
        if latest_data:
            self.add_interaction_data(latest_data)
        
        if element_id not in self.interaction_data or not self.interaction_data[element_id]:
            return None
        
        data = self.interaction_data[element_id][-1]
        
        # 计算各项评分
        responsiveness_score = self._calculate_responsiveness_score(data)
        reliability_score = self._calculate_reliability_score(data)
        user_experience_score = self._calculate_user_experience_score(data)
        performance_score = self._calculate_performance_score(data)
        accessibility_score = self._calculate_accessibility_score(data)
        frequency_score = self._calculate_frequency_score(data)
        
        # 计算加权总分
        overall_score = (
            responsiveness_score * self.weights['responsiveness'] +
            reliability_score * self.weights['reliability'] +
            user_experience_score * self.weights['user_experience'] +
            performance_score * self.weights['performance'] +
            accessibility_score * self.weights['accessibility'] +
            frequency_score * self.weights['frequency']
        )
        
        details = {
            'responsiveness': responsiveness_score,
            'reliability': reliability_score,
            'user_experience': user_experience_score,
            'performance': performance_score,
            'accessibility': accessibility_score,
            'frequency': frequency_score
        }
        
        return InteractionScore(
            overall_score=overall_score,
            quality=InteractionQuality.FAIR,  # 将在__post_init__中重新计算
            details=details
        )
    
    def _calculate_responsiveness_score(self, data: InteractionData) -> float:
        """计算响应性评分"""
        if data.avg_response_time <= 0:
            return 50.0  # 默认中等分数
        
        if data.avg_response_time <= self.thresholds['response_time_excellent']:
            return 100.0
        elif data.avg_response_time <= self.thresholds['response_time_good']:
            return 80.0
        elif data.avg_response_time <= self.thresholds['response_time_poor']:
            return 60.0
        else:
            return 30.0
    
    def _calculate_reliability_score(self, data: InteractionData) -> float:
        """计算可靠性评分"""
        if data.total_interactions == 0:
            return 50.0
        
        success_rate = data.successful_interactions / data.total_interactions
        
        if success_rate >= self.thresholds['success_rate_excellent']:
            return 100.0
        elif success_rate >= self.thresholds['success_rate_good']:
            return 80.0
        elif success_rate >= self.thresholds['success_rate_poor']:
            return 60.0
        else:
            return 30.0
    
    def _calculate_user_experience_score(self, data: InteractionData) -> float:
        """计算用户体验评分"""
        if data.avg_satisfaction <= 0:
            return 50.0
        
        if data.avg_satisfaction >= self.thresholds['satisfaction_excellent']:
            return 100.0
        elif data.avg_satisfaction >= self.thresholds['satisfaction_good']:
            return 80.0
        elif data.avg_satisfaction >= self.thresholds['satisfaction_poor']:
            return 60.0
        else:
            return 30.0
    
    def _calculate_performance_score(self, data: InteractionData) -> float:
        """计算性能评分"""
        score = 100.0
        
        # CPU使用率评分
        if data.avg_cpu_usage > 80:
            score -= 30
        elif data.avg_cpu_usage > 60:
            score -= 20
        elif data.avg_cpu_usage > 40:
            score -= 10
        
        # 内存使用评分
        if data.avg_memory_usage > 500:  # MB
            score -= 20
        elif data.avg_memory_usage > 200:
            score -= 10
        
        # 网络延迟评分
        if data.avg_network_latency > 500:  # 毫秒
            score -= 20
        elif data.avg_network_latency > 200:
            score -= 10
        
        return max(score, 0.0)
    
    def _calculate_accessibility_score(self, data: InteractionData) -> float:
        """计算可访问性评分"""
        score = 0.0
        
        # 键盘使用率评分
        if data.keyboard_usage_rate >= 0.3:
            score += 50.0
        elif data.keyboard_usage_rate >= 0.1:
            score += 30.0
        else:
            score += 10.0
        
        # 屏幕阅读器兼容性评分
        if data.screen_reader_usage_rate >= 0.8:
            score += 50.0
        elif data.screen_reader_usage_rate >= 0.5:
            score += 30.0
        else:
            score += 10.0
        
        return score
    
    def _calculate_frequency_score(self, data: InteractionData) -> float:
        """计算交互频率评分"""
        # 适中的交互频率是最好的
        if 1.0 <= data.interactions_per_minute <= 5.0:
            return 100.0
        elif 0.5 <= data.interactions_per_minute <= 10.0:
            return 80.0
        elif 0.1 <= data.interactions_per_minute <= 20.0:
            return 60.0
        else:
            return 30.0
    
    def analyze_interaction_trend(self, element_id: str, days: int = 7) -> Optional[InteractionTrend]:
        """分析交互性趋势"""
        if element_id not in self.interaction_data:
            return None
        
        data_points = self.interaction_data[element_id]
        if len(data_points) < 2:
            return None
        
        # 获取指定天数内的数据
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_data = [d for d in data_points if d.timestamp >= cutoff_time]
        
        if len(recent_data) < 2:
            return None
        
        # 计算评分序列
        scores = []
        for data in recent_data:
            temp_data = {element_id: [data]}
            old_data = self.interaction_data[element_id]
            self.interaction_data[element_id] = [data]
            score = self.calculate_interaction_score(element_id)
            self.interaction_data[element_id] = old_data
            if score:
                scores.append(score.overall_score)
        
        if len(scores) < 2:
            return None
        
        # 趋势分析
        x = np.arange(len(scores))
        slope, intercept = np.polyfit(x, scores, 1)
        r_squared = np.corrcoef(x, scores)[0, 1] ** 2
        
        # 确定趋势方向
        if abs(slope) < 0.5:
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "improving"
        else:
            trend_direction = "declining"
        
        # 计算统计信息
        avg_score = statistics.mean(scores)
        score_variance = statistics.variance(scores) if len(scores) > 1 else 0
        improvement_rate = slope
        trend_strength = min(abs(slope) / 10.0, 1.0)
        
        # 分析具体指标趋势
        response_times = [d.avg_response_time for d in recent_data]
        success_rates = [d.successful_interactions / max(d.total_interactions, 1) for d in recent_data]
        satisfactions = [d.avg_satisfaction for d in recent_data]
        
        response_time_trend = self._analyze_metric_trend(response_times, reverse=True)
        success_rate_trend = self._analyze_metric_trend(success_rates)
        satisfaction_trend = self._analyze_metric_trend(satisfactions)
        
        # 生成建议
        recommendations = self._generate_interaction_recommendations(recent_data[-1], avg_score)
        
        return InteractionTrend(
            element_id=element_id,
            period_days=days,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            average_score=avg_score,
            score_variance=score_variance,
            improvement_rate=improvement_rate,
            regression_slope=slope,
            regression_r_squared=r_squared,
            response_time_trend=response_time_trend,
            success_rate_trend=success_rate_trend,
            satisfaction_trend=satisfaction_trend,
            recommendations=recommendations
        )
    
    def _analyze_metric_trend(self, values: List[float], reverse: bool = False) -> str:
        """分析单个指标的趋势"""
        if len(values) < 2:
            return "stable"
        
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        if reverse:
            slope = -slope  # 对于响应时间等，下降是好的
        
        if abs(slope) < 0.01:
            return "stable"
        elif slope > 0:
            return "improving"
        else:
            return "declining"
    
    def _generate_interaction_recommendations(self, data: InteractionData, avg_score: float) -> List[str]:
        """生成交互性改进建议"""
        recommendations = []
        
        # 响应时间建议
        if data.avg_response_time > self.thresholds['response_time_poor']:
            recommendations.append("优化响应时间，目标控制在300ms以内")
        
        # 可靠性建议
        if data.error_rate > 0.1:
            recommendations.append("降低错误率，提高交互可靠性")
        
        # 用户体验建议
        if data.avg_satisfaction < self.thresholds['satisfaction_good']:
            recommendations.append("改善用户体验，提高满意度评分")
        
        # 性能建议
        if data.avg_cpu_usage > 60:
            recommendations.append("优化CPU使用率，减少资源消耗")
        if data.avg_memory_usage > 200:
            recommendations.append("优化内存使用，避免内存泄漏")
        
        # 可访问性建议
        if data.keyboard_usage_rate < 0.1:
            recommendations.append("提高键盘可访问性支持")
        if data.screen_reader_usage_rate < 0.5:
            recommendations.append("改善屏幕阅读器兼容性")
        
        # 交互频率建议
        if data.interactions_per_minute > 10:
            recommendations.append("交互频率过高，考虑简化操作流程")
        elif data.interactions_per_minute < 0.5:
            recommendations.append("交互频率过低，可能存在可用性问题")
        
        return recommendations
    
    def get_interaction_summary(self, element_id: str) -> Dict[str, Any]:
        """获取交互性摘要"""
        if element_id not in self.interaction_data and element_id not in self.interaction_events:
            return {}
        
        current_score = self.calculate_interaction_score(element_id)
        trend = self.analyze_interaction_trend(element_id)
        
        summary = {
            'element_id': element_id,
            'current_score': current_score.overall_score if current_score else 0,
            'interaction_quality': current_score.quality.value if current_score else 'unknown',
            'grade': current_score.grade if current_score else 'N/A'
        }
        
        if element_id in self.interaction_events:
            summary['total_events'] = len(self.interaction_events[element_id])
        
        if element_id in self.interaction_data:
            summary['data_points'] = len(self.interaction_data[element_id])
            summary['last_updated'] = self.interaction_data[element_id][-1].timestamp.isoformat()
        
        if trend:
            summary.update({
                'trend_direction': trend.trend_direction,
                'trend_strength': trend.trend_strength,
                'improvement_rate': trend.improvement_rate,
                'response_time_trend': trend.response_time_trend,
                'success_rate_trend': trend.success_rate_trend,
                'satisfaction_trend': trend.satisfaction_trend,
                'recommendations': trend.recommendations
            })
        
        if current_score:
            summary['score_breakdown'] = current_score.details
        
        return summary
    
    def set_baseline(self, element_id: str) -> bool:
        """设置基线交互性评分"""
        score = self.calculate_interaction_score(element_id)
        if score:
            self.baseline_scores[element_id] = score
            return True
        return False
    
    def compare_with_baseline(self, element_id: str) -> Optional[Dict[str, Any]]:
        """与基线进行比较"""
        if element_id not in self.baseline_scores:
            return None
        
        current_score = self.calculate_interaction_score(element_id)
        if not current_score:
            return None
        
        baseline = self.baseline_scores[element_id]
        
        return {
            'baseline_score': baseline.overall_score,
            'current_score': current_score.overall_score,
            'improvement': current_score.overall_score - baseline.overall_score,
            'improvement_percentage': ((current_score.overall_score - baseline.overall_score) / baseline.overall_score) * 100,
            'quality_change': f"{baseline.quality.value} -> {current_score.quality.value}",
            'grade_change': f"{baseline.grade} -> {current_score.grade}"
        }