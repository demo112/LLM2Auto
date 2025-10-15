# -*- encoding=utf8 -*-
"""
智能步骤对齐算法

集成Qwen AI进行语义分析，实现高精度的步骤对齐
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import requests
from difflib import SequenceMatcher

from .enhanced_parser import OperationStep, OperationType
from .qwen_config import QwenConfig, get_default_config


@dataclass
class AlignmentResult:
    """对齐结果"""
    airtest_step: Optional[OperationStep] = None
    poco_step: Optional[OperationStep] = None
    alignment_confidence: float = 0.0
    semantic_similarity: float = 0.0
    syntactic_similarity: float = 0.0
    position_similarity: float = 0.0
    semantic_description: str = ""
    alignment_reason: str = ""


@dataclass
class AlignmentConfig:
    """对齐配置"""
    semantic_weight: float = 0.5      # 语义相似度权重
    syntactic_weight: float = 0.3     # 语法相似度权重
    position_weight: float = 0.2      # 位置相似度权重
    min_confidence_threshold: float = 0.6  # 最小置信度阈值
    use_ai_enhancement: bool = True   # 是否使用AI增强
    ai_batch_size: int = 5           # AI批处理大小


class QwenAlignmentAssistant:
    """Qwen AI对齐助手"""
    
    def __init__(self, config: QwenConfig = None):
        if config is None:
            config = get_default_config()
            if config is None:
                raise ValueError("未提供Qwen配置且无法从环境变量获取")
        
        config.validate()
        self.config = config
        
    async def analyze_step_similarity(self, 
                                    airtest_step: OperationStep, 
                                    poco_step: OperationStep) -> Dict[str, Any]:
        """
        分析步骤相似度
        
        Args:
            airtest_step: Airtest步骤
            poco_step: Poco步骤
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        prompt = self._build_similarity_prompt(airtest_step, poco_step)
        
        try:
            response = await self._call_qwen_api(prompt)
            return self._parse_similarity_response(response)
        except Exception as e:
            print(f"AI分析失败: {e}")
            return {
                'similarity_score': 0.5,
                'semantic_description': '自动生成的描述',
                'confidence': 0.5,
                'reasoning': 'AI分析失败，使用默认值'
            }
    
    def _build_similarity_prompt(self, airtest_step: OperationStep, poco_step: OperationStep) -> str:
        """构建相似度分析提示"""
        prompt = f"""
请分析以下两个移动应用自动化测试步骤的相似度：

Airtest步骤：
- 描述：{airtest_step.description}
- 操作类型：{airtest_step.operation_type.value}
- 目标元素：{airtest_step.target_element}
- 代码：{airtest_step.airtest_code.content if airtest_step.airtest_code else '无'}

Poco步骤：
- 描述：{poco_step.description}
- 操作类型：{poco_step.operation_type.value}
- 目标元素：{poco_step.target_element}
- 代码：{poco_step.poco_code.content if poco_step.poco_code else '无'}

请以JSON格式返回分析结果：
{{
    "similarity_score": 0.0-1.0之间的相似度分数,
    "semantic_description": "这两个步骤的语义描述",
    "confidence": 0.0-1.0之间的置信度,
    "reasoning": "相似度判断的理由",
    "operation_match": true/false是否为相同操作,
    "target_match": true/false目标元素是否匹配
}}
"""
        return prompt
    
    async def _call_qwen_api(self, prompt: str) -> Dict[str, Any]:
        """调用Qwen API，支持重试和错误处理"""
        import aiohttp
        import time
        
        headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 使用OpenAI兼容的API格式
        data = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的移动应用测试脚本分析专家，擅长分析Airtest和Poco脚本的语义相似性。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": False
        }
        
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                     async with session.post(
                         f"{self.config.base_url}/chat/completions",
                         headers=headers,
                         json=data,
                         timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            if 'choices' in result and len(result['choices']) > 0:
                                content = result['choices'][0]['message']['content']
                                return {'content': content}
                            else:
                                raise Exception(f"API响应格式错误: {result}")
                        elif response.status == 429:
                            # 速率限制，等待后重试
                            wait_time = 2 ** attempt
                            print(f"API速率限制，等待{wait_time}秒后重试...")
                            await asyncio.sleep(wait_time)
                            continue
                        elif response.status == 401:
                            raise Exception("API密钥无效或已过期")
                        elif response.status == 403:
                            raise Exception("API访问被拒绝，请检查权限")
                        else:
                            error_text = await response.text()
                            raise Exception(f"API调用失败 (状态码: {response.status}): {error_text}")
                            
            except asyncio.TimeoutError:
                last_exception = Exception(f"API调用超时 (第{attempt + 1}次尝试)")
                if attempt < self.config.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"API调用超时，等待{wait_time}秒后重试...")
                    await asyncio.sleep(wait_time)
                    continue
            except Exception as e:
                last_exception = e
                if attempt < self.config.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"API调用失败: {e}，等待{wait_time}秒后重试...")
                    await asyncio.sleep(wait_time)
                    continue
                     
        # 所有重试都失败了
        raise Exception(f"API调用失败，已重试{self.config.max_retries}次: {last_exception}")
    
    def _parse_similarity_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析相似度分析响应"""
        content = response.get('content', '')
        
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
        except json.JSONDecodeError:
            pass
        
        # 如果JSON解析失败，使用默认值
        return {
            'similarity_score': 0.5,
            'semantic_description': '语义分析',
            'confidence': 0.5,
            'reasoning': '解析失败',
            'operation_match': False,
            'target_match': False
        }
    
    async def generate_fusion_description(self, 
                                        airtest_step: OperationStep, 
                                        poco_step: OperationStep) -> str:
        """生成融合步骤描述"""
        prompt = f"""
