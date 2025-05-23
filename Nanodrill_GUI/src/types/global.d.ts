// global.d.ts - 全局類型定義

declare global {
  interface Window {
    pywebview: {
      api: {
        // 文件操作
        open_folder_dialog: () => Promise<any>;
        get_folder_files: (path: string) => Promise<any>;
        get_txt_file_content: (path: string) => Promise<any>;
        get_int_file_preview: (path: string) => Promise<any>;
        
        // 分析功能
        analyze_int_file_api: (filePath: string) => Promise<any>;
        get_line_profile: (
          imageData: number[][], 
          startPoint: number[], 
          endPoint: number[], 
          scale: number, 
          shiftZero?: boolean
        ) => Promise<any>;
        update_profile: (
          profileData: any, 
          shiftZero?: boolean, 
          autoScale?: boolean, 
          showPeaks?: boolean, 
          peakSensitivity?: number
        ) => Promise<any>;
        
        // 水平調整功能
        apply_flatten: (
          imageData: number[][], 
          method: string, 
          degree?: number
        ) => Promise<any>;
        tilt_image: (
          imageData: number[][], 
          direction: string, 
          fineTune?: boolean
        ) => Promise<any>;
      };
    };
  }
}

export {};
