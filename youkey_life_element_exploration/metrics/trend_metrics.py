"""
趋势分析指标模块

提供综合的趋势分析、预测和模式识别功能。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import statistics
import numpy as np
from enum import Enum
import json


class TrendDirection(Enum):
    """趋势方向"""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


class TrendStrength(Enum):
    """趋势强度"""
    VERY_STRONG = "very_strong"    # 0.8-1.0
    STRONG = "strong"              # 0.6-0.8
    MODERATE = "moderate"          # 0.4-0.6
    WEAK = "weak"                  # 0.2-0.4
    VERY_WEAK = "very_weak"        # 0.0-0.2


class SeasonalityType(Enum):
    """季节性类型"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    NONE = "none"


@dataclass
class TrendPoint:
    """趋势数据点"""
    timestamp: datetime
    value: float
    metric_name: str
    element_id: str
    confidence: float = 1.0  # 数据置信度
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    element_id: str
    metric_name: str
    period_start: datetime
    period_end: datetime
    
    # 基础趋势信息
    direction: TrendDirection
    strength: TrendStrength
    slope: float
    r_squared: float
    
    # 统计信息
    mean_value: float
    median_value: float
    std_deviation: float
    min_value: float
    max_value: float
    
    # 变化信息
    total_change: float
    percentage_change: float
    change_rate: float  # 每单位时间的变化率
    
    # 预测信息
    predicted_next_value: float
    prediction_confidence: float
    
    # 模式识别
    seasonality: SeasonalityType
    cycle_length: Optional[int] = None
    anomaly_count: int = 0
    
    # 质量评估
    data_quality_score: float = 1.0
    missing_data_percentage: float = 0.0
    
    recommendations: List[str] = field(default_factory=list)


@dataclass
class MultiMetricTrend:
    """多指标趋势分析"""
    element_id: str
    period_start: datetime
    period_end: datetime
    
    # 各指标趋势
    metric_trends: Dict[str, TrendAnalysis] = field(default_factory=dict)
    
    # 综合评估
    overall_direction: TrendDirection = TrendDirection.UNKNOWN
    overall_strength: TrendStrength = TrendStrength.VERY_WEAK
    overall_score: float = 0.0
    
    # 相关性分析
    metric_correlations: Dict[Tuple[str, str], float] = field(default_factory=dict)
    
    # 主导因素
    dominant_metrics: List[str] = field(default_factory=list)
    
    # 预测
    predicted_overall_score: float = 0.0
    prediction_confidence: float = 0.0
    
    recommendations: List[str] = field(default_factory=list)


@dataclass
class TrendComparison:
    """趋势比较结果"""
    element_ids: List[str]
    metric_name: str
    period_start: datetime
    period_end: datetime
    
    # 比较结果
    best_performer: str
    worst_performer: str
    performance_ranking: List[Tuple[str, float]] = field(default_factory=list)
    
    # 统计比较
    mean_differences: Dict[str, float] = field(default_factory=dict)
    trend_similarities: Dict[Tuple[str, str], float] = field(default_factory=dict)
    
    # 聚类分析
    performance_clusters: Dict[str, List[str]] = field(default_factory=dict)
    
    insights: List[str] = field(default_factory=list)


