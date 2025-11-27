<template>
  <div class="chat-history-panel">
    <div class="chat-history-content">
      <div class="search-filter-section">
        <div class="search-row">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索聊天记录..."
            clearable
            prefix-icon="Search"
            @input="handleSearch"
          />
          <el-button 
            class="refresh-btn" 
            @click="handleRefresh" 
            :loading="loading"
            circle
          >
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </div>
      <div class="list-divider"></div>
      <div class="history-list-container" v-loading="loading">
        <el-scrollbar>
          <div class="p-8 pt-0">
            <common-list
              :data="displayedList"
              class="mt-8"
              :defaultActive="selectedHistoryId"
              @click="viewDetail"
            >
              <template #default="{ row }">
                <div class="history-item-wrapper">
                  <div class="history-item-content">
                    <div class="history-title">
                      <auto-tooltip :content="row.title || row.application_name">
                        {{ row.title || row.application_name }}
                      </auto-tooltip>
                    </div>
                    <div class="history-meta">
                      <el-tag size="small" type="primary" class="application-tag">
                        {{ row.application_name }}
                      </el-tag>
                      <span class="message-count">
                        <el-icon class="mr-4"><ChatLineRound /></el-icon>
                        {{ row.message_count }} {{ $t('views.user.chatHistory.messages') }}
                      </span>
                      <span class="create-time">
                        <el-icon class="mr-4"><Clock /></el-icon>
                        {{ datetimeFormat(row.create_time) }}
                      </span>
                    </div>
                  </div>
                </div>
              </template>
              <template #empty>
                <div class="text-center p-24">
                  <el-empty :description="$t('views.user.chatHistory.noHistory')" :image-size="100" />
                </div>
              </template>
            </common-list>
          </div>
        </el-scrollbar>
      </div>
      <div class="pagination-section p-16-24 border-t" v-if="paginationConfig.total > 0">
        <div class="pagination-left">
          <span class="pagination-total">共 {{ paginationConfig.total }} 条</span>
          <el-select
            v-model="paginationConfig.page_size"
            size="small"
            style="width: 100px"
            @change="handleSizeChange"
          >
            <el-option :value="10" label="10条/页" />
            <el-option :value="20" label="20条/页" />
            <el-option :value="50" label="50条/页" />
            <el-option :value="100" label="100条/页" />
          </el-select>
        </div>
        <el-pagination
          v-model:current-page="paginationConfig.current_page"
          :page-size="paginationConfig.page_size"
          :total="paginationConfig.total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
          small
        />
      </div>
    </div>
    
    <!-- 聊天详情对话框 - 使用聊天界面样式 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="selectedHistory?.title || selectedHistory?.application_name"
      width="70%"
      destroy-on-close
      append-to-body
      class="chat-detail-dialog"
    >
      <div class="chat-detail-content" v-loading="detailLoading">
        <!-- 只读提示 -->
        <div class="readonly-notice">
          <el-icon><InfoFilled /></el-icon>
          <span>历史对话仅供查看，不可继续对话</span>
        </div>
        
        <!-- 聊天界面容器 -->
        <el-scrollbar height="500px" ref="chatScrollRef">
          <div class="chat-messages">
            <template v-for="(message, index) in chatMessages" :key="index">
              <!-- 用户消息 -->
              <div v-if="message.role === 'user'" class="message-item user-message">
                <div class="message-content user-content">
                  <span>{{ message.content }}</span>
                </div>
              </div>
              
              <!-- AI助手消息 -->
              <div v-else class="message-item ai-message">
                <div class="ai-avatar">
                  <svg width="28" height="28" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="30" cy="30" r="28" stroke="#5E56DD" stroke-width="2" fill="none"/>
                    <text x="30" y="38" text-anchor="middle" fill="#5E56DD" font-size="24" font-weight="bold">Ai</text>
                  </svg>
                </div>
                <div class="message-content ai-content">
                  <div class="ai-answer">
                    <div class="answer-content">
                      <MdRenderer :source="message.content" />
                    </div>
                  </div>
                </div>
              </div>
            </template>
            
            <div v-if="chatMessages.length === 0 && !detailLoading" class="empty-chat">
              <el-empty description="暂无对话记录" :image-size="80" />
            </div>
          </div>
        </el-scrollbar>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, reactive, nextTick } from 'vue'
