<!-- src/components/analysis/ProfileViewer.vue -->
<template>
  <div class="profile-viewer h-full flex flex-col bg-white rounded-lg overflow-hidden"
       :class="{ 'ring-2 ring-primary': isActive }"
       @click="handleClick">
    <!-- 控制欄 -->
    <div class="flex items-center justify-between px-3 py-1.5 bg-gray-50 border-b border-gray-200">
      <h3 class="text-sm font-medium text-gray-700 truncate">{{ title || 'Profile Viewer' }}</h3>
      
      <div class="flex space-x-1">
        <!-- 設定按鈕 -->
        <button 
          v-if="!hideControls" 
          @click.stop="toggleSettings"
          class="p-1 rounded hover:bg-gray-200 text-gray-600 focus:outline-none"
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
          class="p-1 rounded hover:bg-gray-200 text-gray-600 focus:outline-none"
          title="關閉"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
    
    <!-- 主要剖面圖顯示區域 -->
    <div class="flex-grow overflow-hidden relative" ref="profileContainer">
      <!-- 載入中顯示 -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-gray-50">
        <div class="flex flex-col items-center">
          <div class="w-8 h-8 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-2"></div>
          <span class="text-sm text-gray-600">載入中...</span>
        </div>
      </div>
      
      <!-- 實際剖面圖 -->
      <div v-else-if="profileImage" class="h-full w-full flex items-center justify-center p-2">
        <img 
          :src="'data:image/png;base64,' + profileImage" 
          :alt="title" 
          class="max-h-full max-w-full object-contain" />
      </div>
      
      <!-- 無數據提示 -->
      <div v-else class="absolute inset-0 flex items-center justify-center bg-gray-50">
        <div class="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span class="text-sm text-gray-500">尚未生成剖面圖</span>
        </div>
      </div>
    </div>
    
    <!-- 設置面板 -->
    <div v-if="showSettings" class="border-t border-gray-200 p-3 bg-gray-50">
      <div class="space-y-3">
        <!-- 將最小值歸零選項 -->
        <div class="flex items-center">
          <input 
            type="checkbox" 
            id="shift-zero" 
            v-model="shiftZero"
            class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            @change="updateProfileAndEmit"
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
            v-model="autoScale"
            class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            @change="updateProfileAndEmit"
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
            v-model="showPeaks"
            class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            @change="updateProfileAndEmit"
          >
          <label for="show-peaks" class="ml-2 text-sm text-gray-700">
            顯示峰值
          </label>
        </div>
        
        <!-- 峰值敏感度 -->
        <div v-if="showPeaks">
          <div class="flex justify-between mb-1">
            <label class="text-xs text-gray-500">峰值敏感度</label>
            <span class="text-xs text-gray-500">{{ peakSensitivity.toFixed(1) }}</span>
          </div>
          <input 
            type="range" 
            v-model="peakSensitivity" 
            min="0.1" 
            max="5" 
            step="0.1" 
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            @change="updateProfileAndEmit"
          >
        </div>
      </div>
    </div>
    
    <!-- 統計信息面板 -->
    <div v-if="showStats && roughness" class="py-1 px-3 bg-gray-50 border-t border-gray-200 text-xs">
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
import { defineComponent, ref, computed} from 'vue';
import type { PropType } from 'vue';

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
    profileImage: {
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
    
    // 更新剖面圖及發送設置變更事件
    const updateProfileAndEmit = () => {
      const settings = {
        shiftZero: shiftZero.value,
        autoScale: autoScale.value,
        showPeaks: showPeaks.value,
        peakSensitivity: peakSensitivity.value
      };
      
      emit('update:settings', settings);
      emit('refresh');
    };
    
    return {
      showSettings,
      shiftZero,
      autoScale,
      showPeaks,
      peakSensitivity,
      profileLength,
      formatNumber,
      handleClick,
      toggleSettings,
      updateProfileAndEmit
    };
  }
});
</script>

<style scoped>
/* 自定義樣式 */
.profile-viewer.active {
  outline: 2px solid rgba(59, 130, 246, 0.5);
  outline-offset: -2px;
}

/* 自定義範圍輸入滑塊 */
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