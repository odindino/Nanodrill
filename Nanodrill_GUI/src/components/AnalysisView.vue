<!-- src/components/AnalysisView.vue -->
<template>
    <div class="h-full flex flex-col bg-white rounded-lg shadow overflow-hidden">
      <!-- 沒有標籤頁時的歡迎畫面 -->
      <div v-if="analysisTabs.length === 0" class="flex flex-col items-center justify-center h-full p-6 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <p class="text-gray-500 mb-4">尚未開啟任何分析標籤頁</p>
        <p class="text-gray-500 text-sm">請在檔案選擇器中雙擊檔案或使用"分析"按鈕開始進行分析</p>
      </div>
  
      <!-- 有標籤頁時的分析介面 -->
      <div v-else class="h-full flex flex-col">
        <!-- 標籤頁導航列 -->
        <div class="flex px-4 pt-2 border-b border-gray-200 bg-gray-50">
          <div class="flex overflow-x-auto space-x-1 flex-grow">
            <button 
              v-for="tab in analysisTabs" 
              :key="tab.id" 
              @click="switchTab(tab.id)" 
              class="flex items-center px-4 py-2 text-sm rounded-t-md focus:outline-none transition-colors"
              :class="activeTabId === tab.id 
                ? 'bg-white text-primary font-medium border border-gray-200 border-b-white' 
                : 'text-gray-600 hover:bg-gray-100'"
            >
              <span class="truncate max-w-xs">{{ tab.title }}</span>
              <button 
                @click.stop="closeTab(tab.id)" 
                class="ml-2 p-0.5 rounded-full hover:bg-gray-200 text-gray-400 hover:text-gray-600 focus:outline-none"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </button>
          </div>
        </div>
  
        <!-- 標籤頁內容 -->
        <div v-if="activeTab" class="flex-grow overflow-hidden">
          <div class="h-full flex p-4 space-x-4">
            <!-- 左側控制面板 -->
            <div class="w-64 flex-shrink-0 border border-gray-200 rounded-lg overflow-hidden">
              <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 font-medium">控制面板</div>
              
              <!-- 檔案選擇區 -->
              <div class="p-4">
                <h3 class="text-sm font-medium text-gray-700 mb-2">選擇資料檔案</h3>
                
                <div class="mb-4">
                  <label class="text-xs text-gray-500 block mb-1">檔案選擇</label>
                  <select 
                    v-model="selectedFileId" 
                    class="w-full text-sm border border-gray-300 rounded py-1.5 px-2 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
                    :disabled="availableFiles.length === 0"
                  >
                    <option v-for="file in availableFiles" :key="file.path" :value="file.path">
                      {{ file.name }}
                    </option>
                  </select>
                  <p v-if="availableFiles.length === 0" class="text-xs text-gray-500 mt-1">
                    沒有可用的相關檔案
                  </p>
                </div>
                
                <button 
                  @click="loadSelectedFile" 
                  class="w-full py-2 px-4 bg-primary text-white font-medium rounded transition-colors hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="!selectedFileId || isLoading"
                >
                  <span v-if="isLoading">載入中...</span>
                  <span v-else>載入檔案</span>
                </button>
                
                <!-- 檔案資訊區塊 - 改進版 -->
                <div class="mt-4 border-t border-gray-200 pt-4">
                  <h3 class="text-sm font-medium text-gray-700 mb-3">檔案資訊</h3>
                  
                  <div v-if="activeTab && activeTab.txtContent" class="bg-white rounded-lg border border-gray-200 overflow-y-auto max-h-80">
                    <!-- 基本參數 -->
                    <div class="p-3">
                      <h4 class="font-medium text-sm border-b pb-1 mb-3">基本參數</h4>
                      
                      <div class="grid grid-cols-1 gap-1.5">
                        <!-- 參數項目 - 每個參數一行 -->
                        <div v-for="(value, key) in displayParameters" :key="key" class="info-row flex">
                          <div class="text-sm font-medium text-gray-700 w-44 flex-shrink-0">{{ key }}:</div>
                          <div class="text-sm text-gray-900 flex-1">{{ value }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 無檔案資訊時的提示 -->
                  <div v-else class="bg-gray-50 rounded-md p-4 text-center text-gray-500">
                    <p>無檔案資訊</p>
                  </div>
                </div>

              </div>
              
              <!-- 假如載入的是形貌圖，提供影像處理功能 -->
              <div v-if="activeTab.fileType === 'topo' && activeTab.imageData" class="px-4 pb-4 border-t border-gray-200 pt-4">
                <h3 class="text-sm font-medium text-gray-700 mb-3">影像處理</h3>
                
                <div class="space-y-4">
                  <!-- 平面校正 -->
                  <div>
                    <label class="text-xs text-gray-500 block mb-1">平面校正</label>
                    <div class="flex space-x-2">
                      <button 
                        class="flex-1 py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
                      >
                        線性平面化
                      </button>
                      <button 
                        class="flex-1 py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
                      >
                        多項式平面化
                      </button>
                    </div>
                  </div>
                  
                  <!-- 色彩映射 -->
                  <div>
                    <label class="text-xs text-gray-500 block mb-1">色彩映射</label>
                    <select 
                      v-model="activeTab.colormap" 
                      class="w-full text-sm border border-gray-300 rounded py-1.5 px-2 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
                    >
                      <option value="viridis">Viridis</option>
                      <option value="plasma">Plasma</option>
                      <option value="inferno">Inferno</option>
                      <option value="magma">Magma</option>
                      <option value="cividis">Cividis</option>
                      <option value="Oranges">Oranges</option>
                      <option value="hot">Hot</option>
                      <option value="cool">Cool</option>
                      <option value="jet">Jet</option>
                    </select>
                  </div>
                  
                  <!-- 高度縮放 -->
                  <div>
                    <div class="flex justify-between mb-1">
                      <label class="text-xs text-gray-500">高度縮放</label>
                      <span class="text-xs text-gray-500">{{ activeTab.zScale.toFixed(1) }}x</span>
                    </div>
                    <input 
                      type="range" 
                      v-model="activeTab.zScale" 
                      min="0.1" 
                      max="5" 
                      step="0.1" 
                      class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    >
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 右側主要內容區 -->
            <div class="flex-grow flex flex-col border border-gray-200 rounded-lg overflow-hidden">
              <!-- 載入中提示 -->
              <div v-if="isLoading" class="h-full flex items-center justify-center">
                <div class="flex flex-col items-center">
                  <div class="w-12 h-12 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-4"></div>
                  <p class="text-gray-600">正在載入資料...</p>
                </div>
              </div>
              
              <!-- 錯誤提示 -->
              <div v-else-if="loadError" class="h-full flex items-center justify-center p-6">
                <div class="max-w-md bg-red-50 border-l-4 border-red-500 p-4 text-red-800">
                  <p class="font-medium">載入失敗</p>
                  <p class="mt-2">{{ loadError }}</p>
                  <button 
                    @click="loadError = ''" 
                    class="mt-4 py-1.5 px-3 bg-red-100 text-red-800 text-sm font-medium rounded hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                  >
                    清除錯誤
                  </button>
                </div>
              </div>
              
              <!-- 形貌圖顯示 -->
              <div v-else-if="activeTab.fileType === 'topo' && activeTab.imageData" class="h-full flex flex-col">
                <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                  <h2 class="font-medium">{{ activeTab.currentFileName || '形貌分析' }}</h2>
                  
                  <div class="flex space-x-2">
                    <button 
                      title="截圖保存" 
                      class="p-1.5 rounded hover:bg-gray-200 text-gray-500 focus:outline-none"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </button>
                    
                    <button 
                      title="調整視圖" 
                      class="p-1.5 rounded hover:bg-gray-200 text-gray-500 focus:outline-none"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                      </svg>
                    </button>
                  </div>
                </div>
                
                <div class="flex-grow p-4 bg-gray-50 overflow-auto">
                  <div class="bg-white rounded-lg shadow p-4 h-full flex justify-center items-center">
                    <img 
                      :src="'data:image/png;base64,' + activeTab.imageData" 
                      :alt="activeTab.currentFileName" 
                      class="max-w-full max-h-full object-contain"
                    />
                  </div>
                </div>
                
                <!-- 底部統計信息 -->
                <div v-if="activeTab.statistics" class="bg-gray-50 px-4 py-3 border-t border-gray-200">
                  <div class="grid grid-cols-6 gap-2">
                    <div class="bg-white p-2 rounded border border-gray-200">
                      <div class="text-xs text-gray-500">最小值</div>
                      <div class="font-mono text-sm">{{ formatNumber(activeTab.statistics.min) }} {{ activeTab.physUnit }}</div>
                    </div>
                    <div class="bg-white p-2 rounded border border-gray-200">
                      <div class="text-xs text-gray-500">最大值</div>
                      <div class="font-mono text-sm">{{ formatNumber(activeTab.statistics.max) }} {{ activeTab.physUnit }}</div>
                    </div>
                    <div class="bg-white p-2 rounded border border-gray-200">
                      <div class="text-xs text-gray-500">平均值</div>
                      <div class="font-mono text-sm">{{ formatNumber(activeTab.statistics.mean) }} {{ activeTab.physUnit }}</div>
                    </div>
                    <div class="bg-white p-2 rounded border border-gray-200">
                      <div class="text-xs text-gray-500">中位數</div>
                      <div class="font-mono text-sm">{{ formatNumber(activeTab.statistics.median) }} {{ activeTab.physUnit }}</div>
                    </div>
                    <div class="bg-white p-2 rounded border border-gray-200">
                      <div class="text-xs text-gray-500">均方根</div>
                      <div class="font-mono text-sm">{{ formatNumber(activeTab.statistics.rms) }} {{ activeTab.physUnit }}</div>
                    </div>
                    <div class="bg-white p-2 rounded border border-gray-200">
                      <div class="text-xs text-gray-500">標準差</div>
                      <div class="font-mono text-sm">{{ formatNumber(activeTab.statistics.std) }} {{ activeTab.physUnit }}</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 沒有選擇檔案時的提示 -->
              <div v-else class="h-full flex items-center justify-center text-center p-6 text-gray-500">
                <div>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p>請從左側控制面板選擇並載入資料檔案</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, computed, watch, onMounted } from 'vue';
  import { useSpmDataStore } from '../stores/spmDataStore';
  import type { FileInfo } from '../stores/spmDataStore';
  
  // 標籤頁類型定義
  interface AnalysisTab {
    id: string;
    title: string;
    fileId: string;
    fileType: 'topo' | 'iv' | 'lia';
    imageData?: string;
    statistics?: any;
    physUnit?: string;
    dimensions?: {
      width: number;
      height: number;
      xRange: number;
      yRange: number;
    };
    relatedFiles?: FileInfo[];
    currentFileName?: string;
    colormap: string;
    zScale: number;
  }
  
  export default defineComponent({
    name: 'AnalysisView',
    setup() {
      const spmDataStore = useSpmDataStore();
      const analysisTabs = computed(() => spmDataStore.analysisTabs);
      const activeTabId = computed(() => spmDataStore.activeAnalysisTabId);
      const activeTab = computed(() => {
        return analysisTabs.value.find(tab => tab.id === activeTabId.value);
      });
      
      const selectedFileType = ref<'topo' | 'iv' | 'lia'>('topo');
      const selectedFileId = ref<string>('');
      const isLoading = ref<boolean>(false);
      const loadError = ref<string>('');
      
      // 獲取可用的檔案
      const availableFiles = computed(() => {
        if (!activeTab.value || !activeTab.value.relatedFiles) {
            return [];
        }
        
        // 返回所有相關檔案，按檔案類型過濾
        // 輸出所有相關檔案的信息
        console.log('相關檔案數量:', activeTab.value.relatedFiles.length);
        activeTab.value.relatedFiles.forEach(file => {
            console.log('相關檔案:', file.name, file.path);
        });
        
        return activeTab.value.relatedFiles;
        });
      
      // 切換標籤頁
      const switchTab = (tabId: string) => {
        spmDataStore.setActiveAnalysisTab(tabId);
      };
      
      // 關閉標籤頁
      const closeTab = (tabId: string) => {
        spmDataStore.removeAnalysisTab(tabId);
      };
      
      // 載入選擇的檔案
      const loadSelectedFile = async () => {
        if (!selectedFileId.value || !activeTab.value) return;
        
        isLoading.value = true;
        loadError.value = '';
        
        try {
            // 檢查檔案類型
            const selectedFile = availableFiles.value.find(f => f.path === selectedFileId.value);
            const fileName = selectedFile?.name || '';
            
            // 輸出路徑信息以供調試
            console.log('嘗試載入檔案:', selectedFileId.value);
            console.log('檔案名稱:', fileName);
            console.log('標籤頁 TXT 檔案:', activeTab.value.fileId);
            
            if (fileName.toLowerCase().endsWith('.int')) {
              // 處理 .int 檔案 - 調用後端 API 處理 INT 檔案分析
              // 傳遞 INT 檔案路徑和原始 TXT 檔案路徑
              const result = await window.pywebview.api.analyze_int_file_api(selectedFileId.value, activeTab.value.fileId);
            
            if (result.success) {
                // 更新標籤頁的數據
                spmDataStore.updateAnalysisTabData(activeTabId.value, {
                imageData: result.image,
                statistics: result.statistics,
                physUnit: result.physUnit || 'nm',
                dimensions: result.dimensions,
                currentFileName: fileName
                });
            } else {
                loadError.value = result.error || '載入檔案時發生錯誤';
                console.error('載入檔案失敗:', result.error);
            }
            } else {
            // 處理其他類型檔案 (未實現)
            loadError.value = '檔案類型必須是 .int 而不是 ' + fileName.split('.').pop();
            }
        } catch (error) {
            console.error('載入檔案錯誤:', error);
            loadError.value = `載入檔案時發生錯誤: ${error}`;
        } finally {
            isLoading.value = false;
        }
        };
      
      // 格式化數字，保留兩位小數
      const formatNumber = (value: number) => {
        if (value === undefined || value === null) return 'N/A';
        return value.toFixed(2);
      };

      const displayParameters = computed(() => {
        if (!parameters.value) return {};
        
        // 定義想要顯示的參數順序
        const paramOrder = [
          'Version', 'Date', 'Time', 'UserName',
          'SetPoint', 'SetPointPhysUnit', 'FeedBackModus', 'Bias',
          'BiasPhysUnit', 'Ki', 'Kp', 'FeedbackOnCh',
          'XScanRange', 'YScanRange', 'XPhysUnit', 'YPhysUnit',
          'Speed', 'LineRate', 'Angle', 'xPixel',
          'yPixel', 'yCenter', 'xCenter', 'LockInFreq',
          'LockInFreqPhysUnit', 'LockInAmpl', 'LockInAmplPhysUnit'
        ];
        
        // 格式化特定參數顯示
        const formatted = { ...parameters.value };
        
        // 為某些參數添加單位或格式
        if (formatted.Speed) formatted.Speed = `${formatted.Speed} ; lines/sec`;
        if (formatted.LineRate) formatted.LineRate = `${formatted.LineRate} ; lines/sec`;
        
        // 按照順序建立最終顯示參數
        const result: Record<string, string> = {};
        paramOrder.forEach(param => {
          if (formatted[param]) {
            result[param] = formatted[param];
          }
        });
        
        return result;
      });

      // 檔案參數
      const parameters = computed(() => {
        if (!activeTab.value || !activeTab.value.txtContent) return {};
        
        // 如果標籤頁已經有解析好的參數，直接返回
        if (activeTab.value.parameters) {
          return activeTab.value.parameters;
        }
        
        // 否則嘗試從 txtContent 中解析參數
        try {
          const content = activeTab.value.txtContent;
          const parameters: Record<string, string> = {};
          
          // 解析版本信息
          const versionMatch = content.match(/Version\s*:\s*([^\n]+)/);
          if (versionMatch) parameters.Version = versionMatch[1].trim();
          
          // 解析日期
          const dateMatch = content.match(/Date\s*:\s*([^\n]+)/);
          if (dateMatch) parameters.Date = dateMatch[1].trim();
          
          // 解析時間
          const timeMatch = content.match(/Time\s*:\s*([^\n]+)/);
          if (timeMatch) parameters.Time = timeMatch[1].trim();
          
          // 解析用戶名
          const userNameMatch = content.match(/UserName\s*:\s*([^\n]+)/);
          if (userNameMatch) parameters.UserName = userNameMatch[1].trim();
          
          // 解析更多參數...
          const paramPatterns = [
            'SetPoint', 'SetPointPhysUnit', 'FeedBackModus', 'Bias', 'BiasPhysUnit',
            'Ki', 'Kp', 'FeedbackOnCh', 'XScanRange', 'YScanRange', 'XPhysUnit',
            'YPhysUnit', 'Speed', 'LineRate', 'Angle', 'xPixel', 'yPixel',
            'yCenter', 'xCenter', 'LockInFreq', 'LockInFreqPhysUnit', 'LockInAmpl',
            'LockInAmplPhysUnit'
          ];
          
          paramPatterns.forEach(param => {
            const pattern = new RegExp(param + '\\s*:\\s*([^\\n]+)');
            const match = content.match(pattern);
            if (match) {
              parameters[param] = match[1].trim();
            }
          });
          
          // 如果標籤頁中沒有存儲參數，則保存解析結果
          if (activeTab.value && !activeTab.value.parameters) {
            spmDataStore.updateAnalysisTabData(activeTabId.value, {
              parameters: parameters
            });
          }
          
          return parameters;
        } catch (error) {
          console.error('解析參數時出錯:', error);
          return {};
        }
      });
      
      // 當選擇的檔案類型改變時，重設選中的檔案
      watch(selectedFileType, () => {
        selectedFileId.value = '';
      });
      
      // 當標籤頁改變時，如果有可用檔案則自動選中第一個
      watch([activeTabId, availableFiles], () => {
        if (availableFiles.value.length > 0 && !selectedFileId.value) {
          selectedFileId.value = availableFiles.value[0].path;
        }
      }, { immediate: true });
      
      // 當添加了新標籤頁時，自動載入第一個檔案
      watch(analysisTabs, (newTabs, oldTabs) => {
        // 如果添加了新標籤頁
        if (newTabs.length > oldTabs.length) {
          const newTab = newTabs.find(tab => !oldTabs.some(oldTab => oldTab.id === tab.id));
          
          if (newTab && newTab.id === activeTabId.value && availableFiles.value.length > 0) {
            // 自動選擇第一個檔案並載入
            selectedFileId.value = availableFiles.value[0].path;
            
            // 短暫延遲確保 DOM 已更新
            setTimeout(() => {
              loadSelectedFile();
            }, 100);
          }
        }
      }, { deep: true });
      
      return {
        analysisTabs,
        activeTabId,
        activeTab,
        selectedFileType,
        selectedFileId,
        isLoading,
        loadError,
        availableFiles,
        parameters,
        displayParameters,
        switchTab,
        closeTab,
        loadSelectedFile,
        formatNumber
      };
    }
  });
  </script>

<style scoped>
.info-row {
  white-space: nowrap;
  display: flex;
  padding: 4px 0;
}

.max-h-80 {
  scrollbar-width: thin;
  scrollbar-color: #ddd #f1f1f1;
}

/* 自定義滾動條樣式 */
.max-h-80::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.max-h-80::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.max-h-80::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 4px;
}

.max-h-80::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}
</style>