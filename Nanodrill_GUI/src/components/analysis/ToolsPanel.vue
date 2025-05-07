<!-- src/components/analysis/ToolsPanel.vue -->
<template>
  <div 
    class="sidebar-panel bg-white border-r border-gray-200 transition-all duration-300 flex flex-col mt-2"
    :class="showToolsPanel ? 'w-80' : 'w-12'"
  >
    <!-- 標題或迷你按鈕 -->
    <div 
      class="flex items-center p-2 border-b border-gray-200 bg-gray-50"
      :class="showToolsPanel ? 'justify-between' : 'justify-center'"
    >
      <h3 v-if="showToolsPanel" class="text-sm font-medium text-gray-700 truncate">工具列</h3>
      <button 
        @click="toggleToolsPanel"
        class="p-1.5 rounded hover:bg-gray-200 text-gray-600 focus:outline-none"
        :title="showToolsPanel ? '收起工具列' : '展開工具列'"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-5 w-5" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
          :class="{ 'transform rotate-180': showToolsPanel }"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
    </div>
    
    <!-- 工具列內容 -->
    <div v-if="showToolsPanel" class="flex-grow overflow-y-auto p-4">
      <template v-if="activeViewer">
        <div v-if="activeViewer.component === 'ImageViewer'" class="space-y-4">
          <h4 class="font-medium text-sm border-b pb-2 mb-2">影像處理</h4>
          
          <!-- 色彩映射 -->
          <div>
            <label class="text-xs text-gray-500 block mb-1">色彩映射</label>
            <select 
              v-model="colormap" 
              class="w-full text-sm border border-gray-300 rounded py-1.5 px-2 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
              @change="updateImageSettings"
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
              @change="updateImageSettings"
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
        
        <!-- 剖面視圖工具 -->
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
          
          <!-- 測量新剖面按鈕 -->
          <div v-if="activeViewer.props && activeViewer.props.sourceViewerId">
            <button 
              @click="measureNewProfile"
              class="w-full py-2 px-3 text-sm font-medium rounded bg-blue-100 text-blue-700 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 mb-4"
            >
              在來源圖像上測量新剖面
            </button>
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
    
    <!-- 迷你模式下只顯示圖標 -->
    <div v-else class="flex-grow flex flex-col items-center pt-3">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue';
import { useAnalysisStore } from '../../stores/analysisStore';
import { useSpmDataStore } from '../../stores/spmDataStore';

