<template>
  <h4 class="title-decoration-1 mb-8">上传文档</h4>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
  >
    <div class="mt-16 mb-16">
      <el-radio-group v-model="form.fileType" @change="radioChange" class="app-radio-button-group">
        <el-radio-button value="txt">文本文档</el-radio-button>
        <el-radio-button value="table">表格文档</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 问答对选项已隐藏 -->
    
    <el-form-item prop="fileList" v-if="form.fileType === 'table'">
      <div class="update-info flex p-8-12 border-r-4 mb-16 w-full">
        <div class="mt-4">
          <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
        </div>
        <div class="ml-16 lighter">
          <p>
            请上传表格文档，系统支持xls、xlsx、csv格式文件。
            <el-button type="primary" link @click="downloadTableTemplate('excel')">
              下载 Excel 模板
            </el-button>
            <el-button type="primary" link @click="downloadTableTemplate('csv')">
              下载 CSV 模板
            </el-button>
          </p>
          <p>表格文档支持多行多列，第一行为表头，从第二行开始为数据。</p>
          <p>表格文档中每个单元格字符数不超过2048个字符。</p>
          <p>表格文档最大支持10000行，100列。</p>
        </div>
      </div>
      <el-upload
        :webkitdirectory="false"
        class="w-full mb-4"
        drag
        multiple
        v-model:file-list="form.fileList"
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        accept=".xlsx, .xls, .csv"
        :limit="50"
        :on-exceed="onExceed"
        :on-change="fileHandleChange"
        @click.prevent="handlePreview(false)"
      >
        <img src="@/assets/upload-icon.svg" alt="" />
        <div class="el-upload__text">
          <p>
            将文件拖到此处，或
            <em class="hover" @click.prevent="handlePreview(false)">
              点击上传
            </em>
            <em class="hover ml-4" @click.prevent="handlePreview(true)">
              选择文件夹
            </em>
          </p>
          <div class="upload__decoration">
            <p>支持格式：XLS、XLSX、CSV</p>
          </div>
        </div>
      </el-upload>
    </el-form-item>
    
    <el-form-item prop="fileList" v-if="form.fileType === 'txt'">
      <div class="update-info flex p-8-12 border-r-4 mb-16 w-full">
        <div class="mt-4">
          <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
        </div>
        <div class="ml-16 lighter">
          <p>支持 txt、md、docx、pdf、html、xlsx、xls、csv、zip 格式文件，单个文件大小不超过 100MB。</p>
          <p>为保证问答效果，建议上传的文档内容清晰、结构化程度高。</p>
        </div>
      </div>
      <el-upload
        :webkitdirectory="false"
        class="w-full"
        drag
        multiple
        v-model:file-list="form.fileList"
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        accept=".txt, .md, .log, .docx, .pdf, .html,.zip,.xlsx,.xls,.csv"
        :limit="50"
        :on-exceed="onExceed"
        :on-change="fileHandleChange"
        @click.prevent="handlePreview(false)"
      >
        <img src="@/assets/upload-icon.svg" alt="" />
        <div class="el-upload__text">
          <p>
            将文件拖到此处，或
            <em class="hover" @click.prevent="handlePreview(false)">
              点击上传
            </em>
            <em class="hover ml-4" @click.prevent="handlePreview(true)">
              选择文件夹
            </em>
          </p>
          <div class="upload__decoration">
            <p>
              支持格式：TXT、Markdown、PDF、DOCX、HTML、XLS、XLSX、CSV、ZIP
            </p>
          </div>
        </div>
      </el-upload>
    </el-form-item>
  </el-form>
  
  <el-row :gutter="8" v-if="form.fileList?.length">
    <template v-for="(item, index) in form.fileList" :key="index">
      <el-col :span="12" class="mb-8">
        <el-card shadow="never" class="file-List-card">
          <div class="flex-between">
            <div class="flex">
              <img :src="getImgUrl(item && item?.name)" alt="" width="40" />
              <div class="ml-8">
                <p>{{ item && item?.name }}</p>
                <el-text type="info" size="small">{{
                  filesize(item && item?.size) || '0K'
                }}</el-text>
              </div>
            </div>
            <el-button text @click="deleteFile(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </template>
  </el-row>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted, onMounted, computed, watch, nextTick } from 'vue'
import type { UploadFiles, UploadFile } from 'element-plus'
import { filesize, getImgUrl, isRightType } from '@/utils/utils'
import { MsgError } from '@/utils/message'
import documentApi from '@/api/document'
import useStore from '@/stores'
import { t } from '@/locales'
import { Delete } from '@element-plus/icons-vue'
import AppIcon from '@/components/icons/AppIcon.vue'

