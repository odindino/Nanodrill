<!-- src/components/FileSelector.vue -->
<template>
  <div class="h-full flex overflow-hidden">
    <!-- 檔案選擇器主區域 -->
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
                <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 tracking-wider w-24">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr 
                v-for="file in filteredAndSortedFiles" 
                :key="file.path"
                :class="[
                  file.hasDatFile ? 'bg-secondary-50/30' : '',
                  isSelected(file) ? 'bg-primary-50' : '',
                  isPreviewingFile(file) ? 'bg-blue-50' : '',
                  'hover:bg-gray-50'
                ]"
                @dblclick="openFileForAnalysis(file)"
              >
                <td class="px-4 py-2 text-sm" :style="{ maxWidth: columnWidths.filename + 'px' }">
                  <div class="flex items-center space-x-2 overflow-hidden">
                    <span v-if="file.hasDatFile" class="text-secondary flex-shrink-0 text-lg" title="該檔案有對應的 IV 曲線數據">⚡</span>
                    <span 
                      class="truncate cursor-pointer hover:text-primary" 
                      :title="file.name"
                      @click="showPreview(file)"
                    >
                      {{ file.name }}
                    </span>
                  </div>
                </td>
                <td class="px-4 py-2 text-xs text-gray-500 truncate" :style="{ maxWidth: columnWidths.time + 'px' }">
                  {{ file.modTimeStr }}
                </td>
                <td class="px-4 py-2 text-sm text-center">
                  <div class="flex space-x-1 justify-center">
                    <button 
                      @click="showPreview(file)" 
                      class="inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded text-white bg-secondary hover:bg-secondary-dark focus:outline-none focus:ring-1 focus:ring-secondary focus:ring-offset-1"
                      title="預覽圖像"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button 
                      @click="viewFile(file)" 
                      class="inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-1 focus:ring-primary focus:ring-offset-1"
                      title="查看檔案詳情"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </button>
                    <button 
                      @click="openFileForAnalysis(file)" 
                      class="inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-1 focus:ring-green-500 focus:ring-offset-1"
                      title="進行分析"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </button>
                  </div>
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
    
    <!-- 預覽面板 -->
    <div v-if="showPreviewPanel" 
        ref="previewPanelRef"
        class="h-full flex flex-col bg-white shadow-md border-l border-gray-200 transition-all duration-300 ease-in-out overflow-hidden"
        :style="{ width: previewPanelWidth + 'px' }">
      
      <!-- 預覽面板頭部 -->
      <div class="flex items-center justify-between px-4 py-3 bg-gray-100 border-b border-gray-200">
        <h3 class="font-medium text-gray-900 truncate flex-1">
          {{ previewModalTitle }}
        </h3>
        <button @click="closePreview" 
                class="p-1.5 rounded-full hover:bg-gray-200 text-gray-500 focus:outline-none">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <!-- 預覽面板內容 -->
      <div class="flex flex-col flex-grow overflow-hidden">
        <!-- 載入中指示器 -->
        <div v-if="previewLoading" class="flex-grow flex items-center justify-center p-8">
          <div class="flex flex-col items-center">
            <div class="w-10 h-10 border-4 border-gray-200 border-t-primary rounded-full animate-spin mb-4"></div>
            <span class="text-gray-600">正在載入預覽資料...</span>
          </div>
        </div>
        
        <!-- 錯誤訊息 -->
        <div v-else-if="previewError" class="flex-grow p-6 overflow-y-auto">
          <div class="bg-red-50 border-l-4 border-red-500 p-4 text-red-800">
            <p class="font-medium">載入預覽失敗</p>
            <p class="mt-2">{{ previewError }}</p>
          </div>
        </div>
        
        <!-- 預覽內容 -->
        <div v-else-if="previewData" class="flex-grow flex flex-col overflow-hidden">
          <!-- 標籤頁導航 -->
          <div class="bg-gray-50 border-b border-gray-200 flex-shrink-0">
            <div class="flex">
              <button 
                v-for="tab in previewTabs" 
                :key="tab.id" 
                @click="activePreviewTab = tab.id"
                class="px-4 py-2 text-sm font-medium border-b-2 focus:outline-none transition-colors"
                :class="[
                  activePreviewTab === tab.id 
                    ? 'border-primary text-primary' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                {{ tab.name }}
              </button>
            </div>
          </div>
          
          <!-- 標籤頁內容 -->
          <div class="flex-grow flex overflow-hidden">
            <!-- 形貌圖頁面 -->
            <div v-if="activePreviewTab === 'image'" class="flex-grow flex flex-col overflow-hidden">
              <!-- 圖像顯示區域 -->
              <div class="flex-grow overflow-auto p-4 bg-gray-50">
                <img v-if="previewImage" 
                    :src="'data:image/png;base64,' + previewImage" 
                    alt="形貌預覽" 
                    class="w-full max-w-full h-auto rounded border border-gray-200 bg-white" />
                <div v-else class="flex items-center justify-center h-full text-gray-500">
                  無法載入形貌圖像
                </div>
              </div>
              
              <!-- 重要參數展示面板 -->
              <div v-if="previewData && previewData.parameters" class="bg-white border-t border-gray-200 p-3 flex-shrink-0">
                <h4 class="text-gray-700 text-sm font-medium mb-2">重要測量參數</h4>
                <div class="grid grid-cols-2 gap-2 text-sm">
                  <!-- 日期和時間 -->
                  <div class="bg-gray-50 p-2 rounded border border-gray-200">
                    <span class="text-gray-600">量測日期時間:</span>
                    <span class="ml-1 font-medium text-xs">{{ formatDateTime(previewData.parameters.Date, previewData.parameters.Time) }}</span>
                  </div>
                  
                  <!-- 量測電壓 -->
                  <div class="bg-gray-50 p-2 rounded border border-gray-200">
                    <span class="text-gray-600">樣品電壓:</span>
                    <span class="ml-1 font-medium text-xs">{{ previewData.parameters.Bias || 'N/A' }} {{ previewData.parameters.BiasPhysUnit || '' }}</span>
                  </div>
                  
                  <!-- 量測電流 -->
                  <div class="bg-gray-50 p-2 rounded border border-gray-200">
                    <span class="text-gray-600">設定電流:</span>
                    <span class="ml-1 font-medium text-xs">{{ previewData.parameters.SetPoint || 'N/A' }} {{ previewData.parameters.SetPointPhysUnit || '' }}</span>
                  </div>
                  
                  <!-- 量測範圍 -->
                  <div class="bg-gray-50 p-2 rounded border border-gray-200">
                    <span class="text-gray-600">掃描範圍:</span>
                    <span class="ml-1 font-medium text-xs">{{ previewData.parameters.XScanRange || '0' }} × {{ previewData.parameters.YScanRange || '0' }} {{ previewData.parameters.XPhysUnit || 'nm' }}</span>
                  </div>
                  
                  <!-- 量測中心 -->
                  <div class="bg-gray-50 p-2 rounded border border-gray-200">
                    <span class="text-gray-600">掃描中心:</span>
                    <span class="ml-1 font-medium text-xs">{{ previewData.parameters.xCenter || '0' }}, {{ previewData.parameters.yCenter || '0' }} {{ previewData.parameters.XPhysUnit || 'nm' }}</span>
                  </div>
                  
                  <!-- 量測角度 -->
                  <div class="bg-gray-50 p-2 rounded border border-gray-200">
                    <span class="text-gray-600">掃描角度:</span>
                    <span class="ml-1 font-medium text-xs">{{ previewData.parameters.Angle || '0' }}°</span>
                  </div>
                </div>
              </div>
              
              <!-- 統計數據面板 -->
              <div v-if="previewStats" class="p-3 bg-white border-t border-gray-200 flex-shrink-0">
                <h4 class="text-gray-700 text-sm font-medium mb-2">數據統計</h4>
                <div class="grid grid-cols-2 gap-2 text-sm">
                  <div class="bg-gray-50 p-2 rounded border border-gray-200">
                    <span class="text-gray-600">最小值:</span>
                    <span class="ml-1 font-mono text-xs">{{ formatNumber(previewStats.min) }} {{ previewUnit }}</span>
                  </div>
                  <div class="bg-gray-50 p-2 rounded border border-gray-200">
                    <span class="text-gray-600">最大值:</span>
                    <span class="ml-1 font-mono text-xs">{{ formatNumber(previewStats.max) }} {{ previewUnit }}</span>
                  </div>
                  <div class="bg-gray-50 p-2 rounded border border-gray-200">
                    <span class="text-gray-600">平均值:</span>
                    <span class="ml-1 font-mono text-xs">{{ formatNumber(previewStats.mean) }} {{ previewUnit }}</span>
                  </div>
                  <div class="bg-gray-50 p-2 rounded border border-gray-200">
                    <span class="text-gray-600">RMS:</span>
                    <span class="ml-1 font-mono text-xs">{{ formatNumber(previewStats.rms) }} {{ previewUnit }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 參數頁面 -->
            <div v-else-if="activePreviewTab === 'params'" class="flex-grow p-4 overflow-auto bg-gray-50">
              <!-- 基本參數區塊 -->
              <div class="bg-white rounded-lg shadow mb-6 overflow-hidden">
                <div class="bg-gray-100 px-4 py-2 font-medium text-gray-700 border-b border-gray-200">
                  基本參數
                </div>
                <div class="p-4">
                  <div class="grid grid-cols-2 gap-x-6 gap-y-3">
                    <div v-for="(value, key) in basicParameters" :key="key" class="flex justify-between border-b border-gray-100 py-1">
                      <span class="text-sm text-gray-600">{{ key }}:</span>
                      <span class="text-sm font-medium">{{ value }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 檔案描述區塊 -->
              <div v-if="fileDescriptions.length > 0" class="bg-white rounded-lg shadow overflow-hidden">
                <div class="bg-gray-100 px-4 py-2 font-medium text-gray-700 border-b border-gray-200">
                  相關檔案
                </div>
                <div class="p-4">
                  <div v-for="(desc, index) in fileDescriptions" 
                      :key="index" 
                      class="mb-4 last:mb-0 border border-gray-200 rounded-lg overflow-hidden">
                    <div class="bg-gray-50 px-3 py-2 font-medium text-sm border-b border-gray-200">
                      {{ desc.Caption || desc.FileName }}
                    </div>
                    <div class="p-3 grid grid-cols-2 gap-2">
                      <div>
                        <div class="text-xs text-gray-500">檔案名稱</div>
                        <div class="text-sm mt-1">{{ desc.FileName }}</div>
                      </div>
                      <div>
                        <div class="text-xs text-gray-500">物理單位</div>
                        <div class="text-sm mt-1">{{ desc.PhysUnit }}</div>
                      </div>
                      <div class="col-span-2">
                        <div class="text-xs text-gray-500">縮放比例</div>
                        <div class="text-sm font-mono mt-1">{{ desc.Scale }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 原始文件內容頁面 -->
            <div v-else-if="activePreviewTab === 'raw'" class="flex-grow overflow-auto">
              <pre class="p-4 text-xs font-mono whitespace-pre-wrap bg-gray-50 h-full">{{ rawContent }}</pre>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 可調整預覽面板寬度的把手 -->
      <div class="preview-resize-handle" @mousedown="startResizingPreviewWidth"></div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
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

interface FileDescription {
  FileName: string;
  Caption?: string;
  Scale?: string;
  PhysUnit?: string;
  Offset?: string;
}

declare global {
  interface Window {
    pywebview: {
      api: {
        open_folder_dialog: () => Promise<any>;
        get_folder_files: (path: string) => Promise<any>;
        get_txt_file_content: (path: string) => Promise<any>;
        get_int_file_preview: (path: string) => Promise<any>;
      };
    };
  }
}

export default defineComponent({
  name: 'FileSelector',
  emits: ['close', 'width-changed', 'file-selected-for-analysis'],
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
    
    // 預覽面板相關引用
    const previewPanelRef = ref<HTMLDivElement | null>(null);
    
    // 預覽面板相關狀態
    const showPreviewPanel = ref<boolean>(false);
    const previewPanelWidth = ref<number>(userPreferencesStore.previewPanelWidth || 480); // 預覽面板寬度
    const previewModalTitle = ref<string>('');
    const previewLoading = ref<boolean>(false);
    const previewError = ref<string | null>(null);
    const previewImage = ref<string | null>(null);
    const previewStats = ref<any | null>(null);
    const previewUnit = ref<string>('nm');
    const previewFile = ref<string | null>(null);
    const previewData = ref<any | null>(null);
    const rawContent = ref<string>('');
    const fileDescriptions = ref<FileDescription[]>([]);
    
    // 預覽標籤頁
    const activePreviewTab = ref<string>('image');
    const previewTabs = [
      { id: 'image', name: '形貌圖' },
      { id: 'params', name: '參數' },
      { id: 'raw', name: '原始內容' }
    ];
    
    // 從預覽資料中提取基本參數，排除檔案描述
    const basicParameters = computed(() => {
      if (!previewData.value || !previewData.value.parameters) {
        return {};
      }
      
      const params = { ...previewData.value.parameters };
      delete params.FileDescriptions;
      return params;
    });
    
    // 格式化日期和時間
    const formatDateTime = (date: string, time: string) => {
      if (!date && !time) return 'N/A';
      return `${date || ''} ${time || ''}`;
    };
    
    // 檢查是否正在預覽某個檔案
    const isPreviewingFile = (file: FileInfo) => {
      return previewFile.value === file.path && showPreviewPanel.value;
    };
    
    // 監視排序選項變更並保存
    watch(sortOption, (newValue) => {
      userPreferencesStore.setSortOption(newValue);
    });
    
    // 監視預覽面板寬度的變更
    watch(previewPanelWidth, (newWidth) => {
      userPreferencesStore.setPreviewPanelWidth(newWidth);
    });
    
    // 可調整選擇器寬度相關狀態
    const isResizing = ref(false);
    const startX = ref(0);
    const startWidth = ref(0);
    
    // 可調整預覽面板寬度相關狀態
    const isResizingPreview = ref(false);
    const previewStartX = ref(0);
    const previewStartWidth = ref(0);
    
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
        // 先關閉預覽面板
        closePreview();
        
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
    
    // 顯示預覽圖
    const showPreview = async (file: FileInfo) => {
      try {
        // 重置預覽狀態
        previewError.value = null;
        previewImage.value = null;
        previewStats.value = null;
        previewData.value = null;
        rawContent.value = '';
        fileDescriptions.value = [];
        previewLoading.value = true;
        previewFile.value = file.path;
        previewModalTitle.value = `預覽 - ${file.name}`;
        activePreviewTab.value = 'image'; // 預設顯示形貌圖標籤頁
        
        // 顯示預覽面板
        showPreviewPanel.value = true;
        
        // 獲取 TXT 檔案內容
        const txtResult = await window.pywebview.api.get_txt_file_content(file.path);
        
        if (txtResult.success) {
          previewData.value = txtResult;
          rawContent.value = txtResult.content;
          
          if (txtResult.parameters && txtResult.parameters.FileDescriptions) {
            fileDescriptions.value = txtResult.parameters.FileDescriptions;
          }
          
          // 獲取預覽圖
          console.log('正在獲取預覽圖:', file.path);
          const imgResult = await window.pywebview.api.get_int_file_preview(file.path);
          
          if (imgResult.success && imgResult.image) {
            console.log('預覽圖獲取成功，大小:', imgResult.image.length);
            previewImage.value = imgResult.image;
            previewStats.value = imgResult.statistics;
            previewUnit.value = imgResult.physUnit || 'nm';
          } else {
            console.warn('預覽圖獲取失敗:', imgResult.error);
            // 即使圖像獲取失敗，我們仍然顯示 TXT 檔案內容，所以不設置 previewError
          }
        } else {
          console.error('TXT 檔案內容獲取失敗:', txtResult.error);
          previewError.value = txtResult.error || '無法獲取檔案內容';
        }
      } catch (error) {
        console.error('預覽載入錯誤:', error);
        previewError.value = `系統錯誤: ${error}`;
      } finally {
        previewLoading.value = false;
      }
    };
    
    // 關閉預覽面板
    const closePreview = () => {
      showPreviewPanel.value = false;
      previewFile.value = null;
      previewImage.value = null;
      previewStats.value = null;
      previewData.value = null;
      rawContent.value = '';
      fileDescriptions.value = [];
      previewError.value = null;
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

    // 開始調整預覽面板寬度
    const startResizingPreviewWidth = (e: MouseEvent) => {
      e.preventDefault();
      isResizingPreview.value = true;
      previewStartX.value = e.clientX;
      previewStartWidth.value = previewPanelWidth.value;
      
      // 添加全局滑鼠事件
      document.addEventListener('mousemove', onMouseMoveForPreviewPanel);
      document.addEventListener('mouseup', onMouseUpForPreviewPanel);
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

    // 滑鼠移動時調整預覽面板寬度
    const onMouseMoveForPreviewPanel = (e: MouseEvent) => {
      if (!isResizingPreview.value) return;
      
      const newWidth = previewStartWidth.value - (e.clientX - previewStartX.value);
      // 設定最小和最大寬度
      previewPanelWidth.value = Math.max(350, Math.min(900, newWidth));
    };

    // 滑鼠放開時結束調整選擇器寬度，並保存設定
    const onMouseUpForPanel = () => {
      isResizing.value = false;
      document.removeEventListener('mousemove', onMouseMoveForPanel);
      document.removeEventListener('mouseup', onMouseUpForPanel);
      
      // 保存選擇器寬度到偏好設定
      userPreferencesStore.setFileSelectorWidth(selectorWidth.value);
    };

    // 滑鼠放開時結束調整預覽面板寬度，並保存設定
    const onMouseUpForPreviewPanel = () => {
      isResizingPreview.value = false;
      document.removeEventListener('mousemove', onMouseMoveForPreviewPanel);
      document.removeEventListener('mouseup', onMouseUpForPreviewPanel);
      
      // 保存預覽面板寬度到偏好設定
      userPreferencesStore.setPreviewPanelWidth(previewPanelWidth.value);
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
    
    // 格式化數字顯示，保留 2 位小數
    const formatNumber = (value: number) => {
      if (value === null || value === undefined) return 'N/A';
      return value.toFixed(2);
    };
    
    // 處理ESC鍵關閉預覽面板
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && showPreviewPanel.value) {
        closePreview();
      }
    };

    // 打開檔案進行分析
    const openFileForAnalysis = (file: FileInfo) => {
      // 只允許 txt 檔案使用分析功能
      if (file.type !== 'txt') {
        // 可以選擇顯示錯誤提示
        return;
      }
      
      emit('file-selected-for-analysis', file);
    };
    
    // 組件掛載時添加鍵盤事件監聽
    onMounted(() => {
      document.addEventListener('keydown', handleKeyDown);
      
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
              spmDataStore.setCurrentDirectory(lastDir);
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
    
    // 組件卸載時移除事件監聽器
    onBeforeUnmount(() => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousemove', onMouseMoveForPanel);
      document.removeEventListener('mouseup', onMouseUpForPanel);
      document.removeEventListener('mousemove', onMouseMoveForColumn);
      document.removeEventListener('mouseup', onMouseUpForColumn);
      document.removeEventListener('mousemove', onMouseMoveForPreviewPanel);
      document.removeEventListener('mouseup', onMouseUpForPreviewPanel);
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
      showPreviewPanel,
      previewPanelWidth,
      previewPanelRef,
      previewModalTitle,
      previewLoading,
      previewError,
      previewImage,
      previewStats,
      previewUnit,
      previewFile,
      previewData,
      rawContent,
      fileDescriptions,
      activePreviewTab,
      previewTabs,
      basicParameters,
      openFolderDialog,
      viewFile,
      showPreview,
      closePreview,
      isSelected,
      isPreviewingFile,
      startResizingWidth,
      startResizingPreviewWidth,
      startResize,
      formatNumber,
      formatDateTime,
      openFileForAnalysis
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

/* 可調整預覽面板寬度的把手 */
.preview-resize-handle {
  position: absolute;
  left: -4px;
  top: 0;
  bottom: 0;
  width: 7px;
  background: transparent;
  cursor: col-resize;
  z-index: 20;
}

.preview-resize-handle:hover, .preview-resize-handle:active {
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

/* 預覽面板過渡動畫 */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* 確保預覽面板中的形貌圖不會過大 */
.preview-image {
  max-height: 60vh;
  width: auto;
  object-fit: contain;
}

/* 增強重要參數區塊的視覺效果 */
.parameter-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 8px;
}

.parameter-item {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  padding: 8px;
  display: flex;
  flex-direction: column;
}

.parameter-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 2px;
}

.parameter-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
}
</style>