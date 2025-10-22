# -*- encoding=utf8 -*-
"""
迁移指南

帮助从旧的分散模块迁移到新的统一架构
"""

import os
import sys
import importlib
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入新的统一核心模块
from core import (
    create_unified_system, get_system_info,
    UnifiedElementMapper, UnifiedQualityAnalyzer, UnifiedDataAnalyzer,
    UnifiedReportGenerator, UnifiedConfigManager, UnifiedPerformanceOptimizer,
    UnifiedMonitor
)


class MigrationHelper:
    """迁移助手"""
    
    def __init__(self):
        self.migration_log = []
        self.unified_system = None
        
    def check_legacy_modules(self) -> Dict[str, bool]:
        """检查旧模块的可用性"""
        legacy_modules = {
            'mappers.airtest_poco_element_mapper': False,
            'mappers.improved_airtest_poco_mapper': False,
            'mappers.precise_airtest_poco_mapper': False,
            'analyzers.element_analyzer': False,
            'analyzers.quality_analyzer': False,
            'reporters.html_reporter': False,
            'reporters.json_reporter': False,
            'optimizers.performance_optimizer': False,
            'config.config_manager': False,
            'utils.data_processor': False,
            'metrics.quality_metrics': False
        }
        
        for module_name in legacy_modules.keys():
            try:
                importlib.import_module(module_name)
                legacy_modules[module_name] = True
                self.migration_log.append(f"✓ 发现旧模块: {module_name}")
            except ImportError:
                self.migration_log.append(f"✗ 旧模块不存在: {module_name}")
        
        return legacy_modules
    
    def create_unified_system_instance(self, config_file: str = None) -> Dict[str, Any]:
        """创建统一系统实例"""
        try:
            self.unified_system = create_unified_system(config_file)
            self.migration_log.append("✓ 成功创建统一系统实例")
            return self.unified_system
        except Exception as e:
            self.migration_log.append(f"✗ 创建统一系统失败: {e}")
            return {}
    
    def migrate_element_mapping(self, legacy_data: List[Dict]) -> List[Any]:
        """迁移元素映射数据"""
        if not self.unified_system:
            self.migration_log.append("✗ 统一系统未初始化")
            return []
        
        try:
            element_mapper = self.unified_system['element_mapper']
            migrated_mappings = []
            
            for data in legacy_data:
                # 从旧格式转换为新格式
                if 'airtest_element' in data and 'poco_element' in data:
                    mapping = element_mapper.create_mappings(
                        [data['airtest_element']],
                        [data['poco_element']]
                    )[0]
                    migrated_mappings.append(mapping)
            
            self.migration_log.append(f"✓ 成功迁移 {len(migrated_mappings)} 个元素映射")
            return migrated_mappings
            
        except Exception as e:
            self.migration_log.append(f"✗ 元素映射迁移失败: {e}")
            return []
    
    def migrate_quality_analysis(self, legacy_results: List[Dict]) -> List[Any]:
        """迁移质量分析结果"""
        if not self.unified_system:
            self.migration_log.append("✗ 统一系统未初始化")
            return []
        
        try:
            quality_analyzer = self.unified_system['quality_analyzer']
            migrated_results = []
            
            for result in legacy_results:
                # 转换旧的质量分析结果格式
                quality_metrics = quality_analyzer.create_quality_metrics(
                    coverage=result.get('coverage', 0.0),
                    accuracy=result.get('accuracy', 0.0),
                    consistency=result.get('consistency', 0.0),
                    completeness=result.get('completeness', 0.0),
                    reliability=result.get('reliability', 0.0)
                )
                migrated_results.append(quality_metrics)
            
            self.migration_log.append(f"✓ 成功迁移 {len(migrated_results)} 个质量分析结果")
            return migrated_results
            
        except Exception as e:
            self.migration_log.append(f"✗ 质量分析迁移失败: {e}")
            return []
    
    def migrate_configuration(self, legacy_config: Dict[str, Any]) -> bool:
        """迁移配置"""
        if not self.unified_system:
            self.migration_log.append("✗ 统一系统未初始化")
            return False
        
        try:
            config_manager = self.unified_system['config_manager']
            
            # 映射旧配置到新配置结构
            config_mapping = {
                'similarity_threshold': 'mapping.confidence_threshold',
                'quality_weights': 'quality.quality_weights',
                'output_format': 'report.output_formats',
                'max_workers': 'system.max_workers',
                'debug_mode': 'system.enable_debug'
            }
            
            for old_key, new_key in config_mapping.items():
                if old_key in legacy_config:
                    config_manager.set_config(new_key, legacy_config[old_key])
            
            self.migration_log.append("✓ 成功迁移配置")
            return True
            
        except Exception as e:
            self.migration_log.append(f"✗ 配置迁移失败: {e}")
            return False
    
    def generate_migration_report(self) -> str:
        """生成迁移报告"""
        report = []
        report.append("=" * 60)
        report.append("YouKey Life Element Exploration 迁移报告")
        report.append("=" * 60)
        report.append("")
        
        # 系统信息
        system_info = get_system_info()
        report.append(f"新系统版本: {system_info['version']}")
        report.append(f"作者: {system_info['author']}")
        report.append("")
        
        # 核心组件
        report.append("核心组件:")
        for component in system_info['components']:
            report.append(f"  • {component}")
        report.append("")
        
        # 新功能特性
        report.append("新功能特性:")
        for feature in system_info['features']:
            report.append(f"  • {feature}")
        report.append("")
        
        # 迁移日志
        report.append("迁移日志:")
        for log_entry in self.migration_log:
            report.append(f"  {log_entry}")
        report.append("")
        
        # 迁移建议
        report.append("迁移建议:")
        report.append("  1. 使用 create_unified_system() 创建新的系统实例")
        report.append("  2. 通过 UnifiedConfigManager 管理所有配置")
        report.append("  3. 使用 UnifiedElementMapper 替代所有旧的映射器")
        report.append("  4. 使用 UnifiedQualityAnalyzer 进行质量分析")
        report.append("  5. 使用 UnifiedReportGenerator 生成报告")
        report.append("  6. 启用 UnifiedMonitor 进行实时监控")
        report.append("")
        
        # 代码示例
        report.append("代码示例:")
        report.append("```python")
        report.append("from core import create_unified_system")
        report.append("")
        report.append("# 创建统一系统")
        report.append("system = create_unified_system('config.yaml')")
        report.append("")
        report.append("# 使用元素映射器")
        report.append("mapper = system['element_mapper']")
        report.append("mappings = mapper.analyze_file('test_script.py')")
        report.append("")
        report.append("# 使用质量分析器")
        report.append("analyzer = system['quality_analyzer']")
        report.append("quality = analyzer.analyze_mappings(mappings)")
        report.append("")
        report.append("# 生成报告")
        report.append("reporter = system['report_generator']")
        report.append("report = reporter.generate_comprehensive_report(mappings, quality)")
        report.append("```")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def create_migration_script(self, output_file: str = "migrate_to_unified.py") -> bool:
        """创建迁移脚本"""
        try:
            script_content = '''#!/usr/bin/env python3
# -*- encoding=utf8 -*-
"""
自动迁移脚本

将旧的分散模块迁移到新的统一架构
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import create_unified_system, get_system_info
from migration_guide import MigrationHelper


def main():
    """主迁移函数"""
    print("开始迁移到统一架构...")
    
    # 创建迁移助手
    helper = MigrationHelper()
    
    # 检查旧模块
    print("\\n1. 检查旧模块...")
    legacy_modules = helper.check_legacy_modules()
    available_modules = [name for name, available in legacy_modules.items() if available]
    print(f"发现 {len(available_modules)} 个可用的旧模块")
    
    # 创建统一系统
    print("\\n2. 创建统一系统...")
    system = helper.create_unified_system_instance()
    if system:
        print("✓ 统一系统创建成功")
    else:
        print("✗ 统一系统创建失败")
        return
    
    # 迁移示例数据（如果存在）
    print("\\n3. 迁移数据...")
    
    # 这里可以添加具体的数据迁移逻辑
    # 例如：从旧的输出文件中读取数据并迁移
    
    # 生成迁移报告
    print("\\n4. 生成迁移报告...")
    report = helper.generate_migration_report()
    
    # 保存报告
    report_file = "migration_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ 迁移报告已保存到: {report_file}")
    
    # 显示系统信息
    print("\\n5. 新系统信息:")
    system_info = get_system_info()
    print(f"版本: {system_info['version']}")
    print(f"组件数量: {len(system_info['components'])}")
    print(f"功能特性: {len(system_info['features'])}")
    
    print("\\n迁移完成！请查看迁移报告了解详细信息。")


if __name__ == "__main__":
    main()
'''
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 设置执行权限
            os.chmod(output_file, 0o755)
            
            self.migration_log.append(f"✓ 创建迁移脚本: {output_file}")
            return True
            
        except Exception as e:
            self.migration_log.append(f"✗ 创建迁移脚本失败: {e}")
            return False


