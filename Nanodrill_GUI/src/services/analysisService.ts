// src/services/analysisService.ts

/**
 * 分析服務類 - 處理與後端 API 的所有交互
 */
export class AnalysisService {
    /**
     * 載入 INT 文件
     * @param filePath INT 文件路徑
     * @returns 返回分析結果
     */
    static async loadIntFile(filePath: string) {
      try {
        return await window.pywebview.api.analyze_int_file_api(filePath);
      } catch (error) {
        console.error('載入 INT 文件失敗:', error);
        throw error;
      }
    }
    
    /**
     * 獲取線性剖面數據
     * @param imageData 圖像數據
     * @param startPoint 起始點
     * @param endPoint 終止點
     * @param scale 物理尺度
     * @param shiftZero 是否將最小值歸零
     * @returns 返回剖面數據
     */
    static async getLineProfile(imageData: number[][], startPoint: number[], endPoint: number[], scale: number, shiftZero = false) {
      try {
        return await window.pywebview.api.get_line_profile(imageData, startPoint, endPoint, scale, shiftZero);
      } catch (error) {
        console.error('獲取線性剖面失敗:', error);
        throw error;
      }
    }
    
    /**
     * 更新剖面圖設置
     * @param profileData 剖面數據
     * @param settings 設置選項
     * @returns 返回更新後的剖面圖
     */
    static async updateProfile(profileData: any, shiftZero = false, autoScale = true, showPeaks = false, peakSensitivity = 1.0) {
      try {
        return await window.pywebview.api.update_profile(
          profileData,
          shiftZero,
          autoScale,
          showPeaks,
          peakSensitivity
        );
      } catch (error) {
        console.error('更新剖面圖失敗:', error);
        throw error;
      }
    }

    /**
     * 應用平面化處理
     * @param imageData 圖像數據
     * @param method 平面化方法 ("mean", "polyfit", "plane")
     * @param degree 多項式階數（當方法為polyfit時使用）
     * @returns 返回處理後的數據
     */
    static async applyFlatten(imageData: number[][], method: 'mean' | 'polyfit' | 'plane' = 'mean', degree = 1) {
      try {
        return await window.pywebview.api.apply_flatten(imageData, method, degree);
      } catch (error) {
        console.error('平面化處理失敗:', error);
        throw error;
      }
    }

    /**
     * 應用影像傾斜調整
     * @param imageData 圖像數據
     * @param direction 傾斜方向 ("up", "down", "left", "right")
     * @param fineTune 是否為微調模式
     * @returns 返回處理後的數據
     */
    static async tiltImage(imageData: number[][], direction: 'up' | 'down' | 'left' | 'right', fineTune = false) {
      try {
        return await window.pywebview.api.tilt_image(imageData, direction, fineTune);
      } catch (error) {
        console.error('傾斜調整失敗:', error);
        throw error;
      }
    }
  }