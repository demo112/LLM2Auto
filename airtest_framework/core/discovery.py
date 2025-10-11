# -*- encoding=utf8 -*-
"""
自动发现引擎 - 负责发现和解析 .air 测试项目
"""

import os
import re
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class TestMetadata:
    """测试元数据"""
    name: str
    path: str
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    timeout: int = 300
    retry_count: int = 1
    priority: str = "medium"  # 添加优先级属性
    prerequisites: List[str] = field(default_factory=list)
    dependencies_before: List[str] = field(default_factory=list)
    dependencies_after: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    category: str = ""
    test_type: str = ""
    device_requirements: Dict = field(default_factory=dict)  # 添加设备要求
    execution_config: Dict = field(default_factory=dict)  # 添加执行配置
    
    @classmethod
    def from_air_path(cls, air_path: str):
        """从 .air 路径创建测试元数据"""
        path_obj = Path(air_path)
        name = path_obj.stem
        
        # 解析文件名获取元数据
        metadata = cls._parse_filename(name)
        metadata.update({
            'name': name,
            'path': str(path_obj.absolute()),
            'category': path_obj.parent.name
        })
        
        # 尝试加载元数据文件
        metadata_files = [
            path_obj / "metadata.yaml",
            path_obj / "test_metadata.yaml"
        ]
        
        for metadata_file in metadata_files:
            if metadata_file.exists():
                file_metadata = cls._load_metadata_file(metadata_file)
                metadata.update(file_metadata)
                break
        
        return cls(**metadata)
    
    @staticmethod
    def _parse_filename(filename: str) -> Dict:
        """解析文件名获取元数据"""
        metadata = {
            'tags': [],
            'platforms': [],
            'test_type': 'functional',
            'priority': 'medium'
        }
        
        # 解析优先级
        if '高优先级' in filename or '_high' in filename:
            metadata['priority'] = 'high'
        elif '低优先级' in filename or '_low' in filename:
            metadata['priority'] = 'low'
        elif '中优先级' in filename or '_medium' in filename:
            metadata['priority'] = 'medium'
        
        # 解析平台信息
        if 'android' in filename.lower():
            metadata['platforms'].append('android')
            metadata['tags'].append('android')
        if 'ios' in filename.lower():
            metadata['platforms'].append('ios')
            metadata['tags'].append('ios')
        if 'web' in filename.lower():
            metadata['platforms'].append('web')
            metadata['tags'].append('web')
        
        # 解析测试类型
        type_patterns = {
            'smoke': 'smoke',
            'regression': 'regression', 
            'integration': 'integration',
            'e2e': 'e2e',
            'performance': 'performance',
            'security': 'security',
            '登录': 'login',
            '购物': 'shopping',
            '用户管理': 'user_management',
            '接口': 'api'
        }
        
        for pattern, test_type in type_patterns.items():
            if pattern in filename:
                metadata['test_type'] = test_type
                metadata['tags'].append(test_type)
                break
        
        # 如果没有指定平台，默认为通用
        if not metadata['platforms']:
            metadata['platforms'] = ['android']
        
        return metadata
    
    @staticmethod
    def _load_metadata_file(metadata_file: Path) -> Dict:
        """加载元数据文件"""
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 扁平化嵌套结构
            metadata = {}
            if 'test_info' in data:
                metadata.update(data['test_info'])
            if 'execution' in data:
                metadata.update(data['execution'])
            if 'dependencies' in data:
                metadata['dependencies_before'] = data['dependencies'].get('before', [])
                metadata['dependencies_after'] = data['dependencies'].get('after', [])
            if 'tags' in data:
                metadata['tags'] = data['tags']
            if 'platforms' in data:
                metadata['platforms'] = data['platforms']
            if 'priority' in data:
                metadata['priority'] = data['priority']
            if 'device_requirements' in data:
                metadata['device_requirements'] = data['device_requirements']
            if 'execution_config' in data:
                metadata['execution_config'] = data['execution_config']
                
            return metadata
        except Exception as e:
            logging.warning(f"无法加载元数据文件 {metadata_file}: {e}")
            return {}


