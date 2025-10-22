# API参考文档

> **版本**: v2.0.0 | **更新**: 2025-01-17 | **状态**: 正式版

## 快速导航
- [统一系统API](#统一系统api) - 重构后的统一接口
- [传统框架API](#传统框架api) - 原有框架接口
- [数据模型](#数据模型) - 核心数据结构
- [工具类API](#工具类api) - 辅助工具接口

---

## 统一系统API

### UnifiedSystem - 系统入口
```python
from youkey_life_element_exploration import create_unified_system

# 创建系统实例
system = create_unified_system()

# 获取各组件
analyzer = system['analyzer']
monitor = system['monitor'] 
reporter = system['reporter']
optimizer = system['optimizer']
```

### UnifiedAnalyzer - 统一分析器
```python
# 元素映射分析
mappings = analyzer.analyze_elements(airtest_elements, poco_elements)

# 质量分析
quality_score = analyzer.analyze_quality(mappings)

# 数据分析
analysis_result = analyzer.analyze_data(mappings)
```

### UnifiedMonitor - 统一监控器
```python
# 开始监控
monitor.start_monitoring(['element_1', 'element_2'])

# 记录事件
monitor.log_event('user_action', {'action': 'click', 'element': 'button'})

# 获取统计信息
stats = monitor.get_statistics()
```

### UnifiedReporter - 统一报告器
```python
# 生成报告
report_file = reporter.generate_file_report(
    data={'mappings': mappings, 'quality': quality_score},
    report_type="comprehensive",
    format="html"
)
```

---

## 传统框架API

### TestCaseDiscovery - 测试发现
```python
from airtest_framework.core.discovery import TestCaseDiscovery

discovery = TestCaseDiscovery()
tests = discovery.discover_tests(test_root="tests", pattern="*.air")
```

### TestExecutor - 测试执行
```python
from airtest_framework.core.executor import TestExecutor

executor = TestExecutor()
results = executor.execute_tests(tests)
```

---

## 数据模型

### ElementMapping - 元素映射
```python
@dataclass
class ElementMapping:
    airtest_element: AirtestElement
    poco_element: PocoElement
    confidence_score: float
    mapping_type: MappingType
```

### QualityScore - 质量评分
```python
@dataclass  
class QualityScore:
    overall_score: float
    performance_score: float
    visibility_score: float
    accessibility_score: float
```

---

## 工具类API

### 设备工具
```python
from airtest_framework.utils.device_utils import DeviceManager

device_manager = DeviceManager()
devices = device_manager.get_connected_devices()
```

### 文件工具
```python
from airtest_framework.utils.file_utils import FileManager

file_manager = FileManager()
files = file_manager.find_test_files("tests")
```

---

## 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| E001 | 设备连接失败 | 检查设备连接和ADB状态 |
| E002 | 测试文件不存在 | 确认测试文件路径正确 |
| E003 | 配置文件格式错误 | 检查YAML/JSON格式 |

---

## 迁移指南

### 从旧API迁移到统一API
```python
# 旧方式
from youkey_life_element_exploration.analyzers import ElementAnalyzer
analyzer = ElementAnalyzer()

# 新方式  
from youkey_life_element_exploration import create_unified_system
system = create_unified_system()
analyzer = system['analyzer']
```

更多迁移信息请参考 [迁移指南](../youkey_life_element_exploration/migration_guide.py)。