<template>
    <div class="parameter-display">
      <div class="parameter-sections">
        <!-- 基本參數卡片 -->
        <div class="parameter-card">
          <h3>基本資訊</h3>
          <table>
            <tbody>
              <tr v-if="metadata.Version">
                <th>版本</th>
                <td>{{ metadata.Version }}</td>
              </tr>
              <tr v-if="metadata.Date">
                <th>日期</th>
                <td>{{ metadata.Date }}</td>
              </tr>
              <tr v-if="metadata.Time">
                <th>時間</th>
                <td>{{ metadata.Time }}</td>
              </tr>
              <tr v-if="metadata.UserName">
                <th>使用者</th>
                <td>{{ metadata.UserName }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- 掃描參數卡片 -->
        <div class="parameter-card">
          <h3>掃描參數</h3>
          <table>
            <tbody>
              <tr v-if="metadata.XScanRange && metadata.YScanRange">
                <th>掃描範圍</th>
                <td>{{ metadata.XScanRange }} × {{ metadata.YScanRange }} {{ metadata.XPhysUnit }}</td>
              </tr>
              <tr v-if="metadata.xPixel && metadata.yPixel">
                <th>解析度</th>
                <td>{{ metadata.xPixel }} × {{ metadata.yPixel }} 像素</td>
              </tr>
              <tr v-if="metadata.LineRate">
                <th>掃描速率</th>
                <td>{{ metadata.LineRate }} {{ metadata.LineRate ? 'lines/sec' : '' }}</td>
              </tr>
              <tr v-if="metadata.Angle">
                <th>角度</th>
                <td>{{ metadata.Angle }}°</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- 回饋參數卡片 -->
        <div class="parameter-card">
          <h3>回饋參數</h3>
          <table>
            <tbody>
              <tr v-if="metadata.FeedBackModus">
                <th>回饋模式</th>
                <td>{{ metadata.FeedBackModus }}</td>
              </tr>
              <tr v-if="metadata.SetPoint">
                <th>設定點</th>
                <td>{{ metadata.SetPoint }} {{ metadata.SetPointPhysUnit }}</td>
              </tr>
              <tr v-if="metadata.Bias">
                <th>偏壓</th>
                <td>{{ metadata.Bias }} {{ metadata.BiasPhysUnit }}</td>
              </tr>
              <tr v-if="metadata.Ki || metadata.Kp">
                <th>PID 參數</th>
                <td>Ki: {{ metadata.Ki || 'N/A' }}, Kp: {{ metadata.Kp || 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- 檔案描述列表 -->
      <div class="file-descriptions">
        <h3>關聯檔案</h3>
        <div class="description-list">
          <div 
            v-for="(file, index) in fileDescriptions" 
            :key="index"
            class="description-item"
          >
            <div class="description-name">{{ file.FileName }}</div>
            <div class="description-details">
              <span class="description-caption">{{ file.Caption }}</span>
              <span class="description-scale">比例: {{ parseFloat(file.Scale).toExponential(2) }}</span>
              <span class="description-unit">單位: {{ file.PhysUnit }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, computed, PropType } from 'vue';
  import type { MetadataInfo, FileDescription } from '../types';
  
  export default defineComponent({
    name: 'ParameterDisplay',
    
    props: {
      metadata: {
        type: Object as PropType<MetadataInfo>,
        required: true
      }
    },
    
    setup(props) {
      // 取得檔案描述列表
      const fileDescriptions = computed(() => {
        return props.metadata.fileDescriptions || [];
      });
      
      return {
        fileDescriptions
      };
    }
  });
  </script>
  
  <style scoped>
  .parameter-display {
    padding: 1rem;
  }
  
  .parameter-sections {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  
  .parameter-card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    padding: 1rem;
  }
  
  .parameter-card h3 {
    font-size: 1.1rem;
    color: var(--primary-color);
    margin-top: 0;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
  
  th {
    text-align: left;
    font-weight: 500;
    color: var(--text-light);
    padding: 0.4rem 0;
    vertical-align: top;
    width: 40%;
  }
  
  td {
    text-align: right;
    padding: 0.4rem 0;
  }
  
  .file-descriptions {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    padding: 1rem;
    margin-top: 1rem;
  }
  
  .file-descriptions h3 {
    font-size: 1.1rem;
    color: var(--primary-color);
    margin-top: 0;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
  }
  
  .description-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 0.75rem;
  }
  
  .description-item {
    padding: 0.75rem;
    background-color: #f8f9fa;
    border-radius: 6px;
    border-left: 3px solid var(--accent-color);
  }
  
  .description-name {
    font-weight: 500;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: var(--primary-color);
  }
  
  .description-details {
    display: flex;
    flex-direction: column;
    font-size: 0.8rem;
    color: var(--text-light);
  }
  
  .description-details span {
    margin-bottom: 0.25rem;
  }
  </style>