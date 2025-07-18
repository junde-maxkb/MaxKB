<template>
  <div class="chat-log-search-container">
    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-form">
        <div class="search-row">
          <el-input
            v-model="searchParams.query"
            :placeholder="$t('views.application.chatLogsTab.searchPlaceholder')"
            prefix-icon="Search"
            clearable
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <el-select
            v-model="searchParams.application_id"
            :placeholder="$t('views.application.chatLogsTab.selectApplication')"
            clearable
            class="application-select"
          >
            <el-option
              v-for="app in applicationOptions"
              :key="app.value"
              :label="app.label"
              :value="app.value"
            />
          </el-select>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            :range-separator="$t('common.to')"
            :start-placeholder="$t('common.startDate')"
            :end-placeholder="$t('common.endDate')"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="date-picker"
            @change="handleDateChange"
          />
          <el-button type="primary" @click="handleSearch" :loading="loading">
            {{ $t('common.search') }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 结果列表 -->
    <div class="results-section" v-loading="loading">
      <div v-if="chatRecords.length === 0 && !loading && !hasSearched" class="no-search">
        <el-empty description="请输入搜索条件进行搜索" />
      </div>
      
      <div v-if="chatRecords.length === 0 && !loading && hasSearched" class="no-data">
        <el-empty :description="$t('views.application.chatLogsTab.noData')" />
      </div>
      
      <div v-else class="chat-records-list">
        <div 
          v-for="record in chatRecords" 
          :key="record.id" 
          class="chat-record-item"
          @click="viewRecordDetail(record)"
        >
          <div class="record-header">
            <div class="record-info">
              <h4 class="question-text">{{ record.problem_text }}</h4>
              <div class="meta-info">
                <span class="application-name">{{ record.application_name }}</span>
                <span class="chat-time">{{ formatTime(record.create_time) }}</span>
                <span class="user-name" v-if="record.user_name">{{ record.user_name }}</span>
              </div>
            </div>
            <div class="record-actions">
              <el-button text @click.stop="copyText(record.problem_text)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
              <el-button text @click.stop="viewFullDialog(record)">
                <el-icon><View /></el-icon>
              </el-button>
            </div>
          </div>
          <div class="answer-preview">
            <p class="answer-text">{{ truncateText(record.answer_text, 200) }}</p>
          </div>
          <div class="record-stats">
            <el-tag size="small" type="info">
              {{ $t('views.application.chatLogsTab.tokens', { count: record.message_tokens + record.answer_tokens }) }}
            </el-tag>
            <el-tag size="small" type="success" v-if="record.vote_status === '0'">
              {{ $t('views.application.chatLogsTab.liked') }}
            </el-tag>
            <el-tag size="small" type="danger" v-if="record.vote_status === '1'">
              {{ $t('views.application.chatLogsTab.disliked') }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination-section" v-if="total > 0">
        <el-pagination
          v-model:current-page="paginationConfig.current_page"
          v-model:page-size="paginationConfig.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { CopyDocument, View } from '@element-plus/icons-vue'
import logApi from '@/api/log'
import applicationApi from '@/api/application'
import { t } from '@/locales'
import { datetimeFormat } from '@/utils/time'

interface ChatRecord {
  id: string
  problem_text: string
  answer_text: string
  application_name: string
  application_id: string
  user_name?: string
  create_time: string
  message_tokens: number
  answer_tokens: number
  vote_status: string
  chat_id: string
}

interface ApplicationOption {
  label: string
  value: string
}

// 响应式数据
const loading = ref(false)
const chatRecords = ref<ChatRecord[]>([])
const total = ref(0)
const applicationOptions = ref<ApplicationOption[]>([])
const dateRange = ref<[string, string] | null>(null)
const hasSearched = ref(false) // 新增：用于判断是否已进行过搜索

// 搜索参数
const searchParams = reactive({
  query: '',
  application_id: '',
  start_date: '',
  end_date: ''
})

// 分页配置
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20
})

