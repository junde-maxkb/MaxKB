<template>
  <div class="document-detail">
    <!-- 文档信息头部 -->
    <div class="document-header">
      <div class="document-info">
        <h3>{{ document.name }}</h3>
        <div class="document-meta">
          <Status :status="document.status" :statusMeta="document.meta" />
          <span class="meta-item">
            <el-icon><Document /></el-icon>
            {{ formatNumber(document.char_length || 0) }} 字符
          </span>
          <span class="meta-item">
            <el-icon><Collection /></el-icon>
            {{ document.paragraph_count || 0 }} 段落
          </span>
          <span class="meta-item">
            <el-icon><Clock /></el-icon>
            {{ formatTime(document.create_time) }}
          </span>
        </div>
      </div>
      
      <div class="document-actions">
        <el-button @click="refreshDocument" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          重新处理
        </el-button>
        <el-button @click="openParagraphPage">
          <el-icon><View /></el-icon>
          查看段落
        </el-button>
      </div>
    </div>
    
    <!-- 标签页内容 -->
    <el-tabs v-model="activeTab" class="document-tabs">
      <!-- 段落预览 -->
      <el-tab-pane label="段落预览" name="paragraphs">
        <div class="paragraphs-container" v-loading="paragraphsLoading">
          <div class="paragraphs-header">
            <div class="paragraph-stats">
              总计 {{ paragraphList.length }} 个段落
            </div>
          </div>
          
          <div class="paragraphs-list">
            <div v-if="paragraphList.length === 0" class="empty-paragraphs">
              暂无段落数据
            </div>
            <div
              v-for="(paragraph, index) in paragraphList.slice(0, 10)"
              :key="paragraph.id"
              class="paragraph-item"
            >
              <div class="paragraph-header">
                <span class="paragraph-index">{{ index + 1 }}</span>
                <el-tag v-if="paragraph.is_active" type="success" size="small">启用</el-tag>
                <el-tag v-else type="info" size="small">禁用</el-tag>
              </div>
              <div class="paragraph-content">
                {{ paragraph.content }}
              </div>
              <div class="paragraph-meta">
                <span>字符数: {{ paragraph.char_length || 0 }}</span>
                <span v-if="paragraph.hit_num">命中次数: {{ paragraph.hit_num }}</span>
              </div>
            </div>
            
            <div v-if="paragraphList.length > 10" class="more-paragraphs">
              还有 {{ paragraphList.length - 10 }} 个段落，
              <el-button type="text" @click="openParagraphPage">查看全部</el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- 文档设置 -->
      <el-tab-pane label="文档设置" name="settings">
        <div class="document-settings">
          <el-form :model="documentSettings" label-width="120px">
            <el-form-item label="启用状态">
              <el-switch
                v-model="documentSettings.is_active"
                @change="updateDocumentStatus"
              />
              <span class="setting-tip">禁用后此文档不会参与问答</span>
            </el-form-item>
            
            <el-form-item label="相似度阈值">
              <el-slider
                v-model="documentSettings.similarity_threshold"
                :min="0"
                :max="1"
                :step="0.01"
                show-input
                @change="updateDocumentSettings"
              />
              <span class="setting-tip">设置文档片段的匹配阈值</span>
            </el-form-item>
            
            <el-form-item label="权重设置">
              <el-slider
                v-model="documentSettings.weight"
                :min="0"
                :max="1"
                :step="0.01"
                show-input
                @change="updateDocumentSettings"
              />
              <span class="setting-tip">调整文档在搜索结果中的权重</span>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  Collection,
  Clock,
  Refresh,
  View
} from '@element-plus/icons-vue'
import documentApi from '@/api/document'
import paragraphApi from '@/api/paragraph'
import Status from '@/views/document/component/Status.vue'
import { datetimeFormat } from '@/utils/time'

// Props
interface Props {
  document: any
  datasetId: string
}

const props = defineProps<Props>()

