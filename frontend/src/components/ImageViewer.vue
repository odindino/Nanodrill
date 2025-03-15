<template>
  <div class="image-viewer">
    <div class="image-container" ref="imageContainer">
      <img 
        v-if="imageData" 
        :src="`data:image/png;base64,${imageData}`" 
        @load="imageLoaded"
        class="spm-image"
        alt="SPM 掃描圖像"
      />
    </div>
    
    <div class="image-controls">
      <div class="control-group">
        <button @click="resetZoom" :disabled="zoom === 1">重設縮放</button>
        <button @click="zoomIn">放大</button>
        <button @click="zoomOut" :disabled="zoom <= 0.5">縮小</button>
      </div>
      
      <div class="control-group">
        <button @click="toggleLineProfileMode" :class="{ active: lineProfileMode }">
          高度剖面
        </button>
        <button @click="toggleColormap" :disabled="!imageData">切換色彩</button>
      </div>
    </div>
    
    <!-- 線剖面顯示區域 -->
    <div v-if="showLineProfile" class="line-profile-container">
      <canvas ref="profileCanvas" class="profile-canvas"></canvas>
      <div class="profile-info">
        <div>起點: ({{ startPoint.x.toFixed(2) }}, {{ startPoint.y.toFixed(2) }})</div>
        <div>終點: ({{ endPoint.x.toFixed(2) }}, {{ endPoint.y.toFixed(2) }})</div>
        <div>長度: {{ lineLength.toFixed(2) }} {{ metadata?.XPhysUnit || 'nm' }}</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch, PropType } from 'vue';
import type { MetadataInfo } from '../types';

interface Point {
  x: number;
  y: number;
}

