# Airtest 自动化测试框架 - API文档

## 文档信息
- **文档版本**: v1.0.0
- **创建日期**: 2025-10-13
- **最后更新**: 2025-10-13
- **文档状态**: 正式版
- **维护人员**: 开发团队

> **文档定位**：API接口文档，面向开发者和集成人员  
> **相关文档**：[需求文档](./需求文档.md) | [设计文档](./设计文档.md) | [用户手册](./用户手册.md)

## 目录
- [1. 核心框架API](#1-核心框架api)
- [2. 融合测试API](#2-融合测试api)
- [3. 工具类API](#3-工具类api)
- [4. 配置API](#4-配置api)
- [5. 错误码](#5-错误码)

## 1. 核心框架API

### 1.1 TestCaseDiscovery 类

测试用例发现和管理类。

#### 初始化
```python
from airtest_framework.core.discovery import TestCaseDiscovery

discovery = TestCaseDiscovery(config=None)
```

**参数**:
- `config` (Optional[Config]): 配置对象，默认为None

#### discover_tests()
发现测试用例。

```python
def discover_tests(self, 
                  test_root: str = "tests",
                  pattern: str = "*.air") -> List[TestCase]
```

**参数**:
- `test_root` (str): 测试根目录，默认"tests"
- `pattern` (str): 文件匹配模式，默认"*.air"

**返回值**:
- `List[TestCase]`: 发现的测试用例列表

**示例**:
```python
discovery = TestCaseDiscovery()
test_cases = discovery.discover_tests("tests/mobile")
print(f"发现 {len(test_cases)} 个测试用例")
```

#### filter_tests()
过滤测试用例。

```python
def filter_tests(self,
                test_cases: List[TestCase],
                category: Optional[str] = None,
                priority: Optional[str] = None,
                platform: Optional[str] = None,
                tags: Optional[List[str]] = None) -> List[TestCase]
```

**参数**:
- `test_cases` (List[TestCase]): 待过滤的测试用例
- `category` (Optional[str]): 分类过滤
- `priority` (Optional[str]): 优先级过滤
- `platform` (Optional[str]): 平台过滤
- `tags` (Optional[List[str]]): 标签过滤

**返回值**:
- `List[TestCase]`: 过滤后的测试用例列表

### 1.2 TestExecutor 类

测试执行器类。

#### 初始化
```python
from airtest_framework.core.executor import TestExecutor

executor = TestExecutor(config=None)
```

#### execute_test()
执行单个测试用例。

```python
def execute_test(self, test_case: TestCase) -> TestResult
```

**参数**:
- `test_case` (TestCase): 要执行的测试用例

**返回值**:
- `TestResult`: 测试执行结果

#### execute_tests()
批量执行测试用例。

```python
def execute_tests(self, 
                 test_cases: List[TestCase],
                 parallel: bool = False,
                 max_workers: int = 4) -> List[TestResult]
```

**参数**:
- `test_cases` (List[TestCase]): 要执行的测试用例列表
- `parallel` (bool): 是否并行执行，默认False
- `max_workers` (int): 最大并发数，默认4

**返回值**:
- `List[TestResult]`: 测试执行结果列表

### 1.3 TestReporter 类

测试报告生成器类。

#### 初始化
```python
from airtest_framework.core.reporter import TestReporter

reporter = TestReporter(output_dir="reports")
```

#### generate_report()
生成测试报告。

```python
def generate_report(self,
                   results: List[TestResult],
                   format: str = "html",
                   template: Optional[str] = None) -> str
```

**参数**:
- `results` (List[TestResult]): 测试结果列表
- `format` (str): 报告格式，支持"html"、"json"
- `template` (Optional[str]): 自定义模板路径

**返回值**:
- `str`: 生成的报告文件路径

## 2. 融合测试API

### 2.1 FusionTestFramework 类

融合测试框架主类。

#### 初始化
```python
from airtest_framework.fusion.main import FusionTestFramework

framework = FusionTestFramework(config=None)
```

#### discover_test_cases()
发现融合测试用例。

```python
def discover_test_cases(self, 
                       test_root: Optional[str] = None) -> List[TestCaseInfo]
```

**参数**:
- `test_root` (Optional[str]): 测试根目录

**返回值**:
- `List[TestCaseInfo]`: 发现的测试用例信息列表

#### run_test_cases()
执行融合测试用例。

```python
def run_test_cases(self,
                  test_cases: Optional[List[TestCaseInfo]] = None,
                  case_filter: Optional[str] = None) -> List[FusionExecutionResult]
```

**参数**:
- `test_cases` (Optional[List[TestCaseInfo]]): 测试用例列表
- `case_filter` (Optional[str]): 用例过滤条件

**返回值**:
- `List[FusionExecutionResult]`: 执行结果列表

### 2.2 StepAlignment 类

步骤对齐类。

#### 初始化
```python
from airtest_framework.fusion.alignment import StepAlignment

alignment = StepAlignment()
```

#### parse_airtest_script()
解析Airtest脚本。

```python
def parse_airtest_script(self, script_path: str) -> List[ActionStep]
```

**参数**:
- `script_path` (str): Airtest脚本路径

**返回值**:
- `List[ActionStep]`: 解析的动作步骤列表

#### parse_poco_script()
解析Poco脚本。

```python
def parse_poco_script(self, script_path: str) -> List[ActionStep]
```

**参数**:
- `script_path` (str): Poco脚本路径

**返回值**:
- `List[ActionStep]`: 解析的动作步骤列表

#### align_steps()
对齐步骤。

```python
def align_steps(self) -> List[AlignedStepPair]
```

**返回值**:
- `List[AlignedStepPair]`: 对齐的步骤对列表

### 2.3 MultiDimensionExecutor 类

多维度执行器类。

#### 初始化
```python
from airtest_framework.fusion.executor import MultiDimensionExecutor, ExecutionStrategy

executor = MultiDimensionExecutor(strategy=ExecutionStrategy.POCO_FIRST)
```

#### execute_fusion_case()
执行融合测试用例。

```python
def execute_fusion_case(self,
                       case_name: str,
                       aligned_steps: List[AlignedStepPair]) -> FusionExecutionResult
```

**参数**:
- `case_name` (str): 用例名称
- `aligned_steps` (List[AlignedStepPair]): 对齐的步骤列表

**返回值**:
- `FusionExecutionResult`: 融合执行结果

## 3. 工具类API

### 3.1 SmartIconMatcher 类

智能图标匹配工具。

#### 初始化
```python
from airtest_framework.utils.smart_icon_matcher import SmartIconMatcher

matcher = SmartIconMatcher()
```

#### multi_state_touch()
多状态图标点击。

```python
def multi_state_touch(self, 
                     icon_states: List[str],
                     timeout: float = 10.0) -> bool
```

**参数**:
- `icon_states` (List[str]): 图标状态列表
- `timeout` (float): 超时时间，默认10.0秒

**返回值**:
- `bool`: 是否点击成功

#### get_current_state()
获取当前状态。

```python
def get_current_state(self, 
                     state_mapping: Dict[str, str]) -> Optional[str]
```

**参数**:
- `state_mapping` (Dict[str, str]): 状态映射字典

**返回值**:
- `Optional[str]`: 当前状态名称

#### switch_to_state()
切换到指定状态。

```python
def switch_to_state(self,
                   target_state: str,
                   state_mapping: Dict[str, str],
                   max_attempts: int = 3) -> bool
```

**参数**:
- `target_state` (str): 目标状态
- `state_mapping` (Dict[str, str]): 状态映射字典
- `max_attempts` (int): 最大尝试次数，默认3

**返回值**:
- `bool`: 是否切换成功

### 3.2 DeviceUtils 类

设备管理工具。

#### get_connected_devices()
获取已连接设备。

```python
@staticmethod
def get_connected_devices() -> List[str]
```

**返回值**:
- `List[str]`: 设备ID列表

#### connect_device()
连接设备。

```python
@staticmethod
def connect_device(device_uri: str) -> bool
```

**参数**:
- `device_uri` (str): 设备URI

**返回值**:
- `bool`: 是否连接成功

## 4. 配置API

### 4.1 Config 类

配置管理类。

#### 初始化
```python
from airtest_framework.core.config import Config

config = Config.from_file("config.yaml")
```

#### from_file()
从文件加载配置。

```python
@classmethod
def from_file(cls, config_path: str) -> 'Config'
```

**参数**:
- `config_path` (str): 配置文件路径

**返回值**:
- `Config`: 配置对象

#### to_dict()
转换为字典。

```python
def to_dict(self) -> Dict[str, Any]
```

**返回值**:
- `Dict[str, Any]`: 配置字典

## 5. 数据模型

### 5.1 TestCase 类

测试用例数据模型。

```python
@dataclass
class TestCase:
    name: str                    # 用例名称
    path: str                    # 用例路径
    category: str                # 分类
    priority: str                # 优先级
    platform: str                # 平台
    tags: List[str]              # 标签
    description: str             # 描述
    author: str                  # 作者
    created_time: datetime       # 创建时间
    modified_time: datetime      # 修改时间
```

### 5.2 TestResult 类

测试结果数据模型。

```python
@dataclass
class TestResult:
    test_case: TestCase          # 测试用例
    status: str                  # 执行状态
    start_time: datetime         # 开始时间
    end_time: datetime           # 结束时间
    duration: float              # 执行时长
    error_message: str           # 错误信息
    screenshots: List[str]       # 截图列表
    logs: List[str]              # 日志列表
```

### 5.3 FusionExecutionResult 类

融合执行结果数据模型。

```python
@dataclass
class FusionExecutionResult:
    case_name: str                           # 用例名称
    total_steps: int                         # 总步骤数
    successful_steps: int                    # 成功步骤数
    failed_steps: int                        # 失败步骤数
    fallback_steps: int                      # 回退步骤数
    total_execution_time: float              # 总执行时间
    step_results: List[StepExecutionResult]  # 步骤结果列表
    overall_result: ExecutionResult          # 总体结果
```

## 6. 错误码

### 6.1 通用错误码

| 错误码 | 错误信息 | 描述 |
|--------|----------|------|
| E001 | Configuration file not found | 配置文件未找到 |
| E002 | Invalid configuration format | 配置文件格式错误 |
| E003 | Test directory not found | 测试目录未找到 |
| E004 | No test cases discovered | 未发现测试用例 |
| E005 | Device connection failed | 设备连接失败 |

### 6.2 执行错误码

| 错误码 | 错误信息 | 描述 |
|--------|----------|------|
| E101 | Test execution timeout | 测试执行超时 |
| E102 | Script parsing failed | 脚本解析失败 |
| E103 | Element not found | 元素未找到 |
| E104 | Screenshot capture failed | 截图失败 |
| E105 | Poco driver not initialized | Poco驱动未初始化 |

### 6.3 报告错误码

| 错误码 | 错误信息 | 描述 |
|--------|----------|------|
| E201 | Report generation failed | 报告生成失败 |
| E202 | Template not found | 模板未找到 |
| E203 | Output directory not writable | 输出目录不可写 |
| E204 | JSON serialization failed | JSON序列化失败 |

## 7. 使用示例

### 7.1 基本使用示例

```python
from airtest_framework.core import TestFramework

# 创建框架实例
framework = TestFramework()

# 发现测试用例
test_cases = framework.discover_tests("tests/mobile")

# 过滤测试用例
filtered_cases = framework.filter_tests(
    test_cases, 
    category="ui", 
    priority="high"
)

# 执行测试
results = framework.execute_tests(filtered_cases)

# 生成报告
report_path = framework.generate_report(results, format="html")
print(f"报告已生成: {report_path}")
```

### 7.2 融合测试示例

```python
from airtest_framework.fusion import FusionTestFramework

# 创建融合测试框架
framework = FusionTestFramework()

# 发现测试用例
test_cases = framework.discover_test_cases("tests/mobile")

# 执行融合测试
results = framework.run_test_cases(test_cases)

# 生成报告
report_info = framework.generate_report(results)
print(f"HTML报告: {report_info['html']}")
print(f"JSON报告: {report_info['json']}")
```

### 7.3 智能图标匹配示例

```python
from airtest_framework.utils.smart_icon_matcher import SmartIconMatcher

matcher = SmartIconMatcher()

# 多状态图标点击
favorite_states = [
    "favorite_selected.png",
    "favorite_unselected.png"
]

if matcher.multi_state_touch(favorite_states):
    print("成功点击收藏按钮")

# 状态检测和切换
switch_states = {
    "on": "switch_on.png",
    "off": "switch_off.png"
}

current_state = matcher.get_current_state(switch_states)
print(f"当前状态: {current_state}")

# 切换到目标状态
if matcher.switch_to_state("on", switch_states):
    print("成功切换到开启状态")
```

## 8. 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2025-10-13 | 初始版本创建 | 开发团队 |

---

**文档状态**: ✅ 已完成  
**下一步**: 用户手册编写