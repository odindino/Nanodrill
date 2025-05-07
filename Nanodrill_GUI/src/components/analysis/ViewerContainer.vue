<!-- src/components/analysis/ViewerContainer.vue -->
<template>
  <div class="viewer-container bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden mb-4"
       :class="{ 'active': isActive }"
       @click="activateContainer">
    <!-- 標題欄 -->
    <div class="container-header bg-gray-100 px-3 py-2 border-b border-gray-200 flex items-center justify-between">
      <h3 class="font-medium text-sm text-gray-700 truncate">
        {{ title || 'Data Group' }}
      </h3>
      
      <div class="flex space-x-1">
        <!-- 視圖操作按鈕 (如果需要) -->
      </div>
    </div>
    
    <!-- 視圖網格容器 -->
    <div 
      class="viewers-grid p-3 grid gap-3"
      :style="{
        'grid-template-columns': 'repeat(2, 1fr)',
        'grid-auto-rows': `${gridRowHeight}px`
      }"
    >
      <!-- 遍歷渲染所有視圖 -->
      <template v-for="(viewer, index) in viewers" :key="viewer.id">
        <!-- 視圖 -->
        <div 
          class="viewer-cell relative bg-white border border-gray-200 rounded-md overflow-hidden"
          :class="{ 'ring-2 ring-primary ring-opacity-50': isViewerActive(viewer.id) }"
          @click.stop="activateViewer(index)"
        >
          <component 
            :is="viewer.component" 
            v-bind="viewer.props"
            :isActive="isViewerActive(viewer.id)"
            @click.stop="activateViewer(index)"
            @close="removeViewer(index)"
          />
        </div>
      </template>
      
      <!-- 空白狀態 -->
      <div 
        v-if="viewers.length === 0"
        class="empty-state col-span-2 bg-gray-50 rounded-md flex items-center justify-center p-8"
      >
        <div class="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto text-gray-300 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-sm text-gray-500">尚無視圖</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import type { PropType } from 'vue';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useSpmDataStore } from '../../stores/spmDataStore';
import type { Viewer } from '../../stores/spmDataStore';

export default defineComponent({
  name: 'ViewerContainer',
  props: {
    id: {
      type: String,
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    viewers: {
      type: Array as PropType<Viewer[]>,
      default: () => []
    },
    isActive: {
      type: Boolean,
      default: false
    }
  },
  emits: ['activate', 'viewer-removed'],
  setup(props, { emit }) {
    const analysisStore = useAnalysisStore();
    const spmDataStore = useSpmDataStore();
    
    // 設置網格行高
    const gridRowHeight = ref(350);  // 每行的默認高度
    
    // 啟用容器
    const activateContainer = () => {
      emit('activate', props.id);
    };
    
    // 移除視圖
    const removeViewer = (index: number) => {
      if (index < 0 || index >= props.viewers.length) return;
      
      const viewerId = props.viewers[index].id;
      console.log("發送移除視圖事件:", { groupId: props.id, viewerIndex: index, viewerId });
      
      // 發送事件通知父組件處理移除邏輯
      emit('viewer-removed', { groupId: props.id, viewerIndex: index, viewerId });
    };
    
    // 啟用視圖
    const activateViewer = (index: number) => {
      if (index < 0 || index >= props.viewers.length) return;
      
      // 設置活動視圖
      analysisStore.setActiveViewer(props.viewers[index].id);
      
      // 更新視圖的 isActive 屬性
      updateViewersActiveState(index);
    };
    
    // 更新視圖的活動狀態
    const updateViewersActiveState = (activeIndex: number) => {
      const updatedViewers = props.viewers.map((viewer, idx) => ({
        ...viewer,
        props: {
          ...viewer.props,
          isActive: idx === activeIndex
        }
      }));
      
      // 更新標籤頁
      const tabId = getTabIdForGroup(props.id);
      if (tabId) {
        // 找到當前群組的索引
        const tab = spmDataStore.analysisTabs.find(t => t.id === tabId);
        if (tab && tab.viewerGroups) {
          const groupIndex = tab.viewerGroups.findIndex(g => g.id === props.id);
          if (groupIndex !== -1) {
            const updatedGroups = [...tab.viewerGroups];
            updatedGroups[groupIndex] = {
              ...updatedGroups[groupIndex],
              viewers: updatedViewers
            };
            
            // 更新標籤頁
            spmDataStore.updateAnalysisTabData(tabId, {
              viewerGroups: updatedGroups
            });
          }
        }
      }
    };
    
    // 獲取群組所屬的標籤頁ID
    const getTabIdForGroup = (groupId: string): string | null => {
      for (const tab of spmDataStore.analysisTabs) {
        if (tab.viewerGroups && tab.viewerGroups.some(g => g.id === groupId)) {
          return tab.id;
        }
      }
      return null;
    };
    
    // 檢查視圖是否活動
    const isViewerActive = (viewerId: string) => {
      return analysisStore.activeViewerId === viewerId;
    };
    
    return {
      gridRowHeight,
      activateContainer,
      activateViewer,
      removeViewer,
      isViewerActive
    };
  }
});
</script>

<style scoped>
/* 視圖群組高亮 */
.viewer-container.active {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

/* 視圖單元格 */
.viewer-cell {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 確保視圖組件填滿單元格 */
.viewer-cell > * {
  height: 100%;
  width: 100%;
}
</style>