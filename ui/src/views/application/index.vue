<template>
  <div class="application-list-container p-24" style="padding-top: 16px">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane :label="$t('views.application.myApplications')" name="MY"></el-tab-pane>
      <el-tab-pane :label="$t('views.application.sharedApplications')" name="SHARED">
        <el-tabs v-model="sharedType" @tab-change="sharedTabChangeHandle" class="mt-16">
          <el-tab-pane :label="$t('views.application.tabs.organizationApplication')" name="ORGANIZATION"></el-tab-pane>
          <el-tab-pane :label="$t('views.application.tabs.sharedToMeApplication')" name="SHARED_TO_ME"></el-tab-pane>
        </el-tabs>
      </el-tab-pane>
      <el-tab-pane :label="$t('views.application.chatLogsTab.title')" name="CHAT_LOGS">
        <ChatLogSearch />
      </el-tab-pane>
    </el-tabs>

    <!-- 应用列表页面 - 只在非对话日志标签页显示 -->
    <div v-if="activeTab !== 'CHAT_LOGS'">
      <div class="flex-between mb-16">
        <h4></h4>
        <div class="flex-between">
          <el-select
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
            :placeholder="$t('views.application.searchBar.placeholder')"
            prefix-icon="Search"
            class="w-240"
            style="min-width: 240px"
            clearable
          />
        </div>
      </div>
      <div v-loading.fullscreen.lock="paginationConfig.current_page === 1 && loading">
        <InfiniteScroll
          :size="applicationList.length"
          :total="paginationConfig.total"
          :page_size="paginationConfig.page_size"
          v-model:current_page="paginationConfig.current_page"
          @load="getList"
          :loading="loading"
        >
          <el-row :gutter="15">
            <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" class="mb-16" v-if="activeTab === 'MY'">
              <el-card shadow="hover" class="application-card-add" style="--el-card-padding: 8px">
                <div class="card-add-button flex align-center cursor p-8" @click="openCreateDialog">
                  <AppIcon iconName="app-add-application" class="mr-8"></AppIcon>
                  {{ $t('views.application.createApplication') }}
                </div>
                <el-divider style="margin: 8px 0" />
                <el-upload
                  ref="elUploadRef"
                  :file-list="[]"
                  action="#"
                  multiple
                  :auto-upload="false"
                  :show-file-list="false"
                  :limit="1"
                  :on-change="(file: any, fileList: any) => importApplication(file)"
                  class="card-add-button"
                >
                  <div class="flex align-center cursor p-8">
                    <AppIcon iconName="app-import" class="mr-8"></AppIcon>
                    {{ $t('views.application.importApplication') }}
                  </div>
                </el-upload>
              </el-card>
            </el-col>
            <el-col
              :xs="24"
              :sm="12"
              :md="8"
              :lg="6"
              :xl="6"
              v-for="(item, index) in applicationList"
              :key="index"
              class="mb-16"
            >
              <CardBox
                :title="item.name"
                :description="item.desc"
                :class="{'cursor': item.permission !== 'READ' && !(activeTab === 'SHARED' && sharedType === 'ORGANIZATION')}"
                @click="!(activeTab === 'SHARED' && sharedType === 'ORGANIZATION') && item.permission !== 'READ' && router.push({ path: `/application/${item.id}/${item.type}/overview` })"
              >
                <template #icon>
                  <AppAvatar
                    v-if="isAppIcon(item?.icon)"
                    shape="square"
                    :size="32"
                    style="background: none"
                    class="mr-8"
                  >
                    <img :src="item?.icon" alt="" />
                  </AppAvatar>
                  <AppAvatar
                    v-else-if="item?.name"
                    :name="item?.name"
                    pinyinColor
                    shape="square"
                    :size="32"
                    class="mr-8"
                  />
                </template>
                <template #subTitle>
                  <el-text class="color-secondary" size="small">
                    <auto-tooltip :content="item.creator_name">
                      {{ $t('common.creator') }}: {{ item.creator_name }}
                    </auto-tooltip>
                  </el-text>
                </template>
                <div class="status-tag">
                  <el-tag type="warning" v-if="isWorkFlow(item.type)" style="height: 22px">
                    {{ $t('views.application.workflow') }}
                  </el-tag>
                  <el-tag class="blue-tag" v-else style="height: 22px">
                    {{ $t('views.application.simple') }}
                  </el-tag>
                  <el-tag
                    v-if="activeTab === 'SHARED' && sharedType === 'SHARED_TO_ME'"
                    :class="{
                      'purple-tag': item.permission === 'MANAGE',
                      'blue-tag': item.permission === 'WRITE',
                      'green-tag': item.permission === 'READ'
                    }"
                    style="height: 22px; margin-left: 8px"
                  >
                    {{ 
                      item.permission === 'MANAGE' 
                        ? $t('views.application.permissionManage') 
                        : item.permission === 'WRITE' 
                          ? $t('views.application.permissionWrite') 
                          : $t('views.application.permissionRead') 
                    }}
                  </el-tag>
                </div>

                <template #footer>
                  <div class="footer-content">
                    <el-tooltip
                      effect="dark"
                      :content="$t('views.application.setting.demo')"
                      placement="top"
                    >
                      <el-button text @click.stop @click="getAccessToken(item)">
                        <AppIcon iconName="app-view"></AppIcon>
                      </el-button>
                    </el-tooltip>
                    <el-divider direction="vertical" />
                    <el-tooltip effect="dark" :content="$t('common.setting')" placement="top">
                      <el-button text @click.stop="settingApplication(item)" v-if="item.permission !== 'READ' && !(activeTab === 'SHARED' && sharedType === 'ORGANIZATION')">
                        <AppIcon iconName="Setting"></AppIcon>
                      </el-button>
                    </el-tooltip>
                    <el-divider direction="vertical" v-if="item.permission !== 'READ' && !(activeTab === 'SHARED' && sharedType === 'ORGANIZATION')" />
                    <span @click.stop v-if="!(activeTab === 'SHARED' && sharedType === 'ORGANIZATION' && user.userInfo?.role !== 'ADMIN')">
                      <el-dropdown trigger="click">
                        <el-button text @click.stop>
                          <el-icon><MoreFilled /></el-icon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <template v-if="!(activeTab === 'SHARED' && sharedType === 'ORGANIZATION')">
                              <el-dropdown-item
                                v-if="is_show_copy_button(item)"
                                @click="copyApplication(item)"
                              >
                                <AppIcon iconName="app-copy"></AppIcon>
                                {{ $t('common.copy') }}
                              </el-dropdown-item>
                              <el-dropdown-item 
                                v-if="item.permission !== 'READ'"
                                @click.stop="exportApplication(item)"
                              >
                                <AppIcon iconName="app-export"></AppIcon>
                                {{ $t('common.export') }}
                              </el-dropdown-item>
                              <el-dropdown-item 
                                v-if="activeTab === 'MY'"
                                icon="Delete" 
                                @click.stop="deleteApplication(item)"
                              >
                                {{ $t('common.delete') }}
                              </el-dropdown-item>
                            </template>
                            <template v-if="activeTab === 'SHARED' && sharedType === 'ORGANIZATION'">
                              <el-dropdown-item
                                v-if="user.userInfo?.role === 'ADMIN'"
                                @click.stop="addToOrganization(item)"
                              >
                                <AppIcon iconName="app-add"></AppIcon>
                                {{ $t('views.application.addToOrganization.title') }}
                              </el-dropdown-item>
                              <el-dropdown-item
                                v-if="user.userInfo?.role === 'ADMIN'"
                                @click.stop="removeFromOrganization(item)"
                              >
                                <AppIcon iconName="app-remove"></AppIcon>
                                {{ $t('views.application.removeFromOrganization.title') }}
                              </el-dropdown-item>
                            </template>
                            <template v-if="activeTab === 'SHARED' && sharedType === 'SHARED_TO_ME'">
                              <el-dropdown-item
                                @click.stop="exitShare(item)"
                              >
                                <AppIcon iconName="app-exit"></AppIcon>
                                {{ $t('views.application.exitShare.title') }}
                              </el-dropdown-item>
                            </template>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </span>
                  </div>
                </template>
              </CardBox>
            </el-col>
          </el-row>
        </InfiniteScroll>
      </div>
    </div>
    <CreateApplicationDialog ref="CreateApplicationDialogRef" />
    <CopyApplicationDialog ref="CopyApplicationDialogRef" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import applicationApi from '@/api/application'
