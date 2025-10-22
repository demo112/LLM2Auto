"""
可访问性指标计算模块

提供元素可访问性相关的指标计算、分析和评估功能。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import statistics
import numpy as np
from enum import Enum


class AccessibilityLevel(Enum):
    """可访问性等级"""
    EXCELLENT = "excellent"  # 优秀 (90-100)
    GOOD = "good"           # 良好 (70-89)
    FAIR = "fair"           # 一般 (50-69)
    POOR = "poor"           # 较差 (30-49)
    CRITICAL = "critical"   # 严重 (0-29)


@dataclass
class AccessibilityData:
    """可访问性数据"""
    timestamp: datetime
    element_id: str
    
    # 基础可访问性属性
    has_alt_text: bool = False
    has_aria_label: bool = False
    has_role: bool = False
    has_tabindex: bool = False
    
    # 颜色对比度
    color_contrast_ratio: float = 0.0
    background_contrast_ratio: float = 0.0
    
    # 文本可读性
    font_size: float = 0.0
    line_height: float = 0.0
    text_spacing: float = 0.0
    
    # 键盘导航
    is_keyboard_accessible: bool = False
    tab_order: int = -1
    has_focus_indicator: bool = False
    
    # 屏幕阅读器支持
    aria_describedby: bool = False
    aria_expanded: Optional[bool] = None
    aria_hidden: bool = False
    
    # 语义化标签
    semantic_tag: str = ""
    heading_level: int = 0
    landmark_role: str = ""
    
    # 响应式设计
    mobile_friendly: bool = False
    touch_target_size: float = 0.0
    
    # 错误处理
    has_error_message: bool = False
    error_message_associated: bool = False


@dataclass
class AccessibilityScore:
    """可访问性评分"""
    overall_score: float
    level: AccessibilityLevel
    details: Dict[str, float] = field(default_factory=dict)
    percentage: float = 0.0
    grade: str = ""
    
    def __post_init__(self):
        self.percentage = self.overall_score
        if self.overall_score >= 90:
            self.grade = "A+"
            self.level = AccessibilityLevel.EXCELLENT
        elif self.overall_score >= 80:
            self.grade = "A"
            self.level = AccessibilityLevel.GOOD
        elif self.overall_score >= 70:
            self.grade = "B"
            self.level = AccessibilityLevel.GOOD
        elif self.overall_score >= 60:
            self.grade = "C"
            self.level = AccessibilityLevel.FAIR
        elif self.overall_score >= 50:
            self.grade = "D"
            self.level = AccessibilityLevel.FAIR
        else:
            self.grade = "F"
            self.level = AccessibilityLevel.POOR


@dataclass
class AccessibilityTrend:
    """可访问性趋势分析"""
    element_id: str
    period_days: int
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # 0-1, 趋势强度
    average_score: float
    score_variance: float
    improvement_rate: float  # 每天的改进率
    regression_slope: float
    regression_r_squared: float
    recommendations: List[str] = field(default_factory=list)


class AccessibilityMetrics:
    """可访问性指标计算器"""
    
    def __init__(self):
        self.accessibility_data: Dict[str, List[AccessibilityData]] = {}
        self.baseline_scores: Dict[str, AccessibilityScore] = {}
        
        # 可访问性权重配置
        self.weights = {
            'basic_attributes': 0.20,    # 基础属性
            'color_contrast': 0.15,      # 颜色对比度
            'text_readability': 0.15,    # 文本可读性
            'keyboard_navigation': 0.20, # 键盘导航
            'screen_reader': 0.15,       # 屏幕阅读器
            'semantic_markup': 0.10,     # 语义化标签
            'responsive_design': 0.05    # 响应式设计
        }
        
        # 评分阈值
        self.thresholds = {
            'color_contrast_min': 4.5,   # WCAG AA标准
            'color_contrast_aaa': 7.0,   # WCAG AAA标准
            'font_size_min': 12.0,       # 最小字体大小
            'touch_target_min': 44.0,    # 最小触摸目标大小(px)
            'line_height_min': 1.2       # 最小行高比例
        }
    
    def add_accessibility_data(self, data: AccessibilityData) -> None:
        """添加可访问性数据"""
        if data.element_id not in self.accessibility_data:
            self.accessibility_data[data.element_id] = []
        self.accessibility_data[data.element_id].append(data)
    
    def calculate_accessibility_score(self, element_id: str) -> Optional[AccessibilityScore]:
        """计算可访问性评分"""
        if element_id not in self.accessibility_data or not self.accessibility_data[element_id]:
            return None
        
        latest_data = self.accessibility_data[element_id][-1]
        
        # 计算各项评分
        basic_score = self._calculate_basic_attributes_score(latest_data)
        contrast_score = self._calculate_color_contrast_score(latest_data)
        readability_score = self._calculate_text_readability_score(latest_data)
        keyboard_score = self._calculate_keyboard_navigation_score(latest_data)
        screen_reader_score = self._calculate_screen_reader_score(latest_data)
        semantic_score = self._calculate_semantic_markup_score(latest_data)
        responsive_score = self._calculate_responsive_design_score(latest_data)
        
        # 计算加权总分
        overall_score = (
            basic_score * self.weights['basic_attributes'] +
            contrast_score * self.weights['color_contrast'] +
            readability_score * self.weights['text_readability'] +
            keyboard_score * self.weights['keyboard_navigation'] +
            screen_reader_score * self.weights['screen_reader'] +
            semantic_score * self.weights['semantic_markup'] +
            responsive_score * self.weights['responsive_design']
        )
        
        details = {
            'basic_attributes': basic_score,
            'color_contrast': contrast_score,
            'text_readability': readability_score,
            'keyboard_navigation': keyboard_score,
            'screen_reader': screen_reader_score,
            'semantic_markup': semantic_score,
            'responsive_design': responsive_score
        }
        
        return AccessibilityScore(
            overall_score=overall_score,
            level=AccessibilityLevel.FAIR,  # 将在__post_init__中重新计算
            details=details
        )
    
    def _calculate_basic_attributes_score(self, data: AccessibilityData) -> float:
        """计算基础属性评分"""
        score = 0.0
        total_checks = 4
        
        if data.has_alt_text:
            score += 25.0
        if data.has_aria_label:
            score += 25.0
        if data.has_role:
            score += 25.0
        if data.has_tabindex:
            score += 25.0
        
        return score
    
    def _calculate_color_contrast_score(self, data: AccessibilityData) -> float:
        """计算颜色对比度评分"""
        contrast_ratio = max(data.color_contrast_ratio, data.background_contrast_ratio)
        
        if contrast_ratio >= self.thresholds['color_contrast_aaa']:
            return 100.0
        elif contrast_ratio >= self.thresholds['color_contrast_min']:
            return 80.0
        elif contrast_ratio >= 3.0:
            return 60.0
        elif contrast_ratio >= 2.0:
            return 40.0
        else:
            return 20.0
    
    def _calculate_text_readability_score(self, data: AccessibilityData) -> float:
        """计算文本可读性评分"""
        score = 0.0
        
        # 字体大小评分
        if data.font_size >= 16.0:
            score += 40.0
        elif data.font_size >= self.thresholds['font_size_min']:
            score += 25.0
        else:
            score += 10.0
        
        # 行高评分
        if data.line_height >= 1.5:
            score += 30.0
        elif data.line_height >= self.thresholds['line_height_min']:
            score += 20.0
        else:
            score += 10.0
        
        # 文本间距评分
        if data.text_spacing >= 0.12:
            score += 30.0
        elif data.text_spacing >= 0.08:
            score += 20.0
        else:
            score += 10.0
        
        return score
    
    def _calculate_keyboard_navigation_score(self, data: AccessibilityData) -> float:
        """计算键盘导航评分"""
        score = 0.0
        
        if data.is_keyboard_accessible:
            score += 40.0
        if data.tab_order >= 0:
            score += 30.0
        if data.has_focus_indicator:
            score += 30.0
        
        return score
    
    def _calculate_screen_reader_score(self, data: AccessibilityData) -> float:
        """计算屏幕阅读器支持评分"""
        score = 0.0
        
        if data.aria_describedby:
            score += 30.0
        if data.aria_expanded is not None:
            score += 30.0
        if not data.aria_hidden:  # aria-hidden=false是好的
            score += 40.0
        
        return score
    
    def _calculate_semantic_markup_score(self, data: AccessibilityData) -> float:
        """计算语义化标签评分"""
        score = 0.0
        
        if data.semantic_tag and data.semantic_tag != "div":
            score += 40.0
        if data.heading_level > 0:
            score += 30.0
        if data.landmark_role:
            score += 30.0
        
        return score
    
    def _calculate_responsive_design_score(self, data: AccessibilityData) -> float:
        """计算响应式设计评分"""
        score = 0.0
        
        if data.mobile_friendly:
            score += 50.0
        if data.touch_target_size >= self.thresholds['touch_target_min']:
            score += 50.0
        
        return score
    
    def analyze_accessibility_trend(self, element_id: str, days: int = 7) -> Optional[AccessibilityTrend]:
        """分析可访问性趋势"""
        if element_id not in self.accessibility_data:
            return None
        
        data_points = self.accessibility_data[element_id]
        if len(data_points) < 2:
            return None
        
        # 获取指定天数内的数据
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        recent_data = [d for d in data_points if d.timestamp.timestamp() >= cutoff_time]
        
        if len(recent_data) < 2:
            return None
        
        # 计算评分序列
        scores = []
        for data in recent_data:
            temp_data = {element_id: [data]}
            old_data = self.accessibility_data[element_id]
            self.accessibility_data[element_id] = [data]
            score = self.calculate_accessibility_score(element_id)
            self.accessibility_data[element_id] = old_data
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
        improvement_rate = slope  # 每个时间点的改进率
        trend_strength = min(abs(slope) / 10.0, 1.0)  # 归一化趋势强度
        
        # 生成建议
        recommendations = self._generate_accessibility_recommendations(recent_data[-1], avg_score)
        
        return AccessibilityTrend(
            element_id=element_id,
            period_days=days,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            average_score=avg_score,
            score_variance=score_variance,
            improvement_rate=improvement_rate,
            regression_slope=slope,
            regression_r_squared=r_squared,
            recommendations=recommendations
        )
    
    def _generate_accessibility_recommendations(self, data: AccessibilityData, avg_score: float) -> List[str]:
        """生成可访问性改进建议"""
        recommendations = []
        
        # 基础属性建议
        if not data.has_alt_text:
            recommendations.append("添加alt属性为图片提供替代文本")
        if not data.has_aria_label:
            recommendations.append("添加aria-label属性提供可访问的名称")
        if not data.has_role:
            recommendations.append("添加role属性明确元素的语义角色")
        
        # 颜色对比度建议
        if data.color_contrast_ratio < self.thresholds['color_contrast_min']:
            recommendations.append("提高颜色对比度以满足WCAG AA标准(4.5:1)")
        
        # 文本可读性建议
        if data.font_size < self.thresholds['font_size_min']:
            recommendations.append("增加字体大小以提高可读性")
        if data.line_height < self.thresholds['line_height_min']:
            recommendations.append("增加行高以改善文本可读性")
        
        # 键盘导航建议
        if not data.is_keyboard_accessible:
            recommendations.append("确保元素可通过键盘访问")
        if not data.has_focus_indicator:
            recommendations.append("添加明显的焦点指示器")
        
        # 屏幕阅读器建议
        if not data.aria_describedby:
            recommendations.append("使用aria-describedby提供额外的描述信息")
        
        # 语义化建议
        if not data.semantic_tag or data.semantic_tag == "div":
            recommendations.append("使用语义化HTML标签替代通用div元素")
        
        # 响应式设计建议
        if not data.mobile_friendly:
            recommendations.append("优化移动设备的可访问性")
        if data.touch_target_size < self.thresholds['touch_target_min']:
            recommendations.append("增加触摸目标大小至少44px")
        
        return recommendations
    
    def get_accessibility_summary(self, element_id: str) -> Dict[str, Any]:
        """获取可访问性摘要"""
        if element_id not in self.accessibility_data:
            return {}
        
        current_score = self.calculate_accessibility_score(element_id)
        trend = self.analyze_accessibility_trend(element_id)
        
        summary = {
            'element_id': element_id,
            'current_score': current_score.overall_score if current_score else 0,
            'accessibility_level': current_score.level.value if current_score else 'unknown',
            'grade': current_score.grade if current_score else 'N/A',
            'data_points': len(self.accessibility_data[element_id]),
            'last_updated': self.accessibility_data[element_id][-1].timestamp.isoformat()
        }
        
        if trend:
            summary.update({
                'trend_direction': trend.trend_direction,
                'trend_strength': trend.trend_strength,
                'improvement_rate': trend.improvement_rate,
                'recommendations': trend.recommendations
            })
        
        if current_score:
            summary['score_breakdown'] = current_score.details
        
        return summary
    
    def set_baseline(self, element_id: str) -> bool:
        """设置基线可访问性评分"""
        score = self.calculate_accessibility_score(element_id)
        if score:
            self.baseline_scores[element_id] = score
            return True
        return False
    
    def compare_with_baseline(self, element_id: str) -> Optional[Dict[str, Any]]:
        """与基线进行比较"""
        if element_id not in self.baseline_scores:
            return None
        
        current_score = self.calculate_accessibility_score(element_id)
        if not current_score:
            return None
        
        baseline = self.baseline_scores[element_id]
        
        return {
            'baseline_score': baseline.overall_score,
            'current_score': current_score.overall_score,
            'improvement': current_score.overall_score - baseline.overall_score,
            'improvement_percentage': ((current_score.overall_score - baseline.overall_score) / baseline.overall_score) * 100,
            'level_change': f"{baseline.level.value} -> {current_score.level.value}",
            'grade_change': f"{baseline.grade} -> {current_score.grade}"
        }