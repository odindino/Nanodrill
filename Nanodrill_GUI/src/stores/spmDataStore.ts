// src/stores/spmDataStore.ts
import { defineStore } from 'pinia';

export interface FileInfo {
  name: string;
  path: string;
  type: string;
  number: number;
  modTime: number;
  modTimeStr: string;
  hasDatFile?: boolean;
}

export interface TxtParameters {
  [key: string]: any;
}

export interface FileContent {
  content: string;
  parameters: TxtParameters;
  relatedFiles: FileInfo[];
}

// 新增分析標籤頁介面
export interface AnalysisTab {
  id: string;
  title: string;
  fileId: string;
  fileType: 'topo' | 'iv' | 'lia';
  sourcePath: string;
  imageData?: string;
  imageRawData?: number[][]; // 新增原始數據欄位
  statistics?: any;
  physUnit?: string;
  dimensions?: {
    width: number;
    height: number;
    xRange: number;
    yRange: number;
  };
  relatedFiles?: FileInfo[];
  currentFileName?: string;
  colormap: string;
  zScale: number;
  txtContent?: string;
  parameters?: Record<string, string>;
  viewerGroups?: ViewerGroup[]; // 添加視圖群組支持
  activeGroupId?: string; // 活動群組ID
}

// 視圖群組介面
export interface ViewerGroup {
  id: string;
  title: string;
  viewers: Viewer[];
  layout: 'horizontal' | 'vertical';
  height?: number;
}

// 視圖介面
export interface Viewer {
  id: string;
  component: string;
  props: Record<string, any>;
  title?: string;
}

export const useSpmDataStore = defineStore('spmData', {
  state: () => ({
    currentDirectory: '',
    files: [] as FileInfo[],
    selectedFile: null as FileInfo | null,
    fileContents: {} as Record<string, FileContent>,
    loading: false,
    error: '',
    currentView: 'welcome' as 'welcome' | 'data-view' | 'analysis',
    // 新增分析標籤頁相關狀態
    analysisTabs: [] as AnalysisTab[],
    activeAnalysisTabId: '' as string
  }),
  
  getters: {
    txtFiles: (state) => state.files.filter(file => file.type === 'txt'),
    datFiles: (state) => state.files.filter(file => file.type === 'dat'),
    hasSelectedFile: (state) => state.selectedFile !== null,
    selectedFileContent: (state) => 
      state.selectedFile && state.fileContents[state.selectedFile.path]
        ? state.fileContents[state.selectedFile.path]
        : null
  },
  
  actions: {
    setCurrentDirectory(directory: string) {
      this.currentDirectory = directory;
    },
    
    setFiles(files: FileInfo[]) {
      this.files = files;
    },
    
    selectFile(file: FileInfo) {
      this.selectedFile = file;
      this.currentView = 'data-view';
    },
    
    clearSelection() {
      this.selectedFile = null;
      this.currentView = 'welcome';
    },
    
    setFileContent(filePath: string, content: FileContent) {
      this.fileContents[filePath] = content;
    },
    
    setLoading(isLoading: boolean) {
      this.loading = isLoading;
    },
    
    setError(error: string) {
      this.error = error;
    },
    
    clearError() {
      this.error = '';
    },
    
    setCurrentView(view: 'welcome' | 'data-view' | 'analysis') {
      this.currentView = view;
    },

    // 添加新標籤頁
    addNewTab(tabData: AnalysisTab) {
      this.analysisTabs.push(tabData);
    },

    // 獲取視圖所屬的標籤頁和群組
    getViewerLocation(viewerId: string): { tabId: string, groupId: string, viewerIndex: number } | null {
      for (const tab of this.analysisTabs) {
        if (tab.viewerGroups) {
          for (const group of tab.viewerGroups) {
            const viewerIndex = group.viewers.findIndex(v => v.id === viewerId);
            if (viewerIndex !== -1) {
              return {
                tabId: tab.id,
                groupId: group.id,
                viewerIndex
              };
            }
          }
        }
      }
      return null;
    },

    // 新增分析標籤頁
    addAnalysisTab(file: FileInfo, content: FileContent) {
      // 檢查該檔案是否已經開啟了標籤頁
      const existingTabIndex = this.analysisTabs.findIndex(tab => tab.fileId === file.path);
      
      if (existingTabIndex !== -1) {
        // 如果已經存在，切換到該標籤頁
        this.activeAnalysisTabId = this.analysisTabs[existingTabIndex].id;
      } else {
        // 產生唯一 ID
        const tabId = `tab-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
        
        // 處理檔案路徑，確保使用正確的分隔符
        let filePath = file.path;
        let dirPath = filePath.substring(0, filePath.lastIndexOf(filePath.includes('/') ? '/' : '\\') + 1);
        
        console.log('檔案路徑:', filePath);
        console.log('目錄路徑:', dirPath);
        
        // 創建新標籤頁
        const newTab: AnalysisTab = {
          id: tabId,
          title: file.name,
          fileId: file.path,
          fileType: 'topo', // 預設為形貌圖類型
          sourcePath: dirPath, // 記錄檔案來源路徑
          relatedFiles: content.relatedFiles,
          colormap: 'Oranges', // 預設色彩映射
          zScale: 1.0, // 預設高度縮放
          txtContent: content.content, // 存儲txt文件內容
          parameters: content.parameters,
          viewerGroups: [] // 初始化空視圖群組
        };
        
        // 添加到標籤頁列表
        this.analysisTabs.push(newTab);
        
        // 設定為當前標籤頁
        this.activeAnalysisTabId = tabId;
      }
      
      // 切換到分析視圖
      this.currentView = 'analysis';
    },
    
    // 移除分析標籤頁
    removeAnalysisTab(tabId: string) {
      const tabIndex = this.analysisTabs.findIndex(tab => tab.id === tabId);
      
      if (tabIndex !== -1) {
        // 移除標籤頁
        this.analysisTabs.splice(tabIndex, 1);
        
        // 如果沒有標籤頁，切換回歡迎視圖
        if (this.analysisTabs.length === 0) {
          this.activeAnalysisTabId = '';
          this.currentView = 'welcome';
        } else {
          // 如果移除的是當前標籤頁，切換到最近的標籤頁
          if (this.activeAnalysisTabId === tabId) {
            // 如果有下一個標籤頁，切換到下一個，否則切換到上一個
            const newIndex = tabIndex < this.analysisTabs.length ? tabIndex : tabIndex - 1;
            this.activeAnalysisTabId = this.analysisTabs[newIndex].id;
          }
        }
      }
    },
    
    // 設置當前活動的分析標籤頁
    setActiveAnalysisTab(tabId: string) {
      this.activeAnalysisTabId = tabId;
    },
    
    // 更新分析標籤頁數據
    updateAnalysisTabData(tabId: string, data: Partial<AnalysisTab>) {
      const tabIndex = this.analysisTabs.findIndex(tab => tab.id === tabId);
      
      if (tabIndex !== -1) {
        // 更新標籤頁的數據
        this.analysisTabs[tabIndex] = {
          ...this.analysisTabs[tabIndex],
          ...data
        };
      }
    }
  }
});