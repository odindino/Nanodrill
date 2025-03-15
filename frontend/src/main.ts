import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';

// 創建應用實例
const app = createApp(App);

// 掛載 Pinia 狀態管理
app.use(createPinia());

// 掛載路由
app.use(router);

// 掛載應用
app.mount('#app');

// 定義全局 pywebview API 類型
declare global {
  interface Window {
    pywebview: {
      api: {
        open_file_dialog: () => Promise<any>;
        process_selected_file: (filePath: string) => Promise<any>;
        get_txt_file_content: (filePath: string) => Promise<any>;
        load_int_file: (filePath: string, metadata: any) => Promise<any>;
      }
    }
  }
}