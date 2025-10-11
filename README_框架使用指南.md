# Airtest 通用自动化测试框架使用指南

## 概述

这是一个通用的 Airtest 自动化测试框架，允许您将任何 `.air` 项目放置在项目中的任意位置，按照命名规则重命名后即可自动被发现和执行，无需修改项目内部的任何代码。

## 核心特性

### 🚀 零代码集成
- 将 `.air` 项目放入指定目录
- 按照命名规则重命名
- 自动发现和执行，无需修改内部代码

### 📁 智能项目管理
- 自动发现和分类测试项目
- 支持元数据配置
- 灵活的目录结构

### 🔧 强大的执行引擎
- 单个测试和批量执行
- 设备管理和连接
- 错误处理和重试机制

### 📊 完整的报告系统
- HTML、JSON、XML 多格式报告
- 截图和日志集成
- 趋势分析和统计

## 快速开始

### 1. 项目结构设置

```
your_project/
├── airtest_framework/          # 框架代码（已提供）
├── tests/                      # 测试目录
│   ├── mobile/                 # 移动端测试
│   ├── web/                    # Web测试
│   └── api/                    # API测试
├── config/                     # 配置文件
├── reports/                    # 测试报告
└── logs/                       # 日志文件
```

### 2. 添加测试项目

#### 方法一：直接复制
```bash
# 将您的 .air 项目复制到测试目录
cp -r /path/to/your/project.air tests/mobile/android_登录测试.air
```

#### 方法二：使用框架工具
```python
from airtest_framework.utils import FileUtils

# 复制项目并自动重命名
FileUtils.copy_air_project(
    source="/path/to/your/project.air",
    target="tests/mobile/android_登录测试.air"
)
```

### 3. 命名规则

#### 基本格式
```
{平台}_{功能描述}.air
```

#### 示例
- `android_登录测试.air` - Android平台登录测试
- `ios_购物流程.air` - iOS平台购物流程测试
- `web_用户管理.air` - Web平台用户管理测试
- `api_接口测试.air` - API接口测试

#### 高级格式（可选）
```
{平台}_{模块}_{功能}_{优先级}.air
```

示例：
- `android_auth_login_high.air` - 高优先级Android认证登录测试
- `ios_shop_cart_medium.air` - 中优先级iOS购物车测试

### 4. 元数据配置（可选）

在 `.air` 项目根目录创建 `metadata.yaml` 文件：

```yaml
# 基本信息
name: "登录功能测试"
description: "测试用户登录功能的完整流程"
version: "1.0.0"
author: "测试工程师"

# 分类和优先级
category: "mobile"
priority: "high"
tags:
  - "login"
  - "smoke"
  - "android"

# 设备要求
device_requirements:
  platform: "Android"
  min_version: "7.0"

# 执行配置
execution:
  timeout: 300
  retry_count: 2
```

## 使用方法

### 1. 基本使用

```python
from airtest_framework import AirtestFramework

# 创建框架实例
framework = AirtestFramework()

# 发现测试项目
tests = framework.discover_tests("tests/")

# 执行单个测试
result = framework.run_single_test(
    "tests/mobile/android_登录测试.air",
    device_uri="Android:///"
)

# 批量执行
results = framework.run_batch_tests(
    test_paths=["tests/mobile/"],
    device_uri="Android:///"
)
```

### 2. 快速运行

```python
# 一行代码执行测试
result = framework.quick_run(
    "tests/mobile/android_登录测试.air",
    device_uri="Android:///"
)
```

### 3. 高级过滤

```python
# 按分类过滤
mobile_tests = framework.discover_tests("tests/", category="mobile")

# 按标签过滤
smoke_tests = framework.discover_tests("tests/", tags=["smoke"])

# 按优先级过滤
high_priority = framework.discover_tests("tests/", priority="high")

# 组合过滤
android_smoke = framework.discover_tests(
    "tests/", 
    category="mobile", 
    tags=["android", "smoke"]
)
```

### 4. 配置管理

