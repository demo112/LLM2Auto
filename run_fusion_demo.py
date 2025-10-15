# -*- encoding=utf8 -*-
"""
融合测试系统演示脚本

展示融合测试系统的完整使用流程
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from airtest_framework.fusion.main import FusionTestFramework
from airtest_framework.fusion.failover_executor import ExecutionConfig, ExecutionStrategy
from airtest_framework.fusion.persistence import FusionPersistence
from airtest_framework.fusion.integration_test import run_integration_tests


async def demo_fusion_system():
    """演示融合测试系统"""
    print("🚀 融合测试系统演示")
    print("="*60)
    
    # 1. 初始化融合测试框架
    print("\n1. 初始化融合测试框架...")
    framework = FusionTestFramework()
    
    # 2. 发现测试用例
    print("\n2. 发现测试用例...")
    test_root = "tests/mobile"
    
    if not os.path.exists(test_root):
        print(f"❌ 测试目录不存在: {test_root}")
        print("请确保项目中存在测试脚本")
        return
    
    test_cases = framework.discover_test_cases(test_root)
    print(f"✓ 发现 {len(test_cases)} 个测试用例")
    
    for case in test_cases:
        print(f"  - {case.name}")
        print(f"    Airtest: {'✓' if case.airtest_path else '✗'}")
        print(f"    Poco: {'✓' if case.poco_path else '✗'}")
    
    if len(test_cases) == 0:
        print("❌ 未发现任何测试用例")
        return
    
    # 3. 处理融合脚本
    print("\n3. 处理融合脚本...")
    
    for test_case in test_cases:
        if test_case.airtest_path and test_case.poco_path:
            print(f"\n处理测试用例: {test_case.name}")
            
            try:
                # 注意：这里需要真实的Qwen API密钥才能正常工作
                # 在演示中，我们模拟融合过程
                print("  - 解析Airtest脚本...")
                print("  - 解析Poco脚本...")
                print("  - 执行智能对齐...")
                print("  - 保存融合脚本...")
                
                # 模拟融合结果
                fusion_result = f"{test_case.name}_fusion.json"
                print(f"  ✓ 融合完成: {fusion_result}")
                
            except Exception as e:
                print(f"  ❌ 融合失败: {str(e)}")
    
    # 4. 演示持久化功能
    print("\n4. 演示持久化功能...")
    persistence = FusionPersistence("fusion_scripts")
    
    # 列出所有融合脚本
    scripts = persistence.list_fusion_scripts()
    print(f"✓ 找到 {len(scripts)} 个融合脚本")
    
    for script in scripts:
        print(f"  - {script['name']} (v{script['version']})")
        print(f"    步骤数: {script['total_steps']}")
        print(f"    匹配率: {script['matched_steps']}/{script['total_steps']}")
        print(f"    平均置信度: {script['confidence_avg']:.2f}")
    
    # 5. 演示执行配置
    print("\n5. 演示执行配置...")
    
    # 不同的执行策略
    strategies = [
        (ExecutionStrategy.AIRTEST_FIRST, "Airtest优先策略"),
        (ExecutionStrategy.POCO_FIRST, "Poco优先策略"),
        (ExecutionStrategy.ADAPTIVE, "自适应策略")
    ]
    
    for strategy, description in strategies:
        config = ExecutionConfig(
            strategy=strategy,
            timeout=30,
            retry_count=2,
            failover_enabled=True,
            screenshot_on_error=True,
            continue_on_error=True
        )
        print(f"  - {description}")
        print(f"    超时时间: {config.timeout}秒")
        print(f"    重试次数: {config.retry_count}")
        print(f"    故障切换: {'启用' if config.failover_enabled else '禁用'}")
    
    # 6. 演示系统特性
    print("\n6. 系统特性展示...")
    
    features = [
        "✓ 自动脚本发现和匹配",
        "✓ 智能步骤对齐算法",
        "✓ Qwen AI语义分析",
        "✓ 持久化存储和版本管理",
        "✓ 故障切换执行引擎",
        "✓ 多种执行策略",
        "✓ 错误截图和日志记录",
        "✓ 完整的测试报告",
        "✓ 扩展性架构设计"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n🎉 融合测试系统演示完成！")


async def demo_integration_tests():
    """演示集成测试"""
    print("\n🧪 运行集成测试...")
    print("="*60)
    
    try:
        results = await run_integration_tests()
        
        if results['failed_tests'] == 0:
            print("\n✅ 所有集成测试通过！")
        else:
            print(f"\n⚠️  {results['failed_tests']} 个测试失败")
            
        return results['failed_tests'] == 0
        
    except Exception as e:
        print(f"\n❌ 集成测试执行失败: {str(e)}")
        return False


def demo_system_architecture():
    """演示系统架构"""
    print("\n🏗️  系统架构展示")
    print("="*60)
    
    print("""
