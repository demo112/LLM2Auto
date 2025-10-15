# -*- encoding=utf8 -*-
"""
故障切换执行引擎

支持Airtest和Poco之间的智能故障切换，确保测试流程的容错性和连续性
"""

import time
import traceback
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

from .persistence import FusionScript, FusionStep
from .enhanced_parser import OperationType


class ExecutionStrategy(Enum):
    """执行策略"""
    AIRTEST_FIRST = "airtest_first"      # Airtest优先
    POCO_FIRST = "poco_first"            # Poco优先
    PARALLEL = "parallel"                # 并行执行
    ADAPTIVE = "adaptive"                # 自适应选择


class StepResult(Enum):
    """步骤执行结果"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ExecutionConfig:
    """执行配置"""
    strategy: ExecutionStrategy = ExecutionStrategy.ADAPTIVE
    timeout: int = 30                    # 步骤超时时间（秒）
    retry_count: int = 2                 # 重试次数
    failover_enabled: bool = True        # 是否启用故障切换
    screenshot_on_error: bool = True     # 错误时截图
    continue_on_error: bool = True       # 错误时继续执行
    device_id: Optional[str] = None      # 设备ID


@dataclass
class StepExecutionResult:
    """步骤执行结果"""
    step_id: str
    execution_method: str               # airtest 或 poco
    result: StepResult
    execution_time: float
    error_message: str = ""
    screenshot_path: str = ""
    retry_count: int = 0
    fallback_used: bool = False


@dataclass
class FusionExecutionResult:
    """融合执行结果"""
    script_name: str
    total_steps: int
    successful_steps: int
    failed_steps: int
    skipped_steps: int
    total_execution_time: float
    step_results: List[StepExecutionResult]
    overall_success: bool
    error_summary: List[str]


class FailoverExecutor:
    """故障切换执行引擎"""
    
    def __init__(self, config: ExecutionConfig = None):
        """
        初始化执行引擎
        
        Args:
            config: 执行配置
        """
        self.config = config or ExecutionConfig()
        self.poco_driver = None
        self.device = None
        self.execution_context = {}
        
        # 执行统计
        self.stats = {
            'airtest_success': 0,
            'poco_success': 0,
            'failover_count': 0,
            'total_retries': 0
        }
    
    def setup_environment(self, device_uri: str = None):
        """
        设置执行环境
        
        Args:
            device_uri: 设备连接URI
        """
        try:
            # 连接设备
            if device_uri:
                connect_device(device_uri)
            else:
                # 自动连接第一个可用的 Android 设备
                import subprocess
                result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                devices = [line.split('\t')[0] for line in lines if '\tdevice' in line]
                
                if not devices:
                    raise Exception("No Android devices found. Please connect a device and enable USB debugging.")
                
                # 连接第一个可用设备
                device_id = devices[0]
                connect_device(f"Android:///{device_id}")
            
            self.device = device()
            
            # 初始化Poco驱动
            self.poco_driver = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
            
            print("执行环境设置完成")
            
        except Exception as e:
            print(f"设置执行环境失败: {e}")
            raise
    
    def execute_fusion_script(self, fusion_script: FusionScript) -> FusionExecutionResult:
        """
        执行融合脚本
        
        Args:
            fusion_script: 融合脚本
            
        Returns:
            FusionExecutionResult: 执行结果
        """
        print(f"开始执行融合脚本: {fusion_script.metadata.name}")
        
        start_time = time.time()
        step_results = []
        error_summary = []
        
        successful_steps = 0
        failed_steps = 0
        skipped_steps = 0
        
        for step in fusion_script.steps:
            try:
                result = self._execute_fusion_step(step)
                step_results.append(result)
                
                if result.result == StepResult.SUCCESS:
                    successful_steps += 1
                elif result.result == StepResult.FAILED or result.result == StepResult.ERROR:
                    failed_steps += 1
                    error_summary.append(f"步骤 {step.step_id}: {result.error_message}")
                    
                    # 如果不允许错误时继续，则停止执行
                    if not self.config.continue_on_error:
                        print(f"步骤执行失败，停止执行: {result.error_message}")
                        break
                else:
                    skipped_steps += 1
                
                # 步骤间延迟
                time.sleep(0.5)
                
            except Exception as e:
                error_msg = f"执行步骤 {step.step_id} 时发生异常: {str(e)}"
                print(error_msg)
                error_summary.append(error_msg)
                
                step_results.append(StepExecutionResult(
                    step_id=step.step_id,
                    execution_method="unknown",
                    result=StepResult.ERROR,
                    execution_time=0.0,
                    error_message=error_msg
                ))
                
                failed_steps += 1
                
                if not self.config.continue_on_error:
                    break
        
        total_execution_time = time.time() - start_time
        overall_success = failed_steps == 0 and successful_steps > 0
        
        result = FusionExecutionResult(
            script_name=fusion_script.metadata.name,
            total_steps=len(fusion_script.steps),
            successful_steps=successful_steps,
            failed_steps=failed_steps,
            skipped_steps=skipped_steps,
            total_execution_time=total_execution_time,
            step_results=step_results,
            overall_success=overall_success,
            error_summary=error_summary
        )
        
        self._print_execution_summary(result)
        return result
    
    def _execute_fusion_step(self, step: FusionStep) -> StepExecutionResult:
        """
        执行融合步骤
        
        Args:
            step: 融合步骤
            
        Returns:
            StepExecutionResult: 步骤执行结果
        """
        print(f"执行步骤 {step.step_id}: {step.description}")
        
        start_time = time.time()
        
        # 确定执行顺序
        execution_order = self._determine_execution_order(step)
        
        for attempt in range(self.config.retry_count + 1):
            for i, method in enumerate(execution_order):
                success = False
                error_msg = ""
                
                try:
                    if method == "airtest" and step.airtest_code:
                        success = self._execute_airtest_step(step)
                        if success:
                            execution_time = time.time() - start_time
                            self.stats['airtest_success'] += 1
                            return StepExecutionResult(
                                step_id=step.step_id,
                                execution_method="airtest",
                                result=StepResult.SUCCESS,
                                execution_time=execution_time,
                                retry_count=attempt,
                                fallback_used=(i > 0)  # 如果不是第一个方法，说明使用了回退
                            )
                        else:
                            error_msg = f"{method} 执行失败: 方法返回False"
                    
                    elif method == "poco" and step.poco_code:
                        success = self._execute_poco_step(step)
                        if success:
                            execution_time = time.time() - start_time
                            self.stats['poco_success'] += 1
                            return StepExecutionResult(
                                step_id=step.step_id,
                                execution_method="poco",
                                result=StepResult.SUCCESS,
                                execution_time=execution_time,
                                retry_count=attempt,
                                fallback_used=(i > 0)  # 如果不是第一个方法，说明使用了回退
                            )
                        else:
                            error_msg = f"{method} 执行失败: 方法返回False"
                
                except Exception as e:
                    error_msg = f"{method} 执行失败: {str(e)}"
                
                # 如果方法失败（无论是异常还是返回False）
                if not success:
                    print(f"  {error_msg}")
                    
                    # 如果启用故障切换且还有其他方法可尝试
                    if self.config.failover_enabled and i < len(execution_order) - 1:
                        print(f"  尝试故障切换到其他执行方法...")
                        self.stats['failover_count'] += 1
                        continue
                    else:
                        # 如果是最后一个方法也失败了，但还有重试机会，跳出内层循环进行重试
                        if i == len(execution_order) - 1:
                            break
                        
                        # 错误时截图
                        screenshot_path = ""
                        if self.config.screenshot_on_error:
                            screenshot_path = self._take_error_screenshot(step.step_id, attempt)
                        
                        execution_time = time.time() - start_time
                        return StepExecutionResult(
                            step_id=step.step_id,
                            execution_method=method,
                            result=StepResult.ERROR,
                            execution_time=execution_time,
                            error_message=error_msg,
                            screenshot_path=screenshot_path,
                            retry_count=attempt
                        )
            
            # 如果所有方法都失败，等待后重试
            if attempt < self.config.retry_count:
                print(f"  第 {attempt + 1} 次尝试失败，等待重试...")
                time.sleep(1)
                self.stats['total_retries'] += 1
        
        # 所有尝试都失败
        execution_time = time.time() - start_time
        screenshot_path = ""
        if self.config.screenshot_on_error:
            screenshot_path = self._take_error_screenshot(step.step_id, "final")
        
        return StepExecutionResult(
            step_id=step.step_id,
            execution_method="both_failed",
            result=StepResult.FAILED,
            execution_time=execution_time,
            error_message="所有执行方法都失败",
            screenshot_path=screenshot_path,
            retry_count=self.config.retry_count
        )
    
    def _determine_execution_order(self, step: FusionStep) -> List[str]:
        """
        确定执行顺序
        
        Args:
            step: 融合步骤
            
        Returns:
            List[str]: 执行方法顺序
        """
        available_methods = []
        
        if step.airtest_code:
            available_methods.append("airtest")
        
        if step.poco_code:
            available_methods.append("poco")
        
        if not available_methods:
            return []
        
        # 根据策略确定顺序
        if self.config.strategy == ExecutionStrategy.AIRTEST_FIRST:
            return ["airtest", "poco"] if "airtest" in available_methods else ["poco"]
        
        elif self.config.strategy == ExecutionStrategy.POCO_FIRST:
            return ["poco", "airtest"] if "poco" in available_methods else ["airtest"]
        
        elif self.config.strategy == ExecutionStrategy.ADAPTIVE:
            # 自适应策略：根据操作类型和历史成功率选择
            return self._adaptive_order_selection(step, available_methods)
        
        else:  # PARALLEL - 暂时按Airtest优先处理
            return available_methods
    
    def _adaptive_order_selection(self, step: FusionStep, available_methods: List[str]) -> List[str]:
        """
        自适应顺序选择
        
        Args:
            step: 融合步骤
            available_methods: 可用方法
            
        Returns:
            List[str]: 执行方法顺序
        """
        # 根据操作类型选择最佳方法
        operation_type = step.operation_type
        
        # Airtest更适合的操作
        airtest_preferred = [
            OperationType.SWIPE.value,
            OperationType.DRAG.value,
            OperationType.PINCH.value,
            OperationType.KEYEVENT.value
        ]
        
        # Poco更适合的操作
        poco_preferred = [
            OperationType.CLICK.value,
            OperationType.INPUT.value,
            OperationType.SCROLL.value,
            OperationType.WAIT.value
        ]
        
        if operation_type in airtest_preferred and "airtest" in available_methods:
            return ["airtest", "poco"] if "poco" in available_methods else ["airtest"]
        elif operation_type in poco_preferred and "poco" in available_methods:
            return ["poco", "airtest"] if "airtest" in available_methods else ["poco"]
        else:
            # 根据历史成功率选择
            airtest_rate = self.stats['airtest_success'] / max(1, self.stats['airtest_success'] + self.stats['failover_count'])
            poco_rate = self.stats['poco_success'] / max(1, self.stats['poco_success'] + self.stats['failover_count'])
            
            if airtest_rate >= poco_rate:
                return ["airtest", "poco"] if len(available_methods) == 2 else available_methods
            else:
                return ["poco", "airtest"] if len(available_methods) == 2 else available_methods
    
    def _execute_airtest_step(self, step: FusionStep) -> bool:
        """
        执行Airtest步骤
        
        Args:
            step: 融合步骤
            
        Returns:
            bool: 是否执行成功
        """
        if not step.airtest_code:
            return False
        
        try:
            # 构建执行代码
            code_content = step.airtest_code['content']
            
            # 设置超时
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Airtest步骤执行超时")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.config.timeout)
            
            try:
                # 执行代码
                exec_globals = {
                    'touch': touch,
                    'swipe': swipe,
                    'wait': wait,
                    'exists': exists,
                    'find_all': find_all,
                    'sleep': sleep,
                    'keyevent': keyevent,
                    'text': text,
                    'snapshot': snapshot,
                    'Template': Template,
                    'device': device,
                    '__file__': __file__
                }
                
                exec(code_content, exec_globals)
                return True
                
            finally:
                signal.alarm(0)  # 取消超时
        
        except TimeoutError:
            print(f"  Airtest步骤执行超时")
            return False
        except Exception as e:
            print(f"  Airtest步骤执行失败: {str(e)}")
            return False
    
    def _execute_poco_step(self, step: FusionStep) -> bool:
        """
        执行Poco步骤
        
        Args:
            step: 融合步骤
            
        Returns:
            bool: 是否执行成功
        """
        if not step.poco_code or not self.poco_driver:
            return False
        
        try:
            # 构建执行代码
            code_content = step.poco_code['content']
            
            # 设置超时
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Poco步骤执行超时")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.config.timeout)
            
            try:
                # 执行代码
                exec_globals = {
                    'poco': self.poco_driver,
                    'sleep': time.sleep,
                    'TimeoutError': TimeoutError,
                    '__file__': __file__
                }
                
                exec(code_content, exec_globals)
                return True
                
            finally:
                signal.alarm(0)  # 取消超时
        
        except TimeoutError:
            print(f"  Poco步骤执行超时")
            return False
        except Exception as e:
            print(f"  Poco步骤执行失败: {str(e)}")
            return False
    
    def _take_error_screenshot(self, step_id: str, attempt: Any) -> str:
        """
        错误时截图
        
        Args:
            step_id: 步骤ID
            attempt: 尝试次数
            
        Returns:
            str: 截图文件路径
        """
        try:
            timestamp = int(time.time())
            screenshot_name = f"error_{step_id}_{attempt}_{timestamp}.png"
            screenshot_path = f"screenshots/{screenshot_name}"
            
            # 确保目录存在
            Path("screenshots").mkdir(exist_ok=True)
            
            # 截图
            snapshot(screenshot_path)
            
            print(f"  错误截图已保存: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            print(f"  截图失败: {e}")
            return ""
    
    def _print_execution_summary(self, result: FusionExecutionResult):
        """
        打印执行摘要
        
        Args:
            result: 执行结果
        """
        print("\n" + "="*60)
        print(f"融合脚本执行完成: {result.script_name}")
        print("="*60)
        print(f"总步骤数: {result.total_steps}")
        print(f"成功步骤: {result.successful_steps}")
        print(f"失败步骤: {result.failed_steps}")
        print(f"跳过步骤: {result.skipped_steps}")
        print(f"执行时间: {result.total_execution_time:.2f}秒")
        print(f"整体结果: {'成功' if result.overall_success else '失败'}")
        
        print(f"\n执行统计:")
        print(f"  Airtest成功: {self.stats['airtest_success']}")
        print(f"  Poco成功: {self.stats['poco_success']}")
        print(f"  故障切换: {self.stats['failover_count']}")
        print(f"  总重试: {self.stats['total_retries']}")
        
        if result.error_summary:
            print(f"\n错误摘要:")
            for error in result.error_summary:
                print(f"  - {error}")
        
        print("="*60)


def execute_fusion_script_file(script_path: str, 
                              config: ExecutionConfig = None,
                              device_uri: str = None) -> FusionExecutionResult:
    """
    执行融合脚本文件
    
    Args:
        script_path: 脚本文件路径
        config: 执行配置
        device_uri: 设备连接URI
        
    Returns:
        FusionExecutionResult: 执行结果
    """
    from .persistence import FusionPersistence
    
    # 加载融合脚本
    persistence = FusionPersistence()
    fusion_script = persistence.load_fusion_script(script_path)
    
    if not fusion_script:
        raise ValueError(f"无法加载融合脚本: {script_path}")
    
    # 验证脚本
    validation_result = persistence.validate_fusion_script(script_path)
    if not validation_result['valid']:
        print("警告: 融合脚本验证失败")
        for error in validation_result['errors']:
            print(f"  错误: {error}")
        for warning in validation_result['warnings']:
            print(f"  警告: {warning}")
    
    # 创建执行器
    executor = FailoverExecutor(config)
    
    # 设置环境
    executor.setup_environment(device_uri)
    
    # 执行脚本
    return executor.execute_fusion_script(fusion_script)


if __name__ == "__main__":
    # 测试执行引擎
    config = ExecutionConfig(
        strategy=ExecutionStrategy.ADAPTIVE,
        timeout=30,
        retry_count=2,
        failover_enabled=True,
        screenshot_on_error=True,
        continue_on_error=True
    )
    
    print("故障切换执行引擎测试完成")