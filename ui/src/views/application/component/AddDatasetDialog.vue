<template>
  <el-dialog
    :title="$t('views.dataset.addDataset')"
    v-model="dialogVisible"
    width="600"
    append-to-body
    class="addDataset-dialog"
    align-center
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <template #header="{ titleId, titleClass }">
      <div class="flex-between mb-8">
        <h4 :id="titleId" :class="titleClass">
          {{ $t('views.dataset.addDataset') }}
        </h4>
        <div class="flex align-center mr-8">
          <el-button link class="ml-16" @click="refresh">
            <el-icon class="mr-4"><Refresh /></el-icon>{{ $t('common.refresh') }}
          </el-button>
          <el-divider direction="vertical" />
        </div>
      </div>
      <div class="flex-between">
        <el-text type="info" class="color-secondary">
          {{ $t('views.dataset.addDatasetPlaceholder') }}
        </el-text>
        <el-input
          v-model="searchValue"
          :placeholder="$t('views.dataset.searchBar.placeholder')"
          prefix-icon="Search"
          class="w-240"
          clearable
        />
      </div>
    </template>
    <el-scrollbar>
      <div class="max-height">
        <el-row :gutter="12" v-loading="loading">
          <!-- 我的知识库 -->
          <template v-if="myDatasets.length > 0">
            <el-col :span="24" class="mb-8">
              <h5 class="title-decoration-1">{{ $t('views.dataset.myDataset') }}</h5>
            </el-col>
            <el-col :span="12" v-for="(item, index) in myDatasets" :key="index" class="mb-16">
              <CardCheckbox value-field="id" :data="item" v-model="checkList" @change="changeHandle">
                <span class="ellipsis cursor" :title="item.name"> {{ item.name }}</span>
              </CardCheckbox>
            </el-col>
          </template>

          <!-- 共享知识库 -->
          <template v-if="sharedDatasets.length > 0">
            <el-col :span="24" class="mb-8">
              <h5 class="title-decoration-1">{{ $t('views.dataset.sharedDataset') }}</h5>
            </el-col>
            <el-col :span="12" v-for="(item, index) in sharedDatasets" :key="index" class="mb-16">
              <CardCheckbox value-field="id" :data="item" v-model="checkList" @change="changeHandle">
                <span class="ellipsis cursor" :title="item.name"> {{ item.name }}</span>
              </CardCheckbox>
            </el-col>
          </template>

          <!-- 机构知识库 -->
          <template v-if="organizationDatasets.length > 0">
            <el-col :span="24" class="mb-8">
              <h5 class="title-decoration-1">{{ $t('views.dataset.organizationDataset') }}</h5>
            </el-col>
            <el-col :span="12" v-for="(item, index) in organizationDatasets" :key="index" class="mb-16">
              <CardCheckbox value-field="id" :data="item" v-model="checkList" @change="changeHandle">
                <span class="ellipsis cursor" :title="item.name"> {{ item.name }}</span>
              </CardCheckbox>
            </el-col>
          </template>
        </el-row>
      </div>
    </el-scrollbar>
    <template #footer>
      <div class="flex-between">
        <div class="flex">
          <el-text type="info" class="color-secondary mr-8" v-if="checkList.length > 0">
            {{ $t('views.dataset.selected') }} {{ checkList.length }}
            {{ $t('views.dataset.countDataset') }}
          </el-text>
          <el-button link type="primary" v-if="checkList.length > 0" @click="clearCheck">
            {{ $t('common.clear') }}
          </el-button>
        </div>
        <span>
          <el-button @click.prevent="dialogVisible = false">
            {{ $t('common.cancel') }}
          </el-button>
          <el-button type="primary" @click="submitHandle">
            {{ $t('common.confirm') }}
          </el-button>
        </span>
      </div>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import useStore from '@/stores'
import { t } from '@/locales'

interface Dataset {
  id: string
  name: string
  desc: string
  is_shared?: boolean
  is_organization?: boolean
  is_owned?: boolean
  embedding_mode_id?: string
}

const props = defineProps({
  data: {
    type: Array as () => Dataset[],
    default: () => []
  },
  loading: Boolean
})

const emit = defineEmits(['addData', 'refresh'])

const dialogVisible = ref(false)
const loading = ref(false)
const searchValue = ref('')
const checkList = ref<string[]>([])
const currentEmbedding = ref('')
const searchDate = ref<Dataset[]>([])

// 根据知识库类型分类
const myDatasets = computed(() => {
  return filterData.value.filter(item => item.is_owned)
})

const sharedDatasets = computed(() => {
  return filterData.value.filter(item => item.is_shared)
})

const organizationDatasets = computed(() => {
  return filterData.value.filter(item => item.is_organization)
})

// 搜索过滤
const filterData = computed(() => {
  if (!searchValue.value) return props.data
  return props.data.filter(item => 
    item.name.toLowerCase().includes(searchValue.value.toLowerCase()) ||
    item.desc.toLowerCase().includes(searchValue.value.toLowerCase())
  )
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    checkList.value = []
    currentEmbedding.value = ''
    searchValue.value = ''
  }
})

watch(searchValue, (val) => {
  if (val) {
    searchDate.value = props.data.filter((v) => v.name.includes(val))
  } else {
    searchDate.value = props.data
  }
})

function changeHandle() {
  if (checkList.value.length > 0) {
    const dataset = props.data.find(v => v.id === checkList.value[0])
    currentEmbedding.value = dataset?.embedding_mode_id || ''
  } else if (checkList.value.length === 0) {
    currentEmbedding.value = ''
  }
}

function clearCheck() {
  checkList.value = []
  currentEmbedding.value = ''
}

const open = (checked: string[]) => {
  searchDate.value = props.data
  checkList.value = checked
  if (checkList.value.length > 0) {
    const dataset = props.data.find(v => v.id === checkList.value[0])
    currentEmbedding.value = dataset?.embedding_mode_id || ''
  }

  dialogVisible.value = true
}

const submitHandle = () => {
  emit('addData', checkList.value)
  dialogVisible.value = false
}

const refresh = () => {
  emit('refresh')
}

defineExpose({ open })
</script>
<style lang="scss">
.addDataset-dialog {
  padding: 0;
  .el-dialog__header {
    padding: 24px 24px 8px 24px;
  }
  .el-dialog__body {
    padding: 8px !important;
  }
  .el-dialog__footer {
    padding: 8px 24px 24px 24px;
  }

  .el-dialog__headerbtn {
    top: 9px;
  }
  .max-height {
    max-height: calc(100vh - 260px);
    padding: 0 16px;
  }
}
</style>
