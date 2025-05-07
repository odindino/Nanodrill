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
    currentMeasuringViewerId: '', // 添加：當前正在測量的ViewerId
    
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
     * 更新標籤頁數據 - 修改為單容器模式
     */
    updateTabWithLoadedData() {
      const spmDataStore = useSpmDataStore();
      
      if (this.activeTabId && this.imageRawData) {
        // 創建新的視圖
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
            isActive: true,
            linkedProfileViewerId: null  // 初始化為 null，表示尚未綁定 ProfileViewer
          }
        };
        
        // 檢查標籤頁是否已有視圖群組
        const activeTab = spmDataStore.analysisTabs.find(tab => tab.id === this.activeTabId);
        
        if (activeTab) {
          if (!activeTab.viewerGroups || activeTab.viewerGroups.length === 0) {
            // 如果沒有群組，創建新群組
            const groupId = `group-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
            
            spmDataStore.updateAnalysisTabData(this.activeTabId, {
              viewerGroups: [{
                id: groupId,
                title: '數據視圖',
                viewers: [imageViewer],
                layout: 'horizontal'
              }]
            });
            
            // 更新活動群組ID
            this.activeGroupId = groupId;
            this.activeViewerId = imageViewer.id;
          } else {
            // 將所有現有視圖設為非活動
            const updatedViewers = activeTab.viewerGroups[0].viewers.map(viewer => ({
              ...viewer,
              props: {
                ...viewer.props,
                isActive: false
              }
            }));
            
            // 添加新視圖
            updatedViewers.push(imageViewer);
            
            // 更新群組
            const updatedGroups = [...activeTab.viewerGroups];
            updatedGroups[0] = {
              ...updatedGroups[0],
              viewers: updatedViewers
            };
            
            // 更新標籤頁
            spmDataStore.updateAnalysisTabData(this.activeTabId, {
              viewerGroups: updatedGroups
            });
            
            // 更新活動群組和視圖ID
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
          this.currentMeasuringViewerId = '';
          
          // 如果有目標剖面視圖，更新其數據
          if (data.targetProfileViewer) {
            this.updateProfileViewer(data.targetProfileViewer.id, this.profileData, this.roughness);
          }
          
          // 更新 ImageViewer 的測量模式狀態
          this.updateImageViewerMeasureMode(data.sourceViewerId, false);
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
    },
    
    /**
     * 更新特定 ImageViewer 的測量模式狀態
     */
    updateImageViewerMeasureMode(imageViewerId: string, mode: boolean) {
      const spmDataStore = useSpmDataStore();
      const location = spmDataStore.getViewerLocation(imageViewerId);
      
      if (!location) return;
      
      const { tabId, groupId, viewerIndex } = location;
      const tab = spmDataStore.analysisTabs.find(t => t.id === tabId);
      if (!tab || !tab.viewerGroups) return;
      
      const groupIndex = tab.viewerGroups.findIndex(g => g.id === groupId);
      if (groupIndex === -1) return;
      
      const group = tab.viewerGroups[groupIndex];
      const viewer = group.viewers[viewerIndex];
      
      // 確保是 ImageViewer
      if (viewer.component !== 'ImageViewer') return;
      
      // 更新 ImageViewer 的測量模式
      const updatedViewers = [...group.viewers];
      updatedViewers[viewerIndex] = {
        ...viewer,
        props: {
          ...viewer.props,
          profileMeasureMode: mode
        }
      };
      
      // 更新群組
      const updatedGroups = [...tab.viewerGroups];
      updatedGroups[groupIndex] = {
        ...group,
        viewers: updatedViewers
      };
      
      // 更新標籤頁
      spmDataStore.updateAnalysisTabData(tabId, {
        viewerGroups: updatedGroups
      });
    },
    
    /**
     * 切換測量模式
     */
    toggleMeasureMode(viewerId: string) {
      // 如果已經在測量其他視圖，先關閉該視圖的測量模式
      if (this.measureMode && this.currentMeasuringViewerId && this.currentMeasuringViewerId !== viewerId) {
        this.updateImageViewerMeasureMode(this.currentMeasuringViewerId, false);
      }
      
      // 切換當前視圖的測量模式
      this.measureMode = !this.measureMode;
      this.currentMeasuringViewerId = this.measureMode ? viewerId : '';
      
      // 更新視圖的測量模式狀態
      this.updateImageViewerMeasureMode(viewerId, this.measureMode);
    },
    
    /**
     * 清除錯誤消息
     */
    clearError() {
      this.errorMessage = '';
    },

    /**
     * 創建新的視圖群組 - 在單容器模式下不使用
     */
    createNewViewerGroup(tabId: string, title: string, viewers: any[] = []) {
      const spmDataStore = useSpmDataStore();
      
      // 獲取標籤頁
      const tab = spmDataStore.analysisTabs.find(t => t.id === tabId);
      if (!tab) return '';
      
      // 在單容器模式下，只使用第一個容器
      if (!tab.viewerGroups || tab.viewerGroups.length === 0) {
        // 如果沒有群組，創建新群組
        const groupId = `group-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
        
        spmDataStore.updateAnalysisTabData(tabId, {
          viewerGroups: [{
            id: groupId,
            title: title || 'Data Group',
            viewers: viewers || [],
            layout: 'horizontal'
          }]
        });
        
        this.activeGroupId = groupId;
        
        // 如果有視圖，設置第一個視圖為活動視圖
        if (viewers && viewers.length > 0) {
          this.activeViewerId = viewers[0].id;
        }
        
        return groupId;
      } else {
        // 如果已有群組，將視圖添加到現有群組
        const group = tab.viewerGroups[0];
        const updatedGroups = [...tab.viewerGroups];
        
        updatedGroups[0] = {
          ...group,
          viewers: [...group.viewers, ...viewers]
        };
        
        spmDataStore.updateAnalysisTabData(tabId, {
          viewerGroups: updatedGroups
        });
        
        // 如果有新視圖，設置最後一個視圖為活動視圖
        if (viewers && viewers.length > 0) {
          this.activeViewerId = viewers[viewers.length - 1].id;
        }
        
        return group.id;
      }
    },

    /**
     * 更新 ImageViewer 的綁定關係
     */
    updateImageViewerBinding(imageViewerId: string, profileViewerId: string | null) {
      const spmDataStore = useSpmDataStore();
      const location = spmDataStore.getViewerLocation(imageViewerId);
      
      if (!location) return;
      
      const { tabId, groupId, viewerIndex } = location;
      const tab = spmDataStore.analysisTabs.find(t => t.id === tabId);
      if (!tab || !tab.viewerGroups) return;
      
      const groupIndex = tab.viewerGroups.findIndex(g => g.id === groupId);
      if (groupIndex === -1) return;
      
      const group = tab.viewerGroups[groupIndex];
      const viewer = group.viewers[viewerIndex];
      
      // 確保是 ImageViewer
      if (viewer.component !== 'ImageViewer') return;
      
      // 更新 ImageViewer 的 linkedProfileViewerId 屬性
      const updatedViewers = [...group.viewers];
      updatedViewers[viewerIndex] = {
        ...viewer,
        props: {
          ...viewer.props,
          linkedProfileViewerId: profileViewerId
        }
      };
      
      // 更新群組
      const updatedGroups = [...tab.viewerGroups];
      updatedGroups[groupIndex] = {
        ...group,
        viewers: updatedViewers
      };
      
      // 更新標籤頁
      spmDataStore.updateAnalysisTabData(tabId, {
        viewerGroups: updatedGroups
      });
    },

    /**
     * 創建線性剖面視圖 - 單容器模式，處理 ImageViewer 和 ProfileViewer 的綁定關係
     */
    async createLineProfile(sourceViewerId: string) {
      // 首先找到源視圖所在的標籤頁和群組
      const spmDataStore = useSpmDataStore();
      const location = spmDataStore.getViewerLocation(sourceViewerId);
      
      if (!location) return;
      
      const { tabId, groupId, viewerIndex } = location;
      const tab = spmDataStore.analysisTabs.find(t => t.id === tabId);
      if (!tab || !tab.viewerGroups) return;
      
      const sourceGroup = tab.viewerGroups.find(g => g.id === groupId);
      if (!sourceGroup) return;
      
      const sourceViewer = sourceGroup.viewers[viewerIndex];
      if (!sourceViewer || sourceViewer.component !== 'ImageViewer') return;
      
      // 檢查此 ImageViewer 是否已經有綁定的 ProfileViewer
      if (sourceViewer.props.linkedProfileViewerId) {
        console.log("此 ImageViewer 已綁定 ProfileViewer:", sourceViewer.props.linkedProfileViewerId);
        
        // 找到並激活已存在的 ProfileViewer
        for (const group of tab.viewerGroups) {
          for (const viewer of group.viewers) {
            if (viewer.id === sourceViewer.props.linkedProfileViewerId) {
              // 設置為活動視圖
              this.activeViewerId = viewer.id;
              return viewer.id;
            }
          }
        }
        
        // 如果找不到已綁定的 ProfileViewer (可能已被刪除)，則重置 ImageViewer 的綁定
        this.updateImageViewerBinding(sourceViewerId, null);
      }
      
      // 啟動測量模式
      this.toggleMeasureMode(sourceViewerId);
      
      // 生成唯一的剖面視圖ID
      const profileViewerId = `viewer-profile-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
      
      // 創建新的剖面視圖
      const profileViewer = {
        id: profileViewerId,
        component: 'ProfileViewer',
        props: {
          id: profileViewerId,
          title: `剖面圖 - ${sourceViewer.props.title || 'Image'}`,
          physUnit: sourceViewer.props.physUnit || 'nm',
          sourceViewerId: sourceViewerId,
          sourceViewerTitle: sourceViewer.props.title || 'Image',
          isActive: true,
          allowClose: true
        }
      };
      
      // 單容器模式: 將所有視圖添加到同一個容器中
      // 將所有現有視圖設為非活動
      const updatedViewers = sourceGroup.viewers.map((viewer, idx) => {
        if (idx === viewerIndex) {
          // 為源 ImageViewer 添加指向 ProfileViewer 的綁定
          return {
            ...viewer,
            props: {
              ...viewer.props,
              isActive: false,
              linkedProfileViewerId: profileViewerId,  // 添加綁定關係
              profileMeasureMode: true,  // 啟用測量模式
              targetProfileViewer: { id: profileViewerId }  // 設置目標 ProfileViewer
            }
          };
        }
        return {
          ...viewer,
          props: {
            ...viewer.props,
            isActive: false
          }
        };
      });
      
      // 添加新視圖
      updatedViewers.push(profileViewer);
      
      // 更新群組
      const updatedGroups = [...tab.viewerGroups];
      const groupIndex = updatedGroups.indexOf(sourceGroup);
      
      updatedGroups[groupIndex] = {
        ...sourceGroup,
        viewers: updatedViewers
      };
      
      // 更新標籤頁
      spmDataStore.updateAnalysisTabData(tabId, {
        viewerGroups: updatedGroups
      });
      
      // 更新活動視圖ID
      this.activeViewerId = profileViewerId;
      
      return profileViewerId;
    },

    /**
     * 移除視圖 - 單容器模式，處理綁定關係解除
     */
    removeViewer(viewerId: string) {
      console.log("執行移除視圖:", viewerId);
      
      const spmDataStore = useSpmDataStore();
      const location = spmDataStore.getViewerLocation(viewerId);
      
      if (!location) return;
      
      const { tabId, groupId, viewerIndex } = location;
      const tab = spmDataStore.analysisTabs.find(t => t.id === tabId);
      
      if (!tab || !tab.viewerGroups) return;
      
      const groupIndex = tab.viewerGroups.findIndex(g => g.id === groupId);
      if (groupIndex === -1) return;
      
      const group = tab.viewerGroups[groupIndex];
      const viewer = group.viewers[viewerIndex];
      
      // 檢查要移除的是否為 ProfileViewer
      if (viewer.component === 'ProfileViewer' && viewer.props.sourceViewerId) {
        // 如果是 ProfileViewer，則需要解除與 ImageViewer 的綁定
        this.updateImageViewerBinding(viewer.props.sourceViewerId, null);
        
        // 如果當前正在測量，且測量的是關聯的 ImageViewer，則關閉測量模式
        if (this.measureMode && this.currentMeasuringViewerId === viewer.props.sourceViewerId) {
          this.measureMode = false;
          this.currentMeasuringViewerId = '';
          this.updateImageViewerMeasureMode(viewer.props.sourceViewerId, false);
        }
      }
      
      // 檢查要移除的是否為 ImageViewer
      if (viewer.component === 'ImageViewer' && viewer.props.linkedProfileViewerId) {
        // 如果是 ImageViewer，則需要同時移除關聯的 ProfileViewer
        const linkedViewerId = viewer.props.linkedProfileViewerId;
        
        // 首先找到關聯的 ProfileViewer
        let linkedViewerIndex = -1;
        for (let i = 0; i < group.viewers.length; i++) {
          if (group.viewers[i].id === linkedViewerId) {
            linkedViewerIndex = i;
            break;
          }
        }
        
        // 移除指定的視圖和關聯的 ProfileViewer
        const updatedViewers = [...group.viewers];
        
        // 注意要處理索引變化，如果 linkedViewerIndex > viewerIndex
        if (linkedViewerIndex !== -1) {
          if (linkedViewerIndex > viewerIndex) {
            // 先移除 viewerIndex 位置的 viewer
            updatedViewers.splice(viewerIndex, 1);
            // 由於前面已移除一個元素，linkedViewerIndex 要減 1
            updatedViewers.splice(linkedViewerIndex - 1, 1);
          } else {
            // 先移除 linkedViewerIndex 位置的 viewer
            updatedViewers.splice(linkedViewerIndex, 1);
            // 由於前面已移除一個元素，viewerIndex 要減 1
            updatedViewers.splice(viewerIndex - 1, 1);
          }
        } else {
          // 如果找不到關聯的 ProfileViewer，只移除當前視圖
          updatedViewers.splice(viewerIndex, 1);
        }
        
        // 更新群組
        const updatedGroups = [...tab.viewerGroups];
        updatedGroups[groupIndex] = {
          ...group,
          viewers: updatedViewers
        };
        
        // 更新標籤頁
        spmDataStore.updateAnalysisTabData(tabId, {
          viewerGroups: updatedGroups
        });
        
        // 如果被移除的是當前活動視圖，則更新活動視圖ID
        if (this.activeViewerId === viewerId || this.activeViewerId === linkedViewerId) {
          // 如果還有其他視圖，將第一個視圖設為活動
          if (updatedViewers.length > 0) {
            this.activeViewerId = updatedViewers[0].id;
          } else {
            this.activeViewerId = '';
          }
        }
        
        // 如果正在測量模式，關閉測量模式
        if (this.measureMode && (this.currentMeasuringViewerId === viewerId)) {
          this.measureMode = false;
          this.currentMeasuringViewerId = '';
        }
        
        return;
      }
      
      // 一般情況下，移除指定的視圖
      const updatedViewers = [...group.viewers];
      updatedViewers.splice(viewerIndex, 1);
      
      // 更新群組
      const updatedGroups = [...tab.viewerGroups];
      updatedGroups[groupIndex] = {
        ...group,
        viewers: updatedViewers
      };
      
      // 更新標籤頁
      spmDataStore.updateAnalysisTabData(tabId, {
        viewerGroups: updatedGroups
      });
      
      // 如果被移除的是當前活動視圖，則更新活動視圖ID
      if (this.activeViewerId === viewerId) {
        // 如果還有其他視圖，將第一個視圖設為活動
        if (updatedViewers.length > 0) {
          this.activeViewerId = updatedViewers[0].id;
        } else {
          this.activeViewerId = '';
        }
      }
      
      // 如果正在測量模式，關閉測量模式
      if (this.measureMode && this.currentMeasuringViewerId === viewerId) {
        this.measureMode = false;
        this.currentMeasuringViewerId = '';
      }
    }
  }
});