<!-- src/components/analysis/ProfileViewer.vue -->
<template>
  <div class="profile-viewer h-full flex flex-col bg-white rounded-lg overflow-hidden"
       :class="{ 'ring-2 ring-primary': isActive }"
       @click="handleClick">
    <!-- 控制欄 -->
    <div class="flex items-center justify-between px-3 py-2 bg-gray-50 border-b border-gray-200">
      <div class="flex-1 flex flex-col">
        <h3 class="text-sm font-medium text-gray-700 truncate">{{ title || 'Profile Viewer' }}</h3>
        <div v-if="sourceViewerTitle" class="text-xs text-gray-500">
          來源：{{ sourceViewerTitle }}
        </div>
      </div>
      
      <!-- 關閉按鈕 -->
      <button 
        v-if="allowClose" 
        @click.stop="$emit('close')"
        class="p-1.5 rounded hover:bg-gray-200 text-gray-600 focus:outline-none"
        title="關閉"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <!-- 主要剖面圖顯示區域 -->
    <div class="flex-grow overflow-hidden relative" ref="plotlyContainer">
      <!-- 載入中顯示 -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-gray-50">
        <div class="flex flex-col items-center">
          <div class="w-8 h-8 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-2"></div>
          <span class="text-sm text-gray-600">載入中...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import type { PropType } from 'vue';
import Plotly from 'plotly.js-dist-min';

export default defineComponent({
  name: 'ProfileViewer',
  props: {
    id: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: 'Line Profile'
    },
    physUnit: {
      type: String,
      default: 'nm'
    },
    allowClose: {
      type: Boolean,
      default: true
    },
    isActive: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    // 來源ImageViewer的ID
    sourceViewerId: {
      type: String,
      default: ''
    },
    // 來源ImageViewer的標題
    sourceViewerTitle: {
      type: String,
      default: ''
    }
  },
  emits: ['click', 'close'],
  setup(props, { emit }) {
    // Plotly 圖表引用
    const plotlyContainer = ref<HTMLElement | null>(null);
    
    // 處理點擊事件
    const handleClick = (event: MouseEvent) => {
      // 確保 event 是有效的
      if (event) {
        event.stopPropagation();
      }
      emit('click');
    };
    
    // 創建默認的剖面圖
    const createDefaultPlotly = () => {
      if (!plotlyContainer.value) return;
      
      // 創建一個簡單的水平線 (值全為0)
      const x = [0, 1, 2, 3, 4];
      const y = [0, 0, 0, 0, 0];
      
      const data = [{
        x: x,
        y: y,
        type: 'scatter',
        mode: 'lines+markers',
        line: {
          color: 'royalblue',
          width: 2
        },
        name: '剖面數據'
      }];
      
      const layout = {
        title: '',
        xaxis: {
          title: `Distance (${props.physUnit})`,
          showgrid: true,
          gridcolor: '#e5e5e5',
          gridwidth: 1,
          linewidth: 2,
          linecolor: 'black',
          zeroline: false
        },
        yaxis: {
          title: `Height (${props.physUnit})`,
          showgrid: true,
          gridcolor: '#e5e5e5',
          gridwidth: 1,
          linewidth: 2,
          linecolor: 'black',
          zeroline: false
        },
        margin: { l: 60, r: 30, t: 30, b: 60 },
        showlegend: false,
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        autosize: true
      };
      
      const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: [
          'sendDataToCloud', 'editInChartStudio'
        ],
        displaylogo: false
      };
      
      Plotly.newPlot(plotlyContainer.value, data, layout, config);
    };
    
    // 組件掛載時創建圖表
    onMounted(() => {
      createDefaultPlotly();
    });
    
    return {
      plotlyContainer,
      handleClick
    };
  }
});
</script>

<style scoped>
/* 確保視圖高度填滿容器 */
.profile-viewer {
  height: 100%;
}
</style>