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
          v-if="!isSourceViewerMeasuring"
          @click="startLineProfileMeasurement"
          class="w-full py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
        >
          線性剖面測量
        </button>
        
        <div v-else class="space-y-2">
          <button 
            @click="endLineProfileMeasurement"
            class="w-full py-1.5 px-2 text-xs font-medium rounded border border-red-300 bg-red-50 text-red-700 hover:bg-red-100 focus:outline-none focus:ring-1 focus:ring-red-500"
          >
            結束測量模式
          </button>
          
          <div class="p-2 text-xs bg-blue-50 text-blue-600 rounded border border-blue-200">
            請在影像上點擊設置測量點。點擊後將自動繪製剖面線。
          </div>
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
      
      // 在測量模式下，保持 ImageViewer 為活動視圖以便互動
      analysisStore.setActiveViewer(sourceViewerId.value);
    };
    
    // 結束線性剖面測量
    const endLineProfileMeasurement = () => {
      if (!sourceViewerId.value) return;
      
      // 關閉源影像的測量模式
      analysisStore.toggleMeasureMode(sourceViewerId.value);
      
      // 修復：測量結束後，允許正常的視圖切換，不強制設置活動視圖
      // 讓用戶自然地點擊想要的視圖來切換活動狀態
      console.log('線性剖面測量已結束');
    };
    
    return {
      hasSourceViewer,
      sourceViewerTitle,
      isSourceViewerMeasuring,
      startLineProfileMeasurement,
      endLineProfileMeasurement
    };
  }
});
</script>