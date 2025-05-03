<!-- src/components/AnalysisView.vue -->
<template>
  <div class="h-full flex flex-col bg-white rounded-lg shadow overflow-hidden">
    <!-- 沒有標籤頁時的歡迎畫面 -->
    <div v-if="analysisTabs.length === 0" class="flex flex-col items-center justify-center h-full p-6 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <p class="text-gray-500 mb-4">尚未開啟任何分析標籤頁</p>
      <p class="text-gray-500 text-sm">請在檔案選擇器中雙擊檔案或使用"分析"按鈕開始進行分析</p>
    </div>

    <!-- 有標籤頁時的分析介面 -->
    <div v-else class="h-full flex">
      <AnalysisTabs
        :tabs="analysisTabs"
        :active-tab-id="activeTabId"
        @tab-switched="switchTab"
        @tab-closed="closeTab"
        @tab-added="addTab"
        @tab-updated="updateTab"
        @group-to-tab="handleGroupToTab"
        @create-line-profile="createLineProfile"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue';
import { useSpmDataStore } from '../stores/spmDataStore';
import AnalysisTabs from './analysis/AnalysisTabs.vue';
import ImageViewer from './analysis/ImageViewer.vue';
import ProfileViewer from './analysis/ProfileViewer.vue';

export default defineComponent({
  name: 'AnalysisView',
  components: {
    AnalysisTabs,
    ImageViewer,
    ProfileViewer
  },
  setup() {
    const spmDataStore = useSpmDataStore();
    
    // 分析標籤頁
    const analysisTabs = ref<any[]>([]);
    
    // 活動標籤頁ID
    const activeTabId = ref('');
    
    // 從 spmDataStore 獲取分析標籤頁
    const initializeFromStore = () => {
      if (spmDataStore.analysisTabs && spmDataStore.analysisTabs.length > 0) {
        // 轉換存儲中的標籤頁到新格式
        analysisTabs.value = spmDataStore.analysisTabs.map(tab => {
          // 創建視圖群組
          const viewerGroups = [];
          
          // 如果有圖像數據，創建一個包含圖像視圖的群組
          if (tab.imageData) {
            const groupId = `group-${tab.id}-${Date.now()}`;
            const imageViewer = {
              id: `viewer-image-${tab.id}`,
              component: 'ImageViewer',
              props: {
                imageData: tab.imageData,
                title: tab.currentFileName || tab.title,
                imageType: tab.fileType,
                physUnit: tab.physUnit || 'nm',
                colormap: tab.colormap || 'Oranges',
                zScale: tab.zScale || 1.0,
                stats: tab.statistics || null,
                dimensions: tab.dimensions || { width: 0, height: 0, xRange: 0, yRange: 0 }
              }
            };
            
            viewerGroups.push({
              id: groupId,
              title: tab.title,
              viewers: [imageViewer],
              layout: 'horizontal'
            });
          }
          
          return {
            id: tab.id,
            title: tab.title,
            viewerGroups: viewerGroups
          };
        });
        
        // 設定活動標籤頁
        if (spmDataStore.activeAnalysisTabId) {
          activeTabId.value = spmDataStore.activeAnalysisTabId;
        } else if (analysisTabs.value.length > 0) {
          activeTabId.value = analysisTabs.value[0].id;
        }
      }
    };
    
    // 切換標籤頁
    const switchTab = (tabId: string) => {
      activeTabId.value = tabId;
      spmDataStore.setActiveAnalysisTab(tabId);
    };
    
    // 關閉標籤頁
    const closeTab = (tabId: string) => {
      // 從本地狀態移除
      const tabIndex = analysisTabs.value.findIndex(tab => tab.id === tabId);
      if (tabIndex !== -1) {
        analysisTabs.value.splice(tabIndex, 1);
      }
      
      // 從 store 中移除
      spmDataStore.removeAnalysisTab(tabId);
      
      // 如果關閉的是當前標籤頁，切換到其他標籤頁
      if (activeTabId.value === tabId) {
        if (analysisTabs.value.length > 0) {
          const newTabId = analysisTabs.value[0].id;
          activeTabId.value = newTabId;
          spmDataStore.setActiveAnalysisTab(newTabId);
        } else {
          activeTabId.value = '';
        }
      }
    };
    
    // 添加標籤頁
    const addTab = (tab: any) => {
      analysisTabs.value.push(tab);
      
      // 切換到新標籤頁
      activeTabId.value = tab.id;
    };
    
    // 更新標籤頁
    const updateTab = ({ id, changes }: { id: string, changes: any }) => {
      const tabIndex = analysisTabs.value.findIndex(tab => tab.id === id);
      if (tabIndex !== -1) {
        analysisTabs.value[tabIndex] = {
          ...analysisTabs.value[tabIndex],
          ...changes
        };
      }
    };
    
    // 處理群組轉換為標籤頁
    const handleGroupToTab = (groupData: any) => {
      console.log('群組轉換為標籤頁:', groupData);
      // 實現群組轉換為標籤頁的邏輯
    };
    
    // 創建線性剖面
    const createLineProfile = async ({ sourceViewerId, groupId }: { sourceViewerId: string, groupId: string }) => {
      // 找到對應的標籤頁和群組
      const activeTab = analysisTabs.value.find(tab => tab.id === activeTabId.value);
      if (!activeTab) return;
      
      const group = activeTab.viewerGroups.find((g: any) => g.id === groupId);
      if (!group) return;
      
      // 找到源視圖
      const sourceViewerIndex = group.viewers.findIndex((v: any) => v.id === sourceViewerId);
      if (sourceViewerIndex === -1) return;
      
      const sourceViewer = group.viewers[sourceViewerIndex];
      
      try {
        // 啟用源視圖的線性剖面模式
        console.log('啟用源視圖的線性剖面模式');
        
        // 假設已經通過其他方式獲取了剖面數據和圖像
        // 這裡應該調用後端API
        const profileData = {
          distance: [0, 1, 2, 3, 4, 5],
          height: [0, 1, 0.5, 1.5, 1, 0],
          length: 5,
          stats: { min: 0, max: 1.5, mean: 0.75 }
        };
        
        const roughness = {
          Ra: 0.5,
          Rq: 0.6,
          Rz: 1.5,
          Rsk: 0.1,
          Rku: 3.0
        };
        
        // 創建剖面視圖
        const profileViewer = {
          id: `viewer-profile-${Date.now()}`,
          component: 'ProfileViewer',
          props: {
            title: 'Profile: ' + sourceViewer.props.title,
            profileData,
            roughness,
            physUnit: sourceViewer.props.physUnit || 'nm'
          }
        };
        
        // 如果群組中已有兩個視圖，創建新的群組
        if (group.viewers.length >= 2) {
          const newGroupId = `group-${activeTab.id}-${Date.now()}`;
          activeTab.viewerGroups.push({
            id: newGroupId,
            title: 'Profile Group',
            viewers: [profileViewer],
            layout: 'horizontal'
          });
        } else {
          // 否則添加到當前群組
          group.viewers.push(profileViewer);
        }
        
        // 更新標籤頁
        updateTab({
          id: activeTab.id,
          changes: { viewerGroups: activeTab.viewerGroups }
        });
      } catch (error) {
        console.error('創建線性剖面失敗:', error);
      }
    };
    
    // 生命週期鉤子
    onMounted(() => {
      // 初始化標籤頁
      initializeFromStore();
      
      // 監聽 spmDataStore 中的標籤頁變化
      watch(() => spmDataStore.analysisTabs, () => {
        initializeFromStore();
      }, { deep: true });
      
      // 監聽 spmDataStore 中的活動標籤頁變化
      watch(() => spmDataStore.activeAnalysisTabId, (newTabId) => {
        if (newTabId) {
          activeTabId.value = newTabId;
        }
      });
    });
    
    return {
      analysisTabs,
      activeTabId,
      switchTab,
      closeTab,
      addTab,
      updateTab,
      handleGroupToTab,
      createLineProfile
    };
  }
});
</script>