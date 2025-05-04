<!-- src/components/AnalysisView.vue -->
<template>
  <div class="h-full flex flex-col bg-white rounded-lg shadow overflow-hidden relative">
    <!-- 沒有標籤頁時的歡迎畫面 -->
    <div v-if="analysisTabs.length === 0" class="flex flex-col items-center justify-center h-full p-6 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <p class="text-gray-500 mb-4">尚未開啟任何分析標籤頁</p>
      <p class="text-gray-500 text-sm">請在檔案選擇器中雙擊檔案或使用"分析"按鈕開始進行分析</p>
    </div>

    <!-- 有標籤頁時的分析介面 -->
    <div v-else class="h-full flex relative">
      <!-- 左側面板區域 -->
      <div class="h-full flex flex-col">
        <!-- 檔案選擇器迷你面板 -->
        <div 
          class="sidebar-panel bg-white border-r border-gray-200 transition-all duration-300 flex flex-col"
          :class="showFileSelector ? 'w-80' : 'w-12'"
        >
          <!-- 標題或迷你按鈕 -->
          <div 
            class="flex items-center p-2 border-b border-gray-200 bg-gray-50"
            :class="showFileSelector ? 'justify-between' : 'justify-center'"
          >
            <h3 v-if="showFileSelector" class="text-sm font-medium text-gray-700 truncate">檔案選擇</h3>
            <button 
              @click="toggleFileSelector"
              class="p-1.5 rounded hover:bg-gray-200 text-gray-600 focus:outline-none"
              :title="showFileSelector ? '收起檔案選擇器' : '展開檔案選擇器'"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                class="h-5 w-5" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
                :class="{ 'transform rotate-180': showFileSelector }"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
          </div>
          
          <!-- 檔案選擇器內容 -->
          <div v-if="showFileSelector" class="flex-grow overflow-y-auto p-4">
            <div v-if="activeTab">
              <h3 class="text-sm font-medium text-gray-700 mb-2">選擇分析檔案</h3>
              
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
              
              <!-- 檔案資訊區塊 -->
              <div v-if="activeTab && activeTab.txtContent" class="mt-4 pt-4 border-t border-gray-200">
                <h3 class="text-sm font-medium text-gray-700 mb-3">檔案資訊</h3>
                
                <div class="bg-white rounded-lg border border-gray-200 overflow-y-auto max-h-80">
                  <!-- 基本參數 -->
                  <div class="p-3">
                    <h4 class="font-medium text-sm border-b pb-1 mb-3">基本參數</h4>
                    
                    <div class="grid grid-cols-1 gap-1.5">
                      <!-- 參數項目 - 每個參數一行 -->
                      <div v-for="(value, key) in parametersToDisplay" :key="key" class="info-row flex">
                        <div class="text-sm font-medium text-gray-700 w-32 flex-shrink-0">{{ key }}:</div>
                        <div class="text-sm text-gray-900 flex-1">{{ value }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center text-gray-500 text-sm pt-4">
              請先選擇一個分析標籤頁
            </div>
          </div>
          
          <!-- 迷你模式下只顯示圖標 -->
          <div v-else class="flex-grow flex flex-col items-center pt-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
        
        <!-- 工具列迷你面板 -->
        <div 
          class="sidebar-panel bg-white border-r border-gray-200 transition-all duration-300 flex flex-col mt-2"
          :class="showToolsPanel ? 'w-80' : 'w-12'"
        >
          <!-- 標題或迷你按鈕 -->
          <div 
            class="flex items-center p-2 border-b border-gray-200 bg-gray-50"
            :class="showToolsPanel ? 'justify-between' : 'justify-center'"
          >
            <h3 v-if="showToolsPanel" class="text-sm font-medium text-gray-700 truncate">工具列</h3>
            <button 
              @click="toggleToolsPanel"
              class="p-1.5 rounded hover:bg-gray-200 text-gray-600 focus:outline-none"
              :title="showToolsPanel ? '收起工具列' : '展開工具列'"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                class="h-5 w-5" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
                :class="{ 'transform rotate-180': showToolsPanel }"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
          </div>
          
          <!-- 工具列內容 -->
          <div v-if="showToolsPanel" class="flex-grow overflow-y-auto p-4">
            <template v-if="activeViewer">
              <div v-if="activeViewer.component === 'ImageViewer'" class="space-y-4">
                <h4 class="font-medium text-sm border-b pb-2 mb-2">影像處理</h4>
                
                <!-- 平面校正工具 -->
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
                
                <!-- 傾斜調整工具 -->
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
              
              <!-- 剖面視圖工具 -->
              <div v-else-if="activeViewer.component === 'ProfileViewer'" class="space-y-4">
                <h4 class="font-medium text-sm border-b pb-2 mb-2">剖面設定</h4>
                
                <!-- 將最小值歸零選項 -->
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
                
                <!-- 自動縮放選項 -->
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
                
                <!-- 顯示峰值選項 -->
                <div class="flex items-center">
                  <input 
                    type="checkbox" 
                    id="show-peaks" 
                    v-model="profileSettings.showPeaks"
                    class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    @change="updateProfile"
                  >
                  <label for="show-peaks" class="ml-2 text-sm text-gray-700">
                    顯示峰值
                  </label>
                </div>
                
                <!-- 峰值敏感度 -->
                <div v-if="profileSettings.showPeaks">
                  <div class="flex justify-between mb-1">
                    <label class="text-xs text-gray-500">峰值敏感度</label>
                    <span class="text-xs text-gray-500">{{ profileSettings.peakSensitivity.toFixed(1) }}</span>
                  </div>
                  <input 
                    type="range" 
                    v-model="profileSettings.peakSensitivity" 
                    min="0.1" 
                    max="5" 
                    step="0.1" 
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    @change="updateProfile"
                  >
                </div>
              </div>
              
              <div v-else class="p-4 text-center text-gray-500">
                <p>無可用工具</p>
              </div>
            </template>
            
            <div v-else class="p-4 text-center text-gray-500">
              <p>請選擇一個視圖來顯示相應工具</p>
            </div>
          </div>
          
          <!-- 迷你模式下只顯示圖標 -->
          <div v-else class="flex-grow flex flex-col items-center pt-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
        </div>
      </div>
      
      <!-- 主要分析標籤頁區域 -->
      <div class="flex-1 h-full">
        <AnalysisTabs
          :tabs="analysisTabs"
          :active-tab-id="activeTabId"
          @tab-switched="switchTab"
          @tab-closed="closeTab"
          @tab-added="addTab"
          @tab-updated="updateTab"
          @group-to-tab="handleGroupToTab"
          @create-line-profile="createLineProfile"
        />
      </div>

      <!-- 載入中顯示 -->
      <div v-if="isTabLoading" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20 z-50">
        <div class="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
          <div class="w-12 h-12 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-4"></div>
          <p class="text-gray-600">正在載入資料...</p>
        </div>
      </div>

      <!-- 錯誤提示 -->
      <div v-if="tabLoadError" 
           class="absolute top-4 right-4 max-w-md p-4 bg-red-50 border-l-4 border-red-400 text-red-700 z-50 rounded shadow-md">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm">{{ tabLoadError }}</p>
          </div>
          <div class="ml-auto pl-3">
            <button @click="tabLoadError = ''" class="text-red-400 hover:text-red-500 focus:outline-none">
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue';
import { useSpmDataStore } from '../stores/spmDataStore';
import AnalysisTabs from './analysis/AnalysisTabs.vue';

export default defineComponent({
  name: 'AnalysisView',
  components: {
    AnalysisTabs
  },
  setup() {
    const spmDataStore = useSpmDataStore();
    
    // 全局狀態
    const isTabLoading = ref(false);
    const tabLoadError = ref('');
    
    // 側邊面板狀態
    const showFileSelector = ref(true);
    const showToolsPanel = ref(true);
    
    // 取得資料
    const analysisTabs = computed(() => spmDataStore.analysisTabs);
    const activeTabId = computed(() => spmDataStore.activeAnalysisTabId);
    const activeTab = computed(() => {
      return analysisTabs.value.find(tab => tab.id === activeTabId.value) || null;
    });
    
    // 當前活動的視圖
    const activeViewer = computed(() => {
      if (!activeTab.value || !activeTab.value.viewerGroups) return null;
      
      for (const group of activeTab.value.viewerGroups) {
        for (const viewer of group.viewers) {
          if (viewer.props && viewer.props.isActive) {
            return viewer;
          }
        }
      }
      
      return null;
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
    
    // 切換檔案選擇器
    const toggleFileSelector = () => {
      showFileSelector.value = !showFileSelector.value;
    };
    
    // 切換工具面板
    const toggleToolsPanel = () => {
      showToolsPanel.value = !showToolsPanel.value;
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
    
    // 添加標籤頁
    const addTab = (tab: any) => {
      // 實現添加標籤頁的邏輯
    };
    
    // 更新標籤頁
    const updateTab = ({ id, changes }: { id: string, changes: any }) => {
      // 實現更新標籤頁的邏輯
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
            
            // 創建新的視圖群組
            const groupId = `group-${activeTab.value.id}-${Date.now()}`;
            const imageViewer = {
              id: `viewer-image-${Date.now()}`,
              component: 'ImageViewer',
              props: {
                imageData: response.image,
                title: fileName,
                imageType: 'topo',
                physUnit: response.physUnit || 'nm',
                colormap: activeTab.value.colormap || 'Oranges',
                zScale: activeTab.value.zScale || 1.0,
                stats: response.statistics || null,
                dimensions: response.dimensions || { width: 0, height: 0, xRange: 0, yRange: 0 },
                isActive: true
              }
            };
            
            // 如果標籤頁尚未有視圖群組，添加一個新的
            if (!activeTab.value.viewerGroups || activeTab.value.viewerGroups.length === 0) {
              spmDataStore.updateAnalysisTabData(activeTabId.value, {
                viewerGroups: [{
                  id: groupId,
                  title: fileName,
                  viewers: [imageViewer],
                  layout: 'horizontal'
                }]
              });
            } else {
              // 如果已經有視圖群組，添加到第一個群組
              const updatedGroups = [...activeTab.value.viewerGroups];
              updatedGroups[0].viewers.push(imageViewer);
              
              spmDataStore.updateAnalysisTabData(activeTabId.value, {
                viewerGroups: updatedGroups
              });
            }
            
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
    
    // 處理群組轉標籤頁
    const handleGroupToTab = (groupData: any) => {
      // 實現群組轉標籤頁的邏輯
    };
    
    // 創建線性剖面
    const createLineProfile = (data: any) => {
      // 實現創建線性剖面的邏輯
      lineProfileMode.value = true;
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
    const applyFlatten = async (method) => {
      if (!activeViewer.value || activeViewer.value.component !== 'ImageViewer') return;
      
      try {
        // 找到當前活動的視圖
        const group = activeTab.value.viewerGroups.find(g => g.id === activeGroupId);
        if (!group) return;
        
        const viewerIndex = group.viewers.findIndex(v => 
          v.props && v.props.isActive && v.component === 'ImageViewer'
        );
        
        if (viewerIndex === -1) return;
        
        // 獲取當前視圖的原始數據
        const imageData = group.viewers[viewerIndex].props.imageRawData;
        if (!imageData) {
          tabLoadError.value = "沒有可用的圖像數據";
          return;
        }
        
        isTabLoading.value = true;
        
        // 調用API進行平面化處理
        const response = await window.pywebview.api.apply_flatten(
          imageData, 
          method, 
          method === 'polyfit' ? 2 : 1  // 對於多項式方法，使用2階
        );
        
        if (response.success) {
          // 更新視圖數據
          const updatedViewers = [...group.viewers];
          updatedViewers[viewerIndex] = {
            ...updatedViewers[viewerIndex],
            props: {
              ...updatedViewers[viewerIndex].props,
              imageRawData: response.processed_data,
              statistics: response.statistics
            }
          };
          
          // 更新視圖組
          const updatedGroups = [...activeTab.value.viewerGroups];
          updatedGroups[updatedGroups.indexOf(group)] = {
            ...group,
            viewers: updatedViewers
          };
          
          // 更新標籤頁
          spmDataStore.updateAnalysisTabData(activeTabId.value, {
            viewerGroups: updatedGroups
          });
        } else {
          tabLoadError.value = response.error || "平面化處理失敗";
        }
      } catch (error) {
        console.error('平面化處理錯誤:', error);
        tabLoadError.value = `平面化處理時發生錯誤: ${error}`;
      } finally {
        isTabLoading.value = false;
      }
    };
    
    // 調整傾斜
    const adjustTilt = async (direction) => {
      if (!activeViewer.value || activeViewer.value.component !== 'ImageViewer') return;
      
      try {
        // 找到當前活動的視圖
        const group = activeTab.value.viewerGroups.find(g => g.id === activeGroupId);
        if (!group) return;
        
        const viewerIndex = group.viewers.findIndex(v => 
          v.props && v.props.isActive && v.component === 'ImageViewer'
        );
        
        if (viewerIndex === -1) return;
        
        // 獲取當前視圖的原始數據
        const imageData = group.viewers[viewerIndex].props.imageRawData;
        if (!imageData) {
          tabLoadError.value = "沒有可用的圖像數據";
          return;
        }
        
        isTabLoading.value = true;
        
        // 調用API進行傾斜調整
        const response = await window.pywebview.api.tilt_image(
          imageData, 
          direction,
          fineTuneTilt.value
        );
        
        if (response.success) {
          // 更新視圖數據
          const updatedViewers = [...group.viewers];
          updatedViewers[viewerIndex] = {
            ...updatedViewers[viewerIndex],
            props: {
              ...updatedViewers[viewerIndex].props,
              imageRawData: response.processed_data,
              statistics: response.statistics
            }
          };
          
          // 更新視圖組
          const updatedGroups = [...activeTab.value.viewerGroups];
          updatedGroups[updatedGroups.indexOf(group)] = {
            ...group,
            viewers: updatedViewers
          };
          
          // 更新標籤頁
          spmDataStore.updateAnalysisTabData(activeTabId.value, {
            viewerGroups: updatedGroups
          });
        } else {
          tabLoadError.value = response.error || "傾斜調整失敗";
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
          // 自動顯示控制面板
          showFileSelector.value = true;
          
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
        
        // 如果沒有圖像數據，自動顯示控制面板
        if (!activeTab.value.imageData && !activeTab.value.viewerGroups) {
          showFileSelector.value = true;
          
          // 自動載入第一個 INT 檔案
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
      isTabLoading,
      tabLoadError,
      analysisTabs,
      activeTabId,
      activeTab,
      activeViewer,
      selectedFileId,
      availableFiles,
      activeTabColormap,
      activeTabZScale,
      parametersToDisplay,
      showFileSelector,
      showToolsPanel,
      
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
      toggleFileSelector,
      toggleToolsPanel,
      switchTab,
      closeTab,
      addTab,
      updateTab,
      loadSelectedFile,
      handleGroupToTab,
      updateActiveTabSettings,
      createLineProfile,
      updateProfile,
      applyFlatten,
      adjustTilt
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

/* 側邊面板高度設置 */
.sidebar-panel {
  max-height: calc(50vh - 30px);
  min-height: 200px;
}

/* 最大高度限制 */
.max-h-80 {
  max-height: 20rem;
}

/* 滾動條樣式 */
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