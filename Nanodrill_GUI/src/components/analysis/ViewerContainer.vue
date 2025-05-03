<!-- Nanodrill_GUI/src/components/analysis/ViewerContainer.vue -->
<template>
    <div class="flex h-full w-full rounded-lg overflow-hidden"
         :class="{ 'flex-col': layout === 'vertical', 'border border-gray-200': true }">
      <!-- 第一個查看器 -->
      <div :class="firstViewerClass" @click="setActiveViewer(0)">
        <component :is="viewers[0].type"
                   v-bind="viewers[0].props"
                   :isActive="activeViewerIndex === 0"
                   @close="removeViewer(0)"
                   v-on="viewers[0].events || {}" />
      </div>
      
      <!-- 分隔線 -->
      <div v-if="viewers.length > 1" 
           :class="dividerClass"
           @mousedown="startResize">
      </div>
      
      <!-- 第二個查看器 -->
      <div v-if="viewers.length > 1" 
           :class="secondViewerClass" 
           @click="setActiveViewer(1)">
        <component :is="viewers[1].type"
                   v-bind="viewers[1].props"
                   :isActive="activeViewerIndex === 1"
                   @close="removeViewer(1)"
                   v-on="viewers[1].events || {}" />
      </div>
      
      <!-- 拖拽把手 -->
      <div class="absolute right-0 top-0 w-6 h-6 cursor-move"
           @mousedown="startDrag">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 m-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, computed, onBeforeUnmount } from 'vue';
  import type { PropType } from 'vue';
  import ImageViewer from './ImageViewer.vue';
  import ProfileViewer from './ProfileViewer.vue';
  
  // 定義查看器組件
  interface ViewerComponent {
    type: string;
    props: Record<string, any>;
    events?: Record<string, Function>;
  }
  
  export default defineComponent({
    name: 'ViewerContainer',
    components: {
      ImageViewer,
      ProfileViewer
    },
    props: {
      id: {
        type: String,
        required: true
      },
      viewers: {
        type: Array as PropType<ViewerComponent[]>,
        default: () => []
      },
      layout: {
        type: String as PropType<'horizontal' | 'vertical'>,
        default: 'horizontal'
      },
      splitRatio: {
        type: Number,
        default: 0.5
      }
    },
    emits: [
      'update:splitRatio', 
      'update:layout', 
      'viewer-added', 
      'viewer-removed', 
      'active-viewer-changed',
      'drag-start',
      'drag-end',
      'drag-move'
    ],
    setup(props, { emit }) {
      // 本地狀態
      const activeViewerIndex = ref(0);
      const isResizing = ref(false);
      const startPosition = ref(0);
      const startRatio = ref(props.splitRatio);
      const isDragging = ref(false);
      
      // 計算各部分的樣式類
      const firstViewerClass = computed(() => {
        const classes = ['relative'];
        
        // 只有一個查看器
        if (props.viewers.length === 1) {
          classes.push('w-full', 'h-full');
        } 
        // 水平佈局
        else if (props.layout === 'horizontal') {
          classes.push('h-full');
          classes.push(`w-[${props.splitRatio * 100}%]`);
        } 
        // 垂直佈局
        else {
          classes.push('w-full');
          classes.push(`h-[${props.splitRatio * 100}%]`);
        }
        
        return classes;
      });
      
      const secondViewerClass = computed(() => {
        const classes = ['relative'];
        
        // 水平佈局
        if (props.layout === 'horizontal') {
          classes.push('h-full');
          classes.push(`w-[${(1 - props.splitRatio) * 100}%]`);
        } 
        // 垂直佈局
        else {
          classes.push('w-full');
          classes.push(`h-[${(1 - props.splitRatio) * 100}%]`);
        }
        
        return classes;
      });
      
      const dividerClass = computed(() => {
        const classes = ['bg-gray-200', 'hover:bg-primary-300', 'transition-colors'];
        
        // 水平佈局
        if (props.layout === 'horizontal') {
          classes.push('w-1', 'h-full', 'cursor-col-resize');
        } 
        // 垂直佈局
        else {
          classes.push('h-1', 'w-full', 'cursor-row-resize');
        }
        
        if (isResizing.value) {
          classes.push('bg-primary-400');
        }
        
        return classes;
      });
      
      // 設置活動的查看器
      const setActiveViewer = (index: number) => {
        activeViewerIndex.value = index;
        emit('active-viewer-changed', { containerId: props.id, viewerIndex: index });
      };
      
      // 移除查看器
      const removeViewer = (index: number) => {
        emit('viewer-removed', { containerId: props.id, viewerIndex: index });
      };
      
      // 開始調整分隔線位置
      const startResize = (event: MouseEvent) => {
        isResizing.value = true;
        startPosition.value = props.layout === 'horizontal' ? event.clientX : event.clientY;
        startRatio.value = props.splitRatio;
        
        // 添加全局滑鼠事件
        document.addEventListener('mousemove', handleResize);
        document.addEventListener('mouseup', stopResize);
        
        // 防止事件傳播
        event.preventDefault();
        event.stopPropagation();
      };
      
      // 處理調整過程
      const handleResize = (event: MouseEvent) => {
        if (!isResizing.value) return;
        
        // 獲取容器尺寸
        const container = event.currentTarget as HTMLElement;
        const rect = container.getBoundingClientRect();
        
        // 計算新的分割比率
        let newRatio;
        if (props.layout === 'horizontal') {
          const deltaX = event.clientX - startPosition.value;
          const containerWidth = rect.width;
          newRatio = startRatio.value + (deltaX / containerWidth);
        } else {
          const deltaY = event.clientY - startPosition.value;
          const containerHeight = rect.height;
          newRatio = startRatio.value + (deltaY / containerHeight);
        }
        
        // 限制比率範圍
        newRatio = Math.max(0.1, Math.min(0.9, newRatio));
        
        // 更新分割比率
        emit('update:splitRatio', newRatio);
      };
      
      // 停止調整
      const stopResize = () => {
        isResizing.value = false;
        
        // 移除全局滑鼠事件
        document.removeEventListener('mousemove', handleResize);
        document.removeEventListener('mouseup', stopResize);
      };
      
      // 開始拖拽
      const startDrag = (event: MouseEvent) => {
        isDragging.value = true;
        emit('drag-start', { 
          containerId: props.id, 
          event: { 
            x: event.clientX, 
            y: event.clientY 
          } 
        });
        
        // 添加全局滑鼠事件
        document.addEventListener('mousemove', handleDrag);
        document.addEventListener('mouseup', stopDrag);
        
        // 防止事件傳播
        event.preventDefault();
        event.stopPropagation();
      };
      
      // 處理拖拽過程
      const handleDrag = (event: MouseEvent) => {
        if (!isDragging.value) return;
        
        emit('drag-move', { 
          containerId: props.id, 
          event: { 
            x: event.clientX, 
            y: event.clientY 
          } 
        });
      };
      
      // 停止拖拽
      const stopDrag = (event: MouseEvent) => {
        if (!isDragging.value) return;
        
        isDragging.value = false;
        emit('drag-end', { 
          containerId: props.id, 
          event: { 
            x: event.clientX, 
            y: event.clientY 
          } 
        });
        
        // 移除全局滑鼠事件
        document.removeEventListener('mousemove', handleDrag);
        document.removeEventListener('mouseup', stopDrag);
      };
      
      // 組件卸載時清理
      onBeforeUnmount(() => {
        document.removeEventListener('mousemove', handleResize);
        document.removeEventListener('mouseup', stopResize);
        document.removeEventListener('mousemove', handleDrag);
        document.removeEventListener('mouseup', stopDrag);
      });
      
      return {
        activeViewerIndex,
        firstViewerClass,
        secondViewerClass,
        dividerClass,
        setActiveViewer,
        removeViewer,
        startResize,
        startDrag
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
  
  /* 拖拽把手 */
  .cursor-move {
    cursor: move;
  }
  </style>