<template>
    <div class="folder-selector">
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
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref } from 'vue';
  
  declare global {
    interface Window {
      pywebview: {
        api: {
          open_folder_dialog: () => Promise<any>;
          get_folder_contents: (path: string) => Promise<any>;
        };
      };
    }
  }
  
  export default defineComponent({
    name: 'FolderSelector',
    
    setup() {
      const folderPath = ref<string>('');
      const errorMessage = ref<string>('');
      
      const openFolderDialog = async () => {
        try {
          errorMessage.value = '';
          
          // 呼叫 Python 後端 API 開啟資料夾選擇器
          const result = await window.pywebview.api.open_folder_dialog();
          
          if (result.success) {
            folderPath.value = result.path;
            
            // 可選：獲取資料夾內容
            const contentsResult = await window.pywebview.api.get_folder_contents(result.path);
            console.log('資料夾內容:', contentsResult);
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
      
      return {
        folderPath,
        errorMessage,
        openFolderDialog
      };
    }
  });
  </script>
  
  <style scoped>
  .folder-selector {
    display: flex;
    flex-direction: column;
    width: 100%;
    max-width: 800px;
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
  </style>