<template>
  <div class="user-ai-apps-container">
    <div class="apps-content">
      <!-- 应用网格 - 2列4行布局 -->
      <div class="apps-grid">
        <!-- 文库问答卡片 -->
        <div 
          v-for="n in 4" 
          :key="'qa-' + n"
          class="app-card"
          @click="openQAApp"
        >
          <div class="app-icon">
            <el-icon class="icon-qa">
              <ChatDotRound />
            </el-icon>
          </div>
          
          <div class="app-info">
            <h3 class="app-name">文库问答</h3>
            <p class="app-description">知识图谱和大模型有哪些结合方式？</p>
          </div>
        </div>
        
        <!-- 文献综述卡片 -->
        <div 
          v-for="n in 4" 
          :key="'review-' + n"
          class="app-card"
          @click="openReviewApp"
        >
          <div class="app-icon">
            <el-icon class="icon-review">
              <Document />
            </el-icon>
          </div>
          
          <div class="app-info">
            <h3 class="app-name">文献综述</h3>
            <p class="app-description">根据提供的主题和需求，检索并生成文献综述</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { ChatDotRound, Document } from '@element-plus/icons-vue'

// 方法
const openQAApp = () => {
  ElMessage.info('文库问答功能开发中，敬请期待...')
}

const openReviewApp = () => {
  ElMessage.info('文献综述功能开发中，敬请期待...')
}
</script>

<style lang="scss" scoped>
.user-ai-apps-container {
  min-height: calc(100vh - 64px);
  background: #f8fafc;
  padding: 24px;
}

.apps-content {
  max-width: 1000px;
  margin: 0 auto;
}

.apps-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin: 0;
}

.app-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  min-height: 80px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    border-color: #d0d7de;
  }
  
  .app-icon {
    margin-right: 16px;
    flex-shrink: 0;
    
    .icon-qa {
      font-size: 24px;
      color: #4f94cd;
      background: #e8f4fd;
      padding: 8px;
      border-radius: 6px;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .icon-review {
      font-size: 24px;
      color: #4f94cd;
      background: #e8f4fd;
      padding: 8px;
      border-radius: 6px;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
  
  .app-info {
    flex: 1;
    
    .app-name {
      font-size: 16px;
      font-weight: 600;
      color: #2c3e50;
      margin: 0 0 4px 0;
      line-height: 1.4;
    }
    
    .app-description {
      color: #6b7280;
      line-height: 1.4;
      margin: 0;
      font-size: 14px;
    }
  }
}

@media (max-width: 768px) {
  .user-ai-apps-container {
    padding: 16px;
  }
  
  .apps-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .app-card {
    padding: 16px 20px;
    min-height: 70px;
    
    .app-icon {
      margin-right: 12px;
      
      .icon-qa,
      .icon-review {
        width: 36px;
        height: 36px;
        font-size: 20px;
      }
    }
    
    .app-info {
      .app-name {
        font-size: 15px;
      }
      
      .app-description {
        font-size: 13px;
      }
    }
  }
}
</style>