```python
# 加载配置
framework.load_config("config/test_config.yaml")

# 动态配置
config = {
    'device': {
        'default_platform': 'Android',
        'connection_timeout': 30
    },
    'execution': {
        'retry_count': 3,
        'screenshot_on_error': True
    }
}
framework.configure(config)
```

## 命令行使用

### 1. 发现测试

```bash
python -m airtest_framework discover tests/
```

### 2. 执行测试

```bash
# 执行单个测试
python -m airtest_framework run tests/mobile/android_登录测试.air --device Android:///

# 批量执行
python -m airtest_framework run tests/mobile/ --device Android:///

# 按条件执行
python -m airtest_framework run tests/ --category mobile --priority high
```

### 3. 生成报告

```bash
python -m airtest_framework report --input reports/latest.json --format html
```

## 高级功能

### 1. 自定义测试注册

```python
from airtest_framework.core import test_case, test_suite

@test_case(name="custom_test", priority="high", tags=["custom"])
def my_custom_test():
    """自定义测试函数"""
    # 测试逻辑
    pass

@test_suite(name="my_suite", tests=["custom_test", "other_test"])
class MyTestSuite:
    pass
```

### 2. 设备管理

```python
from airtest_framework.utils import DeviceUtils

# 获取设备列表
devices = DeviceUtils.get_android_devices()

# 检查设备连接
is_connected = DeviceUtils.check_device_connection("Android:///")

# 设备信息
device_info = DeviceUtils.get_device_info("Android:///")
```

### 3. 报告分析

```python
# 生成报告
reporter = framework.get_reporter()
report = reporter.generate_html_report(results, "reports/test_report.html")

# 分析趋势
analyzer = reporter.get_analyzer()
trends = analyzer.analyze_test_trends("reports/")
flaky_tests = analyzer.identify_flaky_tests("reports/")
```

## 最佳实践

### 1. 项目组织

- **按平台分类**：`mobile/`, `web/`, `api/`
- **按功能模块**：`auth/`, `shop/`, `user/`
- **按测试类型**：`smoke/`, `regression/`, `performance/`

### 2. 命名约定

- 使用有意义的描述性名称
- 包含平台和功能信息
- 保持一致的命名风格

### 3. 元数据管理

- 为重要测试添加元数据
- 设置合适的优先级和标签
- 配置设备要求和执行参数

### 4. 配置管理

- 使用环境特定的配置文件
- 将敏感信息存储在安全位置
- 定期更新和维护配置

## 故障排除

### 常见问题

#### 1. 测试项目未被发现
- 检查文件名是否符合命名规则
- 确认项目结构完整（包含 `main.py`）
- 验证目录权限

#### 2. 设备连接失败
- 检查设备连接状态
- 验证 ADB 配置
- 确认设备 URI 格式正确

#### 3. 测试执行失败
- 查看详细日志信息
- 检查设备兼容性
- 验证测试脚本语法

### 调试技巧

```python
# 启用调试模式
framework.configure({'framework': {'debug': True}})

# 查看详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 验证项目
is_valid, issues = framework.validate_project("tests/mobile/test.air")
if not is_valid:
    print("项目问题:", issues)
```

## 扩展开发

### 1. 自定义发现器

```python
from airtest_framework.core import AirtestDiscovery

class CustomDiscovery(AirtestDiscovery):
    def discover_tests(self, directory):
        # 自定义发现逻辑
        pass
```

### 2. 自定义执行器

```python
from airtest_framework.core import AirtestExecutor

class CustomExecutor(AirtestExecutor):
    def execute_test(self, test_path, device_uri):
        # 自定义执行逻辑
        pass
```

### 3. 自定义报告器

```python
from airtest_framework.core import TestReporter

class CustomReporter(TestReporter):
    def generate_custom_report(self, results):
        # 自定义报告生成
        pass
```

## 示例项目

查看 `example_project.py` 文件获取完整的使用示例。

## 支持和贡献

- 问题反馈：提交 Issue
- 功能建议：提交 Feature Request
- 代码贡献：提交 Pull Request

## 许可证

本项目采用 MIT 许可证。