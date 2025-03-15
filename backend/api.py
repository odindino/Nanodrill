import os
import json
import re
import numpy as np
import base64
import io
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime
import logging
import traceback
import webview  # 添加webview導入

# 設置日誌
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

from core.parsers.txt_parser import TxtParser
from core.parsers.int_parser import IntParser

class API:
    """後端 API 類別，提供前端所需的所有方法"""
    
    def __init__(self):
        self.window = None
        self.current_data = {}
        self.current_directory = ""
    
    def set_window(self, window):
        """設置 webview 窗口引用"""
        self.window = window
    
    def open_file_dialog(self):
        """打開檔案對話框以選擇檔案"""
        try:
            result = self.window.create_file_dialog(webview.OPEN_DIALOG, 
                                                   allow_multiple=False, 
                                                   file_types=('SPM 檔案 (*.txt;*.int;*.dat)', '*.txt;*.int;*.dat'))
            
            if result and len(result) > 0:
                file_path = result[0]
                return self.process_selected_file(file_path)
            return {"success": False, "message": "未選擇檔案"}
        except Exception as e:
            logger.error(f"開啟檔案對話框錯誤: {str(e)}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    def process_selected_file(self, file_path):
        """處理選定的檔案，掃描資料夾並返回檔案列表"""
        try:
            directory = os.path.dirname(file_path)
            self.current_directory = directory
            
            # 獲取資料夾中所有檔案
            all_files = self._get_folder_files(directory)
            
            # 構建回應
            response = {
                "success": True,
                "directory": directory,
                "selectedFile": os.path.basename(file_path),
                "files": all_files
            }
            
            # 如果是 txt 檔案，解析它以獲取相關聯的檔案
            if file_path.endswith('.txt'):
                txt_info = self._parse_txt_file(file_path)
                if txt_info:
                    response["txtInfo"] = txt_info
            
            return response
        except Exception as e:
            logger.error(f"處理選定檔案時出錯: {str(e)}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    def _get_folder_files(self, directory):
        """獲取資料夾中的所有 .txt 和 .dat 檔案，並排序"""
        files = []
        
        try:
            # 獲取所有 .txt 和 .dat 檔案
            for filename in os.listdir(directory):
                if filename.endswith('.txt') or filename.endswith('.dat'):
                    file_path = os.path.join(directory, filename)
                    
                    # 嘗試從檔名中提取編號
                    number_match = re.search(r'_(\d+)\.', filename)
                    number = int(number_match.group(1)) if number_match else 0
                    
                    # 獲取檔案修改時間
                    mod_time = os.path.getmtime(file_path)
                    
                    # 添加到檔案列表
                    files.append({
                        "name": filename,
                        "path": file_path,
                        "number": number,
                        "type": filename.split('.')[-1],
                        "modTime": mod_time,
                        "modTimeStr": datetime.fromtimestamp(mod_time).strftime('%Y/%m/%d %H:%M:%S')
                    })
            
            # 首先按編號排序，然後按修改時間排序
            files.sort(key=lambda x: (x['number'], x['modTime']))
            
            return files
        except Exception as e:
            logger.error(f"獲取資料夾檔案時出錯: {str(e)}")
            logger.error(traceback.format_exc())
            return []
    
    def _parse_txt_file(self, file_path):
        """解析 .txt 檔案以獲取參數和相關檔案"""
        try:
            parser = TxtParser(file_path)
            metadata = parser.parse()
            
            if metadata:
                return {
                    "parameters": metadata,
                    "fileDescriptions": parser.get_file_descriptions()
                }
            return None
        except Exception as e:
            logger.error(f"解析 TXT 檔案時出錯: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def get_txt_file_content(self, file_path):
        """獲取 txt 檔案的內容及其相關檔案"""
        try:
            # 確保檔案存在
            if not os.path.exists(file_path):
                return {"success": False, "error": f"檔案不存在: {file_path}"}
            
            # 解析 txt 檔案
            parser = TxtParser(file_path)
            metadata = parser.parse()
            file_descriptions = parser.get_file_descriptions()
            
            return {
                "success": True,
                "metadata": metadata,
                "fileDescriptions": file_descriptions
            }
        except Exception as e:
            logger.error(f"獲取 TXT 檔案內容時出錯: {str(e)}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    def load_int_file(self, int_file_path, metadata):
        """載入並解析 .int 檔案，返回圖像資料"""
        try:
            # 從 metadata 中提取所需參數
            x_pixel = int(metadata.get('xPixel', 0))
            y_pixel = int(metadata.get('yPixel', 0))
            
            # 查找對應的 Scale 參數
            scale = None
            filename = os.path.basename(int_file_path)
            
            for file_desc in metadata.get('fileDescriptions', []):
                if filename.endswith(file_desc.get('FileName', '')):
                    scale = float(file_desc.get('Scale', 0))
                    break
            
            if not scale:
                return {"success": False, "error": "無法找到圖像比例因子"}
            
            # 使用 IntParser 解析 .int 檔案
            parser = IntParser(int_file_path, scale, x_pixel, y_pixel)
            image_data = parser.parse()
            
            # 創建圖像並轉換為 base64
            fig, ax = plt.subplots(figsize=(8, 8))
            
            # 使用適合 SPM 數據的顏色映射
            cmap = plt.cm.viridis
            im = ax.imshow(image_data, cmap=cmap, origin='lower')
            
            # 添加標題和軸標籤
            title = os.path.basename(int_file_path).replace('.int', '')
            ax.set_title(title)
            
            # 設置軸單位
            x_unit = metadata.get('XPhysUnit', 'nm')
            y_unit = metadata.get('YPhysUnit', 'nm')
            
            x_scan_range = float(metadata.get('XScanRange', 0))
            y_scan_range = float(metadata.get('YScanRange', 0))
            
            # 設置刻度標籤
            ax.set_xlabel(f'{x_unit}')
            ax.set_ylabel(f'{y_unit}')
            
            # 創建刻度
            x_ticks = np.linspace(0, x_pixel-1, 5)
            y_ticks = np.linspace(0, y_pixel-1, 5)
            
            x_tick_labels = np.linspace(0, x_scan_range, 5)
            y_tick_labels = np.linspace(0, y_scan_range, 5)
            
            ax.set_xticks(x_ticks)
            ax.set_yticks(y_ticks)
            
            ax.set_xticklabels([f'{x:.1f}' for x in x_tick_labels])
            ax.set_yticklabels([f'{y:.1f}' for y in y_tick_labels])
            
            # 添加顏色條
            cbar = plt.colorbar(im, ax=ax)
            unit = metadata.get('ZPhysUnit', 'nm')
            cbar.set_label(unit)
            
            # 轉換為 base64 字符串
            buf = io.BytesIO()
            plt.tight_layout()
            fig.savefig(buf, format='png', dpi=100)
            plt.close(fig)
            buf.seek(0)
            
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            
            return {
                "success": True,
                "imageData": img_base64,
                "dimensions": {
                    "width": x_pixel,
                    "height": y_pixel,
                    "xRange": x_scan_range,
                    "yRange": y_scan_range,
                    "xUnit": x_unit,
                    "yUnit": y_unit
                },
                "rawData": image_data.tolist()  # 發送原始數據以便進一步處理
            }
        except Exception as e:
            logger.error(f"載入 INT 檔案時出錯: {str(e)}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}