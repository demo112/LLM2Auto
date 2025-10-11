# -*- encoding=utf8 -*-
"""
图像处理工具类
"""

import os
import cv2
import numpy as np
import logging
from typing import Tuple, Optional, List, Dict, Any
from PIL import Image, ImageDraw, ImageFont


class ImageUtils:
    """图像处理工具类"""
    
    @staticmethod
    def resize_image(image_path: str, target_size: Tuple[int, int], save_path: Optional[str] = None) -> str:
        """
        调整图像大小
        
        Args:
            image_path: 原图像路径
            target_size: 目标尺寸 (width, height)
            save_path: 保存路径，如果为None则覆盖原文件
            
        Returns:
            str: 处理后的图像路径
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")
            
            resized = cv2.resize(image, target_size)
            
            output_path = save_path or image_path
            cv2.imwrite(output_path, resized)
            
            return output_path
            
        except Exception as e:
            logging.error(f"图像大小调整失败: {e}")
            raise
    
    @staticmethod
    def crop_image(image_path: str, bbox: Tuple[int, int, int, int], save_path: Optional[str] = None) -> str:
        """
        裁剪图像
        
        Args:
            image_path: 原图像路径
            bbox: 裁剪区域 (x, y, width, height)
            save_path: 保存路径，如果为None则覆盖原文件
            
        Returns:
            str: 处理后的图像路径
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")
            
            x, y, w, h = bbox
            cropped = image[y:y+h, x:x+w]
            
            output_path = save_path or image_path
            cv2.imwrite(output_path, cropped)
            
            return output_path
            
        except Exception as e:
            logging.error(f"图像裁剪失败: {e}")
            raise
    
    @staticmethod
    def add_watermark(image_path: str, text: str, position: str = 'bottom-right', 
                     font_size: int = 20, color: Tuple[int, int, int] = (255, 255, 255),
                     save_path: Optional[str] = None) -> str:
        """
        添加水印
        
        Args:
            image_path: 原图像路径
            text: 水印文字
            position: 水印位置 ('top-left', 'top-right', 'bottom-left', 'bottom-right', 'center')
            font_size: 字体大小
            color: 字体颜色 (R, G, B)
            save_path: 保存路径，如果为None则覆盖原文件
            
        Returns:
            str: 处理后的图像路径
        """
        try:
            # 使用PIL处理文字
            pil_image = Image.open(image_path)
            draw = ImageDraw.Draw(pil_image)
            
            # 尝试使用系统字体
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # 获取文字尺寸
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算位置
            img_width, img_height = pil_image.size
            
            if position == 'top-left':
                x, y = 10, 10
            elif position == 'top-right':
                x, y = img_width - text_width - 10, 10
            elif position == 'bottom-left':
                x, y = 10, img_height - text_height - 10
            elif position == 'bottom-right':
                x, y = img_width - text_width - 10, img_height - text_height - 10
            elif position == 'center':
                x, y = (img_width - text_width) // 2, (img_height - text_height) // 2
            else:
                x, y = 10, 10
            
            # 添加文字
            draw.text((x, y), text, font=font, fill=color)
            
            output_path = save_path or image_path
            pil_image.save(output_path)
            
            return output_path
            
        except Exception as e:
            logging.error(f"添加水印失败: {e}")
            raise
    
    @staticmethod
    def compare_images(image1_path: str, image2_path: str, threshold: float = 0.8) -> Dict[str, Any]:
        """
        比较两张图像的相似度
        
        Args:
            image1_path: 第一张图像路径
            image2_path: 第二张图像路径
            threshold: 相似度阈值
            
        Returns:
            Dict[str, Any]: 比较结果
        """
        try:
            # 读取图像
            img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)
            
            if img1 is None or img2 is None:
                raise ValueError("无法读取图像文件")
            
            # 调整图像大小为相同尺寸
            height = min(img1.shape[0], img2.shape[0])
            width = min(img1.shape[1], img2.shape[1])
            
            img1_resized = cv2.resize(img1, (width, height))
            img2_resized = cv2.resize(img2, (width, height))
            
            # 计算结构相似性指数 (SSIM)
            from skimage.metrics import structural_similarity as ssim
            similarity = ssim(img1_resized, img2_resized)
            
            # 计算直方图相似度
            hist1 = cv2.calcHist([img1_resized], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([img2_resized], [0], None, [256], [0, 256])
            hist_similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            result = {
                'ssim_similarity': similarity,
                'histogram_similarity': hist_similarity,
                'average_similarity': (similarity + hist_similarity) / 2,
                'is_similar': (similarity + hist_similarity) / 2 >= threshold,
                'threshold': threshold
            }
            
            return result
            
        except Exception as e:
            logging.error(f"图像比较失败: {e}")
            return {
                'ssim_similarity': 0.0,
                'histogram_similarity': 0.0,
                'average_similarity': 0.0,
                'is_similar': False,
                'threshold': threshold,
                'error': str(e)
            }
    
    @staticmethod
    def extract_template_features(template_path: str) -> Dict[str, Any]:
        """
        提取模板图像特征
        
        Args:
            template_path: 模板图像路径
            
        Returns:
            Dict[str, Any]: 图像特征信息
        """
        try:
            image = cv2.imread(template_path)
            if image is None:
                raise ValueError(f"无法读取图像: {template_path}")
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 获取基本信息
            height, width = gray.shape
            
            # 计算直方图
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            
            # 计算图像统计信息
            mean_val = np.mean(gray)
            std_val = np.std(gray)
            
            # 检测关键点和描述符 (SIFT)
            try:
                sift = cv2.SIFT_create()
                keypoints, descriptors = sift.detectAndCompute(gray, None)
                num_keypoints = len(keypoints) if keypoints else 0
            except:
                num_keypoints = 0
                descriptors = None
            
            features = {
                'width': width,
                'height': height,
                'mean_intensity': float(mean_val),
                'std_intensity': float(std_val),
                'histogram': hist.flatten().tolist(),
                'num_keypoints': num_keypoints,
                'has_descriptors': descriptors is not None,
                'file_size': os.path.getsize(template_path)
            }
            
            return features
            
        except Exception as e:
            logging.error(f"特征提取失败: {e}")
            return {}
    
    @staticmethod
    def create_diff_image(image1_path: str, image2_path: str, save_path: str) -> str:
        """
        创建差异图像
        
        Args:
            image1_path: 第一张图像路径
            image2_path: 第二张图像路径
            save_path: 差异图像保存路径
            
        Returns:
            str: 差异图像路径
        """
        try:
            # 读取图像
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            if img1 is None or img2 is None:
                raise ValueError("无法读取图像文件")
            
            # 调整图像大小为相同尺寸
            height = min(img1.shape[0], img2.shape[0])
            width = min(img1.shape[1], img2.shape[1])
            
            img1_resized = cv2.resize(img1, (width, height))
            img2_resized = cv2.resize(img2, (width, height))
            
            # 计算差异
            diff = cv2.absdiff(img1_resized, img2_resized)
            
            # 增强差异显示
            diff_enhanced = cv2.addWeighted(diff, 2.0, np.zeros(diff.shape, dtype=diff.dtype), 0, 0)
            
            # 保存差异图像
            cv2.imwrite(save_path, diff_enhanced)
            
            return save_path
            
        except Exception as e:
            logging.error(f"创建差异图像失败: {e}")
            raise
    
    @staticmethod
    def optimize_template_image(template_path: str, save_path: Optional[str] = None) -> str:
        """
        优化模板图像以提高识别准确性
        
        Args:
            template_path: 原模板图像路径
            save_path: 保存路径，如果为None则覆盖原文件
            
        Returns:
            str: 优化后的图像路径
        """
        try:
            image = cv2.imread(template_path)
            if image is None:
                raise ValueError(f"无法读取图像: {template_path}")
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 应用高斯模糊减少噪声
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # 增强对比度
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(blurred)
            
            # 转换回BGR格式
            result = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            
            output_path = save_path or template_path
            cv2.imwrite(output_path, result)
            
            return output_path
            
        except Exception as e:
            logging.error(f"模板图像优化失败: {e}")
            raise
    
    @staticmethod
    def batch_process_images(image_dir: str, operation: str, **kwargs) -> List[str]:
        """
        批量处理图像
        
        Args:
            image_dir: 图像目录
            operation: 操作类型 ('resize', 'optimize', 'watermark')
            **kwargs: 操作参数
            
        Returns:
            List[str]: 处理后的图像路径列表
        """
        processed_files = []
        
        try:
            # 支持的图像格式
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
            
            for filename in os.listdir(image_dir):
                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    image_path = os.path.join(image_dir, filename)
                    
                    try:
                        if operation == 'resize':
                            target_size = kwargs.get('target_size', (800, 600))
                            processed_path = ImageUtils.resize_image(image_path, target_size)
                            processed_files.append(processed_path)
                            
                        elif operation == 'optimize':
                            processed_path = ImageUtils.optimize_template_image(image_path)
                            processed_files.append(processed_path)
                            
                        elif operation == 'watermark':
                            text = kwargs.get('text', 'Processed')
                            position = kwargs.get('position', 'bottom-right')
                            processed_path = ImageUtils.add_watermark(image_path, text, position)
                            processed_files.append(processed_path)
                            
                    except Exception as e:
                        logging.warning(f"处理图像失败: {filename} - {e}")
            
        except Exception as e:
            logging.error(f"批量处理图像失败: {e}")
        
        return processed_files