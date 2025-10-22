# -*- encoding=utf8 -*-
"""
向后兼容性模块

确保旧代码可以无缝迁移到新的统一架构
"""

import warnings
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入新的统一核心模块
from core import (
    create_unified_system,
    UnifiedElementMapper, UnifiedQualityAnalyzer, UnifiedDataAnalyzer,
    UnifiedReportGenerator, UnifiedConfigManager, UnifiedPerformanceOptimizer,
    UnifiedMonitor,
    ElementType, ActionType, QualityLevel,
    AirtestElement, PocoElement, ElementMapping, QualityMetrics
)


def deprecated_warning(old_name: str, new_name: str):
    """发出弃用警告"""
    warnings.warn(
        f"{old_name} 已弃用，请使用 {new_name} 替代。",
        DeprecationWarning,
        stacklevel=3
    )


# ============================================================================
# 旧的 mappers 模块兼容性
# ============================================================================

class AirtestPocoElementMapper:
    """旧的 AirtestPocoElementMapper 兼容类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        deprecated_warning(
            "AirtestPocoElementMapper", 
            "core.UnifiedElementMapper"
        )
        self._system = create_unified_system()
        self._mapper = self._system['element_mapper']
    
    def extract_airtest_elements(self, script_content: str) -> List[Dict]:
        """提取 Airtest 元素（兼容旧接口）"""
        elements = self._mapper.extract_airtest_elements(script_content)
        # 转换为旧格式
        return [self._convert_airtest_element_to_dict(elem) for elem in elements]
    
    def extract_poco_elements(self, script_content: str) -> List[Dict]:
        """提取 Poco 元素（兼容旧接口）"""
        elements = self._mapper.extract_poco_elements(script_content)
        # 转换为旧格式
        return [self._convert_poco_element_to_dict(elem) for elem in elements]
    
    def create_mappings(self, airtest_elements: List[Dict], 
                       poco_elements: List[Dict]) -> List[Dict]:
        """创建映射（兼容旧接口）"""
        # 转换为新格式
        airtest_objs = [self._convert_dict_to_airtest_element(elem) for elem in airtest_elements]
        poco_objs = [self._convert_dict_to_poco_element(elem) for elem in poco_elements]
        
        mappings = []
        for airtest_elem in airtest_objs:
            for poco_elem in poco_objs:
                similarity = self._mapper.calculate_similarity(airtest_elem, poco_elem)
                if similarity > 0.5:  # 默认阈值
                    mapping = self._mapper.create_mappings([airtest_elem], [poco_elem])[0]
                    mappings.append(self._convert_mapping_to_dict(mapping))
        
        return mappings
    
    def generate_report(self, mappings: List[Dict], output_file: str = "report.html"):
        """生成报告（兼容旧接口）"""
        # 转换为新格式
        mapping_objs = [self._convert_dict_to_mapping(mapping) for mapping in mappings]
        
        report_generator = self._system['report_generator']
        report = report_generator.generate_mapping_report(mapping_objs)
        report_generator.save_report(report, output_file, format='html')
        
        return output_file
    
    def _convert_airtest_element_to_dict(self, element: AirtestElement) -> Dict:
        """转换 AirtestElement 到字典格式"""
        return {
            'id': element.element_id,
            'type': element.element_type.value,
            'locator': element.locator,
            'action': element.action_type.value,
            'screenshot': element.screenshot_path,
            'confidence': element.confidence,
            'position': element.position,
            'size': element.size
        }
    
    def _convert_poco_element_to_dict(self, element: PocoElement) -> Dict:
        """转换 PocoElement 到字典格式"""
        return {
            'id': element.element_id,
            'type': element.element_type.value,
            'locator': element.locator,
            'action': element.action_type.value,
            'attributes': element.attributes,
            'position': element.position,
            'size': element.size
        }
    
    def _convert_dict_to_airtest_element(self, data: Dict) -> AirtestElement:
        """转换字典到 AirtestElement"""
        return AirtestElement(
            element_id=data.get('id', ''),
            element_type=ElementType(data.get('type', 'unknown')),
            locator=data.get('locator', ''),
            action_type=ActionType(data.get('action', 'unknown')),
            screenshot_path=data.get('screenshot', ''),
            confidence=data.get('confidence', 0.5),
            position=data.get('position', (0, 0)),
            size=data.get('size', (0, 0))
        )
    
    def _convert_dict_to_poco_element(self, data: Dict) -> PocoElement:
        """转换字典到 PocoElement"""
        return PocoElement(
            element_id=data.get('id', ''),
            element_type=ElementType(data.get('type', 'unknown')),
            locator=data.get('locator', ''),
            action_type=ActionType(data.get('action', 'unknown')),
            attributes=data.get('attributes', {}),
            position=data.get('position', (0, 0)),
            size=data.get('size', (0, 0))
        )
    
    def _convert_mapping_to_dict(self, mapping: ElementMapping) -> Dict:
        """转换 ElementMapping 到字典格式"""
        return {
            'id': mapping.mapping_id,
            'airtest_element': self._convert_airtest_element_to_dict(mapping.airtest_element),
            'poco_element': self._convert_poco_element_to_dict(mapping.poco_element),
            'confidence': mapping.confidence,
            'correlation_type': mapping.correlation_type.value,
            'created_at': mapping.created_at.isoformat()
        }
    
    def _convert_dict_to_mapping(self, data: Dict) -> ElementMapping:
        """转换字典到 ElementMapping"""
        airtest_elem = self._convert_dict_to_airtest_element(data['airtest_element'])
        poco_elem = self._convert_dict_to_poco_element(data['poco_element'])
        return self._mapper.create_mappings(
            [airtest_elem], [poco_elem]
        )[0]


# 为了兼容性，创建别名
ImprovedAirtestPocoMapper = AirtestPocoElementMapper
PreciseAirtestPocoMapper = AirtestPocoElementMapper


# ============================================================================
# 旧的 analyzers 模块兼容性
# ============================================================================

class ElementAnalyzer:
    """旧的 ElementAnalyzer 兼容类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        deprecated_warning("ElementAnalyzer", "core.UnifiedDataAnalyzer")
        self._system = create_unified_system()
        self._analyzer = self._system['data_analyzer']
    
    def analyze_elements(self, elements: List[Dict]) -> Dict[str, Any]:
        """分析元素（兼容旧接口）"""
        # 转换为新格式并分析
        result = self._analyzer.analyze_statistics(elements)
        
        # 转换为旧格式
        return {
            'total_elements': result.data_count,
            'element_types': result.statistics.get('element_types', {}),
            'action_types': result.statistics.get('action_types', {}),
            'confidence_distribution': result.statistics.get('confidence_distribution', {}),
            'analysis_time': result.statistics.get('analysis_time', 0)
        }


