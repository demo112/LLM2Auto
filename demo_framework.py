#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Airtest Framework 演示脚本
展示框架的主要功能和使用方法
"""

import sys
import time
from pathlib import Path

# 添加框架路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "airtest_framework"))

from airtest_framework import AirtestFramework


def print_banner():
    """打印横幅"""
    print("=" * 80)
    print("🚀 Airtest Framework 功能演示")
    print("=" * 80)
    print()


def print_section(title):
    """打印章节标题"""
    print(f"\n{'=' * 60}")
    print(f"📋 {title}")
    print("=" * 60)


def demo_test_discovery():
    """演示测试发现功能"""
    print_section("测试发现功能")
    
    # 初始化框架
    framework = AirtestFramework()
    
    # 发现测试
    print("🔍 正在发现测试用例...")
    tests = framework.discover_tests("tests/")
    
    print(f"✅ 发现 {len(tests)} 个测试用例")
    
    for i, test in enumerate(tests, 1):
        print(f"\n📋 {i}. {test.name}")
        print(f"   📁 路径: {test.path}")
        print(f"   📱 分类: {test.category}")
        print(f"   ⭐ 优先级: {test.priority}")
        print(f"   🏷️  标签: {', '.join(test.tags)}")
        print(f"   💻 平台: {', '.join(test.platforms)}")
    
    return framework, tests


def demo_test_filtering(framework, tests):
    """演示测试过滤功能"""
    print_section("测试过滤功能")
    
    # 按分类过滤
    print("🔍 按分类过滤 (mobile)...")
    mobile_tests = framework.discovery.filter_tests(tests, category="mobile")
    print(f"✅ 找到 {len(mobile_tests)} 个移动端测试")
    
    # 按优先级过滤
    print("\n🔍 按优先级过滤 (high)...")
    high_priority_tests = framework.discovery.filter_tests(tests, priority="high")
    print(f"✅ 找到 {len(high_priority_tests)} 个高优先级测试")
    
    # 按标签过滤
    print("\n🔍 按标签过滤 (ui_test)...")
    ui_tests = framework.discovery.filter_tests(tests, tags=["ui_test"])
    print(f"✅ 找到 {len(ui_tests)} 个UI测试")


def demo_test_statistics(framework, tests):
    """演示测试统计功能"""
    print_section("测试统计功能")
    
    stats = framework.discovery.get_test_statistics(tests)
    
    print("📊 测试统计信息:")
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


def demo_test_validation(framework, tests):
    """演示测试验证功能"""
    print_section("测试验证功能")
    
    print("🔍 正在验证测试项目...")
    
    valid_count = 0
    invalid_count = 0
    
    for test in tests:
        is_valid, issues = framework.validate_project(test.path)
        status = "✅ 有效" if is_valid else "❌ 无效"
        print(f"📂 {test.name}: {status}")
        
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            
        if issues:
            for issue in issues:
                icon = "⚠️ " if "建议" in issue else "❌"
                print(f"   {icon} {issue}")
    
    print(f"\n📊 验证结果: ✅ {valid_count} 个有效, ❌ {invalid_count} 个无效")


def demo_configuration():
    """演示配置功能"""
    print_section("配置管理功能")
    
    framework = AirtestFramework()
    config = framework.get_config()
    
    print("⚙️ 当前配置:")
    print(f"   📝 项目名称: {config.project_name}")
    print(f"   📦 版本: {config.version}")
    print(f"   📁 日志目录: {config.log_dir}")
    print(f"   📊 报告格式: {config.report.format}")
    print(f"   🔧 最大工作线程: {config.execution.max_workers}")
    print(f"   ⏱️  超时时间: {config.execution.timeout}秒")


def demo_cli_usage():
    """演示命令行使用方法"""
    print_section("命令行使用演示")
    
    print("🖥️ 主要命令行功能:")
    print()
    
    commands = [
        ("列出所有测试", "python3 run_tests.py list"),
        ("详细列出测试", "python3 run_tests.py list --verbose"),
        ("按分类过滤", "python3 run_tests.py list --category mobile"),
        ("按优先级过滤", "python3 run_tests.py list --priority high"),
        ("按标签过滤", "python3 run_tests.py list --tags ui_test,demo"),
        ("显示统计信息", "python3 run_tests.py stats"),
        ("验证测试项目", "python3 run_tests.py validate"),
        ("模拟执行测试", "python3 run_tests.py run --dry-run"),
        ("执行测试并生成报告", "python3 run_tests.py run --report --output report.json"),
        ("并行执行测试", "python3 run_tests.py run --parallel"),
    ]
    
    for i, (desc, cmd) in enumerate(commands, 1):
        print(f"📋 {i:2d}. {desc}")
        print(f"     💻 {cmd}")
        print()


def main():
    """主函数"""
    print_banner()
    
    try:
        # 演示测试发现
        framework, tests = demo_test_discovery()
        
        # 演示测试过滤
        demo_test_filtering(framework, tests)
        
        # 演示测试统计
        demo_test_statistics(framework, tests)
        
        # 演示测试验证
        demo_test_validation(framework, tests)
        
        # 演示配置管理
        demo_configuration()
        
        # 演示命令行使用
        demo_cli_usage()
        
        print_section("演示完成")
        print("🎉 Airtest Framework 功能演示完成！")
        print("📖 更多详细信息请查看 README.md")
        print("🚀 开始使用: python3 run_tests.py --help")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())