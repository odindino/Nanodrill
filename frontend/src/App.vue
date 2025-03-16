// App.vue
<template>
  <div class="app-container">
    <SideBar @menu-item-clicked="handleMenuItemClick" />
    
    <div class="main-content">
      <transition name="slide">
        <FileSelector 
          v-if="showFileSelector" 
          @close="hideFileSelector"
        />
      </transition>
      
      <main class="content-area">
        <!-- 主要內容區域，將根據選擇的檔案顯示資料分析視圖 -->
        <div v-if="!selectedFile" class="welcome-screen">
          <h2>歡迎使用 SPM 數據分析工具</h2>
          <p>請從左側功能欄選擇「資料集」以開始</p>
        </div>
        
        <!-- 選擇檔案後的內容 -->
        <DataView v-else />
      </main>
    </div>
    
    <footer class="app-footer">
      <p>© 2025 SPM Data Analysis Tool</p>
    </footer>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import SideBar from '@/components/SideBar.vue';
import FileSelector from '@/components/FileSelector.vue';
import DataView from '@/components/DataView.vue';
import { useSpmDataStore } from './stores/spmDataStore';

export default defineComponent({
  name: 'App',
  components: {
    SideBar,
    FileSelector,
    DataView
  },
  setup() {
    const spmDataStore = useSpmDataStore();
    const showFileSelector = ref(false);
    
    const selectedFile = computed(() => spmDataStore.selectedFile);
    
    const handleMenuItemClick = (menuItem: string) => {
      if (menuItem === 'dataset') {
        toggleFileSelector();
      }
    };
    
    const toggleFileSelector = () => {
      showFileSelector.value = !showFileSelector.value;
    };
    
    const hideFileSelector = () => {
      showFileSelector.value = false;
    };
    
    return {
      showFileSelector,
      selectedFile,
      handleMenuItemClick,
      hideFileSelector
    };
  }
});
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  background-color: #f5f5f5;
  color: #333;
  line-height: 1.6;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  display: flex;
  position: relative;
}

.content-area {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.welcome-screen {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: #666;
}

.welcome-screen h2 {
  font-size: 24px;
  margin-bottom: 16px;
}

.welcome-screen p {
  font-size: 16px;
}

.app-footer {
  background-color: #f5f5f5;
  color: #666;
  text-align: center;
  padding: 12px;
  font-size: 14px;
  border-top: 1px solid #ddd;
}

/* 側欄和文件選擇器的過渡動畫 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}
</style>