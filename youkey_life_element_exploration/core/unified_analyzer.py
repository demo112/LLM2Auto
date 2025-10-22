# -*- encoding=utf8 -*-
"""
统一分析器

整合原有的多个分析器功能，提供统一的分析接口
"""

import os
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter

from .unified_models import (
    ElementInfo, ElementMapping, QualityScore, QualityMetrics, AnalysisResult,
    ElementType, CorrelationType, QualityLevel, create_quality_score
)
from .base_interfaces import IQualityAnalyzer, IDataAnalyzer


class UnifiedQualityAnalyzer(IQualityAnalyzer):
    """统一质量分析器"""
    
    def __init__(self, quality_weights: Dict[str, float] = None):
        self.quality_weights = quality_weights or {
            'coverage': 0.25,      # 覆盖率
            'accuracy': 0.25,      # 准确性
            'consistency': 0.20,   # 一致性
            'completeness': 0.15,  # 完整性
            'reliability': 0.15    # 可靠性
        }
        
        # 质量阈值配置
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
    
    def analyze_quality(self, mappings: List[ElementMapping]) -> QualityScore:
        """分析映射质量"""
        if not mappings:
            return create_quality_score(0.0, "无映射数据")
        
        # 计算各项质量指标
        coverage_score = self._calculate_coverage_score(mappings)
        accuracy_score = self._calculate_accuracy_score(mappings)
        consistency_score = self._calculate_consistency_score(mappings)
        completeness_score = self._calculate_completeness_score(mappings)
        reliability_score = self._calculate_reliability_score(mappings)
        
        # 加权计算总分
        total_score = (
            coverage_score * self.quality_weights['coverage'] +
            accuracy_score * self.quality_weights['accuracy'] +
            consistency_score * self.quality_weights['consistency'] +
            completeness_score * self.quality_weights['completeness'] +
            reliability_score * self.quality_weights['reliability']
        )
        
        # 生成详细指标
        metrics = QualityMetrics(
            element_id="quality_analysis",
            timestamp=datetime.now()
        )
        
        # 设置综合评分
        metrics.overall_score = QualityScore(
            score=total_score,
            level=self._determine_quality_level(total_score),
            details={
                'coverage': coverage_score,
                'accuracy': accuracy_score,
                'consistency': consistency_score,
                'completeness': completeness_score,
                'reliability': reliability_score,
                'total_elements': len(mappings),
                'valid_mappings': len([m for m in mappings if m.confidence > 0.5]),
                'error_count': len([m for m in mappings if m.confidence < 0.3])
            }
        )
        
        # 生成建议
        suggestions = self._generate_quality_suggestions(metrics)
        metrics.overall_score.recommendations = suggestions
        
        return metrics.overall_score
    
    def analyze_elements(self, elements: List[ElementInfo]) -> QualityScore:
        """分析元素质量"""
        if not elements:
            return create_quality_score(0.0, "无元素数据")
        
        # 元素质量评估
        valid_elements = [e for e in elements if self._is_valid_element(e)]
        unique_elements = self._get_unique_elements(elements)
        
        # 计算质量指标
        validity_rate = len(valid_elements) / len(elements)
        uniqueness_rate = len(unique_elements) / len(elements)
        completeness_rate = self._calculate_element_completeness(elements)
        
        # 综合评分
        total_score = (validity_rate * 0.4 + uniqueness_rate * 0.3 + completeness_rate * 0.3)
        
        # 创建一个示例元素的QualityMetrics
        element_id = elements[0].element_id if elements else "unknown"
        metrics = QualityMetrics(
            element_id=element_id,
            timestamp=datetime.now(),
            performance_score=create_quality_score(validity_rate * 100),
            visibility_score=create_quality_score(uniqueness_rate * 100),
            accessibility_score=create_quality_score(completeness_rate * 100),
            overall_score=create_quality_score(total_score * 100)
        )
        
        suggestions = self._generate_element_suggestions(elements, metrics)
        
        return QualityScore(
            score=total_score * 100,  # 转换为0-100分制
            level=self._determine_quality_level(total_score * 100),
            details={"validity_rate": validity_rate, "uniqueness_rate": uniqueness_rate, "completeness_rate": completeness_rate},
            recommendations=suggestions
        )
    
    def validate_data(self, data: Any) -> bool:
        """验证数据有效性"""
        if not data:
            return False
        
        if isinstance(data, list):
            if not data:
                return False
            
            # 检查列表中的元素类型
            first_item = data[0]
            if isinstance(first_item, ElementMapping):
                return all(self._is_valid_mapping(item) for item in data)
            elif isinstance(first_item, ElementInfo):
                return all(self._is_valid_element(item) for item in data)
        
        return True
    
    def get_quality_metrics(self, data: Any) -> QualityMetrics:
        """获取质量指标"""
        if isinstance(data, list) and data:
            first_item = data[0]
            if isinstance(first_item, ElementMapping):
                quality_score = self.analyze_quality(data)
                return quality_score.metrics
            elif isinstance(first_item, ElementInfo):
                quality_score = self.analyze_elements(data)
                return quality_score.metrics
        
        # 返回默认指标
        return QualityMetrics(
            total_elements=0,
            valid_mappings=0,
            error_count=0
        )
    
    def _calculate_coverage_score(self, mappings: List[ElementMapping]) -> float:
        """计算覆盖率分数"""
        if not mappings:
            return 0.0
        
        # 统计不同类型的映射
        type_counts = defaultdict(int)
        for mapping in mappings:
            type_counts[mapping.correlation_type] += 1
        
        # 高质量映射的比例
        high_quality = type_counts[CorrelationType.EXACT] + type_counts[CorrelationType.STRONG]
        coverage_rate = high_quality / len(mappings)
        
        return min(coverage_rate * 1.2, 1.0)  # 稍微提升权重
    
    def _calculate_accuracy_score(self, mappings: List[ElementMapping]) -> float:
        """计算准确性分数"""
        if not mappings:
            return 0.0
        
        # 基于置信度的准确性评估
        confidence_sum = sum(mapping.confidence for mapping in mappings)
        average_confidence = confidence_sum / len(mappings)
        
        # 高置信度映射的比例
        high_confidence_count = len([m for m in mappings if m.confidence > 0.8])
        high_confidence_rate = high_confidence_count / len(mappings)
        
        return (average_confidence * 0.6 + high_confidence_rate * 0.4)
    
    def _calculate_consistency_score(self, mappings: List[ElementMapping]) -> float:
        """计算一致性分数"""
        if not mappings:
            return 0.0
        
        # 检查映射的一致性
        element_pairs = {}
        inconsistent_count = 0
        
        for mapping in mappings:
            if mapping.airtest_element and mapping.poco_element:
                key = (mapping.airtest_element.template_file, mapping.poco_element.selector)
                if key in element_pairs:
                    # 检查是否有不一致的映射
                    if abs(element_pairs[key] - mapping.confidence) > 0.3:
                        inconsistent_count += 1
                else:
                    element_pairs[key] = mapping.confidence
        
        consistency_rate = 1.0 - (inconsistent_count / len(mappings))
        return max(consistency_rate, 0.0)
    
    def _calculate_completeness_score(self, mappings: List[ElementMapping]) -> float:
        """计算完整性分数"""
        if not mappings:
            return 0.0
        
        # 检查映射的完整性
        complete_mappings = 0
        for mapping in mappings:
            if (mapping.airtest_element and mapping.poco_element and 
                mapping.evidence and mapping.semantic_name):
                complete_mappings += 1
        
        completeness_rate = complete_mappings / len(mappings)
        return completeness_rate
    
    def _calculate_reliability_score(self, mappings: List[ElementMapping]) -> float:
        """计算可靠性分数"""
        if not mappings:
            return 0.0
        
        # 基于证据数量和质量评估可靠性
        reliable_mappings = 0
        for mapping in mappings:
            evidence_count = len(mapping.evidence) if mapping.evidence else 0
            if evidence_count >= 2 and mapping.confidence > 0.6:
                reliable_mappings += 1
        
        reliability_rate = reliable_mappings / len(mappings)
        return reliability_rate
    
    def _calculate_element_completeness(self, elements: List[ElementInfo]) -> float:
        """计算元素完整性"""
        if not elements:
            return 0.0
        
        complete_elements = 0
        for element in elements:
            if (element.element_id and element.locator and 
                element.line_number > 0 and element.attributes):
                complete_elements += 1
        
        return complete_elements / len(elements)
    
    def _is_valid_element(self, element: ElementInfo) -> bool:
        """检查元素是否有效"""
        return (element and element.element_id and element.locator and 
                element.element_type != ElementType.UNKNOWN)
    
    def _is_valid_mapping(self, mapping: ElementMapping) -> bool:
        """检查映射是否有效"""
        return (mapping and mapping.mapping_id and 
                (mapping.airtest_element or mapping.poco_element) and
                0 <= mapping.confidence <= 1)
    
    def _get_unique_elements(self, elements: List[ElementInfo]) -> List[ElementInfo]:
        """获取唯一元素"""
        seen = set()
        unique = []
        
        for element in elements:
            key = (element.element_type, element.locator)
            if key not in seen:
                seen.add(key)
                unique.append(element)
        
        return unique
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """确定质量等级"""
        if score >= self.quality_thresholds['excellent']:
            return QualityLevel.EXCELLENT
        elif score >= self.quality_thresholds['good']:
            return QualityLevel.GOOD
        elif score >= self.quality_thresholds['fair']:
            return QualityLevel.FAIR
        elif score >= self.quality_thresholds['poor']:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def _generate_quality_suggestions(self, metrics: QualityMetrics) -> List[str]:
        """生成质量改进建议"""
        suggestions = []
        
        # 从overall_score的details中获取指标
        details = metrics.overall_score.details
        
        if details.get('coverage', 0) < 0.7:
            suggestions.append("建议增加元素覆盖率，确保更多元素被正确映射")
        
        if details.get('accuracy', 0) < 0.8:
            suggestions.append("建议提高映射准确性，检查低置信度的映射关系")
        
        if details.get('consistency', 0) < 0.9:
            suggestions.append("发现映射不一致问题，建议检查重复或冲突的映射")
        
        if details.get('completeness', 0) < 0.8:
            suggestions.append("部分映射信息不完整，建议补充缺失的元数据")
        
        if details.get('error_count', 0) > details.get('total_elements', 1) * 0.1:
            suggestions.append("错误映射较多，建议重新检查映射算法和参数")
        
        return suggestions
    
    def _generate_element_suggestions(self, elements: List[ElementInfo], 
                                    metrics: QualityMetrics) -> List[str]:
        """生成元素改进建议"""
        suggestions = []
        
        # 检查元素类型分布
        type_counts = Counter(e.element_type for e in elements)
        if ElementType.UNKNOWN in type_counts:
            suggestions.append(f"发现 {type_counts[ElementType.UNKNOWN]} 个未知类型元素，建议完善元素识别")
        
        # 检查重复元素
        locator_counts = Counter(e.locator for e in elements)
        duplicates = [loc for loc, count in locator_counts.items() if count > 1]
        if duplicates:
            suggestions.append(f"发现 {len(duplicates)} 个重复定位器，建议去重或合并")
        
        # 检查属性完整性
        incomplete_elements = [e for e in elements if not e.attributes]
        if incomplete_elements:
            suggestions.append(f"{len(incomplete_elements)} 个元素缺少属性信息，建议补充")
        
        return suggestions
    
    # ============================================================================
    # IQualityAnalyzer 接口实现
    # ============================================================================
    
    def analyze_element_quality(self, element_id: str, element_data: Dict[str, Any]) -> QualityMetrics:
        """分析元素质量"""
        # 从元素数据创建ElementInfo对象
        if 'elements' in element_data:
            elements = element_data['elements']
            if isinstance(elements, list) and elements:
                quality_score = self.analyze_elements(elements)
                return quality_score.metrics
        
        # 如果是单个元素数据
        element_info = ElementInfo(
            element_id=element_id,
            element_type=ElementType.POCO_ID if element_data.get('type') == 'poco' else ElementType.TEMPLATE,
            locator=element_data.get('locator', ''),
            line_number=element_data.get('line_number', 0),
            attributes=element_data.get('attributes', {}),
            location=element_data.get('location', {})
        )
        
        quality_score = self.analyze_elements([element_info])
        return quality_score.metrics
    
    def calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """计算质量分数"""
        # 从指标数据计算综合分数
        coverage = metrics.get('coverage_rate', 0.0)
        accuracy = metrics.get('accuracy_rate', 0.0)
        consistency = metrics.get('consistency_rate', 0.0)
        completeness = metrics.get('completeness_rate', 0.0)
        reliability = metrics.get('reliability_rate', 0.0)
        
        # 加权计算
        score = (
            coverage * self.quality_weights['coverage'] +
            accuracy * self.quality_weights['accuracy'] +
            consistency * self.quality_weights['consistency'] +
            completeness * self.quality_weights['completeness'] +
            reliability * self.quality_weights['reliability']
        )
        
        return min(score * 100, 100.0)  # 转换为0-100分制
    
    def get_quality_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """获取质量改进建议"""
        recommendations = []
        
        if metrics.coverage_rate < 0.7:
            recommendations.append("提高元素覆盖率：增加更多有效的元素映射")
        
        if metrics.accuracy_rate < 0.7:
            recommendations.append("提高准确性：优化元素识别和匹配算法")
        
        if metrics.consistency_rate < 0.7:
            recommendations.append("提高一致性：统一元素命名和属性规范")
        
        if metrics.completeness_rate < 0.7:
            recommendations.append("提高完整性：补充缺失的元素属性和信息")
        
        if metrics.reliability_rate < 0.7:
            recommendations.append("提高可靠性：增强元素定位的稳定性")
        
        if metrics.error_count > metrics.total_elements * 0.1:
            recommendations.append(f"修复错误：发现 {metrics.error_count} 个错误，建议优先处理")
        
        if metrics.valid_mappings < metrics.total_elements * 0.8:
            recommendations.append("增加有效映射：当前有效映射比例较低，建议优化映射策略")
        
        return recommendations


