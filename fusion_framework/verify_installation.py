#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 Fusion Framework 安装和配置的脚本
"""

import sys
import os
import importlib.util

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    if sys.version_info < (3, 7):
        print("❌ Python版本过低，需要Python 3.7+")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def check_dependencies():
    """检查依赖包"""
    print("\n检查依赖包...")
    required_packages = [
        'airtest',
        'pocoui', 
        'requests',
        'yaml',
        'jinja2',
        'colorama',
        'tqdm'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'pocoui':
                __import__('poco')
            elif package == 'yaml':
                __import__('yaml')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def check_project_structure():
    """检查项目结构"""
    print("\n检查项目结构...")
    
    required_dirs = [
        'src/fusion_framework',
        'src/fusion_framework/core',
        'config',
        'docs',
        'examples',
        'scripts'
    ]
    
    required_files = [
        'src/fusion_framework/__init__.py',
        'src/fusion_framework/core/main.py',
        'src/fusion_framework/core/config.py',
        'config/fusion_config.json',
        'run_fusion_tests.py',
        'setup.py',
        'requirements.txt'
    ]
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查目录
    for dir_path in required_dirs:
        full_path = os.path.join(base_dir, dir_path)
        if os.path.exists(full_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - 目录不存在")
            return False
    
    # 检查文件
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            return False
    
    return True

def check_imports():
    """检查核心模块导入"""
    print("\n检查核心模块导入...")
    
    # 添加src目录到Python路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    try:
        from fusion_framework.core.config import FusionConfig
        print("✅ fusion_framework.core.config")
        
        from fusion_framework.core.main import FusionTestFramework
        print("✅ fusion_framework.core.main")
        
        from fusion_framework.core.discovery import TestCaseDiscovery
        print("✅ fusion_framework.core.discovery")
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def check_config():
    """检查配置文件"""
    print("\n检查配置文件...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, 'config', 'fusion_config.json')
    
    if not os.path.exists(config_file):
        print("❌ 配置文件不存在")
        return False
    
    try:
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ 配置文件格式正确")
        
        # 检查关键配置项
        required_keys = ['qwen_api', 'device', 'logging']
        execution_keys = ['execution_strategy', 'fallback_mode', 'retry', 'timeout']
        
        for key in required_keys:
            if key in config:
                print(f"✅ 配置项: {key}")
            else:
                print(f"❌ 缺少配置项: {key}")
                return False
        
        # 检查execution相关配置
        execution_found = all(key in config for key in execution_keys)
        if execution_found:
            print("✅ 配置项: execution (分散配置)")
        else:
            missing_exec_keys = [key for key in execution_keys if key not in config]
            print(f"❌ 缺少execution配置项: {missing_exec_keys}")
            return False
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Fusion Framework 安装验证")
    print("=" * 50)
    
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("项目结构", check_project_structure),
        ("模块导入", check_imports),
        ("配置文件", check_config)
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有检查通过！Fusion Framework 已正确安装和配置。")
        print("\n可以运行以下命令开始使用:")
        print("  python run_fusion_tests.py --help")
    else:
        print("❌ 部分检查失败，请根据上述提示修复问题。")
        sys.exit(1)

if __name__ == "__main__":
    main()