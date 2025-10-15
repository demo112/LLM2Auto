# Qwen API 配置指南

本指南详细说明如何配置和使用 Qwen API 进行智能步骤对齐。

## 📋 目录

- [快速开始](#快速开始)
- [配置方法](#配置方法)
- [API 参数说明](#api-参数说明)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 🚀 快速开始

### 1. 获取 API 密钥

支持以下 API 提供商：

- **SiliconFlow** (推荐)
  - 注册地址: https://siliconflow.cn
  - 模型: `Qwen/Qwen2.5-7B-Instruct`
  - 基础URL: `https://api.siliconflow.cn/v1`

- **阿里云百炼**
  - 注册地址: https://bailian.console.aliyun.com
  - 模型: `qwen-turbo` 或 `qwen-plus`
  - 基础URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`

### 2. 设置环境变量

```bash
# 必需
export QWEN_API_KEY="your_api_key_here"

# 可选 (有默认值)
export QWEN_BASE_URL="https://api.siliconflow.cn/v1"
export QWEN_MODEL="Qwen/Qwen2.5-7B-Instruct"
export QWEN_MAX_RETRIES="3"
export QWEN_TIMEOUT="30"
```

### 3. 基础使用

```python
from airtest_framework.fusion.qwen_config import get_default_config
from airtest_framework.fusion.intelligent_alignment import QwenAlignmentAssistant

# 从环境变量创建配置
config = get_default_config()

# 创建助手
assistant = QwenAlignmentAssistant(config)

# 使用助手进行步骤分析
result = await assistant.analyze_step_similarity(airtest_step, poco_step)
```

## ⚙️ 配置方法

### 方法1: 环境变量配置 (推荐)

```python
from airtest_framework.fusion.qwen_config import get_default_config

# 自动从环境变量加载
config = get_default_config()
if config:
    print("配置加载成功")
else:
    print("请设置 QWEN_API_KEY 环境变量")
```

### 方法2: 代码配置

```python
from airtest_framework.fusion.qwen_config import create_config

config = create_config(
    api_key="your_api_key_here",
    base_url="https://api.siliconflow.cn/v1",
    model="Qwen/Qwen2.5-7B-Instruct",
    max_retries=3,
    timeout=30,
    temperature=0.7,
    max_tokens=1000
)
```

### 方法3: 配置对象

```python
from airtest_framework.fusion.qwen_config import QwenConfig

config = QwenConfig(
    api_key="your_api_key_here",
    base_url="https://api.siliconflow.cn/v1",
    model="Qwen/Qwen2.5-7B-Instruct",
    max_retries=3,
    timeout=30,
    temperature=0.7,
    max_tokens=1000
)

# 验证配置
config.validate()
```

## 📊 API 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_key` | str | 必需 | API 密钥 |
| `base_url` | str | `https://api.siliconflow.cn/v1` | API 基础URL |
| `model` | str | `Qwen/Qwen2.5-7B-Instruct` | 使用的模型 |
| `max_retries` | int | 3 | 最大重试次数 |
| `timeout` | int | 30 | 请求超时时间(秒) |
| `temperature` | float | 0.7 | 生成温度 (0.0-1.0) |
| `max_tokens` | int | 1000 | 最大生成token数 |

### 模型选择建议

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| `Qwen/Qwen2.5-7B-Instruct` | 平衡性能和成本 | 一般步骤对齐 |
| `Qwen/Qwen2.5-14B-Instruct` | 更高准确性 | 复杂步骤分析 |
| `Qwen/Qwen2.5-32B-Instruct` | 最高准确性 | 关键业务场景 |

## 🛡️ 错误处理

### 常见错误类型

```python
import asyncio
from airtest_framework.fusion.intelligent_alignment import QwenAlignmentAssistant

try:
    assistant = QwenAlignmentAssistant(config)
    result = await assistant.analyze_step_similarity(step1, step2)
    
except ValueError as e:
    # 配置错误
    print(f"配置错误: {e}")
    
except asyncio.TimeoutError:
    # 请求超时
    print("API请求超时，请检查网络连接")
    
except Exception as e:
    error_msg = str(e)
    if "401" in error_msg:
        print("API密钥无效，请检查密钥设置")
    elif "429" in error_msg:
        print("API调用频率过高，请稍后重试")
    elif "403" in error_msg:
        print("API访问被拒绝，请检查权限")
    else:
        print(f"未知错误: {e}")
```

### 降级处理

```python
from airtest_framework.fusion.intelligent_alignment import align_script_pair

async def robust_alignment(airtest_steps, poco_steps):
    """带降级处理的脚本对齐"""
    try:
        # 尝试使用AI增强
        config = get_default_config()
        if config:
            return await align_script_pair(
                airtest_steps, poco_steps, qwen_config=config
            )
    except Exception as e:
        print(f"AI增强失败，使用基础算法: {e}")
    
    # 降级到基础算法
    return await align_script_pair(airtest_steps, poco_steps)
```

## 🎯 最佳实践

### 1. 配置管理

```python
# ✅ 推荐：使用环境变量
config = get_default_config()

# ❌ 不推荐：硬编码密钥
config = create_config(api_key="sk-xxx...")
```

### 2. 错误处理

```python
# ✅ 推荐：完整的错误处理
try:
    config = get_default_config()
    config.validate()
    assistant = QwenAlignmentAssistant(config)
    result = await assistant.analyze_step_similarity(step1, step2)
except Exception as e:
    # 记录错误并降级
    logger.error(f"API调用失败: {e}")
    result = fallback_similarity_analysis(step1, step2)
```

### 3. 性能优化

```python
# ✅ 推荐：批量处理
async def batch_analyze_steps(step_pairs, batch_size=5):
    """批量分析步骤相似度"""
    results = []
    for i in range(0, len(step_pairs), batch_size):
        batch = step_pairs[i:i+batch_size]
        batch_results = await asyncio.gather(*[
            assistant.analyze_step_similarity(pair[0], pair[1])
            for pair in batch
        ])
        results.extend(batch_results)
        
        # 避免频率限制
        if i + batch_size < len(step_pairs):
            await asyncio.sleep(1)
    
    return results
```

### 4. 缓存策略

```python
import hashlib
import json
from functools import lru_cache

class CachedQwenAssistant:
    def __init__(self, config):
        self.assistant = QwenAlignmentAssistant(config)
        self.cache = {}
    
    def _get_cache_key(self, step1, step2):
        """生成缓存键"""
        content = f"{step1.original_code}|{step2.original_code}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def analyze_step_similarity(self, step1, step2):
        """带缓存的相似度分析"""
        cache_key = self._get_cache_key(step1, step2)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = await self.assistant.analyze_step_similarity(step1, step2)
        self.cache[cache_key] = result
        return result
```

## 🔧 故障排除

### 问题1: API密钥无效

**症状**: 收到401错误
```
Exception: API调用失败 (状态码: 401): Invalid API key
```

**解决方案**:
1. 检查API密钥是否正确设置
2. 确认密钥没有过期
3. 验证密钥权限

```bash
# 检查环境变量
echo $QWEN_API_KEY

# 重新设置
export QWEN_API_KEY="your_correct_api_key"
```

### 问题2: 网络连接超时

**症状**: 收到超时错误
```
Exception: API调用超时 (第3次尝试)
```

**解决方案**:
1. 检查网络连接
2. 增加超时时间
3. 使用代理（如需要）

```python
config = create_config(
    api_key="your_key",
    timeout=60,  # 增加到60秒
    max_retries=5  # 增加重试次数
)
```

### 问题3: 频率限制

**症状**: 收到429错误
```
Exception: API调用失败 (状态码: 429): Rate limit exceeded
```

**解决方案**:
1. 减少并发请求
2. 增加请求间隔
3. 升级API套餐

```python
# 添加延迟
import asyncio

async def rate_limited_call():
    try:
        result = await assistant.analyze_step_similarity(step1, step2)
        return result
    except Exception as e:
        if "429" in str(e):
            await asyncio.sleep(5)  # 等待5秒后重试
            return await assistant.analyze_step_similarity(step1, step2)
        raise
```

### 问题4: 模型不支持

**症状**: 收到400或404错误
```
Exception: API调用失败 (状态码: 400): Model not found
```

**解决方案**:
1. 检查模型名称是否正确
2. 确认API提供商支持该模型
3. 使用默认模型

```python
# 使用支持的模型
supported_models = [
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-14B-Instruct",
    "qwen-turbo",
    "qwen-plus"
]

config = create_config(
    api_key="your_key",
    model=supported_models[0]  # 使用第一个支持的模型
)
```

## 📈 监控和日志

### 启用详细日志

```python
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 在API调用中添加日志
class LoggedQwenAssistant(QwenAlignmentAssistant):
    async def analyze_step_similarity(self, step1, step2):
        logger.info(f"分析步骤相似度: {step1.original_code} vs {step2.original_code}")
        try:
            result = await super().analyze_step_similarity(step1, step2)
            logger.info(f"分析完成，置信度: {result.get('confidence', 0):.2f}")
            return result
        except Exception as e:
            logger.error(f"分析失败: {e}")
            raise
```

### API使用统计

```python
class StatsQwenAssistant(QwenAlignmentAssistant):
    def __init__(self, config):
        super().__init__(config)
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0
        }
    
    async def analyze_step_similarity(self, step1, step2):
        self.stats["total_calls"] += 1
        try:
            result = await super().analyze_step_similarity(step1, step2)
            self.stats["successful_calls"] += 1
            return result
        except Exception as e:
            self.stats["failed_calls"] += 1
            raise
    
    def get_stats(self):
        """获取使用统计"""
        success_rate = (
            self.stats["successful_calls"] / self.stats["total_calls"] * 100
            if self.stats["total_calls"] > 0 else 0
        )
        return {
            **self.stats,
            "success_rate": f"{success_rate:.1f}%"
        }
```

## 📚 相关文档

- [融合测试系统概述](./融合测试技术方案.md)
- [智能对齐算法](./融合测试完整实现方案.md)
- [API示例代码](../examples/qwen_api_example.py)
- [测试用例](../test_qwen_api.py)

## 🤝 支持

如果遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查项目的 GitHub Issues
3. 运行示例代码进行测试
4. 联系技术支持

---

*最后更新: 2024年12月*