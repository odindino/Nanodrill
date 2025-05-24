// FolderBrowser.vue
<template>
  <div class="folder-browser">
    <div class="selector-header">
      <h2>SPM 數據分析器</h2>
      <p>請選擇包含 SPM 數據的資料夾</p>
    </div>
    
    <div class="selector-content">
      <div class="path-display">
        <div class="path-label">當前路徑:</div>
        <div class="path-value">{{ folderPath || '尚未選擇資料夾' }}</div>
      </div>
      
      <button class="select-button" @click="openFolderDialog">
        選擇資料夾
      </button>
    </div>
    
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
    
    <div v-if="folderPath && filteredAndSortedFiles.length > 0" class="file-list-container">
      <h3>資料夾內容</h3>
      <div class="filter-controls">
        <div class="search-container">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜尋檔案名稱..." 
            class="search-input"
          />
        </div>
        <div class="sort-container">
          <label for="sort-select">排序方式:</label>
          <select id="sort-select" v-model="sortOption" class="sort-select">
            <option value="time_desc">時間 (新到舊)</option>
            <option value="time_asc">時間 (舊到新)</option>
            <option value="name_asc">名稱 (A-Z)</option>
            <option value="name_desc">名稱 (Z-A)</option>
            <option value="number_asc">編號 (小到大)</option>
            <option value="number_desc">編號 (大到小)</option>
          </select>
        </div>
      </div>
      
      <div class="file-list">
        <table>
          <thead>
            <tr>
              <th>檔案名稱</th>
              <th>類型</th>
              <th>修改時間</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="file in filteredAndSortedFiles" 
              :key="file.path"
              :class="{ 'has-dat': file.hasDatFile }"
            >
              <td>
                <div class="file-name">
                  <span v-if="file.hasDatFile" class="dat-indicator" title="該檔案有對應的 IV 曲線數據">⚡</span>
                  {{ file.name }}
                </div>
              </td>
              <td>{{ file.type.toUpperCase() }}</td>
              <td>{{ file.modTimeStr }}</td>
              <td>
                <button @click="viewFile(file)" class="view-button">
                  查看
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div v-else-if="folderPath && filteredAndSortedFiles.length === 0" class="no-files">
      <p>資料夾中沒有找到 .txt 檔案</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue';

interface FileInfo {
  name: string;
  path: string;
  type: string;
  number: number;
  modTime: number;
  modTimeStr: string;
  hasDatFile: boolean;
}

export default defineComponent({
  name: 'FolderBrowser',
  
  setup() {
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
      
      console.log("TXT 檔案:", txtFiles.map(f => f.name));
      console.log("DAT 檔案:", datFiles.map(f => f.name));
      
      // 從 txt 檔案中提取編號
      const txtNumberMap = new Map<number, string>();
      
      txtFiles.forEach(file => {
        const number = extractNumberFromFilename(file.name);
        if (number >= 0) {
          txtNumberMap.set(number, file.name);
          console.log(`TXT 檔案 ${file.name} 的編號: ${number}`);
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
            // `_${String(number).padStart(3, '0')}`   // 補零到3位數 (001, 002...)
          ];
          
          // 檢查 dat 檔案名稱是否包含任一編號格式
          if (numberFormats.some(format => datFile.name.includes(format))) {
            txtWithDat.add(number);
            console.log(`DAT 檔案 ${datFile.name} 對應到編號 ${number} (${txtName})`);
          }
        });
      });
      
      console.log("有 DAT 檔案的 TXT 編號:", Array.from(txtWithDat));
      
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
    
    // 查看文件
    const viewFile = async (file: FileInfo) => {
      try {
        if (file.type === 'txt') {
          const result = await window.pywebview.api.get_txt_file_content(file.path);
          if (result.success) {
            console.log('TXT 檔案內容:', result);
            // 這裡可以添加顯示文件內容的邏輯
          } else {
            errorMessage.value = result.error || '無法讀取文件內容';
          }
        }
      } catch (error) {
        console.error('查看文件失敗:', error);
        errorMessage.value = `系統錯誤: ${error}`;
      }
    };
    
    return {
      folderPath,
      errorMessage,
      files,
      searchQuery,
      sortOption,
      filteredAndSortedFiles,
      openFolderDialog,
      viewFile
    };
  }
});
</script>

<style scoped>
.folder-browser {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
  font-family: 'Arial', sans-serif;
}

.selector-header {
  margin-bottom: 24px;
  text-align: center;
}

.selector-header h2 {
  font-size: 24px;
  margin-bottom: 8px;
  color: #333;
}

.selector-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.path-display {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.path-label {
  font-weight: bold;
  color: #555;
}

.path-value {
  word-break: break-all;
  color: #0066cc;
  font-family: monospace;
  padding: 8px;
  background-color: #fff;
  border-radius: 2px;
  border: 1px solid #eee;
  min-height: 24px;
}

.select-button {
  padding: 12px 24px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.2s;
  align-self: center;
}

.select-button:hover {
  background-color: #45a049;
}

.error-message {
  margin-top: 16px;
  padding: 12px;
  background-color: #ffebee;
  color: #d32f2f;
  border-radius: 4px;
  border-left: 4px solid #d32f2f;
}

.file-list-container {
  margin-top: 24px;
}

.file-list-container h3 {
  margin-bottom: 16px;
  color: #333;
}

.filter-controls {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.search-container {
  flex: 1;
  min-width: 200px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.sort-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

.file-list {
  overflow-x: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background-color: #f5f5f5;
}

th, td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

th {
  font-weight: bold;
  color: #555;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dat-indicator {
  color: #f57c00;
  font-size: 16px;
}

.has-dat {
  background-color: rgba(245, 124, 0, 0.05);
}

.view-button {
  padding: 6px 12px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.view-button:hover {
  background-color: #0b7dda;
}

.no-files {
  margin-top: 24px;
  padding: 16px;
  background-color: #f5f5f5;
  border-radius: 4px;
  text-align: center;
  color: #757575;
}
</style>