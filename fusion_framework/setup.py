#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fusion Framework 安装配置文件
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Fusion Framework - 智能融合测试框架"

# 读取requirements文件
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'airtest>=1.3.0',
        'pocoui>=1.0.89',
        'requests>=2.25.0',
        'pyyaml>=5.4.0',
        'jinja2>=3.0.0',
        'colorama>=0.4.4',
        'tqdm>=4.62.0',
    ]

setup(
    name="fusion-framework",
    version="1.0.0",
    author="Fusion Framework Team",
    author_email="",
    description="智能融合测试框架 - 专门用于Airtest和Poco脚本智能融合的测试框架",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
        ],
    },
    entry_points={
        'console_scripts': [
            'fusion-test=fusion_framework.scripts.run_fusion_tests:main',
        ],
    },
    include_package_data=True,
    package_data={
        'fusion_framework': [
            'config/*.json',
            'docs/*.md',
            'examples/*.py',
        ],
    },
    zip_safe=False,
)