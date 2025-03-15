<template>
  <div class="main-view">
    <FileExplorer 
      class="file-explorer"
      @file-selected="handleFileSelected"
    />
    
    <div class="content-area">
      <!-- 歡迎頁面 -->
      <div v-if="!selectedFile" class="welcome-panel">
        <div class="welcome-card">
          <h2>歡迎使用 Nanodrill</h2>
          <p>請從左側選擇檔案或點擊下方按鈕開啟檔案</p>
          <button @click="openFileDialog">開啟檔案</button>
        </div>
      </div>
      
      <!-- 檔案數據展示區域 -->
      <div v-else class="data-panel">
        <div class="data-header">
          <h2>{{ selectedFile.name }}</h2>
          <div class="data-controls">
            <select 
              v-if="associatedFiles.length > 0" 
              v-model="selectedDataFile"
              @change="loadDataFile"
            >
              <option value="">選擇數據檔案</option>
              <option 
                v-for="file in associatedFiles" 
                :key="file.fileName" 
                :value="file"
              >
                {{ file.caption }} ({{ file.fileName }})
              </option>
            </select>
          </div>
        </div>
        
        <div class="data-content">
          <!-- 參數顯示區 -->
          <ParameterDisplay 
            v-if="metadata && !imageData" 
            :metadata="metadata" 
          />
          
          <!-- 圖像顯示區 -->
          <ImageViewer 
            v-if="imageData" 
            :imageData="imageData" 
            :metadata="metadata"
          />
          
          <!-- 載入中狀態 -->
          <div v-if="isLoading" class="loading-indicator">
            <div class="spinner"></div>
            <p>載入數據中...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import FileExplorer from '../components/FileExplorer.vue';
import ImageViewer from '../components/ImageViewer.vue';
import ParameterDisplay from '../components/ParameterDisplay.vue';
import { useFileStore } from '../stores/fileStore';
import type { SPMFile, FileDescription, MetadataInfo } from '../types';

export default defineComponent({
  name: 'MainView',
  
  components: {
    FileExplorer,
    ImageViewer,
    ParameterDisplay
  },
  
  setup() {
    const fileStore = useFileStore();
    
    const selectedFile = ref<SPMFile | null>(null);
    const metadata = ref<MetadataInfo | null>(null);
    const selectedDataFile = ref<FileDescription | null>(null);
    const imageData = ref<string | null>(null);
    const isLoading = ref(false);
    
    // 計算關聯檔案列表
    const associatedFiles = computed(() => {
      if (!metadata.value || !metadata.value.fileDescriptions) {
        return [];
      }
      return metadata.value.fileDescriptions;
    });
    
    // 開啟檔案對話框
    const openFileDialog = async () => {
      try {
        fileStore.setStatusMessage('選擇檔案中...');
        isLoading.value = true;
        
        const result = await window.pywebview.api.open_file_dialog();
        
        if (result.success) {
          fileStore.setCurrentDirectory(result.directory);
          fileStore.setFiles(result.files);
          
          if (result.txtInfo) {
            const selectedFileName = result.selectedFile;
            const file = result.files.find((f: SPMFile) => f.name === selectedFileName);
            if (file) {
              handleFileSelected(file);
            }
          }
          
          fileStore.setStatusMessage('檔案載入成功');
        } else {
          fileStore.setStatusMessage('檔案載入失敗: ' + (result.error || '未知錯誤'));
        }
      } catch (error) {
        console.error('開啟檔案對話框錯誤:', error);
        fileStore.setStatusMessage('開啟檔案對話框錯誤');
      } finally {
        isLoading.value = false;
      }
    };
    
    // 處理檔案選擇
    const handleFileSelected = async (file: SPMFile) => {
      selectedFile.value = file;
      metadata.value = null;
      selectedDataFile.value = null;
      imageData.value = null;
      
      if (file && file.type === 'txt') {
        try {
          fileStore.setStatusMessage('載入 TXT 檔案中...');
          isLoading.value = true;
          
          const result = await window.pywebview.api.get_txt_file_content(file.path);
          
          if (result.success) {
            metadata.value = result.metadata;
            fileStore.setStatusMessage('檔案資訊載入成功');
          } else {
            fileStore.setStatusMessage('檔案資訊載入失敗: ' + (result.error || '未知錯誤'));
          }
        } catch (error) {
          console.error('載入 TXT 檔案錯誤:', error);
          fileStore.setStatusMessage('載入 TXT 檔案錯誤');
        } finally {
          isLoading.value = false;
        }
      }
    };
    
    // 載入數據檔案
    const loadDataFile = async () => {
      if (!selectedDataFile.value || !selectedFile.value || !metadata.value) {
        return;
      }
      
      const file = selectedDataFile.value;
      const filePathParts = selectedFile.value.path.split('/');
      filePathParts.pop();
      const basePath = filePathParts.join('/');
      const fullPath = `${basePath}/${file.fileName}`;
      
      // 檢查是否為 .int 檔案
      if (file.fileName.endsWith('.int')) {
        try {
          fileStore.setStatusMessage('載入影像數據中...');
          isLoading.value = true;
          imageData.value = null;
          
          const result = await window.pywebview.api.load_int_file(fullPath, metadata.value);
          
          if (result.success) {
            imageData.value = result.imageData;
            fileStore.setStatusMessage('影像數據載入成功');
          } else {
            fileStore.setStatusMessage('影像數據載入失敗: ' + (result.error || '未知錯誤'));
          }
        } catch (error) {
          console.error('載入 INT 檔案錯誤:', error);
          fileStore.setStatusMessage('載入 INT 檔案錯誤');
        } finally {
          isLoading.value = false;
        }
      } else {
        // 處理其他類型檔案，如 .dat 等
        fileStore.setStatusMessage('暫不支援該檔案類型: ' + file.fileName);
      }
    };
    
    return {
      selectedFile,
      metadata,
      selectedDataFile,
      imageData,
      isLoading,
      associatedFiles,
      openFileDialog,
      handleFileSelected,
      loadDataFile
    };
  }
});
</script>

<style scoped>
.main-view {
  display: flex;
  width: 100%;
  height: 100%;
}

.file-explorer {
  width: 280px;
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
  background-color: #2d333b;
}

.content-area {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.welcome-panel {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 2rem;
}

.welcome-card {
  background-color: var(--card-background);
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  text-align: center;
  max-width: 500px;
}

.welcome-card h2 {
  margin-bottom: 1rem;
  color: var(--primary-color);
}

.welcome-card p {
  margin-bottom: 1.5rem;
  color: var(--text-light);
}

.data-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
}

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.data-header h2 {
  margin: 0;
  color: var(--primary-color);
}

.data-content {
  flex: 1;
  overflow: auto;
  position: relative;
}

.loading-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid var(--accent-color);
  width: 40px;
  height: 40px;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>