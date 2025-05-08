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
        <!-- 重新測量按鈕 -->
        <button 
          v-if="hasProfileData && sourceViewerId"
          @click.stop="startNewMeasurement"
          class="p-1.5 rounded hover:bg-gray-200 text-blue-600 focus:outline-none"
          title="重新測量"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
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
    <div class="flex-grow overflow-hidden relative" ref="plotlyContainer">
      <!-- 載入中顯示 -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-gray-50">
        <div class="flex flex-col items-center">
          <div class="w-8 h-8 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-2"></div>
          <span class="text-sm text-gray-600">載入中...</span>
        </div>
      </div>
      
      <!-- 無數據提示 -->
      <div v-if="!hasProfileData && !loading" class="absolute inset-0 flex items-center justify-center bg-gray-50">
        <div class="text-center p-6">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p class="text-sm text-gray-600 mb-2">尚未有剖面數據</p>
          <div v-if="sourceViewerId" class="mt-3">
            <button 
              @click.stop="startNewMeasurement"
              class="px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              進行剖面測量
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 統計數據面板 -->
    <div v-if="roughnessStats && showStats" class="p-2 bg-gray-50 border-t border-gray-200 text-xs">
      <div class="grid grid-cols-4 gap-2">
        <div class="text-gray-600">
          <span class="font-medium">Ra:</span> {{ formatNumber(roughnessStats.Ra) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">Rq:</span> {{ formatNumber(roughnessStats.Rq) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">Rz:</span> {{ formatNumber(roughnessStats.Rz) }} {{ physUnit }}
        </div>
        <div class="text-gray-600">
          <span class="font-medium">長度:</span> {{ formatNumber(profileLength) }} {{ physUnit }}
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

interface RoughnessStats {
  Ra: number;  // 算術平均粗糙度
  Rq: number;  // 均方根粗糙度
  Rz: number;  // 最大高度差
  Rsk: number; // 偏度
  Rku: number; // 峰度
}

interface ProfilePoint {
  distance: number;
  height: number;
}

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
    },
    // 剖面數據
    profileData: {
      type: Array as PropType<{ distance: number, height: number }[]>,
      default: () => []
    },
    // 粗糙度統計
    roughnessStats: {
      type: Object as PropType<RoughnessStats | null>,
      default: null
    }
  },
  emits: ['click', 'close', 'start-measurement'],
  setup(props, { emit }) {
    // 使用 LineProfileStateStore
    const lineProfileStore = useLineProfileStateStore();
    
    // Plotly 圖表引用
    const plotlyContainer = ref<HTMLElement | null>(null);
    let plotlyInstance: any = null;
    
    // 是否有剖面數據
    const hasProfileData = computed(() => {
      return (props.profileData && props.profileData.length > 0) || 
             (lineProfileStore.profileData && lineProfileStore.profileData.length > 0);
    });
    
    // 獲取實際應使用的剖面數據
    const effectiveProfileData = computed(() => {
      // 優先使用 props 中的數據
      if (props.profileData && props.profileData.length > 0) {
        return props.profileData;
      }
      
      // 其次使用 store 中的數據
      if (lineProfileStore.profileData && lineProfileStore.profileData.length > 0) {
        return lineProfileStore.profileData;
      }
      
      return [];
    });
    
    // 計算剖面線長度
    const profileLength = computed(() => {
      const data = effectiveProfileData.value;
      if (data.length === 0) return 0;
      
      return data[data.length - 1].distance;
    });
    
    // 格式化數字，保留2位小數
    const formatNumber = (value: number) => {
      if (value === undefined || value === null) return 'N/A';
      return value.toFixed(2);
    };
    
    // 處理點擊事件
    const handleClick = (event: MouseEvent) => {
      // 確保 event 是有效的
      if (event) {
        event.stopPropagation();
      }
      emit('click');
    };
    
    // 開始新的測量
    const startNewMeasurement = () => {
      emit('start-measurement');
    };
    
    // 創建 Plotly 剖面圖
    const createPlotlyProfile = () => {
      if (!plotlyContainer.value) return;
      
      const data = effectiveProfileData.value;
      if (data.length === 0) {
        // 沒有數據，創建空圖
        createEmptyPlot();
        return;
      }
      
      // 準備剖面數據 - 加上類型註解
      const distances = data.map((p: ProfilePoint) => p.distance);
      const heights = data.map((p: ProfilePoint) => p.height);
      
      // 準備數據
      const plotData = [{
        x: distances,
        y: heights,
        mode: 'lines',
        type: 'scatter',
        line: {
          color: 'royalblue',
          width: 2
        },
        name: '高度剖面'
      }];
      
      // 準備布局
      const layout = {
        title: '',
        xaxis: {
          title: `距離 (${props.physUnit})`,
          showgrid: true,
          gridcolor: '#e5e5e5',
          gridwidth: 1,
          linewidth: 2,
          linecolor: 'black',
          zeroline: false
        },
        yaxis: {
          title: `高度 (${props.physUnit})`,
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
      Plotly.newPlot(plotlyContainer.value, plotData, layout, config);
      plotlyInstance = plotlyContainer.value;
    };
    
    // 創建空的剖面圖
    const createEmptyPlot = () => {
      if (!plotlyContainer.value) return;
      
      // 創建一個簡單的水平線 (值全為0)
      const x = [0, 1, 2, 3, 4];
      const y = [0, 0, 0, 0, 0];
      
      const data = [{
        x: x,
        y: y,
        type: 'scatter',
        mode: 'lines',
        line: {
          color: 'gray',
          width: 1,
          dash: 'dot'
        },
        name: '無剖面數據'
      }];
      
      const layout = {
        title: '',
        xaxis: {
          title: `距離 (${props.physUnit})`,
          showgrid: true,
          gridcolor: '#e5e5e5',
          gridwidth: 1,
          linewidth: 2,
          linecolor: 'black',
          zeroline: false
        },
        yaxis: {
          title: `高度 (${props.physUnit})`,
          showgrid: true,
          gridcolor: '#e5e5e5',
          gridwidth: 1,
          linewidth: 2,
          linecolor: 'black',
          zeroline: false,
          range: [-1, 1]  // 設置一個固定的範圍
        },
        margin: { l: 60, r: 30, t: 30, b: 60 },
        showlegend: false,
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        autosize: true,
        annotations: [{
          x: 2,
          y: 0,
          xref: 'x',
          yref: 'y',
          text: '暫無剖面數據',
          showarrow: false,
          font: {
            color: 'gray',
            size: 14
          }
        }]
      };
      
      const config = {
        responsive: true,
        displayModeBar: false,
        displaylogo: false
      };
      
      // 創建圖表
      Plotly.newPlot(plotlyContainer.value, data, layout, config);
      plotlyInstance = plotlyContainer.value;
    };
    
    // 更新剖面圖
    const updatePlotlyProfile = () => {
      if (!plotlyInstance) {
        createPlotlyProfile();
        return;
      }
      
      const data = effectiveProfileData.value;
      if (data.length === 0) {
        // 沒有數據，重新創建空圖
        createEmptyPlot();
        return;
      }
      
      // 準備剖面數據
      const distances = data.map((p: ProfilePoint) => p.distance);
      const heights = data.map((p: ProfilePoint) => p.height);
      
      // 更新數據
      Plotly.update(plotlyInstance, {
        'x': [distances],
        'y': [heights]
      }, {
        'xaxis.title': `距離 (${props.physUnit})`,
        'yaxis.title': `高度 (${props.physUnit})`
      });
    };
    
    // 監視剖面數據變化
    watch(() => effectiveProfileData.value, () => {
      updatePlotlyProfile();
    });
    
    // 監視單位變化
    watch(() => props.physUnit, () => {
      if (plotlyInstance) {
        Plotly.relayout(plotlyInstance, {
          'xaxis.title': `距離 (${props.physUnit})`,
          'yaxis.title': `高度 (${props.physUnit})`
        });
      }
    });
    
    // 監視 lineProfileStore 中的剖面數據
    watch(() => lineProfileStore.profileData, () => {
      updatePlotlyProfile();
    });
    
    // 組件掛載時
    onMounted(() => {
      createPlotlyProfile();
    });
    
    // 組件卸載前清理
    onBeforeUnmount(() => {
      if (plotlyInstance) {
        Plotly.purge(plotlyInstance);
        plotlyInstance = null;
      }
    });
    
    return {
      plotlyContainer,
      handleClick,
      startNewMeasurement,
      hasProfileData,
      profileLength,
      formatNumber
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