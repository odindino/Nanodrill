import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';

// 創建 Pinia 實例
const pinia = createPinia();

// 創建 Vue 應用實例
const app = createApp(App);

// 使用 Pinia
app.use(pinia);

// 掛載應用到 DOM
app.mount('#app');