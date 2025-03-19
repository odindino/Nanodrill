<!-- >src/components/FileSelector.vue -->
<template>
    <div class="w-[350px] h-full bg-white shadow-md flex flex-col border-r border-gray-200">
      <div class="flex items-center px-4 py-3 bg-gray-50 border-b border-gray-200">
        <button class="p-1.5 rounded-full hover:bg-gray-200 text-gray-600 focus:outline-none" @click="$emit('close')">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <h2 class="ml-2 text-base font-medium text-gray-800 flex-1 text-center">資料檔案選擇器</h2>
      </div>
      
      <div class="p-4 flex flex-col gap-4">
        <button 
          class="w-full py-2.5 px-4 bg-primary hover:bg-primary-dark text-white font-medium rounded transition-colors focus:outline-none focus:ring-2 focus:ring-primary-light"
          @click="openFolderDialog"
        >
          選擇資料夾
        </button>
        
        <div v-if="folderPath" class="bg-gray-50 rounded border border-gray-200 overflow-hidden">
          <div class="px-3 py-2 text-xs font-medium text-gray-600 bg-gray-100 border-b border-gray-200">
            當前路徑:
          </div>
          <div class="p-3 text-sm text-primary font-mono bg-white break-all max-h-16 overflow-y-auto">
            {{ folderPath }}
          </div>
        </div>
      </div>
      
      <div v-if="errorMessage" class="mx-4 mb-4 px-4 py-3 bg-error-light/20 text-error-dark text-sm rounded border-l-4 border-error">
        {{ errorMessage }}
      </div>
      
      <div v-if="folderPath && filteredAndSortedFiles.length > 0" class="flex-1 flex flex-col px-4 pb-4 overflow-hidden">
        <div class="flex flex-col space-y-3 mb-3">
          <div class="flex items-center space-x-2">
            <div class="relative flex-1">
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="搜尋檔案名稱..." 
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
              />
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            
            <div class="flex items-center space-x-2">
              <label for="sort-select" class="text-xs text-gray-600 whitespace-nowrap">排序:</label>
              <select 
                id="sort-select" 
                v-model="sortOption" 
                class="text-xs border border-gray-300 rounded py-1.5 px-2 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary bg-white"
              >
                <option value="time_desc">時間 (新到舊)</option>
                <option value="time_asc">時間 (舊到新)</option>
                <option value="name_asc">名稱 (A-Z)</option>
                <option value="name_desc">名稱 (Z-A)</option>
                <option value="number_asc">編號 (小到大)</option>
                <option value="number_desc">編號 (大到小)</option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="flex-1 overflow-hidden border border-gray-200 rounded">
          <div class="overflow-y-auto h-full">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50 sticky top-0">
                <tr>
                  <th scope="col" class="px-4 py-2 text-left text-xs font-medium text-gray-500 tracking-wider">檔案名稱</th>
                  <th scope="col" class="px-4 py-2 text-left text-xs font-medium text-gray-500 tracking-wider">修改時間</th>
                  <th scope="col" class="px-4 py-2 text-center text-xs font-medium text-gray-500 tracking-wider w-20">操作</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr 
                  v-for="file in filteredAndSortedFiles" 
                  :key="file.path"
                  :class="[
                    file.hasDatFile ? 'bg-secondary-50/30' : '',
                    isSelected(file) ? 'bg-primary-50' : '',
                    'hover:bg-gray-50'
                  ]"
                >
                  <td class="px-4 py-2 whitespace-nowrap text-sm">
                    <div class="flex items-center space-x-2">
                      <span v-if="file.hasDatFile" class="text-secondary text-lg" title="該檔案有對應的 IV 曲線數據">⚡</span>
                      <span class="truncate max-w-[150px]" :title="file.name">{{ file.name }}</span>
                    </div>
                  </td>
                  <td class="px-4 py-2 whitespace-nowrap text-xs text-gray-500">
                    {{ file.modTimeStr }}
                  </td>
                  <td class="px-4 py-2 whitespace-nowrap text-sm text-center">
                    <button 
                      @click="viewFile(file)" 
                      class="inline-flex items-center px-2.5 py-1 border border-transparent text-xs font-medium rounded text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                    >
                      查看
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <div v-else-if="folderPath && filteredAndSortedFiles.length === 0" class="mt-8 mx-4 p-6 text-center text-gray-500 bg-gray-50 rounded border border-gray-200">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
        </svg>
        <p>資料夾中沒有找到 .txt 檔案</p>
      </div>
    </div>
  </template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue';
import { useSpmDataStore } from '../stores/spmDataStore';

interface FileInfo {
  name: string;
  path: string;
  type: string;
  number: number;
  modTime: number;
  modTimeStr: string;
  hasDatFile: boolean;
}

declare global {
  interface Window {
    pywebview: {
      api: {
        open_folder_dialog: () => Promise<any>;
        get_folder_files: (path: string) => Promise<any>;
        get_txt_file_content: (path: string) => Promise<any>;
      };
    };
  }
}

