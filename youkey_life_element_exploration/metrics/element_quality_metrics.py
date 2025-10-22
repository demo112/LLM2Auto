# -*- encoding=utf8 -*-
"""
元素质量指标计算模块

提供各种元素质量指标的计算方法
"""

import math
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class QualityScore:
    """质量分数"""
    score: float
    max_score: float
    details: Dict[str, Any]
    
    @property
    def percentage(self) -> float:
        """获取百分比分数"""
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0.0
    
    @property
    def grade(self) -> str:
        """获取等级"""
        percentage = self.percentage
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"


class ElementQualityMetrics:
    """元素质量指标计算器"""
    
    def __init__(self):
        """初始化指标计算器"""
        self.history_data: Dict[str, List[Dict[str, Any]]] = {}
    
    def calculate_performance_score(self, element_data: Dict[str, Any]) -> QualityScore:
        """
        计算性能分数
        
        Args:
            element_data: 元素数据
            
        Returns:
            QualityScore: 性能分数
        """
        details = {}
        total_score = 0.0
        max_score = 100.0
        
        # 响应时间分数 (40分)
        response_time = element_data.get('response_time', 0.0)
        if response_time <= 1.0:
            response_score = 40.0
        elif response_time <= 2.0:
            response_score = 30.0
        elif response_time <= 3.0:
            response_score = 20.0
        elif response_time <= 5.0:
            response_score = 10.0
        else:
            response_score = 0.0
        
        total_score += response_score
        details['response_time_score'] = response_score
        details['response_time'] = response_time
        
        # 加载时间分数 (30分)
        load_time = element_data.get('load_time', 0.0)
        if load_time <= 0.5:
            load_score = 30.0
        elif load_time <= 1.0:
            load_score = 25.0
        elif load_time <= 2.0:
            load_score = 20.0
        elif load_time <= 3.0:
            load_score = 10.0
        else:
            load_score = 0.0
        
        total_score += load_score
        details['load_time_score'] = load_score
        details['load_time'] = load_time
        
        # 渲染时间分数 (30分)
        render_time = element_data.get('render_time', 0.0)
        if render_time <= 0.1:
            render_score = 30.0
        elif render_time <= 0.3:
            render_score = 25.0
        elif render_time <= 0.5:
            render_score = 20.0
        elif render_time <= 1.0:
            render_score = 10.0
        else:
            render_score = 0.0
        
        total_score += render_score
        details['render_time_score'] = render_score
        details['render_time'] = render_time
        
        return QualityScore(score=total_score, max_score=max_score, details=details)
    
    def calculate_visibility_score(self, element_data: Dict[str, Any]) -> QualityScore:
        """
        计算可见性分数
        
        Args:
            element_data: 元素数据
            
        Returns:
            QualityScore: 可见性分数
        """
        details = {}
        total_score = 0.0
        max_score = 100.0
        
        # 显示状态 (30分)
        is_displayed = element_data.get('is_displayed', False)
        display_score = 30.0 if is_displayed else 0.0
        total_score += display_score
        details['display_score'] = display_score
        details['is_displayed'] = is_displayed
        
        # 可见状态 (25分)
        is_visible = element_data.get('is_visible', False)
        visible_score = 25.0 if is_visible else 0.0
        total_score += visible_score
        details['visible_score'] = visible_score
        details['is_visible'] = is_visible
        
        # 透明度 (20分)
        opacity = element_data.get('opacity', 1.0)
        opacity_score = opacity * 20.0
        total_score += opacity_score
        details['opacity_score'] = opacity_score
        details['opacity'] = opacity
        
        # 位置在视口内 (15分)
        in_viewport = element_data.get('in_viewport', True)
        viewport_score = 15.0 if in_viewport else 0.0
        total_score += viewport_score
        details['viewport_score'] = viewport_score
        details['in_viewport'] = in_viewport
        
        # Z-index层级 (10分)
        z_index = element_data.get('z_index', 0)
        z_index_score = min(z_index / 10.0 * 10.0, 10.0) if z_index >= 0 else 0.0
        total_score += z_index_score
        details['z_index_score'] = z_index_score
        details['z_index'] = z_index
        
        return QualityScore(score=total_score, max_score=max_score, details=details)
    
    def calculate_accessibility_score(self, element_data: Dict[str, Any]) -> QualityScore:
        """
        计算可访问性分数
        
        Args:
            element_data: 元素数据
            
        Returns:
            QualityScore: 可访问性分数
        """
        details = {}
        total_score = 0.0
        max_score = 100.0
        
        # ARIA标签 (25分)
        has_aria_label = bool(element_data.get('aria_label'))
        aria_score = 25.0 if has_aria_label else 0.0
        total_score += aria_score
        details['aria_score'] = aria_score
        details['has_aria_label'] = has_aria_label
        
        # Alt文本 (20分)
        has_alt_text = bool(element_data.get('alt_text'))
        alt_score = 20.0 if has_alt_text else 0.0
        total_score += alt_score
        details['alt_score'] = alt_score
        details['has_alt_text'] = has_alt_text
        
        # 颜色对比度 (25分)
        contrast_ratio = element_data.get('color_contrast_ratio', 0.0)
        if contrast_ratio >= 7.0:  # AAA级别
            contrast_score = 25.0
        elif contrast_ratio >= 4.5:  # AA级别
            contrast_score = 20.0
        elif contrast_ratio >= 3.0:  # AA大文本级别
            contrast_score = 15.0
        else:
            contrast_score = 0.0
        
        total_score += contrast_score
        details['contrast_score'] = contrast_score
        details['color_contrast_ratio'] = contrast_ratio
        
        # 键盘可访问性 (20分)
        keyboard_accessible = element_data.get('keyboard_accessible', False)
        keyboard_score = 20.0 if keyboard_accessible else 0.0
        total_score += keyboard_score
        details['keyboard_score'] = keyboard_score
        details['keyboard_accessible'] = keyboard_accessible
        
        # 焦点指示器 (10分)
        has_focus_indicator = element_data.get('has_focus_indicator', False)
        focus_score = 10.0 if has_focus_indicator else 0.0
        total_score += focus_score
        details['focus_score'] = focus_score
        details['has_focus_indicator'] = has_focus_indicator
        
        return QualityScore(score=total_score, max_score=max_score, details=details)
    
    def calculate_stability_score(self, element_id: str, element_data: Dict[str, Any]) -> QualityScore:
        """
        计算稳定性分数
        
        Args:
            element_id: 元素ID
            element_data: 元素数据
            
        Returns:
            QualityScore: 稳定性分数
        """
        details = {}
        total_score = 0.0
        max_score = 100.0
        
        # 获取历史数据
        history = self.history_data.get(element_id, [])
        
        # 位置稳定性 (40分)
        position_stability = self._calculate_position_stability(element_data, history)
        position_score = position_stability * 40.0
        total_score += position_score
        details['position_score'] = position_score
        details['position_stability'] = position_stability
        
        # 尺寸稳定性 (30分)
        size_stability = self._calculate_size_stability(element_data, history)
        size_score = size_stability * 30.0
        total_score += size_score
        details['size_score'] = size_score
        details['size_stability'] = size_stability
        
        # 属性稳定性 (20分)
        attribute_stability = self._calculate_attribute_stability(element_data, history)
        attribute_score = attribute_stability * 20.0
        total_score += attribute_score
        details['attribute_score'] = attribute_score
        details['attribute_stability'] = attribute_stability
        
        # 可用性稳定性 (10分)
        availability_stability = self._calculate_availability_stability(element_data, history)
        availability_score = availability_stability * 10.0
        total_score += availability_score
        details['availability_score'] = availability_score
        details['availability_stability'] = availability_stability
        
        # 更新历史数据
        self._update_history(element_id, element_data)
        
        return QualityScore(score=total_score, max_score=max_score, details=details)
    
    def calculate_interaction_score(self, element_data: Dict[str, Any]) -> QualityScore:
        """
        计算交互性分数
        
        Args:
            element_data: 元素数据
            
        Returns:
            QualityScore: 交互性分数
        """
        details = {}
        total_score = 0.0
        max_score = 100.0
        
        # 点击成功率 (40分)
        click_success_rate = element_data.get('click_success_rate', 0.0)
        click_score = click_success_rate * 40.0
        total_score += click_score
        details['click_score'] = click_score
        details['click_success_rate'] = click_success_rate
        
        # 输入成功率 (30分)
        input_success_rate = element_data.get('input_success_rate', 0.0)
        input_score = input_success_rate * 30.0
        total_score += input_score
        details['input_score'] = input_score
        details['input_success_rate'] = input_success_rate
        
        # 响应性 (20分)
        is_enabled = element_data.get('is_enabled', False)
        is_interactive = element_data.get('is_interactive', False)
        responsiveness = 1.0 if (is_enabled and is_interactive) else 0.0
        responsiveness_score = responsiveness * 20.0
        total_score += responsiveness_score
        details['responsiveness_score'] = responsiveness_score
        details['responsiveness'] = responsiveness
        
        # 反馈质量 (10分)
        has_feedback = element_data.get('has_feedback', False)
        feedback_score = 10.0 if has_feedback else 0.0
        total_score += feedback_score
        details['feedback_score'] = feedback_score
        details['has_feedback'] = has_feedback
        
        return QualityScore(score=total_score, max_score=max_score, details=details)
    
    def calculate_overall_score(self, element_data: Dict[str, Any], element_id: str) -> QualityScore:
        """
        计算综合质量分数
        
        Args:
            element_data: 元素数据
            element_id: 元素ID
            
        Returns:
            QualityScore: 综合质量分数
        """
        # 计算各项分数
        performance = self.calculate_performance_score(element_data)
        visibility = self.calculate_visibility_score(element_data)
        accessibility = self.calculate_accessibility_score(element_data)
        stability = self.calculate_stability_score(element_id, element_data)
        interaction = self.calculate_interaction_score(element_data)
        
        # 权重配置
        weights = {
            'performance': 0.25,
            'visibility': 0.20,
            'accessibility': 0.20,
            'stability': 0.20,
            'interaction': 0.15
        }
        
        # 计算加权平均分
        total_score = (
            performance.score * weights['performance'] +
            visibility.score * weights['visibility'] +
            accessibility.score * weights['accessibility'] +
            stability.score * weights['stability'] +
            interaction.score * weights['interaction']
        )
        
        details = {
            'performance': performance,
            'visibility': visibility,
            'accessibility': accessibility,
            'stability': stability,
            'interaction': interaction,
            'weights': weights
        }
        
        return QualityScore(score=total_score, max_score=100.0, details=details)
    
    def _calculate_position_stability(self, current_data: Dict[str, Any], history: List[Dict[str, Any]]) -> float:
        """计算位置稳定性"""
        if len(history) < 2:
            return 1.0
        
        current_pos = current_data.get('position', {})
        current_x = current_pos.get('x', 0)
        current_y = current_pos.get('y', 0)
        
        # 计算位置变化的标准差
        x_positions = [h.get('position', {}).get('x', 0) for h in history[-10:]]
        y_positions = [h.get('position', {}).get('y', 0) for h in history[-10:]]
        
        x_positions.append(current_x)
        y_positions.append(current_y)
        
        if len(x_positions) < 2:
            return 1.0
        
        try:
            x_std = statistics.stdev(x_positions)
            y_std = statistics.stdev(y_positions)
            
            # 位置变化越小，稳定性越高
            position_variance = math.sqrt(x_std ** 2 + y_std ** 2)
            stability = max(0.0, 1.0 - position_variance / 100.0)  # 假设100像素为最大容忍变化
            
            return min(1.0, stability)
        except statistics.StatisticsError:
            return 1.0
    
    def _calculate_size_stability(self, current_data: Dict[str, Any], history: List[Dict[str, Any]]) -> float:
        """计算尺寸稳定性"""
        if len(history) < 2:
            return 1.0
        
        current_size = current_data.get('size', {})
        current_width = current_size.get('width', 0)
        current_height = current_size.get('height', 0)
        
        # 计算尺寸变化的标准差
        widths = [h.get('size', {}).get('width', 0) for h in history[-10:]]
        heights = [h.get('size', {}).get('height', 0) for h in history[-10:]]
        
        widths.append(current_width)
        heights.append(current_height)
        
        if len(widths) < 2:
            return 1.0
        
        try:
            width_std = statistics.stdev(widths)
            height_std = statistics.stdev(heights)
            
            # 尺寸变化越小，稳定性越高
            avg_width = statistics.mean(widths)
            avg_height = statistics.mean(heights)
            
            width_cv = width_std / avg_width if avg_width > 0 else 0
            height_cv = height_std / avg_height if avg_height > 0 else 0
            
            stability = max(0.0, 1.0 - (width_cv + height_cv) / 2)
            
            return min(1.0, stability)
        except (statistics.StatisticsError, ZeroDivisionError):
            return 1.0
    
    def _calculate_attribute_stability(self, current_data: Dict[str, Any], history: List[Dict[str, Any]]) -> float:
        """计算属性稳定性"""
        if len(history) < 2:
            return 1.0
        
        # 检查关键属性的变化
        key_attributes = ['class', 'id', 'tag_name', 'text']
        stable_count = 0
        total_count = len(key_attributes)
        
        for attr in key_attributes:
            current_value = current_data.get(attr)
            
            # 检查最近几次的值是否一致
            recent_values = [h.get(attr) for h in history[-5:]]
            recent_values.append(current_value)
            
            # 计算一致性
            unique_values = set(recent_values)
            if len(unique_values) <= 1:
                stable_count += 1
            elif len(unique_values) <= 2:
                stable_count += 0.5
        
        return stable_count / total_count if total_count > 0 else 1.0
    
    def _calculate_availability_stability(self, current_data: Dict[str, Any], history: List[Dict[str, Any]]) -> float:
        """计算可用性稳定性"""
        if len(history) < 2:
            return 1.0
        
        current_available = current_data.get('is_displayed', False) and current_data.get('is_enabled', False)
        
        # 检查最近的可用性状态
        recent_availability = []
        for h in history[-10:]:
            available = h.get('is_displayed', False) and h.get('is_enabled', False)
            recent_availability.append(available)
        
        recent_availability.append(current_available)
        
        # 计算可用性的一致性
        available_count = sum(recent_availability)
        total_count = len(recent_availability)
        
        # 如果大部分时间都可用或都不可用，则认为稳定
        availability_ratio = available_count / total_count
        stability = 1.0 - abs(availability_ratio - 0.5) * 2  # 越接近0或1越稳定
        
        return max(0.0, stability)
    
    def _update_history(self, element_id: str, element_data: Dict[str, Any]) -> None:
        """更新历史数据"""
        if element_id not in self.history_data:
            self.history_data[element_id] = []
        
        # 添加时间戳
        data_with_timestamp = element_data.copy()
        data_with_timestamp['timestamp'] = datetime.now()
        
        self.history_data[element_id].append(data_with_timestamp)
        
        # 保持最近50条记录
        if len(self.history_data[element_id]) > 50:
            self.history_data[element_id] = self.history_data[element_id][-50:]
    
    def get_trend_analysis(self, element_id: str, metric_name: str, days: int = 7) -> Dict[str, Any]:
        """
        获取趋势分析
        
        Args:
            element_id: 元素ID
            metric_name: 指标名称
            days: 分析天数
            
        Returns:
            Dict[str, Any]: 趋势分析结果
        """
        history = self.history_data.get(element_id, [])
        if not history:
            return {'trend': 'no_data', 'values': [], 'analysis': '无历史数据'}
        
        # 过滤指定天数内的数据
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_data = [
            h for h in history 
            if h.get('timestamp', datetime.now()) >= cutoff_time
        ]
        
        if len(recent_data) < 2:
            return {'trend': 'insufficient_data', 'values': [], 'analysis': '数据不足'}
        
        # 提取指标值
        values = []
        timestamps = []
        for data in recent_data:
            if metric_name in data:
                values.append(data[metric_name])
                timestamps.append(data.get('timestamp', datetime.now()))
        
        if len(values) < 2:
            return {'trend': 'no_metric_data', 'values': [], 'analysis': f'无{metric_name}数据'}
        
        # 计算趋势
        trend_analysis = self._analyze_trend(values)
        
        return {
            'trend': trend_analysis['direction'],
            'values': values,
            'timestamps': [t.isoformat() for t in timestamps],
            'analysis': trend_analysis['description'],
            'slope': trend_analysis['slope'],
            'correlation': trend_analysis['correlation']
        }
    
    def _analyze_trend(self, values: List[float]) -> Dict[str, Any]:
        """分析数值趋势"""
        if len(values) < 2:
            return {'direction': 'stable', 'description': '数据不足', 'slope': 0, 'correlation': 0}
        
        # 计算线性回归
        n = len(values)
        x = list(range(n))
        
        # 计算斜率
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # 计算相关系数
        try:
            correlation = statistics.correlation(x, values)
        except statistics.StatisticsError:
            correlation = 0
        
        # 判断趋势方向
        if abs(slope) < 0.01:  # 阈值可调整
            direction = 'stable'
            description = '指标保持稳定'
        elif slope > 0:
            direction = 'increasing'
            description = f'指标呈上升趋势，斜率: {slope:.4f}'
        else:
            direction = 'decreasing'
            description = f'指标呈下降趋势，斜率: {slope:.4f}'
        
        return {
            'direction': direction,
            'description': description,
            'slope': slope,
            'correlation': correlation
        }