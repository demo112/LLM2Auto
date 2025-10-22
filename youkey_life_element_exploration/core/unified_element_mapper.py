# -*- encoding=utf8 -*-
"""
统一元素映射器

整合原有的三个mapper功能，提供统一的元素映射接口
"""

import os
import re
import shutil
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from .unified_models import (
    AirtestElement, PocoElement, ElementMapping, ElementInfo, ActionInfo,
    ElementType, ActionType, CorrelationType, generate_mapping_id
)
from .base_interfaces import IElementMapper, IElementExtractor


class UnifiedElementExtractor(IElementExtractor):
    """统一元素提取器"""
    
    def __init__(self):
        self.airtest_patterns = {
            'touch': r'touch\(Template\(r?"([^"]+)".*?record_pos=\(([^)]+)\).*?resolution=\(([^)]+)\)',
            'click': r'click\(Template\(r?"([^"]+)".*?record_pos=\(([^)]+)\).*?resolution=\(([^)]+)\)',
            'wait': r'wait\(Template\(r?"([^"]+)".*?record_pos=\(([^)]+)\).*?resolution=\(([^)]+)\)',
            'assert_exists': r'assert_exists\(Template\(r?"([^"]+)".*?record_pos=\(([^)]+)\).*?resolution=\(([^)]+)\)'
        }
        
        self.poco_patterns = {
            'click': r'poco\(([^)]+)\)\.click\(\)',
            'touch': r'poco\(([^)]+)\)\.touch\(\)',
            'wait': r'poco\(([^)]+)\)\.wait_for_appearance\(\)',
            'input': r'poco\(([^)]+)\)\.set_text\([^)]+\)',
            'assert': r'assert poco\(([^)]+)\)'
        }
    
    def extract_elements(self, source: str) -> List[ElementInfo]:
        """提取所有元素信息"""
        elements = []
        
        # 提取Airtest元素
        airtest_elements = self._extract_airtest_elements(source)
        for ae in airtest_elements:
            element_info = ElementInfo(
                element_id=f"airtest_{ae.template_file}_{ae.line_number}",
                element_type=ElementType.TEMPLATE,
                locator=ae.template_file,
                line_number=ae.line_number,
                attributes={
                    'record_pos': ae.record_pos,
                    'resolution': ae.resolution,
                    'operation_type': ae.operation_type,
                    'vector': ae.vector
                }
            )
            elements.append(element_info)
        
        # 提取Poco元素
        poco_elements = self._extract_poco_elements(source)
        for pe in poco_elements:
            element_type = self._determine_poco_element_type(pe.selector_type)
            element_info = ElementInfo(
                element_id=f"poco_{pe.selector}_{pe.line_number}",
                element_type=element_type,
                locator=pe.selector,
                line_number=pe.line_number,
                attributes={
                    'selector_type': pe.selector_type,
                    'operation_type': pe.operation_type,
                    'operation_params': pe.operation_params
                }
            )
            elements.append(element_info)
        
        return elements
    
    def extract_actions(self, source: str) -> List[ActionInfo]:
        """提取操作信息"""
        actions = []
        elements = self.extract_elements(source)
        
        for element in elements:
            operation_type = element.attributes.get('operation_type', 'unknown')
            action_type = self._map_operation_to_action(operation_type)
            
            action = ActionInfo(
                action_type=action_type,
                element=element,
                line_number=element.line_number,
                parameters=element.attributes
            )
            actions.append(action)
        
        return actions
    
    def validate_source(self, source: str) -> bool:
        """验证源文件"""
        if not source or not isinstance(source, str):
            return False
        
        # 检查是否包含Airtest或Poco相关代码
        has_airtest = any(pattern in source for pattern in ['Template(', 'touch(', 'click('])
        has_poco = any(pattern in source for pattern in ['poco(', '.click()', '.touch()'])
        
        return has_airtest or has_poco
    
    def _extract_airtest_elements(self, source: str) -> List[AirtestElement]:
        """提取Airtest元素"""
        elements = []
        lines = source.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            for operation, pattern in self.airtest_patterns.items():
                match = re.search(pattern, line)
                if match:
                    template_file = match.group(1)
                    record_pos = tuple(map(float, match.group(2).split(',')))
                    resolution = tuple(map(int, match.group(3).split(',')))
                    
                    # 提取vector信息（如果存在）
                    vector = None
                    vector_match = re.search(r'vector=\(([^)]+)\)', line)
                    if vector_match:
                        vector = tuple(map(float, vector_match.group(1).split(',')))
                    
                    element = AirtestElement(
                        template_file=template_file,
                        operation_type=operation,
                        record_pos=record_pos,
                        resolution=resolution,
                        line_number=line_num,
                        vector=vector
                    )
                    elements.append(element)
                    break
        
        return elements
    
    def _extract_poco_elements(self, source: str) -> List[PocoElement]:
        """提取Poco元素"""
        elements = []
        lines = source.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            for operation, pattern in self.poco_patterns.items():
                match = re.search(pattern, line)
                if match:
                    selector = match.group(1).strip('"\'')
                    selector_type = self._determine_selector_type(selector)
                    
                    # 提取操作参数
                    operation_params = None
                    if operation == 'input':
                        params_match = re.search(r'set_text\(([^)]+)\)', line)
                        if params_match:
                            operation_params = params_match.group(1)
                    
                    element = PocoElement(
                        selector=selector,
                        selector_type=selector_type,
                        operation_type=operation,
                        line_number=line_num,
                        operation_params=operation_params
                    )
                    elements.append(element)
                    break
        
        return elements
    
    def _determine_selector_type(self, selector: str) -> str:
        """确定选择器类型"""
        if selector.startswith('#'):
            return 'id'
        elif selector.startswith('.'):
            return 'class'
        elif '=' in selector:
            return 'attr'
        elif selector.startswith('//') or selector.startswith('/'):
            return 'xpath'
        else:
            return 'text'
    
    def _determine_poco_element_type(self, selector_type: str) -> ElementType:
        """确定Poco元素类型"""
        type_mapping = {
            'id': ElementType.POCO_ID,
            'text': ElementType.POCO_TEXT,
            'attr': ElementType.POCO_ATTR,
            'class': ElementType.POCO_ATTR,
            'xpath': ElementType.POCO_ATTR
        }
        return type_mapping.get(selector_type, ElementType.UNKNOWN)
    
    def _map_operation_to_action(self, operation_type: str) -> ActionType:
        """映射操作类型到动作类型"""
        mapping = {
            'touch': ActionType.TOUCH,
            'click': ActionType.CLICK,
            'swipe': ActionType.SWIPE,
            'input': ActionType.INPUT,
            'wait': ActionType.WAIT,
            'assert': ActionType.ASSERT,
            'assert_exists': ActionType.ASSERT
        }
        return mapping.get(operation_type, ActionType.UNKNOWN)


