<!-- src/components/analysis/ToolsPanel.vue -->
<template>
  <div 
    class="sidebar-panel bg-white border-r border-gray-200 transition-all duration-300 flex flex-col mt-2"
    :class="showToolsPanel ? 'w-80' : 'w-12'"
  >
    <!-- 標題或迷你按鈕 -->
    <div 
      class="flex items-center p-2 border-b border-gray-200 bg-gray-50"
      :class="showToolsPanel ? 'justify-between' : 'justify-center'"
    >
      <h3 v-if="showToolsPanel" class="text-sm font-medium text-gray-700 truncate">工具列</h3>
      <button 
        @click="toggleToolsPanel"
        class="p-1.5 rounded hover:bg-gray-200 text-gray-600 focus:outline-none"
        :title="showToolsPanel ? '收起工具列' : '展開工具列'"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-5 w-5" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
          :class="{ 'transform rotate-180': showToolsPanel }"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
    </div>
    
    <!-- 工具列內容 -->
    <div v-if="showToolsPanel" class="flex-grow overflow-y-auto p-4">
      <template v-if="activeViewer">
        <div v-if="activeViewer.component === 'ImageViewer'" class="space-y-4">
          <h4 class="font-medium text-sm border-b pb-2 mb-2">影像處理</h4>
          
          <!-- 平面校正工具 -->
          <div>
            <label class="text-xs text-gray-500 block mb-1">平面校正</label>
            <div class="flex space-x-2">
              <button 
                @click="applyFlatten('mean')"
                class="flex-1 py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
              >
                線性平面化
              </button>
              <button 
                @click="applyFlatten('polyfit')"
                class="flex-1 py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
              >
                多項式平面化
              </button>
            </div>
          </div>
          
          <!-- 傾斜調整工具 -->
          <div>
            <label class="text-xs text-gray-500 block mb-1">傾斜調整</label>
            <div class="grid grid-cols-2 gap-2">
              <div class="col-span-2 mb-1">
                <div class="flex items-center">
                  <input 
                    type="checkbox" 
                    id="tilt-fine-tune" 
                    v-model="fineTuneTilt"
                    class="h-3 w-3 text-primary focus:ring-primary border-gray-300 rounded"
                  >
                  <label for="tilt-fine-tune" class="ml-1 text-xs text-gray-700">
                    微調模式
                  </label>
                </div>
              </div>
              <button 
                @click="adjustTilt('up')"
                class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
              >
                向上傾斜
              </button>
              <button 
                @click="adjustTilt('down')"
                class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
              >
                向下傾斜
              </button>
              <button 
                @click="adjustTilt('left')"
                class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
              >
                向左傾斜
              </button>
              <button 
                @click="adjustTilt('right')"
                class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
              >
                向右傾斜
              </button>
            </div>
          </div>
          
          <!-- 色彩映射 -->
          <div>
            <label class="text-xs text-gray-500 block mb-1">色彩映射</label>
            <select 
              v-model="activeTabColormap" 
              class="w-full text-sm border border-gray-300 rounded py-1.5 px-2 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
              @change="updateActiveTabSettings({colormap: activeTabColormap})"
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
          
          <!-- 高度縮放 -->
          <div>
            <div class="flex justify-between mb-1">
              <label class="text-xs text-gray-500">高度縮放</label>
              <span class="text-xs text-gray-500">{{ activeTabZScale.toFixed(1) }}x</span>
            </div>
            <input 
              type="range" 
              v-model="activeTabZScale" 
              min="0.1" 
              max="5" 
              step="0.1" 
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              @change="updateActiveTabSettings({zScale: activeTabZScale})"
            >
          </div>
          
          <!-- 剖面分析 -->
          <div>
            <label class="text-xs text-gray-500 block mb-1">剖面分析</label>
            <button 
              @click="handleCreateLineProfile"
              class="w-full py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
            >
              建立線性剖面
            </button>
          </div>
        </div>
        
        <!-- 剖面視圖工具 -->
        <div v-else-if="activeViewer.component === 'ProfileViewer'" class="space-y-4">
          <h4 class="font-medium text-sm border-b pb-2 mb-2">剖面設定</h4>
          
          <!-- 將最小值歸零選項 -->
          <div class="flex items-center">
            <input 
              type="checkbox" 
              id="shift-zero" 
              v-model="profileSettings.shiftZero"
              class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              @change="updateProfile"
            >
            <label for="shift-zero" class="ml-2 text-sm text-gray-700">
              將最小值歸零
            </label>
          </div>
          
          <!-- 自動縮放選項 -->
          <div class="flex items-center">
            <input 
              type="checkbox" 
              id="auto-scale" 
              v-model="profileSettings.autoScale"
              class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              @change="updateProfile"
            >
            <label for="auto-scale" class="ml-2 text-sm text-gray-700">
              自動縮放
            </label>
          </div>
          
          <!-- 顯示峰值選項 -->
          <div class="flex items-center">
            <input 
              type="checkbox" 
              id="show-peaks" 
              v-model="profileSettings.showPeaks"
              class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              @change="updateProfile"
            >
            <label for="show-peaks" class="ml-2 text-sm text-gray-700">
              顯示峰值
            </label>
          </div>
          
          <!-- 峰值敏感度 -->
          <div v-if="profileSettings.showPeaks">
            <div class="flex justify-between mb-1">
              <label class="text-xs text-gray-500">峰值敏感度</label>
              <span class="text-xs text-gray-500">{{ profileSettings.peakSensitivity.toFixed(1) }}</span>
            </div>
            <input 
              type="range" 
              v-model="profileSettings.peakSensitivity" 
              min="0.1" 
              max="5" 
              step="0.1" 
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              @change="updateProfile"
            >
          </div>
        </div>
        
        <div v-else class="p-4 text-center text-gray-500">
          <p>無可用工具</p>
        </div>
      </template>
      
      <div v-else class="p-4 text-center text-gray-500">
        <p>請選擇一個視圖來顯示相應工具</p>
      </div>
    </div>
    
    <!-- 迷你模式下只顯示圖標 -->
    <div v-else class="flex-grow flex flex-col items-center pt-3">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed} from 'vue';
