# -*- encoding=utf8 -*-
"""
集成示例

展示如何使用新的统一架构替代旧的分散模块
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入新的统一核心模块
from core import (
    create_unified_system, get_system_info,
    ElementType, ActionType, QualityLevel,
    AirtestElement, PocoElement, ElementMapping, ElementInfo,
    QualityScore, QualityMetrics, AnalysisResult
)


class IntegrationExamples:
    """集成示例类"""
    
    def __init__(self, config_file: str = None):
        """初始化集成示例"""
        self.system = create_unified_system(config_file)
        self.examples_data = self._prepare_example_data()
    
    def _prepare_example_data(self) -> Dict[str, Any]:
        """准备示例数据"""
        return {
            'test_scripts': [
                'tests/test_login.py',
                'tests/test_navigation.py',
                'tests/test_search.py'
            ],
            'airtest_elements': [
                AirtestElement(
                    template_file="login_button.png",
                    operation_type="touch",
                    record_pos=(100, 200),
                    resolution=(1920, 1080),
                    line_number=10,
                    threshold=0.8
                ),
                AirtestElement(
                    template_file="search_input.png",
                    operation_type="touch",
                    record_pos=(200, 100),
                    resolution=(1920, 1080),
                    line_number=20,
                    threshold=0.9
                )
            ],
            'poco_elements': [
                PocoElement(
                    selector="login_button",
                    selector_type="text",
                    operation_type="click",
                    line_number=15,
                    attributes={'text': 'Login', 'enabled': True}
                ),
                PocoElement(
                    selector="search_input",
                    selector_type="attr",
                    operation_type="click",
                    line_number=25,
                    attributes={'placeholder': 'Search...', 'enabled': True}
                )
            ]
        }
    
    def example_1_basic_element_mapping(self) -> List[ElementMapping]:
        """示例1: 基础元素映射"""
        print("=" * 50)
        print("示例1: 基础元素映射")
        print("=" * 50)
        
        element_mapper = self.system['element_mapper']
        mappings = []
        
        # 创建元素映射
        for airtest_elem, poco_elem in zip(
            self.examples_data['airtest_elements'],
            self.examples_data['poco_elements']
        ):
            # 转换为 ElementInfo 对象
            airtest_info = ElementInfo(
                element_id=f"airtest_{airtest_elem.template_file}_{airtest_elem.line_number}",
                element_type=ElementType.TEMPLATE,
                locator=airtest_elem.template_file,
                line_number=airtest_elem.line_number,
                attributes={
                    'record_pos': airtest_elem.record_pos,
                    'resolution': airtest_elem.resolution,
                    'operation_type': airtest_elem.operation_type,
                    'vector': airtest_elem.vector,
                    'threshold': airtest_elem.threshold
                }
            )
            
            poco_info = ElementInfo(
                element_id=f"poco_{poco_elem.selector}_{poco_elem.line_number}",
                element_type=ElementType.POCO_TEXT if poco_elem.selector_type == 'text' else ElementType.POCO_ATTR,
                locator=poco_elem.selector,
                line_number=poco_elem.line_number,
                attributes={
                    'selector_type': poco_elem.selector_type,
                    'operation_type': poco_elem.operation_type,
                    'operation_params': poco_elem.operation_params,
                    'attributes': poco_elem.attributes
                }
            )
            
            mapping = element_mapper.create_mappings(
                [airtest_info], [poco_info]
            )[0]
            mappings.append(mapping)
            airtest_id = f"{airtest_elem.template_file}:{airtest_elem.line_number}"
            poco_id = f"{poco_elem.selector}:{poco_elem.line_number}"
            print(f"✓ 创建映射: {airtest_id} <-> {poco_id}")
        
        # 验证映射
        for mapping in mappings:
            is_valid = element_mapper.validate_mapping(mapping)
            print(f"  映射验证: {'✓' if is_valid else '✗'} {mapping.mapping_id}")
        
        print(f"\n总共创建了 {len(mappings)} 个元素映射")
        return mappings
    
    def example_2_file_analysis(self) -> List[ElementMapping]:
        """示例2: 文件分析"""
        print("\n" + "=" * 50)
        print("示例2: 文件分析")
        print("=" * 50)
        
        element_mapper = self.system['element_mapper']
        all_mappings = []
        
        # 分析测试脚本文件
        for script_file in self.examples_data['test_scripts']:
            print(f"\n分析文件: {script_file}")
            
            # 检查文件是否存在
            if not os.path.exists(script_file):
                print(f"  ⚠️  文件不存在，跳过: {script_file}")
                continue
            
            try:
                mappings = element_mapper.analyze_file(script_file)
                all_mappings.extend(mappings)
                print(f"  ✓ 发现 {len(mappings)} 个映射")
                
                # 显示映射详情
                for mapping in mappings[:3]:  # 只显示前3个
                    print(f"    - {mapping.airtest_element.element_id} <-> {mapping.poco_element.element_id}")
                
                if len(mappings) > 3:
                    print(f"    ... 还有 {len(mappings) - 3} 个映射")
                    
            except Exception as e:
                print(f"  ✗ 分析失败: {e}")
        
        print(f"\n总共分析得到 {len(all_mappings)} 个映射")
        return all_mappings
    
    def example_3_quality_analysis(self, mappings: List[ElementMapping]) -> QualityScore:
        """示例3: 质量分析"""
        print("\n" + "=" * 50)
        print("示例3: 质量分析")
        print("=" * 50)
        
        quality_analyzer = self.system['quality_analyzer']
        
        # 分析映射质量
        print("分析映射质量...")
        quality_score = quality_analyzer.analyze_quality(mappings)
        
        print(f"质量指标:")
        details = quality_score.details
        print(f"  覆盖率: {details.get('coverage', 0):.2%}")
        print(f"  准确性: {details.get('accuracy', 0):.2%}")
        print(f"  一致性: {details.get('consistency', 0):.2%}")
        print(f"  完整性: {details.get('completeness', 0):.2%}")
        print(f"  可靠性: {details.get('reliability', 0):.2%}")
        print(f"  总体评分: {quality_score.score:.2f}")
        print(f"  质量等级: {quality_score.level.value}")
        
        # 获取改进建议
        if quality_score.recommendations:
            print(f"\n改进建议:")
            for suggestion in quality_score.recommendations:
                print(f"  • {suggestion}")
        
        return quality_score
    
    def example_4_data_analysis(self, mappings: List[ElementMapping]) -> AnalysisResult:
        """示例4: 数据分析"""
        print("\n" + "=" * 50)
        print("示例4: 数据分析")
        print("=" * 50)
        
        data_analyzer = self.system['data_analyzer']
        
        # 执行综合数据分析
        print("执行综合数据分析...")
        analysis_result = data_analyzer.analyze_data(mappings, "comprehensive")
        
        print(f"分析结果:")
        print(f"  分析类型: {analysis_result.analysis_type}")
        print(f"  分析ID: {analysis_result.analysis_id}")
        print(f"  置信度: {analysis_result.confidence:.2%}")
        print(f"  成功状态: {analysis_result.success}")
        
        # 显示发现
        if analysis_result.findings:
            print(f"\n发现:")
            for finding in analysis_result.findings[:5]:  # 只显示前5个
                print(f"  • {finding}")
        
        # 显示洞察
        if analysis_result.insights:
            print(f"\n洞察:")
            for insight in analysis_result.insights[:5]:  # 只显示前5个
                print(f"  • {insight}")
        
        # 显示建议
        if analysis_result.recommendations:
            print(f"\n建议:")
            for recommendation in analysis_result.recommendations[:3]:  # 只显示前3个
                print(f"  • {recommendation}")
        
        return analysis_result
    
    def example_5_performance_optimization(self, mappings: List[ElementMapping]) -> List[ElementMapping]:
        """示例5: 性能优化"""
        print("\n" + "=" * 50)
        print("示例5: 性能优化")
        print("=" * 50)
        
        optimizer = self.system['performance_optimizer']
        
        # 优化映射
        print("优化元素映射...")
        optimized_mappings = optimizer.optimize_mappings(mappings)
        
        print(f"优化结果:")
        print(f"  原始映射数量: {len(mappings)}")
        print(f"  优化后数量: {len(optimized_mappings)}")
        print(f"  优化比例: {(len(mappings) - len(optimized_mappings)) / len(mappings) * 100:.1f}%")
        
        # 获取性能指标
        metrics = optimizer.get_performance_metrics()
        print(f"\n性能指标:")
        print(f"  执行时间: {metrics.execution_time:.3f}s")
        print(f"  内存使用: {metrics.memory_usage:.1f}%")
        print(f"  CPU使用: {metrics.cpu_usage:.1f}%")
        print(f"  缓存命中率: {metrics.cache_hit_rate:.1f}%")
        print(f"  吞吐量: {metrics.throughput:.2f}")
        print(f"  错误率: {metrics.error_rate:.1f}%")
        
        # 获取优化建议
        suggestions = optimizer.get_optimization_suggestions(metrics)
        if suggestions:
            print(f"\n优化建议:")
            for suggestion in suggestions[:3]:  # 只显示前3个
                print(f"  • {suggestion}")
        
        return optimized_mappings
    
    def example_6_report_generation(self, mappings: List[ElementMapping], 
                                   quality_metrics: QualityScore,
                                   analysis_result: AnalysisResult) -> str:
        """示例6: 报告生成"""
        print("\n" + "=" * 50)
        print("示例6: 报告生成")
        print("=" * 50)
        
        report_generator = self.system['report_generator']
        
        # 生成综合报告
        print("生成综合报告...")
        
        # 准备报告数据
        report_data = {
            'mappings': mappings,
            'quality_metrics': quality_metrics,
            'analysis_result': analysis_result
        }
        
        # 生成HTML报告
        html_file = report_generator.generate_file_report(
            report_data, report_type="comprehensive", format="html"
        )
        print(f"✓ HTML报告已保存: {html_file}")
        
        # 生成JSON报告
        json_file = report_generator.generate_file_report(
            report_data, report_type="comprehensive", format="json"
        )
        print(f"✓ JSON报告已保存: {json_file}")
        
        # 生成Markdown报告
        md_file = report_generator.generate_file_report(
            report_data, report_type="comprehensive", format="markdown"
        )
        print(f"✓ Markdown报告已保存: {md_file}")
        
        return html_file
    
    def example_7_monitoring(self) -> None:
        """示例7: 监控系统"""
        print("\n" + "=" * 50)
        print("示例7: 监控系统")
        print("=" * 50)
        
        monitor = self.system['monitor']
        
        # 记录事件
        print("记录监控事件...")
        monitor.log_event("system_start", "integration_example", {"component": "integration_example"})
        monitor.log_event("mapping_created", "integration_example", {"count": 10})
        monitor.log_event("analysis_completed", "integration_example", {"duration": 2.5})
        
        # 记录性能快照
        print("记录性能快照...")
        monitor.record_performance(
            cpu_usage=45.2,
            memory_usage=512.8,
            active_threads=4,
            cache_hit_rate=0.85,
            processing_rate=10.5,
            error_count=0
        )
        
        # 记录质量快照（需要QualityMetrics对象）
        print("记录质量快照...")
        from core.unified_models import QualityMetrics, QualityScore, QualityLevel
        from datetime import datetime
        
        # 创建质量分数
        performance_score = QualityScore(85.0, QualityLevel.GOOD)
        visibility_score = QualityScore(90.0, QualityLevel.EXCELLENT)
        accessibility_score = QualityScore(75.0, QualityLevel.GOOD)
        stability_score = QualityScore(88.0, QualityLevel.GOOD)
        interaction_score = QualityScore(82.0, QualityLevel.GOOD)
        overall_score = QualityScore(84.0, QualityLevel.GOOD)
        
        quality_metrics = QualityMetrics(
            element_id="integration_test_element",
            timestamp=datetime.now(),
            performance_score=performance_score,
            visibility_score=visibility_score,
            accessibility_score=accessibility_score,
            stability_score=stability_score,
            interaction_score=interaction_score,
            overall_score=overall_score
        )
        monitor.record_quality(quality_metrics)
        
        # 生成监控报告
        print("生成监控报告...")
        monitoring_report = monitor.generate_monitoring_report()
        
        # 保存监控报告
        import json
        monitor_file = "monitoring_report.json"
        with open(monitor_file, 'w', encoding='utf-8') as f:
            json.dump(monitoring_report, f, indent=2, ensure_ascii=False)
        print(f"✓ 监控报告已保存: {monitor_file}")
        
        # 获取统计信息
        statistics = monitor.get_statistics()
        print(f"\n监控统计:")
        for key, value in statistics.items():
            print(f"  {key}: {value}")
    
    def example_8_configuration_management(self) -> None:
        """示例8: 配置管理"""
        print("\n" + "=" * 50)
        print("示例8: 配置管理")
        print("=" * 50)
        
        config_manager = self.system['config_manager']
        
        # 显示当前配置
        print("当前配置:")
        current_config = config_manager.get_all_config()
        for section, settings in current_config.items():
            print(f"  [{section}]")
            if isinstance(settings, dict):
                for key, value in settings.items():
                    print(f"    {key}: {value}")
            else:
                print(f"    {settings}")
        
        # 修改配置
        print(f"\n修改配置...")
        config_manager.set_config('mapping.confidence_threshold', 0.9)
        config_manager.set_config('system.max_workers', 8)
        config_manager.set_config('report.output_formats', ['html', 'json', 'markdown'])
        
        # 验证配置
        print("验证配置...")
        current_config = config_manager.get_all_config()
        is_valid = config_manager.validate_config(current_config)
        print(f"配置验证: {'✓' if is_valid else '✗'}")
        
        # 保存配置
        config_file = "integration_example_config.yaml"
        updated_config = config_manager.get_all_config()
        config_manager.save_config(updated_config, config_file)
        print(f"✓ 配置已保存: {config_file}")
    
    def run_all_examples(self) -> None:
        """运行所有示例"""
        print("YouKey Life Element Exploration - 统一架构集成示例")
        print("=" * 80)
        
        # 显示系统信息
        system_info = get_system_info()
        print(f"系统版本: {system_info['version']}")
        print(f"组件数量: {len(system_info['components'])}")
        print(f"功能特性: {len(system_info['features'])}")
        
        try:
            # 示例1: 基础元素映射
            mappings = self.example_1_basic_element_mapping()
            
            # 示例2: 文件分析
            file_mappings = self.example_2_file_analysis()
            all_mappings = mappings + file_mappings
            
            # 示例3: 质量分析
            quality_score = self.example_3_quality_analysis(all_mappings)
            
            # 示例4: 数据分析
            analysis_result = self.example_4_data_analysis(all_mappings)
            
            # 示例5: 性能优化
            optimized_mappings = self.example_5_performance_optimization(all_mappings)
            
            # 示例6: 报告生成
            report_file = self.example_6_report_generation(
                optimized_mappings, quality_score, analysis_result
            )
            
            # 示例7: 监控系统
            self.example_7_monitoring()
            
            # 示例8: 配置管理
            self.example_8_configuration_management()
            
            print("\n" + "=" * 80)
            print("所有示例执行完成！")
            print("=" * 80)
            print(f"生成的文件:")
            print(f"  • HTML报告: integration_example_report.html")
            print(f"  • JSON报告: integration_example_report.json")
            print(f"  • 数据仪表板: integration_dashboard.html")
            print(f"  • 监控报告: monitoring_report.json")
            print(f"  • 配置文件: integration_example_config.yaml")
            
        except Exception as e:
            print(f"\n✗ 示例执行失败: {e}")
            import traceback
            traceback.print_exc()


def quick_start_example():
    """快速开始示例"""
    print("快速开始示例")
    print("=" * 30)
    
    # 1. 创建统一系统
    print("1. 创建统一系统...")
    system = create_unified_system()
    
    # 2. 创建示例元素
    print("2. 创建示例元素...")
    airtest_elem = AirtestElement(
        template_file="button.png",
        operation_type="touch",
        record_pos=(100, 100),
        resolution=(1920, 1080),
        line_number=1,
        threshold=0.8
    )
    
    poco_elem = PocoElement(
        selector="button",
        selector_type="text",
        operation_type="click",
        line_number=2,
        attributes={'text': 'Click Me'}
    )
    
    # 3. 创建映射
    print("3. 创建元素映射...")
    element_mapper = system['element_mapper']
    
    # 转换为ElementInfo格式
    from core.unified_models import ElementInfo, ElementType, generate_element_id
    
    airtest_info = ElementInfo(
        element_id=generate_element_id(ElementType.TEMPLATE, airtest_elem.template_file, airtest_elem.line_number),
        element_type=ElementType.TEMPLATE,
        locator=f"Template(r'{airtest_elem.template_file}')",
        line_number=airtest_elem.line_number,
        attributes={'operation_type': airtest_elem.operation_type}
    )
    
    poco_info = ElementInfo(
        element_id=generate_element_id(ElementType.POCO_TEXT, poco_elem.selector, poco_elem.line_number),
        element_type=ElementType.POCO_TEXT,
        locator=poco_elem.selector,
        line_number=poco_elem.line_number,
        attributes={'selector_type': poco_elem.selector_type, 'operation_type': poco_elem.operation_type}
    )
    
    mappings = element_mapper.create_mappings([airtest_info], [poco_info])
    if mappings:
        print(f"✓ 映射创建成功: {mappings[0].mapping_id}")
    else:
        print("✗ 映射创建失败")
    
    # 4. 质量分析
    print("4. 执行质量分析...")
    if mappings:
        quality_analyzer = system['quality_analyzer']
        quality = quality_analyzer.analyze_quality(mappings)
        print(f"✓ 质量评分: {quality.score:.2f}")
        
        # 5. 生成报告
        print("5. 生成报告...")
        report_generator = system['report_generator']
        report = report_generator.generate_file_report(mappings)
        print(f"✓ 报告生成完成")
    else:
        print("✗ 无法进行质量分析和报告生成，因为映射创建失败")
    
    print("\n快速开始示例完成！")


if __name__ == "__main__":
    # 运行快速开始示例
    quick_start_example()
    
    print("\n" + "=" * 80)
    
    # 运行完整示例
    examples = IntegrationExamples()
    examples.run_all_examples()