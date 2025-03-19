<!-- src/components/SideBar.vue -->
<template>
    <div class="w-56 h-screen bg-primary text-white flex flex-col">
      <div class="p-5 border-b border-primary-dark">
        <h1 class="text-xl font-bold">SPM Analyzer</h1>
      </div>
      
      <nav class="flex-1 py-4">
        <ul>
          <li 
            class="flex items-center px-5 py-3 cursor-pointer transition-colors duration-150 hover:bg-primary-dark"
            :class="{ 'bg-primary-dark border-l-4 border-white': activeItem === 'dataset' }"
            @click="handleItemClick('dataset')"
          >
            <span class="mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
              </svg>
            </span>
            <span>資料集</span>
          </li>
          
          <li 
            class="flex items-center px-5 py-3 cursor-pointer transition-colors duration-150 hover:bg-primary-dark"
            :class="{ 'bg-primary-dark border-l-4 border-white': activeItem === 'analysis' }"
            @click="handleItemClick('analysis')"
          >
            <span class="mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </span>
            <span>分析</span>
          </li>
          
          <li 
            class="flex items-center px-5 py-3 cursor-pointer transition-colors duration-150 hover:bg-primary-dark"
            :class="{ 'bg-primary-dark border-l-4 border-white': activeItem === 'settings' }"
            @click="handleItemClick('settings')"
          >
            <span class="mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </span>
            <span>設定</span>
          </li>
        </ul>
      </nav>
      
      <div class="px-5 py-3 text-xs text-primary-100 border-t border-primary-dark">
        <div>v1.0.0</div>
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

