<!-- src/components/analysis/tools/ImageViewerTools.vue -->
<template>
  <div class="p-4 space-y-4">
    <h4 class="font-medium text-sm border-b pb-2 mb-2">影像處理</h4>
    
    <!-- 色彩映射 -->
    <div>
      <label class="text-xs text-gray-500 block mb-1">色彩映射</label>
      <select 
        v-model="colormap" 
        class="w-full text-sm border border-gray-300 rounded py-1.5 px-2 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
        @change="updateSettings"
      >
        <option value="viridis">Viridis</option>
        <option value="plasma">Plasma</option>
        <option value="inferno">Inferno</option>
        <option value="magma">Magma</option>
        <option value="cividis">Cividis</option>
        <option value="Oranges">Oranges</option>
        <option value="hot">Hot</option>
        <option value="cool">Cool</option>
        <option value="jet">Jet</option>
      </select>
    </div>
    
    <!-- 高度縮放 -->
    <div>
      <div class="flex justify-between mb-1">
        <label class="text-xs text-gray-500">高度縮放</label>
        <span class="text-xs text-gray-500">{{ zScale.toFixed(1) }}x</span>
      </div>
      <input 
        type="range" 
        v-model="zScale" 
        min="0.1" 
        max="5" 
        step="0.1" 
        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        @change="updateSettings"
      >
    </div>
    
    <!-- 平面校正 -->
    <div>
      <label class="text-xs text-gray-500 block mb-1">平面校正</label>
      <div class="flex space-x-2">
        <button 
          @click="applyFlatten('mean')"
          class="flex-1 py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
        >
          線性平面化
        </button>
        <button 
          @click="applyFlatten('polyfit')"
          class="flex-1 py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
        >
          多項式平面化
        </button>
      </div>
    </div>
    
    <!-- 剖面分析 -->
    <div>
      <label class="text-xs text-gray-500 block mb-1">剖面分析</label>
      <button 
        @click="createLineProfile"
        class="w-full py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
      >
        建立線性剖面
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch} from 'vue';
import type { PropType } from 'vue';
import { useSpmDataStore } from '../../../stores/spmDataStore';
import type { Viewer } from '../../../stores/spmDataStore';

export default defineComponent({
  name: 'ImageViewerTools',
  props: {
    viewer: {
      type: Object as PropType<Viewer>,
      required: true
    }
  },
  emits: ['create-line-profile'],
  setup(props, { emit }) {
    const spmDataStore = useSpmDataStore();
    
    // 圖像工具設置
    const colormap = ref(props.viewer.props.colormap || 'Oranges');
    const zScale = ref(props.viewer.props.zScale || 1.0);
    
    // 當 viewer 變化時，更新工具設置
    watch(() => props.viewer, (newViewer) => {
      colormap.value = newViewer.props.colormap || 'Oranges';
      zScale.value = newViewer.props.zScale || 1.0;
    }, { immediate: true });
    
    // 更新設置
    const updateSettings = () => {
      const viewerId = props.viewer.id;
      const location = spmDataStore.getViewerLocation(viewerId);
      
      if (location) {
        // 找到標籤頁和群組
        const tab = spmDataStore.analysisTabs.find(t => t.id === location.tabId);
        if (tab && tab.viewerGroups) {
          // 更新視圖屬性
          const updatedGroups = [...tab.viewerGroups];
          const group = updatedGroups.find(g => g.id === location.groupId);
          
          if (group) {
            const updatedViewers = [...group.viewers];
            updatedViewers[location.viewerIndex] = {
              ...updatedViewers[location.viewerIndex],
              props: {
                ...updatedViewers[location.viewerIndex].props,
                colormap: colormap.value,
                zScale: zScale.value
              }
            };
            
            // 更新群組
            const groupIndex = updatedGroups.indexOf(group);
            updatedGroups[groupIndex] = {
              ...group,
              viewers: updatedViewers
            };
            
            // 更新標籤頁
            spmDataStore.updateAnalysisTabData(location.tabId, {
              viewerGroups: updatedGroups
            });
          }
        }
      }
    };
    
    // 創建線性剖面
    const createLineProfile = () => {
      emit('create-line-profile', { viewerId: props.viewer.id });
    };
    
    // 平面校正
    const applyFlatten = (method: string) => {
      // 暫時簡單記錄，後續可實現具體功能
      console.log(`應用${method}平面校正`);
    };
    
    return {
      colormap,
      zScale,
      updateSettings,
      createLineProfile,
      applyFlatten
    };
  }
});
</script>

<style scoped>
/* 自定義範圍輸入滑塊 */
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #2563eb;
  border-radius: 50%;
  cursor: pointer;
}

input[type="range"]::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #2563eb;
  border-radius: 50%;
  cursor: pointer;
}
</style>