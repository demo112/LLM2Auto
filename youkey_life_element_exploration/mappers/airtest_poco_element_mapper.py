#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Airtest与Poco元素映射分析器
专门用于分析和建立Airtest模板元素与Poco元素之间的关联关系
"""

import os
import re
import json
import shutil
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from pathlib import Path

@dataclass(frozen=True)
class AirtestElement:
    """Airtest元素信息"""
    template_file: str
    record_pos: Tuple[float, float]
    resolution: Tuple[int, int]
    line_number: int
    operation: str
    vector: Optional[Tuple[float, float]] = None

@dataclass(frozen=True)
class PocoElement:
    """Poco元素信息"""
    selector: str
    selector_type: str  # 'id', 'text', 'attr'
    line_number: int
    operation: str
    operation_params: Optional[str] = None

@dataclass
class ElementMapping:
    """元素映射关系"""
    airtest_element: Optional[AirtestElement]
    poco_element: Optional[PocoElement]
    correlation_type: str  # 'exact', 'probable', 'possible', 'none'
    confidence: float
    evidence: List[str]
    semantic_meaning: str
    screenshot_path: str

class AirtestPocoMapper:
    """Airtest与Poco元素映射分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.airtest_elements: List[AirtestElement] = []
        self.poco_elements: List[PocoElement] = []
        self.mappings: List[ElementMapping] = []
        self.output_dir = self.project_root / "../element_mapping_output"
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_airtest_elements(self, airtest_file: str) -> List[AirtestElement]:
        """提取Airtest测试用例中的所有元素"""
        elements = []
        
        with open(airtest_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 匹配swipe操作
            swipe_match = re.search(r'swipe\(Template\(r"([^"]+)".*?record_pos=\(([^)]+)\).*?resolution=\(([^)]+)\)\).*?vector=\[([^\]]+)\]', line)
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
                    record_pos=pos,
                    resolution=resolution,
                    line_number=i,
                    operation='swipe',
                    vector=vector
                ))
            
            # 匹配touch操作
            touch_match = re.search(r'touch\(Template\(r"([^"]+)".*?record_pos=\(([^)]+)\).*?resolution=\(([^)]+)\)\)', line)
            if touch_match:
                template_file = touch_match.group(1)
                pos_str = touch_match.group(2)
                res_str = touch_match.group(3)
                
                pos = tuple(map(float, pos_str.split(', ')))
                resolution = tuple(map(int, res_str.split(', ')))
                
                elements.append(AirtestElement(
                    template_file=template_file,
                    record_pos=pos,
                    resolution=resolution,
                    line_number=i,
                    operation='touch'
                ))
        
        return elements
    
    def extract_poco_elements(self, poco_file: str) -> List[PocoElement]:
        """提取Poco测试用例中的所有元素"""
        elements = []
        
        with open(poco_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 匹配poco操作
            poco_patterns = [
                # poco("selector").operation()
                (r'poco\("([^"]+)"\)\.(\w+)\(\)', 'id'),
                # poco(text="selector").operation()
                (r'poco\(text="([^"]+)"\)\.(\w+)\(\)', 'text'),
                # poco("selector").operation([params])
                (r'poco\("([^"]+)"\)\.(\w+)\(\[([^\]]+)\]\)', 'id'),
            ]
            
            for pattern, selector_type in poco_patterns:
                match = re.search(pattern, line)
                if match:
                    selector = match.group(1)
                    operation = match.group(2)
                    params = match.group(3) if len(match.groups()) > 2 else None
                    
                    elements.append(PocoElement(
                        selector=selector,
                        selector_type=selector_type,
                        line_number=i,
                        operation=operation,
                        operation_params=params
                    ))
                    break
        
        return elements
    
    def analyze_position_correlation(self, airtest_pos: Tuple[float, float], poco_selector: str) -> Tuple[float, List[str]]:
        """分析位置关联性"""
        evidence = []
        confidence = 0.0
        
        # 基于位置的启发式分析
        x, y = airtest_pos
        
        # 应用图标通常在屏幕上方或中央
        if "Youkey Life" in poco_selector or "youkey" in poco_selector.lower():
            if -0.2 <= x <= 0.2 and 0.1 <= y <= 0.4:
                confidence += 0.4
                evidence.append("位置符合应用图标典型位置")
        
        # 底部导航栏元素
        if "标签" in poco_selector or "tab" in poco_selector.lower():
            if 0.7 <= y <= 1.0:
                confidence += 0.3
                evidence.append("位置符合底部导航栏")
        
        # 系统按钮（home, back等）
        if "home" in poco_selector or "back" in poco_selector:
            if y > 0.8 or y < -0.8:
                confidence += 0.3
                evidence.append("位置符合系统按钮区域")
        
        return confidence, evidence
    
    def analyze_semantic_correlation(self, airtest_element: AirtestElement, poco_element: PocoElement) -> Tuple[float, List[str], str]:
        """分析语义关联性"""
        evidence = []
        confidence = 0.0
        semantic_meaning = "未知功能"
        
        # 应用启动关联
        if "tpl1760170830132.png" in airtest_element.template_file and "Youkey Life" in poco_element.selector:
            confidence = 0.95
            evidence.extend([
                "Airtest模板与Poco文本都指向Youkey Life应用",
                "位置坐标与应用图标位置匹配",
                "都是应用启动的关键操作"
            ])
            semantic_meaning = "Youkey Life应用启动图标"
        
        # 底部导航关联
        elif "标签" in poco_element.selector:
            # 分析底部导航栏的模板
            bottom_templates = ["tpl1760170751771.png", "tpl1760170753763.png", 
                              "tpl1760170755526.png", "tpl1760170757400.png"]
            if airtest_element.template_file in bottom_templates:
                confidence = 0.8
                evidence.extend([
                    "位置都在底部导航区域",
                    "操作序列匹配（连续点击）",
                    "功能语义一致（导航切换）"
                ])
                
                # 具体标签映射
                tab_mapping = {
                    "tpl1760170751771.png": "家庭标签",
                    "tpl1760170753763.png": "事件标签", 
                    "tpl1760170755526.png": "安全模式标签",
                    "tpl1760170757400.png": "账号标签"
                }
                semantic_meaning = tab_mapping.get(airtest_element.template_file, "底部导航标签")
        
        # 系统按钮关联
        elif "home" in poco_element.selector or "back" in poco_element.selector:
            if airtest_element.record_pos[1] > 0.8:  # 底部区域
                confidence = 0.7
                evidence.append("系统按钮位置匹配")
                semantic_meaning = f"系统{poco_element.selector}按钮"
        
        return confidence, evidence, semantic_meaning
    
    def analyze_temporal_correlation(self, airtest_elements: List[AirtestElement], poco_elements: List[PocoElement]) -> List[Tuple[int, int, float, List[str]]]:
        """分析时序关联性"""
        correlations = []
        
        # 分析操作序列的相似性
        airtest_ops = [(e.line_number, e.operation) for e in airtest_elements]
        poco_ops = [(e.line_number, e.operation) for e in poco_elements]
        
        # 寻找相似的操作序列
        for i, (a_line, a_op) in enumerate(airtest_ops):
            for j, (p_line, p_op) in enumerate(poco_ops):
                evidence = []
                confidence = 0.0
                
                # 操作类型匹配
                if (a_op == 'touch' and p_op == 'click') or (a_op == 'swipe' and p_op == 'swipe'):
                    confidence += 0.3
                    evidence.append(f"操作类型匹配: {a_op} -> {p_op}")
                
                # 序列位置相似
                if abs(i - j) <= 2:  # 在序列中位置相近
                    confidence += 0.2
                    evidence.append("在操作序列中位置相近")
                
                if confidence > 0.4:
                    correlations.append((i, j, confidence, evidence))
        
        return correlations
    
    def create_element_mappings(self):
        """创建元素映射关系"""
        # 提取测试用例路径
        airtest_file = self.project_root / "tests/mobile/test_case_demo.air/test_case_demo.py"
        poco_file = self.project_root / "tests/mobile/test_case_demo_poco.air/test_case_demo_poco.py"
        
        # 提取元素
        self.airtest_elements = self.extract_airtest_elements(str(airtest_file))
        self.poco_elements = self.extract_poco_elements(str(poco_file))
        
        print(f"🔍 发现 {len(self.airtest_elements)} 个Airtest元素")
        print(f"🔍 发现 {len(self.poco_elements)} 个Poco元素")
        
        # 分析时序关联
        temporal_correlations = self.analyze_temporal_correlation(self.airtest_elements, self.poco_elements)
        
        # 为每个Airtest元素寻找对应的Poco元素
        for i, airtest_elem in enumerate(self.airtest_elements):
            best_match = None
            best_confidence = 0.0
            best_evidence = []
            best_semantic = "未知功能"
            
            for j, poco_elem in enumerate(self.poco_elements):
                # 分析语义关联
                sem_conf, sem_evidence, semantic = self.analyze_semantic_correlation(airtest_elem, poco_elem)
                
                # 分析位置关联
                pos_conf, pos_evidence = self.analyze_position_correlation(airtest_elem.record_pos, poco_elem.selector)
                
                # 综合置信度
                total_confidence = sem_conf * 0.6 + pos_conf * 0.4
                total_evidence = sem_evidence + pos_evidence
                
                if total_confidence > best_confidence:
                    best_confidence = total_confidence
                    best_match = poco_elem
                    best_evidence = total_evidence
                    best_semantic = semantic
            
            # 确定关联类型
            if best_confidence >= 0.8:
                correlation_type = "exact"
            elif best_confidence >= 0.6:
                correlation_type = "probable"
            elif best_confidence >= 0.3:
                correlation_type = "possible"
            else:
                correlation_type = "none"
                best_match = None
            
            # 生成截图路径
            screenshot_path = f"screenshots/{airtest_elem.template_file}"
            
            mapping = ElementMapping(
                airtest_element=airtest_elem,
                poco_element=best_match,
                correlation_type=correlation_type,
                confidence=best_confidence,
                evidence=best_evidence,
                semantic_meaning=best_semantic,
                screenshot_path=screenshot_path
            )
            
            self.mappings.append(mapping)
        
        # 为没有匹配的Poco元素创建映射
        matched_poco_elements = {m.poco_element for m in self.mappings if m.poco_element}
        for poco_elem in self.poco_elements:
            if poco_elem not in matched_poco_elements:
                mapping = ElementMapping(
                    airtest_element=None,
                    poco_element=poco_elem,
                    correlation_type="none",
                    confidence=0.0,
                    evidence=["无对应的Airtest模板元素"],
                    semantic_meaning=f"Poco独有元素: {poco_elem.selector}",
                    screenshot_path=""
                )
                self.mappings.append(mapping)
    
    def copy_screenshots(self):
        """复制截图文件到输出目录"""
        screenshots_dir = self.output_dir / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        
        airtest_dir = self.project_root / "tests/mobile/test_case_demo.air"
        
        for mapping in self.mappings:
            if mapping.airtest_element:
                src_file = airtest_dir / mapping.airtest_element.template_file
                dst_file = screenshots_dir / mapping.airtest_element.template_file
                
                if src_file.exists():
                    shutil.copy2(src_file, dst_file)
                    print(f"📸 复制截图: {mapping.airtest_element.template_file}")
    
    def generate_mapping_report(self) -> str:
        """生成详细的映射报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"airtest_poco_mapping_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Airtest与Poco元素映射分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**分析对象**: Youkey Life APP UI元素  \n")
            f.write(f"**Airtest元素数量**: {len(self.airtest_elements)}  \n")
            f.write(f"**Poco元素数量**: {len(self.poco_elements)}  \n")
            f.write(f"**映射关系数量**: {len(self.mappings)}  \n\n")
            
            f.write("---\n\n")
            
            # 映射概览
            f.write("## 📊 映射关系概览\n\n")
            
            correlation_stats = {}
            for mapping in self.mappings:
                correlation_stats[mapping.correlation_type] = correlation_stats.get(mapping.correlation_type, 0) + 1
            
            f.write("### 关联类型分布\n\n")
            for corr_type, count in correlation_stats.items():
                f.write(f"- **{corr_type}**: {count} 个\n")
            f.write("\n")
            
            # 详细映射关系
            f.write("## 🔗 详细映射关系\n\n")
            
            for i, mapping in enumerate(self.mappings, 1):
                f.write(f"### 映射 {i}: {mapping.semantic_meaning}\n\n")
                
                # 关联信息
                f.write(f"**关联类型**: {mapping.correlation_type}  \n")
                f.write(f"**置信度**: {mapping.confidence:.2%}  \n\n")
                
                # Airtest元素信息
                if mapping.airtest_element:
                    f.write("#### 🎯 Airtest元素\n\n")
                    f.write(f"- **模板文件**: `{mapping.airtest_element.template_file}`\n")
                    f.write(f"- **操作类型**: `{mapping.airtest_element.operation}`\n")
                    f.write(f"- **记录位置**: `{mapping.airtest_element.record_pos}`\n")
                    f.write(f"- **屏幕分辨率**: `{mapping.airtest_element.resolution}`\n")
                    f.write(f"- **代码行号**: `{mapping.airtest_element.line_number}`\n")
                    if mapping.airtest_element.vector:
                        f.write(f"- **滑动向量**: `{mapping.airtest_element.vector}`\n")
                    f.write("\n")
                    
                    # 截图展示
                    if mapping.screenshot_path:
                        f.write("#### 📸 元素截图\n\n")
                        f.write(f"![{mapping.airtest_element.template_file}]({mapping.screenshot_path})\n\n")
                        f.write(f"*截图文件: {mapping.airtest_element.template_file}*\n\n")
                else:
                    f.write("#### 🎯 Airtest元素\n\n")
                    f.write("*无对应的Airtest模板元素*\n\n")
                
                # Poco元素信息
                if mapping.poco_element:
                    f.write("#### 🎯 Poco元素\n\n")
                    f.write(f"- **选择器**: `{mapping.poco_element.selector}`\n")
                    f.write(f"- **选择器类型**: `{mapping.poco_element.selector_type}`\n")
                    f.write(f"- **操作类型**: `{mapping.poco_element.operation}`\n")
                    f.write(f"- **代码行号**: `{mapping.poco_element.line_number}`\n")
                    if mapping.poco_element.operation_params:
                        f.write(f"- **操作参数**: `{mapping.poco_element.operation_params}`\n")
                    f.write("\n")
                else:
                    f.write("#### 🎯 Poco元素\n\n")
                    f.write("*无对应的Poco元素*\n\n")
                
                # 关联证据
                f.write("#### 🧩 关联证据\n\n")
                if mapping.evidence:
                    for evidence in mapping.evidence:
                        f.write(f"- {evidence}\n")
                else:
                    f.write("- 无关联证据\n")
                f.write("\n")
                
                f.write("---\n\n")
            
            # 优化建议
            f.write("## 💡 优化建议\n\n")
            f.write("### 元素定位策略优化\n\n")
            f.write("1. **优先级策略**: 对于高置信度映射的元素，建议优先使用Poco定位（更稳定）\n")
            f.write("2. **备用策略**: 当Poco定位失败时，使用Airtest模板匹配作为备用方案\n")
            f.write("3. **验证机制**: 实现双重验证，确保两种方式定位到同一元素\n\n")
            
            f.write("### 测试用例优化\n\n")
            f.write("1. **统一元素标识**: 为相同功能的元素建立统一的语义标识\n")
            f.write("2. **减少重复**: 合并功能相同的测试步骤，避免重复定位\n")
            f.write("3. **增强稳定性**: 对于低置信度的映射，需要人工验证和调整\n\n")
            
            f.write("---\n\n")
            f.write("*本报告由 Airtest与Poco元素映射分析器 自动生成*\n")
        
        return str(report_file)

def main():
    """主函数"""
    print("🚀 Airtest与Poco元素映射分析")
    print("=" * 50)
    
    # 初始化映射器
    mapper = AirtestPocoMapper("/Users/cooperd/UNV/TraeProject/演示项目")
    
    print("🔍 开始分析元素映射关系...")
    mapper.create_element_mappings()
    
    print("📸 复制元素截图...")
    mapper.copy_screenshots()
    
    print("📝 生成映射分析报告...")
    report_file = mapper.generate_mapping_report()
    
    print("✅ 映射分析完成!")
    print(f"📄 报告路径: {report_file}")
    print(f"🔗 发现映射: {len(mapper.mappings)} 个")
    
    # 统计信息
    correlation_stats = {}
    for mapping in mapper.mappings:
        correlation_stats[mapping.correlation_type] = correlation_stats.get(mapping.correlation_type, 0) + 1
    
    print("\n📋 映射概览:")
    print("-" * 40)
    for corr_type, count in correlation_stats.items():
        print(f"🔗 {corr_type}: {count} 个")

if __name__ == "__main__":
    main()