import CreateApplicationDialog from './component/CreateApplicationDialog.vue'
import CopyApplicationDialog from './component/CopyApplicationDialog.vue'
import ChatLogSearch from './component/ChatLogSearch.vue'

import { MsgSuccess, MsgConfirm, MsgAlert, MsgError } from '@/utils/message'
import { isAppIcon } from '@/utils/application'
import { useRouter } from 'vue-router'
import { isWorkFlow } from '@/utils/application'
import { ValidType, ValidCount } from '@/enums/common'
import { t } from '@/locales'
import useStore from '@/stores'

const elUploadRef = ref<any>()
const { application, user, common } = useStore()
const router = useRouter()

const CopyApplicationDialogRef = ref()
const CreateApplicationDialogRef = ref()
const loading = ref(false)

const applicationList = ref<any[]>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0
})

interface UserOption {
  label: string
  value: string
}

const userOptions = ref<UserOption[]>([])

const selectUserId = ref('all')

const searchValue = ref('')

const apiInputParams = ref([])

const activeTab = ref('MY')
const sharedType = ref('ORGANIZATION')

const sortField = ref('name')
const sortOptions = [
  { label: '按名称排序', value: 'name' },
  { label: '按创建时间排序', value: 'create_time' },
  { label: '按修改时间排序', value: 'update_time' },
  { label: '按提问次数排序', value: 'chat_record_count' },
  { label: '按Token总数排序', value: 'tokens_num' }
]

