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
    <div v-if="showToolsPanel" class="flex-grow overflow-y-auto">
      <template v-if="activeViewer">
        <!-- 根據 Viewer 類型載入對應的工具面板 -->
        <component 
          :is="getToolsComponent(activeViewer.component)"
          :viewer="activeViewer"
          @create-line-profile="createLineProfile"
          @measure-new-profile="measureNewProfile"
        />
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
import { defineComponent, ref, computed } from 'vue';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useSpmDataStore } from '../../stores/spmDataStore';
import ImageViewerTools from './tools/ImageViewerTools.vue';
import ProfileViewerTools from './tools/ProfileViewerTools.vue';

export default defineComponent({
  name: 'ToolsPanel',
  components: {
    ImageViewerTools,
    ProfileViewerTools
  },
  setup() {
    const analysisStore = useAnalysisStore();
    const spmDataStore = useSpmDataStore();
    
    const showToolsPanel = ref(true);
    
    // 獲取當前活動的視圖
    const activeViewer = computed(() => {
      const viewerId = analysisStore.activeViewerId;
      if (!viewerId) return null;
      
      // 查找擁有該視圖的標籤頁和群組
      for (const tab of spmDataStore.analysisTabs) {
        if (tab.viewerGroups) {
          for (const group of tab.viewerGroups) {
            const viewer = group.viewers.find(v => v.id === viewerId);
            if (viewer) {
              return viewer;
            }
          }
        }
      }
      
      return null;
    });
    
    // 切換工具面板
    const toggleToolsPanel = () => {
      showToolsPanel.value = !showToolsPanel.value;
    };
    
    // 根據 Viewer 類型獲取對應的工具組件
    const getToolsComponent = (viewerType: string) => {
      switch (viewerType) {
        case 'ImageViewer':
          return 'ImageViewerTools';
        case 'ProfileViewer':
          return 'ProfileViewerTools';
        default:
          return null;
      }
    };
    
    // 建立線性剖面
    const createLineProfile = (data: any) => {
      // 調用 analysisStore 中的方法創建線性剖面
      analysisStore.createLineProfile(data.viewerId);
    };
    
    // 測量新的剖面
    const measureNewProfile = (data: any) => {
      // 調用 analysisStore 中的方法測量新的剖面
      if (data.profileViewerId && data.sourceViewerId) {
        analysisStore.createLineProfile(data.sourceViewerId, {
          id: data.profileViewerId
        });
      }
    };
    
    return {
      showToolsPanel,
      activeViewer,
      toggleToolsPanel,
      getToolsComponent,
      createLineProfile,
      measureNewProfile
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