import { Refresh, ChatLineRound, Clock, InfoFilled } from '@element-plus/icons-vue'
import CommonList from '@/components/common-list/index.vue'
import AutoTooltip from '@/components/auto-tooltip/index.vue'
import MdRenderer from '@/components/markdown/MdRenderer.vue'
import userApi from '@/api/user-manage'
import { datetimeFormat } from '@/utils/time'

defineOptions({ name: 'ChatHistoryPanel' })

const props = withDefaults(
  defineProps<{
    userId: string
    username: string
  }>(),
  {
    userId: '',
    username: ''
  }
)

const loading = ref(false)
const detailLoading = ref(false)
const chatHistoryList = ref<any[]>([])
const selectedHistoryId = ref('')
const mouseId = ref('')
const detailDialogVisible = ref(false)
const selectedHistory = ref<any>(null)
const chatMessages = ref<any[]>([])
const searchKeyword = ref('')
const chatScrollRef = ref<any>(null)

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

// 搜索处理函数
function handleSearch() {
  // 搜索时重置到第一页
  paginationConfig.current_page = 1
}

// 列表（增加搜索过滤）
const filteredList = computed(() => {
  let list = [...chatHistoryList.value]

  // 如果有搜索关键词，进行过滤
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    list = list.filter(item => {
      const title = (item.title || item.application_name || '').toLowerCase()
      return title.includes(keyword)
    })
  }

  return list
})

// 分页显示列表
const displayedList = computed(() => {
  const start = (paginationConfig.current_page - 1) * paginationConfig.page_size
  const end = start + paginationConfig.page_size
  return filteredList.value.slice(start, end)
})

function closeHandle() {
  chatHistoryList.value = []
  selectedHistoryId.value = ''
  mouseId.value = ''
  paginationConfig.current_page = 1
  paginationConfig.total = 0
}

function getChatHistory() {
  if (!props.userId) return
  loading.value = true
  // 获取所有历史记录，在前端进行分页
  userApi
    .getChatHistory(props.userId, loading)
    .then((res: any) => {
      if (res.code === 200) {
        chatHistoryList.value = res.data || []
        updatePaginationTotal()
      }
    })
    .finally(() => {
      loading.value = false
    })
}

function handleRefresh() {
  paginationConfig.current_page = 1
  getChatHistory()
}

function updatePaginationTotal() {
  paginationConfig.total = filteredList.value.length
}

function handleSizeChange(size: number) {
  paginationConfig.page_size = size
  paginationConfig.current_page = 1
}

function handlePageChange(page: number) {
  paginationConfig.current_page = page
}

function clickHistoryHandle(item: any) {
  selectedHistoryId.value = item.id
}

function mouseenter(item: any) {
  mouseId.value = item.id
}

async function viewDetail(item: any) {
  selectedHistory.value = item
  detailDialogVisible.value = true
  detailLoading.value = true
  chatMessages.value = []

  try {
    const res = await userApi.getChatMessages(item.id)
    if (res.code === 200) {
      chatMessages.value = res.data || []
      // 按 message_index 排序
      chatMessages.value.sort((a: any, b: any) => {
        return (a.message_index || 0) - (b.message_index || 0)
      })
      // 滚动到顶部
      nextTick(() => {
        if (chatScrollRef.value) {
          chatScrollRef.value.setScrollTop(0)
        }
      })
    }
  } catch (error) {
    console.error('获取聊天消息失败:', error)
  } finally {
    detailLoading.value = false
  }
}

const loadHistory = () => {
  if (props.userId) {
    getChatHistory()
  }
}

watch(
  () => props.userId,
  (newVal) => {
    if (newVal) {
      getChatHistory()
    } else {
      closeHandle()
    }
  },
  { immediate: true }
)

watch(
  () => filteredList.value.length,
  () => {
    updatePaginationTotal()
  }
)

defineExpose({
  loadHistory
})
</script>

<style lang="scss" scoped>
// 紫色主题色变量
$theme-primary: #554BDB;
$theme-primary-light: rgba(85, 75, 219, 0.1);
$theme-primary-lighter: rgba(85, 75, 219, 0.05);
$theme-gradient: linear-gradient(135deg, #554BDB 0%, #7B6FE8 100%);
$theme-gradient-light: linear-gradient(135deg, rgba(85, 75, 219, 0.08) 0%, rgba(123, 111, 232, 0.04) 100%);

.chat-history-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  overflow: hidden;
}

