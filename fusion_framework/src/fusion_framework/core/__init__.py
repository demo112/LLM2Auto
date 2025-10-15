# -*- encoding=utf8 -*-
"""
多维度融合测试框架

该模块提供了一个增强的测试执行框架，能够结合不同的录制素材（Airtest图像识别和Poco元素识别）
来提高测试用例的鲁棒性。当一种方法失败时，框架会自动回退到另一种方法。
"""

from .discovery import TestCaseDiscovery
from .alignment import StepAlignment
from .executor import MultiDimensionExecutor
from .reporter import FusionReporter
from .config import FusionConfig, load_config, create_default_config_file

__all__ = [
    'TestCaseDiscovery',
    'StepAlignment', 
    'MultiDimensionExecutor',
    'FusionReporter',
    'FusionConfig',
    'load_config',
    'create_default_config_file'
]

__version__ = '1.0.0'