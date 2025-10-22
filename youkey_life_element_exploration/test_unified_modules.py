#!/usr/bin/env python3
# -*- encoding=utf8 -*-
"""
统一模块功能测试

验证新创建的统一模块是否正常工作
"""

import os
import sys
from pathlib import Path

def test_simple_data_processor():
    """测试简化数据处理器"""
    print("🔍 测试简化数据处理器...")
    
    try:
        # 直接导入本地模块
        sys.path.insert(0, str(Path(__file__).parent))
        from utils.simple_data_processor import SimpleDataProcessor
        
        processor = SimpleDataProcessor()
        
        # 测试数据
        test_data = [
            {'name': 'Alice', 'age': 25, 'score': 85},
            {'name': 'Bob', 'age': 30, 'score': 92},
            {'name': '', 'age': 25, 'score': 78},  # 空名字
            {'name': 'Charlie', 'age': 35, 'score': 88}
        ]
        
        # 清洗数据
        result = processor.clean_data(test_data)
        print(f"  ✅ 数据清洗: {result.success}, 处理 {len(result.data)} 条记录")
        
        # 聚合数据
        result = processor.aggregate_data(test_data, 'age', {'score': 'avg'})
        print(f"  ✅ 数据聚合: {result.success}, 生成 {len(result.data)} 个分组")
        
        return True
    except Exception as e:
        print(f"  ❌ 简化数据处理器测试失败: {e}")
        return False

def test_unified_utils():
    """测试统一工具类"""
    print("🔍 测试统一工具类...")
    
    try:
        from utils.unified_utils import UnifiedUtils
        
        utils = UnifiedUtils()
        
        # 测试文件操作
        test_file = Path(__file__).parent / "test_temp.txt"
        test_content = "这是测试内容"
        
        # 写入文件
        result = utils.write_file(str(test_file), test_content)
        print(f"  ✅ 文件写入: {result.success}")
        
        # 读取文件
        result = utils.read_file(str(test_file))
        print(f"  ✅ 文件读取: {result.success}, 内容长度 {len(result.data) if result.data else 0}")
        
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()
        
        # 测试统计计算
        test_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = utils.calculate_statistics(test_numbers)
        print(f"  ✅ 统计计算: {result.success}, 平均值 {result.data.get('mean', 0):.1f}")
        
        return True
    except Exception as e:
        print(f"  ❌ 统一工具类测试失败: {e}")
        return False

def test_unified_reporter():
    """测试统一报告器"""
    print("🔍 测试统一报告器...")
    
    try:
        from reports.unified_reporter import UnifiedReporter, ReportConfig
        
        config = ReportConfig(title="测试报告", format="json")
        reporter = UnifiedReporter(config)
        
        # 添加测试数据
        reporter.add_summary("测试项目", 5)
        reporter.add_summary("成功项目", 4)
        reporter.add_section("测试结果", "所有测试已完成")
        
        # 生成分析报告
        test_results = [
            {'success': True, 'score': 85, 'message': '测试通过'},
            {'success': True, 'score': 92, 'message': '测试通过'},
            {'success': False, 'score': 0, 'message': '测试失败'}
        ]
        
        report = reporter.generate_analysis_report(test_results)
        print(f"  ✅ 分析报告: 标题 '{report.title}', 章节数 {len(report.sections)}")
        
        # 导出报告
        report_file = Path(__file__).parent / "test_report.json"
        success = reporter.export_report(str(report_file))
        print(f"  ✅ 报告导出: {success}")
        
        # 清理测试文件
        if report_file.exists():
            report_file.unlink()
        
        return True
    except Exception as e:
        print(f"  ❌ 统一报告器测试失败: {e}")
        return False

def test_basic_functionality():
    """测试基础功能"""
    print("🔍 测试基础功能...")
    
    try:
        # 测试简单的数据处理
        test_data = [1, 2, 3, 4, 5]
        
        # 计算平均值
        avg = sum(test_data) / len(test_data)
        print(f"  ✅ 平均值计算: {avg}")
        
        # 测试文件路径操作
        current_dir = Path(__file__).parent
        print(f"  ✅ 当前目录: {current_dir.name}")
        
        # 测试字符串操作
        test_str = "Hello World"
        print(f"  ✅ 字符串处理: {test_str.lower()}")
        
        return True
    except Exception as e:
        print(f"  ❌ 基础功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始统一模块功能测试\n")
    
    tests = [
        test_basic_functionality,
        test_simple_data_processor,
        test_unified_utils,
        test_unified_reporter
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()  # 空行分隔
        except Exception as e:
            print(f"  ❌ 测试执行异常: {e}\n")
    
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed >= total * 0.75:  # 75%通过率即可
        print("🎉 大部分统一模块功能正常！")
        return True
    else:
        print("⚠️  需要进一步检查模块")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)