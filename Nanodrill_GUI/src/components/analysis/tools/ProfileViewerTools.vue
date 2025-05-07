// src/components/analysis/tools/ProfileViewerTools.vue
<template>
  <div class="p-4 space-y-4">
    <h4 class="font-medium text-sm border-b pb-2 mb-2">剖面設定</h4>
    
    <!-- 來源信息顯示 -->
    <div v-if="hasSourceViewer" class="bg-gray-50 p-3 rounded border border-gray-200">
      <div class="text-sm text-gray-700">
        <span class="font-medium">來源影像:</span> {{ sourceViewerTitle }}
      </div>
      
      <!-- 添加線性剖面測量按鈕 -->
      <div class="mt-3">
        <button 
          @click="measureNewProfile"
          class="w-full py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
          :disabled="isSourceViewerMeasuring"
        >
          線性剖面測量
        </button>
        
        <div v-if="isSourceViewerMeasuring" class="mt-2 text-xs text-blue-600">
          請在影像上點擊設置測量點
        </div>
      </div>
    </div>
    
    <div v-else class="text-sm text-gray-500 italic">
      未連接到來源影像
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';
import type { PropType } from 'vue';
import type { Viewer } from '../../../stores/spmDataStore';
import { useAnalysisStore } from '../../../stores/analysisStore';
import { useSpmDataStore } from '../../../stores/spmDataStore';

export default defineComponent({
  name: 'ProfileViewerTools',
  props: {
    viewer: {
      type: Object as PropType<Viewer>,
      required: true
    }
  },
  setup(props) {
    const analysisStore = useAnalysisStore();
    const spmDataStore = useSpmDataStore();
    
    // 計算屬性
    const hasSourceViewer = computed(() => {
      return !!props.viewer.props.sourceViewerId;
    });
    
    const sourceViewerId = computed(() => {
      return props.viewer.props.sourceViewerId || '';
    });
    
    const sourceViewerTitle = computed(() => {
      return props.viewer.props.sourceViewerTitle || '未知影像';
    });
    
    // 判斷源影像是否正在測量模式
    const isSourceViewerMeasuring = computed(() => {
      if (!sourceViewerId.value) return false;
      
      // 檢查源影像的測量模式狀態
      const location = spmDataStore.getViewerLocation(sourceViewerId.value);
      if (!location) return false;
      
      const { tabId, groupId, viewerIndex } = location;
      const tab = spmDataStore.analysisTabs.find(t => t.id === tabId);
      if (!tab || !tab.viewerGroups) return false;
      
      const group = tab.viewerGroups.find(g => g.id === groupId);
      if (!group) return false;
      
      const sourceViewer = group.viewers[viewerIndex];
      return sourceViewer.props.profileMeasureMode === true;
    });
    
    // 開始新的剖面測量
    const measureNewProfile = () => {
      // 檢查是否有源影像
      if (!sourceViewerId.value) return;
      
      // 直接使用 store 啟動測量模式
      analysisStore.toggleMeasureMode(sourceViewerId.value);
    };
    
    return {
      hasSourceViewer,
      sourceViewerTitle,
      isSourceViewerMeasuring,
      measureNewProfile
    };
  }
});
</script>