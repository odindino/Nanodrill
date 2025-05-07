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
      >
        建立線性剖面
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
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
    
    // 創建線性剖面
    const createLineProfile = () => {
      // 使用 analysisStore 中的方法創建線性剖面
      analysisStore.createLineProfile(props.viewer.id);
    };
    
    return {
      createLineProfile
    };
  }
});
</script>