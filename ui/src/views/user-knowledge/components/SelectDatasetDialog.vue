<template>
  <el-dialog
    title="选择目标知识库"
    v-model="dialogVisible"
    width="600"
    class="select-dataset-dialog"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <template #header="{ titleId, titleClass }">
      <div class="my-header flex">
        <h4 :id="titleId" :class="titleClass">选择目标知识库</h4>
        <el-button link class="ml-16" @click="refresh">
          <el-icon class="mr-4"><Refresh /></el-icon>刷新
        </el-button>
      </div>
    </template>
    <div class="content-height">
      <el-radio-group v-model="selectDataset" class="card__radio">
        <el-scrollbar height="500">
          <div class="p-16">
            <el-row :gutter="12" v-loading="loading">
              <el-col :span="12" v-for="(item, index) in datasetList" :key="index" class="mb-16">
                <el-card shadow="never" :class="item.id === selectDataset ? 'active' : ''">
                  <el-radio :value="item.id" size="large">
                    <div class="flex align-center">
                      <AppAvatar
                        v-if="item?.type === '0'"
                        class="mr-8 avatar-blue"
                        shape="square"
                        :size="32"
                      >
                        <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                      </AppAvatar>
                      <AppAvatar
                        v-if="item?.type === '1'"
                        class="mr-8 avatar-purple"
                        shape="square"
                        :size="32"
                      >
                        <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                      </AppAvatar>
                      <AppAvatar
                        v-if="item?.type === '2'"
                        class="mr-8 avatar-purple"
                        shape="square"
                        :size="32"
                        style="background: none"
                      >
                        <img src="@/assets/logo_lark.svg" style="width: 100%" alt="" />
                      </AppAvatar>
                      <span class="ellipsis" :title="item.name">
                        {{ item.name }}
                      </span>
                    </div>
                  </el-radio>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-scrollbar>
      </el-radio-group>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitHandle" :disabled="!selectDataset || loading">
          确认
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import documentApi from '@/api/document'
import useStore from '@/stores'
import { ElMessage } from 'element-plus'

const { dataset } = useStore()

const emit = defineEmits(['refresh'])

const props = defineProps<{
  currentDatasetId: string
}>()

const loading = ref<boolean>(false)
const dialogVisible = ref<boolean>(false)
const selectDataset = ref('')
const datasetList = ref<any>([])
const documentList = ref<any>([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    selectDataset.value = ''
    datasetList.value = []
    documentList.value = []
  }
})

const open = (list: any) => {
  documentList.value = list
  getDataset()
  dialogVisible.value = true
}

const submitHandle = async () => {
  if (!selectDataset.value) {
    ElMessage.warning('请选择目标知识库')
    return
  }
  
  try {
    loading.value = true
    await documentApi.putMigrateMulDocument(
      props.currentDatasetId, 
      selectDataset.value, 
      documentList.value
    )
    
    ElMessage.success(`成功迁移${documentList.value.length}个文档到目标知识库`)
    emit('refresh')
    dialogVisible.value = false
  } catch (error) {
    console.error('文档迁移失败:', error)
    ElMessage.error('文档迁移失败')
  } finally {
    loading.value = false
  }
}

function getDataset() {
  dataset.asyncGetAllDataset(loading).then((res: any) => {
    // 过滤掉当前知识库，不能迁移到自己
    datasetList.value = res.data?.filter((v: any) => v.id !== props.currentDatasetId)
  })
}

const refresh = () => {
  getDataset()
}

defineExpose({ open })
</script>

<style lang="scss">
.select-dataset-dialog {
  padding: 0;
  .el-dialog__header {
    padding: 24px 24px 0 24px;
  }
  .el-dialog__body {
    padding: 8px !important;
  }
  .el-dialog__footer {
    padding: 0 24px 24px;
  }
}
</style>

