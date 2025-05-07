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
              :disabled="!activeTab || !activeTab.relatedFiles || activeTab.relatedFiles.length === 0"
            >
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
          
          <!-- 檔案資訊區塊 -->
          <div v-if="activeTab && activeTab.txtContent" class="mt-4 pt-4 border-t border-gray-200">
            <h3 class="text-sm font-medium text-gray-700 mb-3">檔案資訊</h3>
            
            <div class="bg-white rounded-lg border border-gray-200 overflow-y-auto max-h-80">
              <!-- 基本參數 -->
              <div class="p-3">
                <h4 class="font-medium text-sm border-b pb-1 mb-3">基本參數</h4>
                
                <div class="grid grid-cols-1 gap-1.5">
                  <!-- 參數項目 - 每個參數一行 -->
                  <div v-for="(value, key) in parametersToDisplay" :key="key" class="info-row flex">
                    <div class="text-sm font-medium text-gray-700 w-32 flex-shrink-0">{{ key }}:</div>
                    <div class="text-sm text-gray-900 flex-1">{{ value }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
  import type { PropType } from 'vue';
  import type { AnalysisTab } from '../../stores/spmDataStore';
  import type { FileInfo } from '../../stores/spmDataStore';
  
  export default defineComponent({
    name: 'FileSelectorPanel',
    props: {
      activeTab: {
        type: Object as PropType<AnalysisTab | null>,
        default: null
      },
      isLoading: {
        type: Boolean,
        default: false
      }
    },
    emits: ['toggle-selector', 'load-file'],
    setup(props, { emit }) {
      const showFileSelector = ref(true);
      const selectedFileId = ref('');
      
      // 可用檔案
      const availableFiles = computed(() => {
        if (!props.activeTab || !props.activeTab.relatedFiles) {
          return [];
        }
        
        // 過濾出.int檔案
        const intFiles = props.activeTab.relatedFiles.filter(file => 
          file.path.toLowerCase().endsWith('.int')
        );
        
        console.log('可用INT檔案:', intFiles);
        return intFiles;
      });
      
      // 要顯示的參數
      const parametersToDisplay = computed(() => {
        if (!props.activeTab || !props.activeTab.parameters) {
          return {};
        }
        
        const params = { ...props.activeTab.parameters };
        // 排除檔案描述
        delete params.FileDescriptions;
        return params;
      });
      
      // 切換檔案選擇器
      const toggleFileSelector = () => {
        showFileSelector.value = !showFileSelector.value;
        emit('toggle-selector', showFileSelector.value);
      };
      
      // 載入選中檔案
      const loadSelectedFile = () => {
        console.log('FileSelectorPanel - loadSelectedFile:', selectedFileId.value);
        if (!selectedFileId.value || !props.activeTab) return;
        
        console.log('發送load-file事件:', {
          selectedFileId: selectedFileId.value,
          activeTabId: props.activeTab.id
        });
        
        emit('load-file', {
          selectedFileId: selectedFileId.value,
          activeTabId: props.activeTab.id
        });
      };
      
      // 監視標籤頁變更，自動選擇第一個可用檔案
      watch(() => props.activeTab, (newTab) => {
        console.log('標籤頁變更:', newTab?.id);
        
        if (newTab && availableFiles.value.length > 0) {
          selectedFileId.value = availableFiles.value[0].path;
          console.log('自動選擇檔案:', selectedFileId.value);
        } else {
          selectedFileId.value = '';
        }
      }, { immediate: true });
      
      // 監視可用檔案變更，自動選擇第一個可用檔案
      watch(availableFiles, (newFiles) => {
        console.log('可用檔案變更:', newFiles.length);
        
        if (newFiles.length > 0 && !selectedFileId.value) {
          selectedFileId.value = newFiles[0].path;
          console.log('自動選擇檔案:', selectedFileId.value);
        } else if (newFiles.length === 0) {
          selectedFileId.value = '';
        }
      }, { immediate: true });
      
      return {
        showFileSelector,
        selectedFileId,
        availableFiles,
        parametersToDisplay,
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
  
  /* 最大高度限制 */
  .max-h-80 {
    max-height: 20rem;
  }
  
  /* 滾動條樣式 */
  .max-h-80::-webkit-scrollbar {
    width: 6px;
  }
  
  .max-h-80::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }
  
  .max-h-80::-webkit-scrollbar-thumb {
    background: #ddd;
    border-radius: 3px;
  }
  
  .max-h-80::-webkit-scrollbar-thumb:hover {
    background: #ccc;
  }
  </style>