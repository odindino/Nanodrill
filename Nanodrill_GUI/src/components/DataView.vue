<!--src/components/DataView.vue-->
<template>
    <div class="h-full flex flex-col bg-white rounded-lg shadow overflow-hidden border border-gray-200">
      <div v-if="!selectedFile" class="flex flex-col items-center justify-center h-full p-6 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-gray-500">請從左側檔案選擇器選擇一個檔案</p>
      </div>
  
      <div v-else class="h-full flex flex-col">
        <div class="flex justify-between items-center px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h2 class="text-lg font-medium text-gray-800">{{ selectedFile.name }}</h2>
          <button 
            class="p-1.5 rounded-full hover:bg-gray-200 text-gray-500 focus:outline-none"
            @click="closeFile"
            title="關閉檔案"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
  
        <div v-if="loading" class="flex flex-col items-center justify-center flex-grow p-8">
          <div class="w-12 h-12 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-4"></div>
          <p class="text-gray-600">正在載入資料...</p>
        </div>
  
        <div v-else-if="errorMessage" class="m-6 p-4 bg-error-50 text-error-800 rounded border-l-4 border-error">
          {{ errorMessage }}
        </div>
  
        <div v-else-if="fileContent" class="flex flex-col flex-grow overflow-hidden">
          <div class="border-b border-gray-200">
            <nav class="flex -mb-px">
              <button 
                class="px-6 py-3 border-b-2 font-medium text-sm focus:outline-none transition-colors duration-200"
                :class="activeTab === 'overview' 
                  ? 'border-primary text-primary' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                @click="activeTab = 'overview'"
              >
                概覽
              </button>
              <button 
                class="px-6 py-3 border-b-2 font-medium text-sm focus:outline-none transition-colors duration-200"
                :class="activeTab === 'parameters' 
                  ? 'border-primary text-primary' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                @click="activeTab = 'parameters'"
              >
                參數
              </button>
              <button 
                class="px-6 py-3 border-b-2 font-medium text-sm focus:outline-none transition-colors duration-200"
                :class="activeTab === 'related-files' 
                  ? 'border-primary text-primary' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                @click="activeTab = 'related-files'"
              >
                相關檔案
              </button>
            </nav>
          </div>
  
          <div class="flex-grow overflow-y-auto p-6">
            <!-- 概覽標籤 -->
            <div v-if="activeTab === 'overview'" class="space-y-6">
              <div v-if="hasRelatedDatFiles" class="p-4 rounded-lg bg-primary-50 border-l-4 border-primary">
                <div class="font-semibold text-primary-700 mb-1">此檔案具有 I-V 曲線數據</div>
                <div class="text-sm text-primary-600">
                  可使用 <code class="px-1.5 py-0.5 bg-white rounded font-mono text-xs">{{ relatedMatrixFile }}</code> 進行 I-V 分析
                </div>
              </div>
  
              <div>
                <h3 class="text-base font-medium text-gray-800 mb-4">檔案資訊</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="bg-gray-50 p-4 rounded border border-gray-200">
                    <div class="text-sm font-medium text-gray-500 mb-1">檔案類型</div>
                    <div>SPM 掃描參數檔案 (.txt)</div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded border border-gray-200">
                    <div class="text-sm font-medium text-gray-500 mb-1">掃描日期</div>
                    <div>{{ fileParameters.Date || '未指定' }} {{ fileParameters.Time || '' }}</div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded border border-gray-200">
                    <div class="text-sm font-medium text-gray-500 mb-1">操作者</div>
                    <div>{{ fileParameters.UserName || '未指定' }}</div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded border border-gray-200">
                    <div class="text-sm font-medium text-gray-500 mb-1">掃描範圍</div>
                    <div>
                      {{ fileParameters.XScanRange || '0' }} × {{ fileParameters.YScanRange || '0' }} 
                      {{ fileParameters.XPhysUnit || 'nm' }}
                    </div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded border border-gray-200">
                    <div class="text-sm font-medium text-gray-500 mb-1">偏壓</div>
                    <div>
                      {{ fileParameters.Bias || '0' }} {{ fileParameters.BiasPhysUnit || 'mV' }}
                    </div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded border border-gray-200">
                    <div class="text-sm font-medium text-gray-500 mb-1">像素</div>
                    <div>
                      {{ fileParameters.xPixel || '0' }} × {{ fileParameters.yPixel || '0' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
  
            <!-- 參數標籤 -->
            <div v-else-if="activeTab === 'parameters'" class="space-y-8">
              <div>
                <h3 class="text-base font-medium text-gray-800 mb-4">基本參數</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2">
                  <div v-for="(value, key) in basicParameters" :key="key" class="py-2 border-b border-gray-200">
                    <div class="flex justify-between">
                      <div class="font-medium text-sm text-gray-600">{{ key }}:</div>
                      <div class="text-sm text-gray-900">{{ value }}</div>
                    </div>
                  </div>
                </div>
              </div>
  
              <div v-if="fileParameters.FileDescriptions">
                <h3 class="text-base font-medium text-gray-800 mb-4">檔案描述</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div 
                    v-for="(desc, index) in fileParameters.FileDescriptions" 
                    :key="index" 
                    class="border border-gray-200 rounded overflow-hidden"
                  >
                    <div class="bg-gray-50 px-4 py-2 font-medium border-b border-gray-200">
                      {{ desc.Caption || desc.FileName }}
                    </div>
                    <div class="p-4 space-y-2">
                      <div>
                        <div class="text-xs text-gray-500">檔案名稱</div>
                        <div class="text-sm">{{ desc.FileName }}</div>
                      </div>
                      <div>
                        <div class="text-xs text-gray-500">縮放比例</div>
                        <div class="text-sm font-mono">{{ desc.Scale }}</div>
                      </div>
                      <div>
                        <div class="text-xs text-gray-500">物理單位</div>
                        <div class="text-sm">{{ desc.PhysUnit }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
  
            <!-- 相關檔案標籤 -->
            <div v-else-if="activeTab === 'related-files'" class="space-y-4">
              <h3 class="text-base font-medium text-gray-800 mb-4">相關檔案</h3>
              <div v-if="relatedFiles.length === 0" class="bg-gray-50 p-6 rounded text-center text-gray-500 border border-gray-200">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto mb-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8" />
                </svg>
                <p>沒有找到相關檔案</p>
              </div>
              <div v-else class="space-y-3">
                <div 
                  v-for="file in relatedFiles" 
                  :key="file.path" 
                  class="flex items-center p-4 bg-white rounded-lg border border-gray-200 hover:bg-gray-50"
                >
                  <div class="flex-shrink-0 mr-3 text-primary">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {{ file.name }}
                    </p>
                    <p class="text-xs text-gray-500">
                      {{ getFileTypeDescription(file.name) }}
                    </p>
                  </div>
                  <button 
                    class="ml-4 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                  >
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