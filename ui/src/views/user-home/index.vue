<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="welcome-content">
        <h1 class="hero-title">中国教育科学研究院AI知识库</h1>
        
        <div class="action-container">
          <el-button 
            class="journey-btn"
            @click="goToKnowledge"
          >
            开启智慧之旅
            <el-icon class="arrow-icon">
              <ArrowRight />
            </el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()

const goToKnowledge = () => {
  router.push('/user-knowledge')
}
</script>

<style lang="scss" scoped>
.home-container {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #cde5ff 0%, #ddeeff 20%, #e8f3ff 40%, #f2f8ff 60%, #f8fcff 80%, #feffff 100%);
  position: relative;
  overflow: hidden;
  
  // 第一层波浪
  &::before {
    content: '';
    position: absolute;
    bottom: 0;
    left: -10%;
    width: 120%;
    height: 200px;
    background: linear-gradient(45deg, rgba(104, 163, 240, 0.4) 0%, rgba(136, 184, 247, 0.3) 100%);
    border-radius: 100% 100% 0 0;
    pointer-events: none;
  }
  
  // 第二层波浪
  &::after {
    content: '';
    position: absolute;
    bottom: 50px;
    left: -5%;
    width: 110%;
    height: 150px;
    background: linear-gradient(60deg, rgba(90, 154, 237, 0.25) 0%, rgba(122, 178, 243, 0.2) 100%);
    border-radius: 120% 120% 0 0;
    pointer-events: none;
  }
  
  .hero-section {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 64px);
    padding: 40px 20px;
    text-align: center;
    position: relative;
    z-index: 1;
    
    .welcome-content {
      max-width: 900px;
      margin: 0 auto;
      
                  .hero-title {
                    font-size: 52px;
                    font-weight: 700;
                    color: #2c5aa0;
                    margin-bottom: 80px;
                    line-height: 1.2;
                    text-shadow: 0 2px 8px rgba(44, 90, 160, 0.15);
                    letter-spacing: 2px;
                  }
      
      .action-container {
        .journey-btn {
          background: rgba(255, 255, 255, 0.9);
          border: 1px solid rgba(255, 255, 255, 0.3);
          color: #2b77d9;
          font-size: 18px;
          font-weight: 600;
          padding: 16px 40px;
          border-radius: 50px;
          box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            0 0 0 1px rgba(255, 255, 255, 0.2) inset;
          backdrop-filter: blur(10px);
          transition: all 0.3s ease;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          
          &:hover {
            background: rgba(255, 255, 255, 0.95);
            transform: translateY(-2px);
            box-shadow: 
              0 12px 40px rgba(0, 0, 0, 0.15),
              0 0 0 1px rgba(255, 255, 255, 0.4) inset;
            color: #1a5fa0;
          }
          
          .arrow-icon {
            font-size: 16px;
            transition: transform 0.3s ease;
          }
          
          &:hover .arrow-icon {
            transform: translateX(4px);
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .home-container {
    .hero-section {
      padding: 40px 20px;
      
      .welcome-content {
        .hero-title {
          font-size: 36px;
          margin-bottom: 60px;
          letter-spacing: 1px;
        }
        
        .action-container {
          .journey-btn {
            font-size: 16px;
            padding: 14px 32px;
          }
        }
      }
    }
  }
}

@media (max-width: 480px) {
  .home-container {
    .hero-section {
      .welcome-content {
        .hero-title {
          font-size: 28px;
          margin-bottom: 50px;
        }
        
        .action-container {
          .journey-btn {
            font-size: 16px;
            padding: 12px 28px;
          }
        }
      }
    }
  }
}

</style>
