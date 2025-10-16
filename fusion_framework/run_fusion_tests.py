#!/usr/bin/env python3
# -*- encoding=utf8 -*-
"""
融合测试框架快速启动脚本

使用示例:
    python run_fusion_tests.py                    # 运行所有测试
    python run_fusion_tests.py --filter "*demo*"  # 运行包含demo的测试
    python run_fusion_tests.py --debug            # 调试模式运行
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from fusion_framework.cli.main import FusionTestFramework
from fusion_framework.core.config import load_config, validate_config


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='融合测试框架快速启动脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                           # 运行所有测试
  %(prog)s --filter "*demo*"         # 运行包含demo的测试
  %(prog)s --test-root tests/mobile  # 指定测试目录
  %(prog)s --debug                   # 调试模式运行
  %(prog)s --config my_config.json   # 使用自定义配置
        """
    )
    
    parser.add_argument(
        '--config', '-c', 
        help='配置文件路径 (默认: fusion_config.json)'
    )
    parser.add_argument(
        '--test-root', '-t', 
        help='测试根目录 (默认: tests)'
    )
    parser.add_argument(
        '--filter', '-f', 
        help='用例过滤器，支持通配符 (例如: "*demo*", "test_case_*")'
    )
    parser.add_argument(
        '--title', 
        help='报告标题', 
        default='融合测试执行报告'
    )
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='启用调试模式'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true', 
        help='详细输出'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='只发现测试用例，不执行'
    )
    
    args = parser.parse_args()
    
    try:
        print("=" * 60)
        print("融合测试框架")
        print("=" * 60)
        
        # 加载配置
        print(f"加载配置文件: {args.config or '默认配置'}")
        config = load_config(args.config)
        
        # 应用命令行参数覆盖配置
        if args.debug:
            config.debug_mode = True
            config.logging.level = 'DEBUG'
            print("启用调试模式")
        
        if args.verbose:
            config.verbose_logging = True
            print("启用详细输出")
        
        if args.test_root:
            config.test_root_dir = args.test_root
            print(f"测试根目录: {args.test_root}")
        
        # 验证配置
        print("验证配置...")
        if not validate_config(config):
            print("配置验证失败，请检查配置文件")
            return 1
        
        # 创建框架实例
        print("初始化融合测试框架...")
        framework = FusionTestFramework(config)
        
        # 发现测试用例
        print(f"发现测试用例 (根目录: {config.test_root_dir})...")
        test_cases = framework.discover_test_cases()
        
        if not test_cases:
            print("❌ 没有发现任何测试用例")
            print(f"请检查测试目录: {config.test_root_dir}")
            return 1
        
        # 应用过滤器
        if args.filter:
            import fnmatch
            filtered_cases = [
                case for case in test_cases 
                if fnmatch.fnmatch(case.name, args.filter)
            ]
            print(f"应用过滤器 '{args.filter}': {len(test_cases)} -> {len(filtered_cases)} 个用例")
            test_cases = filtered_cases
        
        if not test_cases:
            print("❌ 过滤后没有剩余的测试用例")
            return 1
        
        # 打印发现的测试用例
        print(f"\n发现的测试用例 ({len(test_cases)} 个):")
        for i, case in enumerate(test_cases, 1):
            implementations = []
            if hasattr(case, 'airtest_path') and case.airtest_path:
                implementations.append("Airtest")
            if hasattr(case, 'poco_path') and case.poco_path:
                implementations.append("Poco")
            
            impl_str = " + ".join(implementations) if implementations else "未知"
            print(f"  {i:2d}. {case.name} ({impl_str})")
        
        # 如果是dry-run模式，只显示发现的用例
        if args.dry_run:
            print("\n🔍 Dry-run 模式，仅发现测试用例，不执行")
            return 0
        
        print(f"\n开始执行测试...")
        print("-" * 60)
        
        # 执行测试用例
        results = framework.run_test_cases(test_cases)
        
        if not results:
            print("❌ 没有执行任何测试用例")
            return 1
        
        print("-" * 60)
        
        # 生成报告
        print("生成测试报告...")
        report_paths = framework.generate_report(results, args.title)
        
        print("\n📊 测试报告已生成:")
        for report_type, path in report_paths.items():
            print(f"  {report_type.upper()}: {path}")
        
        # 计算总体结果
        total_cases = len(results)
        successful_cases = sum(
            1 for r in results 
            if r.overall_result.value in ['success', 'fallback']
        )
        
        print(f"\n✅ 测试完成: {successful_cases}/{total_cases} 用例成功")
        
        # 如果有HTML报告，提示用户打开
        if 'html' in report_paths:
            html_path = Path(report_paths['html']).absolute()
            print(f"\n💡 在浏览器中查看详细报告:")
            print(f"   file://{html_path}")
        
        return 0 if successful_cases == total_cases else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        return 130
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        
        if args.debug:
            import traceback
            print("\n调试信息:")
            traceback.print_exc()
        
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)