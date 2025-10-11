# -*- encoding=utf8 -*-
"""
配置管理器 - 负责管理框架配置和测试项目配置
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict


@dataclass
class DeviceConfig:
    """设备配置"""
    uri: str = "Android:///"
    platform: str = "Android"
    timeout: int = 60
    retry_count: int = 3
    screenshot_quality: int = 80
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceConfig':
        """从字典创建配置"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class ExecutionConfig:
    """执行配置"""
    parallel: bool = False
    max_workers: int = 1
    timeout: int = 300
    retry_on_failure: bool = True
    retry_count: int = 1
    log_level: str = "INFO"
    screenshot_on_error: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionConfig':
        """从字典创建配置"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class ReportConfig:
    """报告配置"""
    format: str = "html"  # html, json, xml
    output_dir: str = "reports"
    include_screenshots: bool = True
    include_logs: bool = True
    template: str = "default"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportConfig':
        """从字典创建配置"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class FrameworkConfig:
    """框架配置"""
    project_name: str = "Airtest自动化测试"
    version: str = "1.0.0"
    test_dirs: List[str] = field(default_factory=lambda: ["tests/"])
    log_dir: str = "logs"
    temp_dir: str = "temp"
    device: DeviceConfig = field(default_factory=DeviceConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrameworkConfig':
        """从字典创建配置"""
        # 处理嵌套配置
        if 'device' in data and isinstance(data['device'], dict):
            data['device'] = DeviceConfig.from_dict(data['device'])
        if 'execution' in data and isinstance(data['execution'], dict):
            data['execution'] = ExecutionConfig.from_dict(data['execution'])
        if 'report' in data and isinstance(data['report'], dict):
            data['report'] = ReportConfig.from_dict(data['report'])
        
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        
    def _find_config_file(self) -> Optional[str]:
        """查找配置文件"""
        # 查找顺序：当前目录 -> 用户目录 -> 默认配置
        search_paths = [
            "airtest_config.yaml",
            "airtest_config.yml", 
            "config/airtest_config.yaml",
            os.path.expanduser("~/.airtest/config.yaml"),
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                self.logger.info(f"找到配置文件: {path}")
                return path
        
        self.logger.info("未找到配置文件，使用默认配置")
        return None
    
    def _load_config(self) -> FrameworkConfig:
        """加载配置"""
        if not self.config_path or not os.path.exists(self.config_path):
            self.logger.info("使用默认配置")
            return FrameworkConfig()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.endswith('.json'):
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)
            
            config = FrameworkConfig.from_dict(data or {})
            self.logger.info(f"配置加载成功: {self.config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            self.logger.info("使用默认配置")
            return FrameworkConfig()
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """
        保存配置
        
        Args:
            config_path: 保存路径
            
        Returns:
            bool: 是否保存成功
        """
        save_path = config_path or self.config_path or "airtest_config.yaml"
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
            
            # 转换为字典
            config_dict = asdict(self.config)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            self.logger.info(f"配置保存成功: {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"配置保存失败: {e}")
            return False
    
    def get_config(self) -> FrameworkConfig:
        """获取配置"""
        return self.config
    
    def update_config(self, **kwargs) -> bool:
        """
        更新配置
        
        Args:
            **kwargs: 配置项
            
        Returns:
            bool: 是否更新成功
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    self.logger.info(f"配置更新: {key} = {value}")
                else:
                    self.logger.warning(f"未知配置项: {key}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"配置更新失败: {e}")
            return False
    
    def get_device_config(self) -> DeviceConfig:
        """获取设备配置"""
        return self.config.device
    
    def get_execution_config(self) -> ExecutionConfig:
        """获取执行配置"""
        return self.config.execution
    
    def get_report_config(self) -> ReportConfig:
        """获取报告配置"""
        return self.config.report
    
    def create_default_config(self, config_path: str = "airtest_config.yaml") -> bool:
        """
        创建默认配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            bool: 是否创建成功
        """
        try:
            default_config = FrameworkConfig()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(config_path) or ".", exist_ok=True)
            
            # 转换为字典
            config_dict = asdict(default_config)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            self.logger.info(f"默认配置文件创建成功: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"默认配置文件创建失败: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """
        验证配置
        
        Returns:
            List[str]: 验证错误列表
        """
        errors = []
        
        # 验证设备配置
        device_config = self.config.device
        if not device_config.uri:
            errors.append("设备URI不能为空")
        
        if device_config.timeout <= 0:
            errors.append("设备超时时间必须大于0")
        
        # 验证执行配置
        execution_config = self.config.execution
        if execution_config.max_workers <= 0:
            errors.append("最大工作线程数必须大于0")
        
        if execution_config.timeout <= 0:
            errors.append("执行超时时间必须大于0")
        
        # 验证报告配置
        report_config = self.config.report
        if report_config.format not in ['html', 'json', 'xml']:
            errors.append("报告格式必须是 html、json 或 xml")
        
        # 验证目录
        for test_dir in self.config.test_dirs:
            if not os.path.exists(test_dir):
                errors.append(f"测试目录不存在: {test_dir}")
        
        return errors
    
    def setup_logging(self):
        """设置日志"""
        log_level = getattr(logging, self.config.execution.log_level.upper(), logging.INFO)
        
        # 创建日志目录
        os.makedirs(self.config.log_dir, exist_ok=True)
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 文件处理器
        file_handler = logging.FileHandler(
            os.path.join(self.config.log_dir, 'framework.log'),
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        self.logger.info("日志系统初始化完成")
    
    def get_test_metadata_schema(self) -> Dict[str, Any]:
        """获取测试元数据模式"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "测试名称"},
                "description": {"type": "string", "description": "测试描述"},
                "category": {"type": "string", "description": "测试分类"},
                "priority": {"type": "string", "enum": ["high", "medium", "low"], "description": "优先级"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "标签"},
                "timeout": {"type": "integer", "minimum": 1, "description": "超时时间(秒)"},
                "retry_count": {"type": "integer", "minimum": 0, "description": "重试次数"},
                "dependencies": {"type": "array", "items": {"type": "string"}, "description": "依赖测试"},
                "device_requirements": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string", "description": "平台要求"},
                        "min_version": {"type": "string", "description": "最小版本"},
                        "resolution": {"type": "string", "description": "分辨率要求"}
                    }
                },
                "environment": {
                    "type": "object",
                    "description": "环境变量"
                }
            },
            "required": ["name"]
        }


