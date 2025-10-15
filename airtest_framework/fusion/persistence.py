# -*- encoding=utf8 -*-
"""
融合脚本持久化模块

负责融合脚本的序列化、存储、加载和版本管理
"""

import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .enhanced_parser import OperationStep, CodeBlock, OperationType
from .intelligent_alignment import AlignmentResult


@dataclass
class FusionMetadata:
    """融合脚本元数据"""
    name: str                       # 脚本名称
    version: str                    # 版本号
    created_at: str                 # 创建时间
    updated_at: str                 # 更新时间
    airtest_source: str             # Airtest源文件路径
    poco_source: str                # Poco源文件路径
    airtest_hash: str               # Airtest文件哈希
    poco_hash: str                  # Poco文件哈希
    alignment_algorithm: str        # 对齐算法版本
    total_steps: int                # 总步骤数
    matched_steps: int              # 匹配的步骤数
    confidence_avg: float           # 平均置信度


@dataclass
class FusionStep:
    """融合步骤"""
    step_id: str                    # 步骤唯一标识
    description: str                # 步骤描述
    operation_type: str             # 操作类型
    target_element: str             # 目标元素
    airtest_code: Optional[Dict[str, Any]] = None  # Airtest代码块
    poco_code: Optional[Dict[str, Any]] = None     # Poco代码块
    confidence_score: float = 0.0   # 匹配置信度
    semantic_tags: List[str] = None # 语义标签
    alignment_reason: str = ""      # 对齐理由


@dataclass
class FusionScript:
    """融合脚本"""
    metadata: FusionMetadata
    steps: List[FusionStep]


