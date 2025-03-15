/// <reference types="vite/client" />

// 定義 window.pywebview 接口
declare global {
    interface Window {
      pywebview?: {
        api: {
          open_file_dialog: () => Promise<any>;
          process_selected_file: (filePath: string) => Promise<any>;
          get_txt_file_content: (filePath: string) => Promise<any>;
          load_int_file: (intFilePath: string, parameters: Record<string, any>) => Promise<any>;
        }
      }
    }
  }