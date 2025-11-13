<template>
  <div class="chat-history-panel">
    <div class="panel-header border-b p-16-24 flex-between">
      <h4>{{ $t('views.user.chatHistory.title') }} - {{ username }}</h4>
      <div class="flex align-center gap-8">
        <el-button type="primary" text @click="handleRefresh" :loading="loading" :title="$t('common.refresh')">
          <el-icon><Refresh /></el-icon>
        </el-button>
        <el-button type="primary" text @click="handleClose">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>
    <div class="chat-history-content">
      <div class="search-filter-section p-16-24 border-b">
        <div class="search-box mb-12">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索聊天记录标题或内容..."
            clearable
            prefix-icon="Search"
            size="small"
            @input="handleSearch"
          />
        </div>
        <div class="filter-box flex-between">
          <div class="total-info">
            <el-text type="info" size="small">
              {{ $t('common.total') }}: {{ paginationConfig.total }}
              <span v-if="searchKeyword" class="ml-8">
                (搜索到 {{ filteredList.length }} 条记录)
              </span>
            </el-text>
          </div>
        </div>
      </div>
      <div class="history-list-container" v-loading="loading">
        <el-scrollbar>
          <div class="p-8 pt-0">
            <common-list
              :data="displayedList"
              class="mt-8"
              :defaultActive="selectedHistoryId"
              @click="clickHistoryHandle"
              @mouseenter="mouseenter"
              @mouseleave="mouseId = ''"
            >
              <template #default="{ row }">
                <div class="flex-between history-item-wrapper">
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
                  <div class="history-actions" v-if="mouseId === row.id">
                    <el-button
                      type="primary"
                      text
                      size="small"
                      @click.stop="viewDetail(row)"
                      :title="$t('views.user.chatHistory.viewDetail')"
                    >
                      <el-icon><View /></el-icon>
                    </el-button>
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
        <el-pagination
          v-model:current-page="paginationConfig.current_page"
          v-model:page-size="paginationConfig.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="paginationConfig.total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          small
        />
      </div>
    </div>
    
    <!-- 聊天详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="selectedHistory?.title || selectedHistory?.application_name"
      width="70%"
      destroy-on-close
      append-to-body
    >
      <div class="chat-detail-content" v-loading="detailLoading">
        <!-- 聊天详情搜索框 -->
        <div class="detail-search-box mb-12">
          <el-input
            v-model="messageSearchKeyword"
            placeholder="搜索消息内容..."
            clearable
            prefix-icon="Search"
            size="small"
          />
        </div>
        <el-scrollbar height="500px">
          <div class="message-list p-16">
            <div
              v-for="(message, index) in filteredChatMessages"
              :key="index"
              class="message-item mb-16"
              :class="message.role === 'user' ? 'message-user' : 'message-assistant'"
            >
              <div class="message-header mb-8">
                <el-tag :type="message.role === 'user' ? 'primary' : 'success'" size="small">
                  {{ message.role === 'user' ? $t('views.user.chatHistory.user') : $t('views.user.chatHistory.assistant') }}
                </el-tag>
                <span class="message-index ml-8">{{ $t('views.user.chatHistory.messageIndex') }}: {{ message.message_index || index + 1 }}</span>
              </div>
              <div class="message-content">
                <pre class="message-text" v-html="highlightText(message.content, messageSearchKeyword)"></pre>
              </div>
            </div>
            <div v-if="filteredChatMessages.length === 0 && chatMessages.length > 0" class="text-center p-24">
              <el-empty description="没有找到匹配的消息" />
            </div>
            <div v-if="chatMessages.length === 0" class="text-center p-24">
              <el-empty :description="$t('views.user.chatHistory.noMessages')" />
            </div>
          </div>
        </el-scrollbar>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">{{ $t('common.close') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, reactive } from 'vue'
import { Close, Refresh, ChatLineRound, Clock, View } from '@element-plus/icons-vue'
import CommonList from '@/components/common-list/index.vue'
import AutoTooltip from '@/components/auto-tooltip/index.vue'
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

