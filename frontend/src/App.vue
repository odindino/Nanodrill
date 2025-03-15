<template>
  <div class="app-container">
    <FolderSelector />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import FolderSelector from '@/components/FolderSelector.vue';

export default defineComponent({
  name: 'App',
  components: {
    FolderSelector
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
  background-color: #f9f9f9;
  color: #333;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 20px;
}
</style>