请为以下融合的测试步骤生成一个简洁明确的描述：

Airtest实现：{airtest_step.description if airtest_step else '无'}
Poco实现：{poco_step.description if poco_step else '无'}

请生成一个统一的步骤描述，不超过50个字符。
"""
        
        try:
            response = await self._call_qwen_api(prompt)
            content = response.get('content', '').strip()
            # 取第一行作为描述
            description = content.split('\n')[0]
            return description[:50]  # 限制长度
        except Exception as e:
            # 回退到简单合并
            if airtest_step and poco_step:
                return f"融合操作: {airtest_step.operation_type.value}"
            elif airtest_step:
                return airtest_step.description
            elif poco_step:
                return poco_step.description
            else:
                return "未知操作"


class IntelligentStepAlignment:
    """智能步骤对齐器"""
    
    def __init__(self, config: AlignmentConfig = None, qwen_config: QwenConfig = None):
        self.config = config or AlignmentConfig()
        self.qwen_assistant = QwenAlignmentAssistant(qwen_config) if qwen_config else None
        
    async def align_steps(self, 
                         airtest_steps: List[OperationStep], 
                         poco_steps: List[OperationStep]) -> List[AlignmentResult]:
        """
        对齐步骤
        
        Args:
            airtest_steps: Airtest步骤列表
            poco_steps: Poco步骤列表
            
        Returns:
            List[AlignmentResult]: 对齐结果列表
        """
        print(f"开始对齐 {len(airtest_steps)} 个Airtest步骤和 {len(poco_steps)} 个Poco步骤")
        
        # 计算相似度矩阵
        similarity_matrix = await self._calculate_similarity_matrix(airtest_steps, poco_steps)
        
        # 执行对齐算法
        alignments = self._perform_alignment(airtest_steps, poco_steps, similarity_matrix)
        
        # 生成对齐结果
        results = await self._generate_alignment_results(alignments, airtest_steps, poco_steps)
        
        print(f"对齐完成，生成 {len(results)} 个对齐结果")
        return results
    
    async def _calculate_similarity_matrix(self, 
                                         airtest_steps: List[OperationStep], 
                                         poco_steps: List[OperationStep]) -> List[List[float]]:
        """计算相似度矩阵"""
        matrix = []
        
        for i, airtest_step in enumerate(airtest_steps):
            row = []
            for j, poco_step in enumerate(poco_steps):
                similarity = await self._calculate_step_similarity(airtest_step, poco_step)
                row.append(similarity)
            matrix.append(row)
            
        return matrix
    
    async def _calculate_step_similarity(self, 
                                       airtest_step: OperationStep, 
                                       poco_step: OperationStep) -> float:
        """计算两个步骤的相似度"""
        # 语法相似度
        syntactic_sim = self._calculate_syntactic_similarity(airtest_step, poco_step)
        
        # 位置相似度（基于步骤在序列中的相对位置）
        position_sim = self._calculate_position_similarity(airtest_step, poco_step)
        
        # 语义相似度
        semantic_sim = 0.5  # 默认值
        if self.qwen_assistant and self.config.use_ai_enhancement:
            try:
                ai_result = await self.qwen_assistant.analyze_step_similarity(airtest_step, poco_step)
                semantic_sim = ai_result.get('similarity_score', 0.5)
            except Exception as e:
                print(f"AI语义分析失败: {e}")
        
        # 加权计算总相似度
        total_similarity = (
            self.config.semantic_weight * semantic_sim +
            self.config.syntactic_weight * syntactic_sim +
            self.config.position_weight * position_sim
        )
        
        return min(1.0, max(0.0, total_similarity))
    
    def _calculate_syntactic_similarity(self, 
                                      airtest_step: OperationStep, 
                                      poco_step: OperationStep) -> float:
        """计算语法相似度"""
        # 操作类型匹配
        type_match = 1.0 if airtest_step.operation_type == poco_step.operation_type else 0.0
        
        # 目标元素相似度
        target_sim = SequenceMatcher(None, 
                                   airtest_step.target_element.lower(), 
                                   poco_step.target_element.lower()).ratio()
        
        # 参数相似度
        param_sim = self._calculate_parameter_similarity(
            airtest_step.parameters, 
            poco_step.parameters
        )
        
        return (type_match * 0.5 + target_sim * 0.3 + param_sim * 0.2)
    
    def _calculate_parameter_similarity(self, params1: Dict[str, Any], params2: Dict[str, Any]) -> float:
        """计算参数相似度"""
        if not params1 and not params2:
            return 1.0
        
        if not params1 or not params2:
            return 0.0
        
        # 简单的键值对比较
        common_keys = set(params1.keys()) & set(params2.keys())
        if not common_keys:
            return 0.0
        
        similarity_sum = 0.0
        for key in common_keys:
            val1, val2 = str(params1[key]), str(params2[key])
            similarity_sum += SequenceMatcher(None, val1, val2).ratio()
        
        return similarity_sum / len(common_keys)
    
    def _calculate_position_similarity(self, 
                                     airtest_step: OperationStep, 
                                     poco_step: OperationStep) -> float:
        """计算位置相似度（基于步骤ID中的序号）"""
        try:
            # 从step_id中提取序号
            airtest_num = int(airtest_step.step_id.split('_')[-1])
            poco_num = int(poco_step.step_id.split('_')[-1])
            
            # 计算位置差异的相似度
            max_diff = max(airtest_num, poco_num)
            if max_diff == 0:
                return 1.0
            
            diff = abs(airtest_num - poco_num)
            return max(0.0, 1.0 - (diff / max_diff))
        except:
            return 0.5  # 默认值
    
    def _perform_alignment(self, 
                          airtest_steps: List[OperationStep], 
                          poco_steps: List[OperationStep], 
                          similarity_matrix: List[List[float]]) -> List[Tuple[Optional[int], Optional[int], float]]:
        """执行对齐算法"""
        alignments = []
        used_airtest = set()
        used_poco = set()
        
        # 贪心算法：优先匹配相似度最高的步骤对
        while True:
            best_similarity = 0.0
            best_pair = None
            
            for i in range(len(airtest_steps)):
                if i in used_airtest:
                    continue
                for j in range(len(poco_steps)):
                    if j in used_poco:
                        continue
                    
                    similarity = similarity_matrix[i][j]
                    if similarity > best_similarity and similarity >= self.config.min_confidence_threshold:
                        best_similarity = similarity
                        best_pair = (i, j)
            
            if best_pair is None:
                break
            
            i, j = best_pair
            alignments.append((i, j, best_similarity))
            used_airtest.add(i)
            used_poco.add(j)
        
        # 添加未匹配的步骤
        for i in range(len(airtest_steps)):
            if i not in used_airtest:
                alignments.append((i, None, 0.0))
        
        for j in range(len(poco_steps)):
            if j not in used_poco:
                alignments.append((None, j, 0.0))
        
        return alignments
    
    async def _generate_alignment_results(self, 
                                        alignments: List[Tuple[Optional[int], Optional[int], float]], 
                                        airtest_steps: List[OperationStep], 
                                        poco_steps: List[OperationStep]) -> List[AlignmentResult]:
        """生成对齐结果"""
        results = []
        
        for airtest_idx, poco_idx, confidence in alignments:
            airtest_step = airtest_steps[airtest_idx] if airtest_idx is not None else None
            poco_step = poco_steps[poco_idx] if poco_idx is not None else None
            
            # 生成语义描述
            if self.qwen_assistant and airtest_step and poco_step:
                try:
                    semantic_desc = await self.qwen_assistant.generate_fusion_description(
                        airtest_step, poco_step
                    )
                except:
                    semantic_desc = self._generate_fallback_description(airtest_step, poco_step)
            else:
                semantic_desc = self._generate_fallback_description(airtest_step, poco_step)
            
            result = AlignmentResult(
                airtest_step=airtest_step,
                poco_step=poco_step,
                alignment_confidence=confidence,
                semantic_description=semantic_desc,
                alignment_reason=self._generate_alignment_reason(airtest_step, poco_step, confidence)
            )
            
            results.append(result)
        
        return results
    
    def _generate_fallback_description(self, 
                                     airtest_step: Optional[OperationStep], 
                                     poco_step: Optional[OperationStep]) -> str:
        """生成回退描述"""
        if airtest_step and poco_step:
            return f"融合操作: {airtest_step.operation_type.value}"
        elif airtest_step:
            return airtest_step.description
        elif poco_step:
            return poco_step.description
        else:
            return "未知操作"
    
    def _generate_alignment_reason(self, 
                                 airtest_step: Optional[OperationStep], 
                                 poco_step: Optional[OperationStep], 
                                 confidence: float) -> str:
        """生成对齐理由"""
        if airtest_step and poco_step:
            if confidence > 0.8:
                return "高置信度匹配：操作类型和目标元素高度相似"
            elif confidence > 0.6:
                return "中等置信度匹配：操作类型相似"
            else:
                return "低置信度匹配：可能存在差异"
        elif airtest_step:
            return "仅Airtest实现"
        elif poco_step:
            return "仅Poco实现"
        else:
            return "无效对齐"


async def align_script_pair(airtest_steps: List[OperationStep], 
                          poco_steps: List[OperationStep],
                          qwen_api_key: str = None,
                          qwen_config: QwenConfig = None) -> List[AlignmentResult]:
    """
    对齐脚本对
    
    Args:
        airtest_steps: Airtest步骤列表
        poco_steps: Poco步骤列表
        qwen_api_key: Qwen API密钥（已弃用，使用qwen_config）
        qwen_config: Qwen配置对象
        
    Returns:
        List[AlignmentResult]: 对齐结果列表
    """
    # 向后兼容性处理
    if qwen_config is None and qwen_api_key:
        from .qwen_config import create_config
        qwen_config = create_config(qwen_api_key)
    
    config = AlignmentConfig(use_ai_enhancement=bool(qwen_config))
    aligner = IntelligentStepAlignment(config, qwen_config)
    
    return await aligner.align_steps(airtest_steps, poco_steps)


if __name__ == "__main__":
    # 测试对齐算法
    from .enhanced_parser import parse_script_pair
    
    async def test_alignment():
        # 测试路径
        test_airtest = "/Users/cooperd/UNV/TraeProject/演示项目/tests/mobile/test_case_demo_airtest.air/test_case_demo_airtest.py"
        test_poco = "/Users/cooperd/UNV/TraeProject/演示项目/tests/mobile/test_case_demo_poco.air/test_case_demo_poco.py"
        
        try:
            # 解析脚本
            airtest_steps, poco_steps = parse_script_pair(test_airtest, test_poco)
            
            # 对齐步骤
            api_key = "sk-oxvaaywyniqwdriydwxeikmnetpdzgcfuvxjysbuyxrqckab"
            results = await align_script_pair(airtest_steps, poco_steps, api_key)
            
            print(f"对齐结果数量: {len(results)}")
            for i, result in enumerate(results):
                print(f"\n对齐 {i+1}:")
                print(f"  描述: {result.semantic_description}")
                print(f"  置信度: {result.alignment_confidence:.2f}")
                print(f"  理由: {result.alignment_reason}")
                if result.airtest_step:
                    print(f"  Airtest: {result.airtest_step.description}")
                if result.poco_step:
                    print(f"  Poco: {result.poco_step.description}")
                    
        except Exception as e:
            print(f"测试失败: {e}")
    
    # 运行测试
    asyncio.run(test_alignment())