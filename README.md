# Airtest 自动化测试框架

一个基于 Airtest 的企业级移动应用自动化测试框架，提供完整的测试发现、执行、报告和管理功能。

## 🚀 快速开始

### 安装依赖
```bash
pip install airtest
pip install pyyaml
```

### 基本使用
```bash
# 查看帮助
python3 run_tests.py --help

# 列出所有测试
python3 run_tests.py list

# 执行所有测试
python3 run_tests.py run

# 生成测试报告
python3 run_tests.py run --report --output report.json
```

## 📋 主要功能

### 1. 智能测试发现
- 🔍 自动扫描 `.air` 测试项目
- 📝 解析测试元数据（名称、分类、优先级等）
- 🏷️ 支持标签和分类管理
- 📊 提供详细的测试统计信息

### 2. 灵活的测试过滤
```bash
# 按分类过滤
python3 run_tests.py list --category mobile

# 按优先级过滤
python3 run_tests.py list --priority high

# 按平台过滤
python3 run_tests.py list --platform android

# 按标签过滤
python3 run_tests.py list --tags ui_test,demo

# 按名称模式过滤
python3 run_tests.py list --pattern "*login*"
```

### 3. 强大的执行引擎
```bash
# 模拟执行（不实际运行）
python3 run_tests.py run --dry-run

# 指定设备执行
python3 run_tests.py run --device "Android://127.0.0.1:5037/device_id"

# 并行执行（最多3个并行）
python3 run_tests.py run --parallel

# 执行前验证
python3 run_tests.py run --validate
```

### 4. 丰富的报告功能
```bash
# 生成 HTML 报告
python3 run_tests.py run --report

# 生成 JSON 报告
python3 run_tests.py run --report --output report.json

# 自定义输出目录
python3 run_tests.py run --report --output-dir ./reports
```

## 📁 项目结构

```
演示项目/
├── airtest_framework/          # 框架核心代码
│   ├── __init__.py            # 框架入口
│   ├── core/                  # 核心模块
│   │   ├── discovery.py       # 测试发现引擎
│   │   ├── executor.py        # 测试执行引擎
│   │   ├── reporter.py        # 报告生成引擎
│   │   └── config.py          # 配置管理
│   └── utils/                 # 工具模块
│       ├── file_utils.py      # 文件操作工具
│       ├── device_utils.py    # 设备管理工具
│       └── logger.py          # 日志工具
├── tests/                     # 测试用例目录
│   └── mobile/               # 移动端测试
│       ├── test_case_demo.air      # Airtest 测试用例
│       └── test_case_demo_poco.air # POCO 测试用例
├── fusion_framework/         # 融合测试框架
├── youkey_life_element_exploration/ # UI元素探索系统
│   ├── core/                 # 核心功能模块
│   │   ├── quality_monitor.py    # 质量监控器
│   │   ├── intelligent_analyzer.py # 智能分析器
│   │   ├── performance_optimizer.py # 性能优化器
│   │   ├── anomaly_detector.py    # 异常检测器
│   │   └── element_mapper.py      # 元素映射器
│   ├── mappers/              # 元素映射器模块
│   │   ├── airtest_poco_element_mapper.py # 基础映射器
│   │   ├── improved_airtest_poco_mapper.py # 改进映射器
│   │   └── precise_airtest_poco_mapper.py # 精确映射器
│   ├── scripts/              # 演示和实用脚本
│   │   ├── element_extraction_demo.py # 元素提取演示
│   │   └── element_correlation_analyzer.py # 关联分析器
│   ├── analyzers/            # 分析器模块
│   ├── optimizers/           # 优化器模块
│   ├── reporters/            # 报告生成器
│   ├── utils/                # 工具模块
│   └── config/               # 配置管理
├── run_tests.py              # 主程序入口
├── run_fusion_tests.py       # 融合测试入口
└── README.md                 # 项目说明
```

## 🔧 配置管理

### 默认配置
框架会自动使用默认配置，包括：
- 项目名称：Airtest自动化测试
- 测试目录：tests/
- 日志目录：logs/
- 报告格式：HTML
- 设备URI：Android:///

### 自定义配置
创建 `airtest_config.yaml` 文件：
```yaml
project_name: "我的测试项目"
version: "2.0.0"
test_dirs:
  - "tests/"
  - "integration_tests/"
log_dir: "logs"
device:
  uri: "Android://127.0.0.1:5037"
  timeout: 60
execution:
  parallel: true
  max_workers: 3
  timeout: 300
report:
  format: "html"
  output_dir: "reports"
  include_screenshots: true
```

