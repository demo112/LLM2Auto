# -*- encoding=utf8 -*-
"""
融合结果报告器

负责生成融合测试执行的详细报告，包括HTML和JSON格式
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import asdict

from .executor import FusionExecutionResult, StepExecutionResult, ExecutionResult


class FusionReporter:
    """融合测试报告器"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        初始化报告器
        
        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_report(self, 
                       results: List[FusionExecutionResult],
                       report_title: str = "融合测试执行报告") -> Dict[str, str]:
        """
        生成完整报告
        
        Args:
            results: 执行结果列表
            report_title: 报告标题
            
        Returns:
            Dict[str, str]: 生成的报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 生成JSON报告
        json_path = self._generate_json_report(results, timestamp)
        
        # 生成HTML报告
        html_path = self._generate_html_report(results, report_title, timestamp)
        
        return {
            'json': str(json_path),
            'html': str(html_path)
        }
    
    def _generate_json_report(self, 
                            results: List[FusionExecutionResult], 
                            timestamp: str) -> Path:
        """生成JSON格式报告"""
        try:
            summary = self._calculate_summary(results)
            serialized_results = [self._serialize_result(result) for result in results]
            
            report_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'timestamp': timestamp,
                    'total_cases': len(results),
                    'framework_version': '1.0.0'
                },
                'summary': summary,
                'results': serialized_results
            }
            
            json_path = self.output_dir / f"fusion_report_{timestamp}.json"
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            return json_path
        except Exception as e:
            print(f"JSON序列化错误详情: {e}")
            print(f"Results类型: {type(results)}")
            if results:
                print(f"第一个result类型: {type(results[0])}")
                print(f"第一个result内容: {results[0]}")
            raise
    
    def _generate_html_report(self, 
                            results: List[FusionExecutionResult],
                            title: str,
                            timestamp: str) -> Path:
        """生成HTML格式报告"""
        summary = self._calculate_summary(results)
        
        html_content = self._create_html_template(title, summary, results, timestamp)
        
        html_path = self.output_dir / f"fusion_report_{timestamp}.html"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    
    def _calculate_summary(self, results: List[FusionExecutionResult]) -> Dict[str, Any]:
        """计算执行摘要"""
        if not results:
            return {
                'total_cases': 0,
                'successful_cases': 0,
                'failed_cases': 0,
                'fallback_cases': 0,
                'total_steps': 0,
                'successful_steps': 0,
                'failed_steps': 0,
                'fallback_steps': 0,
                'total_execution_time': 0.0,
                'success_rate': 0.0,
                'fallback_rate': 0.0
            }
        
        total_cases = len(results)
        successful_cases = sum(1 for r in results if r.overall_result == ExecutionResult.SUCCESS)
        failed_cases = sum(1 for r in results if r.overall_result == ExecutionResult.FAILED)
        fallback_cases = sum(1 for r in results if r.overall_result == ExecutionResult.FALLBACK)
        
        total_steps = sum(r.total_steps for r in results)
        successful_steps = sum(r.successful_steps for r in results)
        failed_steps = sum(r.failed_steps for r in results)
        fallback_steps = sum(r.fallback_steps for r in results)
        
        total_execution_time = sum(r.total_execution_time for r in results)
        
        success_rate = (successful_cases + fallback_cases) / total_cases * 100 if total_cases > 0 else 0
        fallback_rate = fallback_steps / total_steps * 100 if total_steps > 0 else 0
        
        return {
            'total_cases': total_cases,
            'successful_cases': successful_cases,
            'failed_cases': failed_cases,
            'fallback_cases': fallback_cases,
            'total_steps': total_steps,
            'successful_steps': successful_steps,
            'failed_steps': failed_steps,
            'fallback_steps': fallback_steps,
            'total_execution_time': total_execution_time,
            'success_rate': success_rate,
            'fallback_rate': fallback_rate
        }
    
    def _serialize_result(self, result: FusionExecutionResult) -> Dict[str, Any]:
        """序列化执行结果"""
        return {
            'case_name': result.case_name,
            'total_steps': result.total_steps,
            'successful_steps': result.successful_steps,
            'failed_steps': result.failed_steps,
            'fallback_steps': result.fallback_steps,
            'total_execution_time': result.total_execution_time,
            'overall_result': result.overall_result.value,
            'step_results': [
                {
                    'step_index': step.step_index,
                    'result': step.result.value,
                    'execution_time': step.execution_time,
                    'error_message': step.error_message,
                    'used_strategy': step.used_strategy,
                    'fallback_used': step.fallback_used
                }
                for step in result.step_results
            ]
        }
    
    def _create_html_template(self, 
                            title: str,
                            summary: Dict[str, Any],
                            results: List[FusionExecutionResult],
                            timestamp: str) -> str:
        """创建HTML报告模板"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header .subtitle {{
            margin-top: 10px;
            opacity: 0.9;
        }}
        .summary {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .summary h2 {{
            margin-top: 0;
            color: #333;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .danger {{ color: #dc3545; }}
        .info {{ color: #17a2b8; }}
        
        .results {{
            padding: 30px;
        }}
        .case-result {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }}
        .case-header {{
            padding: 15px 20px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .case-header.success {{ background: #d4edda; color: #155724; }}
        .case-header.warning {{ background: #fff3cd; color: #856404; }}
        .case-header.danger {{ background: #f8d7da; color: #721c24; }}
        
        .case-details {{
            padding: 20px;
        }}
        .step-list {{
            list-style: none;
            padding: 0;
        }}
        .step-item {{
            padding: 10px;
            margin-bottom: 5px;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .step-item.success {{ background: #d4edda; }}
        .step-item.warning {{ background: #fff3cd; }}
        .step-item.danger {{ background: #f8d7da; }}
        
        .step-info {{
            display: flex;
            align-items: center;
        }}
        .step-status {{
            margin-right: 10px;
            font-weight: bold;
        }}
        .step-meta {{
            font-size: 0.9em;
            color: #666;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="subtitle">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="summary">
            <h2>执行摘要</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value info">{summary['total_cases']}</div>
                    <div class="stat-label">总用例数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value success">{summary['successful_cases']}</div>
                    <div class="stat-label">成功用例</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value warning">{summary['fallback_cases']}</div>
                    <div class="stat-label">回退用例</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value danger">{summary['failed_cases']}</div>
                    <div class="stat-label">失败用例</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value info">{summary['success_rate']:.1f}%</div>
                    <div class="stat-label">成功率</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value warning">{summary['fallback_rate']:.1f}%</div>
                    <div class="stat-label">回退率</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value info">{summary['total_execution_time']:.1f}s</div>
                    <div class="stat-label">总执行时间</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value info">{summary['total_steps']}</div>
                    <div class="stat-label">总步骤数</div>
                </div>
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: {summary['success_rate']:.1f}%"></div>
            </div>
        </div>
        
        <div class="results">
            <h2>详细结果</h2>
            {self._generate_case_results_html(results)}
        </div>
    </div>
</body>
</html>
"""
    
    def _generate_case_results_html(self, results: List[FusionExecutionResult]) -> str:
        """生成用例结果HTML"""
        html_parts = []
        
        for result in results:
            # 确定用例状态样式
            if result.overall_result == ExecutionResult.SUCCESS:
                status_class = "success"
                status_text = "✓ 成功"
            elif result.overall_result == ExecutionResult.FALLBACK:
                status_class = "warning"
                status_text = "⚠ 回退成功"
            else:
                status_class = "danger"
                status_text = "✗ 失败"
            
            # 生成步骤列表
            steps_html = []
            for step in result.step_results:
                if step.result in [ExecutionResult.SUCCESS, ExecutionResult.FALLBACK]:
                    step_class = "success" if step.result == ExecutionResult.SUCCESS else "warning"
                    step_icon = "✓" if step.result == ExecutionResult.SUCCESS else "⚠"
                else:
                    step_class = "danger"
                    step_icon = "✗"
                
                fallback_info = " (回退)" if step.fallback_used else ""
                error_info = f" - {step.error_message}" if step.error_message else ""
                
                steps_html.append(f"""
                <li class="step-item {step_class}">
                    <div class="step-info">
                        <span class="step-status">{step_icon}</span>
                        <span>步骤 {step.step_index + 1}: {step.used_strategy}{fallback_info}{error_info}</span>
                    </div>
                    <div class="step-meta">{step.execution_time:.2f}s</div>
                </li>
                """)
            
            case_html = f"""
            <div class="case-result">
                <div class="case-header {status_class}">
                    <span>{result.case_name}</span>
                    <span>{status_text} ({result.successful_steps}/{result.total_steps})</span>
                </div>
                <div class="case-details">
                    <p><strong>执行时间:</strong> {result.total_execution_time:.2f}秒</p>
                    <p><strong>成功步骤:</strong> {result.successful_steps} | 
                       <strong>失败步骤:</strong> {result.failed_steps} | 
                       <strong>回退步骤:</strong> {result.fallback_steps}</p>
                    <ul class="step-list">
                        {''.join(steps_html)}
                    </ul>
                </div>
            </div>
            """
            
            html_parts.append(case_html)
        
        return ''.join(html_parts)
    
    def print_summary(self, results: List[FusionExecutionResult]):
        """打印执行摘要到控制台"""
        summary = self._calculate_summary(results)
        
        print("\n" + "="*60)
        print("融合测试执行摘要")
        print("="*60)
        print(f"总用例数: {summary['total_cases']}")
        print(f"成功用例: {summary['successful_cases']}")
        print(f"回退用例: {summary['fallback_cases']}")
        print(f"失败用例: {summary['failed_cases']}")
        print(f"成功率: {summary['success_rate']:.1f}%")
        print(f"回退率: {summary['fallback_rate']:.1f}%")
        print(f"总执行时间: {summary['total_execution_time']:.2f}秒")
        print("="*60)
        
        for result in results:
            status = "✓" if result.overall_result == ExecutionResult.SUCCESS else \
                    "⚠" if result.overall_result == ExecutionResult.FALLBACK else "✗"
            print(f"{status} {result.case_name}: {result.successful_steps}/{result.total_steps} 步骤成功")