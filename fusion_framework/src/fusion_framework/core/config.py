# -*- encoding=utf8 -*-
"""
融合框架配置模块

定义融合测试框架的各种配置选项和默认值
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum


class ExecutionStrategy(Enum):
    """执行策略枚举"""
    AIRTEST_FIRST = "airtest_first"  # Airtest优先
    POCO_FIRST = "poco_first"        # Poco优先
    PARALLEL = "parallel"            # 并行执行
    AUTO = "auto"                    # 自动选择


class FallbackMode(Enum):
    """回退模式枚举"""
    IMMEDIATE = "immediate"          # 立即回退
    RETRY_THEN_FALLBACK = "retry_then_fallback"  # 重试后回退
    NO_FALLBACK = "no_fallback"      # 不回退


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 2             # 最大重试次数
    retry_delay: float = 1.0         # 重试间隔(秒)
    exponential_backoff: bool = True # 指数退避


@dataclass
class TimeoutConfig:
    """超时配置"""
    step_timeout: float = 30.0       # 单步超时(秒)
    case_timeout: float = 300.0      # 用例超时(秒)
    element_wait_timeout: float = 10.0  # 元素等待超时(秒)


@dataclass
class AlignmentConfig:
    """步骤对齐配置"""
    confidence_threshold: float = 0.7  # 对齐置信度阈值
    max_step_distance: int = 3         # 最大步骤距离
    enable_semantic_matching: bool = True  # 启用语义匹配


@dataclass
class ReportConfig:
    """报告配置"""
    output_dir: str = "reports"       # 输出目录
    generate_html: bool = True        # 生成HTML报告
    generate_json: bool = True        # 生成JSON报告
    include_screenshots: bool = True  # 包含截图
    include_logs: bool = True         # 包含日志


@dataclass
class DeviceConfig:
    """设备配置"""
    android_serial: Optional[str] = None  # Android设备序列号
    ios_bundle_id: Optional[str] = None   # iOS应用包名
    connect_timeout: float = 30.0         # 连接超时
    auto_connect: bool = True             # 自动连接


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"               # 日志级别
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_output: bool = True          # 文件输出
    console_output: bool = True       # 控制台输出
    log_dir: str = "logs"            # 日志目录


@dataclass
class FusionConfig:
    """融合框架主配置"""
    # 基本配置
    test_root_dir: str = "tests"      # 测试根目录
    execution_strategy: ExecutionStrategy = ExecutionStrategy.AUTO
    fallback_mode: FallbackMode = FallbackMode.RETRY_THEN_FALLBACK
    
    # 子配置
    retry: RetryConfig = None
    timeout: TimeoutConfig = None
    alignment: AlignmentConfig = None
    report: ReportConfig = None
    device: DeviceConfig = None
    logging: LoggingConfig = None
    
    # 高级配置
    parallel_execution: bool = False   # 并行执行用例
    max_workers: int = 4              # 最大工作线程数
    enable_performance_monitoring: bool = True  # 启用性能监控
    
    # 调试配置
    debug_mode: bool = False          # 调试模式
    save_intermediate_results: bool = False  # 保存中间结果
    verbose_logging: bool = False     # 详细日志
    
    def __post_init__(self):
        """初始化后处理"""
        if self.retry is None:
            self.retry = RetryConfig()
        if self.timeout is None:
            self.timeout = TimeoutConfig()
        if self.alignment is None:
            self.alignment = AlignmentConfig()
        if self.report is None:
            self.report = ReportConfig()
        if self.device is None:
            self.device = DeviceConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
    
    @classmethod
    def from_file(cls, config_path: str) -> 'FusionConfig':
        """从配置文件加载配置"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() == '.json':
                config_data = json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_file.suffix}")
        
        return cls.from_dict(config_data)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'FusionConfig':
        """从字典创建配置"""
        # 创建配置字典的副本，避免修改原始数据
        config_copy = config_dict.copy()
        
        # 过滤掉不属于FusionConfig的配置项
        if 'qwen_api' in config_copy:
            del config_copy['qwen_api']  # qwen_api由QwenConfig单独处理
        
        # 处理枚举类型
        if 'execution_strategy' in config_copy:
            config_copy['execution_strategy'] = ExecutionStrategy(config_copy['execution_strategy'])
        if 'fallback_mode' in config_copy:
            config_copy['fallback_mode'] = FallbackMode(config_copy['fallback_mode'])
        
        # 处理子配置
        if 'retry' in config_copy:
            config_copy['retry'] = RetryConfig(**config_copy['retry'])
        if 'timeout' in config_copy:
            config_copy['timeout'] = TimeoutConfig(**config_copy['timeout'])
        if 'alignment' in config_copy:
            config_copy['alignment'] = AlignmentConfig(**config_copy['alignment'])
        if 'report' in config_copy:
            config_copy['report'] = ReportConfig(**config_copy['report'])
        if 'device' in config_copy:
            config_copy['device'] = DeviceConfig(**config_copy['device'])
        if 'logging' in config_copy:
            config_copy['logging'] = LoggingConfig(**config_copy['logging'])
        
        return cls(**config_copy)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        
        # 处理枚举类型
        result['execution_strategy'] = self.execution_strategy.value
        result['fallback_mode'] = self.fallback_mode.value
        
        return result
    
    def save_to_file(self, config_path: str):
        """保存配置到文件"""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            if config_file.suffix.lower() == '.json':
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_file.suffix}")
    
    def validate(self) -> List[str]:
        """验证配置有效性"""
        errors = []
        
        # 验证基本配置
        if not self.test_root_dir:
            errors.append("test_root_dir 不能为空")
        
        if not Path(self.test_root_dir).exists():
            errors.append(f"测试根目录不存在: {self.test_root_dir}")
        
        # 验证超时配置
        if self.timeout.step_timeout <= 0:
            errors.append("step_timeout 必须大于0")
        
        if self.timeout.case_timeout <= 0:
            errors.append("case_timeout 必须大于0")
        
        if self.timeout.element_wait_timeout <= 0:
            errors.append("element_wait_timeout 必须大于0")
        
        # 验证重试配置
        if self.retry.max_retries < 0:
            errors.append("max_retries 不能小于0")
        
        if self.retry.retry_delay < 0:
            errors.append("retry_delay 不能小于0")
        
        # 验证对齐配置
        if not 0 <= self.alignment.confidence_threshold <= 1:
            errors.append("confidence_threshold 必须在0-1之间")
        
        if self.alignment.max_step_distance < 0:
            errors.append("max_step_distance 不能小于0")
        
        # 验证并行配置
        if self.max_workers <= 0:
            errors.append("max_workers 必须大于0")
        
        return errors
    
    def get_effective_strategy(self, case_info) -> ExecutionStrategy:
        """获取有效的执行策略"""
        if self.execution_strategy == ExecutionStrategy.AUTO:
            # 自动选择策略的逻辑
            if hasattr(case_info, 'airtest_path') and hasattr(case_info, 'poco_path'):
                # 如果两种实现都存在，优先选择Poco
                return ExecutionStrategy.POCO_FIRST
            elif hasattr(case_info, 'poco_path'):
                return ExecutionStrategy.POCO_FIRST
            else:
                return ExecutionStrategy.AIRTEST_FIRST
        
        return self.execution_strategy


# 默认配置实例
DEFAULT_CONFIG = FusionConfig()


def create_default_config_file(config_path: str = "fusion_config.json"):
    """创建默认配置文件"""
    config = FusionConfig()
    config.save_to_file(config_path)
    return config_path


def load_config(config_path: Optional[str] = None) -> FusionConfig:
    """加载配置"""
    if config_path and Path(config_path).exists():
        return FusionConfig.from_file(config_path)
    
    # 尝试加载默认配置文件
    default_paths = [
        "fusion_config.json",
        "config/fusion_config.json",
        "configs/fusion_config.json"
    ]
    
    for path in default_paths:
        if Path(path).exists():
            return FusionConfig.from_file(path)
    
    # 返回默认配置
    return FusionConfig()


# 配置验证函数
def validate_config(config: FusionConfig) -> bool:
    """验证配置并打印错误信息"""
    errors = config.validate()
    
    if errors:
        print("配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("配置验证通过")
    return True