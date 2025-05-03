<!-- Nanodrill_GUI/src/components/analysis/AnalysisTabs.vue -->
<template>
    <div class="flex flex-col h-full">
      <!-- 標籤列 -->
      <div class="flex px-4 pt-2 border-b border-gray-200 bg-gray-50 overflow-x-auto">
        <div v-for="tab in tabs" 
             :key="tab.id" 
             class="flex flex-shrink-0"
             :class="{'mr-1': true}">
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
              draggable="true"
              @dragstart="handleDragStart($event, tab)"
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
      </div>
      
      <!-- 標籤內容 -->
      <div class="flex-grow overflow-hidden"
           @dragover.prevent="onDragOver"
           @drop.prevent="onDrop"
           @dragleave.prevent="onDragLeave">
        <div v-if="currentTabPanel" class="h-full">
          <component :is="currentTabPanel.component" v-bind="currentTabPanel.props" />
        </div>
        
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
  import { defineComponent, ref, computed } from 'vue';
  import type { PropType } from 'vue';
  import AnalysisPanel from './AnalysisPanel.vue';
  
  // 定義標籤頁
  interface Tab {
    id: string;
    title: string;
    component: string;
    props: Record<string, any>;
  }
  
  export default defineComponent({
    name: 'AnalysisTabs',
    components: {
      AnalysisPanel
    },
    props: {
      tabs: {
        type: Array as PropType<Tab[]>,
        default: () => []
      },
      activeTabId: {
        type: String,
        default: ''
      }
    },
    emits: ['tab-switched', 'tab-closed', 'tab-drop-to-panel'],
    setup(props, { emit }) {
      // 拖拽相關狀態
      const isDragOver = ref(false);
      
      // 計算當前標籤頁面板
      const currentTabPanel = computed(() => {
        if (!props.activeTabId) return null;
        return props.tabs.find(tab => tab.id === props.activeTabId);
      });
      
      // 切換標籤
      const switchTab = (tabId: string) => {
        emit('tab-switched', tabId);
      };
      
      // 關閉標籤
      const closeTab = (tabId: string) => {
        emit('tab-closed', tabId);
      };
      
      // 處理拖拽開始
      const handleDragStart = (event: DragEvent, tab: Tab) => {
        // 設置拖拽數據
        event.dataTransfer?.setData('application/json', JSON.stringify({
          type: 'tab',
          tabId: tab.id
        }));
        
        // 設置拖拽效果
        event.dataTransfer!.effectAllowed = 'move';
        
        // 設置拖拽圖像
        const dragIcon = document.createElement('div');
        dragIcon.textContent = tab.title;
        dragIcon.className = 'px-3 py-1 bg-white shadow border border-gray-200 rounded text-sm';
        dragIcon.style.position = 'absolute';
        dragIcon.style.top = '-1000px';
        document.body.appendChild(dragIcon);
        event.dataTransfer?.setDragImage(dragIcon, 0, 0);
        
        // 延遲移除拖拽圖像元素
        setTimeout(() => {
          document.body.removeChild(dragIcon);
        }, 0);
      };
      
      // 拖拽相關事件處理
      const onDragOver = (event: DragEvent) => {
        isDragOver.value = true;
      };
      
      const onDragLeave = (event: DragEvent) => {
        isDragOver.value = false;
      };
      
      const onDrop = (event: DragEvent) => {
        isDragOver.value = false;
        
        // 獲取拖拽數據
        const data = event.dataTransfer?.getData('application/json');
        if (!data) return;
        
        try {
          const dropData = JSON.parse(data);
          
          // 處理從面板拖回標籤欄的情況
          if (dropData.type === 'container' || dropData.type === 'viewer') {
            emit('tab-drop-to-panel', dropData);
          }
        } catch (error) {
          console.error('無法解析拖拽數據:', error);
        }
      };
      
      return {
        currentTabPanel,
        switchTab,
        closeTab,
        handleDragStart,
        onDragOver,
        onDragLeave,
        onDrop
      };
    }
  });
  </script>
  
  <style scoped>
  /* 自定義滾動條 */
  .overflow-x-auto {
    scrollbar-width: thin;
    scrollbar-color: #ddd #f1f1f1;
  }
  
  .overflow-x-auto::-webkit-scrollbar {
    height: 6px;
  }
  
  .overflow-x-auto::-webkit-scrollbar-track {
    background: #f1f1f1;
  }
  
  .overflow-x-auto::-webkit-scrollbar-thumb {
    background: #ddd;
    border-radius: 3px;
  }
  
  .overflow-x-auto::-webkit-scrollbar-thumb:hover {
    background: #ccc;
  }
  </style>