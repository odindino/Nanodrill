// src/components/analysis/tools/ImageViewerTools.vue
<template>
  <div class="p-4 space-y-4">
    <h4 class="font-medium text-sm border-b pb-2 mb-2">影像處理</h4>
    
    <!-- 剖面分析 -->
    <div>
      <label class="text-xs text-gray-500 block mb-1">剖面分析</label>
      <button 
        @click="createLineProfile"
        class="w-full py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
        :disabled="isProfileViewerLinked"
      >
        建立線性剖面
      </button>
      
      <!-- 如果已有關聯的 ProfileViewer，顯示提示 -->
      <div v-if="isProfileViewerLinked" class="mt-2 text-xs text-gray-500">
        此影像已創建剖面圖。請先關閉現有剖面圖後再建立新的剖面圖。
      </div>
    </div>

    <!-- 水平調整 -->
    <div>
      <label class="text-xs text-gray-500 block mb-2">水平調整</label>
      
      <!-- 平面化處理 -->
      <div class="mb-3">
        <label class="text-xs text-gray-600 block mb-1">平面化處理</label>
        <div class="space-y-1">
          <button 
            @click="applyFlatten('mean')"
            class="w-full py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
            :disabled="processingFlatten"
          >
            平均值平面化
          </button>
          <button 
            @click="applyFlatten('polyfit')"
            class="w-full py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
            :disabled="processingFlatten"
          >
            多項式平面化
          </button>
          <button 
            @click="applyFlatten('plane')"
            class="w-full py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
            :disabled="processingFlatten"
          >
            平面擬合
          </button>
        </div>
      </div>

      <!-- 傾斜調整 -->
      <div>
        <label class="text-xs text-gray-600 block mb-1">傾斜調整</label>
        <div class="grid grid-cols-2 gap-1 mb-2">
          <button 
            @click="tiltImage('up')"
            class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
            :disabled="processingTilt"
          >
            ↑ 上
          </button>
          <button 
            @click="tiltImage('down')"
            class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
            :disabled="processingTilt"
          >
            ↓ 下
          </button>
          <button 
            @click="tiltImage('left')"
            class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
            :disabled="processingTilt"
          >
            ← 左
          </button>
          <button 
            @click="tiltImage('right')"
            class="py-1.5 px-2 text-xs font-medium rounded border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-primary"
            :disabled="processingTilt"
          >
            → 右
          </button>
        </div>
        
        <!-- 微調模式開關 -->
        <div class="flex items-center space-x-2">
          <input 
            type="checkbox" 
            id="fine-tune-mode" 
            v-model="fineTuneMode"
            class="w-3 h-3 text-primary border-gray-300 rounded focus:ring-primary focus:ring-1"
          >
          <label for="fine-tune-mode" class="text-xs text-gray-600">微調模式</label>
        </div>
      </div>

      <!-- 處理狀態提示 -->
      <div v-if="processingFlatten || processingTilt" class="text-xs text-gray-500 flex items-center">
        <div class="animate-spin rounded-full h-3 w-3 border-b-2 border-primary mr-2"></div>
        處理中...
      </div>
    </div>
    
    <!-- 顯示設定 -->
    <div>
      <label class="text-xs text-gray-500 block mb-2">顯示設定</label>
      
      <!-- Colormap 選擇 -->
      <div class="mb-3">
        <label class="text-xs text-gray-600 block mb-1">色彩映射</label>
        <select 
          :value="currentColormap"
          @change="changeColormap(($event.target as HTMLSelectElement)?.value)"
          class="w-full py-1.5 px-2 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option value="Viridis">綠藍色 (Viridis)</option>
          <option value="Plasma">等離子 (Plasma)</option>
          <option value="Inferno">地獄 (Inferno)</option>
          <option value="Magma">岩漿 (Magma)</option>
          <option value="Cividis">色盲友好 (Cividis)</option>
          <option value="Hot">熱力圖 (Hot)</option>
          <option value="Jet">彩虹 (Jet)</option>
          <option value="Rainbow">彩虹2 (Rainbow)</option>
          <option value="Blackbody">黑體 (Blackbody)</option>
          <option value="Earth">地球 (Earth)</option>
          <option value="Electric">電子 (Electric)</option>
          <option value="YlOrRd">黃橘紅 (YlOrRd)</option>
          <option value="YlGnBu">黃綠藍 (YlGnBu)</option>
          <option value="RdYlBu">紅黃藍 (RdYlBu)</option>
          <option value="Portland">波特蘭 (Portland)</option>
          <option value="Picnic">野餐 (Picnic)</option>
          <option value="Blues">藍色 (Blues)</option>
          <option value="Oranges">橘色 (Oranges)</option>
        </select>
      </div>

      <!-- Colorbar 控制 -->
      <div>
        <label class="text-xs text-gray-600 block mb-1">色彩條控制</label>
        <div class="space-y-1">
          <div class="flex items-center space-x-2">
            <input 
              type="checkbox" 
              id="reverse-colormap" 
              v-model="reverseColormap"
              @change="toggleReverseColormap"
              class="w-3 h-3 text-primary border-gray-300 rounded focus:ring-primary focus:ring-1"
            >
            <label for="reverse-colormap" class="text-xs text-gray-600">反轉顏色</label>
          </div>
          <div class="flex items-center space-x-2">
            <input 
              type="checkbox" 
              id="auto-scale" 
              v-model="autoScale"
              @change="toggleAutoScale"
              class="w-3 h-3 text-primary border-gray-300 rounded focus:ring-primary focus:ring-1"
            >
            <label for="auto-scale" class="text-xs text-gray-600">自動縮放</label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue';
