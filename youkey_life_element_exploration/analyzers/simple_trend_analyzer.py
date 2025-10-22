# -*- encoding=utf8 -*-
"""
简化趋势分析器

提供核心趋势分析功能，减少复杂度
"""

import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import statistics


@dataclass
class SimpleTrendResult:
    """简化趋势结果"""
    element_id: str
    metric_name: str
    timestamp: datetime
    
    # 趋势信息
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0-1
    confidence: float  # 0-1
    
    # 统计信息
    current_value: float
    average_value: float
    min_value: float
    max_value: float
    
    # 预测
    predicted_next: Optional[float] = None
    
    # 洞察
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class SimpleTrendAnalyzer:
    """简化趋势分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_history = {}  # element_id -> metric_name -> [(timestamp, value)]
        self.analysis_cache = {}
    
    def analyze_trend(self, element_id: str, metric_name: str, 
                     data_points: List[Tuple[datetime, float]]) -> SimpleTrendResult:
        """分析趋势"""
        if len(data_points) < 3:
            return self._create_insufficient_data_result(element_id, metric_name, data_points)
        
        # 更新历史数据
        self._update_history(element_id, metric_name, data_points)
        
        # 基础统计
        values = [value for _, value in data_points]
        current_value = values[-1]
        average_value = statistics.mean(values)
        min_value = min(values)
        max_value = max(values)
        
        # 趋势分析
        trend_direction, trend_strength = self._analyze_trend_direction(values)
        confidence = self._calculate_confidence(values)
        
        # 简单预测
        predicted_next = self._simple_prediction(values)
        
        # 生成洞察和建议
        insights = self._generate_insights(trend_direction, trend_strength, values)
        recommendations = self._generate_recommendations(trend_direction, metric_name)
        
        return SimpleTrendResult(
            element_id=element_id,
            metric_name=metric_name,
            timestamp=datetime.now(),
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            confidence=confidence,
            current_value=current_value,
            average_value=average_value,
            min_value=min_value,
            max_value=max_value,
            predicted_next=predicted_next,
            insights=insights,
            recommendations=recommendations
        )
    
    def analyze_multiple_metrics(self, element_id: str, 
                               metrics_data: Dict[str, List[Tuple[datetime, float]]]) -> Dict[str, SimpleTrendResult]:
        """分析多个指标的趋势"""
        results = {}
        
        for metric_name, data_points in metrics_data.items():
            try:
                results[metric_name] = self.analyze_trend(element_id, metric_name, data_points)
            except Exception as e:
                self.logger.error(f"分析指标 {metric_name} 趋势失败: {e}")
        
        return results
    
    def get_trend_summary(self, element_id: str) -> Dict[str, Any]:
        """获取趋势摘要"""
        if element_id not in self.data_history:
            return {}
        
        summary = {
            'element_id': element_id,
            'metrics_count': len(self.data_history[element_id]),
            'last_updated': datetime.now(),
            'trends': {}
        }
        
        for metric_name, data_points in self.data_history[element_id].items():
            if len(data_points) >= 3:
                values = [value for _, value in data_points[-10:]]  # 最近10个点
                direction, strength = self._analyze_trend_direction(values)
                
                summary['trends'][metric_name] = {
                    'direction': direction,
                    'strength': strength,
                    'current_value': values[-1],
                    'data_points': len(data_points)
                }
        
        return summary
    
    def _update_history(self, element_id: str, metric_name: str, 
                       data_points: List[Tuple[datetime, float]]) -> None:
        """更新历史数据"""
        if element_id not in self.data_history:
            self.data_history[element_id] = {}
        
        if metric_name not in self.data_history[element_id]:
            self.data_history[element_id][metric_name] = []
        
        # 合并新数据点
        existing_data = self.data_history[element_id][metric_name]
        all_data = existing_data + data_points
        
        # 去重并排序
        unique_data = {}
        for timestamp, value in all_data:
            unique_data[timestamp] = value
        
        sorted_data = sorted(unique_data.items())
        
        # 保持最近100个数据点
        if len(sorted_data) > 100:
            sorted_data = sorted_data[-100:]
        
        self.data_history[element_id][metric_name] = sorted_data
    
    def _analyze_trend_direction(self, values: List[float]) -> Tuple[str, float]:
        """分析趋势方向和强度"""
        if len(values) < 3:
            return "stable", 0.0
        
        # 简单线性回归
        n = len(values)
        x = list(range(n))
        
        # 计算斜率
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable", 0.0
        
        slope = numerator / denominator
        
        # 确定方向和强度
        if abs(slope) < 0.01:
            return "stable", abs(slope) * 10
        elif slope > 0:
            return "increasing", min(abs(slope) * 100, 1.0)
        else:
            return "decreasing", min(abs(slope) * 100, 1.0)
    
    def _calculate_confidence(self, values: List[float]) -> float:
        """计算置信度"""
        if len(values) < 3:
            return 0.0
        
        # 基于数据点数量和变异性
        data_points_factor = min(len(values) / 20, 1.0)  # 20个点为满分
        
        # 计算变异系数
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return data_points_factor * 0.5
        
        std_val = statistics.stdev(values) if len(values) > 1 else 0
        cv = std_val / abs(mean_val)
        
        # 变异系数越小，置信度越高
        variability_factor = max(0, 1 - cv)
        
        return (data_points_factor + variability_factor) / 2
    
    def _simple_prediction(self, values: List[float]) -> Optional[float]:
        """简单预测下一个值"""
        if len(values) < 3:
            return None
        
        # 使用最近3个点的线性趋势
        recent_values = values[-3:]
        n = len(recent_values)
        x = list(range(n))
        
        # 线性回归预测
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(recent_values)
        
        numerator = sum((x[i] - x_mean) * (recent_values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return recent_values[-1]
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # 预测下一个点
        next_x = n
        predicted = slope * next_x + intercept
        
        return max(0, predicted)  # 确保非负
    
    def _generate_insights(self, trend_direction: str, trend_strength: float, 
                          values: List[float]) -> List[str]:
        """生成洞察"""
        insights = []
        
        if trend_direction == "increasing":
            if trend_strength > 0.7:
                insights.append("指标呈现强烈上升趋势")
            elif trend_strength > 0.3:
                insights.append("指标呈现温和上升趋势")
            else:
                insights.append("指标略有上升")
        elif trend_direction == "decreasing":
            if trend_strength > 0.7:
                insights.append("指标呈现强烈下降趋势，需要关注")
            elif trend_strength > 0.3:
                insights.append("指标呈现温和下降趋势")
            else:
                insights.append("指标略有下降")
        else:
            insights.append("指标保持相对稳定")
        
        # 变异性分析
        if len(values) > 1:
            cv = statistics.stdev(values) / abs(statistics.mean(values)) if statistics.mean(values) != 0 else 0
            if cv > 0.3:
                insights.append("数据波动较大，建议关注稳定性")
            elif cv < 0.1:
                insights.append("数据表现稳定")
        
        return insights
    
    def _generate_recommendations(self, trend_direction: str, metric_name: str) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if trend_direction == "decreasing":
            if "performance" in metric_name.lower():
                recommendations.extend([
                    "检查性能瓶颈",
                    "优化代码逻辑",
                    "考虑硬件升级"
                ])
            elif "quality" in metric_name.lower():
                recommendations.extend([
                    "加强质量控制",
                    "增加测试覆盖",
                    "优化测试策略"
                ])
            else:
                recommendations.extend([
                    f"分析{metric_name}下降原因",
                    "制定改进计划"
                ])
        elif trend_direction == "increasing":
            recommendations.append("保持当前良好趋势")
        else:
            recommendations.append("继续监控指标变化")
        
        return recommendations
    
    def _create_insufficient_data_result(self, element_id: str, metric_name: str, 
                                       data_points: List[Tuple[datetime, float]]) -> SimpleTrendResult:
        """创建数据不足的结果"""
        current_value = data_points[-1][1] if data_points else 0.0
        
        return SimpleTrendResult(
            element_id=element_id,
            metric_name=metric_name,
            timestamp=datetime.now(),
            trend_direction="unknown",
            trend_strength=0.0,
            confidence=0.0,
            current_value=current_value,
            average_value=current_value,
            min_value=current_value,
            max_value=current_value,
            insights=["数据点不足，无法进行趋势分析"],
            recommendations=["收集更多数据点以进行有效分析"]
        )