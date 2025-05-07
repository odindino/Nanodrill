<!-- src/components/analysis/tools/ProfileViewerTools.vue -->
<template>
    <div class="p-4 space-y-4">
      <h4 class="font-medium text-sm border-b pb-2 mb-2">剖面設定</h4>
      
      <!-- 將最小值歸零選項 -->
      <div class="flex items-center">
        <input 
          type="checkbox" 
          id="shift-zero" 
          v-model="shiftZero"
          class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
          @change="updateSettings"
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
          @change="updateSettings"
        >
        <label for="auto-scale" class="ml-2 text-sm text-gray-700">
          自動縮放
        </label>
      </div>
      
      <!-- 顯示峰值點 -->
      <div class="flex items-center">
        <input 
          type="checkbox" 
          id="show-peaks" 
          v-model="showPeaks"
          class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
          @change="updateSettings"
        >
        <label for="show-peaks" class="ml-2 text-sm text-gray-700">
          顯示峰值點
        </label>
      </div>
      
      <!-- 測量新剖面按鈕 -->
      <div v-if="hasSourceViewer">
        <button 
          @click="measureNewProfile"
          class="w-full py-2 px-3 text-sm font-medium rounded bg-blue-100 text-blue-700 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 mb-4"
        >
          在來源圖像上測量新剖面
        </button>
      </div>
      
      <!-- 粗糙度分析（可選） -->
      <div v-if="hasProfileData">
        <h4 class="font-medium text-xs border-b pb-1 mb-2 text-gray-500">粗糙度分析</h4>
        <div class="bg-gray-50 p-3 rounded border border-gray-200 text-xs">
          <div class="grid grid-cols-2 gap-2">
            <div class="text-gray-600">
              <span class="font-medium">Ra:</span> {{ formatNumber(roughness?.Ra) }} {{ physUnit }}
            </div>
            <div class="text-gray-600">
              <span class="font-medium">Rq:</span> {{ formatNumber(roughness?.Rq) }} {{ physUnit }}
            </div>
            <div class="text-gray-600">
              <span class="font-medium">Rz:</span> {{ formatNumber(roughness?.Rz) }} {{ physUnit }}
            </div>
            <div class="text-gray-600">
              <span class="font-medium">長度:</span> {{ formatNumber(profileLength) }} {{ physUnit }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, computed, watch} from 'vue';
  import type { PropType } from 'vue';
  import { useSpmDataStore } from '../../../stores/spmDataStore';
  import type { Viewer } from '../../../stores/spmDataStore';
  
  export default defineComponent({
    name: 'ProfileViewerTools',
    props: {
      viewer: {
        type: Object as PropType<Viewer>,
        required: true
      }
    },
    emits: ['measure-new-profile'],
    setup(props, { emit }) {
      const spmDataStore = useSpmDataStore();
      
      // 剖面工具設置
      const shiftZero = ref(props.viewer.props.shiftZero || false);
      const autoScale = ref(props.viewer.props.autoScale !== undefined ? props.viewer.props.autoScale : true);
      const showPeaks = ref(props.viewer.props.showPeaks || false);
      
      // 計算屬性
      const hasSourceViewer = computed(() => {
        return !!props.viewer.props.sourceViewerId;
      });
      
      const hasProfileData = computed(() => {
        return !!props.viewer.props.profileData;
      });
      
      const roughness = computed(() => {
        return props.viewer.props.roughness;
      });
      
      const profileLength = computed(() => {
        return props.viewer.props.profileData?.length || 0;
      });
      
      const physUnit = computed(() => {
        return props.viewer.props.physUnit || 'nm';
      });
      
      // 當 viewer 變化時，更新工具設置
      watch(() => props.viewer, (newViewer) => {
        shiftZero.value = newViewer.props.shiftZero || false;
        autoScale.value = newViewer.props.autoScale !== undefined ? newViewer.props.autoScale : true;
        showPeaks.value = newViewer.props.showPeaks || false;
      }, { immediate: true });
      
      // 測量新剖面
      const measureNewProfile = () => {
        emit('measure-new-profile', {
          profileViewerId: props.viewer.id,
          sourceViewerId: props.viewer.props.sourceViewerId
        });
      };
      
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
                  shiftZero: shiftZero.value,
                  autoScale: autoScale.value,
                  showPeaks: showPeaks.value
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
      
      // 格式化數字
      const formatNumber = (value: number | undefined) => {
        if (value === undefined || value === null) return 'N/A';
        return value.toFixed(2);
      };
      
      return {
        shiftZero,
        autoScale,
        showPeaks,
        hasSourceViewer,
        hasProfileData,
        roughness,
        profileLength,
        physUnit,
        measureNewProfile,
        updateSettings,
        formatNumber
      };
    }
  });
  </script>