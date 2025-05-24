import os
import re
import logging
import webview
import numpy as np
from datetime import datetime
from core.analysis_service import AnalysisService
from core.analysis.int_analysis import IntAnalysis
from core.analysis.profile_analysis import ProfileAnalysis

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
    
    def get_int_file_preview(self, txt_file_path, colormap="Oranges"):
        """為預覽獲取與 txt 檔案相關聯的 TopoFwd.int 檔案圖像，並使用指定的色彩映射"""
        try:
            # 檢查 txt 檔案是否存在
            logger.info(f"[預覽] 嘗試預覽檔案: {txt_file_path}")
            if not os.path.exists(txt_file_path):
                logger.error(f"檔案不存在: {txt_file_path}")
                return {"success": False, "error": f"檔案不存在: {txt_file_path}"}
            
            # 檢查檔案副檔名
            _, ext = os.path.splitext(txt_file_path)
            logger.info(f"檔案副檔名: {ext}")
            
            if ext.lower() != '.txt':
                return {"success": False, "error": f"檔案類型必須是 .txt 而不是 {ext}"}
            
            # 獲取 txt 檔案的內容和參數
            try:
                with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # 解析參數
                parameters = self._parse_txt_parameters(content)
                
                # 從檔案描述中尋找 TopoFwd.int 檔案
                topo_file = None
                directory = os.path.dirname(txt_file_path)
                
                if "FileDescriptions" in parameters:
                    for desc in parameters["FileDescriptions"]:
                        if "FileName" in desc and "TopoFwd" in desc["FileName"] and desc["FileName"].lower().endswith(".int"):
                            topo_file_name = desc["FileName"]
                            topo_file_path = os.path.join(directory, topo_file_name)
                            
                            if os.path.exists(topo_file_path):
                                logger.info(f"找到形貌圖檔案: {topo_file_path}")
                                topo_file = {
                                    "path": topo_file_path,
                                    "scale": desc.get("Scale", "1.0"),
                                    "physUnit": desc.get("PhysUnit", "nm")
                                }
                                break
                
                if not topo_file:
                    logger.error(f"找不到相關的 TopoFwd.int 檔案，txt 檔案: {txt_file_path}")
                    return {"success": False, "error": "找不到相關的 TopoFwd.int 檔案"}
                
                # 使用 AnalysisService 來生成預覽圖
                file_info = {
                    "scale": topo_file.get("scale", None),
                    "physUnit": topo_file.get("physUnit", "nm"),
                    "parameters": parameters
                }
                
                logger.info(f"開始生成預覽圖，scale: {file_info['scale']}, unit: {file_info['physUnit']}, colormap: {colormap}")
                
                # 調用 AnalysisService 處理 INT 檔案
                preview_result = AnalysisService.analyze_int_file(topo_file["path"], file_info, colormap)
                
                return preview_result
                
            except Exception as e:
                logger.error(f"解析 TXT 檔案時出錯: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return {"success": False, "error": f"解析 TXT 檔案時出錯: {str(e)}"}
                
        except Exception as e:
            logger.error(f"獲取 INT 預覽圖時出錯: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": f"獲取預覽圖時發生錯誤: {str(e)}"}

    def analyze_int_file_api(self, int_file_path, txt_file_path=None, colormap="Oranges"):
        """分析指定的 INT 檔案，可選提供相關的 TXT 檔案路徑獲取參數"""
        try:
            # 檢查 INT 檔案是否存在
            logger.info(f"[分析] 嘗試分析檔案: {int_file_path}")
            if not os.path.exists(int_file_path):
                logger.error(f"檔案不存在: {int_file_path}")
                return {"success": False, "error": f"檔案不存在: {int_file_path}"}
            
            # 檢查檔案副檔名
            _, ext = os.path.splitext(int_file_path)
            logger.info(f"檔案副檔名: {ext}")
            
            if ext.lower() != '.int':
                return {"success": False, "error": f"檔案類型必須是 .int 而不是 {ext}"}
            
            # 如果提供了 txt 檔案路徑，則從中獲取參數
            parameters = {}
            if txt_file_path and os.path.exists(txt_file_path):
                try:
                    with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    parameters = self._parse_txt_parameters(content)
                    logger.info(f"從 TXT 檔案 {txt_file_path} 獲取參數")
                except Exception as e:
                    logger.warning(f"無法解析 TXT 檔案 {txt_file_path}: {str(e)}")
            else:
                # 尋找可能的 txt 檔案
                directory = os.path.dirname(int_file_path)
                int_filename = os.path.basename(int_file_path)
                
                # 嘗試從檔名獲取 txt 檔案名
                base_name = int_filename.split('_')[0]
                for filename in os.listdir(directory):
                    if filename.endswith('.txt') and filename.startswith(base_name):
                        txt_file_path = os.path.join(directory, filename)
                        try:
                            with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            parameters = self._parse_txt_parameters(content)
                            logger.info(f"自動找到並從 TXT 檔案 {txt_file_path} 獲取參數")
                            break
                        except Exception as e:
                            logger.warning(f"無法解析 TXT 檔案 {txt_file_path}: {str(e)}")
            
            # 從檔案描述中尋找本 int 檔的比例尺
            scale = None
            phys_unit = "nm"
            
            if "FileDescriptions" in parameters:
                int_filename = os.path.basename(int_file_path)
                for desc in parameters["FileDescriptions"]:
                    if "FileName" in desc and desc["FileName"] == int_filename:
                        if "Scale" in desc:
                            try:
                                scale = float(desc["Scale"])
                                logger.info(f"從 TXT 檔案找到比例尺: {scale}")
                            except (ValueError, TypeError):
                                logger.warning(f"無法轉換比例尺: {desc['Scale']}")
                        
                        if "PhysUnit" in desc:
                            phys_unit = desc["PhysUnit"]
                            logger.info(f"從 TXT 檔案找到物理單位: {phys_unit}")
                        
                        break
            
            # 獲取像素數量
            x_pixel = int(parameters.get("xPixel", 512))
            y_pixel = int(parameters.get("yPixel", 512))
            
            # 準備檔案資訊
            file_info = {
                "scale": scale,
                "physUnit": phys_unit,
                "parameters": parameters
            }
            
            # 使用 AnalysisService 來處理 .int 檔案分析
            logger.info(f"開始分析 INT 檔案，scale: {scale}, unit: {phys_unit}, colormap: {colormap}")
            return AnalysisService.analyze_int_file(int_file_path, file_info, colormap)
            
        except Exception as e:
            logger.error(f"分析 INT 檔案時出錯: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": f"分析 INT 檔案時發生錯誤: {str(e)}"}
            
    def analyze_int_file(self, file_path, parent_file_info=None, colormap="Oranges"):
        """分析 .int 檔案，使用指定的色彩映射"""
        try:
            # 呼叫 AnalysisService 來處理 .int 檔案分析
            return AnalysisService.analyze_int_file(file_path, parent_file_info, colormap)
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
    
    def apply_flatten(self, image_data, method="mean", degree=1):
        """應用平面化處理
        
        Args:
            image_data: 2D數組形式的圖像數據
            method: 平面化方法 ("mean", "polyfit" 或 "plane")
            degree: 使用 polyfit 方法時的多項式階數
        
        Returns:
            包含處理後數據的字典
        """
        try:
            # 將前端發送的數據轉換為numpy數組
            image_data_array = np.array(image_data)
            
            # 根據方法選擇不同的平面化處理
            if method == "mean":
                result = IntAnalysis.linewise_flatten_mean(image_data_array)
            elif method == "polyfit":
                result = IntAnalysis.linewise_flatten_polyfit(image_data_array, deg=degree)
            elif method == "plane":
                result = IntAnalysis.plane_flatten(image_data_array)
            else:
                return {"success": False, "error": f"未知的平面化方法: {method}"}
            
            # 將處理結果轉換回列表格式，以便前端使用
            result_list = result.tolist()
            
            # 計算基本統計數據
            stats = {
                "min": float(np.min(result)),
                "max": float(np.max(result)),
                "mean": float(np.mean(result)),
                "median": float(np.median(result)),
                "std": float(np.std(result)),
                "rms": float(np.sqrt(np.mean(np.square(result - np.mean(result)))))
            }
            
            return {
                "success": True,
                "processed_data": result_list,
                "statistics": stats
            }
        except Exception as e:
            logger.error(f"平面化處理失敗: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
        
    def tilt_image(self, image_data, direction, fine_tune=False):
        """應用影像傾斜調整
        
        Args:
            image_data: 2D數組形式的圖像數據
            direction: 傾斜方向 ("up", "down", "left", "right")
            fine_tune: 是否為微調模式
        
        Returns:
            包含處理後數據的字典
        """
        try:
            # 將前端發送的數據轉換為numpy數組
            image_data_array = np.array(image_data)
            
            # 應用傾斜調整
            result = IntAnalysis.tilt_image(image_data_array, direction, fine_tune=fine_tune)
            
            # 將處理結果轉換回列表格式
            result_list = result.tolist()
            
            # 計算基本統計數據
            stats = {
                "min": float(np.min(result)),
                "max": float(np.max(result)),
                "mean": float(np.mean(result)),
                "median": float(np.median(result)),
                "std": float(np.std(result)),
                "rms": float(np.sqrt(np.mean(np.square(result - np.mean(result)))))
            }
            
            return {
                "success": True,
                "processed_data": result_list,
                "statistics": stats
            }
        except Exception as e:
            logger.error(f"傾斜調整失敗: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    def get_line_profile(self, image_data, start_point, end_point, physical_scale=1.0, shift_zero=False):
        """獲取線性剖面數據和圖像"""
        try:
            # 將前端發送的數據轉換為numpy數組
            image_data_array = np.array(image_data)
            
            # 獲取剖面數據
            profile_data = IntAnalysis.get_line_profile(
                image_data_array, 
                start_point, 
                end_point, 
                physical_scale
            )
            
            # 生成剖面圖像
            profile_image = IntAnalysis.generate_profile_image(
                profile_data, 
                shift_zero=shift_zero
            )
            
            # 計算粗糙度參數
            roughness = ProfileAnalysis.calculate_roughness(profile_data['height'])
            
            return {
                "success": True,
                "profile_data": profile_data,
                "profile_image": profile_image,
                "roughness": roughness
            }
        except Exception as e:
            logger.error(f"獲取剖面失敗: {str(e)}")
            return {"success": False, "error": str(e)}
        
    # analyze_int_file_api 方法已在前方定義，此處刪除重複的方法
        
    def update_profile(self, profile_data, shift_zero=False, auto_scale=True, show_peaks=False, peak_sensitivity=1.0):
        """更新剖面圖設置"""
        try:
            from core.analysis.profile_analysis import ProfileAnalysis
            
            # 生成剖面圖像
            profile_image = ProfileAnalysis.generate_profile_image(
                profile_data,
                shift_zero=shift_zero,
                auto_scale=auto_scale,
                show_peaks=show_peaks,
                peak_sensitivity=peak_sensitivity
            )
            
            return {
                "success": True,
                "profile_image": profile_image
            }
        except Exception as e:
            logger.error(f"更新剖面圖失敗: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}