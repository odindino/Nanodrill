<!-- src/components/AnalysisView.vue -->
<template>
  <div class="h-full flex flex-col bg-white rounded-lg shadow overflow-hidden relative">
    <!-- 沒有標籤頁時的歡迎畫面 -->
    <div v-if="analysisTabs.length === 0" class="flex flex-col items-center justify-center h-full p-6 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <p class="text-gray-500 mb-4">尚未開啟任何分析標籤頁</p>
      <p class="text-gray-500 text-sm">請在檔案選擇器中雙擊檔案或使用"分析"按鈕開始進行分析</p>
    </div>

    <!-- 有標籤頁時的分析介面 -->
    <div v-else class="h-full flex relative">
      <!-- 左側面板區域 -->
      <div class="h-full flex flex-col">
        <!-- 檔案選擇器面板 -->
        <FileSelectorPanel 
          :active-tab="activeTab" 
          :is-loading="isLoading"
          @toggle-selector="showFileSelector = $event"
          @load-file="loadSelectedFile"
        />
        
        <!-- 工具列面板 -->
        <ToolsPanel
          :active-viewer="activeViewer"
          :linked-profiles="getLinkedProfiles()"
          @toggle-panel="showToolsPanel = $event"
          @create-line-profile="createLineProfile"
          @measure-new-profile="handleMeasureNewProfile"
        />
      </div>
      
      <!-- 主要分析標籤頁區域 -->
      <div class="flex-1 h-full">
        <AnalysisTabs
          :tabs="analysisTabs"
          :active-tab-id="activeTabId"
          @tab-switched="switchTab"
          @tab-closed="closeTab"
          @tab-added="addTab"
          @tab-updated="updateTab"
          @viewer-activated="handleViewerActivated"
          @create-line-profile="createLineProfile"
        />
      </div>

      <!-- 載入中顯示 -->
      <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20 z-50">
        <div class="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
          <div class="w-12 h-12 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-4"></div>
          <p class="text-gray-600">正在載入資料...</p>
        </div>
      </div>

      <!-- 錯誤提示 -->
      <div v-if="errorMessage" 
           class="absolute top-4 right-4 max-w-md p-4 bg-red-50 border-l-4 border-red-400 text-red-700 z-50 rounded shadow-md">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm">{{ errorMessage }}</p>
          </div>
          <div class="ml-auto pl-3">
            <button @click="clearError" class="text-red-400 hover:text-red-500 focus:outline-none">
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue';
import { useSpmDataStore } from '../stores/spmDataStore';
import { useAnalysisStore } from '../stores/analysisStore';
import AnalysisTabs from './analysis/AnalysisTabs.vue';
import FileSelectorPanel from './analysis/FileSelectorPanel.vue';
import ToolsPanel from './analysis/ToolsPanel.vue';

// 定義關聯剖面接口
interface LinkedProfile {
  id: string;
  title: string;
  viewerId: string;
}