import type { PropType } from 'vue';
import type { Viewer } from './ViewerGroup.vue';

export default defineComponent({
  name: 'ToolsPanel',
  props: {
    activeViewer: {
      type: Object as PropType<Viewer | null>,
      default: null
    },
    activeTabColormap: {
      type: String,
      default: 'Oranges'
    },
    activeTabZScale: {
      type: Number,
      default: 1.0
    }
  },
  emits: [
    'toggle-panel', 
    'update-settings', 
    'apply-flatten', 
    'adjust-tilt', 
    'create-line-profile', 
    'update-profile'
  ],
  setup(props, { emit }) {
    const showToolsPanel = ref(true);
    const fineTuneTilt = ref(false);
    
    // 剖面相關設置
    const profileSettings = ref({
      shiftZero: false,
      autoScale: true,
      showPeaks: false,
      peakSensitivity: 1.0
    });
    
    // 切換工具面板
    const toggleToolsPanel = () => {
      showToolsPanel.value = !showToolsPanel.value;
      emit('toggle-panel', showToolsPanel.value);
    };
    
    // 更新標籤頁設置
    const updateActiveTabSettings = (settings: any) => {
      emit('update-settings', settings);
    };
    
    // 應用平面化
    const applyFlatten = (method: string) => {
      console.log('工具面板呼叫平面化:', method);
      emit('apply-flatten', method);
    };
    
    // 調整傾斜
    const adjustTilt = (direction: string) => {
      console.log('工具面板呼叫傾斜調整:', direction, fineTuneTilt.value);
      emit('adjust-tilt', { direction, fineTune: fineTuneTilt.value });
    };
    
    // 建立線性剖面 
    const handleCreateLineProfile = () => {
      console.log('工具面板呼叫建立線性剖面');
      emit('create-line-profile');
    };
    
    // 更新剖面圖
    const updateProfile = () => {
      console.log('工具面板呼叫更新剖面:', profileSettings.value);
      emit('update-profile', profileSettings.value);
    };
    
    return {
      showToolsPanel,
      fineTuneTilt,
      profileSettings,
      toggleToolsPanel,
      updateActiveTabSettings,
      applyFlatten,
      adjustTilt,
      handleCreateLineProfile,
      updateProfile
    };
  }
});
</script>

<style scoped>
/* 自定義樣式 */
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 14px;
  background: #2563eb;
  border-radius: 50%;
  cursor: pointer;
}

input[type="range"]::-moz-range-thumb {
  width: 14px;
  height: 14px;
  background: #2563eb;
  border-radius: 50%;
  cursor: pointer;
}

/* 側邊面板高度設置 */
.sidebar-panel {
  max-height: calc(50vh - 30px);
  min-height: 200px;
}
</style>