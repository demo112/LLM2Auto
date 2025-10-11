#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Airtest 自动化测试框架 - 主程序
提供完整的命令行界面，支持测试发现、执行、过滤和报告生成
"""

import sys
import argparse
import json
import logging
import traceback
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# 添加框架路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "airtest_framework"))

from airtest_framework import AirtestFramework
from airtest_framework.core.discovery import TestMetadata


class TestRunner:
    """测试运行器主类"""
    
    def __init__(self):
        """初始化测试运行器"""
        self.framework = AirtestFramework()
        self.start_time = None
        self.end_time = None
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """设置日志配置"""
        logger = logging.getLogger('TestRunner')
        logger.setLevel(logging.INFO)
        
        # 创建日志目录
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # 文件处理器
        file_handler = logging.FileHandler(
            log_dir / f'test_runner_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _handle_error(self, error: Exception, context: str = "") -> None:
        """统一错误处理"""
        error_msg = f"错误发生在 {context}: {str(error)}"
        self.logger.error(error_msg)
        self.logger.debug(traceback.format_exc())
        print(f"❌ {error_msg}")
    
    def _safe_execute(self, func, *args, **kwargs):
        """安全执行函数，带错误处理"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self._handle_error(e, func.__name__)
            return None
    
    def _validate_device(self, device_uri: str) -> bool:
        """验证设备连接"""
        try:
            if device_uri.startswith("Android"):
                # 检查ADB是否可用
                import subprocess
                result = subprocess.run(['adb', 'devices'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    devices = [line for line in result.stdout.split('\n') 
                              if line.strip() and not line.startswith('List of devices')]
                    if devices:
                        print(f"✅ 检测到 {len(devices)} 个Android设备")
                        self.logger.info(f"检测到Android设备: {devices}")
                        return True
                    else:
                        print("⚠️  未检测到Android设备")
                        self.logger.warning("未检测到Android设备")
                        return False
                else:
                    print("⚠️  ADB不可用")
                    self.logger.warning("ADB命令执行失败")
                    return False
            else:
                # 其他设备类型暂时返回True
                return True
        except Exception as e:
            self.logger.warning(f"设备验证失败: {str(e)}")
            print(f"⚠️  设备验证异常: {str(e)}")
            return False
        
    def print_banner(self):
        """打印程序横幅"""
        print("=" * 80)
        print("🚀 Airtest 自动化测试框架")
        print("   Universal Automated Testing Framework")
        print("=" * 80)
        
    def print_separator(self, title: str, char: str = "-"):
        """打印分隔符"""
        print(f"\n{char * 60}")
        print(f"📋 {title}")
        print(f"{char * 60}")
        
    def discover_tests(self, test_dir: str) -> List[TestMetadata]:
        """发现测试项目"""
        print(f"🔍 正在扫描测试目录: {test_dir}")
        self.logger.info(f"开始扫描测试目录: {test_dir}")
        
        try:
            tests = self.framework.discover_tests(test_dir)
            
            if not tests:
                self.logger.warning("未发现任何测试项目")
                print("❌ 未发现任何测试项目")
                return []
                
            self.logger.info(f"发现 {len(tests)} 个测试项目")
            print(f"✅ 发现 {len(tests)} 个测试项目")
            return tests
        except Exception as e:
            self._handle_error(e, "测试发现")
            return []
        
    def filter_tests(self, tests: List[TestMetadata], args) -> List[TestMetadata]:
        """根据命令行参数过滤测试"""
        filtered_tests = tests
        self.logger.info(f"开始过滤测试，初始数量: {len(tests)}")
        
        try:
            # 按分类过滤
            if args.category:
                filtered_tests = self.framework.discovery.filter_tests(
                    filtered_tests, category=args.category
                )
                self.logger.info(f"按分类 '{args.category}' 过滤后: {len(filtered_tests)} 个")
                print(f"🏷️  按分类 '{args.category}' 过滤: {len(filtered_tests)} 个")
                
            # 按优先级过滤
            if args.priority:
                filtered_tests = self.framework.discovery.filter_tests(
                    filtered_tests, priority=args.priority
                )
                self.logger.info(f"按优先级 '{args.priority}' 过滤后: {len(filtered_tests)} 个")
                print(f"⭐ 按优先级 '{args.priority}' 过滤: {len(filtered_tests)} 个")
                
            # 按平台过滤
            if args.platform:
                filtered_tests = self.framework.discovery.filter_tests(
                    filtered_tests, platforms=[args.platform]
                )
                self.logger.info(f"按平台 '{args.platform}' 过滤后: {len(filtered_tests)} 个")
                print(f"💻 按平台 '{args.platform}' 过滤: {len(filtered_tests)} 个")
                
            # 按标签过滤
            if args.tags:
                tag_list = [tag.strip() for tag in args.tags.split(',')]
                filtered_tests = self.framework.discovery.filter_tests(
                    filtered_tests, tags=tag_list
                )
                self.logger.info(f"按标签 '{args.tags}' 过滤后: {len(filtered_tests)} 个")
                print(f"🏷️  按标签 '{args.tags}' 过滤: {len(filtered_tests)} 个")
                
            # 按名称模式过滤
            if args.pattern:
                filtered_tests = [
                    test for test in filtered_tests 
                    if args.pattern.lower() in test.name.lower()
                ]
                self.logger.info(f"按名称模式 '{args.pattern}' 过滤后: {len(filtered_tests)} 个")
                print(f"🔍 按名称模式 '{args.pattern}' 过滤: {len(filtered_tests)} 个")
                
            return filtered_tests
        except Exception as e:
            self._handle_error(e, "测试过滤")
            return tests
        
    def list_tests(self, tests: List[TestMetadata], verbose: bool = False):
        """列出测试项目"""
        if not tests:
            print("📭 没有找到匹配的测试项目")
            return
            
        self.print_separator("测试项目列表")
        
        for i, test in enumerate(tests, 1):
            print(f"\n📋 {i}. {test.name}")
            print(f"   📁 路径: {test.path}")
            print(f"   📱 分类: {test.category}")
            print(f"   ⭐ 优先级: {test.priority}")
            
            if verbose:
                print(f"   🏷️  标签: {', '.join(test.tags) if test.tags else '无'}")
                print(f"   💻 平台: {', '.join(test.platforms) if test.platforms else '无'}")
                print(f"   🧪 类型: {test.test_type}")
                print(f"   👤 作者: {test.author}")
                print(f"   📝 版本: {test.version}")
                print(f"   ⏱️  超时: {test.timeout}秒")
                print(f"   🔄 重试: {test.retry_count}次")
                if test.description:
                    print(f"   📄 描述: {test.description}")
                    
    def validate_tests(self, tests: List[TestMetadata]):
        """验证测试项目"""
        self.print_separator("项目验证")
        self.logger.info(f"开始验证 {len(tests)} 个测试项目")
        
        valid_count = 0
        invalid_count = 0
        
        try:
            for test in tests:
                try:
                    is_valid, issues = self.framework.validate_project(test.path)
                    status = "✅ 有效" if is_valid else "❌ 无效"
                    print(f"📂 {test.name}: {status}")
                    self.logger.info(f"验证项目 {test.name}: {'有效' if is_valid else '无效'}")
                    
                    if is_valid:
                        valid_count += 1
                    else:
                        invalid_count += 1
                        
                    if issues:
                        for issue in issues:
                            icon = "⚠️ " if "建议" in issue else "❌"
                            print(f"   {icon} {issue}")
                            self.logger.warning(f"项目 {test.name} 问题: {issue}")
                except Exception as e:
                    self._handle_error(e, f"验证项目 {test.name}")
                    invalid_count += 1
                    
            self.logger.info(f"验证完成: {valid_count} 个有效, {invalid_count} 个无效")
            print(f"\n📊 验证结果: ✅ {valid_count} 个有效, ❌ {invalid_count} 个无效")
        except Exception as e:
            self._handle_error(e, "测试验证")
        
    def show_statistics(self, tests: List[TestMetadata]):
        """显示测试统计"""
        self.print_separator("统计信息")
        
        stats = self.framework.discovery.get_test_statistics(tests)
        
        print(f"📊 总览:")
        print(f"   📄 总测试数: {stats['total_tests']}")
        
        print(f"\n📱 分类分布:")
        for category, count in stats['by_category'].items():
            print(f"   {category}: {count}")
            
        print(f"\n⭐ 优先级分布:")
        for priority, count in stats['by_priority'].items():
            print(f"   {priority}: {count}")
            
        print(f"\n💻 平台分布:")
        for platform, count in stats['by_platform'].items():
            print(f"   {platform}: {count}")
            
        print(f"\n🧪 类型分布:")
        for test_type, count in stats['by_type'].items():
            print(f"   {test_type}: {count}")
            
    def execute_tests(self, tests: List[TestMetadata], dry_run: bool = False, 
                     device_uri: str = "Android:///", parallel: bool = False):
        """执行测试"""
        if not tests:
            print("❌ 没有可执行的测试项目")
            self.logger.warning("没有可执行的测试项目")
            return False, []
            
        self.print_separator("测试执行")
        self.start_time = datetime.now()
        self.logger.info(f"开始执行测试，数量: {len(tests)}, 设备: {device_uri}, 并行: {parallel}")
        
        if dry_run:
            print("🔍 模拟执行模式 (Dry Run)")
            self.logger.info("模拟执行模式")
            for i, test in enumerate(tests, 1):
                print(f"📋 [{i}/{len(tests)}] 模拟执行: {test.name}")
                print(f"   📁 路径: {test.path}")
                print(f"   ⏱️  预计耗时: {test.timeout}秒")
                print(f"   📱 设备: {device_uri}")
                self.logger.info(f"模拟执行: {test.name}")
            print("✅ 模拟执行完成")
            return True, []
            
        print(f"🚀 开始执行 {len(tests)} 个测试项目...")
        print(f"📱 目标设备: {device_uri}")
        print(f"🔄 执行模式: {'并行' if parallel else '串行'}")
        
        # 验证设备连接
        if not self._validate_device(device_uri):
            print("⚠️  设备验证失败，将以模拟模式执行")
            self.logger.warning("设备验证失败，继续以模拟模式执行")
        
        # tests 已经是 TestMetadata 对象列表
        test_metadata_list = tests
        
        if not test_metadata_list:
            print("❌ 没有有效的测试可执行")
            self.logger.error("没有有效的测试可执行")
            return False, []
        
        # 执行测试
        try:
            self.logger.info(f"开始执行测试套件，并行模式: {parallel}")
            if parallel:
                results = self.framework.executor.execute_test_suite(
                    test_metadata_list, 
                    device_uri=device_uri, 
                    parallel=True,
                    max_workers=min(len(tests), 3)  # 最多3个并行
                )
            else:
                results = self.framework.executor.execute_test_suite(
                    test_metadata_list, 
                    device_uri=device_uri, 
                    parallel=False
                )
                
            self.end_time = datetime.now()
            total_duration = (self.end_time - self.start_time).total_seconds()
            
            # 统计结果
            success_count = sum(1 for r in results if r.success)
            failed_count = len(results) - success_count
            
            self.logger.info(f"测试执行完成: 成功 {success_count}, 失败 {failed_count}, 总耗时 {total_duration:.2f}秒")
            
            # 显示详细结果
            print(f"\n📊 执行结果详情:")
            for i, result in enumerate(results, 1):
                status_icon = "✅" if result.success else "❌"
                print(f"   {status_icon} [{i}] {result.test_name}")
                print(f"       ⏱️  耗时: {result.duration:.2f}秒")
                if result.retry_count > 0:
                    print(f"       🔄 重试: {result.retry_count}次")
                if not result.success:
                    print(f"       ❌ 错误: {result.error_message}")
                    self.logger.error(f"测试失败 {result.test_name}: {result.error_message}")
                if result.screenshots:
                    print(f"       📸 截图: {len(result.screenshots)}张")
                    
            print(f"\n📊 总体统计:")
            print(f"   ✅ 成功: {success_count}")
            print(f"   ❌ 失败: {failed_count}")
            print(f"   📊 成功率: {success_count/len(results)*100:.1f}%")
            print(f"   ⏱️  总耗时: {total_duration:.2f}秒")
            print(f"   ⏱️  平均耗时: {sum(r.duration for r in results)/len(results):.2f}秒")
            
            return failed_count == 0, results
            
        except Exception as e:
            self.end_time = datetime.now()
            self._handle_error(e, "测试执行")
            return False, []
        
    def generate_report(self, tests: List[TestMetadata], test_results: List = None, 
                       output_file: Optional[str] = None):
        """生成测试报告"""
        self.print_separator("生成报告")
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"reports/test_report_{timestamp}.json"
            
        # 确保报告目录存在
        report_path = Path(output_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 计算统计信息
        success_count = 0
        failed_count = 0
        total_duration = 0
        
        if test_results:
            success_count = sum(1 for r in test_results if r.success)
            failed_count = len(test_results) - success_count
            total_duration = sum(r.duration for r in test_results)
        
        # 生成报告数据
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "framework_version": "1.0.0",
            "summary": {
                "total_tests": len(tests),
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": f"{success_count/len(tests)*100:.1f}%" if tests else "0%",
                "total_duration": total_duration,
                "average_duration": total_duration/len(tests) if tests else 0
            },
            "execution_time": {
                "start": self.start_time.isoformat() if self.start_time else None,
                "end": self.end_time.isoformat() if self.end_time else None,
                "duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None
            },
            "statistics": self.framework.discovery.get_test_statistics(tests),
            "test_details": []
        }
        
        # 添加测试详情
        for i, test in enumerate(tests):
            test_detail = {
                "index": i + 1,
                "name": test.name,
                "path": str(test.path),
                "category": test.category,
                "priority": test.priority,
                "tags": test.tags,
                "platforms": test.platforms,
                "test_type": test.test_type,
                "author": test.author,
                "version": test.version,
                "description": test.description,
                "timeout": test.timeout,
                "retry_count": test.retry_count
            }
            
            # 添加执行结果（如果有）
            if test_results:
                result = next((r for r in test_results if r.test_name == test.name), None)
                if result:
                    test_detail.update({
                        "execution_result": {
                            "success": result.success,
                            "status": result.status,
                            "start_time": result.start_time.isoformat(),
                            "end_time": result.end_time.isoformat(),
                            "duration": result.duration,
                            "error_message": result.error_message,
                            "retry_count": result.retry_count,
                            "screenshots": result.screenshots,
                            "logs": result.logs,
                            "device_info": result.device_info
                        }
                    })
            
            report_data["test_details"].append(test_detail)
        
        # 写入JSON报告
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
            
        # 生成HTML报告
        html_path = report_path.with_suffix('.html')
        self._generate_html_report(report_data, html_path)
        
        print(f"📄 JSON报告已生成: {report_path}")
        print(f"🌐 HTML报告已生成: {html_path}")
        print(f"📊 包含 {len(tests)} 个测试项目的详细信息")
        if test_results:
            print(f"✅ 成功: {success_count}, ❌ 失败: {failed_count}")
            
    def _generate_html_report(self, report_data: dict, html_path: Path):
        """生成HTML格式报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Airtest 测试报告</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #e0e0e0; }}
        .header h1 {{ color: #2c3e50; margin: 0; font-size: 2.5em; }}
        .header .subtitle {{ color: #7f8c8d; margin-top: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card.success {{ background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); }}
        .summary-card.failed {{ background: linear-gradient(135deg, #f44336 0%, #da190b 100%); }}
        .summary-card h3 {{ margin: 0 0 10px 0; font-size: 1.2em; }}
        .summary-card .value {{ font-size: 2em; font-weight: bold; }}
        .test-list {{ margin-top: 30px; }}
        .test-item {{ background: #f8f9fa; margin-bottom: 15px; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .test-item.success {{ border-left-color: #28a745; }}
        .test-item.failed {{ border-left-color: #dc3545; }}
        .test-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .test-name {{ font-size: 1.3em; font-weight: bold; color: #2c3e50; }}
        .test-status {{ padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; }}
        .test-status.success {{ background-color: #28a745; }}
        .test-status.failed {{ background-color: #dc3545; }}
        .test-details {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px; }}
        .detail-group {{ background: white; padding: 15px; border-radius: 5px; }}
        .detail-group h4 {{ margin: 0 0 10px 0; color: #495057; font-size: 1em; }}
        .detail-item {{ margin-bottom: 8px; }}
        .detail-label {{ font-weight: bold; color: #6c757d; }}
        .error-message {{ background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin-top: 10px; }}
        .timestamp {{ text-align: center; margin-top: 30px; color: #6c757d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Airtest 测试报告</h1>
            <div class="subtitle">Universal Automated Testing Framework</div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>📊 总测试数</h3>
                <div class="value">{report_data['summary']['total_tests']}</div>
            </div>
            <div class="summary-card success">
                <h3>✅ 成功</h3>
                <div class="value">{report_data['summary']['success_count']}</div>
            </div>
            <div class="summary-card failed">
                <h3>❌ 失败</h3>
                <div class="value">{report_data['summary']['failed_count']}</div>
            </div>
            <div class="summary-card">
                <h3>📈 成功率</h3>
                <div class="value">{report_data['summary']['success_rate']}</div>
            </div>
            <div class="summary-card">
                <h3>⏱️ 总耗时</h3>
                <div class="value">{report_data['summary']['total_duration']:.1f}s</div>
            </div>
        </div>
        
        <div class="test-list">
            <h2>📋 测试详情</h2>
"""
        
        for test in report_data['test_details']:
            status = "success" if test.get('execution_result', {}).get('success', False) else "failed"
            status_text = "PASSED" if status == "success" else "FAILED"
            
            html_content += f"""
            <div class="test-item {status}">
                <div class="test-header">
                    <div class="test-name">{test['name']}</div>
                    <div class="test-status {status}">{status_text}</div>
                </div>
                
                <div class="test-details">
                    <div class="detail-group">
                        <h4>📁 基本信息</h4>
                        <div class="detail-item"><span class="detail-label">路径:</span> {test['path']}</div>
                        <div class="detail-item"><span class="detail-label">分类:</span> {test['category']}</div>
                        <div class="detail-item"><span class="detail-label">优先级:</span> {test['priority']}</div>
                        <div class="detail-item"><span class="detail-label">作者:</span> {test['author']}</div>
                    </div>
                    
                    <div class="detail-group">
                        <h4>🏷️ 标签和平台</h4>
                        <div class="detail-item"><span class="detail-label">标签:</span> {', '.join(test['tags']) if test['tags'] else '无'}</div>
                        <div class="detail-item"><span class="detail-label">平台:</span> {', '.join(test['platforms']) if test['platforms'] else '无'}</div>
                        <div class="detail-item"><span class="detail-label">类型:</span> {test['test_type']}</div>
                    </div>
"""
            
            if 'execution_result' in test:
                result = test['execution_result']
                html_content += f"""
                    <div class="detail-group">
                        <h4>⚡ 执行结果</h4>
                        <div class="detail-item"><span class="detail-label">耗时:</span> {result['duration']:.2f}秒</div>
                        <div class="detail-item"><span class="detail-label">重试次数:</span> {result['retry_count']}</div>
                        <div class="detail-item"><span class="detail-label">截图数量:</span> {len(result['screenshots'])}张</div>
                        <div class="detail-item"><span class="detail-label">日志文件:</span> {len(result['logs'])}个</div>
                    </div>
"""
                if result['error_message']:
                    html_content += f"""
                    <div class="detail-group">
                        <div class="error-message">
                            <strong>❌ 错误信息:</strong><br>
                            {result['error_message']}
                        </div>
                    </div>
"""
            
            html_content += """
                </div>
            </div>
"""
        
        html_content += f"""
        </div>
        
        <div class="timestamp">
            📅 报告生成时间: {report_data['timestamp']}
        </div>
    </div>
</body>
</html>
"""
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
    def run(self, args):
        """运行主程序"""
        try:
            self.print_banner()
            
            # 发现测试
            tests = self.discover_tests(args.test_dir)
            if not tests:
                return 1
                
            # 过滤测试
            if any([args.category, args.priority, args.platform, args.tags, args.pattern]):
                self.print_separator("应用过滤条件")
                tests = self.filter_tests(tests, args)
                
            # 根据命令执行相应操作
            if args.command == 'list':
                self.list_tests(tests, args.verbose)
                
            elif args.command == 'validate':
                self.validate_tests(tests)
                
            elif args.command == 'stats':
                self.show_statistics(tests)
                
            elif args.command == 'run':
                # 验证测试
                if args.validate:
                    self.validate_tests(tests)
                    
                # 执行测试
                success, test_results = self.execute_tests(
                    tests, 
                    dry_run=args.dry_run,
                    device_uri=getattr(args, 'device', 'Android:///'),
                    parallel=getattr(args, 'parallel', False)
                )
                
                # 生成报告
                if args.report:
                    self.generate_report(tests, test_results, args.output)
                    
                return 0 if success else 1
                
            return 0
            
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断执行")
            return 130
            
        except Exception as e:
            print(f"\n❌ 程序执行出错: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            return 1


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Airtest 自动化测试框架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s list                          # 列出所有测试
  %(prog)s list --verbose                # 详细列出所有测试
  %(prog)s run                           # 执行所有测试
  %(prog)s run --dry-run                 # 模拟执行
  %(prog)s run --category mobile         # 执行移动端测试
  %(prog)s run --priority high           # 执行高优先级测试
  %(prog)s run --platform android        # 执行Android测试
  %(prog)s run --tags ui_test,smoke      # 执行带特定标签的测试
  %(prog)s run --pattern login           # 执行名称包含'login'的测试
  %(prog)s run --device Android:///      # 指定设备执行
  %(prog)s run --parallel                # 并行执行测试
  %(prog)s run --report --output report.json  # 执行并生成报告
  %(prog)s validate                      # 验证测试项目
  %(prog)s stats                         # 显示统计信息
        """
    )
    
    # 基本参数
    parser.add_argument(
        'command',
        choices=['list', 'run', 'validate', 'stats'],
        help='要执行的命令'
    )
    
    parser.add_argument(
        '--test-dir', '-d',
        default='tests/',
        help='测试目录路径 (默认: tests/)'
    )
    
    # 过滤参数
    filter_group = parser.add_argument_group('过滤选项')
    filter_group.add_argument(
        '--category', '-c',
        help='按分类过滤 (如: mobile, web, api)'
    )
    
    filter_group.add_argument(
        '--priority', '-p',
        choices=['low', 'medium', 'high'],
        help='按优先级过滤'
    )
    
    filter_group.add_argument(
        '--platform',
        help='按平台过滤 (如: android, ios, web)'
    )
    
    filter_group.add_argument(
        '--tags', '-t',
        help='按标签过滤 (逗号分隔)'
    )
    
    filter_group.add_argument(
        '--pattern',
        help='按名称模式过滤'
    )
    
    # 执行参数
    exec_group = parser.add_argument_group('执行选项')
    exec_group.add_argument(
        '--dry-run',
        action='store_true',
        help='模拟执行，不实际运行测试'
    )
    
    exec_group.add_argument(
        '--validate',
        action='store_true',
        help='执行前验证测试项目'
    )
    
    exec_group.add_argument(
        '--device',
        default='Android:///',
        help='设备URI (默认: Android:///)'
    )
    
    exec_group.add_argument(
        '--parallel',
        action='store_true',
        help='并行执行测试 (最多3个并行)'
    )
    
    # 报告参数
    report_group = parser.add_argument_group('报告选项')
    report_group.add_argument(
        '--report', '-r',
        action='store_true',
        help='生成测试报告'
    )
    
    report_group.add_argument(
        '--output', '-o',
        help='报告输出文件路径'
    )
    
    # 其他参数
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细信息'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    return parser


def main():
    """主函数"""
    # 设置全局日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('main')
    
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        logger.info("程序启动")
        runner = TestRunner()
        exit_code = runner.run(args)
        logger.info(f"程序执行完成，退出码: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.warning("用户中断执行")
        print("\n⚠️  用户中断执行")
        sys.exit(130)
    except FileNotFoundError as e:
        logger.error(f"文件未找到: {str(e)}")
        print(f"❌ 文件未找到: {str(e)}")
        sys.exit(2)
    except PermissionError as e:
        logger.error(f"权限错误: {str(e)}")
        print(f"❌ 权限错误: {str(e)}")
        sys.exit(3)
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        logger.debug(traceback.format_exc())
        print(f"❌ 程序执行出错: {str(e)}")
        print("💡 请查看日志文件获取详细错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()