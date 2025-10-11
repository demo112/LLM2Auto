# -*- encoding=utf8 -*-
"""
测试用例自动注册机制
"""

import os
import sys
import importlib
import inspect
import logging
from typing import Dict, List, Any, Type, Callable, Optional
from dataclasses import dataclass
from pathlib import Path

from .discovery import TestMetadata


@dataclass
class TestCase:
    """测试用例信息"""
    name: str
    description: str
    test_function: Callable
    test_class: Optional[Type] = None
    metadata: Optional[TestMetadata] = None
    priority: str = "medium"
    tags: List[str] = None
    category: str = "general"
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TestRegistry:
    """测试用例注册器"""
    
    def __init__(self):
        self._test_cases: Dict[str, TestCase] = {}
        self._test_suites: Dict[str, List[str]] = {}
        self._categories: Dict[str, List[str]] = {}
        self._tags: Dict[str, List[str]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_test(self, name: str, test_function: Callable, 
                     description: str = "", priority: str = "medium",
                     tags: List[str] = None, category: str = "general",
                     test_class: Type = None, metadata: TestMetadata = None) -> None:
        """
        注册测试用例
        
        Args:
            name: 测试名称
            test_function: 测试函数
            description: 测试描述
            priority: 优先级
            tags: 标签列表
            category: 分类
            test_class: 测试类
            metadata: 元数据
        """
        if name in self._test_cases:
            self.logger.warning(f"测试用例已存在，将被覆盖: {name}")
        
        test_case = TestCase(
            name=name,
            description=description,
            test_function=test_function,
            test_class=test_class,
            metadata=metadata,
            priority=priority,
            tags=tags or [],
            category=category
        )
        
        self._test_cases[name] = test_case
        
        # 更新分类索引
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)
        
        # 更新标签索引
        for tag in test_case.tags:
            if tag not in self._tags:
                self._tags[tag] = []
            self._tags[tag].append(name)
        
        self.logger.debug(f"注册测试用例: {name}")
    
    def register_test_suite(self, suite_name: str, test_names: List[str]) -> None:
        """
        注册测试套件
        
        Args:
            suite_name: 套件名称
            test_names: 测试名称列表
        """
        # 验证测试用例是否存在
        valid_tests = []
        for test_name in test_names:
            if test_name in self._test_cases:
                valid_tests.append(test_name)
            else:
                self.logger.warning(f"测试套件 {suite_name} 中的测试用例不存在: {test_name}")
        
        self._test_suites[suite_name] = valid_tests
        self.logger.debug(f"注册测试套件: {suite_name} ({len(valid_tests)} 个测试)")
    
    def get_test_case(self, name: str) -> Optional[TestCase]:
        """获取测试用例"""
        return self._test_cases.get(name)
    
    def get_test_suite(self, suite_name: str) -> List[TestCase]:
        """获取测试套件"""
        test_names = self._test_suites.get(suite_name, [])
        return [self._test_cases[name] for name in test_names if name in self._test_cases]
    
    def get_tests_by_category(self, category: str) -> List[TestCase]:
        """根据分类获取测试用例"""
        test_names = self._categories.get(category, [])
        return [self._test_cases[name] for name in test_names if name in self._test_cases]
    
    def get_tests_by_tag(self, tag: str) -> List[TestCase]:
        """根据标签获取测试用例"""
        test_names = self._tags.get(tag, [])
        return [self._test_cases[name] for name in test_names if name in self._test_cases]
    
    def get_tests_by_priority(self, priority: str) -> List[TestCase]:
        """根据优先级获取测试用例"""
        return [test for test in self._test_cases.values() if test.priority == priority]
    
    def get_all_tests(self) -> List[TestCase]:
        """获取所有测试用例"""
        return list(self._test_cases.values())
    
    def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        return list(self._categories.keys())
    
    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        return list(self._tags.keys())
    
    def get_all_suites(self) -> List[str]:
        """获取所有测试套件"""
        return list(self._test_suites.keys())
    
    def filter_tests(self, category: str = None, tags: List[str] = None, 
                    priority: str = None, name_pattern: str = None) -> List[TestCase]:
        """
        过滤测试用例
        
        Args:
            category: 分类过滤
            tags: 标签过滤（包含任一标签）
            priority: 优先级过滤
            name_pattern: 名称模式过滤
            
        Returns:
            List[TestCase]: 过滤后的测试用例列表
        """
        tests = self.get_all_tests()
        
        if category:
            tests = [test for test in tests if test.category == category]
        
        if tags:
            tests = [test for test in tests if any(tag in test.tags for tag in tags)]
        
        if priority:
            tests = [test for test in tests if test.priority == priority]
        
        if name_pattern:
            import re
            pattern = re.compile(name_pattern, re.IGNORECASE)
            tests = [test for test in tests if pattern.search(test.name)]
        
        return tests
    
    def clear(self):
        """清空注册器"""
        self._test_cases.clear()
        self._test_suites.clear()
        self._categories.clear()
        self._tags.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取注册统计信息"""
        return {
            'total_tests': len(self._test_cases),
            'total_suites': len(self._test_suites),
            'categories': {cat: len(tests) for cat, tests in self._categories.items()},
            'tags': {tag: len(tests) for tag, tests in self._tags.items()},
            'priorities': {
                'high': len(self.get_tests_by_priority('high')),
                'medium': len(self.get_tests_by_priority('medium')),
                'low': len(self.get_tests_by_priority('low'))
            }
        }


class AutoTestRegistry:
    """自动测试注册器"""
    
    def __init__(self, registry: TestRegistry = None):
        self.registry = registry or TestRegistry()
        self.logger = logging.getLogger(__name__)
    
    def auto_register_from_air_project(self, air_project_path: str, metadata: TestMetadata = None) -> bool:
        """
        从 .air 项目自动注册测试
        
        Args:
            air_project_path: .air 项目路径
            metadata: 项目元数据
            
        Returns:
            bool: 是否注册成功
        """
        try:
            # 查找主测试文件
            main_py = os.path.join(air_project_path, "main.py")
            if not os.path.exists(main_py):
                self.logger.warning(f".air 项目缺少 main.py 文件: {air_project_path}")
                return False
            
            # 动态导入模块
            project_name = os.path.basename(air_project_path)
            spec = importlib.util.spec_from_file_location(f"air_test_{project_name}", main_py)
            module = importlib.util.module_from_spec(spec)
            
            # 添加项目路径到 sys.path
            if air_project_path not in sys.path:
                sys.path.insert(0, air_project_path)
            
            try:
                spec.loader.exec_module(module)
            except Exception as e:
                self.logger.error(f"导入 .air 项目失败: {air_project_path} - {e}")
                return False
            
            # 查找测试函数和类
            test_functions = []
            test_classes = []
            
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and (name.startswith('test_') or name == 'main'):
                    test_functions.append((name, obj))
                elif inspect.isclass(obj) and name.endswith('Test'):
                    test_classes.append((name, obj))
            
            # 注册测试函数
            for func_name, func in test_functions:
                test_name = f"{project_name}.{func_name}"
                description = func.__doc__ or f"来自 {project_name} 的测试函数"
                
                self.registry.register_test(
                    name=test_name,
                    test_function=func,
                    description=description,
                    category=metadata.category if metadata else "mobile",
                    priority=metadata.priority if metadata else "medium",
                    tags=metadata.tags if metadata else [],
                    metadata=metadata
                )
            
            # 注册测试类
            for class_name, test_class in test_classes:
                # 查找类中的测试方法
                test_methods = [name for name, method in inspect.getmembers(test_class, inspect.ismethod) 
                              if name.startswith('test_')]
                
                for method_name in test_methods:
                    test_name = f"{project_name}.{class_name}.{method_name}"
                    method = getattr(test_class, method_name)
                    description = method.__doc__ or f"来自 {project_name}.{class_name} 的测试方法"
                    
                    self.registry.register_test(
                        name=test_name,
                        test_function=method,
                        description=description,
                        test_class=test_class,
                        category=metadata.category if metadata else "mobile",
                        priority=metadata.priority if metadata else "medium",
                        tags=metadata.tags if metadata else [],
                        metadata=metadata
                    )
            
            self.logger.info(f"成功注册 .air 项目: {project_name} "
                           f"({len(test_functions)} 个函数, {len(test_classes)} 个类)")
            return True
            
        except Exception as e:
            self.logger.error(f"自动注册 .air 项目失败: {air_project_path} - {e}")
            return False
        finally:
            # 清理 sys.path
            if air_project_path in sys.path:
                sys.path.remove(air_project_path)
    
    def auto_register_from_directory(self, directory: str) -> int:
        """
        从目录自动注册所有 .air 项目
        
        Args:
            directory: 搜索目录
            
        Returns:
            int: 成功注册的项目数量
        """
        from .discovery import AirtestDiscovery
        
        discovery = AirtestDiscovery()
        projects = discovery.discover_tests(directory)
        
        success_count = 0
        for project in projects:
            if self.auto_register_from_air_project(project.path, project):
                success_count += 1
        
        self.logger.info(f"从目录 {directory} 自动注册了 {success_count}/{len(projects)} 个项目")
        return success_count
    
    def auto_register_from_python_module(self, module_path: str) -> bool:
        """
        从 Python 模块自动注册测试
        
        Args:
            module_path: Python 模块路径
            
        Returns:
            bool: 是否注册成功
        """
        try:
            # 动态导入模块
            spec = importlib.util.spec_from_file_location("test_module", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找测试函数和类
            registered_count = 0
            
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and name.startswith('test_'):
                    self.registry.register_test(
                        name=name,
                        test_function=obj,
                        description=obj.__doc__ or f"Python 测试函数: {name}"
                    )
                    registered_count += 1
                
                elif inspect.isclass(obj) and (name.endswith('Test') or name.startswith('Test')):
                    # 注册测试类的方法
                    for method_name, method in inspect.getmembers(obj, inspect.ismethod):
                        if method_name.startswith('test_'):
                            test_name = f"{name}.{method_name}"
                            self.registry.register_test(
                                name=test_name,
                                test_function=method,
                                test_class=obj,
                                description=method.__doc__ or f"Python 测试方法: {test_name}"
                            )
                            registered_count += 1
            
            self.logger.info(f"从 Python 模块注册了 {registered_count} 个测试: {module_path}")
            return registered_count > 0
            
        except Exception as e:
            self.logger.error(f"从 Python 模块注册测试失败: {module_path} - {e}")
            return False


# 全局注册器实例
_global_registry = TestRegistry()
_auto_registry = AutoTestRegistry(_global_registry)


def get_global_registry() -> TestRegistry:
    """获取全局测试注册器"""
    return _global_registry


def get_auto_registry() -> AutoTestRegistry:
    """获取自动注册器"""
    return _auto_registry


# 装饰器函数
def test_case(name: str = None, description: str = "", priority: str = "medium",
             tags: List[str] = None, category: str = "general"):
    """
    测试用例装饰器
    
    Args:
        name: 测试名称
        description: 测试描述
        priority: 优先级
        tags: 标签列表
        category: 分类
    """
    def decorator(func):
        test_name = name or func.__name__
        _global_registry.register_test(
            name=test_name,
            test_function=func,
            description=description or func.__doc__ or "",
            priority=priority,
            tags=tags or [],
            category=category
        )
        return func
    return decorator


def test_suite(name: str, tests: List[str]):
    """
    测试套件装饰器
    
    Args:
        name: 套件名称
        tests: 测试名称列表
    """
    def decorator(cls):
        _global_registry.register_test_suite(name, tests)
        return cls
    return decorator