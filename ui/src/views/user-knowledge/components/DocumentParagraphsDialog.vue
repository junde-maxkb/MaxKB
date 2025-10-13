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
          <div class="header-actions">
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
        </div>
        
        <div class="paragraphs-list">
          <div v-if="filteredParagraphs.length === 0" class="empty-paragraphs">
            <el-empty description="暂无分段数据" />
          </div>
          <div
            v-for="(paragraph, index) in filteredParagraphs"
            :key="paragraph.id"
            class="paragraph-item"
            :class="{ 'hit-paragraph': paragraph.id === matchedParagraphId }"
            :data-paragraph-id="paragraph.id"
            :data-hit-id="props.hitParagraphId"
          >
            <div class="paragraph-header">
              <span class="paragraph-index">{{ index + 1 }}</span>
              <div class="paragraph-status">
                <el-tag v-if="paragraph.is_active" type="success" size="small">启用</el-tag>
                <el-tag v-else type="info" size="small">禁用</el-tag>
                <span v-if="paragraph.hit_num" class="hit-count">
                  命中 {{ paragraph.hit_num }} 次
                </span>
                <span v-if="paragraph.id === matchedParagraphId" class="debug-info" style="color: red; font-size: 12px;">
                  [命中分段]
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
import { ref, computed, watch, nextTick } from 'vue'
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
  hitParagraphId?: string
  hitParagraphContent?: string
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
const matchedParagraphId = ref<string>('')

// 过滤后的分段列表
const filteredParagraphs = computed(() => {
  let filtered = paragraphList.value
  
  // 搜索过滤
  if (searchText.value) {
    filtered = filtered.filter(paragraph => 
      paragraph.content.toLowerCase().includes(searchText.value.toLowerCase()) ||
      (paragraph.title && paragraph.title.toLowerCase().includes(searchText.value.toLowerCase()))
    )
  }
  
  // 默认按照段落数字顺序排序
  filtered = [...filtered].sort((a, b) => {
    // 提取段落标题中的数字进行排序
    const getParagraphNumber = (title: string) => {
      const match = title.match(/段落\s*(\d+)/)
      return match ? parseInt(match[1], 10) : 0
    }
    
    const numA = getParagraphNumber(a.title || '')
    const numB = getParagraphNumber(b.title || '')
    
    return numA - numB
  })
  
  return filtered
})

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
}

// 通过内容匹配找到分段ID
const findParagraphByContent = (searchContent: string): string | null => {
  if (!searchContent || !paragraphList.value.length) {
    return null
  }
  
  console.log('开始内容匹配，搜索内容长度:', searchContent.length)
  console.log('分段数量:', paragraphList.value.length)
  
  // 清理搜索内容，移除多余的空白字符
  const cleanSearchContent = searchContent.replace(/\s+/g, ' ').trim()
  
  // 尝试精确匹配
  for (const paragraph of paragraphList.value) {
    const cleanParagraphContent = paragraph.content.replace(/\s+/g, ' ').trim()
    if (cleanParagraphContent === cleanSearchContent) {
      console.log('精确匹配成功:', paragraph.id)
      return paragraph.id
    }
  }
  
  // 尝试包含匹配（搜索内容包含在分段内容中）
  for (const paragraph of paragraphList.value) {
    const cleanParagraphContent = paragraph.content.replace(/\s+/g, ' ').trim()
    if (cleanParagraphContent.includes(cleanSearchContent)) {
      console.log('包含匹配成功:', paragraph.id)
      return paragraph.id
    }
  }
  
  // 尝试部分匹配（分段内容包含在搜索内容中）
  for (const paragraph of paragraphList.value) {
    const cleanParagraphContent = paragraph.content.replace(/\s+/g, ' ').trim()
    if (cleanSearchContent.includes(cleanParagraphContent)) {
      console.log('部分匹配成功:', paragraph.id)
      return paragraph.id
    }
  }
  
  // 尝试相似度匹配（简单的字符相似度）
  let bestMatch = null
  let bestSimilarity = 0
  
  for (const paragraph of paragraphList.value) {
    const cleanParagraphContent = paragraph.content.replace(/\s+/g, ' ').trim()
    const similarity = calculateSimilarity(cleanSearchContent, cleanParagraphContent)
    
    if (similarity > bestSimilarity && similarity > 0.7) { // 相似度阈值
      bestSimilarity = similarity
      bestMatch = paragraph.id
    }
  }
  
  if (bestMatch) {
    console.log('相似度匹配成功:', bestMatch, '相似度:', bestSimilarity)
    return bestMatch
  }
  
  console.log('未找到匹配的分段')
  return null
}

// 计算字符串相似度（简单的Jaccard相似度）
const calculateSimilarity = (str1: string, str2: string): number => {
  const set1 = new Set(str1.split(''))
  const set2 = new Set(str2.split(''))
  
  const intersection = new Set([...set1].filter(x => set2.has(x)))
  const union = new Set([...set1, ...set2])
  
  return intersection.size / union.size
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
      console.log('当前命中分段ID:', props.hitParagraphId)
      console.log('分段ID列表:', paragraphList.value.map(p => p.id))
      
      // 通过内容匹配找到正确的分段ID
      if (props.hitParagraphContent) {
        const matchedId = findParagraphByContent(props.hitParagraphContent)
        if (matchedId) {
          matchedParagraphId.value = matchedId
          console.log('通过内容匹配找到分段ID:', matchedId)
        } else {
          console.log('未找到匹配的分段，搜索内容:', props.hitParagraphContent.substring(0, 100) + '...')
        }
      }
      
      // 数据加载完成后，检查并滚动到命中分段
      if (matchedParagraphId.value) {
        nextTick(() => {
          const hitElement = document.querySelector('.hit-paragraph')
          console.log('数据加载后查找命中元素:', hitElement)
          if (hitElement) {
            hitElement.scrollIntoView({ 
              behavior: 'smooth', 
              block: 'center' 
            })
          }
        })
      }
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
  matchedParagraphId.value = ''
}

// 监听对话框显示状态
watch(visible, (newVal) => {
  if (newVal) {
    fetchParagraphs()
  }
})

// 监听命中分段内容变化，重新匹配分段
watch(() => props.hitParagraphContent, (newContent) => {
  console.log('hitParagraphContent changed:', newContent ? newContent.substring(0, 100) + '...' : 'null')
  if (newContent && visible.value && paragraphList.value.length > 0) {
    const matchedId = findParagraphByContent(newContent)
    if (matchedId) {
      matchedParagraphId.value = matchedId
      console.log('重新匹配到分段ID:', matchedId)
      
      nextTick(() => {
        const hitElement = document.querySelector('.hit-paragraph')
        console.log('Found hit element:', hitElement)
        if (hitElement) {
          hitElement.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
          })
        }
      })
    }
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

      .header-actions {
        display: flex;
        align-items: center;
        gap: 16px;

        .sort-buttons {
          .el-button-group {
            .el-button {
              font-size: 12px;
              padding: 6px 12px;
            }
          }
        }

        .search-box {
          width: 300px;
        }
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

        &.hit-paragraph {
          border-color: #f56c6c;
          background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%);
          box-shadow: 0 4px 12px rgba(245, 108, 108, 0.2);
          position: relative;

          &::before {
            content: '命中分段';
            position: absolute;
            top: -1px;
            right: -1px;
            background: #f56c6c;
            color: white;
            padding: 2px 8px;
            border-radius: 0 8px 0 8px;
            font-size: 10px;
            font-weight: 600;
            z-index: 1;
          }

          .paragraph-index {
            background: #f56c6c;
            color: white;
          }
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
