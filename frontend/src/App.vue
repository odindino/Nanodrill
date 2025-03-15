// App.vue
<template>
  <div class="app-container">
    <header class="app-header">
      <h1>SPM 數據分析器</h1>
    </header>
    
    <main class="app-main">
      <FolderBrowser />
    </main>
    
    <footer class="app-footer">
      <p>© 2025 SPM Data Analysis Tool</p>
    </footer>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import FolderBrowser from './components/FolderBrowser.vue';

export default defineComponent({
  name: 'App',
  components: {
    FolderBrowser
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

.app-header {
  background-color: #1976D2;
  color: white;
  padding: 16px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-main {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  background-color: #f5f5f5;
  color: #666;
  text-align: center;
  padding: 12px;
  font-size: 14px;
  border-top: 1px solid #ddd;
}
</style>