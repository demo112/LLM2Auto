# -*- encoding=utf8 -*-
"""
增强的脚本解析器

负责解析airtest和poco脚本，提取完整的代码块和操作步骤，
保持原始代码的完整性，支持融合脚本的持久化需求
"""

import ast
import re
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class OperationType(Enum):
    """操作类型枚举"""
    CLICK = "click"
    SWIPE = "swipe"
    DRAG = "drag"
    PINCH = "pinch"
    ZOOM = "zoom"
    LONG_CLICK = "long_click"
    DOUBLE_CLICK = "double_click"
    SCROLL = "scroll"
    KEYEVENT = "keyevent"
    INPUT = "input"
    WAIT = "wait"
    ASSERT = "assert"
    SETUP = "setup"
    IMPORT = "import"
    VARIABLE = "variable"
    OTHER = "other"


@dataclass
class CodeBlock:
    """代码块"""
    content: str                    # 完整代码内容
    start_line: int                 # 起始行号
    end_line: int                   # 结束行号
    imports: List[str] = field(default_factory=list)     # 依赖导入
    variables: Dict[str, Any] = field(default_factory=dict)  # 变量定义
    raw_lines: List[str] = field(default_factory=list)   # 原始行内容


@dataclass
class OperationStep:
    """操作步骤"""
    step_id: str                    # 步骤唯一标识
    description: str                # 步骤描述
    operation_type: OperationType   # 操作类型
    target_element: str             # 目标元素
    parameters: Dict[str, Any] = field(default_factory=dict)      # 操作参数
    airtest_code: Optional[CodeBlock] = None  # Airtest代码块
    poco_code: Optional[CodeBlock] = None     # Poco代码块
    confidence_score: float = 0.0   # 匹配置信度
    semantic_tags: List[str] = field(default_factory=list)  # 语义标签


@dataclass
class ScriptMetadata:
    """脚本元数据"""
    file_path: str
    script_type: str  # 'airtest' 或 'poco'
    total_lines: int
    imports: List[str] = field(default_factory=list)
    global_variables: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


