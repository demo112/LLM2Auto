#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的Airtest与Poco元素映射分析器
解决时序匹配和语义识别问题
"""

import os
import re
import shutil
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import math

@dataclass(frozen=True)
class AirtestElement:
    """Airtest元素数据类"""
    template_file: str
    operation_type: str
    record_pos: Tuple[float, float]
    resolution: Tuple[int, int]
    line_number: int
    vector: Optional[Tuple[float, float]] = None

@dataclass(frozen=True)
class PocoElement:
    """Poco元素数据类"""
    selector: str
    selector_type: str
    operation_type: str
    line_number: int
    operation_params: Optional[str] = None

@dataclass
class ElementMapping:
    """元素映射关系"""
    airtest_element: Optional[AirtestElement]
    poco_element: Optional[PocoElement]
    correlation_type: str  # 'strong', 'probable', 'possible', 'none'
    confidence: float
    evidence: List[str] = field(default_factory=list)
    semantic_name: str = ""

class ImprovedAirtestPocoMapper:
    """改进的Airtest与Poco元素映射分析器"""
    
    def __init__(self, airtest_file: str, poco_file: str, output_dir: str = "../improved_mapping_output"):
        self.airtest_file = airtest_file
        self.poco_file = poco_file
        self.output_dir = output_dir
        self.airtest_elements: List[AirtestElement] = []
        self.poco_elements: List[PocoElement] = []
        self.mappings: List[ElementMapping] = []
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "screenshots"), exist_ok=True)
        
        # 语义映射字典
        self.semantic_mapping = {
            "家庭": ["home", "家庭", "首页"],
            "事件": ["event", "事件", "活动"],
            "安全模式": ["security", "安全", "安全模式", "safe"],
            "账号": ["account", "账号", "用户", "profile"]
        }
        
    def extract_airtest_elements(self) -> List[AirtestElement]:
        """提取Airtest元素"""
        elements = []
        
        with open(self.airtest_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 匹配touch操作
            touch_match = re.search(r'touch\(Template\(r"([^"]+)",\s*record_pos=\(([^)]+)\),\s*resolution=\(([^)]+)\)\)\)', line)
            if touch_match:
                template_file = touch_match.group(1)
                pos_str = touch_match.group(2)
                res_str = touch_match.group(3)
                
                pos = tuple(map(float, pos_str.split(', ')))
                resolution = tuple(map(int, res_str.split(', ')))
                
                elements.append(AirtestElement(
                    template_file=template_file,
                    operation_type="touch",
                    record_pos=pos,
                    resolution=resolution,
                    line_number=i
                ))
            
            # 匹配swipe操作
            swipe_match = re.search(r'swipe\(Template\(r"([^"]+)",\s*record_pos=\(([^)]+)\),\s*resolution=\(([^)]+)\)\),\s*vector=\[([^\]]+)\]\)', line)
            if swipe_match:
                template_file = swipe_match.group(1)
                pos_str = swipe_match.group(2)
                res_str = swipe_match.group(3)
                vector_str = swipe_match.group(4)
                
                pos = tuple(map(float, pos_str.split(', ')))
                resolution = tuple(map(int, res_str.split(', ')))
                vector = tuple(map(float, vector_str.split(', ')))
                
                elements.append(AirtestElement(
                    template_file=template_file,
                    operation_type="swipe",
                    record_pos=pos,
                    resolution=resolution,
                    line_number=i,
                    vector=vector
                ))
        
        self.airtest_elements = elements
        return elements
    
    def extract_poco_elements(self) -> List[PocoElement]:
        """提取Poco元素"""
        elements = []
        
        with open(self.poco_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 匹配poco操作
            # poco("selector").click()
            click_match = re.search(r'poco\(([^)]+)\)\.click\(\)', line)
            if click_match:
                selector_content = click_match.group(1)
                
                # 判断选择器类型
                if selector_content.startswith('text='):
                    selector = selector_content.replace('text=', '').strip('"')
                    selector_type = "text"
                elif selector_content.startswith('"') and selector_content.endswith('"'):
                    selector = selector_content.strip('"')
                    # 判断是ID还是文本
                    if ":" in selector or "\n" in selector:
                        selector_type = "id"
                    else:
                        selector_type = "text"
                else:
                    selector = selector_content.strip('"')
                    selector_type = "unknown"
                
                elements.append(PocoElement(
                    selector=selector,
                    selector_type=selector_type,
                    operation_type="click",
                    line_number=i
                ))
            
            # poco("selector").swipe([vector])
            swipe_match = re.search(r'poco\(([^)]+)\)\.swipe\(\[([^\]]+)\]\)', line)
            if swipe_match:
                selector_content = swipe_match.group(1)
                vector_str = swipe_match.group(2)
                
                if selector_content.startswith('"') and selector_content.endswith('"'):
                    selector = selector_content.strip('"')
                    selector_type = "id" if ":" in selector else "text"
                else:
                    selector = selector_content
                    selector_type = "unknown"
                
                elements.append(PocoElement(
                    selector=selector,
                    selector_type=selector_type,
                    operation_type="swipe",
                    line_number=i,
                    operation_params=vector_str
                ))
        
        self.poco_elements = elements
        return elements
    
    def extract_semantic_from_poco(self, poco_element: PocoElement) -> str:
        """从Poco元素中提取语义信息"""
        selector = poco_element.selector
        
        # 直接文本匹配
        for semantic, keywords in self.semantic_mapping.items():
            for keyword in keywords:
                if keyword in selector:
                    return semantic
        
        # 特殊处理带序号的标签
        if "标签" in selector:
            if "第 1 个" in selector:
                return "家庭"
            elif "第 2 个" in selector:
                return "事件"
            elif "第 3 个" in selector:
                return "安全模式"
            elif "第 4 个" in selector:
                return "账号"
        
        return "未知"
    
    def calculate_sequence_similarity(self, airtest_elem: AirtestElement, poco_elem: PocoElement) -> float:
        """计算时序相似度"""
        # 获取两个测试用例中底部导航操作的起始行号
        airtest_nav_start = 10  # Airtest中底部导航从第10行开始
        poco_nav_start = 28     # Poco中底部导航从第28行开始
        
        # 计算在各自导航序列中的相对位置
        airtest_relative_pos = airtest_elem.line_number - airtest_nav_start
        poco_relative_pos = poco_elem.line_number - poco_nav_start
        
        # 如果相对位置匹配，给予高分
        if airtest_relative_pos == poco_relative_pos and airtest_relative_pos >= 0:
            return 0.9
        
        # 如果相对位置接近，给予中等分数
        if abs(airtest_relative_pos - poco_relative_pos) <= 1 and airtest_relative_pos >= 0:
            return 0.6
        
        return 0.1
    
    def calculate_semantic_similarity(self, airtest_elem: AirtestElement, poco_elem: PocoElement) -> Tuple[float, str]:
        """计算语义相似度"""
        poco_semantic = self.extract_semantic_from_poco(poco_elem)
        
        # 特殊处理：Youkey Life应用图标
        if "Youkey Life" in poco_elem.selector:
            return 0.95, "Youkey Life应用启动图标"
        
        # 系统按钮匹配
        if "com.android.systemui:id/home" in poco_elem.selector:
            # 检查Airtest元素位置是否在底部系统区域
            if airtest_elem.record_pos[1] > 0.9:  # Y坐标大于0.9表示在底部
                return 0.8, "系统Home按钮"
        
        if "com.android.systemui:id/back" in poco_elem.selector:
            return 0.7, "系统返回按钮"
        
        # 底部导航标签匹配
        if poco_semantic != "未知":
            # 检查Airtest元素是否在底部导航区域
            if 0.8 < airtest_elem.record_pos[1] < 0.95:  # 底部导航区域
                return 0.85, f"{poco_semantic}标签"
        
        return 0.1, "未知功能"
    
    def calculate_position_similarity(self, airtest_elem: AirtestElement, poco_elem: PocoElement) -> float:
        """计算位置相似度"""
        # 对于底部导航元素，主要看Y坐标
        if 0.8 < airtest_elem.record_pos[1] < 0.95:
            # 底部导航区域的元素
            return 0.7
        
        # 对于其他区域的元素
        return 0.5
    
    def create_improved_mappings(self) -> List[ElementMapping]:
        """创建改进的元素映射"""
        mappings = []
        used_poco_elements = set()
        
        # 首先处理高置信度的直接匹配
        for airtest_elem in self.airtest_elements:
            best_match = None
            best_confidence = 0
            best_evidence = []
            best_semantic = ""
            
            for poco_elem in self.poco_elements:
                if poco_elem in used_poco_elements:
                    continue
                
                # 计算各种相似度
                sequence_sim = self.calculate_sequence_similarity(airtest_elem, poco_elem)
                semantic_sim, semantic_name = self.calculate_semantic_similarity(airtest_elem, poco_elem)
                position_sim = self.calculate_position_similarity(airtest_elem, poco_elem)
                
                # 综合置信度计算（时序权重最高）
                confidence = (sequence_sim * 0.5 + semantic_sim * 0.35 + position_sim * 0.15)
                
                evidence = []
                if sequence_sim > 0.8:
                    evidence.append("执行顺序完全匹配")
                elif sequence_sim > 0.5:
                    evidence.append("执行顺序基本匹配")
                
                if semantic_sim > 0.8:
                    evidence.append("语义功能高度一致")
                elif semantic_sim > 0.6:
                    evidence.append("语义功能基本一致")
                
                if position_sim > 0.6:
                    evidence.append("位置区域匹配")
                
                if confidence > best_confidence:
                    best_match = poco_elem
                    best_confidence = confidence
                    best_evidence = evidence
                    best_semantic = semantic_name
            
            # 确定关联类型
            if best_confidence > 0.8:
                correlation_type = "strong"
            elif best_confidence > 0.6:
                correlation_type = "probable"
            elif best_confidence > 0.4:
                correlation_type = "possible"
            else:
                correlation_type = "none"
            
            if best_match and best_confidence > 0.4:
                used_poco_elements.add(best_match)
                mappings.append(ElementMapping(
                    airtest_element=airtest_elem,
                    poco_element=best_match,
                    correlation_type=correlation_type,
                    confidence=best_confidence,
                    evidence=best_evidence,
                    semantic_name=best_semantic
                ))
            else:
                mappings.append(ElementMapping(
                    airtest_element=airtest_elem,
                    poco_element=None,
                    correlation_type="none",
                    confidence=0.0,
                    evidence=["无匹配的Poco元素"],
                    semantic_name="未知功能"
                ))
        
        # 处理未匹配的Poco元素
        for poco_elem in self.poco_elements:
            if poco_elem not in used_poco_elements:
                semantic_name = self.extract_semantic_from_poco(poco_elem)
                mappings.append(ElementMapping(
                    airtest_element=None,
                    poco_element=poco_elem,
                    correlation_type="none",
                    confidence=0.0,
                    evidence=["无对应的Airtest模板元素"],
                    semantic_name=f"Poco独有元素: {semantic_name}"
                ))
        
        self.mappings = mappings
        return mappings
    
    def copy_screenshots(self):
        """复制Airtest模板截图"""
        airtest_dir = os.path.dirname(self.airtest_file)
        target_dir = os.path.join(self.output_dir, "screenshots")
        
        copied_count = 0
        for element in self.airtest_elements:
            src_path = os.path.join(airtest_dir, element.template_file)
            dst_path = os.path.join(target_dir, element.template_file)
            
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                copied_count += 1
                print(f"已复制截图: {element.template_file}")
        
        print(f"总共复制了 {copied_count} 个截图文件")
    
    def generate_improved_report(self) -> str:
        """生成改进的映射报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.output_dir, f"improved_mapping_report_{timestamp}.md")
        
        # 统计信息
        correlation_stats = {}
        for mapping in self.mappings:
            correlation_stats[mapping.correlation_type] = correlation_stats.get(mapping.correlation_type, 0) + 1
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 改进的Airtest与Poco元素映射分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**分析对象**: Youkey Life APP UI元素  \n")
            f.write(f"**Airtest元素数量**: {len(self.airtest_elements)}  \n")
            f.write(f"**Poco元素数量**: {len(self.poco_elements)}  \n")
            f.write(f"**映射关系数量**: {len(self.mappings)}  \n\n")
            
            f.write("---\n\n")
            f.write("## 📊 映射关系概览\n\n")
            f.write("### 关联类型分布\n\n")
            
            for corr_type, count in correlation_stats.items():
                f.write(f"- **{corr_type}**: {count} 个\n")
            
            f.write("\n## 🔗 详细映射关系\n\n")
            
            for i, mapping in enumerate(self.mappings, 1):
                f.write(f"### 映射 {i}: {mapping.semantic_name}\n\n")
                f.write(f"**关联类型**: {mapping.correlation_type}  \n")
                f.write(f"**置信度**: {mapping.confidence:.2%}  \n\n")
                
                if mapping.airtest_element:
                    f.write("#### 🎯 Airtest元素\n\n")
                    elem = mapping.airtest_element
                    f.write(f"- **模板文件**: `{elem.template_file}`\n")
                    f.write(f"- **操作类型**: `{elem.operation_type}`\n")
                    f.write(f"- **记录位置**: `{elem.record_pos}`\n")
                    f.write(f"- **屏幕分辨率**: `{elem.resolution}`\n")
                    f.write(f"- **代码行号**: `{elem.line_number}`\n")
                    if elem.vector:
                        f.write(f"- **滑动向量**: `{elem.vector}`\n")
                    
                    f.write("\n#### 📸 元素截图\n\n")
                    f.write(f"![{elem.template_file}](screenshots/{elem.template_file})\n\n")
                    f.write(f"*截图文件: {elem.template_file}*\n\n")
                else:
                    f.write("#### 🎯 Airtest元素\n\n")
                    f.write("*无对应的Airtest模板元素*\n\n")
                
                if mapping.poco_element:
                    f.write("#### 🎯 Poco元素\n\n")
                    elem = mapping.poco_element
                    f.write(f"- **选择器**: `{elem.selector}`\n")
                    f.write(f"- **选择器类型**: `{elem.selector_type}`\n")
                    f.write(f"- **操作类型**: `{elem.operation_type}`\n")
                    f.write(f"- **代码行号**: `{elem.line_number}`\n")
                    if elem.operation_params:
                        f.write(f"- **操作参数**: `{elem.operation_params}`\n")
                else:
                    f.write("#### 🎯 Poco元素\n\n")
                    f.write("*无对应的Poco元素*\n\n")
                
                f.write("#### 🧩 关联证据\n\n")
                if mapping.evidence:
                    for evidence in mapping.evidence:
                        f.write(f"- {evidence}\n")
                else:
                    f.write("- 无关联证据\n")
                
                f.write("\n---\n\n")
            
            # 优化建议
            f.write("## 💡 优化建议\n\n")
            f.write("### 元素定位策略优化\n\n")
            f.write("1. **时序优先策略**: 基于执行顺序进行元素匹配，确保逻辑一致性\n")
            f.write("2. **语义增强策略**: 结合元素语义信息提高匹配准确性\n")
            f.write("3. **双重验证机制**: 实现Airtest和Poco的互相验证\n\n")
            
            f.write("### 测试用例优化\n\n")
            f.write("1. **统一执行逻辑**: 确保两种测试方式的执行顺序一致\n")
            f.write("2. **语义标识统一**: 为相同功能的元素建立统一的语义标识\n")
            f.write("3. **增强稳定性**: 对于高置信度映射，优先使用Poco定位\n\n")
            
            f.write("---\n\n")
            f.write("*本报告由 改进的Airtest与Poco元素映射分析器 自动生成*\n")
        
        return report_file
    
    def run_analysis(self):
        """运行完整的分析流程"""
        print("开始改进的元素映射分析...")
        
        # 提取元素
        print("提取Airtest元素...")
        airtest_elements = self.extract_airtest_elements()
        print(f"发现 {len(airtest_elements)} 个Airtest元素")
        
        print("提取Poco元素...")
        poco_elements = self.extract_poco_elements()
        print(f"发现 {len(poco_elements)} 个Poco元素")
        
        # 创建映射
        print("创建改进的元素映射...")
        mappings = self.create_improved_mappings()
        print(f"创建了 {len(mappings)} 个映射关系")
        
        # 复制截图
        print("复制Airtest模板截图...")
        self.copy_screenshots()
        
        # 生成报告
        print("生成改进的映射报告...")
        report_file = self.generate_improved_report()
        print(f"报告已生成: {report_file}")
        
        return report_file

def main():
    """主函数"""
    airtest_file = "/Users/cooperd/UNV/TraeProject/演示项目/tests/mobile/test_case_demo.air/test_case_demo.py"
    poco_file = "/Users/cooperd/UNV/TraeProject/演示项目/tests/mobile/test_case_demo_poco.air/test_case_demo_poco.py"
    
    mapper = ImprovedAirtestPocoMapper(airtest_file, poco_file)
    report_file = mapper.run_analysis()
    
    print(f"\n改进的映射分析完成！")
    print(f"报告文件: {report_file}")

if __name__ == "__main__":
    main()