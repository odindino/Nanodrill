<!-- src/components/analysis/ViewerGroup.vue -->
<template>
  <div 
    class="viewer-group bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden mb-4"
    :class="{ 'active': isActive }"
    @click="activateGroup"
  >
    <!-- 標題欄 -->
    <div class="group-header bg-gray-100 px-3 py-2 border-b border-gray-200 flex items-center justify-between">
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
        
        <!-- 拖曳把手 -->
        <div 
          class="p-1 rounded hover:bg-gray-200 text-gray-500 cursor-move"
          @mousedown.stop="startDrag"
          :title="'拖動組'">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
          </svg>
        </div>
        
        <!-- 轉換為標籤頁按鈕 -->
        <button 
          @click.stop="convertToTab"
          class="p-1 rounded hover:bg-gray-200 text-gray-500 focus:outline-none"
          title="轉換為標籤頁">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
        
        <!-- 關閉按鈕 -->
        <button 
          @click.stop="closeGroup"
          class="p-1 rounded hover:bg-gray-200 text-gray-500 focus:outline-none"
          title="關閉群組">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
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
      <!-- 第一個視圖 -->
      <div 
        v-if="viewers.length > 0"
        :class="[
          'viewer-slot relative transition-all',
          layout === 'horizontal' 
            ? 'h-full' 
            : `h-[${firstViewerHeight}%]`,
          'overflow-hidden'
        ]"
        :style="getViewerStyle(0)"
        @click.stop="activateViewer(0)"
      >
        <component 
          :is="viewers[0].component" 
          v-bind="viewers[0].props"
          :isActive="activeViewerIndex === 0"
          @click.stop="activateViewer(0)"
          @close="removeViewer(0)"
        />
      </div>
      
      <!-- 分隔線 -->
      <div 
        v-if="viewers.length > 1"
        :class="[
          'resizer bg-gray-200 hover:bg-blue-300 transition-colors',
          layout === 'horizontal' ? 'w-1 cursor-col-resize' : 'h-1 cursor-row-resize'
        ]"
        @mousedown.stop="startResize"
      ></div>
      
      <!-- 第二個視圖 -->
      <div 
        v-if="viewers.length > 1"
        :class="[
          'viewer-slot relative transition-all',
          layout === 'horizontal' 
            ? 'h-full' 
            : `h-[${100 - firstViewerHeight}%]`,
          'overflow-hidden'
        ]"
        :style="getViewerStyle(1)"
        @click.stop="activateViewer(1)"
      >
        <component 
          :is="viewers[1].component" 
          v-bind="viewers[1].props"
          :isActive="activeViewerIndex === 1"
          @click.stop="activateViewer(1)"
          @close="removeViewer(1)"
        />
      </div>
      
      <!-- 空白狀態 -->
      <div 
        v-if="viewers.length === 0"
        class="empty-state w-full h-full flex items-center justify-center bg-gray-50"
      >
        <div class="text-center p-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto text-gray-300 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-sm text-gray-500">拖放標籤頁或視圖到此處</p>
        </div>
      </div>
      
      <!-- 拖放提示層 -->
      <div 
        v-if="isDragOver"
        class="absolute inset-0 z-10 bg-blue-100 bg-opacity-50 border-2 border-dashed border-blue-400 flex items-center justify-center"
      >
        <p class="font-medium text-blue-600">放開以添加視圖</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import type { PropType } from 'vue';

// 視圖接口
export interface Viewer {
  id: string;
  component: string; // 組件名
  props: Record<string, any>;
  title?: string;
}

