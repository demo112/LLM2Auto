# -*- encoding=utf8 -*-
"""
统一报告生成器

整合原有的多个报告生成器功能，提供统一的报告生成接口
"""

import os
import json
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .unified_models import (
    ElementMapping, ElementInfo, QualityScore, AnalysisResult, Report, ReportSection,
    ElementType, CorrelationType, QualityLevel
)
from .base_interfaces import IReportGenerator


class UnifiedReportGenerator(IReportGenerator):
    """统一报告生成器"""
    
    def __init__(self, output_dir: str = "reports", output_formats: List[str] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.output_formats = output_formats or ['html', 'json', 'markdown']
        
        # 报告模板配置
        self.templates = {
            'html': self._get_html_template(),
            'json': self._get_json_template(),
            'markdown': self._get_markdown_template()
        }
    
    def generate_file_report(self, data: Any, report_type: str = "comprehensive", 
                            format: str = "html") -> str:
        """生成报告文件"""
        # 创建报告对象
        report = self._create_report(data, report_type)
        
        # 根据格式生成报告内容
        if format.lower() == "html":
            content = self._generate_html_report(report)
            filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        elif format.lower() == "json":
            content = self._generate_json_report(report)
            filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        elif format.lower() == "markdown":
            content = self._generate_markdown_report(report)
            filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        else:
            raise ValueError(f"不支持的报告格式: {format}")
        
        # 保存报告文件
        report_path = self.output_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(report_path)
    
    def generate_summary(self, data: Any) -> str:
        """生成摘要"""
        if isinstance(data, list) and data:
            if isinstance(data[0], ElementMapping):
                return self._generate_mapping_summary(data)
            elif isinstance(data[0], ElementInfo):
                return self._generate_element_summary(data)
        elif isinstance(data, QualityScore):
            return self._generate_quality_summary(data)
        elif isinstance(data, AnalysisResult):
            return self._generate_analysis_summary(data)
        
        return "无法生成摘要：不支持的数据类型"
    
    def export_data(self, data: Any, filename: str, format: str = "json") -> str:
        """导出数据"""
        export_path = self.output_dir / filename
        
        if format.lower() == "json":
            content = self._export_to_json(data)
        elif format.lower() == "csv":
            content = self._export_to_csv(data)
        elif format.lower() == "xml":
            content = self._export_to_xml(data)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(export_path)
    
    def create_dashboard(self, data: Any) -> str:
        """创建仪表板"""
        dashboard_content = self._generate_dashboard_html(data)
        dashboard_path = self.output_dir / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        
        return str(dashboard_path)
    
    def _create_report(self, data: Any, report_type: str) -> Report:
        """创建报告对象"""
        sections = []
        
        if report_type == "mapping":
            sections = self._create_mapping_sections(data)
        elif report_type == "quality":
            sections = self._create_quality_sections(data)
        elif report_type == "analysis":
            sections = self._create_analysis_sections(data)
        else:  # comprehensive
            sections = self._create_comprehensive_sections(data)
        
        return Report(
            report_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=f"{report_type.title()} Report",
            report_type=report_type,
            created_at=datetime.now(),
            sections=sections
        )
    
    def _create_mapping_sections(self, mappings: List[ElementMapping]) -> List[ReportSection]:
        """创建映射报告章节"""
        sections = []
        
        # 概览章节
        overview_content = self._generate_mapping_overview(mappings)
        sections.append(ReportSection(
            title="映射概览",
            content=overview_content,
            order=1
        ))
        
        # 详细映射章节
        details_content = self._generate_mapping_details(mappings)
        sections.append(ReportSection(
            title="详细映射",
            content=details_content,
            order=2
        ))
        
        # 统计章节
        stats_content = self._generate_mapping_statistics(mappings)
        sections.append(ReportSection(
            title="统计信息",
            content=stats_content,
            order=3
        ))
        
        return sections
    
    def _create_quality_sections(self, quality_score: QualityScore) -> List[ReportSection]:
        """创建质量报告章节"""
        sections = []
        
        # 质量概览
        overview_content = self._generate_quality_overview(quality_score)
        sections.append(ReportSection(
            title="质量概览",
            content=overview_content,
            order=1
        ))
        
        # 详细指标
        metrics_content = self._generate_quality_metrics(quality_score)
        sections.append(ReportSection(
            title="详细指标",
            content=metrics_content,
            order=2
        ))
        
        # 改进建议
        suggestions_content = self._generate_quality_suggestions(quality_score)
        sections.append(ReportSection(
            title="改进建议",
            content=suggestions_content,
            order=3
        ))
        
        return sections
    
    def _create_analysis_sections(self, analysis_result: AnalysisResult) -> List[ReportSection]:
        """创建分析报告章节"""
        sections = []
        
        # 分析摘要
        summary_content = analysis_result.summary
        sections.append(ReportSection(
            title="分析摘要",
            content=summary_content,
            order=1
        ))
        
        # 详细结果
        details_content = json.dumps(analysis_result.details, indent=2, ensure_ascii=False)
        sections.append(ReportSection(
            title="详细结果",
            content=details_content,
            order=2
        ))
        
        # 指标数据
        metrics_content = json.dumps(analysis_result.metrics, indent=2, ensure_ascii=False)
        sections.append(ReportSection(
            title="指标数据",
            content=metrics_content,
            order=3
        ))
        
        return sections
    
    def _create_comprehensive_sections(self, data: Any) -> List[ReportSection]:
        """创建综合报告章节"""
        sections = []
        
        # 根据数据类型创建相应章节
        if isinstance(data, list) and data:
            if isinstance(data[0], ElementMapping):
                sections.extend(self._create_mapping_sections(data))
            elif isinstance(data[0], ElementInfo):
                sections.extend(self._create_element_sections(data))
        elif isinstance(data, QualityScore):
            sections.extend(self._create_quality_sections(data))
        elif isinstance(data, AnalysisResult):
            sections.extend(self._create_analysis_sections(data))
        
        return sections
    
    def _create_element_sections(self, elements: List[ElementInfo]) -> List[ReportSection]:
        """创建元素报告章节"""
        sections = []
        
        # 元素概览
        overview_content = self._generate_element_overview(elements)
        sections.append(ReportSection(
            title="元素概览",
            content=overview_content,
            order=1
        ))
        
        # 元素详情
        details_content = self._generate_element_details(elements)
        sections.append(ReportSection(
            title="元素详情",
            content=details_content,
            order=2
        ))
        
        return sections
    
    def _generate_html_report(self, report: Report) -> str:
        """生成HTML报告"""
        html_content = self.templates['html'].format(
            title=html.escape(report.title),
            generated_at=report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            sections=self._render_html_sections(report.sections),
            metadata=self._render_html_metadata({"report_type": report.report_type})
        )
        return html_content
    
    def _generate_json_report(self, report: Report) -> str:
        """生成JSON报告"""
        report_dict = {
            "title": report.title,
            "created_at": report.created_at.isoformat(),
            "report_type": report.report_type,
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "order": section.order
                }
                for section in report.sections
            ]
        }
        return json.dumps(report_dict, indent=2, ensure_ascii=False)
    
    def _generate_markdown_report(self, report: Report) -> str:
        """生成Markdown报告"""
        md_content = f"# {report.title}\n\n"
        md_content += f"**生成时间**: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for section in report.sections:
            md_content += f"## {section.title}\n\n"
            md_content += f"{section.content}\n\n"
        
        return md_content
    
    def _generate_dashboard_html(self, data: Any) -> str:
        """生成仪表板HTML"""
        dashboard_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>数据仪表板</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: #f9f9f9; }}
                .card h3 {{ margin-top: 0; color: #333; }}
                .metric {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                .chart {{ height: 200px; background: #fff; border: 1px solid #eee; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>数据仪表板</h1>
            <div class="dashboard">
                {cards}
            </div>
            <p><small>生成时间: {timestamp}</small></p>
        </body>
        </html>
        """
        
        cards = self._generate_dashboard_cards(data)
        
        return dashboard_template.format(
            cards=cards,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def _generate_dashboard_cards(self, data: Any) -> str:
        """生成仪表板卡片"""
        cards = []
        
        if isinstance(data, list) and data:
            if isinstance(data[0], ElementMapping):
                cards.extend(self._generate_mapping_cards(data))
            elif isinstance(data[0], ElementInfo):
                cards.extend(self._generate_element_cards(data))
        
        return "\n".join(cards)
    
    def _generate_mapping_cards(self, mappings: List[ElementMapping]) -> List[str]:
        """生成映射仪表板卡片"""
        cards = []
        
        # 总数卡片
        total_card = f"""
        <div class="card">
            <h3>总映射数</h3>
            <div class="metric">{len(mappings)}</div>
        </div>
        """
        cards.append(total_card)
        
        # 平均置信度卡片
        avg_confidence = sum(m.confidence for m in mappings) / len(mappings)
        confidence_card = f"""
        <div class="card">
            <h3>平均置信度</h3>
            <div class="metric">{avg_confidence:.2f}</div>
        </div>
        """
        cards.append(confidence_card)
        
        # 高质量映射卡片
        high_quality = len([m for m in mappings if m.confidence > 0.8])
        quality_card = f"""
        <div class="card">
            <h3>高质量映射</h3>
            <div class="metric">{high_quality}</div>
            <p>{high_quality/len(mappings)*100:.1f}% 的映射</p>
        </div>
        """
        cards.append(quality_card)
        
        return cards
    
    def _generate_element_cards(self, elements: List[ElementInfo]) -> List[str]:
        """生成元素仪表板卡片"""
        cards = []
        
        # 总数卡片
        total_card = f"""
        <div class="card">
            <h3>总元素数</h3>
            <div class="metric">{len(elements)}</div>
        </div>
        """
        cards.append(total_card)
        
        # 元素类型分布卡片
        type_counts = {}
        for element in elements:
            type_name = element.element_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        type_list = "<br>".join([f"{k}: {v}" for k, v in type_counts.items()])
        type_card = f"""
        <div class="card">
            <h3>元素类型分布</h3>
            <div style="font-size: 14px;">{type_list}</div>
        </div>
        """
        cards.append(type_card)
        
        return cards
    
    def _render_html_sections(self, sections: List[ReportSection]) -> str:
        """渲染HTML章节"""
        html_sections = []
        for section in sections:
            section_html = f"""
            <div class="section">
                <h2>{html.escape(section.title)}</h2>
                <div class="content">
                    <pre>{html.escape(section.content)}</pre>
                </div>
            </div>
            """
            html_sections.append(section_html)
        return "\n".join(html_sections)
    
    def _render_html_metadata(self, metadata: Dict[str, Any]) -> str:
        """渲染HTML元数据"""
        metadata_items = []
        for key, value in metadata.items():
            metadata_items.append(f"<li><strong>{html.escape(key)}</strong>: {html.escape(str(value))}</li>")
        return "<ul>" + "\n".join(metadata_items) + "</ul>"
    
    def _generate_mapping_overview(self, mappings: List[ElementMapping]) -> str:
        """生成映射概览"""
        total = len(mappings)
        high_confidence = len([m for m in mappings if m.confidence > 0.8])
        avg_confidence = sum(m.confidence for m in mappings) / total if total > 0 else 0
        
        return f"""
映射总数: {total}
高置信度映射: {high_confidence} ({high_confidence/total*100:.1f}%)
平均置信度: {avg_confidence:.3f}
        """.strip()
    
    def _generate_mapping_details(self, mappings: List[ElementMapping]) -> str:
        """生成映射详情"""
        details = []
        for i, mapping in enumerate(mappings[:10], 1):  # 只显示前10个
            airtest_info = mapping.airtest_element.template_file if mapping.airtest_element else "N/A"
            poco_info = mapping.poco_element.selector if mapping.poco_element else "N/A"
            
            detail = f"""
{i}. 映射ID: {mapping.mapping_id}
   Airtest: {airtest_info}
   Poco: {poco_info}
   置信度: {mapping.confidence:.3f}
   关联类型: {mapping.correlation_type.value}
            """.strip()
            details.append(detail)
        
        if len(mappings) > 10:
            details.append(f"\n... 还有 {len(mappings) - 10} 个映射")
        
        return "\n\n".join(details)
    
    def _generate_mapping_statistics(self, mappings: List[ElementMapping]) -> str:
        """生成映射统计"""
        from collections import Counter
        
        # 关联类型统计
        correlation_counts = Counter(m.correlation_type for m in mappings)
        correlation_stats = "\n".join([f"  {k.value}: {v}" for k, v in correlation_counts.items()])
        
        # 置信度分布
        confidence_ranges = {
            "0.9-1.0": len([m for m in mappings if 0.9 <= m.confidence <= 1.0]),
            "0.8-0.9": len([m for m in mappings if 0.8 <= m.confidence < 0.9]),
            "0.7-0.8": len([m for m in mappings if 0.7 <= m.confidence < 0.8]),
            "0.6-0.7": len([m for m in mappings if 0.6 <= m.confidence < 0.7]),
            "<0.6": len([m for m in mappings if m.confidence < 0.6])
        }
        confidence_stats = "\n".join([f"  {k}: {v}" for k, v in confidence_ranges.items()])
        
        return f"""
关联类型分布:
{correlation_stats}

置信度分布:
{confidence_stats}
        """.strip()
    
    def _generate_element_overview(self, elements: List[ElementInfo]) -> str:
        """生成元素概览"""
        from collections import Counter
        
        total = len(elements)
        type_counts = Counter(e.element_type for e in elements)
        type_stats = "\n".join([f"  {k.value}: {v}" for k, v in type_counts.items()])
        
        return f"""
元素总数: {total}

元素类型分布:
{type_stats}
        """.strip()
    
    def _generate_element_details(self, elements: List[ElementInfo]) -> str:
        """生成元素详情"""
        details = []
        for i, element in enumerate(elements[:10], 1):  # 只显示前10个
            detail = f"""
{i}. 元素ID: {element.element_id}
   类型: {element.element_type.value}
   定位器: {element.locator}
   行号: {element.line_number}
            """.strip()
            details.append(detail)
        
        if len(elements) > 10:
            details.append(f"\n... 还有 {len(elements) - 10} 个元素")
        
        return "\n\n".join(details)
    
    def _generate_quality_overview(self, quality_score: QualityScore) -> str:
        """生成质量概览"""
        return f"""
质量等级: {quality_score.level.value}
总体得分: {quality_score.score:.3f}
评估时间: {quality_score.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
    
    def _generate_quality_metrics(self, quality_score: QualityScore) -> str:
        """生成质量指标"""
        if not quality_score.metrics:
            return "无详细指标数据"
        
        metrics = quality_score.metrics
        return f"""
覆盖率: {getattr(metrics, 'coverage_rate', 0):.3f}
准确率: {getattr(metrics, 'accuracy_rate', 0):.3f}
一致性: {getattr(metrics, 'consistency_rate', 0):.3f}
完整性: {getattr(metrics, 'completeness_rate', 0):.3f}
可靠性: {getattr(metrics, 'reliability_rate', 0):.3f}
总元素数: {getattr(metrics, 'total_elements', 0)}
有效映射数: {getattr(metrics, 'valid_mappings', 0)}
错误数: {getattr(metrics, 'error_count', 0)}
        """.strip()
    
    def _generate_quality_suggestions(self, quality_score: QualityScore) -> str:
        """生成质量建议"""
        if not quality_score.suggestions:
            return "暂无改进建议"
        
        suggestions = "\n".join([f"• {suggestion}" for suggestion in quality_score.suggestions])
        return f"改进建议:\n{suggestions}"
    
    def _generate_mapping_summary(self, mappings: List[ElementMapping]) -> str:
        """生成映射摘要"""
        total = len(mappings)
        high_quality = len([m for m in mappings if m.confidence > 0.8])
        return f"共 {total} 个映射，其中 {high_quality} 个高质量映射"
    
    def _generate_element_summary(self, elements: List[ElementInfo]) -> str:
        """生成元素摘要"""
        from collections import Counter
        total = len(elements)
        type_counts = Counter(e.element_type for e in elements)
        main_type = type_counts.most_common(1)[0] if type_counts else ("未知", 0)
        return f"共 {total} 个元素，主要类型为 {main_type[0].value} ({main_type[1]} 个)"
    
    def _generate_quality_summary(self, quality_score: QualityScore) -> str:
        """生成质量摘要"""
        return f"质量等级: {quality_score.level.value}，得分: {quality_score.score:.2f}"
    
    def _generate_analysis_summary(self, analysis_result: AnalysisResult) -> str:
        """生成分析摘要"""
        return f"{analysis_result.analysis_type} 分析: {analysis_result.summary}"
    
    def _export_to_json(self, data: Any) -> str:
        """导出为JSON"""
        if hasattr(data, '__dict__'):
            return json.dumps(data.__dict__, indent=2, ensure_ascii=False, default=str)
        elif isinstance(data, list):
            return json.dumps([item.__dict__ if hasattr(item, '__dict__') else str(item) 
                             for item in data], indent=2, ensure_ascii=False, default=str)
        else:
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)
    
    def _export_to_csv(self, data: Any) -> str:
        """导出为CSV"""
        # 简化的CSV导出实现
        if isinstance(data, list) and data:
            if isinstance(data[0], ElementMapping):
                return self._mappings_to_csv(data)
            elif isinstance(data[0], ElementInfo):
                return self._elements_to_csv(data)
        
        return "不支持的CSV导出数据类型"
    
    def _export_to_xml(self, data: Any) -> str:
        """导出为XML"""
        # 简化的XML导出实现
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<data>\n'
        
        if isinstance(data, list):
            for i, item in enumerate(data):
                xml_content += f'  <item index="{i}">\n'
                if hasattr(item, '__dict__'):
                    for key, value in item.__dict__.items():
                        xml_content += f'    <{key}>{html.escape(str(value))}</{key}>\n'
                xml_content += '  </item>\n'
        
        xml_content += '</data>'
        return xml_content
    
    def _mappings_to_csv(self, mappings: List[ElementMapping]) -> str:
        """映射转CSV"""
        csv_lines = ["mapping_id,airtest_element,poco_element,confidence,correlation_type"]
        
        for mapping in mappings:
            airtest_info = mapping.airtest_element.template_file if mapping.airtest_element else ""
            poco_info = mapping.poco_element.selector if mapping.poco_element else ""
            
            csv_lines.append(f'"{mapping.mapping_id}","{airtest_info}","{poco_info}",'
                           f'{mapping.confidence},"{mapping.correlation_type.value}"')
        
        return "\n".join(csv_lines)
    
    def _elements_to_csv(self, elements: List[ElementInfo]) -> str:
        """元素转CSV"""
        csv_lines = ["element_id,element_type,locator,line_number"]
        
        for element in elements:
            csv_lines.append(f'"{element.element_id}","{element.element_type.value}",'
                           f'"{element.locator}",{element.line_number}')
        
        return "\n".join(csv_lines)
    
    def _get_html_template(self) -> str:
        """获取HTML模板"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        .content {{ background: #f9f9f9; padding: 15px; border-radius: 3px; }}
        pre {{ white-space: pre-wrap; word-wrap: break-word; }}
        .metadata {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="timestamp">生成时间: {generated_at}</div>
    
    <div class="metadata">
        <h3>报告元数据</h3>
        {metadata}
    </div>
    
    {sections}
</body>
</html>
        """
    
    def _get_json_template(self) -> str:
        """获取JSON模板"""
        return "{}"  # JSON不需要模板
    
    def _get_markdown_template(self) -> str:
        """获取Markdown模板"""
        return ""  # Markdown不需要模板
    
    def export_report(self, report: Report, format: str = "markdown") -> str:
        """
        导出报告
        
        Args:
            report: 报告对象
            format: 导出格式
            
        Returns:
            导出的报告内容
        """
        if format.lower() == "html":
            return self._generate_html_report(report)
        elif format.lower() == "json":
            return self._generate_json_report(report)
        elif format.lower() == "markdown":
            return self._generate_markdown_report(report)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def validate_report_data(self, data: Dict[str, Any]) -> bool:
        """
        验证报告数据
        
        Args:
            data: 报告数据
            
        Returns:
            验证结果
        """
        if not isinstance(data, dict):
            return False
        
        # 检查必要的字段
        required_fields = ['title', 'sections']
        for field in required_fields:
            if field not in data:
                return False
        
        # 验证sections格式
        sections = data.get('sections', [])
        if not isinstance(sections, list):
            return False
        
        for section in sections:
            if not isinstance(section, dict):
                return False
            if 'title' not in section or 'content' not in section:
                return False
        
        # 验证metadata（如果存在）
        metadata = data.get('metadata', {})
        if metadata and not isinstance(metadata, dict):
            return False
        
        return True
    
    def generate_report(self, report_type: str, data: Dict[str, Any], 
                       output_path: str = None) -> Report:
        """
        生成报告（实现IReportGenerator接口）
        
        Args:
            report_type: 报告类型
            data: 报告数据
            output_path: 输出路径
            
        Returns:
            报告对象
        """
        # 验证数据
        if not self.validate_report_data(data):
            raise ValueError("报告数据验证失败")
        
        # 创建报告对象
        report = Report(
            title=data.get('title', f'{report_type}报告'),
            report_type=report_type,
            sections=[
                ReportSection(
                    title=section.get('title', ''),
                    content=section.get('content', ''),
                    data=section.get('data', {})
                ) for section in data.get('sections', [])
            ],
            metadata=data.get('metadata', {}),
            timestamp=datetime.now()
        )
        
        # 如果指定了输出路径，保存报告
        if output_path:
            content = self.export_report(report, format="html")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return report