import type { PropType } from 'vue';
import { useSpmDataStore } from '../../../stores/spmDataStore';
import { useAnalysisStore } from '../../../stores/analysisStore';
import { AnalysisService } from '../../../services/analysisService';
import type { Viewer } from '../../../stores/spmDataStore';

export default defineComponent({
  name: 'ImageViewerTools',
  props: {
    viewer: {
      type: Object as PropType<Viewer>,
      required: true
    }
  },
  setup(props) {
    const spmDataStore = useSpmDataStore();
    const analysisStore = useAnalysisStore();
    
    // 水平調整相關狀態
    const processingFlatten = ref(false);
    const processingTilt = ref(false);
    const fineTuneMode = ref(false);
    
    // 顏色映射相關狀態
    const currentColormap = ref('Oranges');  // 改為預設 Oranges
    const reverseColormap = ref(false);
    const autoScale = ref(true);
    
    // 計算屬性：檢查是否有已連接的 ProfileViewer
    const isProfileViewerLinked = computed(() => {
      // 獲取最新的 viewer 狀態
      const location = spmDataStore.getViewerLocation(props.viewer.id);
      if (!location) return false;
      
      const { tabId, groupId, viewerIndex } = location;
      const tab = spmDataStore.analysisTabs.find(t => t.id === tabId);
      if (!tab || !tab.viewerGroups) return false;
      
      const group = tab.viewerGroups.find(g => g.id === groupId);
      if (!group) return false;
      
      const currentViewer = group.viewers[viewerIndex];
      
      // 檢查是否有連接的 ProfileViewer 且該 ProfileViewer 是否仍然存在
      if (!currentViewer.props.linkedProfileViewerId) return false;
      
      // 檢查連接的 ProfileViewer 是否仍然存在
      let profileViewerExists = false;
      for (const g of tab.viewerGroups) {
        for (const v of g.viewers) {
          if (v.id === currentViewer.props.linkedProfileViewerId) {
            profileViewerExists = true;
            break;
          }
        }
        if (profileViewerExists) break;
      }
      
      return profileViewerExists;
    });
    
    // 獲取當前影像數據
    const getCurrentImageData = () => {
      // 從 viewer props 中獲取影像數據
      if (props.viewer.props && props.viewer.props.imageRawData) {
        return props.viewer.props.imageRawData;
      }
      return null;
    };
    
    // 更新影像數據
    const updateImageData = (newData: number[][], stats?: any) => {
      // 找到當前 viewer 的位置並更新影像數據
      const location = spmDataStore.getViewerLocation(props.viewer.id);
      if (!location) return;
      
      const { tabId, groupId, viewerIndex } = location;
      const updateData: any = { imageRawData: newData };
      
      // 如果有統計數據，一併更新
      if (stats) {
        updateData.stats = stats;
      }
      
      spmDataStore.updateViewerProps(tabId, groupId, viewerIndex, updateData);
      
      console.log('更新後的影像數據:', updateData);
    };
    
    // 創建線性剖面
    const createLineProfile = () => {
      // 檢查是否可以創建線性剖面
      if (isProfileViewerLinked.value) {
        console.log("此 ImageViewer 已綁定 ProfileViewer，無法創建新的剖面圖");
        return;
      }
      
      // 使用 analysisStore 中的方法創建線性剖面
      analysisStore.createLineProfile(props.viewer.id);
    };
    
    // 應用平面化處理
    const applyFlatten = async (method: 'mean' | 'polyfit' | 'plane') => {
      const imageData = getCurrentImageData();
      if (!imageData) {
        console.error('無法獲取影像數據');
        return;
      }
      
      processingFlatten.value = true;
      
      try {
        const result = await AnalysisService.applyFlatten(imageData, method);
        if (result && result.success && result.processed_data) {
          // 更新圖像數據和統計資訊
          updateImageData(result.processed_data, result.statistics);
          console.log(`${method} 平面化處理完成`, result);
        } else {
          console.error('平面化處理返回錯誤:', result);
        }
      } catch (error) {
        console.error('平面化處理失敗:', error);
      } finally {
        processingFlatten.value = false;
      }
    };
    
    // 應用傾斜調整
    const tiltImage = async (direction: 'up' | 'down' | 'left' | 'right') => {
      const imageData = getCurrentImageData();
      if (!imageData) {
        console.error('無法獲取影像數據');
        return;
      }
      
      processingTilt.value = true;
      
      try {
        const result = await AnalysisService.tiltImage(imageData, direction, fineTuneMode.value);
        if (result && result.success && result.processed_data) {
          // 更新圖像數據和統計資訊
          updateImageData(result.processed_data, result.statistics);
          console.log(`${direction} 方向傾斜調整完成`, result);
        } else {
          console.error('傾斜調整返回錯誤:', result);
        }
      } catch (error) {
        console.error('傾斜調整失敗:', error);
      } finally {
        processingTilt.value = false;
      }
    };
    
    // 顏色映射相關功能
    
    // 更改色彩映射
    const changeColormap = (newColormap: string) => {
      if (!newColormap) return;
      
      // 儲存基礎 colormap 名稱（不含 _r）
      currentColormap.value = newColormap;
      
      // 根據當前反轉狀態構建最終的 colormap 名稱
      const finalColormap = reverseColormap.value ? `${newColormap}_r` : newColormap;
      
      // 更新 viewer 的 colormap 屬性
      updateViewerProps({
        colormap: finalColormap
      });
      
      console.log('色彩映射已更新:', '基礎映射:', newColormap, '反轉狀態:', reverseColormap.value, '最終映射:', finalColormap);
    };
    
    // 切換反轉色彩映射
    const toggleReverseColormap = () => {
      // 根據反轉狀態構建最終的 colormap 名稱
      const finalColormap = reverseColormap.value ? `${currentColormap.value}_r` : currentColormap.value;
      
      updateViewerProps({
        colormap: finalColormap
      });
      
      console.log('色彩映射反轉狀態已更新:', reverseColormap.value, '基礎映射:', currentColormap.value, '最終映射:', finalColormap);
    };
    
    // 切換自動縮放
    const toggleAutoScale = () => {
      updateViewerProps({
        autoScale: autoScale.value
      });
      
      console.log('自動縮放已更新為:', autoScale.value);
    };
    
    // 通用的更新 viewer 屬性方法
    const updateViewerProps = (newProps: Partial<any>) => {
      const location = spmDataStore.getViewerLocation(props.viewer.id);
      if (!location) {
        console.error('無法找到 viewer 位置');
        return;
      }
      
      const { tabId, groupId, viewerIndex } = location;
      
      // 更新 viewer 屬性
      spmDataStore.updateViewerProps(tabId, groupId, viewerIndex, newProps);
    };

    // 初始化 colormap 狀態
    onMounted(() => {
      // 從 viewer 的當前 props 獲取初始 colormap 值
      if (props.viewer.props.colormap) {
        const currentColormapValue = props.viewer.props.colormap;
        // 檢查是否有 _r 後綴
        if (currentColormapValue.endsWith('_r')) {
          currentColormap.value = currentColormapValue.slice(0, -2);
          reverseColormap.value = true;
        } else {
          currentColormap.value = currentColormapValue;
          reverseColormap.value = false;
        }
      } else {
        // 設定初始的 colormap
        updateViewerProps({
          colormap: currentColormap.value
        });
      }
      
      console.log('ImageViewerTools 初始化完成', {
        基礎映射: currentColormap.value,
        反轉狀態: reverseColormap.value,
        當前映射: props.viewer.props.colormap
      });
    });
    
    return {
      isProfileViewerLinked,
      processingFlatten,
      processingTilt,
      fineTuneMode,
      currentColormap,
      reverseColormap,
      autoScale,
      createLineProfile,
      applyFlatten,
      tiltImage,
      changeColormap,
      toggleReverseColormap,
      toggleAutoScale
    };
  }
});
</script>