# -*- encoding=utf8 -*-
"""
操作步骤对齐模块

负责分析和对齐Airtest和Poco脚本中的操作步骤，
建立两种实现方式之间的对应关系
"""

import re
import ast
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """操作类型枚举"""
    CLICK = "click"
    SWIPE = "swipe"
    INPUT = "input"
    WAIT = "wait"
    ASSERT = "assert"
    SETUP = "setup"
    OTHER = "other"


@dataclass
class ActionStep:
    """操作步骤"""
    action_type: ActionType
    target: str  # 目标元素描述
    parameters: Dict[str, Any]  # 操作参数
    line_number: int  # 行号
    original_code: str  # 原始代码
    implementation: str  # 实现方式: 'airtest' 或 'poco'
    confidence: float = 1.0  # 匹配置信度


@dataclass
class AlignedStepPair:
    """对齐的步骤对"""
    airtest_step: Optional[ActionStep] = None
    poco_step: Optional[ActionStep] = None
    alignment_confidence: float = 0.0  # 对齐置信度
    semantic_description: str = ""  # 语义描述


class StepAlignment:
    """步骤对齐器"""
    
    def __init__(self):
        self.airtest_steps: List[ActionStep] = []
        self.poco_steps: List[ActionStep] = []
        self.aligned_pairs: List[AlignedStepPair] = []
        
    def parse_airtest_script(self, script_path: str) -> List[ActionStep]:
        """
        解析Airtest脚本，提取操作步骤
        
        Args:
            script_path: 脚本文件路径
            
        Returns:
            List[ActionStep]: 操作步骤列表
        """
        steps = []
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                step = self._parse_airtest_line(line, line_num)
                if step:
                    steps.append(step)
                    
        except Exception as e:
            print(f"解析Airtest脚本失败: {e}")
            
        self.airtest_steps = steps
        return steps
    
    def parse_poco_script(self, script_path: str) -> List[ActionStep]:
        """
        解析Poco脚本，提取操作步骤
        
        Args:
            script_path: 脚本文件路径
            
        Returns:
            List[ActionStep]: 操作步骤列表
        """
        steps = []
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                step = self._parse_poco_line(line, line_num)
                if step:
                    steps.append(step)
                    
        except Exception as e:
            print(f"解析Poco脚本失败: {e}")
            
        self.poco_steps = steps
        return steps
    
    def _parse_airtest_line(self, line: str, line_num: int) -> Optional[ActionStep]:
        """解析Airtest代码行"""
        # 点击操作
        if 'touch(' in line:
            target = self._extract_template_info(line)
            return ActionStep(
                action_type=ActionType.CLICK,
                target=target,
                parameters=self._extract_airtest_params(line),
                line_number=line_num,
                original_code=line,
                implementation='airtest'
            )
        
        # 滑动操作
        elif 'swipe(' in line:
            target = self._extract_template_info(line)
            vector = self._extract_vector_info(line)
            return ActionStep(
                action_type=ActionType.SWIPE,
                target=target,
                parameters={'vector': vector},
                line_number=line_num,
                original_code=line,
                implementation='airtest'
            )
        
        # 输入操作
        elif 'text(' in line:
            return ActionStep(
                action_type=ActionType.INPUT,
                target="input_field",
                parameters=self._extract_airtest_params(line),
                line_number=line_num,
                original_code=line,
                implementation='airtest'
            )
        
        # 等待操作
        elif 'sleep(' in line or 'wait(' in line:
            return ActionStep(
                action_type=ActionType.WAIT,
                target="time",
                parameters=self._extract_airtest_params(line),
                line_number=line_num,
                original_code=line,
                implementation='airtest'
            )
        
        # 设置操作
        elif 'auto_setup(' in line:
            return ActionStep(
                action_type=ActionType.SETUP,
                target="environment",
                parameters={},
                line_number=line_num,
                original_code=line,
                implementation='airtest'
            )
        
        return None
    
    def _parse_poco_line(self, line: str, line_num: int) -> Optional[ActionStep]:
        """解析Poco代码行"""
        # 点击操作
        if '.click()' in line:
            target = self._extract_poco_selector(line)
            return ActionStep(
                action_type=ActionType.CLICK,
                target=target,
                parameters=self._extract_poco_params(line),
                line_number=line_num,
                original_code=line,
                implementation='poco'
            )
        
        # 滑动操作
        elif '.swipe(' in line:
            target = self._extract_poco_selector(line)
            vector = self._extract_poco_swipe_vector(line)
            return ActionStep(
                action_type=ActionType.SWIPE,
                target=target,
                parameters={'vector': vector},
                line_number=line_num,
                original_code=line,
                implementation='poco'
            )
        
        # 输入操作
        elif '.set_text(' in line:
            target = self._extract_poco_selector(line)
            return ActionStep(
                action_type=ActionType.INPUT,
                target=target,
                parameters=self._extract_poco_params(line),
                line_number=line_num,
                original_code=line,
                implementation='poco'
            )
        
        # 等待操作
        elif 'sleep(' in line or 'time.sleep(' in line:
            return ActionStep(
                action_type=ActionType.WAIT,
                target="time",
                parameters=self._extract_poco_params(line),
                line_number=line_num,
                original_code=line,
                implementation='poco'
            )
        
        # Poco初始化
        elif 'AndroidUiautomationPoco(' in line:
            return ActionStep(
                action_type=ActionType.SETUP,
                target="poco_driver",
                parameters={},
                line_number=line_num,
                original_code=line,
                implementation='poco'
            )
        
        return None
    
    def _extract_template_info(self, line: str) -> str:
        """从Airtest代码中提取模板信息"""
        match = re.search(r'Template\s*\(\s*r?"([^"]+)"', line)
        if match:
            return match.group(1)
        return "unknown_template"
    
    def _extract_vector_info(self, line: str) -> List[float]:
        """从Airtest代码中提取滑动向量"""
        match = re.search(r'vector\s*=\s*\[([^\]]+)\]', line)
        if match:
            try:
                vector_str = match.group(1)
                return [float(x.strip()) for x in vector_str.split(',')]
            except:
                pass
        return [0.0, 0.0]
    
    def _extract_poco_selector(self, line: str) -> str:
        """从Poco代码中提取选择器信息"""
        # 提取poco()调用中的参数
        match = re.search(r'poco\s*\(([^)]+)\)', line)
        if match:
            selector = match.group(1).strip()
            # 移除引号
            if selector.startswith('"') and selector.endswith('"'):
                selector = selector[1:-1]
            elif selector.startswith("'") and selector.endswith("'"):
                selector = selector[1:-1]
            return selector
        return "unknown_element"
    
    def _extract_poco_swipe_vector(self, line: str) -> List[float]:
        """从Poco代码中提取滑动向量"""
        match = re.search(r'\.swipe\s*\(\s*\[([^\]]+)\]', line)
        if match:
            try:
                vector_str = match.group(1)
                return [float(x.strip()) for x in vector_str.split(',')]
            except:
                pass
        return [0.0, 0.0]
    
    def _extract_airtest_params(self, line: str) -> Dict[str, Any]:
        """提取Airtest操作参数"""
        params = {}
        # 这里可以根据需要提取更多参数
        return params
    
    def _extract_poco_params(self, line: str) -> Dict[str, Any]:
        """提取Poco操作参数"""
        params = {}
        # 提取text参数
        text_match = re.search(r'text\s*=\s*"([^"]+)"', line)
        if text_match:
            params['text'] = text_match.group(1)
        return params
    
    def align_steps(self) -> List[AlignedStepPair]:
        """
        对齐操作步骤
        
        Returns:
            List[AlignedStepPair]: 对齐的步骤对列表
        """
        self.aligned_pairs = []
        
        # 过滤掉设置步骤
        airtest_actions = [s for s in self.airtest_steps if s.action_type != ActionType.SETUP]
        poco_actions = [s for s in self.poco_steps if s.action_type != ActionType.SETUP]
        
        # 简单的顺序对齐策略
        max_len = max(len(airtest_actions), len(poco_actions))
        
        for i in range(max_len):
            airtest_step = airtest_actions[i] if i < len(airtest_actions) else None
            poco_step = poco_actions[i] if i < len(poco_actions) else None
            
            # 计算对齐置信度
            confidence = self._calculate_alignment_confidence(airtest_step, poco_step)
            
            # 生成语义描述
            description = self._generate_semantic_description(airtest_step, poco_step)
            
            pair = AlignedStepPair(
                airtest_step=airtest_step,
                poco_step=poco_step,
                alignment_confidence=confidence,
                semantic_description=description
            )
            
            self.aligned_pairs.append(pair)
        
        return self.aligned_pairs
    
    def _calculate_alignment_confidence(self, 
                                     airtest_step: Optional[ActionStep], 
                                     poco_step: Optional[ActionStep]) -> float:
        """计算对齐置信度"""
        if not airtest_step or not poco_step:
            return 0.5  # 单边匹配
        
        if airtest_step.action_type == poco_step.action_type:
            return 0.9  # 操作类型匹配
        
        return 0.3  # 操作类型不匹配
    
    def _generate_semantic_description(self, 
                                     airtest_step: Optional[ActionStep], 
                                     poco_step: Optional[ActionStep]) -> str:
        """生成语义描述"""
        if airtest_step and poco_step:
            action_type = airtest_step.action_type.value
            return f"{action_type}操作 (Airtest + Poco)"
        elif airtest_step:
            action_type = airtest_step.action_type.value
            return f"{action_type}操作 (仅Airtest)"
        elif poco_step:
            action_type = poco_step.action_type.value
            return f"{action_type}操作 (仅Poco)"
        else:
            return "未知操作"
    
    def print_alignment_summary(self):
        """打印对齐结果摘要"""
        print("=== 步骤对齐结果 ===")
        print(f"Airtest步骤数: {len(self.airtest_steps)}")
        print(f"Poco步骤数: {len(self.poco_steps)}")
        print(f"对齐步骤对数: {len(self.aligned_pairs)}")
        print()
        
        for i, pair in enumerate(self.aligned_pairs, 1):
            print(f"步骤 {i}: {pair.semantic_description}")
            print(f"  置信度: {pair.alignment_confidence:.2f}")
            
            if pair.airtest_step:
                print(f"  Airtest: {pair.airtest_step.original_code}")
            
            if pair.poco_step:
                print(f"  Poco: {pair.poco_step.original_code}")
            
            print()