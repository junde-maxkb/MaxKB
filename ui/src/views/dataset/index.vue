<template>
  <div class="dataset-list-container p-24" style="padding-top: 16px">
    <el-tabs v-model="datasetType" @tab-change="tabChangeHandle">
      <el-tab-pane :label="$t('views.dataset.tabs.myDataset')" name="MY"></el-tab-pane>
      <el-tab-pane :label="$t('views.dataset.tabs.sharedDataset')" name="SHARED">
        <el-tabs v-model="sharedType" @tab-change="sharedTabChangeHandle" class="mt-16">
          <el-tab-pane :label="$t('views.dataset.tabs.organizationDataset')" name="ORGANIZATION"></el-tab-pane>
          <el-tab-pane :label="$t('views.dataset.tabs.sharedToMeDataset')" name="SHARED_TO_ME"></el-tab-pane>
        </el-tabs>
      </el-tab-pane>
      <el-tab-pane :label="$t('views.dataset.tabs.searchDataset')" name="SEARCH"></el-tab-pane>
    </el-tabs>
    <div class="flex-between mb-16">
      <h4></h4>
      <div class="flex-between">
        <el-select
          v-if="datasetType === 'MY'"
          v-model="sortField"
          class="mr-12"
          @change="searchHandle"
          style="max-width: 240px; width: 150px"
        >
          <el-option
            v-for="item in sortOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-select
          v-model="selectUserId"
          class="mr-12"
          @change="searchHandle"
          style="max-width: 240px; width: 150px"
        >
          <el-option
            v-for="item in userOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-input
          v-model="searchValue"
          @change="searchHandle"
          :placeholder="$t('views.dataset.searchBar.placeholder')"
          prefix-icon="Search"
          class="w-240"
          style="max-width: 240px"
          clearable
        />
      </div>
    </div>
    <div v-loading.fullscreen.lock="paginationConfig.current_page === 1 && loading">
      <InfiniteScroll
        :size="datasetList.length"
        :total="paginationConfig.total"
        :page_size="paginationConfig.page_size"
        v-model:current_page="paginationConfig.current_page"
        @load="getList"
        :loading="loading"
      >
        <el-row :gutter="15">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" class="mb-16">
            <CardAdd :title="$t('views.dataset.createDataset')" @click="openCreateDialog" />
          </el-col>
          <template v-for="(item, index) in datasetList" :key="index">
            <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" class="mb-16">
              <CardBox
                :title="item.name"
                :description="item.desc"
                class="cursor"
                @click="router.push({ path: `/dataset/${item.id}/document` })"
              >
                <template #icon>
                  <AppAvatar
                    v-if="item.type === '1'"
                    class="mr-8 avatar-purple"
                    shape="square"
                    :size="32"
                  >
                    <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                  </AppAvatar>
                  <AppAvatar
                    v-else-if="item.type === '2'"
                    class="mr-8 avatar-purple"
                    shape="square"
                    :size="32"
                    style="background: none"
                  >
                    <img src="@/assets/logo_lark.svg" style="width: 100%" alt="" />
                  </AppAvatar>
                  <AppAvatar v-else class="mr-8 avatar-blue" shape="square" :size="32">
                    <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                  </AppAvatar>
                </template>
                <template #subTitle>
                  <el-text class="color-secondary" size="small">
                    <auto-tooltip :content="item.username">
                      {{ $t('common.creator') }}: {{ item.username }}
                    </auto-tooltip>
                  </el-text>
                </template>
                <div class="delete-button">
                  <el-tag class="blue-tag" v-if="item.type === '0'" style="height: 22px">{{
                    $t('views.dataset.general')
                  }}</el-tag>
                  <el-tag
                    class="purple-tag"
                    v-else-if="item.type === '1'"
                    type="warning"
                    style="height: 22px"
                    >{{ $t('views.dataset.web') }}</el-tag
                  >
                  <el-tag
                    class="purple-tag"
                    v-else-if="item.type === '2'"
                    type="warning"
                    style="height: 22px"
                    >{{ $t('views.dataset.lark') }}</el-tag
                  >
                  <el-tag
                    class="purple-tag"
                    v-else-if="item.type === '3'"
                    type="warning"
                    style="height: 22px"
                    >{{ $t('views.dataset.yuque') }}</el-tag
                  >
                </div>

                <template #footer>
                  <div class="footer-content flex-between">
                    <div>
                      <span class="bold">{{ item?.document_count || 0 }}</span>
                      {{ $t('views.dataset.document_count') }}<el-divider direction="vertical" />
                      <span class="bold">{{ numberFormat(item?.char_length) || 0 }}</span>
                      {{ $t('common.character') }}<el-divider direction="vertical" />
                      <span class="bold">{{ item?.application_mapping_count || 0 }}</span>
                      {{ $t('views.dataset.relatedApp_count') }}
                    </div>
                    <div @click.stop>
                      <el-dropdown trigger="click">
                        <el-button text @click.stop>
                          <el-icon><MoreFilled /></el-icon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item
                              icon="Refresh"
                              @click.stop="syncDataset(item)"
                              v-if="item.type === '1'"
                              >{{ $t('views.dataset.setting.sync') }}</el-dropdown-item
                            >

                            <el-dropdown-item @click="reEmbeddingDataset(item)">
                              <AppIcon
                                iconName="app-document-refresh"
                                style="font-size: 16px"
                              ></AppIcon>
                              {{ $t('views.dataset.setting.vectorization') }}</el-dropdown-item
                            >
                            <el-dropdown-item
                              icon="Connection"
                              @click.stop="openGenerateDialog(item)"
                              >{{ $t('views.document.generateQuestion.title') }}</el-dropdown-item
                            >
                            <el-dropdown-item
                              icon="Setting"
                              @click.stop="router.push({ path: `/dataset/${item.id}/setting` })"
                            >
                              {{ $t('common.setting') }}</el-dropdown-item
                            >
                            <el-dropdown-item @click.stop="export_dataset(item)">
                              <AppIcon iconName="app-export"></AppIcon
                              >{{ $t('views.document.setting.export') }} Excel</el-dropdown-item
                            >
                            <el-dropdown-item @click.stop="export_zip_dataset(item)">
                              <AppIcon iconName="app-export"></AppIcon
                              >{{ $t('views.document.setting.export') }} ZIP</el-dropdown-item
                            >
                            <el-dropdown-item icon="Delete" @click.stop="deleteDataset(item)">{{
                              $t('common.delete')
                            }}</el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </div>
                  </div>
                </template>
              </CardBox>
            </el-col>
          </template>
        </el-row>
      </InfiniteScroll>
    </div>
    <SyncWebDialog ref="SyncWebDialogRef" @refresh="refresh" />
    <CreateDatasetDialog ref="CreateDatasetDialogRef" />
    <GenerateRelatedDialog ref="GenerateRelatedDialogRef" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue'
