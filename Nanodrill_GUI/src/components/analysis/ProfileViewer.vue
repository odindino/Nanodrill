<!-- src/components/analysis/ProfileViewer.vue -->
<template>
  <div class="profile-viewer h-full flex flex-col bg-white rounded-lg overflow-hidden"
       :class="{ 'ring-2 ring-primary': isActive }"
       @click="handleClick">
    <!-- 控制欄 -->
    <div class="flex items-center justify-between px-3 py-2 bg-gray-50 border-b border-gray-200">
      <h3 class="text-sm font-medium text-gray-700 truncate">{{ title || 'Profile Viewer' }}</h3>
      
      <div class="flex space-x-2">
        <!-- 設定按鈕 -->
        <button 
          v-if="!hideControls" 
          @click.stop="toggleSettings"
          class="p-1.5 rounded hover:bg-gray-200 text-gray-600 focus:outline-none"
          :class="{ 'bg-blue-100 text-blue-600': showSettings }"
          title="設定"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
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
    initialShiftZero: {
      type: Boolean,
      default: false
    },
    initialAutoScale: {
      type: Boolean,
      default: true
    },
    initialShowPeaks: {
      type: Boolean,
      default: false
    },
    initialPeakSensitivity: {
      type: Number,
      default: 1.0
    }
  },
  emits: ['update:settings', 'refresh', 'close', 'click'],
  setup(props, { emit }) {
    // 設置面板控制
    const showSettings = ref(false);
    const plotlyContainer = ref<HTMLElement | null>(null);
    let plotlyInstance: any = null;
    
    // 剖面圖設置
    const shiftZero = ref(props.initialShiftZero);
    const autoScale = ref(props.initialAutoScale);
    const showPeaks = ref(props.initialShowPeaks);
    const peakSensitivity = ref(props.initialPeakSensitivity);
    
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
    
    // 切換設置面板
    const toggleSettings = () => {
      showSettings.value = !showSettings.value;
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
      
      // 如果啟用了查找峰值
      if (showPeaks.value && height.length > 0) {
        // 這裏應該加入峰值檢測邏輯
        // 簡單的例子：找出局部最大值
        const peaks = findPeaks(distance, height, peakSensitivity.value);
        
        if (peaks.indices.length > 0) {
          data.push({
            x: peaks.positions,
            y: peaks.heights,
            type: 'scatter',
            mode: 'markers',
            marker: {
              color: 'red',
              size: 8,
              symbol: 'circle'
            },
            name: 'Peaks'
          });
        }
      }
      
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
      
      console.log('創建Plotly圖表');
      
      // 創建圖表
      Plotly.newPlot(plotlyContainer.value, data, layout, config);
      
      // 保存圖表實例
      plotlyInstance = plotlyContainer.value;
    };
    
    // 簡單的峰值檢測函數
    const findPeaks = (x: number[], y: number[], sensitivity = 1.0) => {
      const indices: number[] = [];
      const positions: number[] = [];
      const heights: number[] = [];
      
      // 簡單的局部最大值檢測
      for (let i = 1; i < y.length - 1; i++) {
        // 檢查當前點是否大於相鄰點
        if (y[i] > y[i-1] && y[i] > y[i+1]) {
          // 使用敏感度過濾雜訊
          const threshold = (Math.max(...y) - Math.min(...y)) * 0.02 / sensitivity;
          if (y[i] - y[i-1] > threshold && y[i] - y[i+1] > threshold) {
            indices.push(i);
            positions.push(x[i]);
            heights.push(y[i]);
          }
        }
      }
      
      return { indices, positions, heights };
    };
    
    // 更新剖面圖
    const updateProfileChart = () => {
      if (plotlyInstance) {
        Plotly.purge(plotlyInstance);
      }
      createPlotlyChart();
    };
    
    // 監視剖面數據變化
    watch(() => props.profileData, () => {
      console.log('profileData變更，更新圖表');
      updateProfileChart();
    }, { deep: true });
    
    // 監視設置變化
    watch([shiftZero, autoScale, showPeaks, peakSensitivity], () => {
      console.log('設置變更，更新圖表');
      updateProfileChart();
      
      // 發送設置更新事件
      emit('update:settings', {
        shiftZero: shiftZero.value,
        autoScale: autoScale.value,
        showPeaks: showPeaks.value,
        peakSensitivity: peakSensitivity.value
      });
    });
    
    // 組件掛載時創建圖表
    onMounted(() => {
      console.log('ProfileViewer掛載');
      createPlotlyChart();
    });
    
    return {
      showSettings,
      shiftZero,
      autoScale,
      showPeaks,
      peakSensitivity,
      profileLength,
      plotlyContainer,
      formatNumber,
      handleClick,
      toggleSettings
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