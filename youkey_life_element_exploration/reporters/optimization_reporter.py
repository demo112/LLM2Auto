# -*- encoding=utf8 -*-
"""
优化报告生成器

提供优化过程和结果的报告生成功能
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

from ..optimizers.element_optimizer import ElementOptimizer, ElementOptimizationResult
from ..optimizers.strategy_optimizer import StrategyOptimizer, StrategyOptimizationResult
from ..optimizers.resource_optimizer import ResourceOptimizer, ResourceOptimizationResult


class OptimizationReportType(Enum):
    """优化报告类型"""
    ELEMENT = "element"          # 元素优化报告
    STRATEGY = "strategy"        # 策略优化报告
    RESOURCE = "resource"        # 资源优化报告
    COMPREHENSIVE = "comprehensive"  # 综合优化报告


class ReportTimeframe(Enum):
    """报告时间范围"""
    REAL_TIME = "real_time"      # 实时
    DAILY = "daily"              # 日报
    WEEKLY = "weekly"            # 周报
    MONTHLY = "monthly"          # 月报
    QUARTERLY = "quarterly"      # 季报


@dataclass
class OptimizationMetrics:
    """优化指标"""
    total_optimizations: int
    successful_optimizations: int
    failed_optimizations: int
    success_rate: float
    average_improvement: float
    total_time_saved: float
    cost_reduction: float
    performance_gain: float
    
    @property
    def failure_rate(self) -> float:
        return 1.0 - self.success_rate


@dataclass
class OptimizationTrend:
    """优化趋势"""
    period: str
    metrics: OptimizationMetrics
    comparison_period: Optional[str] = None
    change_percentage: Optional[float] = None
    trend_direction: Optional[str] = None  # "up", "down", "stable"


@dataclass
class OptimizationInsight:
    """优化洞察"""
    title: str
    description: str
    impact: str
    confidence: float
    category: str
    recommendations: List[str] = field(default_factory=list)
    data_points: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationReportData:
    """优化报告数据"""
    report_type: OptimizationReportType
    timeframe: ReportTimeframe
    start_time: datetime
    end_time: datetime
    metrics: OptimizationMetrics
    trends: List[OptimizationTrend] = field(default_factory=list)
    insights: List[OptimizationInsight] = field(default_factory=list)
    element_results: List[ElementOptimizationResult] = field(default_factory=list)
    strategy_results: List[StrategyOptimizationResult] = field(default_factory=list)
    resource_results: List[ResourceOptimizationResult] = field(default_factory=list)


@dataclass
class OptimizationReport:
    """优化报告"""
    metadata: Dict[str, Any]
    data: OptimizationReportData
    sections: List[Dict[str, Any]] = field(default_factory=list)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'metadata': self.metadata,
            'data': {
                'report_type': self.data.report_type.value,
                'timeframe': self.data.timeframe.value,
                'start_time': self.data.start_time.isoformat(),
                'end_time': self.data.end_time.isoformat(),
                'metrics': {
                    'total_optimizations': self.data.metrics.total_optimizations,
                    'successful_optimizations': self.data.metrics.successful_optimizations,
                    'failed_optimizations': self.data.metrics.failed_optimizations,
                    'success_rate': self.data.metrics.success_rate,
                    'average_improvement': self.data.metrics.average_improvement,
                    'total_time_saved': self.data.metrics.total_time_saved,
                    'cost_reduction': self.data.metrics.cost_reduction,
                    'performance_gain': self.data.metrics.performance_gain
                },
                'trends': [
                    {
                        'period': trend.period,
                        'metrics': {
                            'total_optimizations': trend.metrics.total_optimizations,
                            'success_rate': trend.metrics.success_rate,
                            'average_improvement': trend.metrics.average_improvement
                        },
                        'comparison_period': trend.comparison_period,
                        'change_percentage': trend.change_percentage,
                        'trend_direction': trend.trend_direction
                    }
                    for trend in self.data.trends
                ],
                'insights': [
                    {
                        'title': insight.title,
                        'description': insight.description,
                        'impact': insight.impact,
                        'confidence': insight.confidence,
                        'category': insight.category,
                        'recommendations': insight.recommendations
                    }
                    for insight in self.data.insights
                ]
            },
            'sections': self.sections,
            'charts': self.charts,
            'tables': self.tables,
            'recommendations': self.recommendations
        }


class OptimizationReporter:
    """优化报告生成器"""
    
    def __init__(self):
        self.optimization_history: List[OptimizationReport] = []
        self.metrics_cache: Dict[str, Any] = {}
    
    def generate_element_optimization_report(
        self,
        element_results: List[ElementOptimizationResult],
        timeframe: ReportTimeframe = ReportTimeframe.DAILY,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> OptimizationReport:
        """生成元素优化报告"""
        
        if not start_time:
            start_time = datetime.now() - timedelta(days=1)
        if not end_time:
            end_time = datetime.now()
        
        # 计算指标
        metrics = self._calculate_element_metrics(element_results)
        
        # 生成趋势
        trends = self._analyze_element_trends(element_results, timeframe)
        
        # 生成洞察
        insights = self._generate_element_insights(element_results, metrics)
        
        # 创建报告数据
        report_data = OptimizationReportData(
            report_type=OptimizationReportType.ELEMENT,
            timeframe=timeframe,
            start_time=start_time,
            end_time=end_time,
            metrics=metrics,
            trends=trends,
            insights=insights,
            element_results=element_results
        )
        
        # 生成报告
        report = self._create_optimization_report(
            title="元素优化报告",
            description="元素优化过程和结果的详细分析",
            data=report_data
        )
        
        self.optimization_history.append(report)
        return report
    
    def generate_strategy_optimization_report(
        self,
        strategy_results: List[StrategyOptimizationResult],
        timeframe: ReportTimeframe = ReportTimeframe.WEEKLY,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> OptimizationReport:
        """生成策略优化报告"""
        
        if not start_time:
            start_time = datetime.now() - timedelta(weeks=1)
        if not end_time:
            end_time = datetime.now()
        
        # 计算指标
        metrics = self._calculate_strategy_metrics(strategy_results)
        
        # 生成趋势
        trends = self._analyze_strategy_trends(strategy_results, timeframe)
        
        # 生成洞察
        insights = self._generate_strategy_insights(strategy_results, metrics)
        
        # 创建报告数据
        report_data = OptimizationReportData(
            report_type=OptimizationReportType.STRATEGY,
            timeframe=timeframe,
            start_time=start_time,
            end_time=end_time,
            metrics=metrics,
            trends=trends,
            insights=insights,
            strategy_results=strategy_results
        )
        
        # 生成报告
        report = self._create_optimization_report(
            title="策略优化报告",
            description="优化策略效果和性能分析",
            data=report_data
        )
        
        self.optimization_history.append(report)
        return report
    
    def generate_resource_optimization_report(
        self,
        resource_results: List[ResourceOptimizationResult],
        timeframe: ReportTimeframe = ReportTimeframe.DAILY,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> OptimizationReport:
        """生成资源优化报告"""
        
        if not start_time:
            start_time = datetime.now() - timedelta(days=1)
        if not end_time:
            end_time = datetime.now()
        
        # 计算指标
        metrics = self._calculate_resource_metrics(resource_results)
        
        # 生成趋势
        trends = self._analyze_resource_trends(resource_results, timeframe)
        
        # 生成洞察
        insights = self._generate_resource_insights(resource_results, metrics)
        
        # 创建报告数据
        report_data = OptimizationReportData(
            report_type=OptimizationReportType.RESOURCE,
            timeframe=timeframe,
            start_time=start_time,
            end_time=end_time,
            metrics=metrics,
            trends=trends,
            insights=insights,
            resource_results=resource_results
        )
        
        # 生成报告
        report = self._create_optimization_report(
            title="资源优化报告",
            description="资源分配和利用率优化分析",
            data=report_data
        )
        
        self.optimization_history.append(report)
        return report
    
    def generate_comprehensive_report(
        self,
        element_results: List[ElementOptimizationResult],
        strategy_results: List[StrategyOptimizationResult],
        resource_results: List[ResourceOptimizationResult],
        timeframe: ReportTimeframe = ReportTimeframe.WEEKLY,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> OptimizationReport:
        """生成综合优化报告"""
        
        if not start_time:
            start_time = datetime.now() - timedelta(weeks=1)
        if not end_time:
            end_time = datetime.now()
        
        # 计算综合指标
        metrics = self._calculate_comprehensive_metrics(
            element_results, strategy_results, resource_results
        )
        
        # 生成综合趋势
        trends = self._analyze_comprehensive_trends(
            element_results, strategy_results, resource_results, timeframe
        )
        
        # 生成综合洞察
        insights = self._generate_comprehensive_insights(
            element_results, strategy_results, resource_results, metrics
        )
        
        # 创建报告数据
        report_data = OptimizationReportData(
            report_type=OptimizationReportType.COMPREHENSIVE,
            timeframe=timeframe,
            start_time=start_time,
            end_time=end_time,
            metrics=metrics,
            trends=trends,
            insights=insights,
            element_results=element_results,
            strategy_results=strategy_results,
            resource_results=resource_results
        )
        
        # 生成报告
        report = self._create_optimization_report(
            title="综合优化报告",
            description="全面的优化过程和效果分析",
            data=report_data
        )
        
        self.optimization_history.append(report)
        return report
    
    def _calculate_element_metrics(
        self, 
        results: List[ElementOptimizationResult]
    ) -> OptimizationMetrics:
        """计算元素优化指标"""
        
        if not results:
            return OptimizationMetrics(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        success_rate = successful / total if total > 0 else 0.0
        
        # 计算平均改进
        improvements = [
            r.actual_improvement for r in results 
            if r.success and r.actual_improvement is not None
        ]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0
        
        # 计算时间节省（示例计算）
        time_saved = sum(
            r.execution_time for r in results 
            if r.success and r.execution_time is not None
        )
        
        return OptimizationMetrics(
            total_optimizations=total,
            successful_optimizations=successful,
            failed_optimizations=failed,
            success_rate=success_rate,
            average_improvement=avg_improvement,
            total_time_saved=time_saved,
            cost_reduction=0.0,  # 需要根据实际情况计算
            performance_gain=avg_improvement
        )
    
    def _calculate_strategy_metrics(
        self, 
        results: List[StrategyOptimizationResult]
    ) -> OptimizationMetrics:
        """计算策略优化指标"""
        
        if not results:
            return OptimizationMetrics(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        success_rate = successful / total if total > 0 else 0.0
        
        # 计算平均改进
        improvements = [
            r.improvement_percentage for r in results 
            if r.success and r.improvement_percentage is not None
        ]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0
        
        return OptimizationMetrics(
            total_optimizations=total,
            successful_optimizations=successful,
            failed_optimizations=failed,
            success_rate=success_rate,
            average_improvement=avg_improvement,
            total_time_saved=0.0,
            cost_reduction=0.0,
            performance_gain=avg_improvement
        )
    
    def _calculate_resource_metrics(
        self, 
        results: List[ResourceOptimizationResult]
    ) -> OptimizationMetrics:
        """计算资源优化指标"""
        
        if not results:
            return OptimizationMetrics(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        success_rate = successful / total if total > 0 else 0.0
        
        # 计算平均改进
        improvements = [
            r.efficiency_improvement for r in results 
            if r.success and r.efficiency_improvement is not None
        ]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0
        
        # 计算成本节省
        cost_savings = [
            r.cost_reduction for r in results 
            if r.success and r.cost_reduction is not None
        ]
        total_cost_reduction = sum(cost_savings) if cost_savings else 0.0
        
        return OptimizationMetrics(
            total_optimizations=total,
            successful_optimizations=successful,
            failed_optimizations=failed,
            success_rate=success_rate,
            average_improvement=avg_improvement,
            total_time_saved=0.0,
            cost_reduction=total_cost_reduction,
            performance_gain=avg_improvement
        )
    
    def _calculate_comprehensive_metrics(
        self,
        element_results: List[ElementOptimizationResult],
        strategy_results: List[StrategyOptimizationResult],
        resource_results: List[ResourceOptimizationResult]
    ) -> OptimizationMetrics:
        """计算综合优化指标"""
        
        element_metrics = self._calculate_element_metrics(element_results)
        strategy_metrics = self._calculate_strategy_metrics(strategy_results)
        resource_metrics = self._calculate_resource_metrics(resource_results)
        
        total = (element_metrics.total_optimizations + 
                strategy_metrics.total_optimizations + 
                resource_metrics.total_optimizations)
        
        successful = (element_metrics.successful_optimizations + 
                     strategy_metrics.successful_optimizations + 
                     resource_metrics.successful_optimizations)
        
        failed = total - successful
        success_rate = successful / total if total > 0 else 0.0
        
        # 加权平均改进
        total_improvements = 0.0
        total_weight = 0
        
        if element_metrics.total_optimizations > 0:
            total_improvements += (element_metrics.average_improvement * 
                                 element_metrics.total_optimizations)
            total_weight += element_metrics.total_optimizations
        
        if strategy_metrics.total_optimizations > 0:
            total_improvements += (strategy_metrics.average_improvement * 
                                 strategy_metrics.total_optimizations)
            total_weight += strategy_metrics.total_optimizations
        
        if resource_metrics.total_optimizations > 0:
            total_improvements += (resource_metrics.average_improvement * 
                                 resource_metrics.total_optimizations)
            total_weight += resource_metrics.total_optimizations
        
        avg_improvement = total_improvements / total_weight if total_weight > 0 else 0.0
        
        return OptimizationMetrics(
            total_optimizations=total,
            successful_optimizations=successful,
            failed_optimizations=failed,
            success_rate=success_rate,
            average_improvement=avg_improvement,
            total_time_saved=element_metrics.total_time_saved,
            cost_reduction=resource_metrics.cost_reduction,
            performance_gain=avg_improvement
        )
    
    def _analyze_element_trends(
        self, 
        results: List[ElementOptimizationResult], 
        timeframe: ReportTimeframe
    ) -> List[OptimizationTrend]:
        """分析元素优化趋势"""
        
        # 这里应该根据时间范围分组数据并分析趋势
        # 简化实现，返回当前周期的趋势
        current_metrics = self._calculate_element_metrics(results)
        
        return [OptimizationTrend(
            period=f"当前{timeframe.value}",
            metrics=current_metrics,
            trend_direction="stable"  # 需要与历史数据比较
        )]
    
    def _analyze_strategy_trends(
        self, 
        results: List[StrategyOptimizationResult], 
        timeframe: ReportTimeframe
    ) -> List[OptimizationTrend]:
        """分析策略优化趋势"""
        
        current_metrics = self._calculate_strategy_metrics(results)
        
        return [OptimizationTrend(
            period=f"当前{timeframe.value}",
            metrics=current_metrics,
            trend_direction="stable"
        )]
    
    def _analyze_resource_trends(
        self, 
        results: List[ResourceOptimizationResult], 
        timeframe: ReportTimeframe
    ) -> List[OptimizationTrend]:
        """分析资源优化趋势"""
        
        current_metrics = self._calculate_resource_metrics(results)
        
        return [OptimizationTrend(
            period=f"当前{timeframe.value}",
            metrics=current_metrics,
            trend_direction="stable"
        )]
    
    def _analyze_comprehensive_trends(
        self,
        element_results: List[ElementOptimizationResult],
        strategy_results: List[StrategyOptimizationResult],
        resource_results: List[ResourceOptimizationResult],
        timeframe: ReportTimeframe
    ) -> List[OptimizationTrend]:
        """分析综合优化趋势"""
        
        current_metrics = self._calculate_comprehensive_metrics(
            element_results, strategy_results, resource_results
        )
        
        return [OptimizationTrend(
            period=f"当前{timeframe.value}",
            metrics=current_metrics,
            trend_direction="stable"
        )]
    
    def _generate_element_insights(
        self, 
        results: List[ElementOptimizationResult], 
        metrics: OptimizationMetrics
    ) -> List[OptimizationInsight]:
        """生成元素优化洞察"""
        
        insights = []
        
        # 成功率洞察
        if metrics.success_rate >= 0.9:
            insights.append(OptimizationInsight(
                title="优化成功率优秀",
                description=f"元素优化成功率达到 {metrics.success_rate:.1%}，表现优秀",
                impact="positive",
                confidence=0.9,
                category="performance",
                recommendations=["继续保持当前优化策略"]
            ))
        elif metrics.success_rate < 0.7:
            insights.append(OptimizationInsight(
                title="优化成功率需要改进",
                description=f"元素优化成功率仅为 {metrics.success_rate:.1%}，需要改进",
                impact="negative",
                confidence=0.8,
                category="performance",
                recommendations=["检查优化策略", "分析失败原因", "调整优化参数"]
            ))
        
        # 改进幅度洞察
        if metrics.average_improvement > 20:
            insights.append(OptimizationInsight(
                title="优化效果显著",
                description=f"平均改进幅度达到 {metrics.average_improvement:.1f}%",
                impact="positive",
                confidence=0.85,
                category="effectiveness",
                recommendations=["扩大优化范围", "应用到更多元素"]
            ))
        
        return insights
    
    def _generate_strategy_insights(
        self, 
        results: List[StrategyOptimizationResult], 
        metrics: OptimizationMetrics
    ) -> List[OptimizationInsight]:
        """生成策略优化洞察"""
        
        insights = []
        
        # 策略效果分析
        if results:
            best_strategy = max(results, key=lambda x: x.improvement_percentage or 0)
            insights.append(OptimizationInsight(
                title="最佳策略识别",
                description=f"策略 {best_strategy.strategy_name} 表现最佳",
                impact="positive",
                confidence=0.8,
                category="strategy",
                recommendations=[f"推广使用 {best_strategy.strategy_name} 策略"]
            ))
        
        return insights
    
    def _generate_resource_insights(
        self, 
        results: List[ResourceOptimizationResult], 
        metrics: OptimizationMetrics
    ) -> List[OptimizationInsight]:
        """生成资源优化洞察"""
        
        insights = []
        
        # 成本节省洞察
        if metrics.cost_reduction > 0:
            insights.append(OptimizationInsight(
                title="成本节省效果",
                description=f"资源优化节省成本 {metrics.cost_reduction:.2f}",
                impact="positive",
                confidence=0.9,
                category="cost",
                recommendations=["继续优化资源分配"]
            ))
        
        return insights
    
    def _generate_comprehensive_insights(
        self,
        element_results: List[ElementOptimizationResult],
        strategy_results: List[StrategyOptimizationResult],
        resource_results: List[ResourceOptimizationResult],
        metrics: OptimizationMetrics
    ) -> List[OptimizationInsight]:
        """生成综合优化洞察"""
        
        insights = []
        
        # 综合效果洞察
        insights.append(OptimizationInsight(
            title="综合优化效果",
            description=f"整体优化成功率 {metrics.success_rate:.1%}，平均改进 {metrics.average_improvement:.1f}%",
            impact="neutral",
            confidence=0.85,
            category="overall",
            recommendations=["持续监控优化效果", "定期调整优化策略"]
        ))
        
        # 各模块对比
        element_count = len(element_results)
        strategy_count = len(strategy_results)
        resource_count = len(resource_results)
        
        total_count = element_count + strategy_count + resource_count
        
        if total_count > 0:
            dominant_type = max(
                [("元素", element_count), ("策略", strategy_count), ("资源", resource_count)],
                key=lambda x: x[1]
            )
            
            insights.append(OptimizationInsight(
                title="优化重点分析",
                description=f"{dominant_type[0]}优化占主导地位，共 {dominant_type[1]} 次",
                impact="neutral",
                confidence=0.7,
                category="distribution",
                recommendations=[f"平衡各类型优化的比例"]
            ))
        
        return insights
    
    def _create_optimization_report(
        self, 
        title: str, 
        description: str, 
        data: OptimizationReportData
    ) -> OptimizationReport:
        """创建优化报告"""
        
        metadata = {
            'title': title,
            'description': description,
            'generated_at': datetime.now().isoformat(),
            'generated_by': 'OptimizationReporter',
            'version': '1.0',
            'report_type': data.report_type.value,
            'timeframe': data.timeframe.value
        }
        
        # 创建章节
        sections = []
        
        # 执行摘要
        sections.append({
            'title': '执行摘要',
            'content': self._create_executive_summary(data),
            'order': 1
        })
        
        # 关键指标
        sections.append({
            'title': '关键指标',
            'content': self._create_metrics_section(data.metrics),
            'order': 2
        })
        
        # 趋势分析
        if data.trends:
            sections.append({
                'title': '趋势分析',
                'content': self._create_trends_section(data.trends),
                'order': 3
            })
        
        # 洞察分析
        if data.insights:
            sections.append({
                'title': '洞察分析',
                'content': self._create_insights_section(data.insights),
                'order': 4
            })
        
        # 创建图表
        charts = self._create_charts(data)
        
        # 创建表格
        tables = self._create_tables(data)
        
        # 生成建议
        recommendations = self._generate_recommendations(data)
        
        return OptimizationReport(
            metadata=metadata,
            data=data,
            sections=sections,
            charts=charts,
            tables=tables,
            recommendations=recommendations
        )
    
    def _create_executive_summary(self, data: OptimizationReportData) -> str:
        """创建执行摘要"""
        
        metrics = data.metrics
        
        summary = f"""
        ## 执行摘要
        
        在 {data.timeframe.value} 期间，共执行了 {metrics.total_optimizations} 次优化操作。
        
        ### 关键成果
        - **成功率**: {metrics.success_rate:.1%}
        - **平均改进**: {metrics.average_improvement:.1f}%
        - **成功优化**: {metrics.successful_optimizations} 次
        - **失败优化**: {metrics.failed_optimizations} 次
        
        ### 主要收益
        """
        
        if metrics.total_time_saved > 0:
            summary += f"- **时间节省**: {metrics.total_time_saved:.2f} 小时\n"
        
        if metrics.cost_reduction > 0:
            summary += f"- **成本节省**: {metrics.cost_reduction:.2f}\n"
        
        if metrics.performance_gain > 0:
            summary += f"- **性能提升**: {metrics.performance_gain:.1f}%\n"
        
        return summary
    
    def _create_metrics_section(self, metrics: OptimizationMetrics) -> str:
        """创建指标章节"""
        
        return f"""
        ## 关键指标
        
        ### 优化统计
        - **总优化次数**: {metrics.total_optimizations}
        - **成功次数**: {metrics.successful_optimizations}
        - **失败次数**: {metrics.failed_optimizations}
        - **成功率**: {metrics.success_rate:.1%}
        - **失败率**: {metrics.failure_rate:.1%}
        
        ### 效果指标
        - **平均改进幅度**: {metrics.average_improvement:.2f}%
        - **总时间节省**: {metrics.total_time_saved:.2f} 小时
        - **成本节省**: {metrics.cost_reduction:.2f}
        - **性能提升**: {metrics.performance_gain:.2f}%
        """
    
    def _create_trends_section(self, trends: List[OptimizationTrend]) -> str:
        """创建趋势章节"""
        
        content = "## 趋势分析\n\n"
        
        for trend in trends:
            content += f"### {trend.period}\n"
            content += f"- **优化次数**: {trend.metrics.total_optimizations}\n"
            content += f"- **成功率**: {trend.metrics.success_rate:.1%}\n"
            content += f"- **平均改进**: {trend.metrics.average_improvement:.1f}%\n"
            
            if trend.trend_direction:
                direction_text = {
                    "up": "上升",
                    "down": "下降", 
                    "stable": "稳定"
                }.get(trend.trend_direction, "未知")
                content += f"- **趋势**: {direction_text}\n"
            
            content += "\n"
        
        return content
    
    def _create_insights_section(self, insights: List[OptimizationInsight]) -> str:
        """创建洞察章节"""
        
        content = "## 洞察分析\n\n"
        
        for insight in insights:
            content += f"### {insight.title}\n"
            content += f"{insight.description}\n\n"
            content += f"**影响**: {insight.impact}\n"
            content += f"**置信度**: {insight.confidence:.1%}\n"
            content += f"**类别**: {insight.category}\n"
            
            if insight.recommendations:
                content += "\n**建议**:\n"
                for rec in insight.recommendations:
                    content += f"- {rec}\n"
            
            content += "\n"
        
        return content
    
    def _create_charts(self, data: OptimizationReportData) -> List[Dict[str, Any]]:
        """创建图表"""
        
        charts = []
        
        # 成功率饼图
        charts.append({
            'type': 'pie',
            'title': '优化成功率分布',
            'data': {
                '成功': data.metrics.successful_optimizations,
                '失败': data.metrics.failed_optimizations
            }
        })
        
        # 趋势线图
        if data.trends:
            charts.append({
                'type': 'line',
                'title': '优化趋势',
                'data': {
                    'periods': [trend.period for trend in data.trends],
                    'success_rates': [trend.metrics.success_rate for trend in data.trends],
                    'improvements': [trend.metrics.average_improvement for trend in data.trends]
                }
            })
        
        return charts
    
    def _create_tables(self, data: OptimizationReportData) -> List[Dict[str, Any]]:
        """创建表格"""
        
        tables = []
        
        # 洞察汇总表
        if data.insights:
            insight_data = []
            for insight in data.insights:
                insight_data.append({
                    'title': insight.title,
                    'category': insight.category,
                    'impact': insight.impact,
                    'confidence': f"{insight.confidence:.1%}"
                })
            
            tables.append({
                'title': '洞察汇总',
                'headers': ['标题', '类别', '影响', '置信度'],
                'data': insight_data
            })
        
        return tables
    
    def _generate_recommendations(self, data: OptimizationReportData) -> List[str]:
        """生成建议"""
        
        recommendations = []
        
        # 基于成功率的建议
        if data.metrics.success_rate < 0.7:
            recommendations.append("优化成功率偏低，建议检查优化策略和参数设置")
        elif data.metrics.success_rate > 0.9:
            recommendations.append("优化成功率优秀，可以考虑扩大优化范围")
        
        # 基于改进幅度的建议
        if data.metrics.average_improvement < 10:
            recommendations.append("平均改进幅度较小，建议调整优化目标和方法")
        elif data.metrics.average_improvement > 30:
            recommendations.append("改进效果显著，建议总结经验并推广应用")
        
        # 基于洞察的建议
        for insight in data.insights:
            recommendations.extend(insight.recommendations)
        
        # 去重
        recommendations = list(set(recommendations))
        
        return recommendations
    
    def export_report(
        self, 
        report: OptimizationReport, 
        file_path: str, 
        format: str = "json"
    ) -> bool:
        """导出报告"""
        
        try:
            if format.lower() == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            
            elif format.lower() == "markdown":
                content = self._convert_to_markdown(report)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            else:
                raise ValueError(f"不支持的导出格式: {format}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"导出报告失败: {e}")
            return False
    
    def _convert_to_markdown(self, report: OptimizationReport) -> str:
        """转换为Markdown格式"""
        
        content = f"# {report.metadata['title']}\n\n"
        content += f"{report.metadata['description']}\n\n"
        content += f"**生成时间**: {report.metadata['generated_at']}\n\n"
        
        # 添加各章节
        for section in sorted(report.sections, key=lambda x: x['order']):
            content += section['content'] + "\n\n"
        
        # 添加建议
        if report.recommendations:
            content += "## 总体建议\n\n"
            for i, rec in enumerate(report.recommendations, 1):
                content += f"{i}. {rec}\n"
        
        return content
    
    def get_report_history(self) -> List[OptimizationReport]:
        """获取报告历史"""
        return self.optimization_history.copy()
    
    def clear_report_history(self):
        """清空报告历史"""
        self.optimization_history.clear()
    
    def get_metrics_summary(self, timeframe: ReportTimeframe) -> Dict[str, Any]:
        """获取指标摘要"""
        
        # 从历史报告中提取指定时间范围的指标
        relevant_reports = [
            report for report in self.optimization_history
            if report.data.timeframe == timeframe
        ]
        
        if not relevant_reports:
            return {}
        
        # 计算汇总指标
        total_optimizations = sum(
            report.data.metrics.total_optimizations 
            for report in relevant_reports
        )
        
        total_successful = sum(
            report.data.metrics.successful_optimizations 
            for report in relevant_reports
        )
        
        overall_success_rate = total_successful / total_optimizations if total_optimizations > 0 else 0.0
        
        return {
            'timeframe': timeframe.value,
            'total_optimizations': total_optimizations,
            'total_successful': total_successful,
            'overall_success_rate': overall_success_rate,
            'reports_count': len(relevant_reports)
        }