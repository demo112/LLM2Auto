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
class ScriptQuality:
    """脚本质量评估"""
    score: float = 0.0  # 质量分数 (0-100)
    step_count: int = 0  # 步骤数量
    has_assertions: bool = False  # 是否包含断言
    has_waits: bool = False  # 是否包含等待
    complexity: str = "low"  # 复杂度: low, medium, high
    issues: List[str] = None  # 发现的问题
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


@dataclass
class TestCaseInfo:
    """测试用例信息"""
    name: str  # 用例名称（不含后缀）
    airtest_path: Optional[str] = None  # Airtest实现路径
    poco_path: Optional[str] = None  # Poco实现路径
    metadata: Dict = None  # 元数据信息
    airtest_quality: Optional[ScriptQuality] = None  # Airtest脚本质量
    poco_quality: Optional[ScriptQuality] = None  # Poco脚本质量
    
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
        
        # 评估脚本质量
        if case_info.airtest_path:
            case_info.airtest_quality = self._evaluate_script_quality(script_content, 'airtest')
        elif case_info.poco_path:
            case_info.poco_quality = self._evaluate_script_quality(script_content, 'poco')
        
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
        检测实现类型（优化版）
        
        Args:
            content: 脚本内容
            
        Returns:
            str: 'airtest', 'poco', 或 'mixed'
        """
        # 更精确的Poco检测模式
        poco_patterns = [
            r'from\s+poco\.',  # from poco.xxx import
            r'import\s+poco',  # import poco
            r'poco\s*=\s*UnityPoco',  # poco = UnityPoco()
            r'poco\s*=\s*AndroidPoco',  # poco = AndroidPoco()
            r'poco\s*=\s*iOSPoco',  # poco = iOSPoco()
            r'\.poco\(',  # device.poco()
            r'poco\(["\']',  # poco("selector")
            r'poco\.click\(',  # poco.click()
            r'poco\.wait\(',  # poco.wait()
        ]
        
        # 更精确的Airtest检测模式
        airtest_patterns = [
            r'from\s+airtest\.',  # from airtest.xxx import
            r'import\s+airtest',  # import airtest
            r'Template\s*\(',  # Template()
            r'touch\s*\(',  # touch()
            r'swipe\s*\(',  # swipe()
            r'wait\s*\(',  # wait()
            r'exists\s*\(',  # exists()
            r'find_all\s*\(',  # find_all()
            r'assert_exists\s*\(',  # assert_exists()
        ]
        
        # 计算匹配分数
        poco_score = sum(1 for pattern in poco_patterns if re.search(pattern, content, re.IGNORECASE))
        airtest_score = sum(1 for pattern in airtest_patterns if re.search(pattern, content, re.IGNORECASE))
        
        # 根据分数判断类型
        if poco_score > 0 and airtest_score > 0:
            # 如果两种都有，根据主要使用的API判断
            if poco_score > airtest_score:
                return 'poco'
            elif airtest_score > poco_score:
                return 'mixed'  # Airtest为主但包含Poco
            else:
                return 'mixed'
        elif poco_score > 0:
            return 'poco'
        elif airtest_score > 0:
            return 'airtest'
        else:
             return 'unknown'
    
    def _evaluate_script_quality(self, content: str, script_type: str) -> ScriptQuality:
        """
        评估脚本质量
        
        Args:
            content: 脚本内容
            script_type: 脚本类型 ('airtest', 'poco', 'mixed')
            
        Returns:
            ScriptQuality: 质量评估结果
        """
        quality = ScriptQuality()
        
        # 计算步骤数量
        if script_type == 'airtest':
            action_patterns = [r'touch\s*\(', r'swipe\s*\(', r'wait\s*\(', r'exists\s*\(']
        elif script_type == 'poco':
            action_patterns = [r'\.click\s*\(', r'\.swipe\s*\(', r'\.wait\s*\(', r'poco\s*\(']
        else:
            action_patterns = [r'touch\s*\(', r'swipe\s*\(', r'\.click\s*\(', r'\.swipe\s*\(']
        
        quality.step_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) 
                                for pattern in action_patterns)
        
        # 检查是否包含断言
        assertion_patterns = [r'assert\s+', r'assert_exists\s*\(', r'assert_equal\s*\(']
        quality.has_assertions = any(re.search(pattern, content, re.IGNORECASE) 
                                   for pattern in assertion_patterns)
        
        # 检查是否包含等待
        wait_patterns = [r'wait\s*\(', r'sleep\s*\(', r'\.wait\s*\(']
        quality.has_waits = any(re.search(pattern, content, re.IGNORECASE) 
                              for pattern in wait_patterns)
        
        # 评估复杂度
        if quality.step_count <= 3:
            quality.complexity = "low"
        elif quality.step_count <= 10:
            quality.complexity = "medium"
        else:
            quality.complexity = "high"
        
        # 检查潜在问题
        self._check_script_issues(content, quality)
        
        # 计算质量分数
        quality.score = self._calculate_quality_score(quality)
        
        return quality
    
    def _check_script_issues(self, content: str, quality: ScriptQuality):
        """检查脚本中的潜在问题"""
        # 检查硬编码等待时间
        if re.search(r'sleep\s*\(\s*[5-9]\d*\s*\)', content):
            quality.issues.append("包含过长的硬编码等待时间")
        
        # 检查缺少异常处理
        if quality.step_count > 5 and not re.search(r'try\s*:|except\s*:', content):
            quality.issues.append("缺少异常处理机制")
        
        # 检查缺少断言
        if quality.step_count > 3 and not quality.has_assertions:
            quality.issues.append("缺少验证断言")
        
        # 检查重复代码
        lines = content.split('\n')
        unique_lines = set(line.strip() for line in lines if line.strip())
        if len(lines) - len(unique_lines) > 3:
            quality.issues.append("存在重复代码")
    
    def _calculate_quality_score(self, quality: ScriptQuality) -> float:
        """计算质量分数"""
        score = 50.0  # 基础分数
        
        # 步骤数量加分
        if quality.step_count > 0:
            score += min(quality.step_count * 2, 20)
        
        # 包含断言加分
        if quality.has_assertions:
            score += 15
        
        # 包含等待加分
        if quality.has_waits:
            score += 10
        
        # 复杂度调整
        if quality.complexity == "medium":
            score += 5
        elif quality.complexity == "high":
            score += 10
        
        # 问题扣分
        score -= len(quality.issues) * 5
        
        return max(0, min(100, score))
    
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
        """注册用例信息（优化版）"""
        base_name = self._normalize_case_name(case_info.name)
        
        # 查找最佳匹配的现有用例
        matched_key = self._find_best_match(base_name)
        
        if matched_key:
            # 合并到现有用例
            existing = self.case_pairs[matched_key]
            self._merge_case_info(existing, case_info)
        else:
            # 创建新用例
            case_info.name = base_name
            self.case_pairs[base_name] = case_info
    
    def _normalize_case_name(self, name: str) -> str:
        """标准化用例名称"""
        original_name = name
        
        # 首先移除 _poco 和 _airtest 后缀
        if name.endswith('_poco'):
            name = name[:-5]
        elif name.endswith('_airtest'):
            name = name[:-8]
        
        # 然后移除其他后缀
        other_suffixes = ['_test']
        for suffix in other_suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
        
        # 移除版本号
        name = re.sub(r'_v\d+$', '', name)
        name = re.sub(r'_\d+$', '', name)
        
        return name
    
    def _find_best_match(self, name: str) -> Optional[str]:
        """查找最佳匹配的现有用例"""
        if name in self.case_pairs:
            return name
        
        # 模糊匹配
        for existing_name in self.case_pairs.keys():
            # 计算相似度
            similarity = self._calculate_similarity(name, existing_name)
            if similarity > 0.8:  # 相似度阈值
                return existing_name
        
        return None
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """计算两个名称的相似度"""
        # 简单的编辑距离相似度
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        max_len = max(len(name1), len(name2))
        if max_len == 0:
            return 1.0
        
        distance = levenshtein_distance(name1.lower(), name2.lower())
        return 1.0 - (distance / max_len)
    
    def _merge_case_info(self, existing: TestCaseInfo, new_case: TestCaseInfo):
        """合并用例信息"""
        # 合并路径信息
        if new_case.airtest_path:
            if existing.airtest_path:
                # 如果已有Airtest路径，选择质量更高的
                if (new_case.airtest_quality and existing.airtest_quality and 
                    new_case.airtest_quality.score > existing.airtest_quality.score):
                    existing.airtest_path = new_case.airtest_path
                    existing.airtest_quality = new_case.airtest_quality
            else:
                existing.airtest_path = new_case.airtest_path
                existing.airtest_quality = new_case.airtest_quality
        
        if new_case.poco_path:
            if existing.poco_path:
                # 如果已有Poco路径，选择质量更高的
                if (new_case.poco_quality and existing.poco_quality and 
                    new_case.poco_quality.score > existing.poco_quality.score):
                    existing.poco_path = new_case.poco_path
                    existing.poco_quality = new_case.poco_quality
            else:
                existing.poco_path = new_case.poco_path
                existing.poco_quality = new_case.poco_quality
        
        # 合并元数据
        existing.metadata.update(new_case.metadata)
    
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
        """打印发现结果摘要（优化版）"""
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
                print(f"  📋 {case.name}")
                
                # Airtest信息
                if case.airtest_path and case.airtest_quality:
                    quality = case.airtest_quality
                    print(f"    🔧 Airtest: {case.airtest_path}")
                    print(f"       质量分数: {quality.score:.1f}/100 | 步骤: {quality.step_count} | 复杂度: {quality.complexity}")
                    if quality.issues:
                        print(f"       ⚠️  问题: {', '.join(quality.issues)}")
                
                # Poco信息
                if case.poco_path and case.poco_quality:
                    quality = case.poco_quality
                    print(f"    🎯 Poco: {case.poco_path}")
                    print(f"       质量分数: {quality.score:.1f}/100 | 步骤: {quality.step_count} | 复杂度: {quality.complexity}")
                    if quality.issues:
                        print(f"       ⚠️  问题: {', '.join(quality.issues)}")
                print()
        
        if single:
            print("单一实现用例:")
            for case in single:
                impl_type = "Airtest" if case.airtest_path else "Poco"
                path = case.airtest_path or case.poco_path
                quality = case.airtest_quality or case.poco_quality
                
                print(f"  📄 {case.name} ({impl_type}): {path}")
                if quality:
                    print(f"     质量分数: {quality.score:.1f}/100 | 步骤: {quality.step_count} | 复杂度: {quality.complexity}")
                    if quality.issues:
                        print(f"     ⚠️  问题: {', '.join(quality.issues)}")
        
        # 质量统计
        self._print_quality_statistics()
    
    def _print_quality_statistics(self):
        """打印质量统计信息"""
        all_qualities = []
        for case in self.case_pairs.values():
            if case.airtest_quality:
                all_qualities.append(case.airtest_quality)
            if case.poco_quality:
                all_qualities.append(case.poco_quality)
        
        if not all_qualities:
            return
        
        print("\n=== 质量统计 ===")
        avg_score = sum(q.score for q in all_qualities) / len(all_qualities)
        high_quality = sum(1 for q in all_qualities if q.score >= 80)
        medium_quality = sum(1 for q in all_qualities if 60 <= q.score < 80)
        low_quality = sum(1 for q in all_qualities if q.score < 60)
        
        print(f"平均质量分数: {avg_score:.1f}/100")
        print(f"高质量脚本 (≥80): {high_quality}")
        print(f"中等质量脚本 (60-79): {medium_quality}")
        print(f"低质量脚本 (<60): {low_quality}")
        
        # 常见问题统计
        all_issues = []
        for q in all_qualities:
            all_issues.extend(q.issues)
        
        if all_issues:
            from collections import Counter
            issue_counts = Counter(all_issues)
            print(f"\n常见问题:")
            for issue, count in issue_counts.most_common(3):
                print(f"  - {issue}: {count}次")