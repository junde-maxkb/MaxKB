<template>
  <div class="document-management">
    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="left-actions">
        <el-button type="primary" @click="openUploadDialog">
          <el-icon><Upload /></el-icon>
          上传文档
        </el-button>
        <el-button @click="batchRefresh" :disabled="multipleSelection.length === 0">
          <el-icon><Refresh /></el-icon>
          向量化
        </el-button>
        <el-button @click="batchGenerateQuestions" :disabled="multipleSelection.length === 0">
          <el-icon><QuestionFilled /></el-icon>
          生成智能标签
        </el-button>
        <el-button @click="batchMigrateDocuments" :disabled="multipleSelection.length === 0">
          <el-icon><Operation /></el-icon>
          迁移到其他知识库
        </el-button>
        <el-button @click="batchExportZip" :disabled="multipleSelection.length === 0">
          <el-icon><Download /></el-icon>
          导出ZIP
        </el-button>
        <el-button @click="deleteMulDocument" :disabled="multipleSelection.length === 0">
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
      </div>
      
      <div class="right-actions">
        <el-input
          v-model="filterText"
          placeholder="搜索文档..."
          prefix-icon="Search"
          class="search-input"
          @change="getList"
          clearable
        />
      </div>
    </div>
    
    <!-- 文档表格 -->
    <div class="document-table">
      <app-table
        ref="multipleTableRef"
        :data="documentData"
        :pagination-config="paginationConfig"
        :quick-create="false"
        @sizeChange="handleSizeChange"
        @changePage="getList"
        @cell-mouse-enter="cellMouseEnter"
        @cell-mouse-leave="cellMouseLeave"
        @row-click="rowClickHandle"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
        v-loading="loading"
        :row-key="(row: any) => row.id"
        :storeKey="storeKey"
      >
        <el-table-column type="selection" width="55" :reserve-selection="true" />
        <el-table-column prop="name" label="文档名称" min-width="280">
          <template #default="{ row }">
            <ReadWrite
              @change="editName($event, row.id)"
              :data="row.name"
              :showEditIcon="row.id === currentMouseId"
            />
          </template>
        </el-table-column>
        <el-table-column
          prop="char_length"
          label="字符数"
          align="right"
          min-width="90"
          sortable
        >
          <template #default="{ row }">
            {{ numberFormat(row.char_length) }}
          </template>
        </el-table-column>
        <el-table-column
          prop="paragraph_count"
          label="段落数"
          align="right"
          min-width="90"
          sortable
        />
        <el-table-column prop="status" label="状态" width="130">
          <template #header>
            <div>
              <span>状态</span>
              <el-dropdown trigger="click" @command="dropdownHandle">
                <el-button
                  style="margin-top: 1px"
                  link
                  :type="filterMethod['status'] ? 'primary' : ''"
                >
                  <el-icon>
                    <Filter />
                  </el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu style="width: 100px">
                    <el-dropdown-item
                      :class="filterMethod['status'] ? '' : 'is-active'"
                      :command="beforeCommand('status', '')"
                      class="justify-center"
                      >全部
                    </el-dropdown-item>
                    <el-dropdown-item
                      :class="filterMethod['status'] === State.SUCCESS ? 'is-active' : ''"
                      class="justify-center"
                      :command="beforeCommand('status', State.SUCCESS)"
                      >成功
                    </el-dropdown-item>
                    <el-dropdown-item
                      :class="filterMethod['status'] === State.FAILURE ? 'is-active' : ''"
                      class="justify-center"
                      :command="beforeCommand('status', State.FAILURE)"
                      >失败
                    </el-dropdown-item>
                    <el-dropdown-item
                      :class="
                        filterMethod['status'] === State.STARTED &&
                        filterMethod['task_type'] == TaskType.EMBEDDING
                          ? 'is-active'
                          : ''
                      "
                      class="justify-center"
                      :command="beforeCommand('status', State.STARTED, TaskType.EMBEDDING)"
                      >向量化中
                    </el-dropdown-item>
                    <el-dropdown-item
                      :class="filterMethod['status'] === State.PENDING ? 'is-active' : ''"
                      class="justify-center"
                      :command="beforeCommand('status', State.PENDING)"
                      >等待中
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
          <template #default="{ row }">
            <StatusVlue :status="row.status" :status-meta="row.status_meta"></StatusVlue>
          </template>
        </el-table-column>
        <el-table-column width="130">
          <template #header>
            <div>
              <span>启用状态</span>
              <el-dropdown trigger="click" @command="dropdownHandle">
                <el-button
                  style="margin-top: 1px"
                  link
                  :type="filterMethod['is_active'] ? 'primary' : ''"
                >
                  <el-icon>
                    <Filter />
                  </el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu style="width: 100px">
                    <el-dropdown-item
                      :class="filterMethod['is_active'] === '' ? 'is-active' : ''"
                      :command="beforeCommand('is_active', '')"
                      class="justify-center"
                      >全部
                    </el-dropdown-item>
                    <el-dropdown-item
                      :class="filterMethod['is_active'] === true ? 'is-active' : ''"
                      class="justify-center"
                      :command="beforeCommand('is_active', true)"
                      >启用
                    </el-dropdown-item>
                    <el-dropdown-item
                      :class="filterMethod['is_active'] === false ? 'is-active' : ''"
                      class="justify-center"
                      :command="beforeCommand('is_active', false)"
                      >禁用
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
          <template #default="{ row }">
            <div @click.stop>
              <el-switch
                :loading="switchLoading"
                size="small"
                v-model="row.is_active"
                :before-change="() => changeState(row)"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column width="170" v-if="false">
          <template #header>
            <div>
              <span>命中处理</span>
              <el-dropdown trigger="click" @command="dropdownHandle">
                <el-button
                  style="margin-top: 1px"
                  link
                  :type="filterMethod['hit_handling_method'] ? 'primary' : ''"
                >
                  <el-icon>
                    <Filter />
                  </el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu style="width: 150px">
                    <el-dropdown-item
                      :class="filterMethod['hit_handling_method'] ? '' : 'is-active'"
                      :command="beforeCommand('hit_handling_method', '')"
                      class="justify-center"
                      >全部
                    </el-dropdown-item>
                    <template v-for="(value, key) of hitHandlingMethodText" :key="key">
                      <el-dropdown-item
                        :class="filterMethod['hit_handling_method'] === key ? 'is-active' : ''"
                        class="justify-center"
                        :command="beforeCommand('hit_handling_method', key)"
                        >{{ hitHandlingMethodText[key] }}
                      </el-dropdown-item>
                    </template>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
          <template #default="{ row }">
            {{ hitHandlingMethodText[row.hit_handling_method] || row.hit_handling_method }}
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="175" sortable>
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column
          prop="update_time"
          label="更新时间"
          width="175"
          sortable
        >
          <template #default="{ row }">
            {{ datetimeFormat(row.update_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" align="left" width="110" fixed="right" v-if="false">
          <template #default="{ row }">
            <div>
              <span class="mr-4">
                <el-tooltip
                  effect="dark"
                  v-if="
                    ([State.STARTED, State.PENDING] as Array<string>).includes(
                      getTaskState(row.status, TaskType.EMBEDDING)
                    )
                  "
                  content="取消向量化"
                  placement="top"
                >
                  <el-button
                    type="primary"
                    text
                    @click.stop="cancelTask(row, TaskType.EMBEDDING)"
                  >
                    <AppIcon iconName="app-close" style="font-size: 16px"></AppIcon>
                  </el-button>
                </el-tooltip>
                <el-tooltip
                  v-else
                  effect="dark"
                  content="向量化"
                  placement="top"
                >
                  <el-button type="primary" text @click.stop="refreshDocument(row)">
                    <AppIcon iconName="app-document-refresh" style="font-size: 16px"></AppIcon>
                  </el-button>
                </el-tooltip>
              </span>
              <!-- 设置按钮已隐藏 -->
              <span @click.stop>
                <el-dropdown trigger="click">
                  <el-button text type="primary">
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="refreshDocument(row)">
                        <el-icon><Refresh /></el-icon>
                        向量化
                      </el-dropdown-item>
                      <el-dropdown-item @click="migrateDocument(row)">
                        <el-icon><Operation /></el-icon>
                        迁移到其他知识库
                      </el-dropdown-item>
                      <el-dropdown-item @click="exportDocumentZip(row)">
                        <AppIcon iconName="app-export"></AppIcon>
                        导出 Zip
                      </el-dropdown-item>
                      <el-dropdown-item @click="deleteDocument(row)">
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </span>
            </div>
          </template>
        </el-table-column>
      </app-table>
    </div>
    
    <!-- 上传文档对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文档"
      width="90%"
      top="3vh"
      :close-on-click-modal="false"
      class="upload-dialog"
    >
      <div class="upload-document-container">
        <UploadComponent 
          ref="UploadComponentRef"
          v-if="showUploadDialog"
          :dataset-id="datasetId"
          @upload-success="handleUploadSuccess"
        />
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeUploadDialog" :disabled="uploading">
            取消
          </el-button>
          <el-button
            @click="handleUpload"
            type="primary"
            :disabled="!UploadComponentRef?.form?.fileList?.length"
            :loading="uploading"
          >
            {{ uploading ? (getUploadingText()) : '开始上传' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 文档迁移对话框 -->
    <SelectDatasetDialog 
      ref="SelectDatasetDialogRef" 
      :current-dataset-id="datasetId"
      @refresh="handleMigrationSuccess" 
    />
    
    <!-- 生成智能标签对话框 -->
    <GenerateRelatedDialog 
      ref="GenerateRelatedDialogRef" 
      @refresh="getList" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, nextTick, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Upload,
  Filter,
  MoreFilled,
  Refresh,
  Delete,
  QuestionFilled,
  Operation,
  Download
} from '@element-plus/icons-vue'
import documentApi from '@/api/document'
import UploadComponent from './UploadComponent.vue'
import StatusVlue from '@/views/document/component/Status.vue'
import ReadWrite from '@/components/read-write/index.vue'
import AppIcon from '@/components/icons/AppIcon.vue'
import SelectDatasetDialog from './SelectDatasetDialog.vue'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import { datetimeFormat } from '@/utils/time'
import { numberFormat } from '@/utils/utils'
import { MsgConfirm } from '@/utils/message'
import { TaskType, State } from '@/utils/status'
import useStore from '@/stores'
import datasetApi from '@/api/dataset'

// Props
interface Props {
  datasetId: string
  datasetName: string
}

const props = defineProps<Props>()

// 定义发射的事件
const emit = defineEmits<{
  documentChanged: []
}>()

// Store
const { user } = useStore()
const storeKey = 'user_documents'

// 响应式数据
const loading = ref(false)
const switchLoading = ref(false)
const filterText = ref('')
const documentData = ref<any[]>([])
const multipleSelection = ref<any[]>([])
const showUploadDialog = ref(false)
const currentMouseId = ref('')
const multipleTableRef = ref()
const UploadComponentRef = ref()
const SelectDatasetDialogRef = ref()
const GenerateRelatedDialogRef = ref()
const uploading = ref(false)

// 分页配置
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

// 过滤方法
const filterMethod = ref<any>({})

// 计算属性
const hitHandlingMethodText = computed(() => ({
  'directly_return': '直接返回',
  'optimization': '优化后返回'
} as Record<string, string>))

// 获取上传中的文本
const getUploadingText = () => {
  const fileType = UploadComponentRef.value?.form?.fileType
  if (fileType === 'txt') {
    return '智能分段中...'
  } else if (fileType === 'QA') {
    return '上传问答对中...'
  } else if (fileType === 'table') {
    return '上传表格中...'
  } else if (fileType === 'audio') {
    return '音频转文字中...'
  }
  return '上传中...'
}

// 工具函数
const getTaskState = (status: string, taskType: number) => {
  const statusList = status.split('').reverse()
  return taskType - 1 > statusList.length + 1 ? 'n' : statusList[taskType - 1]
}

// 方法
const getList = async (isPolling = false) => {
  try {
    // 只有非轮询时才显示loading状态
    if (!isPolling) {
      loading.value = true
    }
    const params = {
      ...(filterText.value && { name: filterText.value }),
      current_page: paginationConfig.current_page,
      page_size: paginationConfig.page_size,
      ...filterMethod.value
    }
    
    const response = await documentApi.getDocument(
      props.datasetId,
      paginationConfig as any,
      params,
      isPolling ? undefined : (loading as any)
    )

    if (response.data) {
      documentData.value = response.data.records || []
      paginationConfig.total = response.data.total || 0
    }
  } catch (error) {
    // 轮询时的错误不显示给用户，避免频繁弹窗
    if (!isPolling) {
      console.error('加载文档失败:', error)
      ElMessage.error('加载文档失败')
    }
  } finally {
    // 只有非轮询时才重置loading状态
    if (!isPolling) {
      loading.value = false
    }
  }
}

const handleSelectionChange = (selection: any[]) => {
  multipleSelection.value = selection
}

const handleSizeChange = (size: number) => {
  paginationConfig.page_size = size
  paginationConfig.current_page = 1
  getList()
}

const cellMouseEnter = (row: any) => {
  currentMouseId.value = row.id
}

const cellMouseLeave = () => {
  currentMouseId.value = ''
}

const editName = async (name: string, id: string) => {
  try {
    await documentApi.putDocument(props.datasetId, id, { name })
    ElMessage.success('文档名称修改成功')
    await getList()
  } catch (error) {
    console.error('修改文档名称失败:', error)
    ElMessage.error('修改失败')
  }
}

const rowClickHandle = (row: any) => {
  console.log('行点击:', row)
}

const handleSortChange = (sort: any) => {
  console.log('排序变化:', sort)
}

const beforeCommand = (type: string, value: any, taskType?: number) => {
  return { type, value, taskType }
}

const dropdownHandle = (command: any) => {
  const { type, value, taskType } = command
  if (type === 'status' && taskType) {
    filterMethod.value[type] = value
    filterMethod.value['task_type'] = taskType
  } else {
    filterMethod.value[type] = value
  }
  getList()
}

const changeState = async (row: any) => {
  try {
    switchLoading.value = true
    await documentApi.putDocument(props.datasetId, row.id, {
      is_active: !row.is_active
    })
    ElMessage.success(`文档已${!row.is_active ? '启用' : '禁用'}`)
    // 通知父组件文档发生变化
    emit('documentChanged')
    return true
  } catch (error) {
    console.error('切换文档状态失败:', error)
    ElMessage.error('操作失败')
    return false
  } finally {
    switchLoading.value = false
  }
}

const refreshDocument = async (row: any) => {
  try {
    await documentApi.putDocumentRefresh(props.datasetId, row.id, [])
    ElMessage.success('向量化任务已提交')
    await getList()
  } catch (error) {
    console.error('向量化失败:', error)
    ElMessage.error('向量化失败')
  }
}

// settingDoc 函数已移除（功能已隐藏）

const deleteDocument = async (row: any) => {
  try {
    // 获取知识库详情，检查是否是知识库所有者
    const response = await datasetApi.getDatasetDetail(props.datasetId)
    console.log('知识库详情:', response.data)
    console.log('当前用户:', user.userInfo)
    
    // 检查是否是个人知识库
    if (response.data && String(response.data.user_id) === String(user.userInfo?.id)) {
      await MsgConfirm(`确定要删除文档"${row.name}"吗？此操作不可恢复。`, '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      await documentApi.delDocument(props.datasetId, row.id)
      ElMessage.success('文档删除成功')
      await getList()
      // 通知父组件文档发生变化
      emit('documentChanged')
    } else {
      ElMessage.error('您不能删除非个人知识库中的文档')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

const batchRefresh = async () => {
  if (multipleSelection.value.length === 0) return
  
  try {
    const ids = multipleSelection.value.map(doc => doc.id)
    await documentApi.batchRefresh(props.datasetId, ids, [])
    ElMessage.success('批量向量化任务已提交')
    await getList()
  } catch (error) {
    console.error('批量向量化失败:', error)
    ElMessage.error('批量向量化失败')
  }
}

const deleteMulDocument = async () => {
  if (multipleSelection.value.length === 0) return
  
  try {
    // 获取知识库详情，检查是否是知识库所有者
    const response = await datasetApi.getDatasetDetail(props.datasetId)
    console.log('知识库详情:', response.data)
    console.log('当前用户:', user.userInfo)
    
    // 检查是否是个人知识库
    if (response.data && String(response.data.user_id) === String(user.userInfo?.id)) {
      await MsgConfirm(`确定要删除选中的 ${multipleSelection.value.length} 个文档吗？此操作不可恢复。`, '批量删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      const ids = multipleSelection.value.map(doc => doc.id)
      await documentApi.delMulDocument(props.datasetId, ids)
      ElMessage.success('批量删除成功')
      multipleSelection.value = []
      await getList()
      // 通知父组件文档发生变化
      emit('documentChanged')
    } else {
      ElMessage.error('您不能删除非个人知识库中的文档')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}


// 批量生成智能标签
const batchGenerateQuestions = () => {
  if (multipleSelection.value.length === 0) return
  
  // 获取选中文档的ID列表
  const documentIds = multipleSelection.value.map(doc => doc.id)
  
  // 生成智能标签操作日志
  console.log('正在为', documentIds.length, '个文档生成智能标签，知识库ID:', props.datasetId)
  
  // 打开生成智能标签对话框
  GenerateRelatedDialogRef.value.open(documentIds, 'document', props.datasetId)
}

// 批量迁移文档
const batchMigrateDocuments = () => {
  if (multipleSelection.value.length === 0) return
  
  // 获取选中文档的ID列表
  const documentIds = multipleSelection.value.map(doc => doc.id)
  
  // 打开知识库选择对话框
  SelectDatasetDialogRef.value.open(documentIds)
}



// 单个文档迁移
const migrateDocument = (row: any) => {
  // 打开知识库选择对话框，传入单个文档ID
  SelectDatasetDialogRef.value.open([row.id])
}

// 批量导出ZIP
const batchExportZip = async () => {
  if (multipleSelection.value.length === 0) return
  
  try {
    // 遍历选中的文档，逐个导出
    for (const doc of multipleSelection.value) {
      try {
        await documentApi.exportDocumentZip(doc.name, props.datasetId, doc.id)
      } catch (error) {
        console.error(`导出文档"${doc.name}"失败:`, error)
        ElMessage.warning(`导出文档"${doc.name}"失败`)
      }
    }
    ElMessage.success(`已开始导出 ${multipleSelection.value.length} 个文档`)
  } catch (error) {
    console.error('批量导出失败:', error)
    ElMessage.error('批量导出失败')
  }
}

const cancelTask = async (row: any, taskType: number) => {
  try {
    await documentApi.cancelTask(props.datasetId, row.id, { type: taskType })
    ElMessage.success('任务已取消')
    await getList()
  } catch (error) {
    console.error('取消任务失败:', error)
    ElMessage.error('取消任务失败')
  }
}

// exportDocument 函数已移除（功能已隐藏）

const exportDocumentZip = async (row: any) => {
  try {
    await documentApi.exportDocumentZip(row.name, props.datasetId, row.id)
    ElMessage.success('导出任务已提交')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const handleUpload = async () => {
  if (UploadComponentRef.value && UploadComponentRef.value.validate && UploadComponentRef.value.form) {
    try {
      uploading.value = true
      
      // 验证表单
      const isValid = await UploadComponentRef.value.validate()
      if (!isValid) {
        uploading.value = false
        return
      }
      
      const form = UploadComponentRef.value.form
      const fileType = form.fileType
      const fileList = form.fileList
      
      if (!fileList || fileList.length === 0) {
        ElMessage.error('请选择要上传的文件')
        uploading.value = false
        return
      }
      
      // 根据文件类型处理上传
      if (fileType === 'QA') {
        // QA文档上传
        let fd = new FormData()
        fileList.forEach((item: any) => {
          if (item?.raw) {
            fd.append('file', item.raw)
          }
        })
        await documentApi.postQADocument(props.datasetId, fd)
        ElMessage.success('QA文档上传成功')
      } else if (fileType === 'table') {
        // 表格文档上传
        let fd = new FormData()
        fileList.forEach((item: any) => {
          if (item?.raw) {
            fd.append('file', item.raw)
          }
        })
        await documentApi.postTableDocument(props.datasetId, fd)
        ElMessage.success('表格文档上传成功')
      } else if (fileType === 'txt') {
        // 文本文档：使用智能分段方式直接上传
        await handleTxtDocumentUpload(fileList)
      } else if (fileType === 'audio') {
        // 音频文档：使用后端API处理
        let fd = new FormData()
        fileList.forEach((item: any) => {
          if (item?.raw) {
            fd.append('file', item.raw)
          }
        })
        await documentApi.postAudioDocument(props.datasetId, fd)
        ElMessage.success('音频文档上传成功')
      }
      
      // 上传成功后的处理
      handleUploadSuccess()
      
    } catch (error) {
      console.error('上传失败:', error)
      ElMessage.error('上传失败')
      uploading.value = false
    }
  }
}

// 处理txt文档上传（智能分段）
const handleTxtDocumentUpload = async (fileList: any[]) => {
  try {
    // 第一步：调用分段预览API（批量处理）
    const formData = new FormData()
    fileList.forEach((fileItem) => {
      if (fileItem?.raw) {
        formData.append('file', fileItem.raw)
      }
    })
    
    // 智能分段参数（默认配置）
    formData.append('limit', '800') // 段落长度限制
    formData.append('with_filter', 'true') // 启用过滤
    
    console.log('开始智能分段，文件数量:', fileList.length)
    const splitResult = await documentApi.postSplitDocument(formData)
    
    if (splitResult.data && splitResult.data.length > 0) {
      // 第二步：处理分段结果，转换为文档格式
      const documents = splitResult.data.map((item: any) => {
        // 确保段落数据格式正确
        const paragraphs = item.content.map((paragraph: any, index: number) => ({
          title: paragraph.title || `段落 ${index + 1}`,
          content: paragraph.content,
          serial_number: index
        }))
        
        return {
          name: item.name || '未命名文档',
          paragraphs: paragraphs
        }
      })
      
      // 第三步：提交分段后的文档
      console.log('开始提交文档，文档数量:', documents.length)
      console.log('文档详情:', documents)
      
      await documentApi.postDocument(props.datasetId, documents)
      ElMessage.success(`成功上传 ${documents.length} 个文档，正在进行向量化处理`)
      
      // 统计总段落数
      const totalParagraphs = documents.reduce((sum: number, doc: any) => sum + doc.paragraphs.length, 0)
      console.log(`总共生成 ${totalParagraphs} 个段落`)
      
    } else {
      throw new Error('文档分段失败，没有生成有效段落')
    }
    
  } catch (error) {
    console.error('txt文档上传失败:', error)
    throw error
  }
}


const handleUploadSuccess = () => {
  uploading.value = false
  // 重置上传组件的表单状态
  if (UploadComponentRef.value && UploadComponentRef.value.resetForm) {
    UploadComponentRef.value.resetForm()
  }
  showUploadDialog.value = false
  getList()
  // 通知父组件文档发生变化
  emit('documentChanged')
}

// 迁移成功后刷新列表
const handleMigrationSuccess = () => {
  // 清空选择状态
  multipleTableRef.value?.clearSelection()
  // 重新获取列表
  getList()
  // 通知父组件文档发生变化
  emit('documentChanged')
}

// 打开上传对话框
const openUploadDialog = async () => {
  showUploadDialog.value = true
  // 等待对话框打开和组件渲染完成
  await nextTick()
  // 重置上传组件的表单状态
  if (UploadComponentRef.value && UploadComponentRef.value.resetForm) {
    UploadComponentRef.value.resetForm()
  }
}

// 关闭上传对话框
const closeUploadDialog = () => {
  // 重置上传组件的表单状态
  if (UploadComponentRef.value && UploadComponentRef.value.resetForm) {
    UploadComponentRef.value.resetForm()
  }
  showUploadDialog.value = false
}

// 轮询定时器
let interval: number | null = null

// 初始化轮询（每 6s 拉取一次，避免 loading 闪烁）
const initInterval = () => {
  if (interval) return
  interval = window.setInterval(() => {
    getList(true)
  }, 6000)
}

// 关闭轮询
const closeInterval = () => {
  if (interval) {
    clearInterval(interval)
    interval = null
  }
}

// 组件挂载
onMounted(() => {
  getList()

  // 启动轮询
  initInterval()
})

// 组件卸载
onBeforeUnmount(() => {
  // 清除轮询
  closeInterval()
})
</script>

<style lang="scss" scoped>
.document-management {
  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .left-actions {
      display: flex;
      gap: 8px;
    }
    
    .search-input {
      width: 240px;
    }
  }
  
  .document-table {
    .mr-4 {
      margin-right: 4px;
    }
    
    .justify-center {
      text-align: center;
    }
    
    :deep(.is-active) {
      background-color: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
    }
  }
}

.upload-dialog {
  :deep(.el-dialog__body) {
    padding: 0;
  }
  
  .upload-document-container {
    width: 70%;
    margin: 0 auto;
    margin-bottom: 20px;
    padding: 24px;
  }
  
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
}
.el-button.is-disabled {
--el-button-disabled-text-color: var(--el-text-color-regular)
}
</style>