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
        <!-- 檔案選擇器面板 - 使用新組件 -->
        <FileSelectorPanel 
          :active-tab="activeTab" 
          :is-loading="isTabLoading"
          @toggle-selector="showFileSelector = $event"
          @load-file="loadSelectedFile"
        />
        
        <!-- 工具列面板 - 使用新組件 -->
        <ToolsPanel
          :active-viewer="activeViewer"
          :active-tab-colormap="activeTabColormap"
          :active-tab-z-scale="activeTabZScale"
          :linked-profiles="getLinkedProfiles()"
          @toggle-panel="showToolsPanel = $event"
          @update-settings="updateActiveTabSettings"
          @apply-flatten="applyFlatten"
          @adjust-tilt="adjustTilt"
          @create-line-profile="createLineProfile"
          @update-profile="updateProfile"
          @activate-profile="activateProfileViewer"
          @activate-source-viewer="activateSourceViewer"
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
          @group-to-tab="handleGroupToTab"
          @create-line-profile="createLineProfile"
          @viewer-activated="handleViewerActivated"
        />
      </div>

      <!-- 載入中顯示 -->
      <div v-if="isTabLoading" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20 z-50">
        <div class="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
          <div class="w-12 h-12 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-4"></div>
          <p class="text-gray-600">正在載入資料...</p>
        </div>
      </div>

      <!-- 錯誤提示 -->
      <div v-if="tabLoadError" 
           class="absolute top-4 right-4 max-w-md p-4 bg-red-50 border-l-4 border-red-400 text-red-700 z-50 rounded shadow-md">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm">{{ tabLoadError }}</p>
          </div>
          <div class="ml-auto pl-3">
            <button @click="tabLoadError = ''" class="text-red-400 hover:text-red-500 focus:outline-none">
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
    
    // 全局狀態
    const isTabLoading = ref(false);
    const tabLoadError = ref('');
    
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
    
    // 尋找當前活動的視圖群組
    const findActiveGroup = () => {
      if (!activeTab.value || !activeTab.value.viewerGroups || !activeGroupInfo.value) return null;
      return activeTab.value.viewerGroups.find(group => group.id === activeGroupInfo.value?.groupId) || null;
    };
    
    // 活動標籤頁設置
    const activeTabColormap = ref('Oranges');
    const activeTabZScale = ref(1.0);
    
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
    
    // 處理視圖啟用 - 新函數
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
      
      // 更新當前標籤頁的設置
      const tab = analysisTabs.value.find(tab => tab.id === tabId);
      if (tab) {
        activeTabColormap.value = tab.colormap || 'Oranges';
        activeTabZScale.value = tab.zScale || 1.0;
        
        // 尋找活動的視圖群組和視圖
        if (tab.viewerGroups && tab.viewerGroups.length > 0) {
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
      // 實作更新標籤頁的邏輯
      console.log('更新標籤頁:', id, changes);
      spmDataStore.updateAnalysisTabData(id, changes);
    };
    
    // 更新標籤頁設置
    const updateActiveTabSettings = (settings: any) => {
      if (!activeTabId.value) return;
      
      spmDataStore.updateAnalysisTabData(activeTabId.value, settings);
    };
    
    // 載入選中檔案
    const loadSelectedFile = async ({ selectedFileId, activeTabId }: { selectedFileId: string, activeTabId: string }) => {
      console.log('loadSelectedFile called with:', selectedFileId, activeTabId);
      if (!selectedFileId || !activeTab.value) return;
      
      isTabLoading.value = true;
      tabLoadError.value = '';
      
      try {
        // 檢查檔案類型
        if (selectedFileId.toLowerCase().endsWith('.int')) {
          console.log('處理INT檔案');
          // 處理 INT 檔案
          const response = await window.pywebview.api.analyze_int_file_api(
            selectedFileId, 
            activeTab.value.fileId
          );
          
          console.log('API回應:', response);
          
          if (response.success) {
            // 更新標籤頁數據
            const fileName = selectedFileId.split(/[\/\\]/).pop() || '';
            
            // 創建新的視圖群組
            const groupId = `group-${activeTab.value.id}-${Date.now()}`;
            const imageViewer = {
              id: `viewer-image-${Date.now()}`,
              component: 'ImageViewer',
              props: {
                id: `viewer-image-${Date.now()}`,
                imageData: response.image,
                imageRawData: response.rawData, // 確保傳遞原始數據
                title: fileName,
                imageType: 'topo',
                physUnit: response.physUnit || 'nm',
                colormap: activeTab.value.colormap || 'Oranges',
                zScale: activeTab.value.zScale || 1.0,
                stats: response.statistics || null,
                dimensions: response.dimensions || { width: 0, height: 0, xRange: 0, yRange: 0 },
                isActive: true,
                profileMeasureMode: false // 默認非測量模式
              }
            };
            
            console.log('創建視圖:', imageViewer);
            
            // 如果標籤頁尚未有視圖群組，添加一個新的
            if (!activeTab.value.viewerGroups || activeTab.value.viewerGroups.length === 0) {
              console.log('創建新的視圖群組');
              
              const viewerGroup = {
                id: groupId,
                title: fileName,
                viewers: [imageViewer],
                layout: 'horizontal'
              };
              
              console.log('新視圖群組:', viewerGroup);
              
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
              console.log('添加到現有視圖群組');
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
            
            // 更新UI設置
            activeTabColormap.value = activeTab.value.colormap || 'Oranges';
            activeTabZScale.value = activeTab.value.zScale || 1.0;
          } else {
            console.error('API回應失敗:', response.error);
            tabLoadError.value = response.error || '載入檔案時發生錯誤';
          }
        } else {
          console.error('不支援的檔案類型');
          tabLoadError.value = '檔案類型不支援';
        }
      } catch (error) {
        console.error('載入檔案錯誤:', error);
        tabLoadError.value = `載入檔案時發生錯誤: ${error}`;
      } finally {
        isTabLoading.value = false;
      }
    };
    
    // 處理群組轉標籤頁
    const handleGroupToTab = (groupData: any) => {
      // 實作群組轉標籤頁的邏輯
      console.log('群組轉標籤頁:', groupData);
    };
    
    // 創建線性剖面 - 添加到當前視圖群組
    const createLineProfile = (targetData?: any) => {
      if (!activeTab.value) {
        console.error('無活動標籤頁');
        return;
      }
      
      console.log('創建線性剖面, targetData:', targetData);
      const activeGroup = findActiveGroup();
      
      if (!activeGroup) {
        console.error('找不到活動視圖群組');
        tabLoadError.value = '請先選擇或創建一個視圖群組';
        return;
      }
      
      // 找出當前活動的 ImageViewer
      const sourceViewerIndex = targetData?.viewerIndex || activeGroupInfo.value?.viewerIndex || 0;
      const sourceViewer = activeGroup.viewers[sourceViewerIndex];
      
      if (!sourceViewer || sourceViewer.component !== 'ImageViewer') {
        console.error('找不到有效的源圖像視圖');
        tabLoadError.value = '請先選擇一個圖像視圖';
        return;
      }
      
      // 創建新的ProfileViewer，並設置與ImageViewer的關聯
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
          initialShiftZero: false,
          initialAutoScale: true,
          initialShowPeaks: false,
          isMeasuring: false,
          // 添加源圖像視圖的引用
          sourceViewerId: sourceViewer.id,
          sourceViewerTitle: sourceViewer.props.title || 'Image'
        }
      };
      
      console.log('創建剖面視圖:', profileViewer);
      
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
        
        console.log('更新後的視圖群組:', updatedGroups[groupIndex]);
        console.log('更新後的活動視圖信息:', activeGroupInfo.value);
        console.log('更新後的關聯映射:', profileAssociations.value);
      }
    };
    
    // 更新剖面圖
    const updateProfile = async (settings: any) => {
      if (!activeViewer.value || activeViewer.value.component !== 'ProfileViewer') return;
      
      try {
        isTabLoading.value = true;
        
        // 獲取當前ProfileViewer的profileData
        const profileData = activeViewer.value.props.profileData;
        if (!profileData) {
          console.error('沒有可用的剖面數據');
          return;
        }
        
        // 調用API更新剖面圖
        const response = await window.pywebview.api.update_profile(
          profileData,
          settings.shiftZero,
          settings.autoScale,
          settings.showPeaks,
          settings.peakSensitivity
        );
        
        if (response.success) {
          // 找到活動的視圖群組和視圖
          const activeGroup = findActiveGroup();
          if (!activeGroup) return;
          
          // 獲取當前視圖索引
          const viewerIndex = activeGroupInfo.value?.viewerIndex || 0;
          
          // 更新視圖數據
          const updatedViewers = [...activeGroup.viewers];
          updatedViewers[viewerIndex] = {
            ...updatedViewers[viewerIndex],
            props: {
              ...updatedViewers[viewerIndex].props,
              profileImage: response.profile_image
            }
          };
          
          // 更新視圖群組
          const updatedGroups = [...activeTab.value!.viewerGroups];
          const groupIndex = updatedGroups.findIndex(group => group.id === activeGroup.id);
          
          updatedGroups[groupIndex] = {
            ...activeGroup,
            viewers: updatedViewers
          };
          
          // 更新標籤頁
          spmDataStore.updateAnalysisTabData(activeTabId.value, {
            viewerGroups: updatedGroups
          });
        } else {
          tabLoadError.value = response.error || '更新剖面圖失敗';
        }
      } catch (error) {
        console.error('更新剖面圖錯誤:', error);
        tabLoadError.value = `更新剖面圖時發生錯誤: ${error}`;
      } finally {
        isTabLoading.value = false;
      }
    };
    
    // 應用平面化
    const applyFlatten = async (method: string) => {
      if (!activeViewer.value || activeViewer.value.component !== 'ImageViewer') return;
      
      try {
        // 尋找當前活動的視圖
        const activeGroup = findActiveGroup();
        if (!activeGroup || !activeTab.value) return;
        
        const viewerIndex = activeGroupInfo.value?.viewerIndex;
        if (viewerIndex === undefined || viewerIndex < 0) return;
        
        // 獲取當前視圖的原始數據
        const imageData = activeGroup.viewers[viewerIndex].props.imageRawData;
        if (!imageData) {
          tabLoadError.value = "沒有可用的圖像數據";
          return;
        }
        
        isTabLoading.value = true;
        
        // 調用API進行平面化處理
        const response = await window.pywebview.api.apply_flatten(
          imageData, 
          method, 
          method === 'polyfit' ? 2 : 1  // 對於多項式方法，使用2階
        );
        
        if (response.success) {
          // 更新視圖數據
          const updatedViewers = [...activeGroup.viewers];
          updatedViewers[viewerIndex] = {
            ...updatedViewers[viewerIndex],
            props: {
              ...updatedViewers[viewerIndex].props,
              imageRawData: response.processed_data,
              statistics: response.statistics
            }
          };
          
          // 更新視圖組
          const updatedGroups = [...activeTab.value.viewerGroups];
          const groupIndex = updatedGroups.findIndex(group => group.id === activeGroup.id);
          
          updatedGroups[groupIndex] = {
            ...activeGroup,
            viewers: updatedViewers
          };
          
          // 更新標籤頁
          spmDataStore.updateAnalysisTabData(activeTabId.value, {
            viewerGroups: updatedGroups
          });
        } else {
          tabLoadError.value = response.error || "平面化處理失敗";
        }
      } catch (error) {
        console.error('平面化處理錯誤:', error);
        tabLoadError.value = `平面化處理時發生錯誤: ${error}`;
      } finally {
        isTabLoading.value = false;
      }
    };
    
    // 調整傾斜
    const adjustTilt = async ({ direction, fineTune }: { direction: string, fineTune: boolean }) => {
      if (!activeViewer.value || activeViewer.value.component !== 'ImageViewer') return;
      
      try {
        // 尋找當前活動的視圖
        const activeGroup = findActiveGroup();
        if (!activeGroup || !activeTab.value) return;
        
        const viewerIndex = activeGroupInfo.value?.viewerIndex;
        if (viewerIndex === undefined || viewerIndex < 0) return;
        
        // 獲取當前視圖的原始數據
        const imageData = activeGroup.viewers[viewerIndex].props.imageRawData;
        if (!imageData) {
          tabLoadError.value = "沒有可用的圖像數據";
          return;
        }
        
        isTabLoading.value = true;
        
        // 調用API進行傾斜調整
        const response = await window.pywebview.api.tilt_image(
          imageData, 
          direction,
          fineTune
        );
        
        if (response.success) {
          // 更新視圖數據
          const updatedViewers = [...activeGroup.viewers];
          updatedViewers[viewerIndex] = {
            ...updatedViewers[viewerIndex],
            props: {
              ...updatedViewers[viewerIndex].props,
              imageRawData: response.processed_data,
              statistics: response.statistics
            }
          };
          
          // 更新視圖組
          const updatedGroups = [...activeTab.value.viewerGroups];
          const groupIndex = updatedGroups.findIndex(group => group.id === activeGroup.id);
          
          updatedGroups[groupIndex] = {
            ...activeGroup,
            viewers: updatedViewers
          };
          
          // 更新標籤頁
          spmDataStore.updateAnalysisTabData(activeTabId.value, {
            viewerGroups: updatedGroups
          });
        } else {
          tabLoadError.value = response.error || "傾斜調整失敗";
        }
      } catch (error) {
        console.error('傾斜調整錯誤:', error);
        tabLoadError.value = `傾斜調整時發生錯誤: ${error}`;
      } finally {
        isTabLoading.value = false;
      }
    };
    
    // 處理 ProfileViewer 中的測量模式切換
    const handleToggleMeasureMode = async ({ isMeasuring, sourceViewerId, profileViewerId }: any) => {
      if (!activeTab.value) return;
      
      console.log('處理測量模式切換:', isMeasuring, sourceViewerId, profileViewerId);
      
      // 找到源視圖和剖面視圖
      let sourceViewer = null;
      let sourceViewerGroup = null;
      let sourceViewerIndex = -1;
      
      let profileViewer = null;
      let profileViewerGroup = null;
      let profileViewerIndex = -1;
      
      // 尋找源視圖和剖面視圖
      for (const group of activeTab.value.viewerGroups) {
        // 尋找源視圖
        const srcIndex = group.viewers.findIndex(v => v.id === sourceViewerId);
        if (srcIndex !== -1) {
          sourceViewer = group.viewers[srcIndex];
          sourceViewerGroup = group;
          sourceViewerIndex = srcIndex;
        }
        
        // 尋找剖面視圖
        const profIndex = group.viewers.findIndex(v => v.id === profileViewerId);
        if (profIndex !== -1) {
          profileViewer = group.viewers[profIndex];
          profileViewerGroup = group;
          profileViewerIndex = profIndex;
        }
      }
      
      if (!sourceViewer || !profileViewer) {
        console.error('找不到源視圖或剖面視圖');
        tabLoadError.value = '找不到關聯的視圖';
        return;
      }
      
      // 更新兩個視圖的狀態
      const updatedGroups = [...activeTab.value.viewerGroups];
      
      // 1. 更新源視圖的測量模式
      const sourceGroupIndex = updatedGroups.indexOf(sourceViewerGroup!);
      
      updatedGroups[sourceGroupIndex] = {
        ...sourceViewerGroup!,
        viewers: sourceViewerGroup!.viewers.map((viewer, idx) => {
          if (idx === sourceViewerIndex) {
            return {
              ...viewer,
              props: {
                ...viewer.props,
                profileMeasureMode: isMeasuring,
                // 如果是測量模式，設置目標剖面視圖
                targetProfileViewer: isMeasuring ? {
                  id: profileViewerId,
                  groupId: profileViewerGroup!.id,
                  viewerIndex: profileViewerIndex
                } : null
              }
            };
          }
          return viewer;
        })
      };
      
      // 2. 更新剖面視圖的測量狀態
      const profileGroupIndex = updatedGroups.indexOf(profileViewerGroup!);
      
      // 如果源視圖和剖面視圖在同一個群組
      if (sourceGroupIndex === profileGroupIndex) {
        // 已經更新了整個群組，只需確保剖面視圖的 isMeasuring 狀態正確
        updatedGroups[sourceGroupIndex].viewers[profileViewerIndex] = {
          ...updatedGroups[sourceGroupIndex].viewers[profileViewerIndex],
          props: {
            ...updatedGroups[sourceGroupIndex].viewers[profileViewerIndex].props,
            isMeasuring: isMeasuring
          }
        };
      } else {
        // 源視圖和剖面視圖在不同群組
        updatedGroups[profileGroupIndex] = {
          ...profileViewerGroup!,
          viewers: profileViewerGroup!.viewers.map((viewer, idx) => {
            if (idx === profileViewerIndex) {
              return {
                ...viewer,
                props: {
                  ...viewer.props,
                  isMeasuring: isMeasuring
                }
              };
            }
            return viewer;
          })
        };
      }
      
      // 更新標籤頁
      spmDataStore.updateAnalysisTabData(activeTabId.value, {
        viewerGroups: updatedGroups
      });
      
      // 如果啟用測量模式，激活源視圖
      if (isMeasuring) {
        // 更新活動視圖信息
        activeGroupInfo.value = {
          groupId: sourceViewerGroup!.id,
          viewerIndex: sourceViewerIndex,
          viewerId: sourceViewerId,
          viewerComponent: 'ImageViewer'
        };
      }
    };
    
    // 處理測量完成
    const handleMeasureCompleted = () => {
      // 找到處於測量模式的源視圖
      let sourceViewer = null;
      let sourceViewerGroup = null;
      let sourceViewerIndex = -1;
      
      if (!activeTab.value) return;
      
      // 尋找源視圖
      for (const group of activeTab.value.viewerGroups) {
        const index = group.viewers.findIndex(v => 
          v.component === 'ImageViewer' && 
          v.props && 
          v.props.profileMeasureMode
        );
        
        if (index !== -1) {
          sourceViewer = group.viewers[index];
          sourceViewerGroup = group;
          sourceViewerIndex = index;
          break;
        }
      }
      
      if (!sourceViewer) return;
      
      // 更新視圖狀態 - 關閉測量模式
      const updatedGroups = [...activeTab.value.viewerGroups];
      const groupIndex = updatedGroups.indexOf(sourceViewerGroup!);
      
      updatedGroups[groupIndex] = {
        ...sourceViewerGroup!,
        viewers: sourceViewerGroup!.viewers.map((viewer, idx) => {
          if (idx === sourceViewerIndex) {
            return {
              ...viewer,
              props: {
                ...viewer.props,
                profileMeasureMode: false
              }
            };
          }
          return viewer;
        })
      };
      
      // 更新目標剖面視圖的測量狀態
      const targetProfileViewer = sourceViewer.props.targetProfileViewer;
      if (targetProfileViewer) {
        // 查找目標剖面視圖
        for (let i = 0; i < updatedGroups.length; i++) {
          const group = updatedGroups[i];
          const viewerIndex = group.viewers.findIndex(v => v.id === targetProfileViewer.id);
          
          if (viewerIndex !== -1) {
            updatedGroups[i] = {
              ...group,
              viewers: group.viewers.map((viewer, idx) => {
                if (idx === viewerIndex) {
                  return {
                    ...viewer,
                    props: {
                      ...viewer.props,
                      isMeasuring: false
                    }
                  };
                }
                return viewer;
              })
            };
            break;
          }
        }
      }
      
      // 更新標籤頁
      spmDataStore.updateAnalysisTabData(activeTabId.value, {
        viewerGroups: updatedGroups
      });
    };
    
    // 處理測量新剖面請求
    const handleMeasureNewProfile = (data: any) => {
      if (!activeTab.value) return;
      
      console.log('處理測量新剖面請求:', data);
      
      // 這裡直接複用 handleToggleMeasureMode 的邏輯
      handleToggleMeasureMode({
        isMeasuring: true,
        sourceViewerId: data.sourceViewerId,
        profileViewerId: data.profileViewerId
      });
    };
    
    // 處理線性剖面數據
    const handleLineProfileResult = async (data: any) => {
      if (!activeTab.value) return;
      
      console.log('處理線性剖面數據:', data);
      
      try {
        isTabLoading.value = true;
        
        // 獲取線性剖面數據
        const response = await window.pywebview.api.get_line_profile(
          data.sourceData.imageRawData,
          data.startPoint,
          data.endPoint,
          data.sourceData.dimensions?.xRange || 100,
          false  // 不偏移到零
        );
        
        if (response.success) {
          // 尋找目標 ProfileViewer
          let targetProfileViewer = null;
          let targetGroupId = '';
          let targetViewerIndex = -1;
          
          // 如果指定了目標 ProfileViewer
          if (data.targetProfileViewer) {
            for (const group of activeTab.value.viewerGroups) {
              const viewerIndex = group.viewers.findIndex(viewer => 
                viewer.id === data.targetProfileViewer.id
              );
              
              if (viewerIndex !== -1) {
                targetProfileViewer = group.viewers[viewerIndex];
                targetGroupId = group.id;
                targetViewerIndex = viewerIndex;
                break;
              }
            }
          }
          
          if (targetProfileViewer) {
            // 更新現有的 ProfileViewer
            const updatedGroups = [...activeTab.value.viewerGroups];
            const groupIndex = updatedGroups.findIndex(group => group.id === targetGroupId);
            
            if (groupIndex !== -1) {
              const updatedViewers = [...updatedGroups[groupIndex].viewers];
              
              updatedViewers[targetViewerIndex] = {
                ...updatedViewers[targetViewerIndex],
                props: {
                  ...updatedViewers[targetViewerIndex].props,
                  profileData: response.profile_data,
                  profileImage: response.profile_image,
                  roughness: response.roughness
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
              
              // 延遲後切換到剖面視圖
              setTimeout(() => {
                // 激活更新的 ProfileViewer
                activeGroupInfo.value = {
                  groupId: targetGroupId,
                  viewerIndex: targetViewerIndex,
                  viewerId: targetProfileViewer!.id,
                  viewerComponent: 'ProfileViewer'
                };
              }, 500);
            }
          } else {
            // 應該不會發生，因為現在我們總是有一個目標剖面視圖
            console.error('沒有目標剖面視圖');
          }
        } else {
          tabLoadError.value = response.error || '獲取線性剖面失敗';
        }
      } catch (error) {
        console.error('線性剖面處理錯誤:', error);
        tabLoadError.value = `處理線性剖面時發生錯誤: ${error}`;
      } finally {
        isTabLoading.value = false;
        
        // 處理測量完成
        handleMeasureCompleted();
      }
    };
    
    // 激活指定的ProfileViewer
    const activateProfileViewer = (profileId: string) => {
      if (!activeTab.value) return;
      
      console.log('激活ProfileViewer:', profileId);
      
      // 尋找指定的ProfileViewer
      for (const group of activeTab.value.viewerGroups) {
        const viewerIndex = group.viewers.findIndex(viewer => viewer.id === profileId);
        
        if (viewerIndex !== -1) {
          // 將所有視圖設為非活動
          const updatedViewers = group.viewers.map((viewer, idx) => ({
            ...viewer,
            props: {
              ...viewer.props,
              isActive: idx === viewerIndex
            }
          }));
          
          // 更新視圖群組
          const updatedGroups = [...activeTab.value.viewerGroups];
          const groupIndex = updatedGroups.findIndex(g => g.id === group.id);
          
          if (groupIndex !== -1) {
            updatedGroups[groupIndex] = {
              ...group,
              viewers: updatedViewers
            };
            
            // 更新標籤頁
            spmDataStore.updateAnalysisTabData(activeTabId.value, {
              viewerGroups: updatedGroups
            });
            
            // 更新活動視圖信息
            activeGroupInfo.value = {
              groupId: group.id,
              viewerIndex: viewerIndex,
              viewerId: profileId,
              viewerComponent: 'ProfileViewer'
            };
          }
          
          break;
        }
      }
    };
    
    // 激活源視圖
    const activateSourceViewer = (sourceViewerId: string) => {
      if (!activeTab.value) return;
      
      console.log('激活源視圖:', sourceViewerId);
      
      // 尋找指定的源視圖
      for (const group of activeTab.value.viewerGroups) {
        const viewerIndex = group.viewers.findIndex(viewer => viewer.id === sourceViewerId);
        
        if (viewerIndex !== -1) {
          // 將所有視圖設為非活動
          const updatedViewers = group.viewers.map((viewer, idx) => ({
            ...viewer,
            props: {
              ...viewer.props,
              isActive: idx === viewerIndex
            }
          }));
          
          // 更新視圖群組
          const updatedGroups = [...activeTab.value.viewerGroups];
          const groupIndex = updatedGroups.findIndex(g => g.id === group.id);
          
          if (groupIndex !== -1) {
            updatedGroups[groupIndex] = {
              ...group,
              viewers: updatedViewers
            };
            
            // 更新標籤頁
            spmDataStore.updateAnalysisTabData(activeTabId.value, {
              viewerGroups: updatedGroups
            });
            
            // 更新活動視圖信息
            activeGroupInfo.value = {
              groupId: group.id,
              viewerIndex: viewerIndex,
              viewerId: sourceViewerId,
              viewerComponent: 'ImageViewer'
            };
          }
          
          break;
        }
      }
    };
    
    // 監視標籤頁變化
    watch(activeTabId, () => {
      if (activeTab.value) {
        // 更新當前標籤頁設置
        activeTabColormap.value = activeTab.value.colormap || 'Oranges';
        activeTabZScale.value = activeTab.value.zScale || 1.0;
      }
    });
    
    // 監視標籤頁列表
    watch(analysisTabs, (newTabs, oldTabs) => {
      // 如果添加了新標籤頁
      if (newTabs.length > oldTabs.length) {
        const newTab = newTabs.find(tab => !oldTabs.some(oldTab => oldTab.id === tab.id));
        
        if (newTab) {
          // 自動顯示控制面板
          showFileSelector.value = true;
          
          // 自動載入第一個可用的 INT 檔案
          const intFile = newTab.relatedFiles?.find(f => f.path.toLowerCase().endsWith('.int'));
          
          if (intFile) {
            console.log('新標籤頁自動載入INT檔案:', intFile.path);
            loadSelectedFile({
              selectedFileId: intFile.path,
              activeTabId: newTab.id
            });
          }
        }
      }
    }, { deep: true });
    
    // 初始化
    onMounted(() => {
      // 檢查是否有活動標籤頁
      if (activeTab.value) {
        // 更新當前標籤頁設置
        activeTabColormap.value = activeTab.value.colormap || 'Oranges';
        activeTabZScale.value = activeTab.value.zScale || 1.0;
        
        // 如果沒有圖像數據，自動顯示控制面板
        if (!activeTab.value.imageData && !activeTab.value.viewerGroups) {
          showFileSelector.value = true;
          
          // 自動載入第一個 INT 檔案
          const intFile = activeTab.value.relatedFiles?.find(f => f.path.toLowerCase().endsWith('.int'));
          
          if (intFile) {
            console.log('現有標籤頁自動載入INT檔案:', intFile.path);
            loadSelectedFile({
              selectedFileId: intFile.path,
              activeTabId: activeTab.value.id
            });
          }
        }
        
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
      isTabLoading,
      tabLoadError,
      analysisTabs,
      activeTabId,
      activeTab,
      activeViewer,
      activeTabColormap,
      activeTabZScale,
      showFileSelector,
      showToolsPanel,
      
      // 方法
      switchTab,
      closeTab,
      addTab,
      updateTab,
      loadSelectedFile,
      handleGroupToTab,
      updateActiveTabSettings,
      handleViewerActivated,
      createLineProfile,
      updateProfile,
      applyFlatten,
      adjustTilt,
      getLinkedProfiles,
      activateProfileViewer,
      activateSourceViewer,
      handleMeasureNewProfile,
      handleLineProfileResult,
      handleToggleMeasureMode,
      handleMeasureCompleted
    };
  }
});
</script>

<style scoped>
/* 可以添加一些自定義樣式 */
</style>