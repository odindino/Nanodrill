<!-- src/components/analysis/AnalysisTabs.vue -->
<template>
  <div class="flex flex-col h-full">
    <!-- 標籤列 -->
    <div 
      class="flex px-4 pt-2 border-b border-gray-200 bg-gray-50 overflow-x-auto"
      ref="tabsContainer"
    >
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
            
            <!-- 顯示拖曳複本的圖標 -->
            <div v-if="draggingTabId === tab.id" class="absolute -top-2 -right-2 w-4 h-4 bg-blue-500 rounded-full"></div>
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
    <div 
      class="flex-grow overflow-hidden"
      @dragover.prevent="handleDragOver"
      @drop.prevent="handleDrop"
      @dragleave.prevent="handleDragLeave"
    >
      <!-- 活動標籤頁內容 -->
      <div v-if="activeTab" class="h-full flex flex-col">
        <AnalysisPanel 
          :viewer-groups="activeTab.viewerGroups"
          :active-group-id="activeGroupId"
          @group-updated="updateViewerGroup"
          @group-removed="removeViewerGroup"
          @viewer-removed="handleViewerRemoved"
          @active-group-changed="setActiveGroup"
          @active-viewer-changed="handleViewerActivated"
          @convert-group-to-tab="convertGroupToTab"
          @drop="handlePanelDrop"
          @create-line-profile="handleCreateLineProfile"
        />
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
      
      <!-- 拖放提示區域 -->
      <div 
        v-if="isDragOver" 
        class="absolute inset-0 z-10 bg-blue-100 bg-opacity-50 border-2 border-dashed border-blue-400 flex items-center justify-center"
      >
        <p class="text-blue-600 font-medium">拖放到此處轉換為標籤頁</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import type { PropType } from 'vue';
import AnalysisPanel from './AnalysisPanel.vue';
import type { Viewer } from './ViewerGroup.vue';

// 視圖群組接口
interface ViewerGroup {
  id: string;
  title: string;
  viewers: Viewer[];
  layout: 'horizontal' | 'vertical';
  height?: number;
}