// Props
interface Props {
  datasetId: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  uploadSuccess: []
}>()

// Store
const { dataset } = useStore()
const documentsFiles = computed(() => dataset.documentsFiles)
const documentsType = computed(() => dataset.documentsType)

// 响应式数据
const FormRef = ref()

const form = ref({
  fileType: 'txt',
  fileList: [] as any
})

const rules = reactive({
  fileList: [
    { required: true, message: '请选择要上传的文件', trigger: 'change' }
  ]
})

// 方法
function radioChange() {
  form.value.fileList = []
}

function deleteFile(index: number) {
  form.value.fileList.splice(index, 1)
}

// 上传on-change事件
const fileHandleChange = (file: UploadFile, fileList: UploadFiles) => {
  //1、判断文件大小是否合法，文件限制不能大于100M
  if ((file.size as number) > 1024 * 1024 * 100) {
    MsgError(t('views.document.upload.errorMessage1'))
    fileList.splice(-1, 1)
    return false
  }

  if (!isRightType(file?.name, form.value.fileType)) {
    if (file?.name !== '.DS_Store') {
      MsgError(t('views.document.upload.errorMessage2'))
    }
    fileList.splice(-1, 1)
    return false
  }
}

const handlePreview = (multiple: boolean) => {
  nextTick(() => {
    const inputDom = document.querySelector('.el-upload__input') as HTMLInputElement
    if (inputDom) {
      inputDom.webkitdirectory = multiple
    }
  })
}

const onExceed = () => {
  MsgError(t('views.document.upload.errorMessage3'))
}

// downloadTemplate 函数已移除（问答对功能已隐藏）

const downloadTableTemplate = (type: string) => {
  documentApi.exportTableTemplate(
    `表格模板.${type === 'excel' ? 'xlsx' : 'csv'}`,
    type
  )
}

// 重置表单
function resetForm() {
  form.value = {
    fileType: 'txt',
    fileList: []
  }
  // 清空表单验证状态
  if (FormRef.value) {
    FormRef.value.clearValidate()
  }
}

/**
  表单校验
*/
function validate() {
  if (!FormRef.value) return
  return FormRef.value.validate((valid: boolean) => {
    return valid
  })
}

// Watch form changes and update store
watch(form.value, (value) => {
  dataset.saveDocumentsType(value.fileType)
  dataset.saveDocumentsFile(value.fileList)
})

onMounted(() => {
  if (documentsType.value && ['txt', 'table'].includes(documentsType.value)) {
    form.value.fileType = documentsType.value
  } else {
    // 如果之前选择的是问答对，重置为文本文档
    form.value.fileType = 'txt'
  }
  if (documentsFiles.value) {
    form.value.fileList = documentsFiles.value
  }
})

onUnmounted(() => {
  form.value = {
    fileType: 'txt',
    fileList: []
  }
})

defineExpose({
  validate,
  form,
  resetForm
})
</script>

<style scoped lang="scss">
.upload__decoration {
  font-size: 12px;
  line-height: 20px;
  color: var(--el-text-color-secondary);
}

.el-upload__text {
  .hover:hover {
    color: var(--el-color-primary-light-5);
  }
}

.file-List-card {
  border: 1px solid var(--el-border-color-light);
  
  :deep(.el-card__body) {
    padding: 16px;
  }
}

.flex {
  display: flex;
  align-items: center;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ml-8 {
  margin-left: 8px;
}

.mb-8 {
  margin-bottom: 8px;
}

.mt-16 {
  margin-top: 16px;
}

.mb-16 {
  margin-bottom: 16px;
}

.ml-16 {
  margin-left: 16px;
}

.p-8-12 {
  padding: 8px 12px;
}

.border-r-4 {
  border-left: 4px solid var(--el-color-primary);
}

.w-full {
  width: 100%;
}

.update-info {
  background-color: var(--el-color-primary-light-9);
  border-radius: 4px;
  
  .lighter {
    color: var(--el-text-color-regular);
    font-size: 14px;
    line-height: 1.6;
    
    p {
      margin: 8px 0;
    }
  }
}

.title-decoration-1 {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  position: relative;
  padding-left: 8px;
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 16px;
    background-color: var(--el-color-primary);
    border-radius: 2px;
  }
}

.app-radio-button-group {
  :deep(.el-radio-button) {
    margin-right: 0;
  }
  
  :deep(.el-radio-button:not(:last-child)) {
    margin-right: -1px;
  }
}
</style>