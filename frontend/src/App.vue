<template>
  <div class="app-container">
    <header class="app-header">
      <h1>Nanodrill - SPM 數據分析工具</h1>
    </header>
    
    <main class="app-main">
      <router-view />
    </main>
    
    <footer class="app-footer">
      <div class="status-bar">
        <span>{{ statusMessage }}</span>
      </div>
    </footer>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';
import { useFileStore } from './stores/fileStore';

export default defineComponent({
  name: 'App',
  
  setup() {
    const fileStore = useFileStore();
    const statusMessage = computed(() => fileStore.statusMessage);

    return {
      statusMessage
    };
  }
});
</script>

<style>
:root {
  --primary-color: #2c3e50;
  --secondary-color: #4CAF50;
  --accent-color: #3498db;
  --background-color: #f5f5f5;
  --card-background: #ffffff;
  --border-color: #ddd;
  --text-color: #333;
  --text-light: #666;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
  line-height: 1.6;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.app-header {
  background-color: var(--primary-color);
  color: white;
  padding: 0.8rem 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 500;
}

.app-main {
  flex: 1;
  overflow: hidden;
  display: flex;
}

.app-footer {
  background-color: #f8f9fa;
  border-top: 1px solid var(--border-color);
  padding: 0.5rem 1.5rem;
  font-size: 0.875rem;
}

button {
  cursor: pointer;
  padding: 0.5rem 1rem;
  background-color: var(--secondary-color);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #45a049;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

select {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: white;
  font-size: 0.9rem;
}

.card {
  background-color: var(--card-background);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  margin-bottom: 1rem;
}
</style>