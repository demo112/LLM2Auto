# Fusion Framework - 智能融合测试框架

## 项目简介

Fusion Framework 是一个专门用于Airtest和Poco脚本智能融合的测试框架，集成了Qwen API进行智能对齐和执行。该框架能够自动发现、解析、对齐和执行测试脚本，提供强大的故障转移机制和详细的测试报告。

## 主要特性

### 🚀 智能测试发现
- 自动扫描和发现Airtest/Poco测试脚本
- 支持多种文件格式和目录结构
- 智能过滤和分类测试用例

### 🧠 智能脚本对齐
- 集成Qwen API进行智能脚本对齐
- 自动分析脚本语义和功能
- 生成融合后的优化脚本

### ⚡ 强大的执行引擎
- 支持多种执行策略
- 智能故障转移机制
- 并行执行支持

### 📊 丰富的报告功能
- HTML格式的详细测试报告
- JSON格式的结构化数据
- 实时执行状态监控

## 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd fusion_framework

# 安装依赖
pip install -r requirements.txt

# 或者使用setup.py安装
pip install -e .
```

### 基本使用

#### 1. 查看帮助信息
```bash
python run_fusion_tests.py --help
```

#### 2. 运行所有融合测试
```bash
python run_fusion_tests.py
```

#### 3. 使用关键词过滤测试
```bash
python run_fusion_tests.py --filter "登录"
```

#### 4. 调试模式运行
```bash
python run_fusion_tests.py --debug
```

#### 5. 使用自定义配置
```bash
python run_fusion_tests.py --config config/custom_config.json
```

## 项目结构

```
fusion_framework/
├── src/
│   └── fusion_framework/
│       ├── __init__.py              # 主模块入口
│       ├── core/                    # 核心功能模块
│       │   ├── main.py             # 主框架类
│       │   ├── config.py           # 配置管理
│       │   ├── discovery.py        # 测试发现
│       │   ├── enhanced_parser.py  # 脚本解析
│       │   ├── intelligent_alignment.py  # 智能对齐
│       │   ├── persistence.py      # 数据持久化
│       │   ├── failover_executor.py # 故障转移执行器
│       │   ├── reporter.py         # 报告生成
│       │   └── qwen_config.py      # Qwen API配置
│       └── utils/                   # 工具模块
├── docs/                           # 文档目录
│   ├── README_融合测试系统.md       # 系统说明文档
│   ├── Qwen_API_配置指南.md        # API配置指南
│   └── 融合测试*.md                # 其他相关文档
├── examples/                       # 示例代码
│   └── qwen_api_example.py         # API使用示例
├── scripts/                        # 脚本目录
│   └── fusion_scripts/             # 融合脚本
├── tests/                          # 测试目录
├── config/                         # 配置目录
│   └── fusion_config.json          # 默认配置文件
├── run_fusion_tests.py             # 主执行脚本
├── setup.py                        # 安装配置
├── requirements.txt                # 依赖列表
└── README.md                       # 项目说明
```

## 配置管理

### 配置文件结构

配置文件采用JSON格式，主要包含以下部分：

```json
{
  "qwen_api": {
    "api_key": "your-api-key",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-turbo"
  },
  "test_discovery": {
    "test_root": "./tests",
    "include_patterns": ["*.air", "*.py"],
    "exclude_patterns": ["__pycache__", "*.pyc"]
  },
  "execution": {
    "strategy": "failover",
    "timeout": 300,
    "retry_count": 3
  },
  "reporting": {
    "output_dir": "./reports",
    "formats": ["html", "json"]
  }
}
```

### 环境变量支持

框架支持通过环境变量配置敏感信息：

```bash
export QWEN_API_KEY="your-api-key"
export FUSION_CONFIG_PATH="/path/to/config.json"
```

## 高级功能

### 自定义执行策略

```python
from fusion_framework import ExecutionStrategy, FailoverExecutor

# 创建自定义执行策略
strategy = ExecutionStrategy.PARALLEL
executor = FailoverExecutor(strategy=strategy)
```

### 自定义报告格式

```python
from fusion_framework import FusionReporter

# 创建自定义报告器
reporter = FusionReporter(
    output_dir="./custom_reports",
    formats=["html", "json", "xml"]
)
```

## 故障排除

### 常见问题

1. **API密钥配置错误**
   - 检查配置文件中的API密钥是否正确
   - 确认环境变量设置是否生效

2. **测试脚本发现失败**
   - 检查测试根目录路径是否正确
   - 确认包含/排除模式是否合适

3. **执行超时**
   - 调整配置文件中的超时设置
   - 检查网络连接和设备状态

### 日志调试

启用调试模式获取详细日志：

```bash
python run_fusion_tests.py --debug --log-level DEBUG
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如果您遇到问题或有建议，请：

1. 查看[文档](docs/)
2. 搜索[已知问题](issues)
3. 创建新的[Issue](issues/new)

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的融合测试功能
- 集成Qwen API智能对齐
- 提供HTML和JSON报告格式