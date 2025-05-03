<!-- Nanodrill_GUI/src/components/analysis/ProfileViewer.vue -->
<template>
    <div class="h-full flex flex-col bg-white rounded-lg overflow-hidden border border-gray-200 relative"
         :class="{ 'ring-2 ring-primary': isActive }">
      <!-- 標題欄 -->
      <div class="bg-gray-50 px-3 py-2 border-b border-gray-200 flex items-center justify-between">
        <h3 class="font-medium text-sm truncate flex-grow">{{ title || 'Line Profile' }}</h3>
        
        <!-- 控制按鈕 -->
        <div class="flex space-x-1">
          <button v-if="!hideControls" title="調整設置"
                  class="p-1 rounded hover:bg-gray-200 text-gray-600 text-sm"
                  @click="toggleSettings">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
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
      
      <!-- 主要剖面圖顯示區域 -->
      <div class="flex-grow overflow-hidden relative" @click="$emit('profile-clicked')">
        <!-- 剖面圖載入中顯示 -->
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-gray-50">
          <div class="flex flex-col items-center">
            <div class="w-8 h-8 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-2"></div>
            <span class="text-sm text-gray-600">載入中...</span>
          </div>
        </div>
        
        <!-- 實際剖面圖 -->
        <div v-else class="h-full w-full relative">
          <img v-if="profileImage" 
               :src="'data:image/png;base64,' + profileImage" 
               alt="線性剖面" 
               class="h-full max-h-full max-w-full object-contain mx-auto" />
          
          <!-- 無剖面圖顯示 -->
          <div v-else class="absolute inset-0 flex items-center justify-center bg-gray-50">
            <div class="text-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span class="text-sm text-gray-500">尚未生成剖面圖</span>
            </div>
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
            >
            <label for="show-peaks" class="ml-2 text-sm text-gray-700">
              顯示峰值
            </label>
          </div>
          
          <!-- 峰值檢測敏感度 -->
          <div v-if="showPeaks">
            <div class="flex justify-between mb-1">
              <label class="text-xs text-gray-600">峰值敏感度</label>
              <span class="text-xs text-gray-600">{{ peakSensitivity.toFixed(1) }}</span>
            </div>
            <input 
              type="range" 
              v-model="peakSensitivity" 
              min="0.1" 
              max="5" 
              step="0.1" 
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            >
          </div>
        </div>
      </div>
      
      <!-- 統計信息面板 -->
      <div v-if="showStats && roughness" class="border-t border-gray-200 p-2 bg-gray-50 text-xs">
        <div class="flex flex-wrap justify-between text-gray-600">
          <span>Ra: {{ formatNumber(roughness.Ra) }} {{ physUnit }}</span>
          <span>Rq: {{ formatNumber(roughness.Rq) }} {{ physUnit }}</span>
          <span>Rz: {{ formatNumber(roughness.Rz) }} {{ physUnit }}</span>
          <span>長度: {{ formatNumber(profileLength) }} {{ physUnit }}</span>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, computed, watch, PropType } from 'vue';
  
  // 定義粗糙度介面
  interface Roughness {
    Ra: number;
    Rq: number;
    Rz: number;
    Rsk: number;
    Rku: number;
  }
  
  export default defineComponent({
    name: 'ProfileViewer',
    props: {
      profileImage: {
        type: String,
        default: ''
      },
      profileData: {
        type: Object as PropType<{distance: number[], height: number[], length: number, stats: any}>,
        default: () => ({distance: [], height: [], length: 0, stats: {}})
      },
      roughness: {
        type: Object as PropType<Roughness>,
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
    emits: [
      'update:shiftZero', 
      'update:autoScale', 
      'update:showPeaks', 
      'update:peakSensitivity', 
      'profile-clicked', 
      'refresh', 
      'close'
    ],
    setup(props, { emit }) {
      // 本地狀態
      const showSettings = ref(false);
      const shiftZero = ref(props.initialShiftZero);
      const autoScale = ref(props.initialAutoScale);
      const showPeaks = ref(props.initialShowPeaks);
      const peakSensitivity = ref(1.0);
      
      // 計算剖面長度
      const profileLength = computed(() => {
        return props.profileData?.length || 0;
      });
      
      // 格式化數字，保留兩位小數
      const formatNumber = (value: number) => {
        if (value === undefined || value === null) return 'N/A';
        return value.toFixed(2);
      };
      
      // 切換設置面板顯示
      const toggleSettings = () => {
        showSettings.value = !showSettings.value;
      };
      
      // 保存圖像
      const saveImage = () => {
        if (!props.profileImage) return;
        
        const downloadLink = document.createElement('a');
        downloadLink.href = 'data:image/png;base64,' + props.profileImage;
        downloadLink.download = `${props.title || 'profile'}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
      };
      
      // 監視設置變化
      watch(shiftZero, (newVal) => {
        emit('update:shiftZero', newVal);
        emit('refresh');
      });
      
      watch(autoScale, (newVal) => {
        emit('update:autoScale', newVal);
        emit('refresh');
      });
      
      watch(showPeaks, (newVal) => {
        emit('update:showPeaks', newVal);
        emit('refresh');
      });
      
      watch(peakSensitivity, (newVal) => {
        emit('update:peakSensitivity', newVal);
        emit('refresh');
      });
      
      return {
        showSettings,
        shiftZero,
        autoScale,
        showPeaks,
        peakSensitivity,
        profileLength,
        formatNumber,
        toggleSettings,
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