# -*- encoding=utf8 -*-
"""
融合测试框架核心模块

该模块提供了融合测试框架的核心功能，包括：
- 配置管理
- 测试发现
- 脚本解析
- 智能对齐
- 测试执行
- 报告生成
"""

from .config import FusionConfig, load_config, create_default_config_file
from .discovery import TestCaseDiscovery, TestCaseInfo
from .parser import EnhancedScriptParser
from .alignment import align_script_pair, QwenAlignmentAssistant
from .executor import FailoverExecutor, ExecutionConfig, ExecutionStrategy
from .reporter import FusionReporter

__all__ = [
    'FusionConfig',
    'load_config',
    'create_default_config_file',
    'TestCaseDiscovery',
    'TestCaseInfo',
    'EnhancedScriptParser',
    'align_script_pair',
    'QwenAlignmentAssistant',
    'FailoverExecutor',
    'ExecutionConfig',
    'ExecutionStrategy',
    'FusionReporter',
]

__version__ = '1.0.0'