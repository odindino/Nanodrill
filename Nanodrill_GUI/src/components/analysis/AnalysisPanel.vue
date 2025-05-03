<!-- Nanodrill_GUI/src/components/analysis/AnalysisPanel.vue -->
<template>
    <div class="h-full w-full flex flex-col bg-gray-50 overflow-auto relative">
      <!-- 拖拽疊放區指示 -->
      <div v-if="isDragOver" 
           class="absolute inset-0 bg-primary-100 border-2 border-dashed border-primary-400 z-10 flex items-center justify-center">
        <p class="text-primary-600 font-medium">釋放以添加到此面板</p>
      </div>
      
      <!-- 無內容提示 -->
      <div v-if="containers.length === 0" class="h-full flex flex-col items-center justify-center p-8">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-gray-500 mb-4">此面板尚無內容</p>
        <p class="text-sm text-gray-400">從標籤欄拖曳標籤頁到此處，或開啟新的影像</p>
      </div>
      
      <!-- 容器網格佈局 -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 auto-rows-min">
        <div v-for="container in containers" 
             :key="container.id" 
             class="h-96 min-h-80"
             @dragover.prevent="onDragOver"
             @drop.prevent="onDrop"
             @dragleave.prevent="onDragLeave">
          <ViewerContainer 
            :id="container.id"
            :viewers="container.viewers"
            :layout="container.layout"
            :splitRatio="container.splitRatio"
            @update:splitRatio="updateContainerSplitRatio(container.id, $event)"
            @update:layout="updateContainerLayout(container.id, $event)"
            @viewer-removed="handleViewerRemoved"
            @active-viewer-changed="handleActiveViewerChanged"
            @drag-start="handleContainerDragStart"
            @drag-move="handleContainerDragMove"
            @drag-end="handleContainerDragEnd" />
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref } from 'vue';
  import type { PropType } from 'vue';
  import ViewerContainer from './ViewerContainer.vue';
  
  // 定義查看器容器
  interface ViewerContainer {
    id: string;
    viewers: Array<{
      type: string;
      props: Record<string, any>;
      events?: Record<string, Function>;
    }>;
    layout: 'horizontal' | 'vertical';
    splitRatio: number;
  }
  
  export default defineComponent({
    name: 'AnalysisPanel',
    components: {
      ViewerContainer
    },
    props: {
      containers: {
        type: Array as PropType<ViewerContainer[]>,
        default: () => []
      }
    },
    emits: [
      'container-updated', 
      'container-removed', 
      'active-viewer-changed',
      'drop'
    ],
    setup(props, { emit }) {
      // 拖拽相關狀態
      const isDragOver = ref(false);
      
      // 更新容器分割比率
      const updateContainerSplitRatio = (containerId: string, ratio: number) => {
        emit('container-updated', { 
          id: containerId, 
          changes: { splitRatio: ratio } 
        });
      };
      
      // 更新容器佈局
      const updateContainerLayout = (containerId: string, layout: 'horizontal' | 'vertical') => {
        emit('container-updated', { 
          id: containerId, 
          changes: { layout } 
        });
      };
      
      // 處理查看器移除
      const handleViewerRemoved = ({ containerId, viewerIndex }: { containerId: string, viewerIndex: number }) => {
        // 找到對應的容器
        const container = props.containers.find(c => c.id === containerId);
        if (!container) return;
        
        // 如果容器只有一個查看器，移除整個容器
        if (container.viewers.length <= 1) {
          emit('container-removed', containerId);
        } 
        // 否則，只移除指定的查看器
        else {
          const updatedViewers = [...container.viewers];
          updatedViewers.splice(viewerIndex, 1);
          emit('container-updated', { 
            id: containerId, 
            changes: { viewers: updatedViewers } 
          });
        }
      };
      
      // 處理活動查看器變更
      const handleActiveViewerChanged = ({ containerId, viewerIndex }: { containerId: string, viewerIndex: number }) => {
        emit('active-viewer-changed', { containerId, viewerIndex });
      };
      
      // 處理容器拖拽開始
      const handleContainerDragStart = ({ containerId, event }: { containerId: string, event: { x: number, y: number } }) => {
        // 可以實現拖拽視圖功能
        console.log('Container drag start:', containerId, event);
      };
      
      // 處理容器拖拽移動
      const handleContainerDragMove = ({ containerId, event }: { containerId: string, event: { x: number, y: number } }) => {
        // 可以實現拖拽視圖功能
        console.log('Container drag move:', containerId, event);
      };
      
      // 處理容器拖拽結束
      const handleContainerDragEnd = ({ containerId, event }: { containerId: string, event: { x: number, y: number } }) => {
        // 可以實現拖拽視圖功能
        console.log('Container drag end:', containerId, event);
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
          emit('drop', { dropData, event });
        } catch (error) {
          console.error('無法解析拖拽數據:', error);
        }
      };
      
      return {
        isDragOver,
        updateContainerSplitRatio,
        updateContainerLayout,
        handleViewerRemoved,
        handleActiveViewerChanged,
        handleContainerDragStart,
        handleContainerDragMove,
        handleContainerDragEnd,
        onDragOver,
        onDragLeave,
        onDrop
      };
    }
  });
  </script>
  
  <style scoped>
  /* Auto-rows 需要在Tailwind中單獨設置 */
  .auto-rows-min {
    grid-auto-rows: minmax(384px, auto);
  }
  
  .min-h-80 {
    min-height: 320px;
  }
  </style>