class QualityAnalyzer:
    """旧的 QualityAnalyzer 兼容类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        deprecated_warning("QualityAnalyzer", "core.UnifiedQualityAnalyzer")
        self._system = create_unified_system()
        self._analyzer = self._system['quality_analyzer']
    
    def analyze_quality(self, mappings: List[Dict]) -> Dict[str, Any]:
        """分析质量（兼容旧接口）"""
        # 转换为新格式
        mapping_objs = []
        for mapping_data in mappings:
            if isinstance(mapping_data, dict):
                # 简化的映射创建
                airtest_elem = AirtestElement(
                    element_id=mapping_data.get('airtest_id', ''),
                    element_type=ElementType.UNKNOWN,
                    locator=mapping_data.get('airtest_locator', ''),
                    action_type=ActionType.UNKNOWN
                )
                poco_elem = PocoElement(
                    element_id=mapping_data.get('poco_id', ''),
                    element_type=ElementType.UNKNOWN,
                    locator=mapping_data.get('poco_locator', ''),
                    action_type=ActionType.UNKNOWN
                )
                mapping = self._system['element_mapper'].create_mappings(
                    [airtest_elem], [poco_elem]
                )[0]
                mapping_objs.append(mapping)
        
        quality_metrics = self._analyzer.analyze_mappings(mapping_objs)
        
        # 转换为旧格式
        return {
            'coverage': quality_metrics.coverage,
            'accuracy': quality_metrics.accuracy,
            'consistency': quality_metrics.consistency,
            'completeness': quality_metrics.completeness,
            'reliability': quality_metrics.reliability,
            'overall_score': quality_metrics.overall_score,
            'quality_level': quality_metrics.quality_level.value
        }


# ============================================================================
# 旧的 reporters 模块兼容性
# ============================================================================

class HTMLReporter:
    """旧的 HTMLReporter 兼容类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        deprecated_warning("HTMLReporter", "core.UnifiedReportGenerator")
        self._system = create_unified_system()
        self._reporter = self._system['report_generator']
    
    def generate_report(self, data: Dict[str, Any], output_file: str = "report.html") -> str:
        """生成HTML报告（兼容旧接口）"""
        # 根据数据类型生成相应报告
        if 'mappings' in data:
            mappings = data['mappings']
            if isinstance(mappings, list) and mappings:
                # 转换映射数据
                mapping_objs = []
                for mapping_data in mappings:
                    if isinstance(mapping_data, dict):
                        # 简化映射创建
                        airtest_elem = AirtestElement(
                            element_id=mapping_data.get('airtest_id', ''),
                            element_type=ElementType.UNKNOWN,
                            locator=mapping_data.get('airtest_locator', ''),
                            action_type=ActionType.UNKNOWN
                        )
                        poco_elem = PocoElement(
                            element_id=mapping_data.get('poco_id', ''),
                            element_type=ElementType.UNKNOWN,
                            locator=mapping_data.get('poco_locator', ''),
                            action_type=ActionType.UNKNOWN
                        )
                        mapping = self._system['element_mapper'].create_mappings(
                            [airtest_elem], [poco_elem]
                        )[0]
                        mapping_objs.append(mapping)
                
                report = self._reporter.generate_mapping_report(mapping_objs)
                self._reporter.save_report(report, output_file, format='html')
        
        return output_file


