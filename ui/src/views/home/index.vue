<template>
  <div class="home-container">
    <div class="hero-section" :class="{ 'searched': searchResults.length > 0 || chatMessages.length > 0 || isStreaming }">
      <div class="welcome-content">
        <h1 class="hero-title">{{ $t('views.home.welcome') }}</h1>
        <p class="hero-subtitle">{{ $t('views.home.description') }}</p>
        
        <!-- 知识库范围选择 -->
        <div class="dataset-scope-selector">
          <el-radio-group v-model="datasetScope" @change="handleScopeChange">
          <el-radio-button label="personal">个人知识库</el-radio-button>
          <el-radio-button label="organization">机构知识库</el-radio-button>
        </el-radio-group>
        </div>
        
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
    <div v-if="(searchResults.length > 0 || chatMessages.length > 0 || isStreaming) && (searchQuery || searchResults.length > 0 || chatMessages.length > 0 || isStreaming)" class="search-results-section" :class="{ 'show': searchResults.length > 0 || chatMessages.length > 0 || isStreaming }">
      <div class="container">
        <!-- 多轮对话（AI回答） -->
        <div class="ai-answer-card">
          <div class="answer-header">
            <el-icon class="answer-icon">
              <ChatDotRound />
            </el-icon>
            <h3 class="answer-title">AI回答</h3>
          </div>
          <div class="chat-window">
            <div
              v-for="(msg, idx) in chatMessages"
              :key="idx"
              class="chat-row"
              :class="{ 'from-user': msg.role === 'user', 'from-ai': msg.role !== 'user' }"
            >
              <div class="bubble">{{ msg.content }}</div>
            </div>
            <div v-if="isStreaming" class="chat-row from-ai">
              <div class="bubble">
                <span class="loading-text">回答中</span>
                <span class="dot dot1">.</span>
                <span class="dot dot2">.</span>
                <span class="dot dot3">.</span>
              </div>
            </div>
          </div>

          <div class="chat-input">
            <el-input
              v-model="chatInput"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 4 }"
              placeholder="请输入问题，回车发送"
              @keyup.enter.exact.prevent="sendChat"
            />
            <el-button type="primary" :loading="isStreaming" @click="sendChat">发送</el-button>
          </div>
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
                <span class="result-score">相关度: {{ ((result.similarity || result.comprehensive_score || 0) * 100).toFixed(1) }}%</span>
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
import { ref, onMounted, computed } from 'vue'
import { t } from '@/locales'
import { ElCard, ElRow, ElCol, ElInput, ElButton, ElTag, ElIcon } from 'element-plus'
import { Search, ChatDotRound, Document } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { MsgSuccess, MsgError } from '@/utils/message'
import applicationApi from '@/api/application'
import datasetApi from '@/api/dataset'
import { postModelChat, postModelChatStream } from '@/api/model'

const router = useRouter()

// 搜索相关
const searchQuery = ref('')
const searchLoading = ref(false)
const datasetScope = ref('personal') // 知识库范围：personal-个人, organization-机构
const hotSearches = ref([
  '人工智能',
  '机器学习', 
  '深度学习',
  '自然语言处理',
  '知识图谱'
])

// 搜索结果
const searchResults = ref<any[]>([])
// 多轮对话状态
const chatMessages = ref<Array<{ role: 'user'|'assistant'|'system'; content: string }>>([])
const chatInput = ref('')
const isStreaming = ref(false)
const resultsCount = computed(() => searchResults.value.length)
const isResultsExpanded = ref(false)

// 知识库范围相关
const personalDatasets = ref<any[]>([]) // 个人知识库（我的+共享给我的）
const organizationDatasets = ref<any[]>([]) // 机构知识库

// 处理知识库范围变化
const handleScopeChange = () => {
  // 清空搜索结果
  searchResults.value = []
  chatMessages.value = []

  // 如果切换到个人或机构知识库，可以在这里添加相应的处理逻辑
  // 例如：重新加载对应范围的知识库数据
  if (datasetScope.value === 'personal') {
    // 处理个人知识库逻辑
    console.log('切换到个人知识库')
  } else if (datasetScope.value === 'organization') {
    // 处理机构知识库逻辑
    console.log('切换到机构知识库')
  }
}

// 获取个人知识库（我的知识库 + 共享给我的知识库）
const getPersonalDatasets = async () => {
  try {
    // 获取我的知识库
    const myDatasetsResponse = await datasetApi.getDataset({ current_page: 1, page_size: 1000 }, { type: 'MY' })
    const myDatasets = myDatasetsResponse.data?.records || []
    
    // 获取共享给我的知识库
    const sharedDatasetsResponse = await datasetApi.getSharedToMeDataset({ current_page: 1, page_size: 1000 }, {})
    const sharedDatasets = sharedDatasetsResponse.data?.records || []
    
    // 合并个人知识库
    personalDatasets.value = [...myDatasets, ...sharedDatasets]
    return personalDatasets.value
  } catch (error) {
    console.error('获取个人知识库失败:', error)
    return []
  }
}

