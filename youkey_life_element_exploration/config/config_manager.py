# -*- encoding=utf8 -*-
"""
配置管理器

负责配置文件的加载、保存和管理
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

from .quality_config import QualityConfig


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，默认为当前目录下的config文件夹
        """
        if config_dir is None:
            config_dir = Path.cwd() / "config"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self._config_cache: Dict[str, Any] = {}
    
    def load_quality_config(self, config_file: str = "quality_config.yaml") -> QualityConfig:
        """
        加载质量监控配置
        
        Args:
            config_file: 配置文件名
            
        Returns:
            QualityConfig: 质量监控配置对象
        """
        config_path = self.config_dir / config_file
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                        data = yaml.safe_load(f)
                    else:
                        data = json.load(f)
                
                config = QualityConfig.from_dict(data)
                
                if not config.validate():
                    self.logger.warning(f"配置文件 {config_file} 验证失败，使用默认配置")
                    config = QualityConfig()
                
                self._config_cache[config_file] = config
                self.logger.info(f"成功加载配置文件: {config_path}")
                return config
                
            except Exception as e:
                self.logger.error(f"加载配置文件失败: {config_path}, 错误: {e}")
                self.logger.info("使用默认配置")
                return QualityConfig()
        else:
            self.logger.info(f"配置文件不存在: {config_path}，创建默认配置")
            config = QualityConfig()
            self.save_quality_config(config, config_file)
            return config
    
    def save_quality_config(self, config: QualityConfig, config_file: str = "quality_config.yaml") -> bool:
        """
        保存质量监控配置
        
        Args:
            config: 质量监控配置对象
            config_file: 配置文件名
            
        Returns:
            bool: 保存是否成功
        """
        try:
            config_path = self.config_dir / config_file
            data = config.to_dict()
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
                else:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            self._config_cache[config_file] = config
            self.logger.info(f"配置文件保存成功: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {config_file}, 错误: {e}")
            return False
    
    def update_quality_config(self, updates: Dict[str, Any], config_file: str = "quality_config.yaml") -> bool:
        """
        更新质量监控配置
        
        Args:
            updates: 要更新的配置项
            config_file: 配置文件名
            
        Returns:
            bool: 更新是否成功
        """
        try:
            config = self.load_quality_config(config_file)
            
            # 更新配置
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                elif key in ['thresholds', 'monitoring']:
                    # 更新嵌套配置
                    nested_config = getattr(config, key)
                    if isinstance(value, dict):
                        for nested_key, nested_value in value.items():
                            if hasattr(nested_config, nested_key):
                                setattr(nested_config, nested_key, nested_value)
                else:
                    self.logger.warning(f"未知的配置项: {key}")
            
            # 验证更新后的配置
            if not config.validate():
                self.logger.error("更新后的配置验证失败")
                return False
            
            return self.save_quality_config(config, config_file)
            
        except Exception as e:
            self.logger.error(f"更新配置失败: {e}")
            return False
    
    def get_config_value(self, key_path: str, config_file: str = "quality_config.yaml", default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径，支持点分隔的嵌套路径，如 'thresholds.response_time_threshold'
            config_file: 配置文件名
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        try:
            config = self.load_quality_config(config_file)
            
            keys = key_path.split('.')
            value = config
            
            for key in keys:
                if hasattr(value, key):
                    value = getattr(value, key)
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"获取配置值失败: {key_path}, 错误: {e}")
            return default
    
    def list_config_files(self) -> list:
        """
        列出所有配置文件
        
        Returns:
            list: 配置文件列表
        """
        config_files = []
        for file_path in self.config_dir.glob("*.yaml"):
            config_files.append(file_path.name)
        for file_path in self.config_dir.glob("*.yml"):
            config_files.append(file_path.name)
        for file_path in self.config_dir.glob("*.json"):
            config_files.append(file_path.name)
        
        return sorted(config_files)
    
    def backup_config(self, config_file: str = "quality_config.yaml") -> Optional[Path]:
        """
        备份配置文件
        
        Args:
            config_file: 配置文件名
            
        Returns:
            Optional[Path]: 备份文件路径，失败时返回None
        """
        try:
            import datetime
            
            config_path = self.config_dir / config_file
            if not config_path.exists():
                self.logger.warning(f"配置文件不存在: {config_path}")
                return None
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{config_path.stem}_backup_{timestamp}{config_path.suffix}"
            backup_path = self.config_dir / backup_name
            
            import shutil
            shutil.copy2(config_path, backup_path)
            
            self.logger.info(f"配置文件备份成功: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"备份配置文件失败: {e}")
            return None
    
    def restore_config(self, backup_file: str, target_file: str = "quality_config.yaml") -> bool:
        """
        恢复配置文件
        
        Args:
            backup_file: 备份文件名
            target_file: 目标配置文件名
            
        Returns:
            bool: 恢复是否成功
        """
        try:
            backup_path = self.config_dir / backup_file
            target_path = self.config_dir / target_file
            
            if not backup_path.exists():
                self.logger.error(f"备份文件不存在: {backup_path}")
                return False
            
            import shutil
            shutil.copy2(backup_path, target_path)
            
            # 清除缓存
            if target_file in self._config_cache:
                del self._config_cache[target_file]
            
            self.logger.info(f"配置文件恢复成功: {target_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"恢复配置文件失败: {e}")
            return False