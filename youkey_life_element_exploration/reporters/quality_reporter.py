# -*- encoding=utf8 -*-
"""
质量报告生成器

提供元素质量分析报告的生成功能
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

from ..metrics.element_quality_metrics import ElementQualityMetrics, QualityScore
from ..analyzers.quality_analyzer import QualityAnalyzer, QualityAnalysisResult


class ReportFormat(Enum):
    """报告格式"""
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"
    CSV = "csv"


class ReportLevel(Enum):
    """报告详细程度"""
    SUMMARY = "summary"      # 摘要
    DETAILED = "detailed"    # 详细
    COMPREHENSIVE = "comprehensive"  # 全面


class ReportScope(Enum):
    """报告范围"""
    SINGLE_ELEMENT = "single_element"    # 单个元素
    MULTIPLE_ELEMENTS = "multiple_elements"  # 多个元素
    CATEGORY = "category"                # 分类
    GLOBAL = "global"                    # 全局


@dataclass
class ReportSection:
    """报告章节"""
    title: str
    content: str
    data: Dict[str, Any] = field(default_factory=dict)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    order: int = 0


@dataclass
class ReportMetadata:
    """报告元数据"""
    title: str
    description: str
    generated_at: datetime
    generated_by: str
    version: str
    scope: ReportScope
    level: ReportLevel
    format: ReportFormat
    elements_count: int
    time_range: Optional[Dict[str, datetime]] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class QualityReport:
    """质量报告"""
    metadata: ReportMetadata
    sections: List[ReportSection]
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    attachments: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'metadata': {
                'title': self.metadata.title,
                'description': self.metadata.description,
                'generated_at': self.metadata.generated_at.isoformat(),
                'generated_by': self.metadata.generated_by,
                'version': self.metadata.version,
                'scope': self.metadata.scope.value,
                'level': self.metadata.level.value,
                'format': self.metadata.format.value,
                'elements_count': self.metadata.elements_count,
                'time_range': {
                    k: v.isoformat() if v else None 
                    for k, v in (self.metadata.time_range or {}).items()
                },
                'filters': self.metadata.filters,
                'tags': self.metadata.tags
            },
            'sections': [
                {
                    'title': section.title,
                    'content': section.content,
                    'data': section.data,
                    'charts': section.charts,
                    'tables': section.tables,
                    'order': section.order
                }
                for section in self.sections
            ],
            'summary': self.summary,
            'recommendations': self.recommendations,
            'attachments': self.attachments
        }


class QualityReporter:
    """质量报告生成器"""
    
    def __init__(self):
        self.quality_analyzer = QualityAnalyzer()
        self.report_templates = self._init_templates()
        self.report_history: List[QualityReport] = []
    
    def _init_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化报告模板"""
        return {
            'single_element': {
                'sections': [
                    'element_overview',
                    'quality_scores',
                    'quality_trends',
                    'issues_analysis',
                    'recommendations'
                ]
            },
            'multiple_elements': {
                'sections': [
                    'elements_overview',
                    'quality_comparison',
                    'quality_distribution',
                    'common_issues',
                    'improvement_priorities'
                ]
            },
            'category': {
                'sections': [
                    'category_overview',
                    'quality_statistics',
                    'performance_analysis',
                    'trend_analysis',
                    'optimization_suggestions'
                ]
            },
            'global': {
                'sections': [
                    'global_overview',
                    'quality_dashboard',
                    'trend_analysis',
                    'category_comparison',
                    'strategic_recommendations'
                ]
            }
        }
    
    def generate_single_element_report(
        self,
        element_id: str,
        analysis_result: QualityAnalysisResult,
        level: ReportLevel = ReportLevel.DETAILED,
        format: ReportFormat = ReportFormat.JSON
    ) -> QualityReport:
        """生成单个元素质量报告"""
        
        metadata = ReportMetadata(
            title=f"元素质量报告 - {element_id}",
            description=f"元素 {element_id} 的详细质量分析报告",
            generated_at=datetime.now(),
            generated_by="QualityReporter",
            version="1.0",
            scope=ReportScope.SINGLE_ELEMENT,
            level=level,
            format=format,
            elements_count=1,
            tags=[element_id, "quality", "analysis"]
        )
        
        sections = []
        
        # 元素概览
        sections.append(self._create_element_overview_section(element_id, analysis_result))
        
        # 质量分数
        sections.append(self._create_quality_scores_section(analysis_result))
        
        # 质量趋势
        if level in [ReportLevel.DETAILED, ReportLevel.COMPREHENSIVE]:
            sections.append(self._create_quality_trends_section(analysis_result))
        
        # 问题分析
        sections.append(self._create_issues_analysis_section(analysis_result))
        
        # 建议
        sections.append(self._create_recommendations_section(analysis_result))
        
        # 如果是全面报告，添加更多章节
        if level == ReportLevel.COMPREHENSIVE:
            sections.append(self._create_detailed_metrics_section(analysis_result))
            sections.append(self._create_historical_comparison_section(analysis_result))
        
        # 生成摘要
        summary = self._generate_single_element_summary(analysis_result)
        
        # 生成建议
        recommendations = self._extract_recommendations(analysis_result)
        
        report = QualityReport(
            metadata=metadata,
            sections=sections,
            summary=summary,
            recommendations=recommendations
        )
        
        self.report_history.append(report)
        return report
    
    def generate_multiple_elements_report(
        self,
        elements_data: Dict[str, QualityAnalysisResult],
        level: ReportLevel = ReportLevel.DETAILED,
        format: ReportFormat = ReportFormat.JSON
    ) -> QualityReport:
        """生成多个元素质量对比报告"""
        
        metadata = ReportMetadata(
            title="多元素质量对比报告",
            description=f"包含 {len(elements_data)} 个元素的质量对比分析",
            generated_at=datetime.now(),
            generated_by="QualityReporter",
            version="1.0",
            scope=ReportScope.MULTIPLE_ELEMENTS,
            level=level,
            format=format,
            elements_count=len(elements_data),
            tags=["quality", "comparison", "multiple_elements"]
        )
        
        sections = []
        
        # 元素概览
        sections.append(self._create_elements_overview_section(elements_data))
        
        # 质量对比
        sections.append(self._create_quality_comparison_section(elements_data))
        
        # 质量分布
        sections.append(self._create_quality_distribution_section(elements_data))
        
        # 共同问题
        sections.append(self._create_common_issues_section(elements_data))
        
        # 改进优先级
        sections.append(self._create_improvement_priorities_section(elements_data))
        
        # 生成摘要
        summary = self._generate_multiple_elements_summary(elements_data)
        
        # 生成建议
        recommendations = self._generate_multiple_elements_recommendations(elements_data)
        
        report = QualityReport(
            metadata=metadata,
            sections=sections,
            summary=summary,
            recommendations=recommendations
        )
        
        self.report_history.append(report)
        return report
    
    def generate_category_report(
        self,
        category: str,
        elements_data: Dict[str, QualityAnalysisResult],
        level: ReportLevel = ReportLevel.DETAILED,
        format: ReportFormat = ReportFormat.JSON
    ) -> QualityReport:
        """生成分类质量报告"""
        
        metadata = ReportMetadata(
            title=f"分类质量报告 - {category}",
            description=f"分类 {category} 的质量分析报告",
            generated_at=datetime.now(),
            generated_by="QualityReporter",
            version="1.0",
            scope=ReportScope.CATEGORY,
            level=level,
            format=format,
            elements_count=len(elements_data),
            tags=[category, "quality", "category"]
        )
        
        sections = []
        
        # 分类概览
        sections.append(self._create_category_overview_section(category, elements_data))
        
        # 质量统计
        sections.append(self._create_quality_statistics_section(elements_data))
        
        # 性能分析
        sections.append(self._create_performance_analysis_section(elements_data))
        
        # 趋势分析
        if level in [ReportLevel.DETAILED, ReportLevel.COMPREHENSIVE]:
            sections.append(self._create_trend_analysis_section(elements_data))
        
        # 优化建议
        sections.append(self._create_optimization_suggestions_section(elements_data))
        
        # 生成摘要
        summary = self._generate_category_summary(category, elements_data)
        
        # 生成建议
        recommendations = self._generate_category_recommendations(category, elements_data)
        
        report = QualityReport(
            metadata=metadata,
            sections=sections,
            summary=summary,
            recommendations=recommendations
        )
        
        self.report_history.append(report)
        return report
    
    def _create_element_overview_section(
        self, 
        element_id: str, 
        analysis_result: QualityAnalysisResult
    ) -> ReportSection:
        """创建元素概览章节"""
        
        content = f"""
        ## 元素概览
        
        **元素ID**: {element_id}
        **整体质量分数**: {analysis_result.overall_score:.2f}
        **质量等级**: {analysis_result.quality_level.value}
        **分析时间**: {analysis_result.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}
        
        ### 质量维度分数
        """
        
        for dimension, score in analysis_result.dimension_scores.items():
            content += f"- **{dimension}**: {score:.2f}\n"
        
        data = {
            'element_id': element_id,
            'overall_score': analysis_result.overall_score,
            'quality_level': analysis_result.quality_level.value,
            'dimension_scores': analysis_result.dimension_scores,
            'analysis_time': analysis_result.analysis_time.isoformat()
        }
        
        # 创建质量分数雷达图
        charts = [{
            'type': 'radar',
            'title': '质量维度雷达图',
            'data': {
                'dimensions': list(analysis_result.dimension_scores.keys()),
                'scores': list(analysis_result.dimension_scores.values())
            }
        }]
        
        return ReportSection(
            title="元素概览",
            content=content,
            data=data,
            charts=charts,
            order=1
        )
    
    def _create_quality_scores_section(
        self, 
        analysis_result: QualityAnalysisResult
    ) -> ReportSection:
        """创建质量分数章节"""
        
        content = f"""
        ## 质量分数详情
        
        ### 整体评估
        - **总分**: {analysis_result.overall_score:.2f}/100
        - **等级**: {analysis_result.quality_level.value}
        - **置信度**: {analysis_result.confidence:.2f}
        
        ### 维度分析
        """
        
        # 创建分数表格
        table_data = []
        for dimension, score in analysis_result.dimension_scores.items():
            grade = self._score_to_grade(score)
            table_data.append({
                'dimension': dimension,
                'score': f"{score:.2f}",
                'grade': grade,
                'status': self._get_score_status(score)
            })
        
        tables = [{
            'title': '质量维度详情',
            'headers': ['维度', '分数', '等级', '状态'],
            'data': table_data
        }]
        
        # 创建分数分布图
        charts = [{
            'type': 'bar',
            'title': '质量维度分数分布',
            'data': {
                'dimensions': list(analysis_result.dimension_scores.keys()),
                'scores': list(analysis_result.dimension_scores.values())
            }
        }]
        
        data = {
            'overall_score': analysis_result.overall_score,
            'quality_level': analysis_result.quality_level.value,
            'confidence': analysis_result.confidence,
            'dimension_scores': analysis_result.dimension_scores
        }
        
        return ReportSection(
            title="质量分数",
            content=content,
            data=data,
            charts=charts,
            tables=tables,
            order=2
        )
    
    def _create_issues_analysis_section(
        self, 
        analysis_result: QualityAnalysisResult
    ) -> ReportSection:
        """创建问题分析章节"""
        
        content = f"""
        ## 问题分析
        
        ### 发现的问题
        共发现 {len(analysis_result.issues)} 个问题
        """
        
        if analysis_result.issues:
            content += "\n#### 问题列表\n"
            for i, issue in enumerate(analysis_result.issues, 1):
                content += f"{i}. **{issue.title}** ({issue.severity.value})\n"
                content += f"   - 描述: {issue.description}\n"
                content += f"   - 影响: {issue.impact}\n"
                if issue.suggestion:
                    content += f"   - 建议: {issue.suggestion}\n"
                content += "\n"
        else:
            content += "\n✅ 未发现明显问题\n"
        
        # 创建问题统计表
        severity_count = {}
        for issue in analysis_result.issues:
            severity = issue.severity.value
            severity_count[severity] = severity_count.get(severity, 0) + 1
        
        table_data = [
            {'severity': severity, 'count': count}
            for severity, count in severity_count.items()
        ]
        
        tables = [{
            'title': '问题严重程度统计',
            'headers': ['严重程度', '数量'],
            'data': table_data
        }] if table_data else []
        
        # 创建问题分布图
        charts = [{
            'type': 'pie',
            'title': '问题严重程度分布',
            'data': severity_count
        }] if severity_count else []
        
        data = {
            'issues_count': len(analysis_result.issues),
            'issues': [
                {
                    'title': issue.title,
                    'description': issue.description,
                    'severity': issue.severity.value,
                    'impact': issue.impact,
                    'suggestion': issue.suggestion
                }
                for issue in analysis_result.issues
            ],
            'severity_distribution': severity_count
        }
        
        return ReportSection(
            title="问题分析",
            content=content,
            data=data,
            charts=charts,
            tables=tables,
            order=3
        )
    
    def _create_recommendations_section(
        self, 
        analysis_result: QualityAnalysisResult
    ) -> ReportSection:
        """创建建议章节"""
        
        content = """
        ## 改进建议
        
        基于质量分析结果，提供以下改进建议：
        
        """
        
        if analysis_result.recommendations:
            for i, rec in enumerate(analysis_result.recommendations, 1):
                content += f"{i}. {rec}\n"
        else:
            content += "当前质量状况良好，暂无特殊建议。\n"
        
        # 添加通用建议
        content += "\n### 通用建议\n"
        content += "- 定期进行质量检查\n"
        content += "- 关注用户反馈\n"
        content += "- 持续优化性能\n"
        
        data = {
            'recommendations': analysis_result.recommendations,
            'recommendations_count': len(analysis_result.recommendations)
        }
        
        return ReportSection(
            title="改进建议",
            content=content,
            data=data,
            order=4
        )
    
    def _create_elements_overview_section(
        self, 
        elements_data: Dict[str, QualityAnalysisResult]
    ) -> ReportSection:
        """创建多元素概览章节"""
        
        total_elements = len(elements_data)
        avg_score = sum(result.overall_score for result in elements_data.values()) / total_elements
        
        content = f"""
        ## 元素概览
        
        **元素总数**: {total_elements}
        **平均质量分数**: {avg_score:.2f}
        
        ### 元素列表
        """
        
        # 创建元素列表表格
        table_data = []
        for element_id, result in elements_data.items():
            table_data.append({
                'element_id': element_id,
                'score': f"{result.overall_score:.2f}",
                'level': result.quality_level.value,
                'issues': len(result.issues)
            })
        
        # 按分数排序
        table_data.sort(key=lambda x: float(x['score']), reverse=True)
        
        tables = [{
            'title': '元素质量排名',
            'headers': ['元素ID', '分数', '等级', '问题数'],
            'data': table_data
        }]
        
        data = {
            'total_elements': total_elements,
            'average_score': avg_score,
            'elements': table_data
        }
        
        return ReportSection(
            title="元素概览",
            content=content,
            data=data,
            tables=tables,
            order=1
        )
    
    def _generate_single_element_summary(
        self, 
        analysis_result: QualityAnalysisResult
    ) -> Dict[str, Any]:
        """生成单元素报告摘要"""
        
        return {
            'overall_score': analysis_result.overall_score,
            'quality_level': analysis_result.quality_level.value,
            'issues_count': len(analysis_result.issues),
            'recommendations_count': len(analysis_result.recommendations),
            'confidence': analysis_result.confidence,
            'key_strengths': self._identify_strengths(analysis_result),
            'key_weaknesses': self._identify_weaknesses(analysis_result),
            'priority_actions': self._identify_priority_actions(analysis_result)
        }
    
    def _extract_recommendations(
        self, 
        analysis_result: QualityAnalysisResult
    ) -> List[str]:
        """提取建议"""
        
        recommendations = list(analysis_result.recommendations)
        
        # 基于问题添加建议
        for issue in analysis_result.issues:
            if issue.suggestion and issue.suggestion not in recommendations:
                recommendations.append(issue.suggestion)
        
        return recommendations
    
    def _score_to_grade(self, score: float) -> str:
        """分数转等级"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _get_score_status(self, score: float) -> str:
        """获取分数状态"""
        if score >= 80:
            return "优秀"
        elif score >= 60:
            return "良好"
        elif score >= 40:
            return "一般"
        else:
            return "需改进"
    
    def _identify_strengths(self, analysis_result: QualityAnalysisResult) -> List[str]:
        """识别优势"""
        strengths = []
        for dimension, score in analysis_result.dimension_scores.items():
            if score >= 80:
                strengths.append(f"{dimension}表现优秀")
        return strengths
    
    def _identify_weaknesses(self, analysis_result: QualityAnalysisResult) -> List[str]:
        """识别弱点"""
        weaknesses = []
        for dimension, score in analysis_result.dimension_scores.items():
            if score < 60:
                weaknesses.append(f"{dimension}需要改进")
        return weaknesses
    
    def _identify_priority_actions(self, analysis_result: QualityAnalysisResult) -> List[str]:
        """识别优先行动"""
        actions = []
        
        # 基于严重问题
        critical_issues = [
            issue for issue in analysis_result.issues 
            if issue.severity.value in ['critical', 'high']
        ]
        
        for issue in critical_issues[:3]:  # 最多3个优先行动
            if issue.suggestion:
                actions.append(issue.suggestion)
        
        return actions
    
    def export_report(
        self, 
        report: QualityReport, 
        file_path: str,
        format: Optional[ReportFormat] = None
    ) -> bool:
        """导出报告"""
        
        export_format = format or report.metadata.format
        
        try:
            if export_format == ReportFormat.JSON:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            
            elif export_format == ReportFormat.MARKDOWN:
                content = self._convert_to_markdown(report)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            elif export_format == ReportFormat.HTML:
                content = self._convert_to_html(report)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            else:
                raise ValueError(f"不支持的导出格式: {export_format}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"导出报告失败: {e}")
            return False
    
    def _convert_to_markdown(self, report: QualityReport) -> str:
        """转换为Markdown格式"""
        
        content = f"# {report.metadata.title}\n\n"
        content += f"{report.metadata.description}\n\n"
        content += f"**生成时间**: {report.metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 添加摘要
        if report.summary:
            content += "## 摘要\n\n"
            for key, value in report.summary.items():
                content += f"- **{key}**: {value}\n"
            content += "\n"
        
        # 添加各章节
        for section in sorted(report.sections, key=lambda x: x.order):
            content += section.content + "\n\n"
        
        # 添加建议
        if report.recommendations:
            content += "## 总体建议\n\n"
            for i, rec in enumerate(report.recommendations, 1):
                content += f"{i}. {rec}\n"
        
        return content
    
    def _convert_to_html(self, report: QualityReport) -> str:
        """转换为HTML格式"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{report.metadata.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2, h3 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .summary {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>{report.metadata.title}</h1>
            <p>{report.metadata.description}</p>
            <p><strong>生成时间</strong>: {report.metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        # 添加摘要
        if report.summary:
            html += '<div class="summary"><h2>摘要</h2><ul>'
            for key, value in report.summary.items():
                html += f'<li><strong>{key}</strong>: {value}</li>'
            html += '</ul></div>'
        
        # 添加各章节
        for section in sorted(report.sections, key=lambda x: x.order):
            html += f'<div class="section">{section.content}</div>'
        
        html += '</body></html>'
        return html
    
    def get_report_history(self) -> List[QualityReport]:
        """获取报告历史"""
        return self.report_history.copy()
    
    def clear_report_history(self):
        """清空报告历史"""
        self.report_history.clear()