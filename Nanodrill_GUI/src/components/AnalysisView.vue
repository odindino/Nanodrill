<!-- src/components/AnalysisView.vue (完整版) -->
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
    <div v-else-if="!isGlobalLoading" class="h-full flex">
      <!-- 主要分析區域 -->
      <div class="flex-grow overflow-hidden flex flex-col">
        <!-- 分析標籤頁 -->
        <div class="flex px-4 pt-2 border-b border-gray-200 bg-gray-50 overflow-x-auto">
          <div v-for="tab in analysisTabs" 
               :key="tab.id" 
               class="flex flex-shrink-0"
               :class="{'mr-1': true}">
            <div class="flex group relative">
              <!-- 標籤本身 -->
              <button 
                @click="switchTab(tab.id)" 
                :class="[
                  'flex items-center px-4 py-2 text-sm rounded-t-md focus:outline-none transition-colors',
                  activeTabId === tab.id 
                    ? 'bg-white text-primary font-medium border border-gray-200 border-b-white' 
                    : 'text-gray-600 hover:bg-gray-100'
                ]"
              >
                <span class="truncate max-w-xs">{{ tab.title }}</span>
                
                <!-- 關閉按鈕 -->
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
        </div>
        
        <!-- 標籤內容 -->
        <div class="flex-grow overflow-hidden">
          <div v-if="activeTab" class="h-full flex flex-col">
            <!-- 載入中提示 -->
            <div v-if="isTabLoading" class="flex-grow flex items-center justify-center bg-gray-50">
              <div class="flex flex-col items-center">
                <div class="w-12 h-12 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-4"></div>
                <p class="text-gray-600">正在載入資料...</p>
              </div>
            </div>
            
            <!-- 錯誤提示 -->
            <div v-else-if="tabLoadError" class="flex-grow flex items-center justify-center p-6">
              <div class="max-w-md bg-red-50 border-l-4 border-red-500 p-4 text-red-800">
                <p class="font-medium">載入失敗</p>
                <p class="mt-2">{{ tabLoadError }}</p>
                <button 
                  @click="tabLoadError = ''" 
                  class="mt-4 py-1.5 px-3 bg-red-100 text-red-800 text-sm font-medium rounded hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                >
                  清除錯誤
                </button>
              </div>
            </div>
            
            <!-- 分析面板 -->
            <div v-else class="h-full flex p-4 space-x-4">
              <!-- 左側控制面板 -->
              <div class="flex-shrink-0 border border-gray-200 rounded-lg overflow-hidden w-80">
                <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 font-medium">控制面板</div>
                
                <!-- 檔案選擇區 -->
                <div class="p-4">
                  <h3 class="text-sm font-medium text-gray-700 mb-2">選擇資料檔案</h3>
                  
                  <div class="mb-4">
                    <label class="text-xs text-gray-500 block mb-1">檔案選擇</label>
                    <select 
                      v-model="selectedFileId" 
                      class="w-full text-sm border border-gray-300 rounded py-1.5 px-2 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
                      :disabled="!activeTab || !activeTab.relatedFiles || activeTab.relatedFiles.length === 0"
                    >
                      <option v-for="file in availableFiles" :key="file.path" :value="file.path">
                        {{ file.name }}
                      </option>
                    </select>
                    <p v-if="!availableFiles || availableFiles.length === 0" class="text-xs text-gray-500 mt-1">
                      沒有可用的相關檔案
                    </p>
                  </div>
                  
                  <button 
                    @click="loadSelectedFile" 
                    class="w-full py-2 px-4 bg-primary text-white font-medium rounded transition-colors hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    :disabled="!selectedFileId || isTabLoading"
                  >
                    <span v-if="isTabLoading">載入中...</span>
                    <span v-else>載入檔案</span>
                  </button>
                </div>
                
                <!-- 檔案資訊區塊 -->
                <div class="mt-4 border-t border-gray-200 pt-4 px-4">
                  <h3 class="text-sm font-medium text-gray-700 mb-3">檔案資訊</h3>
                  
                  <div v-if="activeTab && activeTab.txtContent" class="bg-white rounded-lg border border-gray-200 overflow-y-auto max-h-80">
                    <!-- 基本參數 -->
                    <div class="p-3">
                      <h4 class="font-medium text-sm border-b pb-1 mb-3">基本參數</h4>
                      
                      <div class="grid grid-cols-1 gap-1.5">
                        <!-- 參數項目 - 每個參數一行 -->
                        <div v-for="(value, key) in parametersToDisplay" :key="key" class="info-row flex">
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

                <!-- 形貌圖影像處理功能 -->
                <div v-if="activeTab && activeTab.fileType === 'topo' && activeTab.imageData" class="px-4 pb-4 border-t border-gray-200 pt-4">
                  <h3 class="text-sm font-medium text-gray-700 mb-3">影像處理</h3>
                  
                  <div class="space-y-4">
                    <!-- 平面校正 -->
                    <div>
                      <label class="text-xs text-gray-500 block mb-1">平面校正</label>
                      <div class="flex space-x-2">
                        <button 
                          @click="applyFlatten('mean')"
                          class="flex-1 py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
                        >
                          線性平面化
                        </button>
                        <button 
                          @click="applyFlatten('polyfit')"
                          class="flex-1 py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
                        >
                          多項式平面化
                        </button>
                      </div>
                    </div>
                    
                    <!-- 傾斜調整 -->
                    <div>
                      <label class="text-xs text-gray-500 block mb-1">傾斜調整</label>
                      <div class="grid grid-cols-2 gap-2">
                        <div class="col-span-2 mb-1">
                          <div class="flex items-center">
                            <input 
                              type="checkbox" 
                              id="tilt-fine-tune" 
                              v-model="fineTuneTilt"
                              class="h-3 w-3 text-primary focus:ring-primary border-gray-300 rounded"
                            >
                            <label for="tilt-fine-tune" class="ml-1 text-xs text-gray-700">
                              微調模式
                            </label>
                          </div>
                        </div>
                        <button 
                          @click="adjustTilt('up')"
                          class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
                        >
                          向上傾斜
                        </button>
                        <button 
                          @click="adjustTilt('down')"
                          class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
                        >
                          向下傾斜
                        </button>
                        <button 
                          @click="adjustTilt('left')"
                          class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
                        >
                          向左傾斜
                        </button>
                        <button 
                          @click="adjustTilt('right')"
                          class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
                        >
                          向右傾斜
                        </button>
                      </div>
                    </div>
                    
                    <!-- 色彩映射 -->
                    <div>
                      <label class="text-xs text-gray-500 block mb-1">色彩映射</label>
                      <select 
                        v-model="activeTabColormap" 
                        class="w-full text-sm border border-gray-300 rounded py-1.5 px-2 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
                        @change="updateActiveTabSettings({colormap: activeTabColormap})"
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
                        <span class="text-xs text-gray-500">{{ activeTabZScale.toFixed(1) }}x</span>
                      </div>
                      <input 
                        type="range" 
                        v-model="activeTabZScale" 
                        min="0.1" 
                        max="5" 
                        step="0.1" 
                        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                        @change="updateActiveTabSettings({zScale: activeTabZScale})"
                      >
                    </div>
                    
                    <!-- 剖面分析 -->
                    <div>
                      <label class="text-xs text-gray-500 block mb-1">剖面分析</label>
                      <button 
                        @click="createLineProfile"
                        class="w-full py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
                      >
                        建立線性剖面
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 右側主要內容區 -->
              <div class="flex-grow flex flex-col border border-gray-200 rounded-lg overflow-hidden">
                <!-- 形貌圖顯示 -->
                <div v-if="activeTab && activeTab.fileType === 'topo' && activeTab.imageData" class="h-full flex flex-col">
                  <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                    <h2 class="font-medium">{{ activeTab.currentFileName || '形貌分析' }}</h2>
                    
                    <div class="flex space-x-2">
                      <button 
                        title="截圖保存" 
                        class="p-1.5 rounded hover:bg-gray-200 text-gray-500 focus:outline-none"
                        @click="saveImage"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  
                  <div class="flex-grow p-4 bg-gray-50 overflow-auto">
                    <div class="bg-white rounded-lg shadow p-4 h-full flex justify-center items-center relative">
                      <img 
                        :src="'data:image/png;base64,' + activeTab.imageData" 
                        :alt="activeTab.currentFileName" 
                        class="max-w-full max-h-full object-contain"
                        @mousedown="handleImageMouseDown"
                        @mousemove="handleImageMouseMove"
                        @mouseup="handleImageMouseUp"
                        @click="handleImageClick"
                      />
                      
                      <!-- 線性剖面繪製線 -->
                      <svg v-if="lineProfileMode" class="absolute top-0 left-0 w-full h-full pointer-events-none">
                        <line v-if="isDrawingLine || (lineStart && lineEnd)"
                              :x1="lineStart?.x || 0"
                              :y1="lineStart?.y || 0"
                              :x2="isDrawingLine ? mouseMovePos.x : (lineEnd?.x || 0)"
                              :y2="isDrawingLine ? mouseMovePos.y : (lineEnd?.y || 0)"
                              stroke="#ff6b6b"
                              stroke-width="2"
                              stroke-dasharray="5,5" />
                        
                        <!-- 起點圓點 -->
                        <circle v-if="lineStart"
                                :cx="lineStart.x"
                                :cy="lineStart.y"
                                r="4"
                                fill="#ff6b6b" />
                        
                        <!-- 終點圓點 -->
                        <circle v-if="!isDrawingLine && lineEnd"
                                :cx="lineEnd.x"
                                :cy="lineEnd.y"
                                r="4"
                                fill="#ff6b6b" />
                      </svg>
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
                
                <!-- 剖面圖顯示 -->
                <div v-else-if="profileData && profileImage" class="h-full flex flex-col">
                  <div class="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                    <h2 class="font-medium">線性剖面</h2>
                    
                    <div class="flex space-x-2">
                      <button 
                        title="截圖保存" 
                        class="p-1.5 rounded hover:bg-gray-200 text-gray-500 focus:outline-none"
                        @click="saveProfileImage"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  
                  <div class="flex-grow p-4 bg-gray-50 overflow-auto">
                    <div class="bg-white rounded-lg shadow p-4 h-full flex justify-center items-center">
                      <img 
                        :src="'data:image/png;base64,' + profileImage" 
                        alt="線性剖面" 
                        class="max-w-full max-h-full object-contain"
                      />
                    </div>
                  </div>
                  
                  <!-- 剖面設置 -->
                  <div class="bg-gray-50 px-4 py-3 border-t border-gray-200">
                    <div class="grid grid-cols-2 gap-3">
                      <div class="flex items-center">
                        <input 
                          type="checkbox" 
                          id="shift-zero" 
                          v-model="profileSettings.shiftZero"
                          class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                          @change="updateProfile"
                        >
                        <label for="shift-zero" class="ml-2 text-sm text-gray-700">
                          將最小值歸零
                        </label>
                      </div>
                      <div class="flex items-center">
                        <input 
                          type="checkbox" 
                          id="auto-scale" 
                          v-model="profileSettings.autoScale"
                          class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                          @change="updateProfile"
                        >
                        <label for="auto-scale" class="ml-2 text-sm text-gray-700">
                          自動縮放
                        </label>
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
                    <span class="text-sm text-gray-500">尚未載入圖像</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 全局載入中提示 -->
    <div v-else class="h-full flex flex-col items-center justify-center">
      <div class="w-16 h-16 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-6"></div>
      <p class="text-gray-600 text-lg">正在載入資料...</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue';
