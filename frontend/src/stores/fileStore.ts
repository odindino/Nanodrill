import { defineStore } from 'pinia';
import type { SPMFile } from '../types/index';

export const useFileStore = defineStore('file', {
  state: () => ({
    currentDirectory: '',
    files: [] as SPMFile[],
    statusMessage: '就緒'
  }),
  
  actions: {
    setCurrentDirectory(directory: string) {
      this.currentDirectory = directory;
    },
    
    setFiles(files: SPMFile[]) {
      this.files = files;
    },
    
    addFile(file: SPMFile) {
      // 檢查是否已存在相同路徑的檔案
      const existingIndex = this.files.findIndex(f => f.path === file.path);
      
      if (existingIndex >= 0) {
        // 更新現有檔案
        this.files[existingIndex] = file;
      } else {
        // 添加新檔案
        this.files.push(file);
      }
    },
    
    removeFile(filePath: string) {
      this.files = this.files.filter(file => file.path !== filePath);
    },
    
    clearFiles() {
      this.files = [];
    },
    
    setStatusMessage(message: string) {
      this.statusMessage = message;
    }
  }
});