class TrendMetrics:
    """趋势分析指标计算器"""
    
    def __init__(self):
        self.trend_data: Dict[str, Dict[str, List[TrendPoint]]] = {}  # element_id -> metric_name -> points
        self.trend_cache: Dict[str, TrendAnalysis] = {}
        
        # 分析配置
        self.config = {
            'min_data_points': 5,
            'outlier_threshold': 2.0,  # Z-score阈值
            'seasonality_min_cycles': 2,
            'prediction_window_ratio': 0.2,  # 预测窗口占历史数据的比例
            'correlation_threshold': 0.7,
            'trend_strength_thresholds': {
                TrendStrength.VERY_STRONG: 0.8,
                TrendStrength.STRONG: 0.6,
                TrendStrength.MODERATE: 0.4,
                TrendStrength.WEAK: 0.2
            }
        }
    
    def add_trend_point(self, point: TrendPoint) -> None:
        """添加趋势数据点"""
        if point.element_id not in self.trend_data:
            self.trend_data[point.element_id] = {}
        
        if point.metric_name not in self.trend_data[point.element_id]:
            self.trend_data[point.element_id][point.metric_name] = []
        
        self.trend_data[point.element_id][point.metric_name].append(point)
        
        # 按时间排序
        self.trend_data[point.element_id][point.metric_name].sort(key=lambda x: x.timestamp)
        
        # 清除相关缓存
        cache_key = f"{point.element_id}_{point.metric_name}"
        if cache_key in self.trend_cache:
            del self.trend_cache[cache_key]
    
    def analyze_trend(self, element_id: str, metric_name: str, 
                     period_days: Optional[int] = None) -> Optional[TrendAnalysis]:
        """分析单个指标的趋势"""
        cache_key = f"{element_id}_{metric_name}"
        
        # 检查缓存
        if cache_key in self.trend_cache:
            cached = self.trend_cache[cache_key]
            if period_days is None or (datetime.now() - cached.period_end).days <= 1:
                return cached
        
        if (element_id not in self.trend_data or 
            metric_name not in self.trend_data[element_id]):
            return None
        
        points = self.trend_data[element_id][metric_name]
        
        # 过滤时间范围
        if period_days:
            cutoff_time = datetime.now() - timedelta(days=period_days)
            points = [p for p in points if p.timestamp >= cutoff_time]
        
        if len(points) < self.config['min_data_points']:
            return None
        
        # 提取数值和时间
        values = [p.value for p in points]
        timestamps = [p.timestamp.timestamp() for p in points]
        
        # 基础统计
        mean_value = statistics.mean(values)
        median_value = statistics.median(values)
        std_deviation = statistics.stdev(values) if len(values) > 1 else 0.0
        min_value = min(values)
        max_value = max(values)
        
        # 趋势分析
        direction, strength, slope, r_squared = self._analyze_linear_trend(timestamps, values)
        
        # 变化分析
        total_change = values[-1] - values[0]
        percentage_change = (total_change / values[0] * 100) if values[0] != 0 else 0.0
        time_span = (timestamps[-1] - timestamps[0]) / (24 * 3600)  # 天数
        change_rate = total_change / time_span if time_span > 0 else 0.0
        
        # 预测
        predicted_next_value, prediction_confidence = self._predict_next_value(timestamps, values)
        
        # 季节性分析
        seasonality, cycle_length = self._detect_seasonality(timestamps, values)
        
        # 异常检测
        anomaly_count = self._count_anomalies(values)
        
        # 数据质量评估
        data_quality_score, missing_percentage = self._assess_data_quality(points)
        
        # 生成建议
        recommendations = self._generate_trend_recommendations(
            direction, strength, values, anomaly_count
        )
        
        analysis = TrendAnalysis(
            element_id=element_id,
            metric_name=metric_name,
            period_start=points[0].timestamp,
            period_end=points[-1].timestamp,
            direction=direction,
            strength=strength,
            slope=slope,
            r_squared=r_squared,
            mean_value=mean_value,
            median_value=median_value,
            std_deviation=std_deviation,
            min_value=min_value,
            max_value=max_value,
            total_change=total_change,
            percentage_change=percentage_change,
            change_rate=change_rate,
            predicted_next_value=predicted_next_value,
            prediction_confidence=prediction_confidence,
            seasonality=seasonality,
            cycle_length=cycle_length,
            anomaly_count=anomaly_count,
            data_quality_score=data_quality_score,
            missing_data_percentage=missing_percentage,
            recommendations=recommendations
        )
        
        # 缓存结果
        self.trend_cache[cache_key] = analysis
        
        return analysis
    
    def _analyze_linear_trend(self, timestamps: List[float], values: List[float]) -> Tuple[TrendDirection, TrendStrength, float, float]:
        """分析线性趋势"""
        if len(values) < 2:
            return TrendDirection.UNKNOWN, TrendStrength.VERY_WEAK, 0.0, 0.0
        
        # 线性回归
        x = np.array(timestamps)
        y = np.array(values)
        
        # 标准化时间戳
        x_norm = (x - x[0]) / (x[-1] - x[0]) if x[-1] != x[0] else np.zeros_like(x)
        
        slope, intercept = np.polyfit(x_norm, y, 1)
        
        # 计算R²
        y_pred = slope * x_norm + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        
        # 确定趋势方向
        slope_threshold = np.std(y) * 0.1  # 相对于标准差的阈值
        
        if abs(slope) < slope_threshold:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.IMPROVING
        else:
            direction = TrendDirection.DECLINING
        
        # 检查波动性
        if np.std(y) > np.mean(y) * 0.5:  # 标准差大于均值的50%
            direction = TrendDirection.VOLATILE
        
        # 确定趋势强度
        strength_value = min(abs(r_squared), 1.0)
        
        if strength_value >= self.config['trend_strength_thresholds'][TrendStrength.VERY_STRONG]:
            strength = TrendStrength.VERY_STRONG
        elif strength_value >= self.config['trend_strength_thresholds'][TrendStrength.STRONG]:
            strength = TrendStrength.STRONG
        elif strength_value >= self.config['trend_strength_thresholds'][TrendStrength.MODERATE]:
            strength = TrendStrength.MODERATE
        elif strength_value >= self.config['trend_strength_thresholds'][TrendStrength.WEAK]:
            strength = TrendStrength.WEAK
        else:
            strength = TrendStrength.VERY_WEAK
        
        return direction, strength, slope, r_squared
    
    def _predict_next_value(self, timestamps: List[float], values: List[float]) -> Tuple[float, float]:
        """预测下一个值"""
        if len(values) < 3:
            return values[-1] if values else 0.0, 0.0
        
        # 使用线性回归预测
        x = np.array(timestamps)
        y = np.array(values)
        
        # 标准化
        x_norm = (x - x[0]) / (x[-1] - x[0]) if x[-1] != x[0] else np.zeros_like(x)
        
        slope, intercept = np.polyfit(x_norm, y, 1)
        
        # 预测下一个时间点
        next_x = 1.0 + (1.0 / len(x))  # 下一个标准化时间点
        predicted_value = slope * next_x + intercept
        
        # 计算预测置信度（基于R²和数据点数量）
        y_pred = slope * x_norm + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        
        confidence = r_squared * min(len(values) / 10.0, 1.0)  # 考虑数据点数量
        
        return predicted_value, confidence
    
    def _detect_seasonality(self, timestamps: List[float], values: List[float]) -> Tuple[SeasonalityType, Optional[int]]:
        """检测季节性模式"""
        if len(values) < 10:
            return SeasonalityType.NONE, None
        
        # 简化的季节性检测
        # 检查不同周期的自相关性
        periods_to_check = {
            SeasonalityType.DAILY: 24,      # 小时
            SeasonalityType.WEEKLY: 7,      # 天
            SeasonalityType.MONTHLY: 30,    # 天
            SeasonalityType.QUARTERLY: 90,  # 天
        }
        
        best_correlation = 0.0
        best_seasonality = SeasonalityType.NONE
        best_cycle_length = None
        
        for seasonality_type, period in periods_to_check.items():
            if len(values) >= period * self.config['seasonality_min_cycles']:
                correlation = self._calculate_autocorrelation(values, period)
                if correlation > best_correlation and correlation > 0.3:
                    best_correlation = correlation
                    best_seasonality = seasonality_type
                    best_cycle_length = period
        
        return best_seasonality, best_cycle_length
    
    def _calculate_autocorrelation(self, values: List[float], lag: int) -> float:
        """计算自相关性"""
        if len(values) <= lag:
            return 0.0
        
        n = len(values) - lag
        if n <= 0:
            return 0.0
        
        mean_val = np.mean(values)
        
        numerator = sum((values[i] - mean_val) * (values[i + lag] - mean_val) for i in range(n))
        denominator = sum((values[i] - mean_val) ** 2 for i in range(len(values)))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _count_anomalies(self, values: List[float]) -> int:
        """计算异常值数量"""
        if len(values) < 3:
            return 0
        
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if std_val == 0:
            return 0
        
        anomaly_count = 0
        for value in values:
            z_score = abs((value - mean_val) / std_val)
            if z_score > self.config['outlier_threshold']:
                anomaly_count += 1
        
        return anomaly_count
    
    def _assess_data_quality(self, points: List[TrendPoint]) -> Tuple[float, float]:
        """评估数据质量"""
        if not points:
            return 0.0, 100.0
        
        # 计算平均置信度
        avg_confidence = np.mean([p.confidence for p in points])
        
        # 检查数据连续性（简化版本）
        time_gaps = []
        for i in range(1, len(points)):
            gap = (points[i].timestamp - points[i-1].timestamp).total_seconds()
            time_gaps.append(gap)
        
        if time_gaps:
            avg_gap = np.mean(time_gaps)
            gap_variance = np.var(time_gaps)
            continuity_score = 1.0 / (1.0 + gap_variance / (avg_gap ** 2)) if avg_gap > 0 else 1.0
        else:
            continuity_score = 1.0
        
        # 综合质量评分
        quality_score = (avg_confidence + continuity_score) / 2.0
        
        # 缺失数据百分比（简化计算）
        missing_percentage = max(0.0, (1.0 - avg_confidence) * 100)
        
        return quality_score, missing_percentage
    
    def _generate_trend_recommendations(self, direction: TrendDirection, strength: TrendStrength, 
                                      values: List[float], anomaly_count: int) -> List[str]:
        """生成趋势改进建议"""
        recommendations = []
        
        if direction == TrendDirection.DECLINING:
            if strength in [TrendStrength.STRONG, TrendStrength.VERY_STRONG]:
                recommendations.append("指标呈强烈下降趋势，需要立即采取干预措施")
            else:
                recommendations.append("指标呈下降趋势，建议分析原因并制定改进计划")
        
        elif direction == TrendDirection.VOLATILE:
            recommendations.append("指标波动较大，建议稳定影响因素")
        
        elif direction == TrendDirection.STABLE:
            if np.mean(values) < 70:  # 假设70是一个基准分数
                recommendations.append("指标稳定但水平较低，可考虑优化提升")
        
        if anomaly_count > len(values) * 0.1:  # 异常值超过10%
            recommendations.append("存在较多异常值，建议检查数据质量和监控系统")
        
        if strength == TrendStrength.VERY_WEAK:
            recommendations.append("趋势不明显，建议增加数据收集频率或改进监控方法")
        
        return recommendations
    
    def analyze_multi_metric_trend(self, element_id: str, 
                                 metric_names: List[str], 
                                 period_days: Optional[int] = None) -> Optional[MultiMetricTrend]:
        """分析多指标综合趋势"""
        if element_id not in self.trend_data:
            return None
        
        # 分析各个指标
        metric_trends = {}
        valid_trends = []
        
        for metric_name in metric_names:
            trend = self.analyze_trend(element_id, metric_name, period_days)
            if trend:
                metric_trends[metric_name] = trend
                valid_trends.append(trend)
        
        if not valid_trends:
            return None
        
        # 计算综合评估
        overall_direction = self._calculate_overall_direction(valid_trends)
        overall_strength = self._calculate_overall_strength(valid_trends)
        overall_score = self._calculate_overall_score(valid_trends)
        
        # 相关性分析
        correlations = self._calculate_metric_correlations(element_id, metric_names)
        
        # 识别主导因素
        dominant_metrics = self._identify_dominant_metrics(valid_trends)
        
        # 综合预测
        predicted_score, prediction_confidence = self._predict_overall_score(valid_trends)
        
        # 生成综合建议
        recommendations = self._generate_multi_metric_recommendations(valid_trends, correlations)
        
        period_start = min(trend.period_start for trend in valid_trends)
        period_end = max(trend.period_end for trend in valid_trends)
        
        return MultiMetricTrend(
            element_id=element_id,
            period_start=period_start,
            period_end=period_end,
            metric_trends=metric_trends,
            overall_direction=overall_direction,
            overall_strength=overall_strength,
            overall_score=overall_score,
            metric_correlations=correlations,
            dominant_metrics=dominant_metrics,
            predicted_overall_score=predicted_score,
            prediction_confidence=prediction_confidence,
            recommendations=recommendations
        )
    
    def _calculate_overall_direction(self, trends: List[TrendAnalysis]) -> TrendDirection:
        """计算综合趋势方向"""
        direction_weights = {
            TrendDirection.IMPROVING: 1,
            TrendDirection.STABLE: 0,
            TrendDirection.DECLINING: -1,
            TrendDirection.VOLATILE: 0,
            TrendDirection.UNKNOWN: 0
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for trend in trends:
            strength_weight = self._get_strength_weight(trend.strength)
            weighted_sum += direction_weights[trend.direction] * strength_weight
            total_weight += strength_weight
        
        if total_weight == 0:
            return TrendDirection.UNKNOWN
        
        avg_direction = weighted_sum / total_weight
        
        if avg_direction > 0.3:
            return TrendDirection.IMPROVING
        elif avg_direction < -0.3:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.STABLE
    
    def _get_strength_weight(self, strength: TrendStrength) -> float:
        """获取趋势强度权重"""
        weights = {
            TrendStrength.VERY_STRONG: 1.0,
            TrendStrength.STRONG: 0.8,
            TrendStrength.MODERATE: 0.6,
            TrendStrength.WEAK: 0.4,
            TrendStrength.VERY_WEAK: 0.2
        }
        return weights.get(strength, 0.2)
    
    def _calculate_overall_strength(self, trends: List[TrendAnalysis]) -> TrendStrength:
        """计算综合趋势强度"""
        strength_values = [self._get_strength_weight(trend.strength) for trend in trends]
        avg_strength = np.mean(strength_values)
        
        if avg_strength >= 0.8:
            return TrendStrength.VERY_STRONG
        elif avg_strength >= 0.6:
            return TrendStrength.STRONG
        elif avg_strength >= 0.4:
            return TrendStrength.MODERATE
        elif avg_strength >= 0.2:
            return TrendStrength.WEAK
        else:
            return TrendStrength.VERY_WEAK
    
    def _calculate_overall_score(self, trends: List[TrendAnalysis]) -> float:
        """计算综合评分"""
        # 简化的综合评分计算
        scores = []
        for trend in trends:
            # 基于趋势方向和当前值计算评分
            base_score = trend.mean_value
            
            if trend.direction == TrendDirection.IMPROVING:
                base_score *= 1.1
            elif trend.direction == TrendDirection.DECLINING:
                base_score *= 0.9
            
            scores.append(base_score)
        
        return np.mean(scores) if scores else 0.0
    
    def _calculate_metric_correlations(self, element_id: str, metric_names: List[str]) -> Dict[Tuple[str, str], float]:
        """计算指标间相关性"""
        correlations = {}
        
        for i, metric1 in enumerate(metric_names):
            for j, metric2 in enumerate(metric_names[i+1:], i+1):
                correlation = self._calculate_correlation_between_metrics(element_id, metric1, metric2)
                correlations[(metric1, metric2)] = correlation
        
        return correlations
    
    def _calculate_correlation_between_metrics(self, element_id: str, metric1: str, metric2: str) -> float:
        """计算两个指标间的相关性"""
        if (element_id not in self.trend_data or 
            metric1 not in self.trend_data[element_id] or 
            metric2 not in self.trend_data[element_id]):
            return 0.0
        
        points1 = self.trend_data[element_id][metric1]
        points2 = self.trend_data[element_id][metric2]
        
        # 找到时间重叠的数据点
        common_times = set(p.timestamp for p in points1) & set(p.timestamp for p in points2)
        
        if len(common_times) < 3:
            return 0.0
        
        values1 = []
        values2 = []
        
        for time in common_times:
            val1 = next((p.value for p in points1 if p.timestamp == time), None)
            val2 = next((p.value for p in points2 if p.timestamp == time), None)
            
            if val1 is not None and val2 is not None:
                values1.append(val1)
                values2.append(val2)
        
        if len(values1) < 3:
            return 0.0
        
        return np.corrcoef(values1, values2)[0, 1] if len(values1) > 1 else 0.0
    
    def _identify_dominant_metrics(self, trends: List[TrendAnalysis]) -> List[str]:
        """识别主导指标"""
        # 基于趋势强度和变化幅度识别主导指标
        metric_scores = []
        
        for trend in trends:
            strength_weight = self._get_strength_weight(trend.strength)
            change_magnitude = abs(trend.percentage_change) / 100.0
            score = strength_weight * change_magnitude
            metric_scores.append((trend.metric_name, score))
        
        # 排序并选择前几个
        metric_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 选择评分高于平均值的指标
        avg_score = np.mean([score for _, score in metric_scores])
        dominant = [name for name, score in metric_scores if score > avg_score]
        
        return dominant[:3]  # 最多返回3个主导指标
    
    def _predict_overall_score(self, trends: List[TrendAnalysis]) -> Tuple[float, float]:
        """预测综合评分"""
        predictions = []
        confidences = []
        
        for trend in trends:
            predictions.append(trend.predicted_next_value)
            confidences.append(trend.prediction_confidence)
        
        if not predictions:
            return 0.0, 0.0
        
        # 加权平均预测
        weights = np.array(confidences)
        if np.sum(weights) > 0:
            weights = weights / np.sum(weights)
            predicted_score = np.average(predictions, weights=weights)
            avg_confidence = np.mean(confidences)
        else:
            predicted_score = np.mean(predictions)
            avg_confidence = 0.0
        
        return predicted_score, avg_confidence
    
    def _generate_multi_metric_recommendations(self, trends: List[TrendAnalysis], 
                                             correlations: Dict[Tuple[str, str], float]) -> List[str]:
        """生成多指标综合建议"""
        recommendations = []
        
        # 分析整体趋势
        declining_metrics = [t.metric_name for t in trends if t.direction == TrendDirection.DECLINING]
        if declining_metrics:
            recommendations.append(f"以下指标呈下降趋势，需要重点关注: {', '.join(declining_metrics)}")
        
        # 分析高相关性指标
        high_correlations = [(k, v) for k, v in correlations.items() if abs(v) > self.config['correlation_threshold']]
        if high_correlations:
            for (metric1, metric2), corr in high_correlations:
                if corr > 0:
                    recommendations.append(f"{metric1}和{metric2}高度正相关，可以协同优化")
                else:
                    recommendations.append(f"{metric1}和{metric2}高度负相关，需要平衡优化")
        
        # 分析数据质量
        low_quality_metrics = [t.metric_name for t in trends if t.data_quality_score < 0.7]
        if low_quality_metrics:
            recommendations.append(f"以下指标数据质量较低，建议改进监控: {', '.join(low_quality_metrics)}")
        
        return recommendations
    
    def compare_trends(self, element_ids: List[str], metric_name: str, 
                      period_days: Optional[int] = None) -> Optional[TrendComparison]:
        """比较多个元素的趋势"""
        trends = {}
        
        for element_id in element_ids:
            trend = self.analyze_trend(element_id, metric_name, period_days)
            if trend:
                trends[element_id] = trend
        
        if len(trends) < 2:
            return None
        
        # 性能排名
        performance_ranking = [(eid, trend.mean_value) for eid, trend in trends.items()]
        performance_ranking.sort(key=lambda x: x[1], reverse=True)
        
        best_performer = performance_ranking[0][0]
        worst_performer = performance_ranking[-1][0]
        
        # 计算差异
        mean_differences = {}
        best_mean = performance_ranking[0][1]
        for element_id, mean_val in performance_ranking:
            mean_differences[element_id] = mean_val - best_mean
        
        # 趋势相似性
        similarities = {}
        element_list = list(trends.keys())
        for i, eid1 in enumerate(element_list):
            for eid2 in element_list[i+1:]:
                similarity = self._calculate_trend_similarity(trends[eid1], trends[eid2])
                similarities[(eid1, eid2)] = similarity
        
        # 性能聚类（简化版本）
        clusters = self._cluster_by_performance(performance_ranking)
        
        # 生成洞察
        insights = self._generate_comparison_insights(trends, performance_ranking, similarities)
        
        period_start = min(trend.period_start for trend in trends.values())
        period_end = max(trend.period_end for trend in trends.values())
        
        return TrendComparison(
            element_ids=element_ids,
            metric_name=metric_name,
            period_start=period_start,
            period_end=period_end,
            best_performer=best_performer,
            worst_performer=worst_performer,
            performance_ranking=performance_ranking,
            mean_differences=mean_differences,
            trend_similarities=similarities,
            performance_clusters=clusters,
            insights=insights
        )
    
    def _calculate_trend_similarity(self, trend1: TrendAnalysis, trend2: TrendAnalysis) -> float:
        """计算两个趋势的相似性"""
        # 基于多个维度计算相似性
        direction_similarity = 1.0 if trend1.direction == trend2.direction else 0.0
        
        # 斜率相似性
        slope_diff = abs(trend1.slope - trend2.slope)
        slope_similarity = 1.0 / (1.0 + slope_diff)
        
        # 变化率相似性
        change_diff = abs(trend1.percentage_change - trend2.percentage_change)
        change_similarity = 1.0 / (1.0 + change_diff / 100.0)
        
        # 综合相似性
        similarity = (direction_similarity + slope_similarity + change_similarity) / 3.0
        
        return similarity
    
    def _cluster_by_performance(self, performance_ranking: List[Tuple[str, float]]) -> Dict[str, List[str]]:
        """基于性能进行聚类"""
        if len(performance_ranking) < 3:
            return {"all": [eid for eid, _ in performance_ranking]}
        
        values = [val for _, val in performance_ranking]
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        clusters = {"high": [], "medium": [], "low": []}
        
        for element_id, value in performance_ranking:
            if value > mean_val + 0.5 * std_val:
                clusters["high"].append(element_id)
            elif value < mean_val - 0.5 * std_val:
                clusters["low"].append(element_id)
            else:
                clusters["medium"].append(element_id)
        
        # 移除空聚类
        return {k: v for k, v in clusters.items() if v}
    
    def _generate_comparison_insights(self, trends: Dict[str, TrendAnalysis], 
                                    performance_ranking: List[Tuple[str, float]], 
                                    similarities: Dict[Tuple[str, str], float]) -> List[str]:
        """生成比较洞察"""
        insights = []
        
        # 性能差距分析
        best_score = performance_ranking[0][1]
        worst_score = performance_ranking[-1][1]
        gap = best_score - worst_score
        
        if gap > 20:  # 假设20是显著差距
            insights.append(f"性能差距较大({gap:.1f}分)，建议分析最佳实践")
        
        # 趋势一致性分析
        improving_count = sum(1 for trend in trends.values() if trend.direction == TrendDirection.IMPROVING)
        declining_count = sum(1 for trend in trends.values() if trend.direction == TrendDirection.DECLINING)
        
        if improving_count > len(trends) * 0.7:
            insights.append("大部分元素呈改善趋势，整体表现良好")
        elif declining_count > len(trends) * 0.7:
            insights.append("大部分元素呈下降趋势，需要系统性改进")
        
        # 相似性分析
        high_similarities = [v for v in similarities.values() if v > 0.8]
        if len(high_similarities) > len(similarities) * 0.5:
            insights.append("元素间趋势相似性较高，可能受共同因素影响")
        
        return insights
    
    def export_trend_data(self, element_id: str, metric_name: str, 
                         format: str = "json") -> Optional[str]:
        """导出趋势数据"""
        if (element_id not in self.trend_data or 
            metric_name not in self.trend_data[element_id]):
            return None
        
        points = self.trend_data[element_id][metric_name]
        trend_analysis = self.analyze_trend(element_id, metric_name)
        
        data = {
            'element_id': element_id,
            'metric_name': metric_name,
            'data_points': [
                {
                    'timestamp': p.timestamp.isoformat(),
                    'value': p.value,
                    'confidence': p.confidence,
                    'metadata': p.metadata
                }
                for p in points
            ],
            'analysis': {
                'direction': trend_analysis.direction.value,
                'strength': trend_analysis.strength.value,
                'slope': trend_analysis.slope,
                'r_squared': trend_analysis.r_squared,
                'mean_value': trend_analysis.mean_value,
                'total_change': trend_analysis.total_change,
                'percentage_change': trend_analysis.percentage_change,
                'predicted_next_value': trend_analysis.predicted_next_value,
                'prediction_confidence': trend_analysis.prediction_confidence,
                'recommendations': trend_analysis.recommendations
            } if trend_analysis else None
        }
        
        if format.lower() == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return str(data)  # 简化的其他格式支持