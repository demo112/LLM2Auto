#!/usr/bin/env python3
# -*- encoding=utf8 -*-
"""
测试优化后的脚本发现逻辑

验证新增的功能：
1. 改进的脚本类型检测
2. 脚本质量评估
3. 智能用例匹配
4. 详细的发现结果展示
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from airtest_framework.fusion.discovery import TestCaseDiscovery


def main():
    """主函数"""
    print("🔍 测试优化后的脚本发现逻辑")
    print("=" * 60)
    
    # 初始化发现器
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        print(f"❌ 测试目录不存在: {tests_dir}")
        return
    
    discovery = TestCaseDiscovery(str(tests_dir))
    
    print(f"📂 扫描测试目录: {tests_dir}")
    print()
    
    # 发现测试用例
    try:
        cases = discovery.discover_test_cases()
        
        print(f"✅ 发现完成，共找到 {len(cases)} 个用例")
        print()
        
        # 打印详细的发现结果
        discovery.print_discovery_summary()
        
        # 测试特定功能
        print("\n" + "=" * 60)
        print("🧪 功能测试")
        print("=" * 60)
        
        # 测试配对用例
        paired_cases = discovery.get_paired_cases()
        if paired_cases:
            print(f"\n✅ 配对用例测试:")
            for case in paired_cases:
                print(f"  - {case.name}: Airtest + Poco")
                
                # 显示质量对比
                if case.airtest_quality and case.poco_quality:
                    airtest_score = case.airtest_quality.score
                    poco_score = case.poco_quality.score
                    better = "Airtest" if airtest_score > poco_score else "Poco"
                    print(f"    质量对比: Airtest({airtest_score:.1f}) vs Poco({poco_score:.1f}) - {better}更优")
        
        # 测试单一实现用例
        single_cases = discovery.get_single_cases()
        if single_cases:
            print(f"\n📄 单一实现用例:")
            for case in single_cases:
                impl_type = "Airtest" if case.airtest_path else "Poco"
                quality = case.airtest_quality or case.poco_quality
                print(f"  - {case.name} ({impl_type}): 质量分数 {quality.score:.1f}")
        
        # 测试名称标准化
        print(f"\n🔧 名称标准化测试:")
        test_names = [
            "test_case_demo_poco",
            "test_case_demo_airtest", 
            "login_test_v2",
            "payment_demo_1"
        ]
        
        for name in test_names:
            normalized = discovery._normalize_case_name(name)
            print(f"  {name} -> {normalized}")
        
        # 测试相似度计算
        print(f"\n📊 相似度计算测试:")
        similarity_tests = [
            ("test_case_demo", "test_case_demo_poco"),
            ("login_test", "login_test_v2"),
            ("payment", "payment_demo"),
            ("completely_different", "another_name")
        ]
        
        for name1, name2 in similarity_tests:
            similarity = discovery._calculate_similarity(name1, name2)
            print(f"  '{name1}' vs '{name2}': {similarity:.2f}")
        
        print(f"\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 发现过程出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()