export default defineComponent({
  name: 'ViewerGroup',
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
      default: 500 // 增加默認高度
    }
  },
  emits: [
    'activate',
    'activate-viewer',
    'remove-viewer',
    'close',
    'layout-change',
    'convert-to-tab',
    'drag-start',
    'drag-move',
    'drag-end',
    'resize'
  ],
  setup(props, { emit }) {
    // 内部状态
    const activeViewerIndex = ref(props.viewers.length > 0 ? 0 : -1);
    const firstViewerWidth = ref(50); // 水平布局時第一個視圖的寬度百分比
    const firstViewerHeight = ref(50); // 垂直布局時第一個視圖的高度百分比
    
    // 拖曳相關
    const isDragging = ref(false);
    const startX = ref(0);
    const startY = ref(0);
    
    // 調整大小相關
    const isResizing = ref(false);
    const startPosition = ref(0);
    const startSize = ref(0);
    
    // 拖放相關
    const isDragOver = ref(false);
    
    // 獲取視圖樣式
    const getViewerStyle = (index: number) => {
      if (index >= props.viewers.length) return {};
      
      if (props.layout === 'horizontal') {
        return {
          width: index === 0 ? `${firstViewerWidth.value}%` : `${100 - firstViewerWidth.value}%`,
          height: '100%'
        };
      } else {
        return {
          width: '100%'
        };
      }
    };
    
    // 啟用群組
    const activateGroup = () => {
      emit('activate', props.id);
    };
    
    // 啟用視圖
    const activateViewer = (index: number) => {
      console.log(`在群組 ${props.id} 中啟用視圖 ${index}`);
      
      if (index < 0 || index >= props.viewers.length) {
        console.error('無效的視圖索引:', index);
        return;
      }
      
      activeViewerIndex.value = index;
      
      // 發送事件通知父組件視圖被激活
      emit('activate-viewer', { 
        groupId: props.id, 
        viewerIndex: index, 
        viewerId: props.viewers[index].id,
        viewerComponent: props.viewers[index].component
      });
    };
    
    // 移除視圖
    const removeViewer = (index: number) => {
      if (index < 0 || index >= props.viewers.length) {
        console.error('無效的視圖索引:', index);
        return;
      }
      
      emit('remove-viewer', { 
        groupId: props.id, 
        viewerIndex: index, 
        viewerId: props.viewers[index].id 
      });
    };
    
    // 關閉群組
    const closeGroup = () => {
      emit('close', props.id);
    };
    
    // 切換布局
    const toggleLayout = () => {
      const newLayout = props.layout === 'horizontal' ? 'vertical' : 'horizontal';
      emit('layout-change', { groupId: props.id, layout: newLayout });
    };
    
    // 轉換為標籤頁
    const convertToTab = () => {
      emit('convert-to-tab', props.id);
    };
    
    // 開始拖曳
    const startDrag = (event: MouseEvent) => {
      isDragging.value = true;
      startX.value = event.clientX;
      startY.value = event.clientY;
      
      emit('drag-start', { 
        groupId: props.id, 
        event: { x: event.clientX, y: event.clientY }
      });
      
      // 添加全局事件
      document.addEventListener('mousemove', handleDragMove);
      document.addEventListener('mouseup', handleDragEnd);
      
      // 防止事件冒泡
      event.stopPropagation();
    };
    
    // 處理拖曳移動
    const handleDragMove = (event: MouseEvent) => {
      if (!isDragging.value) return;
      
      emit('drag-move', {
        groupId: props.id,
        event: { x: event.clientX, y: event.clientY },
        delta: { x: event.clientX - startX.value, y: event.clientY - startY.value }
      });
    };
    
    // 處理拖曳結束
    const handleDragEnd = (event: MouseEvent) => {
      isDragging.value = false;
      
      emit('drag-end', {
        groupId: props.id,
        event: { x: event.clientX, y: event.clientY }
      });
      
      // 移除全局事件
      document.removeEventListener('mousemove', handleDragMove);
      document.removeEventListener('mouseup', handleDragEnd);
    };
    
    // 開始調整大小
    const startResize = (event: MouseEvent) => {
      isResizing.value = true;
      
      if (props.layout === 'horizontal') {
        startPosition.value = event.clientX;
        startSize.value = firstViewerWidth.value;
      } else {
        startPosition.value = event.clientY;
        startSize.value = firstViewerHeight.value;
      }
      
      // 添加全局事件
      document.addEventListener('mousemove', handleResize);
      document.addEventListener('mouseup', stopResize);
      
      // 防止事件冒泡
      event.stopPropagation();
    };
    
    // 處理調整大小
    const handleResize = (event: MouseEvent) => {
      if (!isResizing.value) return;
      
      const container = event.currentTarget as HTMLElement;
      let containerSize: number;
      let newSize: number;
      
      if (props.layout === 'horizontal') {
        const resizeTarget = document.querySelector('.viewers-container') as HTMLElement;
        if (!resizeTarget) return;
        
        containerSize = resizeTarget.offsetWidth;
        const delta = event.clientX - startPosition.value;
        newSize = startSize.value + (delta / containerSize * 100);
      } else {
        const resizeTarget = document.querySelector('.viewers-container') as HTMLElement;
        if (!resizeTarget) return;
        
        containerSize = resizeTarget.offsetHeight;
        const delta = event.clientY - startPosition.value;
        newSize = startSize.value + (delta / containerSize * 100);
      }
      
      // 限制大小範圍
      newSize = Math.max(20, Math.min(80, newSize));
      
      // 更新大小
      if (props.layout === 'horizontal') {
        firstViewerWidth.value = newSize;
      } else {
        firstViewerHeight.value = newSize;
      }
      
      // 發送調整大小事件
      emit('resize', {
        groupId: props.id,
        layout: props.layout,
        sizes: props.layout === 'horizontal' 
          ? [firstViewerWidth.value, 100 - firstViewerWidth.value]
          : [firstViewerHeight.value, 100 - firstViewerHeight.value]
      });
    };
    
    // 停止調整大小
    const stopResize = () => {
      isResizing.value = false;
      
      // 移除全局事件
      document.removeEventListener('mousemove', handleResize);
      document.removeEventListener('mouseup', stopResize);
    };
    
    // 當組件掛載時設置預設分割比例為 50/50
    onMounted(() => {
      firstViewerWidth.value = 50;
      firstViewerHeight.value = 50;
      
      // 如果有視圖，默認激活第一個
      if (props.viewers.length > 0) {
        activateViewer(0);
      }
    });
    
    return {
      activeViewerIndex,
      firstViewerWidth,
      firstViewerHeight,
      isDragOver,
      getViewerStyle,
      activateGroup,
      activateViewer,
      removeViewer,
      closeGroup,
      toggleLayout,
      convertToTab,
      startDrag,
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
.viewer-group.active {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

/* 拖曳手柄 */
.cursor-move {
  cursor: move;
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