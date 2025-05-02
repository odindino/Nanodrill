import os
import re
import logging
import webview
from datetime import datetime
from core.analysis_service import AnalysisService

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
        """獲取資料夾中的所有 .txt、.dat 和 .int 檔案，並排序"""
        try:
            if folder_path is None:
                folder_path = self.current_directory
                
            if not folder_path or not os.path.exists(folder_path):
                return []
                
            files = []
            
            # 獲取所有 .txt、.dat 和 .int 檔案
            for filename in os.listdir(folder_path):
                if filename.endswith(('.txt', '.dat', '.int')):
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
            
            # 檢查是否有相關的 .dat 和 .int 檔案
            basename = os.path.basename(file_path)
            directory = os.path.dirname(file_path)
            file_prefix = basename.rsplit('.', 1)[0]  # 移除副檔名
            
            related_files = []
            
            # 從檔案描述中尋找相關檔案
            if "FileDescriptions" in parameters:
                for desc in parameters["FileDescriptions"]:
                    if "FileName" in desc:
                        rel_filename = desc["FileName"]
                        rel_path = os.path.join(directory, rel_filename)
                        
                        if os.path.exists(rel_path):
                            file_type = rel_filename.split('.')[-1]
                            mod_time = os.path.getmtime(rel_path)
                            
                            related_files.append({
                                "name": rel_filename,
                                "path": rel_path,
                                "type": file_type,
                                "caption": desc.get("Caption", ""),
                                "scale": desc.get("Scale", ""),
                                "physUnit": desc.get("PhysUnit", ""),
                                "modTime": mod_time,
                                "modTimeStr": datetime.fromtimestamp(mod_time).strftime('%Y/%m/%d %H:%M:%S')
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
    
    def get_int_file_preview(self, file_path):
        """獲取與 txt 檔案相關聯的 INT 檔案預覽圖"""
        try:
            # 檢查檔案是否存在
            logger.info(f"嘗試預覽檔案: {file_path}")
            if not os.path.exists(file_path):
                logger.error(f"檔案不存在: {file_path}")
                return {"success": False, "error": f"檔案不存在: {file_path}"}
            
            # 檢查檔案副檔名
            _, ext = os.path.splitext(file_path)
            logger.info(f"檔案副檔名: {ext}")
            
            if ext.lower() != '.int':
                logger.error(f"檔案類型不支援: {ext}")
                return {"success": False, "error": f"檔案類型必須是 .int，而不是 {ext}"}
            
            # 獲取 txt 檔案的內容和參數
            logger.info(f"開始解析 INT 檔案: {file_path}")
            
            # 使用 AnalysisService 來處理 .int 檔案分析
            return AnalysisService.analyze_int_file(file_path)
            
        except Exception as e:
            logger.error(f"獲取 INT 預覽圖時出錯: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": f"獲取預覽圖時發生錯誤: {str(e)}"}
            
    def analyze_int_file(self, file_path, parent_file_info=None):
        """分析 .int 檔案"""
        try:
            # 呼叫 AnalysisService 來處理 .int 檔案分析
            return AnalysisService.analyze_int_file(file_path, parent_file_info)
        except Exception as e:
            logger.error(f"分析 INT 檔案時出錯: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _parse_txt_parameters(self, content):
        """解析 txt 檔案中的參數"""
        parameters = {}
        
        # 提取版本資訊
        version_match = re.search(r'Version\s*:\s*([^\n]+)', content)
        if version_match:
            parameters['Version'] = version_match.group(1).strip()
        
        # 提取日期和時間
        date_match = re.search(r'Date\s*:\s*([^\n]+)', content)
        if date_match:
            parameters['Date'] = date_match.group(1).strip()
        
        time_match = re.search(r'Time\s*:\s*([^\n]+)', content)
        if time_match:
            parameters['Time'] = time_match.group(1).strip()
        
        # 提取用戶名
        username_match = re.search(r'UserName\s*:\s*([^\n]+)', content)
        if username_match:
            parameters['UserName'] = username_match.group(1).strip()
        
        # 提取掃描參數
        scan_params = [
            'SetPoint', 'SetPointPhysUnit', 'FeedBackModus', 'Bias', 'BiasPhysUnit',
            'Ki', 'Kp', 'FeedbackOnCh', 'XScanRange', 'YScanRange', 'XPhysUnit',
            'YPhysUnit', 'Speed', 'LineRate', 'Angle', 'xPixel', 'yPixel',
            'yCenter', 'xCenter', 'LockInFreq', 'LockInFreqPhysUnit', 'LockInAmpl',
            'LockInAmplPhysUnit'
        ]
        
        for param in scan_params:
            pattern = fr'{param}\s*:\s*([^\n]+)'
            match = re.search(pattern, content)
            if match:
                parameters[param] = match.group(1).strip()
        
        # 解析檔案描述區段
        file_descriptions = []
        file_desc_pattern = r'FileDescBegin(.*?)FileDescEnd'
        file_descs = re.findall(file_desc_pattern, content, re.DOTALL)
        
        for desc_content in file_descs:
            desc = {}
            
            # 提取文件名
            filename_match = re.search(r'FileName\s*:\s*([^\n]+)', desc_content)
            if filename_match:
                desc['FileName'] = filename_match.group(1).strip()
            
            # 提取標題
            caption_match = re.search(r'Caption\s*:\s*([^\n]+)', desc_content)
            if caption_match:
                desc['Caption'] = caption_match.group(1).strip()
            
            # 提取比例因子
            scale_match = re.search(r'Scale\s*:\s*([^\n]+)', desc_content)
            if scale_match:
                desc['Scale'] = scale_match.group(1).strip()
            
            # 提取物理單位
            unit_match = re.search(r'PhysUnit\s*:\s*([^\n]+)', desc_content)
            if unit_match:
                desc['PhysUnit'] = unit_match.group(1).strip()
            
            # 提取偏移量
            offset_match = re.search(r'Offset\s*:\s*([^\n]+)', desc_content)
            if offset_match:
                desc['Offset'] = offset_match.group(1).strip()
            
            file_descriptions.append(desc)
        
        parameters['FileDescriptions'] = file_descriptions
        
        return parameters