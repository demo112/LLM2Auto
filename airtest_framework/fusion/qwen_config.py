# -*- encoding=utf8 -*-
"""
Qwen API配置管理

提供Qwen API的配置管理和验证功能
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class QwenConfig:
    """Qwen API配置"""
    api_key: str
    base_url: str = "https://api.siliconflow.cn/v1"
    model: str = "Qwen/Qwen2.5-7B-Instruct"
    max_retries: int = 3
    timeout: int = 30
    temperature: float = 0.1
    max_tokens: int = 500
    
    @classmethod
    def from_env(cls) -> 'QwenConfig':
        """从环境变量创建配置"""
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            raise ValueError("未设置QWEN_API_KEY环境变量")
        
        return cls(
            api_key=api_key,
            base_url=os.getenv("QWEN_BASE_URL", "https://api.siliconflow.cn/v1"),
            model=os.getenv("QWEN_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
            max_retries=int(os.getenv("QWEN_MAX_RETRIES", "3")),
            timeout=int(os.getenv("QWEN_TIMEOUT", "30")),
            temperature=float(os.getenv("QWEN_TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("QWEN_MAX_TOKENS", "500"))
        )
    
    def validate(self) -> bool:
        """验证配置"""
        if not self.api_key:
            raise ValueError("API密钥不能为空")
        
        if not self.base_url:
            raise ValueError("API基础URL不能为空")
        
        if not self.model:
            raise ValueError("模型名称不能为空")
        
        if self.max_retries < 1:
            raise ValueError("最大重试次数必须大于0")
        
        if self.timeout < 1:
            raise ValueError("超时时间必须大于0")
        
        if not (0 <= self.temperature <= 2):
            raise ValueError("温度参数必须在0-2之间")
        
        if self.max_tokens < 1:
            raise ValueError("最大token数必须大于0")
        
        return True


def get_default_config() -> Optional[QwenConfig]:
    """获取默认配置"""
    try:
        return QwenConfig.from_env()
    except ValueError:
        return None


def create_config(api_key: str, **kwargs) -> QwenConfig:
    """创建配置"""
    config = QwenConfig(api_key=api_key, **kwargs)
    config.validate()
    return config