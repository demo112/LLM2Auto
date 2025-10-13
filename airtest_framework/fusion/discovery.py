# -*- encoding=utf8 -*-
"""
测试用例发现和匹配模块

负责扫描tests目录，发现并匹配同一用例的不同实现方式（Airtest和Poco）
"""

import os
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestCaseInfo:
    """测试用例信息"""
    name: str  # 用例名称（不含后缀）
    airtest_path: Optional[str] = None  # Airtest实现路径
    poco_path: Optional[str] = None  # Poco实现路径
    metadata: Dict = None  # 元数据信息
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TestCaseDiscovery:
    """测试用例发现器"""
    
    def __init__(self, tests_root: str):
        """
        初始化测试用例发现器
        
        Args:
            tests_root: 测试用例根目录路径
        """
        self.tests_root = Path(tests_root)
        self.case_pairs: Dict[str, TestCaseInfo] = {}
        
    def discover_test_cases(self) -> Dict[str, TestCaseInfo]:
        """
        发现并匹配测试用例
        
        Returns:
            Dict[str, TestCaseInfo]: 用例名称到用例信息的映射
        """
        self.case_pairs.clear()
        
        # 递归扫描.air目录
        for air_dir in self._find_air_directories():
            case_info = self._analyze_air_directory(air_dir)
            if case_info:
                self._register_case(case_info)
                
        return self.case_pairs
    
    def _find_air_directories(self) -> List[Path]:
        """查找所有.air目录"""
        air_dirs = []
        for root, dirs, files in os.walk(self.tests_root):
            for dir_name in dirs:
                if dir_name.endswith('.air'):
                    air_dirs.append(Path(root) / dir_name)
        return air_dirs
    
    def _analyze_air_directory(self, air_dir: Path) -> Optional[TestCaseInfo]:
        """
        分析.air目录，提取用例信息
        
        Args:
            air_dir: .air目录路径
            
        Returns:
            TestCaseInfo: 用例信息，如果无效则返回None
        """
        # 提取基础用例名称
        dir_name = air_dir.name
        if not dir_name.endswith('.air'):
            return None
            
        base_name = dir_name[:-4]  # 移除.air后缀
        
        # 查找Python脚本文件
        py_files = list(air_dir.glob('*.py'))
        if not py_files:
            return None
            
        main_script = py_files[0]  # 通常第一个就是主脚本
        
        # 判断是Airtest还是Poco实现
        script_content = self._read_script_content(main_script)
        implementation_type = self._detect_implementation_type(script_content)
        
        # 创建用例信息
        case_info = TestCaseInfo(name=base_name)
        
        if implementation_type == 'airtest':
            case_info.airtest_path = str(main_script)
        elif implementation_type == 'poco':
            case_info.poco_path = str(main_script)
        else:
            # 混合类型，优先判断为poco（因为poco通常也包含airtest）
            case_info.poco_path = str(main_script)
            
        # 读取元数据
        case_info.metadata = self._read_metadata(air_dir)
        
        return case_info
    
    def _read_script_content(self, script_path: Path) -> str:
        """读取脚本内容"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""
    
    def _detect_implementation_type(self, content: str) -> str:
        """
        检测实现类型
        
        Args:
            content: 脚本内容
            
        Returns:
            str: 'airtest', 'poco', 或 'mixed'
        """
        has_poco = bool(re.search(r'from\s+poco|import\s+.*poco|poco\s*\(', content, re.IGNORECASE))
        has_airtest_only = bool(re.search(r'Template\s*\(|touch\s*\(|swipe\s*\(', content))
        
        if has_poco:
            return 'poco'
        elif has_airtest_only:
            return 'airtest'
        else:
            return 'mixed'
    
    def _read_metadata(self, air_dir: Path) -> Dict:
        """读取.air目录的元数据"""
        metadata = {}
        
        # 尝试读取metadata.yaml
        metadata_file = air_dir / 'metadata.yaml'
        if metadata_file.exists():
            try:
                import yaml
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = yaml.safe_load(f) or {}
            except Exception:
                pass
                
        return metadata
    
    def _register_case(self, case_info: TestCaseInfo):
        """注册用例信息"""
        base_name = case_info.name
        
        # 处理带后缀的用例名（如test_case_demo_poco）
        if base_name.endswith('_poco'):
            base_name = base_name[:-5]  # 移除_poco后缀
            
        if base_name in self.case_pairs:
            # 合并到现有用例
            existing = self.case_pairs[base_name]
            if case_info.airtest_path:
                existing.airtest_path = case_info.airtest_path
            if case_info.poco_path:
                existing.poco_path = case_info.poco_path
            existing.metadata.update(case_info.metadata)
        else:
            # 创建新用例
            case_info.name = base_name
            self.case_pairs[base_name] = case_info
    
    def get_paired_cases(self) -> List[TestCaseInfo]:
        """
        获取已配对的测试用例（同时有Airtest和Poco实现）
        
        Returns:
            List[TestCaseInfo]: 已配对的用例列表
        """
        return [
            case for case in self.case_pairs.values()
            if case.airtest_path and case.poco_path
        ]
    
    def get_single_cases(self) -> List[TestCaseInfo]:
        """
        获取单一实现的测试用例
        
        Returns:
            List[TestCaseInfo]: 单一实现的用例列表
        """
        return [
            case for case in self.case_pairs.values()
            if not (case.airtest_path and case.poco_path)
        ]
    
    def print_discovery_summary(self):
        """打印发现结果摘要"""
        paired = self.get_paired_cases()
        single = self.get_single_cases()
        
        print(f"=== 测试用例发现结果 ===")
        print(f"总用例数: {len(self.case_pairs)}")
        print(f"已配对用例: {len(paired)}")
        print(f"单一实现用例: {len(single)}")
        print()
        
        if paired:
            print("已配对用例:")
            for case in paired:
                print(f"  - {case.name}")
                print(f"    Airtest: {case.airtest_path}")
                print(f"    Poco: {case.poco_path}")
                print()
        
        if single:
            print("单一实现用例:")
            for case in single:
                impl_type = "Airtest" if case.airtest_path else "Poco"
                path = case.airtest_path or case.poco_path
                print(f"  - {case.name} ({impl_type}): {path}")