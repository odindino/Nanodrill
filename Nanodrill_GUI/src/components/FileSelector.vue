<!-- src/components/FileSelector.vue -->
<template>
  <div :class="['h-full bg-white shadow-md flex flex-col border-r border-neutral-200 overflow-hidden', { 'resizing': isResizing }]" 
       :style="{ width: selectorWidth + 'px' }">
    <!-- 標題列 - 固定在頂部 -->
    <div class="flex items-center px-4 py-3 bg-neutral-100 border-b border-neutral-200 flex-shrink-0">
      <button class="p-1.5 rounded-full hover:bg-neutral-200 text-neutral-600 focus:outline-none" @click="$emit('close')">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>
      <h2 class="ml-2 text-base font-medium text-neutral-800 flex-1 text-center">資料檔案選擇器</h2>
    </div>
    
    <!-- 操作區 - 固定在頂部 -->
    <div class="p-4 flex flex-col gap-4 flex-shrink-0">
      <button 
        class="w-full py-2.5 px-4 bg-secondary-500 hover:bg-secondary-600 text-white font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:ring-offset-2"
        @click="openFolderDialog"
      >
        選擇資料夾
      </button>
      
      <div v-if="folderPath" class="bg-neutral-50 rounded-md border border-neutral-200 overflow-hidden">
        <div class="px-3 py-2 text-xs font-medium text-neutral-600 bg-neutral-100 border-b border-neutral-200">
          當前路徑:
        </div>
        <div class="p-3 text-sm text-secondary-600 font-mono bg-white break-all max-h-16 overflow-y-auto">
          {{ folderPath }}
        </div>
      </div>
    </div>
    
    <!-- 錯誤訊息區 - 可以捲動 -->
    <div v-if="errorMessage" class="mx-4 mb-4 px-4 py-3 bg-error-light/20 text-error-dark text-sm rounded border-l-4 border-error flex-shrink-0">
      {{ errorMessage }}
    </div>
    
    <!-- 檔案列表區 - 可以捲動 -->
    <div v-if="folderPath && filteredAndSortedFiles.length > 0" class="flex-1 flex flex-col px-4 pb-4 overflow-hidden min-h-0">
      <!-- 搜尋和排序控制項 - 固定在頂部 -->
      <div class="flex flex-col space-y-3 mb-3 flex-shrink-0">
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
      
      <!-- 表格容器 - 可捲動區域 -->
      <div class="flex-1 border border-gray-200 rounded overflow-auto min-h-0">
        <table class="w-full table-fixed divide-y divide-gray-200">
          <thead class="bg-gray-50 sticky top-0 z-10">
            <tr>
              <th 
                class="px-4 py-2 text-left text-xs font-medium text-gray-500 tracking-wider relative"
                :style="{ width: columnWidths.filename + 'px' }"
              >
                檔案名稱
                <div class="column-resizer" @mousedown="startResize($event, 'filename')"></div>
              </th>
              <th 
                class="px-4 py-2 text-left text-xs font-medium text-gray-500 tracking-wider relative"
                :style="{ width: columnWidths.time + 'px' }"
              >
                修改時間
                <div class="column-resizer" @mousedown="startResize($event, 'time')"></div>
              </th>
              <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 tracking-wider w-20">操作</th>
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
              <td class="px-4 py-2 text-sm" :style="{ maxWidth: columnWidths.filename + 'px' }">
                <div class="flex items-center space-x-2 overflow-hidden">
                  <span v-if="file.hasDatFile" class="text-secondary flex-shrink-0 text-lg" title="該檔案有對應的 IV 曲線數據">⚡</span>
                  <span class="truncate" :title="file.name">{{ file.name }}</span>
                </div>
              </td>
              <td class="px-4 py-2 text-xs text-gray-500 truncate" :style="{ maxWidth: columnWidths.time + 'px' }">
                {{ file.modTimeStr }}
              </td>
              <td class="px-4 py-2 text-sm text-center">
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
    
    <!-- 空檔案夾提示 -->
    <div v-else-if="folderPath && filteredAndSortedFiles.length === 0" class="mt-8 mx-4 p-6 text-center text-gray-500 bg-gray-50 rounded border border-gray-200 flex-shrink-0">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
      </svg>
      <p>資料夾中沒有找到 .txt 檔案</p>
    </div>
    
    <!-- 可調整寬度的把手 -->
    <div class="resize-handle" @mousedown="startResizingWidth"></div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { useSpmDataStore } from '../stores/spmDataStore';
