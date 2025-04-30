<!-- App.vue -->
<template>
  <div class="flex flex-col h-screen bg-neutral-50 overflow-hidden">
    <div class="flex flex-1 overflow-hidden">
      <SideBar @menu-item-clicked="handleMenuItemClick" :activeItem="currentView" />
      
      <div class="relative flex flex-1 overflow-hidden">
        <transition name="slide">
          <FileSelector 
            v-if="showFileSelector" 
            @close="hideFileSelector"
            @width-changed="updateFileSelectorWidth"
            :initial-files="spmDataStore.files"
            @file-selected-for-analysis="openFileForAnalysis"
            class="absolute top-0 left-0 z-10 h-full"
          />
        </transition>
        
        <main class="flex-1 p-5 overflow-y-auto bg-neutral-50" 
              :class="{ 'ml-[450px]': showFileSelector }"
              :style="showFileSelector ? { width: `calc(100% - ${fileSelectorWidth}px)` } : {}"
        >
          <div v-if="!spmDataStore.currentView || spmDataStore.currentView === 'welcome'" class="flex flex-col items-center justify-center h-full text-center text-neutral-600">
            <h2 class="mb-4 text-2xl font-semibold">歡迎使用 SPM 數據分析工具</h2>
            <p class="text-base">請從左側功能欄選擇「資料集」以開始</p>
            
            <!-- 如果有上次開啟的資料夾，顯示快速訪問按鈕 -->
            <div v-if="lastDirectory" class="mt-8">
              <p class="mb-3 text-sm text-gray-500">快速訪問上次開啟的資料夾：</p>
              <button 
                @click="openLastDirectory" 
                class="px-4 py-2 bg-secondary-500 hover:bg-secondary-600 text-white font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:ring-offset-2"
              >
                {{ formatDirectoryPath(lastDirectory) }}
              </button>
            </div>
          </div>
          
          <DataView v-else-if="spmDataStore.currentView === 'data-view'" />
          
          <AnalysisView v-else-if="spmDataStore.currentView === 'analysis'" />
        </main>
      </div>
    </div>
    
    <footer class="py-3 text-center text-sm text-neutral-500 border-t border-neutral-200 h-10 bg-white flex-shrink-0">
      © 2025 SPM Data Analysis Tool developed by Odindino
    </footer>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue';
import SideBar from '@/components/SideBar.vue';
import FileSelector from '@/components/FileSelector.vue';
import DataView from '@/components/DataView.vue';
import AnalysisView from '@/components/AnalysisView.vue';
import { useSpmDataStore } from './stores/spmDataStore';
import { useUserPreferencesStore } from './stores/userPreferencesStore';

export default defineComponent({
  name: 'App',
  components: {
    SideBar,
    FileSelector,
    DataView,
    AnalysisView
  },
  setup() {
    const spmDataStore = useSpmDataStore();
    const userPreferencesStore = useUserPreferencesStore();
    
    const showFileSelector = ref(false);
    const fileSelectorWidth = ref(userPreferencesStore.fileSelectorWidth);
    
    const selectedFile = computed(() => spmDataStore.selectedFile);
    const lastDirectory = computed(() => userPreferencesStore.lastDirectory);
    const currentView = computed(() => spmDataStore.currentView);
    
    // 處理側邊欄選單項目點擊
    const handleMenuItemClick = (menuItem: string) => {
      if (menuItem === 'dataset') {
        toggleFileSelector();
      } else if (menuItem === 'analysis') {
        // 切換到分析視圖
        spmDataStore.setCurrentView('analysis');
      }
    };
    
    // 切換檔案選擇器顯示/隱藏
    const toggleFileSelector = () => {
      showFileSelector.value = !showFileSelector.value;
    };
    
    // 隱藏檔案選擇器
    const hideFileSelector = () => {
      showFileSelector.value = false;
    };
    
    // 更新檔案選擇器寬度
    const updateFileSelectorWidth = (width: number) => {
      fileSelectorWidth.value = width;
    };
    
    // 開啟檔案進行分析
    const openFileForAnalysis = async (file: any) => {
      // 檢查檔案內容是否已載入
      let fileContent = spmDataStore.fileContents[file.path];
      
      if (!fileContent) {
        try {
          // 獲取檔案內容
          const result = await window.pywebview.api.get_txt_file_content(file.path);
          if (result.success) {
            fileContent = {
              content: result.content,
              parameters: result.parameters,
              relatedFiles: result.relatedFiles
            };
            spmDataStore.setFileContent(file.path, fileContent);
          } else {
            console.error('無法讀取文件內容:', result.error);
            return;
          }
        } catch (error) {
          console.error('讀取檔案時出錯:', error);
          return;
        }
      }
      
      // 添加到分析標籤頁
      spmDataStore.addAnalysisTab(file, fileContent);
      
      // 隱藏檔案選擇器
      hideFileSelector();
    };
    
    // 格式化目錄路徑顯示（只顯示最後一部分）
    const formatDirectoryPath = (path: string): string => {
      if (!path) return '';
      
      const parts = path.split(/[\/\\]/); // 同時處理 Windows 和 Unix 路徑分隔符
      const lastPart = parts[parts.length - 1];
      
      if (lastPart) {
        return lastPart;
      } else if (parts.length > 1) {
        // 如果路徑以分隔符結尾，則顯示倒數第二部分
        return parts[parts.length - 2];
      }
      
      return path.slice(0, 20) + (path.length > 20 ? '...' : '');
    };
    
    // 開啟上次的資料夾
    const openLastDirectory = async () => {
      if (!lastDirectory.value) return;
      
      try {
        const result = await window.pywebview.api.get_folder_files(lastDirectory.value);
        
        if (result) {
          spmDataStore.setCurrentDirectory(lastDirectory.value);
          spmDataStore.setFiles(result);
          
          // 打開檔案選擇器
          showFileSelector.value = true;
        }
      } catch (error) {
        console.error('Failed to open last directory:', error);
      }
    };
    
    // 當選擇檔案時，自動關閉檔案選擇器
    watch(() => spmDataStore.selectedFile, (newVal) => {
      if (newVal) {
        // 添加短延遲，讓使用者能夠看到選中效果後再關閉選擇器
        setTimeout(() => {
          hideFileSelector();
        }, 300);
      }
    });
    
    return {
      spmDataStore,
      showFileSelector,
      fileSelectorWidth,
      selectedFile,
      lastDirectory,
      currentView,
      handleMenuItemClick,
      hideFileSelector,
      updateFileSelectorWidth,
      formatDirectoryPath,
      openLastDirectory,
      openFileForAnalysis
    };
  }
});
</script>

<style>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}

/* 防止頁面整體捲動 */
html, body {
  overflow: hidden;
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>