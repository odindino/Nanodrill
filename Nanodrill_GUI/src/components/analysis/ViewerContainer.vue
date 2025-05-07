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
        <!-- 布局切換按鈕 -->
        <button 
          v-if="viewers.length > 1"
          @click.stop="toggleLayout"
          class="p-1 rounded hover:bg-gray-200 text-gray-500 focus:outline-none"
          :title="layout === 'horizontal' ? '切換為垂直布局' : '切換為水平布局'"
        >
          <svg v-if="layout === 'horizontal'" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
          </svg>
        </button>
      </div>
    </div>
    
    <!-- 視圖容器 -->
    <div 
      class="viewers-container relative flex"
      :class="layout === 'horizontal' ? 'flex-row' : 'flex-col'"
      :style="{ height: `${groupHeight}px` }"
    >
      <!-- 遍歷渲染所有視圖 - 最多只顯示兩個 -->
      <template v-for="(viewer, index) in limitedViewers" :key="viewer.id">
        <!-- 視圖 -->
        <div 
          class="viewer-slot relative transition-all overflow-hidden"
          :style="layout === 'horizontal' 
            ? { width: `${getViewerWidth(index)}%`, height: '100%' } 
            : { height: `${getViewerHeight(index)}%`, width: '100%' }"
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
        
        <!-- 分隔線 (如果不是最後一個視圖) -->
        <div 
          v-if="index < limitedViewers.length - 1"
          :class="[
            'resizer bg-gray-200 hover:bg-blue-300 transition-colors',
            layout === 'horizontal' ? 'w-1 cursor-col-resize' : 'h-1 cursor-row-resize'
          ]"
          @mousedown.stop="startResize($event, index)"
        ></div>
      </template>
      
      <!-- 空白狀態 -->
      <div 
        v-if="viewers.length === 0"
        class="empty-state w-full h-full flex items-center justify-center bg-gray-50"
      >
        <div class="text-center p-4">
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
import { defineComponent, ref, onMounted, onBeforeUnmount, computed, watch } from 'vue';
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
    layout: {
      type: String as PropType<'horizontal' | 'vertical'>,
      default: 'horizontal'
    },
    isActive: {
      type: Boolean,
      default: false
    },
    groupHeight: {
      type: Number,
      default: 500
    }
  },
  emits: ['activate', 'viewer-removed'],
  setup(props, { emit }) {
    const analysisStore = useAnalysisStore();
    const spmDataStore = useSpmDataStore();
    
    // 視圖大小 - 初始化為平均分配（50%/50%）
    const viewerSizes = ref<number[]>([]);
    
    // 限制最多兩個視圖
    const limitedViewers = computed(() => {
      return props.viewers.slice(0, 2);
    });

    // 監視 viewers 屬性變化
    watch(() => props.viewers, (newViewers) => {
      if (newViewers.length > 2) {
        console.warn('ViewerContainer 不應該包含超過兩個視圖，請創建新的 ViewerContainer');
      }
      initViewerSizes();
    });
    
    // 調整大小相關
    const isResizing = ref(false);
    const resizingIndex = ref(-1);
    const startPosition = ref(0);
    const startSizes = ref<number[]>([]);
    
    // 初始化視圖大小
    const initViewerSizes = () => {
      const count = Math.min(props.viewers.length, 2); // 限制最多兩個視圖
      
      if (count === 0) return;
      
      // 平均分配大小
      const size = 100 / count;
      viewerSizes.value = Array(count).fill(50);
    };
    
    // 獲取視圖寬度
    const getViewerWidth = (index: number) => {
      if (viewerSizes.value.length <= index) {
        initViewerSizes();
      }
      
      // 即使只有一個視圖，也只給它 50% 的空間
      // 這樣第一個視圖就不會佔用 100% 的空間
      return viewerSizes.value[index] || 50;
    };
    
    // 獲取視圖高度
    const getViewerHeight = (index: number) => {
      if (viewerSizes.value.length <= index) {
        initViewerSizes();
      }
      
      // 同樣，即使只有一個視圖，也只給它 50% 的高度
      return viewerSizes.value[index] || 50;
    };
    
    // 啟用容器
    const activateContainer = () => {
      emit('activate', props.id);
    };
    
    // 移除視圖
    const removeViewer = (index: number) => {
      if (index < 0 || index >= limitedViewers.value.length) return;
      
      const viewerId = limitedViewers.value[index].id;
      console.log("發送移除視圖事件:", { groupId: props.id, viewerIndex: index, viewerId });
      
      // 發送事件通知父組件處理移除邏輯
      emit('viewer-removed', { groupId: props.id, viewerIndex: index, viewerId });
    };
    
    // 啟用視圖
    const activateViewer = (index: number) => {
      if (index < 0 || index >= limitedViewers.value.length) return;
      
      // 設置活動視圖
      analysisStore.setActiveViewer(limitedViewers.value[index].id);
      
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
    
    // 切換布局
    const toggleLayout = () => {
      const newLayout = props.layout === 'horizontal' ? 'vertical' : 'horizontal';
      
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
              layout: newLayout
            };
            
            // 更新標籤頁
            spmDataStore.updateAnalysisTabData(tabId, {
              viewerGroups: updatedGroups
            });
          }
        }
      }
    };
    
    // 開始調整大小
    const startResize = (event: MouseEvent, index: number) => {
      isResizing.value = true;
      resizingIndex.value = index;
      
      if (props.layout === 'horizontal') {
        startPosition.value = event.clientX;
      } else {
        startPosition.value = event.clientY;
      }
      
      // 保存當前大小
      startSizes.value = [...viewerSizes.value];
      
      // 添加全局事件
      document.addEventListener('mousemove', handleResize);
      document.addEventListener('mouseup', stopResize);
      
      // 防止事件冒泡
      event.stopPropagation();
    };
    
    // 處理調整大小
    const handleResize = (event: MouseEvent) => {
      if (!isResizing.value || resizingIndex.value === -1) return;
      
      const index = resizingIndex.value;
      const container = document.querySelector('.viewers-container') as HTMLElement;
      if (!container) return;
      
      // 計算新的大小
      let delta: number;
      let containerSize: number;
      
      if (props.layout === 'horizontal') {
        delta = event.clientX - startPosition.value;
        containerSize = container.offsetWidth;
      } else {
        delta = event.clientY - startPosition.value;
        containerSize = container.offsetHeight;
      }
      
      // 計算為百分比
      const deltaPercent = (delta / containerSize) * 100;
      
      // 調整大小
      const newSizes = [...startSizes.value];
      newSizes[index] += deltaPercent;
      newSizes[index + 1] -= deltaPercent;
      
      // 限制大小範圍
      newSizes[index] = Math.max(10, Math.min(90, newSizes[index]));
      newSizes[index + 1] = Math.max(10, Math.min(90, newSizes[index + 1]));
      
      // 更新大小
      viewerSizes.value = newSizes;
    };
    
    // 停止調整大小
    const stopResize = () => {
      isResizing.value = false;
      resizingIndex.value = -1;
      
      // 移除全局事件
      document.removeEventListener('mousemove', handleResize);
      document.removeEventListener('mouseup', stopResize);
    };
    
    // 組件掛載時初始化視圖大小
    onMounted(() => {
      initViewerSizes();
    });
    
    // 組件卸載前清理
    onBeforeUnmount(() => {
      document.removeEventListener('mousemove', handleResize);
      document.removeEventListener('mouseup', stopResize);
    });
    
    return {
      limitedViewers,
      viewerSizes,
      getViewerWidth,
      getViewerHeight,
      activateContainer,
      activateViewer,
      removeViewer,
      isViewerActive,
      toggleLayout,
      startResize
    };
  }
});
</script>

<style scoped>
/* 可調整大小的容器 */
.cursor-col-resize {
  cursor: col-resize;
}

.cursor-row-resize {
  cursor: row-resize;
}

/* 視圖群組高亮 */
.viewer-container.active {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

/* 分隔線懸停效果 */
.resizer:hover {
  transform: scaleX(1.5);
  transition: transform 0.2s ease;
}

.resizer {
  transition: transform 0.2s ease, background-color 0.2s ease;
  z-index: 10;
}

/* 確保視圖高度填滿容器 */
.viewer-slot {
  display: flex;
  flex-direction: column;
}

.viewer-slot > * {
  height: 100%;
  width: 100%;
}
</style>