import { useUserPreferencesStore } from '../stores/userPreferencesStore';

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
  emits: ['close', 'width-changed'],
  setup(props, { emit }) {
    const spmDataStore = useSpmDataStore();
    const userPreferencesStore = useUserPreferencesStore();
    
    const folderPath = ref<string>('');
    const errorMessage = ref<string>('');
    const files = ref<FileInfo[]>([]);
    const searchQuery = ref<string>('');
    
    // 使用儲存的偏好設定
    const sortOption = ref<string>(userPreferencesStore.sortOption);
    const selectorWidth = ref<number>(userPreferencesStore.fileSelectorWidth);
    const columnWidths = ref({
      filename: userPreferencesStore.columnWidths.filename,
      time: userPreferencesStore.columnWidths.time
    });
    
    // 監視排序選項變更並保存
    watch(sortOption, (newValue) => {
      userPreferencesStore.setSortOption(newValue);
    });
    
    // 可調整寬度相關狀態
    const isResizing = ref(false);
    const startX = ref(0);
    const startWidth = ref(0);
    
    // 可調整欄位寬度相關狀態
    const resizingColumn = ref<string | null>(null);
    const columnResizeStartX = ref(0);
    const columnStartWidth = ref(0);
    
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
          
          // 儲存最後開啟的目錄
          userPreferencesStore.setLastDirectory(result.directory);
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
          } else {
            errorMessage.value = result.error || '無法讀取文件內容';
          }
        }
      } catch (error) {
        console.error('查看文件失敗:', error);
        errorMessage.value = `系統錯誤: ${error}`;
      }
    };
    
    // 開始調整選擇器寬度
    const startResizingWidth = (e: MouseEvent) => {
      e.preventDefault();
      isResizing.value = true;
      startX.value = e.clientX;
      startWidth.value = selectorWidth.value;
      
      // 添加全局滑鼠事件
      document.addEventListener('mousemove', onMouseMoveForPanel);
      document.addEventListener('mouseup', onMouseUpForPanel);
    };
    
    // 滑鼠移動時調整選擇器寬度
    const onMouseMoveForPanel = (e: MouseEvent) => {
      if (!isResizing.value) return;
      
      const newWidth = startWidth.value + (e.clientX - startX.value);
      // 設定最小和最大寬度
      selectorWidth.value = Math.max(300, Math.min(800, newWidth));
      
      // 通知父元件寬度已變更
      emit('width-changed', selectorWidth.value);
    };
    
    // 滑鼠放開時結束調整選擇器寬度，並保存設定
    const onMouseUpForPanel = () => {
      isResizing.value = false;
      document.removeEventListener('mousemove', onMouseMoveForPanel);
      document.removeEventListener('mouseup', onMouseUpForPanel);
      
      // 保存選擇器寬度到偏好設定
      userPreferencesStore.setFileSelectorWidth(selectorWidth.value);
    };
    
    // 開始調整欄位寬度
    const startResize = (event: MouseEvent, columnKey: string) => {
      event.preventDefault();
      
      // 設置當前調整的欄位
      resizingColumn.value = columnKey;
      columnResizeStartX.value = event.clientX;
      columnStartWidth.value = columnWidths.value[columnKey as keyof typeof columnWidths.value];
      
      // 添加事件監聽器
      document.addEventListener('mousemove', onMouseMoveForColumn);
      document.addEventListener('mouseup', onMouseUpForColumn);
    };
    
    // 滑鼠移動時調整欄位寬度
    const onMouseMoveForColumn = (event: MouseEvent) => {
      if (!resizingColumn.value) return;
      
      const diff = event.clientX - columnResizeStartX.value;
      let newWidth = columnStartWidth.value + diff;
      
      // 設置最小寬度
      newWidth = Math.max(80, newWidth);
      
      // 更新欄位寬度
      columnWidths.value = {
        ...columnWidths.value,
        [resizingColumn.value]: newWidth
      };
    };
    
    // 滑鼠放開時結束調整欄位寬度，並保存設定
    const onMouseUpForColumn = () => {
      if (resizingColumn.value) {
        // 保存欄位寬度到偏好設定
        userPreferencesStore.setColumnWidth(
          resizingColumn.value, 
          columnWidths.value[resizingColumn.value as keyof typeof columnWidths.value]
        );
      }
      
      resizingColumn.value = null;
      document.removeEventListener('mousemove', onMouseMoveForColumn);
      document.removeEventListener('mouseup', onMouseUpForColumn);
    };
    
    // 組件卸載時移除事件監聽器
    onBeforeUnmount(() => {
      document.removeEventListener('mousemove', onMouseMoveForPanel);
      document.removeEventListener('mouseup', onMouseUpForPanel);
      document.removeEventListener('mousemove', onMouseMoveForColumn);
      document.removeEventListener('mouseup', onMouseUpForColumn);
    });
    
    // 組件掛載時自動開啟上次的目錄
    onMounted(() => {
      // 如果已有選擇的目錄，自動加載
      if (spmDataStore.currentDirectory) {
        folderPath.value = spmDataStore.currentDirectory;
        files.value = spmDataStore.files.map(file => ({
          ...file,
          hasDatFile: file.hasDatFile || false
        }));
      } 
      // 如果沒有當前目錄但有上次開啟的目錄，則嘗試打開上次的目錄
      else if (userPreferencesStore.lastDirectory) {
        const tryLoadLastDir = async () => {
          try {
            const lastDir = userPreferencesStore.lastDirectory;
            if (!lastDir) return;
            
            const result = await window.pywebview.api.get_folder_files(lastDir);
            
            if (result && result.length > 0) {
              folderPath.value = lastDir;
              files.value = processFiles(result);
              spmDataStore.setCurrentDirectory(lastDir); // Use lastDir which we've already verified
              spmDataStore.setFiles(files.value);
            }
          } catch (error) {
            console.warn('Failed to load last directory:', error);
            // 忽略錯誤，避免阻塞使用者體驗
          }
        };
        
        tryLoadLastDir();
      }
    });
    
    return {
      folderPath,
      errorMessage,
      files,
      searchQuery,
      sortOption,
      filteredAndSortedFiles,
      selectorWidth,
      isResizing,
      columnWidths,
      openFolderDialog,
      viewFile,
      isSelected,
      startResizingWidth,
      startResize
    };
  }
});
</script>

<style scoped>
/* 可調整寬度的把手 */
.resize-handle {
  position: absolute;
  right: -4px;
  top: 0;
  bottom: 0;
  width: 7px;
  background: transparent;
  cursor: col-resize;
  z-index: 20;
}

.resize-handle:hover, .resize-handle:active {
  background-color: rgba(0, 120, 212, 0.1);
}

.resizing {
  user-select: none;
  cursor: col-resize;
}

/* 欄位調整把手 */
.column-resizer {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 5px;
  cursor: col-resize;
  z-index: 10;
}

.column-resizer:hover {
  background-color: rgba(0, 120, 212, 0.2);
}

/* 確保表頭固定在頂部 */
thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #f9fafb;
}

/* 確保表格單元格內容正確顯示 */
td {
  position: relative;
  overflow: hidden;
}
</style>