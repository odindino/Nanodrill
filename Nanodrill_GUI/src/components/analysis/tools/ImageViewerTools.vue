// src/components/analysis/tools/ImageViewerTools.vue
<template>
  <div class="p-4 space-y-4">
    <h4 class="font-medium text-sm border-b pb-2 mb-2">影像處理</h4>
    
    <!-- 剖面分析 -->
    <div>
      <label class="text-xs text-gray-500 block mb-1">剖面分析</label>
      <button 
        @click="createLineProfile"
        class="w-full py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
        :disabled="isProfileViewerLinked"
      >
        建立線性剖面
      </button>
      
      <!-- 如果已有關聯的 ProfileViewer，顯示提示 -->
      <div v-if="isProfileViewerLinked" class="mt-2 text-xs text-gray-500">
        此影像已創建剖面圖。請先關閉現有剖面圖後再建立新的剖面圖。
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue';
import type { PropType } from 'vue';
import { useSpmDataStore } from '../../../stores/spmDataStore';
import { useAnalysisStore } from '../../../stores/analysisStore';
import type { Viewer } from '../../../stores/spmDataStore';

export default defineComponent({
  name: 'ImageViewerTools',
  props: {
    viewer: {
      type: Object as PropType<Viewer>,
      required: true
    }
  },
  setup(props) {
    const spmDataStore = useSpmDataStore();
    const analysisStore = useAnalysisStore();
    
    // 計算屬性：檢查是否有已連接的 ProfileViewer
    const isProfileViewerLinked = computed(() => {
      // 獲取最新的 viewer 狀態
      const location = spmDataStore.getViewerLocation(props.viewer.id);
      if (!location) return false;
      
      const { tabId, groupId, viewerIndex } = location;
      const tab = spmDataStore.analysisTabs.find(t => t.id === tabId);
      if (!tab || !tab.viewerGroups) return false;
      
      const group = tab.viewerGroups.find(g => g.id === groupId);
      if (!group) return false;
      
      const currentViewer = group.viewers[viewerIndex];
      
      // 檢查是否有連接的 ProfileViewer 且該 ProfileViewer 是否仍然存在
      if (!currentViewer.props.linkedProfileViewerId) return false;
      
      // 檢查連接的 ProfileViewer 是否仍然存在
      let profileViewerExists = false;
      for (const g of tab.viewerGroups) {
        for (const v of g.viewers) {
          if (v.id === currentViewer.props.linkedProfileViewerId) {
            profileViewerExists = true;
            break;
          }
        }
        if (profileViewerExists) break;
      }
      
      return profileViewerExists;
    });
    
    // 創建線性剖面
    const createLineProfile = () => {
      // 檢查是否可以創建線性剖面
      if (isProfileViewerLinked.value) {
        console.log("此 ImageViewer 已綁定 ProfileViewer，無法創建新的剖面圖");
        return;
      }
      
      // 使用 analysisStore 中的方法創建線性剖面
      analysisStore.createLineProfile(props.viewer.id);
    };
    
    return {
      isProfileViewerLinked,
      createLineProfile
    };
  }
});
</script>