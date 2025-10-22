# -*- encoding=utf8 -*-
"""
导出工具

提供多种格式的数据导出功能
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from enum import Enum
import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
import io
import zipfile
import tempfile
import os


class ExportFormat(Enum):
    """导出格式"""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    EXCEL = "excel"
    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"
    YAML = "yaml"
    ZIP = "zip"


class CompressionType(Enum):
    """压缩类型"""
    NONE = "none"
    ZIP = "zip"
    GZIP = "gzip"


@dataclass
class ExportOptions:
    """导出选项"""
    format: ExportFormat = ExportFormat.JSON
    compression: CompressionType = CompressionType.NONE
    include_metadata: bool = True
    include_timestamp: bool = True
    encoding: str = "utf-8"
    indent: int = 2
    pretty_print: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    filter_fields: Optional[List[str]] = None
    exclude_fields: Optional[List[str]] = None


@dataclass
class ExportMetadata:
    """导出元数据"""
    export_time: datetime = field(default_factory=datetime.now)
    format: str = ""
    source: str = ""
    version: str = "1.0"
    description: str = ""
    record_count: int = 0
    file_size: int = 0
    checksum: str = ""


@dataclass
class ExportResult:
    """导出结果"""
    success: bool = False
    file_path: str = ""
    format: ExportFormat = ExportFormat.JSON
    metadata: Optional[ExportMetadata] = None
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)
    export_time: datetime = field(default_factory=datetime.now)
    file_size: int = 0


class ExportUtils:
    """导出工具"""
    
    def __init__(self):
        self.export_history: List[ExportResult] = []
        self.custom_formatters: Dict[str, callable] = {}
        self.templates: Dict[str, str] = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, str]:
        """初始化模板"""
        
        return {
            "html_table": """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metadata {{ margin-bottom: 20px; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="metadata">
        <h2>{title}</h2>
        <p>导出时间: {export_time}</p>
        <p>记录数量: {record_count}</p>
    </div>
    {table_content}
</body>
</html>
""",
            "markdown_table": """# {title}

**导出时间:** {export_time}  
**记录数量:** {record_count}

{table_content}
""",
            "xml_root": """<?xml version="1.0" encoding="UTF-8"?>
<export>
    <metadata>
        <export_time>{export_time}</export_time>
        <record_count>{record_count}</record_count>
        <description>{description}</description>
    </metadata>
    <data>
        {data_content}
    </data>
</export>
"""
        }
    
    def export_data(
        self,
        data: Union[List[Dict], Dict, Any],
        file_path: str,
        options: Optional[ExportOptions] = None
    ) -> ExportResult:
        """导出数据"""
        
        if options is None:
            options = ExportOptions()
        
        result = ExportResult()
        result.format = options.format
        
        try:
            # 预处理数据
            processed_data = self._preprocess_data(data, options)
            
            # 根据格式导出
            if options.format == ExportFormat.JSON:
                success = self._export_json(processed_data, file_path, options)
            elif options.format == ExportFormat.CSV:
                success = self._export_csv(processed_data, file_path, options)
            elif options.format == ExportFormat.XML:
                success = self._export_xml(processed_data, file_path, options)
            elif options.format == ExportFormat.HTML:
                success = self._export_html(processed_data, file_path, options)
            elif options.format == ExportFormat.MARKDOWN:
                success = self._export_markdown(processed_data, file_path, options)
            elif options.format == ExportFormat.YAML:
                success = self._export_yaml(processed_data, file_path, options)
            else:
                raise ValueError(f"不支持的导出格式: {options.format}")
            
            if success:
                # 应用压缩
                final_path = self._apply_compression(file_path, options.compression)
                
                # 生成元数据
                metadata = self._generate_metadata(processed_data, final_path, options)
                
                result.success = True
                result.file_path = final_path
                result.metadata = metadata
                result.file_size = os.path.getsize(final_path) if os.path.exists(final_path) else 0
            
        except Exception as e:
            result.error_message = str(e)
        
        # 记录导出历史
        self.export_history.append(result)
        
        return result
    
    def _preprocess_data(self, data: Any, options: ExportOptions) -> Any:
        """预处理数据"""
        
        # 转换数据类对象为字典
        if hasattr(data, '__dataclass_fields__'):
            data = asdict(data)
        elif isinstance(data, list) and data and hasattr(data[0], '__dataclass_fields__'):
            data = [asdict(item) for item in data]
        
        # 过滤字段
        if isinstance(data, list) and data and isinstance(data[0], dict):
            if options.filter_fields:
                data = [{k: v for k, v in item.items() if k in options.filter_fields} for item in data]
            elif options.exclude_fields:
                data = [{k: v for k, v in item.items() if k not in options.exclude_fields} for item in data]
        elif isinstance(data, dict):
            if options.filter_fields:
                data = {k: v for k, v in data.items() if k in options.filter_fields}
            elif options.exclude_fields:
                data = {k: v for k, v in data.items() if k not in options.exclude_fields}
        
        return data
    
    def _export_json(self, data: Any, file_path: str, options: ExportOptions) -> bool:
        """导出JSON格式"""
        
        try:
            export_data = data
            
            if options.include_metadata:
                export_data = {
                    "metadata": {
                        "export_time": datetime.now().isoformat(),
                        "format": "json",
                        "version": "1.0"
                    },
                    "data": data
                }
            
            with open(file_path, 'w', encoding=options.encoding) as f:
                json.dump(
                    export_data,
                    f,
                    ensure_ascii=False,
                    indent=options.indent if options.pretty_print else None,
                    default=self._json_serializer
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"JSON导出失败: {e}")
            return False
    
    def _export_csv(self, data: Any, file_path: str, options: ExportOptions) -> bool:
        """导出CSV格式"""
        
        try:
            if not isinstance(data, list) or not data:
                raise ValueError("CSV导出需要非空列表数据")
            
            # 确保所有项都是字典
            if not all(isinstance(item, dict) for item in data):
                raise ValueError("CSV导出需要字典列表")
            
            # 获取所有字段名
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(file_path, 'w', newline='', encoding=options.encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # 写入自定义头部
                if options.custom_headers:
                    for key, value in options.custom_headers.items():
                        f.write(f"# {key}: {value}\n")
                
                # 写入元数据
                if options.include_metadata:
                    f.write(f"# 导出时间: {datetime.now().isoformat()}\n")
                    f.write(f"# 记录数量: {len(data)}\n")
                    f.write(f"# 格式: CSV\n")
                
                writer.writeheader()
                
                for item in data:
                    # 处理复杂数据类型
                    processed_item = {}
                    for key, value in item.items():
                        if isinstance(value, (dict, list)):
                            processed_item[key] = json.dumps(value, ensure_ascii=False, default=self._json_serializer)
                        else:
                            processed_item[key] = value
                    
                    writer.writerow(processed_item)
            
            return True
            
        except Exception as e:
            self.logger.error(f"CSV导出失败: {e}")
            return False
    
    def _export_xml(self, data: Any, file_path: str, options: ExportOptions) -> bool:
        """导出XML格式"""
        
        try:
            root = ET.Element("export")
            
            # 添加元数据
            if options.include_metadata:
                metadata = ET.SubElement(root, "metadata")
                ET.SubElement(metadata, "export_time").text = datetime.now().isoformat()
                ET.SubElement(metadata, "format").text = "xml"
                ET.SubElement(metadata, "version").text = "1.0"
                
                if isinstance(data, list):
                    ET.SubElement(metadata, "record_count").text = str(len(data))
            
            # 添加数据
            data_element = ET.SubElement(root, "data")
            self._add_to_xml_element(data_element, data, "item")
            
            # 格式化XML
            xml_str = ET.tostring(root, encoding='unicode')
            if options.pretty_print:
                dom = minidom.parseString(xml_str)
                xml_str = dom.toprettyxml(indent="  ")
            
            with open(file_path, 'w', encoding=options.encoding) as f:
                f.write(xml_str)
            
            return True
            
        except Exception as e:
            self.logger.error(f"XML导出失败: {e}")
            return False
    
    def _add_to_xml_element(self, parent: ET.Element, data: Any, tag_name: str):
        """添加数据到XML元素"""
        
        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(parent, self._sanitize_xml_tag(key))
                self._add_to_xml_element(child, value, key)
        elif isinstance(data, list):
            for item in data:
                child = ET.SubElement(parent, tag_name)
                self._add_to_xml_element(child, item, "item")
        else:
            parent.text = str(data)
    
    def _sanitize_xml_tag(self, tag: str) -> str:
        """清理XML标签名"""
        # 移除非法字符，确保标签名有效
        import re
        tag = re.sub(r'[^a-zA-Z0-9_-]', '_', str(tag))
        if tag and tag[0].isdigit():
            tag = f"item_{tag}"
        return tag or "item"
    
    def _export_html(self, data: Any, file_path: str, options: ExportOptions) -> bool:
        """导出HTML格式"""
        
        try:
            title = options.custom_headers.get("title", "数据导出")
            export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if isinstance(data, list) and data and isinstance(data[0], dict):
                # 表格格式
                table_content = self._generate_html_table(data)
                record_count = len(data)
            else:
                # 简单格式
                table_content = f"<pre>{json.dumps(data, ensure_ascii=False, indent=2, default=self._json_serializer)}</pre>"
                record_count = 1 if data else 0
            
            html_content = self.templates["html_table"].format(
                title=title,
                export_time=export_time,
                record_count=record_count,
                table_content=table_content
            )
            
            with open(file_path, 'w', encoding=options.encoding) as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"HTML导出失败: {e}")
            return False
    
    def _generate_html_table(self, data: List[Dict]) -> str:
        """生成HTML表格"""
        
        if not data:
            return "<p>无数据</p>"
        
        # 获取所有字段
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        # 生成表格
        table_parts = ["<table>"]
        
        # 表头
        table_parts.append("<thead><tr>")
        for field in fieldnames:
            table_parts.append(f"<th>{field}</th>")
        table_parts.append("</tr></thead>")
        
        # 表体
        table_parts.append("<tbody>")
        for item in data:
            table_parts.append("<tr>")
            for field in fieldnames:
                value = item.get(field, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False, default=self._json_serializer)
                table_parts.append(f"<td>{value}</td>")
            table_parts.append("</tr>")
        table_parts.append("</tbody>")
        
        table_parts.append("</table>")
        
        return "\n".join(table_parts)
    
    def _export_markdown(self, data: Any, file_path: str, options: ExportOptions) -> bool:
        """导出Markdown格式"""
        
        try:
            title = options.custom_headers.get("title", "数据导出")
            export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if isinstance(data, list) and data and isinstance(data[0], dict):
                # 表格格式
                table_content = self._generate_markdown_table(data)
                record_count = len(data)
            else:
                # 代码块格式
                table_content = f"```json\n{json.dumps(data, ensure_ascii=False, indent=2, default=self._json_serializer)}\n```"
                record_count = 1 if data else 0
            
            markdown_content = self.templates["markdown_table"].format(
                title=title,
                export_time=export_time,
                record_count=record_count,
                table_content=table_content
            )
            
            with open(file_path, 'w', encoding=options.encoding) as f:
                f.write(markdown_content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Markdown导出失败: {e}")
            return False
    
    def _generate_markdown_table(self, data: List[Dict]) -> str:
        """生成Markdown表格"""
        
        if not data:
            return "无数据"
        
        # 获取所有字段
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        # 生成表格
        table_parts = []
        
        # 表头
        header = "| " + " | ".join(fieldnames) + " |"
        separator = "| " + " | ".join(["---"] * len(fieldnames)) + " |"
        table_parts.extend([header, separator])
        
        # 表体
        for item in data:
            row_values = []
            for field in fieldnames:
                value = item.get(field, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False, default=self._json_serializer)
                # 转义Markdown特殊字符
                value = str(value).replace("|", "\\|").replace("\n", " ")
                row_values.append(value)
            
            row = "| " + " | ".join(row_values) + " |"
            table_parts.append(row)
        
        return "\n".join(table_parts)
    
    def _export_yaml(self, data: Any, file_path: str, options: ExportOptions) -> bool:
        """导出YAML格式"""
        
        try:
            # 简化的YAML导出（不依赖外部库）
            yaml_content = self._to_yaml(data, 0)
            
            if options.include_metadata:
                metadata_yaml = self._to_yaml({
                    "metadata": {
                        "export_time": datetime.now().isoformat(),
                        "format": "yaml",
                        "version": "1.0"
                    }
                }, 0)
                yaml_content = metadata_yaml + "\n" + yaml_content
            
            with open(file_path, 'w', encoding=options.encoding) as f:
                f.write(yaml_content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"YAML导出失败: {e}")
            return False
    
    def _to_yaml(self, data: Any, indent: int) -> str:
        """转换为YAML格式（简化实现）"""
        
        indent_str = "  " * indent
        
        if isinstance(data, dict):
            if not data:
                return "{}"
            
            lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{indent_str}{key}:")
                    lines.append(self._to_yaml(value, indent + 1))
                else:
                    lines.append(f"{indent_str}{key}: {self._yaml_value(value)}")
            return "\n".join(lines)
        
        elif isinstance(data, list):
            if not data:
                return "[]"
            
            lines = []
            for item in data:
                if isinstance(item, (dict, list)):
                    lines.append(f"{indent_str}-")
                    lines.append(self._to_yaml(item, indent + 1))
                else:
                    lines.append(f"{indent_str}- {self._yaml_value(item)}")
            return "\n".join(lines)
        
        else:
            return f"{indent_str}{self._yaml_value(data)}"
    
    def _yaml_value(self, value: Any) -> str:
        """格式化YAML值"""
        
        if isinstance(value, str):
            # 简单的字符串转义
            if any(char in value for char in ['"', "'", "\n", ":"]):
                return f'"{value.replace('"', '\\"')}"'
            return value
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif value is None:
            return "null"
        else:
            return str(value)
    
    def _apply_compression(self, file_path: str, compression: CompressionType) -> str:
        """应用压缩"""
        
        if compression == CompressionType.NONE:
            return file_path
        
        elif compression == CompressionType.ZIP:
            zip_path = file_path + ".zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, os.path.basename(file_path))
            
            # 删除原文件
            os.remove(file_path)
            return zip_path
        
        else:
            # 其他压缩格式暂不支持
            return file_path
    
    def _generate_metadata(self, data: Any, file_path: str, options: ExportOptions) -> ExportMetadata:
        """生成元数据"""
        
        metadata = ExportMetadata()
        metadata.format = options.format.value
        metadata.source = "export_utils"
        
        if isinstance(data, list):
            metadata.record_count = len(data)
        elif isinstance(data, dict):
            metadata.record_count = len(data)
        else:
            metadata.record_count = 1 if data else 0
        
        if os.path.exists(file_path):
            metadata.file_size = os.path.getsize(file_path)
        
        return metadata
    
    def _json_serializer(self, obj: Any) -> Any:
        """JSON序列化器"""
        
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif hasattr(obj, '__dataclass_fields__'):
            return asdict(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    def export_multiple(
        self,
        datasets: Dict[str, Any],
        base_path: str,
        options: Optional[ExportOptions] = None
    ) -> List[ExportResult]:
        """批量导出多个数据集"""
        
        results = []
        
        for name, data in datasets.items():
            file_path = f"{base_path}_{name}.{options.format.value if options else 'json'}"
            result = self.export_data(data, file_path, options)
            results.append(result)
        
        return results
    
    def create_export_package(
        self,
        datasets: Dict[str, Any],
        package_path: str,
        options: Optional[ExportOptions] = None
    ) -> ExportResult:
        """创建导出包"""
        
        result = ExportResult()
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # 导出各个数据集
                export_results = []
                for name, data in datasets.items():
                    file_path = os.path.join(temp_dir, f"{name}.{options.format.value if options else 'json'}")
                    export_result = self.export_data(data, file_path, options)
                    export_results.append(export_result)
                
                # 创建ZIP包
                with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for export_result in export_results:
                        if export_result.success:
                            zipf.write(export_result.file_path, os.path.basename(export_result.file_path))
                    
                    # 添加导出摘要
                    summary = {
                        "export_time": datetime.now().isoformat(),
                        "datasets": len(datasets),
                        "results": [
                            {
                                "file": os.path.basename(r.file_path),
                                "success": r.success,
                                "error": r.error_message
                            }
                            for r in export_results
                        ]
                    }
                    
                    summary_json = json.dumps(summary, ensure_ascii=False, indent=2)
                    zipf.writestr("export_summary.json", summary_json)
                
                result.success = True
                result.file_path = package_path
                result.format = ExportFormat.ZIP
                result.file_size = os.path.getsize(package_path)
        
        except Exception as e:
            result.error_message = str(e)
        
        return result
    
    def get_export_history(self) -> List[ExportResult]:
        """获取导出历史"""
        return self.export_history.copy()
    
    def clear_export_history(self):
        """清空导出历史"""
        self.export_history.clear()
    
    def add_custom_formatter(self, name: str, formatter: callable):
        """添加自定义格式化器"""
        self.custom_formatters[name] = formatter
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的格式"""
        return [format.value for format in ExportFormat]