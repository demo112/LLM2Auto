# -*- encoding=utf8 -*-
"""
Airtest 测试模板
这是一个标准的 .air 项目测试模板
"""

import os
import sys
import logging
from datetime import datetime

# 添加框架路径
framework_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, framework_path)

from airtest.core.api import *
from airtest.cli.parser import cli_setup


class AirtestTemplate:
    """Airtest 测试模板类"""
    
    def __init__(self, project_path: str):
        """
        初始化测试模板
        
        Args:
            project_path: .air 项目路径
        """
        self.project_path = project_path
        self.logger = None
        self.device = None
        self.start_time = None
        self.screenshots = []
        
    def setup(self, device_uri: str = "Android:///", log_dir: str = None):
        """
        设置测试环境
        
        Args:
            device_uri: 设备URI
            log_dir: 日志目录
        """
        try:
            # 设置日志
            if log_dir:
                log_file = os.path.join(log_dir, f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file, encoding='utf-8'),
                        logging.StreamHandler()
                    ]
                )
            
            self.logger = logging.getLogger(__name__)
            
            # 设置 Airtest
            if not cli_setup():
                auto_setup(__file__, logdir=log_dir, devices=[device_uri])
            
            # 连接设备
            self.device = connect_device(device_uri)
            self.start_time = datetime.now()
            
            self.logger.info(f"测试环境设置完成 - 设备: {device_uri}")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"测试环境设置失败: {e}")
            raise
    
    def teardown(self):
        """清理测试环境"""
        try:
            if self.start_time:
                duration = (datetime.now() - self.start_time).total_seconds()
                if self.logger:
                    self.logger.info(f"测试执行完成，耗时: {duration:.2f}秒")
            
            # 清理资源
            if self.device:
                # 可以在这里添加设备清理逻辑
                pass
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"测试环境清理失败: {e}")
    
    def take_screenshot(self, description: str = ""):
        """
        截取屏幕截图
        
        Args:
            description: 截图描述
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            screenshot_name = f"screenshot_{timestamp}.png"
            
            screenshot_path = snapshot(screenshot_name)
            self.screenshots.append({
                'path': screenshot_path,
                'description': description,
                'timestamp': timestamp
            })
            
            if self.logger:
                self.logger.info(f"截图保存: {screenshot_path} - {description}")
            
            return screenshot_path
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"截图失败: {e}")
            return None
    
    def wait_and_touch(self, template, timeout=10, description=""):
        """
        等待并点击元素
        
        Args:
            template: 模板图像
            timeout: 超时时间
            description: 操作描述
        """
        try:
            if self.logger:
                self.logger.info(f"等待并点击元素: {description}")
            
            # 等待元素出现
            wait(template, timeout=timeout)
            
            # 点击元素
            touch(template)
            
            if self.logger:
                self.logger.info(f"点击成功: {description}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"点击失败: {description} - {e}")
            return False
    
    def swipe_and_wait(self, start_template, end_template, duration=1, description=""):
        """
        滑动操作
        
        Args:
            start_template: 起始位置模板
            end_template: 结束位置模板
            duration: 滑动持续时间
            description: 操作描述
        """
        try:
            if self.logger:
                self.logger.info(f"执行滑动操作: {description}")
            
            # 执行滑动
            swipe(start_template, end_template, duration=duration)
            
            if self.logger:
                self.logger.info(f"滑动成功: {description}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"滑动失败: {description} - {e}")
            return False
    
    def assert_exists(self, template, description=""):
        """
        断言元素存在
        
        Args:
            template: 模板图像
            description: 断言描述
        """
        try:
            if self.logger:
                self.logger.info(f"断言元素存在: {description}")
            
            assert_exists(template, description)
            
            if self.logger:
                self.logger.info(f"断言成功: {description}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"断言失败: {description} - {e}")
            raise
    
    def run_test(self):
        """
        运行测试 - 子类需要重写此方法
        """
        raise NotImplementedError("子类必须实现 run_test 方法")


def main():
    """主函数 - 用于直接执行测试"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Airtest 测试模板')
    parser.add_argument('--device', default='Android:///', help='设备URI')
    parser.add_argument('--logdir', help='日志目录')
    parser.add_argument('--project', default='.', help='项目路径')
    
    args = parser.parse_args()
    
    # 创建测试实例
    test = AirtestTemplate(args.project)
    
    try:
        # 设置测试环境
        test.setup(device_uri=args.device, log_dir=args.logdir)
        
        # 运行测试
        test.run_test()
        
        print("测试执行成功")
        
    except Exception as e:
        print(f"测试执行失败: {e}")
        sys.exit(1)
        
    finally:
        # 清理环境
        test.teardown()


if __name__ == '__main__':
    main()