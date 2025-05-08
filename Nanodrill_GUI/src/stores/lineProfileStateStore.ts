// src/stores/lineProfileStateStore.ts
import { defineStore } from 'pinia';

export interface Point {
  x: number;
  y: number;
  z: number;
}

export interface ProfilePoint {
  distance: number;
  height: number;
}

export interface HoverData {
  x: number;
  y: number;
  z: number;
  curveNumber?: number;
  pointNumber?: number;
  pointIndex?: number[];
}

// 測量狀態枚舉
export enum LineProfileState {
  IDLE = 0,             // 未開始測量
  SELECTING_END = 1,    // 已選起點，正在選終點（滑鼠追蹤中）
  COMPLETED = 2         // 測量完成
}

export const useLineProfileStateStore = defineStore('lineProfileState', {
  state: () => ({
    // 是否在圖表區域內
    inPlotArea: false,
    // 測量狀態 (0: 未測量, 1: 選擇終點/跟隨滑鼠, 2: 測量完成)
    lineProfileMeasureState: LineProfileState.IDLE,
    // 起點座標 {x, y, z}
    startPoint: null as Point | null,
    // 當前滑鼠位置 {x, y, z}
    currentPoint: null as Point | null,
    // 終點座標 {x, y, z}
    endPoint: null as Point | null,
    // 當前 hover 數據
    hoverData: null as HoverData | null,
    // 當前活動的 ImageViewer ID
    activeImageViewerId: null as string | null,
    // 目標 ProfileViewer ID
    targetProfileViewerId: null as string | null,
    // 剖面數據
    profileData: null as ProfilePoint[] | null,
  }),

  actions: {
    // 設置圖表區域狀態
    setInPlotArea(value: boolean) {
      this.inPlotArea = value;
    },
    
    // 更新 hover 數據
    updateHoverData(data: HoverData | null) {
      this.hoverData = data;
      if (data && this.lineProfileMeasureState === LineProfileState.SELECTING_END) {
        this.currentPoint = {
          x: data.x,
          y: data.y,
          z: data.z
        };
      }
    },
    
    // 開始新的測量
    startNewMeasurement(imageViewerId: string, profileViewerId: string | null) {
      // 重要：清除所有現有的點和線段
      this.startPoint = null;
      this.currentPoint = null;
      this.endPoint = null;
      this.lineProfileMeasureState = LineProfileState.IDLE;
      this.activeImageViewerId = imageViewerId;
      this.targetProfileViewerId = profileViewerId;
      this.profileData = null;
    },
    
    // 設置起點，進入測量模式
    setStartPoint(point: Point) {
      // 清除之前的任何數據
      this.endPoint = null;
      this.profileData = null;
      
      // 設置新的起點和當前點
      this.startPoint = { ...point };
      this.currentPoint = { ...point };
      
      // 更新狀態為選擇終點/跟隨滑鼠
      this.lineProfileMeasureState = LineProfileState.SELECTING_END;
    },
    
    // 設置終點，完成測量
    setEndPoint(point: Point) {
      this.endPoint = { ...point };
      this.lineProfileMeasureState = LineProfileState.COMPLETED;
    },
    
    // 設置剖面數據
    setProfileData(data: any) {
      this.profileData = data;
    },
    
    // 重置測量狀態
    resetMeasurement() {
      this.lineProfileMeasureState = LineProfileState.IDLE;
      // 不立即清除點數據，以便可以查看最後的測量結果
    },
    
    // 完全清除測量數據
    clearMeasurement() {
      this.startPoint = null;
      this.currentPoint = null;
      this.endPoint = null;
      this.lineProfileMeasureState = LineProfileState.IDLE;
      this.profileData = null;
    }
  },

  getters: {
    // 是否處於測量模式
    isMeasuring: (state) => state.lineProfileMeasureState > LineProfileState.IDLE,
    
    // 是否已完成測量
    isCompleted: (state) => state.lineProfileMeasureState === LineProfileState.COMPLETED,
    
    // 獲取測量狀態文字
    measureStateText: (state) => {
      switch(state.lineProfileMeasureState) {
        case LineProfileState.IDLE: 
          return '請選擇起點';
        case LineProfileState.SELECTING_END: 
          return '請選擇終點 (移動滑鼠可預覽)';
        case LineProfileState.COMPLETED: 
          return '測量完成，點擊重新開始';
        default: 
          return '';
      }
    }
  }
});