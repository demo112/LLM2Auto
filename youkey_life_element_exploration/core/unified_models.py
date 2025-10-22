# -*- encoding=utf8 -*-
"""
统一数据模型

定义项目中所有模块共用的核心数据结构，避免重复定义
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from datetime import datetime


# ============================================================================
# 基础枚举类型
# ============================================================================

class ElementType(Enum):
    """元素类型"""
    TEMPLATE = "template"      # Airtest模板元素
    POCO_ID = "poco_id"       # POCO ID定位
    POCO_TEXT = "poco_text"   # POCO文本定位
    POCO_ATTR = "poco_attr"   # POCO属性定位
    UNKNOWN = "unknown"


class ActionType(Enum):
    """操作类型"""
    TOUCH = "touch"
    CLICK = "click"
    SWIPE = "swipe"
    INPUT = "input"
    WAIT = "wait"
    ASSERT = "assert"
    UNKNOWN = "unknown"


class CorrelationType(Enum):
    """关联类型"""
    EXACT = "exact"           # 精确匹配
    STRONG = "strong"         # 强关联
    PROBABLE = "probable"     # 可能关联
    POSSIBLE = "possible"     # 弱关联
    NONE = "none"            # 无关联


class QualityLevel(Enum):
    """质量等级"""
    EXCELLENT = "excellent"   # 优秀 (90-100)
    GOOD = "good"            # 良好 (70-89)
    FAIR = "fair"            # 一般 (50-69)
    POOR = "poor"            # 较差 (30-49)
    CRITICAL = "critical"    # 严重 (0-29)


# ============================================================================
# 核心数据模型
# ============================================================================

@dataclass(frozen=True)
class AirtestElement:
    """Airtest元素统一数据模型"""
    template_file: str
    operation_type: str
    record_pos: Tuple[float, float]
    resolution: Tuple[int, int]
    line_number: int
    vector: Optional[Tuple[float, float]] = None
    threshold: float = 0.8
    rgb: bool = True


@dataclass(frozen=True)
class PocoElement:
    """Poco元素统一数据模型"""
    selector: str
    selector_type: str  # 'id', 'text', 'attr', 'xpath'
    operation_type: str
    line_number: int
    operation_params: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ElementInfo:
    """通用元素信息"""
    element_id: str
    element_type: ElementType
    locator: str
    line_number: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)
    location: Dict[str, float] = field(default_factory=dict)  # x, y, width, height
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ActionInfo:
    """操作信息"""
    action_type: ActionType
    element: ElementInfo
    line_number: int = 0
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ElementMapping:
    """元素映射关系统一模型"""
    mapping_id: str
    airtest_element: Optional[AirtestElement]
    poco_element: Optional[PocoElement]
    correlation_type: CorrelationType
    confidence: float
    evidence: List[str] = field(default_factory=list)
    semantic_name: str = ""
    screenshot_path: str = ""
    created_at: datetime = field(default_factory=datetime.now)


# ============================================================================
# 质量指标模型
# ============================================================================

@dataclass
class QualityScore:
    """质量评分统一模型"""
    score: float  # 0-100
    level: QualityLevel
    details: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QualityMetrics:
    """质量指标统一模型"""
    element_id: str
    timestamp: datetime
    
    # 性能指标
    performance_score: QualityScore = field(default_factory=lambda: QualityScore(0.0, QualityLevel.CRITICAL))
    response_time: float = 0.0
    load_time: float = 0.0
    render_time: float = 0.0
    
    # 可见性指标
    visibility_score: QualityScore = field(default_factory=lambda: QualityScore(0.0, QualityLevel.CRITICAL))
    is_displayed: bool = False
    is_enabled: bool = False
    
    # 可访问性指标
    accessibility_score: QualityScore = field(default_factory=lambda: QualityScore(0.0, QualityLevel.CRITICAL))
    has_aria_label: bool = False
    has_alt_text: bool = False
    color_contrast_ratio: float = 0.0
    
    # 稳定性指标
    stability_score: QualityScore = field(default_factory=lambda: QualityScore(0.0, QualityLevel.CRITICAL))
    position_stability: float = 0.0
    size_stability: float = 0.0
    
    # 交互性指标
    interaction_score: QualityScore = field(default_factory=lambda: QualityScore(0.0, QualityLevel.CRITICAL))
    click_success_rate: float = 0.0
    input_success_rate: float = 0.0
    
    # 综合评分
    overall_score: QualityScore = field(default_factory=lambda: QualityScore(0.0, QualityLevel.CRITICAL))
    
    # 错误和警告
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ============================================================================
# 优化相关模型
# ============================================================================

@dataclass
class OptimizationStrategy:
    """优化策略统一模型"""
    strategy_id: str
    name: str
    description: str
    category: str  # performance, visibility, accessibility, stability, interaction
    
    # 策略参数
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"  # low, medium, high, critical
    estimated_impact: float = 0.0  # 预期影响 (0-1)
    implementation_cost: str = "medium"  # low, medium, high
    
    # 适用条件
    applicable_conditions: List[str] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=list)
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationResult:
    """优化结果统一模型"""
    result_id: str
    element_id: str
    strategy_id: str
    timestamp: datetime
    
    # 优化结果
    success: bool
    improvement_score: float  # 改进分数
    before_metrics: QualityMetrics = None
    after_metrics: QualityMetrics = None
    
    # 详细信息
    applied_changes: List[str] = field(default_factory=list)
    performance_gain: Dict[str, float] = field(default_factory=dict)
    side_effects: List[str] = field(default_factory=list)
    
    # 验证结果
    validation_passed: bool = True
    validation_details: Dict[str, Any] = field(default_factory=dict)
    
    # 元数据
    execution_time: float = 0.0
    resource_usage: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# 分析结果模型
# ============================================================================

@dataclass
class AnalysisResult:
    """分析结果统一模型"""
    analysis_id: str
    element_id: str
    analysis_type: str
    timestamp: datetime
    
    # 分析结果
    success: bool
    confidence: float
    findings: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    
    # 数据
    metrics: QualityMetrics = None
    trends: Dict[str, Any] = field(default_factory=dict)
    anomalies: List[str] = field(default_factory=list)
    
    # 建议
    recommendations: List[str] = field(default_factory=list)
    optimization_suggestions: List[OptimizationStrategy] = field(default_factory=list)
    
    # 元数据
    execution_time: float = 0.0
    data_sources: List[str] = field(default_factory=list)


# ============================================================================
# 报告模型
# ============================================================================

@dataclass
class ReportSection:
    """报告章节"""
    title: str
    content: str
    data: Dict[str, Any] = field(default_factory=dict)
    charts: List[str] = field(default_factory=list)  # 图表路径
    order: int = 0


@dataclass
class Report:
    """统一报告模型"""
    report_id: str
    title: str
    report_type: str  # quality, optimization, analysis, mapping
    created_at: datetime
    
    # 报告内容
    summary: str = ""
    sections: List[ReportSection] = field(default_factory=list)
    
    # 数据
    elements: List[str] = field(default_factory=list)  # 涉及的元素ID
    metrics: List[QualityMetrics] = field(default_factory=list)
    results: List[Union[AnalysisResult, OptimizationResult]] = field(default_factory=list)
    
    # 元数据
    format: str = "markdown"  # markdown, html, pdf
    output_path: str = ""
    file_size: int = 0
    generation_time: float = 0.0


# ============================================================================
# 工具函数
# ============================================================================

def get_quality_level(score: float) -> QualityLevel:
    """根据分数获取质量等级"""
    if score >= 90:
        return QualityLevel.EXCELLENT
    elif score >= 70:
        return QualityLevel.GOOD
    elif score >= 50:
        return QualityLevel.FAIR
    elif score >= 30:
        return QualityLevel.POOR
    else:
        return QualityLevel.CRITICAL


def create_quality_score(score: float, details: Dict[str, float] = None, 
                        issues: List[str] = None, recommendations: List[str] = None) -> QualityScore:
    """创建质量评分对象"""
    return QualityScore(
        score=max(0.0, min(100.0, score)),
        level=get_quality_level(score),
        details=details or {},
        issues=issues or [],
        recommendations=recommendations or []
    )


def generate_element_id(element_type: ElementType, locator: str, line_number: int = 0) -> str:
    """生成元素ID"""
    import hashlib
    content = f"{element_type.value}_{locator}_{line_number}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def generate_mapping_id(airtest_element: AirtestElement, poco_element: PocoElement) -> str:
    """生成映射ID"""
    import hashlib
    airtest_id = f"{airtest_element.template_file}_{airtest_element.line_number}" if airtest_element else "none"
    poco_id = f"{poco_element.selector}_{poco_element.line_number}" if poco_element else "none"
    content = f"{airtest_id}_{poco_id}"
    return hashlib.md5(content.encode()).hexdigest()[:12]