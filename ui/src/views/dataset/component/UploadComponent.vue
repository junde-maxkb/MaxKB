<template>
  <h4 class="title-decoration-1 mb-8">{{ $t('views.document.uploadDocument') }}</h4>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
  >
    <div class="mt-16 mb-16">
      <el-radio-group v-model="form.fileType" @change="radioChange" class="app-radio-button-group">
        <el-radio-button value="txt">{{ $t('views.document.fileType.txt.label') }}</el-radio-button>
        <el-radio-button value="table">{{
          $t('views.document.fileType.table.label')
        }}</el-radio-button>
        <el-radio-button v-if="isAdmin" value="QA">{{ $t('views.document.fileType.QA.label') }}</el-radio-button>
        <el-radio-button v-if="isAdmin" value="SQL">{{ $t('views.document.fileType.SQL.label') }}</el-radio-button>
      </el-radio-group>
    </div>

    <el-form-item prop="fileList" v-if="form.fileType === 'QA'">
      <div class="update-info flex p-8-12 border-r-4 mb-16 w-full">
        <div class="mt-4">
          <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
        </div>
        <div class="ml-16 lighter">
          <p>
            {{ $t('views.document.fileType.QA.tip1') }}
            <el-button type="primary" link @click="downloadTemplate('excel')">
              {{ $t('views.document.upload.download') }} Excel
              {{ $t('views.document.upload.template') }}
            </el-button>
            <el-button type="primary" link @click="downloadTemplate('csv')">
              {{ $t('views.document.upload.download') }} CSV
              {{ $t('views.document.upload.template') }}
            </el-button>
          </p>
          <p>{{ $t('views.document.fileType.QA.tip2') }}</p>
          <p>{{ $t('views.document.fileType.QA.tip3') }}</p>
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
        accept=".xlsx, .xls, .csv,.zip"
        :limit="50"
        :on-exceed="onExceed"
        :on-change="fileHandleChange"
        @click.prevent="handlePreview(false)"
      >
        <img src="@/assets/upload-icon.svg" alt="" />
        <div class="el-upload__text">
          <p>
            {{ $t('views.document.upload.uploadMessage') }}
            <em class="hover" @click.prevent="handlePreview(false)">
              {{ $t('views.document.upload.selectFile') }}
            </em>
            <em class="hove ml-4" @click.prevent="handlePreview(true)">
              {{ $t('views.document.upload.selectFiles') }}
            </em>
          </p>
          <div class="upload__decoration">
            <p>{{ $t('views.document.upload.formats') }}XLS、XLSX、CSV、ZIP</p>
          </div>
        </div>
      </el-upload>
    </el-form-item>
    <el-form-item prop="fileList" v-else-if="form.fileType === 'table'">
      <div class="update-info flex p-8-12 border-r-4 mb-16 w-full">
        <div class="mt-4">
          <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
        </div>
        <div class="ml-16 lighter">
          <p>
            {{ $t('views.document.fileType.table.tip1') }}
            <el-button type="primary" link @click="downloadTableTemplate('excel')">
              {{ $t('views.document.upload.download') }} Excel
              {{ $t('views.document.upload.template') }}
            </el-button>
            <el-button type="primary" link @click="downloadTableTemplate('csv')">
              {{ $t('views.document.upload.download') }} CSV
              {{ $t('views.document.upload.template') }}
            </el-button>
          </p>
          <p>{{ $t('views.document.fileType.table.tip2') }}</p>
          <p>{{ $t('views.document.fileType.table.tip3') }}</p>
          <p>{{ $t('views.document.fileType.table.tip4') }}</p>
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
            {{ $t('views.document.upload.uploadMessage') }}
            <em class="hover" @click.prevent="handlePreview(false)">
              {{ $t('views.document.upload.selectFile') }}
            </em>
            <em class="hover ml-4" @click.prevent="handlePreview(true)">
              {{ $t('views.document.upload.selectFiles') }}
            </em>
          </p>
          <div class="upload__decoration">
            <p>{{ $t('views.document.upload.formats') }}XLS、XLSX、CSV</p>
          </div>
        </div>
      </el-upload>
    </el-form-item>
    <!-- SQL数据库连接表单 -->
   
    <el-form-item v-if="form.fileType === 'SQL'">
      <div style="display: flex;   gap: 100px; ">
        <div class="table-list-top" style="flex: 0 0 200px; ">
          <p class="select-ds">
            {{ $t('views.document.db_connect.select_data_source') }}

          </p>
          <!-- 选择数据源下拉列表 -->
          <div>
            <el-select
              v-model="dataSource"
              @focus="handleFocus"
              clearable
              placeholder="Select"
              style="width: 240px"
              :popper-append-to-body="false" 
              :popper-class="'long-scroll-select'"
               @change="handleSelectChange"
               @clear="clearSelectSource"
            >
              <el-option
                v-for="item in state.dataSourceList"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              >
              <div style="display: flex; align-items: center; gap: 8px">
              <!-- 添加 Tickets 图标 -->
              <el-icon><Coin /></el-icon>
              <span>{{ item.name }}</span>
        </div>
            </el-option>
            </el-select>
          </div>
          <div class="team-list-input">
            <span>{{ $t('views.document.db_connect.data_table') }}</span>
            <el-input
              v-model="filterText"
              :placeholder="$t('views.document.db_connect.data_table')"
              prefix-icon="Search"
              clearable
              @clear="clearSelectTable"
            />
          </div>
          <div class="list-height-left" v-show="isListVisible">
            <el-scrollbar>
              <common-list
                :data="filterTeamList"
                class="mt-8"
                v-loading="loading"
                valueKey="value"
                @click="clickListHandle"
              >
                <template #default="{ row }">
                  <div class="flex-between"  style="align-items: center; height: 100%">
                    <div style="display: flex; align-items: center">
                      <el-icon style="font-size: 16px;display: flex; align-items: cente"><Document /></el-icon>&nbsp;&nbsp;
                      <span class="mr-8">{{ row.label }}</span>
                    </div>
                  </div>
                </template>
              </common-list>
            </el-scrollbar>
          </div>
      </div>
      <div class="team-member" v-loading="rLoading" style="width: 700px;">
        <div >字段选择</div>
        <div v-show="isTableVisible">
          <el-table
            ref="multipleTableRef"
            :max-height="400"
            :data="tableData"
            row-key="name"
            style="width: 100%"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" :selectable="selectable" width="100" />
            <el-table-column label="物理字段名">
              <template #default="scope">{{ scope.row.name }}</template>
            </el-table-column>
            <el-table-column label="字段备注">
              <template #default="scope">{{ scope.row.verbose_name }}</template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      </div>
      
        
    </el-form-item>
    <el-form-item prop="fileList" v-if="form.fileType === 'txt'">
      <div class="update-info flex p-8-12 border-r-4 mb-16 w-full">
        <div class="mt-4">
          <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
        </div>
        <div class="ml-16 lighter">
          <p>{{ $t('views.document.fileType.txt.tip1') }}</p>
          <p>{{ $t('views.document.fileType.txt.tip2') }}</p>
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
            {{ $t('views.document.upload.uploadMessage') }}
            <em class="hover" @click.prevent="handlePreview(false)">
              {{ $t('views.document.upload.selectFile') }}
            </em>
            <em class="hover ml-4" @click.prevent="handlePreview(true)">
              {{ $t('views.document.upload.selectFiles') }}
            </em>
          </p>
          <div class="upload__decoration">
            <p>
              {{
                $t('views.document.upload.formats')
              }}TXT、Markdown、PDF、DOCX、HTML、XLS、XLSX、CSV、ZIP
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
import { ref, reactive, onUnmounted, onMounted, computed, watch, nextTick, shallowRef} from 'vue'
import type { UploadFiles } from 'element-plus'
import { filesize, getImgUrl, isRightType } from '@/utils/utils'
import { MsgError,MsgSuccess } from '@/utils/message'
import documentApi from '@/api/document'
import dataSourceApi from '@/api/db-data-source'
import useStore from '@/stores'
import { useRoute } from 'vue-router'
import { t } from '@/locales'
const filterText = ref('')
const { dataset, user } = useStore()
const documentsFiles = computed(() => dataset.documentsFiles)
const documentsType = computed(() => dataset.documentsType)
const isAdmin = computed(() => user.userInfo?.role === 'ADMIN')
const form = ref({
  fileType: 'txt',
  fileList: [] as any
})
const currentSourceId = ref('')
const rules = reactive({
  fileList: [
    { required: true, message: t('views.document.upload.requiredMessage'), trigger: 'change' }
  ]
})
const selectedNames= ref([])
const selectable = (row, index) => {
  return true; 
};
watch(filterText, (val) => {
  if (val) {
    filterTeamList.value = filterTeamList.value.filter((v) =>
      v.label.toLowerCase().includes(val.toLowerCase())
    )
  } else {
    filterTeamList.value = tabelDataList.value
  }
})
const route = useRoute()
const {
  query: { id } 
} = route
const FormRef = ref()
const tableForm = reactive({
  source_id:"",
  table_name:"",
  columns:[]
})
const isListVisible = ref()
const isTableVisible = ref()
const rLoading = ref(false)
const loading = ref(false)
const dbRules = reactive({
  db_type: [{ required: true, message: '请选择数据库类型', trigger: 'change' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  port: [
    { required: true, message: '请输入端口号', trigger: 'blur' },
    { type: 'number', message: '端口号必须为数字', trigger: 'blur' }
  ],
  database: [{ required: true, message: '请输入数据库名称', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
})
const tableData = ref([])
const connectionStatus = reactive({
  message: '',
  type: 'info'
})

const testingConnection = ref(false)
const dbFormRef = ref()

const dataSource = ref('')

const handleFocus = async () => {
  try {
    if (!state.isLoaded) {
      const res = await dataSourceApi.getDbSourceList(); 
      if (res.code === 200) {
        state.dataSourceList = res.data;
        state.isLoaded = true;
      }
    }
  } catch (error) {
    console.error('数据加载失败:', error);
  }
};
const handleSelectionChange = (selectedRows) => {
  selectedNames.value = selectedRows.map(row => row.name);
  tableForm.columns = selectedNames.value
  console.log('已选中的物理字段名:', selectedNames);
  console.log('selectedNames:', selectedNames.value);
};
const state = reactive({
  nodeNameList: [],
  editArr: [],
  dataSourceList: [{'id':1,'name':'124324'}],
  isLoaded: false,
  fieldCollapse: ['dimension', 'quota']
})
const filterTeamList = ref([])
const tabelDataList = ref([])
const showDataSourceDropdown = true
const resetDbForm = () => {
  dbFormRef.value?.resetFields()
  connectionStatus.message = ''
}

watch(form.value, (value) => {
  dataset.saveDocumentsType(value.fileType)
  dataset.saveDocumentsFile(value.fileList)
})
function handleSearch(){
  
}
const clickListHandle = async (selectedValue: any) => {
  isTableVisible.value = true

  try {
    const res = await dataSourceApi.getTableColumns(currentSourceId.value,selectedValue.value); // 调用你的 API 方法
    if (res.code === 200) {
      isListVisible.value = true
      tableData.value = res.data
      tableForm.table_name = selectedValue.value
      
    }
    
  } catch (error) {
    console.error('数据加载失败:', error);
  }
}
const handleSelectChange = async (selectedValue:any) => {
  if(!selectedValue) return
  try {  
    const res = await dataSourceApi.getTable(selectedValue); 
    if (res.code === 200) {
      console.log("res.data",res.data)
      isListVisible.value = true
      tabelDataList.value = res.data.map(item => ({ label: item, value: item }))
      filterTeamList.value = res.data.map(item => ({ label: item, value: item }))
      currentSourceId.value = selectedValue
      tableForm.source_id = selectedValue
    }
    
  } catch (error) {
    console.error('数据加载失败:', error);
  }
};

function downloadTemplate(type: string) {
  documentApi.exportQATemplate(
    `${type}${t('views.document.upload.template')}.${type == 'csv' ? type : 'xlsx'}`,
    type
  )
}
function clearSelectSource(){
  filterTeamList.value = []
  isListVisible.value = false
  filterText.value = ''
}
function clearSelectTable(){
  filterText.value = ""
  isTableVisible.value = false
}
function downloadTableTemplate(type: string) {
  documentApi.exportTableTemplate(
    `${type}${t('views.document.upload.template')}.${type == 'csv' ? type : 'xlsx'}`,
    type
  )
}

function radioChange() {
  form.value.fileList = []
  connectionStatus.message = ''
}

function deleteFile(index: number) {
  form.value.fileList.splice(index, 1)
}

// 上传on-change事件
const fileHandleChange = (file: any, fileList: UploadFiles) => {
  //1、判断文件大小是否合法，文件限制不能大于100M
  const isLimit = file?.size / 1024 / 1024 < 100
  if (!isLimit) {
    MsgError(t('views.document.upload.errorMessage1'))
    fileList.splice(-1, 1) //移除当前超出大小的文件
    return false
  }

  if (!isRightType(file?.name, form.value.fileType)) {
    if (file?.name !== '.DS_Store') {
      MsgError(t('views.document.upload.errorMessage2'))
    }
    fileList.splice(-1, 1)
    return false
  }
  if (file?.size === 0) {
    MsgError(t('views.document.upload.errorMessage3'))
    fileList.splice(-1, 1)
    return false
  }
}

const onExceed = () => {
  MsgError(t('views.document.upload.errorMessage4'))
}

const handlePreview = (bool: boolean) => {
  let inputDom: any = null
  nextTick(() => {
    if (document.querySelector('.el-upload__input') != null) {
      inputDom = document.querySelector('.el-upload__input')
      inputDom.webkitdirectory = bool
    }
  })
}

/*
  表单校验
*/
function validate() {
  if (form.value.fileType === 'SQL') {
    return dbFormRef.value.validate((valid: any) => {
      if (valid) {
        // 这里可以添加额外的验证逻辑
        return true
      }
      return false
    })
  } else {
    if (!FormRef.value) return
    return FormRef.value.validate((valid: any) => {
      return valid
    })
  }
}

onMounted(() => {
  if (documentsType.value) {
    form.value.fileType = documentsType.value
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
  tableForm,

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
.w-400{
  width: 100%;
}
.list-height-left {
  height: calc(var(--create-dataset-height) - 220px);
}
</style>
