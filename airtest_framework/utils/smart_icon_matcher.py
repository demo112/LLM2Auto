# -*- encoding=utf8 -*-
"""
智能图标匹配工具
用于处理同一图标的不同状态（如选中/未选中）的匹配问题
"""

from airtest.core.api import *
from airtest.core.cv import Template
import os
import logging
from typing import List, Dict, Optional, Tuple, Union


class SmartIconMatcher:
    """智能图标匹配器"""
    
    def __init__(self, base_path: str = None):
        """
        初始化智能图标匹配器
        
        Args:
            base_path: 图标资源基础路径
        """
        self.base_path = base_path or os.path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        
    def multi_state_touch(self, icon_states: List[Union[str, Template]], 
                         timeout: float = 10.0, 
                         threshold: float = 0.8) -> bool:
        """
        多状态图标点击
        
        Args:
            icon_states: 图标的多个状态模板列表
            timeout: 超时时间
            threshold: 匹配阈值
            
        Returns:
            bool: 是否成功点击
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            for state in icon_states:
                try:
                    template = self._ensure_template(state, threshold)
                    if exists(template):
                        touch(template)
                        self.logger.info(f"成功点击图标状态: {state}")
                        return True
                except Exception as e:
                    self.logger.debug(f"状态 {state} 匹配失败: {e}")
                    continue
            
            time.sleep(0.5)
        
        self.logger.warning(f"所有图标状态都未找到: {icon_states}")
        return False
    
    def wait_for_any_state(self, icon_states: List[Union[str, Template]], 
                          timeout: float = 10.0, 
                          threshold: float = 0.8) -> Optional[str]:
        """
        等待任意一个状态出现
        
        Args:
            icon_states: 图标的多个状态模板列表
            timeout: 超时时间
            threshold: 匹配阈值
            
        Returns:
            str: 找到的状态名称，未找到返回None
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            for i, state in enumerate(icon_states):
                try:
                    template = self._ensure_template(state, threshold)
                    if exists(template):
                        self.logger.info(f"找到图标状态: {state}")
                        return f"state_{i}" if isinstance(state, str) else str(state)
                except Exception as e:
                    self.logger.debug(f"状态 {state} 检测失败: {e}")
                    continue
            
            time.sleep(0.5)
        
        return None
    
    def get_current_state(self, icon_states: Dict[str, Union[str, Template]], 
                         threshold: float = 0.8) -> Optional[str]:
        """
        获取当前图标状态
        
        Args:
            icon_states: 状态名称到模板的映射
            threshold: 匹配阈值
            
        Returns:
            str: 当前状态名称，未找到返回None
        """
        for state_name, template in icon_states.items():
            try:
                template_obj = self._ensure_template(template, threshold)
                if exists(template_obj):
                    self.logger.info(f"当前图标状态: {state_name}")
                    return state_name
            except Exception as e:
                self.logger.debug(f"状态 {state_name} 检测失败: {e}")
                continue
        
        return None
    
    def toggle_state(self, icon_states: Dict[str, Union[str, Template]], 
                    target_state: str, 
                    max_attempts: int = 3,
                    threshold: float = 0.8) -> bool:
        """
        切换到目标状态
        
        Args:
            icon_states: 状态名称到模板的映射
            target_state: 目标状态名称
            max_attempts: 最大尝试次数
            threshold: 匹配阈值
            
        Returns:
            bool: 是否成功切换到目标状态
        """
        for attempt in range(max_attempts):
            current_state = self.get_current_state(icon_states, threshold)
            
            if current_state == target_state:
                self.logger.info(f"已经是目标状态: {target_state}")
                return True
            
            # 尝试点击当前状态来切换
            if current_state and current_state in icon_states:
                try:
                    template = self._ensure_template(icon_states[current_state], threshold)
                    touch(template)
                    time.sleep(1)  # 等待状态切换
                    self.logger.info(f"尝试从 {current_state} 切换到 {target_state}")
                except Exception as e:
                    self.logger.warning(f"切换状态失败: {e}")
            else:
                # 如果无法识别当前状态，尝试点击所有可能的状态
                for state_name, template in icon_states.items():
                    if state_name != target_state:
                        try:
                            template_obj = self._ensure_template(template, threshold)
                            if exists(template_obj):
                                touch(template_obj)
                                time.sleep(1)
                                break
                        except Exception:
                            continue
        
        # 最终检查是否达到目标状态
        final_state = self.get_current_state(icon_states, threshold)
        success = final_state == target_state
        
        if success:
            self.logger.info(f"成功切换到目标状态: {target_state}")
        else:
            self.logger.warning(f"未能切换到目标状态: {target_state}, 当前状态: {final_state}")
        
        return success
    
    def smart_assert_state(self, icon_states: Dict[str, Union[str, Template]], 
                          expected_state: str,
                          threshold: float = 0.8) -> bool:
        """
        智能断言图标状态
        
        Args:
            icon_states: 状态名称到模板的映射
            expected_state: 期望的状态
            threshold: 匹配阈值
            
        Returns:
            bool: 是否为期望状态
        """
        current_state = self.get_current_state(icon_states, threshold)
        
        if current_state == expected_state:
            self.logger.info(f"状态断言成功: {expected_state}")
            return True
        else:
            self.logger.error(f"状态断言失败: 期望 {expected_state}, 实际 {current_state}")
            return False
    
    def _ensure_template(self, template: Union[str, Template], threshold: float) -> Template:
        """
        确保输入是Template对象
        
        Args:
            template: 模板路径或Template对象
            threshold: 匹配阈值
            
        Returns:
            Template: Template对象
        """
        if isinstance(template, str):
            # 如果是相对路径，加上基础路径
            if not os.path.isabs(template) and self.base_path:
                template = os.path.join(self.base_path, template)
            return Template(template, threshold=threshold)
        elif isinstance(template, Template):
            # 更新阈值
            template.threshold = threshold
            return template
        else:
            raise ValueError(f"不支持的模板类型: {type(template)}")


