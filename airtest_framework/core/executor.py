# -*- encoding=utf8 -*-
"""
执行引擎 - 负责执行 .air 测试项目
"""

import os
import sys
import time
import logging
import subprocess
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

from airtest.core.api import *
from airtest.core.android.adb import ADB

from .discovery import TestMetadata


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    test_path: str
    success: bool
    start_time: datetime
    end_time: datetime
    duration: float
    error_message: str = ""
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    retry_count: int = 0
    device_info: Dict = field(default_factory=dict)
    
    @property
    def status(self) -> str:
        """获取测试状态"""
        return "PASSED" if self.success else "FAILED"


class AirtestExecutor:
    """Airtest 测试执行引擎"""
    
    def __init__(self, config_manager=None):
        """
        初始化执行引擎
        
        Args:
            config_manager: 配置管理器
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.device_pool = []
        self.current_device = None
        
    def setup_device(self, device_uri: str = "Android:///") -> bool:
        """
        设置测试设备
        
        Args:
            device_uri (str): 设备URI
            
        Returns:
            bool: 设置是否成功
        """
        try:
            self.logger.info(f"正在连接设备: {device_uri}")
            
            # 检查ADB设备
            if device_uri.startswith("Android"):
                adb = ADB()
                devices = adb.devices()
                if not devices:
                    raise Exception("未检测到连接的Android设备")
                self.logger.info(f"检测到设备: {devices}")
            
            # 连接设备
            self.current_device = connect_device(device_uri)
            self.logger.info(f"设备连接成功: {self.current_device}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"设备连接失败: {str(e)}")
            return False
    
    def execute_single_test(self, test_metadata: Union[TestMetadata, str], 
                          device_uri: str = "Android:///",
                          log_dir: str = "logs/execution") -> TestResult:
        """
        执行单个测试
        
        Args:
            test_metadata: 测试元数据或路径
            device_uri: 设备URI
            log_dir: 日志目录
            
        Returns:
            TestResult: 测试结果
        """
        # 处理输入参数
        if isinstance(test_metadata, str):
            test_path = test_metadata
            test_name = Path(test_metadata).stem
        else:
            test_path = test_metadata.path
            test_name = test_metadata.name
        
        start_time = datetime.now()
        
        self.logger.info(f"开始执行测试: {test_name}")
        
        try:
            # 设置设备连接
            if not self.setup_device(device_uri):
                raise Exception("设备连接失败")
            
            # 设置日志目录
            os.makedirs(log_dir, exist_ok=True)
            test_log_dir = os.path.join(log_dir, f"{test_name}_{int(time.time())}")
            os.makedirs(test_log_dir, exist_ok=True)
            
            # 设置Airtest环境
            air_dir = Path(test_path)
            if air_dir.is_dir():
                # .air 目录
                py_files = list(air_dir.glob("*.py"))
                if not py_files:
                    raise Exception(f"在 {test_path} 中未找到Python脚本")
                script_path = str(py_files[0])
            else:
                # 直接的Python文件
                script_path = test_path
            
            # 设置工作目录
            original_cwd = os.getcwd()
            os.chdir(str(air_dir.parent if air_dir.is_dir() else Path(test_path).parent))
            
            try:
                # 使用auto_setup设置环境
                auto_setup(script_path, logdir=test_log_dir)
                
                # 执行测试脚本
                self._execute_test_script(script_path)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # 收集截图和日志
                screenshots = self._collect_screenshots(test_log_dir)
                logs = self._collect_logs(test_log_dir)
                
                result = TestResult(
                    test_name=test_name,
                    test_path=test_path,
                    success=True,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    screenshots=screenshots,
                    logs=logs,
                    device_info=self._get_device_info()
                )
                
                self.logger.info(f"测试执行成功: {test_name} (耗时: {duration:.2f}s)")
                return result
                
            finally:
                # 恢复工作目录
                os.chdir(original_cwd)
                
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_msg = str(e)
            self.logger.error(f"测试执行失败: {test_name} - {error_msg}")
            
            result = TestResult(
                test_name=test_name,
                test_path=test_path,
                success=False,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message=error_msg,
                device_info=self._get_device_info()
            )
            
            return result
    
    def execute_test_suite(self, tests: List[TestMetadata], 
                          device_uri: str = "Android:///",
                          parallel: bool = False,
                          max_workers: int = 1) -> List[TestResult]:
        """
        执行测试套件
        
        Args:
            tests: 测试列表
            device_uri: 设备URI
            parallel: 是否并行执行
            max_workers: 最大并行数
            
        Returns:
            List[TestResult]: 测试结果列表
        """
        self.logger.info(f"开始执行测试套件，共 {len(tests)} 个测试")
        
        results = []
        
        if parallel and max_workers > 1:
            # 并行执行
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_test = {
                    executor.submit(self.execute_single_test, test, device_uri): test 
                    for test in tests
                }
                
                for future in concurrent.futures.as_completed(future_to_test):
                    test = future_to_test[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.logger.error(f"测试执行异常: {test.name} - {e}")
                        # 创建失败结果
                        result = TestResult(
                            test_name=test.name,
                            test_path=test.path,
                            success=False,
                            start_time=datetime.now(),
                            end_time=datetime.now(),
                            duration=0,
                            error_message=str(e)
                        )
                        results.append(result)
        else:
            # 串行执行
            for test in tests:
                result = self.execute_single_test(test, device_uri)
                results.append(result)
                
                # 如果测试失败且配置了重试
                if not result.success and hasattr(test, 'retry_count') and test.retry_count > 0:
                    self.logger.info(f"测试失败，开始重试: {test.name}")
                    for retry in range(test.retry_count):
                        self.logger.info(f"第 {retry + 1} 次重试: {test.name}")
                        retry_result = self.execute_single_test(test, device_uri)
                        retry_result.retry_count = retry + 1
                        
                        if retry_result.success:
                            self.logger.info(f"重试成功: {test.name}")
                            results[-1] = retry_result  # 替换原结果
                            break
                        else:
                            self.logger.warning(f"第 {retry + 1} 次重试失败: {test.name}")
        
        # 按原始顺序排序结果
        test_name_to_order = {test.name: i for i, test in enumerate(tests)}
        results.sort(key=lambda r: test_name_to_order.get(r.test_name, 999))
        
        self.logger.info(f"测试套件执行完成，成功: {sum(1 for r in results if r.success)}/{len(results)}")
        return results
    
    def run_tests(self, test_dir: str = "tests/", **filters) -> List[TestResult]:
        """
        运行测试（发现+执行）
        
        Args:
            test_dir: 测试目录
            **filters: 过滤条件
            
        Returns:
            List[TestResult]: 测试结果列表
        """
        from .discovery import AirtestDiscovery
        
        # 发现测试
        discovery = AirtestDiscovery(self.config)
        all_tests = discovery.discover_tests(test_dir)
        
        # 过滤测试
        if filters:
            tests = discovery.filter_tests(all_tests, **filters)
        else:
            tests = all_tests
        
        if not tests:
            self.logger.warning("未发现任何测试用例")
            return []
        
        # 执行测试
        return self.execute_test_suite(tests)
    
    def _execute_test_script(self, script_path: str):
        """
        执行测试脚本
        
        Args:
            script_path: 脚本路径
        """
        # 读取并执行Python脚本
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # 创建执行环境
        exec_globals = {
            '__file__': script_path,
            '__name__': '__main__'
        }
        
        # 导入Airtest API
        exec_globals.update(globals())
        
        # 执行脚本
        exec(script_content, exec_globals)
    
    def _collect_screenshots(self, log_dir: str) -> List[str]:
        """收集截图文件"""
        screenshots = []
        log_path = Path(log_dir)
        
        if log_path.exists():
            for img_file in log_path.glob("*.jpg"):
                screenshots.append(str(img_file))
            for img_file in log_path.glob("*.png"):
                screenshots.append(str(img_file))
        
        return screenshots
    
    def _collect_logs(self, log_dir: str) -> List[str]:
        """收集日志文件"""
        logs = []
        log_path = Path(log_dir)
        
        if log_path.exists():
            for log_file in log_path.glob("*.txt"):
                logs.append(str(log_file))
            for log_file in log_path.glob("*.log"):
                logs.append(str(log_file))
        
        return logs
    
    def _get_device_info(self) -> Dict:
        """获取设备信息"""
        device_info = {}
        
        try:
            if self.current_device:
                device_info['device'] = str(self.current_device)
                
                # 获取Android设备信息
                if hasattr(self.current_device, 'adb'):
                    adb = self.current_device.adb
                    device_info['serial'] = getattr(adb, 'serialno', 'unknown')
                    
                    # 获取设备属性
                    try:
                        device_info['model'] = adb.getprop('ro.product.model')
                        device_info['version'] = adb.getprop('ro.build.version.release')
                        device_info['sdk'] = adb.getprop('ro.build.version.sdk')
                    except:
                        pass
        except Exception as e:
            self.logger.warning(f"获取设备信息失败: {e}")
        
        return device_info
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.current_device:
                self.logger.info("清理设备连接")
                # Airtest会自动清理连接
            self.logger.info("执行引擎资源清理完成")
        except Exception as e:
            self.logger.error(f"资源清理失败: {e}")


class BatchExecutor:
    """批量执行器"""
    
    def __init__(self, executor: AirtestExecutor):
        self.executor = executor
        self.logger = logging.getLogger(__name__)
    
    def execute_by_command_line(self, air_path: str, device_uri: str = "Android:///", 
                              log_dir: str = "logs/execution") -> TestResult:
        """
        使用命令行方式执行测试
        
        Args:
            air_path: .air 项目路径
            device_uri: 设备URI
            log_dir: 日志目录
            
        Returns:
            TestResult: 测试结果
        """
        test_name = Path(air_path).stem
        start_time = datetime.now()
        
        try:
            # 构建命令
            cmd = [
                'airtest', 'run', air_path,
                '--device', device_uri,
                '--log', log_dir
            ]
            
            self.logger.info(f"执行命令: {' '.join(cmd)}")
            
            # 执行命令
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            success = result.returncode == 0
            error_message = result.stderr if not success else ""
            
            return TestResult(
                test_name=test_name,
                test_path=air_path,
                success=success,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message=error_message
            )
            
        except subprocess.TimeoutExpired:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_name=test_name,
                test_path=air_path,
                success=False,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message="测试执行超时"
            )
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_name=test_name,
                test_path=air_path,
                success=False,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message=str(e)
            )