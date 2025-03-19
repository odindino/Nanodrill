<!-- src/components/SideBar.vue -->
<template>
  <div class="w-56 h-screen bg-neutral-800 text-white flex flex-col">
    <div class="p-5 border-b border-neutral-700 bg-neutral-900">
      <h1 class="text-xl font-bold text-white flex items-center">
        <span class="text-secondary-400 mr-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </span>
        Nanodrill
      </h1>
    </div>
    
    <nav class="flex-1 py-4">
      <ul>
        <li 
          class="flex items-center px-5 py-3 cursor-pointer transition-all duration-200 hover:bg-neutral-700"
          :class="{ 'bg-secondary-600 border-l-4 border-secondary-300 pl-4': activeItem === 'dataset' }"
          @click="handleItemClick('dataset')"
        >
          <span class="mr-3 text-secondary-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
            </svg>
          </span>
          <span class="font-medium">資料集</span>
        </li>
        
        <li 
          class="flex items-center px-5 py-3 cursor-pointer transition-all duration-200 hover:bg-neutral-700"
          :class="{ 'bg-secondary-600 border-l-4 border-secondary-300 pl-4': activeItem === 'analysis' }"
          @click="handleItemClick('analysis')"
        >
          <span class="mr-3 text-secondary-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </span>
          <span class="font-medium">分析</span>
        </li>
        
        <li 
          class="flex items-center px-5 py-3 cursor-pointer transition-all duration-200 hover:bg-neutral-700"
          :class="{ 'bg-secondary-600 border-l-4 border-secondary-300 pl-4': activeItem === 'settings' }"
          @click="handleItemClick('settings')"
        >
          <span class="mr-3 text-secondary-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </span>
          <span class="font-medium">設定</span>
        </li>
      </ul>
    </nav>
    
    <div class="px-5 py-4 text-xs text-neutral-400 border-t border-neutral-700 bg-neutral-900">
      <div class="flex items-center justify-between">
        <span>v1.0.0</span>
        <span class="text-secondary-400">SPM Data Analyzer</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'SideBar',
  emits: ['menu-item-clicked'],
  setup(props, { emit }) {
    const activeItem = ref<string | null>('dataset');
    
    const handleItemClick = (item: string) => {
      activeItem.value = item;
      emit('menu-item-clicked', item);
    };
    
    return {
      activeItem,
      handleItemClick
    };
  }
});
</script>