# -*- encoding=utf8 -*-
"""
Airtest 自动化测试框架

一个通用的 Airtest 测试项目管理和执行框架，支持：
- 自动发现和加载 .air 测试项目
- 基于命名规则的测试分类和管理
- 统一的测试执行和报告生成
- 灵活的配置管理
"""

import logging
from typing import List, Dict, Any, Optional

from .core import (
    AirtestDiscovery,
    TestMetadata,
    AirtestExecutor, 
    TestResult,
    BatchExecutor,
    ConfigManager,
    FrameworkConfig,
    TestReporter,
    ReportAnalyzer
)

__version__ = "1.0.0"
__author__ = "Airtest Framework Team"

class AirtestFramework:
    """Airtest 自动化测试框架主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化框架
        
        Args:
            config_path: 配置文件路径
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.config_manager = ConfigManager(config_path)
        self.discovery = AirtestDiscovery(self.config_manager)
        self.executor = AirtestExecutor(self.config_manager)
        self.batch_executor = BatchExecutor(self.executor)
        self.reporter = TestReporter(self.config_manager)
        self.analyzer = ReportAnalyzer()
        
        # 设置日志
        self.config_manager.setup_logging()
        
        self.logger.info("Airtest 自动化测试框架初始化完成")
    
    def discover_tests(self, test_dir: str = "tests/", **filters) -> List[TestMetadata]:
        """
        发现测试用例
        
        Args:
            test_dir: 测试目录
            **filters: 过滤条件
            
        Returns:
            List[TestMetadata]: 测试元数据列表
        """
        self.logger.info(f"开始发现测试用例: {test_dir}")
        
        all_tests = self.discovery.discover_tests(test_dir)
        
        if filters:
            tests = self.discovery.filter_tests(all_tests, **filters)
            self.logger.info(f"应用过滤条件后，发现 {len(tests)} 个测试用例")
        else:
            tests = all_tests
            self.logger.info(f"发现 {len(tests)} 个测试用例")
        
        return tests
    
    def run_tests(self, test_dir: str = "tests/", 
                  device_uri: str = "Android:///",
                  parallel: bool = False,
                  **filters) -> List[TestResult]:
        """
        运行测试
        
        Args:
            test_dir: 测试目录
            device_uri: 设备URI
            parallel: 是否并行执行
            **filters: 过滤条件
            
        Returns:
            List[TestResult]: 测试结果列表
        """
        self.logger.info("开始运行测试")
        
        # 发现测试
        tests = self.discover_tests(test_dir, **filters)
        
        if not tests:
            self.logger.warning("未发现任何测试用例")
            return []
        
        # 执行测试
        config = self.config_manager.get_execution_config()
        results = self.executor.execute_test_suite(
            tests, 
            device_uri=device_uri,
            parallel=parallel or config.parallel,
            max_workers=config.max_workers
        )
        
        self.logger.info(f"测试执行完成，成功: {sum(1 for r in results if r.success)}/{len(results)}")
        return results
    
    def run_single_test(self, test_path: str, 
                       device_uri: str = "Android:///") -> TestResult:
        """
        运行单个测试
        
        Args:
            test_path: 测试路径
            device_uri: 设备URI
            
        Returns:
            TestResult: 测试结果
        """
        self.logger.info(f"运行单个测试: {test_path}")
        return self.executor.execute_single_test(test_path, device_uri)
    
    def generate_report(self, results: List[TestResult], 
                       output_dir: str = "reports", 
                       format: str = "html") -> str:
        """
        生成测试报告
        
        Args:
            results: 测试结果列表
            output_dir: 输出目录
            format: 报告格式
            
        Returns:
            str: 报告文件路径
        """
        self.logger.info(f"生成测试报告: {format} 格式")
        
        report_file = self.reporter.generate_report(results, output_dir, format)
        
        # 发送通知（如果配置了）
        config = self.config_manager.get_config()
        webhook_url = getattr(config, 'webhook_url', None)
        if webhook_url:
            self.reporter.send_notification(results, webhook_url)
        
        return report_file
    
    def run_and_report(self, test_dir: str = "tests/", 
                      output_dir: str = "reports",
                      report_format: str = "html",
                      device_uri: str = "Android:///",
                      **filters) -> Dict[str, Any]:
        """
        运行测试并生成报告（一站式服务）
        
        Args:
            test_dir: 测试目录
            output_dir: 报告输出目录
            report_format: 报告格式
            device_uri: 设备URI
            **filters: 过滤条件
            
        Returns:
            Dict[str, Any]: 执行结果摘要
        """
        self.logger.info("开始一站式测试执行和报告生成")
        
        # 运行测试
        results = self.run_tests(test_dir, device_uri, **filters)
        
        # 生成报告
        report_file = self.generate_report(results, output_dir, report_format)
        
        # 生成摘要
        summary = self.reporter.generate_summary_report(results)
        summary["report_file"] = report_file
        
        self.logger.info("一站式测试执行和报告生成完成")
        return summary
    
    def validate_project(self, project_path: str) -> Dict[str, Any]:
        """
        验证 .air 项目
        
        Args:
            project_path: 项目路径
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        return self.discovery.validate_air_project(project_path)
    
    def get_config(self) -> FrameworkConfig:
        """获取框架配置"""
        return self.config_manager.get_config()
    
    def update_config(self, **kwargs) -> bool:
        """更新框架配置"""
        return self.config_manager.update_config(**kwargs)
    
    def create_default_config(self, config_path: str = "airtest_config.yaml") -> bool:
        """创建默认配置文件"""
        return self.config_manager.create_default_config(config_path)
    
    def analyze_reports(self, report_files: List[str]) -> Dict[str, Any]:
        """分析历史报告"""
        return self.analyzer.analyze_trends(report_files)
    
    def find_flaky_tests(self, report_files: List[str]) -> List[Dict[str, Any]]:
        """查找不稳定的测试"""
        return self.analyzer.find_flaky_tests(report_files)
    
    def cleanup(self):
        """清理资源"""
        try:
            self.executor.cleanup()
            self.logger.info("框架资源清理完成")
        except Exception as e:
            self.logger.error(f"框架资源清理失败: {e}")


# 便捷函数
def quick_run(test_dir: str = "tests/", 
              device_uri: str = "Android:///",
              output_dir: str = "reports") -> Dict[str, Any]:
    """
    快速运行测试（便捷函数）
    
    Args:
        test_dir: 测试目录
        device_uri: 设备URI
        output_dir: 报告输出目录
        
    Returns:
        Dict[str, Any]: 执行结果摘要
    """
    framework = AirtestFramework()
    return framework.run_and_report(test_dir, output_dir, device_uri=device_uri)


def discover_tests(test_dir: str = "tests/", **filters) -> List[TestMetadata]:
    """
    发现测试用例（便捷函数）
    
    Args:
        test_dir: 测试目录
        **filters: 过滤条件
        
    Returns:
        List[TestMetadata]: 测试元数据列表
    """
    framework = AirtestFramework()
    return framework.discover_tests(test_dir, **filters)


__all__ = [
    'AirtestFramework',
    'quick_run',
    'discover_tests',
    'AirtestDiscovery',
    'TestMetadata',
    'AirtestExecutor',
    'TestResult',
    'BatchExecutor',
    'ConfigManager',
    'FrameworkConfig', 
    'TestReporter',
    'ReportAnalyzer'
]