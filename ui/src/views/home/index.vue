<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="welcome-content">
        <h1 class="hero-title">{{ $t('views.home.welcome') }}</h1>
        <p class="hero-subtitle">{{ $t('views.home.description') }}</p>
        
        <!-- 搜索框 -->
        <div class="search-container">
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              :placeholder="$t('views.home.searchPlaceholder')"
              class="search-input"
              size="large"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon class="search-icon">
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-button 
              type="primary" 
              size="large" 
              class="search-button"
              @click="handleSearch"
            >
              {{ $t('views.home.search') }}
            </el-button>
          </div>
          
          <!-- 搜索建议 -->
          <div class="search-suggestions">
            <span class="suggestion-label">{{ $t('views.home.hotSearches') }}：</span>
            <el-tag 
              v-for="tag in hotSearches" 
              :key="tag"
              class="suggestion-tag"
              @click="searchQuery = tag; handleSearch()"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>
    
    <div class="stats-section">
      <div class="container">
        <h2 class="section-title">{{ $t('views.home.overview') }}</h2>
      <el-row :gutter="24">
        <el-col :xs="24" :sm="12" :md="6" :lg="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ applicationCount }}</div>
              <div class="stats-label">{{ $t('views.home.applicationCount') }}</div>
            </div>
            <el-icon class="stats-icon">
              <Operation />
            </el-icon>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6" :lg="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ datasetCount }}</div>
              <div class="stats-label">{{ $t('views.home.datasetCount') }}</div>
            </div>
            <el-icon class="stats-icon">
              <Collection />
            </el-icon>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6" :lg="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ chatCount }}</div>
              <div class="stats-label">{{ $t('views.home.chatCount') }}</div>
            </div>
            <el-icon class="stats-icon">
              <ChatDotRound />
            </el-icon>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6" :lg="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ documentCount }}</div>
              <div class="stats-label">{{ $t('views.home.documentCount') }}</div>
            </div>
            <el-icon class="stats-icon">
              <Document />
            </el-icon>
          </el-card>
        </el-col>
      </el-row>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { t } from '@/locales'
import { ElCard, ElRow, ElCol, ElInput, ElButton, ElTag, ElIcon } from 'element-plus'
import { Search, Operation, Collection, ChatDotRound, Document } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { MsgSuccess } from '@/utils/message'

const router = useRouter()

// 搜索相关
const searchQuery = ref('')
const hotSearches = ref([
  '人工智能',
  '机器学习', 
  '深度学习',
  '自然语言处理',
  '知识图谱'
])

// 统计数据
const applicationCount = ref(0)
const datasetCount = ref(0)
const chatCount = ref(0)
const documentCount = ref(0)

// 搜索功能
const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    return
  }
  
  // 这里可以实现全局搜索功能
  // 暂时跳转到应用页面并搜索
  router.push({
    path: '/application',
    query: { search: searchQuery.value }
  })
  
  MsgSuccess(`搜索：${searchQuery.value}`)
}

onMounted(() => {
  // 这里可以添加API调用来获取实际数据
  applicationCount.value = 0
  datasetCount.value = 0
  chatCount.value = 0
  documentCount.value = 0
})
</script>

<style lang="scss" scoped>
.home-container {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow-x: hidden;
}

.hero-section {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 60px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  .welcome-content {
    text-align: center;
    max-width: 800px;
    width: 100%;
  }
  
  .hero-title {
    font-size: 48px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 16px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .hero-subtitle {
    font-size: 20px;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 40px;
    font-weight: 300;
  }
}

.search-container {
  margin-bottom: 40px;
  
  .search-box {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 24px;
    
    .search-input {
      max-width: 500px;
      flex: 1;
      
      :deep(.el-input__wrapper) {
        background: rgba(255, 255, 255, 0.95);
        border: none;
        border-radius: 50px;
        padding: 0 20px;
        height: 56px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        
        &:hover, &.is-focus {
          background: rgba(255, 255, 255, 1);
          box-shadow: 0 6px 30px rgba(0, 0, 0, 0.15);
        }
      }
      
      :deep(.el-input__inner) {
        font-size: 16px;
        color: #333;
        
        &::placeholder {
          color: #999;
        }
      }
      
      .search-icon {
        color: #666;
        font-size: 18px;
      }
    }
    
    .search-button {
      height: 56px;
      padding: 0 32px;
      border-radius: 50px;
      font-size: 16px;
      font-weight: 500;
      background: linear-gradient(45deg, #ff6b6b, #ee5a24);
      border: none;
      box-shadow: 0 4px 20px rgba(255, 107, 107, 0.3);
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(255, 107, 107, 0.4);
      }
    }
  }
  
  .search-suggestions {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 12px;
    
    .suggestion-label {
      color: rgba(255, 255, 255, 0.8);
      font-size: 14px;
      margin-right: 8px;
    }
    
    .suggestion-tag {
      background: rgba(255, 255, 255, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: rgba(255, 255, 255, 0.9);
      cursor: pointer;
      transition: all 0.3s ease;
      border-radius: 20px;
      padding: 6px 16px;
      
      &:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-1px);
      }
    }
  }
}

.stats-section {
  background: #f8f9fa;
  padding: 80px 0;
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
  }
  
  .section-title {
    text-align: center;
    font-size: 32px;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 48px;
  }
  
  .stats-grid {
    .stats-card {
      height: 140px;
      position: relative;
      cursor: pointer;
      transition: all 0.3s ease;
      border: none;
      border-radius: 16px;
      background: linear-gradient(145deg, #ffffff, #f0f2f5);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
      
      &:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12);
      }
      
      :deep(.el-card__body) {
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 32px;
      }
    }
    
    .stats-content {
      .stats-number {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        margin-bottom: 8px;
      }
      
      .stats-label {
        font-size: 16px;
        color: #64748b;
        font-weight: 500;
      }
    }
    
    .stats-icon {
      font-size: 56px;
      color: #667eea;
      opacity: 0.8;
      transition: all 0.3s ease;
      
      &:hover {
        color: #764ba2;
        opacity: 1;
      }
    }
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 40px 16px;
    
    .hero-title {
      font-size: 36px;
    }
    
    .hero-subtitle {
      font-size: 18px;
    }
  }
  
  .search-container .search-box {
    flex-direction: column;
    gap: 16px;
    
    .search-input {
      max-width: 100%;
    }
    
    .search-button {
      width: 100%;
      max-width: 300px;
    }
  }
  
  .stats-section {
    padding: 60px 0;
    
    .section-title {
      font-size: 28px;
    }
  }
}
</style>