import SyncWebDialog from '@/views/dataset/component/SyncWebDialog.vue'
import CreateDatasetDialog from './component/CreateDatasetDialog.vue'
import datasetApi from '@/api/dataset'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { useRouter } from 'vue-router'
import { numberFormat } from '@/utils/utils'
import { ValidType, ValidCount } from '@/enums/common'
import { t } from '@/locales'
import useStore from '@/stores'
import applicationApi from '@/api/application'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
const { user, common } = useStore()
const router = useRouter()

const CreateDatasetDialogRef = ref()
const SyncWebDialogRef = ref()
const loading = ref(false)
const datasetList = ref<any[]>([])
const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0
})
const GenerateRelatedDialogRef = ref<InstanceType<typeof GenerateRelatedDialog>>()
function openGenerateDialog(row: any) {
  if (GenerateRelatedDialogRef.value) {
    GenerateRelatedDialogRef.value.open([], 'dataset', row.id)
  }
}

const searchValue = ref('')

interface UserOption {
  label: string
  value: string
}

const userOptions = ref<UserOption[]>([])

const selectUserId = ref('all')

const datasetType = ref('MY')
const sharedType = ref('ORGANIZATION')

const sortField = ref('name')
const sortOptions = [
  { label: '按名称排序', value: 'name' },
  { label: '按创建时间排序', value: 'create_time' },
  { label: '按修改时间排序', value: 'update_time' }
]

function sortDatasetList(list: any[]) {
  const field = sortField.value
  return [...list].sort((a, b) => {
    if (field === 'name') {
      return a.name.localeCompare(b.name)
    } else if (field === 'create_time') {
      return new Date(b.create_time).getTime() - new Date(a.create_time).getTime()
    } else if (field === 'update_time') {
      return new Date(b.update_time).getTime() - new Date(a.update_time).getTime()
    }
    return 0
  })
}

