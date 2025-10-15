#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fusion Framework - 智能融合测试框架

一个专门用于Airtest和Poco脚本智能融合的测试框架，
集成Qwen API进行智能对齐和执行。
"""

from .core.main import FusionTestFramework
from .core.config import FusionConfig, load_config, create_default_config_file
from .core.discovery import TestCaseDiscovery, TestCaseInfo
from .core.enhanced_parser import EnhancedScriptParser
from .core.intelligent_alignment import align_script_pair, QwenAlignmentAssistant
from .core.persistence import FusionPersistence, FusionScript, FusionMetadata, FusionStep
from .core.failover_executor import FailoverExecutor, ExecutionConfig, ExecutionStrategy
from .core.reporter import FusionReporter
from .core.qwen_config import QwenConfig, create_config, get_default_config

__version__ = "1.0.0"
__author__ = "Fusion Framework Team"
__description__ = "智能融合测试框架"

__all__ = [
    # 主要类
    'FusionTestFramework',
    'FusionConfig',
    'TestCaseDiscovery',
    'TestCaseInfo',
    'EnhancedScriptParser',
    'FusionPersistence',
    'FusionScript',
    'FusionMetadata', 
    'FusionStep',
    'FailoverExecutor',
    'FusionReporter',
    'QwenAlignmentAssistant',
    'QwenConfig',
    
    # 配置类
    'ExecutionConfig',
    'ExecutionStrategy',
    
    # 函数
    'align_script_pair',
    'load_config',
    'create_default_config_file',
    'create_config',
    'get_default_config',
    
    # 元数据
    '__version__',
    '__author__',
    '__description__',
]