// 標籤頁接口
interface Tab {
  id: string;
  title: string;
  viewerGroups: ViewerGroup[];
  activeGroupId?: string;
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
  emits: [
    'tab-switched', 
    'tab-closed', 
    'tab-added',
    'tab-updated',
    'group-to-tab',
    'create-line-profile',
    'viewer-activated'
  ],
  setup(props, { emit }) {
    // DOM引用
    const tabsContainer = ref<HTMLElement | null>(null);
    
    // 拖曳相關狀態
    const isDragOver = ref(false);
    const draggingTabId = ref<string | null>(null);
    
    // 活動群組ID
    const activeGroupId = ref<string>('');
    
    // 當前活動的標籤頁
    const activeTab = computed(() => {
      return props.tabs.find(tab => tab.id === props.activeTabId);
    });
    
    // 切換標籤頁
    const switchTab = (tabId: string) => {
      emit('tab-switched', tabId);
    };
    
    // 關閉標籤頁
    const closeTab = (tabId: string) => {
      emit('tab-closed', tabId);
    };
    
    // 添加新標籤頁
    const addNewTab = () => {
      const newTabId = `tab-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
      emit('tab-added', {
        id: newTabId,
        title: '新標籤頁',
        viewerGroups: []
      });
    };
    
    // 更新視圖群組
    const updateViewerGroup = ({ id, changes }: { id: string, changes: Partial<ViewerGroup> }) => {
      if (!activeTab.value) return;
      
      const updatedViewerGroups = activeTab.value.viewerGroups.map(group => {
        if (group.id === id) {
          return { ...group, ...changes };
        }
        return group;
      });
      
      emit('tab-updated', {
        id: activeTab.value.id,
        changes: { viewerGroups: updatedViewerGroups }
      });
    };
    
    // 移除視圖群組
    const removeViewerGroup = (groupId: string) => {
      if (!activeTab.value) return;
      
      const updatedViewerGroups = activeTab.value.viewerGroups.filter(group => group.id !== groupId);
      
      emit('tab-updated', {
        id: activeTab.value.id,
        changes: { viewerGroups: updatedViewerGroups }
      });
      
      // 如果移除的是當前活動群組，需要更新活動群組ID
      if (activeGroupId.value === groupId) {
        activeGroupId.value = updatedViewerGroups.length > 0 ? updatedViewerGroups[0].id : '';
      }
    };
    
    // 處理視圖移除
    const handleViewerRemoved = ({ groupId, viewerIndex, viewerId }: any) => {
      if (!activeTab.value) return;
      
      const groupIndex = activeTab.value.viewerGroups.findIndex(group => group.id === groupId);
      if (groupIndex === -1) return;
      
      const group = activeTab.value.viewerGroups[groupIndex];
      
      // 如果群組只有一個視圖，移除整個群組
      if (group.viewers.length <= 1) {
        removeViewerGroup(groupId);
        return;
      }
      
      // 否則只移除視圖
      const updatedViewers = [...group.viewers];
      updatedViewers.splice(viewerIndex, 1);
      
      updateViewerGroup({
        id: groupId,
        changes: { viewers: updatedViewers }
      });
    };
    
    // 設置活動群組
    const setActiveGroup = (groupId: string) => {
      activeGroupId.value = groupId;
      
      // 更新標籤頁的活動群組
      if (activeTab.value) {
        emit('tab-updated', {
          id: activeTab.value.id,
          changes: { activeGroupId: groupId }
        });
      }
    };
    
    // 處理視圖激活
    const handleViewerActivated = (data: any) => {
      // 更新本地狀態
      console.log('分析標籤頁收到視圖激活事件:', data);
      
      // 将事件傳遞給父組件
      emit('viewer-activated', data);
      
      // 處理本地視圖狀態更新
      if (!activeTab.value) return;
      
      const updatedGroups = [...activeTab.value.viewerGroups];
      const groupIndex = updatedGroups.findIndex(g => g.id === data.groupId);
      
      if (groupIndex !== -1) {
        // 更新這個群組的所有視圖的活動狀態
        updatedGroups[groupIndex] = {
          ...updatedGroups[groupIndex],
          viewers: updatedGroups[groupIndex].viewers.map((viewer, idx) => {
            const isActive = idx === data.viewerIndex;
            return {
              ...viewer,
              props: {
                ...viewer.props,
                isActive
              }
            };
          })
        };
        
        // 更新其他群組的視圖活動狀態為false
        for (let i = 0; i < updatedGroups.length; i++) {
          if (i !== groupIndex) {
            updatedGroups[i] = {
              ...updatedGroups[i],
              viewers: updatedGroups[i].viewers.map(viewer => ({
                ...viewer,
                props: {
                  ...viewer.props,
                  isActive: false
                }
              }))
            };
          }
        }
        
        // 更新標籤頁
        emit('tab-updated', {
          id: activeTab.value.id,
          changes: { viewerGroups: updatedGroups }
        });
      }
    };
    
    // 將群組轉換為標籤頁
    const convertGroupToTab = (groupId: string) => {
      if (!activeTab.value) return;
      
      const groupIndex = activeTab.value.viewerGroups.findIndex(group => group.id === groupId);
      if (groupIndex === -1) return;
      
      const group = activeTab.value.viewerGroups[groupIndex];
      
      // 創建新標籤頁
      const newTabId = `tab-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
      const newTab: Tab = {
        id: newTabId,
        title: group.title,
        viewerGroups: [{ ...group }]
      };
      
      // 從當前標籤頁移除該群組
      const updatedViewerGroups = [...activeTab.value.viewerGroups];
      updatedViewerGroups.splice(groupIndex, 1);
      
      // 更新當前標籤頁
      emit('tab-updated', {
        id: activeTab.value.id,
        changes: { viewerGroups: updatedViewerGroups }
      });
      
      // 添加新標籤頁
      emit('tab-added', newTab);
      
      // 切換到新標籤頁
      emit('tab-switched', newTabId);
    };
    
    // 處理拖動開始
    const handleDragStart = (event: DragEvent, tab: Tab) => {
      if (!event.dataTransfer) return;
      
      // 設置拖曳數據
      const dragData = {
        type: 'tab',
        tabId: tab.id
      };
      
      event.dataTransfer.setData('application/json', JSON.stringify(dragData));
      event.dataTransfer.effectAllowed = 'move';
      
      // 設置拖曳圖像
      const ghostElement = document.createElement('div');
      ghostElement.className = 'absolute top-0 left-0 bg-white shadow-lg rounded p-2 opacity-70 pointer-events-none';
      ghostElement.textContent = tab.title;
      ghostElement.style.zIndex = '9999';
      document.body.appendChild(ghostElement);
      
      event.dataTransfer.setDragImage(ghostElement, 10, 10);
      
      // 標記正在拖曳的標籤頁
      draggingTabId.value = tab.id;
      
      // 延遲移除拖曳圖像
      setTimeout(() => {
        document.body.removeChild(ghostElement);
      }, 100);
    };
    
    // 處理拖動經過
    const handleDragOver = (event: DragEvent) => {
      if (!event.dataTransfer) return;
      
      // 檢查拖曳數據類型
      let isValidDrop = false;
      
      try {
        const data = event.dataTransfer.getData('application/json');
        if (data) {
          const parsedData = JSON.parse(data);
          if (parsedData.type === 'group' || parsedData.type === 'viewer') {
            isValidDrop = true;
          }
        }
      } catch (e) {
        // 無法讀取數據，可能是因為正在拖曳中
        // 檢查一下有沒有設置什麼類型
        isValidDrop = event.dataTransfer.types.includes('application/json');
      }
      
      if (isValidDrop) {
        isDragOver.value = true;
      }
    };
    
    // 處理拖動離開
    const handleDragLeave = (event: DragEvent) => {
      isDragOver.value = false;
    };
    
    // 處理拖放
    const handleDrop = (event: DragEvent) => {
      isDragOver.value = false;
      
      if (!event.dataTransfer) return;
      
      // 獲取拖放數據
      const data = event.dataTransfer.getData('application/json');
      if (!data) return;
      
      try {
        const dropData = JSON.parse(data);
        
        // 處理群組到標籤頁的轉換
        if (dropData.type === 'group') {
          emit('group-to-tab', dropData);
        }
      } catch (error) {
        console.error('無法解析拖放數據:', error);
      }
    };
    
    // 處理面板拖放
    const handlePanelDrop = ({ dropData, event }: any) => {
      // 處理標籤頁到群組的轉換
      if (dropData.type === 'tab') {
        // 尋找該標籤頁
        const tabIndex = props.tabs.findIndex(tab => tab.id === dropData.tabId);
        if (tabIndex === -1) return;
        
        const tab = props.tabs[tabIndex];
        
        // 如果標籤頁沒有群組，不進行任何操作
        if (!tab.viewerGroups || tab.viewerGroups.length === 0) return;
        
        // 將標籤頁的群組添加到當前標籤頁
        if (activeTab.value) {
          const updatedGroups = [
            ...activeTab.value.viewerGroups,
            ...tab.viewerGroups
          ];
          
          emit('tab-updated', {
            id: activeTab.value.id,
            changes: { viewerGroups: updatedGroups }
          });
          
          // 如果是從其他標籤頁拖曳過來的，可能需要清空原標籤頁的群組
          // 但這可能導致空標籤頁，需要根據實際需求考慮
        }
      }
    };
    
    // 處理創建線性剖面
    const handleCreateLineProfile = (data: any) => {
      emit('create-line-profile', data);
    };
    
    // 生命週期鉤子
    onMounted(() => {
      // 如果標籤頁有活動群組，同步狀態
      if (activeTab.value && activeTab.value.activeGroupId) {
        activeGroupId.value = activeTab.value.activeGroupId;
      } else if (activeTab.value && activeTab.value.viewerGroups.length > 0) {
        // 否則，如果有群組，設置第一個為活動群組
        activeGroupId.value = activeTab.value.viewerGroups[0].id;
      }
    });
    
    // 監聽活動標籤頁變化
    watch(() => props.activeTabId, (newTabId) => {
      if (newTabId) {
        const tab = props.tabs.find(tab => tab.id === newTabId);
        if (tab) {
          if (tab.activeGroupId) {
            activeGroupId.value = tab.activeGroupId;
          } else if (tab.viewerGroups.length > 0) {
            activeGroupId.value = tab.viewerGroups[0].id;
          } else {
            activeGroupId.value = '';
          }
        }
      } else {
        activeGroupId.value = '';
      }
    });
    
    return {
      tabsContainer,
      activeTab,
      activeGroupId,
      draggingTabId,
      isDragOver,
      switchTab,
      closeTab,
      addNewTab,
      updateViewerGroup,
      removeViewerGroup,
      handleViewerRemoved,
      setActiveGroup,
      handleViewerActivated,
      convertGroupToTab,
      handleDragStart,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      handlePanelDrop,
      handleCreateLineProfile
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