// 响应式数据
const activeTab = ref('paragraphs')
const paragraphsLoading = ref(false)
const refreshing = ref(false)
const paragraphList = ref<any[]>([])

// 文档设置
const documentSettings = reactive({
  is_active: props.document.is_active || true,
  similarity_threshold: 0.7,
  weight: 1.0
})

// 方法
const loadParagraphs = async () => {
  try {
    paragraphsLoading.value = true
    const response = await paragraphApi.getParagraph(
      props.datasetId,
      props.document.id,
      { current_page: 1, page_size: 20 },
      {}
    )
    
    if (response.data) {
      paragraphList.value = response.data.records || []
    }
  } catch (error) {
    console.error('加载段落失败:', error)
    ElMessage.error('加载段落失败')
  } finally {
    paragraphsLoading.value = false
  }
}

const refreshDocument = async () => {
  try {
    refreshing.value = true
    await documentApi.putDocumentRefresh(props.datasetId, props.document.id, [])
    ElMessage.success('重新处理任务已提交')
  } catch (error) {
    console.error('重新处理失败:', error)
    ElMessage.error('重新处理失败')
  } finally {
    refreshing.value = false
  }
}

const openParagraphPage = () => {
  // 在新标签页打开段落详情页面
  window.open(`/dataset/${props.datasetId}/${props.document.id}`, '_blank')
}

const updateDocumentStatus = async () => {
  try {
    await documentApi.putDocument(props.datasetId, props.document.id, {
      is_active: documentSettings.is_active
    })
    ElMessage.success(`文档已${documentSettings.is_active ? '启用' : '禁用'}`)
  } catch (error) {
    console.error('更新文档状态失败:', error)
    ElMessage.error('更新失败')
  }
}

const updateDocumentSettings = async () => {
  try {
    await documentApi.putDocument(props.datasetId, props.document.id, {
      similarity_threshold: documentSettings.similarity_threshold,
      weight: documentSettings.weight
    })
    ElMessage.success('设置已保存')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存失败')
  }
}

// 工具函数
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const formatTime = (time: string) => {
  if (!time) return ''
  return datetimeFormat(time)
}

// 组件挂载
onMounted(() => {
  loadParagraphs()
})
</script>

<style lang="scss" scoped>
.document-detail {
  .document-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 20px 0;
    border-bottom: 1px solid #e4e7ed;
    margin-bottom: 20px;
    
    .document-info {
      flex: 1;
      
      h3 {
        margin: 0 0 12px 0;
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }
      
      .document-meta {
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
        
        .meta-item {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 14px;
          color: #606266;
          
          .el-icon {
            font-size: 16px;
          }
        }
      }
    }
    
    .document-actions {
      display: flex;
      gap: 8px;
      flex-shrink: 0;
    }
  }
  
  .document-tabs {
    :deep(.el-tabs__content) {
      padding-top: 20px;
    }
  }
  
  .paragraphs-container {
    .paragraphs-header {
      margin-bottom: 16px;
      
      .paragraph-stats {
        font-size: 14px;
        color: #606266;
      }
    }
    
    .paragraphs-list {
      .empty-paragraphs {
        text-align: center;
        padding: 40px 0;
        color: #909399;
        font-size: 14px;
      }
      
      .paragraph-item {
        border: 1px solid #e4e7ed;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
        
        .paragraph-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
          
          .paragraph-index {
            background: #f0f2f5;
            color: #606266;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
          }
        }
        
        .paragraph-content {
          font-size: 14px;
          line-height: 1.6;
          color: #303133;
          margin-bottom: 8px;
          max-height: 200px;
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 8;
          -webkit-box-orient: vertical;
        }
        
        .paragraph-meta {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #909399;
        }
      }
      
      .more-paragraphs {
        text-align: center;
        padding: 16px 0;
        color: #606266;
        font-size: 14px;
      }
    }
  }
  
  .document-settings {
    .setting-tip {
      font-size: 12px;
      color: #909399;
      margin-left: 8px;
    }
  }
}
</style>