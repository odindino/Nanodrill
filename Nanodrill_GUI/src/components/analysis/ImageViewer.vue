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
          :class="{'profile-measure-mode': profileMeasureMode}"
          @click="handlePlotClick"
          @mousedown.stop
          @mouseup.stop>
      </div>
      
      <!-- 無圖像數據提示 -->
      <div v-else class="absolute inset-0 flex items-center justify-center bg-gray-50">
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
import { defineComponent, ref, computed, watch, onMounted } from 'vue';
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
    // 圖像容器引用
    const imageContainer = ref<HTMLElement | null>(null);
    const plotlyContainer = ref<HTMLElement | null>(null);
    let plotlyInstance: any = null;
    
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
     * 獲取物理座標
     * @param point 點擊點相對於容器的坐標
     * @param plotlyRect 容器的 DOMRect
     * @returns 物理坐標
     */
    const getPhysicalCoordinates = (point: { x: number, y: number }, plotlyRect: DOMRect) => {
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
        zauto: true
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
      
      // 如果在測量模式下，禁用 Plotly 的默認交互
      if (props.profileMeasureMode) {
        Plotly.relayout(plotlyContainer.value, {
          'dragmode': false,
          'hovermode': false,
          'clickmode': 'none'
        });
      }
      
      // 添加 Plotly 事件監聽，覆蓋默認行為
      if (plotlyInstance) {
        plotlyInstance.on('plotly_click', function(data) {
          if (props.profileMeasureMode) {
            // 阻止默認行為
            return false;
          }
        });
      }

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

    // 測量點處理
    const measurePoints = ref<Point[]>([]);

    // 處理圖表點擊
    const handlePlotClick = (event: MouseEvent) => {
      // 確保 event 是有效的
      if (event) {
        event.stopPropagation();
      }
      
      // 如果不在測量模式或沒有 Plotly 容器，直接返回
      if (!props.profileMeasureMode || !plotlyContainer.value) {
        return;
      }
      
      // 獲取點擊位置相對於 Plotly 容器的坐標
      const rect = plotlyContainer.value.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      // 計算物理坐標
      const physCoords = getPhysicalCoordinates({x, y}, rect);
      
      // 在 Plotly 上標記點
      markPointOnPlot(physCoords);
      
      // 保存測量點
      measurePoints.value.push({
        x: physCoords.physicalX,
        y: physCoords.physicalY
      });
      
      // 如果已經有兩個點，則計算並繪製剖面線
      if (measurePoints.value.length === 2) {
        drawProfileLine();
        // 發送測量完成事件
        emitMeasureCompleted();
        // 清空測量點，準備下一次測量
        measurePoints.value = [];
      }
    };

    /**
     * 在 Plotly 圖表上標記點
     * @param coords 物理坐標
     */
    const markPointOnPlot = (coords: { physicalX: number, physicalY: number }) => {
      if (!plotlyInstance) return;
      
      // 創建標記數據
      const pointData = {
        x: [coords.physicalX],
        y: [coords.physicalY],
        mode: 'markers',
        type: 'scatter',
        marker: {
          size: 10,
          color: 'red',
          symbol: 'circle'
        },
        showlegend: false,
        hoverinfo: 'none'
      };
      
      // 更新 Plotly 圖表，添加標記
      Plotly.addTraces(plotlyInstance, pointData);
    };

    /**
     * 繪製兩點之間的剖面線
     */
    const drawProfileLine = () => {
      if (!plotlyInstance || measurePoints.value.length !== 2) return;
      
      const [start, end] = measurePoints.value;
      
      // 創建線數據
      const lineData = {
        x: [start.x, end.x],
        y: [start.y, end.y],
        mode: 'lines',
        type: 'scatter',
        line: {
          color: 'red',
          width: 2,
          dash: 'solid'
        },
        showlegend: false,
        hoverinfo: 'none'
      };
      
      // 更新 Plotly 圖表，添加線
      Plotly.addTraces(plotlyInstance, lineData);
    };

    /**
     * 發送測量完成事件
     */
    const emitMeasureCompleted = () => {
      if (measurePoints.value.length !== 2) return;
      
      const [start, end] = measurePoints.value;
      
      // 獲取源圖像數據
      const sourceData = {
        imageRawData: props.imageRawData,
        dimensions: props.dimensions
      };
      
      // 計算開始和結束點的像素坐標
      const startPixel = getPixelCoordinates(start);
      const endPixel = getPixelCoordinates(end);
      
      // 發送測量完成事件，包含所需信息
      emit('measure-completed', {
        sourceViewerId: props.id,
        startPoint: [startPixel.x, startPixel.y],
        endPoint: [endPixel.x, endPixel.y],
        sourceData,
        targetProfileViewer: props.targetProfileViewer
      });
      
      // 當測量完成後，關閉測量模式
      // 這可能需要通過 store 來處理
      // 或者發送一個事件通知父組件
    };

    /**
     * 獲取像素坐標
     * @param physPoint 物理坐標點
     * @returns 像素坐標
     */
    const getPixelCoordinates = (physPoint: { x: number, y: number }) => {
      const { width, height, xRange, yRange } = props.dimensions;
      
      // 計算相對位置
      const relX = physPoint.x / xRange;
      const relY = physPoint.y / yRange;
      
      // 計算像素坐標
      const pixelX = Math.floor(relX * width);
      const pixelY = Math.floor((1 - relY) * height); // Y軸原點在左上角，需要翻轉
      
      return { x: pixelX, y: pixelY };
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
    
    // 監視色彩映射變化
    watch(() => props.colormap, () => {
      updatePlotlyChart();
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
      handleClick,
      closeViewer,
      formatNumber,
      handlePlotClick,
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