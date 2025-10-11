# -*- encoding=utf8 -*-
"""
Airtest 自动化测试框架 - 核心模块
"""

from .discovery import AirtestDiscovery, TestMetadata
from .executor import AirtestExecutor, TestResult, BatchExecutor
from .config import ConfigManager, FrameworkConfig, DeviceConfig, ExecutionConfig, ReportConfig, ProjectConfigManager
from .reporter import TestReporter, ReportAnalyzer
from .registry import TestRegistry, AutoTestRegistry, TestCase, get_global_registry, get_auto_registry, test_case, test_suite

__all__ = [
    'AirtestDiscovery',
    'TestMetadata',
    'AirtestExecutor', 
    'TestResult',
    'BatchExecutor',
    'ConfigManager',
    'FrameworkConfig',
    'DeviceConfig', 
    'ExecutionConfig',
    'ReportConfig',
    'ProjectConfigManager',
    'TestReporter',
    'ReportAnalyzer',
    'TestRegistry',
    'AutoTestRegistry',
    'TestCase',
    'get_global_registry',
    'get_auto_registry',
    'test_case',
    'test_suite'
]