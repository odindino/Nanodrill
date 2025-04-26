import os
import re
import logging
import numpy as np
import matplotlib
import base64
import io
matplotlib.use('Agg')  # 設置 matplotlib 為非互動模式
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from .parsers.int_parser import IntParser
from .parsers.txt_parser import TxtParser

logger = logging.getLogger(__name__)

class AnalysisService:
    """提供各種數據分析的服務類"""
    
    @staticmethod
    def analyze_int_file(file_path, file_info=None):
        """分析 .int 檔案並回傳圖像數據"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": f"檔案不存在: {file_path}"}
            
            # 提取參數，從 file_info 或者從檔案名字解析
            scale = None
            x_pixels = None
            y_pixels = None
            phys_unit = "nm"  # 預設單位
            
            if file_info:
                if "scale" in file_info:
                    try:
                        scale = float(file_info["scale"])
                    except (ValueError, TypeError):
                        pass
                
                if "physUnit" in file_info:
                    phys_unit = file_info["physUnit"]
                
                if "parameters" in file_info and file_info["parameters"]:
                    params = file_info["parameters"]
                    if "xPixel" in params:
                        try:
                            x_pixels = int(params["xPixel"])
                        except (ValueError, TypeError):
                            pass
                    if "yPixel" in params:
                        try:
                            y_pixels = int(params["yPixel"])
                        except (ValueError, TypeError):
                            pass
            
            # 如果沒提供參數，嘗試從檔案名解析對應的 txt 檔案來獲取參數
            if scale is None or x_pixels is None or y_pixels is None:
                txt_path = AnalysisService._find_corresponding_txt_file(file_path)
                if txt_path:
                    txt_parser = TxtParser(txt_path)
                    try:
                        metadata = txt_parser.parse()
                        
                        # 從 metadata 中獲取 x_pixels 和 y_pixels
                        if x_pixels is None and "xPixel" in metadata:
                            try:
                                x_pixels = int(metadata["xPixel"])
                            except (ValueError, TypeError):
                                pass
                        
                        if y_pixels is None and "yPixel" in metadata:
                            try:
                                y_pixels = int(metadata["yPixel"])
                            except (ValueError, TypeError):
                                pass
                        
                        # 查找對應的檔案描述以獲取 scale 和 phys_unit
                        int_filename = os.path.basename(file_path)
                        for desc in metadata.get('fileDescriptions', []):
                            if desc.get('FileName') == int_filename:
                                if scale is None and 'Scale' in desc:
                                    try:
                                        scale_str = desc['Scale']
                                        scale = float(scale_str)
                                    except (ValueError, TypeError):
                                        pass
                                
                                if 'PhysUnit' in desc:
                                    phys_unit = desc['PhysUnit']
                                
                                break
                    except Exception as e:
                        logger.warning(f"解析 TXT 檔案失敗: {str(e)}")
            
            # 如果仍然沒有參數，使用預設值
            if scale is None:
                scale = 1.0
                logger.warning(f"無法獲取縮放比例，使用預設值 1.0")
            
            if x_pixels is None or y_pixels is None:
                # 預設為 512x512
                x_pixels = 512
                y_pixels = 512
                logger.warning(f"無法獲取像素尺寸，使用預設值 512x512")
            
            # 使用 IntParser 解析檔案
            parser = IntParser(file_path, scale, x_pixels, y_pixels)
            image_data = parser.parse()
            
            # 生成圖像
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(image_data, cmap='viridis')
            fig.colorbar(im, ax=ax, label=f'高度 ({phys_unit})')
            ax.set_title(f'掃描圖像: {os.path.basename(file_path)}')
            ax.set_xlabel('X 像素')
            ax.set_ylabel('Y 像素')
            
            # 將圖像轉為 base64 字符串
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()
            plt.close(fig)
            
            # 計算一些基本統計數據
            stats = {
                "min": float(np.min(image_data)),
                "max": float(np.max(image_data)),
                "mean": float(np.mean(image_data)),
                "median": float(np.median(image_data)),
                "std": float(np.std(image_data)),
                "rms": float(np.sqrt(np.mean(np.square(image_data))))
            }
            
            return {
                "success": True,
                "image": img_base64,
                "statistics": stats,
                "dimensions": {
                    "width": x_pixels,
                    "height": y_pixels
                },
                "physUnit": phys_unit
            }
            
        except Exception as e:
            logger.error(f"分析 INT 檔案時出錯: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _find_corresponding_txt_file(int_file_path):
        """找到與 .int 檔案對應的 .txt 檔案"""
        directory = os.path.dirname(int_file_path)
        basename = os.path.basename(int_file_path)
        
        # 嘗試找出編號部分
        match = re.search(r'(.+?)_(\d+)([^_]*?)\.(int|dat)$', basename, re.IGNORECASE)
        if match:
            prefix = match.group(1)
            number = match.group(2)
            
            # 在同一目錄中尋找可能的 txt 檔案
            for filename in os.listdir(directory):
                if filename.endswith('.txt') and filename.startswith(f"{prefix}_{number}"):
                    return os.path.join(directory, filename)
        
        return None