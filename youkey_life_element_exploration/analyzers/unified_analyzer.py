# -*- encoding=utf8 -*-
"""
统一分析器

合并多个分析器功能，提供统一的分析接口
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import statistics
import logging


class AnalysisType(Enum):
    """分析类型"""
    ELEMENT = "element"
    QUALITY = "quality"
    TREND = "trend"
    PATTERN = "pattern"
    CORRELATION = "correlation"


class AnalysisLevel(Enum):
    """分析级别"""
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


@dataclass
class UnifiedAnalysisResult:
    """统一分析结果"""
    analysis_id: str
    analysis_type: AnalysisType
    level: AnalysisLevel
    timestamp: datetime
    
    # 核心结果
    success: bool
    confidence: float
    data_count: int
    
    # 分析结果
    findings: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # 统计信息
    statistics: Dict[str, Any] = field(default_factory=dict)
    
    # 质量信息
    quality_score: Optional[float] = None
    quality_level: Optional[str] = None
    
    # 趋势信息
    trend_direction: Optional[str] = None
    trend_strength: Optional[float] = None
    
    # 模式信息
    patterns: Dict[str, Any] = field(default_factory=dict)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedAnalyzer:
    """统一分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analysis_history = []
        self.cache = {}
    
    def analyze(self, data: Any, analysis_type: AnalysisType, 
               level: AnalysisLevel = AnalysisLevel.BASIC) -> UnifiedAnalysisResult:
        """统一分析入口"""
        analysis_id = f"{analysis_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            if analysis_type == AnalysisType.ELEMENT:
                result = self._analyze_elements(data, level, analysis_id)
            elif analysis_type == AnalysisType.QUALITY:
                result = self._analyze_quality(data, level, analysis_id)
            elif analysis_type == AnalysisType.TREND:
                result = self._analyze_trend(data, level, analysis_id)
            elif analysis_type == AnalysisType.PATTERN:
                result = self._analyze_pattern(data, level, analysis_id)
            elif analysis_type == AnalysisType.CORRELATION:
                result = self._analyze_correlation(data, level, analysis_id)
            else:
                result = self._create_error_result(analysis_id, analysis_type, level, "不支持的分析类型")
            
            self.analysis_history.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"分析失败: {e}")
            return self._create_error_result(analysis_id, analysis_type, level, str(e))
    
    def analyze_batch(self, data_list: List[Any], analysis_type: AnalysisType,
                     level: AnalysisLevel = AnalysisLevel.BASIC) -> List[UnifiedAnalysisResult]:
        """批量分析"""
        results = []
        for i, data in enumerate(data_list):
            try:
                result = self.analyze(data, analysis_type, level)
                result.analysis_id = f"{result.analysis_id}_batch_{i}"
                results.append(result)
            except Exception as e:
                self.logger.error(f"批量分析第{i}项失败: {e}")
        
        return results
    
    def get_analysis_summary(self, analysis_type: Optional[AnalysisType] = None) -> Dict[str, Any]:
        """获取分析摘要"""
        filtered_history = self.analysis_history
        if analysis_type:
            filtered_history = [r for r in self.analysis_history if r.analysis_type == analysis_type]
        
        if not filtered_history:
            return {}
        
        return {
            'total_analyses': len(filtered_history),
            'success_rate': sum(1 for r in filtered_history if r.success) / len(filtered_history),
            'average_confidence': statistics.mean(r.confidence for r in filtered_history if r.confidence > 0),
            'analysis_types': list(set(r.analysis_type.value for r in filtered_history)),
            'last_analysis': filtered_history[-1].timestamp,
            'total_data_processed': sum(r.data_count for r in filtered_history)
        }
    
    def _analyze_elements(self, data: Any, level: AnalysisLevel, analysis_id: str) -> UnifiedAnalysisResult:
        """元素分析"""
        if not isinstance(data, list):
            data = [data] if data else []
        
        data_count = len(data)
        findings = []
        insights = []
        recommendations = []
        statistics_data = {}
        
        if data_count == 0:
            return self._create_empty_result(analysis_id, AnalysisType.ELEMENT, level)
        
        # 基础统计
        element_types = {}
        locator_types = {}
        
        for item in data:
            if isinstance(item, dict):
                # 元素类型统计
                element_type = item.get('type', 'unknown')
                element_types[element_type] = element_types.get(element_type, 0) + 1
                
                # 定位器类型统计
                locator = item.get('locator', '')
                if locator.startswith('#'):
                    locator_types['id'] = locator_types.get('id', 0) + 1
                elif locator.startswith('.'):
                    locator_types['class'] = locator_types.get('class', 0) + 1
                elif '.png' in locator or '.jpg' in locator:
                    locator_types['image'] = locator_types.get('image', 0) + 1
                else:
                    locator_types['other'] = locator_types.get('other', 0) + 1
        
        statistics_data = {
            'element_types': element_types,
            'locator_types': locator_types,
            'total_elements': data_count
        }
        
        # 生成发现和洞察
        findings.append(f"分析了 {data_count} 个元素")
        
        if element_types:
            most_common_type = max(element_types, key=element_types.get)
            insights.append(f"最常见的元素类型是 {most_common_type} ({element_types[most_common_type]} 个)")
        
        if locator_types:
            most_common_locator = max(locator_types, key=locator_types.get)
            insights.append(f"最常用的定位方式是 {most_common_locator} ({locator_types[most_common_locator]} 个)")
        
        # 生成建议
        if locator_types.get('other', 0) > data_count * 0.3:
            recommendations.append("建议优化定位器策略，减少其他类型定位器的使用")
        
        if len(element_types) > 10:
            recommendations.append("元素类型过多，建议进行分类整理")
        
        return UnifiedAnalysisResult(
            analysis_id=analysis_id,
            analysis_type=AnalysisType.ELEMENT,
            level=level,
            timestamp=datetime.now(),
            success=True,
            confidence=0.9,
            data_count=data_count,
            findings=findings,
            insights=insights,
            recommendations=recommendations,
            statistics=statistics_data
        )
    
    def _analyze_quality(self, data: Any, level: AnalysisLevel, analysis_id: str) -> UnifiedAnalysisResult:
        """质量分析"""
        if not isinstance(data, list):
            data = [data] if data else []
        
        data_count = len(data)
        
        if data_count == 0:
            return self._create_empty_result(analysis_id, AnalysisType.QUALITY, level)
        
        # 质量评分计算
        quality_scores = []
        completeness_scores = []
        accuracy_scores = []
        
        for item in data:
            if isinstance(item, dict):
                # 完整性评分
                required_fields = ['locator', 'type']
                completeness = sum(1 for field in required_fields if item.get(field)) / len(required_fields)
                completeness_scores.append(completeness)
                
                # 准确性评分（基于置信度）
                confidence = item.get('confidence', 0.5)
                accuracy_scores.append(confidence)
                
                # 综合质量评分
                quality_score = (completeness + confidence) / 2
                quality_scores.append(quality_score)
        
        # 计算平均质量
        avg_quality = statistics.mean(quality_scores) if quality_scores else 0
        avg_completeness = statistics.mean(completeness_scores) if completeness_scores else 0
        avg_accuracy = statistics.mean(accuracy_scores) if accuracy_scores else 0
        
        # 确定质量等级
        if avg_quality >= 0.8:
            quality_level = "excellent"
        elif avg_quality >= 0.6:
            quality_level = "good"
        elif avg_quality >= 0.4:
            quality_level = "fair"
        else:
            quality_level = "poor"
        
        findings = [f"分析了 {data_count} 个项目的质量"]
        insights = [
            f"平均质量评分: {avg_quality:.2f}",
            f"完整性评分: {avg_completeness:.2f}",
            f"准确性评分: {avg_accuracy:.2f}"
        ]
        
        recommendations = []
        if avg_completeness < 0.8:
            recommendations.append("建议补充缺失的必要字段信息")
        if avg_accuracy < 0.7:
            recommendations.append("建议提高元素识别的准确性")
        
        return UnifiedAnalysisResult(
            analysis_id=analysis_id,
            analysis_type=AnalysisType.QUALITY,
            level=level,
            timestamp=datetime.now(),
            success=True,
            confidence=0.85,
            data_count=data_count,
            findings=findings,
            insights=insights,
            recommendations=recommendations,
            quality_score=avg_quality,
            quality_level=quality_level,
            statistics={
                'average_quality': avg_quality,
                'completeness': avg_completeness,
                'accuracy': avg_accuracy,
                'quality_distribution': {
                    'excellent': sum(1 for s in quality_scores if s >= 0.8),
                    'good': sum(1 for s in quality_scores if 0.6 <= s < 0.8),
                    'fair': sum(1 for s in quality_scores if 0.4 <= s < 0.6),
                    'poor': sum(1 for s in quality_scores if s < 0.4)
                }
            }
        )
    
    def _analyze_trend(self, data: Any, level: AnalysisLevel, analysis_id: str) -> UnifiedAnalysisResult:
        """趋势分析"""
        if not isinstance(data, list) or len(data) < 3:
            return self._create_insufficient_data_result(analysis_id, AnalysisType.TREND, level)
        
        # 提取数值数据
        values = []
        for item in data:
            if isinstance(item, (int, float)):
                values.append(item)
            elif isinstance(item, dict) and 'value' in item:
                values.append(item['value'])
        
        if len(values) < 3:
            return self._create_insufficient_data_result(analysis_id, AnalysisType.TREND, level)
        
        # 简单趋势分析
        trend_direction, trend_strength = self._calculate_trend(values)
        
        findings = [f"分析了 {len(values)} 个数据点的趋势"]
        insights = [f"趋势方向: {trend_direction}", f"趋势强度: {trend_strength:.2f}"]
        
        recommendations = []
        if trend_direction == "decreasing" and trend_strength > 0.5:
            recommendations.append("检测到明显下降趋势，建议关注并采取改进措施")
        elif trend_direction == "stable":
            recommendations.append("趋势相对稳定，继续监控")
        
        return UnifiedAnalysisResult(
            analysis_id=analysis_id,
            analysis_type=AnalysisType.TREND,
            level=level,
            timestamp=datetime.now(),
            success=True,
            confidence=0.8,
            data_count=len(values),
            findings=findings,
            insights=insights,
            recommendations=recommendations,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            statistics={
                'data_points': len(values),
                'min_value': min(values),
                'max_value': max(values),
                'mean_value': statistics.mean(values),
                'trend_slope': self._calculate_slope(values)
            }
        )
    
    def _analyze_pattern(self, data: Any, level: AnalysisLevel, analysis_id: str) -> UnifiedAnalysisResult:
        """模式分析"""
        if not isinstance(data, list):
            data = [data] if data else []
        
        data_count = len(data)
        
        if data_count == 0:
            return self._create_empty_result(analysis_id, AnalysisType.PATTERN, level)
        
        patterns = {}
        
        # 查找重复模式
        if isinstance(data[0], dict):
            # 字段模式
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())
            
            key_frequencies = {}
            for key in all_keys:
                key_frequencies[key] = sum(1 for item in data if key in item)
            
            patterns['field_patterns'] = key_frequencies
            
            # 值模式
            for key in all_keys:
                values = [item.get(key) for item in data if key in item]
                unique_values = len(set(str(v) for v in values))
                patterns[f'{key}_uniqueness'] = unique_values / len(values) if values else 0
        
        findings = [f"分析了 {data_count} 个项目的模式"]
        insights = []
        
        if patterns.get('field_patterns'):
            most_common_field = max(patterns['field_patterns'], key=patterns['field_patterns'].get)
            insights.append(f"最常见的字段是 {most_common_field}")
        
        return UnifiedAnalysisResult(
            analysis_id=analysis_id,
            analysis_type=AnalysisType.PATTERN,
            level=level,
            timestamp=datetime.now(),
            success=True,
            confidence=0.75,
            data_count=data_count,
            findings=findings,
            insights=insights,
            patterns=patterns,
            statistics={'pattern_count': len(patterns)}
        )
    
    def _analyze_correlation(self, data: Any, level: AnalysisLevel, analysis_id: str) -> UnifiedAnalysisResult:
        """相关性分析"""
        if not isinstance(data, list) or len(data) < 2:
            return self._create_insufficient_data_result(analysis_id, AnalysisType.CORRELATION, level)
        
        # 简化的相关性分析
        correlations = {}
        
        if isinstance(data[0], dict):
            numeric_fields = []
            for key in data[0].keys():
                values = [item.get(key) for item in data if isinstance(item.get(key), (int, float))]
                if len(values) >= len(data) * 0.5:  # 至少50%的数据是数值
                    numeric_fields.append(key)
            
            # 计算字段间相关性
            for i, field1 in enumerate(numeric_fields):
                for field2 in numeric_fields[i+1:]:
                    values1 = [item.get(field1, 0) for item in data]
                    values2 = [item.get(field2, 0) for item in data]
                    
                    if len(values1) == len(values2) and len(values1) > 1:
                        correlation = self._calculate_correlation(values1, values2)
                        correlations[f"{field1}_vs_{field2}"] = correlation
        
        findings = [f"分析了 {len(data)} 个项目的相关性"]
        insights = []
        
        if correlations:
            strong_correlations = {k: v for k, v in correlations.items() if abs(v) > 0.7}
            if strong_correlations:
                insights.append(f"发现 {len(strong_correlations)} 个强相关性")
        
        return UnifiedAnalysisResult(
            analysis_id=analysis_id,
            analysis_type=AnalysisType.CORRELATION,
            level=level,
            timestamp=datetime.now(),
            success=True,
            confidence=0.7,
            data_count=len(data),
            findings=findings,
            insights=insights,
            statistics={'correlations': correlations}
        )
    
    def _calculate_trend(self, values: List[float]) -> Tuple[str, float]:
        """计算趋势方向和强度"""
        if len(values) < 2:
            return "stable", 0.0
        
        # 简单线性回归
        n = len(values)
        x = list(range(n))
        
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
    
    def _calculate_slope(self, values: List[float]) -> float:
        """计算斜率"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _calculate_correlation(self, values1: List[float], values2: List[float]) -> float:
        """计算相关系数"""
        if len(values1) != len(values2) or len(values1) < 2:
            return 0.0
        
        try:
            mean1 = statistics.mean(values1)
            mean2 = statistics.mean(values2)
            
            numerator = sum((values1[i] - mean1) * (values2[i] - mean2) for i in range(len(values1)))
            
            sum_sq1 = sum((values1[i] - mean1) ** 2 for i in range(len(values1)))
            sum_sq2 = sum((values2[i] - mean2) ** 2 for i in range(len(values2)))
            
            denominator = (sum_sq1 * sum_sq2) ** 0.5
            
            return numerator / denominator if denominator != 0 else 0.0
        except:
            return 0.0
    
    def _create_empty_result(self, analysis_id: str, analysis_type: AnalysisType, 
                           level: AnalysisLevel) -> UnifiedAnalysisResult:
        """创建空结果"""
        return UnifiedAnalysisResult(
            analysis_id=analysis_id,
            analysis_type=analysis_type,
            level=level,
            timestamp=datetime.now(),
            success=True,
            confidence=0.0,
            data_count=0,
            findings=["没有数据可供分析"],
            insights=["需要提供有效的数据进行分析"]
        )
    
    def _create_insufficient_data_result(self, analysis_id: str, analysis_type: AnalysisType,
                                       level: AnalysisLevel) -> UnifiedAnalysisResult:
        """创建数据不足结果"""
        return UnifiedAnalysisResult(
            analysis_id=analysis_id,
            analysis_type=analysis_type,
            level=level,
            timestamp=datetime.now(),
            success=False,
            confidence=0.0,
            data_count=0,
            findings=["数据不足，无法进行有效分析"],
            recommendations=["请提供更多数据以进行准确分析"]
        )
    
    def _create_error_result(self, analysis_id: str, analysis_type: AnalysisType,
                           level: AnalysisLevel, error_msg: str) -> UnifiedAnalysisResult:
        """创建错误结果"""
        return UnifiedAnalysisResult(
            analysis_id=analysis_id,
            analysis_type=analysis_type,
            level=level,
            timestamp=datetime.now(),
            success=False,
            confidence=0.0,
            data_count=0,
            findings=[f"分析失败: {error_msg}"]
        )