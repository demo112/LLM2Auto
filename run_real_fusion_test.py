#!/usr/bin/env python3
# -*- encoding=utf8 -*-
"""
使用真实测试用例运行融合测试系统

本脚本使用 tests 目录中的真实 Airtest 和 Poco 测试用例来演示融合测试系统的功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from airtest_framework.fusion.main import FusionTestFramework
from airtest_framework.fusion.config import FusionConfig, ExecutionStrategy, FallbackMode
from airtest_framework.fusion.persistence import FusionScript
from airtest_framework.fusion.failover_executor import FusionExecutionResult


def print_banner():
    """打印横幅"""
    print("=" * 80)
    print("🚀 融合测试系统 - 真实用例测试")
    print("=" * 80)
    print()


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'=' * 60}")
    print(f"📋 {title}")
    print("=" * 60)


async def run_real_fusion_test():
    """运行真实用例的融合测试"""
    
    print_banner()
    
    # 1. 初始化融合测试框架
    print_section("1. 初始化融合测试框架")
    
    # 配置框架使用真实的tests目录
    config = FusionConfig(
        test_root_dir="tests",  # 使用真实的tests目录
        execution_strategy=ExecutionStrategy.AUTO,
        fallback_mode=FallbackMode.RETRY_THEN_FALLBACK,
        debug_mode=True,
        verbose_logging=True
    )
    
    framework = FusionTestFramework(config)
    print("✅ 融合测试框架初始化完成")
    print(f"   测试根目录: {config.test_root_dir}")
    print(f"   执行策略: {config.execution_strategy.value}")
    print(f"   故障切换模式: {config.fallback_mode.value}")
    
    # 2. 发现真实测试用例
    print_section("2. 发现真实测试用例")
    
    test_cases = framework.discover_test_cases()
    print(f"✅ 发现 {len(test_cases)} 个测试用例:")
    
    for i, case in enumerate(test_cases, 1):
        print(f"   {i}. {case.name}")
        print(f"      Airtest脚本: {case.airtest_path}")
        print(f"      Poco脚本: {case.poco_path}")
        if case.metadata:
            print(f"      描述: {case.metadata.get('description', 'N/A')}")
            print(f"      作者: {case.metadata.get('author', 'N/A')}")
            print(f"      优先级: {case.metadata.get('priority', 'N/A')}")
        print()
    
    if not test_cases:
        print("❌ 未发现任何测试用例，请检查tests目录结构")
        return
    
    # 3. 解析真实脚本内容
    print_section("3. 解析真实脚本内容")
    
    for case in test_cases:
        print(f"📄 解析测试用例: {case.name}")
        
        # 解析Airtest脚本
        if case.airtest_path and os.path.exists(case.airtest_path):
            airtest_metadata, airtest_steps = framework.parser.parse_script_file(case.airtest_path)
            print(f"   ✅ Airtest脚本解析完成 ({airtest_metadata.total_lines} 行)")
            print(f"      解析步骤: {len(airtest_steps)} 个")
            print(f"      操作类型: {_extract_operation_types(airtest_steps)}")
        else:
            print(f"   ⚠️  Airtest脚本不存在: {case.airtest_path}")
        
        # 解析Poco脚本
        if case.poco_path and os.path.exists(case.poco_path):
            poco_metadata, poco_steps = framework.parser.parse_script_file(case.poco_path)
            print(f"   ✅ Poco脚本解析完成 ({poco_metadata.total_lines} 行)")
            print(f"      解析步骤: {len(poco_steps)} 个")
            print(f"      操作类型: {_extract_operation_types(poco_steps)}")
        else:
            print(f"   ⚠️  Poco脚本不存在: {case.poco_path}")
        print()
    
    # 4. 智能融合处理
    print_section("4. 智能融合处理")
    
    fusion_results = []
    
    for case in test_cases:
        if case.airtest_path and case.poco_path and \
           os.path.exists(case.airtest_path) and os.path.exists(case.poco_path):
            
            print(f"🔄 处理融合: {case.name}")
            
            try:
                # 使用框架的融合处理方法
                script_path = await framework.process_fusion(case)
                
                if script_path:
                    print(f"   ✅ 融合脚本生成成功")
                    print(f"      保存路径: {script_path}")
                    
                    # 加载融合脚本以获取详细信息
                    fusion_script = framework.persistence.load_fusion_script(script_path)
                    if fusion_script:
                        print(f"      步骤数量: {len(fusion_script.steps)}")
                        print(f"      平均置信度: {fusion_script.metadata.confidence_avg:.2f}")
                        fusion_results.append(fusion_script)
                    else:
                        print(f"      ⚠️  无法加载融合脚本详细信息")
                else:
                    print(f"   ❌ 融合脚本生成失败")
                    
            except Exception as e:
                print(f"   ❌ 融合处理出错: {e}")
        else:
            print(f"⚠️  跳过 {case.name}: 缺少必要的脚本文件")
        print()
    
    # 5. 执行融合脚本
    print_section("5. 执行融合脚本")
    
    if fusion_results:
        print("🎯 开始执行融合脚本...")
        print("⚠️  注意: 由于没有连接真实设备，这里只进行模拟执行")
        print()
        
        execution_results = []
        
        for fusion_script in fusion_results:
            print(f"▶️  执行: {fusion_script.metadata.name}")
            
            try:
                # 模拟执行（因为没有真实设备）
                result = _simulate_execution(fusion_script)
                execution_results.append(result)
                
                if result.overall_success:
                    print(f"   ✅ 执行成功")
                    print(f"      执行时间: {result.total_execution_time:.2f}秒")
                    print(f"      成功步骤: {result.successful_steps}/{result.total_steps}")
                else:
                    print(f"   ❌ 执行失败")
                    print(f"      成功步骤: {result.successful_steps}/{result.total_steps}")
                    if result.error_summary:
                        print(f"      错误信息: {'; '.join(result.error_summary)}")
                    
            except Exception as e:
                print(f"   ❌ 执行出错: {e}")
            print()
    else:
        print("⚠️  没有可执行的融合脚本")
    
    # 6. 生成测试报告
    print_section("6. 测试总结")
    
    print("📊 测试执行总结:")
    print(f"   发现测试用例: {len(test_cases)}")
    print(f"   成功融合: {len(fusion_results)}")
    
    if 'execution_results' in locals() and execution_results:
        successful_executions = sum(1 for r in execution_results if r.overall_success)
        print(f"   成功执行: {successful_executions}/{len(execution_results)}")
        print(f"   成功率: {successful_executions/len(execution_results)*100:.1f}%")
    else:
        print(f"   成功执行: 0/0")
    
    print("\n🎉 真实用例融合测试完成！")
    
    # 7. 展示融合脚本内容
    if fusion_results:
        print_section("7. 融合脚本示例")
        
        # 展示第一个融合脚本的详细内容
        sample_script = fusion_results[0]
        print(f"📋 融合脚本示例: {sample_script.metadata.name}")
        print(f"   版本: {sample_script.metadata.version}")
        print(f"   平均置信度: {sample_script.metadata.confidence_avg:.2f}")
        print(f"   创建时间: {sample_script.metadata.created_at}")
        print(f"   总步骤数: {sample_script.metadata.total_steps}")
        print("\n   融合步骤:")
        
        for i, step in enumerate(sample_script.steps[:5], 1):  # 只显示前5步
            print(f"     {i}. {step.operation_type}: {step.description}")
            print(f"        目标元素: {step.target_element}")
            print(f"        置信度: {step.confidence_score:.2f}")
            if step.semantic_tags:
                print(f"        语义标签: {', '.join(step.semantic_tags)}")
        
        if len(sample_script.steps) > 5:
            print(f"     ... 还有 {len(sample_script.steps) - 5} 个步骤")


def _extract_operation_types(steps) -> str:
    """从操作步骤列表中提取操作类型"""
    if not steps:
        return 'none'
    
    operation_types = [step.operation_type.value for step in steps]
    unique_types = list(set(operation_types))
    
    return ', '.join(unique_types) if unique_types else 'unknown'


def _simulate_execution(fusion_script: FusionScript) -> FusionExecutionResult:
    """模拟执行融合脚本"""
    import time
    import random
    from airtest_framework.fusion.failover_executor import StepExecutionResult, StepResult
    
    # 模拟执行时间
    execution_time = random.uniform(2.0, 8.0)
    time.sleep(0.1)  # 短暂延迟模拟执行
    
    # 模拟执行结果
    success = random.choice([True, True, True, False])  # 75%成功率
    
    total_steps = len(fusion_script.steps)
    successful_steps = 0
    failed_steps = 0
    step_results = []
    error_summary = []
    
    if success:
        successful_steps = total_steps
        for i, step in enumerate(fusion_script.steps):
            step_results.append(StepExecutionResult(
                step_id=step.step_id,
                execution_method="airtest",
                result=StepResult.SUCCESS,
                execution_time=random.uniform(0.5, 2.0)
            ))
    else:
        # 模拟部分执行
        successful_steps = random.randint(1, total_steps - 1)
        failed_steps = total_steps - successful_steps
        
        for i, step in enumerate(fusion_script.steps):
            if i < successful_steps:
                step_results.append(StepExecutionResult(
                    step_id=step.step_id,
                    execution_method="airtest",
                    result=StepResult.SUCCESS,
                    execution_time=random.uniform(0.5, 2.0)
                ))
            else:
                step_results.append(StepExecutionResult(
                    step_id=step.step_id,
                    execution_method="airtest",
                    result=StepResult.FAILED,
                    execution_time=random.uniform(0.1, 1.0),
                    error_message="模拟执行失败: 设备连接超时"
                ))
        error_summary.append("模拟执行失败: 设备连接超时")
    
    return FusionExecutionResult(
        script_name=fusion_script.metadata.name,
        total_steps=total_steps,
        successful_steps=successful_steps,
        failed_steps=failed_steps,
        skipped_steps=0,
        total_execution_time=execution_time,
        step_results=step_results,
        overall_success=success,
        error_summary=error_summary
    )


if __name__ == "__main__":
    asyncio.run(run_real_fusion_test())