<!-- src/components/analysis/ImageViewer.vue -->
<template>
  <div class="image-viewer h-full flex flex-col bg-white rounded-lg overflow-hidden"
       :class="{ 'ring-2 ring-primary': isActive }"
       @click="handleClick">
    <!-- 控制欄 -->
    <div class="flex items-center justify-between px-3 py-1.5 bg-gray-50 border-b border-gray-200">
      <h3 class="text-sm font-medium text-gray-700 truncate">{{ title || 'Image Viewer' }}</h3>
      
      <div class="flex space-x-1">
        <!-- 線性剖面按鈕 -->
        <button 
          v-if="allowProfile && !hideControls" 
          @click.stop="toggleLineProfile"
          class="p-1 rounded hover:bg-gray-200 text-gray-600 focus:outline-none"
          :class="{ 'bg-blue-100 text-blue-600': lineProfileEnabled }"
          title="線性剖面"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
        </button>
        
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
    <div class="flex-grow overflow-hidden relative" ref="imageContainer">
      <!-- 載入中顯示 -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-gray-50">
        <div class="flex flex-col items-center">
          <div class="w-8 h-8 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-2"></div>
          <span class="text-sm text-gray-600">載入中...</span>
        </div>
      </div>
      
      <!-- 實際圖像 - 使用Plotly互動式圖表 -->
      <div v-else class="h-full w-full relative">
        <!-- Plotly 圖表容器 -->
        <div v-if="imageRawData" 
             ref="plotlyContainer" 
             class="w-full h-full"
             @mousedown="handleMouseDown"
             @mousemove="handleMouseMove"
             @mouseup="handleMouseUp"></div>
        
        <!-- 線性剖面繪製線 -->
        <svg v-if="lineProfileEnabled" class="absolute top-0 left-0 w-full h-full pointer-events-none">
          <line v-if="isDrawingLine || (lineStart && lineEnd)"
                :x1="lineStart?.x || 0"
                :y1="lineStart?.y || 0"
                :x2="isDrawingLine ? mouseMovePos.x : (lineEnd?.x || 0)"
                :y2="isDrawingLine ? mouseMovePos.y : (lineEnd?.y || 0)"
                stroke="#ff6b6b"
                stroke-width="2"
                stroke-dasharray="5,5" />
          
          <!-- 起點圓點 -->
          <circle v-if="lineStart"
                  :cx="lineStart.x"
                  :cy="lineStart.y"
                  r="4"
                  fill="#ff6b6b" />
          
          <!-- 終點圓點 -->
          <circle v-if="!isDrawingLine && lineEnd"
                  :cx="lineEnd.x"
                  :cy="lineEnd.y"
                  r="4"
                  fill="#ff6b6b" />
        </svg>
        
        <!-- 無圖像數據提示 -->
        <div v-if="!imageRawData" class="absolute inset-0 flex items-center justify-center bg-gray-50">
          <div class="text-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="text-sm text-gray-500">尚未載入圖像</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 統計信息面板 -->
    <div v-if="showStats && stats" class="py-1 px-3 bg-gray-50 border-t border-gray-200 text-xs">
      <div class="grid grid-cols-4 gap-2">
        <div class="text-gray-600">
          <span class="font-medium">最小值:</span> {{ formatNumber(stats.min) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">最大值:</span> {{ formatNumber(stats.max) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">平均值:</span> {{ formatNumber(stats.mean) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">RMS:</span> {{ formatNumber(stats.rms) }} {{ physUnit }}
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import type { PropType } from 'vue';
import Plotly from 'plotly.js-dist-min';

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

// 定義位置點介面
interface Point {
  x: number;
  y: number;
}

export default defineComponent({
  name: 'ImageViewer',
  props: {
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
    allowProfile: {
      type: Boolean,
      default: true
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
    }
  },
  emits: ['update:colormap', 'update:zScale', 'line-profile', 'close', 'click'],
  setup(props, { emit }) {
    // 圖像容器引用
    const imageContainer = ref<HTMLElement | null>(null);
    const plotlyContainer = ref<HTMLElement | null>(null);
    let plotlyInstance: any = null;
    
    // 線性剖面相關狀態
    const lineProfileEnabled = ref(false);
    const isDrawingLine = ref(false);
    const lineStart = ref<Point | null>(null);
    const lineEnd = ref<Point | null>(null);
    const mouseMovePos = ref<Point>({ x: 0, y: 0 });
    
    // 格式化數字，保留兩位小數
    const formatNumber = (value: number) => {
      if (value === undefined || value === null) return 'N/A';
      return value.toFixed(2);
    };
    
    // 處理點擊事件
    const handleClick = () => {
      emit('click');
    };
    
    // 切換線性剖面功能
    const toggleLineProfile = () => {
      lineProfileEnabled.value = !lineProfileEnabled.value;
      
      // 如果禁用了線性剖面，重置相關狀態
      if (!lineProfileEnabled.value) {
        isDrawingLine.value = false;
        lineStart.value = null;
        lineEnd.value = null;
      }
    };
    
    // 處理滑鼠按下事件
    const handleMouseDown = (event: MouseEvent) => {
      if (!lineProfileEnabled.value) return;
      
      const rect = (event.target as HTMLElement).getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      // 設置起點並開始繪製
      lineStart.value = { x, y };
      isDrawingLine.value = true;
    };
    
    // 處理滑鼠移動事件
    const handleMouseMove = (event: MouseEvent) => {
      if (!isDrawingLine.value) return;
      
      const rect = (event.target as HTMLElement).getBoundingClientRect();
      mouseMovePos.value = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
      };
    };
    
    // 處理滑鼠放開事件
    const handleMouseUp = (event: MouseEvent) => {
      if (!isDrawingLine.value) return;
      
      const rect = (event.target as HTMLElement).getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      // 設置終點
      lineEnd.value = { x, y };
      isDrawingLine.value = false;
      
      // 發送剖面數據
      sendProfileData();
    };
    
    // 獲取物理座標
    const getPhysicalCoordinates = (point: Point, plotlyRect: DOMRect) => {
      const { width, height, xRange, yRange } = props.dimensions;
      
      // 計算點在圖像上的相對位置
      const relX = point.x / plotlyRect.width;
      const relY = 1 - (point.y / plotlyRect.height); // Y軸翻轉，原點在左下角
      
      // 計算物理座標
      const physX = relX * xRange;
      const physY = relY * yRange;
      
      // 計算像素座標
      const pixelX = Math.floor(relX * width);
      const pixelY = Math.floor((1 - relY) * height); // 翻轉回來，原點在左上角
      
      return {
        physicalX: physX,
        physicalY: physY,
        pixelX,
        pixelY
      };
    };
    
    // 發送剖面數據
    const sendProfileData = () => {
      if (!lineStart.value || !lineEnd.value || !plotlyContainer.value) return;
      
      const rect = plotlyContainer.value.getBoundingClientRect();
      
      const startCoord = getPhysicalCoordinates(lineStart.value, rect);
      const endCoord = getPhysicalCoordinates(lineEnd.value, rect);
      
      // 發送事件
      emit('line-profile', {
        startPoint: [startCoord.pixelY, startCoord.pixelX],
        endPoint: [endCoord.pixelY, endCoord.pixelX],
        physicalStart: [startCoord.physicalX, startCoord.physicalY],
        physicalEnd: [endCoord.physicalX, endCoord.physicalY],
        unit: props.physUnit
      });
      
      // 繪製完成後，禁用線性剖面模式
      lineProfileEnabled.value = false;
      lineStart.value = null;
      lineEnd.value = null;
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
        colorscale: props.colormap,
        showscale: true,
        zauto: true
      }];
      
      // 準備布局
      const layout = {
        title: '',
        margin: { l: 50, r: 50, b: 50, t: 30 },
        xaxis: {
          title: `X (${props.physUnit})`,
          constrain: 'domain'
        },
        yaxis: {
          title: `Y (${props.physUnit})`,
          scaleanchor: 'x',
          constrain: 'domain'
        },
        coloraxis: {
          colorbar: {
            title: `Height (${props.physUnit})`
          }
        },
        autosize: true
      };
      
      // 設置配置
      const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: [
          'toImage', 'sendDataToCloud', 'editInChartStudio', 
          'toggleHover', 'toggleSpikelines', 'resetScale2d'
        ],
        displaylogo: false
      };
      
      // 創建圖表
      Plotly.newPlot(plotlyContainer.value, data, layout, config);
      
      // 保存圖表實例用於更新
      plotlyInstance = plotlyContainer.value;
      console.log('Creating Plotly chart with data:', props.imageRawData);
      console.log('Container element:', plotlyContainer.value);
    };
    
    // 更新 Plotly 圖表
    const updatePlotlyChart = () => {
      if (!props.imageRawData || !plotlyInstance) return;
      
      // 更新數據和顏色映射
      Plotly.update(plotlyInstance, {
        z: [props.imageRawData],
        colorscale: [props.colormap]
      });
    };
    
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
    
    // 監視 colormap 變化
    watch(() => props.colormap, () => {
      updatePlotlyChart();
    });
    
    // 監視 zScale 變化
    watch(() => props.zScale, () => {
      // 這裡我們需要通過修改 coloraxis 來調整顯示範圍
      if (plotlyInstance) {
        const zMin = props.stats ? props.stats.min : null;
        const zMax = props.stats ? props.stats.max : null;
        
        if (zMin !== null && zMax !== null) {
          const zRange = zMax - zMin;
          const mid = (zMax + zMin) / 2;
          
          // 根據 zScale 調整顯示範圍
          const newZMin = mid - (zRange / 2) / props.zScale;
          const newZMax = mid + (zRange / 2) / props.zScale;
          
          Plotly.relayout(plotlyInstance, {
            'coloraxis.cmin': newZMin,
            'coloraxis.cmax': newZMax
          });
        }
      }
    });
    
    // 組件掛載時
    onMounted(() => {
      if (props.imageRawData) {
        createPlotlyChart();
      }
    });
    
    return {
      imageContainer,
      plotlyContainer,
      lineProfileEnabled,
      isDrawingLine,
      lineStart,
      lineEnd,
      mouseMovePos,
      formatNumber,
      handleClick,
      toggleLineProfile,
      handleMouseDown,
      handleMouseMove,
      handleMouseUp
    };
  }
});
</script>

<style scoped>
/* 自定義樣式 */
.image-viewer.active {
  outline: 2px solid rgba(59, 130, 246, 0.5);
  outline-offset: -2px;
}
</style>