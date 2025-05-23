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
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import type { PropType } from 'vue';
import Plotly from 'plotly.js-dist-min';
import { useLineProfileStateStore } from '../../stores/lineProfileStateStore';

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
    }
  },
  emits: ['click', 'close', 'start-measurement'],
  setup(props, { emit }) {
    console.log(`ProfileViewer ${props.id} 初始化, 來源視圖: ${props.sourceViewerId}`);
    
    // 使用 LineProfileStateStore
    const lineProfileStore = useLineProfileStateStore();
    
    // Plotly 圖表引用
    const plotlyContainer = ref<HTMLElement | null>(null);
    let plotlyInstance: any = null;
    
    // 是否有剖面數據
    const hasProfileData = computed(() => {
      // 優先檢查 lineProfileStore 中的數據
      if (lineProfileStore.profileData && lineProfileStore.profileData.length > 0) {
        return true;
      }
      // 然後檢查 props 中的數據
      if (props.profileData && props.profileData.length > 0) {
        return true;
      }
      return false;
    });
    
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
      console.log(`ProfileViewer ${props.id} 請求開始新測量`);
      emit('start-measurement');
    };
    
    // 更新剖面圖
    const updateProfilePlot = (profileData: any[]) => {
      console.log("更新剖面圖，數據點數:", profileData.length);
      
      if (!plotlyContainer.value) {
        console.warn("plotlyContainer 不存在，無法更新圖");
        return;
      }
      
      try {
        // 檢查數據格式
        if (!profileData || profileData.length === 0) {
          console.warn("無效的剖面數據");
          return;
        }
        
        // 準備 X 和 Y 數據數組
        const x = profileData.map(point => point.distance);
        const y = profileData.map(point => point.height);
        
        // 計算統計信息
        const min = Math.min(...y);
        const max = Math.max(...y);
        
        // 創建圖表數據
        const data = [{
          x: x,
          y: y,
          type: 'scatter' as const,
          mode: 'lines',
          line: {
            color: 'blue',
            width: 2
          },
          name: '剖面線'
        }] as any[];
        
        // 創建布局
        const layout = {
          title: { text: '' },
          xaxis: {
            title: { text: `距離 (${props.physUnit})` },
            showgrid: true,
            gridcolor: '#e5e5e5',
            gridwidth: 1,
            range: [0, Math.max(...x)]
          },
          yaxis: {
            title: { text: `高度 (${props.physUnit})` },
            showgrid: true,
            gridcolor: '#e5e5e5',
            gridwidth: 1,
            // 設置 Y 軸範圍，上下留出10%的邊距
            range: [min - (max - min) * 0.1, max + (max - min) * 0.1]
          },
          margin: { l: 60, r: 30, t: 30, b: 60 },
          showlegend: false,
          plot_bgcolor: 'white',
          paper_bgcolor: 'white',
          autosize: true
        } as any;
        
        const config = {
          responsive: true,
          displaylogo: false
        };
        
        // 如果已經有圖表實例，則更新它；否則創建新的
        if (plotlyInstance) {
          Plotly.react(plotlyContainer.value, data, layout, config);
        } else {
          Plotly.newPlot(plotlyContainer.value, data, layout, config);
          plotlyInstance = plotlyContainer.value;
        }
        
        console.log("剖面圖更新成功");
      } catch (error) {
        console.error("更新剖面圖時出錯:", error);
      }
    };
    
    // 監聽 LineProfileStateStore 中的 profileData 變化
    watch(() => lineProfileStore.profileData, (newData) => {
      console.log("ProfileViewer: lineProfileStore.profileData 發生變化", newData);
      if (newData && newData.length > 0) {
        console.log("ProfileViewer: 開始更新剖面圖，數據點數:", newData.length);
        updateProfilePlot(newData);
      } else {
        console.log("ProfileViewer: 數據為空或無效");
      }
    }, { immediate: true, deep: true });
    
    // 監聽 props 中的 profileData 變化
    watch(() => props.profileData, (newData) => {
      if (newData && newData.length > 0) {
        updateProfilePlot(newData);
      }
    });
    
    // 剢建預設剖面圖
    const createDefaultPlot = () => {
      console.log("創建預設剖面圖");
      
      if (!plotlyContainer.value) {
        console.warn("plotlyContainer 不存在，無法創建預設圖");
        return;
      }
      
      try {
        // 創建一個簡單的水平線 (值全為0)
        const x = [0, 1, 2, 3, 4];
        const y = [0, 0, 0, 0, 0];
        
        const data = [{
          x: x,
          y: y,
          type: 'scatter' as const,
          mode: 'lines',
          line: {
            color: 'gray',
            width: 1,
            dash: 'dot'
          },
          name: '無剖面數據'
        }] as any[];
        
        const layout = {
          title: { text: '' },
          xaxis: {
            title: { text: `距離 (${props.physUnit})` },
            showgrid: true,
            gridcolor: '#e5e5e5',
            gridwidth: 1
          },
          yaxis: {
            title: { text: `高度 (${props.physUnit})` },
            showgrid: true,
            gridcolor: '#e5e5e5',
            gridwidth: 1,
            range: [-1, 1]
          },
          margin: { l: 60, r: 30, t: 30, b: 60 },
          showlegend: false,
          plot_bgcolor: 'white',
          paper_bgcolor: 'white',
          autosize: true,
          annotations: [{
            x: 2,
            y: 0,
            xref: 'x' as const,
            yref: 'y' as const,
            text: '等待測量數據',
            showarrow: false,
            font: {
              color: 'gray',
              size: 14
            }
          }] as any
        };
        
        const config = {
          responsive: true,
          displayModeBar: false,
          displaylogo: false
        };
        
        // 創建圖表
        Plotly.newPlot(plotlyContainer.value, data, layout, config);
        plotlyInstance = plotlyContainer.value;
        
        console.log("預設剖面圖創建成功");
      } catch (error) {
        console.error("創建預設剖面圖時出錯:", error);
      }
    };
    
    // 組件掛載時
    onMounted(() => {
      console.log(`ProfileViewer ${props.id} 已掛載`);
      createDefaultPlot();
      
      // 檢查是否已有數據需要顯示
      if (lineProfileStore.profileData && lineProfileStore.profileData.length > 0) {
        console.log("ProfileViewer: 掛載時發現已有數據，立即更新圖表");
        updateProfilePlot(lineProfileStore.profileData);
      } else if (props.profileData && props.profileData.length > 0) {
        console.log("ProfileViewer: 掛載時發現 props 中有數據，立即更新圖表");
        updateProfilePlot(props.profileData);
      }
    });
    
    // 組件卸載前清理
    onBeforeUnmount(() => {
      console.log(`ProfileViewer ${props.id} 即將卸載`);
      
      if (plotlyInstance) {
        console.log("清理 Plotly 實例");
        Plotly.purge(plotlyInstance);
        plotlyInstance = null;
      }
    });
    
    return {
      plotlyContainer,
      handleClick,
      startNewMeasurement,
      hasProfileData
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