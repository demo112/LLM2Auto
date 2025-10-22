# -*- encoding=utf8 -*-
"""
统一配置管理器

整合原有的分散配置功能，提供统一的配置管理接口
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict

from .base_interfaces import IConfigManager


@dataclass
class MappingConfig:
    """映射配置"""
    similarity_weights: Dict[str, float]
    confidence_threshold: float
    max_mappings_per_element: int
    enable_navigation_mapping: bool
    navigation_keywords: list


@dataclass
class QualityConfig:
    """质量配置"""
    quality_weights: Dict[str, float]
    quality_thresholds: Dict[str, float]
    min_confidence_threshold: float
    enable_auto_validation: bool


@dataclass
class ReportConfig:
    """报告配置"""
    output_formats: list
    include_screenshots: bool
    max_details_count: int
    enable_dashboard: bool
    template_style: str


@dataclass
class AnalysisConfig:
    """分析配置"""
    analysis_types: list
    enable_pattern_detection: bool
    statistical_methods: list
    cache_results: bool


@dataclass
class SystemConfig:
    """系统配置"""
    output_directory: str
    log_level: str
    max_workers: int
    timeout_seconds: int
    enable_debug: bool


@dataclass
class UnifiedConfig:
    """统一配置"""
    mapping: MappingConfig
    quality: QualityConfig
    report: ReportConfig
    analysis: AnalysisConfig
    system: SystemConfig


class UnifiedConfigManager(IConfigManager):
    """统一配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config.yaml"
        self.config_path = Path(self.config_file)
        self._config: Optional[UnifiedConfig] = None
        self._load_config()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        self.config_file = config_path
        self.config_path = Path(config_path)
        self._load_config()
        return self.get_all_config()
    
    def save_config(self, config: Dict[str, Any], config_path: str) -> bool:
        """保存配置文件"""
        try:
            # 更新内部配置
            self._update_config_from_dict(config)
            
            # 保存到文件
            config_path_obj = Path(config_path)
            config_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            if config_path.endswith('.json'):
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            else:  # 默认使用YAML
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            return True
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            return False
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        if not self._config:
            return default
        
        # 支持点号分隔的嵌套键
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                else:
                    return default
            return value
        except (AttributeError, KeyError):
            return default
    
    def set_config(self, key: str, value: Any) -> bool:
        """设置配置项"""
        if not self._config:
            self._config = self._create_default_config()
        
        # 支持点号分隔的嵌套键
        keys = key.split('.')
        config_obj = self._config
        
        try:
            # 导航到最后一级的父对象
            for k in keys[:-1]:
                if hasattr(config_obj, k):
                    config_obj = getattr(config_obj, k)
                else:
                    return False
            
            # 设置最终值
            if hasattr(config_obj, keys[-1]):
                setattr(config_obj, keys[-1], value)
                return True
            else:
                return False
        except (AttributeError, KeyError):
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        if not self._config:
            return {}
        
        return asdict(self._config)
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置有效性"""
        try:
            # 尝试创建配置对象来验证结构
            self._create_config_from_dict(config)
            return True
        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            return False
    
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        try:
            self._config = self._create_default_config()
            return True
        except Exception as e:
            self.logger.error(f"重置配置失败: {e}")
            return False
    
    def get_mapping_config(self) -> MappingConfig:
        """获取映射配置"""
        return self._config.mapping if self._config else self._create_default_mapping_config()
    
    def get_quality_config(self) -> QualityConfig:
        """获取质量配置"""
        return self._config.quality if self._config else self._create_default_quality_config()
    
    def get_report_config(self) -> ReportConfig:
        """获取报告配置"""
        return self._config.report if self._config else self._create_default_report_config()
    
    def get_analysis_config(self) -> AnalysisConfig:
        """获取分析配置"""
        return self._config.analysis if self._config else self._create_default_analysis_config()
    
    def get_system_config(self) -> SystemConfig:
        """获取系统配置"""
        return self._config.system if self._config else self._create_default_system_config()
    
    def update_mapping_config(self, **kwargs) -> bool:
        """更新映射配置"""
        if not self._config:
            self._config = self._create_default_config()
        
        try:
            for key, value in kwargs.items():
                if hasattr(self._config.mapping, key):
                    setattr(self._config.mapping, key, value)
            return True
        except Exception as e:
            self.logger.error(f"更新映射配置失败: {e}")
            return False
    
    def update_quality_config(self, **kwargs) -> bool:
        """更新质量配置"""
        if not self._config:
            self._config = self._create_default_config()
        
        try:
            for key, value in kwargs.items():
                if hasattr(self._config.quality, key):
                    setattr(self._config.quality, key, value)
            return True
        except Exception as e:
            self.logger.error(f"更新质量配置失败: {e}")
            return False
    
    def _load_config(self):
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.suffix.lower() == '.json':
                        config_dict = json.load(f)
                    else:  # 默认YAML
                        config_dict = yaml.safe_load(f)
                
                self._config = self._create_config_from_dict(config_dict)
            except Exception as e:
                self.logger.error(f"加载配置文件失败: {e}")
                self._config = self._create_default_config()
        else:
            # 创建默认配置并保存
            self._config = self._create_default_config()
            self._save_default_config()
    
    def _save_default_config(self):
        """保存默认配置"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            config_dict = asdict(self._config)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            self.logger.error(f"保存默认配置失败: {e}")
    
    def _create_default_config(self) -> UnifiedConfig:
        """创建默认配置"""
        return UnifiedConfig(
            mapping=self._create_default_mapping_config(),
            quality=self._create_default_quality_config(),
            report=self._create_default_report_config(),
            analysis=self._create_default_analysis_config(),
            system=self._create_default_system_config()
        )
    
    def _create_default_mapping_config(self) -> MappingConfig:
        """创建默认映射配置"""
        return MappingConfig(
            similarity_weights={
                'position': 0.4,
                'semantic': 0.3,
                'sequence': 0.2,
                'temporal': 0.1
            },
            confidence_threshold=0.3,
            max_mappings_per_element=5,
            enable_navigation_mapping=True,
            navigation_keywords=[
                '首页', 'home', '发现', 'discover', '我的', 'mine', 'profile',
                '设置', 'setting', '消息', 'message', '通知', 'notification',
                '搜索', 'search', '返回', 'back', '确定', 'confirm', '取消', 'cancel'
            ]
        )
    
    def _create_default_quality_config(self) -> QualityConfig:
        """创建默认质量配置"""
        return QualityConfig(
            quality_weights={
                'coverage': 0.25,
                'accuracy': 0.25,
                'consistency': 0.20,
                'completeness': 0.15,
                'reliability': 0.15
            },
            quality_thresholds={
                'excellent': 0.9,
                'good': 0.7,
                'fair': 0.5,
                'poor': 0.3
            },
            min_confidence_threshold=0.3,
            enable_auto_validation=True
        )
    
    def _create_default_report_config(self) -> ReportConfig:
        """创建默认报告配置"""
        return ReportConfig(
            output_formats=['html', 'json'],
            include_screenshots=True,
            max_details_count=50,
            enable_dashboard=True,
            template_style='modern'
        )
    
    def _create_default_analysis_config(self) -> AnalysisConfig:
        """创建默认分析配置"""
        return AnalysisConfig(
            analysis_types=['quality', 'statistics', 'patterns'],
            enable_pattern_detection=True,
            statistical_methods=['basic', 'correlation', 'distribution'],
            cache_results=True
        )
    
    def _create_default_system_config(self) -> SystemConfig:
        """创建默认系统配置"""
        return SystemConfig(
            output_directory='output',
            log_level='INFO',
            max_workers=4,
            timeout_seconds=300,
            enable_debug=False
        )
    
    def _create_config_from_dict(self, config_dict: Dict[str, Any]) -> UnifiedConfig:
        """从字典创建配置对象"""
        # 创建默认配置作为基础
        default_config = self._create_default_config()
        
        # 更新映射配置
        if 'mapping' in config_dict:
            mapping_dict = config_dict['mapping']
            mapping_config = MappingConfig(
                similarity_weights=mapping_dict.get('similarity_weights', default_config.mapping.similarity_weights),
                confidence_threshold=mapping_dict.get('confidence_threshold', default_config.mapping.confidence_threshold),
                max_mappings_per_element=mapping_dict.get('max_mappings_per_element', default_config.mapping.max_mappings_per_element),
                enable_navigation_mapping=mapping_dict.get('enable_navigation_mapping', default_config.mapping.enable_navigation_mapping),
                navigation_keywords=mapping_dict.get('navigation_keywords', default_config.mapping.navigation_keywords)
            )
        else:
            mapping_config = default_config.mapping
        
        # 更新质量配置
        if 'quality' in config_dict:
            quality_dict = config_dict['quality']
            quality_config = QualityConfig(
                quality_weights=quality_dict.get('quality_weights', default_config.quality.quality_weights),
                quality_thresholds=quality_dict.get('quality_thresholds', default_config.quality.quality_thresholds),
                min_confidence_threshold=quality_dict.get('min_confidence_threshold', default_config.quality.min_confidence_threshold),
                enable_auto_validation=quality_dict.get('enable_auto_validation', default_config.quality.enable_auto_validation)
            )
        else:
            quality_config = default_config.quality
        
        # 更新报告配置
        if 'report' in config_dict:
            report_dict = config_dict['report']
            report_config = ReportConfig(
                output_formats=report_dict.get('output_formats', default_config.report.output_formats),
                include_screenshots=report_dict.get('include_screenshots', default_config.report.include_screenshots),
                max_details_count=report_dict.get('max_details_count', default_config.report.max_details_count),
                enable_dashboard=report_dict.get('enable_dashboard', default_config.report.enable_dashboard),
                template_style=report_dict.get('template_style', default_config.report.template_style)
            )
        else:
            report_config = default_config.report
        
        # 更新分析配置
        if 'analysis' in config_dict:
            analysis_dict = config_dict['analysis']
            analysis_config = AnalysisConfig(
                analysis_types=analysis_dict.get('analysis_types', default_config.analysis.analysis_types),
                enable_pattern_detection=analysis_dict.get('enable_pattern_detection', default_config.analysis.enable_pattern_detection),
                statistical_methods=analysis_dict.get('statistical_methods', default_config.analysis.statistical_methods),
                cache_results=analysis_dict.get('cache_results', default_config.analysis.cache_results)
            )
        else:
            analysis_config = default_config.analysis
        
        # 更新系统配置
        if 'system' in config_dict:
            system_dict = config_dict['system']
            system_config = SystemConfig(
                output_directory=system_dict.get('output_directory', default_config.system.output_directory),
                log_level=system_dict.get('log_level', default_config.system.log_level),
                max_workers=system_dict.get('max_workers', default_config.system.max_workers),
                timeout_seconds=system_dict.get('timeout_seconds', default_config.system.timeout_seconds),
                enable_debug=system_dict.get('enable_debug', default_config.system.enable_debug)
            )
        else:
            system_config = default_config.system
        
        return UnifiedConfig(
            mapping=mapping_config,
            quality=quality_config,
            report=report_config,
            analysis=analysis_config,
            system=system_config
        )
    
    def _update_config_from_dict(self, config_dict: Dict[str, Any]):
        """从字典更新配置"""
        if not self._config:
            self._config = self._create_default_config()
        
        # 递归更新配置
        self._update_nested_config(self._config, config_dict)
    
    def _update_nested_config(self, config_obj: Any, config_dict: Dict[str, Any]):
        """递归更新嵌套配置"""
        for key, value in config_dict.items():
            if hasattr(config_obj, key):
                current_value = getattr(config_obj, key)
                if isinstance(current_value, dict) and isinstance(value, dict):
                    # 更新字典类型的配置
                    current_value.update(value)
                elif hasattr(current_value, '__dict__') and isinstance(value, dict):
                    # 递归更新对象类型的配置
                    self._update_nested_config(current_value, value)
                else:
                    # 直接设置值
                    setattr(config_obj, key, value)


# 全局配置管理器实例
_global_config_manager: Optional[UnifiedConfigManager] = None


def get_config_manager(config_file: Optional[str] = None) -> UnifiedConfigManager:
    """获取全局配置管理器实例"""
    global _global_config_manager
    
    if _global_config_manager is None or config_file is not None:
        _global_config_manager = UnifiedConfigManager(config_file)
    
    return _global_config_manager


def get_config(key: str, default: Any = None) -> Any:
    """获取配置项的便捷函数"""
    return get_config_manager().get_config(key, default)


def set_config(key: str, value: Any) -> bool:
    """设置配置项的便捷函数"""
    return get_config_manager().set_config(key, value)