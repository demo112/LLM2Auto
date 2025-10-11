# -*- encoding=utf8 -*-
"""
文件工具类
"""

import os
import shutil
import hashlib
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional


class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_dir(dir_path: str) -> bool:
        """
        确保目录存在
        
        Args:
            dir_path: 目录路径
            
        Returns:
            bool: 是否成功
        """
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def copy_air_project(src_path: str, dst_path: str) -> bool:
        """
        复制 .air 项目
        
        Args:
            src_path: 源路径
            dst_path: 目标路径
            
        Returns:
            bool: 是否成功
        """
        try:
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            
            shutil.copytree(src_path, dst_path)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_hash(file_path: str) -> Optional[str]:
        """
        获取文件哈希值
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[str]: 哈希值
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None
    
    @staticmethod
    def find_files(directory: str, pattern: str = "*", recursive: bool = True) -> List[str]:
        """
        查找文件
        
        Args:
            directory: 搜索目录
            pattern: 文件模式
            recursive: 是否递归搜索
            
        Returns:
            List[str]: 文件路径列表
        """
        path = Path(directory)
        
        if recursive:
            return [str(f) for f in path.rglob(pattern)]
        else:
            return [str(f) for f in path.glob(pattern)]
    
    @staticmethod
    def clean_temp_files(temp_dir: str, max_age_hours: int = 24) -> int:
        """
        清理临时文件
        
        Args:
            temp_dir: 临时目录
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            int: 清理的文件数量
        """
        import time
        
        if not os.path.exists(temp_dir):
            return 0
        
        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        cleaned_count += 1
        except Exception:
            pass
        
        return cleaned_count
    
    @staticmethod
    def archive_logs(log_dir: str, archive_dir: str, days_to_keep: int = 7) -> bool:
        """
        归档日志文件
        
        Args:
            log_dir: 日志目录
            archive_dir: 归档目录
            days_to_keep: 保留天数
            
        Returns:
            bool: 是否成功
        """
        try:
            import time
            from datetime import datetime, timedelta
            
            FileUtils.ensure_dir(archive_dir)
            
            cutoff_time = time.time() - (days_to_keep * 24 * 3600)
            archive_name = f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            archive_path = os.path.join(archive_dir, archive_name)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(log_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        if os.path.getmtime(file_path) < cutoff_time:
                            # 添加到压缩包
                            arcname = os.path.relpath(file_path, log_dir)
                            zipf.write(file_path, arcname)
                            
                            # 删除原文件
                            os.remove(file_path)
            
            return True
        except Exception:
            return False