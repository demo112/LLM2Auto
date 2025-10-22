# -*- encoding=utf8 -*-
"""
优化配置

定义性能优化相关的配置参数
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class OptimizationStrategy(Enum):
    """优化策略枚举"""
    CONSERVATIVE = "conservative"  # 保守策略
    BALANCED = "balanced"  # 平衡策略
    AGGRESSIVE = "aggressive"  # 激进策略
    CUSTOM = "custom"  # 自定义策略


class OptimizationTarget(Enum):
    """优化目标枚举"""
    PERFORMANCE = "performance"  # 性能优化
    VISIBILITY = "visibility"  # 可见性优化
    ACCESSIBILITY = "accessibility"  # 可访问性优化
    STABILITY = "stability"  # 稳定性优化
    INTERACTION = "interaction"  # 交互性优化
    OVERALL = "overall"  # 综合优化


@dataclass
class PerformanceOptimizationConfig:
    """性能优化配置"""
    # 基本配置
    enabled: bool = True
    target_improvement: float = 0.2  # 目标改进幅度（20%）
    
    # 响应时间优化
    response_time_optimization: bool = True
    target_response_time: float = 1.0  # 目标响应时间（秒）
    max_response_time: float = 3.0  # 最大可接受响应时间
    
    # 加载时间优化
    load_time_optimization: bool = True
    target_load_time: float = 0.5  # 目标加载时间（秒）
    max_load_time: float = 2.0  # 最大可接受加载时间
    
    # 渲染优化
    render_optimization: bool = True
    target_render_time: float = 0.3  # 目标渲染时间（秒）
    
    # 资源优化
    resource_optimization: bool = True
    memory_limit_mb: int = 100  # 内存限制（MB）
    cpu_limit_percent: int = 50  # CPU限制（百分比）
    
    # 缓存策略
    caching_enabled: bool = True
    cache_strategies: List[str] = field(default_factory=lambda: [
        "browser_cache", "cdn_cache", "application_cache"
    ])
    
    # 压缩配置
    compression_enabled: bool = True
    compression_types: List[str] = field(default_factory=lambda: [
        "gzip", "brotli"
    ])
    
    # 预加载策略
    preloading_enabled: bool = True
    preload_strategies: List[str] = field(default_factory=lambda: [
        "dns_prefetch", "preconnect", "preload", "prefetch"
    ])


@dataclass
class VisibilityOptimizationConfig:
    """可见性优化配置"""
    # 基本配置
    enabled: bool = True
    target_visibility_score: float = 0.9  # 目标可见性分数
    
    # 布局优化
    layout_optimization: bool = True
    viewport_optimization: bool = True  # 视口优化
    z_index_optimization: bool = True  # 层级优化
    
    # 样式优化
    style_optimization: bool = True
    opacity_threshold: float = 0.8  # 不透明度阈值
    contrast_optimization: bool = True  # 对比度优化
    
    # 位置优化
    position_optimization: bool = True
    auto_scroll_to_view: bool = True  # 自动滚动到视图
    center_in_viewport: bool = False  # 居中显示
    
    # 尺寸优化
    size_optimization: bool = True
    min_width: int = 10  # 最小宽度（像素）
    min_height: int = 10  # 最小高度（像素）
    
    # 动画优化
    animation_optimization: bool = True
    reduce_motion: bool = False  # 减少动画
    animation_duration_limit: float = 1.0  # 动画时长限制（秒）


@dataclass
class AccessibilityOptimizationConfig:
    """可访问性优化配置"""
    # 基本配置
    enabled: bool = True
    target_accessibility_score: float = 0.9  # 目标可访问性分数
    
    # ARIA优化
    aria_optimization: bool = True
    auto_add_aria_labels: bool = True  # 自动添加ARIA标签
    aria_role_optimization: bool = True  # ARIA角色优化
    
    # 颜色对比度优化
    color_contrast_optimization: bool = True
    min_contrast_ratio: float = 4.5  # 最小对比度比例（WCAG AA标准）
    target_contrast_ratio: float = 7.0  # 目标对比度比例（WCAG AAA标准）
    
    # 键盘导航优化
    keyboard_navigation_optimization: bool = True
    tab_index_optimization: bool = True  # Tab索引优化
    focus_indicator_optimization: bool = True  # 焦点指示器优化
    
    # 语义化优化
    semantic_optimization: bool = True
    heading_structure_optimization: bool = True  # 标题结构优化
    landmark_optimization: bool = True  # 地标优化
    
    # 文本优化
    text_optimization: bool = True
    font_size_optimization: bool = True  # 字体大小优化
    line_height_optimization: bool = True  # 行高优化
    
    # 媒体优化
    media_optimization: bool = True
    alt_text_optimization: bool = True  # 替代文本优化
    caption_optimization: bool = True  # 字幕优化


@dataclass
class StabilityOptimizationConfig:
    """稳定性优化配置"""
    # 基本配置
    enabled: bool = True
    target_stability_score: float = 0.9  # 目标稳定性分数
    
    # 布局稳定性
    layout_stability_optimization: bool = True
    cumulative_layout_shift_limit: float = 0.1  # 累积布局偏移限制
    
    # 位置稳定性
    position_stability_optimization: bool = True
    max_position_variance: float = 5.0  # 最大位置变化（像素）
    
    # 尺寸稳定性
    size_stability_optimization: bool = True
    max_size_variance: float = 2.0  # 最大尺寸变化（像素）
    
    # 属性稳定性
    attribute_stability_optimization: bool = True
    critical_attributes: List[str] = field(default_factory=lambda: [
        "id", "class", "data-testid", "aria-label"
    ])
    
    # 可用性稳定性
    availability_optimization: bool = True
    min_availability_rate: float = 0.95  # 最小可用率
    
    # 错误处理
    error_handling_optimization: bool = True
    graceful_degradation: bool = True  # 优雅降级
    fallback_strategies: List[str] = field(default_factory=lambda: [
        "retry", "alternative_selector", "wait_and_retry"
    ])


@dataclass
class InteractionOptimizationConfig:
    """交互优化配置"""
    # 基本配置
    enabled: bool = True
    target_interaction_score: float = 0.9  # 目标交互分数
    
    # 点击优化
    click_optimization: bool = True
    click_target_size: int = 44  # 点击目标大小（像素，符合WCAG标准）
    click_success_rate_target: float = 0.95  # 点击成功率目标
    
    # 输入优化
    input_optimization: bool = True
    input_validation_optimization: bool = True  # 输入验证优化
    input_feedback_optimization: bool = True  # 输入反馈优化
    
    # 响应性优化
    responsiveness_optimization: bool = True
    max_response_delay: float = 0.1  # 最大响应延迟（秒）
    
    # 手势优化
    gesture_optimization: bool = True
    touch_target_optimization: bool = True  # 触摸目标优化
    swipe_optimization: bool = True  # 滑动优化
    
    # 状态管理
    state_management_optimization: bool = True
    state_persistence: bool = True  # 状态持久化
    state_recovery: bool = True  # 状态恢复
    
    # 反馈优化
    feedback_optimization: bool = True
    visual_feedback: bool = True  # 视觉反馈
    haptic_feedback: bool = False  # 触觉反馈
    audio_feedback: bool = False  # 音频反馈


@dataclass
class ResourceOptimizationConfig:
    """资源优化配置"""
    # 基本配置
    enabled: bool = True
    optimization_level: str = "balanced"  # 优化级别
    
    # 内存优化
    memory_optimization: bool = True
    memory_limit_mb: int = 200  # 内存限制
    garbage_collection_optimization: bool = True  # 垃圾回收优化
    
    # CPU优化
    cpu_optimization: bool = True
    cpu_limit_percent: int = 70  # CPU限制
    thread_pool_optimization: bool = True  # 线程池优化
    
    # 网络优化
    network_optimization: bool = True
    connection_pooling: bool = True  # 连接池
    request_batching: bool = True  # 请求批处理
    
    # 存储优化
    storage_optimization: bool = True
    local_storage_limit_mb: int = 50  # 本地存储限制
    cache_optimization: bool = True  # 缓存优化
    
    # 并发优化
    concurrency_optimization: bool = True
    max_concurrent_requests: int = 10  # 最大并发请求数
    queue_management: bool = True  # 队列管理


@dataclass
class OptimizationConfig:
    """优化配置"""
    # 基本配置
    enabled: bool = True
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    primary_target: OptimizationTarget = OptimizationTarget.OVERALL
    
    # 子配置
    performance: PerformanceOptimizationConfig = field(default_factory=PerformanceOptimizationConfig)
    visibility: VisibilityOptimizationConfig = field(default_factory=VisibilityOptimizationConfig)
    accessibility: AccessibilityOptimizationConfig = field(default_factory=AccessibilityOptimizationConfig)
    stability: StabilityOptimizationConfig = field(default_factory=StabilityOptimizationConfig)
    interaction: InteractionOptimizationConfig = field(default_factory=InteractionOptimizationConfig)
    resource: ResourceOptimizationConfig = field(default_factory=ResourceOptimizationConfig)
    
    # 执行配置
    execution_mode: str = "automatic"  # 执行模式：automatic, manual, scheduled
    execution_interval_hours: int = 24  # 执行间隔（小时）
    max_execution_time_minutes: int = 30  # 最大执行时间（分钟）
    
    # 安全配置
    safety_checks: bool = True  # 安全检查
    backup_before_optimization: bool = True  # 优化前备份
    rollback_on_failure: bool = True  # 失败时回滚
    
    # 验证配置
    validation_enabled: bool = True  # 启用验证
    validation_timeout_seconds: int = 30  # 验证超时
    min_improvement_threshold: float = 0.05  # 最小改进阈值（5%）
    
    # 报告配置
    generate_reports: bool = True  # 生成报告
    detailed_reports: bool = True  # 详细报告
    report_formats: List[str] = field(default_factory=lambda: ["json", "html"])
    
    # 并行配置
    parallel_optimization: bool = True  # 并行优化
    max_parallel_tasks: int = 3  # 最大并行任务数
    
    # 学习配置
    learning_enabled: bool = True  # 启用学习
    feedback_collection: bool = True  # 收集反馈
    adaptive_optimization: bool = True  # 自适应优化
    
    def validate(self) -> bool:
        """
        验证配置
        
        Returns:
            bool: 配置是否有效
        """
        try:
            # 验证基本配置
            if not isinstance(self.enabled, bool):
                return False
            
            if not isinstance(self.strategy, OptimizationStrategy):
                return False
            
            if not isinstance(self.primary_target, OptimizationTarget):
                return False
            
            # 验证性能配置
            if self.performance.target_improvement <= 0 or self.performance.target_improvement > 1:
                return False
            
            if self.performance.target_response_time <= 0:
                return False
            
            # 验证可见性配置
            if not (0.0 <= self.visibility.target_visibility_score <= 1.0):
                return False
            
            # 验证可访问性配置
            if self.accessibility.min_contrast_ratio <= 0:
                return False
            
            # 验证稳定性配置
            if not (0.0 <= self.stability.target_stability_score <= 1.0):
                return False
            
            # 验证交互配置
            if self.interaction.click_target_size <= 0:
                return False
            
            # 验证执行配置
            if self.execution_interval_hours <= 0:
                return False
            
            if self.max_execution_time_minutes <= 0:
                return False
            
            # 验证验证配置
            if self.validation_timeout_seconds <= 0:
                return False
            
            if not (0.0 <= self.min_improvement_threshold <= 1.0):
                return False
            
            return True
            
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return {
            'enabled': self.enabled,
            'strategy': self.strategy.value,
            'primary_target': self.primary_target.value,
            'performance': {
                'enabled': self.performance.enabled,
                'target_improvement': self.performance.target_improvement,
                'response_time_optimization': self.performance.response_time_optimization,
                'target_response_time': self.performance.target_response_time,
                'max_response_time': self.performance.max_response_time,
                'load_time_optimization': self.performance.load_time_optimization,
                'target_load_time': self.performance.target_load_time,
                'max_load_time': self.performance.max_load_time,
                'render_optimization': self.performance.render_optimization,
                'target_render_time': self.performance.target_render_time,
                'resource_optimization': self.performance.resource_optimization,
                'memory_limit_mb': self.performance.memory_limit_mb,
                'cpu_limit_percent': self.performance.cpu_limit_percent,
                'caching_enabled': self.performance.caching_enabled,
                'cache_strategies': self.performance.cache_strategies,
                'compression_enabled': self.performance.compression_enabled,
                'compression_types': self.performance.compression_types,
                'preloading_enabled': self.performance.preloading_enabled,
                'preload_strategies': self.performance.preload_strategies
            },
            'visibility': {
                'enabled': self.visibility.enabled,
                'target_visibility_score': self.visibility.target_visibility_score,
                'layout_optimization': self.visibility.layout_optimization,
                'viewport_optimization': self.visibility.viewport_optimization,
                'z_index_optimization': self.visibility.z_index_optimization,
                'style_optimization': self.visibility.style_optimization,
                'opacity_threshold': self.visibility.opacity_threshold,
                'contrast_optimization': self.visibility.contrast_optimization,
                'position_optimization': self.visibility.position_optimization,
                'auto_scroll_to_view': self.visibility.auto_scroll_to_view,
                'center_in_viewport': self.visibility.center_in_viewport,
                'size_optimization': self.visibility.size_optimization,
                'min_width': self.visibility.min_width,
                'min_height': self.visibility.min_height,
                'animation_optimization': self.visibility.animation_optimization,
                'reduce_motion': self.visibility.reduce_motion,
                'animation_duration_limit': self.visibility.animation_duration_limit
            },
            'accessibility': {
                'enabled': self.accessibility.enabled,
                'target_accessibility_score': self.accessibility.target_accessibility_score,
                'aria_optimization': self.accessibility.aria_optimization,
                'auto_add_aria_labels': self.accessibility.auto_add_aria_labels,
                'aria_role_optimization': self.accessibility.aria_role_optimization,
                'color_contrast_optimization': self.accessibility.color_contrast_optimization,
                'min_contrast_ratio': self.accessibility.min_contrast_ratio,
                'target_contrast_ratio': self.accessibility.target_contrast_ratio,
                'keyboard_navigation_optimization': self.accessibility.keyboard_navigation_optimization,
                'tab_index_optimization': self.accessibility.tab_index_optimization,
                'focus_indicator_optimization': self.accessibility.focus_indicator_optimization,
                'semantic_optimization': self.accessibility.semantic_optimization,
                'heading_structure_optimization': self.accessibility.heading_structure_optimization,
                'landmark_optimization': self.accessibility.landmark_optimization,
                'text_optimization': self.accessibility.text_optimization,
                'font_size_optimization': self.accessibility.font_size_optimization,
                'line_height_optimization': self.accessibility.line_height_optimization,
                'media_optimization': self.accessibility.media_optimization,
                'alt_text_optimization': self.accessibility.alt_text_optimization,
                'caption_optimization': self.accessibility.caption_optimization
            },
            'stability': {
                'enabled': self.stability.enabled,
                'target_stability_score': self.stability.target_stability_score,
                'layout_stability_optimization': self.stability.layout_stability_optimization,
                'cumulative_layout_shift_limit': self.stability.cumulative_layout_shift_limit,
                'position_stability_optimization': self.stability.position_stability_optimization,
                'max_position_variance': self.stability.max_position_variance,
                'size_stability_optimization': self.stability.size_stability_optimization,
                'max_size_variance': self.stability.max_size_variance,
                'attribute_stability_optimization': self.stability.attribute_stability_optimization,
                'critical_attributes': self.stability.critical_attributes,
                'availability_optimization': self.stability.availability_optimization,
                'min_availability_rate': self.stability.min_availability_rate,
                'error_handling_optimization': self.stability.error_handling_optimization,
                'graceful_degradation': self.stability.graceful_degradation,
                'fallback_strategies': self.stability.fallback_strategies
            },
            'interaction': {
                'enabled': self.interaction.enabled,
                'target_interaction_score': self.interaction.target_interaction_score,
                'click_optimization': self.interaction.click_optimization,
                'click_target_size': self.interaction.click_target_size,
                'click_success_rate_target': self.interaction.click_success_rate_target,
                'input_optimization': self.interaction.input_optimization,
                'input_validation_optimization': self.interaction.input_validation_optimization,
                'input_feedback_optimization': self.interaction.input_feedback_optimization,
                'responsiveness_optimization': self.interaction.responsiveness_optimization,
                'max_response_delay': self.interaction.max_response_delay,
                'gesture_optimization': self.interaction.gesture_optimization,
                'touch_target_optimization': self.interaction.touch_target_optimization,
                'swipe_optimization': self.interaction.swipe_optimization,
                'state_management_optimization': self.interaction.state_management_optimization,
                'state_persistence': self.interaction.state_persistence,
                'state_recovery': self.interaction.state_recovery,
                'feedback_optimization': self.interaction.feedback_optimization,
                'visual_feedback': self.interaction.visual_feedback,
                'haptic_feedback': self.interaction.haptic_feedback,
                'audio_feedback': self.interaction.audio_feedback
            },
            'resource': {
                'enabled': self.resource.enabled,
                'optimization_level': self.resource.optimization_level,
                'memory_optimization': self.resource.memory_optimization,
                'memory_limit_mb': self.resource.memory_limit_mb,
                'garbage_collection_optimization': self.resource.garbage_collection_optimization,
                'cpu_optimization': self.resource.cpu_optimization,
                'cpu_limit_percent': self.resource.cpu_limit_percent,
                'thread_pool_optimization': self.resource.thread_pool_optimization,
                'network_optimization': self.resource.network_optimization,
                'connection_pooling': self.resource.connection_pooling,
                'request_batching': self.resource.request_batching,
                'storage_optimization': self.resource.storage_optimization,
                'local_storage_limit_mb': self.resource.local_storage_limit_mb,
                'cache_optimization': self.resource.cache_optimization,
                'concurrency_optimization': self.resource.concurrency_optimization,
                'max_concurrent_requests': self.resource.max_concurrent_requests,
                'queue_management': self.resource.queue_management
            },
            'execution_mode': self.execution_mode,
            'execution_interval_hours': self.execution_interval_hours,
            'max_execution_time_minutes': self.max_execution_time_minutes,
            'safety_checks': self.safety_checks,
            'backup_before_optimization': self.backup_before_optimization,
            'rollback_on_failure': self.rollback_on_failure,
            'validation_enabled': self.validation_enabled,
            'validation_timeout_seconds': self.validation_timeout_seconds,
            'min_improvement_threshold': self.min_improvement_threshold,
            'generate_reports': self.generate_reports,
            'detailed_reports': self.detailed_reports,
            'report_formats': self.report_formats,
            'parallel_optimization': self.parallel_optimization,
            'max_parallel_tasks': self.max_parallel_tasks,
            'learning_enabled': self.learning_enabled,
            'feedback_collection': self.feedback_collection,
            'adaptive_optimization': self.adaptive_optimization
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptimizationConfig':
        """
        从字典创建配置
        
        Args:
            data: 配置字典
            
        Returns:
            OptimizationConfig: 优化配置实例
        """
        # 创建子配置对象
        perf_data = data.get('performance', {})
        performance = PerformanceOptimizationConfig(
            enabled=perf_data.get('enabled', True),
            target_improvement=perf_data.get('target_improvement', 0.2),
            response_time_optimization=perf_data.get('response_time_optimization', True),
            target_response_time=perf_data.get('target_response_time', 1.0),
            max_response_time=perf_data.get('max_response_time', 3.0),
            load_time_optimization=perf_data.get('load_time_optimization', True),
            target_load_time=perf_data.get('target_load_time', 0.5),
            max_load_time=perf_data.get('max_load_time', 2.0),
            render_optimization=perf_data.get('render_optimization', True),
            target_render_time=perf_data.get('target_render_time', 0.3),
            resource_optimization=perf_data.get('resource_optimization', True),
            memory_limit_mb=perf_data.get('memory_limit_mb', 100),
            cpu_limit_percent=perf_data.get('cpu_limit_percent', 50),
            caching_enabled=perf_data.get('caching_enabled', True),
            cache_strategies=perf_data.get('cache_strategies', ["browser_cache", "cdn_cache", "application_cache"]),
            compression_enabled=perf_data.get('compression_enabled', True),
            compression_types=perf_data.get('compression_types', ["gzip", "brotli"]),
            preloading_enabled=perf_data.get('preloading_enabled', True),
            preload_strategies=perf_data.get('preload_strategies', ["dns_prefetch", "preconnect", "preload", "prefetch"])
        )
        
        vis_data = data.get('visibility', {})
        visibility = VisibilityOptimizationConfig(
            enabled=vis_data.get('enabled', True),
            target_visibility_score=vis_data.get('target_visibility_score', 0.9),
            layout_optimization=vis_data.get('layout_optimization', True),
            viewport_optimization=vis_data.get('viewport_optimization', True),
            z_index_optimization=vis_data.get('z_index_optimization', True),
            style_optimization=vis_data.get('style_optimization', True),
            opacity_threshold=vis_data.get('opacity_threshold', 0.8),
            contrast_optimization=vis_data.get('contrast_optimization', True),
            position_optimization=vis_data.get('position_optimization', True),
            auto_scroll_to_view=vis_data.get('auto_scroll_to_view', True),
            center_in_viewport=vis_data.get('center_in_viewport', False),
            size_optimization=vis_data.get('size_optimization', True),
            min_width=vis_data.get('min_width', 10),
            min_height=vis_data.get('min_height', 10),
            animation_optimization=vis_data.get('animation_optimization', True),
            reduce_motion=vis_data.get('reduce_motion', False),
            animation_duration_limit=vis_data.get('animation_duration_limit', 1.0)
        )
        
        acc_data = data.get('accessibility', {})
        accessibility = AccessibilityOptimizationConfig(
            enabled=acc_data.get('enabled', True),
            target_accessibility_score=acc_data.get('target_accessibility_score', 0.9),
            aria_optimization=acc_data.get('aria_optimization', True),
            auto_add_aria_labels=acc_data.get('auto_add_aria_labels', True),
            aria_role_optimization=acc_data.get('aria_role_optimization', True),
            color_contrast_optimization=acc_data.get('color_contrast_optimization', True),
            min_contrast_ratio=acc_data.get('min_contrast_ratio', 4.5),
            target_contrast_ratio=acc_data.get('target_contrast_ratio', 7.0),
            keyboard_navigation_optimization=acc_data.get('keyboard_navigation_optimization', True),
            tab_index_optimization=acc_data.get('tab_index_optimization', True),
            focus_indicator_optimization=acc_data.get('focus_indicator_optimization', True),
            semantic_optimization=acc_data.get('semantic_optimization', True),
            heading_structure_optimization=acc_data.get('heading_structure_optimization', True),
            landmark_optimization=acc_data.get('landmark_optimization', True),
            text_optimization=acc_data.get('text_optimization', True),
            font_size_optimization=acc_data.get('font_size_optimization', True),
            line_height_optimization=acc_data.get('line_height_optimization', True),
            media_optimization=acc_data.get('media_optimization', True),
            alt_text_optimization=acc_data.get('alt_text_optimization', True),
            caption_optimization=acc_data.get('caption_optimization', True)
        )
        
        stab_data = data.get('stability', {})
        stability = StabilityOptimizationConfig(
            enabled=stab_data.get('enabled', True),
            target_stability_score=stab_data.get('target_stability_score', 0.9),
            layout_stability_optimization=stab_data.get('layout_stability_optimization', True),
            cumulative_layout_shift_limit=stab_data.get('cumulative_layout_shift_limit', 0.1),
            position_stability_optimization=stab_data.get('position_stability_optimization', True),
            max_position_variance=stab_data.get('max_position_variance', 5.0),
            size_stability_optimization=stab_data.get('size_stability_optimization', True),
            max_size_variance=stab_data.get('max_size_variance', 2.0),
            attribute_stability_optimization=stab_data.get('attribute_stability_optimization', True),
            critical_attributes=stab_data.get('critical_attributes', ["id", "class", "data-testid", "aria-label"]),
            availability_optimization=stab_data.get('availability_optimization', True),
            min_availability_rate=stab_data.get('min_availability_rate', 0.95),
            error_handling_optimization=stab_data.get('error_handling_optimization', True),
            graceful_degradation=stab_data.get('graceful_degradation', True),
            fallback_strategies=stab_data.get('fallback_strategies', ["retry", "alternative_selector", "wait_and_retry"])
        )
        
        int_data = data.get('interaction', {})
        interaction = InteractionOptimizationConfig(
            enabled=int_data.get('enabled', True),
            target_interaction_score=int_data.get('target_interaction_score', 0.9),
            click_optimization=int_data.get('click_optimization', True),
            click_target_size=int_data.get('click_target_size', 44),
            click_success_rate_target=int_data.get('click_success_rate_target', 0.95),
            input_optimization=int_data.get('input_optimization', True),
            input_validation_optimization=int_data.get('input_validation_optimization', True),
            input_feedback_optimization=int_data.get('input_feedback_optimization', True),
            responsiveness_optimization=int_data.get('responsiveness_optimization', True),
            max_response_delay=int_data.get('max_response_delay', 0.1),
            gesture_optimization=int_data.get('gesture_optimization', True),
            touch_target_optimization=int_data.get('touch_target_optimization', True),
            swipe_optimization=int_data.get('swipe_optimization', True),
            state_management_optimization=int_data.get('state_management_optimization', True),
            state_persistence=int_data.get('state_persistence', True),
            state_recovery=int_data.get('state_recovery', True),
            feedback_optimization=int_data.get('feedback_optimization', True),
            visual_feedback=int_data.get('visual_feedback', True),
            haptic_feedback=int_data.get('haptic_feedback', False),
            audio_feedback=int_data.get('audio_feedback', False)
        )
        
        res_data = data.get('resource', {})
        resource = ResourceOptimizationConfig(
            enabled=res_data.get('enabled', True),
            optimization_level=res_data.get('optimization_level', "balanced"),
            memory_optimization=res_data.get('memory_optimization', True),
            memory_limit_mb=res_data.get('memory_limit_mb', 200),
            garbage_collection_optimization=res_data.get('garbage_collection_optimization', True),
            cpu_optimization=res_data.get('cpu_optimization', True),
            cpu_limit_percent=res_data.get('cpu_limit_percent', 70),
            thread_pool_optimization=res_data.get('thread_pool_optimization', True),
            network_optimization=res_data.get('network_optimization', True),
            connection_pooling=res_data.get('connection_pooling', True),
            request_batching=res_data.get('request_batching', True),
            storage_optimization=res_data.get('storage_optimization', True),
            local_storage_limit_mb=res_data.get('local_storage_limit_mb', 50),
            cache_optimization=res_data.get('cache_optimization', True),
            concurrency_optimization=res_data.get('concurrency_optimization', True),
            max_concurrent_requests=res_data.get('max_concurrent_requests', 10),
            queue_management=res_data.get('queue_management', True)
        )
        
        return cls(
            enabled=data.get('enabled', True),
            strategy=OptimizationStrategy(data.get('strategy', 'balanced')),
            primary_target=OptimizationTarget(data.get('primary_target', 'overall')),
            performance=performance,
            visibility=visibility,
            accessibility=accessibility,
            stability=stability,
            interaction=interaction,
            resource=resource,
            execution_mode=data.get('execution_mode', "automatic"),
            execution_interval_hours=data.get('execution_interval_hours', 24),
            max_execution_time_minutes=data.get('max_execution_time_minutes', 30),
            safety_checks=data.get('safety_checks', True),
            backup_before_optimization=data.get('backup_before_optimization', True),
            rollback_on_failure=data.get('rollback_on_failure', True),
            validation_enabled=data.get('validation_enabled', True),
            validation_timeout_seconds=data.get('validation_timeout_seconds', 30),
            min_improvement_threshold=data.get('min_improvement_threshold', 0.05),
            generate_reports=data.get('generate_reports', True),
            detailed_reports=data.get('detailed_reports', True),
            report_formats=data.get('report_formats', ["json", "html"]),
            parallel_optimization=data.get('parallel_optimization', True),
            max_parallel_tasks=data.get('max_parallel_tasks', 3),
            learning_enabled=data.get('learning_enabled', True),
            feedback_collection=data.get('feedback_collection', True),
            adaptive_optimization=data.get('adaptive_optimization', True)
        )