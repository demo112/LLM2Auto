# -*- encoding=utf8 -*-
"""
统一报告模块

合并多个报告器的功能，提供统一的报告生成接口
"""

import json
import csv
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import statistics


@dataclass
class ReportSection:
    """报告章节"""
    title: str
    content: str
    data: Any = None
    charts: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportConfig:
    """报告配置"""
    title: str = "分析报告"
    format: str = "html"  # html, json, csv, txt
    include_charts: bool = True
    include_summary: bool = True
    include_details: bool = True
    template: str = "default"


@dataclass
class UnifiedReport:
    """统一报告"""
    title: str
    generated_at: datetime
    sections: List[ReportSection] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedReporter:
    """统一报告器"""
    
    def __init__(self, config: ReportConfig = None):
        self.config = config or ReportConfig()
        self.report = UnifiedReport(
            title=self.config.title,
            generated_at=datetime.now()
        )
    
    def add_section(self, title: str, content: str, data: Any = None, 
                   charts: List[Dict] = None) -> None:
        """添加报告章节"""
        section = ReportSection(
            title=title,
            content=content,
            data=data,
            charts=charts or []
        )
        self.report.sections.append(section)
    
    def add_summary(self, key: str, value: Any) -> None:
        """添加摘要信息"""
        self.report.summary[key] = value
    
    def add_metadata(self, key: str, value: Any) -> None:
        """添加元数据"""
        self.report.metadata[key] = value
    
    def generate_analysis_report(self, analysis_results: List[Dict]) -> UnifiedReport:
        """生成分析报告"""
        if not analysis_results:
            self.add_section("分析结果", "没有分析数据")
            return self.report
        
        # 总体统计
        total_count = len(analysis_results)
        success_count = sum(1 for r in analysis_results if r.get('success', False))
        
        self.add_summary("总分析数", total_count)
        self.add_summary("成功数", success_count)
        self.add_summary("成功率", f"{(success_count/total_count)*100:.1f}%" if total_count > 0 else "0%")
        
        # 分析概览
        overview_content = f"""
        本次分析共处理 {total_count} 个项目，其中：
        - 成功分析：{success_count} 个
        - 失败分析：{total_count - success_count} 个
        - 成功率：{(success_count/total_count)*100:.1f}%
        """
        self.add_section("分析概览", overview_content.strip())
        
        # 详细结果
        if self.config.include_details:
            for i, result in enumerate(analysis_results[:10]):  # 限制显示前10个
                title = f"分析结果 {i+1}"
                content = self._format_analysis_result(result)
                self.add_section(title, content, result)
        
        # 统计图表
        if self.config.include_charts:
            chart_data = self._generate_analysis_charts(analysis_results)
            self.add_section("统计图表", "分析结果统计图表", charts=chart_data)
        
        return self.report
    
    def generate_quality_report(self, quality_data: Dict) -> UnifiedReport:
        """生成质量报告"""
        # 质量摘要
        overall_score = quality_data.get('overall_score', 0)
        self.add_summary("整体质量分数", f"{overall_score:.1f}")
        
        # 质量维度
        dimensions = quality_data.get('dimensions', {})
        for dim, score in dimensions.items():
            self.add_summary(f"{dim}分数", f"{score:.1f}")
        
        # 质量概览
        overview_content = f"""
        质量评估结果：
        - 整体分数：{overall_score:.1f}/100
        - 评估维度：{len(dimensions)} 个
        - 主要问题：{len(quality_data.get('issues', []))} 个
        """
        self.add_section("质量概览", overview_content.strip())
        
        # 问题详情
        issues = quality_data.get('issues', [])
        if issues:
            issues_content = "\n".join([
                f"- {issue.get('type', '未知')}: {issue.get('description', '无描述')}"
                for issue in issues[:20]  # 限制显示前20个
            ])
            self.add_section("主要问题", issues_content, issues)
        
        # 改进建议
        recommendations = quality_data.get('recommendations', [])
        if recommendations:
            rec_content = "\n".join([
                f"- {rec}" for rec in recommendations[:10]  # 限制显示前10个
            ])
            self.add_section("改进建议", rec_content)
        
        return self.report
    
    def generate_trend_report(self, trend_data: List[Dict]) -> UnifiedReport:
        """生成趋势报告"""
        if not trend_data:
            self.add_section("趋势分析", "没有趋势数据")
            return self.report
        
        # 趋势摘要
        trend_count = len(trend_data)
        positive_trends = sum(1 for t in trend_data if t.get('direction') == 'up')
        negative_trends = sum(1 for t in trend_data if t.get('direction') == 'down')
        
        self.add_summary("趋势数量", trend_count)
        self.add_summary("上升趋势", positive_trends)
        self.add_summary("下降趋势", negative_trends)
        
        # 趋势概览
        overview_content = f"""
        趋势分析结果：
        - 总趋势数：{trend_count}
        - 上升趋势：{positive_trends} 个
        - 下降趋势：{negative_trends} 个
        - 稳定趋势：{trend_count - positive_trends - negative_trends} 个
        """
        self.add_section("趋势概览", overview_content.strip())
        
        # 重要趋势
        important_trends = [t for t in trend_data if t.get('confidence', 0) > 0.7]
        if important_trends:
            trends_content = "\n".join([
                f"- {t.get('metric', '未知指标')}: {t.get('direction', '未知')} "
                f"(置信度: {t.get('confidence', 0):.1%})"
                for t in important_trends[:15]  # 限制显示前15个
            ])
            self.add_section("重要趋势", trends_content, important_trends)
        
        return self.report
    
    def generate_performance_report(self, perf_data: Dict) -> UnifiedReport:
        """生成性能报告"""
        # 性能摘要
        avg_response_time = perf_data.get('avg_response_time', 0)
        throughput = perf_data.get('throughput', 0)
        error_rate = perf_data.get('error_rate', 0)
        
        self.add_summary("平均响应时间", f"{avg_response_time:.2f}ms")
        self.add_summary("吞吐量", f"{throughput:.1f} req/s")
        self.add_summary("错误率", f"{error_rate:.2%}")
        
        # 性能概览
        overview_content = f"""
        性能测试结果：
        - 平均响应时间：{avg_response_time:.2f}ms
        - 吞吐量：{throughput:.1f} 请求/秒
        - 错误率：{error_rate:.2%}
        - 测试持续时间：{perf_data.get('duration', 0):.1f}秒
        """
        self.add_section("性能概览", overview_content.strip())
        
        # 性能指标
        metrics = perf_data.get('metrics', {})
        if metrics:
            metrics_content = "\n".join([
                f"- {key}: {value}" for key, value in metrics.items()
            ])
            self.add_section("详细指标", metrics_content, metrics)
        
        return self.report
    
    def export_report(self, output_path: str) -> bool:
        """导出报告"""
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.config.format == "html":
                content = self._generate_html_report()
            elif self.config.format == "json":
                content = self._generate_json_report()
            elif self.config.format == "csv":
                content = self._generate_csv_report()
            else:  # txt
                content = self._generate_text_report()
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"导出报告失败: {e}")
            return False
    
    def _format_analysis_result(self, result: Dict) -> str:
        """格式化分析结果"""
        lines = []
        
        if result.get('success'):
            lines.append("✅ 分析成功")
        else:
            lines.append("❌ 分析失败")
        
        if 'score' in result:
            lines.append(f"分数: {result['score']:.1f}")
        
        if 'message' in result:
            lines.append(f"消息: {result['message']}")
        
        if 'details' in result:
            details = result['details']
            if isinstance(details, dict):
                for key, value in details.items():
                    lines.append(f"{key}: {value}")
        
        return "\n".join(lines)
    
    def _generate_analysis_charts(self, results: List[Dict]) -> List[Dict]:
        """生成分析图表数据"""
        charts = []
        
        # 成功率饼图
        success_count = sum(1 for r in results if r.get('success', False))
        fail_count = len(results) - success_count
        
        charts.append({
            'type': 'pie',
            'title': '分析成功率',
            'data': {
                'labels': ['成功', '失败'],
                'values': [success_count, fail_count]
            }
        })
        
        # 分数分布直方图
        scores = [r.get('score', 0) for r in results if 'score' in r]
        if scores:
            charts.append({
                'type': 'histogram',
                'title': '分数分布',
                'data': {
                    'values': scores,
                    'bins': 10
                }
            })
        
        return charts
    
    def _generate_html_report(self) -> str:
        """生成HTML报告"""
        html_parts = [
            "<!DOCTYPE html>",
            "<html><head>",
            f"<title>{self.report.title}</title>",
            "<meta charset='utf-8'>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 40px; }",
            "h1 { color: #333; border-bottom: 2px solid #007acc; }",
            "h2 { color: #555; margin-top: 30px; }",
            ".summary { background: #f5f5f5; padding: 15px; border-radius: 5px; }",
            ".section { margin: 20px 0; }",
            "pre { background: #f8f8f8; padding: 10px; border-radius: 3px; }",
            "</style>",
            "</head><body>",
            f"<h1>{self.report.title}</h1>",
            f"<p>生成时间: {self.report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>"
        ]
        
        # 摘要
        if self.report.summary and self.config.include_summary:
            html_parts.append("<div class='summary'><h2>摘要</h2>")
            for key, value in self.report.summary.items():
                html_parts.append(f"<p><strong>{key}:</strong> {value}</p>")
            html_parts.append("</div>")
        
        # 章节
        for section in self.report.sections:
            html_parts.append(f"<div class='section'><h2>{section.title}</h2>")
            html_parts.append(f"<pre>{section.content}</pre>")
            html_parts.append("</div>")
        
        html_parts.extend(["</body></html>"])
        return "\n".join(html_parts)
    
    def _generate_json_report(self) -> str:
        """生成JSON报告"""
        report_dict = {
            'title': self.report.title,
            'generated_at': self.report.generated_at.isoformat(),
            'summary': self.report.summary,
            'sections': [
                {
                    'title': s.title,
                    'content': s.content,
                    'data': s.data,
                    'charts': s.charts
                }
                for s in self.report.sections
            ],
            'metadata': self.report.metadata
        }
        return json.dumps(report_dict, indent=2, ensure_ascii=False, default=str)
    
    def _generate_csv_report(self) -> str:
        """生成CSV报告"""
        lines = [f"# {self.report.title}"]
        lines.append(f"# 生成时间: {self.report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 摘要
        if self.report.summary:
            lines.append("# 摘要")
            for key, value in self.report.summary.items():
                lines.append(f"{key},{value}")
            lines.append("")
        
        # 章节
        for section in self.report.sections:
            lines.append(f"# {section.title}")
            lines.append(section.content.replace('\n', ' | '))
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_text_report(self) -> str:
        """生成文本报告"""
        lines = [
            f"{self.report.title}",
            "=" * len(self.report.title),
            f"生成时间: {self.report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # 摘要
        if self.report.summary and self.config.include_summary:
            lines.extend(["摘要", "-" * 20])
            for key, value in self.report.summary.items():
                lines.append(f"{key}: {value}")
            lines.append("")
        
        # 章节
        for section in self.report.sections:
            lines.extend([
                section.title,
                "-" * len(section.title),
                section.content,
                ""
            ])
        
        return "\n".join(lines)