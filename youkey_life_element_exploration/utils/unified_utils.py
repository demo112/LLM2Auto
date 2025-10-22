# -*- encoding=utf8 -*-
"""
统一工具模块

合并多个工具类的功能，提供统一的工具接口
"""

import os
import json
import csv
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import statistics


@dataclass
class UtilResult:
    """工具操作结果"""
    success: bool
    data: Any = None
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedUtils:
    """统一工具类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    # 文件操作工具
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> UtilResult:
        """读取文件"""
        try:
            path = Path(file_path)
            if not path.exists():
                return UtilResult(False, message=f"文件不存在: {file_path}")
            
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return UtilResult(
                True, 
                content, 
                f"成功读取文件: {file_path}",
                {'file_size': path.stat().st_size, 'encoding': encoding}
            )
        except Exception as e:
            return UtilResult(False, message=f"读取文件失败: {e}")
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> UtilResult:
        """写入文件"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return UtilResult(
                True, 
                message=f"成功写入文件: {file_path}",
                metadata={'file_size': len(content.encode(encoding))}
            )
        except Exception as e:
            return UtilResult(False, message=f"写入文件失败: {e}")
    
    def read_json(self, file_path: str) -> UtilResult:
        """读取JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return UtilResult(
                True, 
                data, 
                f"成功读取JSON: {file_path}",
                {'keys_count': len(data) if isinstance(data, dict) else None}
            )
        except Exception as e:
            return UtilResult(False, message=f"读取JSON失败: {e}")
    
    def write_json(self, file_path: str, data: Any, indent: int = 2) -> UtilResult:
        """写入JSON文件"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            return UtilResult(True, message=f"成功写入JSON: {file_path}")
        except Exception as e:
            return UtilResult(False, message=f"写入JSON失败: {e}")
    
    def read_csv(self, file_path: str) -> UtilResult:
        """读取CSV文件"""
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            return UtilResult(
                True, 
                data, 
                f"成功读取CSV: {file_path}",
                {'rows_count': len(data)}
            )
        except Exception as e:
            return UtilResult(False, message=f"读取CSV失败: {e}")
    
    def write_csv(self, file_path: str, data: List[Dict], fieldnames: List[str] = None) -> UtilResult:
        """写入CSV文件"""
        try:
            if not data:
                return UtilResult(False, message="没有数据可写入")
            
            if not fieldnames:
                fieldnames = list(data[0].keys())
            
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            return UtilResult(
                True, 
                message=f"成功写入CSV: {file_path}",
                metadata={'rows_count': len(data)}
            )
        except Exception as e:
            return UtilResult(False, message=f"写入CSV失败: {e}")
    
    # 数据处理工具
    def clean_data(self, data: List[Dict], remove_nulls: bool = True, 
                   remove_duplicates: bool = True) -> UtilResult:
        """清洗数据"""
        try:
            if not isinstance(data, list):
                return UtilResult(False, message="数据必须是列表格式")
            
            cleaned_data = []
            original_count = len(data)
            
            for record in data:
                if not isinstance(record, dict):
                    continue
                
                cleaned_record = {}
                for key, value in record.items():
                    # 移除空值
                    if remove_nulls and (value is None or value == ""):
                        continue
                    
                    # 字符串处理
                    if isinstance(value, str):
                        value = value.strip()
                        if not value and remove_nulls:
                            continue
                    
                    cleaned_record[key] = value
                
                if cleaned_record:
                    cleaned_data.append(cleaned_record)
            
            # 去重
            if remove_duplicates:
                seen = set()
                unique_data = []
                for record in cleaned_data:
                    record_str = json.dumps(record, sort_keys=True, default=str)
                    if record_str not in seen:
                        seen.add(record_str)
                        unique_data.append(record)
                cleaned_data = unique_data
            
            return UtilResult(
                True,
                cleaned_data,
                f"数据清洗完成: {original_count} -> {len(cleaned_data)}",
                {
                    'original_count': original_count,
                    'cleaned_count': len(cleaned_data),
                    'removed_count': original_count - len(cleaned_data)
                }
            )
        except Exception as e:
            return UtilResult(False, message=f"数据清洗失败: {e}")
    
    def validate_data(self, data: List[Dict], required_fields: List[str] = None,
                     field_types: Dict[str, str] = None) -> UtilResult:
        """验证数据"""
        try:
            issues = []
            
            if required_fields:
                for field in required_fields:
                    missing_count = sum(1 for record in data if not record.get(field))
                    if missing_count > 0:
                        issues.append(f"必填字段 {field} 有 {missing_count} 个缺失值")
            
            if field_types:
                type_mapping = {
                    'int': int, 'float': float, 'str': str, 
                    'bool': bool, 'list': list, 'dict': dict
                }
                
                for field, expected_type in field_types.items():
                    expected_class = type_mapping.get(expected_type)
                    if expected_class:
                        type_errors = 0
                        for record in data:
                            value = record.get(field)
                            if value is not None and not isinstance(value, expected_class):
                                type_errors += 1
                        
                        if type_errors > 0:
                            issues.append(f"字段 {field} 有 {type_errors} 个类型错误")
            
            return UtilResult(
                True,
                issues,
                f"数据验证完成，发现 {len(issues)} 个问题",
                {'issues_count': len(issues)}
            )
        except Exception as e:
            return UtilResult(False, message=f"数据验证失败: {e}")
    
    def aggregate_data(self, data: List[Dict], group_by: str, 
                      aggregations: Dict[str, str]) -> UtilResult:
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
            
            return UtilResult(
                True,
                aggregated_data,
                f"数据聚合完成: {len(data)} -> {len(aggregated_data)}",
                {
                    'original_count': len(data),
                    'groups_count': len(aggregated_data),
                    'group_by': group_by
                }
            )
        except Exception as e:
            return UtilResult(False, message=f"数据聚合失败: {e}")
    
    # 统计工具
    def calculate_statistics(self, data: List[Union[int, float]]) -> UtilResult:
        """计算统计信息"""
        try:
            if not data:
                return UtilResult(False, message="没有数据可计算")
            
            numeric_data = [x for x in data if isinstance(x, (int, float))]
            if not numeric_data:
                return UtilResult(False, message="没有数值数据")
            
            stats = {
                'count': len(numeric_data),
                'min': min(numeric_data),
                'max': max(numeric_data),
                'mean': statistics.mean(numeric_data),
                'median': statistics.median(numeric_data),
                'sum': sum(numeric_data)
            }
            
            if len(numeric_data) > 1:
                stats['std_dev'] = statistics.stdev(numeric_data)
                stats['variance'] = statistics.variance(numeric_data)
            
            return UtilResult(True, stats, "统计计算完成")
        except Exception as e:
            return UtilResult(False, message=f"统计计算失败: {e}")
    
    def find_outliers(self, data: List[Union[int, float]], method: str = 'iqr') -> UtilResult:
        """查找异常值"""
        try:
            if not data:
                return UtilResult(False, message="没有数据可分析")
            
            numeric_data = [x for x in data if isinstance(x, (int, float))]
            if len(numeric_data) < 4:
                return UtilResult(False, message="数据点太少，无法检测异常值")
            
            outliers = []
            
            if method == 'iqr':
                # 使用四分位距方法
                sorted_data = sorted(numeric_data)
                n = len(sorted_data)
                q1 = sorted_data[n // 4]
                q3 = sorted_data[3 * n // 4]
                iqr = q3 - q1
                
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = [x for x in numeric_data if x < lower_bound or x > upper_bound]
            
            elif method == 'zscore':
                # 使用Z分数方法
                mean = statistics.mean(numeric_data)
                std_dev = statistics.stdev(numeric_data) if len(numeric_data) > 1 else 0
                
                if std_dev > 0:
                    outliers = [x for x in numeric_data if abs((x - mean) / std_dev) > 2]
            
            return UtilResult(
                True,
                outliers,
                f"异常值检测完成，发现 {len(outliers)} 个异常值",
                {'method': method, 'outliers_count': len(outliers)}
            )
        except Exception as e:
            return UtilResult(False, message=f"异常值检测失败: {e}")
    
    # 格式化工具
    def format_timestamp(self, timestamp: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """格式化时间戳"""
        if timestamp is None:
            timestamp = datetime.now()
        return timestamp.strftime(format_str)
    
    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def format_percentage(self, value: float, total: float, decimal_places: int = 1) -> str:
        """格式化百分比"""
        if total == 0:
            return "0.0%"
        percentage = (value / total) * 100
        return f"{percentage:.{decimal_places}f}%"
    
    # 路径工具
    def ensure_dir(self, dir_path: str) -> UtilResult:
        """确保目录存在"""
        try:
            path = Path(dir_path)
            path.mkdir(parents=True, exist_ok=True)
            return UtilResult(True, message=f"目录已创建: {dir_path}")
        except Exception as e:
            return UtilResult(False, message=f"创建目录失败: {e}")
    
    def list_files(self, dir_path: str, pattern: str = "*", recursive: bool = False) -> UtilResult:
        """列出文件"""
        try:
            path = Path(dir_path)
            if not path.exists():
                return UtilResult(False, message=f"目录不存在: {dir_path}")
            
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))
            
            file_list = [str(f) for f in files if f.is_file()]
            
            return UtilResult(
                True,
                file_list,
                f"找到 {len(file_list)} 个文件",
                {'files_count': len(file_list), 'pattern': pattern}
            )
        except Exception as e:
            return UtilResult(False, message=f"列出文件失败: {e}")
    
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