.chat-history-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #ffffff;
}

.search-filter-section {
  flex-shrink: 0;
  padding: 0 0 16px 0;
  
  .search-row {
    display: flex;
    align-items: center;
    gap: 12px;
    
    :deep(.el-input) {
      flex: 1;
      
      .el-input__wrapper {
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(85, 75, 219, 0.08);
        border: 1px solid rgba(85, 75, 219, 0.15);
        transition: all 0.3s ease;
        
        &:hover {
          border-color: rgba(85, 75, 219, 0.3);
        }
        
        &.is-focus {
          border-color: $theme-primary;
          box-shadow: 0 0 0 3px rgba(85, 75, 219, 0.12);
        }
      }
      
      .el-input__prefix {
        color: $theme-primary;
      }
    }
  }
  
  .refresh-btn {
    flex-shrink: 0;
    border: 1px solid rgba(85, 75, 219, 0.2);
    background: #ffffff;
    color: $theme-primary;
    transition: all 0.3s ease;
    
    &:hover {
      background: $theme-primary-light;
      border-color: $theme-primary;
    }
  }
}

.list-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(85, 75, 219, 0.15), transparent);
  margin: 0 0 8px 0;
}

.border-t {
  border-top: 1px solid rgba(85, 75, 219, 0.1);
}

.history-list-container {
  flex: 1;
  overflow: hidden;
  min-height: 0;
  
  :deep(.common-list) {
    .list-item {
      margin-bottom: 8px;
      border-radius: 12px;
      border: 1px solid rgba(85, 75, 219, 0.08);
      background: #ffffff;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      
      &:hover {
        transform: translateX(4px);
        border-color: rgba(85, 75, 219, 0.25);
        box-shadow: 0 4px 16px rgba(85, 75, 219, 0.12);
        background: $theme-gradient-light;
      }
      
      &.active {
        border-color: $theme-primary;
        background: $theme-primary-light;
        box-shadow: 0 4px 16px rgba(85, 75, 219, 0.15);
      }
    }
  }
}

.history-item-wrapper {
  width: 100%;
  padding: 8px 4px;
  
  &:hover {
    .history-actions {
      opacity: 1;
    }
  }
}

.history-item-content {
  flex: 1;
  min-width: 0;
}

.history-title {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 10px;
  line-height: 1.5;
  
  :deep(.auto-tooltip) {
    &:hover {
      color: $theme-primary;
    }
  }
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  flex-wrap: wrap;
  
  .application-tag {
    margin-right: 0;
    background: $theme-primary-light;
    border: none;
    color: $theme-primary;
    font-weight: 500;
    padding: 2px 10px;
    border-radius: 6px;
  }
  
  .message-count,
  .create-time {
    display: flex;
    align-items: center;
    color: #718096;
    
    .el-icon {
      font-size: 14px;
      margin-right: 4px;
      color: $theme-primary;
      opacity: 0.7;
    }
  }
  
  .create-time {
    color: #a0aec0;
    
    .el-icon {
      opacity: 0.5;
    }
  }
}

.history-actions {
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
  margin-left: 8px;
}