## 📊 测试项目规范

### 命名规范
- 基础格式：`{平台}_{功能描述}.air`
- 高级格式：`{模块}_{类型}_{平台}_{功能}.air`

### 元数据文件
在 `.air` 目录中创建 `metadata.yaml`：
```yaml
name: "登录功能测试"
description: "测试用户登录流程"
category: "mobile"
priority: "high"
platform: "android"
type: "ui_test"
author: "测试团队"
version: "1.0.0"
tags:
  - "login"
  - "ui_test"
  - "smoke_test"
timeout: 300
retry_count: 2
```

## 📈 测试报告

### HTML 报告
- 📊 测试执行概览
- 📋 详细测试结果
- 🖼️ 截图和日志
- 📈 统计图表

### JSON 报告
```json
{
  "summary": {
    "total": 2,
    "passed": 0,
    "failed": 2,
    "duration": 0.379
  },
  "tests": [
    {
      "name": "mobile_login_test",
      "status": "FAILED",
      "duration": 0.189,
      "error": "设备连接失败"
    }
  ]
}
```

## 🛠️ 高级功能

### 1. 批量操作
```bash
# 验证所有测试项目
python3 run_tests.py validate

# 显示测试统计信息
python3 run_tests.py stats

# 组合过滤条件
python3 run_tests.py run --category mobile --priority high --tags smoke_test
```

### 2. 设备管理
```bash
# 指定具体设备
python3 run_tests.py run --device "Android://127.0.0.1:5037/emulator-5554"

# iOS 设备
python3 run_tests.py run --device "iOS:///http://localhost:8100"
```

### 3. 调试模式
```bash
# 详细输出
python3 run_tests.py list --verbose

# 模拟执行查看计划
python3 run_tests.py run --dry-run --verbose
```

## 🔍 故障排除

### 常见问题

1. **设备连接失败**
   - 检查 ADB 连接：`adb devices`
   - 确认设备 URI 正确
   - 检查设备权限设置

2. **测试发现失败**
   - 确认测试目录存在
   - 检查 `.air` 项目结构
   - 验证文件权限

3. **报告生成失败**
   - 检查输出目录权限
   - 确认磁盘空间充足
   - 验证模板文件完整性

