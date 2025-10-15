# Airtest 自动化测试框架

一个基于 Airtest 的企业级移动应用自动化测试框架，提供完整的测试发现、执行、报告和管理功能。

## 🤖 智能融合测试框架

本项目现在包含一个独立的 **智能融合测试框架**，专门用于 Airtest 和 Poco 脚本的智能分析和对齐。

### 融合框架特性
- 🧠 **AI 驱动对齐**: 使用 Qwen 大语言模型进行智能步骤分析
- 🔄 **多算法支持**: 基础算法 + AI 增强算法
- ⚙️ **灵活配置**: 支持环境变量和代码配置
- 🛡️ **错误处理**: 完善的重试机制和降级方案
- 📊 **性能优化**: 缓存、批处理和超时控制

### 融合框架使用
融合测试框架已独立为单独的项目，位于 `fusion_framework/` 目录：

```bash
cd fusion_framework
python run_fusion_tests.py --help
```

详细使用说明请参考：[Fusion Framework README](fusion_framework/README.md)

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
├── fusion_framework/          # 独立的智能融合测试框架 🆕
│   ├── src/                   # 源代码目录
│   ├── docs/                  # 融合框架文档
│   ├── examples/              # 融合框架示例
│   ├── config/                # 融合框架配置
│   ├── run_fusion_tests.py    # 融合测试入口
│   └── README.md              # 融合框架说明
├── tests/                     # 测试用例目录
│   └── mobile/                # 移动端测试
│       ├── test_case_demo.air # 测试演示
│       └── test_case_demo_poco.air # Poco测试演示
├── docs/                      # 文档目录
│   ├── API文档.md             # API文档
│   ├── 用户手册.md            # 用户手册
│   └── 设计文档.md            # 设计文档
├── run_tests.py              # 主要测试框架入口
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

🎉 **开始你的自动化测试之旅吧！**