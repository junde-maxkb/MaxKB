<template>
  <el-drawer v-model="visible" size="50%" @close="closeHandle" class="chat-history-drawer">
    <template #header>
      <h4>{{ $t('views.user.chatHistory.title') }} - {{ username }}</h4>
    </template>
    <div class="chat-history-content" v-loading="loading">
      <div class="p-24 pb-0">
        <p class="mb-8">{{ $t('views.user.chatHistory.history') }}</p>
      </div>
      <div class="history-list-container">
        <el-scrollbar>
          <div class="p-8 pt-0">
            <common-list
              :data="chatHistoryList"
              class="mt-8"
              :defaultActive="selectedHistoryId"
              @click="clickHistoryHandle"
              @mouseenter="mouseenter"
              @mouseleave="mouseId = ''"
            >
              <template #default="{ row }">
                <div class="flex-between">
                  <div class="history-item-content">
                    <div class="history-title">
                      <auto-tooltip :content="row.title || row.application_name">
                        {{ row.title || row.application_name }}
                      </auto-tooltip>
                    </div>
                    <div class="history-meta">
                      <span class="application-name">{{ row.application_name }}</span>
                      <span class="message-count">{{ row.message_count }} {{ $t('views.user.chatHistory.messages') }}</span>
                      <span class="create-time">{{ datetimeFormat(row.create_time) }}</span>
                    </div>
                  </div>
                </div>
              </template>
              <template #empty>
                <div class="text-center p-24">
                  <el-text type="info">{{ $t('views.user.chatHistory.noHistory') }}</el-text>
                </div>
              </template>
            </common-list>
          </div>
        </el-scrollbar>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import CommonList from '@/components/common-list/index.vue'
import AutoTooltip from '@/components/auto-tooltip/index.vue'
import userApi from '@/api/user-manage'
import { datetimeFormat } from '@/utils/time'

defineOptions({ name: 'ChatHistoryDrawer' })

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

const visible = ref(false)
const loading = ref(false)
const chatHistoryList = ref<any[]>([])
const selectedHistoryId = ref('')
const mouseId = ref('')

function closeHandle() {
  chatHistoryList.value = []
  selectedHistoryId.value = ''
  mouseId.value = ''
}

function getChatHistory() {
  if (!props.userId) return
  loading.value = true
  userApi
    .getChatHistory(props.userId, loading)
    .then((res: any) => {
      if (res.code === 200) {
        chatHistoryList.value = res.data || []
      }
    })
    .finally(() => {
      loading.value = false
    })
}

function clickHistoryHandle(item: any) {
  selectedHistoryId.value = item.id
  // 可以在这里添加点击历史记录后的操作，比如查看详细聊天内容
}

function mouseenter(item: any) {
  mouseId.value = item.id
}

watch(
  () => props.userId,
  (newVal) => {
    if (newVal && visible.value) {
      getChatHistory()
    }
  }
)

watch(visible, (bool) => {
  if (bool && props.userId) {
    getChatHistory()
  } else {
    closeHandle()
  }
})

const open = () => {
  visible.value = true
}

defineExpose({
  open
})
</script>

<style lang="scss" scoped>
.chat-history-drawer {
  :deep(.el-drawer__body) {
    background: var(--app-layout-bg-color);
    padding: 0;
    display: flex;
    flex-direction: column;
    height: calc(100% - 60px);
  }
}

.chat-history-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-list-container {
  flex: 1;
  overflow: hidden;
}

.history-item-content {
  flex: 1;
  min-width: 0;
}

.history-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);

  .application-name {
    color: var(--el-color-primary);
  }

  .message-count {
    color: var(--el-text-color-regular);
  }

  .create-time {
    color: var(--el-text-color-placeholder);
  }
}
</style>

