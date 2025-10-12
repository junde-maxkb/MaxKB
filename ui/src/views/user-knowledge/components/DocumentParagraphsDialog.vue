<template>
  <el-dialog
    v-model="visible"
    :title="`${documentName} - 分段内容`"
    width="80%"
    :before-close="handleClose"
    class="document-paragraphs-dialog"
  >
    <div class="dialog-content" v-loading="loading">
      <!-- 文档信息头部 -->
      <div class="document-header">
        <div class="document-info">
          <h4>{{ documentName }}</h4>
          <div class="document-meta">
            <span class="meta-item">
              <el-icon><Collection /></el-icon>
              {{ paragraphList.length }} 个分段
            </span>
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ formatTime(new Date()) }}
            </span>
          </div>
        </div>
      </div>

      <!-- 分段列表 -->
      <div class="paragraphs-container">
        <div class="paragraphs-header">
          <div class="paragraph-stats">
            总计 {{ paragraphList.length }} 个分段
          </div>
          <div class="search-box">
            <el-input
              v-model="searchText"
              placeholder="搜索分段内容..."
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
        
        <div class="paragraphs-list">
          <div v-if="filteredParagraphs.length === 0" class="empty-paragraphs">
            <el-empty description="暂无分段数据" />
          </div>
          <div
            v-for="(paragraph, index) in filteredParagraphs"
            :key="paragraph.id"
            class="paragraph-item"
          >
            <div class="paragraph-header">
              <span class="paragraph-index">{{ index + 1 }}</span>
              <div class="paragraph-status">
                <el-tag v-if="paragraph.is_active" type="success" size="small">启用</el-tag>
                <el-tag v-else type="info" size="small">禁用</el-tag>
                <span v-if="paragraph.hit_num" class="hit-count">
                  命中 {{ paragraph.hit_num }} 次
                </span>
              </div>
            </div>
            <div class="paragraph-content">
              {{ paragraph.content }}
            </div>
            <div class="paragraph-meta">
              <span>字符数: {{ paragraph.char_length || 0 }}</span>
              <span v-if="paragraph.title">标题: {{ paragraph.title }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Collection, Clock } from '@element-plus/icons-vue'
import paragraphApi from '@/api/paragraph'

interface Paragraph {
  id: string
  content: string
  title?: string
  is_active: boolean
  char_length?: number
  hit_num?: number
  create_time?: string
  update_time?: string
}

interface Props {
  modelValue: boolean
  documentId: string
  datasetId: string
  documentName: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// 格式化时间
const formatTime = (timestamp?: Date) => {
  if (!timestamp) return ''
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(timestamp)
}

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)
const paragraphList = ref<Paragraph[]>([])
const searchText = ref('')

// 过滤后的分段列表
const filteredParagraphs = computed(() => {
  if (!searchText.value) {
    return paragraphList.value
  }
  return paragraphList.value.filter(paragraph => 
    paragraph.content.toLowerCase().includes(searchText.value.toLowerCase()) ||
    (paragraph.title && paragraph.title.toLowerCase().includes(searchText.value.toLowerCase()))
  )
})

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
}

// 获取分段数据
const fetchParagraphs = async () => {
  console.log('fetchParagraphs 调用参数:', {
    documentId: props.documentId,
    datasetId: props.datasetId
  })
  
  if (!props.documentId || !props.datasetId) {
    console.error('缺少必要参数:', {
      documentId: props.documentId,
      datasetId: props.datasetId
    })
    return
  }

  loading.value = true
  try {
    console.log('调用 paragraphApi.getParagraph...')
    const response = await paragraphApi.getParagraph(
      props.datasetId,
      props.documentId,
      { current_page: 1, page_size: 1000 },
      {}
    )
    
    console.log('API响应:', response)
    
    if (response.data && response.data.records) {
      paragraphList.value = response.data.records
      console.log('获取到分段数据:', paragraphList.value.length, '条')
    } else {
      console.log('响应数据格式异常:', response)
      paragraphList.value = []
    }
  } catch (error) {
    console.error('获取分段数据失败:', error)
    ElMessage.error('获取分段数据失败')
    paragraphList.value = []
  } finally {
    loading.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  searchText.value = ''
  paragraphList.value = []
}

// 监听对话框显示状态
watch(visible, (newVal) => {
  if (newVal) {
    fetchParagraphs()
  }
})
</script>

<style scoped lang="scss">
.document-paragraphs-dialog {
  .dialog-content {
    max-height: 70vh;
    overflow-y: auto;
  }

  .document-header {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #e9ecef;

    .document-info {
      h4 {
        margin: 0 0 10px 0;
        color: #303133;
        font-size: 18px;
        font-weight: 600;
      }

      .document-meta {
        display: flex;
        gap: 20px;
        font-size: 14px;
        color: #606266;

        .meta-item {
          display: flex;
          align-items: center;
          gap: 4px;

          .el-icon {
            font-size: 16px;
          }
        }
      }
    }
  }

  .paragraphs-container {
    .paragraphs-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      gap: 20px;

      .paragraph-stats {
        font-size: 14px;
        color: #606266;
        font-weight: 500;
      }

      .search-box {
        width: 300px;
      }
    }

    .paragraphs-list {
      .empty-paragraphs {
        text-align: center;
        padding: 40px 0;
      }

      .paragraph-item {
        background: #f8fafc;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;

        &:hover {
          border-color: #3370ff;
          box-shadow: 0 2px 8px rgba(51, 112, 255, 0.1);
        }

        &:last-child {
          margin-bottom: 0;
        }

        .paragraph-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;

          .paragraph-index {
            background: #3370ff;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            min-width: 24px;
            text-align: center;
          }

          .paragraph-status {
            display: flex;
            align-items: center;
            gap: 8px;

            .hit-count {
              font-size: 12px;
              color: #909399;
            }
          }
        }

        .paragraph-content {
          font-size: 14px;
          line-height: 1.6;
          color: #303133;
          margin-bottom: 12px;
          word-break: break-word;
        }

        .paragraph-meta {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #909399;

          span {
            background: #f5f7fa;
            padding: 2px 6px;
            border-radius: 3px;
          }
        }
      }
    }
  }
}

.dialog-footer {
  text-align: right;
}
</style>