import { useSpmDataStore } from '../stores/spmDataStore';

export default defineComponent({
  name: 'AnalysisView',
  setup() {
    const spmDataStore = useSpmDataStore();
    // 全局狀態
    const isGlobalLoading = ref(false);
    const isTabLoading = ref(false);
    const tabLoadError = ref('');
    
    // 取得資料
    const analysisTabs = computed(() => spmDataStore.analysisTabs);
    const activeTabId = computed(() => spmDataStore.activeAnalysisTabId);
    const activeTab = computed(() => {
      return analysisTabs.value.find(tab => tab.id === activeTabId.value) || null;
    });
    
    // 活動標籤頁設置
    const activeTabColormap = ref('Oranges');
    const activeTabZScale = ref(1.0);
    
    // 檔案選擇
    const selectedFileId = ref('');
    
    // 影像處理設置
    const fineTuneTilt = ref(false);
    
    // 剖面模式
    const lineProfileMode = ref(false);
    const isDrawingLine = ref(false);
    const lineStart = ref<{x: number, y: number} | null>(null);
    const lineEnd = ref<{x: number, y: number} | null>(null);
    const mouseMovePos = ref({x: 0, y: 0});
    
    // 剖面數據
    const profileData = ref<{distance: number[], height: number[], length: number, stats: any} | null>(null);
    const profileImage = ref<string | null>(null);
    const profileSettings = ref({
      shiftZero: false,
      autoScale: true,
      showPeaks: false,
      peakSensitivity: 1.0
    });
    
    // 可用檔案
    const availableFiles = computed(() => {
      if (!activeTab.value || !activeTab.value.relatedFiles) {
        return [];
      }
      
      return activeTab.value.relatedFiles.filter(file => 
        file.path.toLowerCase().endsWith('.int')
      );
    });
    
    // 要顯示的參數
    const parametersToDisplay = computed(() => {
      if (!activeTab.value || !activeTab.value.parameters) {
        return {};
      }
      
      const params = { ...activeTab.value.parameters };
      // 排除檔案描述
      delete params.FileDescriptions;
      return params;
    });
    
    // 格式化數字
    const formatNumber = (value: number) => {
      if (value === undefined || value === null) return 'N/A';
      return value.toFixed(2);
    };
    
    // 切換標籤頁
    const switchTab = (tabId: string) => {
      spmDataStore.setActiveAnalysisTab(tabId);
      
      // 更新當前標籤頁的設置
      const tab = analysisTabs.value.find(tab => tab.id === tabId);
      if (tab) {
        activeTabColormap.value = tab.colormap || 'Oranges';
        activeTabZScale.value = tab.zScale || 1.0;
      }
    };
    
    // 關閉標籤頁
    const closeTab = (tabId: string) => {
      spmDataStore.removeAnalysisTab(tabId);
    };
    
    // 更新標籤頁設置
    const updateActiveTabSettings = (settings: any) => {
      if (!activeTab.value) return;
      
      spmDataStore.updateAnalysisTabData(activeTabId.value, settings);
    };
    
    // 載入選中檔案
    const loadSelectedFile = async () => {
      if (!selectedFileId.value || !activeTab.value) return;
      
      isTabLoading.value = true;
      tabLoadError.value = '';
      
      try {
        // 檢查檔案類型
        if (selectedFileId.value.toLowerCase().endsWith('.int')) {
          // 處理 INT 檔案
          const response = await window.pywebview.api.analyze_int_file_api(
            selectedFileId.value, 
            activeTab.value.fileId
          );
          
          if (response.success) {
            // 更新標籤頁數據
            const fileName = selectedFileId.value.split(/[\/\\]/).pop() || '';
            
            spmDataStore.updateAnalysisTabData(activeTabId.value, {
              imageData: response.image,
              statistics: response.statistics,
              physUnit: response.physUnit || 'nm',
              dimensions: response.dimensions || {width: 0, height: 0, xRange: 0, yRange: 0},
              currentFileName: fileName,
              fileType: 'topo'
            });
            
            // 更新UI設置
            activeTabColormap.value = activeTab.value.colormap || 'Oranges';
            activeTabZScale.value = activeTab.value.zScale || 1.0;
          } else {
            tabLoadError.value = response.error || '載入檔案時發生錯誤';
          }
        } else {
          tabLoadError.value = '檔案類型不支援';
        }
      } catch (error) {
        console.error('載入檔案錯誤:', error);
        tabLoadError.value = `載入檔案時發生錯誤: ${error}`;
      } finally {
        isTabLoading.value = false;
      }
    };
    
    // 保存圖像
    const saveImage = () => {
      if (!activeTab.value || !activeTab.value.imageData) return;
      
      const downloadLink = document.createElement('a');
      downloadLink.href = 'data:image/png;base64,' + activeTab.value.imageData;
      downloadLink.download = `${activeTab.value.currentFileName || 'image'}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
    };
    
    // 保存剖面圖
    const saveProfileImage = () => {
      if (!profileImage.value) return;
      
      const downloadLink = document.createElement('a');
      downloadLink.href = 'data:image/png;base64,' + profileImage.value;
      downloadLink.download = `profile_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
    };
    
    // 創建線性剖面
    const createLineProfile = () => {
      lineProfileMode.value = true;
    };
    
    // 處理圖像點擊
    const handleImageClick = (event: MouseEvent) => {
      if (!lineProfileMode.value) return;
      
      const rect = (event.target as HTMLElement).getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      if (!lineStart.value) {
        lineStart.value = { x, y };
      } else if (!lineEnd.value) {
        lineEnd.value = { x, y };
        generateProfile();
      } else {
        // 重新開始
        lineStart.value = { x, y };
        lineEnd.value = null;
      }
    };
    
    // 處理圖像滑鼠按下
    const handleImageMouseDown = (event: MouseEvent) => {
      if (!lineProfileMode.value) return;
      
      const rect = (event.target as HTMLElement).getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      lineStart.value = { x, y };
      isDrawingLine.value = true;
    };
    
    // 處理圖像滑鼠移動
    const handleImageMouseMove = (event: MouseEvent) => {
      if (!isDrawingLine.value) return;
      
      const rect = (event.target as HTMLElement).getBoundingClientRect();
      mouseMovePos.value = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
      };
    };
    
    // 處理圖像滑鼠放開
    const handleImageMouseUp = (event: MouseEvent) => {
      if (!isDrawingLine.value) return;
      
      const rect = (event.target as HTMLElement).getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      lineEnd.value = { x, y };
      isDrawingLine.value = false;
      
      generateProfile();
    };
    
    // 生成剖面圖
    const generateProfile = async () => {
      if (!activeTab.value || !activeTab.value.imageData || !lineStart.value || !lineEnd.value) return;
      
      try {
        isTabLoading.value = true;
        
        // 計算物理像素位置
        const imgElement = document.querySelector('img') as HTMLImageElement;
        if (!imgElement) return;
        
        const imgRect = imgElement.getBoundingClientRect();
        const imgWidth = imgElement.naturalWidth;
        const imgHeight = imgElement.naturalHeight;
        
        // 計算相對位置 (0-1)
        const startRelX = lineStart.value.x / imgRect.width;
        const startRelY = lineStart.value.y / imgRect.height;
        const endRelX = lineEnd.value.x / imgRect.width;
        const endRelY = lineEnd.value.y / imgRect.height;
        
        // 計算像素位置
        const startPixelX = Math.floor(startRelX * imgWidth);
        const startPixelY = Math.floor(startRelY * imgHeight);
        const endPixelX = Math.floor(endRelX * imgWidth);
        const endPixelY = Math.floor(endRelY * imgHeight);
        
        // 調用API獲取剖面數據
        const response = await window.pywebview.api.get_line_profile(
          activeTab.value.imageData,
          [startPixelY, startPixelX],
          [endPixelY, endPixelX],
          (activeTab.value.dimensions?.xRange || 100) / (activeTab.value.dimensions?.width || 100),
          profileSettings.value.shiftZero
        );
        
        if (response.success) {
          // 更新剖面數據
          profileData.value = response.profile_data;
          profileImage.value = response.profile_image;
          
          // 退出線性剖面模式
          lineProfileMode.value = false;
          lineStart.value = null;
          lineEnd.value = null;
        } else {
          tabLoadError.value = response.error || '獲取剖面數據失敗';
        }
      } catch (error) {
        console.error('生成剖面圖錯誤:', error);
        tabLoadError.value = `生成剖面圖時發生錯誤: ${error}`;
      } finally {
        isTabLoading.value = false;
      }
    };
    
    // 更新剖面圖
    const updateProfile = async () => {
      if (!profileData.value || !activeTab.value) return;
      
      try {
        isTabLoading.value = true;
        
        // 調用API更新剖面圖
        const response = await window.pywebview.api.update_profile(
          profileData.value,
          profileSettings.value.shiftZero,
          profileSettings.value.autoScale,
          profileSettings.value.showPeaks,
          profileSettings.value.peakSensitivity
        );
        
        if (response.success) {
          profileImage.value = response.profile_image;
        } else {
          tabLoadError.value = response.error || '更新剖面圖失敗';
        }
      } catch (error) {
        console.error('更新剖面圖錯誤:', error);
        tabLoadError.value = `更新剖面圖時發生錯誤: ${error}`;
      } finally {
        isTabLoading.value = false;
      }
    };
    
    // 應用平面化
    const applyFlatten = async (method: string) => {
      if (!activeTab.value || !activeTab.value.imageData) return;
      
      try {
        isTabLoading.value = true;
        
        // 調用API進行平面化處理
        const response = await window.pywebview.api.apply_flatten(
          activeTab.value.imageData,
          method,
          method === 'polyfit' ? 1 : undefined
        );
        
        if (response.success) {
          // 更新標籤頁數據
          spmDataStore.updateAnalysisTabData(activeTabId.value, {
            imageData: response.image,
            statistics: response.statistics
          });
        } else {
          tabLoadError.value = response.error || '平面化處理失敗';
        }
      } catch (error) {
        console.error('平面化處理錯誤:', error);
        tabLoadError.value = `平面化處理時發生錯誤: ${error}`;
      } finally {
        isTabLoading.value = false;
      }
    };
    
    // 調整傾斜
    const adjustTilt = async (direction: string) => {
      if (!activeTab.value || !activeTab.value.imageData) return;
      
      try {
        isTabLoading.value = true;
        
        // 調用API進行傾斜調整
        const response = await window.pywebview.api.tilt_image(
          activeTab.value.imageData,
          direction,
          fineTuneTilt.value
        );
        
        if (response.success) {
          // 更新標籤頁數據
          spmDataStore.updateAnalysisTabData(activeTabId.value, {
            imageData: response.image,
            statistics: response.statistics
          });
        } else {
          tabLoadError.value = response.error || '傾斜調整失敗';
        }
      } catch (error) {
        console.error('傾斜調整錯誤:', error);
        tabLoadError.value = `傾斜調整時發生錯誤: ${error}`;
      } finally {
        isTabLoading.value = false;
      }
    };
    
    // 監視標籤頁變化
    watch(activeTabId, () => {
      if (activeTab.value) {
        // 更新當前標籤頁設置
        activeTabColormap.value = activeTab.value.colormap || 'Oranges';
        activeTabZScale.value = activeTab.value.zScale || 1.0;
        
        // 重置剖面模式
        lineProfileMode.value = false;
        lineStart.value = null;
        lineEnd.value = null;
      }
    });
    
    // 監視標籤頁列表
    watch(analysisTabs, (newTabs, oldTabs) => {
      // 如果添加了新標籤頁
      if (newTabs.length > oldTabs.length) {
        const newTab = newTabs.find(tab => !oldTabs.some(oldTab => oldTab.id === tab.id));
        
        if (newTab) {
          // 自動載入第一個可用的 INT 檔案
          const intFile = newTab.relatedFiles?.find(f => f.path.toLowerCase().endsWith('.int'));
          
          if (intFile) {
            selectedFileId.value = intFile.path;
            
            // 延遲執行載入，確保UI已更新
            setTimeout(() => {
              loadSelectedFile();
            }, 100);
          }
        }
      }
    }, { deep: true });
    
    // 初始化
    onMounted(() => {
      // 檢查是否有活動標籤頁
      if (activeTab.value) {
        // 更新當前標籤頁設置
        activeTabColormap.value = activeTab.value.colormap || 'Oranges';
        activeTabZScale.value = activeTab.value.zScale || 1.0;
        
        // 如果沒有圖像數據，自動載入第一個 INT 檔案
        if (!activeTab.value.imageData) {
          const intFile = activeTab.value.relatedFiles?.find(f => f.path.toLowerCase().endsWith('.int'));
          
          if (intFile) {
            selectedFileId.value = intFile.path;
            loadSelectedFile();
          }
        }
      }
    });
    
    return {
      // 狀態
      isGlobalLoading,
      isTabLoading,
      tabLoadError,
      analysisTabs,
      activeTabId,
      activeTab,
      selectedFileId,
      availableFiles,
      activeTabColormap,
      activeTabZScale,
      parametersToDisplay,
      
      // 影像處理
      fineTuneTilt,
      
      // 剖面相關
      lineProfileMode,
      isDrawingLine,
      lineStart,
      lineEnd,
      mouseMovePos,
      profileData,
      profileImage,
      profileSettings,
      
      // 方法
      formatNumber,
      switchTab,
      closeTab,
      loadSelectedFile,
      updateActiveTabSettings,
      saveImage,
      saveProfileImage,
      applyFlatten,
      adjustTilt,
      createLineProfile,
      handleImageClick,
      handleImageMouseDown,
      handleImageMouseMove,
      handleImageMouseUp,
      updateProfile
    };
  }
});
</script>

<style scoped>
/* 自定義樣式 */
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 14px;
  background: #2563eb;
  border-radius: 50%;
  cursor: pointer;
}

input[type="range"]::-moz-range-thumb {
  width: 14px;
  height: 14px;
  background: #2563eb;
  border-radius: 50%;
  cursor: pointer;
}

.max-h-80 {
  max-height: 20rem;
}

.max-h-80::-webkit-scrollbar {
  width: 6px;
}

.max-h-80::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.max-h-80::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.max-h-80::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}
</style>