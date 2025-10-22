# -*- encoding=utf8 -*-
"""
统一监控器

整合原有的分散监控功能，提供统一的监控接口
"""

import time
import threading
import logging
import psutil
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from datetime import datetime, timedelta

from .base_interfaces import IMonitor
from .unified_models import (
    ElementMapping, ElementInfo, QualityMetrics, QualityLevel,
    AnalysisResult, Report
)


@dataclass
class MonitoringEvent:
    """监控事件"""
    timestamp: float
    event_type: str
    source: str
    data: Dict[str, Any]
    severity: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL


@dataclass
class PerformanceSnapshot:
    """性能快照"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    active_threads: int
    cache_hit_rate: float
    processing_rate: float
    error_count: int


@dataclass
class QualitySnapshot:
    """质量快照"""
    timestamp: float
    overall_score: float
    coverage_score: float
    accuracy_score: float
    consistency_score: float
    completeness_score: float
    reliability_score: float
    quality_level: QualityLevel


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    condition: Callable[[Any], bool]
    severity: str
    message_template: str
    cooldown_seconds: float = 300.0
    last_triggered: float = 0.0


class UnifiedMonitor(IMonitor):
    """统一监控器"""
    
    def __init__(self, max_events: int = 10000, max_snapshots: int = 1000):
        self.max_events = max_events
        self.max_snapshots = max_snapshots
        
        # 事件存储
        self._events: deque = deque(maxlen=max_events)
        self._events_lock = threading.RLock()
        
        # 性能快照
        self._performance_snapshots: deque = deque(maxlen=max_snapshots)
        self._performance_lock = threading.RLock()
        
        # 质量快照
        self._quality_snapshots: deque = deque(maxlen=max_snapshots)
        self._quality_lock = threading.RLock()
        
        # 告警规则
        self._alert_rules: List[AlertRule] = []
        self._alert_callbacks: List[Callable[[MonitoringEvent], None]] = []
        
        # 监控状态
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None
        
        # 统计信息
        self._stats = defaultdict(int)
        self._stats_lock = threading.RLock()
        
        # 初始化日志
        self._setup_logging()
        
        # 初始化默认告警规则
        self._setup_default_alert_rules()
    
    def start_monitoring(self, element_ids: List[str] = None) -> str:
        """开始监控"""
        if self._monitoring_active:
            return "existing_session"
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        
        session_id = f"session_{int(time.time())}"
        self.log_event("MONITOR_START", "system", {
            "message": "监控系统已启动",
            "session_id": session_id,
            "element_ids": element_ids or []
        })
        return session_id
    
    def stop_monitoring(self, session_id: str) -> Dict[str, Any]:
        """停止监控"""
        if not self._monitoring_active:
            return {"status": "not_active", "message": "监控系统未运行"}
        
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5.0)
        
        self.log_event("MONITOR_STOP", "system", {
            "message": "监控系统已停止",
            "session_id": session_id
        })
        
        return {
            "status": "stopped",
            "session_id": session_id,
            "message": "监控系统已成功停止"
        }
    
    def get_monitoring_status(self, session_id: str) -> Dict[str, Any]:
        """获取监控状态"""
        return {
            "session_id": session_id,
            "active": self._monitoring_active,
            "thread_alive": self._monitoring_thread.is_alive() if self._monitoring_thread else False,
            "events_count": len(self._events),
            "performance_snapshots_count": len(self._performance_snapshots),
            "quality_snapshots_count": len(self._quality_snapshots),
            "statistics": dict(self._stats)
        }
    
    def log_event(self, event_type: str, source: str, data: Dict[str, Any], 
                  severity: str = "INFO"):
        """记录监控事件"""
        event = MonitoringEvent(
            timestamp=time.time(),
            event_type=event_type,
            source=source,
            data=data,
            severity=severity
        )
        
        with self._events_lock:
            self._events.append(event)
        
        # 更新统计信息
        with self._stats_lock:
            self._stats[f"events_{event_type}"] += 1
            self._stats[f"events_{severity.lower()}"] += 1
        
        # 检查告警规则
        self._check_alert_rules(event)
        
        # 记录到日志
        self._log_to_file(event)
    
    def record_performance(self, cpu_usage: float = 0.0, memory_usage: float = 0.0,
                          active_threads: int = 0, cache_hit_rate: float = 0.0,
                          processing_rate: float = 0.0, error_count: int = 0):
        """记录性能快照"""
        snapshot = PerformanceSnapshot(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_threads=active_threads,
            cache_hit_rate=cache_hit_rate,
            processing_rate=processing_rate,
            error_count=error_count
        )
        
        with self._performance_lock:
            self._performance_snapshots.append(snapshot)
        
        # 检查性能告警
        self._check_performance_alerts(snapshot)
    
    def record_quality(self, quality_metrics: QualityMetrics):
        """记录质量快照"""
        # 从QualityMetrics对象中提取分数
        performance_score = quality_metrics.performance_score.score / 100.0
        visibility_score = quality_metrics.visibility_score.score / 100.0
        accessibility_score = quality_metrics.accessibility_score.score / 100.0
        stability_score = quality_metrics.stability_score.score / 100.0
        interaction_score = quality_metrics.interaction_score.score / 100.0
        
        # 计算总体分数
        overall_score = (
            performance_score * 0.25 +
            visibility_score * 0.25 +
            accessibility_score * 0.20 +
            stability_score * 0.15 +
            interaction_score * 0.15
        )
        
        # 确定质量等级
        if overall_score >= 0.9:
            quality_level = QualityLevel.EXCELLENT
        elif overall_score >= 0.7:
            quality_level = QualityLevel.GOOD
        elif overall_score >= 0.5:
            quality_level = QualityLevel.FAIR
        else:
            quality_level = QualityLevel.POOR
        
        snapshot = QualitySnapshot(
            timestamp=time.time(),
            overall_score=overall_score,
            coverage_score=performance_score,
            accuracy_score=visibility_score,
            consistency_score=accessibility_score,
            completeness_score=stability_score,
            reliability_score=interaction_score,
            quality_level=quality_level
        )
        
        with self._quality_lock:
            self._quality_snapshots.append(snapshot)
        
        # 检查质量告警
        self._check_quality_alerts(snapshot)
    
    def get_events(self, event_type: Optional[str] = None, 
                   source: Optional[str] = None,
                   severity: Optional[str] = None,
                   since: Optional[float] = None,
                   limit: Optional[int] = None) -> List[MonitoringEvent]:
        """获取监控事件"""
        with self._events_lock:
            events = list(self._events)
        
        # 过滤条件
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if source:
            events = [e for e in events if e.source == source]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        # 按时间倒序排列
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 限制数量
        if limit:
            events = events[:limit]
        
        return events
    
    def get_performance_history(self, since: Optional[float] = None,
                               limit: Optional[int] = None) -> List[PerformanceSnapshot]:
        """获取性能历史"""
        with self._performance_lock:
            snapshots = list(self._performance_snapshots)
        
        if since:
            snapshots = [s for s in snapshots if s.timestamp >= since]
        
        # 按时间倒序排列
        snapshots.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            snapshots = snapshots[:limit]
        
        return snapshots
    
    def get_quality_history(self, since: Optional[float] = None,
                           limit: Optional[int] = None) -> List[QualitySnapshot]:
        """获取质量历史"""
        with self._quality_lock:
            snapshots = list(self._quality_snapshots)
        
        if since:
            snapshots = [s for s in snapshots if s.timestamp >= since]
        
        # 按时间倒序排列
        snapshots.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            snapshots = snapshots[:limit]
        
        return snapshots
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._stats_lock:
            stats = dict(self._stats)
        
        # 添加实时统计
        current_time = time.time()
        
        # 最近1小时的事件数
        hour_ago = current_time - 3600
        recent_events = self.get_events(since=hour_ago)
        stats['events_last_hour'] = len(recent_events)
        
        # 最近性能快照
        recent_performance = self.get_performance_history(since=hour_ago, limit=1)
        if recent_performance:
            latest_perf = recent_performance[0]
            stats['current_cpu_usage'] = latest_perf.cpu_usage
            stats['current_memory_usage'] = latest_perf.memory_usage
            stats['current_cache_hit_rate'] = latest_perf.cache_hit_rate
        
        # 最近质量快照
        recent_quality = self.get_quality_history(since=hour_ago, limit=1)
        if recent_quality:
            latest_quality = recent_quality[0]
            stats['current_quality_score'] = latest_quality.overall_score
            stats['current_quality_level'] = latest_quality.quality_level.value
        
        return stats
    
    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self._alert_rules.append(rule)
        self.log_event("ALERT_RULE_ADDED", "monitor", 
                      {"rule_name": rule.name, "severity": rule.severity})
    
    def remove_alert_rule(self, rule_name: str) -> bool:
        """移除告警规则"""
        for i, rule in enumerate(self._alert_rules):
            if rule.name == rule_name:
                del self._alert_rules[i]
                self.log_event("ALERT_RULE_REMOVED", "monitor", 
                              {"rule_name": rule_name})
                return True
        return False
    
    def add_alert_callback(self, callback: Callable[[MonitoringEvent], None]):
        """添加告警回调"""
        self._alert_callbacks.append(callback)
    
    def generate_monitoring_report(self, since: Optional[float] = None) -> Dict[str, Any]:
        """生成监控报告"""
        if since is None:
            since = time.time() - 86400  # 默认最近24小时
        
        # 获取数据
        events = self.get_events(since=since)
        performance_history = self.get_performance_history(since=since)
        quality_history = self.get_quality_history(since=since)
        stats = self.get_statistics()
        
        # 分析事件
        event_summary = self._analyze_events(events)
        
        # 分析性能趋势
        performance_analysis = self._analyze_performance_trends(performance_history)
        
        # 分析质量趋势
        quality_analysis = self._analyze_quality_trends(quality_history)
        
        return {
            'report_time': time.time(),
            'period_start': since,
            'period_end': time.time(),
            'statistics': stats,
            'event_summary': event_summary,
            'performance_analysis': performance_analysis,
            'quality_analysis': quality_analysis,
            'recommendations': self._generate_recommendations(
                event_summary, performance_analysis, quality_analysis
            )
        }
    
    def _monitoring_loop(self):
        """监控循环"""
        while self._monitoring_active:
            try:
                # 收集系统性能指标
                self._collect_system_metrics()
                
                # 清理过期数据
                self._cleanup_old_data()
                
                # 等待下一次监控
                time.sleep(60)  # 每分钟监控一次
                
            except Exception as e:
                self.log_event("MONITOR_ERROR", "system", 
                              {"error": str(e)}, "ERROR")
                time.sleep(10)  # 出错时短暂等待
    
    def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            import psutil
            
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 线程数
            active_threads = threading.active_count()
            
            # 记录性能快照
            self.record_performance(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                active_threads=active_threads
            )
            
        except ImportError:
            # 如果没有psutil，使用简单的指标
            active_threads = threading.active_count()
            self.record_performance(active_threads=active_threads)
        except Exception as e:
            self.log_event("METRICS_COLLECTION_ERROR", "system", 
                          {"error": str(e)}, "WARNING")
    
    def _cleanup_old_data(self):
        """清理过期数据"""
        # 清理过期的统计信息
        cutoff_time = time.time() - 86400 * 7  # 保留7天
        
        with self._stats_lock:
            # 重置一些计数器
            for key in list(self._stats.keys()):
                if key.startswith('temp_'):
                    del self._stats[key]
    
    def _check_alert_rules(self, event: MonitoringEvent):
        """检查告警规则"""
        current_time = time.time()
        
        for rule in self._alert_rules:
            # 检查冷却时间
            if current_time - rule.last_triggered < rule.cooldown_seconds:
                continue
            
            # 检查条件
            try:
                if rule.condition(event):
                    # 触发告警
                    alert_event = MonitoringEvent(
                        timestamp=current_time,
                        event_type="ALERT",
                        source="alert_system",
                        data={
                            "rule_name": rule.name,
                            "message": rule.message_template.format(**event.data),
                            "original_event": event.__dict__
                        },
                        severity=rule.severity
                    )
                    
                    # 记录告警事件
                    with self._events_lock:
                        self._events.append(alert_event)
                    
                    # 调用告警回调
                    for callback in self._alert_callbacks:
                        try:
                            callback(alert_event)
                        except Exception as e:
                            self.log_event("ALERT_CALLBACK_ERROR", "alert_system",
                                          {"error": str(e)}, "ERROR")
                    
                    # 更新触发时间
                    rule.last_triggered = current_time
                    
            except Exception as e:
                self.log_event("ALERT_RULE_ERROR", "alert_system",
                              {"rule_name": rule.name, "error": str(e)}, "ERROR")
    
    def _check_performance_alerts(self, snapshot: PerformanceSnapshot):
        """检查性能告警"""
        # CPU使用率告警
        if snapshot.cpu_usage > 90:
            self.log_event("HIGH_CPU_USAGE", "performance",
                          {"cpu_usage": snapshot.cpu_usage}, "WARNING")
        
        # 内存使用率告警
        if snapshot.memory_usage > 85:
            self.log_event("HIGH_MEMORY_USAGE", "performance",
                          {"memory_usage": snapshot.memory_usage}, "WARNING")
        
        # 缓存命中率告警
        if snapshot.cache_hit_rate < 30:
            self.log_event("LOW_CACHE_HIT_RATE", "performance",
                          {"cache_hit_rate": snapshot.cache_hit_rate}, "WARNING")
        
        # 错误数量告警
        if snapshot.error_count > 10:
            self.log_event("HIGH_ERROR_COUNT", "performance",
                          {"error_count": snapshot.error_count}, "ERROR")
    
    def _check_quality_alerts(self, snapshot: QualitySnapshot):
        """检查质量告警"""
        # 整体质量告警
        if snapshot.overall_score < 0.5:
            self.log_event("LOW_QUALITY_SCORE", "quality",
                          {"overall_score": snapshot.overall_score}, "WARNING")
        
        # 覆盖率告警
        if snapshot.coverage_score < 0.6:
            self.log_event("LOW_COVERAGE", "quality",
                          {"coverage_score": snapshot.coverage_score}, "WARNING")
        
        # 准确性告警
        if snapshot.accuracy_score < 0.7:
            self.log_event("LOW_ACCURACY", "quality",
                          {"accuracy_score": snapshot.accuracy_score}, "WARNING")
    
    def _analyze_events(self, events: List[MonitoringEvent]) -> Dict[str, Any]:
        """分析事件"""
        if not events:
            return {}
        
        # 按类型统计
        event_types = defaultdict(int)
        severity_counts = defaultdict(int)
        source_counts = defaultdict(int)
        
        for event in events:
            event_types[event.event_type] += 1
            severity_counts[event.severity] += 1
            source_counts[event.source] += 1
        
        return {
            'total_events': len(events),
            'event_types': dict(event_types),
            'severity_distribution': dict(severity_counts),
            'source_distribution': dict(source_counts),
            'error_rate': severity_counts.get('ERROR', 0) / len(events) * 100
        }
    
    def _analyze_performance_trends(self, snapshots: List[PerformanceSnapshot]) -> Dict[str, Any]:
        """分析性能趋势"""
        if not snapshots:
            return {}
        
        # 计算平均值
        avg_cpu = sum(s.cpu_usage for s in snapshots) / len(snapshots)
        avg_memory = sum(s.memory_usage for s in snapshots) / len(snapshots)
        avg_cache_hit = sum(s.cache_hit_rate for s in snapshots) / len(snapshots)
        
        # 计算趋势
        if len(snapshots) >= 2:
            recent_cpu = sum(s.cpu_usage for s in snapshots[:10]) / min(10, len(snapshots))
            old_cpu = sum(s.cpu_usage for s in snapshots[-10:]) / min(10, len(snapshots))
            cpu_trend = "increasing" if recent_cpu > old_cpu * 1.1 else "decreasing" if recent_cpu < old_cpu * 0.9 else "stable"
        else:
            cpu_trend = "unknown"
        
        return {
            'average_cpu_usage': avg_cpu,
            'average_memory_usage': avg_memory,
            'average_cache_hit_rate': avg_cache_hit,
            'cpu_trend': cpu_trend,
            'total_snapshots': len(snapshots)
        }
    
    def _analyze_quality_trends(self, snapshots: List[QualitySnapshot]) -> Dict[str, Any]:
        """分析质量趋势"""
        if not snapshots:
            return {}
        
        # 计算平均质量分数
        avg_quality = sum(s.overall_score for s in snapshots) / len(snapshots)
        
        # 质量等级分布
        quality_levels = defaultdict(int)
        for snapshot in snapshots:
            quality_levels[snapshot.quality_level.value] += 1
        
        # 质量趋势
        if len(snapshots) >= 2:
            recent_quality = sum(s.overall_score for s in snapshots[:5]) / min(5, len(snapshots))
            old_quality = sum(s.overall_score for s in snapshots[-5:]) / min(5, len(snapshots))
            quality_trend = "improving" if recent_quality > old_quality * 1.05 else "declining" if recent_quality < old_quality * 0.95 else "stable"
        else:
            quality_trend = "unknown"
        
        return {
            'average_quality_score': avg_quality,
            'quality_level_distribution': dict(quality_levels),
            'quality_trend': quality_trend,
            'total_snapshots': len(snapshots)
        }
    
    def _generate_recommendations(self, event_summary: Dict[str, Any],
                                 performance_analysis: Dict[str, Any],
                                 quality_analysis: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于事件分析的建议
        if event_summary.get('error_rate', 0) > 5:
            recommendations.append("错误率较高，建议检查系统稳定性")
        
        # 基于性能分析的建议
        if performance_analysis.get('average_cpu_usage', 0) > 80:
            recommendations.append("CPU使用率较高，建议优化性能")
        
        if performance_analysis.get('average_memory_usage', 0) > 80:
            recommendations.append("内存使用率较高，建议优化内存管理")
        
        if performance_analysis.get('average_cache_hit_rate', 0) < 50:
            recommendations.append("缓存命中率较低，建议优化缓存策略")
        
        # 基于质量分析的建议
        if quality_analysis.get('average_quality_score', 0) < 0.7:
            recommendations.append("整体质量分数较低，建议提升数据质量")
        
        if quality_analysis.get('quality_trend') == 'declining':
            recommendations.append("质量呈下降趋势，建议加强质量控制")
        
        return recommendations
    
    def _setup_logging(self):
        """设置日志"""
        self.logger = logging.getLogger('unified_monitor')
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        handler = logging.FileHandler('monitor.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _log_to_file(self, event: MonitoringEvent):
        """记录事件到文件"""
        try:
            log_level = getattr(logging, event.severity, logging.INFO)
            self.logger.log(log_level, f"{event.event_type} from {event.source}: {event.data}")
        except Exception:
            pass  # 忽略日志错误
    
    def _setup_default_alert_rules(self):
        """设置默认告警规则"""
        # 高错误率告警
        self.add_alert_rule(AlertRule(
            name="high_error_rate",
            condition=lambda event: event.severity == "ERROR",
            severity="ERROR",
            message_template="检测到错误事件: {message}",
            cooldown_seconds=300
        ))
        
        # 系统异常告警
        self.add_alert_rule(AlertRule(
            name="system_exception",
            condition=lambda event: event.event_type in ["SYSTEM_ERROR", "CRITICAL_ERROR"],
            severity="CRITICAL",
            message_template="系统异常: {message}",
            cooldown_seconds=60
        ))