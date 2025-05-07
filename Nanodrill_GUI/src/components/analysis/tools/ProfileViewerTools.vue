<!-- src/components/analysis/tools/ProfileViewerTools.vue -->
<template>
  <div class="p-4 space-y-4">
    <h4 class="font-medium text-sm border-b pb-2 mb-2">剖面設定</h4>
    
    <!-- 來源信息顯示 -->
    <div v-if="hasSourceViewer" class="bg-gray-50 p-3 rounded border border-gray-200">
      <div class="text-sm text-gray-700">
        <span class="font-medium">來源影像:</span> {{ sourceViewerTitle }}
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

export default defineComponent({
  name: 'ProfileViewerTools',
  props: {
    viewer: {
      type: Object as PropType<Viewer>,
      required: true
    }
  },
  setup(props) {
    // 計算屬性
    const hasSourceViewer = computed(() => {
      return !!props.viewer.props.sourceViewerId;
    });
    
    const sourceViewerTitle = computed(() => {
      return props.viewer.props.sourceViewerTitle || '未知影像';
    });
    
    return {
      hasSourceViewer,
      sourceViewerTitle
    };
  }
});
</script>