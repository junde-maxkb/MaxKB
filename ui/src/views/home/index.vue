<template>
  <div class="home-container">
    <div class="hero-section" :class="{ 'searched': searchResults.length > 0 || aiAnswer }">
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
              :loading="searchLoading"
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

    <!-- 搜索结果展示区域 -->
    <div v-if="searchResults.length > 0 || aiAnswer" class="search-results-section">
      <div class="container">
        <!-- AI回答 -->
        <div v-if="aiAnswer" class="ai-answer-card">
          <div class="answer-header">
            <el-icon class="answer-icon">
              <ChatDotRound />
            </el-icon>
            <h3 class="answer-title">AI回答</h3>
          </div>
          <div class="answer-content" v-html="aiAnswer"></div>
        </div>

        <!-- 检索结果 -->
        <div v-if="searchResults.length > 0" class="search-results">
          <div class="results-header">
            <h3 class="results-title">
              <el-icon class="results-icon">
                <Document />
              </el-icon>
              检索到的知识库条目 ({{ searchResults.length }})
            </h3>
            <el-button 
              type="primary" 
              text 
              @click="toggleResultsExpanded"
            >
              {{ isResultsExpanded ? '收起检索结果' : '展开检索结果' }}
            </el-button>
          </div>
          
          <div class="results-list" :class="{ 'expanded': isResultsExpanded }">
            <div 
              v-for="(result, index) in searchResults" 
              :key="index"
              class="result-item"
            >
              <div class="result-header">
                <span class="result-title">{{ result.title || `条目 ${index + 1}` }}</span>
                <span class="result-score">相关度: {{ (result.score * 100).toFixed(1) }}%</span>
              </div>
              <div class="result-content">{{ result.content }}</div>
              <div class="result-meta">
                <span class="result-source">来源: {{ result.source || '知识库' }}</span>
                <span class="result-dataset">数据集: {{ result.dataset_name || '未知' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { t } from '@/locales'
import { ElCard, ElRow, ElCol, ElInput, ElButton, ElTag, ElIcon } from 'element-plus'
import { Search, ChatDotRound, Document } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { MsgSuccess, MsgError } from '@/utils/message'
import applicationApi from '@/api/application'
import datasetApi from '@/api/dataset'

const router = useRouter()

// 搜索相关
const searchQuery = ref('')
const searchLoading = ref(false)
const hotSearches = ref([
  '人工智能',
  '机器学习', 
  '深度学习',
  '自然语言处理',
  '知识图谱'
])

// 搜索结果
const searchResults = ref<any[]>([])
const aiAnswer = ref('')
const isResultsExpanded = ref(false)

// 默认显示所有知识库检索条目
const allDatasets = ref<any[]>([])
const defaultResults = ref<any[]>([])

// 搜索功能
const handleSearch = async () => {
  // 检查搜索框是否为空，如果为空则显示默认结果
  if (!searchQuery.value || searchQuery.value.trim() === '') {
    await showDefaultResults()
    return
  }
  
  searchLoading.value = true
  searchResults.value = []
  aiAnswer.value = ''
  
  try {
    // 1. 首先进行知识库检索
    await performKnowledgeSearch()
    
    // 2. 使用默认模型进行AI回答
    await performAIAnswer()
    
    MsgSuccess(`搜索完成：${searchQuery.value}`)
  } catch (error) {
    console.error('搜索失败:', error)
    MsgError('搜索失败，请重试')
  } finally {
    searchLoading.value = false
  }
}

// 显示默认结果
// 知识库检索
const showDefaultResults = async () => {
  searchLoading.value = true
  try {
    // 获取所有数据集
    const datasetsResponse = await datasetApi.getAllDataset()
    if (datasetsResponse.code === 200 && datasetsResponse.data) {
      allDatasets.value = datasetsResponse.data
      
      // 对每个数据集进行检索，获取默认条目
      const allResults: any[] = []
      
      for (const dataset of allDatasets.value) {
        try {
          const searchData = {
            query_text: ' ', // 使用空格而不是空字符串
            top_number: 3, // 默认值为3
            similarity: 0.0,
            search_mode: 'embedding' // 默认设置为向量索引
          }
          
          const response = await datasetApi.getDatasetHitTest(dataset.id, searchData)
          if (response.code === 200 && response.data) {
            const results = response.data.map((item: any) => ({
              ...item,
              dataset_name: dataset.name,
              source: dataset.name
            }))
            allResults.push(...results)
          }
        } catch (error) {
          console.warn(`数据集 ${dataset.name} 检索失败:`, error)
        }
      }
      
      // 按相关度排序
      allResults.sort((a, b) => b.score - a.score)
      
      // 只保留前10个最相关的结果
      defaultResults.value = allResults.slice(0, 10)
      searchResults.value = [...defaultResults.value]
    }
  } catch (error) {
    console.error('获取默认结果失败:', error)
  } finally {
    searchLoading.value = false
  }
}

// 知识库检索
// 知识库检索
// 知识库检索
const performKnowledgeSearch = async () => {
  try {
    // 获取所有数据集
    const datasetsResponse = await datasetApi.getAllDataset()
    if (datasetsResponse.code === 200 && datasetsResponse.data) {
      const datasets = datasetsResponse.data
      
      // 对每个数据集进行检索
      for (const dataset of datasets) {
        try {
          // 检查查询文本是否为空，如果为空则使用空格
          const queryText = searchQuery.value || ' ';
          
          const searchData = {
            query_text: queryText,
            top_number: 5, // 默认值为5
            similarity: 0.5,
            search_mode: 'embedding' // 默认设置为向量索引
          }
          
          const response = await datasetApi.getDatasetHitTest(dataset.id, searchData)
          if (response.code === 200 && response.data) {
            const results = response.data.map((item: any) => ({
              ...item,
              dataset_name: dataset.name,
              source: dataset.name
            }))
            searchResults.value.push(...results)
          }
        } catch (error) {
          console.warn(`数据集 ${dataset.name} 检索失败:`, error)
        }
      }
      
      // 按相关度排序
      searchResults.value.sort((a, b) => b.score - a.score)
      
      // 只保留前10个最相关的结果
      searchResults.value = searchResults.value.slice(0, 10)
    }
  } catch (error) {
    console.error('知识库检索失败:', error)
    throw error
  }
}

// AI回答
const performAIAnswer = async () => {
  try {
    // 构建检索到的内容作为上下文
    const context = searchResults.value
      .map(result => result.content)
      .join('\n\n')
    
    // 构建提示词
    const prompt = `基于以下知识库内容回答问题：

知识库内容：
${context}

问题：${searchQuery.value}

请基于上述知识库内容，用简洁明了的语言回答问题。如果知识库中没有相关信息，请说明无法找到相关信息。`

    // 这里需要调用AI模型API
    // 由于没有直接的AI回答API，我们可以创建一个简单的模拟回答
    if (searchResults.value.length > 0) {
      aiAnswer.value = `根据知识库检索结果，我为您找到了相关信息：

${searchResults.value.slice(0, 3).map((result, index) => 
  `${index + 1}. ${result.content.substring(0, 200)}...`
).join('\n\n')}

以上是知识库中最相关的信息。如果您需要更详细的回答，请提供更具体的问题。`
    } else {
      aiAnswer.value = '抱歉，我在知识库中没有找到与您问题相关的信息。请尝试使用其他关键词或重新描述您的问题。'
    }
  } catch (error) {
    console.error('AI回答失败:', error)
    aiAnswer.value = '抱歉，AI回答生成失败，请重试。'
  }
}

// 切换结果展开状态
const toggleResultsExpanded = () => {
  isResultsExpanded.value = !isResultsExpanded.value
}

onMounted(() => {
  // 移除了默认查询操作
  // showDefaultResults()
})
</script>

<style lang="scss" scoped>
.home-container {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #6495ED 0%, #87CEEB 100%);
  overflow-x: hidden;
}

.hero-section {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 60px 24px;
  background: linear-gradient(135deg, #6495ED 0%, #87CEEB 100%);
  transition: all 0.5s ease;
  
  &.searched {
    min-height: 100px;
    padding: 20px 24px;
    
    .hero-title,
    .hero-subtitle,
    .search-suggestions {
      opacity: 0;
      visibility: hidden;
      height: 0;
      margin: 0;
      padding: 0;
      overflow: hidden;
    }
    
    .search-container {
      margin-bottom: 0;
      
      .search-box {
        justify-content: flex-start;
        max-width: 1200px;
        margin: 0 auto;
      }
    }
  }
  
  .welcome-content {
    text-align: center;
    max-width: 800px;
    width: 100%;
    transition: all 0.5s ease;
    
    &.searched {
      max-width: 100%;
    }
  }
  
  .hero-title {
    font-size: 48px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 16px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.5s ease;
  }
  
  .hero-subtitle {
    font-size: 20px;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 40px;
    font-weight: 300;
    transition: all 0.5s ease;
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
      max-width: 600px;
      flex: 1;
      
      :deep(.el-input__wrapper) {
        background: #fff;
        border: 1px solid var(--el-border-color-light);
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
        
        &:hover, &.is-focus {
          border-color: var(--el-color-primary);
          box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
        }
      }
      
      :deep(.el-input__inner) {
        font-size: 14px;
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
      padding: 0 32px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      background: #ffffff;
      color: var(--el-color-primary);
      border: 1px solid var(--el-color-primary);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
      transition: all 0.3s ease;
      
      &:hover {
        background: var(--el-color-primary);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
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

.search-results-section {
  background: #f8f9fa;
  padding: 20px 0 60px 0;
  transition: all 0.5s ease;
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
  }
  
  .ai-answer-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 32px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
    border: 1px solid #e9ecef;
    
    .answer-header {
      display: flex;
      align-items: center;
      margin-bottom: 20px;
      
      .answer-icon {
        font-size: 24px;
        color: #667eea;
        margin-right: 12px;
      }
      
      .answer-title {
        font-size: 20px;
        font-weight: 600;
        color: #2c3e50;
        margin: 0;
      }
    }
    
    .answer-content {
      font-size: 16px;
      line-height: 1.6;
      color: #4a5568;
      white-space: pre-line;
    }
  }
  
  .search-results {
    background: #ffffff;
    border-radius: 16px;
    padding: 32px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
    border: 1px solid #e9ecef;
    
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      
      .results-title {
        display: flex;
        align-items: center;
        font-size: 18px;
        font-weight: 600;
        color: #2c3e50;
        margin: 0;
        
        .results-icon {
          font-size: 20px;
          color: #667eea;
          margin-right: 8px;
        }
      }
    }
    
    .results-list {
      max-height: 400px;
      overflow: hidden;
      transition: max-height 0.3s ease;
      
      &.expanded {
        max-height: none;
      }
      
      &:not(.expanded) {
        max-height: 0;
      }
      
      .result-item {
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        background: #fafbfc;
        transition: all 0.3s ease;
        
        &:hover {
          border-color: #667eea;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
        }
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .result-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          
          .result-title {
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
          }
          
          .result-score {
            font-size: 14px;
            color: #667eea;
            font-weight: 500;
          }
        }
        
        .result-content {
          font-size: 14px;
          line-height: 1.5;
          color: #4a5568;
          margin-bottom: 12px;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        
        .result-meta {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #718096;
          
          .result-source,
          .result-dataset {
            background: #f1f5f9;
            padding: 4px 8px;
            border-radius: 6px;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 40px 16px;
    
    &.searched {
      padding: 15px 16px;
      min-height: 80px;
    }
    
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
  
  .search-results-section {
    padding: 15px 0 40px 0;
    
    .container {
      padding: 0 16px;
    }
    
    .ai-answer-card,
    .search-results {
      padding: 24px;
    }
    
    .results-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
  }
}
</style>