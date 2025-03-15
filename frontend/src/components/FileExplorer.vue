<template>
  <div class="file-explorer">
    <div class="file-explorer-header">
      <h3>檔案瀏覽器</h3>
      <button class="open-file-btn" @click="openFileDialog">
        <span class="btn-icon">+</span>
      </button>
    </div>
    
    <div class="directory-info" v-if="currentDirectory">
      <div class="directory-path">{{ displayPath }}</div>
    </div>
    
    <div class="file-list-container">
      <div v-if="files.length === 0" class="empty-message">
        無檔案。請開啟檔案或拖曳檔案至此區域。
      </div>
      
      <!-- 檔案列表 -->
      <div class="file-list" v-else>
        <div 
          v-for="file in sortedFiles" 
          :key="file.path"
          class="file-item"
          :class="{ 
            'file-item-selected': isSelected(file),
            'file-item-txt': file.type === 'txt',
            'file-item-dat': file.type === 'dat'
          }"
          @click="selectFile(file)"
          @dblclick="openFile(file)"
        >
          <div class="file-icon">
            <span v-if="file.type === 'txt'">📄</span>
            <span v-else-if="file.type === 'dat'">📊</span>
            <span v-else>📁</span>
          </div>
          <div class="file-details">
            <div class="file-name">{{ file.name }}</div>
            <div class="file-meta">
              {{ formatModTime(file.modTime) }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="file-explorer-footer">
      <div class="sort-controls">
        <label>
          <input 
            type="checkbox" 
            v-model="sortByTime"
            @change="handleSortChange"
          > 
          按時間排序
        </label>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { useFileStore } from '../stores/fileStore';
import type { SPMFile } from '../types';

export default defineComponent({
  name: 'FileExplorer',
  
  emits: ['file-selected'],
  
  setup(_, { emit }) {
    const fileStore = useFileStore();
    const sortByTime = ref(false);
    const selectedFileItem = ref<SPMFile | null>(null);
    
    // 取得檔案列表
    const files = computed(() => fileStore.files);
    
    // 取得當前目錄
    const currentDirectory = computed(() => fileStore.currentDirectory);
    
    // 顯示路徑（簡化顯示）
    const displayPath = computed(() => {
      if (!currentDirectory.value) return '';
      // 若路徑過長，顯示末端部分
      const path = currentDirectory.value;
      if (path.length > 30) {
        return '...' + path.substring(path.length - 30);
      }
      return path;
    });
    
    // 依照排序條件對檔案排序
    const sortedFiles = computed(() => {
      if (!files.value.length) return [];
      
      return [...files.value].sort((a, b) => {
        // 先將 txt 檔放前面
        if (a.type === 'txt' && b.type !== 'txt') return -1;
        if (a.type !== 'txt' && b.type === 'txt') return 1;
        
        // 再將 dat 檔放前面
        if (a.type === 'dat' && b.type !== 'dat') return -1;
        if (a.type !== 'dat' && b.type === 'dat') return 1;
        
        // 然後根據排序方式排序
        if (sortByTime.value) {
          // 按時間排序
          return b.modTime - a.modTime;
        } else {
          // 按編號排序
          return a.number - b.number;
        }
      });
    });
    
    // 開啟檔案對話框
    const openFileDialog = async () => {
      try {
        fileStore.setStatusMessage('選擇檔案中...');
        const result = await window.pywebview.api.open_file_dialog();
        
        if (result.success) {
          fileStore.setCurrentDirectory(result.directory);
          fileStore.setFiles(result.files);
          fileStore.setStatusMessage('檔案載入成功');
        } else {
          fileStore.setStatusMessage('檔案載入失敗: ' + (result.error || '未知錯誤'));
        }
      } catch (error) {
        console.error('開啟檔案對話框錯誤:', error);
        fileStore.setStatusMessage('開啟檔案對話框錯誤');
      }
    };
    
    // 選擇檔案
    const selectFile = (file: SPMFile) => {
      selectedFileItem.value = file;
    };
    
    // 開啟檔案（雙擊）
    const openFile = (file: SPMFile) => {
      selectedFileItem.value = file;
      emit('file-selected', file);
    };
    
    // 檢查檔案是否被選中
    const isSelected = (file: SPMFile) => {
      return selectedFileItem.value && selectedFileItem.value.path === file.path;
    };
    
    // 格式化修改時間
    const formatModTime = (timestamp: number) => {
      const date = new Date(timestamp * 1000);
      return date.toLocaleString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
    // 處理排序方式變更
    const handleSortChange = () => {
      fileStore.setStatusMessage(
        sortByTime.value ? '按修改時間排序' : '按檔案編號排序'
      );
    };
    
    return {
      files,
      sortedFiles,
      currentDirectory,
      displayPath,
      selectedFileItem,
      sortByTime,
      openFileDialog,
      selectFile,
      openFile,
      isSelected,
      formatModTime,
      handleSortChange
    };
  }
});
</script>

<style scoped>
.file-explorer {
  display: flex;
  flex-direction: column;
  height: 100%;
  color: #e1e1e1;
  background-color: #2d333b;
}

.file-explorer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #444c56;
}

.file-explorer-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
}

.open-file-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  background-color: #444c56;
  color: #e1e1e1;
  border: none;
  cursor: pointer;
  padding: 0;
}

.open-file-btn:hover {
  background-color: #2ea043;
}

.btn-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.directory-info {
  padding: 0.5rem 1rem;
  background-color: #22272e;
  border-bottom: 1px solid #444c56;
  font-size: 0.8rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.empty-message {
  padding: 1rem;
  text-align: center;
  color: #768390;
  font-style: italic;
}

.file-list {
  list-style: none;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: background-color 0.2s;
}

.file-item:hover {
  background-color: #374151;
}

.file-item-selected {
  background-color: #3a404b;
  border-left-color: #2ea043;
}

.file-item-txt {
  color: #e1e1e1;
}

.file-item-dat {
  color: #a5d6ff;
}

.file-icon {
  margin-right: 0.75rem;
  font-size: 1.1rem;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  font-size: 0.75rem;
  color: #768390;
  margin-top: 0.125rem;
}

.file-explorer-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid #444c56;
  font-size: 0.8rem;
}

.sort-controls {
  display: flex;
  align-items: center;
}

.sort-controls label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.sort-controls input {
  margin-right: 0.5rem;
}
</style>