# -*- encoding=utf8 -*-
"""
日志工具类
"""

import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional, Dict, Any
import json


class LogUtils:
    """日志工具类"""
    
    @staticmethod
    def setup_logger(name: str, log_file: str, level: int = logging.INFO, 
                    max_bytes: int = 10*1024*1024, backup_count: int = 5) -> logging.Logger:
        """
        设置日志记录器
        
        Args:
            name: 日志记录器名称
            log_file: 日志文件路径
            level: 日志级别
            max_bytes: 单个日志文件最大字节数
            backup_count: 备份文件数量
            
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 文件处理器（带轮转）
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    @staticmethod
    def setup_test_logger(test_name: str, log_dir: str) -> logging.Logger:
        """
        为测试用例设置专用日志记录器
        
        Args:
            test_name: 测试名称
            log_dir: 日志目录
            
        Returns:
            logging.Logger: 测试日志记录器
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f"{test_name}_{timestamp}.log")
        
        return LogUtils.setup_logger(f"test.{test_name}", log_file)
    
    @staticmethod
    def log_test_start(logger: logging.Logger, test_name: str, metadata: Dict[str, Any]):
        """
        记录测试开始
        
        Args:
            logger: 日志记录器
            test_name: 测试名称
            metadata: 测试元数据
        """
        logger.info("=" * 80)
        logger.info(f"测试开始: {test_name}")
        logger.info(f"测试描述: {metadata.get('description', 'N/A')}")
        logger.info(f"测试分类: {metadata.get('category', 'N/A')}")
        logger.info(f"优先级: {metadata.get('priority', 'N/A')}")
        logger.info(f"标签: {', '.join(metadata.get('tags', []))}")
        logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
    
    @staticmethod
    def log_test_end(logger: logging.Logger, test_name: str, result: str, 
                    duration: float, error: Optional[str] = None):
        """
        记录测试结束
        
        Args:
            logger: 日志记录器
            test_name: 测试名称
            result: 测试结果
            duration: 执行时长
            error: 错误信息
        """
        logger.info("=" * 80)
        logger.info(f"测试结束: {test_name}")
        logger.info(f"测试结果: {result}")
        logger.info(f"执行时长: {duration:.2f}秒")
        logger.info(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if error:
            logger.error(f"错误信息: {error}")
        
        logger.info("=" * 80)
    
    @staticmethod
    def log_step(logger: logging.Logger, step_name: str, details: Optional[str] = None):
        """
        记录测试步骤
        
        Args:
            logger: 日志记录器
            step_name: 步骤名称
            details: 步骤详情
        """
        logger.info(f"执行步骤: {step_name}")
        if details:
            logger.info(f"步骤详情: {details}")
    
    @staticmethod
    def log_screenshot(logger: logging.Logger, screenshot_path: str, description: str = ""):
        """
        记录截图信息
        
        Args:
            logger: 日志记录器
            screenshot_path: 截图路径
            description: 截图描述
        """
        logger.info(f"截图保存: {screenshot_path}")
        if description:
            logger.info(f"截图描述: {description}")
    
    @staticmethod
    def log_device_info(logger: logging.Logger, device_info: Dict[str, Any]):
        """
        记录设备信息
        
        Args:
            logger: 日志记录器
            device_info: 设备信息
        """
        logger.info("设备信息:")
        for key, value in device_info.items():
            logger.info(f"  {key}: {value}")
    
    @staticmethod
    def log_performance_metrics(logger: logging.Logger, metrics: Dict[str, Any]):
        """
        记录性能指标
        
        Args:
            logger: 日志记录器
            metrics: 性能指标
        """
        logger.info("性能指标:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                logger.info(f"  {metric}: {value:.3f}")
            else:
                logger.info(f"  {metric}: {value}")
    
    @staticmethod
    def create_structured_log(log_file: str, data: Dict[str, Any]):
        """
        创建结构化日志文件
        
        Args:
            log_file: 日志文件路径
            data: 日志数据
        """
        try:
            # 确保目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 添加时间戳
            data['timestamp'] = datetime.now().isoformat()
            
            # 写入JSON格式日志
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logging.error(f"创建结构化日志失败: {e}")
    
    @staticmethod
    def parse_log_file(log_file: str) -> Dict[str, Any]:
        """
        解析日志文件
        
        Args:
            log_file: 日志文件路径
            
        Returns:
            Dict[str, Any]: 解析后的日志数据
        """
        try:
            if log_file.endswith('.json'):
                # JSON格式日志
                with open(log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 文本格式日志
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                return {
                    'file': log_file,
                    'lines': len(lines),
                    'content': ''.join(lines)
                }
                
        except Exception as e:
            logging.error(f"解析日志文件失败: {e}")
            return {}
    
    @staticmethod
    def cleanup_old_logs(log_dir: str, days: int = 7):
        """
        清理旧日志文件
        
        Args:
            log_dir: 日志目录
            days: 保留天数
        """
        try:
            import time
            
            if not os.path.exists(log_dir):
                return
            
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            for filename in os.listdir(log_dir):
                file_path = os.path.join(log_dir, filename)
                
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    
                    if file_time < cutoff_time:
                        try:
                            os.remove(file_path)
                            logging.info(f"删除旧日志文件: {filename}")
                        except Exception as e:
                            logging.warning(f"删除日志文件失败: {filename} - {e}")
                            
        except Exception as e:
            logging.error(f"清理旧日志失败: {e}")
    
    @staticmethod
    def get_log_summary(log_dir: str) -> Dict[str, Any]:
        """
        获取日志目录摘要
        
        Args:
            log_dir: 日志目录
            
        Returns:
            Dict[str, Any]: 日志摘要信息
        """
        summary = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'oldest_file': None,
            'newest_file': None
        }
        
        try:
            if not os.path.exists(log_dir):
                return summary
            
            oldest_time = float('inf')
            newest_time = 0
            
            for filename in os.listdir(log_dir):
                file_path = os.path.join(log_dir, filename)
                
                if os.path.isfile(file_path):
                    summary['total_files'] += 1
                    
                    # 文件大小
                    file_size = os.path.getsize(file_path)
                    summary['total_size'] += file_size
                    
                    # 文件类型
                    ext = os.path.splitext(filename)[1].lower()
                    summary['file_types'][ext] = summary['file_types'].get(ext, 0) + 1
                    
                    # 文件时间
                    file_time = os.path.getmtime(file_path)
                    if file_time < oldest_time:
                        oldest_time = file_time
                        summary['oldest_file'] = filename
                    
                    if file_time > newest_time:
                        newest_time = file_time
                        summary['newest_file'] = filename
            
            # 转换文件大小为可读格式
            if summary['total_size'] > 0:
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if summary['total_size'] < 1024:
                        summary['total_size_readable'] = f"{summary['total_size']:.1f} {unit}"
                        break
                    summary['total_size'] /= 1024
                    
        except Exception as e:
            logging.error(f"获取日志摘要失败: {e}")
        
        return summary