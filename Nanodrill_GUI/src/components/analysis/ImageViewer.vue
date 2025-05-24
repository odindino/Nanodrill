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
import type { ImageStats, Dimensions } from '../../types/analysisTypes';
import { AnalysisService } from '../../services/analysisService';  // 新增匯入

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
    },
    // 關聯的 ProfileViewer ID
    linkedProfileViewerId: {
      type: String,
      default: null
    }
  },
  emits: ['update:colormap', 'update:zScale', 'line-profile', 'close', 'click', 'measure-completed'],
  setup(props, { emit }) {
    console.log(`ImageViewer ${props.id} 初始化，測量模式: ${props.profileMeasureMode}`);
    
    // 使用 LineProfileStateStore
    const lineProfileStore = useLineProfileStateStore();
    
    // 圖像容器引用
    const imageContainer = ref<HTMLElement | null>(null);
    const plotlyContainer = ref<HTMLElement | null>(null);
    let plotlyInstance: any = null;
    
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
    
    // 創建 Plotly 圖表
    const createPlotlyChart = () => {
      console.log("開始創建 Plotly 圖表");
      
      if (!props.imageRawData || !plotlyContainer.value) {
        console.warn("缺少必要數據或容器，無法創建圖表:", {
          hasImageData: !!props.imageRawData,
          hasContainer: !!plotlyContainer.value
        });
        return;
      }
      
      try {
        const { width, height, xRange, yRange } = props.dimensions;
        
        // 創建 x 和 y 座標數組
        const x = Array.from({ length: width }, (_, i) => (i * xRange) / width);
        const y = Array.from({ length: height }, (_, i) => (i * yRange) / height);

        // 獲取數據的最小值和最大值，用於設置顏色條刻度
        let zMin = Infinity;
        let zMax = -Infinity;
        
        if (props.imageRawData) {
          for (let i = 0; i < props.imageRawData.length; i++) {
            for (let j = 0; j < props.imageRawData[i].length; j++) {
              const val = props.imageRawData[i][j];
              if (val < zMin) zMin = val;
              if (val > zMax) zMax = val;
            }
          }
        }
        
        // 計算顏色條的刻度值（均勻分成5等分）
        const zStep = (zMax - zMin) / 4;  // 分成5等分需要4個步長
        const colorbarTicks = [
          zMin, 
          zMin + zStep, 
          zMin + 2 * zStep, 
          zMin + 3 * zStep, 
          zMax
        ];
        
        // 準備數據
        const data = [{
          z: props.imageRawData,
          x: x,
          y: y,
          type: 'heatmap' as const,
          colorscale: props.colormap || 'Oranges',
          showscale: true,
          zauto: false,  // 禁用自動 z 範圍，這樣我們可以設置 zmin 和 zmax
          zmin: zMin,
          zmax: zMax,
          hoverinfo: props.profileMeasureMode ? 'x+y+z' : 'all',
          colorbar: {
            title: `Height (${props.physUnit})`,
            titleside: 'right',
            outlinewidth: 1,
            outlinecolor: 'black',
            thickness: 15,
            len: 1,
            x: 0.9,
            y: 0.5,
            yanchor: 'middle',
            tickvals: colorbarTicks,  // 設置刻度位置
            ticktext: colorbarTicks.map(val => val.toFixed(2)),  // 設置刻度文字（顯示兩位小數）
            nticks: 5  // 指定想要的刻度數量
          }
        }] as any[];
        
        // 準備布局
        const layout = {
          title: { text: '' },
          margin: { l: 0, r: 60, b: 50, t: 30, pad: 0 },
          xaxis: {
            title: `X (${props.physUnit})`,
            constrain: 'domain',
            showgrid: true,
            gridcolor: '#e5e5e5',
            gridwidth: 1,
            linewidth: 2,
            linecolor: 'black',
            mirror: true,
            showline: true,
            range: [0, xRange],  // 明確設置 x 軸範圍，確保完整顯示最大值
            dtick: xRange / 5,   // 設置 tick 間隔，確保能顯示約 5 個刻度
            tickmode: 'linear',
            tick0: 0
          },
          yaxis: {
            title: `Y (${props.physUnit})`,
            scaleanchor: 'x',
            constrain: 'domain',
            showgrid: true,
            gridcolor: '#e5e5e5',
            gridwidth: 1,
            linewidth: 2,
            linecolor: 'black',
            mirror: true,
            showline: true,
            range: [0, yRange],  // 明確設置 y 軸範圍，確保完整顯示最大值
            dtick: yRange / 5,   // 設置 tick 間隔，確保能顯示約 5 個刻度
            tickmode: 'linear',
            tick0: 0
          },
          modebar: {
            // Place modebar at the top-right corner horizontally
            orientation: 'v',
            bgcolor: 'white',
            color: 'black',
            activecolor: 'black',
          },
          aspectmode: 'equal',
          aspectratio: { x: 1, y: 1 },
          plot_bgcolor: 'white',
          paper_bgcolor: 'white',
          autosize: true,
          shapes: []
        } as any;
        
        // 設置配置
        const config = {
          responsive: true,
          modeBarButtonsToRemove: [
            'sendDataToCloud', 'editInChartStudio', 
            'toggleHover', 'toggleSpikelines'
          ] as any[],
          displaylogo: false,
          // 確保互動功能正常
          scrollZoom: true,
          doubleClick: 'reset',
          // 永遠不要鎖定圖表
          staticPlot: false,
          // 確保拖拽功能正常
          editable: false,
          // 確保所有互動都啟用
          showTips: true,
          // 確保 hover 和 click 事件正常工作
          toImageButtonOptions: {
            format: 'png',
            filename: 'nanodrill_image',
            height: 500,
            width: 700,
            scale: 1
          }
        } as any;
        
        // 創建圖表
        Plotly.newPlot(plotlyContainer.value, data, layout, config);
        plotlyInstance = plotlyContainer.value;
        
        console.log("Plotly 圖表創建成功");
        
        // 添加 Plotly 事件處理
        console.log("設置 Plotly 事件處理");
        setupPlotlyEvents();
      } catch (error) {
        console.error("創建 Plotly 圖表時出錯:", error);
      }
    };
    
    // 更新 Plotly 圖表
    const updatePlotlyChart = () => {
      console.log("更新 Plotly 圖表");
      
      if (!props.imageRawData || !plotlyInstance) {
        console.warn("缺少必要數據或實例，無法更新圖表");
        return;
      }
      
      try {
        // 獲取數據的最小值和最大值，用於設置顏色條刻度
        let zMin = Infinity;
        let zMax = -Infinity;
        
        if (props.imageRawData) {
          for (let i = 0; i < props.imageRawData.length; i++) {
            for (let j = 0; j < props.imageRawData[i].length; j++) {
              const val = props.imageRawData[i][j];
              if (val < zMin) zMin = val;
              if (val > zMax) zMax = val;
            }
          }
        }
        
        // 計算顏色條的刻度值（均勻分成5等分）
        const zStep = (zMax - zMin) / 4;  // 分成5等分需要4個步長
        const colorbarTicks = [
          zMin, 
          zMin + zStep, 
          zMin + 2 * zStep, 
          zMin + 3 * zStep, 
          zMax
        ];
        
        // 更新數據和顏色映射
        const updateData = {
          z: [props.imageRawData],
          colorscale: props.colormap || 'Oranges',
          zmin: zMin,
          zmax: zMax,
          colorbar: {
            tickvals: colorbarTicks,
            ticktext: colorbarTicks.map(val => val.toFixed(2))
          }
        } as any;
        
        Plotly.update(plotlyInstance, updateData, {}, [0]);
        
        // 更新軸範圍以確保顯示完整刻度
        const { xRange, yRange } = props.dimensions;
        
        Plotly.relayout(plotlyInstance, {
          'xaxis': {
            range: [0, xRange],
            dtick: xRange / 5,
            tickmode: 'linear',
            tick0: 0
          },
          'yaxis': {
            range: [0, yRange],
            dtick: yRange / 5,
            tickmode: 'linear',
            tick0: 0
          }
        });
        
        console.log("Plotly 圖表更新成功");
      } catch (error) {
        console.error("更新 Plotly 圖表時出錯:", error);
      }
    };
    
    // 新增：繪製線段
    const drawProfileLine = () => {
      if (!plotlyInstance || !lineProfileStore.startPoint || !lineProfileStore.endPoint) {
        return;
      }
      
      try {
        // 計算圓點大小為X或Y範圍的2%
        const { xRange, yRange } = props.dimensions;
        // 使用較小的範圍值來計算圓點尺寸，確保圓點在任何方向都不會太大
        const minRange = Math.min(xRange, yRange);
        const markerSize = minRange * 0.02; // 2% of range
        
        // 定義線段形狀
        const lineShape = {
          type: 'line' as const,
          x0: lineProfileStore.startPoint.x,
          y0: lineProfileStore.startPoint.y,
          x1: lineProfileStore.endPoint.x,
          y1: lineProfileStore.endPoint.y,
          line: {
            color: 'red',
            width: 2,
            dash: 'solid'
          }
        };
        
        // 定義起點和終點標記 - 使用動態大小
        const startMarker = {
          type: 'circle' as const,
          x0: lineProfileStore.startPoint.x - markerSize,
          y0: lineProfileStore.startPoint.y - markerSize,
          x1: lineProfileStore.startPoint.x + markerSize,
          y1: lineProfileStore.startPoint.y + markerSize,
          fillcolor: 'green',
          line: {
            color: 'green',
            width: 1
          }
        };
        
        const endMarker = {
          type: 'circle' as const,
          x0: lineProfileStore.endPoint.x - markerSize,
          y0: lineProfileStore.endPoint.y - markerSize,
          x1: lineProfileStore.endPoint.x + markerSize,
          y1: lineProfileStore.endPoint.y + markerSize,
          fillcolor: 'blue',
          line: {
            color: 'blue',
            width: 1
          }
        };
        
        // 更新圖表的 layout
        Plotly.relayout(plotlyInstance, {
          shapes: [lineShape, startMarker, endMarker] as any[]
        });
        
        console.log("線段繪製成功，標記大小: " + markerSize);
      } catch (error) {
        console.error("繪製線段時出錯:", error);
      }
    };

    // 新增：更新臨時跟隨線段 (在選擇第二點時顯示)
    const updateFollowingLine = () => {
      if (!plotlyInstance || !lineProfileStore.startPoint || !lineProfileStore.hoverData ||
          lineProfileStore.lineProfileMeasureState !== LineProfileState.SELECTING_END) {
        return;
      }
      
      try {
        // 計算圓點大小為X或Y範圍的2%
        const { xRange, yRange } = props.dimensions;
        // 使用較小的範圍值來計算圓點尺寸
        const minRange = Math.min(xRange, yRange);
        const markerSize = minRange * 0.02; // 2% of range
        
        // 定義臨時線段
        const tempLine = {
          type: 'line' as const,
          x0: lineProfileStore.startPoint.x,
          y0: lineProfileStore.startPoint.y,
          x1: lineProfileStore.hoverData.x,
          y1: lineProfileStore.hoverData.y,
          line: {
            color: 'rgba(255, 0, 0, 0.5)',
            width: 2,
            dash: 'dash'
          }
        };
        
        // 定義起點標記 - 使用動態大小
        const startMarker = {
          type: 'circle' as const,
          x0: lineProfileStore.startPoint.x - markerSize,
          y0: lineProfileStore.startPoint.y - markerSize,
          x1: lineProfileStore.startPoint.x + markerSize,
          y1: lineProfileStore.startPoint.y + markerSize,
          fillcolor: 'green',
          line: {
            color: 'green',
            width: 1
          }
        };
        
        // 更新圖表的 layout
        Plotly.relayout(plotlyInstance, {
          shapes: [tempLine, startMarker] as any[]
        });
      } catch (error) {
        console.error("更新臨時線段時出錯:", error);
      }
    };
    
    // 新增：清除所有線段
    const clearAllLines = () => {
      if (!plotlyInstance) return;
      
      try {
        Plotly.relayout(plotlyInstance, {
          shapes: []
        });
      } catch (error) {
        console.error("清除線段時出錯:", error);
      }
    };

    // 新增：獲取剖面數據
    const fetchProfileData = async () => {
      if (!lineProfileStore.startPoint || !lineProfileStore.endPoint || !props.imageRawData) {
        console.warn("無法獲取剖面數據：缺少起點、終點或圖像數據");
        return;
      }

      try {
        console.log("開始獲取剖面數據");
        
        // 將物理座標轉換為像素座標
        const { xRange, yRange } = props.dimensions;
        const imageHeight = props.imageRawData.length;
        const imageWidth = props.imageRawData[0].length;
        
        // 轉換起點座標：從物理座標(nm)轉為像素座標
        const startPixelY = Math.round((lineProfileStore.startPoint.y / yRange) * imageHeight);
        const startPixelX = Math.round((lineProfileStore.startPoint.x / xRange) * imageWidth);
        
        // 轉換終點座標：從物理座標(nm)轉為像素座標
        const endPixelY = Math.round((lineProfileStore.endPoint.y / yRange) * imageHeight);
        const endPixelX = Math.round((lineProfileStore.endPoint.x / xRange) * imageWidth);
        
        // 計算物理尺度 (nm per pixel)
        const physicalScale = Math.max(xRange / imageWidth, yRange / imageHeight);
        
        console.log("座標轉換:", {
          物理起點: [lineProfileStore.startPoint.x, lineProfileStore.startPoint.y],
          像素起點: [startPixelX, startPixelY],
          物理終點: [lineProfileStore.endPoint.x, lineProfileStore.endPoint.y],
          像素終點: [endPixelX, endPixelY],
          物理尺度: physicalScale,
          圖像尺寸: [imageWidth, imageHeight],
          物理範圍: [xRange, yRange]
        });

        // 調用後端 API 獲取剖面數據
        // 注意：後端期待座標格式為 (y, x)，所以需要調換順序
        const result = await AnalysisService.getLineProfile(
          props.imageRawData,
          [startPixelY, startPixelX],
          [endPixelY, endPixelX],
          physicalScale,
          false // shiftZero
        );
        
        if (result && result.success && result.profile_data) {
          // 轉換後端數據格式為前端期望的格式
          const profileDataFormatted = result.profile_data.distance.map((dist: number, index: number) => ({
            distance: dist,
            height: result.profile_data.height[index]
          }));
          
          // 更新 lineProfileStore 中的剖面數據
          lineProfileStore.setProfileData(profileDataFormatted);
          console.log("剖面數據獲取成功，數據點數:", profileDataFormatted.length);
        } else {
          console.error("獲取剖面數據失敗:", result);
        }
      } catch (error) {
        console.error("獲取剖面數據時出錯:", error);
      }
    };

    // 新增：即時獲取剖面數據（用於滑鼠跟隨）
    const fetchRealtimeProfileData = async (endPoint: { x: number, y: number, z: number }) => {
      if (!lineProfileStore.startPoint || !props.imageRawData) {
        return;
      }

      try {
        // 將物理座標轉換為像素座標
        const { xRange, yRange } = props.dimensions;
        const imageHeight = props.imageRawData.length;
        const imageWidth = props.imageRawData[0].length;
        
        // 轉換起點座標：從物理座標(nm)轉為像素座標
        const startPixelY = Math.round((lineProfileStore.startPoint.y / yRange) * imageHeight);
        const startPixelX = Math.round((lineProfileStore.startPoint.x / xRange) * imageWidth);
        
        // 轉換終點座標：從物理座標(nm)轉為像素座標
        const endPixelY = Math.round((endPoint.y / yRange) * imageHeight);
        const endPixelX = Math.round((endPoint.x / xRange) * imageWidth);
        
        // 計算物理尺度 (nm per pixel)
        const physicalScale = Math.max(xRange / imageWidth, yRange / imageHeight);

        // 調用後端 API 獲取剖面數據
        // 注意：後端期待座標格式為 (y, x)，所以需要調換順序
        const result = await AnalysisService.getLineProfile(
          props.imageRawData,
          [startPixelY, startPixelX],
          [endPixelY, endPixelX],
          physicalScale,
          false // shiftZero
        );
        
        if (result && result.success && result.profile_data) {
          // 轉換數據格式
          const profileDataFormatted = result.profile_data.distance.map((dist: number, index: number) => ({
            distance: dist,
            height: result.profile_data.height[index]
          }));
          
          // 更新 lineProfileStore 中的剖面數據
          lineProfileStore.setProfileData(profileDataFormatted);
        }
      } catch (error) {
        // 忽略即時更新的錯誤，避免過多的錯誤訊息
        console.debug("即時剖面數據更新失敗:", error);
      }
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
      if (!plotlyInstance) {
        console.warn("plotlyInstance 不存在，無法設置事件");
        return;
      }
      
      try {
        // 監聽 hover 事件
        plotlyInstance.on('plotly_hover', handlePlotlyHover);
        
        // 監聽 unhover 事件
        plotlyInstance.on('plotly_unhover', handlePlotlyUnhover);
        
        // 監聽 click 事件
        plotlyInstance.on('plotly_click', handlePlotlyClick);
        
        console.log("Plotly 事件監聽器設置完成");
      } catch (error) {
        console.error("設置 Plotly 事件監聽器時出錯:", error);
      }
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
        
        // 如果正在選擇終點，更新臨時線段和即時剖面數據
        if (lineProfileStore.lineProfileMeasureState === LineProfileState.SELECTING_END) {
          updateFollowingLine();
          
          // 即時更新剖面數據
          fetchRealtimeProfileData({
            x: point.x,
            y: point.y,
            z: point.z
          });
        }
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
      console.log("ImageViewer: Plotly 點擊事件被觸發");
      console.log("測量模式狀態:", props.profileMeasureMode);
      console.log("當前 hover 狀態:", lineProfileStore.inPlotArea);
      console.log("當前測量狀態:", lineProfileStore.lineProfileMeasureState);
      
      if (!props.profileMeasureMode) {
        console.log("非測量模式，忽略點擊");
        return;
      }
      
      // 只有當滑鼠在圖表上時才處理點擊 (通過 hover 狀態檢查)
      if (!lineProfileStore.inPlotArea || !lineProfileStore.hoverData) {
        console.log("滑鼠不在圖表區域或無 hover 數據，忽略點擊");
        return;
      }
      
      try {
        switch (lineProfileStore.lineProfileMeasureState) {
          case LineProfileState.IDLE:
            console.log("狀態: IDLE，設置起點");
            // 清除所有線段
            clearAllLines();
            
            // 設置起點
            lineProfileStore.setStartPoint({
              x: lineProfileStore.hoverData.x,
              y: lineProfileStore.hoverData.y,
              z: lineProfileStore.hoverData.z
            });
            
            console.log("起點坐標:", lineProfileStore.startPoint);
            break;
            
          case LineProfileState.SELECTING_END:
            console.log("狀態: SELECTING_END，設置終點");
            // 設置終點
            lineProfileStore.setEndPoint({
              x: lineProfileStore.hoverData.x,
              y: lineProfileStore.hoverData.y,
              z: lineProfileStore.hoverData.z
            });
            
            console.log("終點坐標:", lineProfileStore.endPoint);
            
            // 繪製線段
            drawProfileLine();
            
            // 新增：獲取剖面數據並更新 lineProfileStore
            fetchProfileData();
            
            // 發送測量完成事件
            emit('measure-completed', {
              sourceViewerId: props.id,
              sourceData: {
                imageRawData: props.imageRawData,
                dimensions: props.dimensions
              },
              startPoint: [lineProfileStore.startPoint!.x, lineProfileStore.startPoint!.y],
              endPoint: [lineProfileStore.endPoint!.x, lineProfileStore.endPoint!.y],
              targetProfileViewer: props.targetProfileViewer
            });
            break;
            
          case LineProfileState.COMPLETED:
            console.log("狀態: COMPLETED，重置測量");
            // 重置測量狀態
            lineProfileStore.resetMeasurement();
            
            // 清除所有線段
            clearAllLines();
            
            // 設置新的起點
            lineProfileStore.setStartPoint({
              x: lineProfileStore.hoverData.x,
              y: lineProfileStore.hoverData.y,
              z: lineProfileStore.hoverData.z
            });
            
            console.log("新的起點坐標:", lineProfileStore.startPoint);
            break;
        }
      } catch (error) {
        console.error("處理點擊事件時發生錯誤:", error);
      }
    };
    
    // 監視測量狀態變化
    watch(() => lineProfileStore.lineProfileMeasureState, (newState) => {
      if (newState === LineProfileState.COMPLETED) {
        // 測量完成，繪製最終線段
        drawProfileLine();
      } else if (newState === LineProfileState.IDLE) {
        // 測量重置，清除所有線段
        clearAllLines();
      }
    });
    
    // 監視測量模式變化
    watch(() => props.profileMeasureMode, (newMode) => {
      console.log(`ImageViewer ${props.id} 測量模式變更為:`, newMode);
      
      if (newMode) {
        // 進入測量模式
        console.log("進入測量模式");
        
        // 確保 Plotly 事件監聽器重新設置
        if (plotlyInstance) {
          // 移除舊的監聽器（如果存在）
          plotlyInstance.removeListener('plotly_hover', handlePlotlyHover);
          plotlyInstance.removeListener('plotly_unhover', handlePlotlyUnhover);
          plotlyInstance.removeListener('plotly_click', handlePlotlyClick);
          
          // 重新設置事件監聽器
          setupPlotlyEvents();
        }
        
        // 確保圖表可以互動
        if (plotlyInstance) {
          Plotly.relayout(plotlyInstance, {
            dragmode: 'pan', // 確保可以拖拽
            hovermode: 'closest' // 確保 hover 正常
          });
        }
      } else {
        // 退出測量模式
        console.log("退出測量模式");
        
        // 清除測量狀態
        lineProfileStore.clearMeasurement();
        
        // 清除所有線段
        clearAllLines();
      }
    });
    
    // 監視 colormap 屬性變化
    watch(() => props.colormap, (newColormap) => {
      console.log(`ImageViewer ${props.id} colormap 變更為:`, newColormap);
      if (plotlyInstance && newColormap) {
        updatePlotlyChart();
      }
    });
    
    // 監視圖像數據變化
    watch(() => props.imageRawData, (newData) => {
      console.log(`ImageViewer ${props.id} imageRawData 已更新`);
      if (newData && plotlyContainer.value) {
        if (plotlyInstance) {
          updatePlotlyChart();
        } else {
          createPlotlyChart();
        }
      }
    });
    
    // 組件掛載時
    onMounted(() => {
      console.log(`ImageViewer ${props.id} 已掛載`);
      
      if (props.imageRawData) {
        createPlotlyChart();
      }
    });
    
    // 組件卸載前清理事件監聽
    onBeforeUnmount(() => {
      console.log(`ImageViewer ${props.id} 即將卸載`);
      
      if (plotlyInstance) {
        console.log("移除 Plotly 事件監聽器");
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
  display: flex;
  flex-direction: column;
}

/* 確保主要內容區域可以自適應並填滿空間 */
.flex-grow {
  flex: 1 1 auto;
  min-height: 400px; /* 確保最小高度足夠 */
}

/* 測量模式下的鼠標樣式 */
.profile-measure-mode {
  cursor: crosshair !important;
}

/* Plotly 容器樣式 */
:deep(.js-plotly-plot) {
  width: 100% !important;
  height: 100% !important;
}
</style>