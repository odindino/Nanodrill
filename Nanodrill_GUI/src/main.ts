// src/main.ts
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import './styles.css';  // 確保路徑正確

// 創建 Pinia 實例
const pinia = createPinia();

// 創建 Vue 應用實例
const app = createApp(App);

// 使用 Pinia
app.use(pinia);

// 全局錯誤處理
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err);
  console.info('Vue instance:', instance);
  console.info('Error info:', info);
};

// 掛載應用到 DOM
app.mount('#app');