class FusionPersistence:
    """融合脚本持久化管理器"""
    
    def __init__(self, storage_root: str = None):
        """
        初始化持久化管理器
        
        Args:
            storage_root: 存储根目录
        """
        self.storage_root = Path(storage_root or "fusion_scripts")
        self.cache_dir = self.storage_root / "cache"
        self.history_dir = self.storage_root / "history"
        
        # 创建目录
        self.storage_root.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.history_dir.mkdir(exist_ok=True)
    
    def save_fusion_script(self, 
                          script_name: str,
                          alignment_results: List[AlignmentResult],
                          airtest_source: str,
                          poco_source: str,
                          algorithm_version: str = "qwen_enhanced_v1") -> str:
        """
        保存融合脚本
        
        Args:
            script_name: 脚本名称
            alignment_results: 对齐结果列表
            airtest_source: Airtest源文件路径
            poco_source: Poco源文件路径
            algorithm_version: 对齐算法版本
            
        Returns:
            str: 保存的文件路径
        """
        # 计算文件哈希
        airtest_hash = self._calculate_file_hash(airtest_source)
        poco_hash = self._calculate_file_hash(poco_source)
        
        # 检查是否已存在相同的融合脚本
        existing_path = self._find_existing_script(script_name, airtest_hash, poco_hash)
        if existing_path:
            print(f"融合脚本已存在: {existing_path}")
            return existing_path
        
        # 创建融合脚本
        fusion_script = self._create_fusion_script(
            script_name, alignment_results, airtest_source, poco_source,
            airtest_hash, poco_hash, algorithm_version
        )
        
        # 保存到文件
        file_path = self.storage_root / f"{script_name}.fusion.json"
        
        # 如果文件已存在，备份到历史目录
        if file_path.exists():
            self._backup_to_history(file_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(fusion_script), f, ensure_ascii=False, indent=2)
        
        print(f"融合脚本已保存: {file_path}")
        return str(file_path)
    
    def load_fusion_script(self, script_path: str) -> Optional[FusionScript]:
        """
        加载融合脚本
        
        Args:
            script_path: 脚本文件路径
            
        Returns:
            Optional[FusionScript]: 融合脚本对象
        """
        if not os.path.exists(script_path):
            print(f"融合脚本文件不存在: {script_path}")
            return None
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 反序列化
            metadata = FusionMetadata(**data['metadata'])
            steps = [FusionStep(**step_data) for step_data in data['steps']]
            
            return FusionScript(metadata=metadata, steps=steps)
            
        except Exception as e:
            print(f"加载融合脚本失败: {e}")
            return None
    
    def list_fusion_scripts(self) -> List[Dict[str, Any]]:
        """
        列出所有融合脚本
        
        Returns:
            List[Dict[str, Any]]: 脚本信息列表
        """
        scripts = []
        
        for file_path in self.storage_root.glob("*.fusion.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = data['metadata']
                scripts.append({
                    'name': metadata['name'],
                    'file_path': str(file_path),
                    'version': metadata['version'],
                    'created_at': metadata['created_at'],
                    'updated_at': metadata['updated_at'],
                    'total_steps': metadata['total_steps'],
                    'matched_steps': metadata['matched_steps'],
                    'confidence_avg': metadata['confidence_avg']
                })
                
            except Exception as e:
                print(f"读取脚本信息失败 {file_path}: {e}")
        
        return sorted(scripts, key=lambda x: x['updated_at'], reverse=True)
    
    def delete_fusion_script(self, script_name: str) -> bool:
        """
        删除融合脚本
        
        Args:
            script_name: 脚本名称
            
        Returns:
            bool: 是否删除成功
        """
        file_path = self.storage_root / f"{script_name}.fusion.json"
        
        if not file_path.exists():
            print(f"融合脚本不存在: {script_name}")
            return False
        
        try:
            # 备份到历史目录
            self._backup_to_history(file_path)
            
            # 删除文件
            file_path.unlink()
            
            print(f"融合脚本已删除: {script_name}")
            return True
            
        except Exception as e:
            print(f"删除融合脚本失败: {e}")
            return False
    
    def validate_fusion_script(self, script_path: str) -> Dict[str, Any]:
        """
        验证融合脚本
        
        Args:
            script_path: 脚本文件路径
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'source_files_exist': False,
            'source_files_changed': False
        }
        
        fusion_script = self.load_fusion_script(script_path)
        if not fusion_script:
            result['errors'].append("无法加载融合脚本")
            return result
        
        # 检查源文件是否存在
        airtest_exists = os.path.exists(fusion_script.metadata.airtest_source)
        poco_exists = os.path.exists(fusion_script.metadata.poco_source)
        
        result['source_files_exist'] = airtest_exists and poco_exists
        
        if not airtest_exists:
            result['errors'].append(f"Airtest源文件不存在: {fusion_script.metadata.airtest_source}")
        
        if not poco_exists:
            result['errors'].append(f"Poco源文件不存在: {fusion_script.metadata.poco_source}")
        
        # 检查源文件是否发生变化
        if airtest_exists:
            current_hash = self._calculate_file_hash(fusion_script.metadata.airtest_source)
            if current_hash != fusion_script.metadata.airtest_hash:
                result['source_files_changed'] = True
                result['warnings'].append("Airtest源文件已发生变化")
        
        if poco_exists:
            current_hash = self._calculate_file_hash(fusion_script.metadata.poco_source)
            if current_hash != fusion_script.metadata.poco_hash:
                result['source_files_changed'] = True
                result['warnings'].append("Poco源文件已发生变化")
        
        # 检查步骤完整性
        if not fusion_script.steps:
            result['errors'].append("融合脚本没有步骤")
        
        # 如果没有错误，则认为有效
        result['valid'] = len(result['errors']) == 0
        
        return result
    
    def _create_fusion_script(self, 
                             script_name: str,
                             alignment_results: List[AlignmentResult],
                             airtest_source: str,
                             poco_source: str,
                             airtest_hash: str,
                             poco_hash: str,
                             algorithm_version: str) -> FusionScript:
        """创建融合脚本对象"""
        now = datetime.now().isoformat()
        
        # 计算统计信息
        total_steps = len(alignment_results)
        matched_steps = sum(1 for r in alignment_results 
                          if r.airtest_step and r.poco_step)
        confidence_avg = sum(r.alignment_confidence for r in alignment_results) / total_steps if total_steps > 0 else 0.0
        
        # 创建元数据
        metadata = FusionMetadata(
            name=script_name,
            version="1.0.0",
            created_at=now,
            updated_at=now,
            airtest_source=airtest_source,
            poco_source=poco_source,
            airtest_hash=airtest_hash,
            poco_hash=poco_hash,
            alignment_algorithm=algorithm_version,
            total_steps=total_steps,
            matched_steps=matched_steps,
            confidence_avg=confidence_avg
        )
        
        # 创建步骤
        steps = []
        for i, result in enumerate(alignment_results):
            step = FusionStep(
                step_id=f"fusion_step_{i+1:03d}",
                description=result.semantic_description,
                operation_type=self._get_operation_type(result),
                target_element=self._get_target_element(result),
                confidence_score=result.alignment_confidence,
                alignment_reason=result.alignment_reason
            )
            
            # 添加代码块
            if result.airtest_step and result.airtest_step.airtest_code:
                step.airtest_code = self._serialize_code_block(result.airtest_step.airtest_code)
            
            if result.poco_step and result.poco_step.poco_code:
                step.poco_code = self._serialize_code_block(result.poco_step.poco_code)
            
            # 添加语义标签
            step.semantic_tags = self._merge_semantic_tags(result)
            
            steps.append(step)
        
        return FusionScript(metadata=metadata, steps=steps)
    
    def _serialize_code_block(self, code_block: CodeBlock) -> Dict[str, Any]:
        """序列化代码块"""
        return {
            'content': code_block.content,
            'start_line': code_block.start_line,
            'end_line': code_block.end_line,
            'imports': code_block.imports,
            'variables': code_block.variables,
            'raw_lines': code_block.raw_lines
        }
    
    def _get_operation_type(self, result: AlignmentResult) -> str:
        """获取操作类型"""
        if result.airtest_step:
            return result.airtest_step.operation_type.value
        elif result.poco_step:
            return result.poco_step.operation_type.value
        else:
            return OperationType.OTHER.value
    
    def _get_target_element(self, result: AlignmentResult) -> str:
        """获取目标元素"""
        if result.airtest_step and result.airtest_step.target_element:
            return result.airtest_step.target_element
        elif result.poco_step and result.poco_step.target_element:
            return result.poco_step.target_element
        else:
            return ""
    
    def _merge_semantic_tags(self, result: AlignmentResult) -> List[str]:
        """合并语义标签"""
        tags = set()
        
        if result.airtest_step and result.airtest_step.semantic_tags:
            tags.update(result.airtest_step.semantic_tags)
        
        if result.poco_step and result.poco_step.semantic_tags:
            tags.update(result.poco_step.semantic_tags)
        
        return list(tags)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希"""
        if not os.path.exists(file_path):
            return ""
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def _find_existing_script(self, script_name: str, airtest_hash: str, poco_hash: str) -> Optional[str]:
        """查找已存在的相同融合脚本"""
        file_path = self.storage_root / f"{script_name}.fusion.json"
        
        if not file_path.exists():
            return None
        
        try:
            fusion_script = self.load_fusion_script(str(file_path))
            if (fusion_script and 
                fusion_script.metadata.airtest_hash == airtest_hash and
                fusion_script.metadata.poco_hash == poco_hash):
                return str(file_path)
        except Exception:
            pass
        
        return None
    
    def _backup_to_history(self, file_path: Path):
        """备份文件到历史目录"""
        if not file_path.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.history_dir / backup_name
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"已备份到历史目录: {backup_path}")
        except Exception as e:
            print(f"备份失败: {e}")


def create_fusion_script_from_alignment(script_name: str,
                                       alignment_results: List[AlignmentResult],
                                       airtest_source: str,
                                       poco_source: str,
                                       storage_root: str = None) -> str:
    """
    从对齐结果创建融合脚本
    
    Args:
        script_name: 脚本名称
        alignment_results: 对齐结果列表
        airtest_source: Airtest源文件路径
        poco_source: Poco源文件路径
        storage_root: 存储根目录
        
    Returns:
        str: 保存的文件路径
    """
    persistence = FusionPersistence(storage_root)
    return persistence.save_fusion_script(
        script_name, alignment_results, airtest_source, poco_source
    )


if __name__ == "__main__":
    # 测试持久化功能
    persistence = FusionPersistence("test_fusion_scripts")
    
    # 列出所有脚本
    scripts = persistence.list_fusion_scripts()
    print(f"找到 {len(scripts)} 个融合脚本:")
    for script in scripts:
        print(f"  - {script['name']} (v{script['version']}) - {script['total_steps']} 步骤")