def demonstrate_unified_system():
    """演示统一系统的使用"""
    print("=" * 60)
    print("统一系统演示")
    print("=" * 60)
    
    # 创建统一系统
    print("\\n1. 创建统一系统...")
    system = create_unified_system()
    
    # 显示系统信息
    print("\\n2. 系统信息:")
    info = get_system_info()
    for key, value in info.items():
        if isinstance(value, list):
            print(f"{key}: {len(value)} 项")
            for item in value[:3]:  # 只显示前3项
                print(f"  • {item}")
            if len(value) > 3:
                print(f"  ... 还有 {len(value) - 3} 项")
        else:
            print(f"{key}: {value}")
    
    # 演示配置管理
    print("\\n3. 配置管理演示:")
    config_manager = system['config_manager']
    print(f"映射置信度阈值: {config_manager.get_config('mapping.confidence_threshold')}")
    print(f"系统最大工作线程: {config_manager.get_config('system.max_workers')}")
    
    # 演示元素映射
    print("\\n4. 元素映射演示:")
    element_mapper = system['element_mapper']
    print(f"元素映射器类型: {type(element_mapper).__name__}")
    
    # 演示质量分析
    print("\\n5. 质量分析演示:")
    quality_analyzer = system['quality_analyzer']
    print(f"质量分析器类型: {type(quality_analyzer).__name__}")
    
    # 演示报告生成
    print("\\n6. 报告生成演示:")
    report_generator = system['report_generator']
    print(f"报告生成器类型: {type(report_generator).__name__}")
    
    # 演示性能优化
    print("\\n7. 性能优化演示:")
    optimizer = system['performance_optimizer']
    print(f"性能优化器类型: {type(optimizer).__name__}")
    
    # 演示监控系统
    print("\\n8. 监控系统演示:")
    monitor = system['monitor']
    print(f"监控器类型: {type(monitor).__name__}")
    
    print("\\n演示完成！")


if __name__ == "__main__":
    # 创建迁移助手
    helper = MigrationHelper()
    
    # 检查旧模块
    print("检查旧模块...")
    legacy_modules = helper.check_legacy_modules()
    
    # 创建统一系统
    print("\\n创建统一系统...")
    system = helper.create_unified_system_instance()
    
    # 生成迁移报告
    print("\\n生成迁移报告...")
    report = helper.generate_migration_report()
    print(report)
    
    # 创建迁移脚本
    print("\\n创建迁移脚本...")
    helper.create_migration_script()
    
    # 演示统一系统
    print("\\n" + "=" * 60)
    demonstrate_unified_system()