export default defineComponent({
  name: 'ImageViewer',
  
  props: {
    imageData: {
      type: String,
      required: true
    },
    metadata: {
      type: Object as PropType<MetadataInfo>,
      default: null
    }
  },
  
  setup(props) {
    const imageContainer = ref<HTMLDivElement | null>(null);
    const profileCanvas = ref<HTMLCanvasElement | null>(null);
    
    // 圖像狀態
    const zoom = ref(1);
    const isImageLoaded = ref(false);
    
    // 線剖面相關
    const lineProfileMode = ref(false);
    const showLineProfile = ref(false);
    const startPoint = ref<Point>({ x: 0, y: 0 });
    const endPoint = ref<Point>({ x: 0, y: 0 });
    const lineLength = ref(0);
    const isDrawingLine = ref(false);
    
    // 色彩映射
    const currentColormap = ref('viridis'); // 預設色彩映射
    
    // 監聽圖像數據變化
    watch(() => props.imageData, () => {
      isImageLoaded.value = false;
      resetZoom();
      showLineProfile.value = false;
      lineProfileMode.value = false;
    });
    
    // 圖像載入完成
    const imageLoaded = () => {
      isImageLoaded.value = true;
    };
    
    // 縮放控制
    const zoomIn = () => {
      zoom.value = Math.min(zoom.value + 0.25, 3);
    };
    
    const zoomOut = () => {
      zoom.value = Math.max(zoom.value - 0.25, 0.5);
    };
    
    const resetZoom = () => {
      zoom.value = 1;
    };
    
    // 切換色彩映射
    const toggleColormap = () => {
      // 簡單的色彩映射切換，實際應用中可以有更多選項
      const colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis'];
      const currentIndex = colormaps.indexOf(currentColormap.value);
      const nextIndex = (currentIndex + 1) % colormaps.length;
      currentColormap.value = colormaps[nextIndex];
      
      // 這裡僅改變變數，實際上需要向後端發送請求重新繪製圖像
      // 因為目前後端直接傳來 base64 圖像，前端無法直接修改色彩映射
      // 在完整實現中，應該向後端發送重新渲染請求
    };
    
    // 線剖面模式
    const toggleLineProfileMode = () => {
      lineProfileMode.value = !lineProfileMode.value;
      
      if (!lineProfileMode.value) {
        showLineProfile.value = false;
      }
    };
    
    // 初始化線剖面相關事件處理
    onMounted(() => {
      if (!imageContainer.value) return;
      
      const container = imageContainer.value;
      
      // 滑鼠按下事件
      container.addEventListener('mousedown', (e) => {
        if (!lineProfileMode.value) return;
        
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // 開始繪製線段
        isDrawingLine.value = true;
        startPoint.value = { x, y };
        endPoint.value = { x, y };
        showLineProfile.value = false;
      });
      
      // 滑鼠移動事件
      container.addEventListener('mousemove', (e) => {
        if (!isDrawingLine.value) return;
        
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // 更新終點
        endPoint.value = { x, y };
        
        // 計算線段長度
        const dx = endPoint.value.x - startPoint.value.x;
        const dy = endPoint.value.y - startPoint.value.y;
        
        // 計算長度（像素）
        const pixelLength = Math.sqrt(dx * dx + dy * dy);
        
        // 轉換為實際物理長度
        if (props.metadata) {
          const xScanRange = parseFloat(props.metadata.XScanRange || '0');
          const yPixel = parseInt(props.metadata.xPixel || '0', 10);
          
          if (xScanRange && yPixel) {
            const pixelToUnit = xScanRange / yPixel;
            lineLength.value = pixelLength * pixelToUnit;
          } else {
            lineLength.value = pixelLength;
          }
        } else {
          lineLength.value = pixelLength;
        }
      });
      
      // 滑鼠放開事件
      container.addEventListener('mouseup', () => {
        if (!isDrawingLine.value) return;
        
        isDrawingLine.value = false;
        
        // 完成線段繪製，顯示剖面
        if (lineLength.value > 5) { // 避免太短的線段
          showLineProfile.value = true;
          
          // 在實際實現中，這裡應該向後端請求剖面數據
          // 然後繪製到 profileCanvas 上
          drawDummyProfile();
        }
      });
      
      // 滑鼠離開事件
      container.addEventListener('mouseleave', () => {
        if (isDrawingLine.value) {
          isDrawingLine.value = false;
          showLineProfile.value = false;
        }
      });
    });
    
    // 繪製簡單的虛擬剖面（示例用）
    const drawDummyProfile = () => {
      if (!profileCanvas.value) return;
      
      const canvas = profileCanvas.value;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      
      // 設置 canvas 尺寸
      canvas.width = 400;
      canvas.height = 200;
      
      // 清空畫布
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // 繪製軸
      ctx.beginPath();
      ctx.strokeStyle = '#aaa';
      ctx.moveTo(30, 20);
      ctx.lineTo(30, 180);
      ctx.lineTo(380, 180);
      ctx.stroke();
      
      // 繪製標籤
      ctx.font = '12px Arial';
      ctx.fillStyle = '#333';
      ctx.fillText('高度 (nm)', 10, 100);
      ctx.fillText('距離 (nm)', 200, 195);
      
      // 繪製虛擬數據
      ctx.beginPath();
      ctx.strokeStyle = '#2ea043';
      ctx.lineWidth = 2;
      
      const steps = 100;
      const dx = 350 / steps;
      
      ctx.moveTo(30, 100); // 起始點
      
      // 生成隨機起伏的剖面線
      for (let i = 0; i <= steps; i++) {
        const x = 30 + i * dx;
        const noise = Math.sin(i * 0.1) * 20 + Math.sin(i * 0.05) * 30 + Math.random() * 5;
        const y = 100 - noise;
        ctx.lineTo(x, y);
      }
      
      ctx.stroke();
    };
    
    return {
      imageContainer,
      profileCanvas,
      zoom,
      isImageLoaded,
      lineProfileMode,
      showLineProfile,
      startPoint,
      endPoint,
      lineLength,
      currentColormap,
      imageLoaded,
      zoomIn,
      zoomOut,
      resetZoom,
      toggleColormap,
      toggleLineProfileMode
    };
  }
});
</script>

<style scoped>
.image-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.image-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  background-color: #f8f9fa;
  position: relative;
}

.spm-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transform-origin: center;
  transition: transform 0.2s ease;
}

.image-controls {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #f8f9fa;
  border-top: 1px solid #eaeaea;
}

.control-group {
  display: flex;
  gap: 8px;
}

.control-group button {
  padding: 6px 12px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  color: #333;
  transition: all 0.2s;
}

.control-group button:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.control-group button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-group button.active {
  background-color: #2ea043;
  color: white;
  border-color: #2ea043;
}

.line-profile-container {
  padding: 15px;
  background-color: white;
  border-top: 1px solid #eaeaea;
}

.profile-canvas {
  width: 100%;
  height: 200px;
  background-color: #fafafa;
  border: 1px solid #eaeaea;
  border-radius: 4px;
}

.profile-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 0.9rem;
  color: #666;
}
</style>