### 日志查看
```bash
# 查看执行日志
tail -f logs/execution/*.log

# 查看框架日志
tail -f logs/framework.log
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

- 📧 邮箱：support@example.com
- 📖 文档：[项目文档](https://docs.example.com)
- 🐛 问题反馈：[GitHub Issues](https://github.com/example/airtest-framework/issues)

---

## 📋 项目需求文档

### 1. 功能需求说明

#### 1.1 核心功能模块

**UI元素探索系统 (youkey_life_element_exploration)**
- **元素映射器 (mappers/)**：建立Airtest模板元素与Poco元素之间的精确关联关系
  - 基础映射器：提供基本的元素关联功能
  - 改进映射器：增强时序分析和语义匹配能力
  - 精确映射器：采用预定义规则确保高精度映射
- **质量监控 (core/)**：实时监控UI元素的质量指标和性能表现
- **智能分析 (analyzers/)**：基于历史数据进行趋势分析和模式识别
- **性能优化 (optimizers/)**：提供自动化的性能优化建议和策略
- **异常检测**：检测和预警潜在的质量问题和异常情况

#### 1.2 测试框架集成
- **Airtest框架集成**：完全兼容现有Airtest测试用例
- **POCO框架支持**：支持POCO元素定位和操作
- **多平台支持**：Android、iOS平台的统一测试接口
- **并行执行**：支持多设备并行测试执行

#### 1.3 报告和分析
- **多格式报告**：支持HTML、JSON、Markdown格式报告
- **可视化分析**：提供图表和统计数据展示
- **历史趋势**：跟踪测试质量和性能的历史变化
- **异常告警**：及时发现和通知测试异常

### 2. 项目管理和维护要求

#### 2.1 代码质量标准
- **编码规范**：严格遵循PEP 8 Python编码规范
- **文档要求**：所有模块和函数必须包含详细的docstring
- **类型注解**：使用typing模块提供完整的类型注解
- **单元测试**：核心功能模块测试覆盖率不低于80%

#### 2.2 项目结构管理
- **模块化设计**：采用清晰的模块化架构，职责分离
- **依赖管理**：使用requirements.txt管理项目依赖
- **配置管理**：统一的配置文件管理，支持环境变量覆盖
- **日志管理**：完善的日志记录和分级管理

#### 2.3 性能要求
- **响应时间**：单个测试用例执行时间不超过5分钟
- **内存使用**：单进程内存使用不超过1GB
- **并发支持**：支持最多10个并发测试执行
- **资源清理**：确保测试结束后完全清理临时资源

#### 2.4 维护策略
- **定期更新**：每月进行依赖包安全更新检查
- **性能监控**：建立性能基线，监控性能退化
- **错误处理**：完善的异常处理和错误恢复机制
- **向后兼容**：保证API的向后兼容性

### 3. 与其他系统的集成规范

#### 3.1 CI/CD集成
- **Jenkins集成**：提供Jenkins插件支持
- **GitHub Actions**：支持GitHub Actions工作流
- **Docker支持**：提供Docker镜像和容器化部署
- **测试报告集成**：与主流测试报告平台集成

#### 3.2 设备管理集成
- **设备农场**：支持与设备农场平台集成
- **云测试平台**：兼容主流云测试服务
- **模拟器支持**：支持Android模拟器和iOS模拟器
- **真机测试**：支持真实设备的远程测试

#### 3.3 数据存储集成
- **数据库支持**：支持MySQL、PostgreSQL、SQLite
- **文件存储**：支持本地文件系统和云存储
- **缓存系统**：支持Redis缓存加速
- **备份恢复**：提供数据备份和恢复机制

#### 3.4 监控和告警集成
- **监控系统**：与Prometheus、Grafana集成
- **告警通知**：支持邮件、短信、钉钉、企业微信通知
- **日志收集**：与ELK Stack集成进行日志分析
- **性能追踪**：支持APM工具集成

### 4. 版本控制策略

#### 4.1 分支管理策略
- **主分支 (main)**：稳定的生产版本代码
- **开发分支 (develop)**：集成最新开发功能
- **功能分支 (feature/)**：新功能开发分支
- **修复分支 (hotfix/)**：紧急问题修复分支
- **发布分支 (release/)**：版本发布准备分支

#### 4.2 版本号规范
- **语义化版本**：采用SemVer (MAJOR.MINOR.PATCH)格式
- **版本标签**：使用Git标签标记正式版本
- **变更日志**：维护详细的CHANGELOG.md文件
- **API版本**：重大API变更时增加版本号

#### 4.3 代码审查流程
- **Pull Request**：所有代码变更必须通过PR
- **代码审查**：至少需要一名资深开发者审查
- **自动化检查**：通过CI/CD自动化代码质量检查
- **测试验证**：确保所有测试用例通过

#### 4.4 发布管理
- **发布计划**：制定明确的版本发布计划
- **测试验证**：发布前进行完整的回归测试
- **灰度发布**：支持灰度发布和回滚机制
- **文档更新**：同步更新用户文档和API文档

#### 4.5 依赖管理
- **依赖锁定**：使用requirements.lock锁定依赖版本
- **安全扫描**：定期进行依赖安全漏洞扫描
- **版本升级**：制定依赖版本升级策略
- **兼容性测试**：依赖升级后进行兼容性测试

### 5. 调用关系和交互逻辑

#### 5.1 模块间调用关系
```
父项目 (演示项目)
├── airtest_framework/          # 基础测试框架
├── fusion_framework/           # 融合测试框架
└── youkey_life_element_exploration/  # UI元素探索系统
    ├── core/                   # 核心模块 (被其他模块调用)
    ├── mappers/                # 映射器 (调用core模块)
    ├── scripts/                # 脚本 (调用mappers和core)
    ├── analyzers/              # 分析器 (调用core和utils)
    ├── optimizers/             # 优化器 (调用analyzers和core)
    ├── reporters/              # 报告器 (调用所有模块)
    ├── utils/                  # 工具模块 (被所有模块调用)
    └── config/                 # 配置模块 (被所有模块调用)
```

#### 5.2 外部系统交互
- **测试用例数据源**：从 `tests/mobile/` 目录读取测试用例
- **配置文件**：读取项目根目录的配置文件
- **输出结果**：生成报告到指定输出目录
- **日志记录**：写入到项目日志目录

#### 5.3 API接口规范
- **统一入口**：通过主模块`__init__.py`提供统一API
- **配置驱动**：支持通过配置文件自定义行为
- **插件机制**：支持第三方插件扩展
- **事件通知**：提供事件回调机制

---

🎉 **开始你的自动化测试之旅吧！**