<!-- src/components/analysis/AnalysisTabs.vue -->
<template>
  <div class="flex flex-col h-full">
    <!-- 標籤列 -->
    <div class="flex px-4 pt-2 border-b border-gray-200 bg-gray-50 overflow-x-auto">
      <div v-for="tab in tabs" 
           :key="tab.id" 
           class="flex flex-shrink-0 mr-1">
        <div class="flex group relative">
          <!-- 標籤本身 -->
          <button 
            @click="switchTab(tab.id)" 
            :class="[
              'flex items-center px-4 py-2 text-sm rounded-t-md focus:outline-none transition-colors',
              activeTabId === tab.id 
                ? 'bg-white text-primary font-medium border border-gray-200 border-b-white' 
                : 'text-gray-600 hover:bg-gray-100'
            ]"
          >
            <span class="truncate max-w-xs">{{ tab.title }}</span>
            
            <!-- 關閉按鈕 -->
            <button 
              @click.stop="closeTab(tab.id)" 
              class="ml-2 p-0.5 rounded-full hover:bg-gray-200 text-gray-400 hover:text-gray-600 focus:outline-none"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </button>
        </div>
      </div>
      
      <!-- 添加標籤按鈕 -->
      <button 
        @click="addNewTab"
        class="flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-t-md focus:outline-none"
        title="添加新標籤頁"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
      </button>
    </div>
    
    <!-- 標籤頁內容區域 -->
    <div class="flex-grow overflow-auto">
      <!-- 活動標籤頁內容 -->
      <div v-if="activeTab" class="p-4">
        <!-- 如果有視圖群組，則顯示 ViewerContainer -->
        <div v-if="activeTab.viewerGroups && activeTab.viewerGroups.length > 0">
          <!-- 只使用第一個視圖群組 (方案二) -->
          <ViewerContainer
            :id="activeTab.viewerGroups[0].id"
            :title="activeTab.viewerGroups[0].title"
            :viewers="activeTab.viewerGroups[0].viewers"
            :is-active="true"
            @activate="activateGroup"
            @viewer-removed="handleViewerRemoved"
          />
        </div>
        
        <!-- 無內容提示 -->
        <div v-else class="h-full flex items-center justify-center bg-gray-50">
          <div class="text-center p-8">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-gray-500 mb-2">此標籤頁尚無內容</p>
            <p class="text-sm text-gray-400">請從檔案選擇器中選擇檔案進行分析</p>
          </div>
        </div>
      </div>
      
      <!-- 無標籤頁提示 -->
      <div v-else class="h-full flex items-center justify-center bg-gray-50">
        <div class="text-center p-8">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-gray-500 mb-2">尚未開啟任何分析標籤頁</p>
          <p class="text-sm text-gray-400">請在檔案選擇器中選擇檔案開始分析</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';
import { useSpmDataStore } from '../../stores/spmDataStore';
import { useAnalysisStore } from '../../stores/analysisStore';
import ViewerContainer from './ViewerContainer.vue';

export default defineComponent({
  name: 'AnalysisTabs',
  components: {
    ViewerContainer
  },
  setup() {
    const spmDataStore = useSpmDataStore();
    const analysisStore = useAnalysisStore();
    
    // 從 store 獲取狀態
    const tabs = computed(() => spmDataStore.analysisTabs);
    const activeTabId = computed(() => spmDataStore.activeAnalysisTabId);
    const activeTab = computed(() => tabs.value.find(tab => tab.id === activeTabId.value));
    
    // 切換標籤頁
    const switchTab = (tabId: string) => {
      spmDataStore.setActiveAnalysisTab(tabId);
      analysisStore.setActiveTab(tabId);
    };
    
    // 關閉標籤頁
    const closeTab = (tabId: string) => {
      spmDataStore.removeAnalysisTab(tabId);
    };
    
    // 添加新標籤頁
    const addNewTab = () => {
      const newTabId = `tab-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
      const newGroupId = `group-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
      
      spmDataStore.addNewTab({
        id: newTabId,
        title: '新標籤頁',
        fileId: '',
        fileType: 'topo',
        sourcePath: '',
        colormap: 'Oranges',
        zScale: 1.0,
        viewerGroups: [{
          id: newGroupId,
          title: '數據視圖',
          viewers: [], // 初始為空
          layout: 'horizontal'
        }]
      });
      
      spmDataStore.setActiveAnalysisTab(newTabId);
      analysisStore.setActiveTab(newTabId);
      analysisStore.setActiveGroup(newGroupId);
    };
    
    // 激活群組
    const activateGroup = (groupId: string) => {
      analysisStore.setActiveGroup(groupId);
    };
    
    // 處理視圖移除
    const handleViewerRemoved = (data: { groupId: string, viewerIndex: number, viewerId: string }) => {
      console.log("移除視圖:", data.viewerId);
      analysisStore.removeViewer(data.viewerId);
    };
    
    return {
      tabs,
      activeTabId,
      activeTab,
      switchTab,
      closeTab,
      addNewTab,
      activateGroup,
      handleViewerRemoved
    };
  }
});
</script>