export default defineComponent({
  name: 'FileSelector',
  emits: ['close'],
  setup() {
    const spmDataStore = useSpmDataStore();
    const folderPath = ref<string>('');
    const errorMessage = ref<string>('');
    const files = ref<FileInfo[]>([]);
    const searchQuery = ref<string>('');
    const sortOption = ref<string>('time_desc');
    
    // 過濾並排序檔案 (只顯示 .txt 檔案)
    const filteredAndSortedFiles = computed(() => {
      // 先過濾 .txt 檔案
      let result = files.value.filter(file => {
        // 只顯示 .txt 檔案，並根據搜尋條件過濾
        return file.type === 'txt' && (!searchQuery.value || file.name.toLowerCase().includes(searchQuery.value.toLowerCase()));
      });
      
      // 然後排序
      return result.sort((a, b) => {
        switch (sortOption.value) {
          case 'time_desc':
            return b.modTime - a.modTime;
          case 'time_asc':
            return a.modTime - b.modTime;
          case 'name_asc':
            return a.name.localeCompare(b.name);
          case 'name_desc':
            return b.name.localeCompare(a.name);
          case 'number_asc':
            return a.number - b.number;
          case 'number_desc':
            return b.number - a.number;
          default:
            return 0;
        }
      });
    });
    
    // 開啟資料夾選擇對話框
    const openFolderDialog = async () => {
      try {
        errorMessage.value = '';
        
        // 呼叫 Python 後端 API 開啟資料夾選擇器
        const result = await window.pywebview.api.open_folder_dialog();
        
        if (result.success) {
          folderPath.value = result.directory;
          files.value = processFiles(result.files || []);
          spmDataStore.setCurrentDirectory(result.directory);
          spmDataStore.setFiles(files.value);
        } else {
          if (result.message) {
            errorMessage.value = result.message;
          } else if (result.error) {
            errorMessage.value = `錯誤: ${result.error}`;
          }
        }
      } catch (error) {
        console.error('開啟資料夾對話框失敗:', error);
        errorMessage.value = `系統錯誤: ${error}`;
      }
    };
    
    // 從檔名中提取編號
    const extractNumberFromFilename = (filename: string): number => {
      // 對於 txt 檔案，尋找最後一個底線後面的數字 (支援多位數)
      const numberMatch = filename.match(/_(\d+)\.txt$/i);
      if (numberMatch && numberMatch[1]) {
        return parseInt(numberMatch[1], 10);
      }
      return -1; // 如果沒有找到編號，返回-1
    };
    
    // 處理檔案列表，標記哪些 txt 檔案有對應的 dat 檔案
    const processFiles = (fileList: any[]): FileInfo[] => {
      // 先將檔案分類為 txt 和 dat
      const txtFiles = fileList.filter(file => file.type === 'txt');
      const datFiles = fileList.filter(file => file.type === 'dat');
      
      // 從 txt 檔案中提取編號
      const txtNumberMap = new Map<number, string>();
      
      txtFiles.forEach(file => {
        const number = extractNumberFromFilename(file.name);
        if (number >= 0) {
          txtNumberMap.set(number, file.name);
        }
      });
      
      // 檢查每個 dat 檔案名稱是否對應到 txt 檔案的編號
      const txtWithDat = new Set<number>();
      
      datFiles.forEach(datFile => {
        txtNumberMap.forEach((txtName, number) => {
          // 處理不同長度的編號格式 (例如: 01、1、001 等)
          const numberFormats = [
            `_${number}_`, 
            `_${number}.`,
            `_${number}I`,  // 針對 "01It_to_PC_Matrix.dat" 格式
            `_${number}L`,  // 針對 "01Lia1R_Matrix.dat" 格式
            `_${String(number).padStart(2, '0')}`,  // 補零到2位數 (01, 02...)
          ];
          
          // 檢查 dat 檔案名稱是否包含任一編號格式
          if (numberFormats.some(format => datFile.name.includes(format))) {
            txtWithDat.add(number);
          }
        });
      });
      
      // 標記有對應 dat 檔案的 txt 檔案
      return fileList.map(file => {
        if (file.type === 'txt') {
          const number = extractNumberFromFilename(file.name);
          return {
            ...file,
            number: number,
            hasDatFile: number >= 0 && txtWithDat.has(number)
          };
        } else {
          return {
            ...file,
            number: -1,
            hasDatFile: false
          };
        }
      });
    };
    
    // 檢查檔案是否被選中
    const isSelected = (file: FileInfo) => {
      return spmDataStore.selectedFile && spmDataStore.selectedFile.path === file.path;
    };
    
    // 查看文件
    const viewFile = async (file: FileInfo) => {
      try {
        if (file.type === 'txt') {
          // 將檔案設為選中
          spmDataStore.selectFile(file);
          
          // 獲取檔案內容
          const result = await window.pywebview.api.get_txt_file_content(file.path);
          if (result.success) {
            spmDataStore.setFileContent(file.path, {
              content: result.content,
              parameters: result.parameters,
              relatedFiles: result.relatedFiles
            });
            
            // 關閉檔案選擇器
            setTimeout(() => {
              // 使用 setTimeout 避免可能的渲染更新衝突
              // 這樣使用者可以先看到選擇的檔案被高亮，然後再關閉選擇器
              // 降低學習曲線，讓用戶知道他們已經選擇了什麼
            }, 300);
          } else {
            errorMessage.value = result.error || '無法讀取文件內容';
          }
        }
      } catch (error) {
        console.error('查看文件失敗:', error);
        errorMessage.value = `系統錯誤: ${error}`;
      }
    };
    
    // 如果已有選擇的目錄，自動加載
    if (spmDataStore.currentDirectory) {
      folderPath.value = spmDataStore.currentDirectory;
      files.value = spmDataStore.files.map(file => ({
        ...file,
        hasDatFile: file.hasDatFile || false
      }));
    }
    
    return {
      folderPath,
      errorMessage,
      files,
      searchQuery,
      sortOption,
      filteredAndSortedFiles,
      openFolderDialog,
      viewFile,
      isSelected
    };
  }
});
</script>

