import os
import webview
import logging

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
    
    def open_folder_dialog(self):
        """打開資料夾選擇對話框"""
        try:
            # 使用 webview 的 create_file_dialog 方法開啟資料夾選擇器
            result = webview.windows[0].create_file_dialog(
                webview.FOLDER_DIALOG
            )
            
            if result and len(result) > 0:
                selected_path = result[0]
                logger.info(f"選擇的資料夾路徑: {selected_path}")
                return {
                    "success": True,
                    "path": selected_path
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
    
    def get_folder_contents(self, folder_path):
        """獲取資料夾內容"""
        try:
            if not os.path.exists(folder_path):
                return {
                    "success": False,
                    "error": "資料夾不存在"
                }
            
            files = []
            directories = []
            
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    files.append(item)
                elif os.path.isdir(item_path):
                    directories.append(item)
            
            return {
                "success": True,
                "path": folder_path,
                "files": files,
                "directories": directories
            }
        except Exception as e:
            logger.error(f"獲取資料夾內容錯誤: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }