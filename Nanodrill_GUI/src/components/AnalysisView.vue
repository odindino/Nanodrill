<!-- src/components/AnalysisView.vue -->
<template>
  <div class="h-full flex flex-col bg-white rounded-lg shadow overflow-hidden relative">
    <!-- 沒有標籤頁時的歡迎畫面 -->
    <div v-if="analysisTabs.length === 0" class="flex flex-col items-center justify-center h-full p-6 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <p class="text-gray-500 mb-4">尚未開啟任何分析標籤頁</p>
      <p class="text-gray-500 text-sm">請在檔案選擇器中雙擊檔案或使用"分析"按鈕開始進行分析</p>
    </div>

    <!-- 有標籤頁時的分析介面 -->
    <div v-else class="h-full flex relative">
      <!-- 左側面板區域 -->
      <div class="h-full flex flex-col">
        <!-- 檔案選擇器面板 -->
        <FileSelectorPanel />
        
        <!-- 工具列面板 -->
        <ToolsPanel />
      </div>
      
      <!-- 主要分析標籤頁區域 -->
      <div class="flex-1 h-full">
        <AnalysisTabs />
      </div>

      <!-- 載入中顯示 -->
      <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20 z-50">
        <div class="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
          <div class="w-12 h-12 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-4"></div>
          <p class="text-gray-600">正在載入資料...</p>
        </div>
      </div>

      <!-- 錯誤提示 -->
      <div v-if="errorMessage" 
           class="absolute top-4 right-4 max-w-md p-4 bg-red-50 border-l-4 border-red-400 text-red-700 z-50 rounded shadow-md">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm">{{ errorMessage }}</p>
          </div>
          <div class="ml-auto pl-3">
            <button @click="clearError" class="text-red-400 hover:text-red-500 focus:outline-none">
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';
import { useSpmDataStore } from '../stores/spmDataStore';
import { useAnalysisStore } from '../stores/analysisStore';
import FileSelectorPanel from './analysis/FileSelectorPanel.vue';
import ToolsPanel from './analysis/ToolsPanel.vue';
import AnalysisTabs from './analysis/AnalysisTabs.vue';

export default defineComponent({
  name: 'AnalysisView',
  components: {
    FileSelectorPanel,
    ToolsPanel,
    AnalysisTabs
  },
  setup() {
    const spmDataStore = useSpmDataStore();
    const analysisStore = useAnalysisStore();
    
    // 從 store 獲取狀態
    const analysisTabs = computed(() => spmDataStore.analysisTabs);
    const isLoading = computed(() => analysisStore.isLoading);
    const errorMessage = computed(() => analysisStore.errorMessage);
    
    // 清除錯誤消息
    const clearError = () => {
      analysisStore.clearError();
    };
    
    return {
      analysisTabs,
      isLoading,
      errorMessage,
      clearError
    };
  }
});
</script>