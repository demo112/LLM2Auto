# -*- encoding=utf8 -*-
"""
设备工具类
"""

import logging
from typing import List, Dict, Any, Optional


class DeviceUtils:
    """设备操作工具类"""
    
    @staticmethod
    def get_android_devices() -> List[Dict[str, str]]:
        """
        获取连接的Android设备列表
        
        Returns:
            List[Dict[str, str]]: 设备信息列表
        """
        devices = []
        
        try:
            from airtest.core.android.adb import ADB
            
            adb = ADB()
            device_list = adb.devices()
            
            for device_id in device_list:
                try:
                    device_adb = ADB(serialno=device_id)
                    device_info = {
                        'id': device_id,
                        'model': device_adb.getprop('ro.product.model') or 'Unknown',
                        'version': device_adb.getprop('ro.build.version.release') or 'Unknown',
                        'sdk': device_adb.getprop('ro.build.version.sdk') or 'Unknown',
                        'manufacturer': device_adb.getprop('ro.product.manufacturer') or 'Unknown',
                        'status': 'online'
                    }
                    devices.append(device_info)
                except Exception as e:
                    logging.warning(f"获取设备信息失败: {device_id} - {e}")
                    devices.append({
                        'id': device_id,
                        'model': 'Unknown',
                        'version': 'Unknown',
                        'sdk': 'Unknown',
                        'manufacturer': 'Unknown',
                        'status': 'error'
                    })
        
        except Exception as e:
            logging.error(f"获取Android设备列表失败: {e}")
        
        return devices
    
    @staticmethod
    def check_device_connection(device_uri: str) -> bool:
        """
        检查设备连接状态
        
        Args:
            device_uri: 设备URI
            
        Returns:
            bool: 是否连接成功
        """
        try:
            from airtest.core.api import connect_device
            
            device = connect_device(device_uri)
            return device is not None
        except Exception:
            return False
    
    @staticmethod
    def get_device_info(device_uri: str) -> Dict[str, Any]:
        """
        获取设备详细信息
        
        Args:
            device_uri: 设备URI
            
        Returns:
            Dict[str, Any]: 设备信息
        """
        info = {
            'uri': device_uri,
            'connected': False,
            'platform': 'unknown'
        }
        
        try:
            from airtest.core.api import connect_device
            
            device = connect_device(device_uri)
            if device:
                info['connected'] = True
                
                # 获取平台信息
                if hasattr(device, 'adb'):
                    info['platform'] = 'Android'
                    adb = device.adb
                    
                    try:
                        info.update({
                            'serial': getattr(adb, 'serialno', 'unknown'),
                            'model': adb.getprop('ro.product.model'),
                            'version': adb.getprop('ro.build.version.release'),
                            'sdk': adb.getprop('ro.build.version.sdk'),
                            'manufacturer': adb.getprop('ro.product.manufacturer'),
                            'resolution': str(device.display_info) if hasattr(device, 'display_info') else 'unknown'
                        })
                    except Exception as e:
                        logging.warning(f"获取Android设备详细信息失败: {e}")
                
                elif hasattr(device, 'driver'):
                    info['platform'] = 'iOS'
                    # iOS设备信息获取
                    try:
                        info.update({
                            'model': 'iOS Device',
                            'version': 'unknown'
                        })
                    except Exception as e:
                        logging.warning(f"获取iOS设备详细信息失败: {e}")
        
        except Exception as e:
            logging.error(f"获取设备信息失败: {device_uri} - {e}")
        
        return info
    
    @staticmethod
    def wait_for_device(device_uri: str, timeout: int = 60) -> bool:
        """
        等待设备连接
        
        Args:
            device_uri: 设备URI
            timeout: 超时时间（秒）
            
        Returns:
            bool: 是否连接成功
        """
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if DeviceUtils.check_device_connection(device_uri):
                return True
            
            time.sleep(2)
        
        return False
    
    @staticmethod
    def install_app(device_uri: str, apk_path: str) -> bool:
        """
        安装应用
        
        Args:
            device_uri: 设备URI
            apk_path: APK文件路径
            
        Returns:
            bool: 是否安装成功
        """
        try:
            from airtest.core.api import connect_device
            
            device = connect_device(device_uri)
            if not device:
                return False
            
            if hasattr(device, 'adb'):
                # Android设备
                device.adb.install(apk_path)
                return True
            
        except Exception as e:
            logging.error(f"应用安装失败: {e}")
        
        return False
    
    @staticmethod
    def uninstall_app(device_uri: str, package_name: str) -> bool:
        """
        卸载应用
        
        Args:
            device_uri: 设备URI
            package_name: 包名
            
        Returns:
            bool: 是否卸载成功
        """
        try:
            from airtest.core.api import connect_device
            
            device = connect_device(device_uri)
            if not device:
                return False
            
            if hasattr(device, 'adb'):
                # Android设备
                device.adb.uninstall(package_name)
                return True
            
        except Exception as e:
            logging.error(f"应用卸载失败: {e}")
        
        return False
    
    @staticmethod
    def start_app(device_uri: str, package_name: str) -> bool:
        """
        启动应用
        
        Args:
            device_uri: 设备URI
            package_name: 包名
            
        Returns:
            bool: 是否启动成功
        """
        try:
            from airtest.core.api import connect_device, start_app
            
            device = connect_device(device_uri)
            if not device:
                return False
            
            start_app(package_name)
            return True
            
        except Exception as e:
            logging.error(f"应用启动失败: {e}")
        
        return False
    
    @staticmethod
    def stop_app(device_uri: str, package_name: str) -> bool:
        """
        停止应用
        
        Args:
            device_uri: 设备URI
            package_name: 包名
            
        Returns:
            bool: 是否停止成功
        """
        try:
            from airtest.core.api import connect_device, stop_app
            
            device = connect_device(device_uri)
            if not device:
                return False
            
            stop_app(package_name)
            return True
            
        except Exception as e:
            logging.error(f"应用停止失败: {e}")
        
        return False
    
    @staticmethod
    def clear_app_data(device_uri: str, package_name: str) -> bool:
        """
        清除应用数据
        
        Args:
            device_uri: 设备URI
            package_name: 包名
            
        Returns:
            bool: 是否清除成功
        """
        try:
            from airtest.core.api import connect_device
            
            device = connect_device(device_uri)
            if not device:
                return False
            
            if hasattr(device, 'adb'):
                # Android设备
                device.adb.shell(f"pm clear {package_name}")
                return True
            
        except Exception as e:
            logging.error(f"应用数据清除失败: {e}")
        
        return False
    
    @staticmethod
    def take_screenshot(device_uri: str, save_path: str) -> bool:
        """
        截取屏幕截图
        
        Args:
            device_uri: 设备URI
            save_path: 保存路径
            
        Returns:
            bool: 是否截图成功
        """
        try:
            from airtest.core.api import connect_device, snapshot
            
            device = connect_device(device_uri)
            if not device:
                return False
            
            snapshot(save_path)
            return True
            
        except Exception as e:
            logging.error(f"截图失败: {e}")
        
        return False