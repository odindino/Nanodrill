<!-- Nanodrill_GUI/src/components/analysis/ImageViewer.vue -->
<template>
    <div class="h-full flex flex-col bg-white rounded-lg overflow-hidden border border-gray-200 relative"
         :class="{ 'ring-2 ring-primary': isActive }">
      <!-- 標題欄 -->
      <div class="bg-gray-50 px-3 py-2 border-b border-gray-200 flex items-center justify-between">
        <h3 class="font-medium text-sm truncate flex-grow">{{ title || 'Image Viewer' }}</h3>
        
        <!-- 控制按鈕 -->
        <div class="flex space-x-1">
          <button v-if="!hideControls" title="調整對比度"
                  class="p-1 rounded hover:bg-gray-200 text-gray-600 text-sm"
                  @click="toggleColorbarAdjust">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
            </svg>
          </button>
          <button v-if="!hideControls" title="啟用線性剖面"
                  class="p-1 rounded hover:bg-gray-200 text-gray-600 text-sm"
                  :class="{ 'bg-primary-100 text-primary': lineProfileEnabled }"
                  @click="toggleLineProfile">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </button>
          <button v-if="!hideControls" title="截圖保存"
                  class="p-1 rounded hover:bg-gray-200 text-gray-600 text-sm"
                  @click="saveImage">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
            </svg>
          </button>
          <button v-if="allowClose" title="關閉"
                  class="p-1 rounded hover:bg-gray-200 text-gray-600 text-sm"
                  @click="$emit('close')">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- 主要圖像顯示區域 -->
      <div class="flex-grow overflow-hidden relative" ref="imageContainer" @click="handleImageClick">
        <!-- 影像載入中顯示 -->
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-gray-50">
          <div class="flex flex-col items-center">
            <div class="w-8 h-8 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-2"></div>
            <span class="text-sm text-gray-600">載入中...</span>
          </div>
        </div>
        
        <!-- 實際圖像 -->
        <div v-else class="h-full w-full relative">
          <img v-if="imageData" 
               :src="'data:image/png;base64,' + imageData" 
               alt="形貌圖" 
               class="h-full max-h-full max-w-full object-contain mx-auto"
               @mousedown="handleMouseDown"
               @mouseup="handleMouseUp"
               @mousemove="handleMouseMove" />
          
          <!-- 線性剖面繪製線 -->
          <svg v-if="lineProfileEnabled" class="absolute top-0 left-0 w-full h-full pointer-events-none">
            <line v-if="isDrawingLine || lineStart && lineEnd"
                  :x1="lineStart?.x || 0"
                  :y1="lineStart?.y || 0"
                  :x2="isDrawingLine ? mouseMovePos.x : (lineEnd?.x || 0)"
                  :y2="isDrawingLine ? mouseMovePos.y : (lineEnd?.y || 0)"
                  stroke="#ff6b6b"
                  stroke-width="2"
                  stroke-dasharray="5,5"
                  vector-effect="non-scaling-stroke" />
            
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
        </div>
        
        <!-- 無圖像提示 -->
        <div v-if="!loading && !imageData" class="absolute inset-0 flex items-center justify-center bg-gray-50">
          <div class="text-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="text-sm text-gray-500">尚未載入圖像</span>
          </div>
        </div>
      </div>
      
      <!-- 色彩調整面板 -->
      <div v-if="showColorbarAdjust" class="border-t border-gray-200 p-3 bg-gray-50">
        <div class="space-y-3">
          <div>
            <div class="flex justify-between mb-1">
              <label class="text-xs text-gray-600">色彩映射</label>
              <span class="text-xs text-gray-600">{{ colormap }}</span>
            </div>
            <select 
              v-model="colormap" 
              class="w-full text-sm border border-gray-300 rounded py-1 px-2 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
            >
              <option value="viridis">Viridis</option>
              <option value="plasma">Plasma</option>
              <option value="inferno">Inferno</option>
              <option value="magma">Magma</option>
              <option value="cividis">Cividis</option>
              <option value="Oranges">Oranges</option>
              <option value="hot">Hot</option>
              <option value="cool">Cool</option>
              <option value="jet">Jet</option>
            </select>
          </div>
          
          <div>
            <div class="flex justify-between mb-1">
              <label class="text-xs text-gray-600">Z軸縮放</label>
              <span class="text-xs text-gray-600">{{ zScale.toFixed(1) }}x</span>
            </div>
            <input 
              type="range" 
              v-model="zScale" 
              min="0.1" 
              max="5" 
              step="0.1" 
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            >
          </div>
        </div>
      </div>
      
      <!-- 統計信息面板 -->
      <div v-if="showStats && stats" class="border-t border-gray-200 p-2 bg-gray-50 text-xs">
        <div class="flex flex-wrap justify-between text-gray-600">
          <span>最小值: {{ formatNumber(stats.min) }} {{ physUnit }}</span>
          <span>最大值: {{ formatNumber(stats.max) }} {{ physUnit }}</span>
          <span>平均值: {{ formatNumber(stats.mean) }} {{ physUnit }}</span>
          <span>RMS: {{ formatNumber(stats.rms) }} {{ physUnit }}</span>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