class ProjectConfigManager:
    """项目配置管理器"""
    
    def __init__(self, project_root: str):
        """
        初始化项目配置管理器
        
        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
    
    def load_project_config(self, air_path: str) -> Dict[str, Any]:
        """
        加载 .air 项目配置
        
        Args:
            air_path: .air 项目路径
            
        Returns:
            Dict[str, Any]: 项目配置
        """
        air_dir = Path(air_path)
        config = {}
        
        # 查找配置文件
        config_files = [
            air_dir / "metadata.yaml",
            air_dir / "metadata.yml",
            air_dir / "config.yaml",
            air_dir / "config.yml",
            air_dir / "test_config.yaml"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        file_config = yaml.safe_load(f) or {}
                    config.update(file_config)
                    self.logger.debug(f"加载项目配置: {config_file}")
                except Exception as e:
                    self.logger.warning(f"配置文件加载失败: {config_file} - {e}")
        
        return config
    
    def save_project_config(self, air_path: str, config: Dict[str, Any]) -> bool:
        """
        保存 .air 项目配置
        
        Args:
            air_path: .air 项目路径
            config: 配置数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            air_dir = Path(air_path)
            config_file = air_dir / "metadata.yaml"
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            self.logger.info(f"项目配置保存成功: {config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"项目配置保存失败: {e}")
            return False