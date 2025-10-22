# -*- encoding=utf8 -*-
"""
稳定性指标计算

提供各种稳定性相关指标的计算功能
"""

import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta


@dataclass
class StabilityData:
    """稳定性数据"""
    timestamp: datetime
    position_x: float  # X坐标
    position_y: float  # Y坐标
    width: float  # 宽度
    height: float  # 高度
    is_visible: bool  # 是否可见
    is_enabled: bool  # 是否启用
    is_available: bool  # 是否可用
    attributes: Dict[str, Any]  # 属性字典
    css_properties: Dict[str, str]  # CSS属性
    dom_path: str  # DOM路径
    layout_shift: float = 0.0  # 布局偏移
    rendering_time: float = 0.0  # 渲染时间


@dataclass
class StabilityScore:
    """稳定性分数"""
    overall_score: float  # 总体分数（0-1）
    position_stability: float  # 位置稳定性分数
    size_stability: float  # 尺寸稳定性分数
    visibility_stability: float  # 可见性稳定性分数
    attribute_stability: float  # 属性稳定性分数
    availability_stability: float  # 可用性稳定性分数
    layout_stability: float  # 布局稳定性分数
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
class StabilityTrend:
    """稳定性趋势"""
    metric_name: str  # 指标名称
    trend_direction: str  # 趋势方向：improving, declining, stable
    trend_strength: float  # 趋势强度（0-1）
    variance_trend: float  # 方差趋势
    stability_index: float  # 稳定性指数
    prediction: Optional[float] = None  # 预测值
    confidence: float = 0.0  # 置信度


