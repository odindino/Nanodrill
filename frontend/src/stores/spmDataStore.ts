// src/stores/spmDataStore.ts
import { defineStore } from 'pinia';

interface FileInfo {
  name: string;
  path: string;
  type: string;
  number: number;
  modTime: number;
  modTimeStr: string;
  hasDatFile?: boolean;
}

interface TxtParameters {
  [key: string]: any;
}

interface FileContent {
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
    error: ''
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
      // 處理檔案列表，標記哪些 txt 檔案有對應的 dat 檔案
      const datFileNumbers = new Set<number>();
      
      files.forEach(file => {
        if (file.type === 'dat') {
          datFileNumbers.add(file.number);
        }
      });
      
      this.files = files.map(file => ({
        ...file,
        hasDatFile: file.type === 'txt' && datFileNumbers.has(file.number)
      }));
    },
    // setFiles(files: FileInfo[]) {
    //     // 找出所有 It_to_PC_Matrix.dat 檔案的編號
    //     const itToPcMatrixNumbers = new Set<number>();
        
    //     files.forEach(file => {
    //       if (file.type === 'dat' && file.name.includes('It_to_PC_Matrix.dat')) {
    //         itToPcMatrixNumbers.add(file.number);
    //       }
    //     });
        
    //     this.files = files.map(file => ({
    //       ...file,
    //       hasDatFile: file.type === 'txt' && itToPcMatrixNumbers.has(file.number)
    //     }));
    //   },
    
    selectFile(file: FileInfo) {
      this.selectedFile = file;
    },
    
    clearSelection() {
      this.selectedFile = null;
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
    }
  }
});