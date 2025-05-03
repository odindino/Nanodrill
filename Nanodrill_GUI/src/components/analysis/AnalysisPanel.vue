<!-- src/components/analysis/AnalysisPanel.vue -->
<template>
  <div 
    class="analysis-panel h-full w-full flex flex-col bg-gray-50 overflow-auto relative"
    @dragover.prevent="handleDragOver"
    @drop.prevent="handleDrop"
    @dragleave.prevent="handleDragLeave"
  >
    <!-- 拖拽疊放區指示 -->
    <div v-if="isDragOver" 
         class="absolute inset-0 bg-blue-100 bg-opacity-50 border-2 border-dashed border-blue-400 z-10 flex items-center justify-center">
      <p class="text-blue-600 font-medium">釋放以添加到分析面板</p>
    </div>
    
    <!-- 無內容提示 -->
    <div v-if="viewerGroups.length === 0" class="h-full flex flex-col items-center justify-center p-8">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-gray-500 mb-4">此分析面板尚無內容</p>
      <p class="text-sm text-gray-400">從標籤欄拖曳標籤頁到此處，或開啟新的影像</p>
    </div>
    
    <!-- 視圖群組容器 -->
    <div v-else class="p-4 space-y-4">
      <ViewerGroup 
        v-for="group in viewerGroups" 
        :key="group.id" 
        :id="group.id"
        :title="group.title"
        :viewers="group.viewers"
        :layout="group.layout"
        :is-active="activeGroupId === group.id"
        :group-height="group.height || 400"
        @activate="activateGroup"
        @activate-viewer="handleViewerActivated"
        @remove-viewer="handleViewerRemoved"
        @close="removeGroup"
        @layout-change="updateGroupLayout"
        @convert-to-tab="convertGroupToTab"
        @drag-start="handleGroupDragStart"
        @drag-move="handleGroupDragMove"
        @drag-end="handleGroupDragEnd"
        @resize="handleGroupResize"
      />
    </div>
    
    <!-- 右側工具面板 -->
    <div 
      class="tools-panel absolute right-0 top-0 h-full bg-white shadow-lg transition-all z-20 overflow-hidden"
      :class="{ 'w-0': !showToolsPanel, 'w-64': showToolsPanel }"
    >
      <div class="h-full flex flex-col">
        <!-- 工具面板標題 -->
        <div class="px-4 py-3 bg-gray-100 border-b border-gray-200 flex items-center justify-between">
          <h3 class="font-medium text-gray-700">分析工具</h3>
          <button 
            @click="toggleToolsPanel"
            class="p-1 rounded hover:bg-gray-200 text-gray-500 focus:outline-none"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- 工具面板內容 -->
        <div class="flex-grow overflow-y-auto p-4">
          <template v-if="activeViewer">
            <div v-if="activeViewer.component === 'ImageViewer'" class="space-y-4">
              <h4 class="font-medium text-sm border-b pb-2 mb-2">影像處理</h4>
              
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
              
              <!-- 色彩映射 -->
              <div>
                <label class="text-xs text-gray-500 block mb-1">色彩映射</label>
                <select 
                  v-model="colormap" 
                  class="w-full text-sm border border-gray-300 rounded py-1.5 px-2 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
                  @change="updateViewerSettings({ colormap })"
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
                  @change="updateViewerSettings({ zScale })"
                >
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
            
            <div v-else-if="activeViewer.component === 'ProfileViewer'" class="space-y-4">
              <h4 class="font-medium text-sm border-b pb-2 mb-2">剖面設定</h4>
              
              <!-- 將最小值歸零選項 -->
              <div class="flex items-center">
                <input 
                  type="checkbox" 
                  id="shift-zero" 
                  v-model="shiftZero"
                  class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                  @change="updateProfileSettings"
                >
                <label for="shift-zero" class="ml-2 text-sm text-gray-700">
                  將最小值歸零
                </label>
              </div>
              
              <!-- 自動縮放選項 -->
              <div class="flex items-center">
                <input 
                  type="checkbox" 
                  id="auto-scale" 
                  v-model="autoScale"
                  class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                  @change="updateProfileSettings"
                >
                <label for="auto-scale" class="ml-2 text-sm text-gray-700">
                  自動縮放
                </label>
              </div>
            </div>
            
            <div v-else class="p-4 text-center text-gray-500">
              <p>無可用工具</p>
            </div>
          </template>
          
          <div v-else class="p-4 text-center text-gray-500">
            <p>請選擇一個視圖來顯示相應工具</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 工具面板切換按鈕 -->
    <button 
      v-if="!showToolsPanel"
      @click="toggleToolsPanel"
      class="fixed right-4 top-4 p-2 bg-white rounded-full shadow-md text-gray-600 hover:bg-gray-100 focus:outline-none z-20"
      title="顯示工具面板"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import type { PropType } from 'vue';
