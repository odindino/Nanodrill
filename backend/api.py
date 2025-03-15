import os
import re
import logging
import webview
from datetime import datetime

# 設置日誌
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

class NanodrillAPI:
    """SPM 數據分析器的後端 API 類別"""
    
    def __init__(self):
        """初始化 API"""
        self.window = None
        self.current_directory = ""
    
    def open_folder_dialog(self):
        """打開資料夾選擇對話框"""
        try:
            # 使用 webview 的 create_file_dialog 方法開啟資料夾選擇器
            result = webview.windows[0].create_file_dialog(
                webview.FOLDER_DIALOG
            )
            
            if result and len(result) > 0:
                selected_path = result[0]
                self.current_directory = selected_path
                logger.info(f"選擇的資料夾路徑: {selected_path}")
                
                # 獲取資料夾中的檔案
                files = self.get_folder_files(selected_path)
                
                return {
                    "success": True,
                    "directory": selected_path,
                    "files": files
                }
            else:
                logger.info("沒有選擇資料夾")
                return {
                    "success": False,
                    "message": "沒有選擇資料夾"
                }
        except Exception as e:
            logger.error(f"開啟資料夾對話框錯誤: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_folder_files(self, folder_path=None):
        """獲取資料夾中的所有 .txt 和 .dat 檔案，並排序"""
        try:
            if folder_path is None:
                folder_path = self.current_directory
                
            if not folder_path or not os.path.exists(folder_path):
                return []
                
            files = []
            
            # 獲取所有 .txt 和 .dat 檔案
            for filename in os.listdir(folder_path):
                if filename.endswith('.txt') or filename.endswith('.dat'):
                    file_path = os.path.join(folder_path, filename)
                    
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
            
            return files
        except Exception as e:
            logger.error(f"獲取資料夾檔案時出錯: {str(e)}")
            return []
    
    def get_txt_file_content(self, file_path):
        """獲取 txt 檔案的內容及其相關檔案"""
        try:
            # 確保檔案存在
            if not os.path.exists(file_path):
                return {"success": False, "error": f"檔案不存在: {file_path}"}
            
            # 讀取 txt 檔案內容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 解析基本參數
            parameters = self._parse_txt_parameters(content)
            
            # 檢查是否有相關的 .dat 檔案
            basename = os.path.basename(file_path)
            number_match = re.search(r'_(\d+)\.', basename)
            
            related_files = []
            if number_match:
                file_number = number_match.group(1)
                directory = os.path.dirname(file_path)
                
                # 尋找同編號的 .dat 檔案
                for filename in os.listdir(directory):
                    if filename.endswith('.dat') and f"_{file_number}." in filename:
                        related_files.append({
                            "name": filename,
                            "path": os.path.join(directory, filename),
                            "type": "dat"
                        })
            
            return {
                "success": True,
                "content": content,
                "parameters": parameters,
                "relatedFiles": related_files
            }
        except Exception as e:
            logger.error(f"獲取 TXT 檔案內容時出錯: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _parse_txt_parameters(self, content):
        """解析 txt 檔案中的參數"""
        parameters = {}
        
        # 常見的參數
        param_patterns = {
            "Version": r'Version\s*:\s*([^\n]+)',
            "Date": r'Date\s*:\s*([^\n]+)',
            "Time": r'Time\s*:\s*([^\n]+)',
            "UserName": r'UserName\s*:\s*([^\n]+)',
            "SetPoint": r'SetPoint\s*:\s*([^\n]+)',
            "Bias": r'Bias\s*:\s*([^\n]+)',
            "BiasPhysUnit": r'BiasPhysUnit\s*:\s*([^\n]+)',
            "XScanRange": r'XScanRange\s*:\s*([^\n]+)',
            "YScanRange": r'YScanRange\s*:\s*([^\n]+)',
            "XPhysUnit": r'XPhysUnit\s*:\s*([^\n]+)',
            "YPhysUnit": r'YPhysUnit\s*:\s*([^\n]+)',
            "xPixel": r'xPixel\s*:\s*([^\n]+)',
            "yPixel": r'yPixel\s*:\s*([^\n]+)',
        }
        
        for key, pattern in param_patterns.items():
            match = re.search(pattern, content)
            if match:
                parameters[key] = match.group(1).strip()
        
        # 解析檔案描述區段
        file_descs = []
        file_desc_pattern = r'FileDescBegin(.*?)FileDescEnd'
        file_desc_matches = re.findall(file_desc_pattern, content, re.DOTALL)
        
        for desc_content in file_desc_matches:
            desc = {}
            
            # 提取文件名和其他參數
            filename_match = re.search(r'FileName\s*:\s*([^\n]+)', desc_content)
            if filename_match:
                desc["FileName"] = filename_match.group(1).strip()
            
            caption_match = re.search(r'Caption\s*:\s*([^\n]+)', desc_content)
            if caption_match:
                desc["Caption"] = caption_match.group(1).strip()
            
            scale_match = re.search(r'Scale\s*:\s*([^\n]+)', desc_content)
            if scale_match:
                desc["Scale"] = scale_match.group(1).strip()
            
            phys_unit_match = re.search(r'PhysUnit\s*:\s*([^\n]+)', desc_content)
            if phys_unit_match:
                desc["PhysUnit"] = phys_unit_match.group(1).strip()
            
            file_descs.append(desc)
        
        parameters["FileDescriptions"] = file_descs
        
        return parameters