// 获取机构知识库
const getOrganizationDatasets = async () => {
  try {
    const orgDatasetsResponse = await datasetApi.getOrganizationDataset({ current_page: 1, page_size: 1000 }, {})
    organizationDatasets.value = orgDatasetsResponse.data?.records || []
    return organizationDatasets.value
  } catch (error) {
    console.error('获取机构知识库失败:', error)
    return []
  }
}

// 默认显示所有知识库检索条目
const allDatasets = ref<any[]>([])
const defaultResults = ref<any[]>([])

// 搜索功能
const handleSearch = async () => {
  // 检查搜索框是否为空，如果为空则阻止搜索
  if (!searchQuery.value || searchQuery.value.trim() === '') {
    MsgError('请输入搜索内容')
    return
  }
  
  searchLoading.value = true
  searchResults.value = []
  chatMessages.value = []
  chatInput.value = ''
  isStreaming.value = false
  
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
      
      // 按相似度或综合分排序
      allResults.sort((a, b) => {
        const sa = (a.similarity ?? a.comprehensive_score ?? 0)
        const sb = (b.similarity ?? b.comprehensive_score ?? 0)
        return sb - sa
      })
      
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
const performKnowledgeSearch = async () => {
  try {
    // 根据选择的知识库范围获取相应的数据集
    let datasets = []
    
    if (datasetScope.value === 'personal') {
      // 获取个人知识库
      datasets = await getPersonalDatasets()
    } else if (datasetScope.value === 'organization') {
      // 获取机构知识库
      datasets = await getOrganizationDatasets()
    }
    
    // 清空之前的搜索结果
    searchResults.value = []
    
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
    
    // 按相似度或综合分排序
    searchResults.value.sort((a, b) => {
      const sa = (a.similarity ?? a.comprehensive_score ?? 0)
      const sb = (b.similarity ?? b.comprehensive_score ?? 0)
      return sb - sa
    })
    
    // 只保留前10个最相关的结果
    searchResults.value = searchResults.value.slice(0, 10)
  } catch (error) {
    console.error('知识库检索失败:', error)
    throw error
  }
}

// 解析默认模型ID（本地存储优先，缺省时自动选择第一个可用模型并缓存）
const resolveDefaultModelId = async (): Promise<string> => {
  const cached = localStorage.getItem('home_default_model_id')
  if (cached) return cached
  try {
    const res = await (await import('@/api/model')).default.getModel()
    const list = res.data || []
    const first = list[0]
    if (first?.id) {
      localStorage.setItem('home_default_model_id', first.id)
      return first.id
    }
  } catch (e) {
    console.warn('获取默认模型失败', e)
  }
  return ''
}

// AI回答（改为调用直连模型单轮对话接口）
// 首轮：基于检索上下文发起一轮对话（把上下文放system）
const performAIAnswer = async () => {
  try {
    isStreaming.value = true
    // 构建检索到的内容作为上下文，包含标题、内容、来源和数据集信息
    const buildSearchContext = () => {
      return searchResults.value
        .slice(0, 3) // 只使用前3个最相关的结果
        .map((result, index) => `条目 ${index + 1}：
 标题：${result.title || `条目 ${index + 1}`}
 内容：${result.content}
 来源：${result.source || '知识库'}
 数据集：${result.dataset_name || '未知'}`)
        .join('\n\n')
    }
    const context = buildSearchContext()
    
    // 构建消息
    const messages = [
      { role: 'system', content: '你是一个知识库助手，请根据以下上下文回答问题:\n\n' + context },
      ...chatMessages.value,
      { role: 'user', content: searchQuery.value }
    ]

    // 选择一个默认模型或从配置中获取，这里先从本地存储或固定ID占位
    const defaultModelId = await resolveDefaultModelId()
    if (!defaultModelId) {
      console.warn('未找到可用模型，请先在“模型”中创建/配置。')
      chatMessages.value.push({ role: 'assistant', content: '未找到可用模型，请到“模型”页面创建或配置一个可用的大语言模型后再试。' })
      return
    }

    // 累积到对话窗口
    chatMessages.value.push({ role: 'user', content: searchQuery.value })
    const resp = await postModelChatStream(defaultModelId, { messages })
    if (resp?.body && typeof resp.body.getReader === 'function') {
      const reader = resp.body.getReader()
      const decoder = new TextDecoder('utf-8')
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value)
        const parts = chunk.match(/data:.*\n\n/g)
        if (parts) {
          for (const p of parts) {
            try {
              const json = JSON.parse(p.replace('data:', ''))
              if (json?.content) {
                // 若上一条是assistant，拼接；否则新开一条assistant
                const last = chatMessages.value[chatMessages.value.length - 1]
                if (last && last.role === 'assistant') {
                  last.content += json.content
                } else {
                  chatMessages.value.push({ role: 'assistant', content: json.content })
                }
              }
            } catch (e) {}
          }
        }
      }
    } else if ((resp as any)?.data?.content) {
      chatMessages.value.push({ role: 'assistant', content: (resp as any).data.content })
    } else {
      chatMessages.value.push({ role: 'assistant', content: '抱歉，生成回答失败。' })
    }
  } catch (error) {
    console.error('AI回答失败:', error)
    chatMessages.value.push({ role: 'assistant', content: '抱歉，生成回答时出现错误，请重试。' })
  }
  finally {
    isStreaming.value = false
  }
}

