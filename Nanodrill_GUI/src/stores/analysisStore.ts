// src/stores/analysisStore.ts
import { defineStore } from 'pinia';
import { AnalysisService } from '../services/analysisService';
import { useSpmDataStore } from './spmDataStore';

export interface Dimensions {
  width: number;
  height: number;
  xRange: number;
  yRange: number;
}

export const useAnalysisStore = defineStore('analysis', {
  state: () => ({
    // 當前選擇的文件
    selectedFileId: '',
    currentFileName: '',
    
    // 載入狀態
    isLoading: false,
    errorMessage: '',
    
    // 圖像數據
    imageData: null as string | null,
    imageRawData: null as number[][] | null,
    dimensions: { width: 0, height: 0, xRange: 0, yRange: 0 } as Dimensions,
    physUnit: 'nm',
    
    // 剖面數據
    profileData: null as any | null,
    roughness: null as any | null,
    
    // 測量模式
    measureMode: false,
    
    // 活動視圖信息
    activeTabId: '',
    activeGroupId: '',
    activeViewerId: ''
  }),
  
  actions: {
    /**
     * 選擇文件
     */
    selectFile(fileId: string, fileName: string) {
      this.selectedFileId = fileId;
      this.currentFileName = fileName;
    },
    
    /**
     * 載入選中的文件
     */
    async loadSelectedFile() {
      if (!this.selectedFileId) return;
      
      try {
        this.isLoading = true;
        this.errorMessage = '';
        
        const response = await AnalysisService.loadIntFile(this.selectedFileId);
        
        if (response.success) {
          this.imageData = response.image;
          this.imageRawData = response.rawData;
          this.dimensions = response.dimensions || { width: 512, height: 512, xRange: 100, yRange: 100 };
          this.physUnit = response.physUnit || 'nm';
          
          // 清除剖面數據
          this.profileData = null;
          this.roughness = null;
          
          // 更新標籤頁數據
          this.updateTabWithLoadedData();
        } else {
          this.errorMessage = response.error || '載入文件失敗';
        }
      } catch (error) {
        this.errorMessage = `載入文件時發生錯誤: ${error}`;
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 更新標籤頁數據
     */
    updateTabWithLoadedData() {
      const spmDataStore = useSpmDataStore();
      
      if (this.activeTabId && this.imageRawData) {
        // 創建新的視圖群組
        const groupId = `group-${this.activeTabId}-${Date.now()}`;
        const imageViewer = {
          id: `viewer-image-${Date.now()}`,
          component: 'ImageViewer',
          props: {
            id: `viewer-image-${Date.now()}`,
            imageData: this.imageData,
            imageRawData: this.imageRawData,
            title: this.currentFileName || 'Image',
            imageType: 'topo',
            physUnit: this.physUnit,
            colormap: 'Oranges',
            zScale: 1.0,
            dimensions: this.dimensions,
            isActive: true
          }
        };
        
        // 檢查標籤頁是否已有視圖群組
        const activeTab = spmDataStore.analysisTabs.find(tab => tab.id === this.activeTabId);
        
        if (activeTab) {
          if (!activeTab.viewerGroups || activeTab.viewerGroups.length === 0) {
            // 添加新的視圖群組
            spmDataStore.updateAnalysisTabData(this.activeTabId, {
              viewerGroups: [{
                id: groupId,
                title: this.currentFileName || 'Image Group',
                viewers: [imageViewer],
                layout: 'horizontal'
              }]
            });
            
            // 更新活動群組ID
            this.activeGroupId = groupId;
            this.activeViewerId = imageViewer.id;
          } else {
            // 向現有群組添加視圖
            const updatedGroups = [...activeTab.viewerGroups];
            
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
            
            // 更新標籤頁
            spmDataStore.updateAnalysisTabData(this.activeTabId, {
              viewerGroups: updatedGroups
            });
            
            // 更新活動視圖ID
            this.activeGroupId = updatedGroups[0].id;
            this.activeViewerId = imageViewer.id;
          }
        }
      }
    },
    
    /**
     * 處理線性剖面
     */
    async handleLineProfile(data: any) {
      try {
        this.isLoading = true;
        
        const response = await AnalysisService.getLineProfile(
          data.sourceData.imageRawData,
          data.startPoint,
          data.endPoint,
          data.sourceData.dimensions?.xRange || 100,
          false // 不偏移到零
        );
        
        if (response.success) {
          this.profileData = response.profile_data;
          this.roughness = response.roughness;
          
          // 關閉測量模式
          this.measureMode = false;
          
          // 如果有目標剖面視圖，更新其數據
          if (data.targetProfileViewer) {
            this.updateProfileViewer(data.targetProfileViewer.id, this.profileData, this.roughness);
          }
        } else {
          this.errorMessage = response.error || '獲取剖面失敗';
        }
      } catch (error) {
        this.errorMessage = `處理剖面時發生錯誤: ${error}`;
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 更新剖面視圖數據
     */
    updateProfileViewer(profileViewerId: string, profileData: any, roughness: any) {
      const spmDataStore = useSpmDataStore();
      
      // 尋找包含該剖面視圖的標籤頁和群組
      for (const tab of spmDataStore.analysisTabs) {
        if (tab.viewerGroups) {
          for (const group of tab.viewerGroups) {
            for (let i = 0; i < group.viewers.length; i++) {
              const viewer = group.viewers[i];
              if (viewer.id === profileViewerId) {
                // 找到目標視圖，更新其數據
                const updatedGroups = [...tab.viewerGroups];
                const groupIndex = updatedGroups.indexOf(group);
                
                if (groupIndex !== -1) {
                  const updatedViewers = [...updatedGroups[groupIndex].viewers];
                  updatedViewers[i] = {
                    ...updatedViewers[i],
                    props: {
                      ...updatedViewers[i].props,
                      profileData: profileData,
                      roughness: roughness
                    }
                  };
                  
                  updatedGroups[groupIndex] = {
                    ...updatedGroups[groupIndex],
                    viewers: updatedViewers
                  };
                  
                  // 更新標籤頁
                  spmDataStore.updateAnalysisTabData(tab.id, {
                    viewerGroups: updatedGroups
                  });
                  
                  return;
                }
              }
            }
          }
        }
      }
    },
    
    /**
     * 設置活動標籤頁
     */
    setActiveTab(tabId: string) {
      this.activeTabId = tabId;
      
      // 找出標籤頁的第一個群組作為活動群組
      const spmDataStore = useSpmDataStore();
      const tab = spmDataStore.analysisTabs.find(t => t.id === tabId);
      
      if (tab && tab.viewerGroups && tab.viewerGroups.length > 0) {
        this.activeGroupId = tab.viewerGroups[0].id;
        
        // 找出群組的第一個視圖作為活動視圖
        if (tab.viewerGroups[0].viewers && tab.viewerGroups[0].viewers.length > 0) {
          this.activeViewerId = tab.viewerGroups[0].viewers[0].id;
        }
      }
    },
    
    /**
     * 設置活動群組
     */
    setActiveGroup(groupId: string) {
      this.activeGroupId = groupId;
      
      // 找出群組的第一個視圖作為活動視圖
      const spmDataStore = useSpmDataStore();
      for (const tab of spmDataStore.analysisTabs) {
        if (tab.viewerGroups) {
          const group = tab.viewerGroups.find(g => g.id === groupId);
          if (group && group.viewers && group.viewers.length > 0) {
            this.activeViewerId = group.viewers[0].id;
            break;
          }
        }
      }
    },
    
    /**
     * 設置活動視圖
     */
    setActiveViewer(viewerId: string) {
      this.activeViewerId = viewerId;
      console.log('分析存儲中設置活動視圖:', viewerId);
    },
    
    /**
     * 切換測量模式
     */
    toggleMeasureMode() {
      this.measureMode = !this.measureMode;
      
      // 如果退出測量模式，更新所有 ImageViewer 的測量模式狀態
      if (!this.measureMode) {
        this.updateAllImageViewersMeasureMode(false);
      }
    },
    
    /**
     * 更新所有 ImageViewer 的測量模式狀態
     */
    updateAllImageViewersMeasureMode(mode: boolean) {
      const spmDataStore = useSpmDataStore();
      
      for (const tab of spmDataStore.analysisTabs) {
        if (tab.viewerGroups) {
          const updatedGroups = [...tab.viewerGroups];
          let groupsUpdated = false;
          
          // 更新每個群組中的 ImageViewer
          for (let i = 0; i < updatedGroups.length; i++) {
            const group = updatedGroups[i];
            let viewersUpdated = false;
            
            const updatedViewers = group.viewers.map(viewer => {
              if (viewer.component === 'ImageViewer') {
                viewersUpdated = true;
                return {
                  ...viewer,
                  props: {
                    ...viewer.props,
                    profileMeasureMode: mode,
                    targetProfileViewer: mode ? viewer.props.targetProfileViewer : null
                  }
                };
              }
              return viewer;
            });
            
            if (viewersUpdated) {
              groupsUpdated = true;
              updatedGroups[i] = {
                ...group,
                viewers: updatedViewers
              };
            }
          }
          
          // 如果有更新，更新標籤頁
          if (groupsUpdated) {
            spmDataStore.updateAnalysisTabData(tab.id, {
              viewerGroups: updatedGroups
            });
          }
        }
      }
    },
    
    /**
     * 清除錯誤消息
     */
    clearError() {
      this.errorMessage = '';
    }
  }
});