class AirtestDiscovery:
    """Airtest 测试发现引擎"""
    
    def __init__(self, config_manager=None):
        """
        初始化发现引擎
        
        Args:
            config_manager: 配置管理器
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
    def discover_tests(self, test_dir: str = "tests/") -> List[TestMetadata]:
        """
        发现所有 .air 测试项目
        
        Args:
            test_dir (str): 测试目录路径
            
        Returns:
            List[TestMetadata]: 发现的测试列表
        """
        self.logger.info(f"开始在目录 {test_dir} 中发现测试...")
        
        test_dir_path = Path(test_dir)
        if not test_dir_path.exists():
            self.logger.warning(f"测试目录不存在: {test_dir}")
            return []
        
        tests = []
        air_files = list(test_dir_path.rglob("*.air"))
        
        self.logger.info(f"发现 {len(air_files)} 个 .air 项目")
        
        for air_path in air_files:
            try:
                metadata = TestMetadata.from_air_path(str(air_path))
                tests.append(metadata)
                self.logger.debug(f"发现测试: {metadata.name}")
            except Exception as e:
                self.logger.error(f"解析测试失败 {air_path}: {e}")
        
        # 按依赖关系排序
        sorted_tests = self._sort_by_dependencies(tests)
        
        self.logger.info(f"成功发现 {len(sorted_tests)} 个测试用例")
        return sorted_tests
    
    def filter_tests(self, tests: List[TestMetadata], **filters) -> List[TestMetadata]:
        """
        过滤测试用例
        
        Args:
            tests: 测试列表
            **filters: 过滤条件
                - tags: 标签列表
                - platforms: 平台列表
                - categories: 分类列表
                - test_types: 测试类型列表
                
        Returns:
            List[TestMetadata]: 过滤后的测试列表
        """
        filtered_tests = tests
        
        # 按标签过滤
        if 'tags' in filters:
            target_tags = filters['tags']
            if isinstance(target_tags, str):
                target_tags = [target_tags]
            filtered_tests = [
                test for test in filtered_tests
                if any(tag in test.tags for tag in target_tags)
            ]
        
        # 按平台过滤
        if 'platforms' in filters:
            target_platforms = filters['platforms']
            if isinstance(target_platforms, str):
                target_platforms = [target_platforms]
            filtered_tests = [
                test for test in filtered_tests
                if any(platform in test.platforms for platform in target_platforms)
            ]
        
        # 按分类过滤
        if 'categories' in filters:
            target_categories = filters['categories']
            if isinstance(target_categories, str):
                target_categories = [target_categories]
            filtered_tests = [
                test for test in filtered_tests
                if test.category in target_categories
            ]
        
        # 按测试类型过滤
        if 'test_types' in filters:
            target_types = filters['test_types']
            if isinstance(target_types, str):
                target_types = [target_types]
            filtered_tests = [
                test for test in filtered_tests
                if test.test_type in target_types
            ]
        
        self.logger.info(f"过滤后剩余 {len(filtered_tests)} 个测试用例")
        return filtered_tests
    
    def categorize_tests(self, tests: List[TestMetadata]) -> Dict[str, List[TestMetadata]]:
        """
        按分类组织测试用例
        
        Args:
            tests: 测试列表
            
        Returns:
            Dict[str, List[TestMetadata]]: 分类后的测试字典
        """
        categories = {}
        
        for test in tests:
            category = test.category or 'uncategorized'
            if category not in categories:
                categories[category] = []
            categories[category].append(test)
        
        return categories
    
    def _sort_by_dependencies(self, tests: List[TestMetadata]) -> List[TestMetadata]:
        """
        按依赖关系排序测试用例
        
        Args:
            tests: 测试列表
            
        Returns:
            List[TestMetadata]: 排序后的测试列表
        """
        # 简单的拓扑排序实现
        # 这里可以根据需要实现更复杂的依赖解析
        
        # 创建测试名称到测试对象的映射
        test_map = {test.name: test for test in tests}
        
        # 简单排序：有依赖的测试放在后面
        independent_tests = []
        dependent_tests = []
        
        for test in tests:
            if test.dependencies_before:
                dependent_tests.append(test)
            else:
                independent_tests.append(test)
        
        return independent_tests + dependent_tests
    
    def validate_test_structure(self, air_path: str) -> bool:
        """
        验证 .air 项目结构
        
        Args:
            air_path (str): .air 项目路径
            
        Returns:
            bool: 是否有效
        """
        air_dir = Path(air_path)
        
        # 检查是否是目录
        if not air_dir.is_dir():
            self.logger.error(f"{air_path} 不是有效的目录")
            return False
        
        # 检查是否包含 Python 脚本
        py_files = list(air_dir.glob("*.py"))
        if not py_files:
            self.logger.error(f"{air_path} 中没有找到 Python 脚本")
            return False
        
        # 检查是否包含模板图像
        image_files = list(air_dir.glob("*.png")) + list(air_dir.glob("*.jpg"))
        if not image_files:
            self.logger.warning(f"{air_path} 中没有找到模板图像文件")
        
        return True
    
    def validate_air_project(self, project_path: str) -> tuple[bool, List[str]]:
        """验证 .air 项目并返回详细信息
        
        Returns:
            tuple: (is_valid, issues_list)
        """
        issues = []
        project_path = Path(project_path)
        
        try:
            # 检查是否为目录
            if not project_path.is_dir():
                issues.append("项目路径不是一个有效的目录")
                return False, issues
            
            # 检查是否为 .air 项目
            if not project_path.name.endswith('.air'):
                issues.append("项目目录名称不以 .air 结尾")
            
            # 检查主脚本文件
            main_files = ['main.py', 'untitled.py']
            found_main = False
            for main_file in main_files:
                if (project_path / main_file).exists():
                    found_main = True
                    break
            
            if not found_main:
                issues.append(f"缺少主脚本文件 ({', '.join(main_files)} 中的任意一个)")
            
            # 检查图片模板文件
            image_files = list(project_path.glob('*.png'))
            if not image_files:
                issues.append("建议添加图片模板文件 (.png)")
            
            # 检查元数据文件
            metadata_files = ['metadata.yaml', 'test_metadata.yaml']
            has_metadata = any((project_path / f).exists() for f in metadata_files)
            if not has_metadata:
                issues.append("建议添加元数据文件 (metadata.yaml)")
            
            # 项目有效性判断
            is_valid = found_main and project_path.name.endswith('.air')
            
            return is_valid, issues
            
        except Exception as e:
            issues.append(f"验证过程中出现错误: {e}")
            return False, issues
    
    def get_test_statistics(self, tests: List[TestMetadata]) -> Dict:
        """
        获取测试统计信息
        
        Args:
            tests: 测试列表
            
        Returns:
            Dict: 统计信息
        """
        stats = {
            'total_tests': len(tests),
            'by_category': {},
            'by_platform': {},
            'by_type': {},
            'by_priority': {},
            'by_tags': {}
        }
        
        for test in tests:
            # 按分类统计
            category = test.category or 'uncategorized'
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            # 按平台统计
            for platform in test.platforms:
                stats['by_platform'][platform] = stats['by_platform'].get(platform, 0) + 1
            
            # 按类型统计
            test_type = test.test_type or 'unknown'
            stats['by_type'][test_type] = stats['by_type'].get(test_type, 0) + 1
            
            # 按优先级统计
            priority = test.priority or 'medium'
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            # 按标签统计
            for tag in test.tags:
                stats['by_tags'][tag] = stats['by_tags'].get(tag, 0) + 1
        
        return stats