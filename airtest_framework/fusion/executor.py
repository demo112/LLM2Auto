# -*- encoding=utf8 -*-
"""
多维度执行器

负责执行融合的测试用例，当主策略失败时自动切换到备用策略
"""

import time
import traceback
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .alignment import AlignedStepPair, ActionStep, ActionType


class ExecutionStrategy(Enum):
    """执行策略"""
    AIRTEST_FIRST = "airtest_first"  # Airtest优先
    POCO_FIRST = "poco_first"  # Poco优先
    PARALLEL = "parallel"  # 并行执行


class ExecutionResult(Enum):
    """执行结果"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    FALLBACK = "fallback"  # 回退执行


@dataclass
class StepExecutionResult:
    """步骤执行结果"""
    step_index: int
    result: ExecutionResult
    execution_time: float
    error_message: str = ""
    used_strategy: str = ""  # 使用的策略
    fallback_used: bool = False  # 是否使用了回退


@dataclass
class FusionExecutionResult:
    """融合执行结果"""
    case_name: str
    total_steps: int
    successful_steps: int
    failed_steps: int
    fallback_steps: int
    total_execution_time: float
    step_results: List[StepExecutionResult]
    overall_result: ExecutionResult


class MultiDimensionExecutor:
    """多维度执行器"""
    
    def __init__(self, strategy: ExecutionStrategy = ExecutionStrategy.AIRTEST_FIRST):
        """
        初始化多维度执行器
        
        Args:
            strategy: 执行策略
        """
        self.strategy = strategy
        self.timeout = 30  # 单步超时时间（秒）
        self.retry_count = 2  # 重试次数
        self.fallback_enabled = True  # 是否启用回退
        
        # 执行器映射
        self.executors = {
            'airtest': self._execute_airtest_step,
            'poco': self._execute_poco_step
        }
        
        # 运行时状态
        self.airtest_env = None
        self.poco_driver = None
        self.execution_context = {}
        
    def setup_environment(self, device_uri: str = None):
        """
        设置执行环境
        
        Args:
            device_uri: 设备连接URI
        """
        try:
            # 设置Airtest环境
            from airtest.core.api import auto_setup, connect_device
            if device_uri:
                connect_device(device_uri)
            else:
                auto_setup(__file__)
            
            # 设置Poco环境
            from poco.drivers.android.uiautomation import AndroidUiautomationPoco
            self.poco_driver = AndroidUiautomationPoco(
                use_airtest_input=True, 
                screenshot_each_action=False
            )
            
            print("执行环境设置完成")
            
        except Exception as e:
            print(f"环境设置失败: {e}")
            raise
    
    def execute_fusion_case(self, 
                          case_name: str,
                          aligned_steps: List[AlignedStepPair]) -> FusionExecutionResult:
        """
        执行融合测试用例
        
        Args:
            case_name: 用例名称
            aligned_steps: 对齐的步骤对列表
            
        Returns:
            FusionExecutionResult: 执行结果
        """
        start_time = time.time()
        step_results = []
        successful_steps = 0
        failed_steps = 0
        fallback_steps = 0
        
        print(f"开始执行融合用例: {case_name}")
        print(f"总步骤数: {len(aligned_steps)}")
        
        for i, step_pair in enumerate(aligned_steps):
            print(f"\n执行步骤 {i+1}/{len(aligned_steps)}: {step_pair.semantic_description}")
            
            step_result = self._execute_step_pair(i, step_pair)
            step_results.append(step_result)
            
            if step_result.result == ExecutionResult.SUCCESS:
                successful_steps += 1
            elif step_result.result == ExecutionResult.FAILED:
                failed_steps += 1
            elif step_result.result == ExecutionResult.FALLBACK:
                fallback_steps += 1
                successful_steps += 1  # 回退成功也算成功
            
            # 如果步骤失败且无法回退，可以选择继续或停止
            if step_result.result == ExecutionResult.FAILED and not step_result.fallback_used:
                print(f"步骤 {i+1} 执行失败，继续执行下一步骤")
        
        total_time = time.time() - start_time
        
        # 判断整体结果
        if failed_steps == 0:
            overall_result = ExecutionResult.SUCCESS
        elif successful_steps > failed_steps:
            overall_result = ExecutionResult.FALLBACK
        else:
            overall_result = ExecutionResult.FAILED
        
        result = FusionExecutionResult(
            case_name=case_name,
            total_steps=len(aligned_steps),
            successful_steps=successful_steps,
            failed_steps=failed_steps,
            fallback_steps=fallback_steps,
            total_execution_time=total_time,
            step_results=step_results,
            overall_result=overall_result
        )
        
        self._print_execution_summary(result)
        return result
    
    def _execute_step_pair(self, step_index: int, step_pair: AlignedStepPair) -> StepExecutionResult:
        """
        执行步骤对
        
        Args:
            step_index: 步骤索引
            step_pair: 步骤对
            
        Returns:
            StepExecutionResult: 步骤执行结果
        """
        start_time = time.time()
        
        # 确定主策略和备用策略
        primary_step, fallback_step, primary_type, fallback_type = self._determine_execution_order(step_pair)
        
        # 执行主策略
        if primary_step:
            result = self._execute_single_step(primary_step, primary_type)
            execution_time = time.time() - start_time
            
            if result['success']:
                return StepExecutionResult(
                    step_index=step_index,
                    result=ExecutionResult.SUCCESS,
                    execution_time=execution_time,
                    used_strategy=primary_type,
                    fallback_used=False
                )
        
        # 主策略失败，尝试回退策略
        if self.fallback_enabled and fallback_step:
            print(f"  主策略失败，尝试回退策略: {fallback_type}")
            
            fallback_result = self._execute_single_step(fallback_step, fallback_type)
            execution_time = time.time() - start_time
            
            if fallback_result['success']:
                return StepExecutionResult(
                    step_index=step_index,
                    result=ExecutionResult.FALLBACK,
                    execution_time=execution_time,
                    used_strategy=fallback_type,
                    fallback_used=True
                )
            else:
                return StepExecutionResult(
                    step_index=step_index,
                    result=ExecutionResult.FAILED,
                    execution_time=execution_time,
                    error_message=fallback_result.get('error', ''),
                    used_strategy=fallback_type,
                    fallback_used=True
                )
        
        # 没有可用的回退策略或回退也失败
        execution_time = time.time() - start_time
        error_msg = result.get('error', '') if 'result' in locals() else '无可执行步骤'
        
        return StepExecutionResult(
            step_index=step_index,
            result=ExecutionResult.FAILED,
            execution_time=execution_time,
            error_message=error_msg,
            used_strategy=primary_type if primary_step else 'none',
            fallback_used=False
        )
    
    def _determine_execution_order(self, step_pair: AlignedStepPair) -> tuple:
        """确定执行顺序"""
        if self.strategy == ExecutionStrategy.AIRTEST_FIRST:
            return (step_pair.airtest_step, step_pair.poco_step, 'airtest', 'poco')
        elif self.strategy == ExecutionStrategy.POCO_FIRST:
            return (step_pair.poco_step, step_pair.airtest_step, 'poco', 'airtest')
        else:
            # 默认Airtest优先
            return (step_pair.airtest_step, step_pair.poco_step, 'airtest', 'poco')
    
    def _execute_single_step(self, step: ActionStep, step_type: str) -> Dict[str, Any]:
        """
        执行单个步骤
        
        Args:
            step: 操作步骤
            step_type: 步骤类型 ('airtest' 或 'poco')
            
        Returns:
            Dict: 执行结果
        """
        try:
            executor = self.executors.get(step_type)
            if not executor:
                return {'success': False, 'error': f'未知的执行器类型: {step_type}'}
            
            print(f"    执行 {step_type}: {step.original_code}")
            result = executor(step)
            
            if result['success']:
                print(f"    ✓ 执行成功")
            else:
                print(f"    ✗ 执行失败: {result.get('error', '')}")
            
            return result
            
        except Exception as e:
            error_msg = f"执行异常: {str(e)}"
            print(f"    ✗ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def _execute_airtest_step(self, step: ActionStep) -> Dict[str, Any]:
        """执行Airtest步骤"""
        try:
            from airtest.core.api import touch, swipe, text, sleep, Template
            
            if step.action_type == ActionType.CLICK:
                # 解析Template
                template_path = step.target
                if template_path != "unknown_template":
                    # 构建完整路径
                    full_path = self._resolve_template_path(template_path)
                    template = Template(full_path)
                    touch(template)
                else:
                    return {'success': False, 'error': '无法解析模板路径'}
            
            elif step.action_type == ActionType.SWIPE:
                vector = step.parameters.get('vector', [0, 0])
                template_path = step.target
                if template_path != "unknown_template":
                    full_path = self._resolve_template_path(template_path)
                    template = Template(full_path)
                    swipe(template, vector=vector)
                else:
                    return {'success': False, 'error': '无法解析模板路径'}
            
            elif step.action_type == ActionType.INPUT:
                text_content = step.parameters.get('text', '')
                text(text_content)
            
            elif step.action_type == ActionType.WAIT:
                duration = step.parameters.get('duration', 1)
                sleep(duration)
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_poco_step(self, step: ActionStep) -> Dict[str, Any]:
        """执行Poco步骤"""
        try:
            if not self.poco_driver:
                return {'success': False, 'error': 'Poco驱动未初始化'}
            
            if step.action_type == ActionType.CLICK:
                # 解析选择器
                selector = step.target
                element = self._find_poco_element(selector)
                if element:
                    element.click()
                else:
                    return {'success': False, 'error': f'找不到元素: {selector}'}
            
            elif step.action_type == ActionType.SWIPE:
                selector = step.target
                vector = step.parameters.get('vector', [0, 0])
                element = self._find_poco_element(selector)
                if element:
                    element.swipe(vector)
                else:
                    return {'success': False, 'error': f'找不到元素: {selector}'}
            
            elif step.action_type == ActionType.INPUT:
                selector = step.target
                text_content = step.parameters.get('text', '')
                element = self._find_poco_element(selector)
                if element:
                    element.set_text(text_content)
                else:
                    return {'success': False, 'error': f'找不到元素: {selector}'}
            
            elif step.action_type == ActionType.WAIT:
                duration = step.parameters.get('duration', 1)
                time.sleep(duration)
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _resolve_template_path(self, template_path: str) -> str:
        """解析模板路径"""
        # 这里需要根据实际情况解析相对路径
        # 暂时返回原路径
        return template_path
    
    def _find_poco_element(self, selector: str):
        """查找Poco元素"""
        try:
            # 尝试不同的选择器策略
            if selector.startswith('com.'):
                # 资源ID选择器
                return self.poco_driver(selector)
            else:
                # 文本选择器
                return self.poco_driver(text=selector)
        except:
            return None
    
    def _print_execution_summary(self, result: FusionExecutionResult):
        """打印执行摘要"""
        print(f"\n=== 融合执行结果摘要 ===")
        print(f"用例名称: {result.case_name}")
        print(f"总步骤数: {result.total_steps}")
        print(f"成功步骤: {result.successful_steps}")
        print(f"失败步骤: {result.failed_steps}")
        print(f"回退步骤: {result.fallback_steps}")
        print(f"执行时间: {result.total_execution_time:.2f}秒")
        print(f"整体结果: {result.overall_result.value}")
        
        if result.fallback_steps > 0:
            print(f"\n回退策略使用率: {result.fallback_steps/result.total_steps*100:.1f}%")
        
        print("\n步骤详情:")
        for step_result in result.step_results:
            status_icon = "✓" if step_result.result in [ExecutionResult.SUCCESS, ExecutionResult.FALLBACK] else "✗"
            fallback_info = " (回退)" if step_result.fallback_used else ""
            print(f"  {status_icon} 步骤 {step_result.step_index+1}: {step_result.used_strategy}{fallback_info}")
            if step_result.error_message:
                print(f"    错误: {step_result.error_message}")