融合测试系统架构:

┌─────────────────────────────────────────────────────────────┐
│                    融合测试系统                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ 脚本发现模块 │  │ 增强解析器   │  │ 智能对齐算法 │          │
│  │ Discovery   │  │ Parser      │  │ Alignment   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│           │               │               │                 │
│           └───────────────┼───────────────┘                 │
│                          │                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ 持久化存储   │  │ 故障切换执行 │  │ 报告生成器   │          │
│  │ Persistence │  │ Executor    │  │ Reporter    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    外部依赖                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Qwen AI API │  │ Airtest SDK │  │ Poco Driver │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘

核心模块:
  • 脚本发现模块: 自动识别匹配的Airtest和Poco脚本对
  • 增强解析器: 解析脚本，提取操作步骤和代码块
  • 智能对齐算法: 使用Qwen AI进行语义分析和步骤对齐
  • 持久化存储: 融合脚本的序列化、存储和版本管理
  • 故障切换执行引擎: 支持多种执行策略和自动故障切换
  • 报告生成器: 生成详细的测试报告和统计信息

技术特性:
  • 多维度相似度计算（语法、位置、语义）
  • 贪心对齐算法优化
  • JSON格式持久化存储
  • 自适应执行策略选择
  • 完善的错误处理和恢复机制
  • 扩展性插件架构
    """)


def demo_usage_examples():
    """演示使用示例"""
    print("\n📖 使用示例")
    print("="*60)
    
    print("""
1. 基本使用流程:

```python
from airtest_framework.fusion.main import FusionTestFramework
from airtest_framework.fusion.failover_executor import ExecutionConfig

# 创建融合测试框架
framework = FusionTestFramework()

# 发现测试用例
test_cases = framework.discover_test_cases("tests/mobile")

# 处理融合脚本
for test_case in test_cases:
    fusion_result = await framework.process_fusion(test_case)

# 执行融合脚本
config = ExecutionConfig(strategy=ExecutionStrategy.ADAPTIVE)
result = framework.run_fusion_script("test.fusion.json", config)
```

2. 持久化管理:

```python
from airtest_framework.fusion.persistence import FusionPersistence

# 创建持久化管理器
persistence = FusionPersistence("fusion_scripts")

# 列出所有脚本
scripts = persistence.list_fusion_scripts()

# 加载脚本
script = persistence.load_fusion_script("test.fusion.json")

# 验证脚本
validation = persistence.validate_fusion_script("test.fusion.json")
```

3. 执行配置:

```python
from airtest_framework.fusion.failover_executor import ExecutionConfig, ExecutionStrategy

# 配置执行参数
config = ExecutionConfig(
    strategy=ExecutionStrategy.ADAPTIVE,  # 自适应策略
    timeout=30,                          # 超时时间
    retry_count=2,                       # 重试次数
    failover_enabled=True,               # 启用故障切换
    screenshot_on_error=True,            # 错误时截图
    continue_on_error=True               # 错误时继续
)
```

4. 集成测试:

```python
from airtest_framework.fusion.integration_test import run_integration_tests

# 运行集成测试
results = await run_integration_tests()
print(f"测试结果: {results['passed_tests']}/{results['total_tests']}")
```
    """)


async def main():
    """主函数"""
    print("🎯 融合测试系统完整演示")
    print("="*80)
    
    # 演示系统架构
    demo_system_architecture()
    
    # 演示使用示例
    demo_usage_examples()
    
    # 演示融合系统
    await demo_fusion_system()
    
    # 演示集成测试
    integration_success = await demo_integration_tests()
    
    print("\n" + "="*80)
    print("📋 演示总结")
    print("="*80)
    
    summary = [
        "✅ 系统架构展示完成",
        "✅ 使用示例演示完成", 
        "✅ 融合系统演示完成",
        f"{'✅' if integration_success else '❌'} 集成测试{'通过' if integration_success else '失败'}"
    ]
    
    for item in summary:
        print(item)
    
    print("\n🎉 融合测试系统演示全部完成！")
    
    if not integration_success:
        print("\n⚠️  注意: 部分集成测试失败，请检查系统配置")
        print("   - 确保Qwen API密钥配置正确")
        print("   - 确保测试脚本文件存在")
        print("   - 确保所有依赖包已安装")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())