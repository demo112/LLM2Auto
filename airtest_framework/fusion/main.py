# -*- encoding=utf8 -*-
"""
融合测试框架主入口

提供完整的融合测试执行流程，集成所有组件
"""

import sys
import time
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from .config import FusionConfig, load_config, validate_config
from .discovery import TestCaseDiscovery, TestCaseInfo
from .alignment import StepAlignment
from .executor import MultiDimensionExecutor, FusionExecutionResult
from .reporter import FusionReporter


class FusionTestFramework:
    """融合测试框架主类"""
    
    def __init__(self, config: Optional[FusionConfig] = None):
        """
        初始化融合测试框架
        
        Args:
            config: 配置对象，如果为None则加载默认配置
        """
        self.config = config or load_config()
        self.logger = self._setup_logging()
        
        # 初始化组件
        self.discovery = None  # 延迟初始化，因为需要测试根目录
        self.alignment = StepAlignment()
        self.executor = MultiDimensionExecutor(strategy=self.config.execution_strategy)
        self.reporter = FusionReporter(self.config.report.output_dir)
        
        self.logger.info("融合测试框架初始化完成")
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger('FusionFramework')
        logger.setLevel(getattr(logging, self.config.logging.level))
        
        # 清除现有处理器
        logger.handlers.clear()
        
        formatter = logging.Formatter(self.config.logging.format)
        
        # 控制台输出
        if self.config.logging.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 文件输出
        if self.config.logging.file_output:
            log_dir = Path(self.config.logging.log_dir)
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(
                log_dir / f"fusion_{time.strftime('%Y%m%d_%H%M%S')}.log",
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def discover_test_cases(self, test_root: Optional[str] = None) -> List[TestCaseInfo]:
        """
        发现测试用例
        
        Args:
            test_root: 测试根目录，如果为None则使用配置中的目录
            
        Returns:
            List[TestCaseInfo]: 发现的测试用例列表
        """
        root_dir = test_root or self.config.test_root_dir
        
        self.logger.info(f"开始发现测试用例，根目录: {root_dir}")
        
        # 初始化discovery（如果还没有初始化或根目录改变了）
        if self.discovery is None:
            self.discovery = TestCaseDiscovery(root_dir)
        
        test_cases_dict = self.discovery.discover_test_cases()
        test_cases = list(test_cases_dict.values())
        
        self.logger.info(f"发现 {len(test_cases)} 个测试用例")
        
        if self.config.verbose_logging:
            self.discovery.print_discovery_summary()
        
        return test_cases
    
    def run_test_cases(self, 
                      test_cases: Optional[List[TestCaseInfo]] = None,
                      case_filter: Optional[str] = None) -> List[FusionExecutionResult]:
        """
        执行测试用例
        
        Args:
            test_cases: 要执行的测试用例列表，如果为None则自动发现
            case_filter: 用例名称过滤器（支持通配符）
            
        Returns:
            List[FusionExecutionResult]: 执行结果列表
        """
        # 如果没有提供测试用例，则自动发现
        if test_cases is None:
            test_cases = self.discover_test_cases()
        
        # 应用过滤器
        if case_filter:
            import fnmatch
            test_cases = [
                case for case in test_cases 
                if fnmatch.fnmatch(case.case_name, case_filter)
            ]
            self.logger.info(f"应用过滤器 '{case_filter}' 后，剩余 {len(test_cases)} 个用例")
        
        if not test_cases:
            self.logger.warning("没有找到要执行的测试用例")
            return []
        
        self.logger.info(f"开始执行 {len(test_cases)} 个测试用例")
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            self.logger.info(f"执行用例 {i}/{len(test_cases)}: {test_case.name}")
            
            try:
                # 步骤对齐
                if test_case.airtest_path:
                    self.alignment.parse_airtest_script(test_case.airtest_path)
                if test_case.poco_path:
                    self.alignment.parse_poco_script(test_case.poco_path)
                
                aligned_steps = self.alignment.align_steps()
                
                if not aligned_steps:
                    self.logger.warning(f"用例 {test_case.name} 没有找到可对齐的步骤")
                    continue
                
                # 执行用例
                result = self.executor.execute_fusion_case(test_case.name, aligned_steps)
                results.append(result)
                
                # 打印执行结果
                status = "✓" if result.overall_result.value in ['success', 'fallback'] else "✗"
                self.logger.info(
                    f"{status} {test_case.name}: "
                    f"{result.successful_steps}/{result.total_steps} 步骤成功 "
                    f"({result.total_execution_time:.2f}s)"
                )
                
            except Exception as e:
                self.logger.error(f"执行用例 {test_case.name} 时发生错误: {e}")
                if self.config.debug_mode:
                    import traceback
                    self.logger.error(traceback.format_exc())
        
        self.logger.info(f"测试执行完成，共执行 {len(results)} 个用例")
        
        return results
    
    def generate_report(self, 
                       results: List[FusionExecutionResult],
                       report_title: str = "融合测试执行报告") -> Dict[str, str]:
        """
        生成测试报告
        
        Args:
            results: 执行结果列表
            report_title: 报告标题
            
        Returns:
            Dict[str, str]: 生成的报告文件路径
        """
        self.logger.info("开始生成测试报告")
        
        report_paths = self.reporter.generate_report(results, report_title)
        
        self.logger.info("测试报告生成完成:")
        for report_type, path in report_paths.items():
            self.logger.info(f"  {report_type.upper()}: {path}")
        
        # 打印摘要到控制台
        if self.config.logging.console_output:
            self.reporter.print_summary(results)
        
        return report_paths
    
    def run_full_test_suite(self, 
                           test_root: Optional[str] = None,
                           case_filter: Optional[str] = None,
                           report_title: str = "融合测试执行报告") -> Dict[str, Any]:
        """
        运行完整的测试套件
        
        Args:
            test_root: 测试根目录
            case_filter: 用例过滤器
            report_title: 报告标题
            
        Returns:
            Dict[str, Any]: 包含执行结果和报告路径的字典
        """
        start_time = time.time()
        
        try:
            # 验证配置
            if not validate_config(self.config):
                raise ValueError("配置验证失败")
            
            # 发现测试用例
            test_cases = self.discover_test_cases(test_root)
            
            if not test_cases:
                self.logger.warning("没有发现任何测试用例")
                return {
                    'results': [],
                    'reports': {},
                    'execution_time': 0.0,
                    'success': False
                }
            
            # 执行测试用例
            results = self.run_test_cases(test_cases, case_filter)
            
            # 生成报告
            report_paths = self.generate_report(results, report_title)
            
            execution_time = time.time() - start_time
            
            self.logger.info(f"完整测试套件执行完成，总耗时: {execution_time:.2f}秒")
            
            return {
                'results': results,
                'reports': report_paths,
                'execution_time': execution_time,
                'success': True
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"测试套件执行失败: {e}")
            
            if self.config.debug_mode:
                import traceback
                self.logger.error(traceback.format_exc())
            
            return {
                'results': [],
                'reports': {},
                'execution_time': execution_time,
                'success': False,
                'error': str(e)
            }


def main():
    """命令行入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='融合测试框架')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--test-root', '-t', help='测试根目录')
    parser.add_argument('--filter', '-f', help='用例过滤器（支持通配符）')
    parser.add_argument('--title', help='报告标题', default='融合测试执行报告')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = load_config(args.config) if args.config else load_config()
        
        # 应用命令行参数
        if args.debug:
            config.debug_mode = True
            config.logging.level = 'DEBUG'
        
        if args.verbose:
            config.verbose_logging = True
        
        if args.test_root:
            config.test_root_dir = args.test_root
        
        # 创建框架实例
        framework = FusionTestFramework(config)
        
        # 运行测试套件
        result = framework.run_full_test_suite(
            case_filter=args.filter,
            report_title=args.title
        )
        
        # 返回适当的退出码
        sys.exit(0 if result['success'] else 1)
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()