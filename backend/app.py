import os
import sys
import webview
from api import API

def get_entrypoint():
    """獲取前端入口點"""
    if sys.platform.startswith('win'):
        return os.path.join(os.path.dirname(__file__), '..', 'dist', 'index.html')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dist', 'index.html')

def start_app():
    """啟動應用程式"""
    api = API()
    
    # 開發模式或生產模式
    dev_mode = '--dev' in sys.argv
    
    if dev_mode:
        # 開發模式下使用 Vue 開發伺服器
        url = 'http://localhost:5173'
    else:
        # 生產模式下使用構建的靜態文件
        url = get_entrypoint()
    
    window = webview.create_window(
        'SPM 數據分析器', 
        url,
        js_api=api, 
        width=1200, 
        height=800, 
        min_size=(800, 600)
    )
    api.set_window(window)
    webview.start(debug=True)

if __name__ == '__main__':
    start_app()