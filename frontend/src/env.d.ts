/// <reference types="vite/client" />

// Vue 組件聲明
declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

// 全局 PyWebView API 聲明
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