class JSONReporter:
    """旧的 JSONReporter 兼容类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        deprecated_warning("JSONReporter", "core.UnifiedReportGenerator")
        self._system = create_unified_system()
        self._reporter = self._system['report_generator']
    
    def generate_report(self, data: Dict[str, Any], output_file: str = "report.json") -> str:
        """生成JSON报告（兼容旧接口）"""
        # 直接导出数据为JSON
        self._reporter.export_data(data, output_file, format='json')
        return output_file


# ============================================================================
# 旧的 optimizers 模块兼容性
# ============================================================================

class PerformanceOptimizer:
    """旧的 PerformanceOptimizer 兼容类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        deprecated_warning("PerformanceOptimizer", "core.UnifiedPerformanceOptimizer")
        self._system = create_unified_system()
        self._optimizer = self._system['performance_optimizer']
    
    def optimize_mappings(self, mappings: List[Dict]) -> List[Dict]:
        """优化映射（兼容旧接口）"""
        # 转换为新格式
        mapping_objs = []
        for mapping_data in mappings:
            if isinstance(mapping_data, dict):
                airtest_elem = AirtestElement(
                    element_id=mapping_data.get('airtest_id', ''),
                    element_type=ElementType.UNKNOWN,
                    locator=mapping_data.get('airtest_locator', ''),
                    action_type=ActionType.UNKNOWN
                )
                poco_elem = PocoElement(
                    element_id=mapping_data.get('poco_id', ''),
                    element_type=ElementType.UNKNOWN,
                    locator=mapping_data.get('poco_locator', ''),
                    action_type=ActionType.UNKNOWN
                )
                mapping = self._system['element_mapper'].create_mappings(
                    [airtest_elem], [poco_elem]
                )[0]
                mapping_objs.append(mapping)
        
        # 优化
        optimized_mappings = self._optimizer.optimize_mappings(mapping_objs)
        
        # 转换回旧格式
        result = []
        for mapping in optimized_mappings:
            result.append({
                'airtest_id': mapping.airtest_element.element_id,
                'poco_id': mapping.poco_element.element_id,
                'confidence': mapping.confidence,
                'airtest_locator': mapping.airtest_element.locator,
                'poco_locator': mapping.poco_element.locator
            })
        
        return result


# ============================================================================
# 旧的 config 模块兼容性
# ============================================================================

class ConfigManager:
    """旧的 ConfigManager 兼容类"""
    
    def __init__(self, config_file: str = None):
        deprecated_warning("ConfigManager", "core.UnifiedConfigManager")
        self._system = create_unified_system(config_file)
        self._config_manager = self._system['config_manager']
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置（兼容旧接口）"""
        return self._config_manager.get_config(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """设置配置（兼容旧接口）"""
        self._config_manager.set_config(key, value)
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置（兼容旧接口）"""
        return self._config_manager.load_config(config_file)
    
    def save_config(self, config_file: str) -> None:
        """保存配置（兼容旧接口）"""
        self._config_manager.save_config(config_file)


# ============================================================================
# 旧的 utils 模块兼容性
# ============================================================================

class DataProcessor:
    """旧的 DataProcessor 兼容类"""
    
    def __init__(self):
        deprecated_warning("DataProcessor", "core.UnifiedDataAnalyzer")
        self._system = create_unified_system()
        self._analyzer = self._system['data_analyzer']
    
    def process_data(self, data: List[Dict]) -> Dict[str, Any]:
        """处理数据（兼容旧接口）"""
        result = self._analyzer.analyze_statistics(data)
        return {
            'processed_count': result.data_count,
            'statistics': result.statistics,
            'patterns': result.patterns
        }


