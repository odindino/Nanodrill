<!-- App.vue -->
<template>
  <TestComponent />
  <div class="flex flex-col min-h-screen bg-gray-50">
    <div class="flex flex-1">
      <SideBar @menu-item-clicked="handleMenuItemClick" />
      
      <div class="relative flex flex-1 overflow-hidden">
        <transition name="slide">
          <FileSelector 
            v-if="showFileSelector" 
            @close="hideFileSelector"
            class="relative z-10 h-[calc(100vh-40px)]"
          />
        </transition>
        
        <main class="flex-1 p-5 overflow-y-auto transition-all" :class="{ 'pl-5': showFileSelector }">
          <div v-if="!selectedFile" class="flex flex-col items-center justify-center h-full text-center text-gray-600">
            <h2 class="mb-4 text-2xl font-semibold">歡迎使用 SPM 數據分析工具</h2>
            <p class="text-base">請從左側功能欄選擇「資料集」以開始</p>
          </div>
          
          <DataView v-else />
        </main>
      </div>
    </div>
    
    <footer class="py-3 text-center text-sm text-gray-600 border-t border-gray-200 h-10">
      © 2025 SPM Data Analysis Tool
    </footer>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import SideBar from '@/components/SideBar.vue';
import FileSelector from '@/components/FileSelector.vue';
import DataView from '@/components/DataView.vue';
import { useSpmDataStore } from './stores/spmDataStore';
import TestComponent from './components/TestComponent.vue';


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

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}
</style>