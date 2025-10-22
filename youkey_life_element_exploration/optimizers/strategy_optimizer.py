"""
策略优化器模块

提供优化策略的选择、调整和评估功能，包括策略组合、参数调优等。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta
from enum import Enum
import statistics
import math
from collections import defaultdict, deque
import itertools

from ..config.optimization_config import OptimizationConfig, OptimizationStrategy, OptimizationTarget
from .element_optimizer import ElementOptimizer, OptimizationAction, OptimizationPriority, OptimizationCategory


class StrategyType(Enum):
    """策略类型枚举"""
    AGGRESSIVE = "aggressive"  # 激进策略
    CONSERVATIVE = "conservative"  # 保守策略
    BALANCED = "balanced"  # 平衡策略
    TARGETED = "targeted"  # 针对性策略
    ADAPTIVE = "adaptive"  # 自适应策略


class StrategyScope(Enum):
    """策略范围枚举"""
    SINGLE_ELEMENT = "single_element"  # 单元素
    ELEMENT_GROUP = "element_group"  # 元素组
    PAGE_LEVEL = "page_level"  # 页面级
    SITE_LEVEL = "site_level"  # 站点级


class StrategyPhase(Enum):
    """策略阶段枚举"""
    ANALYSIS = "analysis"  # 分析阶段
    PLANNING = "planning"  # 规划阶段
    EXECUTION = "execution"  # 执行阶段
    VALIDATION = "validation"  # 验证阶段
    OPTIMIZATION = "optimization"  # 优化阶段


@dataclass
class StrategyParameter:
    """策略参数"""
    name: str
    value: Any
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    step: Optional[Any] = None
    description: str = ""
    impact_weight: float = 1.0


@dataclass
class StrategyRule:
    """策略规则"""
    id: str
    name: str
    condition: str  # 条件表达式
    action: str  # 动作
    priority: int
    enabled: bool = True
    description: str = ""


@dataclass
class StrategyTemplate:
    """策略模板"""
    id: str
    name: str
    description: str
    strategy_type: StrategyType
    scope: StrategyScope
    parameters: List[StrategyParameter]
    rules: List[StrategyRule]
    target_metrics: List[str]
    constraints: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class StrategyPerformance:
    """策略性能"""
    strategy_id: str
    execution_count: int
    success_count: int
    failure_count: int
    avg_improvement: float
    avg_execution_time: timedelta
    avg_resource_usage: float
    success_rate: float
    roi: float
    last_updated: datetime


@dataclass
class StrategyOptimizationResult:
    """策略优化结果"""
    original_strategy: StrategyTemplate
    optimized_strategy: StrategyTemplate
    optimization_method: str
    performance_improvement: float
    parameter_changes: Dict[str, Tuple[Any, Any]]  # 参数名 -> (旧值, 新值)
    validation_results: Dict[str, float]
    confidence: float
    recommendations: List[str]
    timestamp: datetime


class StrategyOptimizer:
    """策略优化器
    
    提供优化策略的选择、调整和评估功能。
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        """初始化策略优化器
        
        Args:
            config: 优化配置
        """
        self.config = config or OptimizationConfig()
        self.element_optimizer = ElementOptimizer(config)
        
        # 策略模板库
        self.strategy_templates: Dict[str, StrategyTemplate] = {}
        
        # 策略性能历史
        self.strategy_performance: Dict[str, StrategyPerformance] = {}
        
        # 优化历史
        self.optimization_history: List[StrategyOptimizationResult] = []
        
        # 初始化预定义策略
        self._initialize_strategy_templates()
    
    def _initialize_strategy_templates(self):
        """初始化预定义策略模板"""
        
        # 激进优化策略
        aggressive_strategy = StrategyTemplate(
            id="aggressive_optimization",
            name="激进优化策略",
            description="追求最大化改进效果，可接受较高风险",
            strategy_type=StrategyType.AGGRESSIVE,
            scope=StrategyScope.SINGLE_ELEMENT,
            parameters=[
                StrategyParameter(
                    name="risk_tolerance",
                    value=0.8,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.1,
                    description="风险容忍度",
                    impact_weight=1.5
                ),
                StrategyParameter(
                    name="improvement_threshold",
                    value=0.3,
                    min_value=0.1,
                    max_value=0.5,
                    step=0.05,
                    description="最小改进阈值",
                    impact_weight=1.2
                ),
                StrategyParameter(
                    name="max_actions",
                    value=10,
                    min_value=5,
                    max_value=20,
                    step=1,
                    description="最大动作数量",
                    impact_weight=1.0
                )
            ],
            rules=[
                StrategyRule(
                    id="prioritize_high_impact",
                    name="优先高影响动作",
                    condition="action.estimated_impact >= 0.7",
                    action="increase_priority",
                    priority=1,
                    description="优先执行高影响动作"
                ),
                StrategyRule(
                    id="accept_high_effort",
                    name="接受高工作量",
                    condition="action.estimated_effort <= 0.9",
                    action="accept",
                    priority=2,
                    description="接受高工作量动作"
                )
            ],
            target_metrics=["performance", "accessibility", "interaction"],
            success_criteria=["overall_improvement >= 0.3", "success_rate >= 0.8"]
        )
        
        # 保守优化策略
        conservative_strategy = StrategyTemplate(
            id="conservative_optimization",
            name="保守优化策略",
            description="追求稳定改进，最小化风险",
            strategy_type=StrategyType.CONSERVATIVE,
            scope=StrategyScope.SINGLE_ELEMENT,
            parameters=[
                StrategyParameter(
                    name="risk_tolerance",
                    value=0.3,
                    min_value=0.0,
                    max_value=0.5,
                    step=0.1,
                    description="风险容忍度",
                    impact_weight=2.0
                ),
                StrategyParameter(
                    name="improvement_threshold",
                    value=0.1,
                    min_value=0.05,
                    max_value=0.2,
                    step=0.05,
                    description="最小改进阈值",
                    impact_weight=1.0
                ),
                StrategyParameter(
                    name="max_actions",
                    value=5,
                    min_value=2,
                    max_value=8,
                    step=1,
                    description="最大动作数量",
                    impact_weight=1.5
                )
            ],
            rules=[
                StrategyRule(
                    id="prioritize_low_risk",
                    name="优先低风险动作",
                    condition="action.estimated_effort <= 0.5",
                    action="increase_priority",
                    priority=1,
                    description="优先执行低风险动作"
                ),
                StrategyRule(
                    id="avoid_high_effort",
                    name="避免高工作量",
                    condition="action.estimated_effort > 0.7",
                    action="reject",
                    priority=2,
                    description="避免高工作量动作"
                )
            ],
            target_metrics=["stability", "quality"],
            success_criteria=["overall_improvement >= 0.1", "success_rate >= 0.9"]
        )
        
        # 平衡优化策略
        balanced_strategy = StrategyTemplate(
            id="balanced_optimization",
            name="平衡优化策略",
            description="在效果和风险之间寻求平衡",
            strategy_type=StrategyType.BALANCED,
            scope=StrategyScope.SINGLE_ELEMENT,
            parameters=[
                StrategyParameter(
                    name="risk_tolerance",
                    value=0.5,
                    min_value=0.3,
                    max_value=0.7,
                    step=0.1,
                    description="风险容忍度",
                    impact_weight=1.0
                ),
                StrategyParameter(
                    name="improvement_threshold",
                    value=0.2,
                    min_value=0.1,
                    max_value=0.3,
                    step=0.05,
                    description="最小改进阈值",
                    impact_weight=1.0
                ),
                StrategyParameter(
                    name="max_actions",
                    value=7,
                    min_value=4,
                    max_value=12,
                    step=1,
                    description="最大动作数量",
                    impact_weight=1.0
                )
            ],
            rules=[
                StrategyRule(
                    id="balance_impact_effort",
                    name="平衡影响和工作量",
                    condition="action.estimated_impact / action.estimated_effort >= 1.0",
                    action="accept",
                    priority=1,
                    description="接受影响工作量比合理的动作"
                ),
                StrategyRule(
                    id="moderate_risk",
                    name="中等风险控制",
                    condition="action.estimated_effort <= 0.6",
                    action="prefer",
                    priority=2,
                    description="偏好中等风险动作"
                )
            ],
            target_metrics=["performance", "stability", "accessibility"],
            success_criteria=["overall_improvement >= 0.2", "success_rate >= 0.85"]
        )
        
        # 自适应策略
        adaptive_strategy = StrategyTemplate(
            id="adaptive_optimization",
            name="自适应优化策略",
            description="根据历史表现动态调整策略",
            strategy_type=StrategyType.ADAPTIVE,
            scope=StrategyScope.SINGLE_ELEMENT,
            parameters=[
                StrategyParameter(
                    name="adaptation_rate",
                    value=0.1,
                    min_value=0.05,
                    max_value=0.3,
                    step=0.05,
                    description="适应速率",
                    impact_weight=1.0
                ),
                StrategyParameter(
                    name="performance_window",
                    value=10,
                    min_value=5,
                    max_value=20,
                    step=1,
                    description="性能评估窗口",
                    impact_weight=0.8
                ),
                StrategyParameter(
                    name="min_confidence",
                    value=0.7,
                    min_value=0.5,
                    max_value=0.9,
                    step=0.1,
                    description="最小置信度",
                    impact_weight=1.2
                )
            ],
            rules=[
                StrategyRule(
                    id="adapt_to_performance",
                    name="根据性能调整",
                    condition="recent_success_rate < 0.7",
                    action="reduce_risk",
                    priority=1,
                    description="性能不佳时降低风险"
                ),
                StrategyRule(
                    id="exploit_success",
                    name="利用成功经验",
                    condition="recent_success_rate > 0.9",
                    action="increase_ambition",
                    priority=2,
                    description="成功率高时提高目标"
                )
            ],
            target_metrics=["performance", "stability", "accessibility", "interaction"],
            success_criteria=["adaptive_improvement >= 0.15", "consistency >= 0.8"]
        )
        
        # 保存策略模板
        self.strategy_templates = {
            "aggressive": aggressive_strategy,
            "conservative": conservative_strategy,
            "balanced": balanced_strategy,
            "adaptive": adaptive_strategy
        }
    
    def select_strategy(
        self,
        element_data: Dict[str, Any],
        optimization_goals: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> StrategyTemplate:
        """选择最适合的优化策略
        
        Args:
            element_data: 元素数据
            optimization_goals: 优化目标
            constraints: 约束条件
            
        Returns:
            StrategyTemplate: 选中的策略模板
        """
        constraints = constraints or {}
        
        # 分析元素特征
        element_characteristics = self._analyze_element_characteristics(element_data)
        
        # 评估每个策略的适用性
        strategy_scores = {}
        
        for strategy_id, strategy in self.strategy_templates.items():
            score = self._evaluate_strategy_suitability(
                strategy, element_characteristics, optimization_goals, constraints
            )
            strategy_scores[strategy_id] = score
        
        # 选择得分最高的策略
        best_strategy_id = max(strategy_scores, key=strategy_scores.get)
        selected_strategy = self.strategy_templates[best_strategy_id]
        
        # 根据具体情况调整策略参数
        customized_strategy = self._customize_strategy(
            selected_strategy, element_characteristics, optimization_goals
        )
        
        return customized_strategy
    
    def _analyze_element_characteristics(self, element_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析元素特征
        
        Args:
            element_data: 元素数据
            
        Returns:
            Dict[str, Any]: 元素特征
        """
        characteristics = {
            "complexity": 0.5,  # 复杂度
            "stability": 0.5,   # 稳定性
            "criticality": 0.5, # 关键性
            "performance": 0.5, # 性能状况
            "accessibility": 0.5, # 可访问性状况
            "interaction_frequency": 0.5  # 交互频率
        }
        
        # 基于元素数据计算特征
        if 'quality_score' in element_data:
            quality = element_data['quality_score']
            characteristics["complexity"] = 1.0 - quality  # 质量低则复杂度高
        
        if 'stability_score' in element_data:
            characteristics["stability"] = element_data['stability_score']
        
        if 'performance_score' in element_data:
            characteristics["performance"] = element_data['performance_score']
        
        if 'accessibility_score' in element_data:
            characteristics["accessibility"] = element_data['accessibility_score']
        
        if 'interaction_count' in element_data:
            # 归一化交互频率
            max_interactions = 1000  # 假设的最大交互次数
            characteristics["interaction_frequency"] = min(
                1.0, element_data['interaction_count'] / max_interactions
            )
        
        # 评估关键性（基于多个因素）
        criticality_factors = [
            characteristics["interaction_frequency"],
            1.0 - characteristics["performance"],  # 性能差则关键性高
            1.0 - characteristics["accessibility"]  # 可访问性差则关键性高
        ]
        characteristics["criticality"] = statistics.mean(criticality_factors)
        
        return characteristics
    
    def _evaluate_strategy_suitability(
        self,
        strategy: StrategyTemplate,
        characteristics: Dict[str, Any],
        goals: List[str],
        constraints: Dict[str, Any]
    ) -> float:
        """评估策略适用性
        
        Args:
            strategy: 策略模板
            characteristics: 元素特征
            goals: 优化目标
            constraints: 约束条件
            
        Returns:
            float: 适用性得分
        """
        score = 0.0
        
        # 基于策略类型的适用性
        if strategy.strategy_type == StrategyType.AGGRESSIVE:
            # 激进策略适合低关键性、高性能要求的场景
            score += (1.0 - characteristics["criticality"]) * 0.3
            if "performance" in goals:
                score += 0.4
        
        elif strategy.strategy_type == StrategyType.CONSERVATIVE:
            # 保守策略适合高关键性、稳定性要求的场景
            score += characteristics["criticality"] * 0.3
            if "stability" in goals:
                score += 0.4
        
        elif strategy.strategy_type == StrategyType.BALANCED:
            # 平衡策略适合大多数场景
            score += 0.5  # 基础适用性
        
        elif strategy.strategy_type == StrategyType.ADAPTIVE:
            # 自适应策略适合复杂、变化的场景
            score += characteristics["complexity"] * 0.3
            if len(goals) > 2:  # 多目标优化
                score += 0.3
        
        # 基于目标匹配度
        target_match = len(set(goals) & set(strategy.target_metrics)) / len(goals)
        score += target_match * 0.3
        
        # 基于约束满足度
        constraint_satisfaction = self._check_constraint_satisfaction(strategy, constraints)
        score += constraint_satisfaction * 0.2
        
        # 基于历史性能
        if strategy.id in self.strategy_performance:
            perf = self.strategy_performance[strategy.id]
            score += perf.success_rate * 0.2
        
        return score
    
    def _check_constraint_satisfaction(
        self,
        strategy: StrategyTemplate,
        constraints: Dict[str, Any]
    ) -> float:
        """检查约束满足度
        
        Args:
            strategy: 策略模板
            constraints: 约束条件
            
        Returns:
            float: 满足度得分 (0-1)
        """
        satisfaction = 1.0
        
        # 检查时间约束
        if "max_duration" in constraints:
            max_duration = constraints["max_duration"]
            # 简化：假设策略的预期执行时间与动作数量相关
            max_actions_param = next(
                (p for p in strategy.parameters if p.name == "max_actions"), None
            )
            if max_actions_param:
                estimated_duration = timedelta(hours=max_actions_param.value * 2)
                if estimated_duration > max_duration:
                    satisfaction *= 0.5
        
        # 检查资源约束
        if "max_effort" in constraints:
            max_effort = constraints["max_effort"]
            max_actions_param = next(
                (p for p in strategy.parameters if p.name == "max_actions"), None
            )
            if max_actions_param:
                estimated_effort = max_actions_param.value * 0.1  # 简化计算
                if estimated_effort > max_effort:
                    satisfaction *= 0.7
        
        # 检查风险约束
        if "max_risk" in constraints:
            max_risk = constraints["max_risk"]
            risk_tolerance_param = next(
                (p for p in strategy.parameters if p.name == "risk_tolerance"), None
            )
            if risk_tolerance_param and risk_tolerance_param.value > max_risk:
                satisfaction *= 0.6
        
        return satisfaction
    
    def _customize_strategy(
        self,
        strategy: StrategyTemplate,
        characteristics: Dict[str, Any],
        goals: List[str]
    ) -> StrategyTemplate:
        """定制策略参数
        
        Args:
            strategy: 原始策略模板
            characteristics: 元素特征
            goals: 优化目标
            
        Returns:
            StrategyTemplate: 定制后的策略
        """
        # 创建策略副本
        customized = StrategyTemplate(
            id=f"{strategy.id}_customized_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=f"{strategy.name} (定制版)",
            description=strategy.description,
            strategy_type=strategy.strategy_type,
            scope=strategy.scope,
            parameters=[],
            rules=strategy.rules.copy(),
            target_metrics=strategy.target_metrics.copy(),
            constraints=strategy.constraints.copy(),
            success_criteria=strategy.success_criteria.copy()
        )
        
        # 调整参数
        for param in strategy.parameters:
            new_param = StrategyParameter(
                name=param.name,
                value=param.value,
                min_value=param.min_value,
                max_value=param.max_value,
                step=param.step,
                description=param.description,
                impact_weight=param.impact_weight
            )
            
            # 根据元素特征调整参数
            if param.name == "risk_tolerance":
                # 高关键性元素降低风险容忍度
                adjustment = -characteristics["criticality"] * 0.2
                new_param.value = max(
                    param.min_value or 0,
                    min(param.max_value or 1, param.value + adjustment)
                )
            
            elif param.name == "improvement_threshold":
                # 性能差的元素提高改进阈值
                adjustment = (1.0 - characteristics["performance"]) * 0.1
                new_param.value = max(
                    param.min_value or 0,
                    min(param.max_value or 1, param.value + adjustment)
                )
            
            elif param.name == "max_actions":
                # 复杂元素增加动作数量
                adjustment = int(characteristics["complexity"] * 3)
                new_param.value = max(
                    param.min_value or 1,
                    min(param.max_value or 20, param.value + adjustment)
                )
            
            customized.parameters.append(new_param)
        
        return customized
    
    def optimize_strategy(
        self,
        strategy: StrategyTemplate,
        historical_results: List[Dict[str, Any]],
        optimization_method: str = "grid_search"
    ) -> StrategyOptimizationResult:
        """优化策略参数
        
        Args:
            strategy: 待优化的策略
            historical_results: 历史执行结果
            optimization_method: 优化方法
            
        Returns:
            StrategyOptimizationResult: 优化结果
        """
        if optimization_method == "grid_search":
            return self._optimize_strategy_grid_search(strategy, historical_results)
        elif optimization_method == "random_search":
            return self._optimize_strategy_random_search(strategy, historical_results)
        elif optimization_method == "bayesian":
            return self._optimize_strategy_bayesian(strategy, historical_results)
        else:
            raise ValueError(f"不支持的优化方法: {optimization_method}")
    
    def _optimize_strategy_grid_search(
        self,
        strategy: StrategyTemplate,
        historical_results: List[Dict[str, Any]]
    ) -> StrategyOptimizationResult:
        """使用网格搜索优化策略
        
        Args:
            strategy: 待优化的策略
            historical_results: 历史执行结果
            
        Returns:
            StrategyOptimizationResult: 优化结果
        """
        best_strategy = strategy
        best_score = 0.0
        best_params = {}
        
        # 生成参数组合
        param_combinations = self._generate_parameter_combinations(strategy)
        
        # 评估每个参数组合
        for param_combo in param_combinations[:50]:  # 限制搜索空间
            test_strategy = self._create_strategy_with_params(strategy, param_combo)
            score = self._evaluate_strategy_performance(test_strategy, historical_results)
            
            if score > best_score:
                best_score = score
                best_strategy = test_strategy
                best_params = param_combo
        
        # 计算参数变化
        parameter_changes = {}
        for param in strategy.parameters:
            old_value = param.value
            new_value = best_params.get(param.name, old_value)
            if old_value != new_value:
                parameter_changes[param.name] = (old_value, new_value)
        
        # 验证优化结果
        validation_results = self._validate_optimized_strategy(best_strategy, historical_results)
        
        return StrategyOptimizationResult(
            original_strategy=strategy,
            optimized_strategy=best_strategy,
            optimization_method="grid_search",
            performance_improvement=best_score - self._evaluate_strategy_performance(strategy, historical_results),
            parameter_changes=parameter_changes,
            validation_results=validation_results,
            confidence=min(1.0, best_score),
            recommendations=self._generate_optimization_recommendations(best_strategy, parameter_changes),
            timestamp=datetime.now()
        )
    
    def _generate_parameter_combinations(self, strategy: StrategyTemplate) -> List[Dict[str, Any]]:
        """生成参数组合
        
        Args:
            strategy: 策略模板
            
        Returns:
            List[Dict[str, Any]]: 参数组合列表
        """
        param_ranges = {}
        
        for param in strategy.parameters:
            if param.min_value is not None and param.max_value is not None and param.step is not None:
                if isinstance(param.value, int):
                    values = list(range(
                        int(param.min_value),
                        int(param.max_value) + 1,
                        int(param.step)
                    ))
                else:
                    values = []
                    current = param.min_value
                    while current <= param.max_value:
                        values.append(round(current, 3))
                        current += param.step
                param_ranges[param.name] = values
            else:
                param_ranges[param.name] = [param.value]
        
        # 生成所有组合
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        
        combinations = []
        for combo in itertools.product(*param_values):
            param_dict = dict(zip(param_names, combo))
            combinations.append(param_dict)
        
        return combinations
    
    def _create_strategy_with_params(
        self,
        strategy: StrategyTemplate,
        params: Dict[str, Any]
    ) -> StrategyTemplate:
        """使用指定参数创建策略
        
        Args:
            strategy: 原始策略
            params: 参数字典
            
        Returns:
            StrategyTemplate: 新策略
        """
        new_strategy = StrategyTemplate(
            id=f"{strategy.id}_test",
            name=strategy.name,
            description=strategy.description,
            strategy_type=strategy.strategy_type,
            scope=strategy.scope,
            parameters=[],
            rules=strategy.rules.copy(),
            target_metrics=strategy.target_metrics.copy(),
            constraints=strategy.constraints.copy(),
            success_criteria=strategy.success_criteria.copy()
        )
        
        for param in strategy.parameters:
            new_param = StrategyParameter(
                name=param.name,
                value=params.get(param.name, param.value),
                min_value=param.min_value,
                max_value=param.max_value,
                step=param.step,
                description=param.description,
                impact_weight=param.impact_weight
            )
            new_strategy.parameters.append(new_param)
        
        return new_strategy
    
    def _evaluate_strategy_performance(
        self,
        strategy: StrategyTemplate,
        historical_results: List[Dict[str, Any]]
    ) -> float:
        """评估策略性能
        
        Args:
            strategy: 策略模板
            historical_results: 历史结果
            
        Returns:
            float: 性能得分
        """
        if not historical_results:
            return 0.5  # 默认得分
        
        # 简化的性能评估
        total_score = 0.0
        valid_results = 0
        
        for result in historical_results:
            if 'success_rate' in result and 'improvement' in result:
                # 综合成功率和改进程度
                score = (result['success_rate'] * 0.6 + result['improvement'] * 0.4)
                total_score += score
                valid_results += 1
        
        if valid_results == 0:
            return 0.5
        
        return total_score / valid_results
    
    def _validate_optimized_strategy(
        self,
        strategy: StrategyTemplate,
        historical_results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """验证优化后的策略
        
        Args:
            strategy: 优化后的策略
            historical_results: 历史结果
            
        Returns:
            Dict[str, float]: 验证结果
        """
        validation_results = {
            "consistency": 0.0,
            "robustness": 0.0,
            "efficiency": 0.0,
            "effectiveness": 0.0
        }
        
        if not historical_results:
            return validation_results
        
        # 一致性：结果的稳定性
        improvements = [r.get('improvement', 0) for r in historical_results]
        if improvements:
            mean_improvement = statistics.mean(improvements)
            if mean_improvement > 0:
                cv = statistics.stdev(improvements) / mean_improvement
                validation_results["consistency"] = max(0, 1.0 - cv)
        
        # 鲁棒性：在不同条件下的表现
        success_rates = [r.get('success_rate', 0) for r in historical_results]
        if success_rates:
            validation_results["robustness"] = statistics.mean(success_rates)
        
        # 效率：资源利用率
        efforts = [r.get('effort', 1) for r in historical_results]
        improvements = [r.get('improvement', 0) for r in historical_results]
        if efforts and improvements:
            efficiency_scores = [imp / eff if eff > 0 else 0 
                               for imp, eff in zip(improvements, efforts)]
            validation_results["efficiency"] = statistics.mean(efficiency_scores)
        
        # 有效性：目标达成度
        target_achievements = [r.get('target_achievement', 0) for r in historical_results]
        if target_achievements:
            validation_results["effectiveness"] = statistics.mean(target_achievements)
        
        return validation_results
    
    def _generate_optimization_recommendations(
        self,
        strategy: StrategyTemplate,
        parameter_changes: Dict[str, Tuple[Any, Any]]
    ) -> List[str]:
        """生成优化建议
        
        Args:
            strategy: 优化后的策略
            parameter_changes: 参数变化
            
        Returns:
            List[str]: 建议列表
        """
        recommendations = []
        
        if not parameter_changes:
            recommendations.append("当前策略参数已经较为优化，建议保持现状")
            return recommendations
        
        for param_name, (old_value, new_value) in parameter_changes.items():
            if param_name == "risk_tolerance":
                if new_value > old_value:
                    recommendations.append("提高风险容忍度有助于获得更大改进，但需要加强监控")
                else:
                    recommendations.append("降低风险容忍度提高了稳定性，适合关键场景")
            
            elif param_name == "improvement_threshold":
                if new_value > old_value:
                    recommendations.append("提高改进阈值确保优化效果，但可能减少优化机会")
                else:
                    recommendations.append("降低改进阈值增加优化机会，注意避免过度优化")
            
            elif param_name == "max_actions":
                if new_value > old_value:
                    recommendations.append("增加动作数量可能提高效果，但需要更多资源")
                else:
                    recommendations.append("减少动作数量提高效率，适合资源受限场景")
        
        # 通用建议
        recommendations.append("建议定期重新评估策略参数，适应环境变化")
        recommendations.append("监控优化效果，及时调整策略配置")
        
        return recommendations
    
    def _optimize_strategy_random_search(
        self,
        strategy: StrategyTemplate,
        historical_results: List[Dict[str, Any]]
    ) -> StrategyOptimizationResult:
        """使用随机搜索优化策略"""
        # 简化实现，实际应用中会更复杂
        return self._optimize_strategy_grid_search(strategy, historical_results)
    
    def _optimize_strategy_bayesian(
        self,
        strategy: StrategyTemplate,
        historical_results: List[Dict[str, Any]]
    ) -> StrategyOptimizationResult:
        """使用贝叶斯优化策略"""
        # 简化实现，实际应用中会使用专门的贝叶斯优化库
        return self._optimize_strategy_grid_search(strategy, historical_results)
    
    def update_strategy_performance(
        self,
        strategy_id: str,
        execution_result: Dict[str, Any]
    ):
        """更新策略性能记录
        
        Args:
            strategy_id: 策略ID
            execution_result: 执行结果
        """
        if strategy_id not in self.strategy_performance:
            self.strategy_performance[strategy_id] = StrategyPerformance(
                strategy_id=strategy_id,
                execution_count=0,
                success_count=0,
                failure_count=0,
                avg_improvement=0.0,
                avg_execution_time=timedelta(),
                avg_resource_usage=0.0,
                success_rate=0.0,
                roi=0.0,
                last_updated=datetime.now()
            )
        
        perf = self.strategy_performance[strategy_id]
        
        # 更新计数
        perf.execution_count += 1
        
        if execution_result.get('success', False):
            perf.success_count += 1
        else:
            perf.failure_count += 1
        
        # 更新平均值
        improvement = execution_result.get('improvement', 0.0)
        perf.avg_improvement = (
            (perf.avg_improvement * (perf.execution_count - 1) + improvement) /
            perf.execution_count
        )
        
        execution_time = execution_result.get('execution_time', timedelta())
        if isinstance(execution_time, timedelta):
            total_seconds = (
                perf.avg_execution_time.total_seconds() * (perf.execution_count - 1) +
                execution_time.total_seconds()
            ) / perf.execution_count
            perf.avg_execution_time = timedelta(seconds=total_seconds)
        
        resource_usage = execution_result.get('resource_usage', 0.0)
        perf.avg_resource_usage = (
            (perf.avg_resource_usage * (perf.execution_count - 1) + resource_usage) /
            perf.execution_count
        )
        
        # 更新成功率
        perf.success_rate = perf.success_count / perf.execution_count
        
        # 更新ROI
        if perf.avg_resource_usage > 0:
            perf.roi = perf.avg_improvement / perf.avg_resource_usage
        
        perf.last_updated = datetime.now()
    
    def get_strategy_recommendations(
        self,
        element_data: Dict[str, Any],
        optimization_goals: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """获取策略建议
        
        Args:
            element_data: 元素数据
            optimization_goals: 优化目标
            constraints: 约束条件
            
        Returns:
            Dict[str, Any]: 策略建议
        """
        # 选择推荐策略
        recommended_strategy = self.select_strategy(element_data, optimization_goals, constraints)
        
        # 分析替代策略
        alternative_strategies = []
        for strategy_id, strategy in self.strategy_templates.items():
            if strategy.id != recommended_strategy.id:
                score = self._evaluate_strategy_suitability(
                    strategy, 
                    self._analyze_element_characteristics(element_data),
                    optimization_goals,
                    constraints or {}
                )
                alternative_strategies.append({
                    "strategy": strategy,
                    "score": score,
                    "pros": self._get_strategy_pros(strategy),
                    "cons": self._get_strategy_cons(strategy)
                })
        
        # 按得分排序
        alternative_strategies.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "recommended_strategy": {
                "strategy": recommended_strategy,
                "reasons": self._get_recommendation_reasons(recommended_strategy, element_data),
                "expected_outcomes": self._predict_strategy_outcomes(recommended_strategy, element_data)
            },
            "alternative_strategies": alternative_strategies[:3],  # 前3个替代方案
            "optimization_tips": self._get_optimization_tips(element_data, optimization_goals),
            "risk_assessment": self._assess_strategy_risks(recommended_strategy, element_data)
        }
    
    def _get_strategy_pros(self, strategy: StrategyTemplate) -> List[str]:
        """获取策略优点"""
        pros = []
        
        if strategy.strategy_type == StrategyType.AGGRESSIVE:
            pros.extend(["追求最大化改进", "适合快速优化", "效果显著"])
        elif strategy.strategy_type == StrategyType.CONSERVATIVE:
            pros.extend(["风险较低", "稳定可靠", "适合关键系统"])
        elif strategy.strategy_type == StrategyType.BALANCED:
            pros.extend(["平衡效果与风险", "适用性广", "资源利用合理"])
        elif strategy.strategy_type == StrategyType.ADAPTIVE:
            pros.extend(["自动调整", "适应性强", "持续改进"])
        
        return pros
    
    def _get_strategy_cons(self, strategy: StrategyTemplate) -> List[str]:
        """获取策略缺点"""
        cons = []
        
        if strategy.strategy_type == StrategyType.AGGRESSIVE:
            cons.extend(["风险较高", "可能不稳定", "资源消耗大"])
        elif strategy.strategy_type == StrategyType.CONSERVATIVE:
            cons.extend(["改进有限", "可能错过机会", "进展缓慢"])
        elif strategy.strategy_type == StrategyType.BALANCED:
            cons.extend(["可能不够专业化", "在特定场景下不是最优"])
        elif strategy.strategy_type == StrategyType.ADAPTIVE:
            cons.extend(["复杂度高", "需要更多数据", "调整周期长"])
        
        return cons
    
    def _get_recommendation_reasons(
        self,
        strategy: StrategyTemplate,
        element_data: Dict[str, Any]
    ) -> List[str]:
        """获取推荐理由"""
        reasons = []
        characteristics = self._analyze_element_characteristics(element_data)
        
        if strategy.strategy_type == StrategyType.AGGRESSIVE:
            if characteristics["criticality"] < 0.5:
                reasons.append("元素关键性较低，可以承受较高风险")
            if characteristics["performance"] < 0.6:
                reasons.append("性能有较大改进空间，适合激进优化")
        
        elif strategy.strategy_type == StrategyType.CONSERVATIVE:
            if characteristics["criticality"] > 0.7:
                reasons.append("元素关键性高，需要稳定的优化策略")
            if characteristics["stability"] < 0.6:
                reasons.append("稳定性需要改善，保守策略更安全")
        
        elif strategy.strategy_type == StrategyType.BALANCED:
            reasons.append("综合考虑各项因素，平衡策略最适合")
        
        elif strategy.strategy_type == StrategyType.ADAPTIVE:
            if characteristics["complexity"] > 0.7:
                reasons.append("元素复杂度高，需要自适应策略")
        
        return reasons
    
    def _predict_strategy_outcomes(
        self,
        strategy: StrategyTemplate,
        element_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """预测策略结果"""
        characteristics = self._analyze_element_characteristics(element_data)
        
        # 基于策略类型和元素特征预测结果
        if strategy.strategy_type == StrategyType.AGGRESSIVE:
            expected_improvement = 0.3 + characteristics["performance"] * 0.2
            expected_risk = 0.6 + characteristics["complexity"] * 0.2
            expected_duration = timedelta(days=3, hours=12)
        
        elif strategy.strategy_type == StrategyType.CONSERVATIVE:
            expected_improvement = 0.15 + characteristics["stability"] * 0.1
            expected_risk = 0.2 + characteristics["complexity"] * 0.1
            expected_duration = timedelta(days=2)
        
        elif strategy.strategy_type == StrategyType.BALANCED:
            expected_improvement = 0.2 + characteristics["performance"] * 0.15
            expected_risk = 0.4 + characteristics["complexity"] * 0.15
            expected_duration = timedelta(days=3)
        
        else:  # ADAPTIVE
            expected_improvement = 0.25 + characteristics["complexity"] * 0.1
            expected_risk = 0.3 + characteristics["complexity"] * 0.2
            expected_duration = timedelta(days=4)
        
        return {
            "expected_improvement": min(1.0, expected_improvement),
            "expected_risk": min(1.0, expected_risk),
            "expected_duration": expected_duration,
            "confidence": 0.7 + characteristics["stability"] * 0.2
        }
    
    def _get_optimization_tips(
        self,
        element_data: Dict[str, Any],
        optimization_goals: List[str]
    ) -> List[str]:
        """获取优化提示"""
        tips = []
        characteristics = self._analyze_element_characteristics(element_data)
        
        if characteristics["performance"] < 0.5:
            tips.append("优先关注性能优化，这是当前的主要瓶颈")
        
        if characteristics["accessibility"] < 0.6:
            tips.append("可访问性需要改善，建议优先处理对比度和标签问题")
        
        if characteristics["stability"] < 0.6:
            tips.append("稳定性较差，建议先解决位置和尺寸变化问题")
        
        if "performance" in optimization_goals and "accessibility" in optimization_goals:
            tips.append("性能和可访问性优化可以并行进行，注意避免冲突")
        
        if characteristics["interaction_frequency"] > 0.8:
            tips.append("高频交互元素，优化时要特别注意用户体验")
        
        return tips
    
    def _assess_strategy_risks(
        self,
        strategy: StrategyTemplate,
        element_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估策略风险"""
        characteristics = self._analyze_element_characteristics(element_data)
        
        risks = {
            "technical_risk": 0.0,
            "business_risk": 0.0,
            "user_impact_risk": 0.0,
            "timeline_risk": 0.0
        }
        
        # 技术风险
        if strategy.strategy_type == StrategyType.AGGRESSIVE:
            risks["technical_risk"] = 0.6 + characteristics["complexity"] * 0.3
        else:
            risks["technical_risk"] = 0.2 + characteristics["complexity"] * 0.2
        
        # 业务风险
        risks["business_risk"] = characteristics["criticality"] * 0.5
        
        # 用户影响风险
        risks["user_impact_risk"] = characteristics["interaction_frequency"] * 0.4
        
        # 时间风险
        max_actions_param = next(
            (p for p in strategy.parameters if p.name == "max_actions"), None
        )
        if max_actions_param:
            risks["timeline_risk"] = min(1.0, max_actions_param.value / 10)
        
        return {
            "risks": risks,
            "overall_risk": statistics.mean(risks.values()),
            "mitigation_strategies": self._get_risk_mitigation_strategies(risks)
        }
    
    def _get_risk_mitigation_strategies(self, risks: Dict[str, float]) -> List[str]:
        """获取风险缓解策略"""
        strategies = []
        
        if risks["technical_risk"] > 0.6:
            strategies.append("增加技术评审和测试环节")
            strategies.append("准备详细的回滚计划")
        
        if risks["business_risk"] > 0.6:
            strategies.append("与业务团队密切沟通")
            strategies.append("分阶段实施，降低影响范围")
        
        if risks["user_impact_risk"] > 0.6:
            strategies.append("进行用户测试和反馈收集")
            strategies.append("准备用户沟通和培训材料")
        
        if risks["timeline_risk"] > 0.6:
            strategies.append("合理安排资源和时间")
            strategies.append("设置关键里程碑和检查点")
        
        return strategies