watch(
  [datasetType, sharedType],
  ([newDatasetType, newSharedType]) => {
    paginationConfig.total = 0
    paginationConfig.current_page = 1
    datasetList.value = []
    getList()
  },
  { immediate: true }
)

function tabChangeHandle() {
  selectUserId.value = 'all'
  searchValue.value = ''
}

function sharedTabChangeHandle() {
  selectUserId.value = 'all'
  searchValue.value = ''
}

function openCreateDialog() {
  common.asyncGetValid(ValidType.Dataset, ValidCount.Dataset, loading).then(async (res: any) => {
    if (res?.data) {
      CreateDatasetDialogRef.value.open()
    } else if (res?.code === 400) {
      MsgConfirm(t('common.tip'), t('views.dataset.tip.professionalMessage'), {
        cancelButtonText: t('common.confirm'),
        confirmButtonText: t('common.professional')
      })
        .then(() => {
          window.open('https://maxkb.cn/pricing.html', '_blank')
        })
        .catch(() => {})
    }
  })
}

function refresh() {
  MsgSuccess(t('views.dataset.tip.syncSuccess'))
}

function reEmbeddingDataset(row: any) {
  datasetApi.putReEmbeddingDataset(row.id).then(() => {
    MsgSuccess(t('common.submitSuccess'))
  })
}

function syncDataset(row: any) {
  SyncWebDialogRef.value.open(row.id)
}

function searchHandle() {
  if (user.userInfo) {
    localStorage.setItem(user.userInfo.id + 'dataset', selectUserId.value)
  }
  paginationConfig.current_page = 1
  datasetList.value = []
  getList()
}
const export_dataset = (item: any) => {
  datasetApi.exportDataset(item.name, item.id, loading).then((ok) => {
    MsgSuccess(t('common.exportSuccess'))
  })
}
const export_zip_dataset = (item: any) => {
  datasetApi.exportZipDataset(item.name, item.id, loading).then((ok) => {
    MsgSuccess(t('common.exportSuccess'))
  })
}

function deleteDataset(row: any) {
  MsgConfirm(
    `${t('views.dataset.delete.confirmTitle')}${row.name} ?`,
    `${t('views.dataset.delete.confirmMessage1')} ${row.application_mapping_count} ${t('views.dataset.delete.confirmMessage2')}`,
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      datasetApi.delDataset(row.id, loading).then(() => {
        const index = datasetList.value.findIndex((v) => v.id === row.id)
        datasetList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

function getList() {
  const params = {
    ...(searchValue.value && { name: searchValue.value }),
    ...(selectUserId.value &&
      selectUserId.value !== 'all' && { select_user_id: selectUserId.value }),
    type: datasetType.value,
    ...(datasetType.value === 'SHARED' && { shared_type: sharedType.value })
  }
  datasetApi.getDataset(paginationConfig, params, loading).then((res) => {
    res.data.records.forEach((item: any) => {
      if (user.userInfo && item.user_id === user.userInfo.id) {
        item.username = user.userInfo.username
      } else {
        item.username = userOptions.value.find((v) => v.value === item.user_id)?.label
      }
    })
    paginationConfig.total = res.data.total
    const newRecords = sortDatasetList(res.data.records)
    datasetList.value = [...datasetList.value, ...newRecords]
  })
}

function getUserList() {
  applicationApi.getUserList('DATASET', loading).then((res) => {
    if (res.data) {
      userOptions.value = res.data.map((item: any) => {
        return {
          label: item.username,
          value: item.id
        }
      })
      if (user.userInfo) {
        const selectUserIdValue = localStorage.getItem(user.userInfo.id + 'dataset')
        if (selectUserIdValue && userOptions.value.find((v) => v.value === selectUserIdValue)) {
          selectUserId.value = selectUserIdValue
        }
      }
    }
  })
}

onMounted(() => {
  getUserList()
})
</script>
<style lang="scss" scoped>
.dataset-list-container {
  .delete-button {
    position: absolute;
    right: 12px;
    top: 15px;
    height: auto;
  }
  .footer-content {
    .bold {
      color: var(--app-text-color);
    }
  }
  :deep(.el-divider__text) {
    background: var(--app-layout-bg-color);
  }
}
</style>
