// src/components/analysis/tools/ProfileViewerTools.vue
<template>
  <div class="p-4 space-y-4">
    <h4 class="font-medium text-sm border-b pb-2 mb-2">剖面設定</h4>
    
    <!-- 來源信息顯示 -->
    <div v-if="hasSourceViewer" class="bg-gray-50 p-3 rounded border border-gray-200">
      <div class="text-sm text-gray-700">
        <span class="font-medium">來源影像:</span> {{ sourceViewerTitle }}
      </div>
      
      <!-- 線性剖面測量按鈕 -->
      <div class="mt-3 space-y-2">
        <button 
          @click="startLineProfileMeasurement"
          class="w-full py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
          :class="{ 'bg-primary-100 border-primary-300': isSourceViewerMeasuring }"
        >
          {{ isSourceViewerMeasuring ? '正在測量中...' : '線性剖面測量' }}
        </button>
        
        <div v-if="isSourceViewerMeasuring" class="p-2 text-xs bg-blue-50 text-blue-600 rounded border border-blue-200">
          請在影像上點擊設置測量點。點擊後將自動繪製剖面線。
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
      
      // 獲取最新的源影像狀態
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
    
    // 開始線性剖面測量
    const startLineProfileMeasurement = () => {
      if (!sourceViewerId.value) return;
      
      // 切換源影像的測量模式
      analysisStore.toggleMeasureMode(sourceViewerId.value, props.viewer.id);
      
      // 確保當前活動視圖保持為 ProfileViewer
      analysisStore.setActiveViewer(props.viewer.id);
    };
    
    return {
      hasSourceViewer,
      sourceViewerTitle,
      isSourceViewerMeasuring,
      startLineProfileMeasurement
    };
  }
});
</script>