.pagination-section {
  flex-shrink: 0;
  background: linear-gradient(180deg, #ffffff 0%, #fafbff 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  overflow-x: auto;
  border-top: 1px solid rgba(85, 75, 219, 0.08);
  
  .pagination-left {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .pagination-total {
      font-size: 13px;
      color: #718096;
      white-space: nowrap;
    }
    
    :deep(.el-select) {
      .el-input__wrapper {
        border-radius: 6px;
        
        &:hover, &.is-focus {
          border-color: $theme-primary;
        }
      }
    }
  }
  
  :deep(.el-pagination) {
    .el-pager {
      li {
        border-radius: 6px;
        
        &.is-active {
          background: $theme-primary;
          color: #ffffff;
        }
        
        &:hover:not(.is-active) {
          color: $theme-primary;
        }
      }
    }
    
    .btn-prev, .btn-next {
      border-radius: 6px;
      
      &:hover {
        color: $theme-primary;
      }
    }
  }
}

// 聊天详情对话框样式
.chat-detail-content {
  .readonly-notice {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 20px;
    margin-bottom: 16px;
    background: linear-gradient(135deg, rgba(85, 75, 219, 0.08) 0%, rgba(123, 111, 232, 0.04) 100%);
    border: 1px solid rgba(85, 75, 219, 0.2);
    border-radius: 12px;
    color: $theme-primary;
    font-size: 13px;
    font-weight: 500;
    
    .el-icon {
      font-size: 18px;
    }
  }
  
  // 与 ChatPage 保持一致的消息样式
  .chat-messages {
    padding: 16px;
    background: linear-gradient(180deg, #fafbff 0%, #f5f7ff 100%);
    border-radius: 12px;
    
    .message-item {
      margin-bottom: 24px;

      &.user-message {
        display: flex;
        justify-content: flex-end;

        .user-content {
          display: inline-block;
          background: $theme-gradient;
          border-radius: 16px 16px 4px 16px;
          padding: 12px 18px;
          max-width: 80%;
          word-break: break-word;
          color: #ffffff;
          font-weight: 500;
          box-shadow: 0 4px 12px rgba(85, 75, 219, 0.25);
        }
      }

      &.ai-message {
        display: flex;
        align-items: flex-start;
        gap: 12px;

        .ai-avatar {
          flex-shrink: 0;
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: $theme-primary-light;
          border-radius: 10px;
          
          svg {
            circle {
              stroke: $theme-primary;
            }
            text {
              fill: $theme-primary;
            }
          }
        }

        .ai-content {
          max-width: 80%;

          .ai-answer {
            display: inline-block;
            background: #ffffff;
            border-radius: 4px 16px 16px 16px;
            padding: 16px 20px;
            box-shadow: 0 2px 12px rgba(85, 75, 219, 0.08);
            border: 1px solid rgba(85, 75, 219, 0.08);

            .answer-content {
              :deep(.md-renderer) {
                font-size: 14px;
                line-height: 1.7;
                color: #2d3748;
                
                p {
                  margin: 0 0 8px 0;
                  
                  &:last-child {
                    margin-bottom: 0;
                  }
                }
                
                pre {
                  margin: 12px 0;
                  border-radius: 10px;
                  background: #1e1e2e;
                }
                
                code {
                  font-size: 13px;
                  background: $theme-primary-light;
                  color: $theme-primary;
                  padding: 2px 6px;
                  border-radius: 4px;
                }
                
                a {
                  color: $theme-primary;
                  
                  &:hover {
                    text-decoration: underline;
                  }
                }
                
                strong {
                  color: #1a202c;
                }
              }
            }
          }
        }
      }
    }
    
    .empty-chat {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 200px;
    }
  }
}

// 工具类
.flex {
  display: flex;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.align-center {
  align-items: center;
}

.gap-8 {
  gap: 8px;
}

.gap-12 {
  gap: 12px;
}

.mb-8 {
  margin-bottom: 8px;
}

.mb-12 {
  margin-bottom: 12px;
}

.mb-16 {
  margin-bottom: 16px;
}

.ml-8 {
  margin-left: 8px;
}

.mr-4 {
  margin-right: 4px;
}

.mt-8 {
  margin-top: 8px;
}

.p-8 {
  padding: 8px;
}

.p-16 {
  padding: 16px;
}

.p-24 {
  padding: 24px;
}

.p-16-24 {
  padding: 16px 24px;
}

.pt-0 {
  padding-top: 0;
}

.pb-0 {
  padding-bottom: 0;
}

.text-center {
  text-align: center;
}
</style>

<!-- 对话框样式需要不带 scoped 因为 append-to-body -->
<style lang="scss">
.chat-detail-dialog {
  border-radius: 16px !important;
  overflow: hidden;
  
  .el-dialog__header {
    background: #ffffff;
    padding: 18px 24px;
    margin-right: 0;
    border-bottom: 1px solid #e5e7eb;
    
    .el-dialog__title {
      color: #2d3748;
      font-weight: 600;
      font-size: 16px;
    }
    
    .el-dialog__headerbtn {
      top: 18px;
      right: 20px;
      width: 28px;
      height: 28px;
      
      .el-dialog__close {
        color: #909399;
        font-size: 18px;
        
        &:hover {
          color: #554BDB;
        }
      }
    }
  }
  
  .el-dialog__body {
    padding: 24px;
    background: #ffffff;
  }
}
</style>