import ViewerGroup from './ViewerGroup.vue';
import type { Viewer } from './ViewerGroup.vue';

// 視圖群組接口
interface ViewerGroupData {
  id: string;
  title: string;
  viewers: Viewer[];
  layout: 'horizontal' | 'vertical';
  height?: number;
}

export default defineComponent({
  name: 'AnalysisPanel',
  components: {
    ViewerGroup
  },
  props: {
    viewerGroups: {
      type: Array as PropType<ViewerGroupData[]>,
      default: () => []
    },
    activeGroupId: {
      type: String,
      default: ''
    }
  },
  emits: [
    'group-updated',
    'group-removed',
    'viewer-removed',
    'active-group-changed',
    'active-viewer-changed',
    'convert-group-to-tab',
    'drop',
    'create-line-profile'
  ],
  setup(props, { emit }) {
    // 拖放相關狀態
    const isDragOver = ref(false);
    
    // 工具面板相關狀態
    const showToolsPanel = ref(false);
    
    // 影像處理相關設置
    const colormap = ref('Oranges');
    const zScale = ref(1.0);
    
    // 剖面圖相關設置
    const shiftZero = ref(false);
    const autoScale = ref(true);
    
    // 計算當前活動的視圖
    const activeViewer = computed(() => {
      if (!props.activeGroupId) return null;
      
      const activeGroup = props.viewerGroups.find(group => group.id === props.activeGroupId);
      if (!activeGroup || activeGroup.viewers.length === 0) return null;
      
      // 找出被標記為活動的視圖，或默認取第一個
      for (const viewer of activeGroup.viewers) {
        if (viewer.props && viewer.props.isActive) {
          return viewer;
        }
      }
      
      return activeGroup.viewers[0];
    });
    
    // 激活群組
    const activateGroup = (groupId: string) => {
      emit('active-group-changed', groupId);
    };
    
    // 處理視圖激活
    const handleViewerActivated = ({ groupId, viewerIndex, viewerId }: any) => {
      emit('active-viewer-changed', { groupId, viewerIndex, viewerId });
    };
    
    // 處理視圖移除
    const handleViewerRemoved = ({ groupId, viewerIndex, viewerId }: any) => {
      emit('viewer-removed', { groupId, viewerIndex, viewerId });
    };
    
    // 移除群組
    const removeGroup = (groupId: string) => {
      emit('group-removed', groupId);
    };
    
    // 更新群組布局
    const updateGroupLayout = ({ groupId, layout }: { groupId: string, layout: 'horizontal' | 'vertical' }) => {
      emit('group-updated', { id: groupId, changes: { layout } });
    };
    
    // 處理群組大小調整
    const handleGroupResize = ({ groupId, layout, sizes }: any) => {
      // 可以發送事件或直接更新本地狀態
    };
    
    // 將群組轉換為標籤頁
    const convertGroupToTab = (groupId: string) => {
      emit('convert-group-to-tab', groupId);
    };
    
    // 處理群組拖動開始
    const handleGroupDragStart = ({ groupId, event }: any) => {
      // 處理拖動開始邏輯
    };
    
    // 處理群組拖動移動
    const handleGroupDragMove = ({ groupId, event, delta }: any) => {
      // 處理拖動移動邏輯
    };
    
    // 處理群組拖動結束
    const handleGroupDragEnd = ({ groupId, event }: any) => {
      // 處理拖動結束邏輯
    };
    
    // 處理拖動經過
    const handleDragOver = (event: DragEvent) => {
      isDragOver.value = true;
    };
    
    // 處理拖動離開
    const handleDragLeave = (event: DragEvent) => {
      isDragOver.value = false;
    };
    
    // 處理拖放
    const handleDrop = (event: DragEvent) => {
      isDragOver.value = false;
      
      // 獲取拖放數據
      const data = event.dataTransfer?.getData('application/json');
      if (!data) return;
      
      try {
        const dropData = JSON.parse(data);
        emit('drop', { dropData, event });
      } catch (error) {
        console.error('無法解析拖放數據:', error);
      }
    };
    
    // 切換工具面板
    const toggleToolsPanel = () => {
      showToolsPanel.value = !showToolsPanel.value;
    };
    
    // 更新視圖設置
    const updateViewerSettings = (settings: any) => {
      if (!props.activeGroupId || !activeViewer.value) return;
      
      const groupIndex = props.viewerGroups.findIndex(group => group.id === props.activeGroupId);
      if (groupIndex === -1) return;
      
      const viewerIndex = props.viewerGroups[groupIndex].viewers.findIndex(
        viewer => viewer === activeViewer.value
      );
      if (viewerIndex === -1) return;
      
      // 發送更新事件
      emit('group-updated', {
        id: props.activeGroupId,
        changes: {
          viewers: props.viewerGroups[groupIndex].viewers.map((viewer, idx) => {
            if (idx === viewerIndex) {
              return {
                ...viewer,
                props: {
                  ...viewer.props,
                  ...settings
                }
              };
            }
            return viewer;
          })
        }
      });
    };
    
    // 更新剖面圖設置
    const updateProfileSettings = () => {
      updateViewerSettings({
        shiftZero: shiftZero.value,
        autoScale: autoScale.value
      });
    };
    
    // 應用平面化處理
    const applyFlatten = (method: string) => {
      if (!activeViewer.value || activeViewer.value.component !== 'ImageViewer') return;
      
      // 這裡應該調用後端API或數據處理函數
      console.log('應用平面化處理:', method);
    };
    
    // 創建線性剖面
    const createLineProfile = () => {
      if (!activeViewer.value || activeViewer.value.component !== 'ImageViewer') return;
      
      emit('create-line-profile', {
        sourceViewerId: activeViewer.value.id,
        groupId: props.activeGroupId
      });
    };
    
    return {
      isDragOver,
      showToolsPanel,
      activeViewer,
      colormap,
      zScale,
      shiftZero,
      autoScale,
      activateGroup,
      handleViewerActivated,
      handleViewerRemoved,
      removeGroup,
      updateGroupLayout,
      handleGroupResize,
      convertGroupToTab,
      handleGroupDragStart,
      handleGroupDragMove,
      handleGroupDragEnd,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      toggleToolsPanel,
      updateViewerSettings,
      applyFlatten,
      createLineProfile,
      updateProfileSettings
    };
  }
});
</script>

<style scoped>
/* 自定義滾動條 */
.analysis-panel {
  scrollbar-width: thin;
  scrollbar-color: #ddd #f1f1f1;
}

.analysis-panel::-webkit-scrollbar {
  width: 8px;
}

.analysis-panel::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.analysis-panel::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 4px;
}

.analysis-panel::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}

/* 工具面板過渡動畫 */
.tools-panel {
  transition: width 0.3s ease-in-out;
}

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