class EnhancedScriptParser:
    """增强的脚本解析器"""
    
    def __init__(self):
        self.airtest_patterns = {
            'touch': r'touch\s*\(',
            'swipe': r'swipe\s*\(',
            'text': r'text\s*\(',
            'wait': r'wait\s*\(',
            'assert_exists': r'assert_exists\s*\(',
            'template': r'Template\s*\(',
            'auto_setup': r'auto_setup\s*\(',
        }
        
        self.poco_patterns = {
            'click': r'\.click\s*\(',
            'swipe': r'\.swipe\s*\(',
            'set_text': r'\.set_text\s*\(',
            'wait_for_appearance': r'\.wait_for_appearance\s*\(',
            'exists': r'\.exists\s*\(',
            'poco_selector': r'poco\s*\(',
        }
    
    def parse_script_file(self, script_path: str) -> Tuple[ScriptMetadata, List[OperationStep]]:
        """
        解析脚本文件
        
        Args:
            script_path: 脚本文件路径
            
        Returns:
            Tuple[ScriptMetadata, List[OperationStep]]: 元数据和操作步骤列表
        """
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"脚本文件不存在: {script_path}")
        
        # 读取文件内容
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 检测脚本类型
        script_type = self._detect_script_type(lines)
        
        # 创建元数据
        metadata = ScriptMetadata(
            file_path=script_path,
            script_type=script_type,
            total_lines=len(lines)
        )
        
        # 解析AST
        try:
            tree = ast.parse(''.join(lines))
            self._extract_metadata_from_ast(tree, metadata)
        except SyntaxError as e:
            print(f"警告: AST解析失败 {script_path}: {e}")
        
        # 解析操作步骤
        steps = self._parse_operation_steps(lines, script_type)
        
        return metadata, steps
    
    def _detect_script_type(self, lines: List[str]) -> str:
        """检测脚本类型"""
        content = ''.join(lines)
        
        # 检查特征导入和API调用
        if 'from poco' in content or 'AndroidUiautomationPoco' in content:
            return 'poco'
        elif 'from airtest' in content or 'Template(' in content:
            return 'airtest'
        else:
            # 基于API调用模式判断
            airtest_score = sum(1 for pattern in self.airtest_patterns.values() 
                              if re.search(pattern, content))
            poco_score = sum(1 for pattern in self.poco_patterns.values() 
                           if re.search(pattern, content))
            
            return 'poco' if poco_score > airtest_score else 'airtest'
    
    def _extract_metadata_from_ast(self, tree: ast.AST, metadata: ScriptMetadata):
        """从AST提取元数据"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    metadata.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    metadata.imports.append(full_name)
            elif isinstance(node, ast.Assign):
                # 提取全局变量赋值
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        try:
                            # 尝试获取简单的字面值
                            if isinstance(node.value, (ast.Str, ast.Num, ast.Constant)):
                                if hasattr(node.value, 'value'):
                                    metadata.global_variables[target.id] = node.value.value
                                elif hasattr(node.value, 's'):  # Python < 3.8
                                    metadata.global_variables[target.id] = node.value.s
                                elif hasattr(node.value, 'n'):  # Python < 3.8
                                    metadata.global_variables[target.id] = node.value.n
                        except:
                            pass
    
    def _parse_operation_steps(self, lines: List[str], script_type: str) -> List[OperationStep]:
        """解析操作步骤"""
        steps = []
        step_counter = 1
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过空行和注释
            if not line or line.startswith('#'):
                i += 1
                continue
            
            # 跳过导入语句
            if line.startswith(('import ', 'from ')):
                i += 1
                continue
            
            # 检测操作
            operation_info = self._detect_operation(line, script_type)
            if operation_info:
                # 提取完整的代码块
                code_block, end_line = self._extract_code_block(lines, i)
                
                # 创建操作步骤
                step = OperationStep(
                    step_id=f"step_{step_counter:03d}",
                    description=self._generate_step_description(operation_info, line),
                    operation_type=operation_info['type'],
                    target_element=operation_info['target'],
                    parameters=operation_info['parameters']
                )
                
                # 设置对应的代码块
                if script_type == 'airtest':
                    step.airtest_code = code_block
                else:
                    step.poco_code = code_block
                
                # 添加语义标签
                step.semantic_tags = self._extract_semantic_tags(line, operation_info)
                
                steps.append(step)
                step_counter += 1
                i = end_line + 1
            else:
                i += 1
        
        return steps
    
    def _detect_operation(self, line: str, script_type: str) -> Optional[Dict[str, Any]]:
        """检测操作类型和参数"""
        patterns = self.airtest_patterns if script_type == 'airtest' else self.poco_patterns
        
        for op_name, pattern in patterns.items():
            if re.search(pattern, line):
                return self._extract_operation_details(line, op_name, script_type)
        
        return None
    
    def _extract_operation_details(self, line: str, op_name: str, script_type: str) -> Dict[str, Any]:
        """提取操作详细信息"""
        operation_info = {
            'type': self._map_to_operation_type(op_name),
            'target': '',
            'parameters': {}
        }
        
        if script_type == 'airtest':
            operation_info.update(self._extract_airtest_details(line, op_name))
        else:
            operation_info.update(self._extract_poco_details(line, op_name))
        
        return operation_info
    
    def _extract_airtest_details(self, line: str, op_name: str) -> Dict[str, Any]:
        """提取Airtest操作详情"""
        details = {'target': '', 'parameters': {}}
        
        if op_name == 'touch':
            # 提取Template信息
            template_match = re.search(r'Template\s*\(\s*r?"([^"]+)"', line)
            if template_match:
                details['target'] = template_match.group(1)
            
            # 提取位置信息
            pos_match = re.search(r'record_pos\s*=\s*\(([^)]+)\)', line)
            if pos_match:
                details['parameters']['position'] = pos_match.group(1)
        
        elif op_name == 'swipe':
            # 提取起始Template
            template_match = re.search(r'Template\s*\(\s*r?"([^"]+)"', line)
            if template_match:
                details['target'] = template_match.group(1)
            
            # 提取滑动向量
            vector_match = re.search(r'vector\s*=\s*\[([^\]]+)\]', line)
            if vector_match:
                details['parameters']['vector'] = vector_match.group(1)
        
        elif op_name == 'text':
            # 提取输入文本
            text_match = re.search(r'text\s*\(\s*["\']([^"\']+)["\']', line)
            if text_match:
                details['parameters']['text'] = text_match.group(1)
        
        return details
    
    def _extract_poco_details(self, line: str, op_name: str) -> Dict[str, Any]:
        """提取Poco操作详情"""
        details = {'target': '', 'parameters': {}}
        
        # 提取poco选择器
        selector_patterns = [
            r'poco\s*\(\s*["\']([^"\']+)["\']',  # poco("selector")
            r'poco\s*\(\s*text\s*=\s*["\']([^"\']+)["\']',  # poco(text="text")
            r'poco\s*\(\s*([^)]+)\)',  # poco(complex_selector)
        ]
        
        for pattern in selector_patterns:
            match = re.search(pattern, line)
            if match:
                details['target'] = match.group(1)
                break
        
        if op_name == 'click':
            # 点击操作通常没有额外参数
            pass
        
        elif op_name == 'swipe':
            # 提取滑动向量
            vector_match = re.search(r'swipe\s*\(\s*\[([^\]]+)\]', line)
            if vector_match:
                details['parameters']['vector'] = vector_match.group(1)
        
        elif op_name == 'set_text':
            # 提取输入文本
            text_match = re.search(r'set_text\s*\(\s*["\']([^"\']+)["\']', line)
            if text_match:
                details['parameters']['text'] = text_match.group(1)
        
        return details
    
    def _extract_code_block(self, lines: List[str], start_line: int) -> Tuple[CodeBlock, int]:
        """提取完整的代码块"""
        # 简单实现：单行代码块
        # 可以扩展为多行代码块检测
        line = lines[start_line]
        
        code_block = CodeBlock(
            content=line.strip(),
            start_line=start_line + 1,  # 1-based line numbers
            end_line=start_line + 1,
            raw_lines=[line]
        )
        
        return code_block, start_line
    
    def _map_to_operation_type(self, op_name: str) -> OperationType:
        """映射操作名称到操作类型"""
        mapping = {
            'touch': OperationType.CLICK,
            'click': OperationType.CLICK,
            'swipe': OperationType.SWIPE,
            'text': OperationType.INPUT,
            'set_text': OperationType.INPUT,
            'wait': OperationType.WAIT,
            'wait_for_appearance': OperationType.WAIT,
            'assert_exists': OperationType.ASSERT,
            'exists': OperationType.ASSERT,
            'auto_setup': OperationType.SETUP,
        }
        return mapping.get(op_name, OperationType.OTHER)
    
    def _generate_step_description(self, operation_info: Dict[str, Any], line: str) -> str:
        """生成步骤描述"""
        op_type = operation_info['type']
        target = operation_info['target']
        
        if op_type == OperationType.CLICK:
            return f"点击 {target}" if target else "执行点击操作"
        elif op_type == OperationType.SWIPE:
            return f"在 {target} 上滑动" if target else "执行滑动操作"
        elif op_type == OperationType.INPUT:
            text = operation_info['parameters'].get('text', '')
            return f"在 {target} 输入文本: {text}" if target else f"输入文本: {text}"
        elif op_type == OperationType.WAIT:
            return f"等待 {target} 出现" if target else "等待操作"
        elif op_type == OperationType.ASSERT:
            return f"验证 {target} 存在" if target else "执行断言"
        elif op_type == OperationType.SETUP:
            return "初始化设置"
        else:
            return f"执行操作: {line[:50]}..."
    
    def _extract_semantic_tags(self, line: str, operation_info: Dict[str, Any]) -> List[str]:
        """提取语义标签"""
        tags = []
        
        # 基于操作类型添加标签
        op_type = operation_info['type']
        tags.append(op_type.value)
        
        # 基于目标元素添加标签
        target = operation_info['target'].lower()
        if 'home' in target:
            tags.append('navigation')
        elif 'button' in target or 'btn' in target:
            tags.append('button_interaction')
        elif 'input' in target or 'text' in target:
            tags.append('text_input')
        elif 'tab' in target:
            tags.append('tab_navigation')
        
        # 基于参数添加标签
        if 'vector' in operation_info['parameters']:
            tags.append('gesture')
        
        return tags


def parse_script_pair(airtest_path: str, poco_path: str) -> Tuple[List[OperationStep], List[OperationStep]]:
    """
    解析脚本对
    
    Args:
        airtest_path: Airtest脚本路径
        poco_path: Poco脚本路径
        
    Returns:
        Tuple[List[OperationStep], List[OperationStep]]: Airtest和Poco操作步骤列表
    """
    parser = EnhancedScriptParser()
    
    # 解析Airtest脚本
    airtest_metadata, airtest_steps = parser.parse_script_file(airtest_path)
    
    # 解析Poco脚本
    poco_metadata, poco_steps = parser.parse_script_file(poco_path)
    
    return airtest_steps, poco_steps


if __name__ == "__main__":
    # 测试解析器
    parser = EnhancedScriptParser()
    
    # 测试路径
    test_airtest = "/Users/cooperd/UNV/TraeProject/演示项目/tests/mobile/test_case_demo_airtest.air/test_case_demo_airtest.py"
    test_poco = "/Users/cooperd/UNV/TraeProject/演示项目/tests/mobile/test_case_demo_poco.air/test_case_demo_poco.py"
    
    try:
        airtest_steps, poco_steps = parse_script_pair(test_airtest, test_poco)
        
        print(f"Airtest步骤数量: {len(airtest_steps)}")
        for step in airtest_steps:
            print(f"  - {step.step_id}: {step.description}")
        
        print(f"\nPoco步骤数量: {len(poco_steps)}")
        for step in poco_steps:
            print(f"  - {step.step_id}: {step.description}")
            
    except Exception as e:
        print(f"解析失败: {e}")