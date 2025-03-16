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

export const useSpmDataStore = defineStore('spmData', {
  state: () => ({
    currentDirectory: '',
    files: [] as FileInfo[],
    selectedFile: null as FileInfo | null,
    fileContents: {} as Record<string, FileContent>,
    loading: false,
    error: '',
    currentView: 'welcome' as 'welcome' | 'data-view' | 'analysis'
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
    }
  }
});