class IconStateManager:
    """图标状态管理器"""
    
    def __init__(self):
        self.matcher = SmartIconMatcher()
        self.state_definitions = {}
    
    def define_icon_states(self, icon_name: str, states: Dict[str, str]):
        """
        定义图标的各种状态
        
        Args:
            icon_name: 图标名称
            states: 状态名称到图片路径的映射
        """
        self.state_definitions[icon_name] = states
    
    def click_icon(self, icon_name: str, timeout: float = 10.0) -> bool:
        """
        点击图标（自动处理多状态）
        
        Args:
            icon_name: 图标名称
            timeout: 超时时间
            
        Returns:
            bool: 是否成功点击
        """
        if icon_name not in self.state_definitions:
            raise ValueError(f"未定义的图标: {icon_name}")
        
        states = list(self.state_definitions[icon_name].values())
        return self.matcher.multi_state_touch(states, timeout)
    
    def set_icon_state(self, icon_name: str, target_state: str) -> bool:
        """
        设置图标到指定状态
        
        Args:
            icon_name: 图标名称
            target_state: 目标状态
            
        Returns:
            bool: 是否成功设置
        """
        if icon_name not in self.state_definitions:
            raise ValueError(f"未定义的图标: {icon_name}")
        
        states = self.state_definitions[icon_name]
        return self.matcher.toggle_state(states, target_state)
    
    def get_icon_state(self, icon_name: str) -> Optional[str]:
        """
        获取图标当前状态
        
        Args:
            icon_name: 图标名称
            
        Returns:
            str: 当前状态名称
        """
        if icon_name not in self.state_definitions:
            raise ValueError(f"未定义的图标: {icon_name}")
        
        states = self.state_definitions[icon_name]
        return self.matcher.get_current_state(states)


# 便捷函数
def multi_state_touch(icon_states: List[Union[str, Template]], **kwargs) -> bool:
    """便捷的多状态点击函数"""
    matcher = SmartIconMatcher()
    return matcher.multi_state_touch(icon_states, **kwargs)


def wait_for_any_icon_state(icon_states: List[Union[str, Template]], **kwargs) -> Optional[str]:
    """便捷的多状态等待函数"""
    matcher = SmartIconMatcher()
    return matcher.wait_for_any_state(icon_states, **kwargs)


def toggle_icon_state(icon_states: Dict[str, Union[str, Template]], target_state: str, **kwargs) -> bool:
    """便捷的状态切换函数"""
    matcher = SmartIconMatcher()
    return matcher.toggle_state(icon_states, target_state, **kwargs)