class UnifiedElementMapper(IElementMapper):
    """统一元素映射器"""
    
    def __init__(self, output_dir: str = "mapping_output", 
                 similarity_weights: Dict[str, float] = None,
                 confidence_threshold: float = 0.5):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.extractor = UnifiedElementExtractor()
        self.confidence_threshold = confidence_threshold
        
        # 相似度权重配置
        self.similarity_weights = similarity_weights or {
            'position': 0.4,
            'semantic': 0.3,
            'sequence': 0.2,
            'temporal': 0.1
        }
        
        # 导航栏关键词
        self.navigation_keywords = [
            '首页', 'home', '发现', 'discover', '我的', 'mine', 'profile',
            '设置', 'setting', '消息', 'message', '通知', 'notification',
            '搜索', 'search', '返回', 'back', '确定', 'confirm', '取消', 'cancel'
        ]
    
    def create_mappings(self, airtest_elements: List[ElementInfo], 
                       poco_elements: List[ElementInfo]) -> List[ElementMapping]:
        """创建元素映射关系"""
        mappings = []
        
        # 转换为内部数据结构
        airtest_internal = self._convert_to_airtest_elements(airtest_elements)
        poco_internal = self._convert_to_poco_elements(poco_elements)
        
        # 创建基础映射
        basic_mappings = self._create_basic_mappings(airtest_internal, poco_internal)
        
        # 创建导航栏专用映射
        navigation_mappings = self._create_navigation_mappings(airtest_internal, poco_internal)
        
        # 合并映射结果
        all_mappings = basic_mappings + navigation_mappings
        
        # 去重和优化
        optimized_mappings = self._optimize_mappings(all_mappings)
        
        return optimized_mappings
    
    def calculate_similarity(self, element1: ElementInfo, element2: ElementInfo) -> float:
        """计算两个元素的相似度"""
        # 转换为内部格式
        if element1.element_type == ElementType.TEMPLATE:
            airtest_elem = self._convert_to_airtest_element(element1)
            poco_elem = self._convert_to_poco_element(element2)
        else:
            airtest_elem = self._convert_to_airtest_element(element2)
            poco_elem = self._convert_to_poco_element(element1)
        
        if not airtest_elem or not poco_elem:
            return 0.0
        
        return self._calculate_element_similarity(airtest_elem, poco_elem)
    
    def validate_mapping(self, mapping: ElementMapping) -> bool:
        """验证映射关系的有效性"""
        if not mapping:
            return False
        
        # 检查基本字段
        if not mapping.mapping_id or mapping.confidence < 0 or mapping.confidence > 1:
            return False
        
        # 检查至少有一个元素
        if not mapping.airtest_element and not mapping.poco_element:
            return False
        
        # 检查关联类型
        valid_types = [ct.value for ct in CorrelationType]
        if mapping.correlation_type.value not in valid_types:
            return False
        
        return True
    
    def analyze_from_files(self, airtest_file: str, poco_file: str) -> List[ElementMapping]:
        """从文件分析元素映射"""
        # 读取文件内容
        airtest_content = self._read_file(airtest_file)
        poco_content = self._read_file(poco_file)
        
        if not airtest_content or not poco_content:
            return []
        
        # 提取元素
        airtest_elements = self.extractor.extract_elements(airtest_content)
        poco_elements = self.extractor.extract_elements(poco_content)
        
        # 创建映射
        mappings = self.create_mappings(airtest_elements, poco_elements)
        
        return mappings
    
    def _create_basic_mappings(self, airtest_elements: List[AirtestElement], 
                              poco_elements: List[PocoElement]) -> List[ElementMapping]:
        """创建基础映射"""
        mappings = []
        
        for airtest_elem in airtest_elements:
            best_match = None
            best_similarity = 0.0
            best_evidence = []
            best_semantic = ""
            
            for poco_elem in poco_elements:
                similarity, evidence, semantic = self._calculate_element_similarity_detailed(
                    airtest_elem, poco_elem
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = poco_elem
                    best_evidence = evidence
                    best_semantic = semantic
            
            if best_match and best_similarity > 0.3:  # 最低相似度阈值
                correlation_type = self._determine_correlation_type(best_similarity)
                mapping_id = generate_mapping_id(airtest_elem, best_match)
                
                mapping = ElementMapping(
                    mapping_id=mapping_id,
                    airtest_element=airtest_elem,
                    poco_element=best_match,
                    correlation_type=correlation_type,
                    confidence=best_similarity,
                    evidence=best_evidence,
                    semantic_name=best_semantic
                )
                mappings.append(mapping)
        
        return mappings
    
    def _create_navigation_mappings(self, airtest_elements: List[AirtestElement], 
                                   poco_elements: List[PocoElement]) -> List[ElementMapping]:
        """创建导航栏专用映射"""
        mappings = []
        
        # 识别导航相关元素
        nav_airtest = [elem for elem in airtest_elements 
                      if self._is_navigation_element(elem)]
        nav_poco = [elem for elem in poco_elements 
                   if self._is_navigation_element_poco(elem)]
        
        # 为导航元素创建特殊映射逻辑
        for airtest_elem in nav_airtest:
            for poco_elem in nav_poco:
                # 导航元素使用更宽松的匹配条件
                similarity = self._calculate_navigation_similarity(airtest_elem, poco_elem)
                
                if similarity > 0.5:  # 导航元素的阈值
                    correlation_type = CorrelationType.PROBABLE
                    mapping_id = generate_mapping_id(airtest_elem, poco_elem)
                    
                    mapping = ElementMapping(
                        mapping_id=mapping_id,
                        airtest_element=airtest_elem,
                        poco_element=poco_elem,
                        correlation_type=correlation_type,
                        confidence=similarity,
                        evidence=[f"导航元素匹配: {similarity:.2f}"],
                        semantic_name="导航元素"
                    )
                    mappings.append(mapping)
        
        return mappings
    
    def _calculate_element_similarity(self, airtest_elem: AirtestElement, 
                                    poco_elem: PocoElement) -> float:
        """计算元素相似度"""
        similarity, _, _ = self._calculate_element_similarity_detailed(airtest_elem, poco_elem)
        return similarity
    
    def _calculate_element_similarity_detailed(self, airtest_elem: AirtestElement, 
                                             poco_elem: PocoElement) -> Tuple[float, List[str], str]:
        """计算详细的元素相似度"""
        evidence = []
        semantic_name = ""
        
        # 位置相似度
        position_sim = self._calculate_position_similarity(airtest_elem, poco_elem)
        if position_sim > 0.7:
            evidence.append(f"位置高度相似: {position_sim:.2f}")
        
        # 语义相似度
        semantic_sim, semantic_name = self._calculate_semantic_similarity(airtest_elem, poco_elem)
        if semantic_sim > 0.6:
            evidence.append(f"语义相似: {semantic_name}")
        
        # 序列相似度
        sequence_sim = self._calculate_sequence_similarity(airtest_elem, poco_elem)
        if sequence_sim > 0.5:
            evidence.append(f"序列位置相似: {sequence_sim:.2f}")
        
        # 时序相似度
        temporal_sim = self._calculate_temporal_similarity(airtest_elem, poco_elem)
        if temporal_sim > 0.5:
            evidence.append(f"时序相似: {temporal_sim:.2f}")
        
        # 加权计算总相似度
        total_similarity = (
            position_sim * self.similarity_weights['position'] +
            semantic_sim * self.similarity_weights['semantic'] +
            sequence_sim * self.similarity_weights['sequence'] +
            temporal_sim * self.similarity_weights['temporal']
        )
        
        return total_similarity, evidence, semantic_name
    
    def _calculate_position_similarity(self, airtest_elem: AirtestElement, 
                                     poco_elem: PocoElement) -> float:
        """计算位置相似度"""
        # 基于屏幕位置的相似度计算
        # 这里简化处理，实际应该考虑屏幕分辨率等因素
        if not airtest_elem.record_pos:
            return 0.0
        
        # 假设poco元素也有位置信息（实际需要从运行时获取）
        # 这里使用模拟逻辑
        x, y = airtest_elem.record_pos
        
        # 根据位置判断相似度
        if y < 0.2:  # 顶部区域
            return 0.8 if '首页' in poco_elem.selector or 'home' in poco_elem.selector.lower() else 0.3
        elif y > 0.8:  # 底部区域
            return 0.9 if any(keyword in poco_elem.selector.lower() 
                            for keyword in ['tab', 'bottom', '底部']) else 0.4
        else:  # 中间区域
            return 0.6
    
    def _calculate_semantic_similarity(self, airtest_elem: AirtestElement, 
                                     poco_elem: PocoElement) -> Tuple[float, str]:
        """计算语义相似度"""
        # 从模板文件名提取语义
        template_name = os.path.basename(airtest_elem.template_file).lower()
        selector_text = poco_elem.selector.lower()
        
        # 关键词匹配
        keywords_mapping = {
            'home': ['首页', 'home', 'main'],
            'discover': ['发现', 'discover', 'explore'],
            'mine': ['我的', 'mine', 'profile', 'user'],
            'setting': ['设置', 'setting', 'config'],
            'search': ['搜索', 'search', 'find'],
            'back': ['返回', 'back', 'previous'],
            'confirm': ['确定', 'confirm', 'ok', 'yes'],
            'cancel': ['取消', 'cancel', 'no']
        }
        
        max_similarity = 0.0
        best_semantic = ""
        
        for semantic, keywords in keywords_mapping.items():
            for keyword in keywords:
                if keyword in template_name or keyword in selector_text:
                    similarity = 0.9 if keyword in template_name and keyword in selector_text else 0.7
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_semantic = semantic
        
        return max_similarity, best_semantic
    
    def _calculate_sequence_similarity(self, airtest_elem: AirtestElement, 
                                     poco_elem: PocoElement) -> float:
        """计算序列相似度"""
        # 基于行号的相似度
        line_diff = abs(airtest_elem.line_number - poco_elem.line_number)
        if line_diff <= 2:
            return 0.9
        elif line_diff <= 5:
            return 0.7
        elif line_diff <= 10:
            return 0.5
        else:
            return 0.2
    
    def _calculate_temporal_similarity(self, airtest_elem: AirtestElement, 
                                     poco_elem: PocoElement) -> float:
        """计算时序相似度"""
        # 基于操作类型的相似度
        operation_similarity = {
            ('touch', 'click'): 0.9,
            ('click', 'touch'): 0.9,
            ('touch', 'touch'): 1.0,
            ('click', 'click'): 1.0,
            ('wait', 'wait'): 1.0
        }
        
        key = (airtest_elem.operation_type, poco_elem.operation_type)
        return operation_similarity.get(key, 0.3)
    
    def _calculate_navigation_similarity(self, airtest_elem: AirtestElement, 
                                       poco_elem: PocoElement) -> float:
        """计算导航元素相似度"""
        # 导航元素的特殊相似度计算
        template_name = os.path.basename(airtest_elem.template_file).lower()
        selector_text = poco_elem.selector.lower()
        
        # 检查导航关键词
        nav_score = 0.0
        for keyword in self.navigation_keywords:
            if keyword.lower() in template_name or keyword.lower() in selector_text:
                nav_score += 0.3
        
        # 位置加权（导航通常在顶部或底部）
        if airtest_elem.record_pos:
            y = airtest_elem.record_pos[1]
            if y < 0.2 or y > 0.8:  # 顶部或底部
                nav_score += 0.4
        
        return min(nav_score, 1.0)
    
    def _is_navigation_element(self, airtest_elem: AirtestElement) -> bool:
        """判断是否为导航元素"""
        template_name = os.path.basename(airtest_elem.template_file).lower()
        return any(keyword.lower() in template_name for keyword in self.navigation_keywords)
    
    def _is_navigation_element_poco(self, poco_elem: PocoElement) -> bool:
        """判断Poco元素是否为导航元素"""
        selector_text = poco_elem.selector.lower()
        return any(keyword.lower() in selector_text for keyword in self.navigation_keywords)
    
    def _determine_correlation_type(self, confidence: float) -> CorrelationType:
        """确定关联类型"""
        if confidence >= 0.9:
            return CorrelationType.EXACT
        elif confidence >= 0.7:
            return CorrelationType.STRONG
        elif confidence >= 0.5:
            return CorrelationType.PROBABLE
        elif confidence >= 0.3:
            return CorrelationType.POSSIBLE
        else:
            return CorrelationType.NONE
    
    def _optimize_mappings(self, mappings: List[ElementMapping]) -> List[ElementMapping]:
        """优化映射结果"""
        # 去重
        unique_mappings = {}
        for mapping in mappings:
            key = (mapping.airtest_element.template_file if mapping.airtest_element else None,
                  mapping.poco_element.selector if mapping.poco_element else None)
            
            if key not in unique_mappings or mapping.confidence > unique_mappings[key].confidence:
                unique_mappings[key] = mapping
        
        # 按置信度排序
        optimized = list(unique_mappings.values())
        optimized.sort(key=lambda x: x.confidence, reverse=True)
        
        return optimized
    
    def _convert_to_airtest_elements(self, elements: List[ElementInfo]) -> List[AirtestElement]:
        """转换为Airtest元素"""
        airtest_elements = []
        for elem in elements:
            if elem.element_type == ElementType.TEMPLATE:
                airtest_elem = AirtestElement(
                    template_file=elem.locator,
                    operation_type=elem.attributes.get('operation_type', 'touch'),
                    record_pos=elem.attributes.get('record_pos', (0.5, 0.5)),
                    resolution=elem.attributes.get('resolution', (1080, 1920)),
                    line_number=elem.line_number,
                    vector=elem.attributes.get('vector')
                )
                airtest_elements.append(airtest_elem)
        return airtest_elements
    
    def _convert_to_poco_elements(self, elements: List[ElementInfo]) -> List[PocoElement]:
        """转换为Poco元素"""
        poco_elements = []
        for elem in elements:
            if elem.element_type in [ElementType.POCO_ID, ElementType.POCO_TEXT, ElementType.POCO_ATTR]:
                poco_elem = PocoElement(
                    selector=elem.locator,
                    selector_type=elem.attributes.get('selector_type', 'text'),
                    operation_type=elem.attributes.get('operation_type', 'click'),
                    line_number=elem.line_number,
                    operation_params=elem.attributes.get('operation_params')
                )
                poco_elements.append(poco_elem)
        return poco_elements
    
    def _convert_to_airtest_element(self, element: ElementInfo) -> Optional[AirtestElement]:
        """转换单个元素为Airtest元素"""
        if element.element_type != ElementType.TEMPLATE:
            return None
        
        return AirtestElement(
            template_file=element.locator,
            operation_type=element.attributes.get('operation_type', 'touch'),
            record_pos=element.attributes.get('record_pos', (0.5, 0.5)),
            resolution=element.attributes.get('resolution', (1080, 1920)),
            line_number=element.line_number,
            vector=element.attributes.get('vector')
        )
    
    def _convert_to_poco_element(self, element: ElementInfo) -> Optional[PocoElement]:
        """转换单个元素为Poco元素"""
        if element.element_type not in [ElementType.POCO_ID, ElementType.POCO_TEXT, ElementType.POCO_ATTR]:
            return None
        
        return PocoElement(
            selector=element.locator,
            selector_type=element.attributes.get('selector_type', 'text'),
            operation_type=element.attributes.get('operation_type', 'click'),
            line_number=element.line_number,
            operation_params=element.attributes.get('operation_params')
        )
    
    def _read_file(self, file_path: str) -> Optional[str]:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return None