# -*- encoding=utf8 -*-
"""
可视化工具

提供图表生成、数据可视化和导出功能
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
import json
import base64
from io import BytesIO
import colorsys


class ChartType(Enum):
    """图表类型"""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    AREA = "area"
    HISTOGRAM = "histogram"
    BOX = "box"
    HEATMAP = "heatmap"
    RADAR = "radar"
    TREEMAP = "treemap"


class ColorScheme(Enum):
    """颜色方案"""
    DEFAULT = "default"
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    PURPLE = "purple"
    ORANGE = "orange"
    RAINBOW = "rainbow"
    PASTEL = "pastel"
    DARK = "dark"
    MONOCHROME = "monochrome"


class ExportFormat(Enum):
    """导出格式"""
    SVG = "svg"
    PNG = "png"
    PDF = "pdf"
    HTML = "html"
    JSON = "json"


@dataclass
class ChartStyle:
    """图表样式"""
    width: int = 800
    height: int = 600
    background_color: str = "#ffffff"
    font_family: str = "Arial, sans-serif"
    font_size: int = 12
    title_font_size: int = 16
    color_scheme: ColorScheme = ColorScheme.DEFAULT
    show_grid: bool = True
    show_legend: bool = True
    show_tooltip: bool = True
    animation: bool = True


@dataclass
class ChartData:
    """图表数据"""
    labels: List[str] = field(default_factory=list)
    datasets: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Chart:
    """图表"""
    type: ChartType
    title: str
    data: ChartData
    style: ChartStyle = field(default_factory=ChartStyle)
    options: Dict[str, Any] = field(default_factory=dict)
    svg_content: Optional[str] = None
    html_content: Optional[str] = None


class VisualizationUtils:
    """可视化工具"""
    
    def __init__(self):
        self.color_palettes = self._initialize_color_palettes()
        self.chart_templates = self._initialize_chart_templates()
    
    def _initialize_color_palettes(self) -> Dict[ColorScheme, List[str]]:
        """初始化颜色调色板"""
        
        return {
            ColorScheme.DEFAULT: [
                "#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
                "#1abc9c", "#34495e", "#e67e22", "#95a5a6", "#f1c40f"
            ],
            ColorScheme.BLUE: [
                "#e3f2fd", "#bbdefb", "#90caf9", "#64b5f6", "#42a5f5",
                "#2196f3", "#1e88e5", "#1976d2", "#1565c0", "#0d47a1"
            ],
            ColorScheme.GREEN: [
                "#e8f5e8", "#c8e6c9", "#a5d6a7", "#81c784", "#66bb6a",
                "#4caf50", "#43a047", "#388e3c", "#2e7d32", "#1b5e20"
            ],
            ColorScheme.RED: [
                "#ffebee", "#ffcdd2", "#ef9a9a", "#e57373", "#ef5350",
                "#f44336", "#e53935", "#d32f2f", "#c62828", "#b71c1c"
            ],
            ColorScheme.PURPLE: [
                "#f3e5f5", "#e1bee7", "#ce93d8", "#ba68c8", "#ab47bc",
                "#9c27b0", "#8e24aa", "#7b1fa2", "#6a1b9a", "#4a148c"
            ],
            ColorScheme.ORANGE: [
                "#fff3e0", "#ffe0b2", "#ffcc80", "#ffb74d", "#ffa726",
                "#ff9800", "#fb8c00", "#f57c00", "#ef6c00", "#e65100"
            ],
            ColorScheme.RAINBOW: [
                "#ff0000", "#ff8000", "#ffff00", "#80ff00", "#00ff00",
                "#00ff80", "#00ffff", "#0080ff", "#0000ff", "#8000ff"
            ],
            ColorScheme.PASTEL: [
                "#ffb3ba", "#ffdfba", "#ffffba", "#baffc9", "#bae1ff",
                "#c9baff", "#ffbaff", "#ffbac9", "#c9ffba", "#baffff"
            ],
            ColorScheme.DARK: [
                "#2c3e50", "#34495e", "#7f8c8d", "#95a5a6", "#bdc3c7",
                "#ecf0f1", "#f39c12", "#e67e22", "#e74c3c", "#c0392b"
            ],
            ColorScheme.MONOCHROME: [
                "#000000", "#1a1a1a", "#333333", "#4d4d4d", "#666666",
                "#808080", "#999999", "#b3b3b3", "#cccccc", "#e6e6e6"
            ]
        }
    
    def _initialize_chart_templates(self) -> Dict[ChartType, Dict[str, Any]]:
        """初始化图表模板"""
        
        return {
            ChartType.LINE: {
                "stroke_width": 2,
                "fill": "none",
                "marker_size": 4,
                "smooth": True
            },
            ChartType.BAR: {
                "bar_width": 0.8,
                "spacing": 0.1,
                "orientation": "vertical"
            },
            ChartType.SCATTER: {
                "marker_size": 6,
                "marker_opacity": 0.7
            },
            ChartType.PIE: {
                "start_angle": 0,
                "inner_radius": 0,
                "show_labels": True,
                "label_distance": 1.1
            },
            ChartType.AREA: {
                "fill_opacity": 0.6,
                "stroke_width": 1,
                "stacked": False
            },
            ChartType.HISTOGRAM: {
                "bins": 20,
                "density": False,
                "cumulative": False
            },
            ChartType.HEATMAP: {
                "color_scale": "viridis",
                "show_values": True,
                "value_format": ".2f"
            },
            ChartType.RADAR: {
                "fill_opacity": 0.3,
                "stroke_width": 2,
                "point_size": 4
            }
        }
    
    def create_line_chart(
        self,
        data: Dict[str, List[Union[int, float]]],
        title: str = "折线图",
        x_label: str = "X轴",
        y_label: str = "Y轴",
        style: Optional[ChartStyle] = None
    ) -> Chart:
        """创建折线图"""
        
        if style is None:
            style = ChartStyle()
        
        # 准备数据
        chart_data = ChartData()
        
        # 获取所有x值（假设第一个数据集的索引作为x轴）
        first_key = list(data.keys())[0]
        chart_data.labels = [str(i) for i in range(len(data[first_key]))]
        
        # 准备数据集
        colors = self.color_palettes[style.color_scheme]
        for i, (label, values) in enumerate(data.items()):
            dataset = {
                "label": label,
                "data": values,
                "color": colors[i % len(colors)],
                "type": "line"
            }
            chart_data.datasets.append(dataset)
        
        # 创建图表
        chart = Chart(
            type=ChartType.LINE,
            title=title,
            data=chart_data,
            style=style,
            options={
                "x_label": x_label,
                "y_label": y_label,
                **self.chart_templates[ChartType.LINE]
            }
        )
        
        # 生成SVG
        chart.svg_content = self._generate_line_chart_svg(chart)
        chart.html_content = self._wrap_svg_in_html(chart.svg_content, chart.title)
        
        return chart
    
    def create_bar_chart(
        self,
        data: Dict[str, Union[List[Union[int, float]], Union[int, float]]],
        title: str = "柱状图",
        x_label: str = "类别",
        y_label: str = "数值",
        style: Optional[ChartStyle] = None
    ) -> Chart:
        """创建柱状图"""
        
        if style is None:
            style = ChartStyle()
        
        # 准备数据
        chart_data = ChartData()
        
        # 如果数据是简单的键值对，转换为列表格式
        if all(isinstance(v, (int, float)) for v in data.values()):
            chart_data.labels = list(data.keys())
            colors = self.color_palettes[style.color_scheme]
            dataset = {
                "label": "数据",
                "data": list(data.values()),
                "colors": [colors[i % len(colors)] for i in range(len(data))],
                "type": "bar"
            }
            chart_data.datasets.append(dataset)
        else:
            # 多系列数据
            chart_data.labels = list(data.keys())
            colors = self.color_palettes[style.color_scheme]
            for i, (label, values) in enumerate(data.items()):
                if isinstance(values, list):
                    dataset = {
                        "label": label,
                        "data": values,
                        "color": colors[i % len(colors)],
                        "type": "bar"
                    }
                    chart_data.datasets.append(dataset)
        
        # 创建图表
        chart = Chart(
            type=ChartType.BAR,
            title=title,
            data=chart_data,
            style=style,
            options={
                "x_label": x_label,
                "y_label": y_label,
                **self.chart_templates[ChartType.BAR]
            }
        )
        
        # 生成SVG
        chart.svg_content = self._generate_bar_chart_svg(chart)
        chart.html_content = self._wrap_svg_in_html(chart.svg_content, chart.title)
        
        return chart
    
    def create_pie_chart(
        self,
        data: Dict[str, Union[int, float]],
        title: str = "饼图",
        style: Optional[ChartStyle] = None
    ) -> Chart:
        """创建饼图"""
        
        if style is None:
            style = ChartStyle()
        
        # 准备数据
        chart_data = ChartData()
        chart_data.labels = list(data.keys())
        
        colors = self.color_palettes[style.color_scheme]
        dataset = {
            "label": "数据",
            "data": list(data.values()),
            "colors": [colors[i % len(colors)] for i in range(len(data))],
            "type": "pie"
        }
        chart_data.datasets.append(dataset)
        
        # 创建图表
        chart = Chart(
            type=ChartType.PIE,
            title=title,
            data=chart_data,
            style=style,
            options=self.chart_templates[ChartType.PIE]
        )
        
        # 生成SVG
        chart.svg_content = self._generate_pie_chart_svg(chart)
        chart.html_content = self._wrap_svg_in_html(chart.svg_content, chart.title)
        
        return chart
    
    def create_scatter_plot(
        self,
        x_data: List[Union[int, float]],
        y_data: List[Union[int, float]],
        title: str = "散点图",
        x_label: str = "X轴",
        y_label: str = "Y轴",
        labels: Optional[List[str]] = None,
        style: Optional[ChartStyle] = None
    ) -> Chart:
        """创建散点图"""
        
        if style is None:
            style = ChartStyle()
        
        if len(x_data) != len(y_data):
            raise ValueError("x_data 和 y_data 长度必须相同")
        
        # 准备数据
        chart_data = ChartData()
        chart_data.labels = labels or [f"点{i+1}" for i in range(len(x_data))]
        
        colors = self.color_palettes[style.color_scheme]
        dataset = {
            "label": "数据点",
            "x_data": x_data,
            "y_data": y_data,
            "color": colors[0],
            "type": "scatter"
        }
        chart_data.datasets.append(dataset)
        
        # 创建图表
        chart = Chart(
            type=ChartType.SCATTER,
            title=title,
            data=chart_data,
            style=style,
            options={
                "x_label": x_label,
                "y_label": y_label,
                **self.chart_templates[ChartType.SCATTER]
            }
        )
        
        # 生成SVG
        chart.svg_content = self._generate_scatter_plot_svg(chart)
        chart.html_content = self._wrap_svg_in_html(chart.svg_content, chart.title)
        
        return chart
    
    def create_heatmap(
        self,
        data: List[List[Union[int, float]]],
        x_labels: List[str],
        y_labels: List[str],
        title: str = "热力图",
        style: Optional[ChartStyle] = None
    ) -> Chart:
        """创建热力图"""
        
        if style is None:
            style = ChartStyle()
        
        # 准备数据
        chart_data = ChartData()
        chart_data.labels = x_labels
        
        dataset = {
            "label": "热力图数据",
            "data": data,
            "x_labels": x_labels,
            "y_labels": y_labels,
            "type": "heatmap"
        }
        chart_data.datasets.append(dataset)
        
        # 创建图表
        chart = Chart(
            type=ChartType.HEATMAP,
            title=title,
            data=chart_data,
            style=style,
            options=self.chart_templates[ChartType.HEATMAP]
        )
        
        # 生成SVG
        chart.svg_content = self._generate_heatmap_svg(chart)
        chart.html_content = self._wrap_svg_in_html(chart.svg_content, chart.title)
        
        return chart
    
    def _generate_line_chart_svg(self, chart: Chart) -> str:
        """生成折线图SVG"""
        
        width = chart.style.width
        height = chart.style.height
        margin = 60
        plot_width = width - 2 * margin
        plot_height = height - 2 * margin
        
        # 计算数据范围
        all_values = []
        for dataset in chart.data.datasets:
            all_values.extend(dataset["data"])
        
        min_y = min(all_values) if all_values else 0
        max_y = max(all_values) if all_values else 1
        y_range = max_y - min_y if max_y != min_y else 1
        
        # 开始构建SVG
        svg_parts = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{width}" height="{height}" fill="{chart.style.background_color}"/>',
            f'<style>',
            f'.chart-title {{ font-family: {chart.style.font_family}; font-size: {chart.style.title_font_size}px; text-anchor: middle; }}',
            f'.axis-label {{ font-family: {chart.style.font_family}; font-size: {chart.style.font_size}px; text-anchor: middle; }}',
            f'.grid-line {{ stroke: #e0e0e0; stroke-width: 1; }}',
            f'</style>'
        ]
        
        # 标题
        svg_parts.append(f'<text x="{width/2}" y="30" class="chart-title">{chart.title}</text>')
        
        # 网格线
        if chart.style.show_grid:
            # 垂直网格线
            for i in range(len(chart.data.labels) + 1):
                x = margin + i * plot_width / len(chart.data.labels)
                svg_parts.append(f'<line x1="{x}" y1="{margin}" x2="{x}" y2="{height-margin}" class="grid-line"/>')
            
            # 水平网格线
            for i in range(6):
                y = margin + i * plot_height / 5
                svg_parts.append(f'<line x1="{margin}" y1="{y}" x2="{width-margin}" y2="{y}" class="grid-line"/>')
        
        # 坐标轴
        svg_parts.append(f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="black" stroke-width="2"/>')
        svg_parts.append(f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="black" stroke-width="2"/>')
        
        # 绘制数据线
        for dataset in chart.data.datasets:
            points = []
            for i, value in enumerate(dataset["data"]):
                x = margin + (i + 0.5) * plot_width / len(chart.data.labels)
                y = height - margin - (value - min_y) / y_range * plot_height
                points.append(f"{x},{y}")
            
            if points:
                path = f'M {" L ".join(points)}'
                svg_parts.append(f'<path d="{path}" stroke="{dataset["color"]}" stroke-width="2" fill="none"/>')
                
                # 数据点
                for i, value in enumerate(dataset["data"]):
                    x = margin + (i + 0.5) * plot_width / len(chart.data.labels)
                    y = height - margin - (value - min_y) / y_range * plot_height
                    svg_parts.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{dataset["color"]}"/>')
        
        # X轴标签
        for i, label in enumerate(chart.data.labels):
            x = margin + (i + 0.5) * plot_width / len(chart.data.labels)
            svg_parts.append(f'<text x="{x}" y="{height-margin+20}" class="axis-label">{label}</text>')
        
        # Y轴标签
        for i in range(6):
            y = margin + i * plot_height / 5
            value = max_y - i * y_range / 5
            svg_parts.append(f'<text x="{margin-10}" y="{y+5}" class="axis-label" text-anchor="end">{value:.1f}</text>')
        
        # 轴标题
        svg_parts.append(f'<text x="{width/2}" y="{height-10}" class="axis-label">{chart.options.get("x_label", "")}</text>')
        svg_parts.append(f'<text x="20" y="{height/2}" class="axis-label" transform="rotate(-90, 20, {height/2})">{chart.options.get("y_label", "")}</text>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def _generate_bar_chart_svg(self, chart: Chart) -> str:
        """生成柱状图SVG"""
        
        width = chart.style.width
        height = chart.style.height
        margin = 60
        plot_width = width - 2 * margin
        plot_height = height - 2 * margin
        
        # 计算数据范围
        all_values = []
        for dataset in chart.data.datasets:
            if isinstance(dataset["data"], list):
                all_values.extend(dataset["data"])
            else:
                all_values.append(dataset["data"])
        
        max_y = max(all_values) if all_values else 1
        
        # 开始构建SVG
        svg_parts = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{width}" height="{height}" fill="{chart.style.background_color}"/>',
            f'<style>',
            f'.chart-title {{ font-family: {chart.style.font_family}; font-size: {chart.style.title_font_size}px; text-anchor: middle; }}',
            f'.axis-label {{ font-family: {chart.style.font_family}; font-size: {chart.style.font_size}px; text-anchor: middle; }}',
            f'.grid-line {{ stroke: #e0e0e0; stroke-width: 1; }}',
            f'</style>'
        ]
        
        # 标题
        svg_parts.append(f'<text x="{width/2}" y="30" class="chart-title">{chart.title}</text>')
        
        # 网格线
        if chart.style.show_grid:
            for i in range(6):
                y = margin + i * plot_height / 5
                svg_parts.append(f'<line x1="{margin}" y1="{y}" x2="{width-margin}" y2="{y}" class="grid-line"/>')
        
        # 坐标轴
        svg_parts.append(f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="black" stroke-width="2"/>')
        svg_parts.append(f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="black" stroke-width="2"/>')
        
        # 绘制柱子
        bar_width = plot_width / len(chart.data.labels) * 0.8
        
        for dataset in chart.data.datasets:
            for i, value in enumerate(dataset["data"]):
                x = margin + i * plot_width / len(chart.data.labels) + (plot_width / len(chart.data.labels) - bar_width) / 2
                bar_height = value / max_y * plot_height
                y = height - margin - bar_height
                
                color = dataset.get("colors", [dataset.get("color", "#3498db")])[i % len(dataset.get("colors", [dataset.get("color", "#3498db")]))]
                
                svg_parts.append(f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{color}"/>')
                
                # 数值标签
                svg_parts.append(f'<text x="{x + bar_width/2}" y="{y-5}" class="axis-label">{value}</text>')
        
        # X轴标签
        for i, label in enumerate(chart.data.labels):
            x = margin + (i + 0.5) * plot_width / len(chart.data.labels)
            svg_parts.append(f'<text x="{x}" y="{height-margin+20}" class="axis-label">{label}</text>')
        
        # Y轴标签
        for i in range(6):
            y = margin + i * plot_height / 5
            value = max_y - i * max_y / 5
            svg_parts.append(f'<text x="{margin-10}" y="{y+5}" class="axis-label" text-anchor="end">{value:.1f}</text>')
        
        # 轴标题
        svg_parts.append(f'<text x="{width/2}" y="{height-10}" class="axis-label">{chart.options.get("x_label", "")}</text>')
        svg_parts.append(f'<text x="20" y="{height/2}" class="axis-label" transform="rotate(-90, 20, {height/2})">{chart.options.get("y_label", "")}</text>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def _generate_pie_chart_svg(self, chart: Chart) -> str:
        """生成饼图SVG"""
        
        width = chart.style.width
        height = chart.style.height
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 3
        
        # 计算总值
        dataset = chart.data.datasets[0]
        total = sum(dataset["data"])
        
        # 开始构建SVG
        svg_parts = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{width}" height="{height}" fill="{chart.style.background_color}"/>',
            f'<style>',
            f'.chart-title {{ font-family: {chart.style.font_family}; font-size: {chart.style.title_font_size}px; text-anchor: middle; }}',
            f'.pie-label {{ font-family: {chart.style.font_family}; font-size: {chart.style.font_size}px; text-anchor: middle; }}',
            f'</style>'
        ]
        
        # 标题
        svg_parts.append(f'<text x="{width/2}" y="30" class="chart-title">{chart.title}</text>')
        
        # 绘制扇形
        start_angle = 0
        for i, (label, value) in enumerate(zip(chart.data.labels, dataset["data"])):
            angle = value / total * 360
            end_angle = start_angle + angle
            
            # 计算路径
            start_x = center_x + radius * self._cos_deg(start_angle)
            start_y = center_y + radius * self._sin_deg(start_angle)
            end_x = center_x + radius * self._cos_deg(end_angle)
            end_y = center_y + radius * self._sin_deg(end_angle)
            
            large_arc = 1 if angle > 180 else 0
            
            path = f'M {center_x} {center_y} L {start_x} {start_y} A {radius} {radius} 0 {large_arc} 1 {end_x} {end_y} Z'
            
            color = dataset["colors"][i % len(dataset["colors"])]
            svg_parts.append(f'<path d="{path}" fill="{color}" stroke="white" stroke-width="2"/>')
            
            # 标签
            label_angle = start_angle + angle / 2
            label_x = center_x + (radius + 20) * self._cos_deg(label_angle)
            label_y = center_y + (radius + 20) * self._sin_deg(label_angle)
            
            percentage = value / total * 100
            svg_parts.append(f'<text x="{label_x}" y="{label_y}" class="pie-label">{label} ({percentage:.1f}%)</text>')
            
            start_angle = end_angle
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def _generate_scatter_plot_svg(self, chart: Chart) -> str:
        """生成散点图SVG"""
        
        width = chart.style.width
        height = chart.style.height
        margin = 60
        plot_width = width - 2 * margin
        plot_height = height - 2 * margin
        
        dataset = chart.data.datasets[0]
        x_data = dataset["x_data"]
        y_data = dataset["y_data"]
        
        # 计算数据范围
        min_x, max_x = min(x_data), max(x_data)
        min_y, max_y = min(y_data), max(y_data)
        x_range = max_x - min_x if max_x != min_x else 1
        y_range = max_y - min_y if max_y != min_y else 1
        
        # 开始构建SVG
        svg_parts = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{width}" height="{height}" fill="{chart.style.background_color}"/>',
            f'<style>',
            f'.chart-title {{ font-family: {chart.style.font_family}; font-size: {chart.style.title_font_size}px; text-anchor: middle; }}',
            f'.axis-label {{ font-family: {chart.style.font_family}; font-size: {chart.style.font_size}px; text-anchor: middle; }}',
            f'.grid-line {{ stroke: #e0e0e0; stroke-width: 1; }}',
            f'</style>'
        ]
        
        # 标题
        svg_parts.append(f'<text x="{width/2}" y="30" class="chart-title">{chart.title}</text>')
        
        # 网格线
        if chart.style.show_grid:
            for i in range(6):
                x = margin + i * plot_width / 5
                y = margin + i * plot_height / 5
                svg_parts.append(f'<line x1="{x}" y1="{margin}" x2="{x}" y2="{height-margin}" class="grid-line"/>')
                svg_parts.append(f'<line x1="{margin}" y1="{y}" x2="{width-margin}" y2="{y}" class="grid-line"/>')
        
        # 坐标轴
        svg_parts.append(f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="black" stroke-width="2"/>')
        svg_parts.append(f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="black" stroke-width="2"/>')
        
        # 绘制数据点
        for x_val, y_val in zip(x_data, y_data):
            x = margin + (x_val - min_x) / x_range * plot_width
            y = height - margin - (y_val - min_y) / y_range * plot_height
            svg_parts.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{dataset["color"]}" opacity="0.7"/>')
        
        # 轴标签
        for i in range(6):
            x = margin + i * plot_width / 5
            y = margin + i * plot_height / 5
            x_val = min_x + i * x_range / 5
            y_val = max_y - i * y_range / 5
            svg_parts.append(f'<text x="{x}" y="{height-margin+20}" class="axis-label">{x_val:.1f}</text>')
            svg_parts.append(f'<text x="{margin-10}" y="{y+5}" class="axis-label" text-anchor="end">{y_val:.1f}</text>')
        
        # 轴标题
        svg_parts.append(f'<text x="{width/2}" y="{height-10}" class="axis-label">{chart.options.get("x_label", "")}</text>')
        svg_parts.append(f'<text x="20" y="{height/2}" class="axis-label" transform="rotate(-90, 20, {height/2})">{chart.options.get("y_label", "")}</text>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def _generate_heatmap_svg(self, chart: Chart) -> str:
        """生成热力图SVG"""
        
        width = chart.style.width
        height = chart.style.height
        margin = 80
        plot_width = width - 2 * margin
        plot_height = height - 2 * margin
        
        dataset = chart.data.datasets[0]
        data = dataset["data"]
        x_labels = dataset["x_labels"]
        y_labels = dataset["y_labels"]
        
        rows = len(data)
        cols = len(data[0]) if data else 0
        cell_width = plot_width / cols
        cell_height = plot_height / rows
        
        # 计算数据范围
        all_values = [val for row in data for val in row]
        min_val, max_val = min(all_values), max(all_values)
        val_range = max_val - min_val if max_val != min_val else 1
        
        # 开始构建SVG
        svg_parts = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{width}" height="{height}" fill="{chart.style.background_color}"/>',
            f'<style>',
            f'.chart-title {{ font-family: {chart.style.font_family}; font-size: {chart.style.title_font_size}px; text-anchor: middle; }}',
            f'.axis-label {{ font-family: {chart.style.font_family}; font-size: {chart.style.font_size}px; text-anchor: middle; }}',
            f'.cell-text {{ font-family: {chart.style.font_family}; font-size: {chart.style.font_size-2}px; text-anchor: middle; }}',
            f'</style>'
        ]
        
        # 标题
        svg_parts.append(f'<text x="{width/2}" y="30" class="chart-title">{chart.title}</text>')
        
        # 绘制热力图单元格
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                x = margin + j * cell_width
                y = margin + i * cell_height
                
                # 计算颜色强度
                intensity = (value - min_val) / val_range
                color = self._get_heatmap_color(intensity)
                
                svg_parts.append(f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" fill="{color}" stroke="white" stroke-width="1"/>')
                
                # 显示数值
                if chart.options.get("show_values", True):
                    text_x = x + cell_width / 2
                    text_y = y + cell_height / 2 + 5
                    text_color = "white" if intensity > 0.5 else "black"
                    svg_parts.append(f'<text x="{text_x}" y="{text_y}" class="cell-text" fill="{text_color}">{value:.2f}</text>')
        
        # X轴标签
        for j, label in enumerate(x_labels):
            x = margin + (j + 0.5) * cell_width
            svg_parts.append(f'<text x="{x}" y="{height-margin+20}" class="axis-label">{label}</text>')
        
        # Y轴标签
        for i, label in enumerate(y_labels):
            y = margin + (i + 0.5) * cell_height
            svg_parts.append(f'<text x="{margin-10}" y="{y+5}" class="axis-label" text-anchor="end">{label}</text>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def _get_heatmap_color(self, intensity: float) -> str:
        """获取热力图颜色"""
        # 使用蓝-白-红色谱
        if intensity < 0.5:
            # 蓝到白
            blue_intensity = 1 - intensity * 2
            return f"rgb({int(255 * (1 - blue_intensity))}, {int(255 * (1 - blue_intensity))}, 255)"
        else:
            # 白到红
            red_intensity = (intensity - 0.5) * 2
            return f"rgb(255, {int(255 * (1 - red_intensity))}, {int(255 * (1 - red_intensity))})"
    
    def _cos_deg(self, degrees: float) -> float:
        """度数转弧度并计算余弦"""
        import math
        return math.cos(math.radians(degrees))
    
    def _sin_deg(self, degrees: float) -> float:
        """度数转弧度并计算正弦"""
        import math
        return math.sin(math.radians(degrees))
    
    def _wrap_svg_in_html(self, svg_content: str, title: str) -> str:
        """将SVG包装在HTML中"""
        
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .chart-container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        {svg_content}
    </div>
</body>
</html>
"""
        return html_template
    
    def export_chart(
        self, 
        chart: Chart, 
        file_path: str, 
        format: ExportFormat = ExportFormat.SVG
    ) -> bool:
        """导出图表"""
        
        try:
            if format == ExportFormat.SVG:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(chart.svg_content)
            
            elif format == ExportFormat.HTML:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(chart.html_content)
            
            elif format == ExportFormat.JSON:
                chart_data = {
                    "type": chart.type.value,
                    "title": chart.title,
                    "data": {
                        "labels": chart.data.labels,
                        "datasets": chart.data.datasets,
                        "metadata": chart.data.metadata
                    },
                    "style": {
                        "width": chart.style.width,
                        "height": chart.style.height,
                        "background_color": chart.style.background_color,
                        "font_family": chart.style.font_family,
                        "font_size": chart.style.font_size,
                        "color_scheme": chart.style.color_scheme.value
                    },
                    "options": chart.options
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(chart_data, f, ensure_ascii=False, indent=2, default=str)
            
            else:
                raise ValueError(f"不支持的导出格式: {format}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"导出图表失败: {e}")
            return False
    
    def create_dashboard(
        self, 
        charts: List[Chart], 
        title: str = "数据仪表板",
        layout: str = "grid"
    ) -> str:
        """创建仪表板"""
        
        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="zh-CN">',
            "<head>",
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"<title>{title}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }",
            ".dashboard-title { text-align: center; color: #333; margin-bottom: 30px; }",
            ".chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }",
            ".chart-container { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }",
            "</style>",
            "</head>",
            "<body>",
            f'<h1 class="dashboard-title">{title}</h1>',
            '<div class="chart-grid">'
        ]
        
        # 添加图表
        for chart in charts:
            html_parts.append('<div class="chart-container">')
            html_parts.append(chart.svg_content)
            html_parts.append('</div>')
        
        html_parts.extend([
            '</div>',
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html_parts)
    
    def get_color_palette(self, scheme: ColorScheme, count: int) -> List[str]:
        """获取颜色调色板"""
        
        colors = self.color_palettes[scheme]
        
        if count <= len(colors):
            return colors[:count]
        else:
            # 如果需要更多颜色，生成渐变色
            return self._generate_gradient_colors(colors[0], colors[-1], count)
    
    def _generate_gradient_colors(self, start_color: str, end_color: str, count: int) -> List[str]:
        """生成渐变色"""
        
        # 简化实现，返回重复的颜色
        base_colors = self.color_palettes[ColorScheme.DEFAULT]
        return [base_colors[i % len(base_colors)] for i in range(count)]