function copyApplication(row: any) {
  application.asyncGetApplicationDetail(row.id, loading).then((res: any) => {
    if (res?.data) {
      CopyApplicationDialogRef.value.open({ ...res.data, model_id: res.data.model })
    }
  })
}

const is_show_copy_button = (row: any) => {
  return user.userInfo ? user.userInfo.id == row.user_id : false
}

function settingApplication(row: any) {
  if (isWorkFlow(row.type)) {
    router.push({ path: `/application/${row.id}/workflow` })
  } else {
    router.push({ path: `/application/${row.id}/${row.type}/setting` })
  }
}

const exportApplication = (application: any) => {
  applicationApi.exportApplication(application.id, application.name, loading).catch((e) => {
    if (e.response.status !== 403) {
      e.response.data.text().then((res: string) => {
        MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
      })
    }
  })
}
const importApplication = (file: any) => {
  const formData = new FormData()
  formData.append('file', file.raw, file.name)
  elUploadRef.value.clearFiles()
  applicationApi
    .importApplication(formData, loading)
    .then(async (res: any) => {
      if (res?.data) {
        searchHandle()
      }
    })
    .catch((e) => {
      if (e.code === 400) {
        MsgConfirm(t('common.tip'), t('views.application.tip.professionalMessage'), {
          cancelButtonText: t('common.confirm'),
          confirmButtonText: t('common.professional')
        }).then(() => {
          window.open('https://maxkb.cn/pricing.html', '_blank')
        })
      }
    })
}

function openCreateDialog() {
  common
    .asyncGetValid(ValidType.Application, ValidCount.Application, loading)
    .then(async (res: any) => {
      if (res?.data) {
        CreateApplicationDialogRef.value.open()
      } else if (res?.code === 400) {
        MsgConfirm(t('common.tip'), t('views.application.tip.professionalMessage'), {
          cancelButtonText: t('common.confirm'),
          confirmButtonText: t('common.professional')
        }).then(() => {
          window.open('https://maxkb.cn/pricing.html', '_blank')
        })
      }
    })
}