// 继续多轮：仅把历史 messages 和最新用户输入发送
const sendChat = async () => {
  const content = chatInput.value.trim()
  if (!content) return
  isStreaming.value = true
  try {
    const defaultModelId = await resolveDefaultModelId()
    if (!defaultModelId) {
      MsgError('未找到可用模型，请先在“模型”中创建/配置。')
      isStreaming.value = false
      return
    }
    // 每次追问也附带最近一次检索上下文（放在 system）
    const ctx = searchResults.value
      .slice(0, 3)
      .map((r, i) => `条目 ${i + 1}：\n标题：${r.title || `条目 ${i + 1}`}\n内容：${r.content}\n来源：${r.source || '知识库'}\n数据集：${r.dataset_name || '未知'}`)
      .join('\n\n')
    const messages = [
      { role: 'system', content: '你是一个知识库助手，请根据以下上下文回答问题:\n\n' + ctx },
      ...chatMessages.value,
      { role: 'user', content }
    ]
    chatMessages.value.push({ role: 'user', content })
    chatInput.value = ''
    const resp = await postModelChatStream(defaultModelId, { messages })
    if (resp?.body && typeof resp.body.getReader === 'function') {
      const reader = resp.body.getReader()
      const decoder = new TextDecoder('utf-8')
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value)
        const parts = chunk.match(/data:.*\n\n/g)
        if (parts) {
          for (const p of parts) {
            try {
              const json = JSON.parse(p.replace('data:', ''))
              if (json?.content) {
                const last = chatMessages.value[chatMessages.value.length - 1]
                if (last && last.role === 'assistant') {
                  last.content += json.content
                } else {
                  chatMessages.value.push({ role: 'assistant', content: json.content })
                }
              }
            } catch (e) {}
          }
        }
      }
    } else if ((resp as any)?.data?.content) {
      chatMessages.value.push({ role: 'assistant', content: (resp as any).data.content })
    } else {
      chatMessages.value.push({ role: 'assistant', content: '抱歉，生成回答失败。' })
    }
  } catch (e) {
    console.error(e)
    chatMessages.value.push({ role: 'assistant', content: '服务异常，请稍后再试。' })
  } finally {
    isStreaming.value = false
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
  min-height: 80vh;
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
  
  .dataset-scope-selector {
    margin-bottom: 20px;
    
    :deep(.el-radio-group) {
      .el-radio-button {
        margin-right: 10px;
        
        &:last-child {
          margin-right: 0;
        }
      }
      
      .el-radio-button__inner {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        padding: 12px 20px;
        font-size: 16px;
        
        &:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      }
      
      .el-radio-button:first-child .el-radio-button__inner {
        border-radius: 8px;
      }
      
      .el-radio-button:last-child .el-radio-button__inner {
        border-radius: 8px;
      }
      
      .el-radio-button.is-active {
        .el-radio-button__inner {
          background: #ffffff;
          color: var(--el-color-primary);
          border-color: #ffffff;
        }
      }
    }
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
  display: none;
  
  &.show {
    display: block;
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
  }
  
  .ai-answer-card {
    .chat-window {
      max-height: 400px;
      overflow-y: auto;
      margin-bottom: 16px;
    }

    .chat-row {
      display: flex;
      margin: 8px 0;
      &.from-user { justify-content: flex-end; }
      &.from-ai { justify-content: flex-start; }
      .bubble {
        max-width: 80%;
        padding: 10px 12px;
        border-radius: 12px;
        font-size: 14px;
        line-height: 1.6;
        white-space: pre-wrap;
      }
      &.from-user .bubble {
        background: #4f46e5;
        color: #fff;
      }
      &.from-ai .bubble {
        background: #f3f4f6;
        color: #111827;
      }
    }

    .chat-input {
      display: flex;
      gap: 8px;
      align-items: center;
    }
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

    .answer-loading {
      display: inline-flex;
      align-items: baseline;
      font-size: 16px;
      color: #4a5568;
      .loading-text {
        margin-right: 4px;
      }
      .dot {
        display: inline-block;
        width: 4px;
        height: 4px;
        margin-left: 2px;
        border-radius: 50%;
        background: #667eea;
        opacity: 0.2;
        animation: blink 1.2s infinite ease-in-out;
      }
      .dot1 { animation-delay: 0s; }
      .dot2 { animation-delay: 0.2s; }
      .dot3 { animation-delay: 0.4s; }
    }
  }

@keyframes blink {
  0%, 80%, 100% { opacity: 0.2; }
  40% { opacity: 1; }
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