export default defineComponent({
  name: 'ToolsPanel',
  setup() {
    const analysisStore = useAnalysisStore();
    const spmDataStore = useSpmDataStore();
    
    const showToolsPanel = ref(true);
    
    // 圖像工具設置
    const colormap = ref('Oranges');
    const zScale = ref(1.0);
    
    // 剖面工具設置
    const shiftZero = ref(false);
    const autoScale = ref(true);
    
    // 獲取當前活動的視圖
    const activeViewer = computed(() => {
      const viewerId = analysisStore.activeViewerId;
      if (!viewerId) return null;
      
      // 查找擁有該視圖的標籤頁和群組
      for (const tab of spmDataStore.analysisTabs) {
        if (tab.viewerGroups) {
          for (const group of tab.viewerGroups) {
            const viewer = group.viewers.find(v => v.id === viewerId);
            if (viewer) {
              return viewer;
            }
          }
        }
      }
      
      return null;
    });
    
    // 切換工具面板
    const toggleToolsPanel = () => {
      showToolsPanel.value = !showToolsPanel.value;
    };
    
    // 更新圖像設置
    const updateImageSettings = () => {
      if (!activeViewer.value || activeViewer.value.component !== 'ImageViewer') return;
      
      const viewerId = activeViewer.value.id;
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
    
    // 更新剖面圖設置
    const updateProfileSettings = () => {
      if (!activeViewer.value || activeViewer.value.component !== 'ProfileViewer') return;
      
      const viewerId = activeViewer.value.id;
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
                shiftZero: shiftZero.value,
                autoScale: autoScale.value
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
    
    // 建立線性剖面
    const createLineProfile = () => {
      if (!activeViewer.value || activeViewer.value.component !== 'ImageViewer') return;
      
      const sourceViewerId = activeViewer.value.id;
      const location = spmDataStore.getViewerLocation(sourceViewerId);
      
      if (!location) return;
      
      // 創建新的 ProfileViewer
      const profileViewerId = `viewer-profile-${Date.now()}`;
      const profileViewer = {
        id: profileViewerId,
        component: 'ProfileViewer',
        props: {
          id: profileViewerId,
          title: '線性剖面',
          physUnit: activeViewer.value.props.physUnit || 'nm',
          isActive: true,
          showStats: true,
          sourceViewerId: sourceViewerId,
          sourceViewerTitle: activeViewer.value.props.title || 'Image'
        }
      };
      
      // 找到標籤頁和群組
      const tab = spmDataStore.analysisTabs.find(t => t.id === location.tabId);
      if (tab && tab.viewerGroups) {
        const group = tab.viewerGroups.find(g => g.id === location.groupId);
        
        if (group) {
          // 將所有視圖設為非活動
          const updatedViewers = group.viewers.map(viewer => ({
            ...viewer,
            props: {
              ...viewer.props,
              isActive: false
            }
          }));
          
          // 添加新的剖面視圖
          updatedViewers.push(profileViewer);
          
          // 更新標籤頁
          const updatedGroups = [...tab.viewerGroups];
          const groupIndex = updatedGroups.indexOf(group);
          
          updatedGroups[groupIndex] = {
            ...group,
            viewers: updatedViewers
          };
          
          spmDataStore.updateAnalysisTabData(tab.id, {
            viewerGroups: updatedGroups
          });
          
          // 更新活動視圖
          analysisStore.setActiveViewer(profileViewerId);
          
          // 開始測量模式
          analysisStore.toggleMeasureMode();
          
          // 更新圖像視圖的測量模式
          updateImageViewerMeasureMode(sourceViewerId, true, profileViewerId);
        }
      }
    };
    
    // 測量新剖面
    const measureNewProfile = () => {
      if (!activeViewer.value || activeViewer.value.component !== 'ProfileViewer' || !activeViewer.value.props.sourceViewerId) return;
      
      const sourceViewerId = activeViewer.value.props.sourceViewerId;
      const profileViewerId = activeViewer.value.id;
      
      // 開始測量模式
      analysisStore.toggleMeasureMode();
      
      // 更新圖像視圖的測量模式
      updateImageViewerMeasureMode(sourceViewerId, true, profileViewerId);
      
      // 激活源圖像視圖
      analysisStore.setActiveViewer(sourceViewerId);
    };
    
    // 更新圖像視圖的測量模式
    const updateImageViewerMeasureMode = (viewerId: string, mode: boolean, targetProfileViewerId: string | null = null) => {
      const location = spmDataStore.getViewerLocation(viewerId);
      
      if (!location) return;
      
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
              profileMeasureMode: mode,
              targetProfileViewer: mode && targetProfileViewerId ? {
                id: targetProfileViewerId
              } : null
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
    };
    
    // 當活動視圖變化時，更新工具設置
    watch(() => activeViewer.value, (newViewer) => {
      if (newViewer) {
        // 根據視圖類型更新工具設置
        if (newViewer.component === 'ImageViewer') {
          colormap.value = newViewer.props.colormap || 'Oranges';
          zScale.value = newViewer.props.zScale || 1.0;
        } else if (newViewer.component === 'ProfileViewer') {
          shiftZero.value = newViewer.props.shiftZero || false;
          autoScale.value = newViewer.props.autoScale !== undefined ? newViewer.props.autoScale : true;
        }
      }
    }, { immediate: true });
    
    // 監聽測量模式變化
    watch(() => analysisStore.measureMode, (newMode) => {
      // 測量模式關閉時，更新所有ImageViewer
      if (!newMode) {
        analysisStore.updateAllImageViewersMeasureMode(false);
      }
    });
    
    return {
      showToolsPanel,
      activeViewer,
      colormap,
      zScale,
      shiftZero,
      autoScale,
      toggleToolsPanel,
      updateImageSettings,
      updateProfileSettings,
      createLineProfile,
      measureNewProfile
    };
  }
});
</script>

<style scoped>
/* 側邊面板高度設置 */
.sidebar-panel {
  max-height: calc(50vh - 30px);
  min-height: 200px;
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