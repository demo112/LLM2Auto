#!/usr/bin/env python3
# -*- encoding=utf8 -*-
"""
测试Qwen API集成

验证Qwen API的配置、连接和调用功能
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from airtest_framework.fusion.qwen_config import QwenConfig, get_default_config, create_config
from airtest_framework.fusion.intelligent_alignment import QwenAlignmentAssistant
from airtest_framework.fusion.enhanced_parser import OperationStep, OperationType


def test_config_creation():
    """测试配置创建"""
    print("🔧 测试配置创建...")
    
    # 测试从环境变量创建配置
    try:
        config = get_default_config()
        if config:
            print(f"✅ 从环境变量创建配置成功")
            print(f"   API密钥: {config.api_key[:10]}...")
            print(f"   基础URL: {config.base_url}")
            print(f"   模型: {config.model}")
        else:
            print("⚠️  未设置环境变量，无法创建默认配置")
    except Exception as e:
        print(f"❌ 从环境变量创建配置失败: {e}")
    
    # 测试手动创建配置
    try:
        test_config = create_config(
            api_key="test_key_12345",
            base_url="https://api.test.com/v1",
            model="test-model"
        )
        print(f"✅ 手动创建配置成功")
        print(f"   API密钥: {test_config.api_key}")
        print(f"   基础URL: {test_config.base_url}")
        print(f"   模型: {test_config.model}")
    except Exception as e:
        print(f"❌ 手动创建配置失败: {e}")


async def test_api_connection():
    """测试API连接"""
    print("\n🌐 测试API连接...")
    
    config = get_default_config()
    if not config:
        print("⚠️  跳过API连接测试：未设置API配置")
        return
    
    try:
        assistant = QwenAlignmentAssistant(config)
        
        # 创建测试步骤
        airtest_step = OperationStep(
            operation_type=OperationType.CLICK,
            target="tpl1234567890.png",
            parameters={"pos": [100, 200]},
            code_line="touch(Template(r\"tpl1234567890.png\"))",
            line_number=10
        )
        
        poco_step = OperationStep(
            operation_type=OperationType.CLICK,
            target="login_button",
            parameters={"text": "登录"},
            code_line="poco(\"login_button\").click()",
            line_number=5
        )
        
        print("📤 发送API请求...")
        result = await assistant.analyze_step_similarity(airtest_step, poco_step)
        
        print("✅ API调用成功")
        print(f"   相似度分数: {result.get('similarity_score', 'N/A')}")
        print(f"   语义描述: {result.get('semantic_description', 'N/A')}")
        print(f"   置信度: {result.get('confidence', 'N/A')}")
        print(f"   推理过程: {result.get('reasoning', 'N/A')}")
        
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        
        # 检查常见错误
        if "API密钥无效" in str(e):
            print("💡 建议: 检查QWEN_API_KEY环境变量是否正确设置")
        elif "网络" in str(e) or "连接" in str(e):
            print("💡 建议: 检查网络连接和防火墙设置")
        elif "速率限制" in str(e):
            print("💡 建议: API调用频率过高，请稍后重试")


def test_error_handling():
    """测试错误处理"""
    print("\n🛡️  测试错误处理...")
    
    # 测试无效API密钥
    try:
        invalid_config = create_config(api_key="invalid_key")
        assistant = QwenAlignmentAssistant(invalid_config)
        print("✅ 无效配置创建成功（预期行为）")
    except Exception as e:
        print(f"❌ 无效配置创建失败: {e}")
    
    # 测试配置验证
    try:
        invalid_config = QwenConfig(
            api_key="",  # 空API密钥
            max_retries=-1,  # 无效重试次数
            timeout=0  # 无效超时时间
        )
        invalid_config.validate()
        print("❌ 配置验证应该失败但没有失败")
    except ValueError as e:
        print(f"✅ 配置验证正确捕获错误: {e}")
    except Exception as e:
        print(f"❌ 配置验证出现意外错误: {e}")


async def main():
    """主测试函数"""
    print("🧪 Qwen API集成测试")
    print("=" * 60)
    
    # 检查环境变量
    api_key = os.getenv("QWEN_API_KEY")
    if api_key:
        print(f"🔑 检测到API密钥: {api_key[:10]}...")
    else:
        print("⚠️  未检测到QWEN_API_KEY环境变量")
        print("   某些测试将被跳过")
    
    print()
    
    # 运行测试
    test_config_creation()
    await test_api_connection()
    test_error_handling()
    
    print("\n🎉 测试完成！")


if __name__ == "__main__":
    asyncio.run(main())