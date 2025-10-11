# -*- encoding=utf8 -*-
"""
测试报告生成器 - 负责生成各种格式的测试报告
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import asdict

from .executor import TestResult


class TestReporter:
    """测试报告生成器"""
    
    def __init__(self, config_manager=None):
        """
        初始化报告生成器
        
        Args:
            config_manager: 配置管理器
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
    def generate_report(self, results: List[TestResult], 
                       output_dir: str = "reports",
                       format: str = "html") -> str:
        """
        生成测试报告
        
        Args:
            results: 测试结果列表
            output_dir: 输出目录
            format: 报告格式 (html, json, xml)
            
        Returns:
            str: 报告文件路径
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成报告数据
        report_data = self._generate_report_data(results)
        
        # 根据格式生成报告
        if format.lower() == "html":
            return self._generate_html_report(report_data, output_dir)
        elif format.lower() == "json":
            return self._generate_json_report(report_data, output_dir)
        elif format.lower() == "xml":
            return self._generate_xml_report(report_data, output_dir)
        else:
            raise ValueError(f"不支持的报告格式: {format}")
    
    def _generate_report_data(self, results: List[TestResult]) -> Dict[str, Any]:
        """生成报告数据"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r.duration for r in results)
        
        # 统计信息
        summary = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "average_duration": total_duration / total_tests if total_tests > 0 else 0
        }
        
        # 分类统计
        categories = {}
        for result in results:
            # 从测试路径提取分类
            category = self._extract_category(result.test_path)
            if category not in categories:
                categories[category] = {"total": 0, "passed": 0, "failed": 0}
            
            categories[category]["total"] += 1
            if result.success:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        # 设备统计
        devices = {}
        for result in results:
            device_info = result.device_info
            device_key = device_info.get('model', 'unknown') if device_info else 'unknown'
            if device_key not in devices:
                devices[device_key] = {"total": 0, "passed": 0, "failed": 0}
            
            devices[device_key]["total"] += 1
            if result.success:
                devices[device_key]["passed"] += 1
            else:
                devices[device_key]["failed"] += 1
        
        return {
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "categories": categories,
            "devices": devices,
            "results": [asdict(result) for result in results]
        }
    
    def _extract_category(self, test_path: str) -> str:
        """从测试路径提取分类"""
        path_parts = Path(test_path).parts
        
        # 查找分类关键词
        category_keywords = ["mobile", "web", "api", "ui", "unit", "integration"]
        
        for part in path_parts:
            part_lower = part.lower()
            for keyword in category_keywords:
                if keyword in part_lower:
                    return keyword
        
        # 默认分类
        if "test" in str(test_path).lower():
            return "test"
        
        return "other"
    
    def _generate_html_report(self, report_data: Dict[str, Any], output_dir: str) -> str:
        """生成HTML报告"""
        report_file = os.path.join(output_dir, f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        
        html_content = self._create_html_template(report_data)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 复制静态资源
        self._copy_static_resources(output_dir)
        
        self.logger.info(f"HTML报告生成成功: {report_file}")
        return report_file
    
    def _create_html_template(self, data: Dict[str, Any]) -> str:
        """创建HTML模板"""
        summary = data["summary"]
        results = data["results"]
        
        # 生成测试结果表格
        results_html = ""
        for result in results:
            status_class = "success" if result["success"] else "danger"
            status_text = "通过" if result["success"] else "失败"
            
            # 处理截图
            screenshots_html = ""
            if result.get("screenshots"):
                for screenshot in result["screenshots"][:3]:  # 最多显示3张截图
                    screenshots_html += f'<img src="{screenshot}" class="screenshot-thumb" onclick="showScreenshot(\'{screenshot}\')">'
            
            # 错误信息
            error_html = ""
            if result.get("error_message"):
                error_html = f'<div class="error-message">{result["error_message"]}</div>'
            
            results_html += f"""
            <tr class="{status_class}">
                <td>{result["test_name"]}</td>
                <td><span class="badge badge-{status_class}">{status_text}</span></td>
                <td>{result["duration"]:.2f}s</td>
                <td>{result["start_time"]}</td>
                <td>
                    {screenshots_html}
                    {error_html}
                </td>
            </tr>
            """
        
        # 生成分类统计图表
        categories_data = json.dumps(data["categories"])
        
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Airtest 自动化测试报告</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .stat-card.success {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }}
        .stat-card.danger {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
        }}
        .screenshot-thumb {{
            width: 50px;
            height: 50px;
            object-fit: cover;
            margin: 2px;
            cursor: pointer;
            border-radius: 5px;
        }}
        .error-message {{
            color: #dc3545;
            font-size: 0.8em;
            margin-top: 5px;
        }}
        .chart-container {{
            position: relative;
            height: 300px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <div class="summary-card">
                    <h1 class="text-center">Airtest 自动化测试报告</h1>
                    <p class="text-center">生成时间: {data["generated_at"]}</p>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-3">
                <div class="stat-card">
                    <h3>{summary["total"]}</h3>
                    <p>总测试数</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card success">
                    <h3>{summary["passed"]}</h3>
                    <p>通过测试</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card danger">
                    <h3>{summary["failed"]}</h3>
                    <p>失败测试</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <h3>{summary["pass_rate"]:.1f}%</h3>
                    <p>通过率</p>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>测试结果分布</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="resultChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>分类统计</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="categoryChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>测试详情</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>测试名称</th>
                                        <th>状态</th>
                                        <th>耗时</th>
                                        <th>开始时间</th>
                                        <th>详情</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {results_html}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 截图模态框 -->
    <div class="modal fade" id="screenshotModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">截图详情</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body text-center">
                    <img id="screenshotImage" src="" class="img-fluid">
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 结果分布图表
        const resultCtx = document.getElementById('resultChart').getContext('2d');
        new Chart(resultCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['通过', '失败'],
                datasets: [{{
                    data: [{summary["passed"]}, {summary["failed"]}],
                    backgroundColor: ['#28a745', '#dc3545']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});
        
        // 分类统计图表
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        const categoryData = {categories_data};
        const categoryLabels = Object.keys(categoryData);
        const categoryValues = categoryLabels.map(label => categoryData[label].total);
        
        new Chart(categoryCtx, {{
            type: 'bar',
            data: {{
                labels: categoryLabels,
                datasets: [{{
                    label: '测试数量',
                    data: categoryValues,
                    backgroundColor: '#007bff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});
        
        // 截图显示
        function showScreenshot(src) {{
            document.getElementById('screenshotImage').src = src;
            new bootstrap.Modal(document.getElementById('screenshotModal')).show();
        }}
    </script>
</body>
</html>
        """
        
        return html_template
    
    def _generate_json_report(self, report_data: Dict[str, Any], output_dir: str) -> str:
        """生成JSON报告"""
        report_file = os.path.join(output_dir, f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"JSON报告生成成功: {report_file}")
        return report_file
    
    def _generate_xml_report(self, report_data: Dict[str, Any], output_dir: str) -> str:
        """生成XML报告（JUnit格式）"""
        report_file = os.path.join(output_dir, f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml")
        
        summary = report_data["summary"]
        results = report_data["results"]
        
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Airtest自动化测试" 
           tests="{summary['total']}" 
           failures="{summary['failed']}" 
           time="{summary['total_duration']:.2f}">
"""
        
        for result in results:
            xml_content += f"""    <testcase name="{result['test_name']}" 
                     classname="{self._extract_category(result['test_path'])}" 
                     time="{result['duration']:.2f}">
"""
            
            if not result["success"]:
                error_message = result.get("error_message", "测试失败")
                xml_content += f"""        <failure message="{error_message}">
            <![CDATA[{error_message}]]>
        </failure>
"""
            
            xml_content += "    </testcase>\n"
        
        xml_content += "</testsuite>"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        self.logger.info(f"XML报告生成成功: {report_file}")
        return report_file
    
    def _copy_static_resources(self, output_dir: str):
        """复制静态资源"""
        # 这里可以复制CSS、JS等静态文件
        # 目前使用CDN，所以不需要复制
        pass
    
    def generate_summary_report(self, results: List[TestResult]) -> Dict[str, Any]:
        """生成摘要报告"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r.duration for r in results)
        
        # 失败测试详情
        failed_details = []
        for result in results:
            if not result.success:
                failed_details.append({
                    "name": result.test_name,
                    "error": result.error_message,
                    "duration": result.duration
                })
        
        # 最慢的测试
        slowest_tests = sorted(results, key=lambda r: r.duration, reverse=True)[:5]
        
        return {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration,
                "average_duration": total_duration / total_tests if total_tests > 0 else 0
            },
            "failed_tests": failed_details,
            "slowest_tests": [
                {
                    "name": test.test_name,
                    "duration": test.duration,
                    "success": test.success
                }
                for test in slowest_tests
            ]
        }
    
    def send_notification(self, results: List[TestResult], webhook_url: Optional[str] = None):
        """发送测试结果通知"""
        if not webhook_url:
            return
        
        try:
            import requests
            
            summary = self.generate_summary_report(results)
            
            # 构建通知消息
            message = f"""
📊 Airtest 自动化测试报告

✅ 通过: {summary['summary']['passed']}
❌ 失败: {summary['summary']['failed']}
📈 通过率: {summary['summary']['pass_rate']:.1f}%
⏱️ 总耗时: {summary['summary']['total_duration']:.2f}s

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            # 发送到webhook
            payload = {
                "text": message,
                "summary": summary
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info("测试结果通知发送成功")
            
        except Exception as e:
            self.logger.error(f"测试结果通知发送失败: {e}")


class ReportAnalyzer:
    """报告分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_trends(self, report_files: List[str]) -> Dict[str, Any]:
        """分析测试趋势"""
        trends = {
            "dates": [],
            "pass_rates": [],
            "total_tests": [],
            "durations": []
        }
        
        for report_file in report_files:
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                summary = data.get("summary", {})
                trends["dates"].append(data.get("generated_at", ""))
                trends["pass_rates"].append(summary.get("pass_rate", 0))
                trends["total_tests"].append(summary.get("total", 0))
                trends["durations"].append(summary.get("total_duration", 0))
                
            except Exception as e:
                self.logger.warning(f"分析报告文件失败: {report_file} - {e}")
        
        return trends
    
    def find_flaky_tests(self, report_files: List[str]) -> List[Dict[str, Any]]:
        """查找不稳定的测试"""
        test_results = {}
        
        for report_file in report_files:
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for result in data.get("results", []):
                    test_name = result["test_name"]
                    if test_name not in test_results:
                        test_results[test_name] = {"total": 0, "passed": 0}
                    
                    test_results[test_name]["total"] += 1
                    if result["success"]:
                        test_results[test_name]["passed"] += 1
                        
            except Exception as e:
                self.logger.warning(f"分析报告文件失败: {report_file} - {e}")
        
        # 找出不稳定的测试（通过率在20%-80%之间）
        flaky_tests = []
        for test_name, stats in test_results.items():
            if stats["total"] >= 3:  # 至少执行3次
                pass_rate = stats["passed"] / stats["total"] * 100
                if 20 <= pass_rate <= 80:
                    flaky_tests.append({
                        "name": test_name,
                        "pass_rate": pass_rate,
                        "total_runs": stats["total"],
                        "passed_runs": stats["passed"]
                    })
        
        return sorted(flaky_tests, key=lambda x: abs(x["pass_rate"] - 50))