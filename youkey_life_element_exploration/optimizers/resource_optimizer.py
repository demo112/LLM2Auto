"""
资源优化器模块

提供资源分配、调度和利用率优化功能，包括计算资源、时间资源、人力资源等的优化管理。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta
from enum import Enum
import statistics
import math
from collections import defaultdict, deque
import heapq

from ..config.optimization_config import OptimizationConfig


class ResourceType(Enum):
    """资源类型枚举"""
    COMPUTE = "compute"  # 计算资源
    MEMORY = "memory"    # 内存资源
    STORAGE = "storage"  # 存储资源
    NETWORK = "network"  # 网络资源
    TIME = "time"        # 时间资源
    HUMAN = "human"      # 人力资源


class ResourcePriority(Enum):
    """资源优先级枚举"""
    CRITICAL = "critical"  # 关键
    HIGH = "high"         # 高
    MEDIUM = "medium"     # 中
    LOW = "low"           # 低


class AllocationStrategy(Enum):
    """分配策略枚举"""
    FAIR_SHARE = "fair_share"        # 公平分配
    PRIORITY_BASED = "priority_based" # 基于优先级
    PERFORMANCE_BASED = "performance_based"  # 基于性能
    DEADLINE_AWARE = "deadline_aware"  # 截止时间感知
    ADAPTIVE = "adaptive"            # 自适应


@dataclass
class Resource:
    """资源定义"""
    id: str
    name: str
    resource_type: ResourceType
    total_capacity: float
    available_capacity: float
    unit: str
    cost_per_unit: float = 0.0
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceRequest:
    """资源请求"""
    id: str
    requester_id: str
    resource_type: ResourceType
    requested_amount: float
    priority: ResourcePriority
    deadline: Optional[datetime] = None
    duration: Optional[timedelta] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResourceAllocation:
    """资源分配"""
    id: str
    request_id: str
    resource_id: str
    allocated_amount: float
    start_time: datetime
    end_time: Optional[datetime] = None
    actual_usage: float = 0.0
    efficiency: float = 0.0
    cost: float = 0.0
    status: str = "allocated"  # allocated, active, completed, cancelled


@dataclass
class ResourceUtilization:
    """资源利用率"""
    resource_id: str
    time_period: Tuple[datetime, datetime]
    total_capacity: float
    used_capacity: float
    utilization_rate: float
    peak_usage: float
    average_usage: float
    efficiency_score: float


@dataclass
class OptimizationTask:
    """优化任务"""
    id: str
    name: str
    priority: ResourcePriority
    estimated_duration: timedelta
    resource_requirements: Dict[ResourceType, float]
    dependencies: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    progress: float = 0.0
    status: str = "pending"  # pending, running, completed, failed


@dataclass
class ResourceOptimizationResult:
    """资源优化结果"""
    optimization_id: str
    original_allocation: Dict[str, ResourceAllocation]
    optimized_allocation: Dict[str, ResourceAllocation]
    improvement_metrics: Dict[str, float]
    cost_savings: float
    efficiency_gain: float
    utilization_improvement: float
    recommendations: List[str]
    timestamp: datetime


class ResourceOptimizer:
    """资源优化器
    
    提供资源分配、调度和利用率优化功能。
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        """初始化资源优化器
        
        Args:
            config: 优化配置
        """
        self.config = config or OptimizationConfig()
        
        # 资源池
        self.resources: Dict[str, Resource] = {}
        
        # 资源请求队列
        self.pending_requests: List[ResourceRequest] = []
        
        # 当前分配
        self.current_allocations: Dict[str, ResourceAllocation] = {}
        
        # 利用率历史
        self.utilization_history: List[ResourceUtilization] = []
        
        # 优化任务队列
        self.optimization_tasks: Dict[str, OptimizationTask] = {}
        
        # 优化历史
        self.optimization_history: List[ResourceOptimizationResult] = []
        
        # 初始化默认资源
        self._initialize_default_resources()
    
    def _initialize_default_resources(self):
        """初始化默认资源"""
        
        # 计算资源
        compute_resource = Resource(
            id="compute_pool",
            name="计算资源池",
            resource_type=ResourceType.COMPUTE,
            total_capacity=100.0,
            available_capacity=100.0,
            unit="CPU核心",
            cost_per_unit=10.0,
            constraints={"max_per_request": 20.0}
        )
        
        # 内存资源
        memory_resource = Resource(
            id="memory_pool",
            name="内存资源池",
            resource_type=ResourceType.MEMORY,
            total_capacity=1000.0,
            available_capacity=1000.0,
            unit="GB",
            cost_per_unit=5.0,
            constraints={"max_per_request": 200.0}
        )
        
        # 时间资源
        time_resource = Resource(
            id="time_pool",
            name="时间资源池",
            resource_type=ResourceType.TIME,
            total_capacity=24.0,  # 24小时
            available_capacity=24.0,
            unit="小时",
            cost_per_unit=100.0,
            constraints={"max_per_request": 8.0}
        )
        
        # 人力资源
        human_resource = Resource(
            id="human_pool",
            name="人力资源池",
            resource_type=ResourceType.HUMAN,
            total_capacity=10.0,  # 10个人
            available_capacity=10.0,
            unit="人天",
            cost_per_unit=800.0,
            constraints={"max_per_request": 5.0}
        )
        
        self.resources = {
            "compute_pool": compute_resource,
            "memory_pool": memory_resource,
            "time_pool": time_resource,
            "human_pool": human_resource
        }
    
    def add_resource(self, resource: Resource):
        """添加资源
        
        Args:
            resource: 资源对象
        """
        self.resources[resource.id] = resource
    
    def request_resource(self, request: ResourceRequest) -> str:
        """请求资源
        
        Args:
            request: 资源请求
            
        Returns:
            str: 请求ID
        """
        self.pending_requests.append(request)
        return request.id
    
    def allocate_resources(
        self,
        strategy: AllocationStrategy = AllocationStrategy.PRIORITY_BASED
    ) -> List[ResourceAllocation]:
        """分配资源
        
        Args:
            strategy: 分配策略
            
        Returns:
            List[ResourceAllocation]: 分配结果列表
        """
        if strategy == AllocationStrategy.PRIORITY_BASED:
            return self._allocate_by_priority()
        elif strategy == AllocationStrategy.FAIR_SHARE:
            return self._allocate_fair_share()
        elif strategy == AllocationStrategy.PERFORMANCE_BASED:
            return self._allocate_by_performance()
        elif strategy == AllocationStrategy.DEADLINE_AWARE:
            return self._allocate_deadline_aware()
        elif strategy == AllocationStrategy.ADAPTIVE:
            return self._allocate_adaptive()
        else:
            raise ValueError(f"不支持的分配策略: {strategy}")
    
    def _allocate_by_priority(self) -> List[ResourceAllocation]:
        """基于优先级分配资源"""
        allocations = []
        
        # 按优先级排序请求
        priority_order = {
            ResourcePriority.CRITICAL: 0,
            ResourcePriority.HIGH: 1,
            ResourcePriority.MEDIUM: 2,
            ResourcePriority.LOW: 3
        }
        
        sorted_requests = sorted(
            self.pending_requests,
            key=lambda r: (priority_order[r.priority], r.created_at)
        )
        
        allocated_requests = []
        
        for request in sorted_requests:
            # 查找合适的资源
            suitable_resource = self._find_suitable_resource(request)
            
            if suitable_resource and suitable_resource.available_capacity >= request.requested_amount:
                # 创建分配
                allocation = ResourceAllocation(
                    id=f"alloc_{request.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    request_id=request.id,
                    resource_id=suitable_resource.id,
                    allocated_amount=request.requested_amount,
                    start_time=datetime.now(),
                    end_time=datetime.now() + request.duration if request.duration else None
                )
                
                # 更新资源可用容量
                suitable_resource.available_capacity -= request.requested_amount
                
                # 计算成本
                allocation.cost = request.requested_amount * suitable_resource.cost_per_unit
                
                allocations.append(allocation)
                self.current_allocations[allocation.id] = allocation
                allocated_requests.append(request)
        
        # 移除已分配的请求
        for request in allocated_requests:
            self.pending_requests.remove(request)
        
        return allocations
    
    def _allocate_fair_share(self) -> List[ResourceAllocation]:
        """公平分配资源"""
        allocations = []
        
        if not self.pending_requests:
            return allocations
        
        # 按资源类型分组请求
        requests_by_type = defaultdict(list)
        for request in self.pending_requests:
            requests_by_type[request.resource_type].append(request)
        
        allocated_requests = []
        
        for resource_type, requests in requests_by_type.items():
            # 找到该类型的资源
            available_resources = [
                r for r in self.resources.values()
                if r.resource_type == resource_type and r.available_capacity > 0
            ]
            
            if not available_resources:
                continue
            
            total_available = sum(r.available_capacity for r in available_resources)
            total_requested = sum(r.requested_amount for r in requests)
            
            if total_requested <= total_available:
                # 可以满足所有请求
                for request in requests:
                    suitable_resource = self._find_suitable_resource(request)
                    if suitable_resource:
                        allocation = self._create_allocation(request, suitable_resource, request.requested_amount)
                        allocations.append(allocation)
                        allocated_requests.append(request)
            else:
                # 需要按比例分配
                allocation_ratio = total_available / total_requested
                for request in requests:
                    allocated_amount = request.requested_amount * allocation_ratio
                    suitable_resource = self._find_suitable_resource(request)
                    if suitable_resource:
                        allocation = self._create_allocation(request, suitable_resource, allocated_amount)
                        allocations.append(allocation)
                        allocated_requests.append(request)
        
        # 移除已分配的请求
        for request in allocated_requests:
            self.pending_requests.remove(request)
        
        return allocations
    
    def _allocate_by_performance(self) -> List[ResourceAllocation]:
        """基于性能分配资源"""
        # 简化实现，实际会考虑历史性能数据
        return self._allocate_by_priority()
    
    def _allocate_deadline_aware(self) -> List[ResourceAllocation]:
        """截止时间感知分配"""
        allocations = []
        
        # 按截止时间排序
        requests_with_deadline = [r for r in self.pending_requests if r.deadline]
        requests_without_deadline = [r for r in self.pending_requests if not r.deadline]
        
        requests_with_deadline.sort(key=lambda r: r.deadline)
        
        # 优先处理有截止时间的请求
        all_requests = requests_with_deadline + requests_without_deadline
        allocated_requests = []
        
        for request in all_requests:
            suitable_resource = self._find_suitable_resource(request)
            
            if suitable_resource and suitable_resource.available_capacity >= request.requested_amount:
                allocation = self._create_allocation(request, suitable_resource, request.requested_amount)
                allocations.append(allocation)
                allocated_requests.append(request)
        
        # 移除已分配的请求
        for request in allocated_requests:
            self.pending_requests.remove(request)
        
        return allocations
    
    def _allocate_adaptive(self) -> List[ResourceAllocation]:
        """自适应分配"""
        # 根据当前系统状态选择最佳策略
        current_load = self._calculate_system_load()
        
        if current_load > 0.8:
            # 高负载时使用优先级策略
            return self._allocate_by_priority()
        elif current_load < 0.3:
            # 低负载时使用公平分配
            return self._allocate_fair_share()
        else:
            # 中等负载时使用截止时间感知
            return self._allocate_deadline_aware()
    
    def _find_suitable_resource(self, request: ResourceRequest) -> Optional[Resource]:
        """查找合适的资源
        
        Args:
            request: 资源请求
            
        Returns:
            Optional[Resource]: 合适的资源，如果没有则返回None
        """
        suitable_resources = []
        
        for resource in self.resources.values():
            if (resource.resource_type == request.resource_type and
                resource.available_capacity >= request.requested_amount):
                
                # 检查约束条件
                if self._check_resource_constraints(resource, request):
                    suitable_resources.append(resource)
        
        if not suitable_resources:
            return None
        
        # 选择可用容量最大的资源
        return max(suitable_resources, key=lambda r: r.available_capacity)
    
    def _check_resource_constraints(self, resource: Resource, request: ResourceRequest) -> bool:
        """检查资源约束
        
        Args:
            resource: 资源
            request: 请求
            
        Returns:
            bool: 是否满足约束
        """
        # 检查最大单次请求限制
        if "max_per_request" in resource.constraints:
            if request.requested_amount > resource.constraints["max_per_request"]:
                return False
        
        # 检查其他约束条件
        for constraint_key, constraint_value in request.constraints.items():
            if constraint_key in resource.constraints:
                if resource.constraints[constraint_key] != constraint_value:
                    return False
        
        return True
    
    def _create_allocation(
        self,
        request: ResourceRequest,
        resource: Resource,
        allocated_amount: float
    ) -> ResourceAllocation:
        """创建资源分配
        
        Args:
            request: 资源请求
            resource: 资源
            allocated_amount: 分配数量
            
        Returns:
            ResourceAllocation: 资源分配
        """
        allocation = ResourceAllocation(
            id=f"alloc_{request.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            request_id=request.id,
            resource_id=resource.id,
            allocated_amount=allocated_amount,
            start_time=datetime.now(),
            end_time=datetime.now() + request.duration if request.duration else None,
            cost=allocated_amount * resource.cost_per_unit
        )
        
        # 更新资源可用容量
        resource.available_capacity -= allocated_amount
        
        # 保存分配
        self.current_allocations[allocation.id] = allocation
        
        return allocation
    
    def _calculate_system_load(self) -> float:
        """计算系统负载
        
        Returns:
            float: 系统负载 (0-1)
        """
        if not self.resources:
            return 0.0
        
        total_capacity = sum(r.total_capacity for r in self.resources.values())
        total_used = sum(r.total_capacity - r.available_capacity for r in self.resources.values())
        
        if total_capacity == 0:
            return 0.0
        
        return total_used / total_capacity
    
    def optimize_resource_allocation(
        self,
        optimization_goals: List[str] = None
    ) -> ResourceOptimizationResult:
        """优化资源分配
        
        Args:
            optimization_goals: 优化目标
            
        Returns:
            ResourceOptimizationResult: 优化结果
        """
        optimization_goals = optimization_goals or ["efficiency", "cost", "utilization"]
        
        # 保存原始分配
        original_allocation = self.current_allocations.copy()
        
        # 分析当前分配的问题
        allocation_issues = self._analyze_allocation_issues()
        
        # 生成优化方案
        optimized_allocation = self._generate_optimized_allocation(allocation_issues, optimization_goals)
        
        # 计算改进指标
        improvement_metrics = self._calculate_improvement_metrics(
            original_allocation, optimized_allocation
        )
        
        # 计算成本节省
        cost_savings = self._calculate_cost_savings(original_allocation, optimized_allocation)
        
        # 计算效率提升
        efficiency_gain = self._calculate_efficiency_gain(original_allocation, optimized_allocation)
        
        # 计算利用率改进
        utilization_improvement = self._calculate_utilization_improvement(
            original_allocation, optimized_allocation
        )
        
        # 生成建议
        recommendations = self._generate_optimization_recommendations(
            allocation_issues, improvement_metrics
        )
        
        result = ResourceOptimizationResult(
            optimization_id=f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            original_allocation=original_allocation,
            optimized_allocation=optimized_allocation,
            improvement_metrics=improvement_metrics,
            cost_savings=cost_savings,
            efficiency_gain=efficiency_gain,
            utilization_improvement=utilization_improvement,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
        
        self.optimization_history.append(result)
        return result
    
    def _analyze_allocation_issues(self) -> List[Dict[str, Any]]:
        """分析分配问题
        
        Returns:
            List[Dict[str, Any]]: 问题列表
        """
        issues = []
        
        # 检查资源利用率不均
        utilization_rates = {}
        for resource in self.resources.values():
            utilization_rate = (resource.total_capacity - resource.available_capacity) / resource.total_capacity
            utilization_rates[resource.id] = utilization_rate
        
        if utilization_rates:
            avg_utilization = statistics.mean(utilization_rates.values())
            for resource_id, rate in utilization_rates.items():
                if abs(rate - avg_utilization) > 0.3:  # 差异超过30%
                    issues.append({
                        "type": "uneven_utilization",
                        "resource_id": resource_id,
                        "current_rate": rate,
                        "average_rate": avg_utilization,
                        "severity": "medium"
                    })
        
        # 检查过度分配
        for allocation in self.current_allocations.values():
            if allocation.actual_usage > 0 and allocation.efficiency < 0.7:
                issues.append({
                    "type": "low_efficiency",
                    "allocation_id": allocation.id,
                    "efficiency": allocation.efficiency,
                    "severity": "high" if allocation.efficiency < 0.5 else "medium"
                })
        
        # 检查资源碎片化
        for resource in self.resources.values():
            if 0 < resource.available_capacity < resource.total_capacity * 0.1:
                issues.append({
                    "type": "fragmentation",
                    "resource_id": resource.id,
                    "available_capacity": resource.available_capacity,
                    "total_capacity": resource.total_capacity,
                    "severity": "low"
                })
        
        return issues
    
    def _generate_optimized_allocation(
        self,
        issues: List[Dict[str, Any]],
        goals: List[str]
    ) -> Dict[str, ResourceAllocation]:
        """生成优化分配方案
        
        Args:
            issues: 问题列表
            goals: 优化目标
            
        Returns:
            Dict[str, ResourceAllocation]: 优化后的分配
        """
        optimized = self.current_allocations.copy()
        
        # 处理低效率分配
        for issue in issues:
            if issue["type"] == "low_efficiency":
                allocation_id = issue["allocation_id"]
                if allocation_id in optimized:
                    allocation = optimized[allocation_id]
                    # 减少分配量以提高效率
                    if allocation.actual_usage > 0:
                        new_amount = allocation.actual_usage * 1.1  # 增加10%缓冲
                        if new_amount < allocation.allocated_amount:
                            allocation.allocated_amount = new_amount
                            allocation.efficiency = allocation.actual_usage / new_amount
        
        # 处理资源不均衡
        if "utilization" in goals:
            optimized = self._rebalance_allocations(optimized)
        
        # 处理成本优化
        if "cost" in goals:
            optimized = self._optimize_allocation_costs(optimized)
        
        return optimized
    
    def _rebalance_allocations(
        self,
        allocations: Dict[str, ResourceAllocation]
    ) -> Dict[str, ResourceAllocation]:
        """重新平衡分配
        
        Args:
            allocations: 当前分配
            
        Returns:
            Dict[str, ResourceAllocation]: 平衡后的分配
        """
        # 简化实现：将高利用率资源的部分负载转移到低利用率资源
        resource_loads = defaultdict(float)
        
        for allocation in allocations.values():
            resource_loads[allocation.resource_id] += allocation.allocated_amount
        
        # 找出负载最高和最低的资源
        if len(resource_loads) > 1:
            max_resource = max(resource_loads, key=resource_loads.get)
            min_resource = min(resource_loads, key=resource_loads.get)
            
            # 如果差异较大，尝试转移部分负载
            if resource_loads[max_resource] - resource_loads[min_resource] > 10:
                # 找到可以转移的分配
                for allocation in allocations.values():
                    if (allocation.resource_id == max_resource and
                        allocation.allocated_amount <= resource_loads[max_resource] - resource_loads[min_resource]):
                        # 转移到低负载资源
                        allocation.resource_id = min_resource
                        break
        
        return allocations
    
    def _optimize_allocation_costs(
        self,
        allocations: Dict[str, ResourceAllocation]
    ) -> Dict[str, ResourceAllocation]:
        """优化分配成本
        
        Args:
            allocations: 当前分配
            
        Returns:
            Dict[str, ResourceAllocation]: 成本优化后的分配
        """
        # 简化实现：选择成本最低的资源
        for allocation in allocations.values():
            current_resource = self.resources[allocation.resource_id]
            
            # 查找同类型的更便宜资源
            cheaper_resources = [
                r for r in self.resources.values()
                if (r.resource_type == current_resource.resource_type and
                    r.cost_per_unit < current_resource.cost_per_unit and
                    r.available_capacity >= allocation.allocated_amount)
            ]
            
            if cheaper_resources:
                cheapest_resource = min(cheaper_resources, key=lambda r: r.cost_per_unit)
                allocation.resource_id = cheapest_resource.id
                allocation.cost = allocation.allocated_amount * cheapest_resource.cost_per_unit
        
        return allocations
    
    def _calculate_improvement_metrics(
        self,
        original: Dict[str, ResourceAllocation],
        optimized: Dict[str, ResourceAllocation]
    ) -> Dict[str, float]:
        """计算改进指标
        
        Args:
            original: 原始分配
            optimized: 优化分配
            
        Returns:
            Dict[str, float]: 改进指标
        """
        metrics = {}
        
        # 计算平均效率改进
        original_efficiencies = [a.efficiency for a in original.values() if a.efficiency > 0]
        optimized_efficiencies = [a.efficiency for a in optimized.values() if a.efficiency > 0]
        
        if original_efficiencies and optimized_efficiencies:
            metrics["efficiency_improvement"] = (
                statistics.mean(optimized_efficiencies) - statistics.mean(original_efficiencies)
            )
        else:
            metrics["efficiency_improvement"] = 0.0
        
        # 计算利用率改进
        original_utilization = self._calculate_overall_utilization(original)
        optimized_utilization = self._calculate_overall_utilization(optimized)
        metrics["utilization_improvement"] = optimized_utilization - original_utilization
        
        # 计算负载均衡改进
        original_balance = self._calculate_load_balance(original)
        optimized_balance = self._calculate_load_balance(optimized)
        metrics["balance_improvement"] = optimized_balance - original_balance
        
        return metrics
    
    def _calculate_overall_utilization(self, allocations: Dict[str, ResourceAllocation]) -> float:
        """计算整体利用率
        
        Args:
            allocations: 分配字典
            
        Returns:
            float: 整体利用率
        """
        total_capacity = sum(r.total_capacity for r in self.resources.values())
        total_allocated = sum(a.allocated_amount for a in allocations.values())
        
        if total_capacity == 0:
            return 0.0
        
        return total_allocated / total_capacity
    
    def _calculate_load_balance(self, allocations: Dict[str, ResourceAllocation]) -> float:
        """计算负载均衡度
        
        Args:
            allocations: 分配字典
            
        Returns:
            float: 负载均衡度 (越高越均衡)
        """
        resource_loads = defaultdict(float)
        
        for allocation in allocations.values():
            resource = self.resources[allocation.resource_id]
            utilization = allocation.allocated_amount / resource.total_capacity
            resource_loads[allocation.resource_id] = utilization
        
        if len(resource_loads) <= 1:
            return 1.0
        
        utilizations = list(resource_loads.values())
        mean_utilization = statistics.mean(utilizations)
        
        if mean_utilization == 0:
            return 1.0
        
        # 使用变异系数的倒数作为均衡度指标
        cv = statistics.stdev(utilizations) / mean_utilization
        return 1.0 / (1.0 + cv)
    
    def _calculate_cost_savings(
        self,
        original: Dict[str, ResourceAllocation],
        optimized: Dict[str, ResourceAllocation]
    ) -> float:
        """计算成本节省
        
        Args:
            original: 原始分配
            optimized: 优化分配
            
        Returns:
            float: 成本节省
        """
        original_cost = sum(a.cost for a in original.values())
        optimized_cost = sum(a.cost for a in optimized.values())
        
        return original_cost - optimized_cost
    
    def _calculate_efficiency_gain(
        self,
        original: Dict[str, ResourceAllocation],
        optimized: Dict[str, ResourceAllocation]
    ) -> float:
        """计算效率提升
        
        Args:
            original: 原始分配
            optimized: 优化分配
            
        Returns:
            float: 效率提升
        """
        original_efficiencies = [a.efficiency for a in original.values() if a.efficiency > 0]
        optimized_efficiencies = [a.efficiency for a in optimized.values() if a.efficiency > 0]
        
        if not original_efficiencies or not optimized_efficiencies:
            return 0.0
        
        original_avg = statistics.mean(original_efficiencies)
        optimized_avg = statistics.mean(optimized_efficiencies)
        
        return optimized_avg - original_avg
    
    def _calculate_utilization_improvement(
        self,
        original: Dict[str, ResourceAllocation],
        optimized: Dict[str, ResourceAllocation]
    ) -> float:
        """计算利用率改进
        
        Args:
            original: 原始分配
            optimized: 优化分配
            
        Returns:
            float: 利用率改进
        """
        original_utilization = self._calculate_overall_utilization(original)
        optimized_utilization = self._calculate_overall_utilization(optimized)
        
        return optimized_utilization - original_utilization
    
    def _generate_optimization_recommendations(
        self,
        issues: List[Dict[str, Any]],
        improvements: Dict[str, float]
    ) -> List[str]:
        """生成优化建议
        
        Args:
            issues: 问题列表
            improvements: 改进指标
            
        Returns:
            List[str]: 建议列表
        """
        recommendations = []
        
        # 基于问题生成建议
        for issue in issues:
            if issue["type"] == "uneven_utilization":
                recommendations.append(f"资源 {issue['resource_id']} 利用率不均，建议重新分配负载")
            
            elif issue["type"] == "low_efficiency":
                recommendations.append(f"分配 {issue['allocation_id']} 效率较低，建议调整分配量")
            
            elif issue["type"] == "fragmentation":
                recommendations.append(f"资源 {issue['resource_id']} 存在碎片化，建议整理资源")
        
        # 基于改进指标生成建议
        if improvements.get("efficiency_improvement", 0) > 0.1:
            recommendations.append("效率有显著提升空间，建议实施优化方案")
        
        if improvements.get("utilization_improvement", 0) > 0.1:
            recommendations.append("利用率可以进一步提升，建议优化资源分配")
        
        if improvements.get("balance_improvement", 0) > 0.1:
            recommendations.append("负载均衡可以改善，建议重新分配任务")
        
        # 通用建议
        if not recommendations:
            recommendations.append("当前资源分配较为合理，建议定期监控和调整")
        
        recommendations.append("建议建立资源使用监控机制")
        recommendations.append("定期评估资源需求和分配策略")
        
        return recommendations
    
    def release_resource(self, allocation_id: str):
        """释放资源
        
        Args:
            allocation_id: 分配ID
        """
        if allocation_id in self.current_allocations:
            allocation = self.current_allocations[allocation_id]
            resource = self.resources[allocation.resource_id]
            
            # 释放资源容量
            resource.available_capacity += allocation.allocated_amount
            
            # 更新分配状态
            allocation.status = "completed"
            allocation.end_time = datetime.now()
            
            # 从当前分配中移除
            del self.current_allocations[allocation_id]
    
    def update_resource_usage(self, allocation_id: str, actual_usage: float):
        """更新资源使用情况
        
        Args:
            allocation_id: 分配ID
            actual_usage: 实际使用量
        """
        if allocation_id in self.current_allocations:
            allocation = self.current_allocations[allocation_id]
            allocation.actual_usage = actual_usage
            
            # 计算效率
            if allocation.allocated_amount > 0:
                allocation.efficiency = actual_usage / allocation.allocated_amount
    
    def get_resource_utilization(
        self,
        resource_id: Optional[str] = None,
        time_period: Optional[Tuple[datetime, datetime]] = None
    ) -> List[ResourceUtilization]:
        """获取资源利用率
        
        Args:
            resource_id: 资源ID，如果为None则返回所有资源
            time_period: 时间段，如果为None则使用默认时间段
            
        Returns:
            List[ResourceUtilization]: 利用率列表
        """
        if time_period is None:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)  # 默认24小时
            time_period = (start_time, end_time)
        
        utilizations = []
        
        resources_to_check = [self.resources[resource_id]] if resource_id else self.resources.values()
        
        for resource in resources_to_check:
            # 计算时间段内的利用率
            relevant_allocations = [
                a for a in self.current_allocations.values()
                if (a.resource_id == resource.id and
                    a.start_time <= time_period[1] and
                    (a.end_time is None or a.end_time >= time_period[0]))
            ]
            
            if relevant_allocations:
                used_capacity = sum(a.allocated_amount for a in relevant_allocations)
                utilization_rate = used_capacity / resource.total_capacity
                
                # 计算峰值和平均使用量
                usage_values = [a.actual_usage for a in relevant_allocations if a.actual_usage > 0]
                peak_usage = max(usage_values) if usage_values else 0
                average_usage = statistics.mean(usage_values) if usage_values else 0
                
                # 计算效率得分
                efficiency_scores = [a.efficiency for a in relevant_allocations if a.efficiency > 0]
                efficiency_score = statistics.mean(efficiency_scores) if efficiency_scores else 0
                
                utilization = ResourceUtilization(
                    resource_id=resource.id,
                    time_period=time_period,
                    total_capacity=resource.total_capacity,
                    used_capacity=used_capacity,
                    utilization_rate=utilization_rate,
                    peak_usage=peak_usage,
                    average_usage=average_usage,
                    efficiency_score=efficiency_score
                )
                
                utilizations.append(utilization)
        
        return utilizations
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """获取优化摘要
        
        Returns:
            Dict[str, Any]: 优化摘要
        """
        if not self.optimization_history:
            return {
                "total_optimizations": 0,
                "average_cost_savings": 0.0,
                "average_efficiency_gain": 0.0,
                "average_utilization_improvement": 0.0,
                "recommendations": ["暂无优化历史，建议开始资源优化"]
            }
        
        recent_optimizations = self.optimization_history[-10:]  # 最近10次优化
        
        return {
            "total_optimizations": len(self.optimization_history),
            "average_cost_savings": statistics.mean([o.cost_savings for o in recent_optimizations]),
            "average_efficiency_gain": statistics.mean([o.efficiency_gain for o in recent_optimizations]),
            "average_utilization_improvement": statistics.mean([o.utilization_improvement for o in recent_optimizations]),
            "recent_trends": self._analyze_optimization_trends(recent_optimizations),
            "top_recommendations": self._get_top_recommendations(recent_optimizations)
        }
    
    def _analyze_optimization_trends(self, optimizations: List[ResourceOptimizationResult]) -> Dict[str, str]:
        """分析优化趋势
        
        Args:
            optimizations: 优化结果列表
            
        Returns:
            Dict[str, str]: 趋势分析
        """
        if len(optimizations) < 2:
            return {"trend": "数据不足"}
        
        # 分析成本节省趋势
        cost_savings = [o.cost_savings for o in optimizations]
        cost_trend = "上升" if cost_savings[-1] > cost_savings[0] else "下降"
        
        # 分析效率趋势
        efficiency_gains = [o.efficiency_gain for o in optimizations]
        efficiency_trend = "上升" if efficiency_gains[-1] > efficiency_gains[0] else "下降"
        
        return {
            "cost_savings_trend": cost_trend,
            "efficiency_trend": efficiency_trend,
            "overall_trend": "改善" if cost_trend == "上升" and efficiency_trend == "上升" else "需要关注"
        }
    
    def _get_top_recommendations(self, optimizations: List[ResourceOptimizationResult]) -> List[str]:
        """获取主要建议
        
        Args:
            optimizations: 优化结果列表
            
        Returns:
            List[str]: 主要建议
        """
        all_recommendations = []
        for optimization in optimizations:
            all_recommendations.extend(optimization.recommendations)
        
        # 统计建议频率
        recommendation_counts = defaultdict(int)
        for rec in all_recommendations:
            recommendation_counts[rec] += 1
        
        # 返回最频繁的建议
        top_recommendations = sorted(
            recommendation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return [rec for rec, count in top_recommendations]