import os
import signal
import sys
import webview
from api import NanodrillAPI
import sys

def signal_handler(sig, frame):
    """處理Ctrl+C信號"""
    print("\n正在關閉程式...")
    sys.exit(0)

def on_closed():
    """視窗關閉時的處理"""
    print("視窗已關閉，正在清理資源...")
    sys.exit(0)

def start_app():
    """啟動應用程式"""
    try:
        gui_url = 'http://localhost:5173'
        
        # 設定Ctrl+C信號處理
        signal.signal(signal.SIGINT, signal_handler)
        
        # 初始化API
        api = NanodrillAPI()
        
        window = webview.create_window(
            title='SPM 數據分析器', 
            url=gui_url,
            js_api=api, 
            width=1200, 
            height=800, 
            min_size=(800, 600),
            resizable=True
        )
        
        # 設定視窗關閉時的處理
        window.events.closed += on_closed
        
        # 啟動GUI
        webview.start(debug=True)
    
    except KeyboardInterrupt:
        print("\n接收到中斷信號，正在關閉程式...")
        sys.exit(0)
        
    except Exception as e:
        print(f"程式錯誤: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    start_app()