import { defineComponent, ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import type { PropType } from 'vue';

// 定義統計信息介面
interface ImageStats {
  min: number;
  max: number;
  mean: number;
  median: number;
  std: number;
  rms: number;
}

// 定義線性剖面上的點
interface ProfilePoint {
  x: number;
  y: number;
  // 真實物理坐標
  realX?: number;
  realY?: number;
}

export default defineComponent({
  name: 'ImageViewer',
  props: {
    imageData: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: ''
    },
    imageType: {
      type: String,
      default: 'topo'
    },
    physUnit: {
      type: String,
      default: 'nm'
    },
    initialColormap: {
      type: String,
      default: 'Oranges'
    },
    initialZScale: {
      type: Number,
      default: 1.0
    },
    initialStats: {
      type: Object as PropType<ImageStats | null>,
      default: null
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
    },
    dimensions: {
      type: Object as PropType<{width: number, height: number, xRange: number, yRange: number}>,
      default: () => ({width: 0, height: 0, xRange: 0, yRange: 0})
    }
  },
    emits: ['update:colormap', 'update:zScale', 'line-profile', 'image-clicked', 'close'],
    setup(props, { emit }) {
      // 本地狀態
      const colormap = ref(props.initialColormap);
      const zScale = ref(props.initialZScale);
      const stats = ref<ImageStats | null>(props.initialStats);
      const showColorbarAdjust = ref(false);
      const lineProfileEnabled = ref(false);
      
      // 線性剖面相關狀態
      const imageContainer = ref<HTMLElement | null>(null);
      const isDrawingLine = ref(false);
      const lineStart = ref<ProfilePoint | null>(null);
      const lineEnd = ref<ProfilePoint | null>(null);
      const mouseMovePos = ref({ x: 0, y: 0 });
      
      // 格式化數字，保留兩位小數
      const formatNumber = (value: number) => {
        if (value === undefined || value === null) return 'N/A';
        return value.toFixed(2);
      };
      
      // 切換色彩調整面板顯示
      const toggleColorbarAdjust = () => {
        showColorbarAdjust.value = !showColorbarAdjust.value;
      };
      
      // 切換線性剖面功能
      const toggleLineProfile = () => {
        if (!props.allowProfile) return;
        
        lineProfileEnabled.value = !lineProfileEnabled.value;
        // 如果關閉了線性剖面，重置相關狀態
        if (!lineProfileEnabled.value) {
          isDrawingLine.value = false;
          lineStart.value = null;
          lineEnd.value = null;
        }
      };
      
      // 處理圖像點擊事件
      const handleImageClick = (event: MouseEvent) => {
        // 發送點擊事件
        emit('image-clicked');
        
        // 如果線性剖面功能未啟用，直接返回
        if (!lineProfileEnabled.value) return;
        
        // 獲取點擊位置
        const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // 處理線性剖面相關邏輯
        if (!lineStart.value) {
          // 設置起點
          lineStart.value = { x, y };
        } else if (!lineEnd.value) {
          // 設置終點
          lineEnd.value = { x, y };
          // 通知父組件生成剖面
          sendProfileData();
        } else {
          // 重置，開始新的線
          lineStart.value = { x, y };
          lineEnd.value = null;
        }
      };
      
      // 處理滑鼠按下事件
      const handleMouseDown = (event: MouseEvent) => {
        if (!lineProfileEnabled.value) return;
        
        const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // 設置起點並開始繪製
        lineStart.value = { x, y };
        isDrawingLine.value = true;
      };
      
      // 處理滑鼠移動事件
      const handleMouseMove = (event: MouseEvent) => {
        if (!isDrawingLine.value) return;
        
        const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
        mouseMovePos.value = {
          x: event.clientX - rect.left,
          y: event.clientY - rect.top
        };
      };
      
      // 處理滑鼠放開事件
      const handleMouseUp = (event: MouseEvent) => {
        if (!isDrawingLine.value) return;
        
        const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // 設置終點
        lineEnd.value = { x, y };
        isDrawingLine.value = false;
        
        // 通知父組件生成剖面
        sendProfileData();
      };
      
      // 獲取圖像上的實際物理座標
      const getPhysicalCoordinates = (point: ProfilePoint, imgRect: DOMRect, imgNaturalSize: {width: number, height: number}) => {
        // 計算圖像在容器中的實際尺寸和位置
        const imgRatio = imgNaturalSize.width / imgNaturalSize.height;
        const containerRatio = imgRect.width / imgRect.height;
        
        let imgDisplayWidth, imgDisplayHeight, offsetX, offsetY;
        
        if (imgRatio > containerRatio) {
          // 圖像寬度適應容器
          imgDisplayWidth = imgRect.width;
          imgDisplayHeight = imgDisplayWidth / imgRatio;
          offsetX = 0;
          offsetY = (imgRect.height - imgDisplayHeight) / 2;
        } else {
          // 圖像高度適應容器
          imgDisplayHeight = imgRect.height;
          imgDisplayWidth = imgDisplayHeight * imgRatio;
          offsetX = (imgRect.width - imgDisplayWidth) / 2;
          offsetY = 0;
        }
        
        // 計算點在圖像上的相對位置
        const relX = (point.x - offsetX) / imgDisplayWidth;
        const relY = 1 - (point.y - offsetY) / imgDisplayHeight; // 反轉Y坐標，因為圖像原點在左上角
        
        // 轉換為物理坐標
        const physX = relX * props.dimensions.xRange;
        const physY = relY * props.dimensions.yRange;
        
        // 轉換為像素坐標
        const pixelX = Math.floor(relX * props.dimensions.width);
        const pixelY = Math.floor((1 - relY) * props.dimensions.height);
        
        return {
          realX: physX,
          realY: physY,
          pixelX: pixelX,
          pixelY: pixelY
        };
      };
      
      // 發送剖面資料
      const sendProfileData = () => {
        if (!lineStart.value || !lineEnd.value) return;
        
        const imgElement = imageContainer.value?.querySelector('img');
        if (!imgElement) return;
        
        const imgRect = imgElement.getBoundingClientRect();
        const imgNaturalSize = {
          width: (imgElement as HTMLImageElement).naturalWidth,
          height: (imgElement as HTMLImageElement).naturalHeight
        };
        
        // 獲取起點和終點的物理座標
        const startCoord = getPhysicalCoordinates(lineStart.value, imgRect, imgNaturalSize);
        const endCoord = getPhysicalCoordinates(lineEnd.value, imgRect, imgNaturalSize);
        
        // 發送事件
        emit('line-profile', {
          startPoint: [startCoord.pixelY, startCoord.pixelX], // [y, x]格式
          endPoint: [endCoord.pixelY, endCoord.pixelX],
          startPhysical: [startCoord.realY, startCoord.realX], // [y, x]格式
          endPhysical: [endCoord.realY, endCoord.realX]
        });
      };
      
      // 保存圖像
      const saveImage = () => {
        if (!props.imageData) return;
        
        const downloadLink = document.createElement('a');
        downloadLink.href = 'data:image/png;base64,' + props.imageData;
        downloadLink.download = `${props.title || 'image'}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
      };
      
      // 監視屬性變化
      watch(() => props.initialStats, (newVal) => {
        stats.value = newVal;
      });
      
      watch(colormap, (newVal) => {
        emit('update:colormap', newVal);
      });
      
      watch(zScale, (newVal) => {
        emit('update:zScale', newVal);
      });
      
      // 組件卸載時清理事件
      onBeforeUnmount(() => {
        // 清理可能的全局事件
      });
      
      return {
        colormap,
        zScale,
        stats,
        showColorbarAdjust,
        lineProfileEnabled,
        imageContainer,
        isDrawingLine,
        lineStart,
        lineEnd,
        mouseMovePos,
        formatNumber,
        toggleColorbarAdjust,
        toggleLineProfile,
        handleImageClick,
        handleMouseDown,
        handleMouseMove,
        handleMouseUp,
        saveImage
      };
    }
  });
  </script>
  
  <style scoped>
  /* 自定義樣式 */
  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    background: #2563eb;
    border-radius: 50%;
    cursor: pointer;
  }
  
  input[type="range"]::-moz-range-thumb {
    width: 16px;
    height: 16px;
    background: #2563eb;
    border-radius: 50%;
    cursor: pointer;
  }
  </style>