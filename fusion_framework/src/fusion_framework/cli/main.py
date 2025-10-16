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

# 添加项目根目录到Python路径，支持直接运行
if __name__ == '__main__':
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

# 使用新的模块结构导入
from ..core.config import FusionConfig, load_config, validate_config
from ..core.discovery import TestCaseDiscovery, TestCaseInfo
from ..core.parser import EnhancedScriptParser
from ..core.alignment import align_script_pair
from ..utils.persistence import FusionPersistence, create_fusion_script_from_alignment
from ..core.executor import FailoverExecutor, ExecutionConfig, ExecutionStrategy
from ..core.reporter import FusionReporter
# 报告器期望的结果类型（来自 executor）
from ..core.executor import StepExecutionResult as ExecStepExecutionResult
from ..core.executor import FusionExecutionResult as ExecFusionExecutionResult


class FusionTestFramework:
    """融合测试框架主类"""
    
    def __init__(self, config: Optional[FusionConfig] = None):
        """
        初始化融合测试框架
        
        Args:
            config: 配置对象，如果为None则加载默认配置
        """
        # 加载配置
        if config is None:
            config = load_config()
        
        # 验证配置
        if not validate_config(config):
            raise ValueError("配置验证失败")
        
        self.config = config
        self.logger = self._setup_logging()
        
        # 初始化核心组件
        self.discovery = TestCaseDiscovery(config.test_root_dir)
        self.parser = EnhancedScriptParser()
        self.persistence = FusionPersistence("fusion_scripts")
        self.executor = FailoverExecutor()
        self.reporter = FusionReporter()
        
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
        if self.discovery is None or str(self.discovery.tests_root) != root_dir:
            self.discovery = TestCaseDiscovery(root_dir)
        
        test_cases_dict = self.discovery.discover_test_cases()
        test_cases = list(test_cases_dict.values())
        
        self.logger.info(f"发现 {len(test_cases)} 个测试用例")
        
        if self.config.verbose_logging:
            self.discovery.print_discovery_summary()
        
        return test_cases
    
    async def process_fusion(self, test_case: TestCaseInfo, qwen_api_key: Optional[str] = None) -> str:
        """
        处理融合脚本
        
        Args:
            test_case: 测试用例信息
            qwen_api_key: Qwen API密钥
            
        Returns:
            str: 融合脚本文件名
        """
        import os
        import asyncio
        
        if not (test_case.airtest_path and test_case.poco_path):
            raise ValueError("测试用例缺少Airtest或Poco实现")
        
        self.logger.info(f"开始处理融合脚本: {test_case.name}")
        
        try:
            # 解析脚本获取步骤
            airtest_metadata, airtest_steps = self.parser.parse_script_file(test_case.airtest_path)
            poco_metadata, poco_steps = self.parser.parse_script_file(test_case.poco_path)
            
            # 执行智能对齐
            alignment_result = await align_script_pair(
                airtest_steps=airtest_steps,
                poco_steps=poco_steps,
                qwen_api_key=qwen_api_key or os.getenv("QWEN_API_KEY")
            )
            
            # 创建融合脚本
            script_filename = create_fusion_script_from_alignment(
                script_name=test_case.name,
                alignment_results=alignment_result,
                airtest_source=test_case.airtest_path,
                poco_source=test_case.poco_path
            )
            
            self.logger.info(f"融合脚本已保存: {script_filename}")
            return script_filename
            
        except Exception as e:
            self.logger.error(f"融合处理失败: {e}")
            raise
    
    def run_fusion_script(self, script_filename: str, config: Optional[ExecutionConfig] = None) -> Any:
        """
        执行融合脚本
        
        Args:
            script_filename: 融合脚本文件名
            config: 执行配置
            
        Returns:
            执行结果
        """
        if config is None:
            config = ExecutionConfig(
                strategy=ExecutionStrategy.ADAPTIVE,
                timeout=30,
                retry_count=2,
                failover_enabled=True
            )
        
        self.logger.info(f"开始执行融合脚本: {script_filename}")
        
        try:
            # 构建完整的文件路径
            script_path = Path(script_filename)
            
            # 如果是相对路径且不包含fusion_scripts，则添加fusion_scripts目录
            if not script_path.is_absolute() and not str(script_path).startswith('fusion_scripts'):
                script_path = Path("fusion_scripts") / script_filename
            
            # 加载融合脚本
            fusion_script = self.persistence.load_fusion_script(str(script_path))
            
            if fusion_script is None:
                raise FileNotFoundError(f"无法加载融合脚本: {script_path}")
            
            # 更新执行器配置
            self.executor.config = config
            
            # 设置执行环境（初始化设备连接）
            self.executor.setup_environment()
            
            # 执行脚本（execute_fusion_script 只接受一个参数）
            result = self.executor.execute_fusion_script(fusion_script)
            
            self.logger.info(f"融合脚本执行完成: {script_filename}")
            return result
            
        except Exception as e:
            self.logger.error(f"融合脚本执行失败: {e}")
            raise
    
    def _convert_failover_result(self, failover_result: Any, case_name: str) -> ExecFusionExecutionResult:
        """
        将 FailoverExecutor 的结果转换为报告器所需的 ExecFusionExecutionResult
        """
        # 计算回退步数
        fallback_steps = 0
        exec_step_results: List[ExecStepExecutionResult] = []
        for sr in failover_result.step_results:
            # 映射步骤结果到统一的 ExecutionResult
            if getattr(sr, 'result', None) is not None:
                raw_res = sr.result.name if hasattr(sr.result, 'name') else str(sr.result)
            else:
                raw_res = 'FAILED'
            if raw_res == 'SUCCESS':
                mapped = ExecExecutionResult.SUCCESS
            elif raw_res == 'SKIPPED':
                mapped = ExecExecutionResult.SKIPPED
            else:
                # 将 ERROR/TIMEOUT/FAILED 统一为 FAILED
                mapped = ExecExecutionResult.FAILED
            # 统计回退
            if getattr(sr, 'fallback_used', False):
                fallback_steps += 1
            # used_strategy 用 failover 的执行方法字段替代
            used_strategy = getattr(sr, 'execution_method', '')
            exec_step_results.append(
                ExecStepExecutionResult(
                    step_index=len(exec_step_results),
                    result=mapped,
                    execution_time=getattr(sr, 'execution_time', 0.0),
                    error_message=getattr(sr, 'error_message', ''),
                    used_strategy=used_strategy,
                    fallback_used=getattr(sr, 'fallback_used', False)
                )
            )

        # 计算整体结果：有回退则视为 FALLBACK；否则按是否全部成功
        if getattr(failover_result, 'overall_success', False):
            overall = ExecExecutionResult.FALLBACK if fallback_steps > 0 else ExecExecutionResult.SUCCESS
        else:
            overall = ExecExecutionResult.FAILED

        return ExecFusionExecutionResult(
            case_name=case_name,
            total_steps=getattr(failover_result, 'total_steps', len(exec_step_results)),
            successful_steps=getattr(failover_result, 'successful_steps', 0),
            failed_steps=getattr(failover_result, 'failed_steps', 0),
            fallback_steps=fallback_steps,
            total_execution_time=getattr(failover_result, 'total_execution_time', 0.0),
            step_results=exec_step_results,
            overall_result=overall
        )

    def run_test_cases(self, test_cases: List[TestCaseInfo], case_filter: Optional[str] = None) -> List[ExecFusionExecutionResult]:
        """
        运行测试用例
        
        Args:
            test_cases: 测试用例列表
            case_filter: 用例过滤器（支持通配符）
            
        Returns:
            Dict[str, Any]: 执行结果统计
        """
        import fnmatch
        import asyncio
        import os
        
        # 过滤测试用例
        if case_filter:
            filtered_cases = [
                case for case in test_cases 
                if fnmatch.fnmatch(case.name, case_filter)
            ]
        else:
            filtered_cases = test_cases
        
        self.logger.info(f"准备执行 {len(filtered_cases)} 个测试用例")
        
        results_list: List[ExecFusionExecutionResult] = []
        
        for test_case in filtered_cases:
            try:
                self.logger.info(f"执行测试用例: {test_case.name}")
                
                # 检查是否已有融合脚本
                fusion_script_name = f"{test_case.name}.fusion.json"
                fusion_script_path = Path("fusion_scripts") / fusion_script_name
                
                if not fusion_script_path.exists():
                    self.logger.info(f"融合脚本不存在，开始创建: {fusion_script_name}")
                    
                    # 创建融合脚本
                    script_filename = asyncio.run(self.process_fusion(
                        test_case, 
                        qwen_api_key=os.getenv("QWEN_API_KEY")
                    ))
                else:
                    script_filename = fusion_script_name
                    self.logger.info(f"使用现有融合脚本: {script_filename}")
                
                # 执行融合脚本（获得 failover 执行结果）
                failover_result = self.run_fusion_script(script_filename)
                # 转换为报告器期望的结果类型
                converted = self._convert_failover_result(failover_result, test_case.name)
                results_list.append(converted)
                
                # 日志按整体结果记录
                if converted.overall_result in [ExecExecutionResult.SUCCESS, ExecExecutionResult.FALLBACK]:
                    self.logger.info(f"测试用例执行成功: {test_case.name}")
                else:
                    self.logger.warning(f"测试用例执行失败: {test_case.name}")
                
            except Exception as e:
                self.logger.error(f"测试用例执行失败: {test_case.name}, 错误: {e}")
        
        return results_list
    
    def generate_report(self, results: Any, report_title: str = "融合测试执行报告") -> Dict[str, str]:
        """
        生成测试报告
        
        Args:
            results: 测试执行结果
            report_title: 报告标题
            
        Returns:
            str: 报告文件路径
        """
        try:
            # 如果传入的是聚合 dict，转换为列表
            if isinstance(results, dict) and 'details' in results:
                converted_list: List[ExecFusionExecutionResult] = []
                for item in results.get('details', []):
                    case_name = item.get('name', 'unknown')
                    if 'result' in item:
                        converted_list.append(self._convert_failover_result(item['result'], case_name))
                results_for_report = converted_list
            elif isinstance(results, list):
                results_for_report = results
            else:
                results_for_report = []
            # 使用 FusionReporter 生成报告（返回包含 html/json 的字典）
            report_paths = self.reporter.generate_report(results_for_report, report_title)
            self.logger.info(f"测试报告已生成: {report_paths}")
            return report_paths
        except Exception as e:
            self.logger.error(f"生成报告失败: {e}")
            # 回退生成简单文本报告
            report_content_lines = [
                report_title,
                '=' * len(report_title),
                '',
            ]
            if isinstance(results, list):
                report_content_lines.append(f"总用例数: {len(results)}")
            elif isinstance(results, dict):
                report_content_lines.append(f"总用例数: {results.get('total', 0)}")
                report_content_lines.append(f"成功: {results.get('passed', 0)} 失败: {results.get('failed', 0)} 跳过: {results.get('skipped', 0)}")
            report_content = "\n".join(report_content_lines)
            report_path = f"fusion_test_report_{int(time.time())}.txt"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            return {'txt': report_path}
    
    def run_full_test_suite(self, case_filter: Optional[str] = None, report_title: str = "融合测试执行报告") -> Dict[str, Any]:
        """
        运行完整的测试套件
        
        Args:
            case_filter: 用例过滤器（支持通配符）
            report_title: 报告标题
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            # 发现测试用例
            test_cases = self.discover_test_cases()
            
            if not test_cases:
                self.logger.warning("未发现任何测试用例")
                return {'success': False, 'message': '未发现任何测试用例'}
            
            # 运行测试用例（返回列表）
            results_list = self.run_test_cases(test_cases, case_filter)
            
            # 生成报告
            try:
                report_paths = self.generate_report(results_list, report_title)
                self.logger.info(f"测试报告已生成: {report_paths}")
            except Exception as report_error:
                self.logger.warning(f"报告生成失败: {report_error}")
                report_paths = None
            
            # 计算总体成功
            overall_success = all(
                r.overall_result.value in ['success', 'fallback'] for r in results_list
            ) if results_list else False
            
            return {
                'success': overall_success,
                'results': results_list,
                'report_paths': report_paths
            }
            
        except Exception as e:
            self.logger.error(f"测试套件执行失败: {e}")
            return {'success': False, 'error': str(e)}
    

    



def main():
    """命令行入口函数"""
    import argparse
    import os
    
    # 如果直接运行main.py，切换到项目根目录
    if __name__ == '__main__':
        project_root = Path(__file__).parent.parent.parent
        os.chdir(project_root)
        print(f"工作目录已切换到: {project_root}")
    
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