const emit = defineEmits<{
  close: []
}>()

const loading = ref(false)
const detailLoading = ref(false)
const chatHistoryList = ref<any[]>([])
const selectedHistoryId = ref('')
const mouseId = ref('')
const detailDialogVisible = ref(false)
const selectedHistory = ref<any>(null)
const chatMessages = ref<any[]>([])
const searchKeyword = ref('')
const messageSearchKeyword = ref('')

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

// 高亮文本函数
function highlightText(text: string, keyword: string) {
  if (!keyword || !keyword.trim()) {
    return escapeHtml(text)
  }

  const escapedText = escapeHtml(text)
  const escapedKeyword = escapeHtml(keyword.trim())
  const regex = new RegExp(`(${escapedKeyword})`, 'gi')
  return escapedText.replace(regex, '<mark style="background-color: #ffeb3b; padding: 2px 4px; border-radius: 2px;">$1</mark>')
}

// HTML转义函数
function escapeHtml(text: string) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// 过滤聊天消息
const filteredChatMessages = computed(() => {
  if (!messageSearchKeyword.value.trim()) {
    return chatMessages.value
  }

  const keyword = messageSearchKeyword.value.trim().toLowerCase()
  return chatMessages.value.filter(msg => {
    return msg.content.toLowerCase().includes(keyword)
  })
})

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

function handleClose() {
  emit('close')
  closeHandle()
}

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
  messageSearchKeyword.value = '' // 重置消息搜索关键词

  try {
    const res = await userApi.getChatMessages(item.id)
    if (res.code === 200) {
      chatMessages.value = res.data || []
      // 按 message_index 排序
      chatMessages.value.sort((a: any, b: any) => {
        return (a.message_index || 0) - (b.message_index || 0)
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
.chat-history-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--app-layout-bg-color);
  overflow: hidden;
}

.panel-header {
  background: #ffffff;
  flex-shrink: 0;
  
  h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 500;
    color: var(--el-text-color-primary);
  }
}

.border-b {
  border-bottom: 1px solid var(--el-border-color);
}

.border-t {
  border-top: 1px solid var(--el-border-color);
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
  background: #fafafa;
  
  .search-box {
    margin-bottom: 12px;
  }

  .filter-box {
    justify-content: flex-end;
    
    .total-info {
      display: flex;
      align-items: center;
    }
  }
}

.history-list-container {
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.history-item-wrapper {
  width: 100%;
  padding: 4px 0;
  
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
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  flex-wrap: wrap;
  
  .application-tag {
    margin-right: 0;
  }
  
  .message-count,
  .create-time {
    display: flex;
    align-items: center;
    color: var(--el-text-color-secondary);
    
    .el-icon {
      font-size: 14px;
    }
  }
  
  .create-time {
    color: var(--el-text-color-placeholder);
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
  background: #ffffff;
  display: flex;
  justify-content: flex-end;
}

// 聊天详情对话框样式
.chat-detail-content {
  .detail-search-box {
    padding: 0 16px;
    margin-bottom: 12px;
  }

  .message-list {
    .message-item {
      padding: 12px;
      border-radius: 8px;
      background: var(--el-bg-color-page);
      border: 1px solid var(--el-border-color-lighter);
      
      &.message-user {
        background: var(--el-color-primary-light-9);
        border-color: var(--el-color-primary-light-7);
      }
      
      &.message-assistant {
        background: var(--el-color-success-light-9);
        border-color: var(--el-color-success-light-7);
      }
      
      .message-header {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        
        .message-index {
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
      }
      
      .message-content {
        .message-text {
          margin: 0;
          font-size: 14px;
          line-height: 1.6;
          color: var(--el-text-color-primary);
          white-space: pre-wrap;
          word-wrap: break-word;
          font-family: inherit;

          :deep(mark) {
            background-color: #ffeb3b;
            padding: 2px 4px;
            border-radius: 2px;
            font-weight: 500;
          }
        }
      }
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

