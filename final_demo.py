#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Airtest 自动化测试框架 - 最终演示
使用真实的 test_case_demo.air 项目展示框架的完整功能
"""

import sys
from pathlib import Path

# 添加框架路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "airtest_framework"))

from airtest_framework import AirtestFramework


def print_separator(title: str):
    """打印分隔符"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")


def main():
    """Airtest 框架完整功能演示"""
    print_separator("Airtest 自动化测试框架 - 完整功能演示")
    
    try:
        # 1. 框架初始化
        print("\n📦 1. 框架初始化...")
        framework = AirtestFramework()
        print("✅ 框架初始化成功")
        
        # 2. 测试发现
        print_separator("2. 测试项目发现")
        tests = framework.discover_tests("tests/")
        
        if not tests:
            print("❌ 没有发现任何测试项目")
            return
        
        print(f"✅ 发现 {len(tests)} 个测试项目")
        
        # 3. 详细信息展示
        print_separator("3. 测试项目详细信息")
        for i, test in enumerate(tests, 1):
            print(f"\n📋 项目 {i}: {test.name}")
            print(f"   📁 路径: {test.path}")
            print(f"   📱 分类: {test.category}")
            print(f"   ⭐ 优先级: {test.priority}")
            print(f"   🏷️  标签: {', '.join(test.tags) if test.tags else '无'}")
            print(f"   💻 平台: {', '.join(test.platforms) if test.platforms else '无'}")
            print(f"   🧪 测试类型: {test.test_type}")
            print(f"   👤 作者: {test.author}")
            print(f"   📝 版本: {test.version}")
            print(f"   ⏱️  超时: {test.timeout}秒")
            print(f"   🔄 重试次数: {test.retry_count}")
            print(f"   📄 描述: {test.description if test.description else '无描述'}")
            
            # 显示设备要求
            if test.device_requirements:
                print(f"   📱 设备要求:")
                for key, value in test.device_requirements.items():
                    print(f"      - {key}: {value}")
            
            # 显示执行配置
            if test.execution_config:
                print(f"   ⚙️  执行配置:")
                for key, value in test.execution_config.items():
                    print(f"      - {key}: {value}")
        
        # 4. 项目验证
        print_separator("4. 项目结构验证")
        for test in tests:
            is_valid, issues = framework.validate_project(test.path)
            status = "✅ 有效" if is_valid else "❌ 无效"
            print(f"📂 {test.name}: {status}")
            
            if issues:
                for issue in issues:
                    icon = "⚠️ " if "建议" in issue else "❌"
                    print(f"   {icon} {issue}")
        
        # 5. 项目文件分析
        print_separator("5. 项目文件分析")
        test_case_demo = tests[0]  # 我们知道只有一个项目
        project_path = Path(test_case_demo.path)
        
        print(f"📂 项目路径: {project_path}")
        print(f"📁 项目目录: {project_path.name}")
        
        # 统计文件类型
        files = list(project_path.iterdir())
        py_files = [f for f in files if f.suffix == '.py']
        png_files = [f for f in files if f.suffix == '.png']
        yaml_files = [f for f in files if f.suffix in ['.yaml', '.yml']]
        
        print(f"\n📊 文件统计:")
        print(f"   🐍 Python 脚本: {len(py_files)} 个")
        print(f"   🖼️  图片模板: {len(png_files)} 个")
        print(f"   📋 配置文件: {len(yaml_files)} 个")
        print(f"   📄 总文件数: {len(files)} 个")
        
        # 显示文件列表
        print(f"\n📄 文件列表:")
        for file_path in sorted(files):
            if file_path.is_file():
                size = file_path.stat().st_size
                icon = "🐍" if file_path.suffix == '.py' else "🖼️" if file_path.suffix == '.png' else "📋" if file_path.suffix in ['.yaml', '.yml'] else "📄"
                print(f"   {icon} {file_path.name} ({size:,} bytes)")
        
        # 6. 测试过滤演示
        print_separator("6. 测试过滤功能演示")
        
        # 按优先级过滤
        high_priority_tests = framework.discovery.filter_tests(tests, priority="high")
        print(f"🔥 高优先级测试: {len(high_priority_tests)} 个")
        
        # 按平台过滤
        android_tests = framework.discovery.filter_tests(tests, platforms=["android"])
        print(f"📱 Android 测试: {len(android_tests)} 个")
        
        # 按标签过滤
        ui_tests = framework.discovery.filter_tests(tests, tags=["ui_test"])
        print(f"🖱️  UI 测试: {len(ui_tests)} 个")
        
        # 按分类过滤
        mobile_tests = framework.discovery.filter_tests(tests, category="mobile")
        print(f"📱 移动端测试: {len(mobile_tests)} 个")
        
        # 7. 测试统计
        print_separator("7. 测试统计信息")
        stats = framework.discovery.get_test_statistics(tests)
        
        print(f"📊 统计概览:")
        print(f"   📄 总测试数: {stats['total_tests']}")
        print(f"   📱 分类分布: {dict(stats['by_category'])}")
        print(f"   ⭐ 优先级分布: {dict(stats['by_priority'])}")
        print(f"   💻 平台分布: {dict(stats['by_platform'])}")
        print(f"   🧪 类型分布: {dict(stats['by_type'])}")
        print(f"   🏷️  标签分布: {dict(stats['by_tags'])}")
        
        # 8. 框架配置信息
        print_separator("8. 框架配置信息")
        config = framework.config_manager.get_config()
        
        print(f"⚙️  框架配置:")
        print(f"   📝 项目名称: {config.project_name}")
        print(f"   📝 版本: {config.version}")
        print(f"   📁 日志目录: {config.log_dir}")
        print(f"   📁 临时目录: {config.temp_dir}")
        print(f"   📊 报告格式: {config.report.format}")
        print(f"   📊 报告目录: {config.report.output_dir}")
        print(f"   📸 截图设置: {'启用' if config.report.include_screenshots else '禁用'}")
        print(f"   📝 日志级别: {config.execution.log_level}")
        print(f"   🔄 重试次数: {config.execution.retry_count}")
        print(f"   ⏱️  超时时间: {config.execution.timeout}秒")
        
        # 9. 成功总结
        print_separator("9. 演示完成")
        print("🎉 Airtest 自动化测试框架演示成功完成！")
        print("\n✨ 框架特性总结:")
        print("   🔍 智能测试发现 - 自动识别 .air 项目")
        print("   📋 元数据管理 - 支持 YAML 配置文件")
        print("   🔧 项目验证 - 检查项目结构完整性")
        print("   🎯 灵活过滤 - 支持多维度测试筛选")
        print("   📊 统计分析 - 提供详细的测试统计")
        print("   ⚙️  配置管理 - 灵活的配置系统")
        print("   📝 日志记录 - 完整的操作日志")
        
        print(f"\n🚀 真实项目 '{test_case_demo.name}' 已成功集成到框架中！")
        print("   该项目包含移动应用UI自动化测试，演示了滑动和点击操作。")
        print("   框架能够完整识别项目结构、解析元数据并提供管理功能。")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()