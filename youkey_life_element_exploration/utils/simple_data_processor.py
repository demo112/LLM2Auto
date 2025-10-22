# -*- encoding=utf8 -*-
"""
简化数据处理器

提供核心数据处理功能，减少复杂度
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import statistics
import re


@dataclass
class SimpleProcessingResult:
    """简化处理结果"""
    success: bool
    data: Any
    original_count: int
    processed_count: int
    issues: List[str] = field(default_factory=list)
    transformations: List[str] = field(default_factory=list)


class SimpleDataProcessor:
    """简化数据处理器"""
    
    def __init__(self):
        self.history = []
    
    def clean_data(self, data: Union[List[Dict], Dict], 
                   remove_nulls: bool = True,
                   remove_duplicates: bool = True,
                   trim_strings: bool = True) -> SimpleProcessingResult:
        """清洗数据"""
        if isinstance(data, dict):
            data = [data]
        
        original_count = len(data)
        cleaned_data = []
        issues = []
        transformations = []
        
        for record in data:
            try:
                cleaned_record = self._clean_record(record, remove_nulls, trim_strings)
                if cleaned_record:
                    cleaned_data.append(cleaned_record)
            except Exception as e:
                issues.append(f"记录清洗失败: {str(e)}")
        
        # 去重
        if remove_duplicates:
            original_len = len(cleaned_data)
            cleaned_data = self._remove_duplicates(cleaned_data)
            if len(cleaned_data) < original_len:
                transformations.append(f"移除 {original_len - len(cleaned_data)} 个重复记录")
        
        result = SimpleProcessingResult(
            success=True,
            data=cleaned_data,
            original_count=original_count,
            processed_count=len(cleaned_data),
            issues=issues,
            transformations=transformations
        )
        
        self.history.append(result)
        return result
    
    def transform_data(self, data: Union[List[Dict], Dict], 
                      transformations: Dict[str, str]) -> SimpleProcessingResult:
        """转换数据"""
        if isinstance(data, dict):
            data = [data]
        
        original_count = len(data)
        transformed_data = []
        issues = []
        applied_transformations = []
        
        for record in data:
            try:
                transformed_record = self._transform_record(record, transformations)
                transformed_data.append(transformed_record)
            except Exception as e:
                issues.append(f"记录转换失败: {str(e)}")
        
        for field, transform_type in transformations.items():
            applied_transformations.append(f"字段 {field} 应用 {transform_type} 转换")
        
        result = SimpleProcessingResult(
            success=True,
            data=transformed_data,
            original_count=original_count,
            processed_count=len(transformed_data),
            issues=issues,
            transformations=applied_transformations
        )
        
        self.history.append(result)
        return result
    
    def aggregate_data(self, data: List[Dict], group_by: str, 
                      aggregations: Dict[str, str]) -> SimpleProcessingResult:
        """聚合数据"""
        try:
            grouped_data = {}
            
            # 分组
            for record in data:
                key = record.get(group_by, 'unknown')
                if key not in grouped_data:
                    grouped_data[key] = []
                grouped_data[key].append(record)
            
            # 聚合
            aggregated_data = []
            for group_key, group_records in grouped_data.items():
                aggregated_record = {group_by: group_key}
                
                for field, agg_type in aggregations.items():
                    values = [r.get(field) for r in group_records if r.get(field) is not None]
                    if values:
                        aggregated_record[f"{field}_{agg_type}"] = self._aggregate_values(values, agg_type)
                
                aggregated_data.append(aggregated_record)
            
            return SimpleProcessingResult(
                success=True,
                data=aggregated_data,
                original_count=len(data),
                processed_count=len(aggregated_data),
                transformations=[f"按 {group_by} 分组聚合"]
            )
        
        except Exception as e:
            return SimpleProcessingResult(
                success=False,
                data=[],
                original_count=len(data),
                processed_count=0,
                issues=[f"聚合失败: {str(e)}"]
            )
    
    def validate_data(self, data: List[Dict], 
                     required_fields: List[str] = None,
                     field_types: Dict[str, str] = None) -> List[str]:
        """验证数据"""
        issues = []
        
        if required_fields:
            for field in required_fields:
                missing_count = sum(1 for record in data if not record.get(field))
                if missing_count > 0:
                    issues.append(f"必填字段 {field} 有 {missing_count} 个缺失值")
        
        if field_types:
            for field, expected_type in field_types.items():
                type_errors = 0
                for record in data:
                    value = record.get(field)
                    if value is not None and not self._check_type(value, expected_type):
                        type_errors += 1
                
                if type_errors > 0:
                    issues.append(f"字段 {field} 有 {type_errors} 个类型错误")
        
        return issues
    
    def get_data_profile(self, data: List[Dict]) -> Dict[str, Any]:
        """获取数据概况"""
        if not data:
            return {}
        
        profile = {
            'record_count': len(data),
            'field_count': len(data[0]) if data else 0,
            'fields': {}
        }
        
        # 分析每个字段
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        for field in all_fields:
            values = [record.get(field) for record in data if record.get(field) is not None]
            
            field_profile = {
                'count': len(values),
                'null_count': len(data) - len(values),
                'unique_count': len(set(str(v) for v in values))
            }
            
            # 数值统计
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if numeric_values:
                field_profile.update({
                    'min': min(numeric_values),
                    'max': max(numeric_values),
                    'mean': statistics.mean(numeric_values),
                    'median': statistics.median(numeric_values)
                })
            
            profile['fields'][field] = field_profile
        
        return profile
    
    def _clean_record(self, record: Dict, remove_nulls: bool, trim_strings: bool) -> Optional[Dict]:
        """清洗单条记录"""
        cleaned_record = {}
        
        for key, value in record.items():
            # 移除空值
            if remove_nulls and (value is None or value == ""):
                continue
            
            # 字符串处理
            if isinstance(value, str) and trim_strings:
                value = value.strip()
                if not value and remove_nulls:
                    continue
            
            cleaned_record[key] = value
        
        return cleaned_record if cleaned_record else None
    
    def _remove_duplicates(self, data: List[Dict]) -> List[Dict]:
        """移除重复记录"""
        seen = set()
        unique_data = []
        
        for record in data:
            # 使用JSON字符串作为唯一标识
            record_str = json.dumps(record, sort_keys=True, default=str)
            if record_str not in seen:
                seen.add(record_str)
                unique_data.append(record)
        
        return unique_data
    
    def _transform_record(self, record: Dict, transformations: Dict[str, str]) -> Dict:
        """转换单条记录"""
        transformed_record = record.copy()
        
        for field, transform_type in transformations.items():
            if field not in record:
                continue
            
            value = record[field]
            
            try:
                if transform_type == "normalize" and isinstance(value, (int, float)):
                    # 简单归一化到0-1
                    transformed_record[field] = max(0, min(1, value))
                elif transform_type == "uppercase" and isinstance(value, str):
                    transformed_record[field] = value.upper()
                elif transform_type == "lowercase" and isinstance(value, str):
                    transformed_record[field] = value.lower()
                elif transform_type == "round" and isinstance(value, float):
                    transformed_record[field] = round(value, 2)
                elif transform_type == "abs" and isinstance(value, (int, float)):
                    transformed_record[field] = abs(value)
            except Exception:
                # 转换失败时保持原值
                pass
        
        return transformed_record
    
    def _aggregate_values(self, values: List[Any], agg_type: str) -> Any:
        """聚合值"""
        if not values:
            return None
        
        numeric_values = [v for v in values if isinstance(v, (int, float))]
        
        if agg_type == "sum" and numeric_values:
            return sum(numeric_values)
        elif agg_type == "avg" and numeric_values:
            return statistics.mean(numeric_values)
        elif agg_type == "min" and numeric_values:
            return min(numeric_values)
        elif agg_type == "max" and numeric_values:
            return max(numeric_values)
        elif agg_type == "count":
            return len(values)
        elif agg_type == "unique_count":
            return len(set(str(v) for v in values))
        else:
            return values[0]  # 默认返回第一个值
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """检查类型"""
        type_mapping = {
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict
        }
        
        expected_class = type_mapping.get(expected_type)
        if expected_class:
            return isinstance(value, expected_class)
        
        return True