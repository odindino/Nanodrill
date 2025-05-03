# backend/core/analysis/int_analysis.py
import numpy as np
import logging
from scipy import ndimage, fftpack
import matplotlib.pyplot as plt
import io
import base64

logger = logging.getLogger(__name__)

class IntAnalysis:
    """
    提供SPM .int檔案的各種分析功能
    
    這個類提供各種形貌圖的分析工具，包括平面化、傾斜調整、線性剖面等功能。
    所有方法都設計為不改變原始數據，而是返回處理後的新數據。
    """
    
    @staticmethod
    def linewise_flatten_mean(image_data):
        """
        按行減去均值進行平面化
        
        Args:
            image_data: 2D numpy數組，形貌數據
            
        Returns:
            2D numpy數組，平面化後的數據
        """
        try:
            result = image_data.copy()
            for i in range(len(result)):
                result[i] -= np.mean(result[i])
            return result
        except Exception as e:
            logger.error(f"線性平面化(均值)失敗: {str(e)}")
            return image_data
    
    @staticmethod
    def linewise_flatten_polyfit(image_data, deg=1):
        """
        按行使用多項式擬合進行平面化
        
        Args:
            image_data: 2D numpy數組，形貌數據
            deg: 多項式階數
            
        Returns:
            2D numpy數組，平面化後的數據
        """
        try:
            result = image_data.copy()
            y_size, x_size = result.shape
            x = np.arange(x_size)
            
            for i in range(y_size):
                fit = np.polyfit(x, result[i], deg)
                poly = np.poly1d(fit)
                result[i] -= poly(x)
            
            return result
        except Exception as e:
            logger.error(f"線性平面化(多項式)失敗: {str(e)}")
            return image_data
    
    @staticmethod
    def plane_flatten(image_data):
        """
        全局平面擬合並去除平面
        
        Args:
            image_data: 2D numpy數組，形貌數據
            
        Returns:
            2D numpy數組，平面化後的數據
        """
        try:
            result = image_data.copy()
            y_size, x_size = result.shape
            
            # 創建坐標網格
            x, y = np.meshgrid(np.arange(x_size), np.arange(y_size))
            x = x.flatten()
            y = y.flatten()
            z = result.flatten()
            
            # 擬合平面 z = ax + by + c
            A = np.column_stack((x, y, np.ones_like(x)))
            coeffs, _, _, _ = np.linalg.lstsq(A, z, rcond=None)
            
            # 根據擬合結果創建平面
            plane = coeffs[0] * x.reshape(y_size, x_size) + coeffs[1] * y.reshape(y_size, x_size) + coeffs[2]
            
            # 從原始數據中減去平面
            result -= plane
            
            return result
        except Exception as e:
            logger.error(f"平面擬合失敗: {str(e)}")
            return image_data
    
    @staticmethod
    def tilt_image(image_data, direction, step_size=10, fine_tune=False):
        """
        調整影像傾斜
        
        Args:
            image_data: 2D numpy數組，形貌數據
            direction: 傾斜方向 ('up', 'down', 'left', 'right')
            step_size: 調整步長
            fine_tune: 是否為微調模式
            
        Returns:
            2D numpy數組，調整後的數據
        """
        try:
            result = image_data.copy()
            y_size, x_size = result.shape
            
            # 計算調整變化量
            zmin, zmax = np.min(result), np.max(result)
            dh = (zmax - zmin) / (50 if fine_tune else 10)
            
            # 創建坐標網格
            y, x = np.meshgrid(np.arange(x_size), np.arange(y_size))
            
            # 計算中心點
            center_x = (x_size - 1) / 2
            center_y = (y_size - 1) / 2
            
            # 創建調整矩陣
            if direction in ('up', 'down'):
                dhMatrix = dh * (x - center_y) / center_y
                if direction == 'up':
                    result += dhMatrix
                else:  # direction == 'down'
                    result -= dhMatrix
            elif direction in ('left', 'right'):
                dhMatrix = dh * (y - center_x) / center_x
                if direction == 'left':
                    result += dhMatrix
                else:  # direction == 'right'
                    result -= dhMatrix
            
            return result
        except Exception as e:
            logger.error(f"傾斜調整失敗: {str(e)}")
            return image_data
    
    @staticmethod
    def get_line_profile(image_data, start_point, end_point, physical_scale=1.0):
        """
        獲取兩點間的線性剖面
        
        Args:
            image_data: 2D numpy數組，形貌數據
            start_point: 起始點座標 (y, x)
            end_point: 終止點座標 (y, x)
            physical_scale: 物理單位尺度 (nm/pixel)
            
        Returns:
            dict: 包含剖面數據的字典
                - 'distance': 距離數組
                - 'height': 高度數組
                - 'length': 剖面總長度
                - 'stats': 統計數據
        """
        try:
            # 確保點座標在圖像範圍內
            y_size, x_size = image_data.shape
            start_y, start_x = max(0, min(start_point[0], y_size-1)), max(0, min(start_point[1], x_size-1))
            end_y, end_x = max(0, min(end_point[0], y_size-1)), max(0, min(end_point[1], x_size-1))
            
            # 計算剖面點數 (適當密度)
            length = np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
            num_points = int(np.ceil(length)) * 2  # 確保足夠的取樣點
            
            # 生成剖面點
            y_indices = np.linspace(start_y, end_y, num_points)
            x_indices = np.linspace(start_x, end_x, num_points)
            
            # 用雙線性插值獲取對應高度值
            zi = ndimage.map_coordinates(image_data, [y_indices, x_indices], order=1)
            
            # 物理距離
            physical_length = length * physical_scale
            distances = np.linspace(0, physical_length, num_points)
            
            # 計算統計數據
            stats = {
                'min': float(np.min(zi)),
                'max': float(np.max(zi)),
                'mean': float(np.mean(zi)),
                'median': float(np.median(zi)),
                'std': float(np.std(zi)),
                'range': float(np.max(zi) - np.min(zi)),
                'rms': float(np.sqrt(np.mean(np.square(zi - np.mean(zi)))))
            }
            
            return {
                'distance': distances.tolist(),
                'height': zi.tolist(),
                'length': float(physical_length),
                'stats': stats
            }
        except Exception as e:
            logger.error(f"獲取剖面失敗: {str(e)}")
            return {
                'distance': [],
                'height': [],
                'length': 0,
                'stats': {}
            }
    
    @staticmethod
    def generate_profile_image(profile_data, shift_zero=False, title="Line Profile"):
        """
        生成剖面圖像
        
        Args:
            profile_data: 剖面數據字典
            shift_zero: 是否將最小值歸零
            title: 圖像標題
            
        Returns:
            base64編碼的PNG圖像
        """
        try:
            x = np.array(profile_data['distance'])
            z = np.array(profile_data['height'])
            
            # 是否將最小值歸零
            if shift_zero and len(z) > 0:
                z = z - np.min(z)
            
            # 創建圖像
            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            ax.plot(x, z, '-', linewidth=1.5)
            
            # 設置標題和標籤
            ax.set_title(title)
            ax.set_xlabel('Distance (nm)')
            ax.set_ylabel('Height (nm)')
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # 添加一些統計信息
            if 'stats' in profile_data and profile_data['stats']:
                stats = profile_data['stats']
                stat_text = f"Range: {stats['range']:.2f} nm, RMS: {stats['rms']:.2f} nm"
                ax.annotate(stat_text, xy=(0.02, 0.02), xycoords='axes fraction', 
                           fontsize=8, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
            
            # 轉換為PNG圖像
            buf = io.BytesIO()
            fig.tight_layout()
            fig.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            img_data = buf.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            buf.close()
            plt.close(fig)
            
            return img_base64
        except Exception as e:
            logger.error(f"生成剖面圖像失敗: {str(e)}")
            return ""