function searchHandle() {
  if (user.userInfo) {
    localStorage.setItem(user.userInfo.id + 'application', selectUserId.value)
  }
  applicationList.value = []
  paginationConfig.current_page = 1
  paginationConfig.total = 0
  getList()
}

function mapToUrlParams(map: any[]) {
  const params = new URLSearchParams()

  map.forEach((item: any) => {
    params.append(encodeURIComponent(item.name), encodeURIComponent(item.value))
  })

  return params.toString() // 返回 URL 查询字符串
}

function getAccessToken(item: any) {
  if (!item || !item.id) {
    return
  }
  applicationList.value
    .filter((app) => app.id === item.id)[0]
    ?.work_flow?.nodes?.filter((v: any) => v.id === 'base-node')
    .map((v: any) => {
      apiInputParams.value = v.properties.api_input_field_list
        ? v.properties.api_input_field_list.map((v: any) => {
            return {
              name: v.variable,
              value: v.default_value
            }
          })
        : v.properties.input_field_list
          ? v.properties.input_field_list
              .filter((v: any) => v.assignment_method === 'api_input')
              .map((v: any) => {
                return {
                  name: v.variable,
                  value: v.default_value
                }
              })
          : []
    })

  const apiParams = mapToUrlParams(apiInputParams.value)
    ? '?' + mapToUrlParams(apiInputParams.value)
    : ''
  application.asyncGetAccessToken(item.id, loading).then((res: any) => {
    window.open(application.location + res?.data?.access_token + apiParams)
  })
}