class UnifiedDataAnalyzer(IDataAnalyzer):
    """统一数据分析器"""
    
    def __init__(self):
        self.analysis_cache = {}
        self.quality_analyzer = UnifiedQualityAnalyzer()
    
    def analyze_data(self, data: Any, analysis_type: str = "comprehensive") -> AnalysisResult:
        """分析数据"""
        if not data:
            return AnalysisResult(
                analysis_type=analysis_type,
                summary="无数据可分析",
                details={},
                metrics={},
                timestamp=datetime.now()
            )
        
        # 根据分析类型执行不同的分析
        if analysis_type == "quality":
            return self._analyze_quality_data(data)
        elif analysis_type == "statistics":
            return self._analyze_statistics_data(data)
        elif analysis_type == "patterns":
            return self._analyze_patterns_data(data)
        else:  # comprehensive
            return self._analyze_comprehensive_data(data)
    
    def generate_statistics(self, data: Any) -> Dict[str, Any]:
        """生成统计信息"""
        if not data:
            return {}
        
        stats = {}
        
        if isinstance(data, list):
            stats['total_count'] = len(data)
            
            if data and isinstance(data[0], ElementMapping):
                stats.update(self._generate_mapping_statistics(data))
            elif data and isinstance(data[0], ElementInfo):
                stats.update(self._generate_element_statistics(data))
        
        return stats
    
    def find_patterns(self, data: Any) -> Dict[str, Any]:
        """查找数据模式"""
        patterns = {}
        
        if isinstance(data, list) and data:
            if isinstance(data[0], ElementMapping):
                patterns.update(self._find_mapping_patterns(data))
            elif isinstance(data[0], ElementInfo):
                patterns.update(self._find_element_patterns(data))
        
        return patterns
    
    def calculate_metrics(self, data: Any) -> Dict[str, float]:
        """计算指标"""
        if not data:
            return {}
        
        metrics = {}
        
        if isinstance(data, list) and data:
            if isinstance(data[0], ElementMapping):
                metrics.update(self._calculate_mapping_metrics(data))
            elif isinstance(data[0], ElementInfo):
                metrics.update(self._calculate_element_metrics(data))
        
        return metrics
    
    def analyze_trends(self, data: List[Any], time_window: Optional[str] = None) -> Dict[str, Any]:
        """分析数据趋势"""
        trends = {}
        
        if not data:
            return trends
        
        # 基于时间戳分析趋势
        if data and hasattr(data[0], 'timestamp'):
            timestamps = [item.timestamp for item in data if hasattr(item, 'timestamp') and item.timestamp is not None]
            if timestamps:
                trends['time_span'] = {
                    'start': min(timestamps),
                    'end': max(timestamps),
                    'duration': (max(timestamps) - min(timestamps)).total_seconds()
                }
        
        # 数量趋势
        trends['count_trend'] = len(data)
        
        # 质量趋势（如果是ElementMapping或ElementInfo）
        if isinstance(data[0], ElementMapping):
            confidences = [m.confidence for m in data]
            trends['confidence_trend'] = {
                'average': sum(confidences) / len(confidences),
                'trend_direction': 'stable'  # 简化实现
            }
        elif isinstance(data[0], ElementInfo):
            # 分析元素类型分布趋势
            type_counts = Counter(e.element_type for e in data)
            trends['element_type_trend'] = dict(type_counts)
        
        return trends
    
    def detect_anomalies(self, data: List[Any], threshold: float = 2.0) -> List[Dict[str, Any]]:
        """检测数据异常"""
        anomalies = []
        
        if not data:
            return anomalies
        
        # 检测置信度异常（针对ElementMapping）
        if isinstance(data[0], ElementMapping):
            confidences = [m.confidence for m in data]
            if confidences:
                mean_conf = sum(confidences) / len(confidences)
                std_conf = (sum((x - mean_conf) ** 2 for x in confidences) / len(confidences)) ** 0.5
                
                for i, mapping in enumerate(data):
                    if abs(mapping.confidence - mean_conf) > threshold * std_conf:
                        anomalies.append({
                            'type': 'confidence_anomaly',
                            'index': i,
                            'value': mapping.confidence,
                            'expected_range': (mean_conf - threshold * std_conf, 
                                             mean_conf + threshold * std_conf),
                            'severity': 'high' if abs(mapping.confidence - mean_conf) > 3 * std_conf else 'medium'
                        })
        
        # 检测元素异常（针对ElementInfo）
        elif isinstance(data[0], ElementInfo):
            # 检测行号异常
            line_numbers = [e.line_number for e in data if e.line_number > 0]
            if line_numbers:
                mean_line = sum(line_numbers) / len(line_numbers)
                std_line = (sum((x - mean_line) ** 2 for x in line_numbers) / len(line_numbers)) ** 0.5
                
                for i, element in enumerate(data):
                    if element.line_number > 0 and abs(element.line_number - mean_line) > threshold * std_line:
                        anomalies.append({
                            'type': 'line_number_anomaly',
                            'index': i,
                            'element_id': element.element_id,
                            'value': element.line_number,
                            'expected_range': (mean_line - threshold * std_line,
                                             mean_line + threshold * std_line),
                            'severity': 'medium'
                        })
        
        return anomalies
    
    def predict_quality(self, historical_data: List[Any], prediction_horizon: int = 5) -> Dict[str, Any]:
        """预测质量趋势"""
        prediction = {
            'prediction_horizon': prediction_horizon,
            'confidence': 0.0,
            'predicted_metrics': {},
            'recommendations': []
        }
        
        if not historical_data:
            return prediction
        
        # 基于历史数据预测质量
        if isinstance(historical_data[0], ElementMapping):
            # 分析置信度趋势
            confidences = [m.confidence for m in historical_data]
            if len(confidences) >= 3:  # 至少需要3个数据点
                # 简单线性趋势预测
                recent_avg = sum(confidences[-3:]) / 3
                overall_avg = sum(confidences) / len(confidences)
                trend = recent_avg - overall_avg
                
                predicted_confidence = recent_avg + trend * prediction_horizon
                predicted_confidence = max(0.0, min(1.0, predicted_confidence))  # 限制在[0,1]范围
                
                prediction['predicted_metrics']['confidence'] = predicted_confidence
                prediction['confidence'] = 0.7  # 预测置信度
                
                if trend < -0.1:
                    prediction['recommendations'].append("质量呈下降趋势，建议优化元素映射策略")
                elif trend > 0.1:
                    prediction['recommendations'].append("质量呈上升趋势，当前策略效果良好")
                else:
                    prediction['recommendations'].append("质量保持稳定")
        
        elif isinstance(historical_data[0], ElementInfo):
            # 分析元素完整性趋势
            completeness_scores = []
            for i in range(0, len(historical_data), max(1, len(historical_data) // 10)):
                batch = historical_data[i:i + max(1, len(historical_data) // 10)]
                valid_count = sum(1 for e in batch if self._is_valid_element(e))
                completeness = valid_count / len(batch) if batch else 0
                completeness_scores.append(completeness)
            
            if len(completeness_scores) >= 3:
                recent_avg = sum(completeness_scores[-3:]) / 3
                overall_avg = sum(completeness_scores) / len(completeness_scores)
                trend = recent_avg - overall_avg
                
                predicted_completeness = recent_avg + trend * prediction_horizon
                predicted_completeness = max(0.0, min(1.0, predicted_completeness))
                
                prediction['predicted_metrics']['completeness'] = predicted_completeness
                prediction['confidence'] = 0.6
                
                if trend < -0.1:
                    prediction['recommendations'].append("元素完整性呈下降趋势，建议检查数据源")
                elif trend > 0.1:
                    prediction['recommendations'].append("元素完整性呈上升趋势，数据质量在改善")
                else:
                    prediction['recommendations'].append("元素完整性保持稳定")
        
        return prediction
    
    def _is_valid_element(self, element: ElementInfo) -> bool:
        """检查元素是否有效（复用已有方法）"""
        return (element.element_id and 
                element.element_type and 
                element.locator and 
                element.line_number > 0)
    
    def _analyze_quality_data(self, data: Any) -> AnalysisResult:
        """分析质量数据"""
        if isinstance(data, list) and data:
            if isinstance(data[0], ElementMapping):
                quality_score = self.quality_analyzer.analyze_quality(data)
            elif isinstance(data[0], ElementInfo):
                quality_score = self.quality_analyzer.analyze_elements(data)
            else:
                quality_score = create_quality_score(0.0, "不支持的数据类型")
        else:
            quality_score = create_quality_score(0.0, "无效数据")
        
        return AnalysisResult(
            analysis_id=f"quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            element_id="batch_analysis",
            analysis_type="quality",
            timestamp=datetime.now(),
            success=True,
            confidence=quality_score.score / 100.0,
            findings=[f"质量等级: {quality_score.level.value}, 得分: {quality_score.score:.2f}"],
            recommendations=quality_score.recommendations
        )
    
    def _analyze_statistics_data(self, data: Any) -> AnalysisResult:
        """分析统计数据"""
        stats = self.generate_statistics(data)
        
        return AnalysisResult(
            analysis_id=f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            element_id="batch_analysis",
            analysis_type="statistics",
            timestamp=datetime.now(),
            success=True,
            confidence=0.9,
            findings=[f"数据统计分析完成，共 {stats.get('total_count', 0)} 项数据"],
            insights=[f"发现 {len(stats)} 个统计指标"]
        )
    
    def _analyze_patterns_data(self, data: Any) -> AnalysisResult:
        """分析模式数据"""
        patterns = self.find_patterns(data)
        
        return AnalysisResult(
            analysis_id=f"patterns_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            element_id="batch_analysis",
            analysis_type="patterns",
            timestamp=datetime.now(),
            success=True,
            confidence=0.8,
            findings=[f"模式分析完成，发现 {len(patterns)} 种模式"],
            insights=[f"识别出 {len(patterns)} 个数据模式"]
        )
    
    def _analyze_comprehensive_data(self, data: Any) -> AnalysisResult:
        """综合数据分析"""
        # 执行所有类型的分析
        quality_result = self._analyze_quality_data(data)
        stats_result = self._analyze_statistics_data(data)
        patterns_result = self._analyze_patterns_data(data)
        
        # 合并结果
        all_findings = quality_result.findings + stats_result.findings + patterns_result.findings
        all_insights = quality_result.insights + stats_result.insights + patterns_result.insights
        all_recommendations = quality_result.recommendations + stats_result.recommendations + patterns_result.recommendations
        
        return AnalysisResult(
            analysis_id=f"comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            element_id="batch_analysis",
            analysis_type="comprehensive",
            timestamp=datetime.now(),
            success=True,
            confidence=(quality_result.confidence + stats_result.confidence + patterns_result.confidence) / 3,
            findings=all_findings,
            insights=all_insights,
            recommendations=all_recommendations
        )
    
    def _generate_mapping_statistics(self, mappings: List[ElementMapping]) -> Dict[str, Any]:
        """生成映射统计"""
        stats = {}
        
        # 置信度统计
        confidences = [m.confidence for m in mappings]
        stats['avg_confidence'] = sum(confidences) / len(confidences)
        stats['max_confidence'] = max(confidences)
        stats['min_confidence'] = min(confidences)
        
        # 关联类型统计
        correlation_counts = Counter(m.correlation_type for m in mappings)
        stats['correlation_distribution'] = dict(correlation_counts)
        
        # 证据统计
        evidence_counts = [len(m.evidence) if m.evidence else 0 for m in mappings]
        stats['avg_evidence_count'] = sum(evidence_counts) / len(evidence_counts)
        
        return stats
    
    def _generate_element_statistics(self, elements: List[ElementInfo]) -> Dict[str, Any]:
        """生成元素统计"""
        stats = {}
        
        # 元素类型统计
        type_counts = Counter(e.element_type for e in elements)
        stats['element_type_distribution'] = dict(type_counts)
        
        # 行号统计
        line_numbers = [e.line_number for e in elements if e.line_number > 0]
        if line_numbers:
            stats['avg_line_number'] = sum(line_numbers) / len(line_numbers)
            stats['line_number_range'] = (min(line_numbers), max(line_numbers))
        
        # 属性统计
        attr_counts = [len(e.attributes) if e.attributes else 0 for e in elements]
        stats['avg_attribute_count'] = sum(attr_counts) / len(attr_counts)
        
        return stats
    
    def _find_mapping_patterns(self, mappings: List[ElementMapping]) -> Dict[str, Any]:
        """查找映射模式"""
        patterns = {}
        
        # 高置信度模式
        high_confidence = [m for m in mappings if m.confidence > 0.8]
        patterns['high_confidence_pattern'] = {
            'count': len(high_confidence),
            'percentage': len(high_confidence) / len(mappings) * 100
        }
        
        # 语义名称模式
        semantic_names = [m.semantic_name for m in mappings if m.semantic_name]
        semantic_counts = Counter(semantic_names)
        patterns['semantic_patterns'] = dict(semantic_counts.most_common(5))
        
        return patterns
    
    def _find_element_patterns(self, elements: List[ElementInfo]) -> Dict[str, Any]:
        """查找元素模式"""
        patterns = {}
        
        # 定位器模式
        locators = [e.locator for e in elements]
        locator_patterns = {}
        
        # 分析定位器类型
        for locator in locators:
            if locator.startswith('#'):
                locator_patterns['id_selectors'] = locator_patterns.get('id_selectors', 0) + 1
            elif locator.startswith('.'):
                locator_patterns['class_selectors'] = locator_patterns.get('class_selectors', 0) + 1
            elif '.png' in locator or '.jpg' in locator:
                locator_patterns['image_templates'] = locator_patterns.get('image_templates', 0) + 1
        
        patterns['locator_patterns'] = locator_patterns
        
        return patterns
    
    def _calculate_mapping_metrics(self, mappings: List[ElementMapping]) -> Dict[str, float]:
        """计算映射指标"""
        metrics = {}
        
        if mappings:
            # 平均置信度
            metrics['average_confidence'] = sum(m.confidence for m in mappings) / len(mappings)
            
            # 高质量映射比例
            high_quality = len([m for m in mappings if m.confidence > 0.7])
            metrics['high_quality_ratio'] = high_quality / len(mappings)
            
            # 完整映射比例
            complete = len([m for m in mappings if m.airtest_element and m.poco_element])
            metrics['completeness_ratio'] = complete / len(mappings)
        
        return metrics
    
    def _calculate_element_metrics(self, elements: List[ElementInfo]) -> Dict[str, float]:
        """计算元素指标"""
        metrics = {}
        
        if elements:
            # 有效元素比例
            valid = len([e for e in elements if self.quality_analyzer._is_valid_element(e)])
            metrics['validity_ratio'] = valid / len(elements)
            
            # 唯一元素比例
            unique = len(self.quality_analyzer._get_unique_elements(elements))
            metrics['uniqueness_ratio'] = unique / len(elements)
            
            # 属性完整性
            with_attrs = len([e for e in elements if e.attributes])
            metrics['attribute_completeness'] = with_attrs / len(elements)
        
        return metrics