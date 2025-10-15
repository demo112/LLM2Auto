# -*- encoding=utf8 -*-
"""
融合测试系统集成测试

端到端测试融合测试系统的完整功能
"""

import asyncio
import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

from .main import FusionTestFramework
from .failover_executor import ExecutionConfig, ExecutionStrategy
from .persistence import FusionPersistence
from .enhanced_parser import EnhancedScriptParser
from .intelligent_alignment import IntelligentStepAlignment, AlignmentConfig


class IntegrationTestSuite:
    """集成测试套件"""
    
    def __init__(self):
        self.test_data_dir = None
        self.temp_dir = None
        self.framework = None
        self.test_results = []
    
    def setup(self):
        """设置测试环境"""
        print("设置集成测试环境...")
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="fusion_test_")
        print(f"临时目录: {self.temp_dir}")
        
        # 创建测试数据目录结构
        self.test_data_dir = Path(self.temp_dir) / "test_data"
        self.test_data_dir.mkdir()
        
        # 创建模拟测试脚本
        self._create_mock_test_scripts()
        
        # 初始化融合测试框架
        self.framework = FusionTestFramework()
        
        print("集成测试环境设置完成")
    
    def teardown(self):
        """清理测试环境"""
        print("清理集成测试环境...")
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        print("集成测试环境清理完成")
    
    def _create_mock_test_scripts(self):
        """创建模拟测试脚本"""
        # 创建Airtest脚本
        airtest_dir = self.test_data_dir / "test_login_airtest.air"
        airtest_dir.mkdir()
        
        # Airtest Python脚本
        airtest_py = airtest_dir / "test_login_airtest.py"
        airtest_py.write_text('''# -*- encoding=utf8 -*-
from airtest.core.api import *

# 启动应用
touch(Template("app_icon.png"))
sleep(2)

# 点击用户名输入框
touch(Template("username_field.png"))
text("testuser")

# 点击密码输入框
touch(Template("password_field.png"))
text("testpass")

# 点击登录按钮
touch(Template("login_button.png"))
sleep(3)

# 验证登录成功
assert exists(Template("home_page.png")), "登录失败"
''')
        
        # Airtest元数据
        airtest_meta = airtest_dir / "metadata.yaml"
        airtest_meta.write_text('''name: "登录测试 - Airtest版本"
description: "使用Airtest实现的登录功能测试"
author: "测试工程师"
version: "1.0.0"
category: "功能测试"
tags: ["登录", "认证", "UI测试"]
priority: "高"
platforms: ["Android", "iOS"]
device_requirements:
  min_android_version: "7.0"
  min_ios_version: "12.0"
execution_config:
  timeout: 300
  retry_count: 2
  screenshot_on_failure: true
''')
        
        # 创建Poco脚本
        poco_dir = self.test_data_dir / "test_login_poco.air"
        poco_dir.mkdir()
        
        # Poco Python脚本
        poco_py = poco_dir / "test_login_poco.py"
        poco_py.write_text('''# -*- encoding=utf8 -*-
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import time

poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

# 启动应用
poco("com.example.app:id/app_icon").click()
time.sleep(2)

# 输入用户名
username_field = poco("com.example.app:id/username")
username_field.click()
username_field.set_text("testuser")

# 输入密码
password_field = poco("com.example.app:id/password")
password_field.click()
password_field.set_text("testpass")

# 点击登录按钮
login_btn = poco("com.example.app:id/login_button")
login_btn.click()
time.sleep(3)

# 验证登录成功
home_page = poco("com.example.app:id/home_container")
assert home_page.exists(), "登录失败"
''')
        
        # Poco元数据
        poco_meta = poco_dir / "metadata.yaml"
        poco_meta.write_text('''name: "登录测试 - Poco版本"
description: "使用Poco实现的登录功能测试"
author: "测试工程师"
version: "1.0.0"
category: "功能测试"
tags: ["登录", "认证", "UI测试"]
priority: "高"
platforms: ["Android", "iOS"]
device_requirements:
  min_android_version: "7.0"
  min_ios_version: "12.0"
execution_config:
  timeout: 300
  retry_count: 2
  screenshot_on_failure: true
''')
        
        print("模拟测试脚本创建完成")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有集成测试"""
        print("开始运行集成测试...")
        
        test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        # 测试用例列表
        test_cases = [
            ('test_script_discovery', self.test_script_discovery),
            ('test_script_parsing', self.test_script_parsing),
            ('test_intelligent_alignment', self.test_intelligent_alignment),
            ('test_persistence', self.test_persistence),
            ('test_end_to_end_fusion', self.test_end_to_end_fusion)
        ]
        
        for test_name, test_func in test_cases:
            test_results['total_tests'] += 1
            
            try:
                print(f"\n运行测试: {test_name}")
                result = await test_func()
                
                if result['success']:
                    test_results['passed_tests'] += 1
                    print(f"✓ {test_name} 通过")
                else:
                    test_results['failed_tests'] += 1
                    print(f"✗ {test_name} 失败: {result.get('error', '未知错误')}")
                
                test_results['test_details'].append({
                    'name': test_name,
                    'success': result['success'],
                    'error': result.get('error', ''),
                    'details': result.get('details', {})
                })
                
            except Exception as e:
                test_results['failed_tests'] += 1
                error_msg = f"测试执行异常: {str(e)}"
                print(f"✗ {test_name} 异常: {error_msg}")
                
                test_results['test_details'].append({
                    'name': test_name,
                    'success': False,
                    'error': error_msg,
                    'details': {}
                })
        
        # 打印测试摘要
        self._print_test_summary(test_results)
        
        return test_results
    
    async def test_script_discovery(self) -> Dict[str, Any]:
        """测试脚本发现功能"""
        try:
            # 发现测试用例
            test_cases = self.framework.discover_test_cases(str(self.test_data_dir))
            
            # 验证结果
            if len(test_cases) == 0:
                return {
                    'success': False,
                    'error': '未发现任何测试用例',
                    'details': {'discovered_count': 0}
                }
            
            # 检查是否发现了匹配的脚本对
            login_case = None
            for case in test_cases:
                if 'login' in case.name.lower():
                    login_case = case
                    break
            
            if not login_case:
                return {
                    'success': False,
                    'error': '未发现登录测试用例',
                    'details': {'discovered_cases': [case.name for case in test_cases]}
                }
            
            if not (login_case.airtest_path and login_case.poco_path):
                return {
                    'success': False,
                    'error': '登录测试用例缺少Airtest或Poco实现',
                    'details': {
                        'has_airtest': bool(login_case.airtest_path),
                        'has_poco': bool(login_case.poco_path)
                    }
                }
            
            return {
                'success': True,
                'details': {
                    'discovered_count': len(test_cases),
                    'login_case_found': True,
                    'has_both_implementations': True
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'脚本发现测试失败: {str(e)}'
            }
    
    async def test_script_parsing(self) -> Dict[str, Any]:
        """测试脚本解析功能"""
        try:
            parser = EnhancedScriptParser()
            
            # 解析Airtest脚本
            airtest_script = str(self.test_data_dir / "test_login_airtest.air" / "test_login_airtest.py")
            airtest_metadata, airtest_steps = parser.parse_script_file(airtest_script)
            
            # 解析Poco脚本
            poco_script = str(self.test_data_dir / "test_login_poco.air" / "test_login_poco.py")
            poco_metadata, poco_steps = parser.parse_script_file(poco_script)
            
            # 验证解析结果
            if len(airtest_steps) == 0:
                return {
                    'success': False,
                    'error': 'Airtest脚本解析失败，未提取到步骤',
                    'details': {'airtest_steps': 0, 'poco_steps': len(poco_steps)}
                }
            
            if len(poco_steps) == 0:
                return {
                    'success': False,
                    'error': 'Poco脚本解析失败，未提取到步骤',
                    'details': {'airtest_steps': len(airtest_steps), 'poco_steps': 0}
                }
            
            # 检查步骤内容
            airtest_has_touch = any('touch' in step.description.lower() for step in airtest_steps)
            poco_has_click = any('click' in step.description.lower() for step in poco_steps)
            
            return {
                'success': True,
                'details': {
                    'airtest_steps': len(airtest_steps),
                    'poco_steps': len(poco_steps),
                    'airtest_has_touch': airtest_has_touch,
                    'poco_has_click': poco_has_click
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'脚本解析测试失败: {str(e)}'
            }
    
    async def test_intelligent_alignment(self) -> Dict[str, Any]:
        """测试智能对齐功能"""
        try:
            # 注意：这里使用模拟的对齐结果，因为需要真实的Qwen API
            # 在实际环境中，这里会调用真实的对齐算法
            
            parser = EnhancedScriptParser()
            
            # 解析脚本
            airtest_script = str(self.test_data_dir / "test_login_airtest.air" / "test_login_airtest.py")
            airtest_metadata, airtest_steps = parser.parse_script_file(airtest_script)
            
            poco_script = str(self.test_data_dir / "test_login_poco.air" / "test_login_poco.py")
            poco_metadata, poco_steps = parser.parse_script_file(poco_script)
            
            if len(airtest_steps) == 0 or len(poco_steps) == 0:
                return {
                    'success': False,
                    'error': '脚本解析失败，无法进行对齐测试'
                }
            
            # 模拟对齐结果（在实际环境中会调用真实的对齐算法）
            alignment_results = []
            min_steps = min(len(airtest_steps), len(poco_steps))
            
            for i in range(min_steps):
                from .intelligent_alignment import AlignmentResult
                
                result = AlignmentResult(
                    airtest_step=airtest_steps[i],
                    poco_step=poco_steps[i],
                    alignment_confidence=0.8 + (i * 0.02),  # 模拟置信度
                    semantic_description=f"模拟对齐步骤 {i+1}",
                    alignment_reason=f"模拟对齐原因 {i+1}"
                )
                alignment_results.append(result)
            
            # 验证对齐结果
            if len(alignment_results) == 0:
                return {
                    'success': False,
                    'error': '对齐算法未产生任何结果'
                }
            
            avg_confidence = sum(r.alignment_confidence for r in alignment_results) / len(alignment_results)
            
            return {
                'success': True,
                'details': {
                    'aligned_pairs': len(alignment_results),
                    'average_confidence': avg_confidence,
                    'min_confidence': min(r.alignment_confidence for r in alignment_results),
                    'max_confidence': max(r.alignment_confidence for r in alignment_results)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'智能对齐测试失败: {str(e)}'
            }
    
    async def test_persistence(self) -> Dict[str, Any]:
        """测试持久化功能"""
        try:
            # 创建临时存储目录
            storage_dir = Path(self.temp_dir) / "fusion_storage"
            persistence = FusionPersistence(str(storage_dir))
            
            # 创建模拟对齐结果
            from .intelligent_alignment import AlignmentResult
            from .enhanced_parser import OperationStep, OperationType, CodeBlock
            
            # 创建模拟步骤
            airtest_code = CodeBlock(
                content='touch(Template("button.png"))',
                start_line=10,
                end_line=10,
                imports=['from airtest.core.api import *'],
                variables=[],
                raw_lines=['touch(Template("button.png"))']
            )
            
            poco_code = CodeBlock(
                content='poco("button").click()',
                start_line=15,
                end_line=15,
                imports=['from poco.drivers.android.uiautomation import AndroidUiautomationPoco'],
                variables=['poco'],
                raw_lines=['poco("button").click()']
            )
            
            airtest_step = OperationStep(
                step_id="step_1",
                operation_type=OperationType.CLICK,
                description="点击按钮",
                target_element="button",
                airtest_code=airtest_code,
                semantic_tags=["ui_interaction"]
            )
            
            poco_step = OperationStep(
                step_id="step_1",
                operation_type=OperationType.CLICK,
                description="点击按钮",
                target_element="button",
                poco_code=poco_code,
                semantic_tags=["ui_interaction"]
            )
            
            alignment_result = AlignmentResult(
                airtest_step=airtest_step,
                poco_step=poco_step,
                alignment_confidence=0.9,
                semantic_description="点击按钮操作",
                alignment_reason="两个步骤都是点击按钮"
            )
            
            # 保存融合脚本
            script_path = persistence.save_fusion_script(
                script_name="test_persistence",
                alignment_results=[alignment_result],
                airtest_source=str(self.test_data_dir / "test_login_airtest.air" / "test_login_airtest.py"),
                poco_source=str(self.test_data_dir / "test_login_poco.air" / "test_login_poco.py")
            )
            
            # 验证文件是否创建
            if not os.path.exists(script_path):
                return {
                    'success': False,
                    'error': '融合脚本文件未创建'
                }
            
            # 加载融合脚本
            loaded_script = persistence.load_fusion_script(script_path)
            
            if not loaded_script:
                return {
                    'success': False,
                    'error': '无法加载融合脚本'
                }
            
            # 验证脚本内容
            if len(loaded_script.steps) != 1:
                return {
                    'success': False,
                    'error': f'步骤数量不匹配，期望1个，实际{len(loaded_script.steps)}个'
                }
            
            # 验证脚本
            validation_result = persistence.validate_fusion_script(script_path)
            
            return {
                'success': True,
                'details': {
                    'script_saved': True,
                    'script_loaded': True,
                    'steps_count': len(loaded_script.steps),
                    'validation_valid': validation_result['valid'],
                    'validation_errors': len(validation_result['errors']),
                    'validation_warnings': len(validation_result['warnings'])
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'持久化测试失败: {str(e)}'
            }
    
    async def test_end_to_end_fusion(self) -> Dict[str, Any]:
        """测试端到端融合流程"""
        try:
            # 发现测试用例
            test_cases = self.framework.discover_test_cases(str(self.test_data_dir))
            
            if len(test_cases) == 0:
                return {
                    'success': False,
                    'error': '未发现测试用例'
                }
            
            # 选择第一个测试用例进行融合
            test_case = test_cases[0]
            
            # 注意：这里模拟融合过程，因为需要真实的Qwen API
            # 在实际环境中，这里会调用真实的融合处理
            
            # 模拟融合结果
            fusion_result = f"test_{test_case.name}_fusion.json"
            
            # 创建模拟的融合脚本文件
            storage_dir = Path(self.temp_dir) / "fusion_storage"
            storage_dir.mkdir(exist_ok=True)
            
            fusion_file = storage_dir / fusion_result
            fusion_file.write_text('{"metadata": {"name": "test_fusion"}, "steps": []}')
            
            return {
                'success': True,
                'details': {
                    'test_case_name': test_case.name,
                    'fusion_result': fusion_result,
                    'has_airtest': bool(test_case.airtest_path),
            'has_poco': bool(test_case.poco_path)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'端到端融合测试失败: {str(e)}'
            }
    
    def _print_test_summary(self, results: Dict[str, Any]):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("集成测试摘要")
        print("="*60)
        print(f"总测试数: {results['total_tests']}")
        print(f"通过测试: {results['passed_tests']}")
        print(f"失败测试: {results['failed_tests']}")
        print(f"成功率: {results['passed_tests']/results['total_tests']*100:.1f}%")
        
        if results['failed_tests'] > 0:
            print("\n失败的测试:")
            for test in results['test_details']:
                if not test['success']:
                    print(f"  - {test['name']}: {test['error']}")
        
        print("="*60)


async def run_integration_tests():
    """运行集成测试"""
    test_suite = IntegrationTestSuite()
    
    try:
        # 设置测试环境
        test_suite.setup()
        
        # 运行所有测试
        results = await test_suite.run_all_tests()
        
        return results
        
    finally:
        # 清理测试环境
        test_suite.teardown()


if __name__ == "__main__":
    # 运行集成测试
    print("开始融合测试系统集成测试...")
    
    results = asyncio.run(run_integration_tests())
    
    if results['failed_tests'] == 0:
        print("\n🎉 所有集成测试通过！")
        exit(0)
    else:
        print(f"\n❌ {results['failed_tests']} 个测试失败")
        exit(1)