<!-- src/components/analysis/ImageViewer.vue -->
<template>
  <div class="image-viewer h-full flex flex-col bg-white rounded-lg overflow-hidden"
       :class="{ 'ring-2 ring-primary': isActive }"
       @click="handleClick">
    <!-- 控制欄 -->
    <div class="flex items-center justify-between px-3 py-1.5 bg-gray-50 border-b border-gray-200">
      <h3 class="text-sm font-medium text-gray-700 truncate">{{ title || 'Image Viewer' }}</h3>
      
      <div class="flex space-x-2">
        <!-- 關閉按鈕 -->
        <button 
          v-if="allowClose" 
          @click.stop="$emit('close')"
          class="p-1 rounded hover:bg-gray-200 text-gray-600 focus:outline-none"
          title="關閉"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
    
    <!-- 主要圖像顯示區域 -->
    <div class="flex-grow overflow-hidden relative min-h-[300px]" ref="imageContainer">
      <!-- 載入中顯示 -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-gray-50">
        <div class="flex flex-col items-center">
          <div class="w-8 h-8 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-2"></div>
          <span class="text-sm text-gray-600">載入中...</span>
        </div>
      </div>
      
      <!-- Plotly 圖表容器 -->
      <div v-if="imageRawData" 
          ref="plotlyContainer" 
          class="w-full h-full"
          :class="{'profile-measure-mode': profileMeasureMode}">
      </div>
      
      <!-- 測量狀態提示 -->
      <div v-if="profileMeasureMode" class="absolute top-2 left-2 right-2 bg-blue-100 text-blue-800 text-xs p-2 rounded-md shadow-sm border border-blue-200 z-10">
        {{ measureStateText }}
        <span v-if="!lineProfileStore.inPlotArea" class="block mt-1 text-red-500">
          滑鼠不在圖表區域內，請移回圖表
        </span>
      </div>
      
      <!-- 無圖像數據提示 -->
      <div v-else-if="!imageRawData" class="absolute inset-0 flex items-center justify-center bg-gray-50">
        <div class="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span class="text-sm text-gray-500">尚未載入圖像</span>
        </div>
      </div>
    </div>
    
    <!-- 圖像統計信息 -->
    <div v-if="showStats && stats" class="p-2 bg-gray-50 border-t border-gray-200 text-xs">
      <div class="grid grid-cols-4 gap-2">
        <div class="text-gray-600">
          <span class="font-medium">最小:</span> {{ formatNumber(stats.min) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">最大:</span> {{ formatNumber(stats.max) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">平均:</span> {{ formatNumber(stats.mean) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">RMS:</span> {{ formatNumber(stats.rms) }} {{ physUnit }}
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import type { PropType } from 'vue';
import Plotly from 'plotly.js-dist-min';
import { useLineProfileStateStore, LineProfileState } from '../../stores/lineProfileStateStore';
import type { Point, HoverData } from '../../stores/lineProfileStateStore';

// 定義統計信息介面
interface ImageStats {
  min: number;
  max: number;
  mean: number;
  median: number;
  std: number;
  rms: number;
}

// 定義維度介面
interface Dimensions {
  width: number;
  height: number;
  xRange: number;
  yRange: number;
}

// 定義目標剖面視圖接口
interface TargetProfileViewer {
  id: string;
  groupId?: string;
  viewerIndex?: number;
}

export default defineComponent({
  name: 'ImageViewer',
  props: {
    id: {
      type: String,
      default: ''
    },
    imageData: {
      type: String,
      default: ''
    },
    imageRawData: {
      type: Array as PropType<number[][]>,
      default: null
    },
    title: {
      type: String,
      default: 'Image'
    },
    imageType: {
      type: String,
      default: 'topo'
    },
    physUnit: {
      type: String,
      default: 'nm'
    },
    colormap: {
      type: String,
      default: 'Oranges'
    },
    zScale: {
      type: Number,
      default: 1.0
    },
    stats: {
      type: Object as PropType<ImageStats | null>,
      default: null
    },
    dimensions: {
      type: Object as PropType<Dimensions>,
      default: () => ({ width: 0, height: 0, xRange: 0, yRange: 0 })
    },
    allowClose: {
      type: Boolean,
      default: true
    },
    hideControls: {
      type: Boolean,
      default: false
    },
    isActive: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    showStats: {
      type: Boolean,
      default: true
    },
    // 是否處於剖面測量模式
    profileMeasureMode: {
      type: Boolean,
      default: false
    },
    // 目標剖面視圖
    targetProfileViewer: {
      type: Object as PropType<{ id: string } | null>,
      default: null
    }
  },
  emits: ['update:colormap', 'update:zScale', 'line-profile', 'close', 'click', 'measure-completed'],
  setup(props, { emit }) {
    // 使用 LineProfileStateStore
    const lineProfileStore = useLineProfileStateStore();
    
    // 圖像容器引用
    const imageContainer = ref<HTMLElement | null>(null);
    const plotlyContainer = ref<HTMLElement | null>(null);
    let plotlyInstance: any = null;
    
    // 線條繪製相關變量
    let followingLineIndex: number | null = null;
    let pointMarkerIndices: number[] = [];
    let finalLineIndex: number | null = null;
    
    // 測量狀態提示消息
    const measureStateText = computed(() => {
      if (!props.profileMeasureMode) {
        return '';
      }
      
      return lineProfileStore.measureStateText;
    });
    
    // 格式化數字，保留2位小數
    const formatNumber = (value: number) => {
      if (value === undefined || value === null) return 'N/A';
      return value.toFixed(2);
    };

    // 添加關閉視圖的方法
    const closeViewer = () => {
      emit('close');
    };
    
    // 禁用Plotly默認交互
    const disablePlotlyInteractions = () => {
      if (plotlyInstance) {
        Plotly.relayout(plotlyInstance, {
          'dragmode': false,
          'displayModeBar': false,
          'scrollZoom': false
        });
      }
    };
    
    // 啟用Plotly默認交互
    const enablePlotlyInteractions = () => {
      if (plotlyInstance) {
        Plotly.relayout(plotlyInstance, {
          'dragmode': 'zoom',
          'displayModeBar': true,
          'scrollZoom': true
        });
      }
    };
    
    /**
     * 從物理坐標獲取像素坐標
     */
    const getPixelCoordinates = (point: Point) => {
      const { width, height, xRange, yRange } = props.dimensions;
      
      // 計算相對位置
      const relX = point.x / xRange;
      const relY = point.y / yRange;
      
      // 計算像素坐標
      const pixelX = Math.floor(relX * width);
      const pixelY = Math.floor((1 - relY) * height); // Y軸原點在左上角，需要翻轉
      
      return { x: pixelX, y: pixelY };
    };
    
    // 創建 Plotly 圖表
    const createPlotlyChart = () => {
      if (!props.imageRawData || !plotlyContainer.value) return;
      
      const { width, height, xRange, yRange } = props.dimensions;
      
      // 創建 x 和 y 座標數組
      const x = Array.from({ length: width }, (_, i) => (i * xRange) / width);
      const y = Array.from({ length: height }, (_, i) => (i * yRange) / height);
      
      // 準備數據
      const data = [{
        z: props.imageRawData,
        x: x,
        y: y,
        type: 'heatmap',
        colorscale: props.colormap || 'Oranges',
        showscale: true,
        zauto: true,
        hoverinfo: props.profileMeasureMode ? 'x+y+z' : 'all'
      }];
      
      // 準備布局
      const layout = {
        title: '',
        margin: { l: 50, r: 150, b: 65, t: 25 },
        xaxis: {
          title: `X (${props.physUnit})`,
          constrain: 'domain',
          showgrid: true,
          gridcolor: '#e5e5e5',
          gridwidth: 1,
          linewidth: 2,
          linecolor: 'black'
        },
        yaxis: {
          title: `Y (${props.physUnit})`,
          scaleanchor: 'x',
          constrain: 'domain',
          showgrid: true,
          gridcolor: '#e5e5e5',
          gridwidth: 1,
          linewidth: 2,
          linecolor: 'black'
        },
        coloraxis: {
          colorbar: {
            title: `Height (${props.physUnit})`,
            titleside: 'right',
            outlinewidth: 1,
            outlinecolor: 'black',
            thickness: 20
          }
        },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        autosize: true
      };
      
      // 設置配置
      const config = {
        responsive: true,
        modeBarButtonsToRemove: [
          'sendDataToCloud', 'editInChartStudio', 
          'toggleHover', 'toggleSpikelines'
        ],
        displaylogo: false
      };
      
      // 創建圖表
      Plotly.newPlot(plotlyContainer.value, data, layout, config);
      plotlyInstance = plotlyContainer.value;
      
      // 初始化測量狀態
      if (props.profileMeasureMode) {
        initMeasureMode();
      }
      
      // 添加 Plotly 事件處理
      setupPlotlyEvents();
    };
    
    // 更新 Plotly 圖表
    const updatePlotlyChart = () => {
      if (!props.imageRawData || !plotlyInstance) return;
      
      // 更新數據和顏色映射
      Plotly.update(plotlyInstance, {
        'z': [props.imageRawData],
        'colorscale': props.colormap || 'Oranges'
      });
    };

    // 處理點擊事件 (組件整體)
    const handleClick = (event: MouseEvent) => {
      // 確保 event 是有效的
      if (event) {
        event.stopPropagation();
      }
      
      // 只有在非測量模式下才發出點擊事件
      if (!props.profileMeasureMode) {
        emit('click');
      }
    };

    /**
     * 設置 Plotly 事件處理
     */
    const setupPlotlyEvents = () => {
      if (!plotlyInstance) return;
      
      // 監聽 hover 事件
      plotlyInstance.on('plotly_hover', handlePlotlyHover);
      
      // 監聽 unhover 事件
      plotlyInstance.on('plotly_unhover', handlePlotlyUnhover);
      
      // 監聽 click 事件
      plotlyInstance.on('plotly_click', handlePlotlyClick);
    };
    
    /**
     * 處理 Plotly hover 事件
     */
    const handlePlotlyHover = (data: any) => {
      if (!props.profileMeasureMode) return;
      
      // 設置在圖表區域內
      lineProfileStore.setInPlotArea(true);
      
      // 獲取當前 hover 的點座標
      if (data && data.points && data.points.length > 0) {
        const point = data.points[0];
        const hoverData: HoverData = {
          x: point.x,
          y: point.y,
          z: point.z,
          curveNumber: point.curveNumber,
          pointNumber: point.pointNumber,
          pointIndex: point.pointIndex
        };

        lineProfileStore.updateHoverData(hoverData);
      }
    };
    
    /**
     * 處理 Plotly unhover 事件
     */
    const handlePlotlyUnhover = () => {
      if (!props.profileMeasureMode) return;
      
      // 設置離開圖表區域
      lineProfileStore.setInPlotArea(false);
      // 保留最後的 hover 數據，不清除
    };
    
    /**
     * 處理 Plotly click 事件
     */
    const handlePlotlyClick = (data: any) => {
      if (!props.profileMeasureMode) return;
      
      // 只有當滑鼠在圖表上時才處理點擊 (通過 hover 狀態檢查)
      if (!lineProfileStore.inPlotArea || !lineProfileStore.hoverData) return;
      
      switch (lineProfileStore.lineProfileMeasureState) {
        case LineProfileState.IDLE:
          // 清除現有的線條和點
          clearAllTraces();
          
          // 設置起點
          lineProfileStore.setStartPoint({
            x: lineProfileStore.hoverData.x,
            y: lineProfileStore.hoverData.y,
            z: lineProfileStore.hoverData.z
          });
          
          // 添加起點標記
          addPointMarker(lineProfileStore.startPoint!, 'red');
          break;
          
        case LineProfileState.SELECTING_END:
          // 設置終點
          lineProfileStore.setEndPoint({
            x: lineProfileStore.hoverData.x,
            y: lineProfileStore.hoverData.y,
            z: lineProfileStore.hoverData.z
          });
          
          // 添加終點標記
          addPointMarker(lineProfileStore.endPoint!, 'blue');
          
          // 繪製最終線條
          drawFinalLine();
          
          // 計算剖面數據
          calculateProfileData();
          break;
          
        case LineProfileState.COMPLETED:
          // 清除現有的線條和點
          clearAllTraces();
          
          // 重置測量狀態
          lineProfileStore.resetMeasurement();
          
          // 設置新的起點
          lineProfileStore.setStartPoint({
            x: lineProfileStore.hoverData.x,
            y: lineProfileStore.hoverData.y,
            z: lineProfileStore.hoverData.z
          });
          
          // 添加起點標記
          addPointMarker(lineProfileStore.startPoint!, 'red');
          break;
      }
    };
    
    /**
     * 初始化測量模式
     */
    const initMeasureMode = () => {
      // 清除現有的線條和點
      clearAllTraces();
      
      // 重置狀態
      lineProfileStore.startNewMeasurement(props.id, props.targetProfileViewer?.id || null);
      
      // 禁用 Plotly 默認交互
      disablePlotlyInteractions();
    };
    
    /**
     * 添加點標記
     */
    const addPointMarker = (point: Point, color: string = 'red') => {
      if (!plotlyInstance) return;
      
      // 創建點數據
      const pointData = {
        x: [point.x],
        y: [point.y],
        mode: 'markers',
        type: 'scatter',
        marker: {
          size: 10,
          color: color,
          symbol: 'circle'
        },
        showlegend: false,
        hoverinfo: 'none'
      };
      
      // 添加點到圖表
      Plotly.addTraces(plotlyInstance, pointData);
      
      // 記錄添加的點的索引
      const newTraceIndex = (plotlyInstance.data || []).length - 1;
      pointMarkerIndices.push(newTraceIndex);
    };
    
    /**
     * 更新跟隨滑鼠的線條
     */
    const updateFollowingLine = () => {
      if (!plotlyInstance || !lineProfileStore.startPoint || !lineProfileStore.currentPoint) return;
      
      // 移除現有的臨時線條 (如果有)
      if (followingLineIndex !== null) {
        Plotly.deleteTraces(plotlyInstance, followingLineIndex);
        followingLineIndex = null;
      }
      
      // 創建線數據
      const lineData = {
        x: [lineProfileStore.startPoint.x, lineProfileStore.currentPoint.x],
        y: [lineProfileStore.startPoint.y, lineProfileStore.currentPoint.y],
        mode: 'lines',
        type: 'scatter',
        line: {
          color: 'red',
          width: 2,
          dash: 'dot'
        },
        showlegend: false,
        hoverinfo: 'none'
      };
      
      // 添加線到圖表
      Plotly.addTraces(plotlyInstance, lineData);
      
      // 記錄添加的線的索引
      followingLineIndex = (plotlyInstance.data || []).length - 1;
    };
    
    /**
     * 繪製最終線條
     */
    const drawFinalLine = () => {
      if (!plotlyInstance || !lineProfileStore.startPoint || !lineProfileStore.endPoint) return;
      
      // 移除現有的臨時線條 (如果有)
      if (followingLineIndex !== null) {
        Plotly.deleteTraces(plotlyInstance, followingLineIndex);
        followingLineIndex = null;
      }
      
      // 移除現有的最終線條 (如果有)
      if (finalLineIndex !== null) {
        Plotly.deleteTraces(plotlyInstance, finalLineIndex);
        finalLineIndex = null;
      }
      
      // 創建線數據
      const lineData = {
        x: [lineProfileStore.startPoint.x, lineProfileStore.endPoint.x],
        y: [lineProfileStore.startPoint.y, lineProfileStore.endPoint.y],
        mode: 'lines',
        type: 'scatter',
        line: {
          color: 'blue',
          width: 2,
          dash: 'solid'
        },
        showlegend: false,
        hoverinfo: 'none'
      };
      
      // 添加線到圖表
      Plotly.addTraces(plotlyInstance, lineData);
      
      // 記錄添加的線的索引
      finalLineIndex = (plotlyInstance.data || []).length - 1;
    };
    
    /**
     * 清除所有繪製的痕跡
     */
    const clearAllTraces = () => {
      if (!plotlyInstance) return;
      
      // 清除臨時線條
      if (followingLineIndex !== null) {
        Plotly.deleteTraces(plotlyInstance, followingLineIndex);
        followingLineIndex = null;
      }
      
      // 清除最終線條
      if (finalLineIndex !== null) {
        Plotly.deleteTraces(plotlyInstance, finalLineIndex);
        finalLineIndex = null;
      }
      
      // 清除點標記
      if (pointMarkerIndices.length > 0) {
        // 需要按降序排列索引，以避免刪除後的索引變化問題
        const sortedIndices = [...pointMarkerIndices].sort((a, b) => b - a);
        for (const index of sortedIndices) {
          Plotly.deleteTraces(plotlyInstance, index);
        }
        pointMarkerIndices = [];
      }
    };
    
    /**
     * 計算剖面數據
     */
    const calculateProfileData = () => {
      if (!lineProfileStore.startPoint || !lineProfileStore.endPoint || !props.imageRawData) return;
      
      // 獲取起點和終點的像素坐標
      const start = getPixelCoordinates(lineProfileStore.startPoint);
      const end = getPixelCoordinates(lineProfileStore.endPoint);
      
      // 使用 Bresenham 算法計算線段經過的所有像素
      const linePixels = getLinePixels(start.x, start.y, end.x, end.y);
      
      // 確保像素坐標在圖像範圍內
      const { width, height } = props.dimensions;
      const validPixels = linePixels.filter(
        pixel => pixel.x >= 0 && pixel.x < width && pixel.y >= 0 && pixel.y < height
      );
      
      if (validPixels.length === 0) return;
      
      // 計算每個點的物理距離和高度
      const profileData = validPixels.map((pixel, index) => {
        // 計算距離起點的物理距離
        const dx = (pixel.x - start.x) / width * props.dimensions.xRange;
        const dy = (pixel.y - start.y) / height * props.dimensions.yRange;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        // 獲取高度 (確保在圖像範圍內)
        let height = 0;
        if (pixel.y < props.imageRawData.length && pixel.x < props.imageRawData[0].length) {
          height = props.imageRawData[pixel.y][pixel.x];
        }
        
        return { distance, height };
      });
      
      // 保存剖面數據
      lineProfileStore.setProfileData(profileData);
      
      // 發送測量完成事件
      emit('measure-completed', {
        sourceViewerId: props.id,
        startPoint: [start.x, start.y],
        endPoint: [end.x, end.y],
        profileData: profileData,
        targetProfileViewer: props.targetProfileViewer
      });
    };
    
    /**
     * Bresenham 算法計算線段經過的像素
     */
    const getLinePixels = (x0: number, y0: number, x1: number, y1: number) => {
      const pixels = [];
      const dx = Math.abs(x1 - x0);
      const dy = Math.abs(y1 - y0);
      const sx = (x0 < x1) ? 1 : -1;
      const sy = (y0 < y1) ? 1 : -1;
      let err = dx - dy;
      
      let x = x0;
      let y = y0;
      
      while (true) {
        pixels.push({ x, y });
        
        if (x === x1 && y === y1) break;
        
        const e2 = 2 * err;
        if (e2 > -dy) {
          err -= dy;
          x += sx;
        }
        if (e2 < dx) {
          err += dx;
          y += sy;
        }
      }
      
      return pixels;
    };
    
    // 監視 currentPoint 變化，更新跟隨線
    watch(() => lineProfileStore.currentPoint, () => {
      if (lineProfileStore.lineProfileMeasureState === LineProfileState.SELECTING_END && lineProfileStore.startPoint && lineProfileStore.currentPoint) {
        updateFollowingLine();
      }
    });
    
    // 監視 imageRawData 變化
    watch(() => props.imageRawData, (newData) => {
      if (newData) {
        // 有數據時創建或更新圖表
        if (!plotlyInstance) {
          // 延遲一幀以確保 DOM 已更新
          setTimeout(createPlotlyChart, 0);
        } else {
          updatePlotlyChart();
        }
      }
    }, { immediate: true });
    
    // 監視色彩映射變化
    watch(() => props.colormap, () => {
      updatePlotlyChart();
    });
    
    // 監視測量模式變化
    watch(() => props.profileMeasureMode, (newValue) => {
      if (!plotlyInstance) return;
      
      if (newValue) {
        // 進入測量模式
        initMeasureMode();
      } else {
        // 退出測量模式
        clearAllTraces();
        lineProfileStore.clearMeasurement();
        enablePlotlyInteractions();
      }
    });
    
    // 組件掛載時
    onMounted(() => {
      if (props.imageRawData) {
        createPlotlyChart();
      }
    });
    
    // 組件卸載前清理事件監聽
    onBeforeUnmount(() => {
      if (plotlyInstance) {
        plotlyInstance.removeListener('plotly_hover', handlePlotlyHover);
        plotlyInstance.removeListener('plotly_unhover', handlePlotlyUnhover);
        plotlyInstance.removeListener('plotly_click', handlePlotlyClick);
      }
    });
    
    return {
      imageContainer,
      plotlyContainer,
      lineProfileStore,
      handleClick,
      closeViewer,
      formatNumber,
      measureStateText
    };
  }
});
</script>

<style scoped>
/* 確保視圖高度填滿容器 */
.image-viewer {
  height: 100%;
}

/* 測量模式下的鼠標樣式 */
.profile-measure-mode {
  cursor: crosshair !important;
}
</style>