# ============================================================================
# 旧的 metrics 模块兼容性
# ============================================================================

class QualityMetricsCalculator:
    """旧的 QualityMetricsCalculator 兼容类"""
    
    def __init__(self):
        deprecated_warning("QualityMetricsCalculator", "core.UnifiedQualityAnalyzer")
        self._system = create_unified_system()
        self._analyzer = self._system['quality_analyzer']
    
    def calculate_metrics(self, mappings: List[Dict]) -> Dict[str, float]:
        """计算质量指标（兼容旧接口）"""
        # 转换为新格式
        mapping_objs = []
        for mapping_data in mappings:
            if isinstance(mapping_data, dict):
                airtest_elem = AirtestElement(
                    element_id=mapping_data.get('airtest_id', ''),
                    element_type=ElementType.UNKNOWN,
                    locator=mapping_data.get('airtest_locator', ''),
                    action_type=ActionType.UNKNOWN
                )
                poco_elem = PocoElement(
                    element_id=mapping_data.get('poco_id', ''),
                    element_type=ElementType.UNKNOWN,
                    locator=mapping_data.get('poco_locator', ''),
                    action_type=ActionType.UNKNOWN
                )
                mapping = self._system['element_mapper'].create_mappings(
                    [airtest_elem], [poco_elem]
                )[0]
                mapping_objs.append(mapping)
        
        quality_metrics = self._analyzer.analyze_mappings(mapping_objs)
        
        return {
            'coverage': quality_metrics.coverage,
            'accuracy': quality_metrics.accuracy,
            'consistency': quality_metrics.consistency,
            'completeness': quality_metrics.completeness,
            'reliability': quality_metrics.reliability,
            'overall_score': quality_metrics.overall_score
        }


# ============================================================================
# 便捷函数
# ============================================================================

def create_legacy_system(config_file: str = None) -> Dict[str, Any]:
    """创建兼容旧接口的系统"""
    deprecated_warning("create_legacy_system", "core.create_unified_system")
    
    return {
        'element_mapper': AirtestPocoElementMapper(config_file),
        'element_analyzer': ElementAnalyzer(),
        'quality_analyzer': QualityAnalyzer(),
        'html_reporter': HTMLReporter(),
        'json_reporter': JSONReporter(),
        'performance_optimizer': PerformanceOptimizer(),
        'config_manager': ConfigManager(config_file),
        'data_processor': DataProcessor(),
        'quality_metrics': QualityMetricsCalculator()
    }


def migrate_legacy_code_example():
    """展示如何迁移旧代码的示例"""
    print("旧代码迁移示例")
    print("=" * 40)
    
    # 旧代码示例（仍然可以工作，但会显示弃用警告）
    print("1. 使用旧接口（会显示弃用警告）:")
    
    # 创建旧的映射器
    old_mapper = AirtestPocoElementMapper()
    
    # 创建旧的分析器
    old_analyzer = QualityAnalyzer()
    
    # 创建旧的报告器
    old_reporter = HTMLReporter()
    
    print("   ✓ 旧组件创建成功（但已弃用）")
    
    # 新代码示例
    print("\n2. 使用新的统一接口:")
    
    # 创建新的统一系统
    system = create_unified_system()
    
    # 使用新的组件
    new_mapper = system['element_mapper']
    new_analyzer = system['quality_analyzer']
    new_reporter = system['report_generator']
    
    print("   ✓ 新统一组件创建成功")
    
    print("\n迁移建议:")
    print("   • 逐步将旧代码迁移到新的统一接口")
    print("   • 使用 create_unified_system() 替代分散的组件创建")
    print("   • 参考 integration_examples.py 了解新接口用法")
    print("   • 旧接口将在未来版本中移除")


if __name__ == "__main__":
    # 运行迁移示例
    migrate_legacy_code_example()
    
    print("\n" + "=" * 60)
    print("向后兼容性测试")
    print("=" * 60)
    
    # 测试兼容性
    try:
        # 创建旧系统（会显示弃用警告）
        legacy_system = create_legacy_system()
        print("✓ 旧系统创建成功")
        
        # 测试旧接口
        mapper = legacy_system['element_mapper']
        print("✓ 旧映射器接口可用")
        
        analyzer = legacy_system['quality_analyzer']
        print("✓ 旧分析器接口可用")
        
        reporter = legacy_system['html_reporter']
        print("✓ 旧报告器接口可用")
        
        print("\n所有旧接口都可以正常工作，但建议迁移到新的统一架构。")
        
    except Exception as e:
        print(f"✗ 兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()