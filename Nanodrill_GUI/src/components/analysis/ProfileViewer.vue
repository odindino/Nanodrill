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
      
      <div class="flex space-x-2">
        <!-- 測量新剖面按鈕 -->
        <button 
          v-if="sourceViewerId && !hideControls" 
          @click.stop="toggleMeasureMode"
          class="p-1.5 rounded hover:bg-gray-200 focus:outline-none"
          :class="{ 'bg-blue-500 text-white': isMeasuring, 'text-gray-600': !isMeasuring }"
          :title="isMeasuring ? '取消測量' : '測量新剖面'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
        </button>
        
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
    </div>
    
    <!-- 主要剖面圖顯示區域 -->
    <div class="flex-grow overflow-hidden relative min-h-[300px]" ref="profileContainer">
      <!-- 載入中顯示 -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-gray-50">
        <div class="flex flex-col items-center">
          <div class="w-8 h-8 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-2"></div>
          <span class="text-sm text-gray-600">載入中...</span>
        </div>
      </div>
      
      <!-- Plotly 剖面圖 -->
      <div class="h-full w-full" ref="plotlyContainer"></div>
      
      <!-- 無數據提示 -->
      <div v-if="!profileData && !loading" class="absolute inset-0 flex items-center justify-center bg-gray-50">
        <div class="text-center p-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto text-gray-300 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
          </svg>
          <p class="text-sm text-gray-500 mb-1">尚未有剖面數據</p>
          <p v-if="sourceViewerId" class="text-xs text-gray-400">點擊上方測量按鈕開始新的剖面測量</p>
        </div>
      </div>
      
      <!-- 測量模式提示 -->
      <div v-if="isMeasuring" class="absolute top-2 left-2 right-2 bg-blue-100 text-blue-800 p-2 rounded-md text-sm">
        已進入測量模式！請在圖像視圖中點擊設置起點和終點
      </div>
    </div>
    
    <!-- 統計信息面板 -->
    <div v-if="showStats && roughness" class="py-2 px-3 bg-gray-50 border-t border-gray-200 text-xs">
      <div class="grid grid-cols-4 gap-2">
        <div class="text-gray-600">
          <span class="font-medium">Ra:</span> {{ formatNumber(roughness.Ra) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">Rq:</span> {{ formatNumber(roughness.Rq) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">Rz:</span> {{ formatNumber(roughness.Rz) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">長度:</span> {{ formatNumber(profileLength) }} {{ physUnit }}
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import type { PropType } from 'vue';
import Plotly from 'plotly.js-dist-min';

// 粗糙度介面
interface Roughness {
  Ra: number;
  Rq: number;
  Rz: number;
  Rsk: number;
  Rku: number;
}

// 剖面數據介面
interface ProfileData {
  distance: number[];
  height: number[];
  length: number;
  stats: Record<string, number>;
}

export default defineComponent({
  name: 'ProfileViewer',
  props: {
    id: {
      type: String,
      default: ''
    },
    profileData: {
      type: Object as PropType<ProfileData | null>,
      default: null
    },
    roughness: {
      type: Object as PropType<Roughness | null>,
      default: null
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
  emits: ['click', 'close', 'toggle-measure-mode'],
  setup(props, { emit }) {
    // Plotly 圖表引用
    const plotlyContainer = ref<HTMLElement | null>(null);
    let plotlyInstance: any = null;
    
    // 測量模式狀態
    const isMeasuring = ref(false);
    
    // 計算剖面長度
    const profileLength = computed(() => {
      return props.profileData?.length || 0;
    });
    
    // 格式化數字，保留兩位小數
    const formatNumber = (value: number) => {
      if (value === undefined || value === null) return 'N/A';
      return value.toFixed(2);
    };
    
    // 處理點擊事件
    const handleClick = () => {
      emit('click');
    };
    
    // 切換測量模式
    const toggleMeasureMode = () => {
      isMeasuring.value = !isMeasuring.value;
      emit('toggle-measure-mode', {
        isMeasuring: isMeasuring.value,
        sourceViewerId: props.sourceViewerId,
        profileViewerId: props.id
      });
    };
    
    // 創建默認的剖面數據
    const createDefaultProfileData = () => {
      // 創建一個簡單的水平線 (10 個點)
      const distance = Array.from({ length: 10 }, (_, i) => i);
      const height = Array.from({ length: 10 }, () => 0);
      
      return {
        distance,
        height
      };
    };
    
    // 創建 Plotly 剖面圖
    const createPlotlyChart = () => {
      if (!plotlyContainer.value) return;
      
      // 決定使用實際數據還是默認數據
      const { distance, height } = props.profileData || createDefaultProfileData();
      
      console.log('創建剖面圖，數據點數:', distance.length);
      
      // 準備數據
      const data = [{
        x: distance,
        y: height,
        type: 'scatter',
        mode: 'lines',
        line: {
          color: 'royalblue',
          width: 2
        },
        name: 'Height Profile'
      }];
      
      // 設置布局
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
      
      // 設置配置
      const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: [
          'sendDataToCloud', 'editInChartStudio'
        ],
        displaylogo: false
      };
      
      // 創建圖表
      Plotly.newPlot(plotlyContainer.value, data, layout, config);
      
      // 保存圖表實例
      plotlyInstance = plotlyContainer.value;
    };
    
    // 更新剖面圖
    const updatePlotlyChart = () => {
      if (plotlyInstance) {
        Plotly.purge(plotlyInstance);
      }
      createPlotlyChart();
    };
    
    // 監視剖面數據變化
    watch(() => props.profileData, () => {
      console.log('profileData變更，更新圖表');
      updatePlotlyChart();
    }, { deep: true });
    
    // 組件掛載時創建圖表
    onMounted(() => {
      console.log('ProfileViewer掛載');
      createPlotlyChart();
    });
    
    return {
      plotlyContainer,
      profileLength,
      isMeasuring,
      formatNumber,
      handleClick,
      toggleMeasureMode
    };
  }
});
</script>

<style scoped>
/* 自定義樣式 */
.profile-viewer {
  /* 確保完整高度 */
  height: 100%;
}
</style>