export default defineComponent({
  name: 'AnalysisView',
  components: {
    AnalysisTabs,
    FileSelectorPanel,
    ToolsPanel
  },
  setup() {
    const spmDataStore = useSpmDataStore();
    const analysisStore = useAnalysisStore();
    
    // 側邊面板狀態
    const showFileSelector = ref(true);
    const showToolsPanel = ref(true);
    
    // 取得資料
    const analysisTabs = computed(() => spmDataStore.analysisTabs);
    const activeTabId = computed(() => spmDataStore.activeAnalysisTabId);
    const activeTab = computed(() => {
      return analysisTabs.value.find(tab => tab.id === activeTabId.value) || null;
    });
    
    // 當前活動的視圖和視圖群組
    const activeGroupInfo = ref<{ groupId: string, viewerIndex: number, viewerId: string, viewerComponent: string } | null>(null);
    
    // 基於活動群組信息計算當前活動的視圖
    const activeViewer = computed(() => {
      if (!activeTab.value || !activeTab.value.viewerGroups || !activeGroupInfo.value) return null;
      
      // 尋找活動群組
      const group = activeTab.value.viewerGroups.find(group => group.id === activeGroupInfo.value?.groupId);
      if (!group) return null;
      
      // 返回活動視圖
      return group.viewers[activeGroupInfo.value.viewerIndex] || null;
    });
    
    // 從 analysisStore 獲取狀態
    const isLoading = computed(() => analysisStore.isLoading);
    const errorMessage = computed(() => analysisStore.errorMessage);
    const measureMode = computed(() => analysisStore.measureMode);
    
    // 清除錯誤消息
    const clearError = () => {
      analysisStore.clearError();
    };
    
    // 剖面關聯映射
    // key: ImageViewer ID, value: ProfileViewer ID 數組
    const profileAssociations = ref<Map<string, string[]>>(new Map());
    
    // 獲取與當前活動視圖關聯的剖面視圖
    const getLinkedProfiles = (): LinkedProfile[] => {
      if (!activeViewer.value || activeViewer.value.component !== 'ImageViewer') {
        return [];
      }
      
      const sourceViewerId = activeViewer.value.id;
      const linkedProfileIds = profileAssociations.value.get(sourceViewerId) || [];
      
      const profiles: LinkedProfile[] = [];
      
      // 尋找所有關聯的剖面視圖
      if (activeTab.value && activeTab.value.viewerGroups) {
        for (const group of activeTab.value.viewerGroups) {
          for (const viewer of group.viewers) {
            if (viewer.component === 'ProfileViewer' && linkedProfileIds.includes(viewer.id)) {
              profiles.push({
                id: viewer.id,
                title: viewer.props.title || 'Profile Viewer',
                viewerId: viewer.id
              });
            }
          }
        }
      }
      
      return profiles;
    };
    
    // 處理視圖啟用
    const handleViewerActivated = (data: any) => {
      console.log('AnalysisView 收到視圖啟用事件:', data);
      
      // 更新當前活動的視圖信息
      activeGroupInfo.value = {
        groupId: data.groupId,
        viewerIndex: data.viewerIndex,
        viewerId: data.viewerId,
        viewerComponent: data.viewerComponent
      };
      
      console.log('活動視圖已更新:', activeViewer.value);
    };
    
    // 切換標籤頁
    const switchTab = (tabId: string) => {
      spmDataStore.setActiveAnalysisTab(tabId);
      
      // 尋找活動的視圖群組和視圖
      const tab = analysisTabs.value.find(tab => tab.id === tabId);
      if (tab && tab.viewerGroups && tab.viewerGroups.length > 0) {
        // 尋找第一個有活動視圖的群組
        for (const group of tab.viewerGroups) {
          const activeViewerIndex = group.viewers.findIndex(viewer => viewer.props && viewer.props.isActive);
          if (activeViewerIndex !== -1) {
            // 找到活動視圖
            activeGroupInfo.value = {
              groupId: group.id,
              viewerIndex: activeViewerIndex,
              viewerId: group.viewers[activeViewerIndex].id,
              viewerComponent: group.viewers[activeViewerIndex].component
            };
            break;
          }
        }
        
        // 如果沒有找到活動視圖，設置第一個群組的第一個視圖為活動
        if (!activeGroupInfo.value) {
          const firstGroup = tab.viewerGroups[0];
          if (firstGroup.viewers.length > 0) {
            activeGroupInfo.value = {
              groupId: firstGroup.id,
              viewerIndex: 0,
              viewerId: firstGroup.viewers[0].id,
              viewerComponent: firstGroup.viewers[0].component
            };
          }
        }
      } else {
        // 清空活動視圖信息
        activeGroupInfo.value = null;
      }
    };
    
    // 關閉標籤頁
    const closeTab = (tabId: string) => {
      spmDataStore.removeAnalysisTab(tabId);
      
      // 如果關閉的是當前標籤頁，清空活動視圖信息
      if (tabId === activeTabId.value) {
        activeGroupInfo.value = null;
      }
    };
    
    // 添加標籤頁
    const addTab = (tab: any) => {
      // 實作添加標籤頁的邏輯
      console.log('添加標籤頁:', tab);
      // 如果需要，將tab添加到spmDataStore
    };
    
    // 更新標籤頁
    const updateTab = ({ id, changes }: { id: string, changes: any }) => {
      console.log('更新標籤頁:', id, changes);
      spmDataStore.updateAnalysisTabData(id, changes);
    };
    
    // 載入選中檔案
    const loadSelectedFile = async ({ selectedFileId, activeTabId }: { selectedFileId: string, activeTabId: string }) => {
      console.log('loadSelectedFile called with:', selectedFileId, activeTabId);
      if (!selectedFileId || !activeTab.value) return;
      
      // 使用 analysisStore 載入文件
      analysisStore.selectFile(selectedFileId, '');
      await analysisStore.loadSelectedFile();
      
      // 如果載入成功，更新標籤頁
      if (analysisStore.imageRawData && !errorMessage.value) {
        try {
          // 獲取檔案名稱
          const fileName = selectedFileId.split(/[\/\\]/).pop() || '';
          
          // 創建新的視圖群組
          const groupId = `group-${activeTab.value.id}-${Date.now()}`;
          const imageViewer = {
            id: `viewer-image-${Date.now()}`,
            component: 'ImageViewer',
            props: {
              id: `viewer-image-${Date.now()}`,
              imageData: analysisStore.imageData,
              imageRawData: analysisStore.imageRawData,
              title: fileName,
              imageType: 'topo',
              physUnit: analysisStore.physUnit || 'nm',
              colormap: 'Oranges',
              zScale: 1.0,
              stats: null, // 簡化，移除統計數據
              dimensions: analysisStore.dimensions,
              isActive: true,
              profileMeasureMode: false
            }
          };
          
          // 如果標籤頁尚未有視圖群組，添加一個新的
          if (!activeTab.value.viewerGroups || activeTab.value.viewerGroups.length === 0) {
            const viewerGroup = {
              id: groupId,
              title: fileName,
              viewers: [imageViewer],
              layout: 'horizontal'
            };
            
            spmDataStore.updateAnalysisTabData(activeTabId, {
              viewerGroups: [viewerGroup]
            });
            
            // 更新活動視圖信息
            activeGroupInfo.value = {
              groupId: groupId,
              viewerIndex: 0,
              viewerId: imageViewer.id,
              viewerComponent: 'ImageViewer'
            };
          } else {
            // 如果已經有視圖群組，添加到第一個群組
            const updatedGroups = [...activeTab.value.viewerGroups];
            
            // 將所有視圖設為非活動
            updatedGroups[0].viewers = updatedGroups[0].viewers.map(viewer => ({
              ...viewer,
              props: {
                ...viewer.props,
                isActive: false
              }
            }));
            
            // 添加新視圖
            updatedGroups[0].viewers.push(imageViewer);
            
            spmDataStore.updateAnalysisTabData(activeTabId, {
              viewerGroups: updatedGroups
            });
            
            // 更新活動視圖信息
            activeGroupInfo.value = {
              groupId: updatedGroups[0].id,
              viewerIndex: updatedGroups[0].viewers.length - 1,
              viewerId: imageViewer.id,
              viewerComponent: 'ImageViewer'
            };
          }
        } catch (error) {
          console.error('更新標籤頁數據時出錯:', error);
        }
      }
    };
    
    // 創建線性剖面
    const createLineProfile = () => {
      if (!activeTab.value) {
        console.error('無活動標籤頁');
        return;
      }
      
      // 找出當前活動的視圖群組
      const activeGroup = activeTab.value.viewerGroups.find(group => group.id === activeGroupInfo.value?.groupId);
      if (!activeGroup) {
        console.error('找不到活動視圖群組');
        return;
      }
      
      // 找出當前活動的 ImageViewer
      const sourceViewerIndex = activeGroupInfo.value?.viewerIndex || 0;
      const sourceViewer = activeGroup.viewers[sourceViewerIndex];
      
      if (!sourceViewer || sourceViewer.component !== 'ImageViewer') {
        console.error('找不到有效的源圖像視圖');
        return;
      }
      
      // 創建新的 ProfileViewer
      const profileViewerId = `viewer-profile-${Date.now()}`;
      const profileViewer = {
        id: profileViewerId,
        component: 'ProfileViewer',
        props: {
          id: profileViewerId,
          title: '線性剖面',
          physUnit: sourceViewer.props.physUnit || 'nm',
          isActive: true,
          showStats: true,
          isMeasuring: false,
          sourceViewerId: sourceViewer.id,
          sourceViewerTitle: sourceViewer.props.title || 'Image'
        }
      };
      
      // 將所有視圖設為非活動
      const updatedViewers = activeGroup.viewers.map(viewer => ({
        ...viewer,
        props: {
          ...viewer.props,
          isActive: false
        }
      }));
      
      // 添加新的剖面視圖
      updatedViewers.push(profileViewer);
      
      // 更新視圖群組
      const updatedGroups = [...activeTab.value.viewerGroups];
      const groupIndex = updatedGroups.findIndex(group => group.id === activeGroup.id);
      
      if (groupIndex !== -1) {
        updatedGroups[groupIndex] = {
          ...activeGroup,
          viewers: updatedViewers
        };
        
        // 更新標籤頁
        spmDataStore.updateAnalysisTabData(activeTabId.value, {
          viewerGroups: updatedGroups
        });
        
        // 更新活動視圖信息
        activeGroupInfo.value = {
          groupId: activeGroup.id,
          viewerIndex: updatedViewers.length - 1,
          viewerId: profileViewer.id,
          viewerComponent: 'ProfileViewer'
        };
        
        // 更新關聯映射
        const sourceViewerId = sourceViewer.id;
        const newProfileViewerId = profileViewer.id;
        
        if (!profileAssociations.value.has(sourceViewerId)) {
          profileAssociations.value.set(sourceViewerId, []);
        }
        
        const currentAssociations = profileAssociations.value.get(sourceViewerId) || [];
        if (!currentAssociations.includes(newProfileViewerId)) {
          currentAssociations.push(newProfileViewerId);
          profileAssociations.value.set(sourceViewerId, currentAssociations);
        }
      }
      
      // 開始測量模式
      analysisStore.toggleMeasureMode();
    };
    
    // 處理測量新剖面請求
    const handleMeasureNewProfile = (data: any) => {
      if (!activeTab.value) return;
      
      console.log('處理測量新剖面請求:', data);
      
      // 切換到測量模式
      analysisStore.toggleMeasureMode();
      
      // 更新對應的視圖狀態 - 以在 ProfileViewer 中顯示測量模式
      if (activeTab.value.viewerGroups) {
        const updatedGroups = [...activeTab.value.viewerGroups];
        
        // 尋找包含 ImageViewer 的群組
        for (let i = 0; i < updatedGroups.length; i++) {
          const group = updatedGroups[i];
          const viewerIndex = group.viewers.findIndex(v => v.id === data.sourceViewerId);
          
          if (viewerIndex !== -1) {
            // 更新 ImageViewer 的 profileMeasureMode 屬性
            updatedGroups[i] = {
              ...group,
              viewers: group.viewers.map((viewer, idx) => {
                if (idx === viewerIndex) {
                  return {
                    ...viewer,
                    props: {
                      ...viewer.props,
                      profileMeasureMode: true,
                      targetProfileViewer: {
                        id: data.profileViewerId
                      }
                    }
                  };
                }
                return viewer;
              })
            };
            
            // 更新標籤頁
            spmDataStore.updateAnalysisTabData(activeTabId.value, {
              viewerGroups: updatedGroups
            });
            
            // 激活 ImageViewer
            activeGroupInfo.value = {
              groupId: group.id,
              viewerIndex: viewerIndex,
              viewerId: data.sourceViewerId,
              viewerComponent: 'ImageViewer'
            };
            
            break;
          }
        }
      }
    };
    
    // 監聽測量模式變化
    watch(() => measureMode.value, (newMode) => {
      // 如果退出測量模式，更新視圖狀態
      if (!newMode && activeTab.value && activeTab.value.viewerGroups) {
        const updatedGroups = [...activeTab.value.viewerGroups];
        
        // 尋找所有處於測量模式的 ImageViewer，並關閉其測量模式
        for (let i = 0; i < updatedGroups.length; i++) {
          const group = updatedGroups[i];
          let groupUpdated = false;
          
          const updatedViewers = group.viewers.map(viewer => {
            if (viewer.component === 'ImageViewer' && viewer.props.profileMeasureMode) {
              groupUpdated = true;
              return {
                ...viewer,
                props: {
                  ...viewer.props,
                  profileMeasureMode: false,
                  targetProfileViewer: null
                }
              };
            }
            return viewer;
          });
          
          if (groupUpdated) {
            updatedGroups[i] = {
              ...group,
              viewers: updatedViewers
            };
          }
        }
        
        // 更新標籤頁
        spmDataStore.updateAnalysisTabData(activeTabId.value, {
          viewerGroups: updatedGroups
        });
      }
    });
    
    // 監聽 ImageViewer 發出的線性剖面事件
    const handleLineProfile = (data: any) => {
      // 使用 analysisStore 處理線性剖面
      analysisStore.handleLineProfile(data);
      
      // 如果剖面數據生成成功，更新相關的 ProfileViewer
      watch(() => analysisStore.profileData, (profileData) => {
        if (!profileData || !activeTab.value) return;
        
        // 尋找目標 ProfileViewer 並更新其數據
        if (data.targetProfileViewer && activeTab.value.viewerGroups) {
          for (const group of activeTab.value.viewerGroups) {
            for (let i = 0; i < group.viewers.length; i++) {
              const viewer = group.viewers[i];
              if (viewer.id === data.targetProfileViewer.id) {
                // 更新 ProfileViewer 的數據
                const updatedGroups = [...activeTab.value.viewerGroups];
                const groupIndex = updatedGroups.indexOf(group);
                
                if (groupIndex !== -1) {
                  const updatedViewers = [...updatedGroups[groupIndex].viewers];
                  updatedViewers[i] = {
                    ...updatedViewers[i],
                    props: {
                      ...updatedViewers[i].props,
                      profileData: profileData,
                      roughness: analysisStore.roughness
                    }
                  };
                  
                  updatedGroups[groupIndex] = {
                    ...updatedGroups[groupIndex],
                    viewers: updatedViewers
                  };
                  
                  // 更新標籤頁
                  spmDataStore.updateAnalysisTabData(activeTabId.value, {
                    viewerGroups: updatedGroups
                  });
                  
                  break;
                }
              }
            }
          }
        }
      }, { immediate: true });
    };
    
    // 組件掛載時
    onMounted(() => {
      // 檢查是否有活動標籤頁
      if (activeTab.value) {
        // 尋找活動的視圖群組和視圖
        if (activeTab.value.viewerGroups && activeTab.value.viewerGroups.length > 0) {
          // 尋找第一個有活動視圖的群組
          for (const group of activeTab.value.viewerGroups) {
            const activeViewerIndex = group.viewers.findIndex(viewer => viewer.props && viewer.props.isActive);
            if (activeViewerIndex !== -1) {
              // 找到活動視圖
              activeGroupInfo.value = {
                groupId: group.id,
                viewerIndex: activeViewerIndex,
                viewerId: group.viewers[activeViewerIndex].id,
                viewerComponent: group.viewers[activeViewerIndex].component
              };
              break;
            }
          }
          
          // 如果沒有找到活動視圖，設置第一個群組的第一個視圖為活動
          if (!activeGroupInfo.value) {
            const firstGroup = activeTab.value.viewerGroups[0];
            if (firstGroup.viewers.length > 0) {
              activeGroupInfo.value = {
                groupId: firstGroup.id,
                viewerIndex: 0,
                viewerId: firstGroup.viewers[0].id,
                viewerComponent: firstGroup.viewers[0].component
              };
            }
          }
        }
      }
    });
    
    return {
      // 狀態
      analysisTabs,
      activeTabId,
      activeTab,
      activeViewer,
      activeGroupInfo,
      showFileSelector,
      showToolsPanel,
      isLoading,
      errorMessage,
      
      // 方法
      switchTab,
      closeTab,
      addTab,
      updateTab,
      loadSelectedFile,
      handleViewerActivated,
      createLineProfile,
      handleMeasureNewProfile,
      handleLineProfile,
      getLinkedProfiles,
      clearError
    };
  }
});
</script>