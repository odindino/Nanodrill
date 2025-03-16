// src/components/DataView.vue
<template>
  <div class="data-view">
    <div v-if="!selectedFile" class="no-file-selected">
      <p>請從左側檔案選擇器選擇一個檔案</p>
    </div>
    
    <div v-else class="file-content">
      <div class="file-header">
        <h2>{{ selectedFile.name }}</h2>
        <div class="file-actions">
          <button class="close-button" @click="closeFile">
            <span>&times;</span>
          </button>
        </div>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>正在載入資料...</p>
      </div>
      
      <div v-else-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
      
      <div v-else-if="fileContent" class="content-container">
        <div class="tabs">
          <button 
            class="tab-button" 
            :class="{ active: activeTab === 'overview' }"
            @click="activeTab = 'overview'"
          >
            概覽
          </button>
          <button 
            class="tab-button" 
            :class="{ active: activeTab === 'parameters' }"
            @click="activeTab = 'parameters'"
          >
            參數
          </button>
          <button 
            class="tab-button" 
            :class="{ active: activeTab === 'related-files' }"
            @click="activeTab = 'related-files'"
          >
            相關檔案
          </button>
        </div>
        
        <div class="tab-content">
          <div v-if="activeTab === 'overview'" class="overview-tab">
            <div v-if="hasRelatedDatFiles" class="related-dat-files">
              <div class="label">此檔案具有 I-V 曲線數據</div>
              <div class="info">
                可使用 <code>{{ relatedMatrixFile }}</code> 進行 I-V 分析
              </div>
            </div>
            
            <h3>檔案資訊</h3>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">檔案類型:</div>
                <div class="info-value">SPM 掃描參數檔案 (.txt)</div>
              </div>
              <div class="info-item">
                <div class="info-label">掃描日期:</div>
                <div class="info-value">
                  {{ fileParameters.Date || '未指定' }} {{ fileParameters.Time || '' }}
                </div>
              </div>
              <div class="info-item">
                <div class="info-label">操作者:</div>
                <div class="info-value">{{ fileParameters.UserName || '未指定' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">掃描範圍:</div>
                <div class="info-value">
                  {{ fileParameters.XScanRange || '0' }} × {{ fileParameters.YScanRange || '0' }} 
                  {{ fileParameters.XPhysUnit || 'nm' }}
                </div>
              </div>
              <div class="info-item">
                <div class="info-label">偏壓:</div>
                <div class="info-value">
                  {{ fileParameters.Bias || '0' }} {{ fileParameters.BiasPhysUnit || 'mV' }}
                </div>
              </div>
              <div class="info-item">
                <div class="info-label">像素:</div>
                <div class="info-value">
                  {{ fileParameters.xPixel || '0' }} × {{ fileParameters.yPixel || '0' }}
                </div>
              </div>
            </div>
          </div>
          
          <div v-else-if="activeTab === 'parameters'" class="parameters-tab">
            <div class="parameter-group">
              <h3>基本參數</h3>
              <div class="parameter-list">
                <div v-for="(value, key) in basicParameters" :key="key" class="parameter-item">
                  <div class="parameter-key">{{ key }}:</div>
                  <div class="parameter-value">{{ value }}</div>
                </div>
              </div>
            </div>
            
            <div class="parameter-group" v-if="fileParameters.FileDescriptions">
              <h3>檔案描述</h3>
              <div class="file-descriptions">
                <div 
                  v-for="(desc, index) in fileParameters.FileDescriptions" 
                  :key="index" 
                  class="file-description"
                >
                  <div class="desc-header">{{ desc.Caption || desc.FileName }}</div>
                  <div class="desc-details">
                    <div class="desc-item">
                      <span class="desc-label">檔案名稱:</span>
                      <span class="desc-value">{{ desc.FileName }}</span>
                    </div>
                    <div class="desc-item">
                      <span class="desc-label">縮放比例:</span>
                      <span class="desc-value">{{ desc.Scale }}</span>
                    </div>
                    <div class="desc-item">
                      <span class="desc-label">物理單位:</span>
                      <span class="desc-value">{{ desc.PhysUnit }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else-if="activeTab === 'related-files'" class="related-files-tab">
            <h3>相關檔案</h3>
            <div v-if="relatedFiles.length === 0" class="no-related-files">
              <p>沒有找到相關檔案</p>
            </div>
            <div v-else class="related-files-list">
              <div v-for="file in relatedFiles" :key="file.path" class="related-file-item">
                <div class="file-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" 
                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                </div>
                <div class="file-details">
                  <div class="file-name">{{ file.name }}</div>
                  <div class="file-type">{{ getFileTypeDescription(file.name) }}</div>
                </div>
                <button class="view-file-button">
                  查看
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { useSpmDataStore } from '../stores/spmDataStore';
import type { FileInfo } from '../stores/spmDataStore';

export default defineComponent({
  name: 'DataView',
  setup() {
    const spmDataStore = useSpmDataStore();
    const activeTab = ref('overview');
    const loading = ref(false);
    const errorMessage = ref('');
    
    // 選中的檔案
    const selectedFile = computed(() => spmDataStore.selectedFile);
    
    // 檔案內容
    const fileContent = computed(() => spmDataStore.selectedFileContent);
    
    // 檔案參數
    const fileParameters = computed(() => {
      if (!fileContent.value || !fileContent.value.parameters) {
        return {};
      }
      return fileContent.value.parameters;
    });
    
    // 基本參數 (排除 FileDescriptions 以便單獨顯示)
    const basicParameters = computed(() => {
      if (!fileParameters.value) {
        return {};
      }
      
      const params = { ...fileParameters.value };
      delete params.FileDescriptions;
      return params;
    });
    
    // 相關檔案
    const relatedFiles = computed(() => {
      if (!fileContent.value || !fileContent.value.relatedFiles) {
        return [];
      }
      return fileContent.value.relatedFiles;
    });
    
    // 是否有相關的 dat 檔案
    const hasRelatedDatFiles = computed(() => {
      return relatedFiles.value.some(file => file.name.includes('It_to_PC_Matrix.dat'));
    });
    
    // 相關的矩陣檔案名稱
    const relatedMatrixFile = computed(() => {
      const file = relatedFiles.value.find(file => file.name.includes('It_to_PC_Matrix.dat'));
      return file ? file.name : 'It_to_PC_Matrix.dat';
    });
    
    // 獲取檔案類型描述
    const getFileTypeDescription = (fileName: string) => {
      if (fileName.includes('It_to_PC_Matrix.dat')) {
        return 'I-V 曲線數據';
      } else if (fileName.includes('Lia1R_Matrix.dat')) {
        return 'LIA R 數據';
      } else if (fileName.includes('.dat')) {
        return '數據檔案';
      } else if (fileName.includes('.int')) {
        return '形貌數據';
      } else {
        return '未知類型';
      }
    };
    
    // 關閉檔案
    const closeFile = () => {
      spmDataStore.clearSelection();
    };
    
    return {
      selectedFile,
      fileContent,
      fileParameters,
      basicParameters,
      relatedFiles,
      activeTab,
      loading,
      errorMessage,
      hasRelatedDatFiles,
      relatedMatrixFile,
      getFileTypeDescription,
      closeFile
    };
  }
});
</script>

<style scoped>
.data-view {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.no-file-selected {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #666;
  font-size: 16px;
}

.file-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.file-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.file-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.file-actions {
  display: flex;
  gap: 8px;
}

.close-button {
  background: transparent;
  border: none;
  cursor: pointer;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  color: #666;
  font-size: 20px;
}

.close-button:hover {
  background-color: #e0e0e0;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1976D2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  margin: 20px;
  padding: 16px;
  background-color: #ffebee;
  color: #d32f2f;
  border-radius: 4px;
  border-left: 4px solid #d32f2f;
}

.content-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f5f5f5;
}

.tab-button {
  padding: 12px 20px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #555;
  border-bottom: 2px solid transparent;
}

.tab-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.tab-button.active {
  color: #1976D2;
  border-bottom-color: #1976D2;
}

.tab-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 概覽標籤樣式 */
.overview-tab {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.related-dat-files {
  background-color: #e3f2fd;
  border-left: 4px solid #1976D2;
  padding: 16px;
  border-radius: 4px;
}

.related-dat-files .label {
  font-weight: bold;
  margin-bottom: 8px;
  color: #1976D2;
}

.related-dat-files .info {
  color: #555;
  font-size: 14px;
}

.related-dat-files code {
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.overview-tab h3 {
  margin-bottom: 16px;
  font-size: 16px;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-weight: bold;
  color: #555;
  font-size: 14px;
}

.info-value {
  color: #333;
}

/* 參數標籤樣式 */
.parameters-tab {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.parameter-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.parameter-group h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.parameter-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
}

.parameter-item {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.parameter-key {
  font-weight: bold;
  color: #555;
}

.parameter-value {
  color: #333;
  word-break: break-word;
}

.file-descriptions {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.file-description {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.desc-header {
  padding: 12px;
  background-color: #f5f5f5;
  font-weight: bold;
  border-bottom: 1px solid #e0e0e0;
}

.desc-details {
  padding: 12px;
}

.desc-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.desc-label {
  font-size: 12px;
  color: #666;
}

.desc-value {
  font-family: monospace;
  word-break: break-all;
}

/* 相關檔案標籤樣式 */
.related-files-tab {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.related-files-tab h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.no-related-files {
  color: #666;
  font-style: italic;
}

.related-files-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-file-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: white;
}

.file-icon {
  color: #1976D2;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: bold;
  color: #333;
  word-break: break-all;
}

.file-type {
  font-size: 12px;
  color: #666;
}

.view-file-button {
  padding: 6px 12px;
  background-color: #1976D2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  white-space: nowrap;
}

.view-file-button:hover {
  background-color: #1565C0;
}
</style>