class StabilityMetrics:
    """稳定性指标计算器"""
    
    def __init__(self):
        """初始化稳定性指标计算器"""
        self.stability_history: List[StabilityData] = []
        self.baseline_data: Optional[StabilityData] = None
        self.critical_attributes = [
            'id', 'class', 'data-testid', 'aria-label', 'role', 'type'
        ]
        self.thresholds = {
            'position_variance': {'excellent': 2.0, 'good': 5.0, 'acceptable': 10.0},
            'size_variance': {'excellent': 1.0, 'good': 3.0, 'acceptable': 5.0},
            'layout_shift': {'excellent': 0.05, 'good': 0.1, 'acceptable': 0.25},
            'availability_rate': {'excellent': 99.5, 'good': 99.0, 'acceptable': 95.0},
            'attribute_change_rate': {'excellent': 1.0, 'good': 5.0, 'acceptable': 10.0}
        }
    
    def add_stability_data(self, data: StabilityData) -> None:
        """
        添加稳定性数据
        
        Args:
            data: 稳定性数据
        """
        self.stability_history.append(data)
        
        # 保持历史数据在合理范围内（最近1000条记录）
        if len(self.stability_history) > 1000:
            self.stability_history = self.stability_history[-1000:]
    
    def calculate_stability_score(self, window_size: int = 10) -> StabilityScore:
        """
        计算稳定性分数
        
        Args:
            window_size: 分析窗口大小
            
        Returns:
            StabilityScore: 稳定性分数
        """
        if len(self.stability_history) < 2:
            return StabilityScore(
                overall_score=0.0,
                position_stability=0.0,
                size_stability=0.0,
                visibility_stability=0.0,
                attribute_stability=0.0,
                availability_stability=0.0,
                layout_stability=0.0
            )
        
        # 获取最近的数据
        recent_data = self.stability_history[-window_size:] if len(self.stability_history) >= window_size else self.stability_history
        
        # 计算各项稳定性分数
        position_stability = self._calculate_position_stability(recent_data)
        size_stability = self._calculate_size_stability(recent_data)
        visibility_stability = self._calculate_visibility_stability(recent_data)
        attribute_stability = self._calculate_attribute_stability(recent_data)
        availability_stability = self._calculate_availability_stability(recent_data)
        layout_stability = self._calculate_layout_stability(recent_data)
        
        # 计算总体分数（加权平均）
        weights = {
            'position': 0.20,
            'size': 0.15,
            'visibility': 0.15,
            'attribute': 0.20,
            'availability': 0.20,
            'layout': 0.10
        }
        
        overall_score = (
            position_stability * weights['position'] +
            size_stability * weights['size'] +
            visibility_stability * weights['visibility'] +
            attribute_stability * weights['attribute'] +
            availability_stability * weights['availability'] +
            layout_stability * weights['layout']
        )
        
        # 详细信息
        details = {
            'weights': weights,
            'window_size': len(recent_data),
            'analysis_period': {
                'start': recent_data[0].timestamp.isoformat(),
                'end': recent_data[-1].timestamp.isoformat()
            },
            'variance_metrics': self._calculate_variance_metrics(recent_data),
            'change_frequency': self._calculate_change_frequency(recent_data),
            'stability_patterns': self._analyze_stability_patterns(recent_data)
        }
        
        return StabilityScore(
            overall_score=overall_score,
            position_stability=position_stability,
            size_stability=size_stability,
            visibility_stability=visibility_stability,
            attribute_stability=attribute_stability,
            availability_stability=availability_stability,
            layout_stability=layout_stability,
            details=details
        )
    
    def calculate_stability_trends(self, days: int = 7) -> List[StabilityTrend]:
        """
        计算稳定性趋势
        
        Args:
            days: 分析天数
            
        Returns:
            List[StabilityTrend]: 稳定性趋势列表
        """
        if len(self.stability_history) < 10:
            return []
        
        # 获取指定天数内的数据
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_data = [
            data for data in self.stability_history
            if data.timestamp >= cutoff_time
        ]
        
        if len(recent_data) < 10:
            return []
        
        trends = []
        
        # 分析位置稳定性趋势
        position_trend = self._calculate_position_trend(recent_data)
        if position_trend:
            trends.append(position_trend)
        
        # 分析尺寸稳定性趋势
        size_trend = self._calculate_size_trend(recent_data)
        if size_trend:
            trends.append(size_trend)
        
        # 分析可见性稳定性趋势
        visibility_trend = self._calculate_visibility_trend(recent_data)
        if visibility_trend:
            trends.append(visibility_trend)
        
        # 分析属性稳定性趋势
        attribute_trend = self._calculate_attribute_trend(recent_data)
        if attribute_trend:
            trends.append(attribute_trend)
        
        # 分析布局稳定性趋势
        layout_trend = self._calculate_layout_trend(recent_data)
        if layout_trend:
            trends.append(layout_trend)
        
        return trends
    
    def get_stability_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        获取稳定性摘要
        
        Args:
            days: 分析天数
            
        Returns:
            Dict[str, Any]: 稳定性摘要
        """
        if not self.stability_history:
            return {}
        
        # 获取指定天数内的数据
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_data = [
            data for data in self.stability_history
            if data.timestamp >= cutoff_time
        ]
        
        if not recent_data:
            return {}
        
        # 计算最新分数
        latest_score = self.calculate_stability_score()
        
        # 计算趋势
        trends = self.calculate_stability_trends(days)
        
        # 计算统计信息
        position_variances = self._calculate_position_variances(recent_data)
        size_variances = self._calculate_size_variances(recent_data)
        
        return {
            'period': f"最近{days}天",
            'data_points': len(recent_data),
            'latest_score': latest_score,
            'statistics': {
                'position_variance': {
                    'x_variance': position_variances['x_variance'],
                    'y_variance': position_variances['y_variance'],
                    'total_variance': position_variances['total_variance']
                },
                'size_variance': {
                    'width_variance': size_variances['width_variance'],
                    'height_variance': size_variances['height_variance'],
                    'area_variance': size_variances['area_variance']
                },
                'availability': {
                    'total_checks': len(recent_data),
                    'available_count': sum(1 for d in recent_data if d.is_available),
                    'availability_rate': (sum(1 for d in recent_data if d.is_available) / len(recent_data)) * 100
                },
                'visibility': {
                    'total_checks': len(recent_data),
                    'visible_count': sum(1 for d in recent_data if d.is_visible),
                    'visibility_rate': (sum(1 for d in recent_data if d.is_visible) / len(recent_data)) * 100
                }
            },
            'trends': trends,
            'alerts': self._generate_stability_alerts(recent_data)
        }
    
    def set_baseline(self, data: StabilityData) -> None:
        """
        设置基线数据
        
        Args:
            data: 基线稳定性数据
        """
        self.baseline_data = data
    
    def compare_with_baseline(self, data: StabilityData) -> Dict[str, Any]:
        """
        与基线比较
        
        Args:
            data: 当前稳定性数据
            
        Returns:
            Dict[str, Any]: 与基线的差异
        """
        if not self.baseline_data:
            return {}
        
        baseline = self.baseline_data
        
        return {
            'position_change': {
                'x_diff': data.position_x - baseline.position_x,
                'y_diff': data.position_y - baseline.position_y,
                'distance': ((data.position_x - baseline.position_x) ** 2 + 
                           (data.position_y - baseline.position_y) ** 2) ** 0.5
            },
            'size_change': {
                'width_diff': data.width - baseline.width,
                'height_diff': data.height - baseline.height,
                'area_diff': (data.width * data.height) - (baseline.width * baseline.height)
            },
            'state_change': {
                'visibility_changed': data.is_visible != baseline.is_visible,
                'enabled_changed': data.is_enabled != baseline.is_enabled,
                'availability_changed': data.is_available != baseline.is_available
            },
            'attribute_changes': self._compare_attributes(data.attributes, baseline.attributes),
            'css_changes': self._compare_css_properties(data.css_properties, baseline.css_properties)
        }
    
    def _calculate_position_stability(self, data_list: List[StabilityData]) -> float:
        """计算位置稳定性"""
        if len(data_list) < 2:
            return 1.0
        
        x_positions = [d.position_x for d in data_list]
        y_positions = [d.position_y for d in data_list]
        
        x_variance = statistics.variance(x_positions) if len(x_positions) > 1 else 0.0
        y_variance = statistics.variance(y_positions) if len(y_positions) > 1 else 0.0
        
        total_variance = (x_variance + y_variance) ** 0.5
        
        # 根据方差计算分数
        if total_variance <= self.thresholds['position_variance']['excellent']:
            return 1.0
        elif total_variance <= self.thresholds['position_variance']['good']:
            ratio = (total_variance - self.thresholds['position_variance']['excellent']) / \
                   (self.thresholds['position_variance']['good'] - self.thresholds['position_variance']['excellent'])
            return 1.0 - ratio * 0.2
        elif total_variance <= self.thresholds['position_variance']['acceptable']:
            ratio = (total_variance - self.thresholds['position_variance']['good']) / \
                   (self.thresholds['position_variance']['acceptable'] - self.thresholds['position_variance']['good'])
            return 0.8 - ratio * 0.3
        else:
            return max(0.5 - (total_variance - self.thresholds['position_variance']['acceptable']) / 20, 0.0)
    
    def _calculate_size_stability(self, data_list: List[StabilityData]) -> float:
        """计算尺寸稳定性"""
        if len(data_list) < 2:
            return 1.0
        
        widths = [d.width for d in data_list]
        heights = [d.height for d in data_list]
        
        width_variance = statistics.variance(widths) if len(widths) > 1 else 0.0
        height_variance = statistics.variance(heights) if len(heights) > 1 else 0.0
        
        total_variance = (width_variance + height_variance) ** 0.5
        
        # 根据方差计算分数
        if total_variance <= self.thresholds['size_variance']['excellent']:
            return 1.0
        elif total_variance <= self.thresholds['size_variance']['good']:
            ratio = (total_variance - self.thresholds['size_variance']['excellent']) / \
                   (self.thresholds['size_variance']['good'] - self.thresholds['size_variance']['excellent'])
            return 1.0 - ratio * 0.2
        elif total_variance <= self.thresholds['size_variance']['acceptable']:
            ratio = (total_variance - self.thresholds['size_variance']['good']) / \
                   (self.thresholds['size_variance']['acceptable'] - self.thresholds['size_variance']['good'])
            return 0.8 - ratio * 0.3
        else:
            return max(0.5 - (total_variance - self.thresholds['size_variance']['acceptable']) / 10, 0.0)
    
    def _calculate_visibility_stability(self, data_list: List[StabilityData]) -> float:
        """计算可见性稳定性"""
        if not data_list:
            return 0.0
        
        visibility_changes = 0
        for i in range(1, len(data_list)):
            if data_list[i].is_visible != data_list[i-1].is_visible:
                visibility_changes += 1
        
        # 计算稳定性分数（变化次数越少越好）
        change_rate = visibility_changes / len(data_list)
        
        if change_rate == 0:
            return 1.0
        elif change_rate <= 0.1:  # 10%以下的变化率
            return 0.9
        elif change_rate <= 0.2:  # 20%以下的变化率
            return 0.7
        elif change_rate <= 0.3:  # 30%以下的变化率
            return 0.5
        else:
            return max(0.3 - change_rate, 0.0)
    
    def _calculate_attribute_stability(self, data_list: List[StabilityData]) -> float:
        """计算属性稳定性"""
        if len(data_list) < 2:
            return 1.0
        
        total_changes = 0
        total_comparisons = 0
        
        for i in range(1, len(data_list)):
            current_attrs = data_list[i].attributes
            previous_attrs = data_list[i-1].attributes
            
            # 检查关键属性的变化
            for attr in self.critical_attributes:
                total_comparisons += 1
                if current_attrs.get(attr) != previous_attrs.get(attr):
                    total_changes += 1
        
        if total_comparisons == 0:
            return 1.0
        
        change_rate = (total_changes / total_comparisons) * 100
        
        # 根据变化率计算分数
        if change_rate <= self.thresholds['attribute_change_rate']['excellent']:
            return 1.0
        elif change_rate <= self.thresholds['attribute_change_rate']['good']:
            ratio = (change_rate - self.thresholds['attribute_change_rate']['excellent']) / \
                   (self.thresholds['attribute_change_rate']['good'] - self.thresholds['attribute_change_rate']['excellent'])
            return 1.0 - ratio * 0.2
        elif change_rate <= self.thresholds['attribute_change_rate']['acceptable']:
            ratio = (change_rate - self.thresholds['attribute_change_rate']['good']) / \
                   (self.thresholds['attribute_change_rate']['acceptable'] - self.thresholds['attribute_change_rate']['good'])
            return 0.8 - ratio * 0.3
        else:
            return max(0.5 - (change_rate - self.thresholds['attribute_change_rate']['acceptable']) / 20, 0.0)
    
    def _calculate_availability_stability(self, data_list: List[StabilityData]) -> float:
        """计算可用性稳定性"""
        if not data_list:
            return 0.0
        
        available_count = sum(1 for d in data_list if d.is_available)
        availability_rate = (available_count / len(data_list)) * 100
        
        # 根据可用性率计算分数
        if availability_rate >= self.thresholds['availability_rate']['excellent']:
            return 1.0
        elif availability_rate >= self.thresholds['availability_rate']['good']:
            ratio = (self.thresholds['availability_rate']['excellent'] - availability_rate) / \
                   (self.thresholds['availability_rate']['excellent'] - self.thresholds['availability_rate']['good'])
            return 1.0 - ratio * 0.2
        elif availability_rate >= self.thresholds['availability_rate']['acceptable']:
            ratio = (self.thresholds['availability_rate']['good'] - availability_rate) / \
                   (self.thresholds['availability_rate']['good'] - self.thresholds['availability_rate']['acceptable'])
            return 0.8 - ratio * 0.3
        else:
            return max(0.5 - (self.thresholds['availability_rate']['acceptable'] - availability_rate) / 20, 0.0)
    
    def _calculate_layout_stability(self, data_list: List[StabilityData]) -> float:
        """计算布局稳定性"""
        if not data_list:
            return 1.0
        
        layout_shifts = [d.layout_shift for d in data_list if d.layout_shift > 0]
        
        if not layout_shifts:
            return 1.0
        
        avg_layout_shift = statistics.mean(layout_shifts)
        
        # 根据平均布局偏移计算分数
        if avg_layout_shift <= self.thresholds['layout_shift']['excellent']:
            return 1.0
        elif avg_layout_shift <= self.thresholds['layout_shift']['good']:
            ratio = (avg_layout_shift - self.thresholds['layout_shift']['excellent']) / \
                   (self.thresholds['layout_shift']['good'] - self.thresholds['layout_shift']['excellent'])
            return 1.0 - ratio * 0.2
        elif avg_layout_shift <= self.thresholds['layout_shift']['acceptable']:
            ratio = (avg_layout_shift - self.thresholds['layout_shift']['good']) / \
                   (self.thresholds['layout_shift']['acceptable'] - self.thresholds['layout_shift']['good'])
            return 0.8 - ratio * 0.3
        else:
            return max(0.5 - (avg_layout_shift - self.thresholds['layout_shift']['acceptable']) / 0.5, 0.0)
    
    def _calculate_variance_metrics(self, data_list: List[StabilityData]) -> Dict[str, float]:
        """计算方差指标"""
        if len(data_list) < 2:
            return {}
        
        x_positions = [d.position_x for d in data_list]
        y_positions = [d.position_y for d in data_list]
        widths = [d.width for d in data_list]
        heights = [d.height for d in data_list]
        
        return {
            'position_x_variance': statistics.variance(x_positions),
            'position_y_variance': statistics.variance(y_positions),
            'width_variance': statistics.variance(widths),
            'height_variance': statistics.variance(heights),
            'position_x_std': statistics.stdev(x_positions),
            'position_y_std': statistics.stdev(y_positions),
            'width_std': statistics.stdev(widths),
            'height_std': statistics.stdev(heights)
        }
    
    def _calculate_change_frequency(self, data_list: List[StabilityData]) -> Dict[str, float]:
        """计算变化频率"""
        if len(data_list) < 2:
            return {}
        
        position_changes = 0
        size_changes = 0
        visibility_changes = 0
        availability_changes = 0
        
        for i in range(1, len(data_list)):
            current = data_list[i]
            previous = data_list[i-1]
            
            # 位置变化（阈值：1像素）
            if abs(current.position_x - previous.position_x) > 1 or abs(current.position_y - previous.position_y) > 1:
                position_changes += 1
            
            # 尺寸变化（阈值：1像素）
            if abs(current.width - previous.width) > 1 or abs(current.height - previous.height) > 1:
                size_changes += 1
            
            # 可见性变化
            if current.is_visible != previous.is_visible:
                visibility_changes += 1
            
            # 可用性变化
            if current.is_available != previous.is_available:
                availability_changes += 1
        
        total_intervals = len(data_list) - 1
        
        return {
            'position_change_frequency': position_changes / total_intervals,
            'size_change_frequency': size_changes / total_intervals,
            'visibility_change_frequency': visibility_changes / total_intervals,
            'availability_change_frequency': availability_changes / total_intervals
        }
    
    def _analyze_stability_patterns(self, data_list: List[StabilityData]) -> Dict[str, Any]:
        """分析稳定性模式"""
        if len(data_list) < 5:
            return {}
        
        # 分析周期性模式
        position_pattern = self._detect_periodic_pattern([d.position_x for d in data_list])
        size_pattern = self._detect_periodic_pattern([d.width for d in data_list])
        
        # 分析趋势模式
        position_trend = self._detect_trend_pattern([d.position_x for d in data_list])
        size_trend = self._detect_trend_pattern([d.width for d in data_list])
        
        return {
            'periodic_patterns': {
                'position_period': position_pattern,
                'size_period': size_pattern
            },
            'trend_patterns': {
                'position_trend': position_trend,
                'size_trend': size_trend
            }
        }
    
    def _detect_periodic_pattern(self, values: List[float]) -> Optional[int]:
        """检测周期性模式"""
        if len(values) < 6:
            return None
        
        # 简单的周期检测：查找重复模式
        for period in range(2, len(values) // 2):
            is_periodic = True
            for i in range(period, len(values)):
                if abs(values[i] - values[i % period]) > 1.0:  # 允许1像素的误差
                    is_periodic = False
                    break
            
            if is_periodic:
                return period
        
        return None
    
    def _detect_trend_pattern(self, values: List[float]) -> str:
        """检测趋势模式"""
        if len(values) < 3:
            return "stable"
        
        # 计算简单的趋势
        increases = 0
        decreases = 0
        
        for i in range(1, len(values)):
            diff = values[i] - values[i-1]
            if diff > 1.0:
                increases += 1
            elif diff < -1.0:
                decreases += 1
        
        total_changes = increases + decreases
        if total_changes == 0:
            return "stable"
        
        if increases / total_changes > 0.7:
            return "increasing"
        elif decreases / total_changes > 0.7:
            return "decreasing"
        else:
            return "fluctuating"
    
    def _calculate_position_variances(self, data_list: List[StabilityData]) -> Dict[str, float]:
        """计算位置方差"""
        if len(data_list) < 2:
            return {'x_variance': 0.0, 'y_variance': 0.0, 'total_variance': 0.0}
        
        x_positions = [d.position_x for d in data_list]
        y_positions = [d.position_y for d in data_list]
        
        x_variance = statistics.variance(x_positions)
        y_variance = statistics.variance(y_positions)
        total_variance = (x_variance + y_variance) ** 0.5
        
        return {
            'x_variance': x_variance,
            'y_variance': y_variance,
            'total_variance': total_variance
        }
    
    def _calculate_size_variances(self, data_list: List[StabilityData]) -> Dict[str, float]:
        """计算尺寸方差"""
        if len(data_list) < 2:
            return {'width_variance': 0.0, 'height_variance': 0.0, 'area_variance': 0.0}
        
        widths = [d.width for d in data_list]
        heights = [d.height for d in data_list]
        areas = [d.width * d.height for d in data_list]
        
        width_variance = statistics.variance(widths)
        height_variance = statistics.variance(heights)
        area_variance = statistics.variance(areas)
        
        return {
            'width_variance': width_variance,
            'height_variance': height_variance,
            'area_variance': area_variance
        }
    
    def _compare_attributes(self, current_attrs: Dict[str, Any], baseline_attrs: Dict[str, Any]) -> Dict[str, Any]:
        """比较属性"""
        changes = {}
        
        # 检查所有属性
        all_keys = set(current_attrs.keys()) | set(baseline_attrs.keys())
        
        for key in all_keys:
            current_value = current_attrs.get(key)
            baseline_value = baseline_attrs.get(key)
            
            if current_value != baseline_value:
                changes[key] = {
                    'old_value': baseline_value,
                    'new_value': current_value,
                    'change_type': 'modified' if key in baseline_attrs and key in current_attrs else 
                                  'added' if key in current_attrs else 'removed'
                }
        
        return changes
    
    def _compare_css_properties(self, current_css: Dict[str, str], baseline_css: Dict[str, str]) -> Dict[str, Any]:
        """比较CSS属性"""
        changes = {}
        
        # 检查所有CSS属性
        all_keys = set(current_css.keys()) | set(baseline_css.keys())
        
        for key in all_keys:
            current_value = current_css.get(key)
            baseline_value = baseline_css.get(key)
            
            if current_value != baseline_value:
                changes[key] = {
                    'old_value': baseline_value,
                    'new_value': current_value,
                    'change_type': 'modified' if key in baseline_css and key in current_css else 
                                  'added' if key in current_css else 'removed'
                }
        
        return changes
    
    def _calculate_position_trend(self, data_list: List[StabilityData]) -> Optional[StabilityTrend]:
        """计算位置趋势"""
        if len(data_list) < 5:
            return None
        
        # 计算位置方差的趋势
        window_size = 5
        variances = []
        
        for i in range(window_size, len(data_list) + 1):
            window_data = data_list[i-window_size:i]
            x_positions = [d.position_x for d in window_data]
            y_positions = [d.position_y for d in window_data]
            
            x_var = statistics.variance(x_positions) if len(x_positions) > 1 else 0.0
            y_var = statistics.variance(y_positions) if len(y_positions) > 1 else 0.0
            total_var = (x_var + y_var) ** 0.5
            
            variances.append(total_var)
        
        if len(variances) < 2:
            return None
        
        # 分析方差趋势
        variance_trend = self._analyze_variance_trend(variances)
        
        return StabilityTrend(
            metric_name="position_stability",
            trend_direction=variance_trend['direction'],
            trend_strength=variance_trend['strength'],
            variance_trend=variance_trend['slope'],
            stability_index=1.0 - (variances[-1] / max(variances) if max(variances) > 0 else 0.0),
            confidence=variance_trend['confidence']
        )
    
    def _calculate_size_trend(self, data_list: List[StabilityData]) -> Optional[StabilityTrend]:
        """计算尺寸趋势"""
        if len(data_list) < 5:
            return None
        
        # 计算尺寸方差的趋势
        window_size = 5
        variances = []
        
        for i in range(window_size, len(data_list) + 1):
            window_data = data_list[i-window_size:i]
            widths = [d.width for d in window_data]
            heights = [d.height for d in window_data]
            
            width_var = statistics.variance(widths) if len(widths) > 1 else 0.0
            height_var = statistics.variance(heights) if len(heights) > 1 else 0.0
            total_var = (width_var + height_var) ** 0.5
            
            variances.append(total_var)
        
        if len(variances) < 2:
            return None
        
        # 分析方差趋势
        variance_trend = self._analyze_variance_trend(variances)
        
        return StabilityTrend(
            metric_name="size_stability",
            trend_direction=variance_trend['direction'],
            trend_strength=variance_trend['strength'],
            variance_trend=variance_trend['slope'],
            stability_index=1.0 - (variances[-1] / max(variances) if max(variances) > 0 else 0.0),
            confidence=variance_trend['confidence']
        )
    
    def _calculate_visibility_trend(self, data_list: List[StabilityData]) -> Optional[StabilityTrend]:
        """计算可见性趋势"""
        if len(data_list) < 5:
            return None
        
        # 计算可见性变化频率的趋势
        window_size = 5
        change_rates = []
        
        for i in range(window_size, len(data_list) + 1):
            window_data = data_list[i-window_size:i]
            changes = 0
            
            for j in range(1, len(window_data)):
                if window_data[j].is_visible != window_data[j-1].is_visible:
                    changes += 1
            
            change_rate = changes / (len(window_data) - 1) if len(window_data) > 1 else 0.0
            change_rates.append(change_rate)
        
        if len(change_rates) < 2:
            return None
        
        # 分析变化率趋势
        trend_analysis = self._analyze_variance_trend(change_rates)
        
        return StabilityTrend(
            metric_name="visibility_stability",
            trend_direction="declining" if trend_analysis['direction'] == "increasing" else "improving",
            trend_strength=trend_analysis['strength'],
            variance_trend=trend_analysis['slope'],
            stability_index=1.0 - change_rates[-1],
            confidence=trend_analysis['confidence']
        )
    
    def _calculate_attribute_trend(self, data_list: List[StabilityData]) -> Optional[StabilityTrend]:
        """计算属性趋势"""
        if len(data_list) < 5:
            return None
        
        # 计算属性变化频率的趋势
        window_size = 5
        change_rates = []
        
        for i in range(window_size, len(data_list) + 1):
            window_data = data_list[i-window_size:i]
            total_changes = 0
            total_comparisons = 0
            
            for j in range(1, len(window_data)):
                current_attrs = window_data[j].attributes
                previous_attrs = window_data[j-1].attributes
                
                for attr in self.critical_attributes:
                    total_comparisons += 1
                    if current_attrs.get(attr) != previous_attrs.get(attr):
                        total_changes += 1
            
            change_rate = total_changes / total_comparisons if total_comparisons > 0 else 0.0
            change_rates.append(change_rate)
        
        if len(change_rates) < 2:
            return None
        
        # 分析变化率趋势
        trend_analysis = self._analyze_variance_trend(change_rates)
        
        return StabilityTrend(
            metric_name="attribute_stability",
            trend_direction="declining" if trend_analysis['direction'] == "increasing" else "improving",
            trend_strength=trend_analysis['strength'],
            variance_trend=trend_analysis['slope'],
            stability_index=1.0 - change_rates[-1],
            confidence=trend_analysis['confidence']
        )
    
    def _calculate_layout_trend(self, data_list: List[StabilityData]) -> Optional[StabilityTrend]:
        """计算布局趋势"""
        if len(data_list) < 5:
            return None
        
        # 计算布局偏移的趋势
        layout_shifts = [d.layout_shift for d in data_list]
        
        if not any(shift > 0 for shift in layout_shifts):
            return StabilityTrend(
                metric_name="layout_stability",
                trend_direction="stable",
                trend_strength=0.0,
                variance_trend=0.0,
                stability_index=1.0,
                confidence=1.0
            )
        
        # 分析布局偏移趋势
        trend_analysis = self._analyze_variance_trend(layout_shifts)
        
        return StabilityTrend(
            metric_name="layout_stability",
            trend_direction="declining" if trend_analysis['direction'] == "increasing" else "improving",
            trend_strength=trend_analysis['strength'],
            variance_trend=trend_analysis['slope'],
            stability_index=1.0 - (layout_shifts[-1] / max(layout_shifts) if max(layout_shifts) > 0 else 0.0),
            confidence=trend_analysis['confidence']
        )
    
    def _analyze_variance_trend(self, values: List[float]) -> Dict[str, Any]:
        """分析方差趋势"""
        if len(values) < 2:
            return {'direction': 'stable', 'strength': 0.0, 'slope': 0.0, 'confidence': 0.0}
        
        # 简单线性回归
        n = len(values)
        x_values = list(range(n))
        
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        try:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # 计算相关系数
            mean_x = sum_x / n
            mean_y = sum_y / n
            
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
            denominator_x = sum((x - mean_x) ** 2 for x in x_values)
            denominator_y = sum((y - mean_y) ** 2 for y in values)
            
            if denominator_x > 0 and denominator_y > 0:
                correlation = numerator / (denominator_x * denominator_y) ** 0.5
            else:
                correlation = 0.0
            
            # 确定趋势方向
            if abs(slope) < 0.001:
                direction = "stable"
                strength = 0.0
            elif slope > 0:
                direction = "increasing"
                strength = min(abs(correlation), 1.0)
            else:
                direction = "decreasing"
                strength = min(abs(correlation), 1.0)
            
            return {
                'direction': direction,
                'strength': strength,
                'slope': slope,
                'confidence': abs(correlation)
            }
            
        except ZeroDivisionError:
            return {'direction': 'stable', 'strength': 0.0, 'slope': 0.0, 'confidence': 0.0}
    
    def _generate_stability_alerts(self, data_list: List[StabilityData]) -> List[Dict[str, Any]]:
        """生成稳定性告警"""
        alerts = []
        
        if not data_list:
            return alerts
        
        # 计算最近的稳定性指标
        recent_data = data_list[-10:] if len(data_list) >= 10 else data_list
        
        # 位置稳定性告警
        position_variances = self._calculate_position_variances(recent_data)
        if position_variances['total_variance'] > self.thresholds['position_variance']['acceptable']:
            alerts.append({
                'type': 'stability',
                'severity': 'medium',
                'metric': 'position_stability',
                'value': position_variances['total_variance'],
                'threshold': self.thresholds['position_variance']['acceptable'],
                'message': f"位置稳定性差: 方差{position_variances['total_variance']:.2f} (阈值: {self.thresholds['position_variance']['acceptable']})"
            })
        
        # 尺寸稳定性告警
        size_variances = self._calculate_size_variances(recent_data)
        if size_variances['width_variance'] > self.thresholds['size_variance']['acceptable'] or \
           size_variances['height_variance'] > self.thresholds['size_variance']['acceptable']:
            alerts.append({
                'type': 'stability',
                'severity': 'medium',
                'metric': 'size_stability',
                'value': max(size_variances['width_variance'], size_variances['height_variance']),
                'threshold': self.thresholds['size_variance']['acceptable'],
                'message': f"尺寸稳定性差: 宽度方差{size_variances['width_variance']:.2f}, 高度方差{size_variances['height_variance']:.2f}"
            })
        
        # 可用性告警
        available_count = sum(1 for d in recent_data if d.is_available)
        availability_rate = (available_count / len(recent_data)) * 100
        
        if availability_rate < self.thresholds['availability_rate']['acceptable']:
            alerts.append({
                'type': 'availability',
                'severity': 'high',
                'metric': 'availability_rate',
                'value': availability_rate,
                'threshold': self.thresholds['availability_rate']['acceptable'],
                'message': f"可用性过低: {availability_rate:.1f}% (阈值: {self.thresholds['availability_rate']['acceptable']}%)"
            })
        
        # 布局偏移告警
        layout_shifts = [d.layout_shift for d in recent_data if d.layout_shift > 0]
        if layout_shifts:
            avg_layout_shift = statistics.mean(layout_shifts)
            if avg_layout_shift > self.thresholds['layout_shift']['acceptable']:
                alerts.append({
                    'type': 'layout',
                    'severity': 'medium',
                    'metric': 'layout_shift',
                    'value': avg_layout_shift,
                    'threshold': self.thresholds['layout_shift']['acceptable'],
                    'message': f"布局偏移过大: {avg_layout_shift:.3f} (阈值: {self.thresholds['layout_shift']['acceptable']})"
                })
        
        return alerts