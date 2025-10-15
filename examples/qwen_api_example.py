#!/usr/bin/env python3
"""
Qwen API 使用示例

这个示例展示了如何配置和使用 Qwen API 进行智能步骤对齐。
包含了完整的配置、错误处理和最佳实践。

使用前请确保：
1. 设置环境变量 QWEN_API_KEY
2. 安装必要的依赖：pip install aiohttp
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from airtest_framework.fusion.qwen_config import QwenConfig, create_config, get_default_config
from airtest_framework.fusion.intelligent_alignment import QwenAlignmentAssistant, align_script_pair
from airtest_framework.fusion.enhanced_parser import OperationStep, OperationType


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print('='*60)


def print_step(step: str, status: str = "info"):
    """打印步骤信息"""
    icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
    print(f"{icons.get(status, 'ℹ️')} {step}")


async def example_1_basic_configuration():
    """示例1: 基础配置"""
    print_section("示例1: 基础配置")
    
    # 方法1: 从环境变量创建配置
    try:
        config = get_default_config()
        if config:
            print_step("从环境变量成功创建配置", "success")
            print(f"   API密钥: {config.api_key[:10]}...")
            print(f"   基础URL: {config.base_url}")
            print(f"   模型: {config.model}")
        else:
            print_step("环境变量未设置，使用手动配置", "warning")
    except Exception as e:
        print_step(f"配置创建失败: {e}", "error")
    
    # 方法2: 手动创建配置
    manual_config = create_config(
        api_key="your_api_key_here",
        base_url="https://api.siliconflow.cn/v1",
        model="Qwen/Qwen2.5-7B-Instruct",
        max_retries=3,
        timeout=30
    )
    print_step("手动创建配置成功", "success")
    print(f"   重试次数: {manual_config.max_retries}")
    print(f"   超时时间: {manual_config.timeout}秒")


async def example_2_api_assistant():
    """示例2: 使用 QwenAlignmentAssistant"""
    print_section("示例2: 使用 QwenAlignmentAssistant")
    
    # 创建测试步骤
    airtest_step = OperationStep(
        step_id="test_001",
        description="点击登录按钮",
        operation_type=OperationType.CLICK,
        target_element="login_button",
        parameters={"target": "login_button", "position": (100, 200)}
    )
    
    poco_step = OperationStep(
        step_id="test_002", 
        description="点击登录按钮",
        operation_type=OperationType.CLICK,
        target_element="login_btn",
        parameters={"selector": "login_btn", "text": "登录"}
    )
    
    print_step("创建测试步骤", "info")
    print(f"   Airtest步骤: {airtest_step.description} ({airtest_step.operation_type.value})")
    print(f"   Poco步骤: {poco_step.description} ({poco_step.operation_type.value})")
    
    # 检查API配置
    config = get_default_config()
    if not config:
        print_step("跳过API调用：未设置API密钥", "warning")
        print("   请设置环境变量 QWEN_API_KEY 来启用真实API调用")
        return
    
    try:
        # 创建助手
        assistant = QwenAlignmentAssistant(config)
        print_step("创建 QwenAlignmentAssistant", "success")
        
        # 分析步骤相似度
        print_step("正在分析步骤相似度...", "info")
        similarity_result = await assistant.analyze_step_similarity(airtest_step, poco_step)
        
        print_step("相似度分析完成", "success")
        print(f"   语义相似度: {similarity_result.get('semantic_similarity', 0):.2f}")
        print(f"   语法相似度: {similarity_result.get('syntactic_similarity', 0):.2f}")
        print(f"   整体置信度: {similarity_result.get('confidence', 0):.2f}")
        print(f"   分析说明: {similarity_result.get('explanation', 'N/A')}")
        
    except Exception as e:
        print_step(f"API调用失败: {e}", "error")
        print("   这可能是由于网络问题、API密钥无效或配额不足")


async def example_3_script_alignment():
    """示例3: 完整的脚本对齐"""
    print_section("示例3: 完整的脚本对齐")
    
    # 创建测试脚本步骤
    airtest_steps = [
        OperationStep(
            step_id="airtest_001",
            description="点击用户名输入框",
            operation_type=OperationType.CLICK,
            target_element="username_field",
            parameters={"target": "username_field"}
        ),
        OperationStep(
            step_id="airtest_002",
            description="输入用户名",
            operation_type=OperationType.INPUT,
            target_element="username_field",
            parameters={"text": "admin"}
        ),
        OperationStep(
            step_id="airtest_003",
            description="点击登录按钮",
            operation_type=OperationType.CLICK,
            target_element="login_button",
            parameters={"target": "login_button"}
        )
    ]
    
    poco_steps = [
        OperationStep(
            step_id="poco_001",
            description="点击用户名输入框",
            operation_type=OperationType.CLICK,
            target_element="input[name='username']",
            parameters={"selector": "input[name='username']"}
        ),
        OperationStep(
            step_id="poco_002",
            description="输入用户名",
            operation_type=OperationType.INPUT,
            target_element="input[name='username']",
            parameters={"text": "admin"}
        ),
        OperationStep(
            step_id="poco_003",
            description="点击登录按钮",
            operation_type=OperationType.CLICK,
            target_element="button.login",
            parameters={"selector": "button.login"}
        )
    ]
    
    print_step(f"创建测试脚本 (Airtest: {len(airtest_steps)}步, Poco: {len(poco_steps)}步)", "info")
    
    # 检查API配置
    config = get_default_config()
    if not config:
        print_step("使用基础对齐算法（无AI增强）", "warning")
        config = None
    else:
        print_step("使用AI增强的对齐算法", "success")
    
    try:
        # 执行脚本对齐
        print_step("正在执行脚本对齐...", "info")
        alignment_results = await align_script_pair(
            airtest_steps=airtest_steps,
            poco_steps=poco_steps,
            qwen_config=config
        )
        
        print_step(f"对齐完成，发现 {len(alignment_results)} 个对齐结果", "success")
        
        # 显示对齐结果
        for i, result in enumerate(alignment_results, 1):
            print(f"\n   对齐结果 {i}:")
            print(f"     置信度: {result.alignment_confidence:.2f}")
            if result.airtest_step:
                print(f"     Airtest: {result.airtest_step.description} ({result.airtest_step.operation_type.value})")
            if result.poco_step:
                print(f"     Poco: {result.poco_step.description} ({result.poco_step.operation_type.value})")
            print(f"     说明: {result.semantic_description}")
            
    except Exception as e:
        print_step(f"脚本对齐失败: {e}", "error")


async def example_4_error_handling():
    """示例4: 错误处理和最佳实践"""
    print_section("示例4: 错误处理和最佳实践")
    
    # 测试无效配置
    print_step("测试无效配置处理", "info")
    try:
        invalid_config = QwenConfig(
            api_key="",  # 空API密钥
            base_url="invalid_url",
            model="invalid_model"
        )
        invalid_config.validate()
    except ValueError as e:
        print_step(f"正确捕获配置错误: {e}", "success")
    
    # 测试网络错误处理
    print_step("测试网络错误处理", "info")
    try:
        # 使用无效的API配置
        invalid_config = create_config(
            api_key="invalid_key",
            base_url="https://invalid.api.endpoint/v1",
            model="test-model",
            timeout=5  # 短超时用于快速测试
        )
        
        assistant = QwenAlignmentAssistant(invalid_config)
        
        # 创建简单的测试步骤
        test_step1 = OperationStep(
            step_id="test_step1",
            description="测试步骤1",
            operation_type=OperationType.CLICK,
            target_element="test",
            parameters={"target": "test"}
        )
        test_step2 = OperationStep(
            step_id="test_step2",
            description="测试步骤2",
            operation_type=OperationType.CLICK,
            target_element="test",
            parameters={"target": "test"}
        )
        
        # 这应该会失败并触发错误处理
        await assistant.analyze_step_similarity(test_step1, test_step2)
        
    except Exception as e:
        print_step(f"正确处理网络错误: {type(e).__name__}", "success")
        print(f"     错误详情: {str(e)[:100]}...")


def print_configuration_guide():
    """打印配置指南"""
    print_section("配置指南")
    
    print("📋 环境变量配置:")
    print("   export QWEN_API_KEY='your_api_key_here'")
    print("   export QWEN_BASE_URL='https://api.siliconflow.cn/v1'  # 可选")
    print("   export QWEN_MODEL='Qwen/Qwen2.5-7B-Instruct'  # 可选")
    
    print("\n🔧 代码配置:")
    print("   from airtest_framework.fusion.qwen_config import create_config")
    print("   config = create_config(")
    print("       api_key='your_api_key',")
    print("       base_url='https://api.siliconflow.cn/v1',")
    print("       model='Qwen/Qwen2.5-7B-Instruct'")
    print("   )")
    
    print("\n⚡ 性能优化建议:")
    print("   • 设置合理的超时时间 (推荐: 30秒)")
    print("   • 配置重试次数 (推荐: 3次)")
    print("   • 批量处理步骤以减少API调用")
    print("   • 缓存相似的分析结果")
    
    print("\n🛡️ 错误处理:")
    print("   • 始终验证配置: config.validate()")
    print("   • 使用try-catch处理API调用")
    print("   • 提供降级方案（基础算法）")
    print("   • 监控API配额和速率限制")


async def main():
    """主函数"""
    print("🚀 Qwen API 集成示例")
    print("=" * 60)
    
    # 检查环境
    api_key = os.getenv('QWEN_API_KEY')
    if api_key:
        print_step(f"检测到API密钥: {api_key[:10]}...", "success")
    else:
        print_step("未检测到QWEN_API_KEY环境变量", "warning")
        print("   某些示例将使用模拟数据或被跳过")
    
    try:
        # 运行所有示例
        await example_1_basic_configuration()
        await example_2_api_assistant()
        await example_3_script_alignment()
        await example_4_error_handling()
        
        # 显示配置指南
        print_configuration_guide()
        
        print_section("示例完成")
        print_step("所有示例运行完成！", "success")
        print("📚 更多信息请参考项目文档")
        
    except KeyboardInterrupt:
        print_step("用户中断", "warning")
    except Exception as e:
        print_step(f"运行出错: {e}", "error")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())