<!-- src/components/analysis/FileSelectorPanel.vue -->
<template>
  <div 
    class="sidebar-panel bg-white border-r border-gray-200 transition-all duration-300 flex flex-col"
    :class="showFileSelector ? 'w-80' : 'w-12'"
  >
    <!-- 標題或迷你按鈕 -->
    <div 
      class="flex items-center p-2 border-b border-gray-200 bg-gray-50"
      :class="showFileSelector ? 'justify-between' : 'justify-center'"
    >
      <h3 v-if="showFileSelector" class="text-sm font-medium text-gray-700 truncate">檔案選擇</h3>
      <button 
        @click="toggleFileSelector"
        class="p-1.5 rounded hover:bg-gray-200 text-gray-600 focus:outline-none"
        :title="showFileSelector ? '收起檔案選擇器' : '展開檔案選擇器'"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-5 w-5" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
          :class="{ 'transform rotate-180': showFileSelector }"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
    </div>
    
    <!-- 檔案選擇器內容 -->
    <div v-if="showFileSelector" class="flex-grow overflow-y-auto p-4">
      <div v-if="activeTab">
        <h3 class="text-sm font-medium text-gray-700 mb-2">選擇分析檔案</h3>
        
        <div class="mb-4">
          <label class="text-xs text-gray-500 block mb-1">檔案選擇</label>
          <select 
            v-model="selectedFileId" 
            class="w-full text-sm border border-gray-300 rounded py-1.5 px-2 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
            :disabled="!availableFiles || availableFiles.length === 0 || isLoading"
          >
            <option value="">請選擇檔案</option>
            <option v-for="file in availableFiles" :key="file.path" :value="file.path">
              {{ file.name }}
            </option>
          </select>
          <p v-if="!availableFiles || availableFiles.length === 0" class="text-xs text-gray-500 mt-1">
            沒有可用的相關檔案
          </p>
        </div>
        
        <button 
          @click="loadSelectedFile" 
          class="w-full py-2 px-4 bg-primary text-white font-medium rounded transition-colors hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!selectedFileId || isLoading"
        >
          <span v-if="isLoading">載入中...</span>
          <span v-else>載入檔案</span>
        </button>
      </div>
      <div v-else class="text-center text-gray-500 text-sm pt-4">
        請先選擇一個分析標籤頁
      </div>
    </div>
    
    <!-- 迷你模式下只顯示圖標 -->
    <div v-else class="flex-grow flex flex-col items-center pt-3">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue';
import { useSpmDataStore } from '../../stores/spmDataStore';
import { useAnalysisStore } from '../../stores/analysisStore';

export default defineComponent({
  name: 'FileSelectorPanel',
  setup() {
    const spmDataStore = useSpmDataStore();
    const analysisStore = useAnalysisStore();
    
    const showFileSelector = ref(true);
    const selectedFileId = ref('');
    
    // 從 store 獲取狀態
    const isLoading = computed(() => analysisStore.isLoading);
    const activeTabId = computed(() => spmDataStore.activeAnalysisTabId);
    const activeTab = computed(() => 
      spmDataStore.analysisTabs.find(tab => tab.id === activeTabId.value)
    );
    
    // 可用檔案
    const availableFiles = computed(() => {
      if (!activeTab.value || !activeTab.value.relatedFiles) {
        return [];
      }
      
      // 過濾出.int檔案
      return activeTab.value.relatedFiles.filter(file => 
        file.path.toLowerCase().endsWith('.int')
      );
    });
    
    // 切換檔案選擇器
    const toggleFileSelector = () => {
      showFileSelector.value = !showFileSelector.value;
    };
    
    // 載入選中檔案
    const loadSelectedFile = () => {
      if (!selectedFileId.value || !activeTabId.value) return;
      
      // 設置分析 store 中的活動標籤頁
      analysisStore.activeTabId = activeTabId.value;
      
      // 選擇文件
      analysisStore.selectFile(selectedFileId.value, getFileName(selectedFileId.value));
      
      // 載入文件
      analysisStore.loadSelectedFile();
    };
    
    // 獲取檔案名稱
    const getFileName = (path: string): string => {
      if (!path) return '';
      
      // 提取檔案名
      const parts = path.split(/[\/\\]/);
      return parts[parts.length - 1] || '';
    };
    
    // 監視標籤頁變更，自動選擇第一個可用檔案
    watch(() => activeTab.value, () => {
      if (activeTab.value && availableFiles.value.length > 0) {
        selectedFileId.value = availableFiles.value[0].path;
      } else {
        selectedFileId.value = '';
      }
    }, { immediate: true });
    
    return {
      showFileSelector,
      selectedFileId,
      isLoading,
      activeTab,
      availableFiles,
      toggleFileSelector,
      loadSelectedFile
    };
  }
});
</script>

<style scoped>
/* 側邊面板高度設置 */
.sidebar-panel {
  max-height: calc(50vh - 30px);
  min-height: 200px;
}
</style>