// src/stores/analysisStore.ts

import { defineStore } from 'pinia';
import { AnalysisService } from '../services/analysisService';

export interface Dimensions {
  width: number;
  height: number;
  xRange: number;
  yRange: number;
}

export const useAnalysisStore = defineStore('analysis', {
  state: () => ({
    // 當前選擇的文件
    selectedFileId: '',
    currentFileName: '',
    
    // 載入狀態
    isLoading: false,
    errorMessage: '',
    
    // 圖像數據
    imageData: null as string | null,
    imageRawData: null as number[][] | null,
    dimensions: { width: 0, height: 0, xRange: 0, yRange: 0 } as Dimensions,
    physUnit: 'nm',
    
    // 剖面數據
    profileData: null as any | null,
    roughness: null as any | null,
    
    // 測量模式
    measureMode: false,
  }),
  
  actions: {
    /**
     * 選擇文件
     */
    selectFile(fileId: string, fileName: string) {
      this.selectedFileId = fileId;
      this.currentFileName = fileName;
    },
    
    /**
     * 載入選中的文件
     */
    async loadSelectedFile() {
      if (!this.selectedFileId) return;
      
      try {
        this.isLoading = true;
        this.errorMessage = '';
        
        const response = await AnalysisService.loadIntFile(this.selectedFileId);
        
        if (response.success) {
          this.imageData = response.image;
          this.imageRawData = response.rawData;
          this.dimensions = response.dimensions || { width: 512, height: 512, xRange: 100, yRange: 100 };
          this.physUnit = response.physUnit || 'nm';
          
          // 清除剖面數據
          this.profileData = null;
          this.roughness = null;
        } else {
          this.errorMessage = response.error || '載入文件失敗';
        }
      } catch (error) {
        this.errorMessage = `載入文件時發生錯誤: ${error}`;
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 處理線性剖面
     */
    async handleLineProfile(data: any) {
      try {
        this.isLoading = true;
        
        const response = await AnalysisService.getLineProfile(
          data.sourceData.imageRawData,
          data.startPoint,
          data.endPoint,
          data.sourceData.dimensions?.xRange || 100,
          false // 不偏移到零
        );
        
        if (response.success) {
          this.profileData = response.profile_data;
          this.roughness = response.roughness;
          
          // 關閉測量模式
          this.measureMode = false;
        } else {
          this.errorMessage = response.error || '獲取剖面失敗';
        }
      } catch (error) {
        this.errorMessage = `處理剖面時發生錯誤: ${error}`;
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 切換測量模式
     */
    toggleMeasureMode() {
      this.measureMode = !this.measureMode;
    },
    
    /**
     * 清除錯誤消息
     */
    clearError() {
      this.errorMessage = '';
    }
  }
});