function deleteApplication(row: any) {
  MsgConfirm(
    // @ts-ignore
    `${t('views.application.delete.confirmTitle')}${row.name} ?`,
    t('views.application.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      applicationApi.delApplication(row.id, loading).then(() => {
        const index = applicationList.value.findIndex((v) => v.id === row.id)
        applicationList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

function handleTabChange() {
  selectUserId.value = 'all'
  searchValue.value = ''
  applicationList.value = []
  paginationConfig.current_page = 1
  paginationConfig.total = 0
  getList()
}

function sharedTabChangeHandle() {
  selectUserId.value = 'all'
  searchValue.value = ''
  applicationList.value = []
  paginationConfig.current_page = 1
  paginationConfig.total = 0
  getList()
}

function sortApplicationList(list: any[]) {
  // 后端已经处理排序，直接返回列表
  return list
}

function getList() {
  const params = {
    ...(searchValue.value && { name: searchValue.value }),
    ...(selectUserId.value &&
      selectUserId.value !== 'all' && { select_user_id: selectUserId.value }),
    order_by: sortField.value
  }
  
  let apiPromise
  if (activeTab.value === 'SHARED' && sharedType.value === 'SHARED_TO_ME') {
    apiPromise = applicationApi.getShareToMePage(paginationConfig, params, loading)
  } else if (activeTab.value === 'SHARED' && sharedType.value === 'ORGANIZATION') {
    apiPromise = applicationApi.getOrganizationPage(paginationConfig, params, loading)
  } else {
    apiPromise = applicationApi.getApplication(paginationConfig, {
      ...params,
      type: activeTab.value,
      ...(activeTab.value === 'SHARED' && { shared_type: sharedType.value })
    }, loading)
  }

  apiPromise.then((res: any) => {
    res.data.records.forEach((item: any) => {
      // 确保creator_name字段有值
      if (!item.creator_name) {
      if (activeTab.value === 'SHARED' && sharedType.value === 'SHARED_TO_ME') {
          item.creator_name = item.username || ''
      } else {
        if (user.userInfo && item.user_id === user.userInfo.id) {
            item.creator_name = user.userInfo.username
        } else {
            item.creator_name = userOptions.value.find((v) => v.value === item.user_id)?.label || ''
          }
        }
      }
      
      // 保持username字段的兼容性
      item.username = item.creator_name
    })
    paginationConfig.total = res.data.total
    let newRecords = sortApplicationList(res.data.records)
    
    if (activeTab.value === 'SHARED' && sharedType.value === 'SHARED_TO_ME' && user.userInfo?.id) {
      newRecords = newRecords.filter(item => item.user_id !== user.userInfo?.id)
      paginationConfig.total = applicationList.value.length + newRecords.length
    }
    
    applicationList.value = [...applicationList.value, ...newRecords]
  })
}

function getUserList() {
  applicationApi.getUserList('APPLICATION', loading).then((res) => {
    if (res.data) {
      userOptions.value = res.data.map((item: any) => {
        return {
          label: item.username,
          value: item.id
        }
      })
      if (user.userInfo) {
        const selectUserIdValue = localStorage.getItem(user.userInfo.id + 'application')
        if (selectUserIdValue && userOptions.value.find((v) => v.value === selectUserIdValue)) {
          selectUserId.value = selectUserIdValue
        }
      }
      getList()
    }
  })
}

function exitShare(row: any) {
  MsgConfirm(
    // @ts-ignore
    `${t('views.application.exitShare.confirmTitle')}${row.name} ?`,
    t('views.application.exitShare.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      applicationApi.exitShare(row.id, loading).then(() => {
        paginationConfig.current_page = 1
        applicationList.value = []
        getList()
        MsgSuccess(t('common.exitSuccess'))
      })
    })
    .catch(() => {})
}

function addToOrganization(row: any) {
  MsgConfirm(
    t('views.application.addToOrganization.confirmTitle'),
    t('views.application.addToOrganization.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'primary'
    }
  )
    .then(() => {
      applicationApi.addToOrganization(row.id, loading).then(() => {
        MsgSuccess(t('views.application.addToOrganization.success'))
      })
    })
    .catch(() => {})
}

function removeFromOrganization(row: any) {
  MsgConfirm(
    t('views.application.removeFromOrganization.confirmTitle'),
    t('views.application.removeFromOrganization.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      applicationApi.removeFromOrganization(row.id, loading).then(() => {
        MsgSuccess(t('views.application.removeFromOrganization.success'))
        paginationConfig.current_page = 1
        applicationList.value = []
        getList()
      })
    })
    .catch(() => {})
}

onMounted(() => {
  getUserList()
})
</script>
<style lang="scss" scoped>
.application-card-add {
  width: 100%;
  font-size: 14px;
  min-height: var(--card-min-height);
  border: 1px dashed var(--el-border-color);
  background: var(--el-disabled-bg-color);
  border-radius: 8px;
  box-sizing: border-box;

  &:hover {
    border: 1px solid var(--el-card-bg-color);
    background-color: var(--el-card-bg-color);
  }

  .card-add-button {
    &:hover {
      border-radius: 4px;
      background: var(--app-text-color-light-1);
    }

    :deep(.el-upload) {
      display: block;
      width: 100%;
      color: var(--el-text-color-regular);
    }
  }
}

.application-card {
  .status-tag {
    position: absolute;
    right: 16px;
    top: 15px;
  }
}

.dropdown-custom-switch {
  padding: 5px 11px;
  font-size: 14px;
  font-weight: 400;

  span {
    margin-right: 26px;
  }
}

.el-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 16px;
  }
}

.status-tag {
  position: absolute;
  right: 16px;
  top: 15px;
  display: flex;
  gap: 8px;
}

// 权限标签样式
:deep(.green-tag) {
  background-color: var(--el-color-success-light-9);
  border-color: var(--el-color-success-light-7);
  color: var(--el-color-success);
}

:deep(.purple-tag) {
  background-color: var(--el-color-warning-light-9);
  border-color: var(--el-color-warning-light-7);
  color: var(--el-color-warning);
}

:deep(.blue-tag) {
  background-color: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-7);
  color: var(--el-color-primary);
}
</style>