// 获取应用列表选项
const getApplicationOptions = async () => {
  try {
    const res = await applicationApi.getApplication(
      { current_page: 1, page_size: 1000 }, 
      { type: 'ALL' }
    )
    applicationOptions.value = [
      { label: t('views.application.chatLogsTab.allApplications'), value: '' },
      ...res.data.records.map((app: any) => ({
        label: app.name,
        value: app.id
      }))
    ]
  } catch (error) {
    console.error('获取应用列表失败:', error)
  }
}

// 处理日期范围变化
const handleDateChange = (dates: [string, string] | null) => {
  if (dates) {
    searchParams.start_date = dates[0]
    searchParams.end_date = dates[1]
  } else {
    searchParams.start_date = ''
    searchParams.end_date = ''
  }
}

// 搜索对话记录
const handleSearch = async () => {
  loading.value = true
  hasSearched.value = true
  
  try {
    const params = {
      ...searchParams,
      current_page: paginationConfig.current_page,
      page_size: paginationConfig.page_size
    }
    
    console.log('发起搜索请求:', params)
    
    const res = await logApi.searchChatRecords(params)
    
    console.log('搜索响应:', res)
    
    if (res && res.data) {
      chatRecords.value = res.data.records || []
      total.value = res.data.total || 0
    } else {
      console.error('搜索响应格式错误:', res)
      ElMessage.error('搜索响应格式错误')
      chatRecords.value = []
      total.value = 0
    }
  } catch (error: any) {
    console.error('搜索对话记录失败:', error)
    ElMessage.error(`搜索失败: ${error.message || '未知错误'}`)
    chatRecords.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 查看记录详情
const viewRecordDetail = (record: ChatRecord) => {
  console.log('查看记录详情:', record)
}

// 查看完整对话
const viewFullDialog = (record: ChatRecord) => {
  // 跳转到应用的对话日志页面
  window.open(`/application/${record.application_id}/log`, '_blank')
}

// 复制文本
const copyText = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success(t('common.copySuccess'))
  } catch (error) {
    ElMessage.error(t('common.copyError'))
  }
}

// 截断文本
const truncateText = (text: string, maxLength: number) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 格式化时间
const formatTime = (time: string) => {
  return datetimeFormat(new Date(time))
}

// 组件挂载时初始化
onMounted(async () => {
  await getApplicationOptions()
  // 移除自动搜索，让用户手动触发搜索
})
</script>

<style lang="scss" scoped>
.chat-log-search-container {
  padding: 24px;
  
  .search-section {
    margin-bottom: 24px;
    
    .search-form {
      .search-row {
        display: flex;
        gap: 16px;
        align-items: center;
        flex-wrap: wrap;
        
        .search-input {
          flex: 1;
          min-width: 300px;
        }
        
        .application-select {
          width: 200px;
        }
        
        .date-picker {
          width: 300px;
        }
      }
    }
  }
  
  .results-section {
    .no-search {
      text-align: center;
      padding: 60px 0;
    }
    
    .no-data {
      text-align: center;
      padding: 60px 0;
    }
    
    .chat-records-list {
      .chat-record-item {
        background: var(--el-bg-color);
        border: 1px solid var(--el-border-color);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          border-color: var(--el-color-primary);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .record-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 12px;
          
          .record-info {
            flex: 1;
            
            .question-text {
              font-size: 16px;
              font-weight: 500;
              color: var(--el-text-color-primary);
              margin: 0 0 8px 0;
              line-height: 1.4;
            }
            
            .meta-info {
              display: flex;
              gap: 16px;
              align-items: center;
              font-size: 12px;
              color: var(--el-text-color-secondary);
              
              .application-name {
                color: var(--el-color-primary);
                font-weight: 500;
              }
            }
          }
          
          .record-actions {
            display: flex;
            gap: 8px;
          }
        }
        
        .answer-preview {
          margin-bottom: 12px;
          
          .answer-text {
            color: var(--el-text-color-regular);
            line-height: 1.6;
            margin: 0;
            background: var(--el-fill-color-lighter);
            padding: 12px;
            border-radius: 6px;
          }
        }
        
        .record-stats {
          display: flex;
          gap: 8px;
          align-items: center;
        }
      }
    }
    
    .pagination-section {
      display: flex;
      justify-content: center;
      margin-top: 32px;
    }
  }
}
</style> 